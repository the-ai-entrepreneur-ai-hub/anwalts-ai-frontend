<template>
  <div class="min-h-screen">
    <FramerPage />


  </div>
  
</template>

<script setup>
import FramerPage from '~/components/FramerPage.vue'

definePageMeta({
  layout: false
})

// Sanitize unwanted message params like ?message=free_limit_reached
if (process.client) {
  const url = new URL(window.location.href)
  if (url.searchParams.has('message')) {
    url.searchParams.delete('message')
    window.history.replaceState({}, document.title, url.pathname + url.search)
  }
}
</script>

<style scoped>
/* minimal wrapper only */
</style>