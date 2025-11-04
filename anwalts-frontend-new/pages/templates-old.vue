<template>
  <div>
    <!-- Header -->
    <header class="px-6 py-4 bg-white border-b border-gray-200">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h.01M12 17h.01M7 17h.01M7 12h10M7 7h10M5 5h14a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2z"/></svg>
          </div>
          <div>
            <h1 class="text-xl font-semibold text-gray-900">Vorlagenbibliothek</h1>
            <p class="text-xs text-gray-500">Professionelle Rechtsdokument?Vorlagen, abgestimmt auf die Kanzlei</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <NuxtLink to="/documents" class="px-3 py-2 rounded-md text-sm bg-blue-600 text-white hover:bg-blue-700">Dokumente</NuxtLink>
        </div>
      </div>
    </header>

    <!-- Content -->
    <main class="max-w-7xl mx-auto p-6">
      <!-- Tools -->
      <div class="mb-4 flex flex-col md:flex-row md:items-center gap-3">
        <div class="flex-1">
          <input v-model="q" type="search" placeholder="Suchen (Titel, Kategorie, Beschreibung)?" class="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:border-blue-500 focus:ring-blue-500" />
        </div>
        <div class="flex items-center gap-2">
          <button class="px-3 py-2 rounded-md text-sm border border-gray-300 bg-white hover:bg-gray-100" @click="clearSearch">Zur?cksetzen</button>
          <NuxtLink to="/documents" class="px-3 py-2 rounded-md text-sm bg-blue-600 text-white hover:bg-blue-700">Neues Dokument</NuxtLink>
        </div>
      </div>

      <!-- Loading / Error states -->
      <div v-if="pending" class="p-6 bg-white rounded-lg border border-gray-200 text-gray-600">Lade Vorlagen?</div>
      <div v-else-if="error" class="p-6 bg-white rounded-lg border border-gray-200 text-red-600">Fehler beim Laden der Vorlagen</div>

      <!-- Empty state -->
      <div v-else-if="filtered.length === 0" class="p-10 bg-white rounded-lg border border-gray-200 text-center">
        <div class="mx-auto w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center mb-3">
          <svg class="w-6 h-6 text-blue-600" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
        </div>
        <div class="text-gray-900 font-medium">Keine Vorlagen gefunden</div>
        <div class="text-gray-600 text-sm">Passen Sie Ihre Suche an oder f?gen Sie neue Vorlagen hinzu.</div>
      </div>

      <!-- Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <article v-for="t in filtered" :key="t.id" class="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-lg transition-shadow flex flex-col">
          <div class="p-4 flex-1 flex flex-col">
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <h3 class="text-gray-900 font-medium truncate" :title="t.name || t.title">{{ t.name || t.title }}</h3>
                <p class="text-xs text-gray-500 line-clamp-2" v-if="desc(t)">{{ desc(t) }}</p>
              </div>
              <span class="inline-block px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-600 flex-shrink-0" v-if="t.category">{{ t.category }}</span>
            </div>
            <div class="mt-3 text-xs text-gray-500 flex items-center gap-3">
              <span v-if="t.usage_count">Verwendet {{ t.usage_count }}?</span>
              <span v-if="t.type">Typ: {{ t.type }}</span>
            </div>
          </div>
          <div class="px-4 py-3 border-t border-gray-200 flex items-center gap-2">
            <button class="px-3 py-2 rounded-md text-sm border border-gray-300 bg-white hover:bg-gray-100" @click="preview(t)">Vorschau</button>
            <button class="ml-auto px-3 py-2 rounded-md text-sm bg-blue-600 text-white hover:bg-blue-700" @click="useTemplate(t)">Verwenden</button>
          </div>
        </article>
      </div>
    </main>

    <!-- Simple preview modal -->
    <div v-if="showPreview" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg shadow-lg w-full max-w-2xl">
        <div class="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <div class="font-medium text-gray-900 truncate" :title="current?.name || current?.title">{{ current?.name || current?.title }}</div>
          <button class="text-sm text-gray-500 hover:text-gray-700" @click="closePreview">Schlie?en</button>
        </div>
        <div class="p-4">
          <div class="prose max-w-none text-sm" v-html="(current?.content || '').slice(0, 3000)"></div>
        </div>
        <div class="px-4 py-3 border-t border-gray-200 flex items-center gap-2">
          <button class="px-3 py-2 rounded-md text-sm border border-gray-300 bg-white hover:bg-gray-100" @click="closePreview">Abbrechen</button>
          <button class="ml-auto px-3 py-2 rounded-md text-sm bg-blue-600 text-white hover:bg-blue-700" @click="useTemplate(current)">Verwenden</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const q = ref('')
const items = ref<any[]>([])
const pending = ref(true)
const error = ref<Error | null>(null)

function desc(t: any): string {
  return (t.description || t.prompt || (t.content ? String(t.content).replace(/<[^>]+>/g, ' ') : '') || '').trim()
}

const filtered = computed(() => {
  const s = q.value.trim().toLowerCase()
  if (!s) return items.value
  return items.value.filter((t) => {
    const hay = [t.name, t.title, t.category, desc(t)].join(' ').toLowerCase()
    return hay.includes(s)
  })
})

const showPreview = ref(false)
const current = ref<any | null>(null)

function preview(t: any) {
  current.value = t
  showPreview.value = true
}
function closePreview() { showPreview.value = false; current.value = null }

function clearSearch() { q.value = '' }

function useTemplate(t: any) {
  try { localStorage.setItem('anwalt.templateId', String(t.id || t.key || t.slug || '')) } catch {}
  // Optionally also store minimal context for better UX
  try { localStorage.setItem('anwalt.templateTitle', String(t.name || t.title || '')) } catch {}
  router.push('/documents')
}

onMounted(async () => {
  try {
    const res = await fetch('/api/auth/proxy?path=/api/templates', { credentials: 'include' })
    if (!res.ok) throw new Error('HTTP ' + res.status)
    const data = await res.json()
    items.value = Array.isArray(data) ? data : []
  } catch (e: any) {
    error.value = e
  } finally {
    pending.value = false
  }
})
</script>

<style scoped>
.prose :where(p, ul, ol, h1, h2, h3, h4){
  margin: 0 0 0.75rem 0;
}
.line-clamp-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
</style>

