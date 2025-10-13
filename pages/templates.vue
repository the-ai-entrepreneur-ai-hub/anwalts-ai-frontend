<template>
  <PortalShell>
    <main class="templates-body">
      <section class="templates-intro surface">
        <div class="templates-intro__top">
          <div class="templates-intro__copy">
            <span class="templates-eyebrow">Vorlagen</span>
            <h1 class="templates-title">Mandantenbibliothek</h1>
            <p class="templates-lead">
              Präzise kuratierte Muster für europäische Compliance, Mandantenkommunikation und wiederkehrende Vorgänge.
            </p>
          </div>
          <div class="templates-intro__actions">
            <button type="button" class="btn ghost" @click="handleFilter">
              <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              Filtern
            </button>
            <button type="button" class="btn outline" @click="handleImport">
              <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
              </svg>
              Importieren
            </button>
            <button type="button" class="btn primary" @click="createTemplate">
              <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v12m6-6H6" />
              </svg>
              Neue Vorlage
            </button>
          </div>
        </div>
        <div class="templates-intro__bottom">
          <label class="intro-search" for="templateSearch">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M18 10.5a7.5 7.5 0 11-15 0 7.5 7.5 0 0115 0z" />
            </svg>
            <input
              id="templateSearch"
              v-model="searchQuery"
              class="search-input"
              type="search"
              placeholder="Vorlagen, Typen oder Klauseln schnell finden"
            />
          </label>
          <dl class="intro-metrics">
            <div class="intro-metric">
              <dt>Aktive Vorlagen</dt>
              <dd>{{ templates.length || '–' }}</dd>
            </div>
            <div class="intro-metric">
              <dt>Letzte Pflege</dt>
              <dd>{{ lastUpdatedLabel }}</dd>
            </div>
          </dl>
          <div class="intro-user" aria-label="Angemeldeter Benutzer">
            <span class="intro-avatar">{{ portalUserInitials }}</span>
            <span class="intro-username">{{ portalUserName }}</span>
          </div>
        </div>
      </section>

      <div class="templates-layout">
        <aside class="templates-rail" aria-label="Mandanten-Highlights">
          <section class="surface section-block highlight-section">
            <header class="section-heading">
              <h2 class="section-title">Mandantenqualität</h2>
              <p class="section-sub">Schnelle Einschätzung des Template-Streams</p>
            </header>
            <ul class="stat-list">
              <li
                v-for="stat in highlightCards"
                :key="stat.id"
                class="stat-item"
              >
                <span class="stat-icon">
                  <svg v-if="stat.icon === 'shield'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 4l8 4v5c0 5-3.582 9-8 9s-8-4-8-9V8l8-4z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M10 13l2 2 4-4" />
                  </svg>
                  <svg v-else-if="stat.icon === 'clock'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="12" cy="12" r="9" stroke-width="1.8" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 7v5l3 3" />
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M8 9h8M8 13h5" />
                  </svg>
                </span>
                <div>
                  <p class="stat-title">{{ stat.title }}</p>
                  <p class="stat-note">{{ stat.note }}</p>
                </div>
              </li>
            </ul>
          </section>

          <section class="surface section-block clause-section">
            <header class="section-heading section-heading--row">
              <div>
                <h2 class="section-title">Klauselbibliothek</h2>
                <p class="section-sub">Direkt in Entwürfe übernehmen</p>
              </div>
              <button type="button" class="btn text" @click="openClauseLibrary">
                Alle anzeigen
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="chevron">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </header>
            <div class="clause-list">
              <button
                v-for="clause in clauses"
                :key="clause.id"
                type="button"
                class="clause-pill"
                @click="copyClause(clause)"
              >
                <div class="clause-pill__text">
                  <span class="clause-title">{{ clause.name }}</span>
                  <span class="clause-desc">{{ clause.desc }}</span>
                </div>
                <span class="clause-pill__icon" :class="{ 'is-locked': clause.locked }">
                  <svg
                    v-if="clause.locked"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M7 11V8a5 5 0 1110 0v3" />
                    <rect x="5" y="11" width="14" height="10" rx="2" ry="2" stroke-width="1.8" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 15v2" />
                  </svg>
                  <svg
                    v-else
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 5l7 7-7 7" />
                  </svg>
                </span>
              </button>
            </div>
          </section>
        </aside>

        <section class="templates-main">
          <article class="surface section-block templates-panel">
            <header class="panel-heading">
              <div>
                <h2 class="panel-title">Vorlageninventar</h2>
                <p class="panel-subtitle">Mandantenfertige Dokumente für wiederkehrende Situationen.</p>
              </div>
              <button type="button" class="btn primary" @click="createTemplate">
                <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v12m6-6H6" />
                </svg>
                Neue Vorlage
              </button>
            </header>

            <div v-if="isLoading" class="templates-skeleton">
              <div v-for="i in 8" :key="`skeleton-${i}`" class="skeleton-card">
                <span class="skeleton-line short"></span>
                <span class="skeleton-line"></span>
                <div class="skeleton-tags">
                  <span></span>
                  <span></span>
                </div>
                <span class="skeleton-button"></span>
              </div>
            </div>

            <div v-else-if="filteredTemplates.length === 0" class="templates-empty">
              <div class="empty-icon">
                <svg class="empty-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.915a1 1 0 00.951-.69z" />
                </svg>
              </div>
              <h3 class="empty-title">Noch keine Vorlagen</h3>
              <p class="empty-text">Importieren oder erstellen Sie eine Vorlage, um Ihren Mandantenstartpunkt aufzubauen.</p>
              <div class="empty-actions">
                <button type="button" class="btn primary" @click="handleImport">
                  <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                  </svg>
                  Importieren
                </button>
                <button type="button" class="btn ghost" @click="createTemplate">
                  <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v12m6-6H6" />
                  </svg>
                  Erstellen
                </button>
              </div>
            </div>

            <div v-else class="templates-grid">
              <article
                v-for="template in filteredTemplates"
                :key="template.id"
                class="template-card"
              >
                <header class="template-card__header">
                  <h3 class="template-title">{{ template.name }}</h3>
                  <button type="button" class="template-chip" @click="useTemplate(template)">
                    Verwenden
                  </button>
                </header>
                <p class="template-description">
                  {{ template.description || template.summary || template.content }}
                </p>
                <div class="template-meta">
                  <div class="meta-block">
                    <svg class="meta-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    <span>{{ template.createdBy || 'Ihr Team' }}</span>
                  </div>
                  <div class="meta-block">
                    <svg class="meta-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>{{ formatDate(template.updatedAt) }}</span>
                  </div>
                </div>
                <div class="template-tags">
                  <span
                    v-for="tag in getTemplateTags(template)"
                    :key="tag"
                    class="tag-chip"
                  >
                    {{ tag }}
                  </span>
                </div>
                <footer class="template-footer">
                  <div class="template-actions">
                    <button type="button" class="icon-button" @click="editTemplate(template)" :title="`${template.name} bearbeiten`">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button type="button" class="icon-button" @click="duplicateTemplate(template)" :title="`${template.name} duplizieren`">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </button>
                    <button type="button" class="icon-button danger" @click="deleteTemplate(template)" :title="`${template.name} löschen`">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </footer>
              </article>
            </div>
          </article>
        </section>

        <aside class="templates-aside" aria-label="Empfehlungen & Kennzahlen">
          <section class="surface section-block recommendations">
            <header class="section-heading">
              <h2 class="section-title">Empfehlungen</h2>
              <p class="section-sub">Auf Basis Ihrer letzten Mandate</p>
            </header>
            <div class="recommend-list">
              <article
                v-for="suggestion in suggestedTemplates"
                :key="suggestion.id"
                class="recommend-card"
              >
                <div class="recommend-card__body">
                  <h3 class="recommend-title">{{ suggestion.name }}</h3>
                  <p class="recommend-note">{{ suggestion.note }}</p>
                  <div class="recommend-progress">
                    <div class="progress-track">
                      <span class="progress-fill" :style="{ width: suggestion.match + '%' }"></span>
                    </div>
                    <span class="recommend-score">{{ suggestion.match }}%</span>
                  </div>
                </div>
                <button type="button" class="btn ghost" @click="handleSuggestion(suggestion)">
                  Verwenden
                </button>
              </article>
            </div>
          </section>

          <section class="surface section-block metrics">
            <header class="section-heading">
              <h2 class="section-title">Kennzahlen</h2>
              <p class="section-sub">Beliebte Themen aus den letzten Wochen</p>
            </header>
            <div class="metric-list">
              <div v-for="item in mostUsed" :key="item.label" class="metric-pill">
                <span class="metric-label">{{ item.label }}</span>
                <span class="metric-value">{{ item.count }}</span>
              </div>
            </div>
          </section>
        </aside>
      </div>
    </main>

    <transition-group
      v-if="toasts.length > 0"
      name="toast"
      tag="div"
      class="toast-stack"
    >
      <div v-for="toast in toasts" :key="toast.id" class="toast-item">
        <div>
          <div class="toast-title">{{ toast.title }}</div>
          <div v-if="toast.description" class="toast-message">{{ toast.description }}</div>
        </div>
        <button
          type="button"
          class="icon-button ghost"
          @click="dismissToast(toast.id)"
          aria-label="Benachrichtigung schließen"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </transition-group>

    <div
      v-if="showCreateModal"
      class="modal-backdrop"
      @click.self="showCreateModal = false"
    >
      <div class="modal-shell">
        <header class="modal-header">
          <h2 class="modal-title">Neue Vorlage erstellen</h2>
          <button
            type="button"
            class="icon-button ghost"
            @click="showCreateModal = false"
            aria-label="Schließen"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </header>
        <form @submit.prevent="handleCreateTemplate" class="modal-body">
          <label class="field-group">
            <span class="field-label">Vorlagenname</span>
            <input
              v-model="templateForm.name"
              type="text"
              required
              class="field-input"
              placeholder="Vorlagenname eingeben"
            />
          </label>
          <label class="field-group">
            <span class="field-label">Kategorie</span>
            <input
              v-model="templateForm.category"
              type="text"
              class="field-input"
              placeholder="Kategorie eingeben (optional)"
            />
          </label>
          <label class="field-group">
            <span class="field-label">Inhalt</span>
            <textarea
              v-model="templateForm.content"
              rows="10"
              required
              class="field-textarea"
              placeholder="Vorlageninhalt eingeben"
            ></textarea>
          </label>
          <div class="modal-actions">
            <button type="button" class="btn ghost" @click="showCreateModal = false">
              Abbrechen
            </button>
            <button type="submit" class="btn primary" :disabled="isCreating">
              {{ isCreating ? 'Wird erstellt…' : 'Vorlage erstellen' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </PortalShell>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import PortalShell from '~/components/PortalShell.vue'
import { usePortalUser } from '~/composables/usePortalUser'

definePageMeta({ layout: false })

const templates = ref<any[]>([])
const searchQuery = ref('')
const isLoading = ref(true)
const showCreateModal = ref(false)
const isCreating = ref(false)
const toasts = ref<any[]>([])

const templateForm = ref({
  name: '',
  category: '',
  content: ''
})

const highlightCards = [
  {
    id: 'mandanten',
    icon: 'shield',
    title: 'Mandanten-ready',
    note: 'Freigegebene Muster mit klarer Kommentierung & Optionsfeldern.'
  },
  {
    id: 'speed',
    icon: 'clock',
    title: 'Schnelle Durchlaufzeit',
    note: 'Ø Generierung: 22 Sekunden inklusive Qualitätscheck.'
  },
  {
    id: 'feedback',
    icon: 'chat',
    title: 'Mandantenfeedback 4,6/5',
    note: 'Transparente Feedback-Optionen für jede Dokumentversion.'
  }
]

const suggestedTemplates = ref([
  { id: 's1', name: 'Geheimhaltungsvereinbarung (Beidseitig)', note: 'Basierend auf Ihrer Aktivität', match: 92, source: 'System' },
  { id: 's2', name: 'Vertrag – Dienstleistung', note: 'Häufig angefordert', match: 88, source: 'System' },
  { id: 's3', name: 'Mahnung – Zahlungserinnerung', note: 'Ähnlich zu letztem Dokument', match: 85, source: 'Individuell' },
  { id: 's4', name: 'Datenverarbeitungsvereinbarung (DVV)', note: 'Basierend auf Ihrer Aktivität', match: 90, source: 'System' }
])

const mostUsed = ref([
  { label: 'Mahnung', count: 28 },
  { label: 'Vertrag', count: 22 },
  { label: 'NDA', count: 18 },
  { label: 'DPA', count: 11 }
])

const clauses = ref([
  { id: 'c1', name: 'Vertraulichkeit', desc: 'Definiert vertrauliche Informationen und erlaubte Offenlegungen.', locked: true },
  { id: 'c2', name: 'Anwendbares Recht', desc: 'Wählt Gerichtsbarkeit und Kollisionsnormen.', locked: false },
  { id: 'c3', name: 'Haftungsbeschränkung', desc: 'Begrenzt Schadensersatz; schließt indirekte und Folgeschäden aus.', locked: true },
  { id: 'c4', name: 'Ordentliche Kündigung', desc: 'Ermöglicht beiden Parteien Kündigung mit Kündigungsfrist.', locked: true }
])

const { user, loadUser } = usePortalUser()
const portalUserName = computed(() => user.value?.name || user.value?.email || 'Benutzer')
const portalUserInitials = computed(() => {
  const parts = portalUserName.value.split(/\s+/).filter(Boolean)
  if (!parts.length) return 'AN'
  const initials = parts.map(part => part.charAt(0).toUpperCase()).slice(0, 2).join('')
  return initials || 'AN'
})

const filteredTemplates = computed(() => {
  if (!searchQuery.value) return templates.value
  const query = searchQuery.value.toLowerCase()
  return templates.value.filter(template =>
    template.name.toLowerCase().includes(query) ||
    (template.content || '').toLowerCase().includes(query) ||
    (template.category || '').toLowerCase().includes(query)
  )
})

const lastUpdatedLabel = computed(() => {
  const candidates = templates.value
    .map(item => item?.updatedAt)
    .filter((value): value is string => Boolean(value))
    .map(value => new Date(value))
    .filter(date => !Number.isNaN(date.getTime()))

  if (!candidates.length) return 'Gerade eben'

  candidates.sort((a, b) => b.getTime() - a.getTime())
  const newest = candidates[0]
  const now = new Date()
  const diff = now.getTime() - newest.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) return 'Heute'
  if (days === 1) return 'Gestern'
  if (days < 7) return `vor ${days} Tagen`
  if (days < 30) return `vor ${Math.floor(days / 7)} Wochen`
  return newest.toLocaleDateString()
})

const showToast = (toast: { title: string; description?: string }) => {
  const id = Date.now() + Math.random()
  toasts.value.push({ id, ...toast })
  setTimeout(() => {
    dismissToast(id)
  }, 4000)
}

const dismissToast = (id: number) => {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
  }
}

const loadTemplates = async () => {
  try {
    const r = await fetch(`/api/auth/proxy.get?path=${encodeURIComponent('/api/templates')}`)
    const data = await r.json().catch(() => ({ items: [] }))
    templates.value = Array.isArray(data?.items) ? data.items : (Array.isArray(data) ? data : [])
  } catch (e) {
    console.warn('load templates failed', e)
  } finally {
    isLoading.value = false
  }
}

const handleCreateTemplate = async () => {
  isCreating.value = true
  try {
    const payload = {
      path: '/api/templates',
      method: 'POST',
      body: {
        name: templateForm.value.name,
        content: templateForm.value.content,
        category: templateForm.value.category || 'general',
        type: 'document'
      }
    }
    const r = await fetch('/api/auth/proxy.post', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (r.ok) {
      showCreateModal.value = false
      templateForm.value = { name: '', category: '', content: '' }
      await loadTemplates()
      showToast({ title: 'Vorlage erstellt', description: 'Ihre neue Vorlage wurde erfolgreich gespeichert.' })
    }
  } catch (e) {
    console.warn('create template failed', e)
    showToast({ title: 'Fehler', description: 'Vorlage konnte nicht erstellt werden. Bitte versuchen Sie es erneut.' })
  } finally {
    isCreating.value = false
  }
}

const createTemplate = () => {
  showCreateModal.value = true
}

const useTemplate = (template: any) => {
  navigateTo('/documents')
  showToast({ title: 'Vorlage geladen', description: `${template.name} ist bereit zur Verwendung.` })
}

const editTemplate = (template: any) => {
  showToast({ title: 'Vorlage bearbeiten', description: 'Bearbeitungsfunktion kommt bald.' })
}

const duplicateTemplate = (template: any) => {
  showToast({ title: 'Vorlage dupliziert', description: `Kopie von ${template.name} erstellt.` })
}

const deleteTemplate = async (template: any) => {
  if (!confirm(`Möchten Sie "${template.name}" wirklich löschen?`)) return

  try {
    showToast({ title: 'Vorlage gelöscht', description: `${template.name} wurde gelöscht.` })
    await loadTemplates()
  } catch (e) {
    showToast({ title: 'Fehler', description: 'Vorlage konnte nicht gelöscht werden.' })
  }
}

const handleSuggestion = (suggestion: any) => {
  showToast({ title: 'Vorlage geöffnet', description: `${suggestion.name} wird vorbereitet.` })
}

const copyClause = (clause: any) => {
  showToast({ title: 'Klausel kopiert', description: `${clause.name} in die Zwischenablage kopiert.` })
}

const openClauseLibrary = () => {
  showToast({ title: 'Klauselbibliothek', description: 'Erweiterte Ansicht wird in Kürze freigeschaltet.' })
}

const handleImport = () => {
  showToast({ title: 'Importieren', description: 'Importfunktion kommt bald.' })
}

const handleFilter = () => {
  showToast({ title: 'Filter', description: 'Filteroptionen kommen bald.' })
}

const getTemplateTags = (template: any) => {
  const tags = []
  if (template.category) tags.push(template.category)
  tags.push('Vorlage')
  return tags
}

const formatDate = (dateString: string) => {
  if (!dateString) return 'Nie'
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) return 'Heute'
  if (days === 1) return 'Gestern'
  if (days < 7) return `vor ${days} Tagen`
  if (days < 30) return `vor ${Math.floor(days / 7)} Wochen`
  return date.toLocaleDateString()
}

onMounted(() => {
  loadTemplates()
  loadUser()
})
</script>

<style scoped>
:root {
  --chrome-bg: rgba(255, 255, 255, 0.94);
  --border-soft: rgba(36, 51, 83, 0.08);
  --border-strong: rgba(36, 51, 83, 0.14);
  --shadow-soft: 0 20px 45px rgba(30, 46, 120, 0.12);
  --surface: #ffffff;
  --surface-tint: #f4f6ff;
  --text-strong: #16213e;
  --text-muted: #5d6582;
  --primary: #5b73f2;
  --primary-strong: #3f51d8;
  --primary-soft: rgba(91, 115, 242, 0.14);
  --danger: #e24d4d;
}

* {
  box-sizing: border-box;
}

.templates-intro {
  padding: 32px 28px;
  display: flex;
  flex-direction: column;
  gap: 22px;
  margin-bottom: 28px;
}

.templates-intro__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 28px;
  flex-wrap: wrap;
}

.templates-intro__copy {
  max-width: 760px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.templates-eyebrow {
  font-size: 12px;
  letter-spacing: 0.24em;
  text-transform: uppercase;
  color: var(--primary-strong);
  font-weight: 600;
}

.templates-title {
  font-size: 32px;
  font-weight: 600;
  color: var(--text-strong);
  line-height: 1.2;
}

.templates-lead {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-muted);
  max-width: 640px;
}

.templates-intro__actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.templates-intro__bottom {
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
}

.intro-search {
  flex: 1 1 320px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-radius: 16px;
  border: 1px solid var(--border-soft);
  background: #fff;
  padding: 12px 16px;
  box-shadow: 0 10px 32px rgba(60, 76, 150, 0.1);
}

.search-icon {
  width: 18px;
  height: 18px;
  color: var(--text-muted);
}

.search-input {
  border: none;
  outline: none;
  background: transparent;
  flex: 1;
  font-size: 14px;
  color: var(--text-strong);
}

.search-input::placeholder {
  color: rgba(93, 101, 130, 0.65);
}

.intro-metrics {
  display: flex;
  align-items: stretch;
  gap: 16px;
}

.intro-metric {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 10px 16px;
  border-radius: 14px;
  border: 1px solid var(--border-soft);
  background: linear-gradient(135deg, rgba(91, 115, 242, 0.08), rgba(91, 115, 242, 0.02));
  min-width: 150px;
}

.intro-metric dt {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: rgba(22, 33, 62, 0.65);
  margin-bottom: 6px;
}

.intro-metric dd {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-strong);
}

.intro-user {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  border-radius: 16px;
  border: 1px solid var(--border-soft);
  background: #fff;
  padding: 10px 14px;
  box-shadow: 0 10px 28px rgba(60, 76, 150, 0.12);
}

.intro-avatar {
  width: 34px;
  height: 34px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(91, 115, 242, 0.25), rgba(91, 115, 242, 0.45));
  display: grid;
  place-items: center;
  font-weight: 600;
  color: var(--text-strong);
  font-size: 13px;
  letter-spacing: 0.06em;
}

.intro-username {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-strong);
}

.templates-body {
  background: linear-gradient(180deg, #f4f5fb 0%, #f7f8ff 40%, #ffffff 100%);
  padding: 26px 48px 48px;
}

.templates-layout {
  display: grid;
  grid-template-columns: minmax(260px, 320px) minmax(0, 1fr) minmax(240px, 320px);
  gap: 28px;
  align-items: start;
}

.templates-rail,
.templates-main,
.templates-aside {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.surface {
  background: var(--surface);
  border: 1px solid var(--border-soft);
  border-radius: 24px;
  box-shadow: 0 22px 44px rgba(40, 58, 120, 0.1);
}

.section-block {
  padding: 26px;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.section-heading {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.section-heading--row {
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-strong);
}

.section-sub {
  font-size: 13px;
  color: var(--text-muted);
}

.stat-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.stat-item {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  background: var(--primary-soft);
  color: var(--primary-strong);
  display: grid;
  place-items: center;
}

.stat-icon svg {
  width: 20px;
  height: 20px;
}

.stat-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-strong);
}

.stat-note {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: 14px;
  padding: 10px 18px;
  font-size: 13px;
  font-weight: 600;
  border: 1px solid transparent;
  background: #fff;
  color: var(--text-strong);
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease, background 0.18s ease;
}

.btn .btn-icon {
  width: 16px;
  height: 16px;
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 18px 28px rgba(60, 76, 150, 0.18);
}

.btn.primary {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-strong) 100%);
  color: #fff;
  border-color: rgba(91, 115, 242, 0.18);
}

.btn.primary:hover {
  box-shadow: 0 22px 40px rgba(64, 84, 208, 0.32);
}

.btn.outline {
  border-color: var(--border-strong);
  background: #fff;
}

.btn.outline:hover {
  border-color: rgba(91, 115, 242, 0.38);
}

.btn.ghost {
  border-color: rgba(91, 115, 242, 0.2);
  background: rgba(91, 115, 242, 0.08);
  color: var(--primary-strong);
}

.btn.ghost:hover {
  background: rgba(91, 115, 242, 0.12);
  border-color: rgba(91, 115, 242, 0.32);
}

.btn.text {
  border-color: transparent;
  background: transparent;
  color: var(--primary-strong);
  font-size: 13px;
  padding: 8px 0;
}

.btn.text:hover {
  color: var(--primary);
  transform: none;
  box-shadow: none;
}

.btn.text .chevron {
  width: 16px;
  height: 16px;
  margin-left: 6px;
}

.clause-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.clause-pill {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  border-radius: 18px;
  border: 1px solid var(--border-soft);
  background: rgba(255, 255, 255, 0.92);
  padding: 16px 18px;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
  text-align: left;
}

.clause-pill:hover {
  transform: translateY(-1px);
  border-color: rgba(91, 115, 242, 0.4);
  box-shadow: 0 18px 32px rgba(64, 84, 208, 0.18);
}

.clause-pill__text {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.clause-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-strong);
}

.clause-desc {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
}

.clause-pill__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 12px;
  border: 1px solid rgba(91, 115, 242, 0.2);
  background: rgba(91, 115, 242, 0.1);
  color: var(--primary-strong);
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.clause-pill__icon svg {
  width: 18px;
  height: 18px;
}

.clause-pill__icon.is-locked {
  border-color: rgba(226, 77, 77, 0.25);
  background: rgba(226, 77, 77, 0.12);
  color: #c94141;
}

.templates-panel {
  gap: 28px;
}

.panel-heading {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 18px;
}

.panel-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-strong);
}

.panel-subtitle {
  font-size: 14px;
  color: var(--text-muted);
  margin-top: 6px;
}

.templates-skeleton {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}

.skeleton-card {
  position: relative;
  padding: 22px;
  border-radius: 20px;
  background: rgba(236, 240, 255, 0.5);
  overflow: hidden;
}

.skeleton-card::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(120deg, transparent 0%, rgba(255, 255, 255, 0.65) 50%, transparent 100%);
  animation: shimmer 1.6s ease-in-out infinite;
}

.skeleton-line {
  display: block;
  height: 12px;
  background: rgba(210, 216, 245, 0.7);
  border-radius: 8px;
  margin-bottom: 14px;
}

.skeleton-line.short {
  width: 60%;
}

.skeleton-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.skeleton-tags span {
  flex: 1;
  height: 10px;
  background: rgba(210, 216, 245, 0.7);
  border-radius: 8px;
}

.skeleton-button {
  display: block;
  width: 40%;
  height: 14px;
  background: rgba(210, 216, 245, 0.7);
  border-radius: 999px;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.templates-empty {
  padding: 40px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
  text-align: center;
}

.empty-icon {
  width: 72px;
  height: 72px;
  border-radius: 24px;
  background: var(--primary-soft);
  color: var(--primary-strong);
  display: grid;
  place-items: center;
}

.empty-svg {
  width: 34px;
  height: 34px;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-strong);
}

.empty-text {
  font-size: 14px;
  color: var(--text-muted);
  max-width: 360px;
}

.empty-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 22px;
}

.template-card {
  border: 1px solid rgba(91, 115, 242, 0.12);
  border-radius: 22px;
  padding: 24px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.9) 0%, #ffffff 100%);
  display: flex;
  flex-direction: column;
  gap: 18px;
  box-shadow: 0 20px 36px rgba(36, 51, 104, 0.08);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.template-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 28px 50px rgba(36, 51, 104, 0.16);
}

.template-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.template-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-strong);
  line-height: 1.3;
}

.template-chip {
  background: rgba(91, 115, 242, 0.12);
  color: var(--primary-strong);
  border: 1px solid rgba(91, 115, 242, 0.22);
  border-radius: 999px;
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease;
}

.template-chip:hover {
  background: rgba(91, 115, 242, 0.2);
}

.template-description {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.55;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.template-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.meta-block {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
}

.meta-icon {
  width: 16px;
  height: 16px;
}

.template-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  border: 1px solid rgba(91, 115, 242, 0.18);
  background: rgba(91, 115, 242, 0.08);
  color: var(--primary-strong);
  font-size: 11px;
  padding: 6px 12px;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.template-footer {
  margin-top: auto;
  display: flex;
  justify-content: flex-end;
}

.template-actions {
  display: inline-flex;
  gap: 10px;
}

.icon-button {
  width: 34px;
  height: 34px;
  border-radius: 12px;
  border: 1px solid rgba(91, 115, 242, 0.18);
  background: rgba(255, 255, 255, 0.94);
  display: grid;
  place-items: center;
  color: var(--text-strong);
  cursor: pointer;
  transition: background 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
}

.icon-button:hover {
  transform: translateY(-1px);
  border-color: rgba(91, 115, 242, 0.32);
  background: rgba(91, 115, 242, 0.1);
  color: var(--primary-strong);
}

.icon-button svg {
  width: 16px;
  height: 16px;
}

.icon-button.danger {
  border-color: rgba(226, 77, 77, 0.18);
  color: #b93838;
}

.icon-button.danger:hover {
  background: rgba(226, 77, 77, 0.12);
  border-color: rgba(226, 77, 77, 0.32);
  color: #a52727;
}

.recommend-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.recommend-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
  border-radius: 18px;
  border: 1px solid rgba(91, 115, 242, 0.14);
  padding: 18px;
  background: rgba(249, 250, 255, 0.9);
}

.recommend-card__body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.recommend-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-strong);
}

.recommend-note {
  font-size: 12px;
  color: var(--text-muted);
}

.recommend-progress {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-track {
  flex: 1;
  height: 6px;
  border-radius: 999px;
  background: rgba(91, 115, 242, 0.16);
  overflow: hidden;
}

.progress-fill {
  display: block;
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-strong) 100%);
}

.recommend-score {
  font-size: 12px;
  font-weight: 600;
  color: var(--primary-strong);
}

.metric-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metric-pill {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  border-radius: 16px;
  border: 1px solid rgba(91, 115, 242, 0.12);
  background: rgba(91, 115, 242, 0.08);
}

.metric-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: rgba(22, 33, 62, 0.68);
}

.metric-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-strong);
}

.toast-stack {
  position: fixed;
  bottom: 32px;
  right: 32px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 80;
}

.toast-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  min-width: 260px;
  border-radius: 16px;
  border: 1px solid rgba(22, 33, 62, 0.08);
  background: rgba(255, 255, 255, 0.96);
  padding: 14px 18px;
  box-shadow: 0 16px 28px rgba(36, 51, 104, 0.18);
}

.toast-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-strong);
}

.toast-message {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(14px);
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 22, 45, 0.32);
  backdrop-filter: blur(6px);
  display: grid;
  place-items: center;
  padding: 24px;
  z-index: 90;
}

.modal-shell {
  width: min(720px, 100%);
  border-radius: 28px;
  background: var(--surface);
  border: 1px solid rgba(36, 51, 83, 0.12);
  box-shadow: var(--shadow-soft);
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 28px;
  border-bottom: 1px solid rgba(36, 51, 83, 0.08);
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-strong);
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 28px;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-strong);
}

.field-input,
.field-textarea {
  border: 1px solid rgba(36, 51, 83, 0.14);
  border-radius: 14px;
  padding: 12px 14px;
  font-size: 14px;
  color: var(--text-strong);
  resize: vertical;
  background: #fff;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.field-input:focus,
.field-textarea:focus {
  border-color: rgba(91, 115, 242, 0.5);
  box-shadow: 0 0 0 4px rgba(91, 115, 242, 0.14);
  outline: none;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 12px;
}

@media (max-width: 1280px) {
  .templates-layout {
    grid-template-columns: minmax(220px, 280px) minmax(0, 1fr);
  }

  .templates-aside {
    grid-column: 1 / -1;
    flex-direction: row;
    flex-wrap: wrap;
  }

  .templates-aside > * {
    flex: 1 1 320px;
  }
}

@media (max-width: 960px) {
  .templates-intro {
    padding: 24px 20px;
  }

  .templates-intro__top {
    flex-direction: column;
  }

  .templates-intro__actions {
    align-self: flex-start;
  }

  .templates-intro__bottom {
    flex-direction: column;
    align-items: stretch;
  }

  .intro-search {
    width: 100%;
  }

  .intro-metrics {
    width: 100%;
    justify-content: space-between;
  }

  .intro-user {
    align-self: flex-start;
  }

  .templates-layout {
    grid-template-columns: 1fr;
  }

  .templates-rail,
  .templates-main,
  .templates-aside {
    flex-direction: column;
  }

  .templates-aside {
    gap: 24px;
  }

  .templates-body {
    padding: 24px 20px 40px;
  }

  .templates-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .templates-intro {
    padding: 22px 18px;
  }

  .templates-body {
    padding: 24px 16px 40px;
  }

  .intro-metrics {
    flex-direction: column;
    gap: 12px;
  }

  .intro-metric {
    width: 100%;
  }

  .intro-user {
    width: 100%;
    justify-content: center;
  }

  .templates-grid {
    gap: 18px;
  }

  .toast-stack {
    left: 16px;
    right: 16px;
    bottom: 20px;
    align-items: stretch;
  }

  .toast-item {
    width: 100%;
  }
}
</style>
