<template>
  <div class="framer-landing-wrapper">
    <!-- Loading state -->
    <div v-if="loading" class="min-h-screen bg-gradient-to-br from-blue-600 to-purple-700 flex items-center justify-center">
      <div class="text-white text-center">
        <div class="animate-spin w-8 h-8 border-4 border-white border-t-transparent rounded-full mx-auto mb-4"></div>
        <p>Loading ANWALTS.AI...</p>
      </div>
    </div>

    <!-- Framer content -->
    <div v-else-if="framerContent" class="framer-landing-page" v-html="framerContent"></div>

    <!-- Fallback landing page with glassmorphism -->
    <div v-else class="min-h-screen relative overflow-hidden">
      <!-- Background gradient -->
      <div class="absolute inset-0 bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900"></div>
      
      <!-- Animated background elements -->
      <div class="absolute inset-0">
        <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div class="absolute bottom-1/4 right-1/4 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>
      
      <!-- Content -->
      <div class="relative z-10 container mx-auto px-4 py-20">
        <!-- Header with glassmorphism -->
        <header class="fixed top-0 left-0 right-0 z-50 bg-white/10 backdrop-blur-md border-b border-white/20">
          <div class="container mx-auto px-4 py-4 flex items-center justify-between">
            <div class="text-2xl font-bold text-white">ANWALTS.AI</div>
            <nav class="hidden md:flex space-x-8">
              <a href="/dashboard" class="text-white/80 hover:text-white transition-colors">Dashboard</a>
              <a href="/dashboard/research" class="text-white/80 hover:text-white transition-colors">Fragen</a>
              <a href="http://Www.kunden.anwalts.ai" class="text-white/80 hover:text-white transition-colors">Vertrieb</a>
            </nav>
            <NuxtLink to="/dashboard"
              class="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg"
            >
              Zum Dashboard
            </NuxtLink>
          </div>
        </header>

        <!-- Hero section -->
        <div class="pt-32 text-center">
          <h1 class="text-6xl md:text-8xl font-bold text-white mb-6 tracking-tight">
            ANWALTS.AI
          </h1>
          <p class="text-xl md:text-2xl text-white/80 mb-12 max-w-3xl mx-auto">
            KI-gestützte Rechtslösungen für die moderne Anwaltskanzlei
          </p>
          
          <!-- CTA Buttons -->
          <div class="flex flex-col sm:flex-row gap-4 justify-center items-center mb-20">
            <button 
              @click="goToDashboard"
              class="bg-white/20 backdrop-blur-sm text-white px-12 py-4 rounded-xl font-semibold hover:bg-white/30 transition-all border border-white/20 shadow-xl text-lg"
            >
              Kostenlos registrieren
            </button>
            <NuxtLink 
              to="/dashboard"
              class="border-2 border-white/50 text-white px-12 py-4 rounded-xl font-semibold hover:bg-white hover:text-blue-600 transition-all text-lg"
            >
              Zum Dashboard
            </NuxtLink>
          </div>

          <!-- Features -->
          <div class="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div class="bg-white/10 backdrop-blur-sm p-8 rounded-2xl border border-white/20">
              <div class="text-4xl mb-4">⚖️</div>
              <h3 class="text-xl font-semibold text-white mb-3">Rechtsprechung</h3>
              <p class="text-white/80">KI-gestützte Suche durch Rechtsdatenbanken und Fallrecht</p>
            </div>
            
            <div class="bg-white/10 backdrop-blur-sm p-8 rounded-2xl border border-white/20">
              <div class="text-4xl mb-4">📄</div>
              <h3 class="text-xl font-semibold text-white mb-3">Dokumentenanalyse</h3>
              <p class="text-white/80">Intelligente Dokumentenprüfung und Vertragsanalyse</p>
            </div>
            
            <div class="bg-white/10 backdrop-blur-sm p-8 rounded-2xl border border-white/20">
              <div class="text-4xl mb-4">🤖</div>
              <h3 class="text-xl font-semibold text-white mb-3">KI-Assistent</h3>
              <p class="text-white/80">24/7 KI-Assistent für juristische Fragen und Beratung</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Authentication Modal -->
    <StackAuthModal 
      :is-open="showAuthModal" 
      @close="showAuthModal = false"
      @auth-success="handleAuthSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'

// Clean landing component. We do not open any modals here.
// All CTAs navigate to the dashboard. The live static page
// content is served from /public/page.html which mirrors
// /var/www/html/preview/clean.

const goToDashboard = () => {
  navigateTo('/dashboard')
}

const loading = ref(true)
const framerContent = ref('')

onMounted(async () => {
  // Make the function globally available for Framer/Framer-export integration
  if (process.client) {
    // Clean landing page - no auth modals, just navigate to dashboard
    window.openSignInModal = () => navigateTo('/dashboard')
    window.openAuthModal = () => navigateTo('/dashboard')
    window.showSignInModal = () => navigateTo('/dashboard')

    // DISABLED: Removed auto-opening modal on login parameter
    // This was causing modal to open on every page load

    // DISABLED: Removed problematic auto-opening event listeners
    // These were causing the modal to open unexpectedly

    console.log('Auth modal integration setup complete')
  }

  try {
    console.log('Landing: using fallback content (no remote Framer load)')
    // DISABLED to prevent Framer external links from loading
    // framerContent.value = '' // Keep empty to show fallback

    console.log('Using fallback content instead of problematic Framer content')
  } catch (error) {
    console.error('Error loading Framer content:', error)
  } finally {
    loading.value = false

    // DISABLED: setupFramerInteractions was causing auto-modal opening
    // await nextTick()
    // try { setupFramerInteractions() } catch (_) {}
  }
})

// DISABLED: This function was causing modal to auto-open by finding "Registrieren" text
// const setupFramerInteractions = () => {
//   const buttons = document.querySelectorAll('[data-framer-name*="cta"], [data-framer-name*="secondary cta"], .framer-gosiQ')
//   buttons.forEach(button => {
//     button.addEventListener('click', (e) => {
//       e.preventDefault()
//       e.stopPropagation()
//       showSignInModal()
//     })
//   })
//   
//   const links = document.querySelectorAll('a')
//   links.forEach(link => {
//     if (link.textContent?.includes('Registrieren') || link.href?.includes('framer.link')) {
//       link.addEventListener('click', (e) => {
//         e.preventDefault()
//         e.stopPropagation()
//         showSignInModal()
//       })
//     }
//   })
// }

// Clean landing page setup complete
</script>

<style scoped>
.framer-landing-wrapper {
  width: 100%;
  min-height: 100vh;
}

/* Ensure Framer content displays properly */
.framer-landing-page {
  width: 100%;
  min-height: 100vh;
}

/* Override any conflicting styles */
.framer-landing-page :deep(*) {
  box-sizing: border-box;
}

/* Ensure glassmorphism effects work */
.framer-landing-page :deep(header) {
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}
</style>
