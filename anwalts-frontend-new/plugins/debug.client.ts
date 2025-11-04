export default defineNuxtPlugin((nuxtApp) => {
  const sendLog = (payload: Record<string, any>) => {
    try {
      const body = JSON.stringify({
        ts: new Date().toISOString(),
        href: location.href,
        ua: navigator.userAgent,
        ...payload,
      })
      const url = '/api/debug/log'
      if ('sendBeacon' in navigator) {
        const blob = new Blob([body], { type: 'application/json' })
        navigator.sendBeacon(url, blob)
      } else {
        fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body }).catch(() => {})
      }
    } catch {}
  }

  const enabled = (() => {
    try {
      const qs = new URLSearchParams(location.search)
      return qs.get('debug') === '1'
    } catch { return false }
  })()
  if (!enabled) return

  // Global window errors
  window.addEventListener('error', (e) => {
    sendLog({ type: 'window.error', message: String(e.message || ''), filename: (e as any).filename, lineno: (e as any).lineno, colno: (e as any).colno, stack: (e as any).error?.stack })
  })
  window.addEventListener('unhandledrejection', (e) => {
    sendLog({ type: 'window.unhandledrejection', reason: String((e as any).reason || ''), stack: (e as any).reason?.stack })
  })

  // Nuxt/Vue app error hooks
  nuxtApp.hook('app:error', (err) => {
    sendLog({ type: 'nuxt.app_error', message: String(err?.message || err), stack: (err as any)?.stack })
  })

  // Mark mount
  sendLog({ type: 'debug.mark', message: 'debug plugin mounted' })
})
