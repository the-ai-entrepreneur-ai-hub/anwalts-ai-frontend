import { defineEventHandler, sendRedirect, getQuery, setCookie } from 'h3'
import { createClient } from '@supabase/supabase-js'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const code = query.code as string
  const state = query.state as string
  
  console.log('[Supabase OAuth] Callback received:', { 
    hasCode: !!code, 
    hasState: !!state,
    stateLength: state?.length
  })
  
  if (!code) {
    // If no code, this might be a Supabase redirect - check for error
    const error = query.error as string
    const errorDescription = query.error_description as string
    
    if (error) {
      console.error('[Supabase OAuth] Error:', error, errorDescription)
      return sendRedirect(event, `/login?error=${encodeURIComponent(error)}`, 302)
    }
    
    // Otherwise redirect to backend OAuth endpoint
    const backendUrl = `http://localhost:8000/auth/google/callback${event.node.req.url?.split('/callback')[1] || ''}`
    console.log('[Supabase OAuth] Redirecting to backend:', backendUrl)
    return sendRedirect(event, backendUrl, 302)
  }
  
  try {
    // Initialize Supabase client
    const supabaseUrl = process.env.SUPABASE_URL || 'https://portal-anwalts.ai/supabase'
    const supabaseAnonKey = process.env.SUPABASE_ANON_KEY || 'sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH'
    
    const supabase = createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        autoRefreshToken: false,
        persistSession: false,
        detectSessionInUrl: false,
        flowType: 'pkce'
      }
    })
    
    // If this is a Supabase state token, exchange it
    if (state && state.includes('eyJ')) {
      // This looks like a Supabase state token - handle via Supabase
      const { data, error } = await supabase.auth.exchangeCodeForSession(code)
      
      if (error) {
        console.error('[Supabase OAuth] Session exchange error:', error)
        // Fallback to backend
        const backendUrl = `http://localhost:8000/auth/google/callback?code=${code}&state=${state}`
        return sendRedirect(event, backendUrl, 302)
      }
      
      if (data?.session) {
        // Set session cookies
        setCookie(event, 'sb-access-token', data.session.access_token, {
          httpOnly: true,
          secure: true,
          sameSite: 'lax',
          path: '/',
          maxAge: 60 * 60 * 24 * 7 // 7 days
        })
        
        setCookie(event, 'sb-refresh-token', data.session.refresh_token, {
          httpOnly: true,
          secure: true,
          sameSite: 'lax',
          path: '/',
          maxAge: 60 * 60 * 24 * 30 // 30 days
        })
        
        console.log('[Supabase OAuth] Session created for user:', data.session.user?.email)
        return sendRedirect(event, '/dashboard', 302)
      }
    }
    
    // Otherwise proxy to backend
    const backendUrl = `http://localhost:8000/auth/google/callback?code=${code}&state=${state || ''}`
    console.log('[Supabase OAuth] Proxying to backend:', backendUrl)
    return sendRedirect(event, backendUrl, 302)
    
  } catch (error: any) {
    console.error('[Supabase OAuth] Callback error:', error)
    
    // Last resort: try backend directly
    const backendUrl = `http://localhost:8000/auth/google/callback?code=${code}&state=${state || ''}`
    return sendRedirect(event, backendUrl, 302)
  }
})
