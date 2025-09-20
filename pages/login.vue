<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-4">
    <div class="max-w-md w-full">
      <!-- Logo and Title -->
      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-gradient-to-br from-[#5b7ce6] to-[#4a6cd4] rounded-xl flex items-center justify-center mx-auto mb-4">
          <span class="text-white font-bold text-xl">A</span>
        </div>
        <h1 class="text-3xl font-bold text-white mb-2">ANWALTS.AI</h1>
        <p class="text-gray-300">Kanzlei-Dashboard Login</p>
      </div>

      <!-- Login Form -->
      <div class="bg-white/10 backdrop-blur-sm p-8 rounded-xl border border-white/20">
        <form @submit.prevent="handleLogin" class="space-y-6">
          <div>
            <button
              type="button"
              class="w-full flex items-center justify-center gap-3 bg-white text-slate-900 py-3 rounded-lg font-semibold hover:bg-slate-100 transition-colors border border-white/40 shadow-lg shadow-black/10"
              @click="handleGoogle"
            >
              <svg class="w-5 h-5" viewBox="0 0 24 24" aria-hidden="true"><path fill="#4285F4" d="M21.35 11.1h-9.17v2.96h5.27c-.23 1.24-.94 2.28-2.01 3.05v2.54h3.24c1.9-1.75 2.99-4.34 2.99-7.4 0-.52-.05-1.03-.14-1.52z"/><path fill="#34A853" d="M12.18 22c2.7 0 4.97-.9 6.63-2.45l-3.24-2.54c-.9.6-2.06.95-3.39.95-2.6 0-4.81-1.75-5.6-4.11H3.2v2.58C4.84 19.59 8.2 22 12.18 22z"/><path fill="#FBBC05" d="M6.58 13.85A5.91 5.91 0 0 1 6.26 12c0-.64.11-1.27.32-1.85V7.57H3.2A9.98 9.98 0 0 0 2.18 12c0 1.56.36 3.03 1.02 4.43l3.38-2.58z"/><path fill="#EA4335" d="M12.18 6.58c1.47 0 2.79.5 3.83 1.48l2.87-2.87C17.13 3.33 14.86 2.4 12.18 2.4 8.2 2.4 4.84 4.81 3.2 8.02l3.38 2.58c.79-2.36 3-4.02 5.6-4.02z"/></svg>
              <span>Mit Google anmelden</span>
            </button>
          </div>

          <div>
            <label class="block text-white mb-2 text-sm font-medium">E-Mail-Adresse</label>
            <input
              v-model="loginForm.email"
              type="email"
              required
              class="w-full p-3 rounded-lg bg-white/20 text-white placeholder-white/60 border border-white/30 focus:border-[#5b7ce6] focus:outline-none focus:ring-2 focus:ring-[#5b7ce6]/50"
              placeholder="ihre@email.com"
            >
          </div>

          <div>
            <label class="block text-white mb-2 text-sm font-medium">Passwort</label>
            <input
              v-model="loginForm.password"
              type="password"
              required
              class="w-full p-3 rounded-lg bg-white/20 text-white placeholder-white/60 border border-white/30 focus:border-[#5b7ce6] focus:outline-none focus:ring-2 focus:ring-[#5b7ce6]/50"
              placeholder="Ihr Passwort"
            >
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-[#5b7ce6] text-white py-3 rounded-lg font-semibold hover:bg-[#4a6cd4] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ loading ? 'Anmeldung...' : 'Anmelden' }}
          </button>
        </form>

        <!-- Error Message -->
        <div v-if="error" class="mt-4 p-4 rounded-lg bg-red-500/20 border border-red-500/30">
          <p class="text-red-200 text-sm">{{ error }}</p>
        </div>

        <!-- Success Message -->
        <div v-if="success" class="mt-4 p-4 rounded-lg bg-green-500/20 border border-green-500/30">
          <p class="text-green-200 text-sm">{{ success }}</p>
        </div>
      </div>

      <!-- Test Credentials Info -->
      <div class="mt-6 bg-white/5 backdrop-blur-sm p-4 rounded-lg border border-white/10">
        <p class="text-gray-300 text-sm text-center mb-2">Test-Anmeldedaten:</p>
        <div class="grid grid-cols-2 gap-2 text-xs">
          <div class="text-gray-400">Admin:</div>
          <div class="text-gray-300">admin@anwalts.ai / admin123</div>
          <div class="text-gray-400">Demo:</div>
          <div class="text-gray-300">demo@anwalts.ai / demo123</div>
        </div>
      </div>

      <!-- Back to Home -->
      <div class="text-center mt-6">
        <NuxtLink to="/" class="text-gray-400 hover:text-white text-sm transition-colors">
          ← Zurück zur Startseite
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

definePageMeta({
  layout: false
})

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const error = ref('')
const success = ref('')

const loginForm = reactive({
  email: '',
  password: ''
})

// Get redirect path from URL parameters
const redirectPath = ref('/dashboard')

onMounted(() => {
  const redirect = route.query.redirect
  if (redirect && typeof redirect === 'string') {
    redirectPath.value = decodeURIComponent(redirect)
  }
})

const handleGoogle = () => {
  if (process.client) {
    const url = new URL('/auth/google/authorize', window.location.origin)
    url.searchParams.set('redirect', redirectPath.value)
    window.location.href = url.pathname + url.search
  }
}

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  success.value = ''

  try {
    const response = await $fetch('/api/auth/login', {
      method: 'POST',
      body: {
        email: loginForm.email,
        password: loginForm.password,
        remember_me: false,
        csrf_token: 'login-form',
        device_fingerprint: null
      }
    })

    if (response?.success && response?.user) {
      // Store user data
      localStorage.setItem('auth_user', JSON.stringify(response.user))
      localStorage.setItem('auth_success', 'true')

      success.value = '✅ Anmeldung erfolgreich! Weiterleitung...'

      // Redirect after short delay
      setTimeout(() => {
        if (redirectPath.value.startsWith('/')) {
          navigateTo(redirectPath.value)
        } else {
          navigateTo('/dashboard')
        }
      }, 1200)
    } else {
      throw new Error('Ungültige Anmeldedaten')
    }
  } catch (err) {
    console.error('Login error:', err)
    error.value = err?.data?.message || err?.message || '❌ Anmeldung fehlgeschlagen'
  } finally {
    loading.value = false
  }
}

// Pre-fill for testing
onMounted(() => {
  // Uncomment to pre-fill admin credentials for testing
  // loginForm.email = 'admin@anwalts.ai'
  // loginForm.password = 'admin123'
})
</script>

<style scoped>
/* Additional styles if needed */
</style>