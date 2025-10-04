import { buildBackendUrl } from '~/server/utils/backend'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const payload = {
    email: body?.email,
    password: body?.password,
    first_name: body?.first_name,
    last_name: body?.last_name,
    title: body?.title,
    firm_name: body?.firm_name,
    terms_accepted: !!body?.terms_accepted,
    csrf_token: body?.csrf_token || 'stub-csrf-token'
  }

  const backendUrl = buildBackendUrl(event, '/auth/register')
  const headers: Record<string, string> = { 'Content-Type': 'application/json', Accept: 'application/json' }
  const incomingCookies = getHeader(event, 'cookie')
  if (incomingCookies) headers.Cookie = incomingCookies

  const res = await fetch(backendUrl, { method: 'POST', headers, body: JSON.stringify(payload) })
  const rawCookies = (res.headers as any).raw?.()['set-cookie'] || res.headers.get('set-cookie')
  if (rawCookies) {
    event.node.res.setHeader('set-cookie', Array.isArray(rawCookies) ? rawCookies : [rawCookies])
  }

  const text = await res.text()
  let data: any = {}
  if (text) { try { data = JSON.parse(text) } catch {} }
  setResponseStatus(event, res.status)
  if (!res.ok || data?.success === false) {
    const message = data?.error?.message || data?.message || 'Registration failed'
    throw createError({ statusCode: res.status || 400, statusMessage: message })
  }
  return data
})

