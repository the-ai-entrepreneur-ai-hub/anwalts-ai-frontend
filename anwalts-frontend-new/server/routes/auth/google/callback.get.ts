import { defineEventHandler, getQuery, sendRedirect } from 'h3'
import { proxyBackendResponse } from '~/server/utils/oauthProxy'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const code = query.code as string | undefined
  const error = query.error as string | undefined

  console.log('[OAuth] Proxying /auth/google/callback to backend', {
    hasCode: !!code,
    hasError: !!error
  })

  if (error) {
    console.error('[OAuth] Provider returned error during callback:', error, query.error_description)
    return sendRedirect(event, '/?auth_error=' + encodeURIComponent(error), 302)
  }

  if (!code) {
    console.error('[OAuth] Missing authorization code during callback')
    return sendRedirect(event, '/?auth_error=no_code', 302)
  }

  return proxyBackendResponse(event, '/auth/google/callback', query)
})
