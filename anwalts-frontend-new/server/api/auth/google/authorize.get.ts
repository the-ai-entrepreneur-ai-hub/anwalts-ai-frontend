import { defineEventHandler, getQuery } from 'h3'
import { proxyBackendRedirect } from '~/server/utils/oauthProxy'

export default defineEventHandler(async (event) => {
  console.log('[OAuth] Proxying /api/auth/google/authorize via backend')
  return proxyBackendRedirect(event, '/auth/google/authorize', getQuery(event))
})
