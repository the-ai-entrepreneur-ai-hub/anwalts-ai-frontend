import { deleteCookie, getCookie, setCookie } from 'h3'
import type { H3Event } from 'h3'
import type { Session } from '@supabase/supabase-js'

const COOKIE_NAME = 'supabase-session'
const COOKIE_MAX_AGE = 60 * 60 * 24 * 7 // 7 days

const cookieOptions = {
  httpOnly: true,
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'lax' as const,
  path: '/',
  maxAge: COOKIE_MAX_AGE
}

type SessionPayload = Pick<Session, 'access_token' | 'refresh_token' | 'expires_at'> | {
  access_token?: string | null
  refresh_token?: string | null
  expires_at?: number | null
}

export const setSupabaseSessionCookie = (event: H3Event, session: SessionPayload | null) => {
  if (!session?.access_token || !session?.refresh_token) {
    return
  }

  const payload = {
    access_token: session.access_token,
    refresh_token: session.refresh_token,
    expires_at: session.expires_at ?? null
  }

  setCookie(event, COOKIE_NAME, JSON.stringify(payload), cookieOptions)
}

export const clearSupabaseSessionCookie = (event: H3Event) => {
  deleteCookie(event, COOKIE_NAME)
}

export const readSupabaseSessionCookie = (event: H3Event) => {
  const value = getCookie(event, COOKIE_NAME)
  if (!value) return null

  try {
    return JSON.parse(value) as SessionPayload
  } catch {
    return null
  }
}
