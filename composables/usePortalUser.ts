import { useState, useNuxtApp } from '#imports'

interface PortalUser {
  name?: string
  email?: string
  role?: string
}

const resolveStoredUser = (): PortalUser | null => {
  if (!process.client) return null
  try {
    const raw = localStorage.getItem('auth_user') || localStorage.getItem('anwalts_user')
    return raw ? JSON.parse(raw) : null
  } catch (_) {
    return null
  }
}

const hasStoredAuthEvidence = (): boolean => {
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

export const usePortalUser = () => {
  const user = useState<PortalUser | null>('portal-user', () => null)
  const status = useState<'idle' | 'loading' | 'loaded'>('portal-user-status', () => 'idle')
  const nuxtApp = useNuxtApp()

  const loadUser = async (): Promise<PortalUser | null> => {
    if (!process.client) return user.value
    if (status.value === 'loading') return user.value
    if (status.value === 'loaded' && user.value) return user.value

    status.value = 'loading'

    const stored = resolveStoredUser()
    if (stored) {
      user.value = stored
    }

    if (!user.value) {
      try {
        const stackApp = (nuxtApp as any)?.$stackAuth
        if (stackApp?.getUser) {
          const stackUser = await stackApp.getUser({ or: 'return-null' })
          if (stackUser) {
            user.value = {
              name: stackUser.displayName || stackUser.primaryEmail,
              email: stackUser.primaryEmail,
              role: stackUser.role || stackUser.projectRole || 'Benutzer'
            }
          }
        }
      } catch (error) {
        console.warn('Stack Auth lookup failed', error)
      }
    }

    if (!user.value) {
      try {
        const response = await fetch('/api/auth/me', { credentials: 'include' })
        if (response.ok) {
          const payload = await response.json().catch(() => null)
          if (payload?.user) {
            user.value = payload.user
          }
        }
      } catch (error) {
        console.warn('Portal user fetch failed', error)
      }
    }

    status.value = 'loaded'
    return user.value
  }

  return {
    user,
    loadUser,
    hasStoredAuthEvidence,
  }
}
