import { createError, getQuery, type H3Event } from 'h3'
import { resolveBackendAuthHeader } from '~/server/utils/backendAuth'

const resolveBackendBase = () => {
  const config = useRuntimeConfig()
  return (config.backendBase || process.env.BACKEND_BASE || 'http://backend:8000').replace(/\/$/, '')
}

export const fetchTemplatesFromBackend = async (event: H3Event) => {
  const authHeader = await resolveBackendAuthHeader(event, 'documents-templates')
  const backendBase = resolveBackendBase()
  const query = getQuery(event)
  const url = new URL(`${backendBase}/api/templates`)
  const category = (query?.category ?? query?.categoryId) as string | undefined
  if (category) {
    url.searchParams.set('category', category)
  }

  try {
    return await $fetch(url.toString(), {
      headers: {
        authorization: authHeader,
      },
    })
  } catch (err: any) {
    const statusCode = err?.statusCode || err?.status || 500
    if (statusCode === 401) {
      return []
    }
    const statusMessage = err?.data?.detail || err?.message || 'Template fetch failed'
    throw createError({ statusCode, statusMessage, data: err?.data })
  }
}

export const fetchClausesFromBackend = async (event: H3Event) => {
  const authHeader = await resolveBackendAuthHeader(event, 'documents-clauses')
  const backendBase = resolveBackendBase()

  try {
    return await $fetch(`${backendBase}/api/clauses`, {
      headers: {
        authorization: authHeader,
      },
    })
  } catch (err: any) {
    const statusCode = err?.statusCode || err?.status || 500
    if (statusCode === 401) {
      return []
    }
    const statusMessage = err?.data?.detail || err?.message || 'Clause fetch failed'
    throw createError({ statusCode, statusMessage, data: err?.data })
  }
}
