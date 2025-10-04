import { buildBackendUrl } from '~/server/utils/backend'

export default defineEventHandler(async (event) => {
  const backendUrl = buildBackendUrl(event, '/auth/logout')
  const headers: Record<string, string> = { 'Accept': 'application/json' }
  const incomingCookies = getHeader(event, 'cookie')
  const auth = getHeader(event, 'authorization')
  if (incomingCookies) headers.Cookie = incomingCookies
  if (auth) headers.Authorization = auth

  const res = await fetch(backendUrl, { method: 'POST', headers })
  const text = await res.text()
  let data: any = {}
  if (text) { try { data = JSON.parse(text) } catch {} }
  setResponseStatus(event, res.status)
  return data
})

