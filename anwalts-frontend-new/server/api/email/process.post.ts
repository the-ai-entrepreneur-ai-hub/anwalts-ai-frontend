import { defineEventHandler, readBody, createError } from 'h3'
import { resolveBackendAuthHeader } from '~/server/utils/backendAuth'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const backendBase = (config.backendBase || process.env.BACKEND_BASE || 'http://backend:8000').replace(/\/$/, '')
  const targetUrl = `${backendBase}/api/email/process`
  const body = await readBody(event)

  let authHeader: string
  try {
    authHeader = await resolveBackendAuthHeader(event, 'email-process-ai')
  } catch (err: any) {
    const message = err?.statusMessage || err?.message || 'Authentication required'
    throw createError({ statusCode: err?.statusCode || err?.status || 401, statusMessage: message })
  }

  try {
    return await $fetch(targetUrl, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        authorization: authHeader,
      },
      body: JSON.stringify(body ?? {}),
    })
  } catch (err: any) {
    console.error('[Email] process proxy error:', err)
    const statusCode = err?.statusCode || err?.status || 500
    const message = err?.data?.detail || err?.message || 'Email processing failed'
    throw createError({ statusCode, statusMessage: message, data: err?.data })
  }
})
