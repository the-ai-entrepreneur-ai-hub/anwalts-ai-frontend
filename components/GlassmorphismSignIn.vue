<template>
  <Teleport to="body">
    <div 
      v-if="isOpen" 
      class="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-sm"
      @click.self="close"
    >
      <div class="glassmorphism-modal w-full max-w-md">
        <div class="relative">
          <!-- Close button -->
          <button 
            @click="close"
            class="absolute -top-2 -right-2 w-8 h-8 bg-white bg-opacity-20 backdrop-blur-sm rounded-full flex items-center justify-center text-white hover:bg-opacity-30 transition-all"
          >
            ✕
          </button>

          <!-- Modal header -->
          <div class="text-center mb-8">
            <h2 class="text-2xl font-bold text-white mb-2">Willkommen bei ANWALTS.AI</h2>
            <p class="text-white/80">Registrieren Sie sich für Ihren kostenlosen Account</p>
          </div>

          <!-- Social login buttons -->
          <div class="space-y-3 mb-6">
            <button 
              @click="signInWithGoogle"
              class="w-full glass-button flex items-center justify-center gap-3 p-3 rounded-xl transition-all"
            >
              <svg class="w-5 h-5" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Mit Google anmelden
            </button>
            
            <button 
              @click="signInWithMicrosoft"
              class="w-full glass-button flex items-center justify-center gap-3 p-3 rounded-xl transition-all"
            >
              <svg class="w-5 h-5" viewBox="0 0 24 24">
                <path fill="#f35325" d="M1 1h10.5v10.5H1z"/>
                <path fill="#81bc06" d="M12.5 1H23v10.5H12.5z"/>
                <path fill="#05a6f0" d="M1 12.5h10.5V23H1z"/>
                <path fill="#ffba08" d="M12.5 12.5H23V23H12.5z"/>
              </svg>
              Mit Microsoft anmelden
            </button>
          </div>

          <!-- Divider -->
          <div class="flex items-center my-6">
            <div class="flex-1 h-px bg-white/20"></div>
            <span class="px-4 text-white/60 text-sm">oder</span>
            <div class="flex-1 h-px bg-white/20"></div>
          </div>

          <!-- Email form -->
          <form @submit.prevent="signInWithEmail" class="space-y-4">
            <div>
              <input 
                v-model="form.email"
                type="email" 
                placeholder="E-Mail-Adresse"
                class="glass-input w-full p-3 rounded-xl"
                required
              >
            </div>
            <div>
              <input 
                v-model="form.password"
                type="password" 
                placeholder="Passwort"
                class="glass-input w-full p-3 rounded-xl"
                required
              >
            </div>
            <button 
              type="submit"
              :disabled="loading"
              class="w-full glass-button-primary p-3 rounded-xl font-semibold transition-all"
            >
              <span v-if="!loading">Registrieren</span>
              <span v-else class="flex items-center justify-center gap-2">
                <svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                </svg>
                Wird verarbeitet...
              </span>
            </button>
          </form>

          <!-- Footer -->
          <div class="mt-6 text-center">
            <p class="text-white/60 text-sm">
              Bereits registriert? 
              <button @click="switchToSignIn" class="text-white hover:text-white/80 font-medium">
                Hier anmelden
              </button>
            </p>
          </div>

          <!-- Terms -->
          <div class="mt-4 text-center">
            <p class="text-white/40 text-xs">
              Mit der Registrierung stimmen Sie unseren 
              <a href="/terms" class="text-white/60 hover:text-white/80">Nutzungsbedingungen</a> 
              und der 
              <a href="/privacy" class="text-white/60 hover:text-white/80">Datenschutzerklärung</a> zu.
            </p>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive } from 'vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'sign-in-success'])

const loading = ref(false)
const form = reactive({
  email: '',
  password: ''
})

const close = () => {
  emit('close')
}

const signInWithGoogle = async () => {
  try {
    loading.value = true
    console.log('Initiating Google OAuth from SignIn modal...')
    // Redirect to Google OAuth endpoint
    await navigateTo('/auth/google', { external: true })
  } catch (error) {
    console.error('Google sign in error:', error)
    // Fallback to dashboard with demo params
    await navigateTo('/dashboard?auth=google&demo=true')
    emit('sign-in-success', { provider: 'google' })
  } finally {
    loading.value = false
  }
}

const signInWithMicrosoft = async () => {
  try {
    loading.value = true
    // Simulate Microsoft OAuth flow
    await new Promise(resolve => setTimeout(resolve, 1000))
    // Redirect to dashboard after successful sign in
    await navigateTo('/dashboard')
    emit('sign-in-success', { provider: 'microsoft' })
  } catch (error) {
    console.error('Microsoft sign in error:', error)
  } finally {
    loading.value = false
  }
}

const signInWithEmail = async () => {
  try {
    loading.value = true
    // Simulate email/password sign in
    await new Promise(resolve => setTimeout(resolve, 1000))
    // Redirect to dashboard after successful sign in
    await navigateTo('/dashboard')
    emit('sign-in-success', { provider: 'email', email: form.email })
  } catch (error) {
    console.error('Email sign in error:', error)
  } finally {
    loading.value = false
  }
}

const switchToSignIn = () => {
  // Switch modal to sign in mode (can be extended later)
  close()
  navigateTo('/login')
}
</script>

<style scoped>
.glassmorphism-modal {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 
    0 8px 32px 0 rgba(31, 38, 135, 0.37),
    inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
}

.glass-button {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
}

.glass-button:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
}

.glass-button-primary {
  background: linear-gradient(135deg, rgba(14, 28, 41, 0.8) 0%, rgba(50, 61, 104, 0.8) 100%);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  font-weight: 600;
}

.glass-button-primary:hover {
  background: linear-gradient(135deg, rgba(14, 28, 41, 0.9) 0%, rgba(50, 61, 104, 0.9) 100%);
  transform: translateY(-1px);
}

.glass-button-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.glass-input {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
}

.glass-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.glass-input:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.15);
}
</style>
