import { createServerClient } from '@supabase/ssr'
import type { H3Event } from 'h3'
import { deleteCookie, getCookie, setCookie, getRequestURL } from 'h3'

const getCookieDomain = (event: H3Event) => {
  const fromEnv = process.env.SUPABASE_COOKIE_DOMAIN?.trim()
  if (fromEnv) return fromEnv

  try {
    const url = getRequestURL(event)
    const host = url?.hostname || ''
    if (!host || host === 'localhost' || host === '127.0.0.1') {
      return undefined
    }
    return host
  } catch {
    return undefined
  }
}

export const useSupabaseServer = (event: H3Event) => {
  const config = useRuntimeConfig()

  const supabaseUrl = config.public.supabaseUrl
  // Use the ANON public key for SSR auth flows so storageKey/cookies match the browser client
  const supabaseAnonKey = config.public.supabaseKey

  if (!supabaseUrl || !supabaseAnonKey) {
    throw new Error('Supabase URL and Service Key must be configured')
  }

  const secure = process.env.NODE_ENV === 'production'
  const sameSite = secure ? 'none' : 'lax'
  const cookieDomain = getCookieDomain(event)

  const sharedCookieOptions: Record<string, any> = {
    path: '/',
    sameSite,
    secure
  }

  if (cookieDomain) {
    sharedCookieOptions.domain = cookieDomain
  }

  (event.context as any)._supabaseCookieOptions = sharedCookieOptions

  return createServerClient(supabaseUrl, supabaseAnonKey, {
    auth: {
      flowType: 'pkce',
      detectSessionInUrl: false
    },
    cookieOptions: {
      ...sharedCookieOptions
    },
    cookies: {
      get: (key: string) => getCookie(event, key),
      set: (key: string, value: string, options: any) => {
        const computedOptions = {
          ...sharedCookieOptions,
          ...(options || {})
        }

        if (!cookieDomain && computedOptions.domain) {
          delete computedOptions.domain
        }

        if (!secure && computedOptions.sameSite === 'none') {
          computedOptions.sameSite = 'lax'
        }

        if (key.endsWith('-code-verifier')) {
          (event.context as any)._supabaseCookiePrefix = key.replace(/-code-verifier$/, '')
        }

        console.log('[Supabase Cookies] set', key, {
          hasValue: Boolean(value),
          sameSite: computedOptions.sameSite,
          domain: computedOptions.domain,
          secure: computedOptions.secure
        })

        setCookie(event, key, value, {
          ...computedOptions,
          httpOnly: options?.httpOnly ?? true
        })
      },
      remove: (key: string, options: any) => {
        const computedOptions = {
          ...sharedCookieOptions,
          ...(options || {})
        }

        if (!cookieDomain && computedOptions.domain) {
          delete computedOptions.domain
        }

        if (!secure && computedOptions.sameSite === 'none') {
          computedOptions.sameSite = 'lax'
        }

        deleteCookie(event, key, {
          ...computedOptions
        })
      }
    }
  })
}
