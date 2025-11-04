import { buildBackendUrl } from '~/server/utils/backend'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const email = body?.email?.trim?.()
  const password = body?.password
  if (!email || !password) {
    throw createError({ statusCode: 400, statusMessage: 'Email and password are required' })
  }

  const backendUrl = buildBackendUrl(event, '/auth/login')
  const headers: Record<string, string> = { 'Content-Type': 'application/json', Accept: 'application/json' }
  const incomingCookies = getHeader(event, 'cookie')
  if (incomingCookies) headers.Cookie = incomingCookies

  const payload = {
    email,
    password,
    remember_me: !!body?.remember_me,
    csrf_token: body?.csrf_token || 'stub-csrf-token',
    device_fingerprint: body?.device_fingerprint ?? null,
  }

  const res = await fetch(backendUrl, { method: 'POST', headers, body: JSON.stringify(payload) })
  const rawCookies = (res.headers as any).raw?.()['set-cookie'] || res.headers.get('set-cookie')
  if (rawCookies) {
    event.node.res.setHeader('set-cookie', Array.isArray(rawCookies) ? rawCookies : [rawCookies])
  }

  const text = await res.text()
  let data: any = {}
  if (text) {
    try { data = JSON.parse(text) } catch {}
  }

  setResponseStatus(event, res.status)
  if (!res.ok || data?.success === false) {
    const message = data?.error?.message || data?.message || 'Invalid email or password'
    throw createError({ statusCode: res.status || 401, statusMessage: message })
  }
  return data
})

