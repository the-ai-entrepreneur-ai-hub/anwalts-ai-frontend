/**
 * Google OAuth Entry Point
 * Redirects to /auth/google/authorize with preserved query parameters
 */
export default defineEventHandler((event) => {
  // Preserve any query parameters
  const query = getQuery(event)
  const queryString = Object.keys(query).length > 0 
    ? '?' + new URLSearchParams(query as Record<string, string>).toString()
    : ''
  
  // Redirect to authorize endpoint
  return sendRedirect(event, `/auth/google/authorize${queryString}`, 302)
})