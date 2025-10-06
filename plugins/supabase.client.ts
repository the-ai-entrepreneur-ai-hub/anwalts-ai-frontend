import { createClient } from '@supabase/supabase-js'

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  
  const supabaseUrl = config.public.supabaseUrl || 'https://portal-anwalts.ai/supabase'
  const supabaseKey = config.public.supabaseKey || 'sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH'
  
  const supabase = createClient(supabaseUrl, supabaseKey, {
    auth: {
      autoRefreshToken: true,
      persistSession: true,
      detectSessionInUrl: true,
      flowType: 'pkce',
      storage: {
        getItem: (key: string) => {
          if (process.client) {
            return localStorage.getItem(key)
          }
          return null
        },
        setItem: (key: string, value: string) => {
          if (process.client) {
            localStorage.setItem(key, value)
          }
        },
        removeItem: (key: string) => {
          if (process.client) {
            localStorage.removeItem(key)
          }
        }
      }
    }
  })
  
  // Handle auth state changes
  if (process.client) {
    supabase.auth.onAuthStateChange((event, session) => {
      console.log('[Supabase] Auth state changed:', event, session?.user?.email)
      
      if (event === 'SIGNED_IN' && session) {
        // Store session in localStorage for persistence
        localStorage.setItem('supabase.auth.token', JSON.stringify(session))
        
        // Redirect to dashboard after successful sign in
        if (window.location.pathname === '/login' || window.location.pathname === '/') {
          window.location.href = '/dashboard'
        }
      } else if (event === 'SIGNED_OUT') {
        // Clear session
        localStorage.removeItem('supabase.auth.token')
        
        // Redirect to login
        if (window.location.pathname !== '/login' && window.location.pathname !== '/') {
          window.location.href = '/login'
        }
      }
    })
  }
  
  return {
    provide: {
      supabase
    }
  }
})
