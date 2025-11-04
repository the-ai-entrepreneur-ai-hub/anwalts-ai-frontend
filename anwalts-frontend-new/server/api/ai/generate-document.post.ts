import { defineEventHandler, readBody, createError } from 'h3'
import { resolveBackendAuthHeader } from '~/server/utils/backendAuth'

export default defineEventHandler(async (event) => {
  console.log('[AI] Proxying generate-document request to backend')

  const authHeader = await resolveBackendAuthHeader(event, 'ai-generate-document')
  const config = useRuntimeConfig()
  const backendBase = (config.backendBase || process.env.BACKEND_BASE || 'http://backend:8000').replace(/\/$/, '')
  const targetUrl = `${backendBase}/api/ai/generate-document`

  const body = await readBody(event)

  try {
    const response = await $fetch(targetUrl, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        authorization: authHeader,
      },
      body: JSON.stringify(body),
    })
    return response
  } catch (err: any) {
    console.error('[AI] generate-document proxy error:', err)
    const statusCode = err.statusCode || err.status || 500
    const message = err.data?.detail || err.message || 'Document generation failed'
    throw createError({ statusCode, statusMessage: message })
  }
})
