<template>
  <div class="min-h-screen bg-slate-950 bg-gradient-to-br from-slate-900 via-slate-950 to-blue-950 text-white flex flex-col">
    <header class="py-6 px-6 sm:px-8 flex items-center justify-between">
      <NuxtLink to="/" class="flex items-center gap-3 text-white/90 hover:text-white transition">
        <img src="/favicon.png" alt="ANWALTS.AI" class="h-8 w-8 rounded" />
        <span class="font-semibold tracking-wide">ANWALTS.AI</span>
      </NuxtLink>
      <NuxtLink to="/" class="text-sm text-white/60 hover:text-white transition">Zurück zur Startseite</NuxtLink>
    </header>

    <main class="flex-1 flex items-center justify-center px-6 pb-20">
      <div class="w-full max-w-lg bg-white/5 backdrop-blur-md border border-white/10 rounded-3xl p-8 shadow-xl">
        <h1 class="text-3xl font-semibold text-white mb-3">Melden Sie sich an</h1>
        <p class="text-white/70 text-sm leading-relaxed mb-8">
          Nutzen Sie Ihren Google-Account oder Ihre Zugangsdaten, um das ANWALTS.AI Dashboard zu öffnen.
          Ihre Sitzung bleibt geschützt durch sichere Cookies (HttpOnly, SameSite=None).
        </p>

        <div class="space-y-3">
          <button
            type="button"
            class="w-full flex items-center justify-center gap-3 py-3 rounded-xl bg-white text-slate-900 font-medium shadow hover:bg-slate-100 transition"
            @click="triggerModal('login')"
          >
            <svg class="h-5 w-5" viewBox="0 0 24 24" aria-hidden="true"><path fill="#4285f4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34a853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#fbbc05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#ea4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
            <span>Mit Google anmelden</span>
          </button>
          <button
            type="button"
            class="w-full py-3 rounded-xl border border-white/20 text-white font-medium hover:border-white/40 transition"
            @click="triggerModal('signup')"
          >Kostenlos registrieren</button>
        </div>

        <div class="mt-10 text-xs text-white/50 leading-relaxed">
          <p>
            Sie werden zum sicheren ANWALTS.AI Auth-Dialog weitergeleitet. Nach erfolgreichem Login bringen wir Sie automatisch zurück zu:
            <span class="text-white/80 break-words">{{ decodedRedirect }}</span>
          </p>
          <p class="mt-3">
            Bei Problemen wenden Sie sich bitte an <a href="mailto:support@anwalts.ai" class="underline text-white">support@anwalts.ai</a>.
          </p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from '#imports'

definePageMeta({ layout: false })

const route = useRoute()
const router = useRouter()
const redirectParam = computed(() => route.query.redirect || '/dashboard')
const decodedRedirect = computed(() => {
  try {
    return decodeURIComponent(String(redirectParam.value))
  } catch (_) {
    return '/dashboard'
  }
})

const triggerModal = (mode = 'login') => {
  if (typeof window === 'undefined') return
  const normalized = ['signup', 'register'].includes(String(mode).toLowerCase()) ? 'signup' : 'login'
  if (typeof window.openAuthModal === 'function') {
    window.openAuthModal(normalized)
    return
  }
  try {
    window.postMessage({ type: 'ANWALTS_OPEN_AUTH', mode: normalized }, '*')
  } catch (_) {}
}

onMounted(() => {
  triggerModal(route.query.mode === 'signup' ? 'signup' : 'login')
  const onBridgeReady = () => triggerModal(route.query.mode === 'signup' ? 'signup' : 'login')
  window.addEventListener('anwalts-auth-bridge-ready', onBridgeReady, { once: true })

  if (route.query.redirect && !String(route.query.redirect).startsWith('/')) {
    router.replace({ query: { ...route.query, redirect: '/dashboard' } })
  }
})
</script>
