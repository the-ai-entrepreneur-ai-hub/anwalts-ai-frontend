import { defineEventHandler, sendRedirect, getQuery } from 'h3'
import { proxyBackendResponse } from '~/server/utils/oauthProxy'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const code = query.code as string | undefined
  const error = query.error as string | undefined

  console.log('[Google OAuth] Callback received:', {
    hasCode: !!code,
    hasError: !!error
  })

  if (error) {
    console.error('[Google OAuth] Error from provider:', error, query.error_description)
    return sendRedirect(event, '/?auth_error=' + encodeURIComponent(error), 302)
  }

  if (!code) {
    console.error('[Google OAuth] No code in callback')
    return sendRedirect(event, '/?auth_error=no_code', 302)
  }

  return proxyBackendResponse(event, '/auth/google/callback', query)
})
