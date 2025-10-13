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
            <div class="content-card">
              <div class="card-header">
                <h2 class="card-title">Dokument hochladen <span class="card-subtle">(optional)</span></h2>
                <button type="button" class="link-accent" id="btnClearUpload">Zurücksetzen</button>
              </div>
              <div class="card-body">
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

            <div class="content-card">
              <div class="card-header">
                <h2 class="card-title">Angaben &amp; Vorgaben</h2>
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
              <div class="card-body">
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
                  <label class="field-label">Optionale Bausteine</label>
                  <div class="clause-chips">
                    <button class="chip" data-clause="Gerichtsstand">Gerichtsstand</button>
                    <button class="chip" data-clause="Vertragsstrafe">Vertragsstrafe</button>
                    <button class="chip" data-clause="Vertraulichkeit">Vertraulichkeit</button>
                    <button class="chip" data-clause="Kündigung">Kündigung</button>
                    <button class="chip" data-clause="Verjährung">Verjährung</button>
                  </div>
                </div>

                <div class="field action-row">
                  <div class="action-button-group">
                    <button id="btnTemplates" type="button" class="btn-ghost">Vorlagen</button>
                    <button id="btnClear" type="button" class="btn-ghost">Löschen</button>
                  </div>
                  <button id="btnSend" type="button" class="btn-send">
                    <svg class="btn-send-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10l9-7 9 7-9 7-9-7z"/>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 19h18"/>
                    </svg>
                    Zur Verarbeitung senden
                  </button>
                </div>
              </div>
            </div>
          </section>

          <section class="preview-panel">
            <div id="previewContainer" class="preview-container" style="min-height: 600px;">
              <div class="preview-toolbar">
                <span id="wordCount" class="toolbar-meta">0 Wörter</span>
                <div class="toolbar-actions">
                  <button id="btnGenerate" type="button" class="btn-generate">
                    <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                    </svg>
                    Dokument erzeugen
                  </button>
                  <div id="actionBar" class="action-bar hidden">
                <div id="feedbackStatus" class="feedback-status hidden"></div>
                    <div class="feedback-group">
                      <button class="feedback-button feedback-accept" id="btnAccept" aria-label="Dokument akzeptieren" type="button">
                        <svg class="feedback-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4"/>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 21c4.971 0 9-4.029 9-9s-4.029-9-9-9-9 4.029-9 9 4.029 9 9 9z"/>
                        </svg>
                      </button>
                      <button class="feedback-button feedback-reject" id="btnReject" aria-label="Dokument ablehnen" type="button">
                        <svg class="feedback-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 9l-6 6m0-6l6 6"/>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 21c4.971 0 9-4.029 9-9s-4.029-9-9-9-9 4.029-9 9 4.029 9 9 9z"/>
                        </svg>
                      </button>
                      <button class="feedback-button feedback-note" id="btnAnnotate" aria-label="Anmerkung verfassen" type="button">
                        <svg class="feedback-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 20h9"/>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16.5 3.5a2.121 2.121 0 013 3L8 18l-4 1 1-4 11.5-11.5z"/>
                        </svg>
                      </button>
                      <button class="feedback-button feedback-retry" id="btnRetry" aria-label="Erneut generieren" type="button">
                        <svg class="feedback-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v6h6"/>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 20v-6h-6"/>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.5 13.5a7 7 0 019.9 4.5M18.5 10.5a7 7 0 00-9.9-4.5"/>
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
                      <button class="btn-action" id="btnExport" aria-label="DOCX exportieren" type="button">
                        <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                        DOCX
                      </button>
                      <button class="btn-action" id="btnExportPdf" aria-label="PDF exportieren" type="button">
                        <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"/></svg>
                        PDF
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div id="previewArea" class="preview-area">
                <div id="previewEmpty" class="preview-empty">
                  <div class="preview-placeholder">
                    <div class="preview-icon">
                      <svg class="preview-icon-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
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
            </div>

            <p class="shortcut-bar">
              <kbd>Strg</kbd> + <kbd>Enter</kbd> generiert neu • <kbd>Alt</kbd> + <kbd>C</kbd> kopiert
            </p>
          </section>
        </div>
      </div>
    </main>
    <!-- Templates Modal -->
    <div id="tplModal" class="modal">
      <div class="modal-shell">
        <div class="modal-header">
          <h3 class="modal-title">Vorlagen auswählen</h3>
          <button class="modal-close" id="tplClose" aria-label="Schließen">
            <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <input id="tplSearch" class="modal-search field-input" placeholder="Vorlagen durchsuchen (z. B. NDA, Klage, Abmahnung)"/>
          <div id="tplGrid" class="modal-grid"></div>
        </div>
      </div>
    </div>
  </PortalShell>
</template>

<script setup>
import { useTour } from '#imports'
import { onMounted } from 'vue'
import { useRuntimeConfig } from '#imports'
import PortalShell from '~/components/PortalShell.vue'

definePageMeta({ layout: false })

onMounted(() => {
  const $ = (s, r=document) => r.querySelector(s)
  const $$ = (s, r=document) => Array.from(r.querySelectorAll(s))
  const { public: { apiBase = '', apiEndpoints = {} } } = useRuntimeConfig()
  const proxyPostUrl = '/api/auth/proxy'
  const proxyGetUrl = '/api/auth/proxy'
  const proxyUploadUrl = '/api/auth/proxy-upload'
  const ep = {
    generate: apiEndpoints.generate || (apiBase ? `${apiBase}/ai/generate-document` : ''),
    generateSimple: apiBase ? `${apiBase}/ai/generate-document-simple` : '',
    templates: apiEndpoints.templates || (apiBase ? `${apiBase}/templates` : ''),
    upload: apiEndpoints.upload || '',
    save: apiEndpoints.save || '',
    exportBase: apiEndpoints.exportBase || '',
    status: apiEndpoints.status || ''
  }

  function getAuthHeader() {
    try {
      let token = localStorage.getItem('token') || localStorage.getItem('access_token') || localStorage.getItem('sat') || localStorage.getItem('anwalts_auth_token')
      if (!token && document && document.cookie) {
        const map = Object.fromEntries(document.cookie.split(';').map(s => {
          const i = s.indexOf('=');
          const k = decodeURIComponent(s.slice(0, i).trim());
          const v = decodeURIComponent(s.slice(i + 1));
          return [k, v]
        }))
        token = map['token'] || map['access_token'] || map['sat'] || map['auth_token']
      }
      return token ? { Authorization: `Bearer ${decodeURIComponent(token)}` } : {}
    } catch (_) { return {} }
  }

  async function proxyPost(path, bodyObj) {
    const res = await fetch(proxyPostUrl, {
      method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path, method: 'POST', body: bodyObj })
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return res
  }
  async function proxyGet(pathWithQuery) {
    const url = proxyGetUrl + '?path=' + encodeURIComponent(pathWithQuery)
    const res = await fetch(url, { credentials: 'include' })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return res
  }

  let TEMPLATE_STORE = [
    {
      id: 'nda',
      title: 'NDA – Standard (DE)',
      category: 'Vertrag',
      docType: 'Geheimhaltungsvereinbarung (NDA)',
      prompt: 'Parteien, Zweck, Laufzeit, Vertragsstrafe, Gerichtsstand',
      body: `
<h2>Geheimhaltungsvereinbarung (NDA)</h2>
<p>zwischen <strong>[PARTEI A]</strong>, [ADRESSE A], und <strong>[PARTEI B]</strong>, [ADRESSE B] (zusammen die "Parteien").</p>
<h3>§ 1 Gegenstand</h3>
<p>Die Parteien beabsichtigen, Informationen zum Zweck <strong>[ZWECK]</strong> auszutauschen. "Vertrauliche Informationen" sind alle nicht öffentlichen Informationen, gleich in welcher Form.</p>
<h3>§ 2 Pflichten</h3>
<p>Empfangende Partei: (a) nutzt Informationen nur zu dem genannten Zweck, (b) wahrt Vertraulichkeit mindestens mit derselben Sorgfalt wie eigene Informationen, (c) gibt sie nur an <strong>[KREIS DER EMPFÄNGER]</strong> weiter.</p>
<h3>§ 3 Laufzeit</h3>
<p>Diese Vereinbarung gilt ab Unterzeichnung für <strong>[LAUFZEIT]</strong>.</p>
<h3>§ 4 Vertragsstrafe</h3>
<p>Bei schuldhaftem Verstoß schuldet die verletzende Partei eine angemessene Vertragsstrafe <strong>[VERTRAGSSTRAFE]</strong>.</p>
<h3>§ 5 Rückgabe</h3>
<p>Auf Verlangen sind Kopien und Unterlagen unverzüglich zurückzugeben oder zu löschen.</p>
<h3>§ 6 Schlussbestimmungen</h3>
<p>Gerichtsstand: <strong>[GERICHTSSTAND]</strong>. Anwendbares Recht: <strong>[RECHT]</strong>. Änderungen bedürfen der Schriftform.</p>
<p>Ort/Datum: [ORT], [DATUM] – Unterschriften: [PARTEI A], [PARTEI B]</p>`
    },
    {
      id: 'klage',
      title: 'Klageentwurf – Zivil',
      category: 'Zivil',
      docType: 'Klageentwurf (Zivilrecht)',
      prompt: 'Parteien, Anspruch, Streitwert, Beweismittel, Anträge',
      body: `
<h2>Klage</h2>
<p>des Klägers <strong>[KLÄGER]</strong>, gegen den Beklagten <strong>[BEKLAGTER]</strong>.</p>
<h3>I. Zuständigkeit</h3>
<p>Sachliche und örtliche Zuständigkeit: <strong>[ZUSTÄNDIGKEIT]</strong>.</p>
<h3>II. Sachverhalt</h3>
<p>[SACHVERHALT – CHRONOLOGIE]</p>
<h3>III. Rechtliche Würdigung</h3>
<p>Anspruchsgrundlagen: <strong>[ANSPRÜCHE]</strong>. Der Anspruch ist begründet, weil …</p>
<h3>IV. Beweismittel</h3>
<p>[BEWEISMITTEL (Urkunden, Zeugen, Sachverständige)]</p>
<h3>V. Anträge</h3>
<p>1. Der Beklagte wird verurteilt, an den Kläger <strong>[BETRAG]</strong> zu zahlen.<br>2. Hilfsweise: <strong>[HILFSANTRAG]</strong>.</p>
<p>Streitwert: <strong>[STREITWERT]</strong>. Datum/Unterschrift.</p>`
    },
    {
      id: 'abmahnung',
      title: 'Abmahnung – UWG',
      category: 'Wettbewerb',
      docType: 'Abmahnung (UWG)',
      prompt: 'Adressat, Verstoß, Unterlassung, Frist, Vertragsstrafe',
      body: `
<h2>Abmahnung</h2>
<p>Adressat: <strong>[UNTERNEHMEN]</strong>, <strong>[ANSCHRIFT]</strong>.</p>
<p>Sie bewerben/verwenden <strong>[VERSTOSS]</strong> und verstoßen damit gegen <strong>[RECHTSNORM]</strong>.</p>
<h3>Forderungen</h3>
<ol>
<li>Abgabe einer strafbewehrten Unterlassungserklärung (Vertragsstrafe: <strong>[STRAFE]</strong>).</li>
<li>Auskunft über Umfang der Handlung.</li>
<li>Kostenersatz nach RVG aus <strong>[GEGENSTANDSWERT]</strong>.</li>
</ol>
<p>Frist: <strong>[FRIST]</strong>. Andernfalls gerichtliche Schritte.</p>`
    },
    {
      id: 'vergleich',
      title: 'Vergleichsangebot',
      category: 'Zivil',
      docType: 'Vergleichsangebot',
      prompt: 'Zahlung, Bedingungen, Verzicht, Vertraulichkeit, Datum',
      body: `
<h2>Vergleichsangebot</h2>
<p>Zwischen <strong>[PARTEI A]</strong> und <strong>[PARTEI B]</strong>.</p>
<h3>1. Leistung</h3>
<p>[PARTEI A] zahlt an [PARTEI B] <strong>[BETRAG]</strong> bis <strong>[FÄLLIGKEIT]</strong>.</p>
<h3>2. Gegenseitiger Verzicht</h3>
<p>Mit Erfüllung sind sämtliche Ansprüche erledigt.</p>
<h3>3. Vertraulichkeit</h3>
<p>Inhalt dieses Vergleichs ist vertraulich.</p>
<h3>4. Schluss</h3>
<p>Gerichtsstand <strong>[GERICHTSSTAND]</strong>. Datum/Unterschrift.</p>`
    }
  ]

  let SELECTED_TEMPLATE = null

  function renderTemplates(list){
    const grid = document.getElementById('tplGrid')
    if (!grid) return
    grid.innerHTML = ''
    list.forEach(t => {
      const card = document.createElement('div')
      card.className = 'template-card'
      card.innerHTML = `
        <div class="template-card-header">
          <div class="template-card-info">
            <div class="template-card-title">${t.title}</div>
            <div class="template-card-text">${t.prompt}</div>
          </div>
          <span class="template-badge">${t.category}</span>
        </div>
        <button class="template-apply" data-apply="${t.id}">Übernehmen</button>`
      grid.appendChild(card)
    })

    grid.querySelectorAll('[data-apply]').forEach(btn => btn.addEventListener('click', (e)=>{
      const id = e.currentTarget.getAttribute('data-apply')
      const tpl = TEMPLATE_STORE.find(x=>x.id===id)
      applyTemplate(tpl)
      try{ localStorage.setItem('anwalt.templateId', id) }catch(_){ }
      document.getElementById('tplModal')?.classList.remove('open')
    }))
  }

  function setPreview(text){
    const preview = document.getElementById('preview')
    const wordCount = document.getElementById('wordCount')
    if (!preview) return
    preview.innerHTML = text.split('\n').join('<br/>')
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
    const actionBar = document.getElementById('actionBar'); actionBar?.classList.add('hidden')
  }

  // Upload interactions
  const dz = document.getElementById('dropzone')
  const fileInput = document.getElementById('fileInput')
  const uploadInfo = document.getElementById('uploadInfo')
  dz?.addEventListener('click', () => fileInput?.click())
  dz?.addEventListener('dragover', (e)=>{ e.preventDefault(); dz.classList.add('dragover') })
  dz?.addEventListener('dragleave', ()=> dz.classList.remove('dragover'))
  dz?.addEventListener('drop', (e)=>{ e.preventDefault(); dz.classList.remove('dragover'); if(e.dataTransfer.files && e.dataTransfer.files.length){ fileInput.files = e.dataTransfer.files; handleFile(fileInput.files[0]) }})
  fileInput?.addEventListener('change', (e)=>{ const f = e.target.files[0]; if (f) handleFile(f) })
  document.getElementById('btnClearUpload')?.addEventListener('click', ()=>{ if (fileInput) fileInput.value=''; uploadInfo?.classList.add('hidden'); if (uploadInfo) uploadInfo.textContent='' })

  async function handleFile(file){
    if (!uploadInfo) return
    uploadInfo.textContent = 'Lade hoch: ' + file.name
    uploadInfo.classList.remove('hidden')
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await fetch(proxyUploadUrl, { method: 'POST', body: form, credentials: 'include' })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      const label = data?.filename || data?.name || file.name
      uploadInfo.textContent = `✓ Hochgeladen: ${label}`
      window.__lastUploadId = data?.id || data?.fileId || data?.file_id
    } catch (e) {
      uploadInfo.textContent = `Fehler: ${String(e)}`
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

  const clauseButtons = $$('[data-clause]')
  if (Array.isArray(clauseButtons)) clauseButtons.forEach(btn=> btn.addEventListener('click', ()=>{
    if (!req) return
    const txt = btn.getAttribute('data-clause')
    req.value += '\n• Klausel: ' + txt
    req.dispatchEvent(new Event('input'))
  }))

  ;(async () => {
    try {
      if (!ep.templates) return
      const res = await fetch(ep.templates, { credentials: 'include', headers: { ...getAuthHeader() } })
      if (res.ok) {
        const data = await res.json()
        if (Array.isArray(data) && data.length) {
          TEMPLATE_STORE = data.map(t => ({
            id: t.id || t.key || t.slug,
            title: t.name || t.title,
            category: t.category || t.type || 'Allgemein',
            docType: t.type === 'document' ? (t.name || 'Rechtsdokument') : 'Rechtsdokument',
            prompt: t.description || '',
            body: t.content || ''
          }))
        }
      }
    } catch (_) {}
  })()

  // Templates modal
  const tplModal = document.getElementById('tplModal')
  document.getElementById('btnTemplates')?.addEventListener('click', ()=> {
    tplModal?.classList.add('open')
    renderTemplates(TEMPLATE_STORE)
    const inp = document.getElementById('tplSearch'); if (inp) inp.value=''
  })
  document.getElementById('tplClose')?.addEventListener('click', ()=> tplModal?.classList.remove('open'))
  document.getElementById('tplSearch')?.addEventListener('input', (e)=>{
    const q = e.target.value.toLowerCase()
    const filtered = TEMPLATE_STORE.filter(t => (t.title + ' ' + t.category + ' ' + t.prompt).toLowerCase().includes(q))
    renderTemplates(filtered)
  })

  // Generate
  const preview = document.getElementById('preview')
  const previewEmpty = document.getElementById('previewEmpty')
  const wordCount = document.getElementById('wordCount')
  const feedbackStatus = document.getElementById('feedbackStatus')

  const updateFeedbackStatus = (message, tone = 'info') => {
    if (!feedbackStatus) return
    feedbackStatus.textContent = message
    feedbackStatus.classList.remove('hidden', 'visible', 'success', 'danger', 'info')
    feedbackStatus.classList.add('visible')
    if (tone) feedbackStatus.classList.add(tone)
  }

  const clearFeedbackStatus = () => {
    if (!feedbackStatus) return
    feedbackStatus.textContent = ''
    feedbackStatus.classList.remove('visible', 'success', 'danger', 'info')
    feedbackStatus.classList.add('hidden')
  }

  async function generate(){
    previewEmpty?.classList.add('hidden')
    preview?.classList.add('hidden')
    const overlay = document.getElementById('genOverlay')
    overlay?.classList.remove('hidden')
    const actionBar = document.getElementById('actionBar')
    actionBar?.classList.add('hidden')
    clearFeedbackStatus()
    let contentSet = false

    const type = document.getElementById('docType')?.value || (SELECTED_TEMPLATE?.docType || 'Rechtsdokument')
    const instr = req?.value.trim() || ''
    const toneLegal = document.getElementById('switchLegalTone')?.checked
    const plain = document.getElementById('switchPlain')?.checked

    try {
      const candidates = [
        apiEndpoints.generateSimple || (apiBase ? `${apiBase}/ai/generate-document-simple` : ''),
        apiEndpoints.generate || (apiBase ? `${apiBase}/ai/generate-document` : '')
      ].filter(Boolean)

      let payload = null
      let saw403 = false
      for (const url of candidates) {
        try {
          const isSimple = url.includes('generate-document-simple')
          const reqBody = isSimple
            ? {
                title: type,
                document_type: type,
                instructions: instr,
                tone: toneLegal ? (plain ? 'legal+plain' : 'legal') : (plain ? 'plain' : 'neutral'),
                template_content: SELECTED_TEMPLATE?.body || '',
                template_id: SELECTED_TEMPLATE?.id || null,
                variables: {},
                model: null,
                uploadId: (window).__lastUploadId || null
              }
            : {
                title: type,
                document_type: type,
                template_content: SELECTED_TEMPLATE?.body || '',
                variables: {},
                template_id: SELECTED_TEMPLATE?.id || null,
                model: null
              }

          const res = await proxyPost(url, reqBody)
          if (res.status === 403) { saw403 = true; continue }
          if (res.ok) { payload = await res.json(); break }
        } catch (_) { /* try next */ }
      }
      if (!payload) throw new Error('Generate endpoint not configured')
      const doc = payload?.document || payload
      const bodyHtml = doc?.content || doc?.html || doc?.contentHtml || (doc?.text ? `<p>${doc.text.replace(/\n/g,'<br/>')}</p>` : '')
      if (bodyHtml) {
        const styleNote = toneLegal ? (plain ? 'Juristisch präzise – zugleich gut lesbar.' : 'Juristisch präzise Formulierung.') : (plain ? 'Leicht verständliche Formulierung.' : 'Neutraler Stil.')
        const header = `<h2 style="margin:0">${type}</h2><hr/><p><em>${styleNote}</em></p>`
        const withInstr = instr ? `<h3>Vorgaben</h3><p>${instr.replace(/\n/g,'<br/>')}</p>` : ''
        setPreview(header + bodyHtml + withInstr)
        contentSet = true
        actionBar?.classList.remove('hidden'); if (actionBar) actionBar.style.display = 'flex'
      }
    } catch (e) {
      console.error('Generate failed:', e)
      if (saw403) updateFeedbackStatus('Nicht autorisiert (403). Bitte erneut anmelden oder Token prüfen.', 'danger')
      else updateFeedbackStatus('Generierung fehlgeschlagen. Bitte erneut versuchen.', 'danger')
    } finally {
      if (contentSet) {
        preview?.classList.remove('hidden'); if (preview) preview.style.display = ''
        previewEmpty?.classList.add('hidden')
        updateFeedbackStatus('Dokument aktualisiert. Bitte prüfen.', 'info')
      } else {
        preview?.classList.add('hidden'); if (preview) preview.style.display = 'none'
        previewEmpty?.classList.remove('hidden')
        actionBar?.classList.add('hidden'); if (actionBar) actionBar.style.display = 'none'
        clearFeedbackStatus()
      }
      overlay?.classList.add('hidden')
      const trimmed = preview?.innerText.trim()
      const wc = trimmed ? trimmed.split(/[ \t\r\n]+/).filter(Boolean).length : 0
      if (wordCount) wordCount.textContent = wc + ' Wörter'
    }
  }

  const genBtn = document.getElementById('btnGenerate')
  if (genBtn) genBtn.addEventListener('click', generate)
  document.addEventListener('keydown', (e)=>{ if ((e.ctrlKey||e.metaKey) && e.key==='Enter') { generate() } })

  // Copy / Export
  const acceptBtn = document.getElementById('btnAccept')
  const rejectBtn = document.getElementById('btnReject')
  const annotateBtn = document.getElementById('btnAnnotate')
  const retryBtn = document.getElementById('btnRetry')
  const copyBtn = document.getElementById('btnCopy')
  const exportBtn = document.getElementById('btnExport')
  const exportPdfBtn = document.getElementById('btnExportPdf')
  const editBtn = document.getElementById('btnEdit')
  const sendBtn = document.getElementById('btnSend')
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

  annotateBtn?.addEventListener('click', () => {
    if (!req) return
    req.focus({ preventScroll: false })
    req.scrollIntoView({ behavior: 'smooth', block: 'center' })
    updateFeedbackStatus('Bitte Anmerkungen ergänzen. Eingabefeld wurde fokussiert.', 'info')
  })

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

  exportBtn?.addEventListener('click', async () => {
    if (!preview || !preview.innerHTML.trim()) {
      updateFeedbackStatus('Nichts zu exportieren.', 'danger')
      return
    }
    try {
      if (!ep.save) throw new Error('Save endpoint not configured')
      const savePath = (apiEndpoints.save || (apiBase ? `${apiBase}/documents/save` : ''))
      const res = await proxyPost(savePath, {
        title: document.getElementById('docType')?.value || 'Rechtsdokument',
        html: preview.innerHTML,
        uploadedFileId: window.__lastUploadId || null
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const saved = await res.json()
      const id = saved?.id || saved?.documentId
      window.__lastDocId = id
      if (!id) {
        updateFeedbackStatus('Gespeichert, aber keine ID erhalten.', 'danger')
        return
      }
      const exportBase = apiEndpoints.exportBase || (apiBase ? `${apiBase}/documents` : '')
      const url = `${exportBase}/${id}/export?format=docx`
      const resp = await proxyGet(url)
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      const blob = await resp.blob()
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = (document.getElementById('docType')?.value || 'Dokument') + '.docx'
      document.body.appendChild(a); a.click(); a.remove()
      updateFeedbackStatus('DOCX-Datei erfolgreich exportiert.', 'success')
    } catch (e) {
      updateFeedbackStatus('Export fehlgeschlagen: ' + String(e), 'danger')
    }
  })

  exportPdfBtn?.addEventListener('click', async () => {
    if (!preview || !preview.innerHTML.trim()) {
      updateFeedbackStatus('Nichts zu exportieren.', 'danger')
      return
    }
    try {
      if (!ep.save) throw new Error('Save endpoint not configured')
      const savePath = (apiEndpoints.save || (apiBase ? `${apiBase}/documents/save` : ''))
      const res = await proxyPost(savePath, { title: document.getElementById('docType')?.value || 'Rechtsdokument', html: preview.innerHTML })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const saved = await res.json()
      const id = saved?.id || saved?.documentId
      window.__lastDocId = id
      const exportBase = apiEndpoints.exportBase || (apiBase ? `${apiBase}/documents` : '')
      if (id && exportBase) {
        const url = `${exportBase}/${id}/export?format=pdf`
        const resp = await proxyGet(url)
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        const blob = await resp.blob()
        const a = document.createElement('a')
        a.href = URL.createObjectURL(blob)
        a.download = (document.getElementById('docType')?.value || 'Dokument') + '.pdf'
        document.body.appendChild(a); a.click(); a.remove()
        updateFeedbackStatus('PDF-Datei erfolgreich exportiert.', 'success')
      }
    } catch (e) {
      updateFeedbackStatus('Export fehlgeschlagen: ' + String(e), 'danger')
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

  sendBtn?.addEventListener('click', () => {
    const content = preview?.innerText.trim()
    if (!content) return updateFeedbackStatus('Kein Dokument vorhanden. Bitte zuerst generieren.', 'danger')
    updateFeedbackStatus('Dokument zur Verarbeitung übermittelt.', 'success')
  })

  // Clear
  const clearBtn = document.getElementById('btnClear')
  if (clearBtn) clearBtn.addEventListener('click', ()=>{
    const docType = document.getElementById('docType'); if (docType) docType.value=''
    if (req) { req.value=''; req.dispatchEvent(new Event('input')) }
    setPreview(''); preview?.classList.add('hidden'); previewEmpty?.classList.remove('hidden')
    SELECTED_TEMPLATE=null; try{ localStorage.removeItem('anwalt.templateId') }catch(_){ }
    const actionBar = document.getElementById('actionBar'); actionBar?.classList.add('hidden')
  })

  // Initial state
  renderTemplates(TEMPLATE_STORE)
  try {
    const preview = document.getElementById('preview')
    const previewEmpty = document.getElementById('previewEmpty')
    const actionBar = document.getElementById('actionBar')
    if (preview) preview.innerHTML = ''
    preview?.classList.add('hidden')
    previewEmpty?.classList.remove('hidden')
    actionBar?.classList.add('hidden')
  } catch (_) {}
})
</script>

<style scoped>
:root {
  --surface: #ffffff;
  --surface-alt: #f5f7ff;
  --border: #e3e8fb;
  --text: #111827;
  --muted: #6b7299;
  --primary: #2563eb;
  --primary-soft: rgba(111, 134, 255, 0.14);
  --primary-strong: #2563eb;
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
  box-shadow: 0 16px 36px rgba(111, 134, 255, 0.08);
  transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
  animation: cardRise 0.4s ease both;
}

.step-card:hover {
  border-color: #c8d4ff;
  box-shadow: 0 22px 44px rgba(111, 134, 255, 0.18);
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
}

@media (min-width: 1024px) {
  .documents-grid {
    grid-template-columns: minmax(0, 1.65fr) minmax(0, 1fr);
    gap: 32px;
    align-items: flex-start;
  }
}

.inputs-panel,
.preview-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

@media (min-width: 1024px) {
  .inputs-panel {
    padding-right: 12px;
  }
  .preview-panel {
    padding-left: 12px;
    position: sticky;
    top: 32px;
  }
}

.content-card {
  background: #fff;
  border: 1px solid rgba(209, 218, 255, 0.8);
  border-radius: 20px;
  box-shadow: 0 20px 50px rgba(111, 134, 255, 0.12);
  overflow: hidden;
  animation: cardRise 0.45s ease both;
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
  color: var(--primary-strong);
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: color 0.2s ease, text-shadow 0.2s ease;
}

.link-accent:hover {
  color: #4057e6;
  text-shadow: 0 6px 18px rgba(79, 110, 245, 0.35);
}

.link-accent:focus-visible {
  outline: 2px solid rgba(79, 110, 245, 0.35);
  outline-offset: 2px;
}

.link-small {
  font-size: 12px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
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
  border-color: rgba(111, 134, 255, 0.85);
  box-shadow: 0 0 0 4px rgba(111, 134, 255, 0.18);
  background: rgba(243, 246, 255, 0.85);
  outline: none;
}

.field-textarea {
  min-height: 140px;
  resize: vertical;
}

.helper-text {
  font-size: 12px;
  color: #6e78a5;
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

.chip:hover {
  border-color: var(--primary-strong);
  background: rgba(111, 134, 255, 0.16);
  color: #4357ea;
}

.btn-ghost {
  height: 44px;
  padding: 0 16px;
  border-radius: 12px;
  border: 1px solid rgba(206, 214, 255, 0.9);
  background: rgba(244, 247, 255, 0.9);
  font-size: 14px;
  font-weight: 500;
  color: #1f2a51;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.btn-ghost:hover {
  background: rgba(230, 236, 255, 0.95);
  border-color: rgba(187, 198, 255, 0.95);
  box-shadow: 0 12px 28px rgba(140, 159, 255, 0.18);
}

.btn-ghost:focus-visible {
  outline: 2px solid rgba(45, 74, 160, 0.4);
  outline-offset: 2px;
}

.action-row {
  padding-top: 6px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.action-button-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.btn-send {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  height: 44px;
  padding: 0 20px;
  border-radius: 12px;
  border: 1px solid rgba(175, 188, 255, 0.85);
  background: rgba(202, 211, 255, 0.6);
  color: #1b2650;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.btn-send:hover {
  background: rgba(184, 198, 255, 0.72);
  box-shadow: 0 16px 34px rgba(160, 176, 255, 0.28);
}

.btn-send:active {
  transform: translateY(1px);
}

.btn-send-icon {
  width: 18px;
  height: 18px;
  stroke-width: 1.8;
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
  border-color: rgba(111, 134, 255, 0.85);
  background: rgba(225, 232, 255, 0.9);
  box-shadow: 0 22px 60px rgba(111, 134, 255, 0.22);
  transform: translateY(-1px);
}

.dropzone-icon {
  width: 48px;
  height: 48px;
  color: var(--primary-strong);
  margin: 0 auto 12px;
}

.dropzone-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 6px;
}

.dropzone-title span {
  color: var(--primary-strong);
}

.dropzone-formats {
  font-size: 12px;
  color: #7280a7;
}

.upload-info {
  border-radius: 14px;
  border: 1px solid rgba(111, 134, 255, 0.35);
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
  box-shadow: 0 20px 48px rgba(111, 134, 255, 0.16);
  transition: border-color 0.22s ease, box-shadow 0.22s ease, transform 0.22s ease;
  animation: cardRise 0.45s ease 0.08s both;
}

.template-card:hover {
  border-color: rgba(173, 186, 255, 0.9);
  box-shadow: 0 26px 64px rgba(111, 134, 255, 0.22);
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
  background: rgba(127, 152, 255, 0.22);
  color: #4356d2;
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
  background: var(--primary-strong);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}

.template-apply:hover {
  background: #4357ea;
  box-shadow: 0 14px 36px rgba(79, 110, 245, 0.26);
}

.template-apply:active {
  transform: translateY(1px);
}

.template-apply:focus-visible {
  outline: 2px solid rgba(79, 110, 245, 0.4);
  outline-offset: 2px;
}

.preview-container {
  background: #fff;
  border: 1px solid rgba(208, 216, 255, 0.85);
  border-radius: 20px;
  box-shadow: 0 24px 64px rgba(111, 134, 255, 0.2);
  overflow: hidden;
  animation: cardRise 0.5s ease 0.05s both;
}

.preview-toolbar {
  position: sticky;
  top: 0;
  z-index: 5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 18px 22px;
  border-bottom: 1px solid rgba(210, 218, 255, 0.8);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(6px);
}

.feedback-status {
  display: none;
  margin: 12px 22px 0;
  padding: 10px 14px;
  border-radius: 12px;
  border: 1px solid rgba(208, 216, 255, 0.85);
  background: rgba(234, 238, 255, 0.72);
  font-size: 13px;
  color: #21305c;
  box-shadow: 0 12px 26px rgba(155, 169, 255, 0.18);
}

.feedback-status.visible { display: block; }

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
}

.btn-generate {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  height: 44px;
  padding: 0 20px;
  border-radius: 12px;
  border: none;
  background: var(--primary-strong);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.25s ease, transform 0.2s ease, box-shadow 0.25s ease;
}

.btn-generate:hover {
  background: #4357ea;
  box-shadow: 0 18px 46px rgba(79, 110, 245, 0.28);
}

.btn-generate:active {
  transform: translateY(1px);
}

.btn-generate:focus-visible {
  outline: 2px solid rgba(79, 110, 245, 0.4);
  outline-offset: 2px;
}

.btn-icon {
  width: 16px;
  height: 16px;
}

.action-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16px;
}

.feedback-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.utility-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.feedback-button {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  border: 1px solid rgba(198, 210, 255, 0.9);
  background: rgba(218, 227, 255, 0.55);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, background 0.2s ease;
}

.feedback-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 14px 28px rgba(155, 169, 255, 0.25);
}

.feedback-button:focus-visible {
  outline: 2px solid rgba(111, 134, 255, 0.4);
  outline-offset: 2px;
}

.feedback-button.feedback-accept {
  border-color: rgba(165, 223, 199, 0.9);
  background: rgba(207, 240, 225, 0.7);
  color: #16603c;
}

.feedback-button.feedback-accept:hover {
  border-color: rgba(143, 214, 186, 0.95);
  background: rgba(187, 232, 210, 0.85);
  box-shadow: 0 14px 30px rgba(121, 200, 166, 0.26);
}

.feedback-button.feedback-reject {
  border-color: rgba(255, 195, 195, 0.9);
  background: rgba(255, 226, 226, 0.7);
  color: #9f1f1f;
}

.feedback-button.feedback-reject:hover {
  border-color: rgba(255, 177, 177, 0.95);
  background: rgba(255, 208, 208, 0.85);
  box-shadow: 0 14px 30px rgba(255, 164, 164, 0.25);
}

.feedback-button.feedback-note {
  border-color: rgba(224, 207, 255, 0.9);
  background: rgba(237, 227, 255, 0.72);
  color: #5b3bbd;
}

.feedback-button.feedback-note:hover {
  border-color: rgba(206, 188, 255, 0.95);
  background: rgba(226, 214, 255, 0.85);
}

.feedback-button.feedback-retry {
  border-color: rgba(201, 214, 255, 0.9);
  background: rgba(219, 229, 255, 0.72);
  color: #2a4098;
}

.feedback-button.feedback-retry:hover {
  border-color: rgba(183, 200, 255, 0.95);
  background: rgba(207, 221, 255, 0.85);
}

.feedback-icon {
  width: 18px;
  height: 18px;
}

.btn-action {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 40px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid rgba(204, 212, 250, 0.9);
  background: #f8f9ff;
  font-size: 13px;
  font-weight: 500;
  color: #1e2a51;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.btn-action:hover {
  background: rgba(111, 134, 255, 0.18);
  border-color: rgba(173, 186, 255, 0.9);
  box-shadow: 0 12px 30px rgba(145, 163, 255, 0.25);
}

.btn-action:focus-visible {
  outline: 2px solid rgba(111, 134, 255, 0.4);
  outline-offset: 2px;
}

.preview-area {
  position: relative;
  min-height: 480px;
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
  background: rgba(111, 134, 255, 0.18);
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-icon-svg {
  width: 36px;
  height: 36px;
  color: var(--primary-strong);
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
  border: 4px solid rgba(111, 134, 255, 0.25);
  border-top-color: var(--primary-strong);
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
  padding: 24px;
  font-size: 15px;
  line-height: 1.7;
  color: #1f2937;
}

.preview-content.editing-active {
  outline: 2px solid rgba(111, 134, 255, 0.45);
  outline-offset: 6px;
  background: rgba(238, 241, 255, 0.45);
  border-radius: 12px;
}

.preview-content :deep(hr) {
  margin: 24px 0;
  border: 0;
  border-top: 1px solid #e5e8f0;
}

.preview-content :deep(ul),
.preview-content :deep(ol) {
  margin: 16px 0;
  padding-left: 20px;
}

.preview-content :deep(li) {
  margin-bottom: 8px;
}

.shortcut-bar {
  margin-top: 18px;
  text-align: center;
  font-size: 12px;
  color: #6e78a5;
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

.modal {
  position: fixed;
  inset: 0;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(17, 24, 39, 0.55);
  z-index: 50;
}

.modal.open {
  display: flex;
}

.modal-shell {
  width: min(880px, 100%);
  max-height: 85vh;
  background: #fff;
  border: 1px solid rgba(204, 212, 250, 0.9);
  border-radius: 20px;
  box-shadow: 0 28px 70px rgba(111, 134, 255, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: cardRise 0.4s ease both;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(210, 218, 255, 0.8);
}

.modal-title {
  font-size: 16px;
  font-weight: 600;
  color: #253060;
}

.modal-close {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: none;
  background: transparent;
  color: #475569;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s ease;
}

.modal-close:hover {
  background: rgba(230, 236, 255, 0.85);
}

.modal-close:focus-visible {
  outline: 2px solid rgba(45, 74, 160, 0.4);
  outline-offset: 2px;
}

.modal-body {
  padding: 20px;
  background: rgba(247, 249, 255, 0.65);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.modal-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

@media (min-width: 768px) {
  .modal-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

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
  .toolbar-actions {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  .btn-generate {
    width: 100%;
    justify-content: center;
  }
  .action-bar {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
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
  .btn-send {
    width: 100%;
    justify-content: center;
  }
  .documents-grid {
    gap: 20px;
  }
}

/* Override to match Overview page */
.sidebar-link.active {
  background-color: #eff6ff !important;
  color: #2563eb !important;
  box-shadow: none !important;
  transform: none !important;
}
</style>
