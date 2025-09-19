<template>
  <Teleport to="body">
    <Transition name="anwalts-auth-fade">
      <div
        v-if="isOpen"
        class="anwalts-auth-overlay is-open"
        :data-mode="currentMode"
        aria-hidden="false"
        @click.self="requestClose"
      >
        <div
          ref="dialogRef"
          class="anwalts-auth-modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="auth-modal-title"
          tabindex="-1"
        >
          <button type="button" class="anwalts-auth-close" aria-label="Schließen" @click="requestClose">
            <span aria-hidden="true">&times;</span>
          </button>

          <div class="anwalts-auth-header">
            <h2 class="anwalts-auth-title" id="auth-modal-title">{{ copy.title }}</h2>
            <p class="anwalts-auth-subtitle">{{ copy.subtitle }}</p>
          </div>

          <div class="anwalts-auth-toggle">
            <button
              type="button"
              :class="{ 'is-active': currentMode === 'login' }"
              @click="setMode('login')"
            >
              Anmelden
            </button>
            <button
              type="button"
              :class="{ 'is-active': currentMode === 'signup' }"
              @click="setMode('signup')"
            >
              Registrieren
            </button>
          </div>

          <button type="button" class="anwalts-auth-google" @click="handleGoogle">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path fill="#4285f4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="#34a853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#fbbc05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path fill="#ea4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
            <span>Mit Google fortfahren</span>
          </button>

          <div class="anwalts-auth-divider"><span>oder mit E-Mail</span></div>

          <form class="anwalts-auth-form" @submit.prevent="handleSubmit">
            <div class="anwalts-auth-field" data-auth-section="signup">
              <label for="auth-name">Vollständiger Name</label>
              <input
                id="auth-name"
                ref="nameRef"
                v-model.trim="form.name"
                name="name"
                type="text"
                autocomplete="name"
                placeholder="Dr. Max Müller"
              />
            </div>

            <div class="anwalts-auth-field">
              <label for="auth-email">E-Mail-Adresse</label>
              <input
                id="auth-email"
                ref="emailRef"
                v-model.trim="form.email"
                name="email"
                type="email"
                autocomplete="email"
                placeholder="kanzlei@example.de"
                required
              />
            </div>

            <div class="anwalts-auth-field">
              <label for="auth-password">Passwort</label>
              <input
                id="auth-password"
                ref="passwordRef"
                v-model="form.password"
                name="password"
                type="password"
                autocomplete="current-password"
                placeholder="••••••••"
                required
              />
            </div>

            <div class="anwalts-auth-field" data-auth-section="signup">
              <label for="auth-confirm">Passwort bestätigen</label>
              <input
                id="auth-confirm"
                ref="confirmRef"
                v-model="form.confirm"
                name="confirm"
                type="password"
                autocomplete="new-password"
                placeholder="Passwort bestätigen"
              />
            </div>

            <label class="anwalts-auth-checkbox" data-auth-section="signup">
              <input v-model="form.terms" type="checkbox" name="terms" />
              <span>
                Ich stimme den
                <NuxtLink to="/terms" target="_blank">AGB</NuxtLink>
                und
                <NuxtLink to="/privacy" target="_blank">Datenschutzbestimmungen</NuxtLink>
                zu.
              </span>
            </label>

            <div class="anwalts-auth-error" role="alert" aria-live="polite">{{ errorMessage }}</div>
            <div class="anwalts-auth-message" aria-live="polite">{{ statusMessage }}</div>

            <button type="submit" class="anwalts-auth-submit" :disabled="submitting">
              {{ submitting ? copy.submitBusy : copy.submit }}
            </button>
          </form>

          <div class="anwalts-auth-footer">
            <span>{{ copy.footerPrompt }}</span>
            <button type="button" @click="toggleMode">{{ copy.footerCta }}</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, reactive, ref, watch } from 'vue'
import { useNuxtApp } from '#app'

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  mode: { type: String, default: 'login' }
})

const emit = defineEmits<{ (e: 'close'): void; (e: 'auth-success'): void }>()

const dialogRef = ref<HTMLElement | null>(null)
const nameRef = ref<HTMLInputElement | null>(null)
const emailRef = ref<HTMLInputElement | null>(null)
const passwordRef = ref<HTMLInputElement | null>(null)
const confirmRef = ref<HTMLInputElement | null>(null)

const currentMode = ref<Mode>(normalizeMode(props.mode))
const submitting = ref(false)
const errorMessage = ref('')
const statusMessage = ref('')
let lastFocused: HTMLElement | null = null

const form = reactive({
  name: '',
  email: '',
  password: '',
  confirm: '',
  terms: false
})

const GOOGLE_REDIRECT = '/auth/google/authorize?redirect=/dashboard'
const { $fetch } = useNuxtApp()

type Mode = 'login' | 'signup'

watch(
  () => props.mode,
  (value) => {
    const normalized = normalizeMode(value)
    if (normalized !== currentMode.value) {
      currentMode.value = normalized
      clearMessages()
      focusField()
    }
  }
)

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      lastFocused = document.activeElement instanceof HTMLElement ? document.activeElement : null
      document.body.classList.add('anwalts-auth-modal-open')
      nextTick(() => {
        focusField()
        document.addEventListener('keydown', handleKeydown, true)
      })
    } else {
      document.body.classList.remove('anwalts-auth-modal-open')
      document.removeEventListener('keydown', handleKeydown, true)
      if (lastFocused) {
        try { lastFocused.focus() } catch (error) { console.debug(error) }
      }
      lastFocused = null
      clearMessages()
      resetIfNeeded()
    }
  }
)

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeydown, true)
})

const isOpen = computed(() => props.isOpen)

const copy = computed(() => {
  if (currentMode.value === 'signup') {
    return {
      title: 'Konto erstellen',
      subtitle: 'Registrieren Sie sich kostenlos und starten Sie mit ANWALTS.AI.',
      submit: 'Registrieren',
      submitBusy: 'Registrieren…',
      footerPrompt: 'Bereits Kunde?',
      footerCta: 'Jetzt anmelden'
    }
  }
  return {
    title: 'Willkommen zurück',
    subtitle: 'Melden Sie sich an, um Ihr Kanzlei-Dashboard zu öffnen.',
    submit: 'Anmelden',
    submitBusy: 'Anmelden…',
    footerPrompt: 'Neu bei ANWALTS.AI?',
    footerCta: 'Jetzt registrieren'
  }
})

function requestClose() {
  emit('close')
}

function toggleMode() {
  setMode(currentMode.value === 'login' ? 'signup' : 'login')
}

function setMode(mode: Mode) {
  if (currentMode.value === mode) return
  currentMode.value = mode
  clearMessages()
  focusField()
}

function clearMessages() {
  errorMessage.value = ''
  statusMessage.value = ''
}

function focusField() {
  nextTick(() => {
    if (!isOpen.value) return
    if (currentMode.value === 'signup' && nameRef.value) {
      nameRef.value.focus()
      return
    }
    if (emailRef.value) {
      emailRef.value.focus()
    }
  })
}

function handleGoogle() {
  window.location.href = GOOGLE_REDIRECT
}

async function handleSubmit() {
  if (submitting.value) return
  clearMessages()

  const email = form.email.trim().toLowerCase()
  const password = form.password

  if (!/.+@.+\..+/.test(email)) {
    errorMessage.value = 'Bitte geben Sie eine gültige E-Mail-Adresse ein.'
    focusField()
    return
  }

  if (!password || password.length < 6) {
    errorMessage.value = 'Bitte geben Sie ein Passwort mit mindestens 6 Zeichen ein.'
    if (passwordRef.value) passwordRef.value.focus()
    return
  }

  if (currentMode.value === 'signup') {
    if (!form.name.trim()) {
      errorMessage.value = 'Bitte geben Sie Ihren Namen an.'
      if (nameRef.value) nameRef.value.focus()
      return
    }
    if (!form.confirm || form.confirm !== password) {
      errorMessage.value = 'Bitte bestätigen Sie Ihr Passwort.'
      if (confirmRef.value) confirmRef.value.focus()
      return
    }
    if (!form.terms) {
      errorMessage.value = 'Bitte akzeptieren Sie die Bedingungen.'
      return
    }
  }

  try {
    submitting.value = true
    if (currentMode.value === 'signup') {
      await submitSignup(email, password)
    } else {
      await submitLogin(email, password)
    }
    statusMessage.value = 'Weiterleitung zum Dashboard …'
    emit('auth-success')
  } catch (error: any) {
    errorMessage.value = error?.message || 'Vorgang fehlgeschlagen.'
  } finally {
    submitting.value = false
  }
}

async function submitLogin(email: string, password: string) {
  try {
    const response: any = await $fetch('/auth/login', {
      method: 'POST',
      credentials: 'include',
      body: { email, password }
    })
    if (!response || response?.success === false || response?.error) {
      throw new Error(response?.error || 'Anmeldung fehlgeschlagen.')
    }
    const token = response.token || response.access_token
    if (!token) throw new Error('Token konnte nicht erstellt werden.')
    persistSession(token, response.user || { email })
    window.location.href = '/dashboard'
  } catch (error: any) {
    const message = resolveErrorMessage(error)
    throw new Error(message || 'Anmeldung fehlgeschlagen.')
  }
}

async function submitSignup(email: string, password: string) {
  try {
    const response: any = await $fetch('/auth/register', {
      method: 'POST',
      credentials: 'include',
      body: { email, name: form.name.trim(), password }
    })
    if (response?.error || response?.detail) {
      throw new Error(response.error || response.detail)
    }
    await submitLogin(email, password)
  } catch (error: any) {
    const message = resolveErrorMessage(error)
    throw new Error(message || 'Registrierung fehlgeschlagen.')
  }
}

function persistSession(token: string, user: any) {
  try {
    localStorage.setItem('anwalts_auth_token', token)
    if (user) localStorage.setItem('anwalts_user', JSON.stringify(user))
  } catch (error) {
    console.debug('localStorage unavailable', error)
  }

  const maxAge = 60 * 60 * 24
  const cookie = `sat=${encodeURIComponent(token)}; path=/; max-age=${maxAge}; secure; samesite=None`
  document.cookie = cookie
  try {
    const host = window.location.hostname.split('.')
    if (host.length > 2) {
      const domain = '.' + host.slice(-2).join('.')
      document.cookie = `${cookie}; domain=${domain}`
    }
  } catch (error) {
    console.debug('cookie domain fallback', error)
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (!isOpen.value || !dialogRef.value) return
  if (event.key === 'Escape') {
    event.preventDefault()
    requestClose()
    return
  }
  if (event.key !== 'Tab') return

  const focusable = Array.from(dialogRef.value.querySelectorAll<HTMLElement>(
    'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
  )).filter((el) => el.offsetParent !== null)

  if (!focusable.length) {
    event.preventDefault()
    return
  }

  const first = focusable[0]
  const last = focusable[focusable.length - 1]

  if (event.shiftKey) {
    if (document.activeElement === first) {
      event.preventDefault()
      last.focus()
    }
  } else if (document.activeElement === last) {
    event.preventDefault()
    first.focus()
  }
}

function resolveErrorMessage(error: any) {
  if (!error) return ''
  if (typeof error === 'string') return error
  if (error?.data?.error) return error.data.error
  if (error?.data?.detail) return error.data.detail
  if (error?.statusMessage) return error.statusMessage
  if (error?.message) return error.message
  return ''
}

function resetIfNeeded() {
  if (currentMode.value === 'login') return
  form.confirm = ''
}

function normalizeMode(value: string): Mode {
  const lowered = (value || '').toLowerCase()
  return lowered === 'signup' || lowered === 'register' || lowered === 'sign-up' ? 'signup' : 'login'
}
</script>

<style>
@import url('/shared/anwalts-auth.css');

.anwalts-auth-fade-enter-active,
.anwalts-auth-fade-leave-active {
  transition: opacity 0.18s ease;
}

.anwalts-auth-fade-enter-from,
.anwalts-auth-fade-leave-to {
  opacity: 0;
}
</style>
