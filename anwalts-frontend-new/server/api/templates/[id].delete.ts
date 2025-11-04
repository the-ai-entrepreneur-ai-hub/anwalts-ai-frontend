import { defineEventHandler, createError, getQuery } from 'h3'
import { resolveBackendAuthHeader } from '~/server/utils/backendAuth'

const resolveBackendBase = () => {
  const config = useRuntimeConfig()
  return (config.backendBase || process.env.BACKEND_BASE || 'http://backend:8000').replace(/\/$/, '')
}

export default defineEventHandler(async (event) => {
  const params = event.context.params || {}
  const id = params.id
  if (!id) {
    throw createError({ statusCode: 400, statusMessage: 'Template ID erforderlich.' })
  }

  const query = getQuery(event)
  const updatedAt = (query.updatedAt ?? query.updated_at) as string | undefined

  const authHeader = await resolveBackendAuthHeader(event, `templates-delete-${id}`)
  const backendBase = resolveBackendBase()
  const target = new URL(`${backendBase}/api/templates/${id}`)
  if (updatedAt) {
    target.searchParams.set('updated_at', updatedAt)
  }

  try {
    return await $fetch(target.toString(), {
      method: 'DELETE',
      headers: {
        authorization: authHeader
      }
    })
  } catch (err: any) {
    const statusCode = err?.statusCode || err?.status || 500
    const message = err?.data?.detail || err?.message || 'Vorlage konnte nicht gelöscht werden.'
    throw createError({ statusCode, statusMessage: message, data: err?.data })
  }
})
