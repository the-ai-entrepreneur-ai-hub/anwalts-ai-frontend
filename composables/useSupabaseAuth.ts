import { useNuxtApp } from '#app'
import { createClient } from '@supabase/supabase-js'
import { createBrowserClient } from '@supabase/ssr'
import type { Session, User } from '@supabase/supabase-js'

type StoredSessionPayload = {
  access_token: string
  refresh_token: string
  expires_at: number | null
}

const STORAGE_SESSION_KEY = 'supabase-session'
const STORAGE_USER_KEY = 'anwalts_user'
const STORAGE_PROFILE_KEY = 'anwalts_profile'

export const useSupabaseAuth = () => {
  const config = useRuntimeConfig()
  const nuxtApp = useNuxtApp()
  const user = useState<User | null>('supabase-user', () => null)
  const session = useState<Session | null>('supabase-session', () => null)
  const profile = useState<Record<string, any> | null>('supabase-profile', () => null)

  // Force browser client creation only on client-side
  const supabase = (() => {
    if (process.client) {
      console.log('[OAuth] Creating browser client with PKCE flow (default cookie config)')
      // Use default cookie handling - let @supabase/ssr handle cookies automatically
      const client = createBrowserClient(config.public.supabaseUrl, config.public.supabaseKey)

      // Log the client type for debugging
      console.log('[OAuth] Browser client type:', client.constructor.name)
      console.log('[OAuth] Browser client storage key:', (client as any).storageKey || 'unknown')

      return client
    } else {
      return createClient(config.public.supabaseUrl, config.public.supabaseKey, {
        auth: {
          persistSession: false
        }
      })
    }
  })()

  const persistLocalStorage = (
    sessionPayload: StoredSessionPayload | null,
    userPayload: Record<string, any> | null = null,
    profilePayload: Record<string, any> | null = null
  ) => {
    if (!process.client) return

    try {
      if (sessionPayload?.access_token && sessionPayload?.refresh_token) {
        localStorage.setItem(STORAGE_SESSION_KEY, JSON.stringify(sessionPayload))
      } else {
        localStorage.removeItem(STORAGE_SESSION_KEY)
      }
    } catch (error) {
      console.warn('Failed to persist session storage', error)
    }

    try {
      if (userPayload) {
        localStorage.setItem(STORAGE_USER_KEY, JSON.stringify(userPayload))
      } else {
        localStorage.removeItem(STORAGE_USER_KEY)
      }
    } catch (error) {
      console.warn('Failed to persist user storage', error)
    }

    try {
      if (profilePayload) {
        localStorage.setItem(STORAGE_PROFILE_KEY, JSON.stringify(profilePayload))
      } else {
        localStorage.removeItem(STORAGE_PROFILE_KEY)
      }
    } catch (error) {
      console.warn('Failed to persist profile storage', error)
    }
  }

  const loadStoredSession = (): StoredSessionPayload | null => {
    if (!process.client) return null
    const raw = localStorage.getItem(STORAGE_SESSION_KEY)
    if (!raw) return null
    try {
      const parsed = JSON.parse(raw)
      if (parsed?.access_token && parsed?.refresh_token) {
        return {
          access_token: parsed.access_token,
          refresh_token: parsed.refresh_token,
          expires_at: typeof parsed.expires_at === 'number' ? parsed.expires_at : null
        }
      }
    } catch {
      return null
    }
    return null
  }

  const loadStoredUser = (): Record<string, any> | null => {
    if (!process.client) return null
    const raw = localStorage.getItem(STORAGE_USER_KEY)
    if (!raw) return null
    try {
      return JSON.parse(raw)
    } catch {
      return null
    }
  }

  const loadStoredProfile = (): Record<string, any> | null => {
    if (!process.client) return null
    const raw = localStorage.getItem(STORAGE_PROFILE_KEY)
    if (!raw) return null
    try {
      return JSON.parse(raw)
    } catch {
      return null
    }
  }

  const assignStateFromSession = (
    newSession: Session | null,
    fallbackUser: Record<string, any> | null = null,
    fallbackProfile: Record<string, any> | undefined = undefined
  ) => {
    session.value = newSession
    user.value = newSession?.user ?? (fallbackUser as User | null) ?? null

    if (typeof fallbackProfile !== 'undefined') {
      profile.value = fallbackProfile
    } else if (!newSession) {
      profile.value = null
    }

    const profileToPersist = profile.value ?? null

    if (newSession?.access_token && newSession?.refresh_token) {
      persistLocalStorage({
        access_token: newSession.access_token,
        refresh_token: newSession.refresh_token,
        expires_at: newSession.expires_at ?? null
      }, user.value ?? fallbackUser ?? null, profileToPersist)
    } else if (!newSession) {
      persistLocalStorage(null, null, null)
    }

    return newSession
  }

  const isStoredSessionExpired = (stored: StoredSessionPayload | null) => {
    if (!stored) return true
    if (typeof stored.expires_at !== 'number') return false
    return stored.expires_at * 1000 < Date.now()
  }

  const setClientSessionFromTokens = async (
    payload: StoredSessionPayload | null,
    fallbackUser: Record<string, any> | null = null,
    fallbackProfile: Record<string, any> | undefined = undefined
  ) => {
    if (!payload?.access_token || !payload?.refresh_token) return null
    if (!process.client) return null

    try {
      const { data, error } = await supabase.auth.setSession({
        access_token: payload.access_token,
        refresh_token: payload.refresh_token
      })

      if (error) {
        console.error('Failed to set Supabase session', error)
        persistLocalStorage(null, null, null)
        return null
      }

      if (data.session) {
        assignStateFromSession(data.session, fallbackUser, fallbackProfile)
        return data.session
      }
    } catch (err) {
      console.error('Supabase setSession failed', err)
      persistLocalStorage(null, null, null)
    }

    return null
  }

  const fetchSessionFromServer = async () => {
    try {
      const response = await nuxtApp.$fetch('/api/auth/session') as {
        session: StoredSessionPayload | null
        user: Record<string, any> | null
        profile: Record<string, any> | null
      }

      if (response?.session?.access_token && response.session.refresh_token) {
        return await setClientSessionFromTokens(response.session, response.user, response.profile ?? null)
      }

      if (!response?.session) {
        persistLocalStorage(null, null, null)
      }
    } catch (error) {
      console.error('Failed to fetch session from server', error)
    }

    return null
  }

  const restoreFromLocalStorage = async () => {
    const storedSession = loadStoredSession()
    if (!storedSession) return null

    if (isStoredSessionExpired(storedSession)) {
      persistLocalStorage(null, null, null)
      return null
    }

    const storedUser = loadStoredUser()
    const storedProfile = loadStoredProfile()
    return await setClientSessionFromTokens(storedSession, storedUser, storedProfile ?? null)
  }

  const signUp = async (credentials: {
    email: string
    password: string
    name: string
    law_institution: string
    phone: string
    address: string
  }) => {
    const { data, error } = await supabase.auth.signUp({
      email: credentials.email,
      password: credentials.password,
      options: {
        data: {
          name: credentials.name,
          law_institution: credentials.law_institution,
          phone: credentials.phone,
          address: credentials.address
        }
      }
    })

    if (error) throw error

    if (data.session) {
      assignStateFromSession(data.session)
    }

    if (data.user) {
      user.value = data.user
    }

    return data
  }

  const signIn = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password
    })

    if (error) throw error

    if (data.session) {
      assignStateFromSession(data.session)
    }

    if (data.user) {
      user.value = data.user
    }

    return data
  }

  type OAuthOptions = {
    skipBrowserRedirect?: boolean
    redirectTo?: string
  }

  const signInWithOAuth = async (provider: 'google', options: OAuthOptions = {}) => {
    console.log('[OAuth] Calling signInWithOAuth with provider:', provider)

    const skipBrowserRedirect = options.skipBrowserRedirect ?? true

    const redirectUrl = (() => {
      if (!process.client) return undefined
      if (options.redirectTo) return options.redirectTo
      return `${window.location.origin}/api/auth/google/callback`
    })()

    if (redirectUrl) {
      console.log('[OAuth] Redirect URL:', redirectUrl)
    }

    const { data, error} = await supabase.auth.signInWithOAuth({
      provider,
      options: {
        redirectTo: redirectUrl,
        skipBrowserRedirect,
        queryParams: skipBrowserRedirect ? undefined : { prompt: 'consent' }
      }
    })

    console.log('[OAuth] signInWithOAuth response:', {
      hasData: !!data,
      hasError: !!error,
      provider: data?.provider,
      url: data?.url?.substring(0, 50) + '...'
    })

    // Diagnostic logging for PKCE cookie presence
    // Note: PKCE cookies might be HttpOnly and not visible via document.cookie
    if (process.client) {
      setTimeout(() => {
        const allCookies = document.cookie
        const cookieNames = allCookies ? allCookies.split(';').map(c => c.trim().split('=')[0]) : []
        const hasCodeVerifier = cookieNames.some(name => name.includes('code-verifier'))
        const hasFlowState = cookieNames.some(name => name.includes('flow'))

        console.log('[OAuth] PKCE cookies check after signInWithOAuth:', {
          hasCodeVerifier,
          hasFlowState,
          allCookieNames: cookieNames,
          totalCookies: cookieNames.length,
          note: 'HttpOnly cookies will not appear here - check Network tab instead'
        })
      }, 100) // Small delay to allow cookie setting
    }

    if (error) throw error
    return data
  }

  const signOut = async () => {
    persistLocalStorage(null, null, null)
    session.value = null
    user.value = null
    profile.value = null

    if (process.client) {
      try {
        await nuxtApp.$fetch('/api/auth/logout', { method: 'POST' })
      } catch (err) {
        console.warn('Failed to clear server session', err)
      }
    }

    try {
      await supabase.auth.signOut()
    } catch (error) {
      console.warn('Supabase signOut warning', error)
    }
  }

  const getSession = async () => {
    if (session.value && !isSessionExpired(session.value)) {
      return session.value
    }

    if (!process.client) {
      const serverSession = await fetchSessionFromServer()
      return serverSession
    }

    const { data, error } = await supabase.auth.getSession()
    if (error) throw error

    if (data.session && !isSessionExpired(data.session)) {
      return assignStateFromSession(data.session)
    }

    const restored = await restoreFromLocalStorage()
    if (restored) return restored

    return await fetchSessionFromServer()
  }

  const syncSessionFromTokens = async (
    sessionPayload: StoredSessionPayload | null,
    userPayload: Record<string, any> | null = null,
    profilePayload: Record<string, any> | null = null
  ) => {
    if (!sessionPayload) {
      persistLocalStorage(null, null, null)
      session.value = null
      user.value = null
      profile.value = null
      return null
    }

    return await setClientSessionFromTokens(sessionPayload, userPayload, profilePayload ?? undefined)
  }

  const isSessionExpired = (value: Session | null): boolean => {
    if (!value) return true
    return value.expires_at ? value.expires_at * 1000 < Date.now() : false
  }

  return {
    supabase,
    user,
    session,
    profile,
    signUp,
    signIn,
    signInWithOAuth,
    signOut,
    getSession,
    syncSessionFromTokens,
    isSessionExpired
  }
}
