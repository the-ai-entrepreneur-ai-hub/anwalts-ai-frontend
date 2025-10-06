<template>
  <div class="min-h-screen">
    <FramerPage />
    <GlassmorphismAuthModal
      :isOpen="authModal.isOpen.value"
      @close="authModal.close"
    />
  </div>
  
</template>

<script setup>
import { onBeforeUnmount, onMounted } from 'vue'
import FramerPage from '~/components/FramerPage.vue'
import GlassmorphismAuthModal from '~/components/GlassmorphismAuthModal.vue'
import { useAuthModal } from '~/composables/useAuthModal'

definePageMeta({
  layout: false
})

const authModal = useAuthModal()

// Include auth modal styles and bridge script
useHead({
  link: [
    { rel: 'stylesheet', href: '/shared/anwalts-auth.css' }
  ],
  script: [
    { src: '/shared/auth-modal-bridge.js', defer: true }
  ]
})

if (process.client) {
  let messageHandler = null

  onMounted(() => {
    try {
      const url = new URL(window.location.href)
      const shouldOpen = url.searchParams.get('auth') === 'required'

      if (shouldOpen) {
        authModal.open()
      } else {
        authModal.close()
      }

      let urlChanged = false
      if (url.searchParams.has('message')) {
        url.searchParams.delete('message')
        urlChanged = true
      }
      if (url.searchParams.has('auth')) {
        url.searchParams.delete('auth')
        urlChanged = true
      }

      if (urlChanged) {
        const nextPath = `${url.pathname}${url.search}${url.hash || ''}`
        window.history.replaceState({}, document.title, nextPath)
      }
    } catch (error) {
      console.warn('Failed to parse landing page URL', error)
    }

    messageHandler = (event) => {
      if (!event?.data || !event.data.type) return

      switch (event.data.type) {
        case 'ANWALTS_OPEN_AUTH':
        case 'openSignInModal':
          authModal.open()
          break
        case 'ANWALTS_CLOSE_AUTH':
          authModal.close()
          break
      }
    }

    window.addEventListener('message', messageHandler)

    window.__anwaltsAuthModal = {
      open: () => authModal.open(),
      close: () => authModal.close(),
      state: authModal
    }
  })

  onBeforeUnmount(() => {
    if (messageHandler) {
      window.removeEventListener('message', messageHandler)
      messageHandler = null
    }

    if (window.__anwaltsAuthModal?.state === authModal) {
      delete window.__anwaltsAuthModal
    }
  })
}
</script>

<style scoped>
/* minimal wrapper only */
</style>
