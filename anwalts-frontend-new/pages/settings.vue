<template>
  <PortalShell>
    <template #header>
      <!-- Header -->
      <header class="page-header">
        <div class="header-inner">
          <div class="header-top">
            <div class="header-title">
              <NuxtLink to="/dashboard" class="back-link" aria-label="Zur Übersicht">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
                </svg>
              </NuxtLink>
              <div class="title-group">
                <h1 class="h1">Systemeinstellungen</h1>
                <p class="subtitle">Verwaltung und Konfiguration der Plattform</p>
              </div>
            </div>
            <div class="header-actions">
              <span
                v-if="lastUpdate && sectionsReady.overview"
                class="last-update"
              >
                Zuletzt aktualisiert: {{ lastUpdate }}
              </span>
              <button
                @click="refreshData"
                class="btn btn-secondary refresh-btn"
                :class="{ 'opacity-60 cursor-not-allowed': refreshing }"
                :disabled="refreshing"
                :aria-busy="refreshing"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                </svg>
                <span>{{ refreshing ? 'Aktualisieren…' : 'Aktualisieren' }}</span>
              </button>
            </div>
          </div>

          <div class="header-tabs">
            <nav class="tab-list" aria-label="Tabs">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                @click="activeTab = tab.id"
                :class="['tab', { 'tab-active': activeTab === tab.id }]"
              >
                <span class="flex items-center gap-2">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="tab.iconPath"/>
                  </svg>
                  {{ tab.name }}
                  <span v-if="tab.badge" class="badge"
                    :class="tab.badgeClass">{{ tab.badge }}</span>
                </span>
              </button>
            </nav>
          </div>
        </div>
      </header>
    </template>

    <!-- Main Content -->
    <div class="main-content">
      <main class="main-container">
      <!-- Analytics & Metrics Tab -->
      <div v-if="activeTab === 'analytics'" class="tab-content space-y-10">
        <SettingsSkeleton v-if="!sectionsReady.overview" />
        <div v-else class="flex flex-col gap-12">
          <p v-if="hydration.errors.overview" class="error-message">
            {{ hydration.errors.overview }}
          </p>

          <!-- KPI Cards -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 xl:gap-10">
            <div v-for="kpi in kpis" :key="kpi.label" class="card">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm font-medium text-gray-600">{{ kpi.label }}</p>
                  <p class="text-2xl font-semibold text-gray-900">{{ kpi.value }}</p>
                  <p class="text-sm text-gray-500">
                    <span>{{ kpi.change > 0 ? '↑' : '↓' }} {{ Math.abs(kpi.change) }}%</span>
                    <span class="ml-1">vs. letzte Woche</span>
                  </p>
                </div>
                <div class="p-3 rounded-lg bg-gray-100">
                  <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="kpi.iconPath"/>
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <div v-if="overviewMeta" class="grid grid-cols-1 sm:grid-cols-3 gap-8 xl:gap-10">
            <div class="card">
              <p class="text-sm text-gray-500 mb-1">Vorlagen insgesamt</p>
              <p class="text-2xl font-semibold text-gray-900">{{ formatNumber(overviewMeta.templates_total || 0) }}</p>
            </div>
            <div class="card">
              <p class="text-sm text-gray-500 mb-1">Aktive Webhooks</p>
              <p class="text-2xl font-semibold text-gray-900">{{ formatNumber(overviewMeta.webhooks_total || 0) }}</p>
            </div>
            <div v-if="apiSummary" class="card">
              <p class="text-sm text-gray-500 mb-1">API-Erfolgsquote</p>
              <p class="text-2xl font-semibold text-gray-900">{{ apiSummary.successRate ? apiSummary.successRate + '%' : '–' }}</p>
              <p class="text-xs text-gray-600 mt-0.5" v-if="apiSummary.avgLatency">Ø {{ apiSummary.avgLatency }} ms</p>
            </div>
          </div>

          <!-- System Health -->
          <div class="card">
            <h3 class="h3">Systemstatus</h3>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div v-for="service in systemHealth" :key="service.name"
                class="p-6 rounded-lg border flex flex-col justify-between"
                :class="service.status === 'Betriebsbereit' ? 'status-active' : 'status-error'">
                <div>
                  <p class="font-medium text-gray-900">{{ service.name }}</p>
                  <p class="text-sm text-gray-600">
                    {{ service.uptime != null ? service.uptime + '%' : '–' }} Verfügbarkeit
                  </p>
                  <p v-if="service.latency_ms" class="text-sm text-gray-500">Latenz: {{ service.latency_ms }} ms</p>
                </div>
                <span class="badge"
                  :class="service.status === 'Betriebsbereit' ? 'badge-success' : 'badge-danger'">
                  {{ service.status }}
                </span>
              </div>
            </div>
          </div>

          <!-- Charts -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div class="card">
              <h3 class="h3">Benutzerwachstum</h3>
              <div class="chart-container">
                <svg
                  v-if="userGrowthSeries.length"
                  class="w-full h-full"
                  viewBox="0 0 100 100"
                  preserveAspectRatio="none"
                >
                  <defs>
                    <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
                      <path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(0,255,65,0.08)" stroke-width="0.3"/>
                    </pattern>
                  </defs>
                  <rect width="100" height="100" fill="url(#grid)" />
                  <polyline
                    :points="userGrowthPath"
                    fill="none"
                    stroke="#00ff41"
                    stroke-width="0.6"
                    stroke-linecap="square"
                    stroke-linejoin="miter"
                  />
                </svg>
                <span v-else class="text-green-400 font-mono text-sm">Keine Daten verfügbar</span>
              </div>
            </div>
            <div class="card">
              <h3 class="h3">API-Nutzung</h3>
              <div class="chart-container">
                <svg
                  v-if="apiUsageSeries.length"
                  class="w-full h-full"
                  viewBox="0 0 100 100"
                  preserveAspectRatio="none"
                >
                  <defs>
                    <pattern id="grid2" width="10" height="10" patternUnits="userSpaceOnUse">
                      <path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(0,255,65,0.08)" stroke-width="0.3"/>
                    </pattern>
                  </defs>
                  <rect width="100" height="100" fill="url(#grid2)" />
                  <polyline
                    :points="apiUsagePath"
                    fill="none"
                    stroke="#00ff41"
                    stroke-width="0.6"
                    stroke-linecap="square"
                    stroke-linejoin="miter"
                  />
                </svg>
                <span v-else class="text-green-400 font-mono text-sm">Keine Daten verfügbar</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- API Management Tab -->
      <div v-if="activeTab === 'api'" class="tab-content space-y-10">
        <p v-if="hydration.errors.apiKeys || hydration.errors.endpoints" class="error-message">
          {{ hydration.errors.apiKeys || hydration.errors.endpoints }}
        </p>

        <!-- API Keys -->
        <div class="card">
          <div class="card-header">
            <h3 class="h3">API-Schlüssel</h3>
            <button
              @click="generateApiKey"
              class="btn btn-primary"
              :disabled="!sectionsReady.api"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
              Neuer API-Schlüssel
            </button>
          </div>
          <div class="card-body">
            <div v-if="apiKeys.length" class="space-y-4">
              <div
                v-for="key in apiKeys"
                :key="key.id"
                class="list-item"
              >
                <div class="flex-1">
                  <div class="flex items-center gap-3">
                    <code class="code">{{ key.display }}</code>
                    <button
                      @click="copyKey(key)"
                      class="btn-icon"
                      :disabled="!sectionsReady.api"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                      </svg>
                    </button>
                  </div>
                  <div class="mt-2 flex items-center gap-4 text-sm text-gray-500">
                    <span>Erstellt: {{ key.created }}</span>
                    <span>Zuletzt verwendet: {{ key.lastUsed }}</span>
                    <span class="badge"
                      :class="key.active ? 'badge-success' : 'badge-secondary'"
                    >
                      {{ key.active ? 'Aktiv' : 'Inaktiv' }}
                    </span>
                  </div>
                </div>
                <button
                  @click="revokeKey(key.id)"
                  class="btn-icon btn-danger"
                  :disabled="!sectionsReady.api"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                </button>
              </div>
            </div>
            <p v-else class="empty-state">
              Noch keine API-Schlüssel vorhanden.
            </p>
          </div>
        </div>

        <!-- API Endpoints -->
        <div class="card">
          <div class="card-header">
            <h3 class="h3">API Endpunkte</h3>
            <p v-if="apiSummary" class="subtitle">
              {{ apiSummary.total }} Aufrufe in 7 Tagen • {{ apiSummary.errors }} Fehler gesamt
            </p>
          </div>
          <div class="divide-y divide-gray-200" v-if="apiEndpoints.length">
            <div v-for="endpoint in apiEndpoints" :key="`${endpoint.method}-${endpoint.path}`" class="list-item">
              <div class="flex-1">
                <div class="flex items-center gap-3">
                  <span class="badge"
                    :class="endpoint.method === 'GET' ? 'badge-info' : 
                            endpoint.method === 'POST' ? 'badge-success' : 
                            'badge-warning'"
                  >
                    {{ endpoint.method }}
                  </span>
                  <code class="code">{{ endpoint.path }}</code>
                </div>
                <div class="mt-2 flex items-center gap-4 text-sm text-gray-500">
                  <span>Aufrufe (7 Tage): {{ endpoint.call_count ?? 0 }}</span>
                  <span>Ø Latenz: {{ endpoint.avg_latency_ms ?? 0 }} ms</span>
                  <span>Peak pro Minute: {{ endpoint.peak_per_minute ?? 0 }}</span>
                </div>
              </div>
              <button
                class="btn btn-secondary"
                :disabled="!sectionsReady.api"
              >
                Testen
              </button>
            </div>
          </div>
          <p v-else class="empty-state">
            Es liegen noch keine Messwerte für API-Endpunkte vor.
          </p>
        </div>
      </div>

      <!-- Webhooks Tab -->
      <div v-if="activeTab === 'webhooks'" class="tab-content space-y-10">
        <div class="card">
          <div class="card-header">
            <h3 class="h3">Webhook-Konfiguration</h3>
            <button
              @click="openWebhookModal('create')"
              class="btn btn-primary"
              :disabled="!sectionsReady.webhooks"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
              Webhook erstellen
            </button>
          </div>
          <div class="card-body">
            <p v-if="hydration.errors.webhooks" class="error-message">
              {{ hydration.errors.webhooks }}
            </p>
            <div v-if="webhooks.length" class="space-y-4">
              <div v-for="webhook in webhooks" :key="webhook.id" class="list-item">
                <div class="flex-1">
                  <div class="flex items-center gap-3">
                    <h4 class="font-medium text-gray-900">{{ webhook.name }}</h4>
                    <span class="badge"
                      :class="webhook.isActive ? 'badge-success' : 'badge-secondary'"
                    >
                      {{ webhook.isActive ? 'Aktiv' : 'Pausiert' }}
                    </span>
                    <span v-if="webhook.hasSecret" class="text-xs text-gray-500">Signatur aktiv</span>
                  </div>
                  <code class="code block mt-2">{{ webhook.url }}</code>
                  <div class="mt-3 flex flex-wrap gap-2">
                    <span v-for="event in webhook.events" :key="event" 
                      class="badge badge-info">
                      {{ event }}
                    </span>
                  </div>
                </div>
                <div class="flex items-center gap-2 md:self-start">
                  <button
                    @click="testWebhook(webhook.id)"
                    class="btn-icon"
                    :disabled="!sectionsReady.webhooks"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                  </button>
                  <button
                    @click="openWebhookModal('edit', webhook)"
                    class="btn-icon"
                    :disabled="!sectionsReady.webhooks"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                    </svg>
                  </button>
                  <button
                    @click="deleteWebhook(webhook.id)"
                    class="btn-icon btn-danger"
                    :disabled="!sectionsReady.webhooks"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                  </button>
                </div>
                <!-- Webhook Logs -->
                <div class="mt-4 pt-4 border-t border-gray-200">
                  <div class="flex flex-col md:flex-row md:items-center gap-2 mb-2">
                    <span class="text-sm font-medium text-gray-700">Letzte Aufrufe</span>
                    <button class="text-sm text-blue-600 hover:text-blue-800">Alle anzeigen</button>
                  </div>
                  <div class="space-y-1">
                    <div v-for="log in webhook.recentLogs" :key="log.id" 
                      class="flex flex-col md:flex-row md:items-center gap-3 text-sm">
                      <span class="text-gray-600">{{ formatTime(log.timestamp) }}</span>
                      <span class="badge"
                        :class="log.status === 200 ? 'badge-success' : 'badge-danger'"
                      >
                        {{ log.status }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <p v-else class="empty-state">
              Noch keine Webhooks angelegt.
            </p>
          </div>
        </div>
      </div>

      <!-- Users Tab -->
      <div v-if="activeTab === 'users'" class="tab-content space-y-10">
        <!-- User Controls -->
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div class="flex flex-col gap-4 sm:flex-row sm:items-center">
            <div class="relative search-field">
              <input
                v-model="userSearch"
                type="text"
                placeholder="Benutzer suchen..."
                class="form-input"
                :disabled="!sectionsReady.users"
              >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
            </div>
            <select
              v-model="userFilter"
              class="form-select"
              :disabled="!sectionsReady.users"
            >
              <option value="all">Alle Rollen</option>
              <option value="admin">Administratoren</option>
              <option value="staff">Mitarbeiter</option>
              <option value="viewer">Betrachter</option>
            </select>
          </div>
          <button
            @click="showAddUserModal = true"
            class="btn btn-primary"
            :disabled="!sectionsReady.users"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/>
            </svg>
            Benutzer hinzufügen
          </button>
        </div>

        <p v-if="hydration.errors.users" class="error-message">
          {{ hydration.errors.users }}
        </p>

        <!-- User Table -->
        <div class="card">
          <div class="overflow-x-auto">
            <table class="table">
              <thead>
                <tr>
                  <th>Benutzer</th>
                  <th>Rolle</th>
                  <th>Status</th>
                  <th>Letzte Anmeldung</th>
                  <th>Aktionen</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in filteredUsers" :key="user.id">
                  <td>
                    <div class="flex items-center">
                      <div class="flex-shrink-0 h-10 w-10">
                        <div class="avatar">
                          <span>{{ user.initials }}</span>
                        </div>
                      </div>
                      <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">{{ user.name }}</div>
                        <div class="text-sm text-gray-500">{{ user.email }}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span class="badge"
                      :class="user.role === 'admin' ? 'badge-primary' : 
                              user.role === 'staff' ? 'badge-info' : 
                              'badge-secondary'"
                    >
                      {{ user.role }}
                    </span>
                  </td>
                  <td>
                    <span class="badge"
                      :class="user.isActive ? 'badge-success' : 'badge-danger'"
                    >
                      {{ user.isActive ? 'Aktiv' : 'Gesperrt' }}
                    </span>
                  </td>
                  <td>
                    {{ user.lastLogin }}
                  </td>
                  <td>
                    <div class="flex flex-wrap gap-2">
                      <button
                        v-if="user.role !== 'admin'"
                        @click="promoteToAdmin(user.id)"
                        class="btn-link"
                        :disabled="!sectionsReady.users"
                      >
                        Befördern
                      </button>
                      <button
                        v-else-if="user.id !== currentUserId"
                        @click="demoteFromAdmin(user.id)"
                        class="btn-link btn-warning"
                        :disabled="!sectionsReady.users"
                      >
                        Herabstufen
                      </button>
                      <button
                        @click="editUser(user.id)"
                        class="btn-link"
                        :disabled="!sectionsReady.users"
                      >
                        Bearbeiten
                      </button>
                      <button
                        @click="toggleUserStatus(user.id)"
                        class="btn"
                        :class="user.isActive ? 'btn-soft-danger' : 'btn-success'"
                        :disabled="!sectionsReady.users"
                      >
                        {{ user.isActive ? 'Sperren' : 'Aktivieren' }}
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="!filteredUsers.length">
                  <td colspan="5" class="empty-state">
                    Keine Benutzer gefunden.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- General Settings Tab -->
      <div v-if="activeTab === 'general'" class="tab-content space-y-10">
        <p v-if="hydration.errors.preferences" class="error-message">
          {{ hydration.errors.preferences }}
        </p>
        <!-- Platform Configuration -->
        <div class="card">
          <h3 class="h3">Plattform-Konfiguration</h3>
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <label class="form-label">Sprache</label>
              <select v-model="preferences.language" @change="onPreferenceChange" class="form-select" :disabled="!sectionsReady.preferences || preferencesLoading || preferencesSaving">
                <option value="de">Deutsch</option>
                <option value="en">Englisch</option>
                <option value="fr">Französisch</option>
              </select>
            </div>
            <div>
              <label class="form-label">Zeitzone</label>
              <select v-model="preferences.timezone" @change="onPreferenceChange" class="form-select" :disabled="!sectionsReady.preferences || preferencesLoading || preferencesSaving">
                <option value="Europe/Berlin">Europe/Berlin (UTC+1)</option>
                <option value="Europe/London">Europe/London (UTC+0)</option>
                <option value="America/New_York">America/New_York (UTC-5)</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Security Settings -->
        <div class="card">
          <h3 class="h3">Sicherheitseinstellungen</h3>
          <div class="space-y-4">
            <div class="setting-item">
              <div>
                <h4 class="h4">Zwei-Faktor-Authentifizierung</h4>
                <p class="subtitle">Erfordert zusätzliche Verifizierung bei der Anmeldung</p>
              </div>
              <label class="switch">
                <input type="checkbox" v-model="preferences.require_two_factor" @change="onPreferenceChange" :disabled="!sectionsReady.preferences || preferencesLoading || preferencesSaving">
                <span class="slider"></span>
              </label>
            </div>
            <div class="setting-item">
              <div>
                <h4 class="h4">SSO-Integration</h4>
                <p class="subtitle">Anmeldung über Unternehmens-Identitätsanbieter</p>
              </div>
              <label class="switch">
                <input type="checkbox" v-model="preferences.enable_sso" @change="onPreferenceChange" :disabled="!sectionsReady.preferences || preferencesLoading || preferencesSaving">
                <span class="slider"></span>
              </label>
            </div>
            <div>
              <h4 class="h4">Passwort-Richtlinien</h4>
              <div class="space-y-2">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="preferences.password_min_length" @change="onPreferenceChange" :disabled="!sectionsReady.preferences || preferencesLoading || preferencesSaving">
                  <span>Mindestens 12 Zeichen</span>
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" v-model="preferences.password_require_special" @change="onPreferenceChange" :disabled="!sectionsReady.preferences || preferencesLoading || preferencesSaving">
                  <span>Sonderzeichen erforderlich</span>
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" v-model="preferences.password_require_numbers" @change="onPreferenceChange" :disabled="!sectionsReady.preferences || preferencesLoading || preferencesSaving">
                  <span>Zahlen erforderlich</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Data Export -->
        <div class="card">
          <h3 class="h3">Datenexport</h3>
          <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-5">
            <div>
              <p class="subtitle">Exportieren Sie alle Plattformdaten für Audits oder Backups</p>
            </div>
            <div class="flex items-center gap-3">
              <button @click="exportCsv" class="btn btn-secondary" :disabled="!sectionsReady.preferences">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                </svg>
                CSV-Export
              </button>
              <button @click="exportJson" class="btn btn-secondary" :disabled="!sectionsReady.preferences">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                </svg>
                JSON-Export
              </button>
            </div>
          </div>
        </div>
      </div>
      </main>
    </div>

    <!-- Webhook Modal -->
    <div v-if="showWebhookModal" class="modal-overlay show">
      <div class="modal">
        <div class="modal-header">
          <h3 class="modal-title">
            {{ webhookModalMode === 'edit' ? 'Webhook bearbeiten' : 'Webhook erstellen' }}
          </h3>
          <button class="modal-close" @click="showWebhookModal = false">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <form @submit.prevent="submitWebhook" class="modal-body">
          <div>
            <label class="form-label">Name</label>
            <input v-model="webhookForm.name" type="text" required class="form-input" placeholder="z.B. Slack-Benachrichtigungen"/>
          </div>
          <div>
            <label class="form-label">URL</label>
            <input v-model="webhookForm.url" type="url" required class="form-input" placeholder="https://"/>
          </div>
          <div>
            <label class="form-label">Events</label>
            <textarea v-model="webhookForm.eventsText" rows="2" class="form-input" placeholder="document.created document.updated"></textarea>
            <p class="form-help">Mehrere Events durch Leerzeichen oder Komma trennen.</p>
          </div>
          <div>
            <label class="form-label">Geheimes Token (optional)</label>
            <input v-model="webhookForm.secret" type="text" class="form-input" placeholder="Wird zur Signierung verwendet"/>
          </div>
          <div class="modal-footer">
            <div class="flex items-center gap-2">
              <label class="switch">
                <input type="checkbox" v-model="webhookForm.isActive">
                <span class="slider"></span>
              </label>
              <span class="text-sm text-gray-700">Aktiv</span>
            </div>
            <div class="flex items-center gap-2">
              <button type="button" class="btn btn-secondary" @click="showWebhookModal = false">Abbrechen</button>
              <button type="submit" class="btn btn-primary" :disabled="webhookSubmitting">
                {{ webhookSubmitting ? 'Speichern…' : 'Speichern' }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- Confirmation Modal -->
    <div v-if="showConfirmModal" class="modal-overlay show">
      <div class="modal">
        <div class="modal-body text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100">
            <svg class="h-6 w-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
          </div>
          <h3 class="h3 mt-4">{{ confirmModal.title }}</h3>
          <div class="mt-2 px-7 py-3">
            <p class="text-sm text-gray-500">{{ confirmModal.message }}</p>
          </div>
          <div class="modal-footer">
            <button @click="confirmAction" class="btn btn-danger">
              Bestätigen
            </button>
            <button @click="showConfirmModal = false" class="btn btn-secondary">
              Abbrechen
            </button>
          </div>
        </div>
      </div>
    </div>
  </PortalShell>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import PortalShell from '~/components/PortalShell.vue'
import { useSettingsHydration } from '~/composables/useSettingsData'

definePageMeta({ layout: false })

// Auth helpers
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

  const readFromLocalStorage = () => {
    try {
      if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
        return ''
      }
      for (const key of storageKeys) {
        const value = localStorage.getItem(key)
        if (value) {
          return value
        }
      }
    } catch (err) {
      console.warn('Failed to retrieve auth token from localStorage', err)
    }
    return ''
  }

  const token = readFromLocalStorage() || readFromCookies()
  return token || ''
}

const getAuthHeaders = () => {
  const token = getAuthToken()
  if (!token) return {}
  const bearer = token.startsWith('Bearer ') ? token : `Bearer ${token}`
  return {
    'Authorization': bearer,
    'X-Portal-Auth': bearer
  }
}

// Tab management
const activeTab = ref('analytics')
const tabs = ref([
  { 
    id: 'analytics', 
    name: 'Analytics & Metriken', 
    iconPath: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
    badge: 'Live', 
    badgeClass: 'bg-green-100 text-green-800' 
  },
  { 
    id: 'api', 
    name: 'API-Verwaltung', 
    iconPath: 'M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4'
  },
  { 
    id: 'webhooks', 
    name: 'Webhooks', 
    iconPath: 'M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1',
    badge: null, 
    badgeClass: 'bg-blue-100 text-blue-800' 
  },
  { 
    id: 'users', 
    name: 'Benutzer & Rollen', 
    iconPath: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z'
  },
  { 
    id: 'general', 
    name: 'Allgemeine Einstellungen', 
    iconPath: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z'
  }
])

// Analytics & overview state
const lastUpdate = ref('')
const overviewLoading = ref(false)
const kpis = ref([])
const systemHealth = ref([])
const userGrowthSeries = ref([])
const apiUsageSeries = ref([])
const overviewMeta = ref(null)

// Charts helpers
const buildSparkline = (series) => {
  if (!series || !series.length) return ''
  const values = series.map((point) => Number(point.value) || 0)
  const max = Math.max(...values)
  const min = Math.min(...values)
  const range = max - min || 1
  const denominator = series.length > 1 ? series.length - 1 : 1
  return series
    .map((point, index) => {
      const x = (index / denominator) * 100
      const y = 100 - (((Number(point.value) || 0) - min) / range) * 100
      return `${x.toFixed(2)},${y.toFixed(2)}`
    })
    .join(' ')
}

const userGrowthPath = computed(() => buildSparkline(userGrowthSeries.value))
const apiUsagePath = computed(() => buildSparkline(apiUsageSeries.value))

// API management state
const apiKeys = ref([])
const apiKeysLoading = ref(false)
const recentTokenSecret = ref(null)

const apiEndpoints = ref([])
const apiEndpointsLoading = ref(false)

// Webhook state
const webhooks = ref([])
const webhooksLoading = ref(false)
const showWebhookModal = ref(false)
const webhookModalMode = ref('create')
const webhookSubmitting = ref(false)
const webhookForm = reactive({
  id: null,
  name: '',
  url: '',
  eventsText: '',
  isActive: true,
  secret: ''
})

// User management state
const currentUserId = ref(null)
const userSearch = ref('')
const userFilter = ref('all')
const users = ref([])
const usersLoading = ref(false)
const usersPagination = reactive({ page: 1, pageSize: 25, total: 0 })
let searchDebounce = null

const filteredUsers = computed(() => users.value)

// Preferences state
const preferences = reactive({
  language: 'de',
  timezone: 'Europe/Berlin',
  require_two_factor: false,
  enable_sso: false,
  password_min_length: true,
  password_require_special: true,
  password_require_numbers: true,
  email_notifications: true,
  browser_notifications: false,
  ai_updates: true,
  ai_model: 'qwen_legal_q4_k_m',
  ai_creativity: 70,
  auto_save: true
})
const preferencesLoading = ref(false)
const preferencesSaving = ref(false)

// Modals
const showConfirmModal = ref(false)
const confirmModal = ref({
  title: '',
  message: '',
  action: null
})
const showAddUserModal = ref(false)

const formatNumber = (value) => {
  const numeric = Number(value) || 0
  return numeric.toLocaleString('de-DE')
}

const formatDate = (iso) => {
  if (!iso) return '–'
  return new Date(iso).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const formatTime = (iso) => {
  if (!iso) return '–'
  return new Date(iso).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
}

const relativeTime = (iso) => {
  if (!iso) return 'Noch nie'
  const date = new Date(iso)
  const diff = Date.now() - date.getTime()
  const rtf = new Intl.RelativeTimeFormat('de', { style: 'long' })
  const minutes = Math.round(diff / 60000)
  if (Math.abs(minutes) < 60) return rtf.format(-minutes, 'minute')
  const hours = Math.round(minutes / 60)
  if (Math.abs(hours) < 24) return rtf.format(-hours, 'hour')
  const days = Math.round(hours / 24)
  if (Math.abs(days) < 30) return rtf.format(-days, 'day')
  const months = Math.round(days / 30)
  return rtf.format(-months, 'month')
}

const initialsFor = (name) => {
  if (!name) return '??'
  const parts = name.split(' ').filter(Boolean)
  if (!parts.length) return name.slice(0, 2).toUpperCase()
  const letters = parts.slice(0, 2).map((part) => part[0])
  return letters.join('').toUpperCase()
}

const hydration = useSettingsHydration()

const sectionsReady = computed(() => ({
  overview: hydration.pending.overview === false,
  api: hydration.pending.apiKeys === false && hydration.pending.endpoints === false,
  webhooks: hydration.pending.webhooks === false,
  users: hydration.pending.users === false,
  preferences: hydration.pending.preferences === false
}))

const refreshing = computed(() => hydration.busySegments.value > 0)

const apiSummary = computed(() => {
  const meta = overviewMeta.value
  if (!meta?.api) return null
  const successRate = typeof meta.api.success_rate === 'number' ? meta.api.success_rate.toFixed(1) : null
  const avgLatency = typeof meta.api.avg_latency_ms === 'number' ? Math.round(meta.api.avg_latency_ms) : null
  return {
    successRate,
    avgLatency,
    total: meta.api.total_current ?? 0,
    errors: meta.api.error_calls ?? 0,
    lastSeen: meta.api.last_seen ?? null
  }
})

const loadOverview = async () => {
  hydration.start('overview')
  overviewLoading.value = true
  try {
    const data = await $fetch('/api/settings/overview', {
      headers: getAuthHeaders()
    })
    kpis.value = (data?.kpis || []).map((item) => ({
      ...item,
      value: item.value ?? formatNumber(0),
      change: Number(item.change ?? 0)
    }))
    systemHealth.value = data?.systemHealth || []
    overviewMeta.value = data?.meta || null
    userGrowthSeries.value = data?.userGrowth || []
    apiUsageSeries.value = data?.apiUsage || []
    lastUpdate.value = data?.generatedAt
      ? new Date(data.generatedAt).toLocaleString('de-DE')
      : new Date().toLocaleString('de-DE')
  } catch (error) {
    console.error('Fehler beim Laden der Übersicht', error)
    overviewMeta.value = null
    hydration.fail('overview', 'Übersicht konnte nicht geladen werden')
  } finally {
    overviewLoading.value = false
    hydration.finish('overview')
  }
}

const loadApiTokens = async () => {
  hydration.start('apiKeys')
  apiKeysLoading.value = true
  try {
    const response = await $fetch('/api/settings/api/tokens', {
      headers: getAuthHeaders()
    })
    apiKeys.value = (response?.tokens || []).map((token) => ({
      id: token.id,
      display: `anw_••••${token.last4 || '0000'}`,
      created: token.created_at ? formatDate(token.created_at) : '–',
      lastUsed: token.last_used_at ? relativeTime(token.last_used_at) : 'Noch nie',
      active: token.active !== false,
      secret: null,
      last4: token.last4
    }))
  } catch (error) {
    console.error('API-Schlüssel konnten nicht geladen werden', error)
    hydration.fail('apiKeys', 'API-Schlüssel konnten nicht geladen werden')
  } finally {
    apiKeysLoading.value = false
    hydration.finish('apiKeys')
  }
}

const loadApiEndpoints = async () => {
  hydration.start('endpoints')
  apiEndpointsLoading.value = true
  try {
    const response = await $fetch('/api/settings/api/endpoints', {
      headers: getAuthHeaders()
    })
    apiEndpoints.value = response?.metrics || []
  } catch (error) {
    console.error('API-Endpunkte konnten nicht geladen werden', error)
    hydration.fail('endpoints', 'API-Endpunkte konnten nicht geladen werden')
  } finally {
    apiEndpointsLoading.value = false
    hydration.finish('endpoints')
  }
}

const loadWebhooks = async () => {
  hydration.start('webhooks')
  webhooksLoading.value = true
  try {
    const response = await $fetch('/api/settings/webhooks', {
      headers: getAuthHeaders()
    })
    webhooks.value = (response?.webhooks || []).map((webhook) => ({
      id: webhook.id,
      name: webhook.name,
      url: webhook.url,
      events: webhook.events || [],
      isActive: webhook.is_active !== false,
      hasSecret: webhook.has_secret || false,
      createdAt: webhook.created_at,
      recentLogs: (webhook.recent_logs || webhook.recentLogs || []).map((log) => ({
        id: log.id,
        status: log.status ?? log.status_code,
        latency: log.latency_ms,
        response: log.response,
        timestamp: log.timestamp || log.created_at
      }))
    }))
    const webhookTab = tabs.value.find((tab) => tab.id === 'webhooks')
    if (webhookTab) webhookTab.badge = String(webhooks.value.length)
  } catch (error) {
    console.error('Webhooks konnten nicht geladen werden', error)
    hydration.fail('webhooks', 'Webhooks konnten nicht geladen werden')
  } finally {
    webhooksLoading.value = false
    hydration.finish('webhooks')
  }
}

const loadUsers = async (page = usersPagination.page) => {
  hydration.start('users')
  usersLoading.value = true
  try {
    const response = await $fetch('/api/settings/users', {
      headers: getAuthHeaders(),
      query: {
        search: userSearch.value || undefined,
        role: userFilter.value || undefined,
        page,
        page_size: usersPagination.pageSize
      }
    })
    usersPagination.page = response?.page || page
    usersPagination.total = response?.total || 0
    users.value = (response?.users || []).map((user) => ({
      id: user.id,
      name: user.name,
      email: user.email,
      role: user.role,
      isActive: user.is_active !== false,
      lastLogin: user.last_activity ? relativeTime(user.last_activity) : 'Noch nie',
      initials: initialsFor(user.name)
    }))
  } catch (error) {
    console.error('Benutzer konnten nicht geladen werden', error)
    hydration.fail('users', 'Benutzer konnten nicht geladen werden')
  } finally {
    usersLoading.value = false
    hydration.finish('users')
  }
}

const loadPreferences = async () => {
  hydration.start('preferences')
  preferencesLoading.value = true
  try {
    const response = await $fetch('/api/settings/preferences', {
      headers: getAuthHeaders()
    })
    Object.assign(preferences, response?.preferences || {})
  } catch (error) {
    console.error('Einstellungen konnten nicht geladen werden', error)
    hydration.fail('preferences', 'Einstellungen konnten nicht geladen werden')
  } finally {
    preferencesLoading.value = false
    hydration.finish('preferences')
  }
}

const refreshData = async () => {
  hydration.reset()
  await Promise.all([
    loadOverview(),
    loadApiTokens(),
    loadApiEndpoints(),
    loadWebhooks(),
    loadUsers(1),
    loadPreferences()
  ])
}

const generateApiKey = async () => {
  if (!sectionsReady.value.api) return
  try {
    const response = await $fetch('/api/settings/api/tokens', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: { expires_in_days: 365 }
    })
    const secret = response?.token
    recentTokenSecret.value = secret
    apiKeys.value.unshift({
      id: response?.metadata?.id,
      display: `anw_••••${response?.metadata?.last4 || '0000'}`,
      created: formatDate(response?.metadata?.created_at),
      lastUsed: 'Noch nie',
      active: true,
      secret,
      last4: response?.metadata?.last4
    })
    if (secret && typeof window !== 'undefined') {
      window.setTimeout(() => {
        window.alert(`Neuer API-Schlüssel:

${secret}

Bitte sicher speichern. Nach dem Schließen ist er nicht mehr einsehbar.`)
      })
    }
  } catch (error) {
    console.error('API-Schlüssel konnte nicht erstellt werden', error)
  }
}

const copyKey = async (entry) => {
  if (!entry.secret) {
    if (typeof window !== 'undefined') {
      window.alert('Der vollständige Schlüssel ist nach dem Erstellen nicht mehr abrufbar.')
    }
    return
  }
  try {
    await navigator.clipboard.writeText(entry.secret)
  } catch (error) {
    console.error('Kopieren fehlgeschlagen', error)
  }
}

const revokeKey = (id) => {
  confirmModal.value = {
    title: 'API-Schlüssel widerrufen',
    message: 'Sind Sie sicher, dass Sie diesen API-Schlüssel widerrufen möchten?',
    action: async () => {
      try {
        await $fetch(`/api/settings/api/tokens/${id}`, {
          method: 'DELETE',
          headers: getAuthHeaders()
        })
        await loadApiTokens()
      } catch (error) {
        console.error('Schlüssel konnte nicht widerrufen werden', error)
      }
    }
  }
  showConfirmModal.value = true
}

const submitWebhook = async () => {
  webhookSubmitting.value = true
  try {
    const payload = {
      name: webhookForm.name,
      url: webhookForm.url,
      events: webhookForm.eventsText
        .split(/[\s,]+/)
        .map((event) => event.trim())
        .filter(Boolean),
      is_active: webhookForm.isActive,
      secret: webhookForm.secret || undefined
    }
    if (webhookModalMode.value === 'edit' && webhookForm.id) {
      await $fetch(`/api/settings/webhooks/${webhookForm.id}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: payload
      })
    } else {
      await $fetch('/api/settings/webhooks', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: payload
      })
    }
    await loadWebhooks()
    showWebhookModal.value = false
  } catch (error) {
    console.error('Webhook konnte nicht gespeichert werden', error)
  } finally {
    webhookSubmitting.value = false
  }
}

const openWebhookModal = (mode = 'create', webhook = null) => {
  webhookModalMode.value = mode
  if (webhook) {
    webhookForm.id = webhook.id
    webhookForm.name = webhook.name
    webhookForm.url = webhook.url
    webhookForm.eventsText = webhook.events.join(', ')
    webhookForm.isActive = webhook.isActive
    webhookForm.secret = ''
  } else {
    webhookForm.id = null
    webhookForm.name = ''
    webhookForm.url = ''
    webhookForm.eventsText = ''
    webhookForm.isActive = true
    webhookForm.secret = ''
  }
  showWebhookModal.value = true
}

const deleteWebhook = (id) => {
  confirmModal.value = {
    title: 'Webhook löschen',
    message: 'Möchten Sie diesen Webhook wirklich entfernen?',
    action: async () => {
      try {
        await $fetch(`/api/settings/webhooks/${id}`, {
          method: 'DELETE',
          headers: getAuthHeaders()
        })
        await loadWebhooks()
      } catch (error) {
        console.error('Webhook konnte nicht gelöscht werden', error)
      }
    }
  }
  showConfirmModal.value = true
}

const testWebhook = async (id) => {
  try {
    const result = await $fetch(`/api/settings/webhooks/${id}/test`, {
      method: 'POST',
      headers: getAuthHeaders()
    })
    if (typeof window !== 'undefined') {
      window.alert(`Webhook-Test abgeschlossen:
Status: ${result.status ?? 'n/a'}
Antwortzeit: ${result.latency_ms ?? 'n/a'} ms`)
    }
    await loadWebhooks()
  } catch (error) {
    console.error('Webhook-Test fehlgeschlagen', error)
  }
}

const promoteToAdmin = (id) => {
  confirmModal.value = {
    title: 'Benutzer befördern',
    message: 'Soll dieser Benutzer Administratorrechte erhalten?',
    action: () => updateUserRole(id, 'admin')
  }
  showConfirmModal.value = true
}

const demoteFromAdmin = (id) => {
  confirmModal.value = {
    title: 'Administratorrechte entziehen',
    message: 'Administratorrechte wirklich entziehen?',
    action: () => updateUserRole(id, 'staff')
  }
  showConfirmModal.value = true
}

const updateUserRole = async (id, role) => {
  try {
    await $fetch(`/api/settings/users/${id}/role`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: { role }
    })
    await loadUsers(usersPagination.page)
  } catch (error) {
    console.error('Rolle konnte nicht aktualisiert werden', error)
  }
}

const editUser = (id) => {
  console.info('Benutzerbearbeitung folgt', id)
}

const toggleUserStatus = (id) => {
  const user = users.value.find((entry) => entry.id === id)
  if (!user) return
  confirmModal.value = {
    title: user.isActive ? 'Benutzer sperren' : 'Benutzer aktivieren',
    message: user.isActive
      ? 'Der Benutzer kann sich danach nicht mehr anmelden.'
      : 'Der Benutzer kann sich danach wieder anmelden.',
    action: async () => {
      try {
        await $fetch(`/api/settings/users/${id}/toggle`, {
          method: 'POST',
          headers: getAuthHeaders(),
          body: { active: !user.isActive }
        })
        await loadUsers(usersPagination.page)
      } catch (error) {
        console.error('Benutzerstatus konnte nicht angepasst werden', error)
      }
    }
  }
  showConfirmModal.value = true
}

const confirmAction = async () => {
  if (confirmModal.value.action) {
    await confirmModal.value.action()
  }
  showConfirmModal.value = false
}

const savePreferences = async () => {
  if (preferencesLoading.value || !sectionsReady.value.preferences) return
  preferencesSaving.value = true
  try {
    await $fetch('/api/settings/preferences', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: preferences
    })
  } catch (error) {
    console.error('Einstellungen konnten nicht gespeichert werden', error)
  } finally {
    preferencesSaving.value = false
  }
}

const onPreferenceChange = () => {
  savePreferences()
}

const exportCsv = async () => {
  if (!sectionsReady.value.preferences) return
  if (typeof window === 'undefined') return
  try {
    const response = await fetch('/api/settings/export.csv', {
      credentials: 'include',
      headers: getAuthHeaders()
    })
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'anwalts-settings-export.csv'
    link.click()
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('CSV-Export fehlgeschlagen', error)
  }
}

const exportJson = async () => {
  if (!sectionsReady.value.preferences) return
  if (typeof window === 'undefined') return
  try {
    const response = await fetch('/api/settings/export.json', {
      credentials: 'include',
      headers: getAuthHeaders()
    })
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'anwalts-settings-export.json'
    link.click()
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('JSON-Export fehlgeschlagen', error)
  }
}

watch([userFilter, userSearch], () => {
  if (searchDebounce) clearTimeout(searchDebounce)
  searchDebounce = setTimeout(() => loadUsers(1), 300)
})

onMounted(async () => {
  await refreshData()
})

</script>

<style scoped>
.main-content {
  width: 100%;
  background: linear-gradient(180deg, rgba(243, 245, 251, 0.9) 0%, rgba(255, 255, 255, 0.95) 42%, #ffffff 100%);
  padding: 0 clamp(1.5rem, 4vw, 2.5rem) clamp(3rem, 6vw, 4rem);
}

.main-container {
  width: 100%;
  max-width: 1240px;
  margin: 0 auto;
  padding: clamp(1.75rem, 3vw, 2.75rem) clamp(1.75rem, 5vw, 3rem) clamp(2.75rem, 5vw, 3.5rem);
  background-color: #ffffff;
  border-radius: 28px;
  box-shadow: 0 24px 60px rgba(18, 26, 64, 0.06);
  border: 1px solid rgba(79, 99, 222, 0.08);
}

.main-container p {
  line-height: 1.6;
}

.tab-content {
  display: flex;
  flex-direction: column;
  gap: clamp(2rem, 3vw, 2.75rem);
  margin-top: 1.75rem;
  padding-bottom: 2.5rem;
}

.tab-content > .card,
.tab-content > .flex,
.tab-content > .grid {
  margin: 0;
}

.card h3,
.card .subtitle {
  margin-bottom: 0.75rem;
}

.error-message {
  font-size: var(--text-sm);
  color: var(--error-500);
  margin-bottom: 1.5rem;
}

.list-item {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.25rem 1.5rem;
  background-color: var(--surface);
  box-shadow: var(--shadow-sm);
}

@media (min-width: 768px) {
  .list-item {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.code {
  font-family: monospace;
  background-color: var(--neutral-100);
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm);
}

.empty-state {
  font-size: var(--text-sm);
  color: var(--text-strong);
}

.table {
  min-width: 680px;
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 1rem 1.5rem;
  text-align: left;
  border-bottom: 1px solid var(--border);
}

.table th {
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  color: var(--text-strong);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background-color: var(--neutral-50);
}

.avatar {
  height: 2.5rem;
  width: 2.5rem;
  border-radius: 9999px;
  background-color: var(--neutral-200);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar span {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-strong);
}

.btn-link {
  color: var(--primary-strong);
  text-decoration: none;
}

.btn-link:hover {
  text-decoration: underline;
}

.btn-link.btn-warning {
  color: var(--warning-600);
}

.btn-link.btn-danger {
  color: var(--error-600);
}

.btn-link.btn-success {
  color: var(--success-600);
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border-radius: var(--radius-lg);
  font-weight: var(--font-semibold);
  padding: 0.55rem 1.25rem;
  box-shadow: var(--shadow-sm);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.btn svg {
  width: 1rem;
  height: 1rem;
}

.btn-primary {
  background: linear-gradient(135deg, #4f63de, #6e8bff);
  color: #ffffff;
  border: none;
  box-shadow: 0 12px 24px rgba(79, 99, 222, 0.22);
}

.btn-primary:hover {
  background: linear-gradient(135deg, #4257d2, #5f7eed);
  transform: translateY(-1px);
  box-shadow: 0 16px 32px rgba(79, 99, 222, 0.26);
}

.btn-secondary {
  background: #1f2c4f;
  color: #ffffff;
  border: none;
}

.btn-secondary:hover {
  background: #1a2646;
  transform: translateY(-1px);
}

.btn-danger {
  background: linear-gradient(135deg, #ef4444, #b91c1c);
  color: #ffffff;
  border: none;
  box-shadow: 0 12px 24px rgba(239, 68, 68, 0.2);
}

.btn-danger:hover {
  background: linear-gradient(135deg, #dc2626, #991b1b);
  transform: translateY(-1px);
}

.btn-soft-danger {
  background: rgba(239, 68, 68, 0.12);
  color: #b91c1c;
  border: 1px solid rgba(239, 68, 68, 0.35);
  box-shadow: 0 10px 20px rgba(239, 68, 68, 0.1);
}

.btn-soft-danger:hover {
  background: rgba(220, 38, 38, 0.18);
  border-color: rgba(220, 38, 38, 0.45);
  transform: translateY(-1px);
  box-shadow: 0 12px 28px rgba(220, 38, 38, 0.16);
}

.btn-success {
  background: linear-gradient(135deg, #16a34a, #15803d);
  color: #ffffff;
  border: none;
  box-shadow: 0 12px 24px rgba(22, 163, 74, 0.2);
}

.btn-success:hover {
  background: linear-gradient(135deg, #15803d, #166534);
  transform: translateY(-1px);
  box-shadow: 0 16px 32px rgba(22, 163, 74, 0.24);
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background-color: var(--neutral-50);
  box-shadow: var(--shadow-sm);
}

@media (min-width: 768px) {
  .setting-item {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.switch {
  position: relative;
  display: inline-block;
  width: 2.75rem;
  height: 1.5rem;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--neutral-200);
  transition: 0.4s;
  border-radius: 1.5rem;
}

.slider:before {
  position: absolute;
  content: "";
  height: 1.25rem;
  width: 1.25rem;
  left: 0.125rem;
  bottom: 0.125rem;
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: var(--primary-600);
}

input:focus + .slider {
  box-shadow: 0 0 1px var(--primary-600);
}

input:checked + .slider:before {
  transform: translateX(1.25rem);
}

.checkbox-label {
  display: flex;
  align-items: center;
}

.checkbox-label input {
  margin-right: 0.5rem;
}

.form-help {
  font-size: var(--text-xs);
  color: var(--text-strong);
  margin-top: 0.25rem;
}

.search-field svg {
  position: absolute;
  pointer-events: none;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--neutral-500);
}

.search-field .form-input {
  padding-left: 2.75rem;
}

.search-field .form-input:disabled {
  padding-left: 2.75rem;
}

@media (max-width: 1280px) {
  .main-content {
    padding: 0 clamp(1.25rem, 3vw, 2rem) clamp(2.75rem, 5vw, 3.5rem);
  }

  .main-container {
    border-radius: 24px;
    padding: clamp(1.75rem, 3vw, 2.25rem) clamp(1.5rem, 4vw, 2.5rem) clamp(2.5rem, 5vw, 3rem);
  }
}

@media (max-width: 900px) {
  .main-content {
    padding: 0 1.5rem 3rem;
  }

  .main-container {
    padding: 1.75rem 1.75rem 2.75rem;
  }

  .table {
    min-width: initial;
  }
}

@media (max-width: 640px) {
  .main-content {
    padding: 0 1rem 2.5rem;
  }

  .main-container {
    padding: 1.5rem 1.25rem 2.5rem;
    border-radius: 20px;
  }

  .tab-content {
    gap: 2rem;
    margin-top: 1.25rem;
  }

  .list-item,
  .setting-item {
    padding: 1.1rem 1.25rem;
  }
}
</style>
