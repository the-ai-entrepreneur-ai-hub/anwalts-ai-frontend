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

    const body = await readBody(event)
    const id = body?.id as string
    const add = (body?.add as string[]) || []
    const remove = (body?.remove as string[]) || []
    if (!id) { setResponseStatus(event, 400); return { error: 'missing_id' } }

    const res = await fetch(`https://gmail.googleapis.com/gmail/v1/users/me/messages/${id}/modify`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token.access_token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ addLabelIds: add, removeLabelIds: remove })
    })

    if (!res.ok) {
      const text = await res.text()
      setResponseStatus(event, res.status)
      return { error: 'modify_failed', detail: text }
    }

    return { success: true }
  } catch (e: any) {
    setResponseStatus(event, 500)
    return { error: String(e?.message||e) }
  }
})
