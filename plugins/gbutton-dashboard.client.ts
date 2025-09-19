import { defineNuxtPlugin } from '#app'

export default defineNuxtPlugin((nuxtApp) => {
  if (process.server) return

  const ensure = () => {
    if (!location.pathname.startsWith('/dashboard')) return
    if (!document.querySelector('script[data-gbutton]')) {
      const s = document.createElement('script')
      s.src = '/shared/gbutton.js'
      s.defer = true
      s.setAttribute('data-gbutton', '1')
      document.head.appendChild(s)
    }
  }

  nuxtApp.hook('page:finish', ensure)
  if (document.readyState === 'complete' || document.readyState === 'interactive') setTimeout(ensure, 0)
  else window.addEventListener('DOMContentLoaded', ensure as any, { once: true } as any)
})
