<template>
  <div class="min-h-screen">
    <FramerPage />
    <GlassmorphismAuthModal :isOpen="authModal.isOpen" @close="authModal.close" />
  </div>
  
</template>

<script setup>
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

// Listen for postMessage events from iframe
if (process.client) {
  // Open modal when auth=required is present
  try {
    const u = new URL(window.location.href)
    if (u.searchParams.get('auth') === 'required') {
      authModal.open()
    }
  } catch {}

  window.addEventListener('message', (event) => {
    if (!event.data || !event.data.type) return
    
    switch (event.data.type) {
      case 'ANWALTS_OPEN_AUTH':
        authModal.open()
        break
      case 'ANWALTS_CLOSE_AUTH':
        authModal.close()
        break
      case 'openSignInModal':
        // Legacy support
        authModal.open()
        break
    }
  })
  
  // Register the auth modal handler globally for bridge script
  window.__anwaltsAuthModal = authModal
  
  // Sanitize unwanted params like ?message=free_limit_reached or lingering auth flags
  const url = new URL(window.location.href)
  let changed = false
  if (url.searchParams.has('message')) { url.searchParams.delete('message'); changed = true }
  if (url.searchParams.has('auth')) { url.searchParams.delete('auth'); changed = true }
  if (changed) {
    window.history.replaceState({}, document.title, url.pathname + url.search)
  }
}
</script>

<style scoped>
/* minimal wrapper only */
</style>
