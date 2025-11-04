import { defineEventHandler, readBody, createError } from 'h3'
import { resolveBackendAuthHeader } from '~/server/utils/backendAuth'

export default defineEventHandler(async (event) => {
  console.log('[AI] Proxying AI complete request to backend')

  const authHeader = await resolveBackendAuthHeader(event, 'ai-complete')

  const config = useRuntimeConfig()
  const backendBase = (config.backendBase || process.env.BACKEND_BASE || 'http://backend:8000').replace(/\/$/, '')
  const targetUrl = `${backendBase}/api/ai/complete`

  const body = await readBody(event)

  const headers: Record<string, string> = {
    'content-type': 'application/json',
    'authorization': authHeader,
  }

  try {
    const response = await $fetch(targetUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify(body)
    })

    console.log('[AI] Complete request successful')
    return response
  } catch (err: any) {
    console.error('[AI] Complete proxy error:', err)
    
    // Pass through the error status and message from backend
    const statusCode = err.statusCode || err.status || 500
    const message = err.data?.detail || err.message || 'AI completion request failed'
    
    throw createError({
      statusCode,
      statusMessage: message
    })
  }
})
