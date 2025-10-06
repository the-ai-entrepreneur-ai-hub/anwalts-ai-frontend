import { clearSupabaseSessionCookie, readSupabaseSessionCookie } from '~/server/utils/sessionCookie'

export default defineEventHandler(async (event) => {
  const supabase = useSupabaseServer(event)

  // Get session from cookie
  const sessionCookie = readSupabaseSessionCookie(event)

  if (sessionCookie?.access_token) {
    try {
      await supabase.auth.admin.signOut(sessionCookie.access_token)
    } catch (error) {
      console.warn('Supabase logout warning', error)
    }
  }

  // Clear session cookie
  clearSupabaseSessionCookie(event)

  return {
    success: true,
    message: 'Logged out successfully'
  }
})
