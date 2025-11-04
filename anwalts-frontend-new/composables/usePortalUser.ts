import { useState, useNuxtApp } from '#imports'

interface PortalUser {
  name?: string
  email?: string
  role?: string
  profile_picture?: string | null
}

const resolveAuthToken = (): string | null => {
  if (!process.client) return null
  const storageKeys = ['auth_token', 'anwalts_auth_token', 'access_token', 'token', 'sat']
  for (const key of storageKeys) {
    try {
      const value = localStorage.getItem(key)
      if (value) {
        return value
      }
    } catch (_) {}
  }
  try {
    if (typeof document !== 'undefined' && document.cookie) {
      const match = document.cookie
        .split(';')
        .map(entry => entry.trim())
        .find(entry =>
          entry.startsWith('auth_token=') ||
          entry.startsWith('anwalts_auth_token=') ||
          entry.startsWith('sat=')
        )
      if (match) {
        const [, rawValue] = match.split('=')
        return decodeURIComponent(rawValue || '')
      }
    }
  } catch (_) {}
  return null
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
      localStorage.getItem('auth_token') ||
      localStorage.getItem('token') ||
      localStorage.getItem('sat')
    ) {
      return true
    }
    if (typeof document !== 'undefined' && document.cookie) {
      return /(anwalts_auth_token|auth_token|access_token|token|sat)=/.test(document.cookie)
    }
  } catch (_) {}
  return false
}

export const usePortalUser = () => {
  const user = useState<PortalUser | null>('portal-user', () => null)
  const status = useState<'idle' | 'loading' | 'loaded'>('portal-user-status', () => 'idle')
  const nuxtApp = useNuxtApp()

  const loadUser = async (options?: { force?: boolean }): Promise<PortalUser | null> => {
    const force = Boolean(options?.force)
    if (!process.client) return user.value

    const stored = resolveStoredUser()
    const storedEmail = stored?.email?.toLowerCase() || null
    const currentEmail = user.value?.email?.toLowerCase() || null

    if (!force && status.value === 'loading') {
      return user.value
    }
    if (
      !force &&
      status.value === 'loaded' &&
      user.value &&
      (
        (!storedEmail && !currentEmail) ||
        (storedEmail && currentEmail && storedEmail === currentEmail)
      )
    ) {
      return user.value
    }

    status.value = 'loading'

    if (stored && (!currentEmail || storedEmail !== currentEmail)) {
      user.value = stored
    }

    try {
      const stackApp = (nuxtApp as any)?.$stackAuth
      if (stackApp?.getUser) {
        const stackUser = await stackApp.getUser({ or: 'return-null' })
        if (stackUser) {
          user.value = {
            name: stackUser.displayName || stackUser.primaryEmail,
            email: stackUser.primaryEmail,
            role: stackUser.role || stackUser.projectRole || 'Benutzer',
            profile_picture: stackUser.profile_picture || null
          }
        }
      }
    } catch (error) {
      console.warn('Stack Auth lookup failed', error)
    }

    try {
      const headers: Record<string, string> = { Accept: 'application/json' }
      const token = resolveAuthToken()
      if (token) {
        headers.Authorization = `Bearer ${token}`
      }
      const response = await fetch('/api/auth/me', {
        headers,
        credentials: 'include'
      })
      if (response.ok) {
        const payload = await response.json().catch(() => null)
        const normalized =
          payload && typeof payload === 'object'
            ? (payload.user && typeof payload.user === 'object' ? payload.user : payload)
            : null
        if (normalized && (normalized.email || normalized.name)) {
          user.value = {
            name: normalized.name,
            email: normalized.email,
            role: normalized.role,
            profile_picture: normalized.profile_picture || null
          }
        }
      } else if (response.status === 401 || response.status === 403) {
        user.value = null
        try {
          localStorage.removeItem('auth_user')
          localStorage.removeItem('anwalts_user')
        } catch (_) {}
      }
    } catch (error) {
      console.warn('Portal user fetch failed', error)
    }

    status.value = 'loaded'

    if (process.client) {
      try {
        if (user.value) {
          const serialized = JSON.stringify(user.value)
          localStorage.setItem('auth_user', serialized)
          localStorage.setItem('anwalts_user', serialized)
        } else {
          localStorage.removeItem('auth_user')
          localStorage.removeItem('anwalts_user')
        }
      } catch (_) {}
    }

    return user.value
  }

  return {
    user,
    loadUser,
    hasStoredAuthEvidence,
  }
}
