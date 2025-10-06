import { clearSupabaseSessionCookie, readSupabaseSessionCookie, setSupabaseSessionCookie } from '~/server/utils/sessionCookie'

export default defineEventHandler(async (event) => {
  const supabase = useSupabaseServer(event)
  const stored = readSupabaseSessionCookie(event)

  if (!stored || !stored.access_token || !stored.refresh_token) {
    if (stored && (!stored.access_token || !stored.refresh_token)) {
      clearSupabaseSessionCookie(event)
    }
    return {
      session: null,
      user: null,
      profile: null
    }
  }

  let activeSession = stored
  let user = null

  try {
    const isExpired = typeof activeSession.expires_at === 'number' && activeSession.expires_at * 1000 <= Date.now()

    if (isExpired && activeSession.refresh_token) {
      const { data: refreshData, error: refreshError } = await supabase.auth.refreshSession({
        refresh_token: activeSession.refresh_token
      })

      if (refreshError || !refreshData.session) {
        clearSupabaseSessionCookie(event)
        return {
          session: null,
          user: null,
          profile: null
        }
      }

      activeSession = {
        access_token: refreshData.session.access_token,
        refresh_token: refreshData.session.refresh_token,
        expires_at: refreshData.session.expires_at ?? null
      }

      setSupabaseSessionCookie(event, activeSession)
      user = refreshData.session.user ?? null
    }

    if (!user) {
      const { data: userData, error: userError } = await supabase.auth.getUser(activeSession.access_token)

      if (userError || !userData.user) {
        clearSupabaseSessionCookie(event)
        return {
          session: null,
          user: null,
          profile: null
        }
      }

      user = userData.user
    }

    let profile = null
    if (user?.id) {
      try {
        const { data: profileData } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', user.id)
          .single()

        profile = profileData ?? null
      } catch {
        profile = null
      }
    }

    return {
      session: activeSession,
      user: user ? {
        id: user.id,
        email: user.email,
        role: user.role,
        aud: user.aud,
        created_at: user.created_at,
        last_sign_in_at: user.last_sign_in_at,
        user_metadata: user.user_metadata ?? {}
      } : null,
      profile
    }
  } catch (error) {
    console.error('Failed to resolve session from cookie', error)
    clearSupabaseSessionCookie(event)
    return {
      session: null,
      user: null,
      profile: null
    }
  }
})
