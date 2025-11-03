<template>
  <PortalShell>
    <template #header>
      <div v-if="uiReady && currentView === 'inbox'" class="inbox-header">
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
          <button @click="requestSync" class="icon-button" title="Aktualisieren">
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
      <div v-if="uiReady && currentView === 'consent'" class="consent-screen">
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

        <div v-if="connectionSuccess" class="consent-success">
          <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
          <span class="ml-2">Gmail erfolgreich verbunden! E-Mails werden geladen...</span>
        </div>

        <div v-if="errorMessage" class="consent-error">
          <svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <span class="ml-2">{{ errorMessage }}</span>
        </div>
      </div>
    </div>

    <!-- Inbox View -->
    <div v-if="uiReady && currentView === 'inbox'" class="inbox-layout">
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
              <button class="toolbar-button" title="Aktualisieren" @click="requestSync">
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

          <div v-if="emailError" class="email-error-banner">
            <svg class="email-error-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <span>{{ emailError }}</span>
          </div>

          <!-- Loading State -->
          <div v-if="showSkeleton" class="loading-state">
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
          <template v-else>
            <Transition name="fade-300" mode="out-in">
              <div :key="`${activeFolder}-${listVersion}`" class="email-list">
                <div v-if="isRefreshing" class="list-loading-indicator">
                  <svg class="list-loading-spinner" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                  </svg>
                  <span>E-Mails werden aktualisiert…</span>
                </div>

                <div class="email-rows">
                  <TransitionGroup name="fade-rows" tag="div" class="email-rows-inner">
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

                      <div class="email-actions">
                        <button
                          class="email-action-button"
                          type="button"
                          title="Archivieren"
                          aria-label="E-Mail archivieren"
                          @click.stop="archiveEmail(email)"
                        >
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"/>
                          </svg>
                        </button>

                        <button
                          class="email-action-button"
                          type="button"
                          title="In Papierkorb verschieben"
                          aria-label="E-Mail löschen"
                          @click.stop="moveEmailToTrash(email)"
                        >
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                          </svg>
                        </button>

                        <button
                          class="email-action-button"
                          type="button"
                          :title="email.starred ? 'Markierung entfernen' : 'Markieren'"
                          :aria-label="email.starred ? 'Markierung entfernen' : 'E-Mail markieren'"
                          @click.stop="toggleStar(email.id)"
                        >
                          <svg v-if="email.starred" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                          </svg>
                          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/>
                          </svg>
                        </button>

                        <button
                          class="email-action-button"
                          type="button"
                          :title="email.status === 'Ungelesen' ? 'Als gelesen markieren' : 'Als ungelesen markieren'"
                          :aria-label="email.status === 'Ungelesen' ? 'Als gelesen markieren' : 'Als ungelesen markieren'"
                          @click.stop="toggleReadState(email)"
                        >
                          <svg v-if="email.status === 'Ungelesen'" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8m-18 8V8a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
                          </svg>
                          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                          </svg>
                        </button>
                      </div>
                    </div>
                  </TransitionGroup>
                </div>

                <div class="email-footer">
                  <span class="email-footer-count">Showing {{ filteredEmails.length }} E-Mails</span>
                  <div v-if="loadingMore" class="load-more-progress">
                    <svg class="load-more-spinner" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V2C5.373 2 0 7.373 0 14h4zm2 5.291A7.962 7.962 0 014 14H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Weitere E-Mails werden geladen...</span>
                  </div>
                  <button
                    v-else-if="showLoadMoreButton"
                    class="load-more-button"
                    type="button"
                    @click="loadMoreEmails"
                  >
                    <svg class="load-more-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                    </svg>
                    Mehr laden
                  </button>
                </div>
              </div>
            </Transition>
          </template>
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
                <div v-if="selectedEmail.priority" class="priority-badge">
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
                  <div class="ai-summary-title">
                    <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
                    </svg>
                    <span>KI-Zusammenfassung</span>
                  </div>
                  <button
                    class="ai-summary-refresh"
                    type="button"
                    :disabled="currentAiStatus === 'loading'"
                    @click.stop="refreshAiSummary"
                    title="Zusammenfassung aktualisieren"
                  >
                    <svg
                      class="w-4 h-4"
                      :class="{ 'ai-spinner': currentAiStatus === 'loading' }"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                    </svg>
                  </button>
                </div>
                <div v-if="currentAiStatus === 'loading'" class="ai-summary-loading">
                  <svg class="w-4 h-4 ai-spinner" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 12a8 8 0 0116 0"/>
                  </svg>
                  <span>KI analysiert die E-Mail …</span>
                </div>
                <div v-else-if="currentAiStatus === 'error'" class="ai-summary-error">
                  <span>{{ currentAiError || 'Die KI-Zusammenfassung konnte nicht erstellt werden.' }}</span>
                  <button type="button" class="ai-retry-button" @click.stop="refreshAiSummary">
                    Erneut versuchen
                  </button>
                </div>
                <template v-else-if="currentAiSummary">
                  <p class="ai-summary-text">{{ currentAiSummary.summary }}</p>
                  <div class="ai-summary-tags">
                    <span class="ai-tag">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/>
                      </svg>
                      Kategorie: {{ currentAiCategory }}
                    </span>
                    <span v-if="selectedEmail.priority" class="ai-tag">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                      </svg>
                      Priorität: Hoch
                    </span>
                    <span v-if="currentAiSummary.processedAt" class="ai-tag">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                      </svg>
                      Aktualisiert: {{ currentAiProcessedAt }}
                    </span>
                  </div>
                </template>
                <div v-else class="ai-summary-placeholder">
                  <span>Keine KI-Zusammenfassung vorhanden. Nutzen Sie die Aktualisieren-Schaltfläche, um die Analyse zu starten.</span>
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
            
            <!-- AI Floating Actions -->
            <div class="ai-floating-actions" v-if="selectedEmail">
              <div class="ai-actions-row">
                <button class="ai-action-btn primary" :disabled="aiActions.generatingReply" @click="onGenerateReply" title="Antwortentwurf erstellen">
                  <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"/></svg>
                  <span>{{ aiActions.generatingReply ? 'Erzeuge Antwort…' : 'Antwortentwurf' }}</span>
                </button>
                <button class="ai-action-btn secondary" @click="onSendToDocuments" title="Im Dokument-Assistenten weiterführen">
                  <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                  <span>Zu Dokumenten</span>
                </button>
              </div>

              <!-- Reply Result -->
              <div v-if="aiActions.replyText || aiActions.replyError" class="ai-result">
                <div class="ai-result-header">
                  <span class="ai-result-title">Antwortentwurf</span>
                  <div class="ai-result-actions">
                    <button v-if="aiActions.replyText" class="mini" @click="copyReplyToClipboard">Kopieren</button>
                  </div>
                </div>
                <div v-if="aiActions.replyError" class="ai-error">{{ aiActions.replyError }}</div>
                <pre v-else class="reply-preview">{{ aiActions.replyText }}</pre>
              </div>

              <!-- Document Result -->
              <div v-if="aiActions.docResult || aiActions.docError" class="ai-result">
                <div class="ai-result-header">
                  <span class="ai-result-title">Dokument</span>
                </div>
                <div v-if="aiActions.docError" class="ai-error">{{ aiActions.docError }}</div>
                <div v-else class="ai-doc-success" v-if="aiActions.docResult">
                  <div class="ai-doc-title">{{ aiActions.docResult.title }}</div>
                  <div class="ai-doc-links" v-if="aiActions.docResult.download">
                    <a v-if="aiActions.docResult.download.pdf" :href="aiActions.docResult.download.pdf" target="_blank" rel="noopener">PDF</a>
                    <a v-if="aiActions.docResult.download.docx" :href="aiActions.docResult.download.docx" target="_blank" rel="noopener">DOCX</a>
                  </div>
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
import { ref, computed, watch, onMounted, onBeforeUnmount, reactive } from 'vue'
import PortalShell from '~/components/PortalShell.vue'

definePageMeta({ layout: false })

const PAGE_SIZE = 20
const FOLDER_LABEL_MAP = Object.freeze({
  inbox: 'INBOX',
  starred: 'STARRED',
  flagged: 'STARRED',
  sent: 'SENT',
  drafts: 'DRAFT',
  archive: 'ARCHIVE',
  trash: 'TRASH',
  spam: 'SPAM',
  all: 'ALL'
})

// State
// UI gating to avoid consent flash after user connected
const uiReady = ref(false)
const currentView = ref('consent')
const selectedEmail = ref(null)
const activeFolder = ref('inbox')
const activeLabel = ref(FOLDER_LABEL_MAP[activeFolder.value] || 'INBOX')
const searchQuery = ref('')
const sortBy = ref('date-desc')
const selectAll = ref(false)
const emails = ref([])
const loading = ref(false)
const showSettings = ref(false)
const composing = ref(false)
const lastSyncTime = ref(new Date())
const connectionSuccess = ref(false)
const errorMessage = ref('')
const nextPageToken = ref('')
const loadingMore = ref(false)
const emailError = ref('')
const listVersion = ref(0)

const consents = ref({
  oauth: false,
  aiReading: false
})

const settings = ref({
  aiReadAccess: false,
  draftOnlyMode: true,
  consentTimestamp: null
})

const lastManualSyncReason = ref(null)

const aiState = reactive({
  summaries: {},
  status: {},
  errors: {}
})

// Floating AI actions state
const aiActions = reactive({
  generatingReply: false,
  replyText: '',
  replyError: '',
  generatingDoc: false,
  docResult: null,
  docError: ''
})

const gmailErrorMessages = {
  login_email_conflict: 'Verbinden Sie bitte ein separates Gmail-Konto. Ihre Portal-Login-E-Mail kann nicht für die Postfach-Verknüpfung verwendet werden.'
}

const resolveLabelForFolder = (folderKey) => {
  if (!folderKey) {
    return 'INBOX'
  }
  const normalized = String(folderKey).toLowerCase()
  return FOLDER_LABEL_MAP[normalized] || 'INBOX'
}

// Mock data - matches Gmail API response structure
const mockEmails = [
  {
    id: '18c1f2a3b4d5e6f7',
    sender: { name: 'Dr. Sarah Mitchell', email: 'smitchell@lawfirm.com', initials: 'SM' },
    subject: 'Vertragsprüfung - Henderson Fall',
    snippet: 'Bitte überprüfen Sie die beigefügte Vergleichsvereinbarung für die Henderson-Angelegenheit. Wichtige Bedingungen umfassen Vertraulichkeitsklauseln, Zahlungspläne und Haftungsausschlüsse...',
    date: new Date(Date.now() - 2 * 3600000),
    type: 'Contract',
    status: 'Ungelesen',
    priority: true,
    hasAttachment: true,
    starred: false
  },
  {
    id: '18c1f2a3b4d5e6f8',
    sender: { name: 'James Chen', email: 'jchen@corporate.com', initials: 'JC' },
    subject: 'Aktualisierung Zeugenaussage-Termin',
    snippet: 'Die für nächsten Dienstag geplante Zeugenaussage wurde auf Donnerstag 14 Uhr verschoben. Alle Parteien wurden benachrichtigt...',
    date: new Date(Date.now() - 5 * 3600000),
    type: 'Reminder',
    status: 'Read',
    priority: false,
    hasAttachment: false,
    starred: true
  },
  {
    id: '18c1f2a3b4d5e6f9',
    sender: { name: 'Emily Rodriguez', email: 'erodriguez@client.com', initials: 'ER' },
    subject: 'Kündigungsvereinbarung - Finaler Entwurf',
    snippet: 'Anbei der finale Entwurf der Arbeitskündigungsvereinbarung mit allen angeforderten Überarbeitungen einschließlich Abfindungsbedingungen...',
    date: new Date(Date.now() - 24 * 3600000),
    type: 'Termination',
    status: 'Read',
    priority: true,
    hasAttachment: true,
    starred: false
  },
  {
    id: '18c1f2a3b4d5e700',
    sender: { name: 'Gerichtskanzlei', email: 'clerk@court.gov', initials: 'GK' },
    subject: 'Einreichungsbestätigung - Fall 2025-CV-1842',
    snippet: 'Ihr Antrag wurde erfolgreich eingereicht. Die Anhörung ist für den 25. September um 10:00 Uhr in Gerichtssaal 3B geplant...',
    date: new Date(Date.now() - 48 * 3600000),
    type: 'General',
    status: 'Read',
    priority: false,
    hasAttachment: false,
    starred: false
  },
  {
    id: '18c1f2a3b4d5e701',
    sender: { name: 'Michael Thompson', email: 'mthompson@opposing.com', initials: 'MT' },
    subject: 'Beweisanfrage - Johnson gegen Smith',
    snippet: 'Bitte stellen Sie alle Dokumente im Zusammenhang mit dem Vorfall vom 15. März 2025 bereit. Antwort innerhalb von 30 Tagen fällig...',
    date: new Date(Date.now() - 72 * 3600000),
    type: 'Contract',
    status: 'Ungelesen',
    priority: true,
    hasAttachment: true,
    starred: false
  },
  {
    id: '18c1f2a3b4d5e702',
    sender: { name: 'Rechtsassistent', email: 'assistant@lawfirm.com', initials: 'RA' },
    subject: 'Mandantentermin Erinnerung - Morgen 15 Uhr',
    snippet: 'Erinnerung: Sie haben morgen um 15 Uhr einen Mandantentermin. Konferenzraum B ist reserviert...',
    date: new Date(Date.now() - 96 * 3600000),
    type: 'Reminder',
    status: 'Read',
    priority: false,
    hasAttachment: false,
    starred: true
  }
]

const computeInitials = (name = '', email = '') => {
  const cleanedName = name.replace(/[<>"']/g, ' ').trim()
  const parts = cleanedName.split(/\s+/).filter(Boolean)
  const letters = parts.map(part => part[0]).filter(Boolean)
  const candidate = (letters[0] || '') + (letters[1] || '')
  const alphaCandidate = candidate.replace(/[^A-Za-zÄÖÜäöüß]/g, '')
  if (alphaCandidate.length >= 2) {
    return alphaCandidate.slice(0, 2).toUpperCase()
  }
  if (alphaCandidate.length === 1) {
    return alphaCandidate.toUpperCase()
  }
  const fallback = (email || '').replace(/[^A-Za-z]/g, '')
  if (fallback.length >= 2) {
    return fallback.slice(0, 2).toUpperCase()
  }
  const alnum = (email || '').replace(/[^A-Za-z0-9]/g, '')
  return alnum.slice(0, 2).toUpperCase() || 'U'
}

const normalizeEmailRecord = (email) => {
  const senderName = email.senderName || email.sender?.name || ''
  const senderEmail = email.senderEmail || email.sender?.email || ''
  const displayName = senderName || senderEmail || 'Unbekannt'
  const dateValue = email.date ? new Date(email.date) : new Date()
  const date = isNaN(dateValue.getTime()) ? new Date() : dateValue

  return {
    id: email.id,
    labelIds: Array.isArray(email.labelIds) ? [...email.labelIds] : [],
    sender: {
      name: displayName,
      email: senderEmail,
      initials: computeInitials(displayName, senderEmail)
    },
    subject: email.subject || '(kein Betreff)',
    snippet: email.snippet || '',
    date,
    type: email.type || 'General',
    status: email.unread || email.status === 'Unread' || email.status === 'Ungelesen' ? 'Ungelesen' : 'Read',
    priority: Boolean(email.priority),
    hasAttachment: Boolean(email.hasAttachment),
    starred: Boolean(email.starred)
  }
}

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
    filtered = [...filtered].sort((a, b) => b.date.getTime() - a.date.getTime())
  } else if (sortBy.value === 'date-asc') {
    filtered = [...filtered].sort((a, b) => a.date.getTime() - b.date.getTime())
  } else if (sortBy.value === 'sender') {
    filtered = [...filtered].sort((a, b) => {
      const aName = (a.sender.name || a.sender.email || '').toLowerCase()
      const bName = (b.sender.name || b.sender.email || '').toLowerCase()
      if (aName === bName) {
        return (a.sender.email || '').localeCompare(b.sender.email || '')
      }
      return aName.localeCompare(bName)
    })
  } else if (sortBy.value === 'subject') {
    filtered = [...filtered].sort((a, b) => {
      const aSubject = (a.subject || '').toLowerCase()
      const bSubject = (b.subject || '').toLowerCase()
      if (aSubject === bSubject) {
        return b.date.getTime() - a.date.getTime()
      }
      return aSubject.localeCompare(bSubject)
    })
  }

  return filtered
})

const showLoadMoreButton = computed(() =>
  Boolean(nextPageToken.value) &&
  !loading.value &&
  !loadingMore.value &&
  !searchQuery.value.trim()
)

const showSkeleton = computed(() => loading.value && emails.value.length === 0)
const isRefreshing = computed(() => loading.value && emails.value.length > 0)

const currentAiSummary = computed(() => {
  const id = selectedEmail.value?.id
  if (!id) return null
  return aiState.summaries[id] || null
})

const currentAiStatus = computed(() => {
  const id = selectedEmail.value?.id
  if (!id) return 'idle'
  return aiState.status[id] || 'idle'
})

const currentAiError = computed(() => {
  const id = selectedEmail.value?.id
  if (!id) return ''
  return aiState.errors[id] || ''
})

const currentAiCategory = computed(() => currentAiSummary.value?.category || 'General')

const currentAiProcessedAt = computed(() => {
  const processedAt = currentAiSummary.value?.processedAt
  if (!processedAt) return ''
  return formatRelativeTime(processedAt)
})

// Methods
const persistConsentPreferences = async () => {
  const headers = {
    'Content-Type': 'application/json'
  }
  const authToken = getAuthToken()
  if (authToken) {
    const bearer = authToken.startsWith('Bearer ') ? authToken : `Bearer ${authToken}`
    headers.Authorization = bearer
    headers['X-Portal-Auth'] = bearer
  }

  const payload = {
    oauth_consent: consents.value.oauth,
    ai_read_consent: consents.value.aiReading,
    draft_only_mode: settings.value.draftOnlyMode
  }

  const response = await fetch('/api/user/gmail/consent', {
    method: 'POST',
    headers,
    credentials: 'include',
    body: JSON.stringify(payload)
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    console.error('Gmail consent save failed:', {
      status: response.status,
      statusText: response.statusText,
      errorData
    })
    const detail = errorData.detail || errorData.message || 'Zustimmungen konnten nicht gespeichert werden.'
    throw new Error(detail)
  }

  return response.json().catch(() => ({}))
}

const handleOAuthConnect = async (provider) => {
  if (!consents.value.oauth || !consents.value.aiReading) {
    errorMessage.value = 'Bitte akzeptieren Sie beide Zustimmungen.'
    setTimeout(() => { errorMessage.value = '' }, 3000)
    return
  }

  if (provider === 'gmail') {
    loading.value = true
    errorMessage.value = ''
    connectionSuccess.value = false

    try {
      console.log('Persisting consent preferences...')
      await persistConsentPreferences()
      console.log('Consent saved successfully')
      settings.value.aiReadAccess = true

      // Store return path for OAuth callback to redirect back here
      const returnPath = '/email'
      try {
        sessionStorage.setItem('gmail_oauth_return', returnPath)
        localStorage.removeItem('gmail_oauth_return')
      } catch (err) {
        console.warn('Failed to persist gmail return path in sessionStorage', err)
        // Fallback for environments without sessionStorage support
        try { localStorage.setItem('gmail_oauth_return', returnPath) } catch (_) {}
      }

      // Redirect to backend OAuth flow which will include Gmail scopes
      const authorizeUrl = new URL('/auth/google/authorize', window.location.origin)
      authorizeUrl.searchParams.set('mode', 'gmail')
      window.location.href = authorizeUrl.toString()
    } catch (error) {
      console.error('OAuth connection error:', error)
      errorMessage.value = typeof error?.message === 'string'
        ? error.message
        : 'Fehler beim Verbinden mit Gmail. Bitte versuchen Sie es erneut.'
      loading.value = false
      setTimeout(() => { errorMessage.value = '' }, 5000)
    }
  } else {
    // Outlook support not yet implemented
    errorMessage.value = 'Outlook-Integration kommt bald'
    setTimeout(() => { errorMessage.value = '' }, 3000)
  }
}

// Helper function to get auth token consistently
const getAuthToken = () => {
  const storageKeys = ['auth_token', 'anwalts_auth_token', 'access_token', 'token', 'sat']
  if (typeof window === 'undefined') {
    return ''
  }

  const readFromCookies = () => {
    try {
      if (typeof document === 'undefined' || !document.cookie) {
        return ''
      }
      const entries = document.cookie.split(';').map(entry => entry.trim()).filter(Boolean)
      for (const entry of entries) {
        const [name, ...rest] = entry.split('=')
        if (storageKeys.includes(name)) {
          return decodeURIComponent(rest.join('=') || '')
        }
      }
    } catch (err) {
      console.warn('Failed to retrieve auth token from cookies', err)
    }
    return ''
  }

  // Prefer cookie-based session token so backend always sees the active user even if localStorage is stale
  const cookieValue = readFromCookies()
  if (cookieValue) {
    return cookieValue
  }

  const readFromStorage = (storage) => {
    if (!storage) {
      return ''
    }
    try {
      for (const key of storageKeys) {
        const value = storage.getItem(key)
        if (value) {
          return value
        }
      }
    } catch (err) {
      console.warn('Failed to read auth token from web storage', err)
    }
    return ''
  }

  const localValue = typeof localStorage !== 'undefined' ? readFromStorage(localStorage) : ''
  if (localValue) {
    return localValue
  }

  const sessionValue = typeof sessionStorage !== 'undefined' ? readFromStorage(sessionStorage) : ''
  if (sessionValue) {
    return sessionValue
  }

  return ''
}

const consumeGmailErrorFromLocation = () => {
  if (typeof window === 'undefined') {
    return
  }
  try {
    const params = new URLSearchParams(window.location.search)
    const errorCode = params.get('gmail_error')
    if (!errorCode) {
      return
    }

    errorMessage.value = gmailErrorMessages[errorCode] || 'Gmail-Verknüpfung fehlgeschlagen. Bitte wählen Sie ein anderes Konto.'
    setTimeout(() => { errorMessage.value = '' }, 5000)

    params.delete('gmail_error')
    const nextQuery = params.toString()
    const nextUrl = `${window.location.pathname}${nextQuery ? `?${nextQuery}` : ''}${window.location.hash}`
    window.history.replaceState({}, '', nextUrl)
  } catch (err) {
    console.warn('Failed to parse gmail_error query parameter', err)
  }
}

const runManualSync = async ({
  pageToken = '',
  append = false,
  labelOverride,
  folderOverride,
} = {}) => {
  if (append && loadingMore.value) {
    return { ok: false, reason: 'in_progress' }
  }
  if (!append && loading.value) {
    return { ok: false, reason: 'in_progress' }
  }

  const headers = {}
  const authToken = getAuthToken()
  if (authToken) {
    const bearer = authToken.startsWith('Bearer ') ? authToken : `Bearer ${authToken}`
    headers.Authorization = bearer
    headers['X-Portal-Auth'] = bearer
  }

  const params = new URLSearchParams()
  params.set('limit', String(PAGE_SIZE))

  const effectiveFolder = (folderOverride || activeFolder.value || 'inbox').toLowerCase()
  if (effectiveFolder) {
    params.set('folder', effectiveFolder)
  }

  const requestLabel = typeof labelOverride === 'string'
    ? labelOverride
    : (activeLabel.value || resolveLabelForFolder(activeFolder.value))
  if (requestLabel) {
    params.set('label', requestLabel)
  }

  if (pageToken) {
    params.set('pageToken', pageToken)
  }

  const endpoint = `/api/user/gmail/sync?${params.toString()}`

  if (append) {
    loadingMore.value = true
  } else {
    loading.value = true
  }
  emailError.value = ''

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers,
      credentials: 'include'
    })

    const parsePayload = async () => {
      try {
        return await response.json()
      } catch (_err) {
        return {}
      }
    }

    if (response.ok) {
      const data = await parsePayload()
      if (data && data.success && Array.isArray(data.emails)) {
        const normalized = data.emails.map(normalizeEmailRecord)
        if (append) {
          const existingIds = new Set(emails.value.map(e => e.id))
          const deduped = normalized.filter(item => {
            if (existingIds.has(item.id)) {
              return false
            }
            existingIds.add(item.id)
            return true
          })
          if (deduped.length > 0) {
            emails.value = [...emails.value, ...deduped]
          }
        } else {
          emails.value = normalized
        }

        const selectedId = selectedEmail.value?.id
        if (selectedId) {
          const updated = emails.value.find(e => e.id === selectedId)
          selectedEmail.value = updated || null
        }

        nextPageToken.value = data.nextPageToken || ''
        lastSyncTime.value = new Date()
        if (!append) {
          listVersion.value += 1
        }
        return { ok: true }
      }

      if (!append) {
        emails.value = []
        nextPageToken.value = ''
      }
      return { ok: true }
    }

    const payload = await parsePayload()
    const detail = typeof payload.detail === 'string' ? payload.detail : ''
    const message = payload.message || detail || ''
    const errorCode = payload.error || ''

    if (response.status === 401) {
      if (errorCode === 'not_linked' || /Kein verknüpftes/i.test(detail || '')) {
        return { ok: false, reason: 'not_linked', detail: detail || 'Konto nicht verknüpft' }
      }
      emailError.value = message || 'Authentifizierungsfehler bei der Synchronisation.'
      return { ok: false, reason: 'unauthorized', detail: message }
    }

    if (response.status === 403) {
      emailError.value = message || 'Zugriff auf Gmail wurde nicht freigegeben.'
      return { ok: false, reason: 'forbidden', detail: message }
    }

    if (response.status === 429) {
      emailError.value = 'Zu viele Synchronisationsanfragen. Bitte warten Sie einen Moment.'
      return { ok: false, reason: 'rate_limited' }
    }

    // If manual endpoint is missing (404) or other server error, signal fallback by returning reason=null
    if (response.status === 404) {
      console.warn('[Email Sync] Manual endpoint not found; will fallback to list endpoint')
      return { ok: false, reason: null }
    }
    emailError.value = message || `Fehler beim Synchronisieren der E-Mails (Status ${response.status}).`
    console.warn('[Email Sync] API error:', response.status, emailError.value)
    return { ok: false, reason: 'error', detail: message }
  } catch (error) {
    console.error('Manual sync failed:', error)
    // Let caller fallback to list endpoint when network fails
    return { ok: false, reason: null, detail: String(error) }
  } finally {
    if (append) {
      loadingMore.value = false
    } else {
      loading.value = false
    }
  }
}

const syncEmails = async ({ pageToken = '', append = false, labelOverride, manual = false } = {}) => {
  if (manual) {
    const manualResult = await runManualSync({ pageToken, append, labelOverride, folderOverride: activeFolder.value })
    lastManualSyncReason.value = manualResult.reason || null

    if (!manualResult.ok) {
      if (manualResult.reason === 'not_linked') {
        currentView.value = 'consent'
        emails.value = mockEmails
        nextPageToken.value = ''
        Object.keys(aiState.summaries).forEach(key => delete aiState.summaries[key])
        Object.keys(aiState.status).forEach(key => delete aiState.status[key])
        Object.keys(aiState.errors).forEach(key => delete aiState.errors[key])
        settings.value.aiReadAccess = false
        return false
      }
      // Fallback: use standard list endpoint when manual sync is unavailable or fails
      const ok2 = await syncEmails({ pageToken: '', append: false, labelOverride, manual: false })
      lastManualSyncReason.value = null
      return ok2
    }

    lastManualSyncReason.value = null
    return true
  }
  lastManualSyncReason.value = null
  if (append && loadingMore.value) {
    return
  }
  if (!append && loading.value) {
    return
  }

  if (append && !pageToken) {
    pageToken = nextPageToken.value
  }

  if (append && !pageToken) {
    return
  }

  if (!append) {
    nextPageToken.value = ''
    selectAll.value = false
  }

  if (append) {
    loadingMore.value = true
  } else {
    loading.value = true
  }

  emailError.value = ''

  try {
    const headers = {}
    const authToken = getAuthToken()
    if (authToken) {
      const bearer = authToken.startsWith('Bearer ') ? authToken : `Bearer ${authToken}`
      headers.Authorization = bearer
      headers['X-Portal-Auth'] = bearer
    }

    const query = new URLSearchParams()
    query.set('limit', String(PAGE_SIZE))
    if (pageToken) {
      query.set('pageToken', pageToken)
    }

    const requestLabel = typeof labelOverride === 'string'
      ? labelOverride
      : (activeLabel.value || resolveLabelForFolder(activeFolder.value))

    if (requestLabel) {
      query.set('label', requestLabel)
    }

    if (!query.has('label') && activeFolder.value) {
      query.set('folder', activeFolder.value.toLowerCase())
    }

    const queryString = query.toString()
    const endpoint = queryString ? `/api/email/list?${queryString}` : '/api/email/list'

    const response = await fetch(endpoint, {
      headers,
      credentials: 'include'
    })

    if (response.ok) {
      const data = await response.json()
      if (data.success && Array.isArray(data.emails)) {
        const normalized = data.emails.map(normalizeEmailRecord)
        if (append) {
          const existingIds = new Set(emails.value.map(e => e.id))
          const deduped = normalized.filter(item => {
            if (existingIds.has(item.id)) {
              return false
            }
            existingIds.add(item.id)
            return true
          })
          if (deduped.length > 0) {
            emails.value = [...emails.value, ...deduped]
          }
        } else {
          emails.value = normalized
        }

        const selectedId = selectedEmail.value?.id
        if (selectedId) {
          const updated = emails.value.find(e => e.id === selectedId)
          selectedEmail.value = updated || null
        }

        nextPageToken.value = data.nextPageToken || ''
        lastSyncTime.value = new Date()
        if (!append) {
          listVersion.value += 1
        }
      } else if (!append) {
        emails.value = []
        nextPageToken.value = ''
      }
    } else if (response.status === 401) {
      const errorData = await response.json().catch(() => ({}))
      const detail = typeof errorData.detail === 'string' ? errorData.detail : ''
      const errorCode = errorData.error
      if (errorCode === 'not_linked' || /Kein verknüpftes/i.test(detail || '')) {
        currentView.value = 'consent'
        emails.value = mockEmails
        nextPageToken.value = ''
        Object.keys(aiState.summaries).forEach(key => delete aiState.summaries[key])
        Object.keys(aiState.status).forEach(key => delete aiState.status[key])
        Object.keys(aiState.errors).forEach(key => delete aiState.errors[key])
        settings.value.aiReadAccess = false
      } else {
        const message = errorData.message || detail || 'Authentifizierungsfehler beim Abrufen der E-Mails.'
        emailError.value = message
        console.warn('[Email List] Authentication error:', message)
      }
    } else {
      const errorData = await response.json().catch(() => ({}))
      const detail = typeof errorData.detail === 'string' ? errorData.detail : ''
      const message = errorData.message || detail || `Fehler beim Abrufen der E-Mails (Status ${response.status}).`
      emailError.value = message
      console.warn('[Email List] API error:', response.status, message)
      if (!append && emails.value.length === 0) {
        emails.value = []
      }
    }
  } catch (error) {
    console.error('Error syncing emails:', error)
    emailError.value = 'Netzwerkfehler beim Abrufen der E-Mails. Bitte versuchen Sie es erneut.'
    if (!append && emails.value.length === 0) {
      emails.value = []
    }
  } finally {
    if (append) {
      loadingMore.value = false
    } else {
      loading.value = false
    }
  }
}

const requestSync = async () => {
  const ok = await syncEmails({ manual: true, append: false, labelOverride: activeLabel.value })
  if (!ok && lastManualSyncReason.value !== 'not_linked') {
    console.warn('Manual sync did not complete successfully:', lastManualSyncReason.value)
  }
}

const mutateEmailLabels = async (emailId, labelsToAdd = [], labelsToRemove = []) => {
  if (!emailId) {
    return false
  }

  const headers = {
    'Content-Type': 'application/json'
  }
  const authToken = getAuthToken()
  if (authToken) {
    const bearer = authToken.startsWith('Bearer ') ? authToken : `Bearer ${authToken}`
    headers.Authorization = bearer
    headers['X-Portal-Auth'] = bearer
  }

  try {
    const response = await fetch('/api/email/modify', {
      method: 'POST',
      headers,
      credentials: 'include',
      body: JSON.stringify({ id: emailId, add: labelsToAdd, remove: labelsToRemove })
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const detail = errorData.detail || errorData.message || 'E-Mail-Aktion fehlgeschlagen.'
      throw new Error(detail)
    }

    return true
  } catch (error) {
    console.error('Failed to mutate email labels:', error)
    const message = typeof error?.message === 'string' ? error.message : 'E-Mail-Aktion fehlgeschlagen.'
    emailError.value = message
    setTimeout(() => {
      if (emailError.value === message) {
        emailError.value = ''
      }
    }, 4000)
    return false
  }
}

const fetchAiSummary = async (email, { force = false } = {}) => {
  if (!email?.id || !settings.value.aiReadAccess) {
    return
  }

  const emailId = email.id
  const status = aiState.status[emailId]
  if (!force) {
    if (status === 'loading') return
    if (status === 'success') return
  }

  aiState.status[emailId] = 'loading'
  aiState.errors[emailId] = ''

  try {
    const headers = {
      'Content-Type': 'application/json'
    }
    const authToken = getAuthToken()
    if (authToken) {
      const bearer = authToken.startsWith('Bearer ') ? authToken : `Bearer ${authToken}`
      headers.Authorization = bearer
      headers['X-Portal-Auth'] = bearer
    }

    const response = await fetch('/api/email/process', {
      method: 'POST',
      headers,
      credentials: 'include',
      body: JSON.stringify({ email_id: emailId })
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const detail = errorData.detail || errorData.message || `AI-Verarbeitung fehlgeschlagen (${response.status}).`
      aiState.errors[emailId] = detail
      aiState.status[emailId] = 'error'
      return
    }

    const data = await response.json()
    if (!data?.success) {
      const detail = data?.detail || data?.message || 'AI-Verarbeitung ohne Ergebnis abgeschlossen.'
      aiState.errors[emailId] = detail
      aiState.status[emailId] = 'error'
      return
    }

    const summaryPayload = data.summary || {}
    const summaryPoints = Array.isArray(summaryPayload.summary_points) ? summaryPayload.summary_points : []
    const risks = Array.isArray(summaryPayload.risks) ? summaryPayload.risks : []
    const actions = Array.isArray(summaryPayload.actions) ? summaryPayload.actions : []
    const summaryText = summaryPoints.length > 0
      ? summaryPoints.join('\n')
      : (summaryPayload.summary || summaryPayload.raw || 'Keine Zusammenfassung verfügbar.')

    aiState.summaries[emailId] = {
      summary: summaryText,
      points: summaryPoints,
      actions,
      risks,
      deadline: summaryPayload.deadline || '',
      category: summaryPayload.category || data.category || 'General',
      processedAt: summaryPayload.generated_at || data.processed_at || data.processedAt || null,
      raw: summaryPayload
    }
    aiState.status[emailId] = 'success'
  } catch (error) {
    console.error('AI processing error:', error)
    aiState.errors[emailId] = error?.message || 'Netzwerkfehler bei der AI-Verarbeitung.'
    aiState.status[emailId] = 'error'
  }
}

const refreshAiSummary = async () => {
  if (!selectedEmail.value) {
    return
  }
  await fetchAiSummary(selectedEmail.value, { force: true })
}

const openEmail = (email) => {
  selectedEmail.value = email
  if (email.status === 'Ungelesen') {
    email.status = 'Read'
  }
  if (settings.value.aiReadAccess) {
    fetchAiSummary(email).catch((err) => {
      console.warn('Failed to start AI processing', err)
    })
  }
  // Reset floating actions state for new selection
  aiActions.replyText = ''
  aiActions.replyError = ''
  aiActions.docResult = null
  aiActions.docError = ''
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

const toggleStar = async (emailId) => {
  const email = emails.value.find(e => e.id === emailId)
  if (!email) {
    return
  }

  const shouldStar = !email.starred
  const success = await mutateEmailLabels(emailId, shouldStar ? ['STARRED'] : [], shouldStar ? [] : ['STARRED'])
  if (!success) {
    return
  }

  email.starred = shouldStar
  email.labelIds = Array.isArray(email.labelIds) ? [...email.labelIds] : []
  if (shouldStar) {
    if (!email.labelIds.includes('STARRED')) {
      email.labelIds.push('STARRED')
    }
  } else {
    email.labelIds = email.labelIds.filter(label => label !== 'STARRED')
  }

  if (selectedEmail.value?.id === emailId) {
    selectedEmail.value = {
      ...selectedEmail.value,
      starred: shouldStar,
      labelIds: [...email.labelIds]
    }
  }

  if (!shouldStar && activeFolder.value === 'starred') {
    emails.value = emails.value.filter(e => e.id !== emailId)
    if (selectedEmail.value?.id === emailId) {
      selectedEmail.value = null
    }
  }
}

const archiveEmail = async (email) => {
  if (!email?.id) {
    return
  }
  const success = await mutateEmailLabels(email.id, [], ['INBOX'])
  if (!success) {
    return
  }

  email.labelIds = Array.isArray(email.labelIds) ? email.labelIds.filter(label => label !== 'INBOX') : []
  email.status = 'Archived'

  if (selectedEmail.value?.id === email.id) {
    selectedEmail.value = {
      ...selectedEmail.value,
      status: email.status,
      labelIds: [...email.labelIds]
    }
  }

  if (activeFolder.value === 'inbox') {
    emails.value = emails.value.filter(e => e.id !== email.id)
    if (selectedEmail.value?.id === email.id) {
      selectedEmail.value = null
    }
  }
}

const moveEmailToTrash = async (email) => {
  if (!email?.id) {
    return
  }
  const success = await mutateEmailLabels(email.id, ['TRASH'], ['INBOX'])
  if (!success) {
    return
  }

  const nextLabels = Array.isArray(email.labelIds) ? email.labelIds.filter(label => label !== 'INBOX') : []
  if (!nextLabels.includes('TRASH')) {
    nextLabels.push('TRASH')
  }
  email.labelIds = nextLabels
  email.status = 'Deleted'

  if (selectedEmail.value?.id === email.id) {
    selectedEmail.value = {
      ...selectedEmail.value,
      status: email.status,
      labelIds: [...email.labelIds]
    }
  }

  if (activeFolder.value !== 'trash') {
    emails.value = emails.value.filter(e => e.id !== email.id)
    if (selectedEmail.value?.id === email.id) {
      selectedEmail.value = null
    }
  }
}

const toggleReadState = async (email) => {
  if (!email?.id) {
    return
  }
  const labelIds = Array.isArray(email.labelIds) ? [...email.labelIds] : []
  const isUnread = labelIds.includes('UNREAD') || email.status === 'Ungelesen'
  const add = isUnread ? [] : ['UNREAD']
  const remove = isUnread ? ['UNREAD'] : []

  const success = await mutateEmailLabels(email.id, add, remove)
  if (!success) {
    return
  }

  let nextStatus = 'Read'
  let nextLabels = labelIds.filter(label => label !== 'UNREAD')
  if (!isUnread) {
    nextLabels = [...nextLabels, 'UNREAD']
    nextStatus = 'Ungelesen'
  }

  email.labelIds = nextLabels
  email.status = nextStatus

  if (selectedEmail.value?.id === email.id) {
    selectedEmail.value = {
      ...selectedEmail.value,
      status: nextStatus,
      labelIds: [...nextLabels]
    }
  }
}

// Floating actions handlers
const onGenerateReply = async () => {
  if (!selectedEmail.value || aiActions.generatingReply) return
  aiActions.replyError = ''
  aiActions.replyText = ''
  aiActions.generatingReply = true
  try {
    const headers = { 'Content-Type': 'application/json' }
    const authToken = getAuthToken()
    if (authToken) {
      const bearer = authToken.startsWith('Bearer ') ? authToken : `Bearer ${authToken}`
      headers.Authorization = bearer
      headers['X-Portal-Auth'] = bearer
    }
    // Use assistant chat endpoint to generate a formal German reply
    const prompt = [
      'Formuliere eine professionelle Antwort-E-Mail in der Sie-Form.',
      'Ton: juristisch präzise, knapp, freundlich.',
      `Betreff: ${selectedEmail.value.subject || '(kein Betreff)'}`,
      'Originaltext (Auszug):',
      (selectedEmail.value.snippet || '').slice(0, 12000)
    ].join('\n\n')
    const res = await fetch('/api/assistant/chat', {
      method: 'POST',
      headers,
      credentials: 'include',
      body: JSON.stringify({ message: prompt, temperature: 0.25 })
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail || data.message || `Fehler (${res.status})`)
    }
    const data = await res.json()
    aiActions.replyText = (data.content || '').trim()
  } catch (e) {
    aiActions.replyError = e?.message || 'Antwortentwurf fehlgeschlagen.'
  } finally {
    aiActions.generatingReply = false
  }
}

const copyReplyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(aiActions.replyText || '')
    // Optional: simple toast
    console.log('Antwort in die Zwischenablage kopiert')
  } catch (e) {
    console.warn('Kopieren fehlgeschlagen', e)
  }
}

// Hand-off to Documents page with prefill
const router = useRouter()
const onSendToDocuments = async () => {
  if (!selectedEmail.value) return
  try {
    const payload = {
      subject: selectedEmail.value.subject || 'E-Mail',
      content: (selectedEmail.value.snippet || '').slice(0, 20000)
    }
    try { localStorage.setItem('anwalt.emailToDocument', JSON.stringify(payload)) } catch (_) {}
    await router.push({ path: '/documents', query: { from: 'email' } })
  } catch (e) {
    console.warn('[Email] Navigation to documents failed:', e)
  }
}

const loadMoreEmails = () => {
  if (!nextPageToken.value || loadingMore.value || searchQuery.value.trim()) {
    return
  }
  syncEmails({ append: true })
}

const formatRelativeTime = (isoString) => {
  try {
    const timestamp = new Date(isoString)
    if (Number.isNaN(timestamp.getTime())) {
      return ''
    }
    const now = new Date()
    const diffMs = now.getTime() - timestamp.getTime()
    const diffMinutes = Math.floor(diffMs / 60000)
    if (diffMinutes < 1) return 'Gerade eben'
    if (diffMinutes < 60) return `Vor ${diffMinutes} Min.`
    const diffHours = Math.floor(diffMinutes / 60)
    if (diffHours < 24) return `Vor ${diffHours} Std.`
    const diffDays = Math.floor(diffHours / 24)
    if (diffDays === 1) return 'Vor 1 Tag'
    if (diffDays < 7) return `Vor ${diffDays} Tagen`
    return timestamp.toLocaleDateString('de-DE', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    })
  } catch (err) {
    console.warn('Failed to format relative time', err)
    return ''
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
    'AI Pending': 'status-pending',
    'Archived': 'status-archived',
    'Deleted': 'status-deleted'
  }
  return classes[status] || 'status-read'
}

const handleRevokeAccess = async () => {
  if (!confirm('Sind Sie sicher, dass Sie den E-Mail-Zugriff widerrufen möchten? Sie müssen die Verbindung wiederherstellen, um diese Funktion zu nutzen.')) {
    return
  }

  try {
    const authToken = getAuthToken()
    if (!authToken) {
      console.error('No auth token available')
      alert('Authentifizierungsfehler. Bitte melden Sie sich erneut an.')
      return
    }

    const response = await fetch('/api/user/gmail/revoke', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`
      },
      credentials: 'include'
    })

    if (response.ok) {
      currentView.value = 'consent'
      consents.value = { oauth: false, aiReading: false }
      emails.value = []
      settings.value = {
        aiReadAccess: false,
        draftOnlyMode: true,
        consentTimestamp: null
      }
      Object.keys(aiState.summaries).forEach(key => delete aiState.summaries[key])
      Object.keys(aiState.status).forEach(key => delete aiState.status[key])
      Object.keys(aiState.errors).forEach(key => delete aiState.errors[key])
      showSettings.value = false
      console.log('Gmail access revoked successfully')
    } else {
      const errorData = await response.json().catch(() => ({}))
      console.error('Failed to revoke access:', response.status, errorData)
      alert('Fehler beim Widerrufen des Zugriffs. Bitte versuchen Sie es erneut.')
    }
  } catch (error) {
    console.error('Error revoking Gmail access:', error)
    alert('Netzwerkfehler beim Widerrufen des Zugriffs. Bitte überprüfen Sie Ihre Internetverbindung.')
  }
}

// Watchers
watch(() => currentView.value, async (newView) => {
  if (newView === 'inbox') {
    activeLabel.value = resolveLabelForFolder(activeFolder.value)
    if (emails.value.length === 0) {
      await syncEmails({ append: false, labelOverride: activeLabel.value })
    }
  }
})

watch(activeFolder, async (nextFolder) => {
  if (currentView.value === 'consent') {
    return
  }
  activeLabel.value = resolveLabelForFolder(nextFolder)
  if (currentView.value !== 'inbox') {
    currentView.value = 'inbox'
  }
  selectedEmail.value = null
  await syncEmails({ append: false, labelOverride: activeLabel.value })
})

watch(() => settings.value.aiReadAccess, (enabled) => {
  if (enabled && selectedEmail.value) {
    fetchAiSummary(selectedEmail.value).catch((err) => {
      console.warn('Failed to initiate AI summary after enabling access', err)
    })
  }
})

// Lifecycle
onMounted(async () => {
  consumeGmailErrorFromLocation()
  // Pre-set view from last known state to minimize flicker (client-only)
  try {
    if (typeof window !== 'undefined') {
      const last = localStorage.getItem('anwalt.email.connected')
      if (last === '1') currentView.value = 'inbox'
    }
  } catch(_) {}

  // Check Gmail connection status
  try {
    const headers = {}
    const authToken = getAuthToken()
    if (authToken) {
      const bearer = authToken.startsWith('Bearer ') ? authToken : `Bearer ${authToken}`
      headers.Authorization = bearer
      headers['X-Portal-Auth'] = bearer
    }

    const response = await fetch('/api/user/gmail/status', {
      headers,
      credentials: 'include'
    })

    if (response.ok) {
      const data = await response.json()
      if (data.connected) {
        // Gmail is connected, show inbox
        connectionSuccess.value = true
        setTimeout(() => { connectionSuccess.value = false }, 2000)
        currentView.value = 'inbox'
        try { localStorage.setItem('anwalt.email.connected', '1') } catch(_) {}
        if (data.consent_timestamp) {
          settings.value.consentTimestamp = new Date(data.consent_timestamp)
        }
        if (typeof data.ai_read_consent !== 'undefined') {
          settings.value.aiReadAccess = Boolean(data.ai_read_consent)
        } else if (typeof data.aiReadConsent !== 'undefined') {
          settings.value.aiReadAccess = Boolean(data.aiReadConsent)
        } else {
          settings.value.aiReadAccess = true
        }
        console.log('Gmail connected, loading emails...')
        activeLabel.value = resolveLabelForFolder(activeFolder.value)
        const manualLoaded = await syncEmails({ manual: true, append: false, labelOverride: activeLabel.value })
        if (!manualLoaded && !lastManualSyncReason.value) {
          await syncEmails({ append: false, labelOverride: activeLabel.value })
        }
      } else {
        // Not connected, show consent screen
        console.log('Gmail not connected, showing consent screen')
        currentView.value = 'consent'
        try { localStorage.removeItem('anwalt.email.connected') } catch(_) {}
        emails.value = mockEmails
        nextPageToken.value = ''
        Object.keys(aiState.summaries).forEach(key => delete aiState.summaries[key])
        Object.keys(aiState.status).forEach(key => delete aiState.status[key])
        Object.keys(aiState.errors).forEach(key => delete aiState.errors[key])
        settings.value.aiReadAccess = false
      }
    } else if (response.status === 401) {
      // Authentication error
      console.warn('Authentication error checking Gmail status')
      currentView.value = 'consent'
      try { localStorage.removeItem('anwalt.email.connected') } catch(_) {}
      emails.value = mockEmails
      nextPageToken.value = ''
    } else {
      // Other error, show consent screen
      console.error(`Error checking Gmail status: ${response.status}`)
      currentView.value = 'consent'
      try { localStorage.removeItem('anwalt.email.connected') } catch(_) {}
      emails.value = mockEmails
      nextPageToken.value = ''
    }
  } catch (error) {
    console.error('Network error checking Gmail status:', error)
    currentView.value = 'consent'
    try { localStorage.removeItem('anwalt.email.connected') } catch(_) {}
    emails.value = mockEmails
    nextPageToken.value = ''
  }

  // Release UI gating after status resolved
  uiReady.value = true

  const interval = setInterval(() => {
    if (currentView.value === 'inbox') {
      syncEmails() // Auto-refresh emails every 30 seconds
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

.consent-success {
  margin-top: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #10b981;
  font-size: 0.875rem;
  font-weight: 500;
}

.consent-error {
  margin-top: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ef4444;
  font-size: 0.875rem;
  font-weight: 500;
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
  transition: all 0.3s ease;
  color: var(--text-medium);
  font-size: 0.8125rem;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
}

.tab-item:hover {
  background: var(--hover-bg);
  color: var(--text-strong);
}

.tab-item::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  height: 2px;
  background: var(--primary);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
}

.tab-item:hover::after {
  transform: scaleX(0.4);
}

.tab-item-active {
  background: var(--primary-soft) !important;
  color: var(--primary) !important;
  font-weight: 600;
}

.tab-item-active::after {
  transform: scaleX(1);
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
  min-height: 0;
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
  min-height: 0;
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
  transition: transform 0.2s ease, box-shadow 0.2s ease;
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

.email-error-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0.75rem 1.5rem 0;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  background: rgba(254, 226, 226, 0.75);
  border: 1px solid rgba(254, 202, 202, 0.9);
  color: #b91c1c;
  font-size: 0.875rem;
}

.email-error-icon {
  width: 1.1rem;
  height: 1.1rem;
}

/* Email List */
.email-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--surface);
  overflow: hidden;
  min-height: 0;
}

.email-rows {
  flex: 1;
  overflow-y: auto;
  position: relative;
}

.email-rows-inner {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.email-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  padding-right: 5.5rem;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  transition: all 0.15s ease;
  position: relative;
}

.load-more-progress {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.load-more-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.3rem;
  border-radius: 9999px;
  border: 1px solid rgba(91, 124, 230, 0.35);
  background: rgba(91, 124, 230, 0.12);
  color: var(--primary);
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  cursor: pointer;
}

.load-more-button:hover {
  background: rgba(91, 124, 230, 0.18);
  border-color: rgba(91, 124, 230, 0.55);
  transform: translateY(-1px);
  animation: pulse 1.4s ease-in-out infinite;
}

.load-more-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.load-more-icon {
  width: 1.1rem;
  height: 1.1rem;
}

.load-more-spinner {
  width: 1.75rem;
  height: 1.75rem;
  color: var(--primary);
  animation: spin 1s linear infinite;
}

@keyframes pulse {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(91, 124, 230, 0.35);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(91, 124, 230, 0);
  }
}

.email-footer {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem 5.5rem; /* extra bottom space to clear chat widget */
  background: var(--surface);
  border-top: 1px solid var(--border);
}

.email-footer-count {
  font-size: 0.8125rem;
  color: var(--text-muted);
  text-align: center;
}

.fade-300-enter-active,
.fade-300-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-300-enter-from,
.fade-300-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

.fade-rows-enter-active,
.fade-rows-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.fade-rows-enter-from,
.fade-rows-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

.fade-rows-move {
  transition: transform 0.25s ease;
}

@media (max-width: 1024px) {
  .email-footer { padding-bottom: 6.5rem; }
  .inbox-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-center {
    width: 100%;
  }

  .header-right {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .compose-button {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .email-tabs {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .tab-item {
    width: 100%;
    justify-content: space-between;
  }

  .email-row {
    flex-direction: column;
    align-items: flex-start;
    padding-right: 1.5rem;
    gap: 0.75rem;
  }

  .email-sender {
    width: 100%;
  }

  .email-meta {
    width: 100%;
    justify-content: space-between;
  }

  .email-date {
    width: auto;
  }

  .email-actions {
    position: static;
    transform: none;
    opacity: 1;
    pointer-events: auto;
    width: 100%;
    justify-content: flex-start;
    margin-top: 0.25rem;
    gap: 0.5rem;
  }

  .email-action-button {
    width: 36px;
    height: 36px;
  }

  .email-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
}

.list-loading-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.75rem;
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.list-loading-spinner {
  width: 1rem;
  height: 1rem;
  animation: spin 0.9s linear infinite;
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

.email-actions {
  position: absolute;
  right: 1.5rem;
  top: 50%;
  transform: translateY(-50%) translateX(12px);
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.email-row:hover .email-actions,
.email-row.email-selected .email-actions,
.email-row:focus-within .email-actions {
  opacity: 1;
  transform: translateY(-50%) translateX(0);
  pointer-events: auto;
}

.email-action-button {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  border: 1px solid transparent;
  background: rgba(91, 124, 230, 0.08);
  color: var(--primary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  pointer-events: auto;
}

.email-action-button:hover {
  background: rgba(91, 124, 230, 0.16);
  border-color: rgba(91, 124, 230, 0.35);
  transform: translateY(-1px);
}

.email-action-button:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px rgba(91, 124, 230, 0.25);
}

.email-action-button svg {
  width: 1rem;
  height: 1rem;
}

.email-checkbox input {
  width: 16px;
  height: 16px;
  accent-color: var(--primary);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.checkbox-all input:active,
.email-checkbox input:active {
  transform: scale(0.92);
}

.checkbox-all input:checked,
.email-checkbox input:checked {
  transform: scale(1.08);
  box-shadow: 0 0 0 3px rgba(91, 124, 230, 0.25);
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

.status-archived {
  background: rgba(99, 102, 241, 0.14);
  color: #6366f1;
}

.status-deleted {
  background: rgba(239, 68, 68, 0.14);
  color: #ef4444;
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
  justify-content: space-between;
  gap: 0.75rem;
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--primary);
  margin-bottom: 0.75rem;
}

.ai-summary-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.ai-summary-refresh {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 999px;
  border: 1px solid rgba(91, 124, 230, 0.3);
  background: rgba(91, 124, 230, 0.08);
  color: var(--primary);
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.ai-summary-refresh:hover:not(:disabled) {
  background: rgba(91, 124, 230, 0.16);
  border-color: rgba(91, 124, 230, 0.45);
}

.ai-summary-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.ai-summary-loading,
.ai-summary-error,
.ai-summary-placeholder {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  line-height: 1.45;
}

.ai-summary-loading {
  color: var(--text-muted);
}

.ai-summary-error {
  color: #ef4444;
  flex-wrap: wrap;
}

.ai-summary-placeholder {
  color: var(--text-muted);
}

.ai-retry-button {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  border: 1px solid rgba(239, 68, 68, 0.4);
  background: rgba(239, 68, 68, 0.08);
  color: #ef4444;
  font-size: 0.75rem;
  font-weight: 500;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.ai-retry-button:hover {
  background: rgba(239, 68, 68, 0.16);
  border-color: rgba(239, 68, 68, 0.5);
}

.ai-spinner {
  animation: spin 1s linear infinite;
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

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
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

/* AI Floating Actions */
.ai-floating-actions {
  position: sticky;
  bottom: 0;
  margin-top: 0.5rem;
  padding: 0.75rem;
  background: var(--surface);
  border-top: 1px solid var(--border);
  border-radius: 10px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.08);
}
.ai-actions-row {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}
.ai-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 14px;
  border: 1px solid rgba(91, 124, 230, 0.25);
  background: rgba(91, 124, 230, 0.06);
  color: var(--text-strong);
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease, background 0.18s ease;
}
.ai-action-btn.primary {
  background: linear-gradient(135deg, #5b7ce6 0%, #4a6cd4 100%);
  color: #fff;
  border-color: rgba(91, 124, 230, 0.25);
  box-shadow: 0 10px 30px rgba(91, 124, 230, 0.25);
}
.ai-action-btn.secondary {
  border-color: rgba(91, 124, 230, 0.3);
  background: rgba(91, 124, 230, 0.1);
  color: var(--primary-strong);
}
.ai-action-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.ai-action-btn:hover:not(:disabled) { box-shadow: 0 18px 28px rgba(60, 76, 150, 0.18); transform: translateY(-1px); }

.ai-result { margin-top: 0.75rem; }
.ai-result-header { display:flex; align-items:center; justify-content: space-between; margin-bottom: 0.25rem; }
.ai-result-title { font-weight: 600; color: var(--text-strong); }
.ai-result-actions .mini { font-size: 0.75rem; padding: 0.25rem 0.5rem; border: 1px solid var(--border); border-radius: 6px; background: var(--background); }
.reply-preview { white-space: pre-wrap; background: var(--background); border: 1px dashed var(--border); border-radius: 8px; padding: 0.5rem; font-size: 0.875rem; line-height: 1.35; }
.ai-error { color: #b91c1c; font-size: 0.875rem; }
.ai-doc-success { font-size: 0.875rem; }
.ai-doc-title { font-weight: 600; margin-bottom: 0.25rem; }
.ai-doc-links a { margin-right: 0.5rem; color: var(--primary); text-decoration: underline; }
</style>
