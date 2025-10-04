import { buildBackendUrl } from '~/server/utils/backend'

export default defineEventHandler( async (event) => {
  const backendUrl = buildBackendUrl(event, '/auth/validate')
  const headers: Record<string, string> = { 'Accept': 'application/json' }
  const incomingCookies = getHeader(event, 'cookie')
  const auth = getHeader(event, 'authorization')
  if (incomingCookies) headers.Cookie = incomingCookies
  if (auth) headers.Authorization = auth

  try {
    const res = await fetch(backendUrl, { headers })
    const text = await res.text()
    let data: any = {}
    if (text) { try { data = JSON.parse(text) } catch {} }
    if (!res.ok) {
      setResponseStatus(event, 200)
      return { authenticated: false, timestamp: new Date().toISOString() }
    }
    setResponseStatus(event, 200)
    return { authenticated: true, user: data?.user || null, timestamp: new Date().toISOString() }
  } catch {
    setResponseStatus(event, 200)
    return { authenticated: false, timestamp: new Date().toISOString() }
  }
})

