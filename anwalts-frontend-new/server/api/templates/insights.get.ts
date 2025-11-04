import { defineEventHandler, createError } from 'h3'
import { resolveBackendAuthHeader } from '~/server/utils/backendAuth'

const resolveBackendBase = () => {
  const config = useRuntimeConfig()
  return (config.backendBase || process.env.BACKEND_BASE || 'http://backend:8000').replace(/\/$/, '')
}

export default defineEventHandler(async (event) => {
  const authHeader = await resolveBackendAuthHeader(event, 'templates-insights')
  const backendBase = resolveBackendBase()

  try {
    return await $fetch(`${backendBase}/api/templates/insights`, {
      headers: {
        authorization: authHeader
      }
    })
  } catch (err: any) {
    const statusCode = err?.statusCode || err?.status || 500
    const message = err?.data?.detail || err?.message || 'Vorlagenstatistiken konnten nicht geladen werden.'
    throw createError({ statusCode, statusMessage: message, data: err?.data })
  }
})
