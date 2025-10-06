import { defineEventHandler, sendRedirect } from 'h3'

export default defineEventHandler(async (event) => {
  console.log('[OAuth] Proxying /api/auth/google/authorize to backend')
  
  // Proxy to backend OAuth authorize endpoint
  return sendRedirect(event, 'http://backend:8000/auth/google/authorize', 302)
})
