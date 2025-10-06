import { defineEventHandler, createError, sendRedirect, getRequestHeaders } from 'h3'

export default defineEventHandler(async (event) => {
  console.log('[OAuth] Proxying /api/auth/google/authorize via backend')

  const config = useRuntimeConfig()
  const backendBase = (config.backendBase || process.env.BACKEND_BASE || 'http://backend:8000').replace(/\/$/, '')
  const targetUrl = `${backendBase}/auth/google/authorize`

  const incoming = getRequestHeaders(event)
  const headers: Record<string, string> = {}

  if (incoming['user-agent']) {
    headers['user-agent'] = incoming['user-agent'] as string
  }
  if (incoming['x-forwarded-for']) {
    headers['x-forwarded-for'] = incoming['x-forwarded-for'] as string
  }
  if (incoming['x-forwarded-host']) {
    headers['x-forwarded-host'] = incoming['x-forwarded-host'] as string
  } else if (incoming.host) {
    headers['x-forwarded-host'] = incoming.host as string
  }

  try {
    const response = await $fetch.raw(targetUrl, {
      method: 'GET',
      redirect: 'manual',
      headers
    })

    const location = response.headers.get('location')
    if (!location) {
      throw new Error('Missing Location header from backend authorize endpoint')
    }

    const status = response.status || 302
    return sendRedirect(event, location, status)
  } catch (err) {
    console.error('[OAuth] authorize proxy error:', err)
    throw createError({
      statusCode: 502,
      statusMessage: 'Google OAuth authorize proxy failed'
    })
  }
})
