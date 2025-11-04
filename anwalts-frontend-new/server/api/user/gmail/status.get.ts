import { defineEventHandler, createError } from 'h3'
import { buildBackendUrl } from '~/server/utils/backend'
import { resolveBackendAuthHeader } from '~/server/utils/backendAuth'

export default defineEventHandler(async (event) => {
  const authHeader = await resolveBackendAuthHeader(event, 'gmail-status')
  const backendUrl = buildBackendUrl(event, '/api/user/gmail/status')

  try {
    return await $fetch(backendUrl, {
      headers: {
        authorization: authHeader
      },
      credentials: 'include'
    })
  } catch (err: any) {
    const statusCode = err?.statusCode || err?.status || 500
    const statusMessage = err?.data?.detail || err?.message || 'Gmail-Status konnte nicht geladen werden.'
    throw createError({ statusCode, statusMessage, data: err?.data })
  }
})
