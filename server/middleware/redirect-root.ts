import { defineEventHandler, getQuery, sendRedirect } from 'h3'

export default defineEventHandler((event) => {
  const path = event.path || event.node.req.url || ''
  if (!path || path.startsWith('/api') || path.startsWith('/auth/')) {
    return
  }
  const query = getQuery(event)
  if (query.redirect) {
    const value = Array.isArray(query.redirect) ? query.redirect[0] : query.redirect
    if (typeof value === 'string' && value.trim().length > 0) {
      const target = `/auth/login?redirect=${encodeURIComponent(value)}`
      if (target !== path) {
        return sendRedirect(event, target, 302)
      }
    }
  }
})
