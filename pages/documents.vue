<template>
  <div>
    <!-- Header -->
    <header class="px-3 md:px-6 py-3 md:py-4 bg-white border-b border-gray-200">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="icon-box">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
          </div>
          <div>
            <h1 class="text-xl font-semibold text-gray-900">Rechtsdokument‑Assistent</h1>
            <p class="text-xs text-gray-500">Erstellen, prüfen und perfektionieren – mit konsistenten Kanzlei‑Bausteinen.</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <a href="/dashboard" class="btn-secondary text-sm" title="Zurück zum Dashboard">Zurück</a>
          <button id="btnHelp" class="toolbar-btn text-[color:var(--primary)]">Hilfe</button>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto p-3 md:p-4">
      <!-- Stepper -->
      <div class="mb-3 grid grid-cols-1 md:grid-cols-3 gap-2 md:gap-3">
        <div class="card flex items-center gap-3 py-2">
          <div class="icon-box">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115 7h1a3 3 0 010 6h-1"/></svg>
          </div>
          <div>
            <div class="text-sm font-medium">1. Dokument hochladen</div>
            <div class="text-xs text-gray-500">Optional</div>
          </div>
        </div>
        <div class="card flex items-center gap-3 py-2">
          <div class="icon-box">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 20l9-5-9-5-9 5 9 5z"/></svg>
          </div>
          <div>
            <div class="text-sm font-medium">2. Angaben & Vorgaben</div>
            <div class="text-xs text-gray-500">Pflichtfelder</div>
          </div>
        </div>
        <div class="card flex items-center gap-3 py-2">
          <div class="icon-box">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4"/></svg>
          </div>
          <div>
            <div class="text-sm font-medium">3. Vorschau & Feinschliff</div>
            <div class="text-xs text-gray-500">Export bereit</div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 xl:grid-cols-5 gap-3 md:gap-4">
        <!-- Left -->
        <section class="xl:col-span-3 space-y-3">
          <!-- Upload -->
          <div class="card" aria-label="Dokument hochladen">
            <div class="card-header">
              <div class="flex items-center gap-2">
                <div class="icon-box" aria-hidden="true"><svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1M12 12V4m0 0L8 8m4-4l4 4"/></svg></div>
                <h2 class="card-title">Dokument hochladen <span class="text-gray-400 text-sm">(optional)</span></h2>
              </div>
              <button class="btn-text text-sm" id="btnClearUpload">Zurücksetzen</button>
            </div>
            <div id="dropzone" class="dropzone">
              <div>
                <div class="mx-auto icon-box mb-2" aria-hidden="true"><svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg></div>
                <p class="text-sm text-gray-700"><span class="text-[color:var(--primary)]">Datei hier ablegen</span> oder klicken</p>
                <p class="text-xs text-gray-500">PDF, DOC, DOCX, TXT</p>
              </div>
              <input id="fileInput" type="file" class="hidden" accept=".pdf,.doc,.docx,.txt" />
            </div>
            <div id="uploadInfo" class="hidden mt-3 text-sm text-gray-600"></div>
          </div>

          <!-- AI Instructions -->
          <div class="card" aria-label="KI‑Anweisungen">
            <div class="card-header">
              <div class="flex items-center gap-2">
                <div class="icon-box" aria-hidden="true"><svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 20l9-5-9-5-9 5 9 5z"/></svg></div>
                <h2 class="card-title">KI‑Anweisungen</h2>
              </div>
              <div class="flex items-center gap-3 text-xs text-gray-500">
                <label class="flex items-center gap-2">
                  <span>Juristische Sprache</span>
                  <span class="switch"><input id="switchLegalTone" type="checkbox" checked><span class="dot"></span></span>
                </label>
                <label class="flex items-center gap-2">
                  <span>Leichte Sprache</span>
                  <span class="switch"><input id="switchPlain" type="checkbox"><span class="dot"></span></span>
                </label>
              </div>
            </div>

            <label class="text-xs text-gray-500">Dokumenttyp</label>
            <input id="docType" class="input-field mt-1" placeholder="z. B. Mietvertrag, Abmahnung, Vergleich, NDA…" />

            <div class="mt-4">
              <div class="flex items-center justify-between">
                <label class="text-xs text-gray-500">Sachverhalt & Anforderungen</label>
                <button id="btnInsertChecklist" class="btn-text text-xs">Beispiel‑Checkliste einfügen</button>
              </div>
              <textarea id="requirements" class="input-field mt-1" rows="6" placeholder="Beschreiben Sie kurz den Fall. Nennen Sie Parteien, Ziele und besondere Bedingungen."></textarea>
              <p class="text-xs text-gray-400 mt-1" id="charCount">0 Zeichen</p>
            </div>

            <div class="mt-4">
              <label class="text-xs text-gray-500">Optionale Bausteine</label>
              <div class="mt-2 flex flex-wrap gap-2">
                <button class="chip" data-clause="Gerichtsstand">Gerichtsstand</button>
                <button class="chip" data-clause="Vertragsstrafe">Vertragsstrafe</button>
                <button class="chip" data-clause="Vertraulichkeit">Vertraulichkeit</button>
                <button class="chip" data-clause="Kündigung">Kündigung</button>
                <button class="chip" data-clause="Verjährung">Verjährung</button>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="card">
            <div class="flex items-center justify-between">
              <div class="text-sm text-gray-600">Bereit, wenn Sie es sind. Sie können jederzeit neu generieren.</div>
              <div class="flex items-center gap-3">
                <button id="btnTemplates" class="btn-secondary text-sm">Vorlagen</button>
                <button id="btnClear" class="btn-secondary text-sm">Alle löschen</button>
                <button id="btnGenerate" class="btn-primary text-sm">Dokument erstellen ⏎</button>
              </div>
            </div>
          </div>
        </section>

        <!-- Right -->
        <section class="xl:col-span-2">
          <div id="previewContainer" class="card" style="min-height: 480px;">
            <div class="card-header">
              <div class="flex items-center gap-2">
                <div class="icon-box" aria-hidden="true"><svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 01-2 2z"/></svg></div>
                <h2 class="card-title">Dokument‑Vorschau</h2>
              </div>
              <div id="actionBar" class="flex items-center gap-2 text-sm flex-wrap hidden" style="display:none">
                <span id="wordCount" class="text-gray-500 mr-2">0 Wörter</span>
                <button class="toolbar-btn" id="btnCopy" title="In Zwischenablage kopieren">
                  <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2M8 16h8a2 2 0 002-2v-2m-6 6H8a2 2 0 01-2-2v-2m10-6h2"/></svg>
                  Kopieren
                </button>
                <button class="toolbar-btn" id="btnEdit" title="Bearbeiten umschalten">
                  <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5h2m2 0h2m-8 0H7m0 0H5m2 0v2m0 2v2m0 2v2m0 2v2m2-2h2m2 0h2m2 0h2"/></svg>
                  Bearbeiten
                </button>
                <button class="toolbar-btn" id="btnSave" title="Speichern">
                  <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7"/></svg>
                  Speichern
                </button>
                <button class="toolbar-btn" id="btnApprove" title="Freigeben">
                  <svg class="w-4 h-4 inline mr-1 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                  Freigeben
                </button>
                <button class="toolbar-btn" id="btnReject" title="Ablehnen">
                  <svg class="w-4 h-4 inline mr-1 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                  Ablehnen
                </button>
                <button class="toolbar-btn" id="btnAccept" title="Annehmen">
                  <svg class="w-4 h-4 inline mr-1 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4"/></svg>
                  Annehmen
                </button>
                <button class="toolbar-btn" id="btnExport" title="Als DOCX exportieren">
                  <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v12m0 0l-4-4m4 4l4-4M4 20h16"/></svg>
                  DOCX
                </button>
                <button class="toolbar-btn" id="btnExportPdf" title="Als PDF exportieren">
                  <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0l-4-4m4 4l-4 4"/></svg>
                  PDF
                </button>
              </div>
            </div>

            <div id="previewArea" class="relative min-h-[360px]">
              <div id="previewEmpty" class="absolute inset-0 flex items-center justify-center text-center text-gray-500">
                <div>
                  <div class="mx-auto icon-box mb-3"><svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg></div>
                  <div class="font-medium text-gray-700">Noch kein Dokument erstellt</div>
                  <div class="text-xs">Laden Sie ein Dokument hoch oder geben Sie Anweisungen ein, um zu starten.</div>
                </div>
              </div>

              <div id="previewSkeleton" class="hidden space-y-3 p-4">
                <div class="skeleton h-6"></div>
                <div class="skeleton h-6 w-11/12"></div>
                <div class="skeleton h-6 w-10/12"></div>
                <div class="skeleton h-6 w-9/12"></div>
                <div class="skeleton h-6 w-8/12"></div>
              </div>

              <div id="genOverlay" class="hidden absolute inset-0 bg-white/80 backdrop-blur-[1px] flex flex-col items-center justify-center rounded">
                <div class="w-16 h-16 rounded-full border-4 border-blue-200 border-t-[color:var(--primary)] animate-spin mb-3"></div>
                <div class="text-sm text-gray-700">Anwalts AI in Aktion …</div>
              </div>

              <article id="preview" class="prose max-w-none hidden p-4"></article>
            </div>
          </div>

          <div class="mt-3 text-xs text-gray-500">Tastatur: <kbd>Strg</kbd> + <kbd>Enter</kbd> generiert neu · <kbd>Alt</kbd> + <kbd>C</kbd> kopiert.</div>
        </section>
      </div>
    </main>
    <!-- Templates Modal (keeps original look) -->
    <div id="tplModal" class="modal">
      <div class="card w-[820px] max-h-[80vh] overflow-auto">
        <div class="card-header">
          <h3 class="card-title">Vorlagen auswählen</h3>
          <button class="toolbar-btn" id="tplClose">Schließen</button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="md:col-span-2">
            <input id="tplSearch" class="input-field" placeholder="Vorlagen durchsuchen… (z. B. NDA, Klage, Abmahnung)"/>
            <div id="tplGrid" class="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3"></div>
          </div>
          <aside class="hidden md:block text-sm text-gray-600">
            <div class="text-xs text-gray-500">Tipps</div>
            <ul class="mt-2 list-disc pl-5">
              <li>Mit <em>Übernehmen</em> landet die Vorlage direkt in der Vorschau.</li>
              <li>Platzhalter wie [PARTEI A] später ersetzen.</li>
              <li>Ihre letzte Auswahl wird gespeichert.</li>
            </ul>
          </aside>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useTour } from '#imports'
import { onMounted } from 'vue'
import { useHead, useRuntimeConfig } from '#imports'

definePageMeta({ layout: false })

onMounted(() => {
  const $ = (s, r=document) => r.querySelector(s)
  const $$ = (s, r=document) => Array.from(r.querySelectorAll(s))
  const { public: { apiBase = '', apiEndpoints = {} } } = useRuntimeConfig()
  // Tour will be initialized later in the main setup
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
      card.className = 'p-4 rounded-lg bg-gray-50 border border-gray-200 flex flex-col'
      card.innerHTML = `
        <div class="flex items-start justify-between gap-3">
          <div>
            <div class="font-medium text-gray-900">${t.title}</div>
            <div class="text-xs text-gray-500">${t.prompt}</div>
          </div>
          <span class="inline-block px-2 py-1 rounded-full text-xs bg-[rgba(91,124,230,0.12)] text-[color:var(--primary)]">${t.category}</span>
        </div>
        <div class="mt-3 flex items-center gap-2">
          <button class="btn-primary px-3 py-2 rounded-md text-sm" data-apply="${t.id}">Übernehmen</button>
          <button class="btn-secondary px-3 py-2 rounded-md text-sm" data-preview="${t.id}">Vorschau</button>
        </div>`
      grid.appendChild(card)
    })

    grid.querySelectorAll('[data-apply]').forEach(btn => btn.addEventListener('click', (e)=>{
      const id = e.currentTarget.getAttribute('data-apply')
      const tpl = TEMPLATE_STORE.find(x=>x.id===id)
      applyTemplate(tpl)
      try{ localStorage.setItem('anwalt.templateId', id) }catch(_){ }
      document.getElementById('tplModal')?.classList.remove('open')
    }))

    grid.querySelectorAll('[data-preview]').forEach(btn => btn.addEventListener('click', (e)=>{
      const id = e.currentTarget.getAttribute('data-preview')
      const tpl = TEMPLATE_STORE.find(x=>x.id===id)
      quickPreview(tpl)
    }))
  }

  function quickPreview(){ /* disabled: templates should not render into preview */ }

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
    // Do not preview template content automatically; only AI results should render
    const actionBar = document.getElementById('actionBar'); actionBar?.classList.add('hidden')
  }

  function loadLastTemplate(){
    try{ localStorage.removeItem('anwalt.templateId') }catch(_){ }
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
    uploadInfo.textContent = 'Lade hoch … ' + file.name
    uploadInfo.classList.remove('hidden')
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await fetch(proxyUploadUrl, { method: 'POST', body: form, credentials: 'include' })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      const label = data?.filename || data?.name || file.name
      uploadInfo.textContent = `Hochgeladen: ${label}`
      window.__lastUploadId = data?.id || data?.fileId || data?.file_id
    } catch (e) {
      uploadInfo.textContent = `Upload fehlgeschlagen: ${String(e)}`
    }
  }

  // Character counter & helpers
  const req = document.getElementById('requirements')
  const charCount = document.getElementById('charCount')
  req?.addEventListener('input', ()=>{ if (charCount) charCount.textContent = req.value.length + ' Zeichen' })

  document.getElementById('btnInsertChecklist')?.addEventListener('click', ()=>{
    const sample = '• Beteiligte Parteien (Namen, Adressen)\n• Wesentliche Bedingungen (z. B. Preis, Laufzeit)\n• Besondere Anforderungen (z. B. Geheimhaltung, Vertragsstrafe)\n• Fristen/Termine (konkretes Datum oder Zeitraum)'
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

  // Help tour via shared composable (documents)
  const docsTour = useTour({ storageKey: 'docsTourDismissed' })
  docsTour.setSteps([
    { sel: '#docType', text: '<b>Dokumenttyp</b><br/>Wählen oder benennen Sie den gewünschten Dokumenttyp.' },
    { sel: '#requirements', text: '<b>Sachverhalt & Anforderungen</b><br/>Beschreiben Sie kurz den Fall und Vorgaben.' },
    { sel: '#btnGenerate', text: '<b>Generieren</b><br/>Erstellt einen ersten Entwurf basierend auf Ihren Angaben.' },
    { sel: '#previewContainer', text: '<b>Ergebnisbereich</b><br/>Hier erscheint das generierte Dokument mit Vorschau, Aktionen und Export.' }
  ])
  docsTour.attachDefaultHandlers()
  // Help button click handler - single clean implementation
  document.getElementById('btnHelp')?.addEventListener('click', (e) => {
    e.preventDefault()
    docsTour.startTour()
  })

  // Auto-start disabled, use Help button

  // Try load templates from backend
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
  const previewSkeleton = document.getElementById('previewSkeleton')
  const wordCount = document.getElementById('wordCount')

  async function generate(){
    // Render generation state inside the preview area only
    previewEmpty?.classList.add('hidden')
    preview?.classList.add('hidden')
    const overlay = document.getElementById('genOverlay')
    overlay?.classList.remove('hidden')
    const actionBar = document.getElementById('actionBar')
    actionBar?.classList.add('hidden')
    let contentSet = false

    const type = document.getElementById('docType')?.value || (SELECTED_TEMPLATE?.docType || 'Rechtsdokument')
    const instr = req?.value.trim() || ''
    const toneLegal = document.getElementById('switchLegalTone')?.checked
    const plain = document.getElementById('switchPlain')?.checked

    try {
      // Try generate endpoint fallbacks via SSR proxy (converts cookies to Authorization)
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
                // Strict schema for /api/ai/generate-document
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
        const header = `<h2 style=\"margin:0\">${type}</h2><hr/><p><em>${styleNote}</em></p>`
        const withInstr = instr ? `<h3>Vorgaben</h3><p>${instr.replace(/\n/g,'<br/>')}</p>` : ''
        setPreview(header + bodyHtml + withInstr)
        contentSet = true
        actionBar?.classList.remove('hidden'); if (actionBar) actionBar.style.display = 'flex'
      }
    } catch (e) {
      console.error('Generate failed:', e)
      if (saw403) alert('Nicht autorisiert (403). Bitte erneut anmelden oder Token prüfen.')
    } finally {
      if (contentSet) {
        preview?.classList.remove('hidden'); if (preview) preview.style.display = ''
        previewEmpty?.classList.add('hidden')
      } else {
        preview?.classList.add('hidden'); if (preview) preview.style.display = 'none'
        previewEmpty?.classList.remove('hidden')
        actionBar?.classList.add('hidden'); if (actionBar) actionBar.style.display = 'none'
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

  // Copy / Export (demo)
  const copyBtn = document.getElementById('btnCopy')
  if (copyBtn) copyBtn.addEventListener('click', async ()=>{
    if (!preview) return
    const tmp = document.createElement('div'); tmp.innerHTML = preview.innerHTML; const text = tmp.innerText; await navigator.clipboard.writeText(text); alert('In Zwischenablage kopiert')
  })
  const exportBtn = document.getElementById('btnExport')
  if (exportBtn) exportBtn.addEventListener('click', async ()=>{
    if (!preview) return alert('Nichts zu exportieren')
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
      if (id) {
        const exportBase = apiEndpoints.exportBase || (apiBase ? `${apiBase}/documents` : '')
        const url = `${exportBase}/${id}/export?format=docx`
        const resp = await proxyGet(url)
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        const blob = await resp.blob()
        const a = document.createElement('a')
        a.href = URL.createObjectURL(blob)
        a.download = (document.getElementById('docType')?.value || 'Dokument') + '.docx'
        document.body.appendChild(a); a.click(); a.remove()
      } else {
        alert('Gespeichert, aber keine ID erhalten.')
      }
    } catch (e) {
      alert('Export fehlgeschlagen: ' + String(e))
    }
  })

  // PDF export button
  const exportPdfBtn = document.getElementById('btnExportPdf')
  if (exportPdfBtn) exportPdfBtn.addEventListener('click', async ()=>{
    if (!preview) return alert('Nichts zu exportieren')
    try {
      if (!ep.save) throw new Error('Save endpoint not configured')
      const savePath = (apiEndpoints.save || (apiBase ? `${apiBase}/documents/save` : ''))
      const res = await proxyPost(savePath, { title: document.getElementById('docType')?.value || 'Rechtsdokument', html: preview.innerHTML })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const saved = await res.json(); const id = saved?.id || saved?.documentId
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
      }
    } catch (e) { alert('Export fehlgeschlagen: ' + String(e)) }
  })

  // Edit/Save/Approve/Reject/Accept actions
  const editBtn = document.getElementById('btnEdit')
  const saveBtn = document.getElementById('btnSave')
  const approveBtn = document.getElementById('btnApprove')
  const rejectBtn = document.getElementById('btnReject')
  const acceptBtn = document.getElementById('btnAccept')

  if (editBtn) editBtn.addEventListener('click', ()=>{
    if (!preview) return
    const editable = preview.getAttribute('contenteditable') === 'true'
    preview.setAttribute('contenteditable', editable ? 'false' : 'true')
    preview.classList.toggle('ring-2')
    preview.classList.toggle('ring-blue-400')
  })

  if (saveBtn) saveBtn.addEventListener('click', async ()=>{
    if (!preview) return
    try {
      if (!ep.save) throw new Error('Save endpoint not configured')
      const res = await fetch(ep.save, {
        method: 'POST', headers: { 'Content-Type': 'application/json', ...getAuthHeader() }, credentials: 'include',
        body: JSON.stringify({ title: document.getElementById('docType')?.value || 'Rechtsdokument', html: preview.innerHTML })
      })
      if (!res.ok) throw new Error('HTTP ' + res.status)
      const saved = await res.json(); window.__lastDocId = saved?.id || saved?.documentId; alert('Gespeichert')
    } catch (e) { alert('Speichern fehlgeschlagen: ' + String(e)) }
  })

  async function setStatus(status){
    try {
      if (!((apiEndpoints.status || (apiBase ? `${apiBase}/documents/status` : '')) || (apiEndpoints.exportBase || (apiBase ? `${apiBase}/documents` : '')))) throw new Error('Status endpoint not configured')
      const did = (window).__lastDocId
      let url = (apiEndpoints.status || (apiBase ? `${apiBase}/documents/status` : ''))
      if (!url && did) {
        const exportBase = apiEndpoints.exportBase || (apiBase ? `${apiBase}/documents` : '')
        if (exportBase) url = `${exportBase}/${did}/status`
      }
      const res = await proxyPost(url, { status, doc_id: did || null })
      if (!res.ok) throw new Error('HTTP ' + res.status)
      alert('Status: ' + status)
    } catch (e) { alert('Status Änderung fehlgeschlagen: ' + String(e)) }
  }
  if (approveBtn) approveBtn.addEventListener('click', ()=> setStatus('approved'))
  if (rejectBtn) rejectBtn.addEventListener('click', ()=> setStatus('rejected'))
  if (acceptBtn) acceptBtn.addEventListener('click', ()=> setStatus('accepted'))

  // Clear
  const clearBtn = document.getElementById('btnClear')
  if (clearBtn) clearBtn.addEventListener('click', ()=>{
    const docType = document.getElementById('docType'); if (docType) docType.value=''
    if (req) { req.value=''; req.dispatchEvent(new Event('input')) }
    setPreview(''); preview?.classList.add('hidden'); previewEmpty?.classList.remove('hidden')
    SELECTED_TEMPLATE=null; try{ localStorage.removeItem('anwalt.templateId') }catch(_){ }
    const actionBar = document.getElementById('actionBar'); actionBar?.classList.add('hidden')
  })

  // Boot: render template cards, but do NOT auto-load any previous template
  renderTemplates(TEMPLATE_STORE)

  // Enforce clean initial state: no preview or action bar until AI generates
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

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --primary: #5b7ce6;
  --primary-hover: #4a6cd4;
  --icon-bg: rgba(91,124,230,0.12);
  --bg: #f8f9fa;
  --text: #2c3e50;
  --muted: #e8ecf3;
  --muted-hover: #d8dfe9;
}

body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }

.card { background: #fff; border-radius: 12px; padding: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.06); }
.card-header { display:flex; align-items:center; justify-content:space-between; margin-bottom: 12px; }
.card-title { font-weight: 600; color:#0f172a; }

.btn-primary { background: var(--primary); color:#fff; padding:10px 16px; border-radius: 10px; font-weight:500; }
.btn-primary:hover { background: var(--primary-hover); }
.btn-secondary { background: var(--muted); color: var(--text); padding:10px 16px; border-radius: 10px; font-weight:500; }
.btn-secondary:hover { background: var(--muted-hover); }
.btn-text { color: var(--primary); }

.input-field { width: 100%; padding: 12px 14px; border: 1px solid #e0e6ed; border-radius: 10px; background: #fff; transition: border-color 0.2s; font-size:14px; }
.input-field:focus { outline:none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(91,124,230,0.15); }

.icon { border: 0; }
.icon-box { background: var(--icon-bg); color: var(--primary); border-radius: 10px; width: 36px; height: 36px; display:flex; align-items:center; justify-content:center; }

.dropzone { border: 1.5px dashed #cbd5e1; border-radius: 12px; background: #f8fafc; min-height: 120px; display:flex; align-items:center; justify-content:center; text-align:center; }
.dropzone.dragover { border-color: var(--primary); background: #f1f5ff; }

.skeleton { position: relative; overflow: hidden; background: #eef1f6; border-radius: 8px; }
.skeleton::after { content:""; position: absolute; inset: 0; transform: translateX(-100%); background: linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent); animation: shimmer 1.2s infinite; }
@keyframes shimmer { 100% { transform: translateX(100%); } }

.toolbar-btn { display:inline-flex; align-items:center; gap:6px; padding:8px 12px; border:1px solid #e5e7eb; border-radius:8px; color:#374151; background:#fff; transition: all .15s ease-in-out; }
.toolbar-btn:hover { background:#f9fafb; border-color:#d1d5db }
.toolbar-btn:active { transform: translateY(0.5px) }
.toolbar-btn:focus-visible { outline: 2px solid rgba(59,130,246,0.5); outline-offset: 2px }

.chip { border: 1px solid #e0e6ed; background: white; padding: 6px 10px; border-radius: 9999px; font-size: 12px; }

.switch { position: relative; width: 40px; height: 22px; background: #e5e7eb; border-radius: 9999px; transition: background .2s; }
.switch input { display:none; }
.switch .dot { position: absolute; top: 2px; left: 2px; width: 18px; height: 18px; background: #fff; border-radius: 50%; transition: transform .2s; box-shadow: 0 1px 2px rgba(0,0,0,0.2); }
.switch input:checked + .dot { transform: translateX(18px); }

.modal { position: fixed; inset: 0; display:none; align-items:center; justify-content:center; background: rgba(17,24,39,0.55); z-index: 50; }
.modal:not(.open) { pointer-events: none; }
.modal.open { display:flex; }

/* Spinner */
.spinner {
  width: 18px; height: 18px; border-radius: 9999px; border: 2px solid #cbd5e1; border-top-color: var(--primary); animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Tour (match dashboard behavior) */
.tour-overlay { position: fixed; inset: 0; background: rgba(17,24,39,0.55); z-index: 9998; display: none; pointer-events: none; }
.tour-step { position: absolute; background: #fff; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); padding: 16px; width: 320px; z-index: 9999; }
.tour-arrow { width: 0; height: 0; border-left: 8px solid transparent; border-right: 8px solid transparent; border-top: 8px solid #fff; position: absolute; top: -8px; left: 24px; }
.tour-focus { outline: 3px solid var(--primary); outline-offset: 2px; border-radius: 6px; transition: outline-color .2s; }
</style>

/* remove docs tour */
.tour-overlay{display:none!important}
.tour-step{display:none!important}
#btnHelp{display:none!important}
