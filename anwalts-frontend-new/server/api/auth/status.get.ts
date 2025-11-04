import { buildBackendUrl } from '~/server/utils/backend'

export default defineEventHandler(async (event) => {
  const backendUrl = buildBackendUrl(event, '/api/auth/status')

  const headers: Record<string, string> = {
    Accept: 'application/json',
  }

  const cookies = getHeader(event, 'cookie')
  if (cookies) headers.Cookie = cookies

  const auth = getHeader(event, 'authorization')
  if (auth) headers.Authorization = auth

  const backendResponse = await fetch(backendUrl, { headers }).catch((error) => {
    console.error('Auth status proxy error', error)
    throw createError({ statusCode: 502, statusMessage: 'Authentication service unavailable' })
  })

  const rawCookies = (backendResponse.headers as any).raw?.()['set-cookie'] || backendResponse.headers.get('set-cookie')
  if (rawCookies) {
    event.node.res.setHeader('set-cookie', Array.isArray(rawCookies) ? rawCookies : [rawCookies])
  }

  event.node.res.statusCode = backendResponse.status

  const text = await backendResponse.text()
  let result: any = {}
  if (text) {
    try {
      result = JSON.parse(text)
    } catch (error) {
      console.warn('Auth status: failed to parse backend response', error)
    }
  }

  if (!backendResponse.ok) {
    const message = result?.error?.message || result?.message || 'Not authenticated'
    throw createError({ statusCode: backendResponse.status || 401, statusMessage: message })
  }

  return result
})
