export default defineEventHandler(async (event) => {
  const next = (getQuery(event)?.next as string) || '/dashboard'

  // If Google session cookie present, go to dashboard (or next)
  const userData = getCookie(event, 'user_data')
  if (userData) {
    try {
      const parsed = JSON.parse(userData)
      if (parsed && parsed.email) {
        await sendRedirect(event, next, 302)
        return
      }
    } catch {}
  }

  // Otherwise, require auth
  await sendRedirect(event, '/?auth=required', 302)
})
