import { describe, expect, beforeEach, afterEach, vi, it } from 'vitest'
import jwt from 'jsonwebtoken'

vi.mock('~/server/utils/sessionCookie', () => ({
  readSupabaseSessionCookie: vi.fn(() => null)
}))

const requestHeaders = new Map<string, string>()
const cookieJar = new Map<string, string>()

vi.mock('h3', async () => {
  const actual = await vi.importActual<any>('h3')
  return {
    ...actual,
    createError: ({ statusCode, statusMessage }: { statusCode: number; statusMessage: string }) => {
      const error = new Error(statusMessage)
      ;(error as any).statusCode = statusCode
      return error
    },
    getRequestHeader: (_event: any, name: string) => requestHeaders.get(name.toLowerCase()) ?? null,
    getCookie: (_event: any, name: string) => cookieJar.get(name) ?? null
  }
})

describe('resolveBackendAuthHeader', () => {
  const event = {} as any
  const purpose = 'email-test'
  let resolveBackendAuthHeader: (event: any, purpose: string) => Promise<string>

  beforeEach(() => {
    process.env.JWT_SECRET_KEY = 'test-secret'
    requestHeaders.clear()
    cookieJar.clear()
    ;(global as any).useSupabaseServer = vi.fn()
    vi.resetModules()
  })

  afterEach(() => {
    delete process.env.JWT_SECRET_KEY
    vi.resetAllMocks()
  })

  it('accepts a forwarded Authorization bearer token', async () => {
    ;({ resolveBackendAuthHeader } = await import('~/server/utils/backendAuth'))
    const token = jwt.sign({ sub: 'user-123', email: 'forward@example.com' }, 'test-secret', { algorithm: 'HS256' })
    requestHeaders.set('authorization', `Bearer ${token}`)

    const header = await resolveBackendAuthHeader(event, purpose)
    expect(header).toBe(`Bearer ${token}`)
    expect((global as any).useSupabaseServer).not.toHaveBeenCalled()
  })

  it('accepts a forwarded x-portal-auth token when Authorization header missing', async () => {
    ;({ resolveBackendAuthHeader } = await import('~/server/utils/backendAuth'))
    const token = jwt.sign({ sub: 'user-456', email: 'portal@example.com' }, 'test-secret', { algorithm: 'HS256' })
    requestHeaders.set('x-portal-auth', token)

    const header = await resolveBackendAuthHeader(event, purpose)
    expect(header).toBe(`Bearer ${token}`)
  })

  it('falls back to auth_token cookie when no forwarded artefact present', async () => {
    ;({ resolveBackendAuthHeader } = await import('~/server/utils/backendAuth'))
    cookieJar.set('auth_token', 'cookie-token-abc')
    const header = await resolveBackendAuthHeader(event, purpose)
    expect(header).toBe('Bearer cookie-token-abc')
  })

  it('throws when no authentication artefact is available', async () => {
    ;({ resolveBackendAuthHeader } = await import('~/server/utils/backendAuth'))
    await expect(resolveBackendAuthHeader(event, purpose)).rejects.toMatchObject({ statusCode: 401 })
  })
})
