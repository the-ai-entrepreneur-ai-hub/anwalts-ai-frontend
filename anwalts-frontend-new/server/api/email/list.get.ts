import { defineEventHandler, getQuery, createError } from 'h3'
import { buildBackendUrl } from '~/server/utils/backend'
import { resolveBackendAuthHeader } from '~/server/utils/backendAuth'

export default defineEventHandler(async (event) => {
  const authHeader = await resolveBackendAuthHeader(event, 'email-list')
  const query = getQuery(event)
  const backendUrl = new URL(buildBackendUrl(event, '/api/email/list'))

  const accountId = (query.account_id as string) || (query.accountId as string)
  if (accountId) backendUrl.searchParams.set('account_id', accountId)
  if (query.limit) backendUrl.searchParams.set('limit', String(query.limit))
  if (query.folder) backendUrl.searchParams.set('folder', String(query.folder))

  try {
    return await $fetch(backendUrl.toString(), {
      headers: {
        authorization: authHeader
      },
      credentials: 'include'
    })
  } catch (err: any) {
    const statusCode = err?.statusCode || err?.status || 500
    const statusMessage = err?.data?.detail || err?.message || 'E-Mails konnten nicht geladen werden.'
    throw createError({ statusCode, statusMessage, data: err?.data })
  }
})
