import { defineEventHandler, readBody, createError } from 'h3'
import { buildBackendUrl } from '~/server/utils/backend'
import { resolveBackendAuthHeader } from '~/server/utils/backendAuth'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const authHeader = await resolveBackendAuthHeader(event, 'gmail-consent')
  const backendUrl = buildBackendUrl(event, '/api/user/gmail/consent')

  try {
    return await $fetch(backendUrl, {
      method: 'POST',
      headers: {
        authorization: authHeader,
        'content-type': 'application/json'
      },
      body: JSON.stringify(body),
      credentials: 'include'
    })
  } catch (err: any) {
    const statusCode = err?.statusCode || err?.status || 500
    const statusMessage = err?.data?.detail || err?.message || 'Zustimmungen konnten nicht gespeichert werden.'
    throw createError({ statusCode, statusMessage, data: err?.data })
  }
})
