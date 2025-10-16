<template>
  <PortalShell>
    <template #header>
      <div v-if="currentView === 'inbox'" class="inbox-header">
        <div class="header-left">
          <NuxtLink to="/dashboard" class="back-link">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
            </svg>
          </NuxtLink>
          <div class="header-brand">
            <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
            <h1>E-Mail</h1>
          </div>
        </div>

        <div class="header-center">
          <div class="search-box">
            <svg class="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            <input
              type="text"
              placeholder="E-Mails durchsuchen..."
              v-model="searchQuery"
              class="search-input"
            />
          </div>
        </div>

        <div class="header-right">
          <button @click="syncEmails" class="icon-button" title="Aktualisieren">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
          </button>
          <button @click="showSettings = true" class="icon-button" title="Einstellungen">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
          </button>
          <button @click="composing = true" class="compose-button">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
            </svg>
            <span>Verfassen</span>
          </button>
        </div>
      </div>
    </template>

    <div class="email-app">

      <!-- Consent Screen -->
      <div v-if="currentView === 'consent'" class="consent-screen">
      <NuxtLink
        to="/dashboard"
        class="back-to-dashboard"
        aria-label="Zurück zum Dashboard"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
        </svg>
        <span class="text-sm font-medium">Übersicht</span>
      </NuxtLink>

      <div class="consent-card">
        <div class="consent-header">
          <div class="consent-icon">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
          </div>
          <h1 class="consent-title">E-Mail verbinden</h1>
          <p class="consent-subtitle">Verbinden Sie sicher Ihr professionelles E-Mail-Konto</p>
        </div>

        <div class="oauth-buttons">
          <button
            @click="handleOAuthConnect('gmail')"
            :disabled="!consents.oauth || !consents.aiReading"
            class="oauth-button"
          >
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
              <path fill="#4285f4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34a853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#fbbc05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#ea4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            <span>Weiter mit Gmail</span>
          </button>

          <button
            @click="handleOAuthConnect('outlook')"
            :disabled="!consents.oauth || !consents.aiReading"
            class="oauth-button"
          >
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M11.4 24H0V12.6h11.4V24zM24 24H12.6V12.6H24V24zM11.4 11.4H0V0h11.4v11.4zM24 11.4H12.6V0H24v11.4z"/>
            </svg>
            <span>Weiter mit Outlook / Microsoft 365</span>
          </button>
        </div>

        <div class="consent-checkboxes">
          <label class="consent-checkbox-label">
            <input
              type="checkbox"
              v-model="consents.oauth"
              class="consent-checkbox"
            />
            <span class="consent-checkbox-text">
              Ich stimme zu, meine E-Mail über OAuth 2.0 sichere Authentifizierung zu verbinden
            </span>
          </label>

          <label class="consent-checkbox-label">
            <input
              type="checkbox"
              v-model="consents.aiReading"
              class="consent-checkbox"
            />
            <span class="consent-checkbox-text">
              Ich stimme zu, dass die KI meine E-Mails liest, um Zusammenfassungen vorzuschlagen und Antworten zu entwerfen. Die KI wird niemals ohne meine Überprüfung senden.
            </span>
          </label>
        </div>

        <div class="consent-footer">
          <a href="/privacy" class="consent-link">Datenschutz</a>
          <span class="consent-separator">•</span>
          <a href="/terms" class="consent-link">Datennutzung</a>
          <span class="consent-separator">•</span>
          <a href="#" class="consent-link">Zugriff widerrufen</a>
        </div>

        <div v-if="loading" class="consent-loading">
          <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span class="ml-2">Sichere Verbindung wird hergestellt...</span>
        </div>
      </div>
    </div>

    <!-- Inbox View -->
    <div v-if="currentView === 'inbox'" class="inbox-layout">
      <!-- Email Tabs -->
      <div class="email-tabs">
        <button
          v-for="folder in folders"
          :key="folder.key"
          @click="activeFolder = folder.key"
          :class="['tab-item', { 'tab-item-active': activeFolder === folder.key }]"
        >
          <svg class="tab-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="folder.icon"/>
          </svg>
          <span class="tab-label">{{ folder.label }}</span>
          <span v-if="folder.count > 0" class="tab-count">{{ folder.count }}</span>
        </button>
      </div>

      <!-- Main Content Area -->
      <div class="inbox-body">

        <!-- Email List -->
        <div class="email-list-container">
          <!-- Toolbar -->
          <div class="email-toolbar">
            <div class="toolbar-left">
              <label class="checkbox-all">
                <input type="checkbox" v-model="selectAll" />
              </label>
              <button class="toolbar-button" title="Aktualisieren" @click="syncEmails">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                </svg>
              </button>
              <button class="toolbar-button" title="Archivieren">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"/>
                </svg>
              </button>
              <button class="toolbar-button" title="Löschen">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
              <button class="toolbar-button" title="Als gelesen markieren">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 19v-8.93a2 2 0 01.89-1.664l7-4.666a2 2 0 012.22 0l7 4.666A2 2 0 0121 10.07V19M3 19a2 2 0 002 2h14a2 2 0 002-2M3 19l6.75-4.5M21 19l-6.75-4.5M3 10l6.75 4.5M21 10l-6.75 4.5m0 0l-1.14.76a2 2 0 01-2.22 0l-1.14-.76"/>
                </svg>
              </button>
            </div>

            <div class="toolbar-right">
              <span class="email-count">{{ filteredEmails.length }} E-Mails</span>
              <select class="sort-select" v-model="sortBy">
                <option value="date-desc">Neueste zuerst</option>
                <option value="date-asc">Älteste zuerst</option>
                <option value="sender">Absender</option>
                <option value="subject">Betreff</option>
              </select>
            </div>
          </div>

          <!-- Loading State -->
          <div v-if="loading" class="loading-state">
            <div v-for="i in 5" :key="i" class="email-skeleton"></div>
          </div>

          <!-- Empty State -->
          <div v-else-if="filteredEmails.length === 0" class="empty-state">
            <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
            </svg>
            <p class="empty-text">Keine E-Mails gefunden</p>
            <p class="empty-subtext">Ihr Posteingang ist leer oder alle E-Mails sind gefiltert</p>
          </div>

          <!-- Email List -->
          <div v-else class="email-list">
            <div
              v-for="email in filteredEmails"
              :key="email.id"
              @click="openEmail(email)"
              :class="['email-row', { 'email-unread': email.status === 'Ungelesen', 'email-selected': email.id === selectedEmail?.id }]"
            >
              <div class="email-checkbox">
                <input type="checkbox" :value="email.id" @click.stop />
              </div>

              <div class="email-star" @click.stop="toggleStar(email.id)">
                <svg v-if="email.starred" class="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                </svg>
                <svg v-else class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/>
                </svg>
              </div>

              <div class="email-sender">
                <span class="sender-name">{{ email.sender.name }}</span>
              </div>

              <div class="email-content">
                <div class="email-subject-line">
                  <span class="subject-text">{{ email.subject }}</span>
                  <svg v-if="email.hasAttachment" class="email-attachment-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"/>
                  </svg>
                </div>
                <div class="email-snippet">{{ email.snippet }}</div>
              </div>

              <div class="email-meta">
                <span :class="['status-badge', getStatusClass(email.status)]">
                  {{ email.status }}
                </span>
                <span class="email-date">{{ formatEmailDate(email.date) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Email Detail Modal -->
    <Teleport to="body">
      <div v-if="selectedEmail && !composing" class="email-modal-overlay" @click="closeEmail">
        <div class="email-modal" @click.stop>
          <!-- Modal Header -->
          <div class="modal-header">
            <div class="modal-header-left">
              <button @click="closeEmail" class="modal-back-button">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
                </svg>
              </button>
              <h2 class="modal-title">{{ selectedEmail.subject }}</h2>
            </div>
            <div class="modal-header-right">
              <button class="modal-icon-button" title="Drucken">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/>
                </svg>
              </button>
              <button class="modal-icon-button" title="In neuem Fenster öffnen">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                </svg>
              </button>
              <button @click="closeEmail" class="modal-icon-button" title="Schließen">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Modal Content -->
          <div class="modal-body">
            <!-- Email Header -->
            <div class="email-header">
              <div class="email-header-top">
                <div class="sender-info">
                  <div class="sender-avatar">
                    {{ selectedEmail.sender.initials }}
                  </div>
                  <div class="sender-details">
                    <div class="sender-name-large">{{ selectedEmail.sender.name }}</div>
                    <div class="sender-email-address">&lt;{{ selectedEmail.sender.email }}&gt;</div>
                  </div>
                </div>
                <div class="email-date-large">
                  {{ formatLongDate(selectedEmail.date) }}
                </div>
              </div>

              <div class="email-header-info">
                <div class="header-info-row">
                  <span class="info-label">An:</span>
                  <span class="info-value">Sie</span>
                </div>
                <div v-if="selectedEmail.priority === 'High'" class="priority-badge">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                  </svg>
                  <span>Hohe Priorität</span>
                </div>
              </div>
            </div>

            <!-- Email Body -->
            <div class="email-body-content">
              <div class="email-text">
                <p>{{ selectedEmail.snippet }}</p>
                <p class="mt-4">
                  Diese Angelegenheit erfordert Ihre sofortige Aufmerksamkeit. Die folgenden Punkte müssen bearbeitet werden:
                </p>
                <ul class="email-list-items">
                  <li>Alle vertraglichen Verpflichtungen überprüfen und Einhaltung sicherstellen</li>
                  <li>Notwendige Unterlagen für die Einreichung vorbereiten</li>
                  <li>Mit relevanten Parteien für Unterschriften koordinieren</li>
                  <li>Sicherstellen, dass alle Fristen gemäß Gerichtsanforderungen eingehalten werden</li>
                </ul>
                <p class="mt-4">
                  Bitte beachten Sie, dass Verzögerungen den Fallzeitplan und die Kundenerwartungen beeinflussen können.
                </p>
                <p class="mt-6">
                  Mit freundlichen Grüßen,<br/>
                  <strong>{{ selectedEmail.sender.name }}</strong>
                </p>
              </div>

              <!-- AI Summary -->
              <div v-if="settings.aiReadAccess" class="ai-summary">
                <div class="ai-summary-header">
                  <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
                  </svg>
                  <span>KI-Zusammenfassung</span>
                </div>
                <p class="ai-summary-text">{{ getAISummary(selectedEmail) }}</p>
                <div class="ai-summary-tags">
                  <span class="ai-tag">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    Frist: 3 Tage
                  </span>
                  <span class="ai-tag">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/>
                    </svg>
                    Priorität: {{ selectedEmail.priority }}
                  </span>
                </div>
              </div>

              <!-- Attachments -->
              <div v-if="selectedEmail.hasAttachment" class="email-attachments">
                <div class="attachments-header">Anhänge</div>
                <div class="attachment-item">
                  <div class="attachment-thumbnail">
                    <svg class="attachment-thumbnail-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
                    </svg>
                  </div>
                  <div class="attachment-info">
                    <div class="attachment-name">Vertragsentwurf.pdf</div>
                    <div class="attachment-size">245 KB</div>
                  </div>
                  <button class="attachment-download">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Modal Footer -->
          <div class="modal-footer">
            <button class="footer-button footer-button-primary" @click="replyToEmail">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"/>
              </svg>
              <span>Antworten</span>
            </button>
            <button class="footer-button" @click="forwardEmail">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
              </svg>
              <span>Weiterleiten</span>
            </button>
            <button class="footer-button">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"/>
              </svg>
              <span>Archivieren</span>
            </button>
            <button class="footer-button footer-button-danger">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
              <span>Löschen</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Settings Modal -->
    <Teleport to="body">
      <div v-if="showSettings" class="settings-modal-overlay" @click="showSettings = false">
        <div class="settings-modal" @click.stop>
          <div class="settings-header">
            <h2 class="settings-title">E-Mail Einstellungen</h2>
            <button @click="showSettings = false" class="settings-close">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <div class="settings-body">
            <label class="setting-item">
              <input type="checkbox" v-model="settings.aiReadAccess" class="setting-checkbox" />
              <div class="setting-info">
                <div class="setting-label">KI-Lesezugriff erlauben</div>
                <div class="setting-description">KI kann E-Mails lesen und Zusammenfassungen erstellen</div>
              </div>
            </label>

            <label class="setting-item">
              <input type="checkbox" v-model="settings.draftOnlyMode" class="setting-checkbox" />
              <div class="setting-info">
                <div class="setting-label">Nur-Entwurf-Modus</div>
                <div class="setting-description">KI erstellt nur Entwürfe, sendet niemals automatisch</div>
              </div>
            </label>

            <div class="settings-info-section">
              <div class="info-item">
                <span class="info-item-label">Zustimmungszeitpunkt:</span>
                <span class="info-item-value">{{ settings.consentTimestamp ? formatLongDate(settings.consentTimestamp) : '—' }}</span>
              </div>
              <div class="info-item">
                <span class="info-item-label">Letzte Synchronisation:</span>
                <span class="info-item-value">{{ formatLongDate(lastSyncTime) }}</span>
              </div>
            </div>

            <button @click="handleRevokeAccess" class="revoke-button">
              Zugriff widerrufen
            </button>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
  </PortalShell>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import PortalShell from '~/components/PortalShell.vue'

definePageMeta({ layout: false })

// State
const currentView = ref('consent')
const selectedEmail = ref(null)
const activeFolder = ref('inbox')
const activeLabel = ref(null)
const searchQuery = ref('')
const sortBy = ref('date-desc')
const selectAll = ref(false)
const emails = ref([])
const loading = ref(false)
const showSettings = ref(false)
const composing = ref(false)
const lastSyncTime = ref(new Date())

const consents = ref({
  oauth: false,
  aiReading: false
})

const settings = ref({
  aiReadAccess: true,
  draftOnlyMode: true,
  consentTimestamp: null
})

// Mock data
const mockEmails = [
  {
    id: 1,
    sender: { name: 'Dr. Sarah Mitchell', email: 'smitchell@lawfirm.com', initials: 'SM' },
    subject: 'Vertragsprüfung - Henderson Fall',
    snippet: 'Bitte überprüfen Sie die beigefügte Vergleichsvereinbarung für die Henderson-Angelegenheit. Wichtige Bedingungen umfassen Vertraulichkeitsklauseln, Zahlungspläne und Haftungsausschlüsse...',
    date: new Date(Date.now() - 2 * 3600000),
    type: 'Contracts',
    status: 'Ungelesen',
    priority: 'High',
    hasAttachment: true,
    starred: false
  },
  {
    id: 2,
    sender: { name: 'James Chen', email: 'jchen@corporate.com', initials: 'JC' },
    subject: 'Aktualisierung Zeugenaussage-Termin',
    snippet: 'Die für nächsten Dienstag geplante Zeugenaussage wurde auf Donnerstag 14 Uhr verschoben. Alle Parteien wurden benachrichtigt...',
    date: new Date(Date.now() - 5 * 3600000),
    type: 'Reminders',
    status: 'Read',
    priority: 'Normal',
    hasAttachment: false,
    starred: true
  },
  {
    id: 3,
    sender: { name: 'Emily Rodriguez', email: 'erodriguez@client.com', initials: 'ER' },
    subject: 'Kündigungsvereinbarung - Finaler Entwurf',
    snippet: 'Anbei der finale Entwurf der Arbeitskündigungsvereinbarung mit allen angeforderten Überarbeitungen einschließlich Abfindungsbedingungen...',
    date: new Date(Date.now() - 24 * 3600000),
    type: 'Terminations',
    status: 'AI Draft',
    priority: 'High',
    hasAttachment: true,
    starred: false
  },
  {
    id: 4,
    sender: { name: 'Gerichtskanzlei', email: 'clerk@court.gov', initials: 'GK' },
    subject: 'Einreichungsbestätigung - Fall 2025-CV-1842',
    snippet: 'Ihr Antrag wurde erfolgreich eingereicht. Die Anhörung ist für den 25. September um 10:00 Uhr in Gerichtssaal 3B geplant...',
    date: new Date(Date.now() - 48 * 3600000),
    type: 'All',
    status: 'Read',
    priority: 'Normal',
    hasAttachment: false,
    starred: false
  },
  {
    id: 5,
    sender: { name: 'Michael Thompson', email: 'mthompson@opposing.com', initials: 'MT' },
    subject: 'Beweisanfrage - Johnson gegen Smith',
    snippet: 'Bitte stellen Sie alle Dokumente im Zusammenhang mit dem Vorfall vom 15. März 2025 bereit. Antwort innerhalb von 30 Tagen fällig...',
    date: new Date(Date.now() - 72 * 3600000),
    type: 'Contracts',
    status: 'Ungelesen',
    priority: 'High',
    hasAttachment: true,
    starred: false
  },
  {
    id: 6,
    sender: { name: 'Rechtsassistent', email: 'assistant@lawfirm.com', initials: 'RA' },
    subject: 'Mandantentermin Erinnerung - Morgen 15 Uhr',
    snippet: 'Erinnerung: Sie haben morgen um 15 Uhr einen Mandantentermin. Konferenzraum B ist reserviert...',
    date: new Date(Date.now() - 96 * 3600000),
    type: 'Reminders',
    status: 'AI Pending',
    priority: 'Normal',
    hasAttachment: false,
    starred: true
  }
]

// Folders and Labels
const folders = computed(() => [
  { key: 'inbox', label: 'Posteingang', icon: 'M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4', count: emails.value.filter(e => e.status === 'Ungelesen').length },
  { key: 'starred', label: 'Markiert', icon: 'M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z', count: emails.value.filter(e => e.starred).length },
  { key: 'sent', label: 'Gesendet', icon: 'M12 19l9 2-9-18-9 18 9-2zm0 0v-8', count: 0 },
  { key: 'drafts', label: 'Entwürfe', icon: 'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z', count: 0 },
  { key: 'archive', label: 'Archiv', icon: 'M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4', count: 0 },
  { key: 'trash', label: 'Papierkorb', icon: 'M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16', count: 0 }
])

const labels = [
  { key: 'urgent', label: 'Dringend', color: '#ef4444', count: 2 },
  { key: 'client', label: 'Mandant', color: '#3b82f6', count: 4 },
  { key: 'court', label: 'Gericht', color: '#8b5cf6', count: 1 },
  { key: 'contracts', label: 'Verträge', color: '#10b981', count: 3 }
]

// Computed
const filteredEmails = computed(() => {
  let filtered = emails.value

  if (activeFolder.value === 'starred') {
    filtered = filtered.filter(e => e.starred)
  } else if (activeFolder.value === 'inbox') {
    filtered = filtered.filter(e => e.status !== 'Archived' && e.status !== 'Deleted')
  }

  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(e =>
      e.subject.toLowerCase().includes(query) ||
      e.snippet.toLowerCase().includes(query) ||
      e.sender.name.toLowerCase().includes(query) ||
      e.sender.email.toLowerCase().includes(query)
    )
  }

  // Sort
  if (sortBy.value === 'date-desc') {
    filtered = [...filtered].sort((a, b) => b.date - a.date)
  } else if (sortBy.value === 'date-asc') {
    filtered = [...filtered].sort((a, b) => a.date - b.date)
  }

  return filtered
})

// Methods
const handleOAuthConnect = (provider) => {
  if (consents.value.oauth && consents.value.aiReading) {
    loading.value = true
    setTimeout(() => {
      settings.value.consentTimestamp = new Date()
      currentView.value = 'inbox'
      loading.value = false
    }, 1500)
  }
}

const syncEmails = () => {
  loading.value = true
  setTimeout(() => {
    lastSyncTime.value = new Date()
    loading.value = false
  }, 1000)
}

const openEmail = (email) => {
  selectedEmail.value = email
  if (email.status === 'Ungelesen') {
    email.status = 'Read'
  }
}

const closeEmail = () => {
  selectedEmail.value = null
}

const replyToEmail = () => {
  composing.value = true
  selectedEmail.value = null
}

const forwardEmail = () => {
  composing.value = true
  selectedEmail.value = null
}

const toggleStar = (emailId) => {
  const email = emails.value.find(e => e.id === emailId)
  if (email) {
    email.starred = !email.starred
  }
}

const formatEmailDate = (date) => {
  const now = new Date()
  const diff = now - date
  const hours = Math.floor(diff / 3600000)

  if (hours < 1) return 'Gerade eben'
  if (hours < 24) return `Vor ${hours}h`
  if (hours < 48) return 'Gestern'
  return date.toLocaleDateString('de-DE', { day: '2-digit', month: 'short' })
}

const formatLongDate = (date) => {
  return date.toLocaleString('de-DE', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusClass = (status) => {
  const classes = {
    'Ungelesen': 'status-unread',
    'Read': 'status-read',
    'AI Draft': 'status-draft',
    'AI Pending': 'status-pending'
  }
  return classes[status] || 'status-read'
}

const getAISummary = (email) => {
  const summaries = {
    'Contracts': 'Wichtige Vertragsüberprüfung erforderlich. Schwerpunkt auf Haftungsausschlüssen und Zahlungsbedingungen. Antwort innerhalb von 48 Stunden empfohlen.',
    'Reminders': 'Terminaktualisierung - Zeugenaussage verschoben auf Donnerstag 14 Uhr. Keine Aktion erforderlich, nur zur Kenntnis.',
    'Terminations': 'Finaler Entwurf der Kündigungsvereinbarung bereit zur Überprüfung. Alle vorherigen Überarbeitungen wurden berücksichtigt.',
    'All': 'Gerichtseinreichung bestätigt - Anhörung geplant für 25. September 10:00 Uhr, Saal 3B.'
  }
  return summaries[email.type] || 'Keine KI-Zusammenfassung verfügbar.'
}

const handleRevokeAccess = () => {
  if (confirm('Sind Sie sicher, dass Sie den E-Mail-Zugriff widerrufen möchten? Sie müssen die Verbindung wiederherstellen, um diese Funktion zu nutzen.')) {
    currentView.value = 'consent'
    consents.value = { oauth: false, aiReading: false }
    emails.value = []
    settings.value = {
      aiReadAccess: true,
      draftOnlyMode: true,
      consentTimestamp: null
    }
    showSettings.value = false
  }
}

// Watchers
watch(() => currentView.value, (newView) => {
  if (newView === 'inbox') {
    loading.value = true
    setTimeout(() => {
      emails.value = mockEmails
      loading.value = false
      lastSyncTime.value = new Date()
    }, 1000)
  }
})

// Lifecycle
onMounted(() => {
  const interval = setInterval(() => {
    if (currentView.value === 'inbox') {
      lastSyncTime.value = new Date()
    }
  }, 30000)

  onBeforeUnmount(() => {
    clearInterval(interval)
  })
})
</script>

<style scoped>
/* Color Variables - Matching existing theme */
:root {
  --primary: #5b7ce6;
  --primary-hover: #4a6cd4;
  --primary-soft: rgba(91, 124, 230, 0.14);
  --surface: #ffffff;
  --border: #e5e7eb;
  --border-soft: rgba(208, 216, 255, 0.85);
  --text-strong: #111827;
  --text-medium: #374151;
  --text-muted: #6b7280;
  --background: #f9fafb;
  --hover-bg: #f3f4f6;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
}

.email-app {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100%;
  background: linear-gradient(180deg, #f4f5fb 0%, #f7f8ff 40%, #ffffff 100%);
}

/* ========== CONSENT SCREEN ========== */
.consent-screen {
  flex: 1;
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  position: relative;
}

.back-to-dashboard {
  position: absolute;
  top: 1.5rem;
  left: 1.5rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
  font-weight: 500;
  padding: 0.5rem 0.75rem;
  border-radius: 12px;
  transition: all 0.2s;
  text-decoration: none;
}

.back-to-dashboard:hover {
  color: var(--primary);
  background: var(--primary-soft);
}

.consent-card {
  max-width: 28rem;
  width: 100%;
  background: var(--surface);
  border: 1px solid var(--border-soft);
  border-radius: 24px;
  padding: 2rem;
  box-shadow: 0 20px 50px rgba(111, 134, 255, 0.12);
}

.consent-header {
  text-align: center;
  margin-bottom: 2rem;
}

.consent-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 4rem;
  height: 4rem;
  background: var(--primary-soft);
  border-radius: 20px;
  color: var(--primary);
  margin-bottom: 1rem;
}

.consent-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-strong);
  margin-bottom: 0.5rem;
}

.consent-subtitle {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.oauth-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.oauth-button {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  font-weight: 500;
  color: var(--text-strong);
  cursor: pointer;
  transition: all 0.2s;
}

.oauth-button:hover:not(:disabled) {
  background: var(--primary-soft);
  border-color: var(--primary);
  transform: translateY(-1px);
  box-shadow: 0 10px 30px rgba(91, 124, 230, 0.15);
}

.oauth-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.consent-checkboxes {
  background: var(--background);
  border-radius: 16px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.consent-checkbox-label {
  display: flex;
  align-items: start;
  gap: 0.75rem;
  cursor: pointer;
}

.consent-checkbox {
  margin-top: 0.125rem;
  flex-shrink: 0;
  width: 16px;
  height: 16px;
  accent-color: var(--primary);
}

.consent-checkbox-text {
  font-size: 0.875rem;
  color: var(--text-strong);
  line-height: 1.5;
  flex: 1;
}

.consent-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  font-size: 0.875rem;
}

.consent-link {
  color: var(--text-muted);
  text-decoration: underline;
  transition: color 0.2s;
}

.consent-link:hover {
  color: var(--primary);
}

.consent-separator {
  color: rgba(107, 114, 128, 0.3);
}

.consent-loading {
  margin-top: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  font-size: 0.875rem;
}

/* ========== INBOX LAYOUT ========== */
.inbox-layout {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* Header */
.inbox-header {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-link {
  color: var(--text-muted);
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.2s;
  text-decoration: none;
}

.back-link:hover {
  background: var(--hover-bg);
  color: var(--primary);
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-brand h1 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-strong);
}

.header-center {
  flex: 1;
  max-width: 600px;
}

.search-box {
  position: relative;
  width: 100%;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1.25rem;
  height: 1.25rem;
  color: var(--text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 3rem;
  border: 1px solid var(--border);
  border-radius: 12px;
  font-size: 0.875rem;
  background: var(--background);
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary);
  background: var(--surface);
  box-shadow: 0 0 0 3px var(--primary-soft);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.icon-button {
  padding: 0.5rem;
  border: none;
  background: transparent;
  color: var(--text-muted);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.icon-button:hover {
  background: var(--hover-bg);
  color: var(--primary);
}

.compose-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(91, 124, 230, 0.25);
}

.compose-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(91, 124, 230, 0.35);
}

/* Body */
/* Email Tabs - Horizontal */
.email-tabs {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1.25rem;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  overflow-x: auto;
  flex-shrink: 0;
}

.tab-item {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-medium);
  font-size: 0.8125rem;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
}

.tab-item:hover {
  background: var(--hover-bg);
  color: var(--text-strong);
}

.tab-item-active {
  background: var(--primary-soft) !important;
  color: var(--primary) !important;
  font-weight: 600;
}

.tab-label {
  font-size: 0.8125rem;
}

.tab-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.125rem;
  height: 1.125rem;
  padding: 0 0.375rem;
  background: var(--primary);
  color: white;
  border-radius: 999px;
  font-size: 0.6875rem;
  font-weight: 600;
}

.tab-icon {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
}

.tab-item-active .tab-count {
  background: var(--primary);
  color: white;
}

.inbox-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.folder-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
}

.folder-label {
  flex: 1;
}

.folder-count {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  background: var(--background);
  padding: 0.125rem 0.5rem;
  border-radius: 999px;
}

.sidebar-divider {
  height: 1px;
  background: var(--border);
  margin: 1rem 0;
}

.label-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  color: var(--text-medium);
  font-size: 0.875rem;
}

.label-item:hover {
  background: var(--hover-bg);
}

.label-item-active {
  background: var(--primary-soft) !important;
  color: var(--primary) !important;
}

.label-dot {
  width: 0.75rem;
  height: 0.75rem;
  border-radius: 50%;
  flex-shrink: 0;
}

.label-text {
  flex: 1;
}

.label-count {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Email List Container */
.email-list-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--background);
}

.email-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.checkbox-all input {
  width: 16px;
  height: 16px;
  accent-color: var(--primary);
  cursor: pointer;
}

.toolbar-button {
  padding: 0.5rem;
  border: none;
  background: transparent;
  color: var(--text-muted);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.toolbar-button:hover {
  background: var(--hover-bg);
  color: var(--primary);
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.email-count {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.sort-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 0.875rem;
  background: var(--surface);
  color: var(--text-medium);
  cursor: pointer;
}

/* Email List */
.email-list {
  flex: 1;
  overflow-y: auto;
  background: var(--surface);
}

.email-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  transition: all 0.15s;
}

.email-row:hover {
  background: var(--hover-bg);
}

.email-unread {
  background: rgba(91, 124, 230, 0.04);
}

.email-unread:hover {
  background: rgba(91, 124, 230, 0.08);
}

.email-selected {
  background: rgba(91, 124, 230, 0.12) !important;
}

.email-checkbox input {
  width: 16px;
  height: 16px;
  accent-color: var(--primary);
  cursor: pointer;
}

.email-star {
  cursor: pointer;
  flex-shrink: 0;
}

.email-sender {
  width: 200px;
  flex-shrink: 0;
}

.sender-name {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--text-strong);
}

.email-unread .sender-name {
  font-weight: 700;
}

.email-content {
  flex: 1;
  min-width: 0;
}

.email-subject-line {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.subject-text {
  font-size: 0.875rem;
  color: var(--text-strong);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.email-unread .subject-text {
  font-weight: 600;
}

.email-attachment-icon {
  width: 0.875rem;
  height: 0.875rem;
  color: var(--text-muted);
  flex-shrink: 0;
}

.email-snippet {
  font-size: 0.8125rem;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.email-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.status-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.625rem;
  border-radius: 999px;
}

.status-unread {
  background: rgba(59, 130, 246, 0.14);
  color: #3b82f6;
}

.status-read {
  background: rgba(156, 163, 175, 0.14);
  color: #6b7280;
}

.status-draft {
  background: rgba(139, 92, 246, 0.14);
  color: #8b5cf6;
}

.status-pending {
  background: rgba(245, 158, 11, 0.14);
  color: #f59e0b;
}

.email-date {
  font-size: 0.75rem;
  color: var(--text-muted);
  width: 80px;
  text-align: right;
}

/* Loading State */
.loading-state {
  padding: 1rem 1.5rem;
  background: var(--surface);
}

.email-skeleton {
  height: 72px;
  background: linear-gradient(90deg, var(--background) 25%, var(--hover-bg) 50%, var(--background) 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  background: var(--surface);
}

.empty-icon {
  width: 4rem;
  height: 4rem;
  color: var(--text-muted);
  opacity: 0.5;
  margin-bottom: 1rem;
}

.empty-text {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-strong);
  margin-bottom: 0.5rem;
}

.empty-subtext {
  font-size: 0.875rem;
  color: var(--text-muted);
}

/* ========== EMAIL MODAL ========== */
.email-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 1rem;
}

.email-modal {
  background: var(--surface);
  border-radius: 24px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.modal-header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
  min-width: 0;
}

.modal-back-button {
  padding: 0.5rem;
  border: none;
  background: transparent;
  color: var(--text-muted);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.modal-back-button:hover {
  background: var(--hover-bg);
  color: var(--primary);
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-strong);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.modal-header-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.modal-icon-button {
  padding: 0.5rem;
  border: none;
  background: transparent;
  color: var(--text-muted);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-icon-button:hover {
  background: var(--hover-bg);
  color: var(--primary);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.email-header {
  margin-bottom: 2rem;
}

.email-header-top {
  display: flex;
  align-items: start;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.sender-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.sender-avatar {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(91, 124, 230, 0.25), rgba(91, 124, 230, 0.45));
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.125rem;
  color: var(--primary);
  flex-shrink: 0;
}

.sender-details {
  flex: 1;
}

.sender-name-large {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-strong);
  margin-bottom: 0.25rem;
}

.sender-email-address {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.email-date-large {
  font-size: 0.875rem;
  color: var(--text-muted);
  flex-shrink: 0;
}

.email-header-info {
  background: var(--background);
  border-radius: 12px;
  padding: 1rem;
}

.header-info-row {
  display: flex;
  gap: 0.75rem;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.info-label {
  font-weight: 600;
  color: var(--text-medium);
}

.info-value {
  color: var(--text-muted);
}

.priority-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 600;
}

.email-body-content {
  line-height: 1.7;
}

.email-text {
  font-size: 0.9375rem;
  color: var(--text-medium);
  margin-bottom: 2rem;
}

.email-list-items {
  list-style: disc;
  padding-left: 1.5rem;
  margin: 1rem 0;
}

.email-list-items li {
  margin-bottom: 0.5rem;
}

.ai-summary {
  background: rgba(91, 124, 230, 0.04);
  border: 1px solid rgba(91, 124, 230, 0.2);
  border-radius: 12px;
  padding: 1rem;
  margin-top: 2rem;
}

.ai-summary-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--primary);
  margin-bottom: 0.75rem;
}

.ai-summary-text {
  font-size: 0.875rem;
  color: var(--text-medium);
  line-height: 1.6;
  margin-bottom: 0.75rem;
}

.ai-summary-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.ai-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 0.75rem;
  color: var(--text-medium);
  font-weight: 500;
}

.email-attachments {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
}

.attachments-header {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-strong);
  margin-bottom: 0.75rem;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 10px;
}

.attachment-thumbnail {
  width: 1.5rem;
  height: 1.5rem;
  flex-shrink: 0;
  border-radius: 10px;
  background: var(--primary-soft);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.attachment-thumbnail-icon {
  width: 1.125rem;
  height: 1.125rem;
}

.attachment-info {
  flex: 1;
}

.attachment-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-strong);
  margin-bottom: 0.125rem;
}

.attachment-size {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.attachment-download {
  padding: 0.5rem;
  border: none;
  background: transparent;
  color: var(--primary);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.attachment-download:hover {
  background: var(--primary-soft);
}

.modal-footer {
  display: flex;
  gap: 0.75rem;
  padding: 1.25rem 1.5rem;
  border-top: 1px solid var(--border);
  background: var(--background);
  flex-shrink: 0;
  flex-wrap: wrap;
}

.footer-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-medium);
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.footer-button:hover {
  background: var(--hover-bg);
  border-color: var(--primary);
  color: var(--primary);
}

.footer-button-primary {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%);
  color: white;
  border-color: transparent;
}

.footer-button-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(91, 124, 230, 0.25);
  border-color: transparent;
  color: white;
}

.footer-button-danger:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: #ef4444;
  color: #ef4444;
}

/* ========== SETTINGS MODAL ========== */
.settings-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 60;
  padding: 1rem;
}

.settings-modal {
  background: var(--surface);
  border-radius: 20px;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
}

.settings-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border);
}

.settings-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-strong);
}

.settings-close {
  padding: 0.5rem;
  border: none;
  background: transparent;
  color: var(--text-muted);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.settings-close:hover {
  background: var(--hover-bg);
  color: var(--primary);
}

.settings-body {
  padding: 1.5rem;
}

.setting-item {
  display: flex;
  align-items: start;
  gap: 1rem;
  padding: 1rem;
  background: var(--background);
  border-radius: 12px;
  margin-bottom: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.setting-item:hover {
  background: var(--hover-bg);
}

.setting-checkbox {
  width: 18px;
  height: 18px;
  accent-color: var(--primary);
  cursor: pointer;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.setting-info {
  flex: 1;
}

.setting-label {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--text-strong);
  margin-bottom: 0.25rem;
}

.setting-description {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.settings-info-section {
  background: var(--background);
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  font-size: 0.8125rem;
  margin-bottom: 0.5rem;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-item-label {
  font-weight: 600;
  color: var(--text-medium);
}

.info-item-value {
  color: var(--text-muted);
  text-align: right;
}

.revoke-button {
  width: 100%;
  padding: 0.75rem;
  background: transparent;
  border: 1px solid #ef4444;
  color: #ef4444;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.revoke-button:hover {
  background: rgba(239, 68, 68, 0.1);
}

/* ========== RESPONSIVE ========== */
@media (max-width: 1024px) {
  .email-sender {
    width: 150px;
  }
}

@media (max-width: 768px) {
  .inbox-header {
    flex-wrap: wrap;
  }

  .header-center {
    order: 3;
    width: 100%;
    margin-top: 1rem;
  }

  .email-tabs {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    padding: 0.375rem 0.875rem;
  }

  .tab-item {
    padding: 0.4375rem 0.625rem;
    font-size: 0.75rem;
  }

  .email-sender {
    display: none;
  }

  .email-row {
    gap: 0.75rem;
    padding: 0.75rem 1rem;
  }

  .email-meta {
    flex-direction: column;
    align-items: flex-end;
    gap: 0.5rem;
  }

  .modal-footer {
    flex-direction: column;
  }

  .footer-button {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 640px) {
  .compose-button span {
    display: none;
  }

  .email-date {
    width: auto;
  }
}
</style>
