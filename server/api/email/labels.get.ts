export default defineEventHandler(async (event) => {
  try {
    const rt = getCookie(event, 'gmail_rt')
    if (!rt) { setResponseStatus(event, 401); return { error: 'not_linked' } }

    const clientId = process.env.GOOGLE_CLIENT_ID || (globalThis as any).GOOGLE_CLIENT_ID
    const clientSecret = process.env.GOOGLE_CLIENT_SECRET || (globalThis as any).GOOGLE_CLIENT_SECRET

    const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        client_id: clientId!, client_secret: clientSecret!,
        refresh_token: rt, grant_type: 'refresh_token'
      })
    })
    const token = await tokenRes.json()
    if (!token.access_token) { setResponseStatus(event, 401); return { error: 'token_refresh_failed' } }

    const res = await fetch('https://gmail.googleapis.com/gmail/v1/users/me/labels', {
      headers: { Authorization: `Bearer ${token.access_token}` }
    })

    if (!res.ok) {
      setResponseStatus(event, res.status)
      return { error: 'labels_failed' }
    }

    const data = await res.json()
    const labels = Array.isArray(data.labels) ? data.labels.map((l:any) => ({ id: l.id, name: l.name, type: l.type })) : []
    return { success: true, labels }
  } catch (e:any) {
    setResponseStatus(event, 500)
    return { error: String(e?.message||e) }
  }
})
