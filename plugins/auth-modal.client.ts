import { defineNuxtPlugin } from '#app'
import { createApp, h, ref } from 'vue'
import GlassmorphismAuthModal from '~/components/GlassmorphismAuthModal.vue'

type Mode = 'login' | 'signup'

const normalizeMode = (value?: string): Mode => {
  const lowered = (value || '').toLowerCase()
  return lowered === 'signup' || lowered === 'register' || lowered === 'sign-up' ? 'signup' : 'login'
}

export default defineNuxtPlugin(() => {
  if (process.server || typeof window === 'undefined') return

  if ((window as any).__anwaltsAuth) {
    const api = (window as any).__anwaltsAuth
    window.openAuthModal = api.open
    window.closeAuthModal = api.close
    return { provide: { authModal: api } }
  }

  const isOpen = ref(false)
  const mode = ref<Mode>('login')

  const open = (nextMode?: string) => {
    mode.value = normalizeMode(nextMode)
    isOpen.value = true
  }

  const close = () => {
    isOpen.value = false
  }

  const container = document.createElement('div')
  container.id = 'anwalts-auth-modal-host'
  document.body.appendChild(container)

  const root = createApp({
    setup() {
      const handleClose = () => close()
      const handleSuccess = () => {
        close()
      }
      return () => h(GlassmorphismAuthModal, {
        isOpen: isOpen.value,
        mode: mode.value,
        onClose: handleClose,
        onAuthSuccess: handleSuccess
      })
    }
  })

  root.mount(container)

  const api = { open, close, isOpen, mode }
  ;(window as any).__anwaltsAuth = api
  ;(window as any).__anwaltsAuthOpen = open
  ;(window as any).__anwaltsAuthClose = close
  window.openAuthModal = open
  window.closeAuthModal = close

  window.addEventListener('message', (event: MessageEvent) => {
    if (!event || typeof event.data !== 'object') return
    if (event.data.type === 'ANWALTS_OPEN_AUTH') open(event.data.mode)
    if (event.data.type === 'ANWALTS_CLOSE_AUTH') close()
  })

  window.dispatchEvent(new CustomEvent('anwalts-auth-modal-ready'))

  return {
    provide: {
      authModal: api
    }
  }
})
