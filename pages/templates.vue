<template>
  <div class="max-w-6xl mx-auto p-6">
    <div class="flex items-center justify-between mb-4">
      <div>
        <h1 class="text-xl font-semibold text-gray-900">Vorlagen</h1>
        <p class="text-sm text-gray-500">Eigene und geteilte Textbausteine verwalten.</p>
      </div>
      <button id="btnCreateTemplate" class="btn-primary" @click="open = true">Neue Vorlage</button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="t in templates" :key="t.id" class="card">
        <div class="card-header">
          <div>
            <div class="card-title">{{ t.name }}</div>
            <div class="text-xs text-gray-500">{{ t.category || 'Allgemein' }}</div>
          </div>
          <button class="btn-text" @click="openDetails(t)">Details</button>
        </div>
        <div class="p-3 text-sm text-gray-700 truncate">{{ t.content?.slice(0, 160) }}</div>
      </div>
    </div>

    <dialog v-if="open" open class="p-0 rounded-lg border border-gray-200 w-full max-w-lg shadow-xl">
      <form @submit.prevent="create" class="p-4 space-y-3">
        <div class="text-lg font-semibold">Neue Vorlage erstellen</div>
        <input v-model="form.name" placeholder="Name" class="input-field w-full" required />
        <input v-model="form.category" placeholder="Kategorie (optional)" class="input-field w-full" />
        <textarea v-model="form.content" placeholder="Inhalt" class="input-field w-full h-40" required></textarea>
        <div class="flex justify-end gap-2 pt-2">
          <button type="button" class="btn-secondary" @click="open=false">Abbrechen</button>
          <button type="submit" class="btn-primary" :disabled="busy">{{ busy ? 'Speichern…' : 'Erstellen' }}</button>
        </div>
      </form>
    </dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

const templates = ref<any[]>([])
const open = ref(false)
const busy = ref(false)
const form = ref({ name: '', category: '', content: '', type: 'document' })

const load = async () => {
  try{
    const r = await fetch(`/api/auth/proxy.get?path=${encodeURIComponent('/api/templates')}`)
    const data = await r.json().catch(()=>({ items: [] }))
    templates.value = Array.isArray(data?.items) ? data.items : (Array.isArray(data) ? data : [])
  }catch(e){ console.warn('load templates failed', e) }
}

const create = async () => {
  busy.value = true
  try{
    const payload = { path: '/api/templates', method: 'POST', body: { name: form.value.name, content: form.value.content, category: form.value.category || 'general', type: 'document' } }
    const r = await fetch('/api/auth/proxy.post', { method:'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
    if (r.ok) { open.value = false; form.value = { name:'',category:'',content:'', type:'document' } as any; await load() }
  }catch(e){ console.warn('create template failed', e) }
  finally{ busy.value = false }
}

const openDetails = (t:any) => {
  alert(`Vorlage: ${t.name}\nKategorie: ${t.category || ''}`)
}

onMounted(load)
</script>