export default defineNuxtRouteMiddleware(async (to) => {
  // Allow public pages
  const PUBLIC = new Set<string>(['/', '/privacy', '/terms', '/contact', '/changelog', '/test-login', '/test-auth'])
  if (PUBLIC.has(to.path)) return

  // Server-side: skip redirect to let client check auth after hydration
  if (process.server) {
    return
  }

  // Client-side guard - check for simple JWT token first
  if (process.client) {
    try {
      // Check for simple auth token (from OAuth or login)
      const authToken = localStorage.getItem('auth_token')
      const userId = localStorage.getItem('user_id')
      
      if (authToken && userId) {
        console.log('[Auth Guard] Valid JWT token found')
        return // User is authenticated with JWT
      }

      // Fallback: try Supabase session
      const { getSession, isSessionExpired } = useSupabaseAuth()
      const session = await getSession()

      if (session && !isSessionExpired(session)) {
        console.log('[Auth Guard] Valid Supabase session found')
        return // User is authenticated with Supabase
      }
    } catch (err) {
      console.error('Auth guard error:', err)
    }

    // Not authenticated - redirect to home with auth=required
    console.log('[Auth Guard] No valid auth found, redirecting to home')
    return navigateTo('/?auth=required')
  }
})
