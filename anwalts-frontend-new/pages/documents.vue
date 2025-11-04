<template>
  <PortalShell>
    <template #header>
      <header class="bg-white border-b border-slate-200">
        <div class="mx-auto max-w-7xl px-6 py-5 lg:px-10">
          <div class="inline-flex items-center rounded-full bg-indigo-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-wide text-indigo-600">
            Dokumente
          </div>
          <h1 class="mt-3 text-2xl font-semibold text-slate-900">Rechtsdokument-Assistent</h1>
          <p class="mt-2 max-w-2xl text-sm text-slate-600">
            Erstellen und verfeinern Sie juristische Dokumente mit einem Klick.
          </p>
        </div>
      </header>
    </template>


    <main class="bg-slate-50 pb-16">
      <div class="mx-auto max-w-7xl space-y-8 px-6 pt-6 lg:px-10">
        <section class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(0,1.35fr)]">
          <div class="space-y-6">
            <section class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">Ablauf</h2>
              <div class="mt-4 grid gap-3 sm:grid-cols-3">
                <div
                  v-for="step in workflowSteps"
                  :key="step.number"
                  class="flex items-start gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 transition hover:border-indigo-200 hover:bg-white"
                >
                  <div class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-indigo-100 text-sm font-semibold text-indigo-700">
                    {{ step.number }}
                  </div>
                  <div class="space-y-1">
                    <p class="text-sm font-semibold text-slate-900">{{ step.title }}</p>
                    <p class="text-xs text-slate-600">{{ step.description }}</p>
                  </div>
                </div>
              </div>
            </section>

            <section class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <header class="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 class="text-sm font-semibold text-slate-900">Dokument-Basisdaten</h2>
                  <p class="text-xs text-slate-500">Titel, Tonalität und Ausgangsinformationen</p>
                </div>
                <button
                  type="button"
                  class="text-xs font-medium text-indigo-600 hover:text-indigo-500"
                  @click="resetForm"
                >
                  Zurücksetzen
                </button>
              </header>

              <div class="mt-4 space-y-4">
                <label class="block text-sm font-medium text-slate-700">
                  Dokumenttyp
                  <input
                    v-model="form.docType"
                    type="text"
                    placeholder="z. B. Mietvertrag, Abmahnung, Vergleich"
                    class="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                  >
                </label>

                <div class="grid gap-3 rounded-xl border border-slate-100 bg-slate-50/80 p-3">
                  <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Tonalität</p>
                  <div class="flex flex-wrap gap-3">
                    <button
                      type="button"
                      :class="toneButtonClass('legal')"
                      @click="setTone('legal')"
                    >
                      Juristisch präzise
                    </button>
                    <button
                      type="button"
                      :class="toneButtonClass('legal+plain')"
                      @click="setTone('legal+plain')"
                    >
                      Juristisch &amp; verständlich
                    </button>
                    <button
                      type="button"
                      :class="toneButtonClass('plain')"
                      @click="setTone('plain')"
                    >
                      Leichte Sprache
                    </button>
                    <button
                      type="button"
                      :class="toneButtonClass('neutral')"
                      @click="setTone('neutral')"
                    >
                      Neutral
                    </button>
                  </div>
                </div>
              </div>
            </section>

            <section class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <header class="mb-4 flex items-center justify-between">
                <div>
                  <h2 class="text-sm font-semibold text-slate-900">Uploads</h2>
                  <p class="text-xs text-slate-500">Dateien hinzufügen – vertraulich verarbeitet</p>
                </div>
                <button
                  v-if="uploadState.id"
                  type="button"
                  class="text-xs font-medium text-indigo-600 hover:text-indigo-500"
                  @click="clearUpload"
                >
                  Entfernen
                </button>
              </header>
              <div>
                <label
                  for="fileInput"
                  class="group relative flex cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-slate-300 bg-white px-6 py-10 text-center transition hover:border-indigo-300 hover:bg-indigo-50"
                  @dragover.prevent="isDragActive = true"
                  @dragleave="isDragActive = false"
                  @drop.prevent="handleDrop"
                  :class="{ 'border-indigo-400 bg-indigo-50': isDragActive }"
                >
                  <input
                    id="fileInput"
                    ref="fileInputRef"
                    type="file"
                    class="hidden"
                    accept=".pdf,.doc,.docx,.txt"
                    @change="handleFileChange"
                  >
                  <svg class="h-10 w-10 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                  </svg>
                  <div>
                    <p class="text-sm font-medium text-slate-900">
                      <span class="text-indigo-600">Datei hier ablegen</span> oder klicken
                    </p>
                    <p class="text-xs text-slate-500">PDF, DOC, DOCX oder TXT · max. 10 MB</p>
                  </div>
                </label>
                <p v-if="uploadState.fileName" class="mt-3 flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 text-xs text-slate-600">
                  <span class="truncate font-medium text-slate-700">{{ uploadState.fileName }}</span>
                  <span>{{ uploadState.fileSize }}</span>
                </p>
                <p v-if="uploadState.error" class="mt-2 text-xs text-red-600">{{ uploadState.error }}</p>
              </div>
            </section>

            <section class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <div class="flex flex-col gap-6">
                <div>
                  <header class="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <h2 class="text-sm font-semibold text-slate-900">Klauselbausteine</h2>
                      <p class="text-xs text-slate-500">Relevante Kategorien auswählen</p>
                    </div>
                    <button
                      type="button"
                      class="text-xs font-medium text-indigo-600 hover:text-indigo-500"
                      @click="refreshClauses"
                    >
                      Aktualisieren
                    </button>
                  </header>
                  <p v-if="clauseMessage" class="mt-3 text-xs text-slate-500">{{ clauseMessage }}</p>
                  <div class="mt-3 flex flex-wrap gap-2">
                    <button
                      v-for="clause in clauses"
                      :key="clause.id"
                      type="button"
                      @click="toggleClause(clause.title)"
                      :class="clauseChipClass(clause.title)"
                    >
                      {{ clause.title }}
                    </button>
                  </div>
                  <div
                    v-if="featuredTemplates.length"
                    class="mt-4 rounded-xl border border-slate-100 bg-slate-50/80 p-3"
                  >
                    <div class="flex flex-wrap items-center justify-between gap-2">
                      <p class="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Empfohlene Vorlagen</p>
                      <span class="text-[11px] font-medium text-slate-400">
                        {{ templates.length }} verfügbar
                      </span>
                    </div>
                    <p v-if="templateMessage" :class="templateMessageTone" class="mt-1">
                      {{ templateMessage }}
                    </p>
                    <div class="mt-3 grid gap-2 sm:grid-cols-2">
                      <button
                        v-for="template in featuredTemplates"
                        :key="template.id"
                        type="button"
                        class="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-3 py-2 text-left text-sm font-medium text-slate-700 transition hover:border-indigo-300 hover:bg-indigo-50"
                        @click="goToTemplates(template)"
                      >
                        <span class="truncate">{{ template.title }}</span>
                        <span class="text-xs font-semibold text-indigo-500">Öffnen →</span>
                      </button>
                    </div>
                  </div>
                </div>

                <div class="border-t border-slate-100 pt-5">
                  <header class="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <h3 class="text-sm font-semibold text-slate-900">Sachverhalt &amp; Vorgaben</h3>
                      <p class="text-xs text-slate-500">Beschreiben Sie Ziele, Klauseln oder Besonderheiten</p>
                    </div>
                    <button
                      type="button"
                      class="text-xs font-medium text-indigo-600 hover:text-indigo-500"
                      @click="insertChecklist"
                    >
                      Checkliste einfügen
                    </button>
                  </header>
                  <label class="mt-4 block">
                    <span class="sr-only">Sachverhalt &amp; Vorgaben</span>
                    <textarea
                      v-model="form.requirements"
                      placeholder="Beschreiben Sie den Sachverhalt, gewünschte Klauseln oder Besonderheiten..."
                      rows="6"
                      class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-900 shadow-sm focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                    ></textarea>
                    <div class="mt-2 text-right text-xs text-slate-500">
                      {{ form.requirements.length }} Zeichen
                    </div>
                  </label>
                </div>
              </div>
            </section>

            <section class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 class="text-sm font-semibold text-slate-900">Erstellung</h2>
              <p class="mt-1 text-xs text-slate-500">Dokument generieren oder KI-Analyse starten</p>
              <div class="mt-4 flex flex-col gap-2 sm:flex-row">
                <button
                  type="button"
                  class="inline-flex flex-1 items-center justify-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200 disabled:cursor-not-allowed disabled:bg-indigo-300"
                  :disabled="!canGenerate || isGenerating"
                  @click="generateDocument"
                >
                  <span v-if="isGenerating" class="h-4 w-4 animate-spin rounded-full border-2 border-white/70 border-t-transparent"></span>
                  {{ isGenerating ? 'Generierung läuft…' : 'Dokument generieren' }}
                </button>
                <button
                  type="button"
                  class="inline-flex flex-1 items-center justify-center rounded-xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-slate-300 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-100 disabled:cursor-not-allowed disabled:text-slate-400"
                  :disabled="isGenerating || !previewHtml"
                  @click="runAnalysis"
                >
                  KI-Analyse starten
                </button>
              </div>
              <p class="mt-3 text-[11px] text-slate-500">
                <kbd class="rounded bg-slate-100 px-1">Strg</kbd> + <kbd class="rounded bg-slate-100 px-1">Enter</kbd> für eine schnelle Neu-Generierung.
              </p>
            </section>
          </div>

          <div class="space-y-6 xl:col-span-1 xl:sticky xl:top-20">
            <div
              v-if="processingState !== 'idle'"
              class="flex items-center gap-3 rounded-2xl border border-indigo-100 bg-indigo-50 px-5 py-4 text-sm text-indigo-900 shadow-sm"
            >
              <span v-if="processingState === 'running'" class="h-3 w-3 animate-pulse rounded-full bg-indigo-500"></span>
              <span v-else-if="processingState === 'success'" class="h-3 w-3 rounded-full bg-green-500"></span>
              <span v-else class="h-3 w-3 rounded-full bg-red-500"></span>
              <div>
                <p class="font-semibold">{{ processingMessage }}</p>
                <p v-if="processingSubtext" class="text-xs text-indigo-700">{{ processingSubtext }}</p>
              </div>
            </div>

            <section class="rounded-2xl border border-slate-200 bg-white shadow-sm">
              <header class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 px-6 py-4">
                <div>
                  <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Vorschau</p>
                  <p class="text-sm font-semibold text-slate-900">
                    {{ form.docType || 'Neues Rechtsdokument' }}
                  </p>
                </div>
                <div class="flex flex-wrap items-center gap-2 text-xs text-slate-500">
                  <span>{{ wordCount }} Wörter</span>
                  <span class="text-slate-300">•</span>
                  <span>{{ selectedClauses.length }} Klauseln</span>
                  <span class="text-slate-300">•</span>
                  <span>{{ qualityBadge }}</span>
                </div>
              </header>

              <div class="space-y-4 px-6 py-5">
                <div class="flex flex-wrap items-center gap-2">
                  <button
                    type="button"
                    class="feedback-button"
                    :class="{ 'feedback-button--active': feedbackSelection === 'accepted' }"
                    @click="submitFeedback('accepted')"
                    :disabled="!currentDocument.id"
                  >
                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span>Freigeben</span>
                  </button>
                  <button
                    type="button"
                    class="feedback-button"
                    :class="{ 'feedback-button--active': feedbackSelection === 'rejected' }"
                    @click="submitFeedback('rejected')"
                    :disabled="!currentDocument.id"
                  >
                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12c0 4.418-4.03 8-9 8s-9-3.582-9-8 4.03-8 9-8 9 3.582 9 8z" />
                    </svg>
                    <span>Überarbeiten</span>
                  </button>
                  <button
                    type="button"
                    class="feedback-button"
                    @click="regenerateDocument"
                    :disabled="isGenerating || !canGenerate"
                  >
                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.5 12a7.5 7.5 0 0112.65-5.303" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.5 12a7.5 7.5 0 01-12.65 5.303" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16.15 5.2L17 3v3.5h-3.5l1.2-1.3" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7.85 18.8L7 21v-3.5h3.5l-1.2 1.3" />
                    </svg>
                    <span>Erneut generieren</span>
                  </button>
                  <span class="flex-1"></span>
                  <button
                    type="button"
                    class="toolbar-button"
                    @click="copyPreview"
                    :disabled="!previewHtml"
                  >
                    <span>Kopieren</span>
                  </button>
                  <button
                    type="button"
                    class="toolbar-button"
                    @click="toggleEditing"
                    :disabled="!previewHtml"
                  >
                    {{ isEditingPreview ? 'Bearbeitung sperren' : 'Direkt bearbeiten' }}
                  </button>
                  <button
                    type="button"
                    class="toolbar-button"
                    @click="saveDocument"
                    :disabled="isSaving || !previewHtml"
                  >
                    {{ isSaving ? 'Speichere…' : 'Speichern' }}
                  </button>
                  <button
                    type="button"
                    class="toolbar-button"
                    @click="exportPdf"
                    :disabled="!previewHtml"
                  >
                    PDF exportieren
                  </button>
                </div>

                <p v-if="feedbackStatus.message" :class="feedbackStatusClass" class="text-xs">
                  {{ feedbackStatus.message }}
                </p>

                <div
                  v-if="previewHtml"
                  ref="previewContainer"
                  class="preview-surface"
                  :class="{ 'preview-surface--editing': isEditingPreview }"
                  contenteditable="false"
                  @input="syncPreviewFromDom"
                  v-html="previewHtml"
                ></div>
                <div
                  v-else
                  class="flex min-h-[360px] flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-slate-200 bg-slate-50 text-center"
                >
                  <svg class="h-12 w-12 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 21h8m-4-4v4m0-4l-3-3m3 3l3-3M4 13l1.375-5.5a2 2 0 011.938-1.5H8m0 0l.879-3.515A1 1 0 019.857 2h4.286a1 1 0 01.978.79L16 6h.687a2 2 0 011.938 1.5L20 13" />
                  </svg>
                  <p class="text-sm font-semibold text-slate-700">Noch kein Entwurf</p>
                  <p class="max-w-sm text-xs text-slate-500">Füllen Sie links den Sachverhalt aus und klicken Sie auf „Dokument generieren“, um den ersten Entwurf zu erstellen.</p>
                  <button
                    type="button"
                    class="mt-1 inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-sm transition hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-200 disabled:cursor-not-allowed disabled:bg-indigo-300"
                    :disabled="!canGenerate || isGenerating"
                    @click="generateDocument"
                  >
                    Jetzt generieren
                  </button>
                </div>
              </div>
            </section>

            <div v-if="analysisSnapshot" class="rounded-2xl border border-emerald-100 bg-emerald-50 p-6 shadow-sm">
              <header class="mb-3 flex items-center justify-between">
                <div>
                  <p class="text-xs font-semibold uppercase tracking-wide text-emerald-600">Analyse</p>
                  <h3 class="text-sm font-semibold text-emerald-900">Wesentliche Erkenntnisse</h3>
                </div>
                <button type="button" class="text-xs font-medium text-emerald-700 hover:text-emerald-600" @click="analysisSnapshot = null">
                  Analyse ausblenden
                </button>
              </header>
              <ul class="space-y-2 text-sm text-emerald-900">
                <li v-for="(point, idx) in analysisHeadline" :key="idx" class="flex items-start gap-2">
                  <span class="mt-1 h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
                  <span>{{ point }}</span>
                </li>
              </ul>
              <div v-if="analysisSnapshot.next_steps?.length" class="mt-4 rounded-xl border border-emerald-200 bg-white/70 p-4 text-sm text-emerald-900">
                <p class="mb-2 font-semibold">Empfohlene nächste Schritte</p>
                <ul class="space-y-1 text-sm">
                  <li v-for="(step, idx) in analysisSnapshot.next_steps" :key="idx" class="flex items-start gap-2">
                    <span class="mt-1 h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
                    <span>{{ step }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  </PortalShell>
</template>

<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref, reactive, watch } from 'vue'
import { useRuntimeConfig, useRouter, useRoute } from '#imports'
import PortalShell from '~/components/PortalShell.vue'
import { usePortalUser } from '~/composables/usePortalUser'

definePageMeta({ layout: false })

interface TemplateSummary {
  id: string
  title: string
  docType: string
  category: string
  prompt: string
  body: string
}

interface ClauseSummary {
  id: string
  title: string
  summary?: string
}

const runtimeConfig = useRuntimeConfig()
const router = useRouter()
const route = useRoute()
const { user: portalUser, loadUser } = usePortalUser()

const workflowSteps = [
  {
    number: '1',
    title: 'Sammeln',
    description: 'Sachverhalt beschreiben oder Dateien hochladen'
  },
  {
    number: '2',
    title: 'Prüfen',
    description: 'Klauseln ergänzen, Vorlagen kombinieren, Feedback geben'
  },
  {
    number: '3',
    title: 'Exportieren',
    description: 'PDF oder DOCX herunterladen und weitergeben'
  }
]

const form = reactive({
  docType: '',
  requirements: '',
  tone: 'legal' as 'legal' | 'legal+plain' | 'plain' | 'neutral'
})

const uploadState = reactive({
  fileName: '',
  fileSize: '',
  id: null as string | null,
  error: '',
  progress: 0
})

const selectedTemplate = ref<TemplateSummary | null>(null)
const templates = ref<TemplateSummary[]>([])
const templateMessage = ref('Beispielvorlagen werden angezeigt.')
const templateTone = ref<'info' | 'success' | 'danger'>('info')
const featuredTemplates = computed(() => templates.value.slice(0, 3))

const clauses = ref<ClauseSummary[]>([])
const clauseMessage = ref('')
const selectedClauses = ref<string[]>([])

const previewHtml = ref('')
const previewContainer = ref<HTMLElement | null>(null)
const isEditingPreview = ref(false)
const isDragActive = ref(false)
const isGenerating = ref(false)
const isSaving = ref(false)
const isAnalyzing = ref(false)
const lastGeneratedAt = ref<Date | null>(null)
const lastSavedAt = ref<Date | null>(null)
const lastExportAt = ref<Date | null>(null)
const lastExportState = ref<'idle' | 'success' | 'error'>('idle')
const lastExportError = ref('')

const feedbackSelection = ref<'accepted' | 'rejected' | null>(null)
const feedbackStatus = reactive({ tone: 'info' as 'info' | 'success' | 'danger', message: '' })

const processingState = ref<'idle' | 'running' | 'success' | 'error'>('idle')
const processingMessage = ref('Bereit zur Generierung')
const processingSubtext = ref('Füllen Sie die Basisdaten aus.')

const currentDocument = reactive({
  id: null as string | null,
  download: {} as Record<string, string>,
  metadata: {} as Record<string, unknown>
})

const analysisSnapshot = ref<any>(null)

const fileInputRef = ref<HTMLInputElement | null>(null)

const endpoints = computed(() => {
  const publicConfig = (runtimeConfig.public || {}) as Record<string, any>
  const apiBase = (publicConfig.apiBase as string) || ''
  const apiEndpoints = (publicConfig.apiEndpoints || {}) as Record<string, string>
  const normalize = (value: string | undefined, fallback: string) => {
    if (value && /^https?:\/\//i.test(value)) return value
    if (value) return value
    if (!apiBase) return fallback
    const base = apiBase.replace(/\/$/, '')
    return `${base}${fallback}`
  }
  return {
    process: normalize(apiEndpoints.process, '/api/documents/process'),
    templates: normalize(apiEndpoints.templates, '/api/documents/templates'),
    clauses: normalize(apiEndpoints.clauses, '/api/documents/clauses'),
    upload: normalize(apiEndpoints.upload, '/api/files/upload'),
    save: normalize(apiEndpoints.save, '/api/documents/save'),
    exportBase: normalize(apiEndpoints.exportBase, '/api/documents'),
    status: normalize(apiEndpoints.status, '/api/documents/status'),
    analyze: normalize(apiEndpoints.analyze, '/api/documents/analyze')
  }
})

const canGenerate = computed(() => form.requirements.trim().length >= 10 && !!form.docType.trim())

const previewWordCount = computed(() => {
  if (!previewHtml.value) return 0
  const text = stripHtml(previewHtml.value)
  if (!text) return 0
  return text.split(/[\s\r\n]+/).filter(Boolean).length
})

const qualityBadge = computed(() => {
  if (!previewHtml.value) return 'Entwurf ausstehend'
  if (selectedClauses.value.length >= 3) return 'Inhaltlich abgesichert'
  return 'Entwurf in Prüfung'
})

const analysisHeadline = computed(() => {
  if (!analysisSnapshot.value) return [] as string[]
  const summary = analysisSnapshot.value.summary
  const summaryPoints = Array.isArray(analysisSnapshot.value.summary_points)
    ? analysisSnapshot.value.summary_points
    : Array.isArray(summary?.points)
      ? summary.points
      : []
  if (summaryPoints.length) return summaryPoints
  if (typeof summary === 'string' && summary) return [summary]
  if (analysisSnapshot.value.title) return [analysisSnapshot.value.title]
  return [] as string[]
})

const numberFormatter = new Intl.NumberFormat('de-DE')
const timeFormatter = new Intl.DateTimeFormat('de-DE', { hour: '2-digit', minute: '2-digit' })
const fullDateFormatter = new Intl.DateTimeFormat('de-DE', { dateStyle: 'medium', timeStyle: 'short' })

const hasDraft = computed(() => !!previewHtml.value)
const clauseCount = computed(() => selectedClauses.value.length)

function formatNumber(value: number): string {
  try {
    return numberFormatter.format(value)
  } catch (_) {
    return String(value)
  }
}

function formatTime(value: Date | null): string {
  if (!value) return '—'
  try {
    return timeFormatter.format(value)
  } catch (_) {
    return value.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
  }
}

function formatTimeTitle(value: Date | null): string | undefined {
  if (!value) return undefined
  try {
    return fullDateFormatter.format(value)
  } catch (_) {
    return value.toISOString()
  }
}

function toneButtonClass(tone: 'legal' | 'legal+plain' | 'plain' | 'neutral') {
  const isActive = form.tone === tone
  return [
    'inline-flex items-center rounded-xl border px-3 py-2 text-xs font-semibold transition focus:outline-none focus:ring-2 focus:ring-indigo-100',
    isActive
      ? 'border-indigo-500 bg-indigo-500 text-white shadow'
      : 'border-slate-200 bg-white text-slate-600 hover:border-indigo-300 hover:text-indigo-600'
  ].join(' ')
}

function clauseChipClass(title: string) {
  const active = selectedClauses.value.includes(title)
  return [
    'inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium transition',
    active
      ? 'border-indigo-400 bg-indigo-100 text-indigo-700 shadow-sm'
      : 'border-slate-200 bg-white text-slate-600 hover:border-indigo-300 hover:text-indigo-600'
  ].join(' ')
}

const feedbackStatusClass = computed(() => {
  const base = 'rounded-xl px-3 py-2 font-medium'
  if (feedbackStatus.tone === 'success') return `${base} bg-emerald-50 text-emerald-700 border border-emerald-100`
  if (feedbackStatus.tone === 'danger') return `${base} bg-red-50 text-red-600 border border-red-100`
  return `${base} bg-slate-50 text-slate-600 border border-slate-100`
})

const templateMessageTone = computed(() => {
  if (templateTone.value === 'success') return 'text-xs text-emerald-600'
  if (templateTone.value === 'danger') return 'text-xs text-red-600'
  return 'text-xs text-slate-500'
})

function setTone(nextTone: 'legal' | 'legal+plain' | 'plain' | 'neutral') {
  form.tone = nextTone
}

function insertChecklist() {
  const checklist = [
    '• Parteien & Vertragsbeziehung eindeutig beschreiben',
    '• Relevante Termine, Fristen und Beträge angeben',
    '• Besondere Klauseln (z. B. Haftung, Geheimhaltung) erwähnen'
  ].join('\n')
  if (!form.requirements) {
    form.requirements = checklist
    return
  }
  form.requirements = `${form.requirements.trim()}\n\n${checklist}`
}

function stripHtml(input: string): string {
  return input.replace(/<[^>]*>/g, ' ').replace(/&nbsp;/g, ' ').replace(/\s+/g, ' ').trim()
}

function resolveAuthHeaders(extra: Record<string, string> = {}) {
  const storageKeys = ['auth_token', 'anwalts_auth_token', 'access_token', 'token', 'sat']
  let token: string | null = null
  if (typeof window !== 'undefined') {
    for (const key of storageKeys) {
      try {
        const value = window.localStorage.getItem(key)
        if (value) {
          token = value
          break
        }
      } catch (_) { /* ignore */ }
    }
    if (!token && typeof document !== 'undefined') {
      const cookies = document.cookie.split(';').map(entry => entry.trim()).filter(Boolean)
      for (const cookie of cookies) {
        const [k, ...rest] = cookie.split('=')
        if (storageKeys.includes(decodeURIComponent(k))) {
          token = decodeURIComponent(rest.join('=') || '')
          break
        }
      }
    }
  }
  if (!token) return { ...extra }
  let cleaned = decodeURIComponent(token)
  cleaned = cleaned.trim().replace(/^['"]|['"]$/g, '')
  const bearer = cleaned.startsWith('Bearer ') ? cleaned : `Bearer ${cleaned}`
  return { ...extra, Authorization: bearer, 'X-Portal-Auth': bearer }
}

function handleAuthExpiration() {
  if (typeof window === 'undefined') return
  ;['auth_token', 'anwalts_auth_token', 'access_token', 'token', 'sat'].forEach((key) => {
    try {
      window.localStorage.removeItem(key)
    } catch (_) {}
  })
  setFeedback('danger', 'Sitzung abgelaufen. Bitte erneut anmelden – Sie werden weitergeleitet.')
  setTimeout(() => {
    const redirect = encodeURIComponent(window.location.pathname || '/documents')
    window.location.href = `/login?redirect=${redirect}`
  }, 1200)
}

async function apiFetch(url: string, options: RequestInit = {}) {
  const requestUrl = url
  const headers = new Headers(options.headers || {})
  const authHeaders = resolveAuthHeaders()
  Object.entries(authHeaders).forEach(([key, value]) => {
    if (!headers.has(key) && value) headers.set(key, value as string)
  })
  if (options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  const response = await fetch(requestUrl, {
    ...options,
    headers,
    credentials: 'include'
  })
  if (response.status === 401) {
    handleAuthExpiration()
    throw new Error('Nicht authentifiziert')
  }
  return response
}

async function apiJson(url: string, options: RequestInit = {}) {
  const response = await apiFetch(url, options)
  if (!response.ok) {
    const message = await safeParseError(response)
    const error = new Error(message)
    ;(error as any).status = response.status
    throw error
  }
  if (response.status === 204) return null
  return await response.json()
}

async function safeParseError(response: Response) {
  try {
    const data = await response.json()
    if (typeof data?.detail === 'string') return data.detail
    if (typeof data?.message === 'string') return data.message
  } catch (_) {}
  return `HTTP ${response.status}`
}

function setFeedback(tone: 'info' | 'success' | 'danger', message: string, timeout = 3500) {
  feedbackStatus.tone = tone
  feedbackStatus.message = message
  if (timeout > 0) {
    window.setTimeout(() => {
      if (feedbackStatus.message === message) feedbackStatus.message = ''
    }, timeout)
  }
}

function resetForm() {
  form.docType = ''
  form.requirements = ''
  form.tone = 'legal'
  selectedClauses.value = []
  selectedTemplate.value = null
  previewHtml.value = ''
  feedbackSelection.value = null
  lastGeneratedAt.value = null
  lastSavedAt.value = null
  lastExportAt.value = null
  lastExportState.value = 'idle'
  lastExportError.value = ''
  processingState.value = 'idle'
  processingMessage.value = 'Bereit zur Generierung'
  processingSubtext.value = 'Füllen Sie die Basisdaten aus.'
  setFeedback('info', 'Formular zurückgesetzt.', 2000)
}

async function loadTemplates() {
  const endpoint = endpoints.value.templates
  templateTone.value = 'info'
  templateMessage.value = 'Vorlagen werden geladen…'
  try {
    let data: any = null
    if (portalUser.value) {
      data = await apiJson(endpoint)
    }
    if (!Array.isArray(data) || data.length === 0) {
      templates.value = getSampleTemplates()
      templateTone.value = 'info'
      templateMessage.value = portalUser.value
        ? 'Keine eigenen Vorlagen gefunden, wir zeigen Beispiele.'
        : 'Bitte anmelden, um eigene Vorlagen zu laden. Wir zeigen Beispiele.'
      return
    }
    templates.value = data.map(normalizeTemplate)
    templateTone.value = 'success'
    templateMessage.value = `${templates.value.length} Vorlagen bereit.`
  } catch (error: any) {
    templates.value = getSampleTemplates()
    templateTone.value = 'danger'
    templateMessage.value = `Vorlagen konnten nicht geladen werden: ${error?.message || 'Unbekannter Fehler'}`
  }
}

async function loadClauses() {
  const endpoint = endpoints.value.clauses
  clauseMessage.value = 'Lade Klauselvorschläge…'
  try {
    const data = await apiJson(endpoint)
    if (!Array.isArray(data) || data.length === 0) {
      clauses.value = getSampleClauses()
      clauseMessage.value = 'Beispielklauseln werden angezeigt.'
      return
    }
    clauses.value = data.map((item: any) => ({
      id: String(item.id || item.slug || item.title || crypto.randomUUID()),
      title: item.title || item.name || 'Baustein',
      summary: item.summary || ''
    }))
    clauseMessage.value = `${clauses.value.length} Klauselbausteine verfügbar.`
  } catch (error: any) {
    clauses.value = getSampleClauses()
    clauseMessage.value = `Klauseln konnten nicht geladen werden (${error?.message || 'Unbekannter Fehler'}). Beispielklauseln werden angezeigt.`
  }
}

function normalizeTemplate(entry: any): TemplateSummary {
  const toPlain = (html = '') => stripHtml(html).slice(0, 180)
  return {
    id: String(entry.id || entry.slug || entry.name || crypto.randomUUID()),
    title: entry.title || entry.name || 'Vorlage',
    docType: entry.document_type || entry.type || entry.title || 'Dokument',
    category: entry.category || 'Allgemein',
    prompt: toPlain(entry.content || entry.prompt || ''),
    body: entry.content || ''
  }
}

function getSampleTemplates(): TemplateSummary[] {
  return [
    {
      id: 'sample-nda',
      title: 'Geheimhaltungsvereinbarung (NDA)',
      docType: 'Geheimhaltungsvereinbarung',
      category: 'Vertragsrecht',
      prompt: 'Klare Definition der vertraulichen Informationen, Laufzeit der Geheimhaltung, Konventionalstrafe und Gerichtsstand angeben.',
      body: '<p>[Parteien] vereinbaren absolute Vertraulichkeit über sämtliche Geschäfts- und Betriebsgeheimnisse.</p>'
    },
    {
      id: 'sample-arbeitsrecht',
      title: 'Abmahnung wegen Pflichtverletzung',
      docType: 'Abmahnung',
      category: 'Arbeitsrecht',
      prompt: 'Beschreibung der Pflichtwidrigkeit, Datum, Zeugen, Hinweis auf Wiederholungsgefahr und Kündigungsandrohung.',
      body: '<p>Sehr geehrte/r [Mitarbeiter/in], hiermit mahnen wir das Verhalten vom [Datum] ab…</p>'
    },
    {
      id: 'sample-mietrecht',
      title: 'Mieterhöhung nach § 558 BGB',
      docType: 'Mieterhöhungserklärung',
      category: 'Mietrecht',
      prompt: 'Begründung mit Vergleichsmiete, Frist beachten, Modernisierungszuschläge erläutern.',
      body: '<p>Sehr geehrte/r Mieter/in, wir passen die Miete zum [Datum] auf Grundlage von § 558 BGB an.</p>'
    }
  ]
}

function getSampleClauses(): ClauseSummary[] {
  return [
    { id: 'clause-1', title: 'Gerichtsstand / Schiedsgericht' },
    { id: 'clause-2', title: 'Haftungsbeschränkung' },
    { id: 'clause-3', title: 'Datenschutz / DSGVO' },
    { id: 'clause-4', title: 'Salvatorische Klausel' }
  ]
}

function applyTemplate(template: TemplateSummary) {
  selectedTemplate.value = template
  if (!form.docType) {
    form.docType = template.docType
  }
  form.requirements = [
    '• Platzhalter wie [Name] oder [Datum] ersetzen',
    `• ${template.prompt}`
  ].join('\n')
  setFeedback('info', `Vorlage „${template.title}“ übernommen.`, 2500)
}

function toggleClause(title: string) {
  if (!title) return
  const list = new Set(selectedClauses.value)
  if (list.has(title)) {
    list.delete(title)
  } else {
    list.add(title)
  }
  selectedClauses.value = Array.from(list)
}

function openTemplates() {
  router.push({ path: '/templates', query: { origin: 'documents' } })
}

function goToTemplates(template: TemplateSummary) {
  if (!template?.id) {
    openTemplates()
    return
  }
  router.push({ path: '/templates', query: { origin: 'documents', templateId: template.id } })
}

function syncPreviewFromDom() {
  if (!previewContainer.value) return
  previewHtml.value = previewContainer.value.innerHTML
}

function toggleEditing() {
  if (!previewContainer.value || !previewHtml.value) return
  isEditingPreview.value = !isEditingPreview.value
  previewContainer.value.setAttribute('contenteditable', isEditingPreview.value ? 'true' : 'false')
  if (isEditingPreview.value) {
    previewContainer.value.focus()
    setFeedback('info', 'Direktbearbeitung aktiviert. Änderungen werden lokal gespeichert.', 2500)
  } else {
    syncPreviewFromDom()
    setFeedback('success', 'Direktbearbeitung gespeichert.', 2000)
  }
}

function handleDrop(event: DragEvent) {
  isDragActive.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file) {
    handleFileUpload(file)
  }
}

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) {
    handleFileUpload(file)
  }
}

function clearUpload() {
  uploadState.fileName = ''
  uploadState.fileSize = ''
  uploadState.id = null
  uploadState.error = ''
  uploadState.progress = 0
  if (fileInputRef.value) fileInputRef.value.value = ''
  setFeedback('info', 'Anhang entfernt.', 2000)
}

async function handleFileUpload(file: File) {
  if (!file) return
  uploadState.error = ''
  uploadState.fileName = file.name
  uploadState.fileSize = `${(file.size / 1024).toFixed(0)} KB`
  uploadState.progress = 10
  try {
    if (file.size > 10 * 1024 * 1024) {
      throw new Error('Die Datei überschreitet das Limit von 10 MB.')
    }
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiJson(endpoints.value.upload, {
      method: 'POST',
      body: formData
    })
    uploadState.id = response?.id || response?.file_id || null
    uploadState.progress = 100
    setFeedback('success', 'Datei erfolgreich hochgeladen.', 2500)
  } catch (error: any) {
    uploadState.error = error?.message || 'Upload fehlgeschlagen.'
    uploadState.progress = 0
    setFeedback('danger', uploadState.error, 3500)
  }
}

function buildDocumentHtml(title: string, bodyHtml: string) {
  const toneDescription = {
    legal: 'Juristisch präzise Formulierung.',
    'legal+plain': 'Juristisch präzise und zugleich verständlich.',
    plain: 'Leicht verständliche Formulierung.',
    neutral: 'Neutraler Stil.'
  }[form.tone]
  return `
    <header style="border-bottom:1px solid #E2E8F0;padding-bottom:12px;margin-bottom:24px">
      <h1 style="font-size:22px;font-weight:600;color:#111827;margin:0">${escapeHtml(title)}</h1>
      <p style="font-size:13px;color:#475569;margin-top:4px">${toneDescription}</p>
    </header>
    ${bodyHtml}
  `
}

function escapeHtml(value: string) {
  return value.replace(/[&<>"']/g, (char) => {
    const entities: Record<string, string> = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    }
    return entities[char] || char
  })
}

async function generateDocument() {
  if (!canGenerate.value || isGenerating.value) return
  isGenerating.value = true
  processingState.value = 'running'
  processingMessage.value = 'Dokument wird erstellt …'
  processingSubtext.value = 'KI-Analyse läuft'
  try {
    const payload = {
      title: form.docType,
      document_type: form.docType,
      instructions: form.requirements.trim(),
      tone: form.tone,
      template_content: selectedTemplate.value?.body || '',
      template_id: selectedTemplate.value?.id || null,
      variables: {},
      uploadId: uploadState.id,
      metadata: currentDocument.metadata,
      categories: selectedClauses.value
    }
    const response = await apiJson(endpoints.value.process, {
      method: 'POST',
      body: JSON.stringify({ action: 'generate', payload })
    })
    const doc = response?.document || {}
    const contentHtml = doc?.content || doc?.html || ''
    if (!contentHtml) {
      throw new Error('Backend lieferte kein verwendbares Dokument.')
    }
    const html = buildDocumentHtml(form.docType, contentHtml)
    previewHtml.value = html
    if (previewContainer.value) {
      previewContainer.value.innerHTML = html
    }
    analysisSnapshot.value = null
    currentDocument.id = doc?.id || response?.id || null
    currentDocument.download = response?.download || doc?.download || {}
    currentDocument.metadata = doc?.metadata || response?.metadata || {}
    feedbackSelection.value = null
    processingState.value = 'success'
    processingMessage.value = 'Dokument erfolgreich aktualisiert.'
    processingSubtext.value = doc?.metadata?.redactions ? `Automatische Schwärzungen: ${summarizeRedactions(doc.metadata.redactions)}` : ''
    lastGeneratedAt.value = new Date()
    lastExportState.value = 'idle'
    lastExportError.value = ''
    lastExportAt.value = null
    setFeedback('info', 'Entwurf aktualisiert. Prüfen und optional bearbeiten.', 4000)
    await saveDocument({ silent: true, status: 'generated' })
  } catch (error: any) {
    processingState.value = 'error'
    processingMessage.value = 'Generierung fehlgeschlagen.'
    processingSubtext.value = error?.message || 'Bitte erneut versuchen.'
    setFeedback('danger', error?.message || 'Generierung fehlgeschlagen.', 4000)
  } finally {
    isGenerating.value = false
  }
}

function summarizeRedactions(redactions: Record<string, number>) {
  if (!redactions) return ''
  return Object.entries(redactions)
    .filter(([, count]) => typeof count === 'number' && count > 0)
    .map(([token, count]) => `${count}× ${token.replace(/\[|\]/g, '')}`)
    .join(', ')
}

async function regenerateDocument() {
  if (!canGenerate.value || isGenerating.value) return
  await generateDocument()
}

async function saveDocument(options: { silent?: boolean; status?: string } = {}) {
  if (!previewHtml.value) {
    if (!options.silent) setFeedback('danger', 'Kein Inhalt zum Speichern vorhanden.', 2500)
    return
  }
  try {
    isSaving.value = true
    const response = await apiJson(endpoints.value.save, {
      method: 'POST',
      body: JSON.stringify({
        title: form.docType,
        html: previewHtml.value,
        content: previewHtml.value,
        document_type: form.docType,
        uploadedFileId: uploadState.id,
        metadata: currentDocument.metadata,
        status: options.status || 'saved'
      })
    })
    const doc = response?.document || {}
    currentDocument.id = response?.id || response?.documentId || doc?.id || currentDocument.id
    currentDocument.download = response?.download || doc?.download || currentDocument.download
    lastSavedAt.value = new Date()
    if (!options.silent) {
      processingMessage.value = 'Dokument gespeichert.'
      processingSubtext.value = ''
    }
    if (!options.silent) setFeedback('success', 'Dokument gespeichert. Export bereit.', 3000)
  } catch (error: any) {
    if (!options.silent) setFeedback('danger', `Speichern fehlgeschlagen: ${error?.message || 'Unbekannter Fehler'}`, 3500)
    throw error
  } finally {
    isSaving.value = false
  }
}

async function exportPdf() {
  if (!previewHtml.value) return
  try {
    if (!currentDocument.id) {
      await saveDocument({ silent: true })
    }
    if (!currentDocument.id) {
      throw new Error('Es konnte keine Dokument-ID ermittelt werden.')
    }
    const url = `${endpoints.value.exportBase.replace(/\/$/, '')}/${currentDocument.id}/export?format=pdf`
    const response = await apiFetch(url)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const blob = await response.blob()
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${slugify(form.docType || 'Rechtsdokument')}.pdf`
    document.body.appendChild(link)
    link.click()
    link.remove()
    lastExportState.value = 'success'
    lastExportAt.value = new Date()
    lastExportError.value = ''
    setFeedback('success', 'PDF erfolgreich heruntergeladen.', 2500)
  } catch (error: any) {
    lastExportState.value = 'error'
    lastExportError.value = error?.message || 'Unbekannter Fehler'
    lastExportAt.value = new Date()
    setFeedback('danger', `PDF-Export fehlgeschlagen: ${error?.message || 'Unbekannter Fehler'}`, 3500)
  }
}

async function submitFeedback(status: 'accepted' | 'rejected') {
  if (!currentDocument.id || !previewHtml.value) {
    setFeedback('danger', 'Bitte zuerst ein Dokument generieren.', 2500)
    return
  }
  try {
    setFeedback('info', 'Feedback wird gespeichert…', 1200)
    await apiJson(endpoints.value.status, {
      method: 'POST',
      body: JSON.stringify({ doc_id: currentDocument.id, status })
    })
    feedbackSelection.value = status
    setFeedback(status === 'accepted' ? 'success' : 'info', status === 'accepted' ? 'Dokument freigegeben.' : 'Als Überarbeitung markiert.', 2500)
  } catch (error: any) {
    setFeedback('danger', `Feedback konnte nicht gespeichert werden: ${error?.message || 'Unbekannter Fehler'}`, 3500)
  }
}

async function runAnalysis() {
  if (!previewHtml.value || isAnalyzing.value) return
  isAnalyzing.value = true
  setFeedback('info', 'Analyse wird vorbereitet …', 1500)
  try {
    const response = await apiJson(endpoints.value.analyze, {
      method: 'POST',
      body: JSON.stringify({
        title: form.docType || 'Dokument',
        content: stripHtml(previewHtml.value),
        categories: selectedClauses.value
      })
    })
    analysisSnapshot.value = response?.analysis || response
    setFeedback('success', 'Analyse abgeschlossen. Ergebnisse rechts dargestellt.', 2500)
  } catch (error: any) {
    setFeedback('danger', `Analyse fehlgeschlagen: ${error?.message || 'Unbekannter Fehler'}`, 3500)
  } finally {
    isAnalyzing.value = false
  }
}

async function copyPreview() {
  if (!previewHtml.value) return
  try {
    await navigator.clipboard.writeText(stripHtml(previewHtml.value))
    setFeedback('success', 'Dokument in Zwischenablage kopiert.', 2500)
  } catch (error: any) {
    setFeedback('danger', `Kopieren fehlgeschlagen: ${error?.message || 'Nicht unterstützt'}`, 3000)
  }
}

function slugify(value: string) {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '') || 'dokument'
}

function hydrateTemplateSelection() {
  if (typeof window === 'undefined') return
  try {
    const raw = window.localStorage.getItem('anwalt.templateSelection')
    if (raw) {
      const tpl = JSON.parse(raw)
      applyTemplate(normalizeTemplate(tpl))
      window.localStorage.removeItem('anwalt.templateSelection')
    }
  } catch (_) {}
}

function hydrateEmailHandOff() {
  if (typeof window === 'undefined') return
  try {
    const raw = window.localStorage.getItem('anwalt.emailToDocument')
    if (raw) {
      const data = JSON.parse(raw)
      form.docType = data?.subject || form.docType
      form.requirements = [data?.content || '', form.requirements].filter(Boolean).join('\n\n')
      window.localStorage.removeItem('anwalt.emailToDocument')
      setFeedback('info', 'E-Mail-Inhalt übernommen. Sie können jetzt generieren.', 3500)
    }
  } catch (_) {}
}

function hydrateQueryTemplate() {
  const tplId = (route.query.templateId || route.query.tpl) as string | undefined
  if (!tplId) return
  const template = templates.value.find((tpl) => tpl.id === tplId)
  if (template) {
    applyTemplate(template)
  } else {
    // fallback: store so that loadTemplates can apply later
    if (typeof window !== 'undefined') {
      try {
        window.localStorage.setItem('anwalt.templateId', tplId)
      } catch (_) {}
    }
  }
}

function refreshClauses() {
  loadClauses()
}

function hydrateDeferredTemplate() {
  if (typeof window === 'undefined') return
  try {
    const templateId = window.localStorage.getItem('anwalt.templateId')
    if (!templateId) return
    const template = templates.value.find((tpl) => tpl.id === templateId)
    if (template) {
      applyTemplate(template)
      window.localStorage.removeItem('anwalt.templateId')
    }
  } catch (_) {}
}

function handleHotkeys(event: KeyboardEvent) {
  if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
    event.preventDefault()
    if (canGenerate.value && !isGenerating.value) {
      generateDocument()
    }
  }
}

onMounted(async () => {
  await loadUser()
  await Promise.all([loadTemplates(), loadClauses()])
  hydrateDeferredTemplate()
  hydrateTemplateSelection()
  hydrateEmailHandOff()
  hydrateQueryTemplate()
  window.addEventListener('keydown', handleHotkeys)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleHotkeys)
})

watch(() => route.query.templateId, hydrateQueryTemplate)

watch(() => templates.value, () => {
  hydrateDeferredTemplate()
})

watch(previewHtml, () => {
  if (previewContainer.value && !isEditingPreview.value) {
    previewContainer.value.innerHTML = previewHtml.value
  }
})

watch(processingState, (state) => {
  if (state === 'success') {
    window.setTimeout(() => {
      if (processingState.value === state) {
        processingState.value = 'idle'
      }
    }, 2500)
  }
})

</script>

<style scoped>
.feedback-button,
.toolbar-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  border-radius: 9999px;
  border: 1px solid rgba(226, 232, 240, 1);
  background: #ffffff;
  padding: 0.5rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
  transition: border-color 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
}

.feedback-button:hover,
.toolbar-button:hover {
  border-color: rgba(99, 102, 241, 0.4);
  color: #4338ca;
}

.feedback-button:focus-visible,
.toolbar-button:focus-visible {
  outline: 2px solid rgba(99, 102, 241, 0.35);
  outline-offset: 2px;
}

.feedback-button:disabled,
.toolbar-button:disabled {
  cursor: not-allowed;
  color: #94a3b8;
  border-color: rgba(226, 232, 240, 0.8);
}

.feedback-button--active {
  border-color: rgba(99, 102, 241, 0.9);
  background: rgba(99, 102, 241, 1);
  color: #ffffff;
  box-shadow: 0 5px 14px rgba(99, 102, 241, 0.25);
}

.preview-surface {
  min-height: clamp(420px, 65vh, 720px);
  border-radius: 1rem;
  border: 1px solid rgba(226, 232, 240, 0.8);
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.9) 0%, #fff 120%);
  padding: 24px;
  font-family: "Noto Serif", "Georgia", serif;
  color: #1f2937;
  line-height: 1.65;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6);
  transition: border 0.2s ease, box-shadow 0.2s ease;
  overflow-wrap: anywhere;
}

.preview-surface p {
  margin-bottom: 12px;
}

.preview-surface h1,
.preview-surface h2,
.preview-surface h3 {
  font-family: "Inter", "Helvetica Neue", sans-serif;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 16px;
}

.preview-surface--editing {
  border: 1px solid rgba(99, 102, 241, 0.5);
  box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.12);
  background: #ffffff;
}

.preview-surface:focus-visible {
  outline: none;
  border: 1px solid rgba(99, 102, 241, 0.5);
  box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.12);
}
</style>
