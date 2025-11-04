import { defineEventHandler, readBody, createError } from 'h3'
import { resolveBackendAuthHeader } from '~/server/utils/backendAuth'

type DocumentAction = 'generate' | 'submit'

const GENERATE_ENDPOINTS = [
  '/api/ai/generate-document-simple',
  '/api/ai/generate-document'
]

function buildBackendPayload(base: Record<string, any>) {
  const uploadId = base.uploadId ?? base.upload_id ?? null
  return {
    ...base,
    uploadId,
    upload_id: uploadId,
    document_type: base.document_type || base.docType || 'custom',
    instructions: base.instructions || base.prompt || base.requirements || '',
    tone: base.tone || 'neutral'
  }
}

function normalizeDocumentResponse(raw: any, processingState: string) {
  const doc = raw?.document ?? raw ?? {}
  const id = doc.id ?? raw?.id ?? null
  const metadata = doc.metadata ?? raw?.metadata ?? {}
  const download = raw?.download ?? doc.download ?? (id
    ? {
        docx: `/api/documents/${id}/export?format=docx`,
        pdf: `/api/documents/${id}/export?format=pdf`
      }
    : null)

  return {
    success: true,
    document: {
      id,
      title: doc.title ?? raw?.title ?? 'Rechtsdokument',
      content: doc.content ?? doc.html ?? '',
      document_type: doc.document_type ?? doc.type ?? raw?.document_type ?? 'custom',
      created_at: doc.created_at ?? raw?.created_at ?? new Date().toISOString(),
      metadata,
      status: doc.status ?? raw?.status ?? processingState,
      processing_state: doc.processing_state ?? processingState,
      download
    },
    metadata,
    download,
    status: doc.status ?? raw?.status ?? processingState,
    processingState,
    documentId: id,
    id
  }
}

async function callBackend<T = any>(url: string, authHeader: string, body: any) {
  return await $fetch<T>(url, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      authorization: authHeader
    },
    body: JSON.stringify(body)
  })
}

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const action: DocumentAction = (body?.action || 'generate').toLowerCase()

  if (!['generate', 'submit'].includes(action)) {
    throw createError({ statusCode: 400, statusMessage: `Unsupported action "${action}"` })
  }

  const authHeader = await resolveBackendAuthHeader(event, `documents-${action}`)
  const config = useRuntimeConfig()
  const backendBase = (config.backendBase || process.env.BACKEND_BASE || 'http://backend:8000').replace(/\/$/, '')

  if (action === 'generate') {
    const payload = buildBackendPayload(body?.payload || body)

    let lastError: any = null
    for (const endpoint of GENERATE_ENDPOINTS) {
      try {
        const targetUrl = `${backendBase}${endpoint}`
        const response = await callBackend(targetUrl, authHeader, payload)
        return {
          action,
          ...normalizeDocumentResponse(response, response?.processing_state ?? 'generated')
        }
      } catch (err: any) {
        lastError = err
        if (err?.statusCode === 403) continue
      }
    }

    const statusCode = lastError?.statusCode || lastError?.status || 502
    const message = lastError?.data?.detail || lastError?.message || 'Document generation failed'
    throw createError({ statusCode, statusMessage: message, data: lastError?.data })
  }

  if (action === 'submit') {
    const payload = body?.payload || body || {}
    const targetUrl = `${backendBase}/api/documents/save`

    try {
      const response: any = await callBackend(targetUrl, authHeader, payload)

      // Optionally update status to submitted
      const documentId = response?.id || response?.documentId || response?.document?.id
      const desiredStatus = payload.status || 'submitted'
      if (documentId && desiredStatus) {
        try {
          await callBackend(
            `${backendBase}/api/documents/${documentId}/status`,
            authHeader,
            { status: desiredStatus }
          )
        } catch (statusErr) {
          console.warn('[documents-process] status update failed', statusErr)
        }
      }

      return {
        action,
        ...normalizeDocumentResponse(
          {
            ...response,
            status: desiredStatus || response?.status || response?.document?.status
          },
          response?.processing_state ?? 'submitted'
        )
      }
    } catch (err: any) {
      const statusCode = err?.statusCode || err?.status || 500
      const message = err?.data?.detail || err?.message || 'Document submission failed'
      throw createError({ statusCode, statusMessage: message, data: err?.data })
    }
  }
})
