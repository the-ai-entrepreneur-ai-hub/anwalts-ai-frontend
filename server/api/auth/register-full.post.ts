import { buildBackendUrl } from '~/server/utils/backend'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const backendUrl = buildBackendUrl(event, '/auth/register-full')
  const headers: Record<string, string> = { 'Content-Type': 'application/json', Accept: 'application/json' }
  const incomingCookies = getHeader(event, 'cookie')
  if (incomingCookies) headers.Cookie = incomingCookies

  const res = await fetch(backendUrl, { method: 'POST', headers, body: JSON.stringify(body||{}) })
  const text = await res.text()
  let data: any = {}
  if (text) { try { data = JSON.parse(text) } catch {} }
  setResponseStatus(event, res.status)
  if (!res.ok) {
    const message = data?.detail || data?.message || 'Registration failed'
    throw createError({ statusCode: res.status || 400, statusMessage: message })
  }
  return data
})

