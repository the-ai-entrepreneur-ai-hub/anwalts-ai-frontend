import { defineEventHandler, readBody, createError } from 'h3'
import { buildBackendUrl } from '~/server/utils/backend'
import { resolveBackendAuthHeader } from '~/server/utils/backendAuth'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const authHeader = await resolveBackendAuthHeader(event, 'email-modify')
  const backendUrl = buildBackendUrl(event, '/api/email/modify')

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
    const statusMessage = err?.data?.detail || err?.message || 'E-Mail konnte nicht aktualisiert werden.'
    throw createError({ statusCode, statusMessage, data: err?.data })
  }
})
