import { createError, sendRedirect, getQuery, getRequestHeaders, appendResponseHeader, splitCookiesString } from 'h3'
import type { H3Event } from 'h3'
import { resolveBackendBase } from '~/server/utils/backend'

const FALLBACK_BACKEND_BASES = [
  'http://backend:8000'
]

type QueryInput = ReturnType<typeof getQuery> | Record<string, unknown>

function buildSearchParams(query: QueryInput): URLSearchParams {
  const params = new URLSearchParams()
  Object.entries(query).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach((entry) => {
        if (entry !== undefined && entry !== null) {
          params.append(key, String(entry))
        }
      })
    } else if (value !== undefined && value !== null) {
      params.append(key, String(value))
    }
  })
  return params
}

function gatherForwardHeaders(event: H3Event, options?: { includeCookies?: boolean }) {
  const { includeCookies = false } = options ?? {}
  const incoming = getRequestHeaders(event)
  const headers: Record<string, string> = {}

  if (includeCookies && incoming.cookie) {
    headers.cookie = incoming.cookie
  }
  if (incoming['user-agent']) {
    headers['user-agent'] = incoming['user-agent']
  }
  if (incoming['x-forwarded-for']) {
    headers['x-forwarded-for'] = incoming['x-forwarded-for']
  }
  if (incoming['x-forwarded-host']) {
    headers['x-forwarded-host'] = incoming['x-forwarded-host']
  } else if (incoming.host) {
    headers['x-forwarded-host'] = incoming.host
  }

  return headers
}

function buildBackendCandidates(event: H3Event) {
  const resolved = resolveBackendBase(event)
  return Array.from(
    new Set(
      [resolved, ...FALLBACK_BACKEND_BASES].filter((value) => typeof value === 'string' && value.length > 0)
    )
  )
}

function joinUrl(base: string, path: string, params: URLSearchParams) {
  const normalizedBase = base.replace(/\/$/, '')
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  const query = params.toString()
  return query ? `${normalizedBase}${normalizedPath}?${query}` : `${normalizedBase}${normalizedPath}`
}

export async function proxyBackendRedirect(event: H3Event, path: string, query?: QueryInput) {
  const params = buildSearchParams(query ?? getQuery(event))
  const headers = gatherForwardHeaders(event, { includeCookies: true })
  const candidates = buildBackendCandidates(event)

  let lastError: unknown = null

  for (const backendBase of candidates) {
    const targetUrl = joinUrl(backendBase, path, params)
    try {
      const response = await fetch(targetUrl, {
        method: 'GET',
        headers,
        redirect: 'manual'
      })

      const location = response.headers.get('location')
      if (!location) {
        lastError = new Error(`Missing Location header from backend authorize endpoint (${targetUrl})`)
        continue
      }

      // Forward any Set-Cookie headers before sending redirect
      const rawSetCookie = typeof response.headers.getSetCookie === 'function'
        ? response.headers.getSetCookie()
        : response.headers.get('set-cookie')
      
      // Handle missing cookies gracefully
      if (!rawSetCookie) {
        const status = response.status && response.status !== 0 ? response.status : 302
        return sendRedirect(event, location, status)
      }
      
      const setCookies = Array.isArray(rawSetCookie)
        ? rawSetCookie
        : typeof rawSetCookie === 'string'
          ? splitCookiesString(rawSetCookie)
          : []
      
      // Validate and filter cookies before forwarding
      for (const cookie of setCookies) {
        if (cookie && typeof cookie === 'string' && cookie.trim().length > 0) {
          appendResponseHeader(event, 'set-cookie', cookie)
        }
      }

      // Create redirect response (after Set-Cookie headers have been forwarded)
      const status = response.status && response.status !== 0 ? response.status : 302
      return sendRedirect(event, location, status)
    } catch (error) {
      lastError = error
      console.warn(`[OAuth] Backend redirect proxy failed for ${targetUrl}`, error)
    }
  }

  console.error('[OAuth] Backend redirect proxy exhausted all candidates', lastError)
  throw createError({
    statusCode: 502,
    statusMessage: 'Google OAuth authorize proxy failed'
  })
}

export async function proxyBackendResponse(event: H3Event, path: string, query?: QueryInput) {
  const params = buildSearchParams(query ?? getQuery(event))
  const headers = gatherForwardHeaders(event, { includeCookies: true })
  const candidates = buildBackendCandidates(event)

  let lastError: unknown = null

  for (const backendBase of candidates) {
    const targetUrl = joinUrl(backendBase, path, params)
    try {
      const response = await fetch(targetUrl, {
        method: 'GET',
        headers,
        redirect: 'manual'
      })

      const body = await response.arrayBuffer()
      const headersInit = new Headers()

      response.headers.forEach((value, key) => {
        if (key.toLowerCase() !== 'set-cookie') {
          headersInit.set(key, value)
        }
      })

      const setCookies =
        typeof response.headers.getSetCookie === 'function'
          ? response.headers.getSetCookie()
          : response.headers.get('set-cookie')

      // Validate and filter cookies before forwarding
      if (Array.isArray(setCookies)) {
        setCookies.forEach((cookie) => {
          if (cookie && typeof cookie === 'string' && cookie.trim().length > 0) {
            headersInit.append('set-cookie', cookie)
          }
        })
      } else if (typeof setCookies === 'string' && setCookies.trim().length > 0) {
        headersInit.set('set-cookie', setCookies)
      }

      return new Response(body, {
        status: response.status,
        statusText: response.statusText,
        headers: headersInit
      })
    } catch (error) {
      lastError = error
      console.warn(`[OAuth] Backend response proxy failed for ${targetUrl}`, error)
    }
  }

  console.error('[OAuth] Backend response proxy exhausted all candidates', lastError)
  throw createError({
    statusCode: 502,
    statusMessage: 'Google OAuth callback proxy failed'
  })
}
