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

    const limit = Math.max(1, Math.min(25, parseInt((getQuery(event).limit as string) || '15')))
    const pageToken = (getQuery(event).pageToken as string) || ''
    const listUrl = new URL('https://gmail.googleapis.com/gmail/v1/users/me/messages')
    listUrl.searchParams.set('labelIds','INBOX')
    listUrl.searchParams.set('maxResults', String(limit))
    if (pageToken) listUrl.searchParams.set('pageToken', pageToken)
    const listRes = await fetch(listUrl.toString(), {
      headers: { Authorization: `Bearer ${token.access_token}` }
    })
    const listing = await listRes.json()
    const messages = Array.isArray(listing.messages) ? listing.messages : []
    const nextPageToken = listing.nextPageToken || ''

    const results: any[] = []
    for (const m of messages) {
      const mr = await fetch(`https://gmail.googleapis.com/gmail/v1/users/me/messages/${m.id}?format=metadata&metadataHeaders=From&metadataHeaders=Subject`, {
        headers: { Authorization: `Bearer ${token.access_token}` }
      })
      const md = await mr.json()
      const hdrs: Record<string,string> = {}
      for (const h of (md.payload?.headers||[])) { hdrs[h.name] = h.value }
      const from = hdrs['From'] || ''
      const subject = hdrs['Subject'] || '(no subject)'
      const snippet = (md.snippet || '').replace(/\s+/g,' ').slice(0, 140)
      const match = from.match(/^(.*)<(.*)>$/)
      const senderName = match ? match[1].trim().replace(/\"/g,'') : from
      const senderEmail = match ? match[2].trim() : ''
      
      const labelIds = md.labelIds||[]
      const isImportant = labelIds.includes('IMPORTANT')
      const subjLower = String(subject||'').toLowerCase()
      let type = 'General'
      if (/(contract|vertrag)/i.test(subject)) type = 'Contract'
      else if (/(termination|kündigung|kuendigung)/i.test(subject)) type = 'Termination'
      else if (/(reminder|erinnerung|mahnung)/i.test(subject)) type = 'Reminder'
      results.push({
        id: md.id,
        labelIds: (md.labelIds||[]),
        starred: (md.labelIds||[]).includes('STARRED'),
        
        threadId: md.threadId,
        openUrl: `https://mail.google.com/mail/u/0/#all/${md.id}`,
        senderName: senderName || senderEmail,
        senderEmail,
        subject,
        snippet,
        date: new Date((md.internalDate && Number(md.internalDate)) || Date.now()).toISOString(),
        type,
        status: labelIds.includes('UNREAD') ? 'Unread' : 'Read',
        unread: labelIds.includes('UNREAD'),
        priority: isImportant
      })
    
    }

    return { success: true, emails: results, nextPageToken }
  } catch (e: any) {
    setResponseStatus(event, 500)
    return { error: String(e?.message||e) }
  }
})
