<template>
  <PortalShell>
    <template #header>
      <header class="bg-white border-b border-gray-200">
        <div class="px-8 py-4">
            <div class="flex items-center justify-between flex-wrap gap-3">
            <div class="header-stack">
              <h1 class="text-xl font-semibold text-gray-900">Rechtsdokument-Assistent</h1>
              <p class="text-sm text-gray-600 mt-0.5">KI-gestützte Dokumentenerstellung für Ihre Kanzlei</p>
            </div>
          </div>
        </div>
      </header>
    </template>

    <main class="documents-page">
      <div class="process-steps-wrapper">
        <div class="step-card">
          <span class="step-accent" aria-hidden="true"></span>
          <div>
            <div class="step-title">1. Dokument hochladen</div>
            <div class="step-subtitle">Optional</div>
          </div>
        </div>
        <div class="step-card">
          <span class="step-accent" aria-hidden="true"></span>
          <div>
            <div class="step-title">2. Angaben &amp; Vorgaben</div>
            <div class="step-subtitle">Pflichtfelder</div>
          </div>
        </div>
        <div class="step-card">
          <span class="step-accent" aria-hidden="true"></span>
          <div>
            <div class="step-title">3. Vorschau &amp; Feinschliff</div>
            <div class="step-subtitle">Export bereit</div>
          </div>
        </div>
      </div>

      <div class="documents-container">
        <div class="documents-grid">
          <section class="inputs-panel">
            <div class="panel-scroll">
              <div class="content-card form-card form-card--combined">
                <div class="card-body card-body--combined">
                  <div class="card-section section-upload">
                    <div class="card-section-header">
                      <div>
                        <h2 class="card-section-title">Dokument hochladen</h2>
                        <p class="card-section-subtle">(optional)</p>
                      </div>
                      <button type="button" class="link-accent" id="btnClearUpload">Zurücksetzen</button>
                    </div>
                    <div class="card-section-body">
                      <div id="dropzone" class="dropzone">
                        <svg class="dropzone-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"/>
                        </svg>
                        <p class="dropzone-title"><span>Datei hier ablegen</span> oder zum Durchsuchen klicken</p>
                        <p class="dropzone-formats">PDF, DOC, DOCX, TXT &middot; Maximal 10 MB</p>
                        <input id="fileInput" type="file" class="hidden" accept=".pdf,.doc,.docx,.txt" />
                      </div>
                      <p class="helper-text">Dokumente werden vertraulich verarbeitet.</p>
                      <div id="uploadInfo" class="upload-info hidden"></div>
                    </div>
                  </div>

                  <div class="card-section section-details">
                    <div class="card-section-header">
                      <h2 class="card-section-title">Angaben &amp; Vorgaben</h2>
                      <div class="tone-toggle">
                        <label class="tone-option">
                          <span>Juristische Sprache</span>
                          <span class="switch"><input id="switchLegalTone" type="checkbox" checked><span class="dot"></span></span>
                        </label>
                        <label class="tone-option">
                          <span>Leichte Sprache</span>
                          <span class="switch"><input id="switchPlain" type="checkbox"><span class="dot"></span></span>
                        </label>
                      </div>
                    </div>
                    <div class="card-section-body">
                      <div class="field">
                        <label class="field-label" for="docType">Dokumenttyp</label>
                        <input id="docType" class="field-input" placeholder="z. B. Mietvertrag, Abmahnung, Vergleich, NDA" />
                      </div>

                      <div class="field">
                        <div class="field-label-row">
                          <label class="field-label" for="requirements">Sachverhalt &amp; Anforderungen</label>
                          <button id="btnInsertChecklist" type="button" class="link-accent link-small">Beispiel-Checkliste einfügen</button>
                        </div>
                        <textarea id="requirements" class="field-textarea" rows="6" placeholder="Beschreiben Sie kurz den Fall. Nennen Sie Parteien, Ziele und besondere Bedingungen."></textarea>
                        <p class="helper-text" id="charCount">0 Zeichen</p>
                      </div>

                      <div class="field">
                        <div class="field-label-row">
                          <label class="field-label">Optionale Bausteine</label>
                          <span id="clauseStatus" class="helper-text hidden"></span>
                        </div>
                        <div class="clause-chips" id="clauseChipContainer"></div>
                      </div>

                      <div class="field">
                        <div class="field-label-row">
                          <label class="field-label">Vorlagen (Schnellauswahl)</label>
                          <button id="btnTemplatesInline" type="button" class="link-accent link-small" @click.prevent="navigateToTemplates">Alle Vorlagen öffnen</button>
                        </div>
                        <div id="inlineTemplates" class="inline-templates"></div>
                      </div>
                    </div>
                  </div>

                </div>
                <footer class="action-footer" aria-label="Dokumentaktionen">
                  <div class="action-footer-row">
                    <div class="action-button-group">
                      <button id="btnTemplates" type="button" class="toolbar-btn toolbar-btn-secondary" @click.prevent="navigateToTemplates">
                        <svg class="toolbar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h10M7 11h10M7 15h6M5 5a2 2 0 012-2h10a2 2 0 012 2v14a2 2 0 01-2 2H7a2 2 0 01-2-2V5z"/>
                        </svg>
                        Vorlagen
                      </button>
                      <button id="btnClear" type="button" class="toolbar-btn toolbar-btn-secondary">
                        <svg class="toolbar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                        </svg>
                        Leeren
                      </button>
                    </div>
                    <div class="primary-action-group">
                      <button id="btnAnalyze" type="button" class="toolbar-btn toolbar-btn-secondary">
                        <svg class="toolbar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c1.657 0 3-1.567 3-3.5S13.657 1 12 1 9 2.567 9 4.5 10.343 8 12 8zm0 3c-2.5 0-7 1.25-7 3.75V18a1 1 0 001 1h12a1 1 0 001-1v-3.25C19 12.25 14.5 11 12 11z"/>
                        </svg>
                        Dokument analysieren
                      </button>
                      <button id="btnGenerate" type="button" class="toolbar-btn toolbar-btn-primary btn-generate">
                        <svg class="toolbar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                        </svg>
                        Dokument erzeugen
                      </button>
                    </div>
                  </div>
                </footer>
              </div>
            </div>
          </section>

          <section class="preview-panel">
            <div id="previewContainer" class="preview-container">
              <div class="preview-toolbar">
                <div class="toolbar-left">
                  <span id="wordCount" class="toolbar-meta">0 Wörter</span>
                </div>
              </div>
              <p id="templateStatus" class="toolbar-helper helper-text hidden"></p>

              <div class="preview-body">
                <div id="previewArea" class="preview-area">
                  <div id="previewEmpty" class="preview-empty">
                    <div class="preview-placeholder">
                    <div class="preview-icon">
                      <svg class="preview-icon-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                      </svg>
                    </div>
                    <div class="preview-empty-title">Noch kein Dokument erstellt</div>
                    <div class="preview-empty-text">Fügen Sie Angaben hinzu oder laden Sie ein Dokument hoch, um zu beginnen.</div>
                  </div>
                </div>

                <div id="genOverlay" class="generate-overlay hidden" role="status" aria-live="polite">
                  <div class="generate-spinner"></div>
                  <div class="generate-text">Dokument wird erstellt...</div>
                  <div class="generate-subtext">KI-Analyse läuft</div>
                </div>

                <article id="preview" class="preview-content hidden"></article>
                </div>

                <div id="actionBar" class="action-bar hidden">
                  <div id="feedbackStatus" class="feedback-status hidden"></div>
                  <div class="action-groups">
                    <div class="feedback-group">
                      <button class="feedback-button feedback-accept" id="btnAccept" aria-label="Dokument akzeptieren" type="button" title="Positiv" data-hint="Positiv">
                        <svg class="feedback-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4"/>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 21c4.971 0 9-4.029 9-9s-4.029-9-9-9-9 4.029-9 9 4.029 9 9 9z"/>
                        </svg>
                      </button>
                      <button class="feedback-button feedback-reject" id="btnReject" aria-label="Dokument ablehnen" type="button" title="Negativ" data-hint="Negativ">
                        <svg class="feedback-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 9l-6 6m0-6l6 6"/>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 21c4.971 0 9-4.029 9-9s-4.029-9-9-9-9 4.029-9 9 4.029 9 9 9z"/>
                        </svg>
                      </button>
                      <button class="feedback-button feedback-retry" id="btnRetry" aria-label="Erneut generieren" type="button" title="Erneut generieren" data-hint="Erneut generieren">
                        <svg class="feedback-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.5 12a7.5 7.5 0 0112.65-5.303"/>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.5 12a7.5 7.5 0 01-12.65 5.303"/>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16.15 5.2L17 3v3.5h-3.5l1.2-1.3"/>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7.85 18.8L7 21v-3.5h3.5l-1.2 1.3"/>
                        </svg>
                      </button>
                    </div>
                    <div class="utility-group">
                      <button class="btn-action" id="btnCopy" aria-label="In Zwischenablage kopieren" type="button">
                        <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
                        Kopieren
                      </button>
                      <button class="btn-action" id="btnEdit" aria-label="Bearbeiten" type="button">
                        <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                        Bearbeiten
                      </button>
                      <button class="btn-action" id="btnSave" aria-label="Dokument speichern" type="button" title="Speichern">
                        <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16a2 2 0 01-2 2H9a2 2 0 01-2-2V7a2 2 0 012-2h6l4 4v7z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 10h10"/></svg>
                        Speichern
                      </button>
                      <button class="btn-action icon-only hidden" id="btnExportPdf" aria-label="PDF herunterladen" type="button" title="PDF herunterladen">
                        <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                      </button>
                </div>
                <div id="feedbackHint" class="feedback-hint" aria-live="polite"></div>
              </div>
                </div>
                <p class="shortcut-bar">
                  <kbd>Strg</kbd> + <kbd>Enter</kbd> generiert neu • <kbd>Alt</kbd> + <kbd>C</kbd> kopiert
                </p>
              </div>

            </div>

          </section>
        </div>
      </div>
    </main>
    <!-- Templates modal removed: inline list is used consistently -->
  </PortalShell>
</template>

<script setup>
import { onMounted, onBeforeUnmount, watch } from 'vue'
import { useRuntimeConfig, useRouter } from '#imports'
import PortalShell from '~/components/PortalShell.vue'
import { usePortalUser } from '~/composables/usePortalUser'

definePageMeta({ layout: false })

const { user: portalUser, loadUser } = usePortalUser()
const router = useRouter()

const openTemplates = (templateId) => {
  const query = { origin: 'documents' }
  if (templateId) {
    query.templateId = templateId
  }

  router.push({ path: '/templates', query }).catch((err) => {
    console.warn('[Documents] Templates navigation failed:', err)
  })
}

const navigateToTemplates = (event) => {
  if (event?.preventDefault) event.preventDefault()
  openTemplates()
}

const viewTemplateDetails = (templateId) => {
  if (!templateId) {
    openTemplates()
    return
  }

  try {
    localStorage.setItem('anwalt.templateId', templateId)
  } catch (_) {}

  openTemplates(templateId)
}

let catalogInitialized = false
let handleWindowFocus = () => {}

// Helper: Show re-login prompt and redirect
function showReLoginPrompt() {
  console.error('[Documents] Session expired - clearing token and redirecting')
  // Clear expired tokens
  try {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('anwalts_auth_token')
    localStorage.removeItem('token')
    localStorage.removeItem('access_token')
    localStorage.removeItem('sat')
  } catch(e) { console.error('localStorage clear error:', e) }
  
  // Show visible error message (will be defined in onMounted scope)
  if (typeof updateFeedbackStatus === 'function') {
    updateFeedbackStatus(
      '⚠️ Ihre Sitzung ist abgelaufen. Sie werden zur Anmeldung weitergeleitet...',
      'danger'
    )
  }
  
  // Auto-redirect after 2 seconds
  setTimeout(() => {
    const currentPath = window.location.pathname
    window.location.href = '/login?redirect=' + encodeURIComponent(currentPath)
  }, 2000)
}

onMounted(() => {
  console.log('[Documents] onMounted started at', new Date().toISOString())

  try {
    const $ = (s, r=document) => r.querySelector(s)
    const $$ = (s, r=document) => Array.from(r.querySelectorAll(s))
    const { public: { apiBase = '', apiEndpoints = {} } } = useRuntimeConfig()
    
    console.log('[Documents] API configuration:', { apiBase, hasEndpoints: !!apiEndpoints })
    
    const ep = {
      generate: apiEndpoints.generate || (apiBase ? `${apiBase}/ai/generate-document` : ''),
      generateSimple: apiEndpoints.generateSimple || (apiBase ? `${apiBase}/ai/generate-document-simple` : ''),
      process: apiEndpoints.process || (apiBase ? `${apiBase}/documents/process` : '/api/documents/process'),
      templates: apiEndpoints.templates || (apiBase ? `${apiBase}/documents/templates` : '/api/documents/templates'),
      clauses: apiEndpoints.clauses || (apiBase ? `${apiBase}/documents/clauses` : '/api/documents/clauses'),
      upload: apiEndpoints.upload || (apiBase ? `${apiBase}/files/upload` : '/api/files/upload'),
      save: apiEndpoints.save || (apiBase ? `${apiBase}/documents/save` : '/api/documents/save'),
      exportBase: apiEndpoints.exportBase || (apiBase ? `${apiBase}/documents` : '/api/documents'),
      status: apiEndpoints.status || ''
    }
    
    console.log('[Documents] Endpoints configured:', ep)

  const actionBarEl = document.getElementById('actionBar')

  function setActionBarVisibility(isVisible) {
    if (!actionBarEl) return
    if (isVisible) {
      actionBarEl.classList.remove('hidden')
      actionBarEl.style.display = 'flex'
    } else {
      actionBarEl.classList.add('hidden')
      actionBarEl.style.display = 'none'
    }
  }

  function getAuthHeader() {
    try {
      let token = localStorage.getItem('auth_token') || localStorage.getItem('anwalts_auth_token') || localStorage.getItem('token') || localStorage.getItem('access_token') || localStorage.getItem('sat')
      if (!token && document && document.cookie) {
        const map = Object.fromEntries(document.cookie.split(';').map(s => {
          const i = s.indexOf('=');
          const k = decodeURIComponent(s.slice(0, i).trim());
          const v = decodeURIComponent(s.slice(i + 1));
          return [k, v]
        }))
        token = map['auth_token'] || map['anwalts_auth_token'] || map['token'] || map['access_token'] || map['sat']
      }
      console.log('[Documents] Auth token:', token ? 'Found (' + token.substring(0, 20) + '...)' : 'NOT FOUND - User may need to log in')
      return token ? { Authorization: `Bearer ${decodeURIComponent(token)}` } : {}
    } catch (_) { return {} }
  }

  function buildUrl(path) {
    if (!path) return ''
    if (/^https?:\/\//i.test(path)) return path
    if (path.startsWith('/')) return path
    const base = apiBase || ''
    const trimmedBase = base.endsWith('/') ? base.slice(0, -1) : base
    return `${trimmedBase}/${path.replace(/^\//, '')}`
  }

  async function backendPostJson(path, bodyObj) {
    console.log('[Documents] 📤 POST request:', { path, bodyKeys: Object.keys(bodyObj || {}) })
    const url = buildUrl(path)
    console.log('[Documents] 📍 Full URL:', url)
    
    const headers = {
      'Content-Type': 'application/json',
      ...getAuthHeader()
    }
    console.log('[Documents] 🔑 Auth header present:', !!headers.Authorization)
    
    const res = await fetch(url, {
      method: 'POST',
      credentials: 'include',
      headers,
      body: JSON.stringify(bodyObj ?? {})
    })
    
    console.log('[Documents] 📥 Response:', { status: res.status, ok: res.ok, statusText: res.statusText })
    
    // Check for 401 and trigger re-login
    if (res.status === 401) {
      console.error('[Documents] ❌ 401 Unauthorized - token expired or invalid')
      showReLoginPrompt()
      throw new Error('Authentifizierung abgelaufen')
    }
    
    const text = await res.text()
    console.log('[Documents] 📄 Response text length:', text?.length || 0)
    let data = null
    if (text) {
      try { 
        data = JSON.parse(text)
        console.log('[Documents] ✅ Parsed JSON response:', { success: data?.success, hasDocument: !!data?.document })
      } catch (e) { 
        console.error('[Documents] ❌ Failed to parse JSON:', text.substring(0, 200))
        throw new Error('Ungültige Server-Antwort') 
      }
    }
    if (!res.ok) {
      console.error('[Documents] ❌ HTTP error:', { status: res.status, detail: data?.detail })
      const err = new Error(data?.detail || `HTTP ${res.status}`)
      err.status = res.status
      err.data = data
      throw err
    }
    return data
  }

  async function backendGetJson(path) {
    const url = buildUrl(path)
    const res = await fetch(url, {
      credentials: 'include',
      headers: {
        Accept: 'application/json',
        ...getAuthHeader()
      }
    })
    
    // Check for 401 and trigger re-login
    if (res.status === 401) {
      console.error('[Documents] 401 Unauthorized - token expired or invalid')
      showReLoginPrompt()
      throw new Error('Authentifizierung abgelaufen')
    }
    
    if (!res.ok) {
      const err = new Error(`HTTP ${res.status}`)
      err.status = res.status
      try {
        err.data = await res.json()
      } catch (_) {}
      throw err
    }
    return await res.json()
  }

  async function backendFetchRaw(path, options = {}) {
    const url = buildUrl(path)
    const res = await fetch(url, {
      credentials: 'include',
      ...options,
      headers: {
        ...(options.headers || {}),
        ...getAuthHeader()
      }
    })
    
    // Check for 401 and trigger re-login
    if (res.status === 401) {
      console.error('[Documents] 401 Unauthorized - token expired or invalid')
      showReLoginPrompt()
      throw new Error('Authentifizierung abgelaufen')
    }
    
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return res
  }

  const overlay = document.getElementById('genOverlay')
  const overlaySpinner = overlay?.querySelector('.generate-spinner')
  const overlayText = overlay?.querySelector('.generate-text')
  const overlaySubtext = overlay?.querySelector('.generate-subtext')

  function showProcessingOverlay(message = 'Dokument wird erstellt...', subtext = 'KI-Analyse läuft') {
    console.log('[Documents] Showing processing overlay:', message)
    if (!overlay) {
      console.warn('[Documents] Overlay element not found!')
      return
    }
    overlay.classList.remove('hidden')
    overlay.setAttribute('data-state', 'running')
    overlay.style.display = 'flex'  // Ensure it's visible
    overlaySpinner?.classList.remove('hidden')
    if (overlayText) overlayText.textContent = message
    if (overlaySubtext) {
      overlaySubtext.textContent = subtext || ''
      overlaySubtext.classList.toggle('hidden', !subtext)
    }
  }

  function showProcessingSuccess(message = 'Dokument aktualisiert.', subtext = '') {
    if (!overlay) return
    overlay.classList.remove('hidden')
    overlay.setAttribute('data-state', 'success')
    overlaySpinner?.classList.add('hidden')
    if (overlayText) overlayText.textContent = message
    if (overlaySubtext) {
      overlaySubtext.textContent = subtext || ''
      overlaySubtext.classList.toggle('hidden', !subtext)
    }
    window.setTimeout(() => hideProcessingOverlay(), 1200)
  }

  function showProcessingError(message = 'Fehler bei der Verarbeitung.') {
    if (!overlay) return
    overlay.classList.remove('hidden')
    overlay.setAttribute('data-state', 'error')
    overlaySpinner?.classList.add('hidden')
    if (overlayText) overlayText.textContent = message
    overlaySubtext?.classList.add('hidden')
    window.setTimeout(() => hideProcessingOverlay(), 1600)
  }

  function hideProcessingOverlay() {
    console.log('[Documents] Hiding processing overlay')
    if (!overlay) return
    overlay.classList.add('hidden')
    overlay.style.display = 'none'  // Ensure it's hidden
    overlay.removeAttribute('data-state')
    overlaySpinner?.classList.remove('hidden')
    if (overlaySubtext) {
      overlaySubtext.classList.remove('hidden')
      overlaySubtext.textContent = 'KI-Analyse läuft'
    }
    if (overlayText) overlayText.textContent = 'Dokument wird erstellt...'
  }

  function escapeHtml(str = '') {
    return str.replace(/[&<>"']/g, c => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    })[c] || c)
  }

  const INLINE_TEMPLATE_PREVIEW_LIMIT = 4
  let TEMPLATE_STORE = []
  let CLAUSE_STORE = []
  let PENDING_TEMPLATE_ID = null

  const templateStatus = document.getElementById('templateStatus')
  const clauseStatus = document.getElementById('clauseStatus')
  const clauseContainer = document.getElementById('clauseChipContainer')

  function setInlineMessage(el, message = '', tone = 'info') {
    if (!el) return
    if (!message) {
      el.textContent = ''
      el.classList.add('hidden')
      el.removeAttribute('data-tone')
      el.style.color = ''
      return
    }
    el.textContent = message
    el.classList.remove('hidden')
    el.setAttribute('data-tone', tone)
    el.style.color = tone === 'danger' ? '#b91c1c' : tone === 'success' ? '#047857' : ''
  }

  function makeLocalId(prefix = 'item') {
    try {
      if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
        return `${prefix}_${crypto.randomUUID()}`
      }
    } catch (_) {}
    return `${prefix}_${Math.random().toString(36).slice(2, 10)}`
  }

  async function documentAction(action, payload) {
    const target = ep.process || '/api/documents/process'
    return await backendPostJson(target, { action, payload })
  }

  let SELECTED_TEMPLATE = null

  // Capture any template id provided via URL early, before async loads
  try {
    const _params = new URLSearchParams(window.location.search)
    const _q = _params.get('templateId') || _params.get('tpl')
    if (_q) PENDING_TEMPLATE_ID = _q
  } catch(_) {}

  async function loadTemplates(){
    if (!portalUser.value) {
      // Even when unauthenticated, keep the UI useful with sample templates
      const samples = getSampleTemplates()
      TEMPLATE_STORE = samples
      try { renderInlineTemplates(samples) } catch(_) {}
      setInlineMessage(templateStatus, 'Beispielvorlagen (Bitte anmelden, um eigene Vorlagen zu sehen).', 'info')
      return
    }
    if (!ep.templates) {
      setInlineMessage(templateStatus, 'Keine Vorlage konfiguriert.', 'info')
      // Fallback: show a few sample templates so the left card is useful
      const samples = getSampleTemplates()
      TEMPLATE_STORE = samples
      try { renderInlineTemplates(samples) } catch(_) {}
      return
    }
    setInlineMessage(templateStatus, 'Vorlagen werden geladen…', 'info')
    try {
      const data = await backendGetJson(ep.templates)
      if (Array.isArray(data) && data.length) {
        TEMPLATE_STORE = data.map(t => {
          const id = String(t.id || t.slug || t.name || makeLocalId('tpl'))
          const title = t.title || t.name || 'Vorlage'
          return {
            id,
            title,
            docType: t.document_type || t.type || title,
            category: t.category || 'Allgemein',
            prompt: summarizeTemplateContent(t.content || ''),
            body: t.content || ''
          }
        })
        setInlineMessage(templateStatus, `${TEMPLATE_STORE.length} Vorlagen geladen.`, 'success')
      } else {
        // Fallback to curated samples when no user templates exist yet
        const samples = getSampleTemplates()
        TEMPLATE_STORE = samples
        setInlineMessage(templateStatus, 'Beispielvorlagen geladen. Eigene Vorlagen können im Bereich Vorlagen erstellt werden.', 'info')
      }
      // Populate inline quick-pick list
      try { renderInlineTemplates(TEMPLATE_STORE) } catch(_) {}
      // If a templateId was passed via query before templates loaded, apply it now
      if (PENDING_TEMPLATE_ID) {
        const hit = TEMPLATE_STORE.find(t => t.id === PENDING_TEMPLATE_ID)
        if (hit) {
          applyTemplate(hit)
          try { localStorage.setItem('anwalt.templateId', hit.id) } catch(_) {}
          setInlineMessage(templateStatus, `Vorlage "${hit.title}" übernommen.`, 'success')
          PENDING_TEMPLATE_ID = null
        }
      }
    } catch (err) {
      // On error, still offer samples to keep the UI functional
      const samples = getSampleTemplates()
      TEMPLATE_STORE = samples
      try { renderInlineTemplates(samples) } catch(_) {}
      const isAuthFailure = err && (err.status === 401 || /401/.test(String(err?.status || err?.message || '')))
      if (isAuthFailure) {
        setInlineMessage(templateStatus, 'Bitte melden Sie sich an, um Ihre Vorlagen zu sehen.', 'info')
        return
      }
      setInlineMessage(templateStatus, 'Vorlagen konnten nicht geladen werden. Beispielvorlagen werden angezeigt.', 'danger')
    }
  }

  // Provide a small, safe set of local samples as a UI fallback
  function getSampleTemplates(){
    return [
      {
        id: 'sample-nda',
        title: 'Geheimhaltungsvereinbarung (NDA) – Standard',
        docType: 'Geheimhaltungsvereinbarung (NDA)',
        category: 'Vertrag',
        prompt: 'Parteien, Zweck, Laufzeit, Vertragsstrafe, Gerichtsstand',
        body: '<h2>Geheimhaltungsvereinbarung (NDA)</h2><p>Zwischen den Parteien [A] und [B]…</p>'
      },
      {
        id: 'sample-klage',
        title: 'Klageentwurf – Zivilrecht',
        docType: 'Klageentwurf (Zivilrecht)',
        category: 'Zivil',
        prompt: 'Parteien, Anspruch, Streitwert, Beweismittel, Anträge',
        body: '<h2>Klage</h2><p>des Klägers [Name] gegen den Beklagten [Name]…</p>'
      },
      {
        id: 'sample-abmahnung',
        title: 'Abmahnung – UWG',
        docType: 'Abmahnung (UWG)',
        category: 'Wettbewerb',
        prompt: 'Adressat, Verstoß, Unterlassung, Frist, Vertragsstrafe',
        body: '<h2>Abmahnung</h2><p>Adressat: [Unternehmen], [Anschrift]…</p>'
      }
    ]
  }

  async function loadClauses(){
    if (!portalUser.value) {
      // Keep UI responsive, but clauses require auth: show empty with info
      CLAUSE_STORE = []
      renderClauseChips(CLAUSE_STORE)
      setInlineMessage(clauseStatus, 'Bitte anmelden, um optionale Bausteine zu sehen.', 'info')
      return
    }
    if (!ep.clauses) {
      setInlineMessage(clauseStatus, 'Keine Baustein-Schnittstelle konfiguriert.', 'info')
      renderClauseChips([])
      return
    }
    setInlineMessage(clauseStatus, 'Bausteine werden geladen…', 'info')
    try {
      const data = await backendGetJson(ep.clauses)
      if (Array.isArray(data) && data.length) {
        CLAUSE_STORE = data.map(c => ({
          id: String(c.id || c.slug || c.title || makeLocalId('clause')),
          title: c.title || 'Baustein',
          category: c.category || 'Allgemein',
          language: c.language || 'de',
          summary: summarizeTemplateContent(c.content || ''),
          content: c.content || ''
        }))
        setInlineMessage(clauseStatus, `${CLAUSE_STORE.length} Bausteine geladen.`, 'success')
      } else {
        CLAUSE_STORE = []
        setInlineMessage(clauseStatus, 'Keine optionalen Bausteine gefunden.', 'info')
      }
      renderClauseChips(CLAUSE_STORE)
    } catch (err) {
      CLAUSE_STORE = []
      renderClauseChips(CLAUSE_STORE)
      const isAuthFailure = err && (err.status === 401 || /401/.test(String(err?.status || err?.message || '')))
      if (isAuthFailure) {
        setInlineMessage(clauseStatus, 'Bitte melden Sie sich an, um optionale Bausteine zu nutzen.', 'info')
        return
      }
      setInlineMessage(clauseStatus, 'Bausteine konnten nicht geladen werden.', 'danger')
    }
  }

const ensureAuthenticatedMessaging = () => {
  catalogInitialized = false
  // Show sample templates so the inline list remains useful
  try {
    const samples = getSampleTemplates()
    TEMPLATE_STORE = samples
    renderInlineTemplates(samples)
  } catch (_) {}
  renderClauseChips([])
  setInlineMessage(templateStatus, 'Beispielvorlagen – bitte anmelden, um eigene Vorlagen zu sehen.', 'info')
  setInlineMessage(clauseStatus, 'Bitte melden Sie sich an, um optionale Bausteine zu nutzen.', 'info')
}

const triggerInitialLoads = () => {
  if (catalogInitialized) return
  catalogInitialized = true
  if (!ep.templates && !ep.clauses) return
  if (ep.templates) loadTemplates()
  if (ep.clauses) loadClauses()
}

  handleWindowFocus = () => {
    if (!catalogInitialized) return
    loadTemplates().catch(() => {})
  }

  ensureAuthenticatedMessaging()

  if (typeof window !== 'undefined') {
    window.addEventListener('focus', handleWindowFocus)
  }

  watch(() => portalUser.value, (val) => {
    if (val) {
      triggerInitialLoads()
    } else {
      ensureAuthenticatedMessaging()
    }
  })

  if (typeof loadUser === 'function') {
    loadUser()
      .then((val) => {
        if (val) {
          triggerInitialLoads()
        } else {
          ensureAuthenticatedMessaging()
        }
      })
      .catch(() => {})
  }


  function summarizeTemplateContent(html = '') {
    const text = html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()
    if (!text) return 'Keine Beschreibung hinterlegt.'
    return text.length > 180 ? `${text.slice(0, 177)}…` : text
  }

  // Legacy modal renderer removed; inline-only templates are used consistently

  function renderInlineTemplates(list){
    const cont = document.getElementById('inlineTemplates')
    if (!cont) return
    cont.innerHTML = ''
    const items = Array.isArray(list)
      ? list.slice(0, INLINE_TEMPLATE_PREVIEW_LIMIT)
      : []
    if (!items.length) {
      const msg = document.createElement('div')
      msg.className = 'helper-text'
      msg.textContent = 'Keine Vorlagen vorhanden.'
      cont.appendChild(msg)
      return
    }
    items.forEach(t => {
      const el = document.createElement('div')
      el.className = 'inline-template-card'
      const docLabel = (t.docType || t.title || 'Vorlage').toString().trim()
      const categoryLabel = (t.category || '').toString().trim()
      const descriptionSource = (t.prompt || summarizeTemplateContent(t.body || '') || '').toString().trim()
      const description = descriptionSource.length > 160 ? `${descriptionSource.slice(0, 157)}…` : (descriptionSource || 'Schnellstart für häufige Anwendungsfälle.')
      el.innerHTML = `
        <div class="inline-template-meta">
          <div class="inline-template-tags">
            <span class="inline-template-tag">${escapeHtml(docLabel)}</span>
            ${categoryLabel && categoryLabel.toLowerCase() !== docLabel.toLowerCase() ? `<span class="inline-template-tag inline-template-tag--muted">${escapeHtml(categoryLabel)}</span>` : ''}
          </div>
          <h3 class="inline-template-title">${escapeHtml(t.title)}</h3>
          <p class="inline-template-desc">${escapeHtml(description)}</p>
        </div>
        <div class="inline-template-actions">
          <button class="inline-template-apply" data-apply="${escapeHtml(t.id)}">Übernehmen</button>
          <button class="inline-template-view" data-view="${escapeHtml(t.id)}">Details</button>
        </div>
      `
      cont.appendChild(el)
    })
    if (Array.isArray(list) && list.length > INLINE_TEMPLATE_PREVIEW_LIMIT) {
      const note = document.createElement('p')
      note.className = 'helper-text inline-template-note'
      note.textContent = 'Weitere Vorlagen finden Sie im Vorlagenbereich.'
      cont.appendChild(note)
    }
    cont.querySelectorAll('[data-apply]').forEach(btn => btn.addEventListener('click', (e) => {
      const id = (e.currentTarget).getAttribute('data-apply')
      if (!id) return
      const tpl = TEMPLATE_STORE.find(x => x.id === id)
      if (!tpl) return updateFeedbackStatus('Vorlage konnte nicht geladen werden.', 'danger')
      applyTemplate(tpl)
      try { localStorage.setItem('anwalt.templateId', id) } catch(_) {}
    }))

    cont.querySelectorAll('[data-view]').forEach(btn => btn.addEventListener('click', (e) => {
      const id = (e.currentTarget).getAttribute('data-view')
      if (!id) return
      viewTemplateDetails(id)
    }))
  }

  function renderClauseChips(list){
    if (!clauseContainer) return
    clauseContainer.innerHTML = ''
    const entries = Array.isArray(list) ? list : []
    if (!entries.length) {
      const msg = document.createElement('span')
      msg.className = 'helper-text'
      msg.textContent = 'Keine optionalen Bausteine verfügbar.'
      clauseContainer.appendChild(msg)
      return
    }
    entries.forEach(clause => {
      const btn = document.createElement('button')
      btn.type = 'button'
      btn.className = 'chip'
      const label = clause.title || 'Baustein'
      btn.setAttribute('data-clause', label)
      if (clause.summary) {
        btn.title = clause.summary
      }
      btn.textContent = label
      clauseContainer.appendChild(btn)
    })
    cont.querySelectorAll('[data-view]').forEach(btn => btn.addEventListener('click', (e) => {
      const id = (e.currentTarget).getAttribute('data-view')
      if (!id) return
      viewTemplateDetails(id)
    }))
  }

  function setPreview(text){
    const preview = document.getElementById('preview')
    const wordCount = document.getElementById('wordCount')
    if (!preview) return
    preview.innerHTML = text || ''
    const trimmed = preview.innerText.trim()
    const wc = trimmed ? trimmed.split(/[ \t\r\n]+/).filter(Boolean).length : 0
    if (wordCount) wordCount.textContent = wc + ' Wörter'
  }

  function applyTemplate(tpl){
    SELECTED_TEMPLATE = tpl
    const docType = document.getElementById('docType')
    const req = document.getElementById('requirements')
    if (docType) docType.value = tpl.docType
    if (req) {
      req.value = `• Bitte Platzhalter ersetzen: [ … ]\n• ${tpl.prompt}`
      req.dispatchEvent(new Event('input'))
    }
    setActionBarVisibility(false)
  }

  // Upload interactions
  const dz = document.getElementById('dropzone')
  const fileInput = document.getElementById('fileInput')
  const uploadInfo = document.getElementById('uploadInfo')

  function resetUploadState(options = {}) {
    const { silent = false } = options || {}
    if (fileInput) fileInput.value = ''
    if (uploadInfo) {
      uploadInfo.innerHTML = ''
      uploadInfo.classList.add('hidden')
    }
    if (typeof window !== 'undefined') {
      window.__lastUploadId = null
      window.__lastUploadData = null
    }
    if (!silent) {
      updateFeedbackStatus('Upload zurückgesetzt.', 'info')
    }
  }
  dz?.addEventListener('click', () => fileInput?.click())
  dz?.addEventListener('dragover', (e)=>{ e.preventDefault(); dz.classList.add('dragover') })
  dz?.addEventListener('dragleave', ()=> dz.classList.remove('dragover'))
  dz?.addEventListener('drop', (e)=>{ e.preventDefault(); dz.classList.remove('dragover'); if(e.dataTransfer.files && e.dataTransfer.files.length){ fileInput.files = e.dataTransfer.files; handleFile(fileInput.files[0]) }})
  fileInput?.addEventListener('change', (e)=>{ const f = e.target.files[0]; if (f) handleFile(f) })
  document.getElementById('btnClearUpload')?.addEventListener('click', () => {
    resetUploadState()
  })

  async function handleFile(file){
    console.log('[Documents] 🔥 handleFile called:', {
      name: file.name,
      size: file.size,
      type: file.type,
      endpoint: ep.upload
    })
    
    if (!uploadInfo) {
      console.error('[Documents] ❌ uploadInfo element not found!')
      return
    }
    uploadInfo.textContent = 'Lade hoch: ' + file.name
    uploadInfo.classList.remove('hidden')
    
    // Show loading overlay
    showProcessingOverlay('Datei wird hochgeladen...', `${file.name} (${Math.round(file.size / 1024)} KB)`)
    
    try {
      const form = new FormData()
      form.append('file', file)
      
      console.log('[Documents] 📤 Uploading to:', ep.upload)
      console.log('[Documents] 🔑 Auth header present:', !!getAuthHeader().Authorization)
      
      const res = await backendFetchRaw(ep.upload, { method: 'POST', body: form })
      
      console.log('[Documents] 📥 Upload response:', { status: res.status, ok: res.ok })
      
      if (!res.ok) {
        console.error('[Documents] ❌ Upload failed with status:', res.status)
        throw new Error(`Upload failed: HTTP ${res.status}`)
      }
      
      const data = await res.json()
      console.log('[Documents] ✅ Upload successful:', data)
      
      const label = data?.filename || data?.name || file.name
      const sanitizedPreviewRaw = data?.sanitized_preview || data?.content_preview || ''
      const preview = sanitizedPreviewRaw ? escapeHtml(sanitizedPreviewRaw) : ''
      const redactionSummary = data?.replacements && Object.keys(data.replacements).length
        ? Object.entries(data.replacements)
            .map(([token, count]) => `${count}× ${token.replace(/\[|\]/g, '')}`)
            .join(', ')
        : ''
      const redactionLine = redactionSummary
        ? `Automatische Schwärzungen: ${escapeHtml(redactionSummary)}`
        : 'Automatische Schwärzungen: Keine'
      const previewBlock = preview
        ? `<div class="upload-preview"><strong>Bereinigte Vorschau</strong><br>${preview}</div>`
        : ''

      uploadInfo.innerHTML = `✓ Hochgeladen: ${escapeHtml(label)}<br>` +
        `<span class="upload-meta">${redactionLine}</span>${previewBlock}`
      
      window.__lastUploadId = data?.file_id || data?.fileId || data?.id
      window.__lastUploadData = { ...data, sanitized_preview: sanitizedPreviewRaw }
      
      updateFeedbackStatus(
        `✓ Upload erfolgreich! Datei bereit zur Verarbeitung. Schwärzungen: ${redactionSummary || 'Keine'}`,
        'success'
      )
      const successDetail = redactionSummary ? `${label} - ${redactionSummary}` : `${label} - Keine Schwärzungen erforderlich`
      showProcessingSuccess('Upload erfolgreich', successDetail)
      
    } catch (e) {
      console.error('[Documents] Upload error:', e)
      uploadInfo.textContent = `❌ Fehler: ${String(e)}`
      
      if (e.message?.includes('401') || e.message?.includes('Authentifizierung')) {
        updateFeedbackStatus(
          '⚠️ Upload fehlgeschlagen: Nicht angemeldet. Sie werden zur Anmeldung weitergeleitet...',
          'danger'
        )
        showProcessingError('Authentifizierung fehlgeschlagen')
      } else {
        updateFeedbackStatus(
          'Upload fehlgeschlagen. Bitte erneut versuchen.',
          'danger'
        )
        showProcessingError('Upload fehlgeschlagen')
      }
    }
  }

  // Character counter
  const req = document.getElementById('requirements')
  const charCount = document.getElementById('charCount')
  req?.addEventListener('input', ()=>{ if (charCount) charCount.textContent = req.value.length + ' Zeichen' })

  document.getElementById('btnInsertChecklist')?.addEventListener('click', ()=>{
    const sample = '• Beteiligte Parteien (Namen, Adressen)\n• Wesentliche Bedingungen (z. B. Preis, Laufzeit)\n• Besondere Anforderungen (z. B. Geheimhaltung, Vertragsstrafe)\n• Fristen/Termine (konkretes Datum oder Zeitraum)'
    if (req && req.value.indexOf('Beteiligte Parteien') === -1) req.value = (req.value ? req.value + '\n' : '') + sample
    req?.dispatchEvent(new Event('input'))
  })

  const clauseSelections = new Set()
  clauseContainer?.addEventListener('click', (event) => {
    const target = event.target instanceof HTMLElement ? event.target.closest('[data-clause]') : null
    if (!target || !(target instanceof HTMLElement)) return
    if (!req) {
      updateFeedbackStatus('Eingabefeld nicht gefunden.', 'danger')
      return
    }
    const txt = target.getAttribute('data-clause')
    if (!txt) return
    const marker = `• Klausel: ${txt}`
    const lines = req.value ? req.value.split('\n') : []

    if (clauseSelections.has(txt)) {
      clauseSelections.delete(txt)
      target.classList.remove('chip-active')
      req.value = lines.filter(line => line.trim() !== marker).join('\n')
      updateFeedbackStatus(`Optionaler Baustein "${txt}" wurde entfernt.`, 'info')
    } else {
      clauseSelections.add(txt)
      target.classList.add('chip-active')
      if (!lines.some(line => line.trim() === marker)) {
        req.value = (req.value ? req.value.trimEnd() + '\n' : '') + marker
      }
      updateFeedbackStatus(`Optionaler Baustein "${txt}" hinzugefügt.`, 'info')
    }

    req.dispatchEvent(new Event('input'))
  })

  // Generate
  const preview = document.getElementById('preview')
  const previewEmpty = document.getElementById('previewEmpty')
  const wordCount = document.getElementById('wordCount')
  const feedbackStatus = document.getElementById('feedbackStatus')

  let __feedbackHideTimer = null
  const updateFeedbackStatus = (message, tone = 'info') => {
    if (!feedbackStatus) return
    console.log('[Documents] Feedback status:', tone, '-', message)
    feedbackStatus.textContent = message
    feedbackStatus.classList.remove('hidden', 'visible', 'success', 'danger', 'info')
    feedbackStatus.classList.add('visible')
    if (tone) feedbackStatus.classList.add(tone)
    // Make sure it's visible
    feedbackStatus.style.display = 'block'
    // Auto-hide after a short delay (keep errors longer until dismissed by next action)
    try {
      if (__feedbackHideTimer) window.clearTimeout(__feedbackHideTimer)
      const hideAfter = tone === 'danger' ? 7000 : 3500
      __feedbackHideTimer = window.setTimeout(() => {
        clearFeedbackStatus()
      }, hideAfter)
    } catch (_) {}
  }

  const clearFeedbackStatus = () => {
    if (!feedbackStatus) return
    feedbackStatus.textContent = ''
    feedbackStatus.classList.remove('visible', 'success', 'danger', 'info')
    feedbackStatus.classList.add('hidden')
    feedbackStatus.style.display = 'none'
  }

  const runDocumentAnalysis = async () => {
    const docTypeInput = document.getElementById('docType')
    const requirementsInput = document.getElementById('requirements')
    const draftText = requirementsInput && 'value' in requirementsInput ? requirementsInput.value : ''
    const renderedText = preview?.innerText?.trim() || ''
    const contentForAnalysis = renderedText || draftText.trim()

    if (!contentForAnalysis) {
      updateFeedbackStatus('Keine Inhalte zur Analyse vorhanden. Bitte geben Sie Text ein oder generieren Sie ein Dokument.', 'info')
      return
    }

    const titleValue = docTypeInput && 'value' in docTypeInput && docTypeInput.value
      ? String(docTypeInput.value)
      : 'Dokument'

    try {
      updateFeedbackStatus('Dokument wird analysiert …', 'info')
      const response = await backendPostJson('/api/documents/analyze', {
        title: titleValue,
        content: contentForAnalysis,
        categories: Array.from(clauseSelections || []),
      })

      const analysis = response?.analysis || {}
      window.__lastDocumentAnalysis = analysis

      const summaryPoints = Array.isArray(analysis.summary_points)
        ? analysis.summary_points
        : Array.isArray(analysis.summary?.points)
          ? analysis.summary.points
          : []

      const headline = summaryPoints.length ? summaryPoints[0] : (analysis.summary || analysis.title || 'Analyse abgeschlossen')
      const nextSteps = Array.isArray(analysis.next_steps) ? analysis.next_steps : []

      let message = `Analyse abgeschlossen: ${headline}`
      if (nextSteps.length > 0) {
        message += ` — Empfehlung: ${nextSteps[0]}`
      }

      updateFeedbackStatus(message, 'success')
    } catch (err) {
      console.error('[Documents] Analyse fehlgeschlagen', err)
      updateFeedbackStatus('Dokumentanalyse fehlgeschlagen. Bitte versuchen Sie es erneut.', 'danger')
    }
  }

  const summarizeRedactions = (redactions) => {
    if (!redactions || typeof redactions !== 'object') return ''
    const parts = Object.entries(redactions)
      .filter(([_, count]) => typeof count === 'number' && count > 0)
      .map(([token, count]) => `${count}× ${token.replace(/\[|\]/g, '')}`)
    return parts.join(', ')
  }

  async function generate(){
    console.log('[Documents] 🚀 generate() called')
    const type = document.getElementById('docType')?.value || (SELECTED_TEMPLATE?.docType || 'Rechtsdokument')
    const instr = req?.value?.trim() || ''
    console.log('[Documents] 📋 Generate params:', { type, instrLength: instr.length, hasTemplate: !!SELECTED_TEMPLATE })
    
    if (!instr || instr.length < 10) {
      console.warn('[Documents] Instructions too short or empty')
      updateFeedbackStatus('Bitte geben Sie mindestens 10 Zeichen Sachverhalt ein.', 'danger')
      return
    }
    const toneLegal = document.getElementById('switchLegalTone')?.checked
    const plain = document.getElementById('switchPlain')?.checked
    const toneKey = toneLegal ? (plain ? 'legal+plain' : 'legal') : (plain ? 'plain' : 'neutral')

    previewEmpty?.classList.add('hidden')
    preview?.classList.add('hidden')
    setActionBarVisibility(false)
    clearFeedbackStatus()
    showProcessingOverlay('Dokument wird erstellt...', 'KI-Analyse läuft')

    let succeeded = false

    try {
      console.log('[Documents] Calling documentAction with generate')
      console.log('[Documents] API endpoint:', ep.process || '/api/documents/process')
      const response = await documentAction('generate', {
        title: type,
        document_type: type,
        instructions: instr,
        tone: toneKey,
        template_content: SELECTED_TEMPLATE?.body || '',
        template_id: SELECTED_TEMPLATE?.id || null,
        variables: {},
        model: null,
        uploadId: (window).__lastUploadId || null,
        metadata: window.__lastDocMetadata || null
      })

      if (response?.success === false) {
        const detail = response?.error || response?.message || 'KI-Dienst meldet einen Fehler'
        throw new Error(detail)
      }

      const doc = response?.document || {}
      const metadata = doc?.metadata || response?.metadata || {}
      const sanitizedInstructions = metadata?.sanitized?.instructions || ''
      const bodyHtml = doc?.content || doc?.html || doc?.contentHtml || (doc?.text ? `<p>${escapeHtml(doc.text).replace(/\n/g,'<br/>')}</p>` : '')
      if (!bodyHtml || !bodyHtml.trim()) {
        throw new Error('Backend lieferte kein verwendbares Dokument.')
      }

      const styleNote = toneLegal ? (plain ? 'Juristisch präzise – zugleich gut lesbar.' : 'Juristisch präzise Formulierung.') : (plain ? 'Leicht verständliche Formulierung.' : 'Neutraler Stil.')
      const header = `<h2 style="margin:0">${escapeHtml(type)}</h2><hr/><p><em>${styleNote}</em></p>`
      const documentHtml = header + bodyHtml
      setPreview(documentHtml)

      const resolvedDocId = doc?.id || response?.id || null
      window.__lastDocId = resolvedDocId
      window.__lastDocMetadata = metadata || {}
      window.__lastDownloadLinks = response?.download || doc?.download || null

      preview?.classList.remove('hidden'); if (preview) preview.style.display = ''
      previewEmpty?.classList.add('hidden')
      setActionBarVisibility(Boolean(resolvedDocId))
      // Always gate PDF download until explicit save
      try { exportPdfBtn?.classList.add('hidden') } catch(_) {}

      const summary = summarizeRedactions(metadata?.redactions)
      const statusText = summary ? `Dokument aktualisiert. Automatische Schwärzungen: ${summary}` : 'Dokument aktualisiert. Bitte prüfen.'
      updateFeedbackStatus(statusText, 'info')

      const successSub = summary ? `Schwärzungen: ${summary}` : (sanitizedInstructions ? 'Bereinigte Vorgaben übernommen.' : '')
      showProcessingSuccess('Dokument aktualisiert.', successSub)

      succeeded = true
    } catch (e) {
      console.error('[Documents] Generate failed:', e)
      console.error('[Documents] Error status:', e?.status)
      console.error('[Documents] Error message:', e?.message)
      const status = e?.status
      const detail = e?.message || 'Bitte erneut versuchen.'
      if (status === 401 || status === 403) {
        console.error('[Documents] AUTHENTICATION ERROR - User needs to log in!')
        updateFeedbackStatus('⚠️ Nicht angemeldet! Bitte melden Sie sich zuerst an.', 'danger')
      } else if (status === 404) {
        console.error('[Documents] ENDPOINT NOT FOUND - Backend may not be running')
        updateFeedbackStatus(`Generierung fehlgeschlagen: Endpunkt nicht gefunden (${ep.process})`, 'danger')
      } else {
        updateFeedbackStatus(`Generierung fehlgeschlagen: ${detail}`, 'danger')
      }
      preview?.classList.add('hidden'); if (preview) preview.style.display = 'none'
      previewEmpty?.classList.remove('hidden')
      setActionBarVisibility(false)
      showProcessingError('Generierung fehlgeschlagen.')
    } finally {
      if (succeeded) {
        const trimmed = preview?.innerText.trim()
        const wc = trimmed ? trimmed.split(/[ \t\r\n]+/).filter(Boolean).length : 0
        if (wordCount) wordCount.textContent = wc + ' Wörter'
      } else if (wordCount) {
        wordCount.textContent = '0 Wörter'
      }
    }
  }

  const genBtn = document.getElementById('btnGenerate')
  const analyzeBtn = document.getElementById('btnAnalyze')
  console.log('[Documents] 🔘 Generate button setup:', {
    found: !!genBtn,
    id: genBtn?.id,
    disabled: genBtn?.disabled,
    visible: genBtn ? window.getComputedStyle(genBtn).display !== 'none' : false
  })
  if (genBtn) {
    genBtn.addEventListener('click', () => {
      console.log('[Documents] ✅✅✅ Generate button CLICKED ✅✅✅')
      generate()
    })
    console.log('[Documents] ✓ Generate button listener attached successfully')
  } else {
    console.error('[Documents] ❌ Generate button NOT FOUND in DOM')
  }

  if (analyzeBtn) {
    analyzeBtn.addEventListener('click', () => {
      console.log('[Documents] 🧠 Analyse button clicked')
      runDocumentAnalysis()
    })
  }
  document.addEventListener('keydown', (e)=>{ if ((e.ctrlKey||e.metaKey) && e.key==='Enter') { generate() } })

  // Copy / Export
  const acceptBtn = document.getElementById('btnAccept')
  const rejectBtn = document.getElementById('btnReject')
  // annotate button removed per requirements
  const retryBtn = document.getElementById('btnRetry')
  const copyBtn = document.getElementById('btnCopy')
  const saveBtn = document.getElementById('btnSave')
  const exportPdfBtn = document.getElementById('btnExportPdf')
  const editBtn = document.getElementById('btnEdit')
  let isEditing = false

  acceptBtn?.addEventListener('click', () => {
    const content = preview?.innerText.trim()
    if (!content) return updateFeedbackStatus('Kein Dokument vorhanden. Bitte zuerst generieren.', 'danger')
    updateFeedbackStatus('Dokument akzeptiert und zur Übergabe markiert.', 'success')
  })

  rejectBtn?.addEventListener('click', () => {
    const content = preview?.innerText.trim()
    if (!content) return updateFeedbackStatus('Kein Dokument vorhanden. Bitte zuerst generieren.', 'danger')
    updateFeedbackStatus('Dokument abgelehnt. Bitte überarbeiten.', 'danger')
  })

  // no annotate handler

  retryBtn?.addEventListener('click', () => {
    updateFeedbackStatus('Neue Version wird erstellt...', 'info')
    generate()
  })

  copyBtn?.addEventListener('click', async () => {
    if (!preview) return
    try {
      const tmp = document.createElement('div')
      tmp.innerHTML = preview.innerHTML
      const textValue = tmp.innerText
      await navigator.clipboard.writeText(textValue)
      updateFeedbackStatus('Dokument in die Zwischenablage kopiert.', 'info')
    } catch (err) {
      updateFeedbackStatus('Kopieren nicht möglich.', 'danger')
    }
  })

  saveBtn?.addEventListener('click', async () => {
    if (!preview || !preview.innerHTML.trim()) {
      updateFeedbackStatus('Nichts zu speichern.', 'danger')
      return
    }
    try {
      if (!ep.save) throw new Error('Save endpoint not configured')
      const savePath = ep.save
      const saved = await backendPostJson(savePath, {
        title: document.getElementById('docType')?.value || 'Rechtsdokument',
        html: preview.innerHTML,
        uploadedFileId: window.__lastUploadId || null,
        metadata: window.__lastDocMetadata || null
      })
      const id = saved?.id || saved?.documentId
      window.__lastDocId = id
      if (!id) {
        updateFeedbackStatus('Gespeichert, aber keine ID erhalten.', 'danger')
        return
      }
      // Reveal PDF download icon after successful save
      exportPdfBtn?.classList.remove('hidden')
      updateFeedbackStatus('Dokument gespeichert. PDF-Download verfügbar.', 'success')
      // Make PDF icon visible only for a short time
      try { setTimeout(() => exportPdfBtn?.classList.add('hidden'), 15000) } catch(_) {}
    } catch (e) {
      updateFeedbackStatus('Speichern fehlgeschlagen: ' + String(e), 'danger')
    }
  })

  exportPdfBtn?.addEventListener('click', async () => {
    if (!preview || !preview.innerHTML.trim()) {
      updateFeedbackStatus('Nichts zu exportieren.', 'danger')
      return
    }
    try {
      const id = window.__lastDocId
      if (!id) {
        updateFeedbackStatus('Bitte zuerst speichern, dann PDF herunterladen.', 'info')
        return
      }
      const exportBase = ep.exportBase
      const url = `${exportBase}/${id}/export?format=pdf`
      const resp = await backendFetchRaw(url)
      const blob = await resp.blob()
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = (document.getElementById('docType')?.value || 'Dokument') + '.pdf'
      document.body.appendChild(a); a.click(); a.remove()
      updateFeedbackStatus('PDF erfolgreich heruntergeladen.', 'success')
    } catch (e) {
      updateFeedbackStatus('PDF-Export fehlgeschlagen: ' + String(e), 'danger')
    }
  })

  editBtn?.addEventListener('click', () => {
    if (!preview) return
    isEditing = !isEditing
    preview.setAttribute('contenteditable', isEditing ? 'true' : 'false')
    preview.classList.toggle('editing-active', isEditing)
    if (isEditing) preview?.focus()
    updateFeedbackStatus(isEditing ? 'Direktbearbeitung aktiviert. Änderungen werden lokal gespeichert.' : 'Direktbearbeitung beendet.', 'info')
  })

  // Clear
  const clearBtn = document.getElementById('btnClear')
  if (clearBtn) clearBtn.addEventListener('click', ()=>{
    resetUploadState({ silent: true })
    if (typeof window !== 'undefined') {
      window.__lastDocId = null
      window.__lastDocMetadata = null
      window.__lastDownloadLinks = null
    }
    const docType = document.getElementById('docType'); if (docType) docType.value=''
    if (req) { req.value=''; req.dispatchEvent(new Event('input')) }
    setPreview(''); preview?.classList.add('hidden'); previewEmpty?.classList.remove('hidden')
    SELECTED_TEMPLATE=null; try{ localStorage.removeItem('anwalt.templateId') }catch(_){ }
    setActionBarVisibility(false)
    clauseSelections.clear()
    clauseContainer?.querySelectorAll('.chip-active').forEach(btn => btn.classList.remove('chip-active'))
    updateFeedbackStatus('Formular wurde zurückgesetzt.', 'info')
    // Refresh inline quick picks so the left panel stays helpful
    try {
      // Prefer existing store, but fall back to samples to avoid empties
      const list = (Array.isArray(TEMPLATE_STORE) && TEMPLATE_STORE.length) ? TEMPLATE_STORE : getSampleTemplates()
      TEMPLATE_STORE = list
      renderInlineTemplates(list)
    } catch(_) {}
  })

  // Hover/focus hints for feedback icons (group delegation)
  const feedbackHint = document.getElementById('feedbackHint')
  const setHint = (text) => {
    if (!feedbackHint) return
    const nextText = text || ''
    const nextState = nextText ? '1' : '0'
    if (feedbackHint.textContent === nextText && feedbackHint.dataset.show === nextState) return
    feedbackHint.textContent = nextText
    feedbackHint.dataset.show = nextState
  }
  const actionBar = document.getElementById('actionBar')
  const feedbackGroup = actionBar?.querySelector('.feedback-group')
  feedbackGroup?.addEventListener('mouseover', (e) => {
    const btn = e.target?.closest?.('.feedback-button')
    if (btn && feedbackGroup.contains(btn)) setHint(btn.dataset.hint || '')
  })
  feedbackGroup?.addEventListener('mouseleave', () => setHint(''))
  feedbackGroup?.addEventListener('focusin', (e) => {
    const btn = e.target?.closest?.('.feedback-button')
    if (btn && feedbackGroup.contains(btn)) setHint(btn.dataset.hint || '')
  })
  feedbackGroup?.addEventListener('focusout', (e) => {
    // Clear when focus leaves the group
    const next = e.relatedTarget
    if (!next || !feedbackGroup.contains(next)) setHint('')
  })

  // Initial state
  try { renderInlineTemplates(TEMPLATE_STORE) } catch(_) {}
  try {
    const preview = document.getElementById('preview')
    const previewEmpty = document.getElementById('previewEmpty')
    if (preview) preview.innerHTML = ''
    preview?.classList.add('hidden')
    previewEmpty?.classList.remove('hidden')
    setActionBarVisibility(false)
  } catch (_) {}
  
  // Log initialization checkpoint
  console.log('[Documents] 🔍 Initialization checkpoint:', {
    generateBtn: !!document.getElementById('btnGenerate'),
    dropzone: !!document.getElementById('dropzone'),
    fileInput: !!document.getElementById('fileInput'),
    endpoints: ep,
    authToken: !!getAuthHeader().Authorization,
    apiBase: apiBase
  })
  
  console.log('[Documents] ✅ onMounted completed successfully')
  window.__DOCUMENTS_INITIALIZED = true

  // After core init, try to adopt a template selection from Templates page
  try {
    const params = new URLSearchParams(window.location.search)
    const qId = params.get('templateId') || params.get('tpl')
    if (qId) PENDING_TEMPLATE_ID = qId
    const raw = localStorage.getItem('anwalt.templateSelection')
    if (raw) {
      try {
        const incoming = JSON.parse(raw)
        const tpl = {
          id: String(incoming.id || incoming.name || makeLocalId('tpl')),
          title: incoming.name || incoming.title || 'Vorlage',
          docType: incoming.name || 'Rechtsdokument',
          category: incoming.category || 'Allgemein',
          prompt: summarizeTemplateContent(incoming.content || ''),
          body: incoming.content || ''
        }
        applyTemplate(tpl)
        setInlineMessage(templateStatus, `Vorlage "${tpl.title}" übernommen.`, 'success')
      } catch(_) {}
      // Clean up after applying once
      try { localStorage.removeItem('anwalt.templateSelection') } catch(_) {}
    }
  } catch(_) {}

  // Hand-off from Email page: prefill fields when available
  try {
    const rawEmailPrefill = localStorage.getItem('anwalt.emailToDocument')
    if (rawEmailPrefill) {
      const incoming = JSON.parse(rawEmailPrefill)
      const subject = (incoming?.subject || 'E-Mail')
      const content = (incoming?.content || '').trim()
      const docTypeEl = document.getElementById('docType')
      const reqEl = document.getElementById('requirements')
      if (docTypeEl) docTypeEl.value = subject
      if (reqEl) reqEl.value = content
      // Provide a small confirmation toast/status
      updateFeedbackStatus('E-Mail-Inhalt übernommen. Sie können jetzt generieren.', 'success')
      // Clean up key to avoid reapplying on refresh
      try { localStorage.removeItem('anwalt.emailToDocument') } catch(_) {}
    }
  } catch(e) {
    console.warn('[Documents] Email hand-off parse failed:', e)
  }
  
  } catch (error) {
    console.error('[Documents] CRITICAL: onMounted failed:', error)
    console.error('[Documents] Error stack:', error.stack)
    // Show error to user
    const mainElement = document.querySelector('.documents-page')
    if (mainElement) {
      const errorDiv = document.createElement('div')
      errorDiv.style.cssText = 'position:fixed;top:20px;left:50%;transform:translateX(-50%);background:#fee;border:2px solid #f00;padding:20px;border-radius:8px;z-index:9999;max-width:600px;'
      errorDiv.innerHTML = `<strong>Fehler beim Laden der Seite:</strong><br>${error.message}<br><small>Bitte Seite neu laden oder Support kontaktieren.</small>`
      document.body.appendChild(errorDiv)
    }
    throw error
  }
})

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('focus', handleWindowFocus)
  }
})
</script>

<style scoped>
:global(:root) {
  --surface: #ffffff;
  --surface-alt: #f5f7ff;
  --border: #e3e8fb;
  --text: #111827;
  --muted: #6b7299;
  --primary: #556cf0;
  --primary-soft: rgba(85, 108, 240, 0.14);
  --primary-strong: #556cf0;
}

a, button {
  font-family: inherit;
}


.documents-page {
  min-height: 100vh;
  background: var(--surface-alt);
  animation: pageFade 0.35s ease both;
}

.header-stack {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.process-steps-wrapper {
  display: grid;
  grid-template-columns: repeat(1, minmax(0, 1fr));
  gap: 12px;
  max-width: 1200px;
  padding: 24px 16px 12px;
  margin: 0 auto;
}

@media (min-width: 1280px) {
  .process-steps-wrapper {
    max-width: 1360px;
  }
}

@media (min-width: 768px) {
  .process-steps-wrapper {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.step-card {
  position: relative;
  display: flex;
  gap: 14px;
  align-items: center;
  padding: 16px 18px;
  border-radius: 14px;
  border: 1px solid #dee6ff;
  background: #fff;
  box-shadow: 0 16px 36px rgba(85, 108, 240, 0.08);
  transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
  animation: cardRise 0.4s ease both;
}

.step-card:hover {
  border-color: #c8d4ff;
  box-shadow: 0 22px 44px rgba(85, 108, 240, 0.18);
  transform: translateY(-2px);
}

.step-accent {
  width: 4px;
  height: 40px;
  border-radius: 999px;
  background: linear-gradient(180deg, #7f98ff 0%, #5e76f0 100%);
}

.step-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
}

.step-subtitle {
  font-size: 12px;
  color: #6e78a5;
  margin-top: 2px;
}

.documents-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px 48px;
}

@media (min-width: 1280px) {
  .documents-container {
    max-width: 1360px;
  }
}

@media (min-width: 1024px) {
  .documents-container {
    padding: 0 32px 64px;
  }
}

.documents-grid {
  display: grid;
  gap: 24px;
  grid-template-columns: 1fr;
  align-items: stretch;
}

@media (min-width: 1024px) {
  .documents-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    align-items: stretch;
    height: calc(100vh - 220px);
  }
  .documents-grid > section {
    display: flex;
    flex-direction: column;
    min-height: 0;
  }
  .content-card {
    height: 100%;
  }
}

@media (min-width: 1280px) {
  .documents-grid {
    gap: 36px;
  }
}

@media (min-width: 1440px) {
  .documents-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.inputs-panel,
.preview-panel {
  display: flex;
  flex-direction: column;
  min-height: 0;
  flex: 1;
}

@media (min-width: 1024px) {
  .inputs-panel,
  .preview-panel {
    height: 100%;
    flex: 1 1 auto;
    max-width: none;
  }
  .inputs-panel { padding-right: 16px; }
  .preview-panel { padding-left: 16px; }
}

.panel-scroll {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-height: 0;
}

@media (min-width: 1024px) {
  .panel-scroll {
    height: 100%;
    padding-right: 0;
  }
}

.content-card {
  background: #fff;
  border: 1px solid #eef2f9;
  border-radius: 16px;
  box-shadow: 0 12px 40px rgba(15, 23, 42, 0.06);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: cardRise 0.45s ease both;
  min-height: 0;
}

.form-card {
  overflow: visible;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.form-card .card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.form-card--combined .card-body--combined {
  flex: 1;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 32px;
  overflow-y: auto;
  min-height: 0;
}

.card-section {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.card-section + .card-section {
  padding-top: 24px;
  border-top: 1px solid rgba(211, 220, 255, 0.7);
}

.card-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.card-section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
}

.card-section-subtle {
  font-size: 13px;
  color: var(--muted);
  margin-top: 2px;
}

.card-section-body {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-card .action-footer {
  margin-top: auto;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 22px;
  border-bottom: 1px solid rgba(211, 220, 255, 0.7);
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
}

.card-subtle {
  font-size: 13px;
  font-weight: 400;
  color: var(--muted);
  margin-left: 6px;
}

.card-body {
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.link-accent {
  border: none;
  background: none;
  color: var(--primary-strong, #556cf0);
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: color 0.2s ease, text-shadow 0.2s ease;
}

.link-accent:hover {
  color: #3f55d5;
  text-shadow: 0 6px 18px rgba(69, 89, 223, 0.35);
}

.link-accent:focus-visible {
  outline: 2px solid rgba(69, 89, 223, 0.35);
  outline-offset: 2px;
}

.link-small {
  font-size: 12px;
}

.field {
  display: flex !important;
  flex-direction: column;
  gap: 8px;
}

.field.action-row {
  display: flex !important;
  visibility: visible !important;
  opacity: 1 !important;
}

.field-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.field-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
}

.field-input,
.field-textarea,
.modal-search {
  width: 100%;
  border: 1px solid rgba(205, 212, 246, 0.9);
  border-radius: 14px;
  padding: 10px 12px;
  font-size: 15px;
  line-height: 1.6;
  background: #fff;
  color: var(--text);
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.field-input:focus,
.field-textarea:focus,
.modal-search:focus {
  border-color: rgba(85, 108, 240, 0.85);
  box-shadow: 0 0 0 4px rgba(85, 108, 240, 0.18);
  background: rgba(243, 246, 255, 0.85);
  outline: none;
}

.field-textarea {
  min-height: 140px;
  resize: vertical;
}

/* Inline templates quick-pick */
.inline-templates {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

.inline-template-card {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 18px 20px;
  border: 1px solid rgba(205, 212, 246, 0.9);
  border-radius: 16px;
  background: linear-gradient(180deg, #ffffff 0%, #f7f8ff 100%);
  box-shadow: 0 18px 32px rgba(85, 108, 240, 0.08);
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease, background 0.25s ease;
}

.inline-template-card:hover {
  transform: translateY(-3px);
  border-color: rgba(85, 108, 240, 0.35);
  box-shadow: 0 24px 48px rgba(85, 108, 240, 0.16);
  background: linear-gradient(180deg, #ffffff 0%, #eef2ff 100%);
}

.inline-template-meta {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.inline-template-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.inline-template-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(85, 108, 240, 0.16);
  color: var(--primary-strong);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.01em;
  text-transform: uppercase;
}

.inline-template-tag--muted {
  background: rgba(17, 24, 39, 0.08);
  color: var(--muted);
}

.inline-template-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
  line-height: 1.45;
  margin: 0;
}

.inline-template-desc {
  font-size: 13px;
  color: var(--muted);
  line-height: 1.5;
}

.inline-template-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.inline-template-apply {
  border: none;
  background: linear-gradient(135deg, #6279f5 0%, #4f63de 100%);
  color: #fff;
  font-weight: 600;
  font-size: 13px;
  padding: 8px 16px;
  border-radius: 999px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.inline-template-apply:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(79, 99, 222, 0.25);
}

.inline-template-view {
  border: 1px solid rgba(85, 108, 240, 0.28);
  background: transparent;
  color: var(--primary-strong);
  font-weight: 600;
  font-size: 12px;
  padding: 7px 14px;
  border-radius: 999px;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.inline-template-view:hover {
  background: rgba(85, 108, 240, 0.1);
  border-color: rgba(85, 108, 240, 0.48);
}

.helper-text {
  font-size: 12px;
  color: #6e78a5;
}

.upload-meta {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #4b5563;
}

.upload-preview {
  margin-top: 6px;
  padding: 8px;
  border-radius: 8px;
  background: rgba(37, 99, 235, 0.06);
  color: #1f2937;
  font-size: 12px;
  line-height: 1.4;
  max-height: 120px;
  overflow-y: auto;
}

.tone-toggle {
  display: flex;
  gap: 18px;
  align-items: center;
  font-size: 12px;
  color: #6e78a5;
}

.tone-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.switch {
  position: relative;
  width: 40px;
  height: 22px;
  background: rgba(190, 199, 255, 0.7);
  border-radius: 11px;
  transition: background-color 0.2s ease;
  cursor: pointer;
}

.switch input {
  display: none;
}

.switch .dot {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 18px;
  height: 18px;
  background: #fff;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(88, 109, 215, 0.25);
  transition: transform 0.2s ease;
}

.switch input:checked ~ .dot {
  transform: translateX(18px);
}

.switch:focus-visible {
  outline: 2px solid rgba(45, 74, 160, 0.4);
  outline-offset: 2px;
}

.switch input:checked + .dot,
.switch input:checked ~ .dot {
  background: #fff;
}

.switch input:checked {
  background: transparent;
}

.switch input:checked::after {
  content: '';
}

.switch.has-checked,
.switch:has(input:checked) {
  background: linear-gradient(135deg, #7f98ff 0%, #5f74f1 100%);
}

.clause-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.chip {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid #d7dce5;
  background: #fff;
  font-size: 12px;
  font-weight: 500;
  color: #24335a;
  cursor: pointer;
  transition: border-color 0.2s ease, background-color 0.2s ease, color 0.2s ease;
}

.chip-active,
.chip.chip-active:hover {
  border-color: #5f74f1;
  background: rgba(95, 116, 241, 0.16);
  color: #1d2b6d;
}

.chip:hover {
  border-color: var(--primary-strong, #556cf0);
  background: rgba(85, 108, 240, 0.16);
  color: #4b5fe5;
}

.btn-ghost {
  height: 44px;
  padding: 0 16px;
  border-radius: 12px;
  border: 1px solid transparent;
  background: rgba(244, 247, 255, 0.9);
  font-size: 14px;
  font-weight: 500;
  color: #1f2a51;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.btn-ghost:hover,
.btn-ghost:focus-visible {
  border-color: rgba(187, 198, 255, 0.95);
  background: rgba(230, 236, 255, 0.95);
  box-shadow: 0 12px 28px rgba(140, 159, 255, 0.18);
  outline: none;
}

.action-row {
  padding-top: 6px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-start;
  gap: 12px;
}

.action-button-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.action-footer-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  justify-content: space-between;
}

.action-footer {
  position: sticky;
  bottom: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 0;
  padding: 16px 24px;
  background: #ffffff;
  border-top: 1px solid #eef2f9;
  box-shadow: 0 -6px 18px rgba(15, 23, 42, 0.06);
  border-bottom-left-radius: 16px;
  border-bottom-right-radius: 16px;
  z-index: 6;
}

.action-footer .helper-text {
  margin: 6px 0 0;
}

.primary-action-group {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  margin-left: auto;
}


.dropzone {
  position: relative;
  border: 1px dashed rgba(139, 154, 255, 0.6);
  border-radius: 18px;
  padding: 34px 24px;
  background: rgba(238, 241, 255, 0.65);
  text-align: center;
  cursor: pointer;
  transition: border-color 0.25s ease, background 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
}

.dropzone:hover {
  border-color: rgba(85, 108, 240, 0.85);
  background: rgba(225, 232, 255, 0.9);
  box-shadow: 0 22px 60px rgba(85, 108, 240, 0.22);
  transform: translateY(-1px);
}

.dropzone-icon {
  width: 48px;
  height: 48px;
  color: var(--primary-strong, #556cf0);
  margin: 0 auto 12px;
}

.dropzone-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 6px;
}

.dropzone-title span {
  color: var(--primary-strong, #556cf0);
}

.dropzone-formats {
  font-size: 12px;
  color: #7280a7;
}

.upload-info {
  border-radius: 14px;
  border: 1px solid rgba(85, 108, 240, 0.35);
  background: rgba(233, 237, 255, 0.9);
  padding: 14px 18px;
  font-size: 14px;
  color: #414f87;
}

.template-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 18px 20px;
  border-radius: 16px;
  border: 1px solid rgba(208, 216, 255, 0.85);
  background: #fff;
  box-shadow: 0 20px 48px rgba(85, 108, 240, 0.16);
  transition: border-color 0.22s ease, box-shadow 0.22s ease, transform 0.22s ease;
  animation: cardRise 0.45s ease 0.08s both;
}

.template-card:hover {
  border-color: rgba(173, 186, 255, 0.9);
  box-shadow: 0 26px 64px rgba(85, 108, 240, 0.22);
  transform: translateY(-2px);
}

.template-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.template-card-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.template-card-title {
  font-size: 14px;
  font-weight: 600;
  color: #233160;
}

.template-card-text {
  font-size: 12px;
  color: #6a7199;
  line-height: 1.6;
}

.template-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(134, 151, 247, 0.22);
  color: #4b5fe5;
  font-size: 11px;
  font-weight: 600;
}

.template-apply {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 38px;
  padding: 0 18px;
  border-radius: 12px;
  border: none;
  background: var(--primary-strong, #556cf0);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}

.template-apply:hover {
  background: #4b5fe5;
  box-shadow: 0 14px 36px rgba(63, 85, 213, 0.3);
}

.template-apply:active {
  transform: translateY(1px);
}

.template-apply:focus-visible {
  outline: 2px solid rgba(69, 89, 223, 0.35);
  outline-offset: 2px;
}

.preview-container {
  background: #fff;
  border: 1px solid #eef2f9;
  border-radius: 16px;
  box-shadow: 0 12px 40px rgba(15, 23, 42, 0.06);
  overflow: hidden;
  animation: cardRise 0.5s ease 0.05s both;
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 540px;
}

@media (min-width: 1024px) {
  .preview-container {
    height: 100%;
    min-height: 0;
  }
}

.preview-toolbar {
  position: sticky;
  top: 0;
  z-index: 5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  padding: 20px 24px;
  border-bottom: 1px solid #eef2f9;
  background: #ffffff;
}

.preview-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-height: 0;
}

@media (max-width: 1023px) {
  .inputs-panel,
  .preview-panel {
    height: auto;
  }

  .panel-scroll {
    height: auto;
    padding-right: 0;
  }

  .preview-container {
    min-height: 540px;
  }

  .preview-body {
    gap: 16px;
  }

  .preview-toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }

  .toolbar-left {
    justify-content: space-between;
  }

  .toolbar-actions {
    width: 100%;
    justify-content: stretch;
    gap: 10px;
  }

  .toolbar-btn {
    flex: 1 1 auto;
    justify-content: center;
  }

  .toolbar-helper {
    margin: -8px 0 4px;
  }

  .action-footer {
    position: static;
    margin: 16px 0 0;
    padding: 16px 0 0;
    box-shadow: none;
    border-top: 1px solid rgba(211, 220, 255, 0.7);
  }
}

.feedback-status {
  display: none;
  margin: 0;
  padding: 10px 14px;
  border-radius: 12px;
  border: 1px solid rgba(208, 216, 255, 0.85);
  background: rgba(234, 238, 255, 0.72);
  font-size: 13px;
  color: #21305c;
  box-shadow: 0 12px 26px rgba(155, 169, 255, 0.18);
  width: 100%;
}

.feedback-status.visible { display: block; }

.feedback-hint {
  margin: 0;
  padding: 4px 8px;
  font-size: 12px;
  color: #6e78a5;
  text-align: center;
  height: 18px; /* reserve space to prevent shift */
  line-height: 18px;
  pointer-events: none;
  opacity: 0;
}

.feedback-hint[data-show='1'] { opacity: 1; }

.feedback-status.success {
  border-color: rgba(173, 224, 200, 0.9);
  background: rgba(215, 240, 227, 0.8);
  color: #185b3b;
}

.feedback-status.danger {
  border-color: rgba(255, 199, 199, 0.9);
  background: rgba(255, 226, 226, 0.78);
  color: #8f1f1f;
}

.feedback-status.info {
  border-color: rgba(204, 212, 250, 0.9);
  background: rgba(223, 229, 255, 0.82);
  color: #27326a;
}

.toolbar-meta {
  font-size: 13px;
  color: #5a6390;
  font-weight: 500;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
  pointer-events: auto;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 44px;
  padding: 0 20px;
  border-radius: 14px;
  border: 1px solid transparent;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease, color 0.2s ease;
}

.toolbar-btn:focus-visible {
  outline: 2px solid rgba(85, 108, 240, 0.4);
  outline-offset: 2px;
}

.toolbar-btn-secondary {
  background: rgba(238, 243, 255, 0.9);
  border-color: rgba(196, 206, 249, 0.8);
  color: #4a5edf;
}

.toolbar-btn-secondary:hover,
.toolbar-btn-secondary:focus-visible {
  background: rgba(222, 231, 255, 0.95);
  border-color: rgba(174, 188, 250, 0.95);
  box-shadow: 0 12px 28px rgba(89, 108, 217, 0.22);
}

.toolbar-btn-primary {
  background: linear-gradient(135deg, #556cf0, #4559df);
  border-color: #4559df;
  color: #fff;
  box-shadow: 0 16px 38px rgba(69, 89, 223, 0.35);
}

.toolbar-btn-primary:hover {
  background: linear-gradient(135deg, #4b5fe5, #3f55d5);
  border-color: #3f55d5;
  box-shadow: 0 18px 42px rgba(63, 85, 213, 0.38);
}

.toolbar-btn-primary:focus-visible {
  outline: 2px solid rgba(69, 89, 223, 0.35);
  outline-offset: 2px;
}

.toolbar-icon {
  width: 16px;
  height: 16px;
}

.toolbar-helper {
  margin: 0 24px 4px;
}

.btn-generate {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  height: 44px;
  padding: 0 20px;
  min-width: 0;
  border-radius: 14px;
  border: none;
  background: linear-gradient(135deg, #556cf0, #4559df);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.25s ease, transform 0.2s ease, box-shadow 0.25s ease;
  position: relative;
  z-index: 10;
}

.btn-generate:hover {
  background: linear-gradient(135deg, #4b5fe5, #3f55d5);
  box-shadow: 0 18px 46px rgba(63, 85, 213, 0.32);
}

.btn-generate:active {
  transform: translateY(1px);
}

.btn-generate:focus-visible {
  outline: 2px solid rgba(69, 89, 223, 0.35);
  outline-offset: 2px;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.action-bar {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 0 24px 12px;
  width: 100%;
  margin-top: auto;
}

.action-groups {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  justify-content: space-between;
}

.feedback-group,
.utility-group {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.feedback-button {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: none;
  background: transparent;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.feedback-button:hover { box-shadow: none; }

.feedback-button:focus-visible {
  outline: 2px solid rgba(85, 108, 240, 0.35);
  outline-offset: 2px;
}

.feedback-button.feedback-accept { color: #16603c; }
.feedback-button.feedback-reject { color: #9f1f1f; }
.feedback-button.feedback-note { color: #5b3bbd; }
.feedback-button.feedback-retry { color: #2a4098; }

.feedback-button.feedback-accept:hover { background: rgba(22, 96, 60, 0.08); }
.feedback-button.feedback-reject:hover { background: rgba(159, 31, 31, 0.08); }
.feedback-button.feedback-note:hover { background: rgba(91, 59, 189, 0.08); }
.feedback-button.feedback-retry:hover { background: rgba(42, 64, 152, 0.08); }

.feedback-icon {
  width: 18px;
  height: 18px;
}

.btn-action {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 38px;
  padding: 0 12px;
  border-radius: 12px;
  border: 1px solid transparent;
  background: #f8f9ff;
  font-size: 13px;
  font-weight: 500;
  color: #1e2a51;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

/* Compact icon-only button variant for tight layouts */
.btn-action.icon-only {
  width: 38px;
  height: 38px;
  padding: 0;
  justify-content: center;
}

.btn-action:hover {
  background: rgba(85, 108, 240, 0.18);
  border-color: rgba(173, 186, 255, 0.9);
  box-shadow: 0 12px 30px rgba(145, 163, 255, 0.25);
}

.btn-action:focus-visible {
  outline: 2px solid rgba(85, 108, 240, 0.4);
  outline-offset: 2px;
}

.preview-area {
  position: relative;
  flex: 1;
  min-height: 480px;
  overflow-y: auto;
  padding: 32px 32px 48px;
  background: linear-gradient(180deg, rgba(242, 245, 255, 0.85) 0%, rgba(233, 238, 255, 0.6) 100%);
}

.preview-area::-webkit-scrollbar {
  width: 6px;
}

.preview-area::-webkit-scrollbar-thumb {
  background: rgba(164, 177, 236, 0.45);
  border-radius: 999px;
}

.preview-empty {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  text-align: center;
}

.preview-placeholder {
  max-width: 320px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
}

.preview-icon {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: rgba(85, 108, 240, 0.18);
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-icon-svg {
  width: 36px;
  height: 36px;
  color: var(--primary-strong, #556cf0);
}

.preview-empty-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
}

.preview-empty-text {
  font-size: 13px;
  color: #5c658c;
  line-height: 1.6;
}

.generate-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: center;
  justify-content: center;
  border-radius: 18px;
  background: rgba(247, 249, 255, 0.92);
}

.generate-spinner {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 4px solid rgba(85, 108, 240, 0.25);
  border-top-color: var(--primary-strong, #556cf0);
  animation: spin 1s linear infinite;
}

.generate-text {
  font-size: 14px;
  font-weight: 600;
  color: #253060;
}

.generate-subtext {
  font-size: 12px;
  color: #6e78a5;
}


@keyframes pageFade {
  from { opacity: 0; transform: translateY(18px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes cardRise {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.preview-content {
  --page-width: 794px; /* approx A4 @96dpi */
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 20px 50px rgba(31, 41, 55, 0.08);
  border: 1px solid rgba(225, 231, 255, 0.8);
  padding: 56px 64px; /* ~1 inch margins */
  font-size: 15px;
  line-height: 1.75;
  color: #1f2937;
  width: 100%;
  max-width: var(--page-width);
  margin: 24px auto 40px;
  -webkit-hyphens: auto;
  hyphens: auto;
  word-break: break-word;
  text-align: left;
}

.preview-content.editing-active {
  outline: 2px solid rgba(85, 108, 240, 0.45);
  outline-offset: 6px;
  background: rgba(238, 241, 255, 0.45);
  border-radius: 12px;
}

.preview-content :deep(hr) { margin: 20px 0; border: 0; border-top: 1px solid #e5e8f0; }

.preview-content :deep(h1) {
  font-size: 22px;
  line-height: 1.4;
  font-weight: 700;
  margin: 0 0 16px 0;
  color: #111827;
}

.preview-content :deep(h2) {
  font-size: 18px;
  line-height: 1.5;
  font-weight: 700;
  margin: 18px 0 12px 0;
  color: #111827;
}

.preview-content :deep(h3) {
  font-size: 16px;
  line-height: 1.5;
  font-weight: 600;
  margin: 16px 0 10px 0;
  color: #1f2937;
}

.preview-content :deep(p) {
  margin: 0 0 14px 0;
}

.preview-content :deep(ul),
.preview-content :deep(ol) {
  margin: 14px 0 16px 0;
  padding-left: 24px;
}

.preview-content :deep(li) { margin-bottom: 8px; }

.preview-content :deep(blockquote) {
  margin: 14px 0;
  padding: 10px 14px;
  border-left: 3px solid #cfd7ff;
  background: #f7f9ff;
}

.shortcut-bar {
  padding: 16px 24px;
  margin: 20px 0 0 0;
  text-align: center;
  font-size: 12px;
  color: #6e78a5;
  background: rgba(247, 249, 255, 0.5);
  border-top: 1px solid rgba(211, 220, 255, 0.5);
  width: 100%;
  box-sizing: border-box;
}

.shortcut-bar kbd {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  padding: 2px 6px;
  margin: 0 4px;
  border-radius: 6px;
  border: 1px solid rgba(189, 201, 255, 0.9);
  background: rgba(230, 235, 255, 0.9);
  font-size: 12px;
  font-weight: 600;
  color: #2e3a66;
}

/* removed legacy modal styles (no longer used) */

@media (max-width: 1023px) {
  .preview-panel {
    position: static;
    top: auto;
    padding-left: 0;
  }
  .inputs-panel {
    padding-right: 0;
  }
  .feedback-status {
    margin: 12px 0 0;
  }
}

@media (max-width: 767px) {
  .documents-container {
    padding: 0 16px 56px;
  }
  .header-stack {
    width: 100%;
  }
  .preview-toolbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  .btn-generate {
    width: 100%;
    justify-content: center;
  }
  .primary-action-group {
    flex: 1 1 100%;
    justify-content: center;
    margin-left: 0;
  }
  .action-button-group {
    width: 100%;
    justify-content: center;
    margin-left: 0;
  }
  .action-bar {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  .action-footer-row {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }
  .feedback-group,
  .utility-group {
    width: 100%;
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
  }
  .feedback-button,
  .btn-action {
    flex: 1 1 48%;
    justify-content: center;
  }
  .documents-grid {
    gap: 20px;
  }
}

/* Override to match Overview page */
.sidebar-link.active {
  background-color: #eff6ff !important;
  color: #556cf0 !important;
  box-shadow: none !important;
  transform: none !important;
}

</style>
