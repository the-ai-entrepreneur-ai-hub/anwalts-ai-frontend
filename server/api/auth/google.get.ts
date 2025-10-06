import { defineEventHandler, sendRedirect } from 'h3'

export default defineEventHandler(async (event) => {
  console.log('[OAuth] Proxying /api/auth/google to backend authorize endpoint')
  
  // Always use backend OAuth (no Supabase)
  return sendRedirect(event, 'http://backend:8000/auth/google/authorize', 302)
})
