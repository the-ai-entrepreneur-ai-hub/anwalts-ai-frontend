import { getCookie, defineEventHandler } from 'h3'
import { buildBackendUrl } from '~/server/utils/backend'

type SessionPayload = {
  access_token: string | null
  refresh_token: string | null
  expires_at: number | null
}

type SessionResponse = {
  session: SessionPayload | null
  user: Record<string, any> | null
  profile: Record<string, any> | null
}

export default defineEventHandler<SessionResponse>(async (event) => {
  const token =
    getCookie(event, 'auth_token') ||
    getCookie(event, 'anwalts_auth_token') ||
    getCookie(event, 'sat') ||
    getCookie(event, 'sid')

  if (!token) {
    return {
      session: null,
      user: null,
      profile: null
    }
  }

  try {
    const backendUrl = buildBackendUrl(event, '/api/auth/me')
    const backendResponse = await fetch(backendUrl, {
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: 'application/json'
      }
    })

    if (!backendResponse.ok) {
      return {
        session: {
          access_token: token,
          refresh_token: null,
          expires_at: null
        },
        user: null,
        profile: null
      }
    }

    const user = await backendResponse.json().catch(() => null)

    return {
      session: {
        access_token: token,
        refresh_token: null,
        expires_at: null
      },
      user: user && typeof user === 'object' ? user : null,
      profile: null
    }
  } catch (error) {
    console.error('[Auth Session] Failed to load session from backend', error)
    return {
      session: {
        access_token: token,
        refresh_token: null,
        expires_at: null
      },
      user: null,
      profile: null
    }
  }
})

