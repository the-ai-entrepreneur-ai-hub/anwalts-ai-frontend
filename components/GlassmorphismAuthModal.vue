<template>
  <Teleport to="body">
    <div 
      v-if="props.isOpen"
      class="auth-modal-overlay"
      @click="handleOverlayClick"
      aria-hidden="false"
      role="dialog"
    >
      <div 
        class="auth-modal"
        @click.stop
      >
        <div class="auth-modal-header">
          <h2 class="auth-modal-title">{{ isSignUp ? 'Registrieren' : 'Anmelden' }}</h2>
          <button class="auth-modal-close" @click="$emit('close')">×</button>
        </div>



        <div class="auth-content">
        <!-- Social Login Section -->
        <div class="social-login-section">
          <button class="social-button google" @click="handleGoogleAuth">
            <svg width="20" height="20" viewBox="0 0 24 24">
              <path fill="#4285f4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34a853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#fbbc05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#ea4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Mit Google {{ isSignUp ? 'registrieren' : 'anmelden' }}
          </button>
        </div>

        <!-- Divider -->
        <div class="auth-divider">
          <span>oder mit E-Mail</span>
        </div>

        <!-- Authentication Form -->
        <form id="authForm" @submit.prevent="handleSubmit" class="auth-form">
          <!-- Name fields (only for sign up) -->
          <div v-if="isSignUp" class="auth-grid-2">
            <div class="auth-form-group">
              <label class="auth-form-label" for="authFirstName">Vorname</label>
              <input v-model="formData.firstName" type="text" id="authFirstName" class="auth-form-input" placeholder="Max">
            </div>
            <div class="auth-form-group">
              <label class="auth-form-label" for="authLastName">Nachname</label>
              <input v-model="formData.lastName" type="text" id="authLastName" class="auth-form-input" placeholder="Müller">
            </div>
          </div>
          <div v-if="isSignUp" class="auth-form-group">
            <label class="auth-form-label" for="authFullName">Vollständiger Name</label>
            <input v-model="formData.name" type="text" id="authFullName" class="auth-form-input" placeholder="Dr. Max Müller">
            <div v-if="errors.name" class="auth-error">{{ errors.name }}</div>
          </div>

          <!-- Email field -->
          <div class="auth-form-group">
            <label class="auth-form-label" for="authEmail">E-Mail-Adresse</label>
            <input 
              v-model="formData.email"
              type="email" 
              id="authEmail" 
              class="auth-form-input" 
              placeholder="ihre@email.com" 
              required
            >
            <div v-if="errors.email" class="auth-error">{{ errors.email }}</div>
          </div>

          <!-- Password field -->
          <div class="auth-form-group">
            <label class="auth-form-label" for="authPassword">Passwort</label>
            <input 
              v-model="formData.password"
              type="password" 
              id="authPassword" 
              class="auth-form-input" 
              placeholder="Ihr Passwort" 
              required
            >
            <div v-if="errors.password" class="auth-error">{{ errors.password }}</div>
          </div>

          <!-- Confirm Password field (only for sign up) -->
          <div v-if="isSignUp" class="auth-form-group">
            <label class="auth-form-label" for="authConfirmPassword">Passwort bestätigen</label>
            <input 
              v-model="formData.confirmPassword"
              type="password" 
              id="authConfirmPassword" 
              class="auth-form-input" 
              placeholder="Passwort bestätigen"
            >
            <div v-if="errors.confirmPassword" class="auth-error">{{ errors.confirmPassword }}</div>
          </div>

          <!-- Contact details (only for sign up) -->
          <div v-if="isSignUp" class="auth-grid-2">
            <div class="auth-form-group">
              <label class="auth-form-label" for="authPhone">Telefon</label>
              <input v-model="formData.phone" type="tel" id="authPhone" class="auth-form-input" placeholder="+49 170 1234567">
              <div v-if="errors.phone" class="auth-error">{{ errors.phone }}</div>
            </div>
            <div class="auth-form-group">
              <label class="auth-form-label" for="authCompany">Kanzlei/Firma</label>
              <input v-model="formData.company" type="text" id="authCompany" class="auth-form-input" placeholder="ANWALTS.AI GmbH">
            </div>
          </div>

          <!-- Address (only for sign up) -->
          <div v-if="isSignUp" class="auth-form-group">
            <label class="auth-form-label" for="authAddress1">Adresse</label>
            <input v-model="formData.addressLine1" type="text" id="authAddress1" class="auth-form-input" placeholder="Musterstraße 1">
            <div v-if="errors.addressLine1" class="auth-error">{{ errors.addressLine1 }}</div>
          </div>
          <div v-if="isSignUp" class="auth-form-group">
            <input v-model="formData.addressLine2" type="text" class="auth-form-input" placeholder="Adresszusatz (optional)">
          </div>
          <div v-if="isSignUp" class="auth-grid-2">
            <div class="auth-form-group">
              <label class="auth-form-label" for="authCity">Stadt</label>
              <input v-model="formData.city" type="text" id="authCity" class="auth-form-input" placeholder="Berlin">
              <div v-if="errors.city" class="auth-error">{{ errors.city }}</div>
            </div>
            <div class="auth-form-group">
              <label class="auth-form-label" for="authPostal">PLZ</label>
              <input v-model="formData.postalCode" type="text" id="authPostal" class="auth-form-input" placeholder="10115">
              <div v-if="errors.postalCode" class="auth-error">{{ errors.postalCode }}</div>
            </div>
          </div>
          <div v-if="isSignUp" class="auth-form-group">
            <label class="auth-form-label" for="authCountry">Land</label>
            <input v-model="formData.country" type="text" id="authCountry" class="auth-form-input" placeholder="Deutschland">
            <div v-if="errors.country" class="auth-error">{{ errors.country }}</div>
          </div>

          <!-- Form Options -->
          <div v-if="!isSignUp" class="auth-form-options">
            <label class="auth-checkbox-group">
              <input
                v-model="formData.rememberMe"
                type="checkbox"
                class="auth-checkbox"
              >
              <span>Angemeldet bleiben</span>
            </label>
            <a href="#" class="auth-link" @click="handleForgotPassword">Passwort vergessen?</a>
            <a href="#" class="auth-link" style="margin-left:12px" @click="enterResetMode">Code bereits erhalten?</a>
          </div>

          <!-- Password reset section (OTP) -->
          <div v-if="!isSignUp && isResetMode" class="auth-form-group">
            <label class="auth-form-label" for="authResetOtp">Einmal-Code</label>
            <input v-model="reset.otp" id="authResetOtp" class="auth-form-input" placeholder="6-stelliger Code" />
          </div>
          <div v-if="!isSignUp && isResetMode" class="auth-form-group">
            <label class="auth-form-label" for="authResetNew">Neues Passwort</label>
            <input v-model="reset.newPassword" type="password" id="authResetNew" class="auth-form-input" placeholder="Neues Passwort" />
          </div>
          <div v-if="!isSignUp && isResetMode" class="auth-actions">
            <button type="button" class="auth-submit-button" :disabled="loading || !reset.otp || !reset.newPassword" @click="handleResetSubmit">
              Passwort zurücksetzen
            </button>
          </div>

          <!-- Actions now appear at the end of the form (scroll to reach) -->
          <div class="auth-actions">
            <div v-if="isSignUp" class="auth-consent-row">
              <label class="auth-checkbox-group auth-consent-checkbox">
                <input 
                  v-model="formData.acceptTerms"
                  type="checkbox" 
                  class="auth-checkbox" 
                  required
                >
                <span>Ich akzeptiere</span>
              </label>
              <NuxtLink to="/terms" class="auth-link">AGB</NuxtLink>
              <span>und</span>
              <NuxtLink to="/privacy" class="auth-link">Datenschutz</NuxtLink>
            </div>
            <div v-if="errors.terms && isSignUp" class="auth-error">{{ errors.terms }}</div>
            <button 
              type="submit" 
              class="auth-submit-button cta-with-lights" 
              :disabled="loading"
            >
              <span v-if="!loading">{{ isSignUp ? 'Registrieren' : 'Anmelden' }}</span>
              <div v-else class="auth-loading"></div>
            </button>
            <div class="auth-form-toggle auth-form-toggle-bottom">
              <span>{{ isSignUp ? 'Bereits ein Konto?' : 'Noch kein Konto?' }}</span>
              <button type="button" @click="toggleMode">
                {{ isSignUp ? 'Jetzt anmelden' : 'Jetzt registrieren' }}
              </button>
            </div>
          </div>

        </form>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close', 'auth-success'])

const { syncSessionFromTokens } = useSupabaseAuth()

const isSignUp = ref(false)
const isResetMode = ref(false)
const loading = ref(false)

const reset = reactive({ otp: '', newPassword: '' })

const formData = reactive({
  // Shared
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
  rememberMe: false,
  acceptTerms: false,
  // Registration details
  firstName: '',
  lastName: '',
  phone: '',
  company: '',
  addressLine1: '',
  addressLine2: '',
  city: '',
  postalCode: '',
  country: ''
})

const errors = reactive({
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
  terms: '',
  phone: '',
  company: '',
  addressLine1: '',
  city: '',
  postalCode: '',
  country: ''
})

const handleOverlayClick = () => {
  emit('close')
}

const toggleMode = () => {
  isSignUp.value = !isSignUp.value
  isResetMode.value = false
  clearErrors()
}

const clearErrors = () => {
  Object.keys(errors).forEach(key => errors[key] = '')
}

const validateForm = () => {
  clearErrors()
  let isValid = true

  if (isSignUp.value && !formData.name.trim()) {
    errors.name = 'Name ist erforderlich'
    isValid = false
  }

  if (!formData.email.trim()) {
    errors.email = 'E-Mail ist erforderlich'
    isValid = false
  }

  if (!formData.password.trim()) {
    errors.password = 'Passwort ist erforderlich'
    isValid = false
  }

  if (isSignUp.value) {
    if (!formData.confirmPassword.trim()) {
      errors.confirmPassword = 'Passwort bestätigen ist erforderlich'
      isValid = false
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Passwörter stimmen nicht überein'
      isValid = false
    }

    // Additional recommended fields for registration
    if (!formData.firstName.trim()) {
      errors.name = 'Vorname ist erforderlich'
      isValid = false
    }
    if (!formData.lastName.trim()) {
      errors.name = errors.name || 'Nachname ist erforderlich'
      isValid = false
    }
    if (!formData.phone.trim()) {
      errors.phone = 'Telefonnummer ist erforderlich'
      isValid = false
    }
    if (!formData.addressLine1.trim()) {
      errors.addressLine1 = 'Adresse ist erforderlich'
      isValid = false
    }
    if (!formData.city.trim()) {
      errors.city = 'Stadt ist erforderlich'
      isValid = false
    }
    if (!formData.postalCode.trim()) {
      errors.postalCode = 'PLZ ist erforderlich'
      isValid = false
    }
    if (!formData.country.trim()) {
      errors.country = 'Land ist erforderlich'
      isValid = false
    }

    if (!formData.acceptTerms) {
      errors.terms = 'Sie müssen die AGB akzeptieren'
      isValid = false
    }
  }

  return isValid
}

const handleSubmit = async () => {
  if (!validateForm()) return

  loading.value = true

  try {
    if (isSignUp.value) {
      // Construct full address string from components
      const addressParts = [
        formData.addressLine1,
        formData.addressLine2,
        formData.city,
        formData.postalCode,
        formData.country
      ].filter(Boolean)

      const fullAddress = addressParts.join(', ')

      // Supabase signup
      const response = await $fetch('/api/auth/signup', {
        method: 'POST',
        body: {
          email: formData.email,
          password: formData.password,
          name: formData.name || `${formData.firstName} ${formData.lastName}`,
          law_institution: formData.company || 'Kanzlei',
          phone: formData.phone,
          address: fullAddress
        }
      })

      if (!response?.user) {
        errors.email = 'Registrierung fehlgeschlagen'
        return
      }

      if (response.session) {
        await syncSessionFromTokens(response.session, response.user, response.profile ?? null)
      }

      emit('auth-success', {
        user: response.user,
        type: 'signup',
        provider: 'email'
      })
    } else {
      // Supabase login
      const response = await $fetch('/api/auth/signin', {
        method: 'POST',
        body: {
          email: formData.email,
          password: formData.password
        }
      })

      if (!response?.user) {
        errors.email = 'Ungültige E-Mail oder Passwort'
        return
      }

      if (response.session) {
        await syncSessionFromTokens(response.session, response.user, response.profile ?? null)
      }

      emit('auth-success', {
        user: response.user,
        type: 'signin',
        provider: 'email'
      })

      // Redirect to dashboard
      navigateTo('/dashboard')
    }
  } catch (error) {
    console.error('❌ Authentication error:', error)

    // Handle account locked error
    if (error?.statusCode === 429) {
      const remaining = error?.data?.remaining_seconds
      const minutes = remaining ? Math.ceil(remaining / 60) : 15
      errors.email = `Konto gesperrt wegen mehrfacher Fehlversuche. Bitte versuchen Sie es in ${minutes} Minuten erneut.`
      return
    }

    // Map error messages
    const detail = error?.data?.statusMessage || error?.statusMessage || error?.message || ''
    const msg = String(detail).toLowerCase()

    if (isSignUp.value && (msg.includes('already') || msg.includes('exists') || msg.includes('registr'))) {
      errors.email = 'E-Mail ist bereits registriert'
    } else if (!isSignUp.value && msg.includes('invalid')) {
      errors.email = 'Ungültige E-Mail oder Passwort'
    } else {
      errors.email = isSignUp.value ? 'Registrierung fehlgeschlagen' : 'Anmeldung fehlgeschlagen. Bitte versuchen Sie es erneut.'
    }
  } finally {
    loading.value = false
  }
}

const handleGoogleAuth = async () => {
  if (!process.client) {
    console.warn('[OAuth] handleGoogleAuth called on server-side, skipping')
    return
  }

  try {
    loading.value = true

    const authorizeUrl = new URL('/api/auth/google/authorize', window.location.origin).toString()
    window.location.assign(authorizeUrl)
  } catch (error) {
    console.error('Google OAuth error:', error)
    errors.email = 'Google-Anmeldung fehlgeschlagen'
  } finally {
    loading.value = false
  }
}

const handleForgotPassword = async (e) => {
  e.preventDefault()
  try {
    if (!formData.email) {
      errors.email = 'E-Mail ist erforderlich'
      return
    }
    const res = await $fetch('/api/auth/forgot-password', {
      method: 'POST',
      body: { email: formData.email }
    })
    // In dev we may get OTP back for testing
    if (res?.otp && process.dev) {
      console.log('DEV OTP:', res.otp)
    }
    isResetMode.value = true
    alert('Wenn ein Konto existiert, wurde ein Einmal-Code an Ihre E-Mail gesendet.')
  } catch (err) {
    console.error('Forgot password error', err)
    alert('Fehler beim Senden des Einmal-Codes')
  }
}

const enterResetMode = (e) => { e?.preventDefault?.(); isResetMode.value = true }

const handleResetSubmit = async () => {
  try {
    if (!formData.email || !reset.otp || !reset.newPassword) return
    const res = await $fetch('/api/auth/reset-password', {
      method: 'POST',
      body: { email: formData.email, otp: reset.otp, new_password: reset.newPassword }
    })
    // Using basic truthy check without TS syntax for broad build compatibility
    if (res && res.success) {
      isResetMode.value = false
      alert('Passwort erfolgreich zurückgesetzt. Bitte melden Sie sich an.')
    } else {
      alert('Ungültiger Code oder Fehler beim Zurücksetzen')
    }
  } catch (err) {
    console.error('Reset error', err)
    alert('Fehler beim Zurücksetzen des Passworts')
  }
}

// A11y: focus management, trap, and body scroll lock while open
if (process.client) {
  let keydownHandler = null
  const trapFocus = (e) => {
    if (e.key !== 'Tab') return
    const root = document.querySelector('.auth-modal')
    if (!root) return
    const focusable = root.querySelectorAll([
      'a[href]', 'button:not([disabled])', 'textarea', 'input', 'select', '[tabindex]:not([tabindex="-1"])'
    ].join(','))
    if (!focusable.length) return
    const first = focusable[0]
    const last = focusable[focusable.length - 1]
    const active = document.activeElement
    if (e.shiftKey) {
      if (active === first) { e.preventDefault(); last.focus() }
    } else {
      if (active === last) { e.preventDefault(); first.focus() }
    }
  }

  watch(() => props.isOpen, (isOpen) => {
    try { document.body.style.overflow = isOpen ? 'hidden' : '' } catch (_) {}
    if (isOpen) {
      // initial focus
      setTimeout(() => {
        const email = document.getElementById('authEmail')
        if (email) email.focus()
      }, 0)
      // key handlers
      keydownHandler = (e) => {
        if (e.key === 'Escape') emit('close')
        trapFocus(e)
      }
      document.addEventListener('keydown', keydownHandler)
    } else {
      if (keydownHandler) document.removeEventListener('keydown', keydownHandler)
      keydownHandler = null
    }
  }, { immediate: true })
}
</script>

<style scoped>
/* Authentication Modal Overlay */
.auth-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  z-index: 9999;
  animation: fadeIn 0.2s ease-out;
}

/* Ensure overlay only intercepts when visible */
.auth-modal-overlay[hidden], .auth-modal-overlay.hidden { pointer-events: none; }

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Authentication Modal */
.auth-modal {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  padding: 2rem;
  width: 100%;
  max-width: 520px;
  max-height: min(90vh, 760px);
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
  animation: slideIn 0.3s ease-out;
  position: relative;
  z-index: 10000;
  display: flex;
  flex-direction: column;
}

/* Scroll container inside modal to ensure full content is reachable */
.auth-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  flex: 1 1 auto;
  overflow-y: auto;
  padding-right: 6px;
  padding-bottom: 12px;
}
.auth-content::-webkit-scrollbar { width: 8px; }
.auth-content::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.15); border-radius: 999px; }

@keyframes slideIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* Modal Header */
.auth-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.auth-modal-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.auth-modal-close {
  background: none;
  border: none;
  color: rgba(0, 0, 0, 0.5);
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.auth-modal-close:hover {
  color: #1e293b;
  background: rgba(0, 0, 0, 0.05);
}

/* Social Login Section */
.social-login-section {
  margin-bottom: 1.5rem;
}

.social-button {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  margin-bottom: 0.75rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  color: #374151;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.social-button:hover {
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(0, 0, 0, 0.2);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Form Divider */
.auth-divider {
  display: flex;
  align-items: center;
  margin: 1.5rem 0;
  color: #64748b;
  font-size: 0.875rem;
}

.auth-divider::before,
.auth-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: rgba(0, 0, 0, 0.1);
}

.auth-divider span {
  padding: 0 1rem;
}

/* Form Groups */
.auth-form-group {
  margin-bottom: 1rem;
}

.auth-form-label {
  display: block;
  margin-bottom: 0.5rem;
  color: #374151;
  font-size: 0.875rem;
  font-weight: 500;
}

.auth-form-input {
  width: 100%;
  padding: 0.875rem 1rem;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  color: #1e293b;
  font-size: 1rem;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.auth-form-input:focus {
  outline: none;
  border-color: #3b82f6;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.auth-form-input::placeholder {
  color: #94a3b8;
}

/* Form Options */
.auth-form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.auth-checkbox-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #374151;
  cursor: pointer;
}

.auth-checkbox {
  width: 1rem;
  height: 1rem;
}

.auth-link {
  color: #3b82f6;
  text-decoration: none;
  font-size: 0.875rem;
  transition: color 0.2s ease;
}

.auth-link:hover {
  color: #1d4ed8;
  text-decoration: underline;
}

/* Submit Button */
.auth-submit-button {
  width: 100%;
  padding: 0.875rem 1rem;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.auth-submit-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
}

.auth-submit-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

/* Loading Animation */
.auth-loading {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
  margin: 0 auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Form Toggle */
.auth-form-toggle {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.875rem;
  color: #64748b;
}

.auth-form-toggle button {
  background: none;
  border: none;
  color: #3b82f6;
  cursor: pointer;
  margin-left: 0.5rem;
  transition: color 0.2s ease;
}

.auth-form-toggle button:hover {
  color: #1d4ed8;
  text-decoration: underline;
}

.auth-form-toggle-bottom {
  margin-top: 0.5rem;
  padding-top: 0.25rem;
  border-top: 1px dashed rgba(0,0,0,0.08);
}

/* Error Messages */
.auth-error {
  color: #ef4444;
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

/* Quick switch note under header */
.auth-switch-note {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 0.25rem;
  margin-top: -0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: #64748b;
}
.auth-switch-link {
  background: none;
  border: none;
  color: #3b82f6;
  cursor: pointer;
}
.auth-switch-link:hover {
  color: #1d4ed8;
  text-decoration: underline;
}

/* Mobile Responsive */
@media (max-width: 640px) {
  .auth-modal {
    margin: 1rem;
    padding: 1.5rem;
    border-radius: 20px;
  }

  .auth-form-options {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}

/* Form layout helpers */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.auth-form::-webkit-scrollbar { width: 6px; }
.auth-form::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.15); border-radius: 999px; }
.auth-grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
@media (max-width: 640px) {
  .auth-grid-2 { grid-template-columns: 1fr; }
}

/* Sticky actions at the end of the scroll content */
.auth-actions {
  margin-top: 0.5rem;
}

.auth-consent-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}
.auth-consent-checkbox {
  margin-right: 0.25rem;
}
</style>
