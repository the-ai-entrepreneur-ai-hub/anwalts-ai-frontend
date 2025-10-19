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
            <button type="button" class="btn ghost" @click="openClauseModal">
              <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 6a2 2 0 012-2h6l6 6v8a2 2 0 01-2 2H7a2 2 0 01-2-2V6z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-3-3v6" />
              </svg>
              Neue Klausel
            </button>
            <button type="button" class="btn outline" @click="handleImport" :disabled="isImporting">
              <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
              </svg>
              {{ isImporting ? 'Import läuft…' : 'Importieren' }}
            </button>
            <button type="button" class="btn primary" @click="createTemplate">
              <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v12m6-6H6" />
              </svg>
              Neue Vorlage
            </button>
            <input
              ref="importInputRef"
              type="file"
              class="visually-hidden"
              :disabled="isImporting"
              accept=".pdf,.doc,.docx,.txt,.rtf,.md,.markdown,.html,.odt"
              @change="onImportSelected"
            />
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
              <div class="clause-actions">
                <button type="button" class="btn ghost" @click="openClauseModal">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M5 6a2 2 0 012-2h6l6 6v8a2 2 0 01-2 2H7a2 2 0 01-2-2V6z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 12h6m-3-3v6" />
                  </svg>
                  Neue Klausel
                </button>
                <button type="button" class="btn text" @click="openClauseLibrary">
                  Alle anzeigen
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" class="chevron">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            </header>
            <p v-if="isUsingFallbackClauses" class="clause-hint">
              Vorschläge basieren auf Standardklauseln – legen Sie eigene Bausteine über „Neue Klausel“ an.
            </p>
            <div v-if="isClausesLoading" class="clause-empty">
              <span>Bausteine werden geladen…</span>
            </div>
            <div v-else-if="clausesError" class="clause-empty clause-empty--error">
              <span>{{ clausesError }}</span>
            </div>
            <div v-else-if="clauses.length === 0" class="clause-empty">
              <span>Noch keine Bausteine vorhanden.</span>
            </div>
            <div v-else class="clause-list">
              <button
                v-for="clause in clauses"
                :key="clause.id"
                type="button"
                class="clause-pill"
                @click="copyClause(clause)"
              >
                <div class="clause-pill__text">
                  <div class="clause-pill__headline">
                    <span class="clause-title">{{ clause.name }}</span>
                    <span v-if="clause.isFallback" class="clause-badge">Vorschlag</span>
                  </div>
                  <span class="clause-desc">{{ clause.desc }}</span>
                  <span v-if="clause.category" class="clause-meta">{{ clause.category }}</span>
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

            <div v-if="isTemplatesLoading" class="templates-skeleton">
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

            <div v-else-if="templatesError" class="templates-empty templates-empty--error">
              <div class="empty-icon">
                <svg class="empty-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 class="empty-title">Vorlagen konnten nicht geladen werden</h3>
              <p class="empty-text">{{ templatesError }}</p>
              <div class="empty-actions">
                <button type="button" class="btn primary" @click="refreshCatalog" :disabled="isRefreshing">
                  Erneut versuchen
                </button>
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
                <button type="button" class="btn primary" @click="handleImport" :disabled="isImporting">
                  <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                  </svg>
                  {{ isImporting ? 'Import läuft…' : 'Importieren' }}
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
      v-if="showTemplateModal"
      class="modal-backdrop"
      @click.self="showTemplateModal = false"
    >
      <div class="modal-shell">
        <header class="modal-header">
          <h2 class="modal-title">Neue Vorlage erstellen</h2>
          <button
            type="button"
            class="icon-button ghost"
            @click="showTemplateModal = false"
            aria-label="Schließen"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </header>
        <form @submit.prevent="submitTemplateForm" class="modal-body">
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
            <button type="button" class="btn ghost" @click="showTemplateModal = false">
              Abbrechen
            </button>
            <button type="submit" class="btn primary" :disabled="isSavingTemplate">
              {{ isSavingTemplate ? 'Wird gespeichert…' : (modalMode === 'create' ? 'Vorlage erstellen' : 'Änderungen speichern') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div
      v-if="showClauseModal"
      class="modal-backdrop"
      @click.self="closeClauseModal"
    >
      <div class="modal-shell clause-modal">
        <header class="modal-header">
          <h2 class="modal-title">Neue Klausel anlegen</h2>
          <button
            type="button"
            class="icon-button ghost"
            @click="closeClauseModal"
            aria-label="Schließen"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </header>
        <form @submit.prevent="submitClauseForm" class="modal-body">
          <label class="field-group">
            <span class="field-label">Titel</span>
            <input
              v-model="clauseForm.title"
              type="text"
              required
              class="field-input"
              placeholder="Bezeichnung der Klausel"
            />
          </label>
          <label class="field-group">
            <span class="field-label">Kategorie</span>
            <input
              v-model="clauseForm.category"
              type="text"
              class="field-input"
              placeholder="Z. B. Vertragsrecht"
            />
          </label>
          <label class="field-group">
            <span class="field-label">Sprache</span>
            <select v-model="clauseForm.language" class="field-input">
              <option value="de">Deutsch</option>
              <option value="en">Englisch</option>
            </select>
          </label>
          <label class="field-group">
            <span class="field-label">Inhalt</span>
            <textarea
              v-model="clauseForm.content"
              class="field-textarea"
              rows="8"
              required
              placeholder="Klauseltext hier einfügen oder formulieren"
            ></textarea>
          </label>
          <footer class="modal-actions">
            <button
              type="button"
              class="btn ghost"
              @click="closeClauseModal"
              :disabled="isSavingClause"
            >
              Abbrechen
            </button>
            <button
              type="submit"
              class="btn primary"
              :disabled="isSavingClause"
            >
              {{ isSavingClause ? 'Speichern…' : 'Klausel speichern' }}
            </button>
          </footer>
        </form>
      </div>
    </div>
  </PortalShell>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import PortalShell from '~/components/PortalShell.vue'
import { usePortalUser } from '~/composables/usePortalUser'

definePageMeta({ layout: false })

type TemplateRecord = {
  id: string
  name: string
  content: string
  category?: string
  description?: string
  usageCount?: number
  createdBy?: string
  createdAt?: string | null
  updatedAt?: string | null
  type?: string
}

interface TemplateSuggestion {
  id: string
  name: string
  category?: string
  usage_count: number
  match_score: number
  updated_at?: string | null
}

interface TemplateInsights {
  counts: {
    active: number
    updated_recent: number
    usage_events: number
  }
  last_updated_at?: string | null
  suggestions: TemplateSuggestion[]
  top_categories: { label: string; count: number }[]
  recent_templates: TemplateRecord[]
}

type ClauseRecord = {
  id: string
  name: string
  desc: string
  content: string
  locked: boolean
  category?: string | null
  language?: string | null
  isFallback?: boolean
}

const randomId = (prefix = 'item') => `${prefix}_${Math.random().toString(36).slice(2, 10)}`

const templates = ref<TemplateRecord[]>([])
const templatesError = ref<string | null>(null)
const isTemplatesLoading = ref(true)
const importInputRef = ref<HTMLInputElement | null>(null)
const isImporting = ref(false)

const IMPORT_MAX_BYTES = 10 * 1024 * 1024
const IMPORT_ACCEPTED_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
  'text/rtf',
  'application/rtf',
  'text/markdown',
  'text/html',
  'application/vnd.oasis.opendocument.text'
]

const insights = ref<TemplateInsights | null>(null)
const insightsError = ref<string | null>(null)
const isInsightsLoading = ref(true)

const clauses = ref<ClauseRecord[]>([])
const clausesError = ref<string | null>(null)
const isClausesLoading = ref(true)
const isUsingFallbackClauses = ref(false)

const searchQuery = ref('')
const showTemplateModal = ref(false)
const modalMode = ref<'create' | 'edit'>('create')
const isSavingTemplate = ref(false)
const isRefreshing = ref(false)
const toasts = ref<Array<{ id: number; title: string; description?: string }>>([])
const showClauseModal = ref(false)
const isSavingClause = ref(false)

const templateForm = ref({
  id: '',
  name: '',
  category: '',
  content: '',
  updatedAt: ''
})

const clauseForm = ref({
  title: '',
  category: '',
  language: 'de',
  content: ''
})

const summarizeContent = (source: string): string => {
  const text = String(source || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()
  if (!text) return ''
  return text.length > 180 ? `${text.slice(0, 177)}…` : text
}

const normalizeTemplate = (entry: any): TemplateRecord => ({
  id: String(entry?.id ?? entry?.template_id ?? ''),
  name: entry?.title || entry?.name || 'Vorlage',
  content: entry?.content || '',
  category: entry?.category || 'Allgemein',
  description: entry?.description || entry?.summary || summarizeContent(entry?.content || ''),
  usageCount: Number(entry?.usage_count ?? entry?.usageCount ?? 0),
  createdBy: entry?.created_by || entry?.createdBy || entry?.author || 'Ihr Team',
  createdAt: entry?.created_at || entry?.createdAt || null,
  updatedAt: entry?.updated_at || entry?.updatedAt || null,
  type: entry?.type || 'document'
})

const normalizeClause = (entry: any): ClauseRecord => ({
  id: String(entry?.id ?? randomId('clause')),
  name: entry?.title || entry?.name || 'Klausel',
  desc: entry?.summary || entry?.desc || summarizeContent(entry?.content || ''),
  content: entry?.content || entry?.body || '',
  locked: Boolean(entry?.locked ?? entry?.premium ?? false),
  category: entry?.category || null,
  language: entry?.language || null,
  isFallback: false
})

const normalizeInsights = (raw: any): TemplateInsights => ({
  counts: {
    active: Number(raw?.counts?.active || 0),
    updated_recent: Number(raw?.counts?.updated_recent || 0),
    usage_events: Number(raw?.counts?.usage_events || 0)
  },
  last_updated_at: raw?.last_updated_at || null,
  suggestions: Array.isArray(raw?.suggestions)
    ? raw.suggestions
        .map((item: any) => ({
          id: String(item?.id ?? ''),
          name: item?.name || 'Vorlage',
          category: item?.category || 'Allgemein',
          usage_count: Number(item?.usage_count || 0),
          match_score: Number(item?.match_score || 35),
          updated_at: item?.updated_at || null
        }))
        .filter((item: TemplateSuggestion) => item.id)
    : [],
  top_categories: Array.isArray(raw?.top_categories)
    ? raw.top_categories.map((item: any) => ({
        label: item?.label || 'Allgemein',
        count: Number(item?.count || 0)
      }))
    : [],
  recent_templates: Array.isArray(raw?.recent_templates)
    ? raw.recent_templates
        .map(normalizeTemplate)
        .filter((item: TemplateRecord) => Boolean(item.id))
    : []
})

const showToast = (toast: { title: string; description?: string }) => {
  const id = Date.now() + Math.random()
  toasts.value.push({ id, ...toast })
  setTimeout(() => dismissToast(id), 4000)
}

const dismissToast = (id: number) => {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
  }
}

const buildClauseFallback = (): ClauseRecord[] => [
  {
    id: 'fallback_bgb_242',
    name: 'Treu und Glauben (§ 242 BGB)',
    desc: 'Erinnert an die Pflicht zu loyalem Verhalten zwischen Schuldner und Gläubiger.',
    content: '„Der Schuldner ist verpflichtet, die Leistung so zu bewirken, wie Treu und Glauben mit Rücksicht auf die Verkehrssitte es erfordern.“ (§ 242 BGB)',
    locked: false,
    category: 'BGB · Allgemeines Schuldrecht',
    language: 'de',
    isFallback: true
  },
  {
    id: 'fallback_bgb_305c',
    name: 'Überraschungsklausel (§ 305c BGB)',
    desc: 'Stellt klar, dass ungewöhnliche Klauseln in AGB unwirksam sind.',
    content: '„Bestimmungen in Allgemeinen Geschäftsbedingungen, die nach den Umständen, insbesondere nach dem äußeren Erscheinungsbild des Vertrags, so ungewöhnlich sind, dass der Vertragspartner mit ihnen nicht zu rechnen braucht, werden nicht Vertragsbestandteil.“ (§ 305c Abs. 1 BGB)',
    locked: false,
    category: 'BGB · Vertragsrecht',
    language: 'de',
    isFallback: true
  },
  {
    id: 'fallback_bgb_307',
    name: 'Inhaltskontrolle (§ 307 BGB)',
    desc: 'Verhindert unangemessene Benachteiligung innerhalb vorformulierter Klauseln.',
    content: '„(1) Bestimmungen in Allgemeinen Geschäftsbedingungen sind unwirksam, wenn sie den Vertragspartner des Verwenders entgegen den Geboten von Treu und Glauben unangemessen benachteiligen.“ (§ 307 Abs. 1 BGB)',
    locked: false,
    category: 'BGB · Vertragsrecht',
    language: 'de',
    isFallback: true
  },
  {
    id: 'fallback_bgb_675o',
    name: 'Informationspflicht (§ 675o BGB)',
    desc: 'Sichert transparente Kommunikation bei Zahlungsdiensteverträgen ab.',
    content: '§ 675o Abs. 1 BGB verpflichtet Zahlungsdienstleister, ihren Kunden rechtzeitig Informationen über Vertragsbedingungen, Entgelte und Pflichten zur Verfügung zu stellen.',
    locked: false,
    category: 'BGB · Zahlungsdienste',
    language: 'de',
    isFallback: true
  },
  {
    id: 'fallback_bgb_823',
    name: 'Schadensersatzpflicht (§ 823 BGB)',
    desc: 'Grundlage für Schadensersatzansprüche bei widerrechtlicher Verletzung geschützter Rechtsgüter.',
    content: '„Wer vorsätzlich oder fahrlässig das Leben, den Körper, die Gesundheit, die Freiheit, das Eigentum oder ein sonstiges Recht eines anderen widerrechtlich verletzt, ist dem anderen zum Ersatz des daraus entstehenden Schadens verpflichtet.“ (§ 823 Abs. 1 BGB)',
    locked: false,
    category: 'BGB · Deliktsrecht',
    language: 'de',
    isFallback: true
  },
  {
    id: 'fallback_gwg_6',
    name: 'Sorgfaltspflichten (§ 6 GwG)',
    desc: 'Pflichten zur Identifizierung und Risikoprüfung bei neuen Mandaten.',
    content: '§ 6 Abs. 1 GwG verpflichtet Verpflichtete, risikoorientierte Sorgfaltspflichten einschließlich Identifizierung des Vertragspartners und der wirtschaftlich Berechtigten anzuwenden.',
    locked: false,
    category: 'GwG · Compliance',
    language: 'de',
    isFallback: true
  }
]

const loadTemplates = async () => {
  isTemplatesLoading.value = true
  templatesError.value = null
  try {
    const response = await $fetch<any[]>('/api/templates', {
      headers: { accept: 'application/json' }
    })
    const records = Array.isArray(response) ? response.map(normalizeTemplate).filter(item => item.id) : []
    records.sort((a, b) => {
      const aTime = new Date(a.updatedAt || a.createdAt || 0).getTime()
      const bTime = new Date(b.updatedAt || b.createdAt || 0).getTime()
      return bTime - aTime
    })
    templates.value = records
  } catch (error: any) {
    const message = error?.data?.detail || error?.message || 'Vorlagen konnten nicht geladen werden.'
    templatesError.value = message
    templates.value = []
    showToast({ title: 'Fehler', description: message })
  } finally {
    isTemplatesLoading.value = false
  }
}

const loadClauses = async () => {
  isClausesLoading.value = true
  clausesError.value = null
  try {
    const response = await $fetch<any[]>('/api/documents/clauses', {
      headers: { accept: 'application/json' }
    })
    const list = Array.isArray(response) ? response.map(normalizeClause) : []
    if (list.length) {
      clauses.value = list
      isUsingFallbackClauses.value = false
    } else {
      clauses.value = buildClauseFallback()
      isUsingFallbackClauses.value = true
    }
  } catch (error: any) {
    const message = error?.data?.detail || error?.message || 'Bausteine konnten nicht geladen werden.'
    if (!isUsingFallbackClauses.value) {
      showToast({
        title: 'Hinweis',
        description: 'Eigene Klauseln konnten nicht geladen werden. Es werden Vorschläge angezeigt.'
      })
    }
    clausesError.value = null
    clauses.value = buildClauseFallback()
    isUsingFallbackClauses.value = true
    console.warn(message)
  } finally {
    isClausesLoading.value = false
  }
}

const loadInsights = async () => {
  isInsightsLoading.value = true
  insightsError.value = null
  try {
    const response = await $fetch('/api/templates/insights', {
      headers: { accept: 'application/json' }
    })
    insights.value = normalizeInsights(response)
  } catch (error: any) {
    const message = error?.data?.detail || error?.message || 'Vorlagenstatistiken konnten nicht geladen werden.'
    insightsError.value = message
    insights.value = null
    showToast({ title: 'Hinweis', description: message })
  } finally {
    isInsightsLoading.value = false
  }
}

const refreshCatalog = async () => {
  if (isRefreshing.value) return
  isRefreshing.value = true
  try {
    await Promise.all([loadTemplates(), loadInsights(), loadClauses()])
  } finally {
    isRefreshing.value = false
  }
}

const resetTemplateForm = () => {
  templateForm.value = {
    id: '',
    name: '',
    category: '',
    content: '',
    updatedAt: ''
  }
}

const createTemplate = () => {
  modalMode.value = 'create'
  resetTemplateForm()
  showTemplateModal.value = true
}

const editTemplate = (template: TemplateRecord) => {
  modalMode.value = 'edit'
  templateForm.value = {
    id: template.id,
    name: template.name,
    category: template.category || '',
    content: template.content || '',
    updatedAt: template.updatedAt || ''
  }
  showTemplateModal.value = true
}

const submitTemplateForm = async () => {
  if (isSavingTemplate.value) return
  const name = templateForm.value.name.trim()
  const content = templateForm.value.content.trim()
  if (!name || !content) {
    showToast({ title: 'Fehlende Angaben', description: 'Name und Inhalt der Vorlage sind erforderlich.' })
    return
  }

  isSavingTemplate.value = true
  try {
    if (modalMode.value === 'create') {
      await $fetch('/api/templates', {
        method: 'POST',
        body: {
          title: name,
          name,
          content,
          category: templateForm.value.category.trim() || null,
          type: 'document'
        }
      })
      showToast({ title: 'Vorlage erstellt', description: `"${name}" ist jetzt verfügbar.` })
    } else {
      if (!templateForm.value.id || !templateForm.value.updatedAt) {
        throw new Error('Aktuelle Versionsinformation fehlt.')
      }
      await $fetch(`/api/templates/${templateForm.value.id}`, {
        method: 'PUT',
        body: {
          title: name,
          name,
          content,
          category: templateForm.value.category.trim() || null,
          type: 'document',
          updated_at: templateForm.value.updatedAt
        }
      })
      showToast({ title: 'Vorlage aktualisiert', description: `"${name}" wurde gespeichert.` })
    }

    showTemplateModal.value = false
    resetTemplateForm()
    await refreshCatalog()
  } catch (error: any) {
    const message = error?.data?.detail || error?.message || 'Aktion fehlgeschlagen.'
    showToast({ title: 'Fehler', description: message })
  } finally {
    isSavingTemplate.value = false
  }
}

const duplicateTemplate = async (template: TemplateRecord) => {
  const duplicateName = `${template.name} (Kopie)`
  try {
    await $fetch('/api/templates', {
      method: 'POST',
      body: {
        title: duplicateName,
        name: duplicateName,
        content: template.content,
        category: template.category || null,
        type: template.type || 'document'
      }
    })
    showToast({ title: 'Vorlage dupliziert', description: `"${duplicateName}" wurde angelegt.` })
    await refreshCatalog()
  } catch (error: any) {
    const message = error?.data?.detail || error?.message || 'Vorlage konnte nicht dupliziert werden.'
    showToast({ title: 'Fehler', description: message })
  }
}

const deleteTemplate = async (template: TemplateRecord) => {
  if (!confirm(`Möchten Sie "${template.name}" wirklich löschen?`)) return
  try {
    const query = template.updatedAt ? `?updatedAt=${encodeURIComponent(template.updatedAt)}` : ''
    await $fetch(`/api/templates/${template.id}${query}`, { method: 'DELETE' })
    showToast({ title: 'Vorlage gelöscht', description: `"${template.name}" wurde entfernt.` })
    await refreshCatalog()
  } catch (error: any) {
    const message = error?.data?.detail || error?.message || 'Vorlage konnte nicht gelöscht werden.'
    showToast({ title: 'Fehler', description: message })
  }
}

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

const highlightCards = computed(() => {
  const counts = insights.value?.counts
  const now = Date.now()
  const fallbackActive = templates.value.length
  const fallbackUpdated = templates.value.filter(template => {
    const ts = new Date(template.updatedAt || template.createdAt || 0).getTime()
    if (Number.isNaN(ts) || !ts) return false
    const diffDays = (now - ts) / (1000 * 60 * 60 * 24)
    return diffDays <= 30
  }).length
  const fallbackUsage = templates.value.reduce((sum, template) => sum + (template.usageCount || 0), 0)
  const active = Math.max(counts?.active ?? 0, fallbackActive)
  const updatedRecent = Math.max(counts?.updated_recent ?? 0, fallbackUpdated)
  const usageEvents = Math.max(counts?.usage_events ?? 0, fallbackUsage)
  return [
    {
      id: 'active',
      icon: 'shield',
      title: 'Aktive Vorlagen',
      note: active > 0 ? `${active} im Katalog` : 'Noch keine Vorlagen'
    },
    {
      id: 'updated',
      icon: 'clock',
      title: 'Aktualisiert (30 Tage)',
      note: updatedRecent > 0 ? `${updatedRecent} aktualisiert` : 'Keine Aktualisierungen im letzten Monat'
    },
    {
      id: 'usage',
      icon: 'chat',
      title: 'Verwendungen',
      note: usageEvents > 0 ? `${usageEvents} Übergaben an Dokumente` : 'Noch keine dokumentierten Übergaben'
    }
  ]
})

const suggestedTemplates = computed(() => {
  const items = insights.value?.suggestions || []
  if (items.length) {
    return items.map(item => ({
      id: item.id,
      name: item.name,
      note: item.category ? `Kategorie: ${item.category}` : 'Empfehlung aus Nutzungsmustern',
      match: Math.min(100, Math.max(35, item.match_score))
    }))
  }
  return templates.value.slice(0, 3).map((template, index) => ({
    id: template.id,
    name: template.name,
    note: template.category ? `Kategorie: ${template.category}` : 'Vorlage aus Ihrem Katalog',
    match: Math.max(45, 70 - index * 10)
  }))
})

const mostUsed = computed(() => {
  const categories = insights.value?.top_categories || []
  if (categories.length) {
    return categories
  }
  const fallback = templates.value.reduce<Record<string, number>>((acc, template) => {
    const key = template.category || 'Allgemein'
    acc[key] = (acc[key] || 0) + 1
    return acc
  }, {})
  return Object.entries(fallback).map(([label, count]) => ({ label, count }))
})

const recentTemplateCards = computed(() => {
  return (insights.value?.recent_templates || []).map(item => ({
    id: item.id,
    name: item.name,
    desc: item.category ? `Kategorie: ${item.category}` : 'Neu hinzugefügt',
    updatedAt: item.updatedAt || item.createdAt,
    template: item
  }))
})

const lastUpdatedLabel = computed(() => {
  const last = insights.value?.last_updated_at
  const candidates = [
    ...(last ? [new Date(last)] : []),
    ...templates.value
      .map(item => item.updatedAt || item.createdAt)
      .filter(Boolean)
      .map(value => new Date(value as string))
  ].filter(date => !Number.isNaN(date.getTime()))

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

const useTemplate = (template: TemplateRecord) => {
  try {
    const payload = {
      id: template.id,
      name: template.name,
      content: template.content,
      category: template.category || 'Allgemein',
      updatedAt: template.updatedAt || new Date().toISOString(),
      ts: Date.now()
    }
    localStorage.setItem('anwalt.templateSelection', JSON.stringify(payload))
    if (payload.id) localStorage.setItem('anwalt.templateId', String(payload.id))
  } catch (_) {}

  const idParam = encodeURIComponent(template.id || template.name)
  navigateTo(`/documents${idParam ? `?templateId=${idParam}` : ''}`)
  showToast({ title: 'Vorlage geladen', description: `${template.name} ist bereit zur Verwendung.` })
}

const useTemplateById = async (id: string) => {
  if (!id) return
  let template = templates.value.find(item => item.id === id)
  if (!template) {
    await loadTemplates()
    template = templates.value.find(item => item.id === id)
  }
  if (template) {
    useTemplate(template)
  } else {
    showToast({ title: 'Vorlage nicht gefunden', description: 'Bitte laden Sie die Übersicht neu.' })
  }
}

const handleSuggestion = (suggestion: { id: string; name: string }) => {
  useTemplateById(suggestion.id)
}

const resetImportInput = () => {
  if (importInputRef.value) {
    importInputRef.value.value = ''
  }
}

const handleImport = () => {
  if (isImporting.value) return
  importInputRef.value?.click()
}

const onImportSelected = async (event: Event) => {
  const target = event.target as HTMLInputElement | null
  const file = target?.files?.[0]
  if (!file) {
    resetImportInput()
    return
  }

  if (file.size > IMPORT_MAX_BYTES) {
    showToast({
      title: 'Upload zu groß',
      description: 'Bitte wählen Sie eine Datei unter 10 MB.'
    })
    resetImportInput()
    return
  }

  if (IMPORT_ACCEPTED_TYPES.length && file.type && !IMPORT_ACCEPTED_TYPES.includes(file.type)) {
    showToast({
      title: 'Format nicht unterstützt',
      description: 'Bitte verwenden Sie PDF, DOCX, DOC oder TXT.'
    })
    resetImportInput()
    return
  }

  const formData = new FormData()
  formData.append('file', file)

  isImporting.value = true
  showToast({
    title: 'Import gestartet',
    description: 'Vorlage wird aus dem Dokument erstellt…'
  })

  try {
    const response = await $fetch('/api/templates/import', {
      method: 'POST',
      body: formData
    })
    const imported = normalizeTemplate(response)
    if (!imported.id) {
      throw new Error('Importierte Vorlage enthält keine ID.')
    }
    templatesError.value = null
    templates.value = [
      imported,
      ...templates.value.filter(template => template.id !== imported.id)
    ]
    showToast({
      title: 'Vorlage importiert',
      description: `"${imported.name}" wurde erfolgreich angelegt.`
    })
    // Refresh insights asynchronously; ignore failures
    loadInsights().catch(() => {})
  } catch (error: any) {
    const message = error?.data?.detail || error?.message || 'Import fehlgeschlagen.'
    showToast({
      title: 'Import fehlgeschlagen',
      description: message
    })
  } finally {
    isImporting.value = false
    resetImportInput()
  }
}

const copyClause = async (clause: ClauseRecord) => {
  const payload = clause.content || clause.desc || clause.name
  try {
    if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(payload)
      showToast({ title: 'Klausel kopiert', description: `${clause.name} wurde in die Zwischenablage kopiert.` })
    } else {
      throw new Error('Clipboard API nicht verfügbar')
    }
  } catch (error) {
    showToast({ title: 'Fehler', description: 'Klausel konnte nicht kopiert werden.' })
  }
}

const openClauseLibrary = () => {
  showToast({ title: 'Klauselbibliothek', description: 'Erweiterte Ansicht ist in Vorbereitung.' })
}

const resetClauseForm = () => {
  clauseForm.value = {
    title: '',
    category: '',
    language: 'de',
    content: ''
  }
}

const openClauseModal = () => {
  resetClauseForm()
  showClauseModal.value = true
}

const closeClauseModal = () => {
  if (isSavingClause.value) return
  showClauseModal.value = false
}

const getTemplateTags = (template: TemplateRecord) => {
  const tags = []
  if (template.category) tags.push(template.category)
  if (template.type) tags.push(template.type)
  tags.push('Vorlage')
  return tags
}

const formatDate = (dateString: string | null | undefined) => {
  if (!dateString) return 'Nie'
  const date = new Date(dateString)
  if (Number.isNaN(date.getTime())) return 'Nie'
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) return 'Heute'
  if (days === 1) return 'Gestern'
  if (days < 7) return `vor ${days} Tagen`
  if (days < 30) return `vor ${Math.floor(days / 7)} Wochen`
  return date.toLocaleDateString()
}

const submitClauseForm = async () => {
  const title = clauseForm.value.title.trim()
  const content = clauseForm.value.content.trim()
  const category = clauseForm.value.category.trim()
  const language = clauseForm.value.language || 'de'

  if (!title || !content) {
    showToast({ title: 'Hinweis', description: 'Bitte geben Sie Titel und Inhalt der Klausel an.' })
    return
  }

  isSavingClause.value = true
  try {
    await $fetch('/api/clauses', {
      method: 'POST',
      body: {
        title,
        content,
        category: category || null,
        language
      }
    })
    showToast({ title: 'Klausel erstellt', description: `"${title}" steht jetzt im Katalog bereit.` })
    showClauseModal.value = false
    resetClauseForm()
    await loadClauses()
  } catch (error: any) {
    const message = error?.data?.detail || error?.message || 'Klausel konnte nicht erstellt werden.'
    showToast({ title: 'Fehler', description: message })
  } finally {
    isSavingClause.value = false
  }
}

watch(templates, () => {
  if (isUsingFallbackClauses.value) {
    clauses.value = buildClauseFallback()
  }
})

onMounted(async () => {
  await Promise.all([loadTemplates(), loadInsights(), loadClauses()])
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
  --primary: #5b7ce6;
  --primary-strong: #5b7ce6;
  --primary-soft: rgba(91, 124, 230, 0.14);
  --danger: #e24d4d;
}

* {
  box-sizing: border-box;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
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
  background: linear-gradient(135deg, rgba(91, 124, 230, 0.08), rgba(91, 124, 230, 0.02));
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
  background: linear-gradient(135deg, rgba(91, 124, 230, 0.25), rgba(91, 124, 230, 0.45));
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
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 22px;
  overflow: hidden;
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
  gap: 14px;
  align-items: flex-start;
  overflow: hidden;
}

.stat-icon {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  flex-shrink: 0;
  background: rgba(91, 124, 230, 0.12);
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
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.stat-note {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
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
  transition: all 0.2s ease;
}

.btn:active {
  transform: translateY(0) scale(0.98);
}

.btn.primary {
  background: linear-gradient(135deg, #5b7ce6 0%, #4a6cd4 100%);
  color: #fff;
  border-color: rgba(91, 124, 230, 0.25);
  font-weight: 600;
  box-shadow: 0 10px 30px rgba(91, 124, 230, 0.25);
}

.btn.primary:hover {
  box-shadow: 0 18px 40px rgba(91, 124, 230, 0.35);
  transform: translateY(-2px);
  background: linear-gradient(135deg, #4a6cd4 0%, #3b5fc7 100%);
}

.btn.outline {
  border-color: rgba(91, 124, 230, 0.3);
  background: rgba(91, 124, 230, 0.06);
  color: var(--primary-strong);
  font-weight: 600;
}

.btn.outline:hover {
  border-color: rgba(91, 124, 230, 0.5);
  background: rgba(91, 124, 230, 0.12);
  box-shadow: 0 10px 25px rgba(91, 124, 230, 0.15);
}

.btn.ghost {
  border-color: rgba(91, 124, 230, 0.25);
  background: rgba(91, 124, 230, 0.1);
  color: var(--primary-strong);
  font-weight: 600;
}

.btn.ghost:hover {
  background: rgba(91, 124, 230, 0.16);
  border-color: rgba(91, 124, 230, 0.4);
  box-shadow: 0 10px 25px rgba(91, 124, 230, 0.15);
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

.clause-empty {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 96px;
  border-radius: 16px;
  border: 1px dashed var(--border-soft);
  background: rgba(91, 124, 230, 0.06);
  color: var(--text-muted);
  font-size: 13px;
  text-align: center;
  padding: 16px;
}

.clause-empty--error {
  border-color: rgba(226, 77, 77, 0.4);
  background: rgba(226, 77, 77, 0.08);
  color: #b91c1c;
}

.clause-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.clause-hint {
  margin: 0 0 12px;
  font-size: 12px;
  color: rgba(22, 33, 62, 0.68);
}

.clause-pill {
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid rgba(91, 124, 230, 0.16);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.92);
  padding: 14px 16px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  text-align: left;
  overflow: hidden;
}

.clause-pill:hover {
  transform: translateX(4px);
  border-color: rgba(91, 124, 230, 0.3);
  background: rgba(91, 124, 230, 0.05);
  box-shadow: 0 12px 30px rgba(91, 124, 230, 0.12);
}

.clause-pill:active {
  transform: translateY(0) scale(0.98);
}

.clause-pill__text {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.clause-pill__headline {
  display: flex;
  align-items: center;
  gap: 8px;
}

.clause-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-strong);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.clause-badge {
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(91, 124, 230, 0.16);
  color: var(--primary-strong);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-weight: 600;
}

.clause-desc {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.clause-meta {
  font-size: 11px;
  color: rgba(22, 33, 62, 0.6);
}

.clause-pill__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  flex-shrink: 0;
  height: 32px;
  border-radius: 12px;
  border: 1px solid rgba(91, 124, 230, 0.2);
  background: rgba(91, 124, 230, 0.1);
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

.templates-empty--error {
  border-radius: 24px;
  border: 1px solid rgba(226, 77, 77, 0.3);
  background: rgba(226, 77, 77, 0.08);
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
  border: 1px solid rgba(91, 124, 230, 0.12);
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
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.template-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  flex-wrap: wrap;
}

.template-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-strong);
  line-height: 1.3;
  flex: 1 1 auto;
  min-width: 0;
  word-wrap: break-word;
}

.template-chip {
  background: rgba(91, 124, 230, 0.12);
  color: var(--primary-strong);
  border: 1px solid rgba(91, 124, 230, 0.22);
  border-radius: 999px;
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease;
}

.template-chip:hover {
  background: rgba(91, 124, 230, 0.2);
}

.template-description {
  font-size: 12px;
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
  max-width: 100%;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  border: 1px solid rgba(91, 124, 230, 0.25);
  background: rgba(91, 124, 230, 0.1);
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
  padding-top: 8px;
}

.template-actions {
  display: inline-flex;
  gap: 10px;
  flex-wrap: wrap;
}

.icon-button {
  width: 34px;
  height: 34px;
  border-radius: 12px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.18s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.icon-button:hover {
  background: rgba(91, 124, 230, 0.08);
  border-color: transparent;
  color: var(--primary-strong);
  transform: translateY(-1px);
}

.icon-button:active {
  background: rgba(91, 124, 230, 0.14);
  border-color: rgba(91, 124, 230, 0.3);
  color: var(--primary-strong);
  transform: translateY(0);
}

.icon-button svg {
  width: 16px;
  height: 16px;
}

.icon-button.danger {
  border-color: transparent;
  color: var(--text-muted);
}

.icon-button.danger:hover {
  background: rgba(226, 77, 77, 0.08);
  border-color: transparent;
  color: #b93838;
}

.icon-button.danger:active {
  background: rgba(226, 77, 77, 0.14);
  border-color: rgba(226, 77, 77, 0.3);
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
  gap: 12px;
  border-radius: 18px;
  border: 1px solid rgba(91, 124, 230, 0.14);
  padding: 16px;
  background: rgba(249, 250, 255, 0.9);
  overflow: hidden;
}

.recommend-card__body {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.recommend-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-strong);
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.4;
}

.recommend-note {
  font-size: 12px;
  color: var(--text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  background: rgba(91, 124, 230, 0.16);
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
  white-space: nowrap;
  flex-shrink: 0;
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
  padding: 12px 16px;
  border-radius: 16px;
  border: 1px solid rgba(91, 124, 230, 0.12);
  background: rgba(91, 124, 230, 0.08);
  overflow: hidden;
}

.metric-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: rgba(22, 33, 62, 0.68);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  min-width: 0;
}

.metric-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-strong);
  white-space: nowrap;
  flex-shrink: 0;
  margin-left: 8px;
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
  width: min(840px, 100%);
  max-width: 840px;
  min-width: min(640px, 100%);
  border-radius: 28px;
  background: var(--surface);
  border: 1px solid rgba(36, 51, 83, 0.12);
  box-shadow: var(--shadow-soft);
  overflow: hidden;
  animation: modalSlideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes modalSlideUp {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 28px;
  border-bottom: 1px solid rgba(91, 124, 230, 0.12);
  background: linear-gradient(135deg, rgba(91, 124, 230, 0.05), rgba(91, 124, 230, 0.02));
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-strong);
  display: flex;
  align-items: center;
  gap: 12px;
}

.modal-body {
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-height: calc(90vh - 200px);
  overflow-y: auto;
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
  border-color: rgba(91, 124, 230, 0.5);
  box-shadow: 0 0 0 4px rgba(91, 124, 230, 0.14);
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
    padding: 10px 14px;
  }

  .search-input {
    font-size: 16px;
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
    gap: 18px;
  }

  .template-card {
    padding: 20px;
  }

  .panel-heading {
    flex-direction: column;
    align-items: flex-start;
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

  .modal-backdrop {
    padding: 0;
    align-items: flex-end;
  }

  .modal-shell {
    width: 100%;
    max-width: 100%;
    min-width: 100%;
    border-radius: 24px 24px 0 0;
    max-height: 92vh;
    overflow: hidden;
  }

  .modal-header,
  .modal-body {
    padding: 24px;
  }

  .modal-body {
    max-height: calc(92vh - 184px);
  }
}

/* Keyboard navigation focus rings */
.btn:focus-visible,
.icon-button:focus-visible,
.clause-pill:focus-visible {
  outline: 2px solid #5b7ce6;
  outline-offset: 2px;
}

.field-input:focus-visible,
.field-textarea:focus-visible {
  outline: none;
}

/* Respect user motion preferences */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Override to match Overview page */
.sidebar-link.active {
  background-color: #eff6ff !important;
  color: #5b7ce6 !important;
  box-shadow: none !important;
  transform: none !important;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.97);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
</style>
