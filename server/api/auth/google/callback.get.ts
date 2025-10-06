import { defineEventHandler, sendRedirect, getQuery, createError } from 'h3'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const code = query.code as string
  const error = query.error as string

  console.log('[Google OAuth] Callback received:', {
    hasCode: !!code,
    hasError: !!error
  })

  if (error) {
    console.error('[Google OAuth] Error from provider:', error, query.error_description)
    return sendRedirect(event, '/?auth_error=' + encodeURIComponent(error), 302)
  }

  if (!code) {
    console.error('[Google OAuth] No code in callback')
    return sendRedirect(event, '/?auth_error=no_code', 302)
  }

  const config = useRuntimeConfig()
  const backendBase = (config.backendBase || process.env.BACKEND_BASE || 'http://backend:8000').replace(/\/$/, '')
  const targetUrl = `${backendBase}/auth/google/callback`

  const headers: Record<string, string> = {}
  const incoming = event.node.req.headers

  if (incoming.cookie) {
    headers.cookie = incoming.cookie as string
  }
  if (incoming['user-agent']) {
    headers['user-agent'] = incoming['user-agent'] as string
  }
  if (incoming['x-forwarded-for']) {
    headers['x-forwarded-for'] = incoming['x-forwarded-for'] as string
  }
  if (incoming.host) {
    headers['x-forwarded-host'] = incoming.host as string
  }

  try {
    const searchParams = new URLSearchParams()
    Object.entries(query).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        value.forEach((v) => searchParams.append(key, String(v)))
      } else if (value !== undefined && value !== null) {
        searchParams.append(key, String(value))
      }
    })

    const url = `${targetUrl}?${searchParams.toString()}`

    const response = await fetch(url, {
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

    const setCookies = typeof response.headers.getSetCookie === 'function'
      ? response.headers.getSetCookie()
      : []
    for (const cookie of setCookies) {
      headersInit.append('set-cookie', cookie)
    }

    return new Response(body, {
      status: response.status,
      statusText: response.statusText,
      headers: headersInit
    })
  } catch (err) {
    console.error('[Google OAuth] Callback proxy error:', err)
    throw createError({
      statusCode: 502,
      statusMessage: 'Google OAuth callback proxy failed'
    })
  }
})
