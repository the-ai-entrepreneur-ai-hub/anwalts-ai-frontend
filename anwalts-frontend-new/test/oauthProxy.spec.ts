import { describe, it, expect, beforeAll, afterAll } from 'vitest'
import http from 'node:http'
import { createApp, eventHandler, toNodeListener } from 'h3'
import { proxyBackendRedirect } from '../server/utils/oauthProxy'

function startBackend(port: number) {
  const srv = http.createServer((req, res) => {
    if (req.url?.startsWith('/auth/google/authorize')) {
      // Simulate backend authorize redirect with cookies the frontend must forward
      res.statusCode = 302
      res.setHeader('Location', 'https://accounts.google.com/o/oauth2/v2/auth?fake=1')
      res.setHeader('Set-Cookie', [
        'oauth_flow_mode=gmail; Path=/; HttpOnly; Secure; SameSite=Lax',
        'email_link_uid=12345; Path=/; HttpOnly; Secure; SameSite=Lax',
      ])
      res.end()
      return
    }
    res.statusCode = 404
    res.end('not found')
  })
  return new Promise<http.Server>((resolve) => srv.listen(port, () => resolve(srv)))
}

function startFrontend(port: number) {
  const app = createApp()
  // minimal route that proxies to backend authorize endpoint
  app.use(
    '/api/auth/google/authorize',
    eventHandler((event) => proxyBackendRedirect(event, '/auth/google/authorize'))
  )
  const srv = http.createServer(toNodeListener(app))
  return new Promise<http.Server>((resolve) => srv.listen(port, () => resolve(srv)))
}

describe('oauthProxy cookie forwarding', () => {
  const backendPort = 18080
  const frontendPort = 19090
  let backendSrv: http.Server
  let frontendSrv: http.Server

  beforeAll(async () => {
    process.env.BACKEND_BASE = `http://127.0.0.1:${backendPort}`
    backendSrv = await startBackend(backendPort)
    frontendSrv = await startFrontend(frontendPort)
  })

  afterAll(async () => {
    await new Promise<void>((resolve) => backendSrv.close(() => resolve()))
    await new Promise<void>((resolve) => frontendSrv.close(() => resolve()))
  })

  it('forwards Set-Cookie headers from backend during redirect', async () => {
    const res = await fetch(`http://127.0.0.1:${frontendPort}/api/auth/google/authorize?mode=gmail`, {
      redirect: 'manual'
    })
    // sendRedirect should keep status code from backend (302)
    expect(res.status).toBe(302)
    const loc = res.headers.get('location')
    expect(loc).toBeTruthy()

    const setCookies = (typeof (res.headers as any).getSetCookie === 'function')
      ? (res.headers as any).getSetCookie()
      : (res.headers.get('set-cookie') ? [res.headers.get('set-cookie') as string] : [])

    expect(setCookies.length).toBeGreaterThan(0)
    const serialized = Array.isArray(setCookies) ? setCookies.join('\n') : String(setCookies)
    expect(serialized).toContain('oauth_flow_mode=gmail')
    expect(serialized).toContain('email_link_uid=')
  })
})

