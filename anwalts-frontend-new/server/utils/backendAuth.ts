import { createError, getCookie, getRequestHeader } from 'h3'
import jwt from 'jsonwebtoken'
import type { H3Event } from 'h3'
import { readSupabaseSessionCookie } from '~/server/utils/sessionCookie'

// Development fallback keeps local DX working without leaking production secrets
const FALLBACK_JWT_SECRET = process.env.NODE_ENV === 'development' ? 'dev-only-jwt-secret-change-me' : undefined

export async function resolveBackendAuthHeader(event: H3Event, purpose: string): Promise<string> {
  const jwtSecret = process.env.JWT_SECRET_KEY || FALLBACK_JWT_SECRET
  const acceptForwardedBearer = (rawValue: string | null | undefined, source: string): string | null => {
    if (!rawValue) return null
    const value = rawValue.trim()
    if (!value) return null
    const bearerValue = value.toLowerCase().startsWith('bearer ') ? value : `Bearer ${value}`
    const token = bearerValue.split(' ')[1]
    if (!token || !jwtSecret) {
      if (!jwtSecret) {
        console.warn(`[Auth:${purpose}] Cannot verify ${source} token because JWT secret is not configured`)
      }
      return null
    }
    try {
      jwt.verify(token, jwtSecret, { algorithms: ['HS256'] })
      console.info(`[Auth:${purpose}] Accepted forwarded bearer token via ${source}`)
      return `Bearer ${token}`
    } catch (err: any) {
      console.warn(`[Auth:${purpose}] Forwarded ${source} token rejected: ${err?.message || err}`)
      return null
    }
  }

  const directAuthHeader = getRequestHeader(event, 'authorization')
  const forwardedPortalHeader = getRequestHeader(event, 'x-portal-auth')

  let authHeader: string | null = acceptForwardedBearer(directAuthHeader, 'authorization header')
  if (!authHeader) {
    authHeader = acceptForwardedBearer(forwardedPortalHeader, 'x-portal-auth header')
  }

  const sessionCookie = readSupabaseSessionCookie(event)

  if (!authHeader && sessionCookie?.access_token) {
    const supabase = useSupabaseServer(event)
    const { data: userData, error } = await supabase.auth.getUser(sessionCookie.access_token)
    if (!error && userData.user) {
      console.log(`[Auth:${purpose}] Authenticated via Supabase: ${userData.user.email} (${userData.user.id})`)
      if (!jwtSecret) {
        throw createError({ statusCode: 500, statusMessage: 'JWT secret not configured' })
      }
      const backendToken = jwt.sign(
        { sub: userData.user.id, email: userData.user.email, type: 'access' },
        jwtSecret,
        { expiresIn: '1h', algorithm: 'HS256' }
      )
      authHeader = `Bearer ${backendToken}`
    } else {
      console.warn(`[Auth:${purpose}] Supabase session invalid, falling back to backend auth cookie`)
    }
  }

  if (!authHeader) {
    const backendCookieToken = getCookie(event, 'auth_token') || getCookie(event, 'sid')
    if (backendCookieToken) {
      console.log(`[Auth:${purpose}] Using backend auth cookie (auth_token/sid)`)
      authHeader = `Bearer ${backendCookieToken}`
    }
  }

  if (!authHeader) {
    console.error(`[Auth:${purpose}] No valid session artefact found (authorization header, Supabase, auth_token, sid)`)
    throw createError({ statusCode: 401, statusMessage: 'Authentication required - please log in' })
  }

  return authHeader
}
