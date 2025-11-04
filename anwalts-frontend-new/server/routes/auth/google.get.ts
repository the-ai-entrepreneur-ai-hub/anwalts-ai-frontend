import { defineEventHandler, getQuery } from 'h3'
import { proxyBackendRedirect } from '~/server/utils/oauthProxy'

export default defineEventHandler(async (event) => {
  console.log('[OAuth] Proxying /auth/google to backend authorize endpoint')
  return proxyBackendRedirect(event, '/auth/google/authorize', getQuery(event))
})
