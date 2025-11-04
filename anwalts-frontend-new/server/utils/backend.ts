import type { H3Event } from 'h3'

const DEFAULT_BACKEND_BASE = 'http://backend:8000'

export function resolveBackendBase(event?: H3Event): string {
  // Prefer runtimeConfig if available
  try {
    // @ts-ignore runtime available in Nitro
    const { useRuntimeConfig } = require('#imports')
    const cfg = event ? useRuntimeConfig(event) : useRuntimeConfig()
    const candidate = (cfg as any)?.backendBase || process.env.BACKEND_BASE
    const base = typeof candidate === 'string' && candidate.trim().length > 0 ? candidate.trim() : DEFAULT_BACKEND_BASE
    return base.replace(/\/?$/, '')
  } catch {
    const base = process.env.BACKEND_BASE || DEFAULT_BACKEND_BASE
    return base.replace(/\/?$/, '')
  }
}

export function buildBackendUrl(event: H3Event, path: string): string {
  const base = resolveBackendBase(event)
  const normalized = path.startsWith('/') ? path : `/${path}`
  return `${base}${normalized}`
}

