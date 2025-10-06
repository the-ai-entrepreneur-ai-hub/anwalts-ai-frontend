import { defineEventHandler, proxyRequest, getQuery, getCookie } from 'h3'

// This middleware proxies all /api/* requests to the backend FastAPI server
// EXCEPT for Nuxt's own server API routes that are explicitly defined

export default defineEventHandler(async (event) => {
  const path = event.node.req.url || ''
  
  // Only handle /api/* paths
  if (!path.startsWith('/api/')) {
    return
  }

  // Skip if this is a Nuxt server API route that exists
  // Check for specific routes that should NOT be proxied
  const nuxtHandledRoutes = [
    '/api/profile',
    '/api/dashboard/summary'
  ]
  
  // These routes should be handled by Nuxt, not proxied
  const nuxtAuthRoutes = [
    '/api/auth/signin',
    '/api/auth/signup',
    '/api/auth/session',
    '/api/auth/logout',
    '/api/auth/login',
    '/api/auth/register',
    '/api/auth/register-full',
    '/api/auth/status',
    '/api/auth/google/callback',
    '/api/auth/google/authorize',
    '/api/auth/google'
  ]
  
  // Check if this is a Nuxt-handled auth route
  const isNuxtAuthRoute = nuxtAuthRoutes.some(route => path === route || path.startsWith(route + '?'))
  
  const shouldSkip = isNuxtAuthRoute || nuxtHandledRoutes.some(route => path.startsWith(route))
  
  if (shouldSkip) {
    return // Let Nuxt handle these routes
  }

  // Proxy everything else to the backend
  const backendBase = process.env.BACKEND_BASE || 'http://localhost:8000'
  const targetUrl = `${backendBase}${path}`
  
  console.log(`[API Proxy] Proxying ${path} to ${targetUrl}`)
  
  try {
    // Get headers from the original request
    const headers: Record<string, string> = {}
    const originalHeaders = event.node.req.headers
    
    // Forward important headers
    if (originalHeaders.authorization) {
      headers.authorization = originalHeaders.authorization as string
    }
    if (originalHeaders['content-type']) {
      headers['content-type'] = originalHeaders['content-type'] as string
    }
    if (originalHeaders.cookie) {
      headers.cookie = originalHeaders.cookie as string
    }
    // Forward the original host header for OAuth
    if (originalHeaders.host) {
      headers['x-forwarded-host'] = originalHeaders.host as string
    }
    
    // Make the proxy request
    return await proxyRequest(event, targetUrl, {
      headers,
      // Pass through query parameters
      query: getQuery(event)
    })
  } catch (error) {
    console.error(`[API Proxy] Error proxying to backend:`, error)
    throw error
  }
})
