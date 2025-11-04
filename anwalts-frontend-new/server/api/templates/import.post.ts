import { defineEventHandler, readMultipartFormData, createError } from 'h3'
import { Buffer } from 'node:buffer'
import { resolveBackendAuthHeader } from '~/server/utils/backendAuth'

const resolveBackendBase = () => {
  const config = useRuntimeConfig()
  return (config.backendBase || process.env.BACKEND_BASE || 'http://backend:8000').replace(/\/$/, '')
}

export default defineEventHandler(async (event) => {
  const form = await readMultipartFormData(event)
  if (!form || form.length === 0) {
    throw createError({ statusCode: 400, statusMessage: 'Keine Datei übermittelt.' })
  }

  const authHeader = await resolveBackendAuthHeader(event, 'templates-import')
  const backendBase = resolveBackendBase()

  const forwardForm = new FormData()
  for (const part of form) {
    if (!part.name) continue
    if (part.filename) {
      const blob = new Blob([part.data], { type: part.type || 'application/octet-stream' })
      forwardForm.append(part.name, blob, part.filename)
    } else {
      const value =
        typeof part.data === 'string'
          ? part.data
          : part.data instanceof Uint8Array
            ? Buffer.from(part.data).toString('utf-8')
            : String(part.data ?? '')
      forwardForm.append(part.name, value)
    }
  }

  try {
    return await $fetch(`${backendBase}/api/templates/import`, {
      method: 'POST',
      headers: {
        authorization: authHeader
      },
      body: forwardForm
    })
  } catch (err: any) {
    const statusCode = err?.statusCode || err?.status || 500
    const message = err?.data?.detail || err?.message || 'Import fehlgeschlagen.'
    throw createError({ statusCode, statusMessage: message, data: err?.data })
  }
})
