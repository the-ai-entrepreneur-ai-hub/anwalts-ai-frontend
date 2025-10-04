/**
 * Google OAuth Authorization Handler
 * Redirects to backend OAuth endpoint or directly to Google OAuth
 */
export default defineEventHandler((event) => {
  const config = useRuntimeConfig()
  const query = getQuery(event)
  
  // Preserve redirect parameter if present
  const redirectParam = query.redirect ? `?redirect=${encodeURIComponent(query.redirect as string)}` : ''
  
  // Strategy 1: If backend base URL is configured, redirect to backend OAuth endpoint
  const backendBase = config.backendBase || process.env.BACKEND_BASE
  if (backendBase) {
    const backendUrl = `${backendBase}/auth/google/authorize${redirectParam}`
    console.log('[Google OAuth] Redirecting to backend:', backendUrl)
    return sendRedirect(event, backendUrl, 302)
  }
  
  // Strategy 2: Direct Google OAuth flow if credentials are configured
  const clientId = config.GOOGLE_CLIENT_ID || process.env.GOOGLE_CLIENT_ID
  const redirectUri = config.GOOGLE_REDIRECT_URI || process.env.GOOGLE_REDIRECT_URI
  
  if (clientId && redirectUri) {
    const scopes = [
      'openid',
      'https://www.googleapis.com/auth/userinfo.email',
      'https://www.googleapis.com/auth/userinfo.profile'
    ]
    
    const params = new URLSearchParams({
      client_id: clientId,
      redirect_uri: redirectUri,
      response_type: 'code',
      scope: scopes.join(' '),
      access_type: 'offline',
      prompt: 'consent',
      state: query.redirect ? String(query.redirect) : '/'
    })
    
    const googleAuthUrl = `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`
    console.log('[Google OAuth] Redirecting to Google:', googleAuthUrl)
    return sendRedirect(event, googleAuthUrl, 302)
  }
  
  // Strategy 3: Fallback - redirect to home with error parameter
  console.warn('[Google OAuth] No backend or credentials configured')
  return sendRedirect(event, '/?auth=google_not_configured', 302)
})