<template>
  <div>
    <!-- Loading while redirecting to static page -->
    <div class="min-h-screen bg-gradient-to-br from-blue-600 to-purple-700 flex items-center justify-center">
      <div class="text-white text-center">
        <div class="animate-spin w-8 h-8 border-4 border-white border-t-transparent rounded-full mx-auto mb-4"></div>
        <p>Loading ANWALTS.AI...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
definePageMeta({
  layout: false
})

// Redirect to static Framer page
onMounted(() => {
  if (process.client) {
    window.location.href = '/page.html'
  }
})
</script>