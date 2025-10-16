<template>
  <PortalShell>
    <template #header>
      <!-- Header -->
      <header class="bg-white border-b border-gray-200">
        <div class="px-8 py-4">
          <div class="responsive-stack">
            <div class="flex items-center gap-4">
              <NuxtLink to="/dashboard" class="text-gray-500 hover:text-gray-700">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
                </svg>
              </NuxtLink>
              <div>
                <h1 class="text-2xl font-semibold text-gray-900">Systemeinstellungen</h1>
                <p class="text-sm text-gray-500">Verwaltung und Konfiguration der Plattform</p>
              </div>
            </div>
            <div class="flex items-center gap-3 self-start md:self-auto">
              <span class="text-sm text-gray-500 hidden sm:inline">Zuletzt aktualisiert: {{ lastUpdate }}</span>
              <button @click="refreshData" class="btn-secondary">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                </svg>
                Aktualisieren
              </button>
            </div>
          </div>
        </div>

        <!-- Tab Navigation -->
        <div class="border-t border-gray-200">
          <div class="px-8">
            <nav class="flex space-x-4 sm:space-x-8 overflow-x-auto" aria-label="Tabs">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                @click="activeTab = tab.id"
                :class="[
                  'py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap transition-colors',
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                ]"
              >
                <span class="flex items-center gap-2">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="tab.iconPath"/>
                  </svg>
                  {{ tab.name }}
                  <span v-if="tab.badge" class="ml-2 px-2 py-0.5 text-xs rounded-full"
                    :class="tab.badgeClass">{{ tab.badge }}</span>
                </span>
              </button>
            </nav>
          </div>
        </div>
      </header>
    </template>

    <div class="bg-gray-50 w-full">
    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Analytics & Metrics Tab -->
      <div v-if="activeTab === 'analytics'" class="settings-section">
        <!-- KPI Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          <div v-for="kpi in kpis" :key="kpi.label" class="card p-6">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600">{{ kpi.label }}</p>
                <p class="text-2xl font-semibold text-gray-900">{{ kpi.value }}</p>
                <p class="text-sm" :class="kpi.change > 0 ? 'text-green-600' : 'text-red-600'">
                  <span>{{ kpi.change > 0 ? '↑' : '↓' }} {{ Math.abs(kpi.change) }}%</span>
                  <span class="text-gray-500 ml-1">vs. letzte Woche</span>
                </p>
              </div>
              <div class="p-3 rounded-lg" :class="kpi.iconBg">
                <svg class="w-6 h-6" :class="kpi.iconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="kpi.iconPath"/>
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Charts -->
        <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <div class="card p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Benutzerwachstum</h3>
            <div class="h-80 bg-gray-100 rounded-lg flex items-center justify-center">
              <span class="text-gray-500">Diagramm-Platzhalter</span>
            </div>
          </div>
          <div class="card p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">API-Nutzung</h3>
            <div class="h-80 bg-gray-100 rounded-lg flex items-center justify-center">
              <span class="text-gray-500">Diagramm-Platzhalter</span>
            </div>
          </div>
        </div>

        <!-- System Health -->
        <div class="card p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Systemstatus</h3>
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div v-for="service in systemHealth" :key="service.name" 
              class="responsive-stack status-row p-4 rounded-lg border"
              :class="service.status === 'Betriebsbereit' ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'">
              <div>
                <p class="font-medium text-gray-900">{{ service.name }}</p>
                <p class="text-sm text-gray-600">{{ service.uptime }}% Verfügbarkeit</p>
              </div>
              <span class="px-2 py-1 text-xs font-medium rounded-full"
                :class="service.status === 'Betriebsbereit' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                {{ service.status }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- API Management Tab -->
      <div v-if="activeTab === 'api'" class="settings-section">
        <!-- API Keys -->
        <div class="card">
          <div class="p-6 border-b border-gray-200">
            <div class="responsive-stack card-header-content">
              <h3 class="text-lg font-medium text-gray-900">API-Schlüssel</h3>
              <button @click="generateApiKey" class="btn-primary">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                </svg>
                Neuer API-Schlüssel
              </button>
            </div>
          </div>
          <div class="p-6">
            <div class="space-y-4">
              <div v-for="key in apiKeys" :key="key.id" 
                class="responsive-stack api-key-row">
                <div class="flex-1">
                  <div class="flex items-center gap-3">
                    <code class="text-sm font-mono bg-gray-100 px-2 py-1 rounded">{{ key.key }}</code>
                    <button @click="copyKey(key.key)" class="text-gray-400 hover:text-gray-600">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                      </svg>
                    </button>
                  </div>
                  <div class="mt-2 flex items-center gap-4 text-sm text-gray-500">
                    <span>Erstellt: {{ key.created }}</span>
                    <span>Zuletzt verwendet: {{ key.lastUsed }}</span>
                    <span class="px-2 py-0.5 rounded-full text-xs font-medium"
                      :class="key.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'">
                      {{ key.active ? 'Aktiv' : 'Inaktiv' }}
                    </span>
                  </div>
                </div>
                <button @click="revokeKey(key.id)" class="text-red-600 hover:text-red-800 md:self-center">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- API Endpoints -->
        <div class="card">
          <div class="p-6 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">API Endpunkte</h3>
          </div>
          <div class="divide-y divide-gray-200">
            <div v-for="endpoint in apiEndpoints" :key="endpoint.path" class="p-6">
              <div class="responsive-stack-start endpoint-row">
                <div class="flex-1">
                  <div class="flex items-center gap-3">
                    <span class="px-2 py-1 text-xs font-medium rounded"
                      :class="endpoint.method === 'GET' ? 'bg-blue-100 text-blue-800' : 
                              endpoint.method === 'POST' ? 'bg-green-100 text-green-800' : 
                              'bg-yellow-100 text-yellow-800'">
                      {{ endpoint.method }}
                    </span>
                    <code class="text-sm font-mono">{{ endpoint.path }}</code>
                  </div>
                  <p class="mt-2 text-sm text-gray-600">{{ endpoint.description }}</p>
                  <div class="mt-2 flex items-center gap-4 text-sm text-gray-500">
                    <span>Ratenlimit: {{ endpoint.rateLimit }}/min</span>
                    <span>Durchschn. Antwort: {{ endpoint.avgResponse }}ms</span>
                  </div>
                </div>
                <button class="text-blue-600 hover:text-blue-800 text-sm md:self-center">Testen</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Webhooks Tab -->
      <div v-if="activeTab === 'webhooks'" class="settings-section">
        <div class="card">
          <div class="p-6 border-b border-gray-200">
            <div class="responsive-stack card-header-content">
              <h3 class="text-lg font-medium text-gray-900">Webhook-Konfiguration</h3>
              <button @click="showWebhookModal = true" class="btn-primary">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                </svg>
                Webhook erstellen
              </button>
            </div>
          </div>
          <div class="p-6">
            <div class="space-y-4">
              <div v-for="webhook in webhooks" :key="webhook.id" class="webhook-card">
                <div class="p-4">
                  <div class="responsive-stack-start webhook-row">
                    <div class="flex-1">
                      <div class="flex items-center gap-3">
                        <h4 class="font-medium text-gray-900">{{ webhook.name }}</h4>
                        <span class="px-2 py-0.5 text-xs font-medium rounded-full"
                          :class="webhook.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'">
                          {{ webhook.active ? 'Aktiv' : 'Pausiert' }}
                        </span>
                      </div>
                      <code class="mt-2 text-sm text-gray-600 block">{{ webhook.url }}</code>
                      <div class="mt-3 flex flex-wrap gap-2">
                        <span v-for="event in webhook.events" :key="event" 
                          class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                          {{ event }}
                        </span>
                      </div>
                    </div>
                    <div class="flex items-center gap-2 md:self-start">
                      <button @click="testWebhook(webhook.id)" class="text-blue-600 hover:text-blue-800">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                      </button>
                      <button @click="editWebhook(webhook.id)" class="text-gray-600 hover:text-gray-800">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                        </svg>
                      </button>
                      <button @click="deleteWebhook(webhook.id)" class="text-red-600 hover:text-red-800">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                        </svg>
                      </button>
                    </div>
                  </div>
                  <!-- Webhook Logs -->
                  <div class="mt-4 pt-4 border-t border-gray-200">
                    <div class="responsive-stack log-header mb-2">
                      <span class="text-sm font-medium text-gray-700">Letzte Aufrufe</span>
                      <button class="text-sm text-blue-600 hover:text-blue-800">Alle anzeigen</button>
                    </div>
                    <div class="space-y-1">
                      <div v-for="log in webhook.recentLogs" :key="log.timestamp" 
                        class="responsive-stack log-row text-sm">
                        <span class="text-gray-600">{{ log.timestamp }}</span>
                        <span class="px-2 py-0.5 rounded text-xs font-medium"
                          :class="log.status === 200 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                          {{ log.status }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Users Tab -->
      <div v-if="activeTab === 'users'" class="settings-section">
        <!-- User Controls -->
        <div class="responsive-stack user-toolbar">
          <div class="flex flex-col gap-4 sm:flex-row sm:items-center">
            <div class="relative">
              <input v-model="userSearch" type="text" placeholder="Benutzer suchen..." 
                class="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
              <svg class="absolute left-3 top-2.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
            </div>
            <select v-model="userFilter" class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
              <option value="all">Alle Rollen</option>
              <option value="admin">Administratoren</option>
              <option value="staff">Mitarbeiter</option>
              <option value="viewer">Betrachter</option>
            </select>
          </div>
          <button @click="showAddUserModal = true" class="btn-primary self-start md:self-auto">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/>
            </svg>
            Benutzer hinzufügen
          </button>
        </div>

        <!-- User Table -->
        <div class="card overflow-hidden">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Benutzer
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rolle
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Letzte Anmeldung
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Aktionen
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="user in filteredUsers" :key="user.id">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10">
                      <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                        <span class="text-sm font-medium text-gray-700">{{ user.initials }}</span>
                      </div>
                    </div>
                    <div class="ml-4">
                      <div class="text-sm font-medium text-gray-900">{{ user.name }}</div>
                      <div class="text-sm text-gray-500">{{ user.email }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                    :class="user.role === 'admin' ? 'bg-purple-100 text-purple-800' : 
                            user.role === 'staff' ? 'bg-blue-100 text-blue-800' : 
                            'bg-gray-100 text-gray-800'">
                    {{ user.role }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                    :class="user.active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                    {{ user.active ? 'Aktiv' : 'Gesperrt' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ user.lastLogin }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div class="flex items-center gap-2">
                    <button v-if="user.role !== 'admin'" @click="promoteToAdmin(user.id)" 
                      class="text-purple-600 hover:text-purple-900">Befördern</button>
                    <button v-else-if="user.id !== currentUserId" @click="demoteFromAdmin(user.id)" 
                      class="text-orange-600 hover:text-orange-900">Herabstufen</button>
                    <button @click="editUser(user.id)" class="text-indigo-600 hover:text-indigo-900">Bearbeiten</button>
                    <button @click="toggleUserStatus(user.id)" 
                      :class="user.active ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'">
                      {{ user.active ? 'Sperren' : 'Aktivieren' }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- General Settings Tab -->
      <div v-if="activeTab === 'general'" class="settings-section">
        <!-- Platform Configuration -->
        <div class="card p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Plattform-Konfiguration</h3>
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Sprache</label>
              <select class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                <option>Deutsch</option>
                <option>Englisch</option>
                <option>Französisch</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Zeitzone</label>
              <select class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                <option>Europe/Berlin (UTC+1)</option>
                <option>Europe/London (UTC+0)</option>
                <option>America/New_York (UTC-5)</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Security Settings -->
        <div class="card p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Sicherheitseinstellungen</h3>
          <div class="space-y-4">
            <div class="responsive-stack setting-row">
              <div>
                <h4 class="text-sm font-medium text-gray-900">Zwei-Faktor-Authentifizierung</h4>
                <p class="text-sm text-gray-500">Erfordert zusätzliche Verifizierung bei der Anmeldung</p>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="settings.twoFactor" class="sr-only peer">
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
            <div class="responsive-stack setting-row">
              <div>
                <h4 class="text-sm font-medium text-gray-900">SSO-Integration</h4>
                <p class="text-sm text-gray-500">Anmeldung über Unternehmens-Identitätsanbieter</p>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="settings.sso" class="sr-only peer">
                <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
            <div>
              <h4 class="text-sm font-medium text-gray-900 mb-2">Passwort-Richtlinien</h4>
              <div class="space-y-2">
                <label class="flex items-center">
                  <input type="checkbox" v-model="settings.passwordPolicy.minLength" class="mr-2">
                  <span class="text-sm text-gray-700">Mindestens 12 Zeichen</span>
                </label>
                <label class="flex items-center">
                  <input type="checkbox" v-model="settings.passwordPolicy.requireSpecial" class="mr-2">
                  <span class="text-sm text-gray-700">Sonderzeichen erforderlich</span>
                </label>
                <label class="flex items-center">
                  <input type="checkbox" v-model="settings.passwordPolicy.requireNumbers" class="mr-2">
                  <span class="text-sm text-gray-700">Zahlen erforderlich</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Data Export -->
        <div class="card p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Datenexport</h3>
          <div class="responsive-stack data-export-row">
            <div>
              <p class="text-sm text-gray-600">Exportieren Sie alle Plattformdaten für Audits oder Backups</p>
            </div>
            <div class="flex items-center gap-3">
              <button class="btn-secondary">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                </svg>
                CSV-Export
              </button>
              <button class="btn-secondary">
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

    <!-- Confirmation Modal -->
    <div v-if="showConfirmModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3 text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100">
            <svg class="h-6 w-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
          </div>
          <h3 class="text-lg leading-6 font-medium text-gray-900 mt-4">{{ confirmModal.title }}</h3>
          <div class="mt-2 px-7 py-3">
            <p class="text-sm text-gray-500">{{ confirmModal.message }}</p>
          </div>
          <div class="items-center px-4 py-3">
            <button @click="confirmAction" class="px-4 py-2 bg-red-600 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500">
              Bestätigen
            </button>
            <button @click="showConfirmModal = false" class="mt-3 px-4 py-2 bg-white text-gray-800 text-base font-medium rounded-md w-full shadow-sm border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300">
              Abbrechen
            </button>
          </div>
        </div>
      </div>
    </div>
    </div>
  </PortalShell>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import PortalShell from '~/components/PortalShell.vue'

definePageMeta({ layout: false })

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
    badge: '3', 
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

// Analytics data
const lastUpdate = ref(new Date().toLocaleString('de-DE'))
const kpis = ref([
  { 
    label: 'Aktive Benutzer', 
    value: '1,234', 
    change: 12, 
    iconPath: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
    iconBg: 'bg-blue-100', 
    iconColor: 'text-blue-600' 
  },
  { 
    label: 'Dokumente', 
    value: '8,456', 
    change: 8, 
    iconPath: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    iconBg: 'bg-green-100', 
    iconColor: 'text-green-600' 
  },
  { 
    label: 'Neue Fälle', 
    value: '234', 
    change: -3, 
    iconPath: 'M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z',
    iconBg: 'bg-yellow-100', 
    iconColor: 'text-yellow-600' 
  },
  { 
    label: 'API-Aufrufe', 
    value: '45.2K', 
    change: 24, 
    iconPath: 'M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01',
    iconBg: 'bg-purple-100', 
    iconColor: 'text-purple-600' 
  }
])

const systemHealth = ref([
  { name: 'Webserver', status: 'Betriebsbereit', uptime: 99.99 },
  { name: 'API-Gateway', status: 'Betriebsbereit', uptime: 99.95 },
  { name: 'Datenbank', status: 'Betriebsbereit', uptime: 99.98 }
])

// API Management
const apiKeys = ref([
  { id: 1, key: 'sk_live_4242424242424242', created: '01.09.2024', lastUsed: 'Vor 2 Stunden', active: true },
  { id: 2, key: 'sk_test_1234567890123456', created: '15.08.2024', lastUsed: 'Vor 3 Tagen', active: true }
])

const apiEndpoints = ref([
  { method: 'GET', path: '/api/v1/documents', description: 'Liste aller Dokumente abrufen', rateLimit: 100, avgResponse: 120 },
  { method: 'POST', path: '/api/v1/documents', description: 'Neues Dokument erstellen', rateLimit: 50, avgResponse: 250 },
  { method: 'PUT', path: '/api/v1/documents/:id', description: 'Dokument aktualisieren', rateLimit: 50, avgResponse: 180 }
])

// Webhooks
const webhooks = ref([
  { 
    id: 1, 
    name: 'Slack-Benachrichtigungen', 
    url: 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX',
    events: ['document.created', 'case.updated'],
    active: true,
    recentLogs: [
      { timestamp: '12:34:56', status: 200 },
      { timestamp: '11:23:45', status: 200 },
      { timestamp: '10:12:34', status: 500 }
    ]
  }
])

// Users
const currentUserId = ref(1)
const userSearch = ref('')
const userFilter = ref('all')
const users = ref([
  { id: 1, name: 'Max Mustermann', email: 'max@example.de', role: 'admin', active: true, lastLogin: 'Vor 1 Stunde', initials: 'MM' },
  { id: 2, name: 'Anna Schmidt', email: 'anna@example.de', role: 'staff', active: true, lastLogin: 'Vor 3 Stunden', initials: 'AS' },
  { id: 3, name: 'Tom Weber', email: 'tom@example.de', role: 'viewer', active: false, lastLogin: 'Vor 2 Tagen', initials: 'TW' }
])

const filteredUsers = computed(() => {
  return users.value.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(userSearch.value.toLowerCase()) ||
                         user.email.toLowerCase().includes(userSearch.value.toLowerCase())
    const matchesFilter = userFilter.value === 'all' || user.role === userFilter.value
    return matchesSearch && matchesFilter
  })
})

// Settings
const settings = ref({
  twoFactor: true,
  sso: false,
  passwordPolicy: {
    minLength: true,
    requireSpecial: true,
    requireNumbers: true
  }
})

// Modals
const showConfirmModal = ref(false)
const showWebhookModal = ref(false)
const showAddUserModal = ref(false)
const confirmModal = ref({
  title: '',
  message: '',
  action: null
})

// Methods
const refreshData = () => {
  lastUpdate.value = new Date().toLocaleString('de-DE')
  // Refresh data logic
}

const generateApiKey = () => {
  const newKey = {
    id: Date.now(),
    key: 'sk_live_' + Math.random().toString(36).substr(2, 16),
    created: new Date().toLocaleDateString('de-DE'),
    lastUsed: 'Noch nie',
    active: true
  }
  apiKeys.value.push(newKey)
}

const copyKey = (key) => {
  navigator.clipboard.writeText(key)
  // Show toast notification
}

const revokeKey = (id) => {
  confirmModal.value = {
    title: 'API-Schlüssel widerrufen',
    message: 'Sind Sie sicher, dass Sie diesen API-Schlüssel widerrufen möchten? Diese Aktion kann nicht rückgängig gemacht werden.',
    action: () => {
      apiKeys.value = apiKeys.value.filter(k => k.id !== id)
    }
  }
  showConfirmModal.value = true
}

const testWebhook = (id) => {
  // Test webhook logic
  console.log('Webhook testen:', id)
}

const editWebhook = (id) => {
  // Edit webhook logic
  console.log('Webhook bearbeiten:', id)
}

const deleteWebhook = (id) => {
  confirmModal.value = {
    title: 'Webhook löschen',
    message: 'Sind Sie sicher, dass Sie diesen Webhook löschen möchten?',
    action: () => {
      webhooks.value = webhooks.value.filter(w => w.id !== id)
    }
  }
  showConfirmModal.value = true
}

const promoteToAdmin = (id) => {
  confirmModal.value = {
    title: 'Zum Administrator befördern',
    message: 'Dieser Benutzer erhält vollständige Administratorrechte. Sind Sie sicher?',
    action: () => {
      const user = users.value.find(u => u.id === id)
      if (user) user.role = 'admin'
    }
  }
  showConfirmModal.value = true
}

const demoteFromAdmin = (id) => {
  confirmModal.value = {
    title: 'Administratorrechte entziehen',
    message: 'Dieser Benutzer verliert alle Administratorrechte. Fortfahren?',
    action: () => {
      const user = users.value.find(u => u.id === id)
      if (user) user.role = 'staff'
    }
  }
  showConfirmModal.value = true
}

const editUser = (id) => {
  // Edit user logic
  console.log('Benutzer bearbeiten:', id)
}

const toggleUserStatus = (id) => {
  const user = users.value.find(u => u.id === id)
  if (user) {
    confirmModal.value = {
      title: user.active ? 'Benutzer sperren' : 'Benutzer aktivieren',
      message: user.active ? 'Der Benutzer kann sich nicht mehr anmelden.' : 'Der Benutzer kann sich wieder anmelden.',
      action: () => {
        user.active = !user.active
      }
    }
    showConfirmModal.value = true
  }
}

const confirmAction = () => {
  if (confirmModal.value.action) {
    confirmModal.value.action()
  }
  showConfirmModal.value = false
}

onMounted(() => {
  // Initialize data fetching
  refreshData()
})
</script>

<style scoped>
.settings-section {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

.responsive-stack,
.responsive-stack-start {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

@media (min-width: 768px) {
  .responsive-stack {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }

  .responsive-stack-start {
    flex-direction: row;
    align-items: flex-start;
    justify-content: space-between;
  }
}

.card-header-content {
  gap: 1rem;
}

.status-row {
  gap: 1rem;
}

@media (min-width: 768px) {
  .status-row {
    align-items: center;
  }
}

.api-key-row {
  border: 1px solid rgba(229, 231, 235, 1);
  border-radius: 0.75rem;
  padding: 1.25rem;
  background: #f9fafb;
}

.api-key-row > button {
  flex-shrink: 0;
}

.endpoint-row {
  gap: 1.25rem;
}

@media (min-width: 768px) {
  .endpoint-row {
    align-items: center;
  }
}

.webhook-card {
  border: 1px solid rgba(229, 231, 235, 1);
  border-radius: 0.75rem;
  background: #ffffff;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

.webhook-row {
  gap: 1.25rem;
}

.log-header,
.log-row {
  gap: 0.75rem;
}

@media (min-width: 768px) {
  .log-row {
    align-items: center;
  }
}

.user-toolbar {
  gap: 1.5rem;
}

.setting-row {
  padding: 1rem 1.25rem;
  border-radius: 0.75rem;
  border: 1px solid rgba(226, 232, 240, 1);
  background: #f8fafc;
}

.data-export-row {
  gap: 1.25rem;
}

.card {
  background: white;
  border-radius: 0.5rem;
  border: 1px solid rgba(226, 232, 240, 0.7);
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #2563eb;
}

.btn-secondary {
  background-color: #f3f4f6;
  color: #374151;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  transition: background-color 0.2s;
}

.btn-secondary:hover {
  background-color: #e5e7eb;
}

/* Override to match Overview page */
.sidebar-link.active {
  background-color: #eff6ff !important;
  color: #2563eb !important;
  box-shadow: none !important;
  transform: none !important;
}
</style>
