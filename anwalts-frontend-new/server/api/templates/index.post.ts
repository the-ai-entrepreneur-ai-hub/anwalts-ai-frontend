import { defineEventHandler, readBody, createError } from 'h3'
import { resolveBackendAuthHeader } from '~/server/utils/backendAuth'

const resolveBackendBase = () => {
  const config = useRuntimeConfig()
  return (config.backendBase || process.env.BACKEND_BASE || 'http://backend:8000').replace(/\/$/, '')
}

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const authHeader = await resolveBackendAuthHeader(event, 'templates-create')
  const backendBase = resolveBackendBase()

  try {
    return await $fetch(`${backendBase}/api/templates`, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        authorization: authHeader
      },
      body: JSON.stringify(body ?? {})
    })
  } catch (err: any) {
    const statusCode = err?.statusCode || err?.status || 500
    const message = err?.data?.detail || err?.message || 'Vorlage konnte nicht erstellt werden.'
    throw createError({ statusCode, statusMessage: message, data: err?.data })
  }
})
