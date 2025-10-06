import { ref, computed } from 'vue'
import { useNuxtApp } from '#app'

export const useAuthUser = () => {
  const nuxtApp = useNuxtApp()
  const currentUser = useState<any>('current-user', () => null)

  const userName = computed(() => {
    if (!currentUser.value) return 'Benutzer'
    return currentUser.value.name || currentUser.value.email || 'Benutzer'
  })

  const userRole = computed(() => {
    if (!currentUser.value || !currentUser.value.role) return 'Eingeloggt'
    const role = currentUser.value.role
    return role.charAt(0).toUpperCase() + role.slice(1)
  })

  const userInitials = computed(() => {
    const name = userName.value
    if (name === 'Benutzer') return 'U'
    const parts = name.split(' ')
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase()
    }
    return name.substring(0, 2).toUpperCase()
  })

  const resolveStoredUser = () => {
    if (!process.client) return null
    try {
      const raw = localStorage.getItem('auth_user') || localStorage.getItem('anwalts_user')
      return raw ? JSON.parse(raw) : null
    } catch (_) {
      return null
    }
  }

  const hasStoredAuthEvidence = () => {
    if (!process.client) return false
    try {
      if (
        localStorage.getItem('anwalts_auth_token') ||
        localStorage.getItem('auth_user') ||
        localStorage.getItem('anwalts_user') ||
        localStorage.getItem('auth_success') === 'true' ||
        localStorage.getItem('access_token') ||
        localStorage.getItem('token') ||
        localStorage.getItem('sat')
      ) {
        return true
      }
      if (typeof document !== 'undefined' && document.cookie) {
        return /(anwalts_auth_token|access_token|token|sat)=/.test(document.cookie)
      }
    } catch (_) {}
    return false
  }

  const loadUser = async () => {
    if (!currentUser.value) {
      const stored = resolveStoredUser()
      if (stored) {
        currentUser.value = stored
      }
    }

    try {
      const stackApp = nuxtApp.$stackAuth
      if (!currentUser.value && stackApp?.getUser) {
        const stackUser = await stackApp.getUser({ or: 'return-null' })
        if (stackUser) {
          currentUser.value = {
            name: stackUser.displayName || stackUser.primaryEmail,
            email: stackUser.primaryEmail,
            role: stackUser.role || stackUser.projectRole || 'Benutzer'
          }
        }
      }
    } catch (error) {
      console.warn('Unable to resolve Stack Auth user', error)
    }

    if (!currentUser.value) {
      try {
        const response = await fetch('/api/auth/me', { credentials: 'include' })
        if (response.ok) {
          const payload = await response.json().catch(() => null)
          if (payload?.user) {
            currentUser.value = payload.user
          }
        }
      } catch (error) {
        console.warn('Fallback /api/auth/me failed', error)
      }
    }

    return currentUser.value
  }

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem('access_token') || localStorage.getItem('token') || localStorage.getItem('sat')
      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include',
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      })
    } catch (_) {}

    // Clear all auth data
    try {
      localStorage.removeItem('access_token')
      localStorage.removeItem('token')
      localStorage.removeItem('sat')
      localStorage.removeItem('auth_user')
      localStorage.removeItem('anwalts_user')
      localStorage.removeItem('supabase.auth.token')
      localStorage.removeItem('supabase-session')
      document.cookie = 'access_token=; Max-Age=0; Path=/; Secure; SameSite=Lax'
      document.cookie = 'token=; Max-Age=0; Path=/; Secure; SameSite=Lax'
      document.cookie = 'sat=; Max-Age=0; Path=/; Secure; SameSite=Lax'
    } catch (_) {}

    window.location.replace('/')
  }

  return {
    currentUser,
    userName,
    userRole,
    userInitials,
    loadUser,
    handleLogout,
    hasStoredAuthEvidence
  }
}
