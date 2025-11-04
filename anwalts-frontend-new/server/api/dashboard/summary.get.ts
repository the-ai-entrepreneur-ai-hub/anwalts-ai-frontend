/**
 * Dashboard Summary API Route
 * 
 * This proxies dashboard requests to the Python backend which has access
 * to the PostgreSQL database containing all documents, users, and analytics.
 * 
 * Updated: 2025-11-03 - Changed from Supabase to PostgreSQL backend proxy
 */

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const backendBase = config.backendBase || 'http://backend:8000'

  // Get auth token from request headers or cookies
  const authHeader = getRequestHeader(event, 'authorization')
  const cookies = parseCookies(event)
  
  let authToken = null
  if (authHeader && authHeader.startsWith('Bearer ')) {
    authToken = authHeader.substring(7)
  } else {
    // Try various cookie names
    authToken = cookies.auth_token || cookies.access_token || cookies.token || cookies.sat
  }

  if (!authToken) {
    console.error('[Dashboard] No auth token found in request')
    throw createError({
      statusCode: 401,
      statusMessage: 'Authentication required'
    })
  }

  try {
    console.log('[Dashboard] Proxying request to backend:', `${backendBase}/api/dashboard/summary`)
    
    // Proxy request to Python backend with auth token
    const response = await $fetch(`${backendBase}/api/dashboard/summary`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      }
    })

    console.log('[Dashboard] ? Successfully fetched dashboard data from backend')
    return response

  } catch (error: any) {
    console.error('[Dashboard] ? Backend request failed:', error.message || error)
    
    // If backend returns an error, pass it through
    if (error.statusCode) {
      throw createError({
        statusCode: error.statusCode,
        statusMessage: error.message || 'Backend error'
      })
    }

    throw createError({
      statusCode: 500,
      statusMessage: 'Dashboard summary unavailable'
    })
  }
})
