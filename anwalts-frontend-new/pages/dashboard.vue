<template>
  <PortalShell>
    <template #header>
        <header class="page-header">
          <div class="header-content">
            <div class="flex-1">
              <div class="global-search" aria-label="Globale Suche">
                <input id="globalSearch" type="search" placeholder="Suche..." class="search-input" aria-label="Suche" />
                <div class="quick-filters" aria-label="Schnellfilter">
                  <button class="filter-chip" data-chip="dokumente" title="Zu Dokumente wechseln (g d)">Dokumente</button>
                  <button class="filter-chip" data-chip="emails" title="Zu E‑Mails wechseln (g e)">E‑Mails</button>
                  <button class="filter-chip" data-chip="vorlagen" title="Zu Vorlagen wechseln (g v)">Vorlagen</button>
                </div>
              </div>
            </div>

            <div class="header-actions">
              <button class="icon-button" aria-label="Benachrichtigungen öffnen" title="Benachrichtigungen">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
                </svg>
              </button>
              <button id="btnNewDoc" class="btn btn-primary" aria-label="Neues Dokument erstellen" title="Neues Dokument (n)">Neues Dokument</button>
              <button id="btnLogout" class="btn btn-secondary" title="Abmelden">Abmelden</button>
            </div>
          </div>
        </header>
    </template>

    <div class="main-content">
          <!-- Continue Bar -->
          <div v-if="continueSuggestion" id="continueBar" class="continue-bar" role="region" aria-live="polite">
            <div class="continue-text">
              <span class="font-medium">Weiter mit:</span>
              <span>
                {{ continueSuggestion.title }} ({{ continueSuggestion.progress }}%)
                <template v-if="continueSuggestion.deadline">
                  · Frist {{ getRelativeDateLabel(continueSuggestion.deadline) }}
                </template>
              </span>
            </div>
            <div class="continue-actions">
              <button id="btnContinueOpen" class="btn btn-secondary" data-action="open-doc" aria-label="Dokument öffnen">Öffnen</button>
              <button id="btnContinueClose" class="icon-button" aria-label="Leiste schließen" title="Schließen">✕</button>
            </div>
          </div>

          <!-- Page Title -->
          <div class="page-title">
            <div>
              <h2 class="h2">Übersicht</h2>
              <p class="subtitle">Willkommen zurück{{ userName ? ', ' + userName : '' }}</p>
            </div>
            <button id="btnStartTour" class="btn-link" aria-label="Kurze Tour starten">Kurze Tour starten</button>
          </div>

          <!-- Stats Grid -->
          <div class="stats-grid">
            <div class="stat-card">
              <div class="flex items-center justify-between mb-3">
                <div class="stat-icon">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 01-2 2z"></path>
                  </svg>
                </div>
              </div>
              <div class="text-2xl font-semibold">{{ stats?.newCases ?? 0 }}</div>
              <div class="text-sm text-gray-500 mt-1">Neue Fälle</div>
            </div>

            <div class="stat-card">
              <div class="flex items-center justify-between mb-3">
                <div class="stat-icon">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                </div>
                <span v-if="stats?.documents && stats.documents > 0" class="badge badge-primary" title="Aktiv im Bearbeitungsprozess">Aktiv</span>
              </div>
              <div class="text-2xl font-semibold">{{ stats?.documents ?? 0 }}</div>
              <div class="text-sm text-gray-500 mt-1">Dokumente</div>
            </div>

            <div class="stat-card">
              <div class="flex items-center justify-between mb-3">
                <div class="stat-icon">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                  </svg>
                </div>
              </div>
              <div class="text-2xl font-semibold">{{ stats?.emails ?? 0 }}</div>
              <div class="text-sm text-gray-500 mt-1">E‑Mails</div>
            </div>

            <div class="stat-card" id="nextDeadlineCard">
              <div class="flex items-center justify-between mb-3">
                <div class="stat-icon">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                <span v-if="stats?.nextDeadline" class="badge badge-warning" :title="getRelativeDateLabel(stats.nextDeadline)">{{ getRelativeDateLabel(stats.nextDeadline) }}</span>
              </div>
              <div v-if="stats?.nextDeadline" class="text-2xl font-semibold">
                {{ new Date(stats.nextDeadline).toLocaleDateString('de-DE', { day: '2-digit', month: 'short' }) }}
                <span class="text-sm text-gray-500">({{ getRelativeDateLabel(stats.nextDeadline) }})</span>
              </div>
              <div v-else class="text-2xl font-semibold">—</div>
              <div class="text-sm text-gray-500 mt-1">Nächste Frist</div>
            </div>
          </div>

          <!-- Content Grid -->
          <div class="content-grid">
            <!-- Recent Documents -->
            <div class="main-column section-card" aria-label="Aktuelle Dokumente" id="recentDocs">
              <div class="section-header">
                <h3 class="h3">Aktuelle Dokumente</h3>
                <button
                  class="btn btn-secondary"
                  type="button"
                  aria-label="Alle Dokumente anzeigen"
                  title="Alle Dokumente anzeigen"
                  @click="openDocumentsOverlay"
                >
                  Alle anzeigen
                </button>
              </div>

              <!-- Skeleton -->
              <div id="docsSkeleton" class="space-y-4 hidden">
                <div class="skeleton-item"></div>
                <div class="skeleton-item"></div>
                <div class="skeleton-item"></div>
              </div>

              <div id="docsList" class="space-y-4">
                <div v-for="(d, idx) in documents" :key="d.id">
                  <div class="document-list-item">
                    <div class="flex items-center gap-3">
                      <div class="stat-icon" aria-hidden="true">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                      </div>
                      <div>
                        <p class="font-medium">{{ d.title }}</p>
                        <p class="text-sm text-gray-500">{{ formatRelativeTime(d.updated_at) }}</p>
                      </div>
                    </div>
                    <div class="flex items-center gap-3">
                      <button
                        class="btn-link toggle-details"
                        type="button"
                        :aria-expanded="isDocumentExpanded(d.id)"
                        @click="toggleDocumentDetail(d.id)"
                      >
                        {{ isDocumentExpanded(d.id) ? 'Details verbergen' : 'Details' }}
                      </button>
                      <template v-if="d.statusType === 'progress'">
                        <div class="flex items-center gap-2">
                          <span class="badge badge-primary" :title="'Fortschritt'">{{ d.progress }}%</span>
                          <div class="w-24 h-1.5 bg-gray-200 rounded-full overflow-hidden"><div class="bg-primary-600 h-full" :style="{ width: d.progress + '%' }"></div></div>
                        </div>
                      </template>
                      <template v-else-if="d.statusType === 'final'">
                        <span class="badge badge-success" title="Finalisiert">Final</span>
                      </template>
                      <template v-else>
                        <span class="badge badge-warning" title="Zur Prüfung">Prüfung</span>
                      </template>
                    </div>
                  </div>
                  <div v-if="d.details && isDocumentExpanded(d.id)" class="document-details">
                    {{ d.details }}
                  </div>
                </div>

                <!-- Empty state -->
                <div v-if="!isLoading && documents && documents.length === 0" id="docsEmpty" class="p-8 text-center">
                  <p class="mb-3">Noch keine Dokumente</p>
                  <button class="btn btn-primary" data-action="create-doc">Neues Dokument</button>
                </div>
              </div>
            </div>

            <!-- Deadlines -->
            <div class="section-card" aria-label="Fristen" id="deadlines">
              <div class="section-header">
                <h3 class="h3">Fristen</h3>
                <button class="btn-link" aria-label="Alle Fristen anzeigen">Alle</button>
              </div>

              <div id="deadlineList" class="space-y-4">
                <div v-for="deadline in deadlines" :key="deadline.id" class="deadlines-list-item" :class="getDeadlineBorderColor(deadline.due_date)">
                  <p class="font-medium">{{ deadline.title }}</p>
                  <p class="text-sm text-gray-500">{{ deadline.description }}</p>
                  <span class="badge mt-2" :class="getDeadlineBadgeClass(deadline.due_date)" :title="getRelativeDateLabel(deadline.due_date)">
                    {{ getRelativeDateLabel(deadline.due_date) }}
                  </span>
                </div>

                <!-- Empty state -->
                <div v-if="!isLoading && deadlines && deadlines.length === 0" class="p-8 text-center">
                  <p>Keine anstehenden Fristen</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Templates Section -->
          <div id="templates" class="section-card mt-6" aria-label="Vorlagen">
            <div class="section-header">
              <h3 class="h3">Vorlagen</h3>
              <div class="flex items-center gap-2">
                <input type="text" class="search-input" placeholder="Vorlage suchen…" aria-label="Vorlagen durchsuchen" />
                <button class="btn btn-secondary">Neue Vorlage</button>
              </div>
            </div>

            <!-- Loading state -->
            <div v-if="isLoadingTemplates" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              <div v-for="i in 6" :key="i" class="skeleton-item"></div>
            </div>

            <!-- Dynamic templates from API -->
            <div v-else-if="templates && templates.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              <div v-for="template in templates.slice(0, 6)" :key="template.id" class="template-card">
                <div class="flex items-start justify-between">
                  <div>
                    <p class="font-medium">{{ template.title || template.name }}</p>
                    <p class="text-xs text-gray-500 mt-1">
                      Letztes Update: {{ formatDate(template.updated_at || template.created_at) }}
                      <template v-if="template.version"> · Version {{ template.version }}</template>
                      <template v-if="template.status === 'published'"> · Freigegeben</template>
                    </p>
                  </div>
                  <span class="badge badge-primary" :title="template.category || 'Kategorie'">
                    {{ template.category || 'Allgemein' }}
                  </span>
                </div>
                <div class="mt-4 flex items-center gap-2">
                  <button 
                    class="btn btn-primary" 
                    @click="useTemplate(template)"
                    :aria-label="`${template.title || template.name}-Vorlage erstellen`">
                    Erstellen
                  </button>
                  <button class="btn btn-secondary" @click="navigateTo(`/templates`)">
                    Ansehen
                  </button>
                </div>
              </div>
            </div>

            <!-- Fallback: Static templates if API fails or returns empty -->
            <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              <div class="template-card">
                <div class="flex items-start justify-between">
                  <div>
                    <p class="font-medium">NDA – Standard (DE)</p>
                    <p class="text-xs text-gray-500 mt-1">Letztes Update: 12. Aug 2025 · Freigegeben</p>
                  </div>
                  <span class="badge badge-primary" title="Kategorie">Vertrag</span>
                </div>
                <div class="mt-4 flex items-center gap-2">
                  <button class="btn btn-primary" aria-label="NDA-Vorlage erstellen" data-template="nda">Erstellen</button>
                  <button class="btn btn-secondary">Ansehen</button>
                </div>
              </div>

              <div class="template-card">
                <div class="flex items-start justify-between">
                  <div>
                    <p class="font-medium">Klageentwurf – Zivil</p>
                    <p class="text-xs text-gray-500 mt-1">Letztes Update: 30. Jul 2025 · Version 7</p>
                  </div>
                  <span class="badge badge-primary">Zivil</span>
                </div>
                <div class="mt-4 flex items-center gap-2">
                  <button class="btn btn-primary" data-template="klage-zivil">Erstellen</button>
                  <button class="btn btn-secondary">Ansehen</button>
                </div>
              </div>

              <div class="template-card">
                <div class="flex items-start justify-between">
                  <div>
                    <p class="font-medium">Vergleichsangebot</p>
                    <p class="text-xs text-gray-500 mt-1">Letztes Update: 04. Aug 2025 · Freigegeben</p>
                  </div>
                  <span class="badge badge-primary">Zivil</span>
                </div>
                <div class="mt-4 flex items-center gap-2">
                  <button class="btn btn-primary" data-template="vergleich">Erstellen</button>
                  <button class="btn btn-secondary">Ansehen</button>
                </div>
              </div>

              <div class="template-card">
                <div class="flex items-start justify-between">
                  <div>
                    <p class="font-medium">Abmahnung – UWG</p>
                    <p class="text-xs text-gray-500 mt-1">Letztes Update: 18. Jun 2025 · Version 3</p>
                  </div>
                  <span class="badge badge-primary">Wettbewerb</span>
                </div>
                <div class="mt-4 flex items-center gap-2">
                  <button class="btn btn-primary" data-template="abmahnung">Erstellen</button>
                  <button class="btn btn-secondary">Ansehen</button>
                </div>
              </div>

              <div class="template-card">
                <div class="flex items-start justify-between">
                  <div>
                    <p class="font-medium">Vollmacht – Mandanten</p>
                    <p class="text-xs text-gray-500 mt-1">Letztes Update: 10. Aug 2025</p>
                  </div>
                  <span class="badge badge-primary">Allgemein</span>
                </div>
                <div class="mt-4 flex items-center gap-2">
                  <button class="btn btn-primary" data-template="vollmacht">Erstellen</button>
                  <button class="btn btn-secondary">Ansehen</button>
                </div>
              </div>

              <div class="template-card">
                <div class="flex items-start justify-between">
                  <div>
                    <p class="font-medium">DSGVO – Auskunftsersuchen</p>
                    <p class="text-xs text-gray-500 mt-1">Letztes Update: 05. Aug 2025</p>
                  </div>
                  <span class="badge badge-primary">Datenschutz</span>
                </div>
                <div class="mt-4 flex items-center gap-2">
                  <button class="btn btn-primary" data-template="dsgvo-auskunft">Erstellen</button>
                  <button class="btn btn-secondary">Ansehen</button>
                </div>
              </div>
            </div>
          </div>

          <!-- "Neue Eingänge" section removed 2025-11-03 - displayed hardcoded test data with no value -->

    </div>

    <!-- Documents Overlay -->
    <div
      v-if="showDocumentOverlay"
      class="docs-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="documentsOverlayTitle"
      @click.self="closeDocumentsOverlay"
    >
      <div
        class="docs-overlay-panel"
        ref="documentsOverlayRef"
        tabindex="-1"
      >
        <div class="docs-overlay-header">
          <div>
            <h3 id="documentsOverlayTitle" class="docs-overlay-title">Alle Dokumente</h3>
            <p class="docs-overlay-subtitle">Übersicht über alle zuletzt erzeugten oder bearbeiteten Dokumente</p>
          </div>
          <button
            type="button"
            class="icon-button docs-overlay-close"
            aria-label="Dokumentenübersicht schließen"
            @click="closeDocumentsOverlay"
          >
            <svg class="w-5 h-5" viewBox="0 0 20 20" fill="none" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 6l8 8M6 14L14 6" />
            </svg>
          </button>
        </div>

        <div class="docs-overlay-body">
          <div v-if="allDocuments.length === 0" class="docs-overlay-empty">
            <p>Noch keine Dokumente vorhanden.</p>
          </div>
          <ul v-else class="docs-overlay-list">
            <li v-for="doc in allDocuments" :key="doc.id" class="docs-overlay-item">
              <div class="docs-overlay-item-header">
                <div>
                  <p class="docs-overlay-item-title">{{ doc.title || 'Unbenanntes Dokument' }}</p>
                  <p class="docs-overlay-item-meta">
                    {{ formatRelativeTime(doc.updated_at) }}
                    <template v-if="doc.status"> · {{ doc.status }}</template>
                  </p>
                </div>
                <span
                  v-if="doc.statusType === 'progress'"
                  class="badge badge-primary"
                  aria-label="Dokument in Bearbeitung"
                >
                  {{ doc.progress }}%
                </span>
                <span
                  v-else-if="doc.statusType === 'final'"
                  class="badge badge-success"
                  aria-label="Dokument abgeschlossen"
                >
                  Final
                </span>
                <span
                  v-else-if="doc.statusType === 'review'"
                  class="badge badge-warning"
                  aria-label="Dokument in Prüfung"
                >
                  Prüfung
                </span>
              </div>
              <div v-if="doc.details" class="docs-overlay-item-actions">
                <button
                  type="button"
                  class="btn-link docs-overlay-details"
                  @click.stop="toggleOverlayDetails(doc.id)"
                  :aria-expanded="isOverlayExpanded(doc.id)"
                >
                  {{ isOverlayExpanded(doc.id) ? 'Details verbergen' : 'Details anzeigen' }}
                </button>
              </div>
              <p
                v-if="doc.details && isOverlayExpanded(doc.id)"
                class="docs-overlay-item-details"
              >
                {{ doc.details }}
              </p>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div id="toast" class="toast hidden"></div>

    <!-- Tour Elements -->
    <div id="tourOverlay" class="modal-overlay hidden"></div>
    <div id="tourStep" class="modal hidden">
      <div class="modal-arrow"></div>
      <div id="tourContent" class="modal-body"></div>
      <div class="modal-footer">
        <div class="flex items-center gap-2">
          <button id="tourPrev" class="btn btn-secondary">Zurück</button>
          <button id="tourNext" class="btn btn-primary">Weiter</button>
        </div>
        <button id="tourClose" class="btn-link">Schließen</button>
      </div>
      <button id="tourNever" class="text-xs text-gray-500 underline mt-2">Nicht mehr zeigen</button>
    </div>

  </PortalShell>
</template>

<style scoped>
.page-header {
  background-color: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 1rem 2rem;
}
.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.global-search {
  position: relative;
  max-width: 28rem;
}
.search-input {
  width: 100%;
  padding: 0.5rem 1rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background-color: var(--surface-input);
  color: var(--text-strong);
  height: 2.75rem;
}
.search-input:focus {
  outline: none;
  border-color: var(--primary-strong);
  box-shadow: 0 0 0 2px var(--primary-focus-ring);
}
.quick-filters {
  margin-top: 0.75rem;
  display: flex;
  gap: 0.5rem;
}
.filter-chip {
  padding: 0.25rem 0.75rem;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-strong);
  background-color: var(--surface);
  border: 1px solid var(--border);
  border-radius: 9999px;
  cursor: pointer;
  transition: background-color 0.2s;
}
.filter-chip:hover {
  background-color: var(--surface-hover);
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.icon-button {
  padding: 0.5rem;
  border-radius: var(--radius-lg);
  color: var(--text-strong);
}
.icon-button:hover {
  background-color: var(--surface-hover);
}
.main-content {
  padding: 2rem;
}
.continue-bar {
  background-color: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}
.continue-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: var(--text-sm);
  color: var(--text-strong);
}
.continue-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.page-title {
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}
@media (min-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (min-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
.stat-card {
  background-color: var(--surface);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  box-shadow: var(--shadow-sm);
}
.stat-icon {
  width: 2.5rem;
  height: 2.5rem;
  background-color: var(--primary-100);
  color: var(--primary-600);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
}
.content-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 1.5rem;
}
@media (min-width: 1024px) {
  .content-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
.main-column {
  grid-column: span 1 / span 1;
}
@media (min-width: 1024px) {
  .main-column {
    grid-column: span 2 / span 2;
  }
}
.section-card {
  background-color: var(--surface);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
}
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}
.skeleton-item {
  padding: 1rem;
  background-color: var(--surface-muted);
  border-radius: var(--radius-lg);
  height: 4rem;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
.document-list-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background-color: var(--surface-muted);
  border-radius: var(--radius-lg);
}
.document-details {
  padding: 1rem;
  padding-top: 0;
  font-size: var(--text-sm);
  color: var(--text-strong);
}
.deadlines-list-item {
  border-left-width: 4px;
  padding-left: 1rem;
}
.template-card {
  padding: 1rem;
  border-radius: var(--radius-lg);
  background-color: var(--surface-muted);
}
.activity-table {
  width: 100%;
}
.activity-table th, .activity-table td {
  padding: 0.75rem 1rem;
  text-align: left;
}
.activity-table th {
  border-bottom: 1px solid var(--border);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-strong);
}
.activity-table tbody tr {
  border-bottom: 1px solid var(--border-muted);
}

.docs-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1.5rem;
  z-index: 70;
}
.docs-overlay-panel {
  width: min(720px, 92vw);
  max-height: min(80vh, 720px);
  background-color: var(--surface);
  border-radius: 1.25rem;
  box-shadow: 0 24px 48px rgba(15, 23, 42, 0.25);
  display: flex;
  flex-direction: column;
  outline: none;
}
.docs-overlay-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 1.5rem 1.75rem 1rem;
  gap: 1rem;
  border-bottom: 1px solid var(--border);
}
.docs-overlay-title {
  font-size: clamp(1.125rem, 1.8vw, 1.4rem);
  font-weight: var(--font-semibold);
  color: var(--text-strong);
}
.docs-overlay-subtitle {
  margin-top: 0.25rem;
  font-size: var(--text-sm);
  color: var(--text-medium);
}
.docs-overlay-close {
  border: 1px solid transparent;
}
.docs-overlay-close:hover {
  background-color: var(--surface-hover);
}
.docs-overlay-body {
  padding: 1.5rem 1.75rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.docs-overlay-empty {
  text-align: center;
  color: var(--text-medium);
  padding: 3rem 1.5rem;
  border: 1px dashed var(--border-muted, rgba(148, 163, 184, 0.45));
  border-radius: var(--radius-lg);
  background: var(--surface-muted);
}
.docs-overlay-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.docs-overlay-item {
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.125rem 1.25rem;
  background: var(--surface-muted);
  display: grid;
  gap: 0.75rem;
}
.docs-overlay-item-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}
.docs-overlay-item-title {
  font-weight: var(--font-medium);
  color: var(--text-strong);
  margin-bottom: 0.25rem;
}
.docs-overlay-item-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}
.docs-overlay-details {
  font-size: var(--text-sm);
}
.docs-overlay-details:hover {
  text-decoration: underline;
}
.docs-overlay-item-meta {
  font-size: var(--text-sm);
  color: var(--text-medium);
}
.docs-overlay-item-details {
  font-size: var(--text-sm);
  color: var(--text-strong);
  line-height: 1.45;
}

@media (max-width: 640px) {
  .docs-overlay {
    padding: 1rem;
  }
  .docs-overlay-panel {
    width: 100%;
    max-height: 90vh;
    border-radius: 1rem;
  }
  .docs-overlay-header {
    padding: 1.25rem 1.25rem 0.75rem;
  }
  .docs-overlay-body {
    padding: 1.25rem;
  }
}
</style>

<script setup>
import { onMounted, onBeforeUnmount, ref, computed, watch, nextTick, reactive } from 'vue'
import PortalShell from '~/components/PortalShell.vue'
import { usePortalUser } from '~/composables/usePortalUser'
import { useDashboardStore } from '~/stores/dashboard'

definePageMeta({ 
  layout: false,
  middleware: ['auth-guard']
})

const { user: currentUser, loadUser, hasStoredAuthEvidence } = usePortalUser()
const dashboardStore = useDashboardStore()

// Computed properties for dashboard data
const stats = computed(() => dashboardStore.stats)
const documents = computed(() => dashboardStore.documents)
const deadlines = computed(() => dashboardStore.deadlines)
const activities = computed(() => dashboardStore.activity)
const continueSuggestion = computed(() => dashboardStore.continueSuggestion)
const userName = computed(() => dashboardStore.userName || currentUser.value?.name || 'Benutzer')
const isLoading = computed(() => dashboardStore.isLoading)

// Templates data
const templates = ref([])
const isLoadingTemplates = ref(false)

// Documents overlay state
const showDocumentOverlay = ref(false)
const documentsOverlayRef = ref(null)
const allDocuments = computed(() => Array.isArray(documents.value) ? documents.value : [])
const expandedDocuments = reactive({})
const overlayExpanded = reactive({})
let previousFocusElement = null
let previousBodyOverflow = ''

function openDocumentsOverlay() {
  if (typeof document !== 'undefined') {
    previousFocusElement = document.activeElement
  }
  showDocumentOverlay.value = true
}

function closeDocumentsOverlay() {
  showDocumentOverlay.value = false
}

function toggleOverlayDetails(id) {
  const key = String(id ?? '')
  if (!key) return
  overlayExpanded[key] = !overlayExpanded[key]
}

function isOverlayExpanded(id) {
  const key = String(id ?? '')
  return Boolean(overlayExpanded[key])
}

function toggleDocumentDetail(id) {
  const key = String(id ?? '')
  if (!key) return
  expandedDocuments[key] = !expandedDocuments[key]
}

function isDocumentExpanded(id) {
  const key = String(id ?? '')
  return Boolean(expandedDocuments[key])
}

watch(showDocumentOverlay, (visible) => {
  if (typeof document === 'undefined') return
  if (visible) {
    previousBodyOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    nextTick(() => {
      documentsOverlayRef.value?.focus?.()
    })
  } else {
    document.body.style.overflow = previousBodyOverflow || ''
    if (previousFocusElement && typeof previousFocusElement.focus === 'function') {
      previousFocusElement.focus()
    }
    previousFocusElement = null
    Object.keys(overlayExpanded).forEach((key) => {
      delete overlayExpanded[key]
    })
  }
})

// Helper functions for date formatting
function getRelativeDateLabel(dateStr) {
  if (!dateStr) return ''
  
  const date = new Date(dateStr)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)
  
  const targetDate = new Date(date)
  targetDate.setHours(0, 0, 0, 0)
  
  const diffTime = targetDate.getTime() - today.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return 'Heute'
  if (diffDays === 1) return 'Morgen'
  if (diffDays > 1 && diffDays <= 7) return `in ${diffDays} Tagen`
  return `in ${diffDays} Tagen`
}

function formatRelativeTime(dateStr) {
  if (!dateStr) return ''
  
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffMins < 1) return 'gerade eben'
  if (diffMins < 60) return `vor ${diffMins} Minute${diffMins !== 1 ? 'n' : ''}`
  if (diffHours < 24) return `vor ${diffHours} Stunde${diffHours !== 1 ? 'n' : ''}`
  if (diffDays === 1) return 'gestern'
  if (diffDays < 7) return `vor ${diffDays} Tagen`
  return date.toLocaleDateString('de-DE', { day: '2-digit', month: 'short' })
}

function getDeadlineBorderColor(dateStr) {
  const label = getRelativeDateLabel(dateStr)
  if (label === 'Heute') return 'border-red-500'
  if (label === 'Morgen') return 'border-orange-500'
  return 'border-green-500'
}

function getDeadlineBadgeClass(dateStr) {
  const label = getRelativeDateLabel(dateStr)
  if (label === 'Heute') return 'text-red-700 bg-red-100'
  if (label === 'Morgen') return 'text-yellow-700 bg-yellow-100'
  return 'text-green-700 bg-green-100'
}

// Format date for template display (German format)
function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('de-DE', { 
    day: '2-digit', 
    month: 'short',
    year: 'numeric'
  })
}

// Fetch templates from API
async function fetchTemplates() {
  try {
    isLoadingTemplates.value = true
    const response = await fetch('/api/templates', {
      headers: getAuthHeader()
    })
    if (response.ok) {
      const data = await response.json()
      templates.value = data.templates || data || []
      console.log('✅ Loaded templates:', templates.value.length)
    } else {
      console.warn('Templates API returned non-OK status:', response.status)
      // Keep templates empty - will show static fallback
    }
  } catch (err) {
    console.error('Failed to load templates:', err)
    // Keep templates empty - will show static fallback
  } finally {
    isLoadingTemplates.value = false
  }
}

// Use template (navigate to documents page with template pre-filled)
function useTemplate(template) {
  try {
    const payload = {
      id: template.id,
      name: template.name || template.title,
      content: template.content,
      category: template.category,
      tags: template.tags || []
    }
    localStorage.setItem('anwalt.templateSelection', JSON.stringify(payload))
    if (payload.id) localStorage.setItem('anwalt.templateId', String(payload.id))
  } catch (_) {}

  const idParam = encodeURIComponent(template.id || template.name)
  navigateTo(`/documents${idParam ? `?templateId=${idParam}` : ''}`)
}

// Inject Tailwind CDN for this page to match the provided design

onMounted(() => {
  (async () => {
    await loadUser()

    if (!currentUser.value) {
      if (hasStoredAuthEvidence()) {
        console.info('Auth evidence present, skipping modal auto-open')
        return
      }
      if (typeof window.openAuthModal === 'function') {
        window.openAuthModal('login')
      } else {
        window.location.replace('/')
      }
      return
    }

    // Fetch dashboard data
    try {
      await dashboardStore.fetchSummary()
    } catch (err) {
      console.error('Failed to load dashboard data:', err)
      // Continue - dashboard will show empty states
    }

    // Fetch templates
    try {
      await fetchTemplates()
    } catch (err) {
      console.error('Failed to load templates:', err)
      // Continue - dashboard will show static fallback templates
    }
  })();
  // Utilities
  const $ = (sel, root = document) => root.querySelector(sel)
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel))
  let toastTimer = null

  // Auth helpers
  function getAuthHeader() {
    try {
      let token = localStorage.getItem('auth_token') || localStorage.getItem('anwalts_auth_token') || localStorage.getItem('access_token') || localStorage.getItem('token') || localStorage.getItem('sat')
      if (!token && document && document.cookie) {
        const map = Object.fromEntries(document.cookie.split(';').map(s => s.trim().split('=')))
        token = map['auth_token'] || map['anwalts_auth_token'] || map['access_token'] || map['token'] || map['sat']
      }
      return token ? { Authorization: `Bearer ${decodeURIComponent(token)}` } : {}
    } catch (_) { return {} }
  }
  function clearAuth() {
    try {
      localStorage.removeItem('auth_token'); localStorage.removeItem('anwalts_auth_token'); localStorage.removeItem('access_token'); localStorage.removeItem('token'); localStorage.removeItem('sat')
      document.cookie = 'access_token=; Max-Age=0; Path=/; Secure; SameSite=Lax'
      document.cookie = 'token=; Max-Age=0; Path=/; Secure; SameSite=Lax'
      document.cookie = 'sat=; Max-Age=0; Path=/; Secure; SameSite=Lax'
      document.cookie = 'auth_token=; Max-Age=0; Path=/; Secure; SameSite=Lax'
    } catch (_) {}
  }

  console.log('✅ Stack Auth session verified for dashboard')

  // Metrics
  const metrics = { loadTs: performance.now(), firstActionTs: null }
  function markFirstAction() {
    if (!metrics.firstActionTs) {
      metrics.firstActionTs = performance.now()
      console.info('Time-to-first-action (ms):', Math.round(metrics.firstActionTs - metrics.loadTs))
    }
  }

  // Toast
  function showToast(msg) {
    const t = $('#toast')
    if (!t) return
    t.textContent = msg
    t.classList.remove('hidden')
    clearTimeout(toastTimer)
    toastTimer = setTimeout(() => t.classList.add('hidden'), 2500)
  }

  // Keyboard shortcuts
  let gotoArmed = false
  let gotoTimer = null
  window.addEventListener('keydown', (e) => {
    if (showDocumentOverlay.value) {
      if (e.key === 'Escape') {
        e.preventDefault()
        closeDocumentsOverlay()
      }
      return
    }
    const tag = document.activeElement?.tagName?.toLowerCase()
    if (tag === 'input' || tag === 'textarea') return
    if (e.key === 'f') { e.preventDefault(); $('#globalSearch')?.focus(); showToast('Suche fokussiert'); markFirstAction(); return }
    if (e.key === 'n') { e.preventDefault(); $('#btnNewDoc')?.click(); return }
    if (e.key === 'g') { gotoArmed = true; clearTimeout(gotoTimer); gotoTimer = setTimeout(() => gotoArmed = false, 1000); return }
    if (gotoArmed) {
      if (e.key === 'd') {
        e.preventDefault()
        showToast('Gehe zu Dokumente')
        markFirstAction()
        gotoArmed = false
        navigateTo('/documents')
      } else if (e.key === 'e') {
        e.preventDefault()
        showToast('Gehe zu E‑Mails')
        markFirstAction()
        gotoArmed = false
        navigateTo('/email')
      } else if (e.key === 'v') {
        e.preventDefault()
        showToast('Gehe zu Vorlagen')
        markFirstAction()
        gotoArmed = false
        navigateTo('/templates')
      }
    }
  })

  // Chip clicks
  $$('[data-chip]')?.forEach(chip => {
    chip.addEventListener('click', () => {
      const type = chip.getAttribute('data-chip')
      if (type === 'vorlagen') {
        showToast('Gehe zu Vorlagen')
        markFirstAction()
        navigateTo('/templates')
      }
      if (type === 'dokumente') {
        showToast('Gehe zu Dokumente')
        markFirstAction()
        navigateTo('/documents')
      }
      if (type === 'emails') {
        showToast('Gehe zu E‑Mails')
        markFirstAction()
        navigateTo('/email')
      }
    })
  })

  // Sidebar link: Vorlagen scroll
  document.getElementById('linkTemplates')?.addEventListener('click', (e) => {
    e.preventDefault()
    window.location.href = '/templates'
    showToast('Vorlagen geöffnet')
  });

  // Sidebar link: KI-Assistent navigate to /assistant
  document.getElementById('linkAssistant')?.addEventListener('click', (e) => {
    // let native anchor handle, but ensure immediate navigation in SPA context
    e.preventDefault();
    window.location.assign('/assistant');
  })

  // Sidebar active state toggle (client-only visual feedback)
  const setActive = (el) => {
    document.querySelectorAll('.sidebar-link').forEach(a => a.classList.remove('active'))
    el?.classList.add('active')
  }
  // Let anchors navigate; keep visual active state for instant feedback
  document.getElementById('linkOverview')?.addEventListener('click', () => { setActive(document.getElementById('linkOverview')) })
  document.getElementById('linkDocuments')?.addEventListener('click', () => { setActive(document.getElementById('linkDocuments')) })
  document.getElementById('linkEmails')?.addEventListener('click', () => { setActive(document.getElementById('linkEmails')) })
  document.getElementById('linkSettings')?.addEventListener('click', () => { setActive(document.getElementById('linkSettings')) })

  // Continue bar logic (now using dynamic data from store)
  ;(function initContinueBar() {
    const dismissed = localStorage.getItem('continueBarDismissed') === '1'
    const bar = $('#continueBar')
    // Bar visibility now controlled by continueSuggestion data
    if (bar && !dismissed && continueSuggestion.value) { 
      bar.classList.remove('hidden') 
    }
    $('#btnContinueClose')?.addEventListener('click', () => { 
      bar?.classList.add('hidden')
      localStorage.setItem('continueBarDismissed', '1') 
    })
    $('#btnContinueOpen')?.addEventListener('click', () => { 
      markFirstAction()
      const docTitle = continueSuggestion.value?.title || 'Dokument'
      showToast(`Dokument geöffnet: ${docTitle}`)
    })
  })()

  // Sorting now handled by API queries with ORDER BY clauses
  // No need for client-side sorting anymore

  // Skeletons reveal
  window.addEventListener('load', () => {
    setTimeout(() => {
      $('#docsSkeleton')?.classList.add('hidden')
      $('#docsList')?.classList.remove('hidden')
      $('#activitySkeleton')?.classList.add('hidden')
      $('#activityBody')?.classList.remove('hidden')
    }, 600)
  })

  // KI progress removed - no longer hard-coded

  // Details toggles
  // Button actions
  $('#btnNewDoc')?.addEventListener('click', () => { 
    markFirstAction(); 
    window.location.href = '/assistant';  // Navigate to AI assistant for document creation
  })
  $('#btnLogout')?.addEventListener('click', async () => {
    try { await fetch('/auth/logout', { method: 'POST', credentials: 'include', headers: { ...getAuthHeader() } }) } catch (_) {}
    clearAuth(); window.location.replace('/')
  })
  $$('[data-template]')?.forEach(btn => btn.addEventListener('click', () => { 
    markFirstAction();
    const templateId = btn.dataset.template;
    // Store template context and navigate to documents page
    try {
      localStorage.setItem('anwalt.templateId', String(templateId))
    } catch (_) {}
    window.location.href = `/documents?templateId=${encodeURIComponent(templateId)}`;
  }))
  $$('[data-action="create-doc"]')?.forEach(btn => btn.addEventListener('click', () => {
    markFirstAction();
    window.location.href = '/assistant';  // Navigate to assistant for document creation
  }))
  // Dates now calculated dynamically in Vue template - no hard-coded dates
})

onBeforeUnmount(() => {
  if (typeof document !== 'undefined') {
    document.body.style.overflow = previousBodyOverflow || ''
  }
  showDocumentOverlay.value = false
  previousFocusElement = null
  Object.keys(overlayExpanded).forEach((key) => {
    delete overlayExpanded[key]
  })
  Object.keys(expandedDocuments).forEach((key) => {
    delete expandedDocuments[key]
  })
})
</script>
