<!-- Sidebar nav intentionally excludes a Cases/Fälle entry per product direction. -->
<template>
  <div class="min-h-screen">
    <div class="flex h-screen">
      <!-- Sidebar -->
      <aside class="relative w-64 bg-white border-r border-gray-200">
        <div class="p-6 border-b border-gray-200">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-gradient-to-br from-[#5b7ce6] to-[#4a6cd4] rounded-lg flex items-center justify-center text-white font-bold">A</div>
            <div>
              <h1 class="font-semibold text-gray-900">ANWALTS.AI</h1>
              <p class="text-xs text-gray-500">Kanzlei-Dashboard</p>
            </div>
          </div>
        </div>

        <nav class="p-4 relative z-20">
          <a href="/dashboard" id="linkOverview" class="sidebar-link active" aria-current="page" title="Übersicht öffnen">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0h6"></path>
            </svg>
            <span>Übersicht</span>
          </a>

          <a href="/assistant" id="linkAssistant" class="sidebar-link" title="KI-Assistent öffnen">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
            </svg>
            <span>KI-Assistent</span>
          </a>

          <a href="/documents" id="linkDocuments" class="sidebar-link" title="Dokumente öffnen">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            <span>Dokumente</span>
          </a>

          <a href="/templates" id="linkTemplates" class="sidebar-link" title="Vorlagen öffnen">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h10M7 11h10M7 15h6M5 5a2 2 0 012-2h10a2 2 0 012 2v14a2 2 0 01-2 2H7a2 2 0 01-2-2V5z"></path>
            </svg>
            <span>Vorlagen</span>
          </a>

          <a href="/email" id="linkEmails" class="sidebar-link" title="E-Mails öffnen">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
            </svg>
            <span>E‑Mails</span>
          </a>

          <a href="/settings" id="linkSettings" class="sidebar-link" title="Einstellungen öffnen">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
            <span>Einstellungen</span>
          </a>
        </nav>

        <div class="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 pointer-events-none">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-gray-300 rounded-full" aria-hidden="true"></div>
            <div>
              <p class="text-sm font-medium text-gray-900">{{ currentUser?.name || currentUser?.email || "Benutzer" }}</p>
              <p class="text-xs text-gray-500">{{ currentUser?.role ? (currentUser.role.charAt(0).toUpperCase() + currentUser.role.slice(1)) : "Eingeloggt" }}</p>
            </div>
          </div>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="flex-1 overflow-auto">
        <!-- Header -->
        <header class="bg-white border-b border-gray-200 px-8 py-4">
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <div class="relative max-w-md" aria-label="Globale Suche">
                <input id="globalSearch" type="search" placeholder="Suche..." class="input-field h-11" aria-label="Suche" />
                <div class="mt-3 flex gap-2" aria-label="Schnellfilter">
                  <button class="chip" data-chip="faelle" title="Zu Fälle wechseln (g f)">Fälle</button>
                  <button class="chip" data-chip="dokumente" title="Zu Dokumente wechseln (g d)">Dokumente</button>
                  <button class="chip" data-chip="emails" title="Zu E‑Mails wechseln (g e)">E‑Mails</button>
                  <button class="chip" data-chip="vorlagen" title="Zu Vorlagen wechseln (g v)">Vorlagen</button>
                </div>
              </div>
            </div>

            <div class="flex items-center gap-3">
              <button class="p-2 hover:bg-gray-100 rounded-lg" aria-label="Benachrichtigungen öffnen" title="Benachrichtigungen">
                <svg class="w-5 h-5 text-gray-600 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
                </svg>
              </button>
              <button id="btnNewDoc" class="btn-primary" aria-label="Neues Dokument erstellen" title="Neues Dokument (n)">Neues Dokument</button>
              <button id="btnLogout" class="btn-secondary text-sm" title="Abmelden">Abmelden</button>
            </div>
          </div>
        </header>

        <!-- Dashboard Content -->
        <div class="p-8">
          <!-- Continue Bar -->
          <div id="continueBar" class="continue-bar mb-6 hidden" role="region" aria-live="polite">
            <div class="flex items-center gap-2 text-sm text-gray-700">
              <span class="font-medium">Weiter mit:</span>
              <span>Klageentwurf Schmidt (80%) · Frist in <span id="relDays">2</span> Tagen</span>
            </div>
            <div class="flex items-center gap-2">
              <button id="btnContinueOpen" class="btn-secondary" data-action="open-doc" aria-label="Dokument öffnen">Öffnen</button>
              <button id="btnContinueClose" class="p-2 rounded-lg hover:bg-gray-100" aria-label="Leiste schließen" title="Schließen">✕</button>
            </div>
          </div>

          <!-- Page Title -->
          <div class="mb-3 flex items-center justify-between">
            <div>
              <h2 class="text-2xl font-semibold text-gray-900">Übersicht</h2>
              <p class="text-gray-500 mt-1">Willkommen zurück</p>
            </div>
            <button id="btnStartTour" class="text-sm text-[color:var(--primary)] hover:opacity-80" aria-label="Kurze Tour starten">Kurze Tour starten</button>
          </div>

          <!-- Stats Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div class="stat-card">
              <div class="flex items-center justify-between mb-3">
                <div class="w-10 h-10 icon-box rounded-lg flex items-center justify-center">
                  <svg class="w-6 h-6 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 01-2 2z"></path>
                  </svg>
                </div>
                <span class="badge badge-success" title="Zuwachs gegenüber letzter Woche">+12%</span>
              </div>
              <div class="text-2xl font-semibold text-gray-900">42</div>
              <div class="text-sm text-gray-500 mt-1">Neue Fälle</div>
            </div>

            <div class="stat-card">
              <div class="flex items-center justify-between mb-3">
                <div class="w-10 h-10 icon-box rounded-lg flex items-center justify-center">
                  <svg class="w-6 h-6 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                </div>
                <span class="badge badge-primary" title="Aktiv im Bearbeitungsprozess">Aktiv</span>
              </div>
              <div class="text-2xl font-semibold text-gray-900">156</div>
              <div class="text-sm text-gray-500 mt-1">Dokumente</div>
            </div>

            <div class="stat-card">
              <div class="flex items-center justify-between mb-3">
                <div class="w-10 h-10 icon-box rounded-lg flex items-center justify-center">
                  <svg class="w-6 h-6 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                  </svg>
                </div>
                <span class="badge badge-primary" title="Automatisch verarbeitet">72 automatisch</span>
              </div>
              <div class="text-2xl font-semibold text-gray-900">389</div>
              <div class="text-sm text-gray-500 mt-1">E‑Mails</div>
            </div>

            <div class="stat-card" id="nextDeadlineCard">
              <div class="flex items-center justify-between mb-3">
                <div class="w-10 h-10 icon-box rounded-lg flex items-center justify-center">
                  <svg class="w-6 h-6 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                <span class="badge badge-warning" title="Zeit bis zur nächsten Frist">2 Tage</span>
              </div>
              <div class="text-2xl font-semibold text-gray-900">28. Aug <span class="text-sm text-gray-500" id="deadlineRel">(in 7 Tagen)</span></div>
              <div class="text-sm text-gray-500 mt-1">Nächste Frist</div>
            </div>
          </div>

          <!-- Content Grid -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Recent Documents -->
            <div class="lg:col-span-2 card" aria-label="Aktuelle Dokumente" id="recentDocs">
              <div class="flex items-center justify-between mb-6">
                <h3 class="text-lg font-semibold text-gray-900">Aktuelle Dokumente</h3>
                <button class="btn-secondary text-sm" aria-label="Alle Dokumente anzeigen" title="Alle Dokumente anzeigen">Alle anzeigen</button>
              </div>

              <!-- Skeleton -->
              <div id="docsSkeleton" class="space-y-4 hidden">
                <div class="p-4 bg-gray-50 rounded-lg skeleton h-16"></div>
                <div class="p-4 bg-gray-50 rounded-lg skeleton h-16"></div>
                <div class="p-4 bg-gray-50 rounded-lg skeleton h-16"></div>
              </div>

              <div id="docsList" class="space-y-4">
                <div v-for="(d, idx) in docs" :key="d.id">
                  <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div class="flex items-center gap-3">
                      <div class="w-10 h-10 icon-box rounded-lg flex items-center justify-center" aria-hidden="true">
                        <svg class="w-6 h-6 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                      </div>
                      <div>
                        <p class="font-medium text-gray-900">{{ d.title }}</p>
                        <p class="text-sm text-gray-500">{{ d.updatedLabel }}</p>
                      </div>
                    </div>
                    <div class="flex items-center gap-3">
                      <button class="text-sm text-[color:var(--primary)] hover:opacity-80 toggle-details" :aria-expanded="false">Details</button>
                      <template v-if="d.statusType === 'progress'">
                        <div class="flex items-center gap-2">
                          <span class="badge badge-primary" :title="'Fortschritt'">{{ d.progress }}%</span>
                          <div class="progress"><div :style="{ width: d.progress + '%' }"></div></div>
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
                  <div class="hidden details p-4 pt-0 text-sm text-gray-600">{{ d.details }}</div>
                </div>

                <!-- Empty state -->
                <div v-if="docs.length === 0" id="docsEmpty" class="p-8 text-center text-gray-600">
                  <p class="mb-3">Noch keine Dokumente</p>
                  <button class="btn-primary" data-action="create-doc">Neues Dokument</button>
                </div>
              </div>
            </div>

            <!-- Deadlines -->
            <div class="card" aria-label="Fristen" id="deadlines">
              <div class="flex items-center justify-between mb-6">
                <h3 class="text-lg font-semibold text-gray-900">Fristen</h3>
                <button class="text-sm text-[color:var(--primary)] hover:opacity-80" aria-label="Alle Fristen anzeigen">Alle</button>
              </div>

              <div id="deadlineList" class="space-y-4">
                <div class="border-l-4 border-red-500 pl-4" data-due="2025-08-21">
                  <p class="font-medium text-gray-900">Beschwerdebegründung</p>
                  <p class="text-sm text-gray-500">OLG Stuttgart</p>
                  <span class="badge badge-danger mt-2" title="Heute fällig">Heute</span>
                </div>

                <div class="border-l-4 border-orange-500 pl-4" data-due="2025-08-22">
                  <p class="font-medium text-gray-900">Gütetermin</p>
                  <p class="text-sm text-gray-500">AG Berlin – 10:30</p>
                  <span class="badge badge-warning mt-2" title="Morgen">Morgen</span>
                </div>

                <div class="border-l-4 border-green-500 pl-4" data-due="2025-08-24">
                  <p class="font-medium text-gray-900">Mandanten‑Call</p>
                  <p class="text-sm text-gray-500">Kronos GmbH</p>
                  <span class="badge badge-success mt-2" title="In 3 Tagen">3 Tage</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Templates Section -->
          <div id="templates" class="card mt-6" aria-label="Vorlagen">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-lg font-semibold text-gray-900">Vorlagen</h3>
              <div class="flex items-center gap-2">
                <input type="text" class="input-field w-64" placeholder="Vorlage suchen…" aria-label="Vorlagen durchsuchen" />
                <button class="btn-secondary text-sm" aria-label="Neue Vorlage anlegen">Neue Vorlage</button>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              <!-- Template cards -->
              <div class="p-4 rounded-lg bg-gray-50">
                <div class="flex items-start justify-between">
                  <div>
                    <p class="font-medium text-gray-900">NDA – Standard (DE)</p>
                    <p class="text-xs text-gray-500 mt-1">Letztes Update: 12. Aug 2025 · Freigegeben</p>
                  </div>
                  <span class="badge badge-primary" title="Kategorie">Vertrag</span>
                </div>
                <div class="mt-4 flex items-center gap-2">
                  <button class="btn-primary text-sm" aria-label="NDA-Vorlage erstellen" data-template="nda">Erstellen</button>
                  <button class="btn-secondary text-sm" aria-label="NDA‑Vorlage ansehen">Ansehen</button>
                </div>
              </div>

              <div class="p-4 rounded-lg bg-gray-50">
                <div class="flex items-start justify-between">
                  <div>
                    <p class="font-medium text-gray-900">Klageentwurf – Zivil</p>
                    <p class="text-xs text-gray-500 mt-1">Letztes Update: 30. Jul 2025 · Version 7</p>
                  </div>
                  <span class="badge badge-primary">Zivil</span>
                </div>
                <div class="mt-4 flex items-center gap-2">
                  <button class="btn-primary text-sm" data-template="klage-zivil">Erstellen</button>
                  <button class="btn-secondary text-sm">Ansehen</button>
                </div>
              </div>

              <div class="p-4 rounded-lg bg-gray-50">
                <div class="flex items-start justify-between">
                  <div>
                    <p class="font-medium text-gray-900">Vergleichsangebot</p>
                    <p class="text-xs text-gray-500 mt-1">Letztes Update: 04. Aug 2025 · Freigegeben</p>
                  </div>
                  <span class="badge badge-primary">Zivil</span>
                </div>
                <div class="mt-4 flex items-center gap-2">
                  <button class="btn-primary text-sm" data-template="vergleich">Erstellen</button>
                  <button class="btn-secondary text-sm">Ansehen</button>
                </div>
              </div>

              <div class="p-4 rounded-lg bg-gray-50">
                <div class="flex items-start justify-between">
                  <div>
                    <p class="font-medium text-gray-900">Abmahnung – UWG</p>
                    <p class="text-xs text-gray-500 mt-1">Letztes Update: 18. Jun 2025 · Version 3</p>
                  </div>
                  <span class="badge badge-primary">Wettbewerb</span>
                </div>
                <div class="mt-4 flex items-center gap-2">
                  <button class="btn-primary text-sm" data-template="abmahnung">Erstellen</button>
                  <button class="btn-secondary text-sm">Ansehen</button>
                </div>
              </div>

              <div class="p-4 rounded-lg bg-gray-50">
                <div class="flex items-start justify-between">
                  <div>
                    <p class="font-medium text-gray-900">Vollmacht – Mandanten</p>
                    <p class="text-xs text-gray-500 mt-1">Letztes Update: 10. Aug 2025</p>
                  </div>
                  <span class="badge badge-primary">Allgemein</span>
                </div>
                <div class="mt-4 flex items-center gap-2">
                  <button class="btn-primary text-sm" data-template="vollmacht">Erstellen</button>
                  <button class="btn-secondary text-sm">Ansehen</button>
                </div>
              </div>

              <div class="p-4 rounded-lg bg-gray-50">
                <div class="flex items-start justify-between">
                  <div>
                    <p class="font-medium text-gray-900">DSGVO – Auskunftsersuchen</p>
                    <p class="text-xs text-gray-500 mt-1">Letztes Update: 05. Aug 2025</p>
                  </div>
                  <span class="badge badge-primary">Datenschutz</span>
                </div>
                <div class="mt-4 flex items-center gap-2">
                  <button class="btn-primary text-sm" data-template="dsgvo-auskunft">Erstellen</button>
                  <button class="btn-secondary text-sm">Ansehen</button>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Activity (E-Mails etc.) -->
          <div class="card mt-6" aria-label="Neue Eingänge">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-lg font-semibold text-gray-900">Neue Eingänge</h3>
              <div class="flex items-center gap-2">
                <select class="input-field w-auto" aria-label="Typen filtern">
                  <option>Alle Typen</option>
                  <option>E‑Mails</option>
                  <option>Dokumente</option>
                  <option>Anrufe</option>
                </select>
              </div>
            </div>

            <div class="overflow-x-auto">
              <table class="w-full">
                <thead>
                  <tr class="border-b border-gray-200">
                    <th class="text-left py-3 px-4 text-sm font-medium text-gray-700">Typ</th>
                    <th class="text-left py-3 px-4 text-sm font-medium text-gray-700">Betreff</th>
                    <th class="text-left py-3 px-4 text-sm font-medium text-gray-700">Mandant</th>
                    <th class="text-left py-3 px-4 text-sm font-medium text-gray-700">Status</th>
                    <th class="text-right py-3 px-4 text-sm font-medium text-gray-700">Aktion</th>
                  </tr>
                </thead>
                <tbody id="activitySkeleton">
                  <tr><td colspan="5" class="py-3 px-4"><div class="skeleton h-8 w-full rounded"></div></td></tr>
                  <tr><td colspan="5" class="py-3 px-4"><div class="skeleton h-8 w-full rounded"></div></td></tr>
                  <tr><td colspan="5" class="py-3 px-4"><div class="skeleton h-8 w-full rounded"></div></td></tr>
                </tbody>
                <tbody id="activityBody" class="hidden">
                  <tr class="border-b border-gray-100">
                    <td class="py-3 px-4"><span class="badge badge-primary" title="E‑Mail‑Eingang">E‑Mail</span></td>
                    <td class="py-3 px-4 text-sm text-gray-900">Angebot Vergleich – Glaser GmbH</td>
                    <td class="py-3 px-4 text-sm text-gray-600">Schmidt</td>
                    <td class="py-3 px-4"><span class="badge badge-warning" title="Wartet auf juristische Prüfung">Prüfung</span></td>
                    <td class="py-3 px-4 text-right"><button class="text-sm text-[color:var(--primary)] hover:opacity-80" data-action="open-email" aria-label="E‑Mail öffnen">Öffnen</button></td>
                  </tr>

                  <tr class="border-b border-gray-100">
                    <td class="py-3 px-4"><span class="badge badge-primary" title="Telefonnotiz">Telefon</span></td>
                    <td class="py-3 px-4 text-sm text-gray-900">Rückruf erbeten – Zeugenaussage</td>
                    <td class="py-3 px-4 text-sm text-gray-600">Meyer</td>
                    <td class="py-3 px-4"><span class="badge badge-success" title="Termin vorgemerkt">Termin</span></td>
                    <td class="py-3 px-4 text-right"><button class="text-sm text-[color:var(--primary)] hover:opacity-80" data-action="plan-call" aria-label="Termin planen">Planen</button></td>
                  </tr>

                  <tr class="border-b border-gray-100">
                    <td class="py-3 px-4"><span class="badge badge-primary" title="Upload eingegangen">Upload</span></td>
                    <td class="py-3 px-4 text-sm text-gray-900">Kontoauszüge (3 Dateien)</td>
                    <td class="py-3 px-4 text-sm text-gray-600">Kronos GmbH</td>
                    <td class="py-3 px-4">
                      <div class="flex items-center gap-2">
                        <span class="badge badge-primary" title="Analyse durch KI läuft">KI‑Analyse</span>
                        <div class="progress"><div id="kiProgress"></div></div>
                        <span id="kiProgressLabel" class="text-xs text-gray-500">0%</span>
                      </div>
                    </td>
                    <td class="py-3 px-4 text-right"><button class="text-sm text-[color:var(--primary)] hover:opacity-80" data-action="view-upload" aria-label="Upload ansehen">Ansehen</button></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </main>
    </div>

    <!-- Toast -->
    <div id="toast" class="fixed bottom-6 right-6 hidden"></div>

    <!-- Tour Elements -->
    <div id="tourOverlay" class="tour-overlay"></div>
    <div id="tourStep" class="tour-step hidden">
      <div class="tour-arrow"></div>
      <div id="tourContent" class="text-sm text-gray-800"></div>
      <div class="mt-3 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <button id="tourPrev" class="btn-secondary text-sm">Zurück</button>
          <button id="tourNext" class="btn-primary text-sm">Weiter</button>
        </div>
        <button id="tourClose" class="text-sm text-gray-500">Schließen</button>
      </div>
      <button id="tourNever" class="mt-2 text-xs text-gray-500 underline">Nicht mehr zeigen</button>
    </div>

  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useHead } from '#imports'

definePageMeta({ layout: false })
const nuxtApp = useNuxtApp()
const currentUser = ref(null)

const resolveStoredUser = () => {
  if (!process.client) return null
  try {
    const raw = localStorage.getItem('auth_user') || localStorage.getItem('anwalts_user')
    return raw ? JSON.parse(raw) : null
  } catch (_) {
    return null
  }
}

const hasStoredAuthEvidence = () => {
  if (!process.client) return false
  try {
    if (
      localStorage.getItem('anwalts_auth_token') ||
      localStorage.getItem('auth_user') ||
      localStorage.getItem('anwalts_user') ||
      localStorage.getItem('auth_success') === 'true' ||
      localStorage.getItem('access_token') ||
      localStorage.getItem('token') ||
      localStorage.getItem('sat')
    ) {
      return true
    }
    if (typeof document !== 'undefined' && document.cookie) {
      return /(anwalts_auth_token|access_token|token|sat)=/.test(document.cookie)
    }
  } catch (_) {}
  return false
}

// Inject Tailwind CDN for this page to match the provided design

onMounted(() => {
  (async () => {
    if (!currentUser.value) {
      const stored = resolveStoredUser()
      if (stored) {
        currentUser.value = stored
      }
    }

    try {
      const stackApp = nuxtApp.$stackAuth;
      if (!currentUser.value && stackApp?.getUser) {
        const stackUser = await stackApp.getUser({ or: 'return-null' })
        if (stackUser) {
          currentUser.value = {
            name: stackUser.displayName || stackUser.primaryEmail,
            email: stackUser.primaryEmail,
            role: stackUser.role || stackUser.projectRole || 'Benutzer'
          }
        }
      }
    } catch (error) {
      console.warn('Unable to resolve Stack Auth user on dashboard', error)
    }

    if (!currentUser.value) {
      try {
        const response = await fetch('/api/auth/me', { credentials: 'include' })
        if (response.ok) {
          const payload = await response.json().catch(() => null)
          if (payload?.user) {
            currentUser.value = payload.user
          }
        }
      } catch (error) {
        console.warn('Fallback /api/auth/me failed', error)
      }
    }

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
  })();
  // Utilities
  const $ = (sel, root = document) => root.querySelector(sel)
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel))
  let toastTimer = null

  // Auth helpers
  function getAuthHeader() {
    try {
      let token = localStorage.getItem('access_token') || localStorage.getItem('token') || localStorage.getItem('sat')
      if (!token && document && document.cookie) {
        const map = Object.fromEntries(document.cookie.split(';').map(s => s.trim().split('=')))
        token = map['access_token'] || map['token'] || map['sat']
      }
      return token ? { Authorization: `Bearer ${decodeURIComponent(token)}` } : {}
    } catch (_) { return {} }
  }
  function clearAuth() {
    try {
      localStorage.removeItem('access_token'); localStorage.removeItem('token'); localStorage.removeItem('sat')
      document.cookie = 'access_token=; Max-Age=0; Path=/; Secure; SameSite=Lax'
      document.cookie = 'token=; Max-Age=0; Path=/; Secure; SameSite=Lax'
      document.cookie = 'sat=; Max-Age=0; Path=/; Secure; SameSite=Lax'
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
    const tag = document.activeElement?.tagName?.toLowerCase()
    if (tag === 'input' || tag === 'textarea') return
    if (e.key === 'f') { e.preventDefault(); $('#globalSearch')?.focus(); showToast('Suche fokussiert'); markFirstAction(); return }
    if (e.key === 'n') { e.preventDefault(); $('#btnNewDoc')?.click(); return }
    if (e.key === 'g') { gotoArmed = true; clearTimeout(gotoTimer); gotoTimer = setTimeout(() => gotoArmed = false, 1000); return }
    if (gotoArmed) {
      if (e.key === 'f') { showToast('Gehe zu Fälle'); markFirstAction(); gotoArmed = false }
      else if (e.key === 'd') { showToast('Gehe zu Dokumente'); markFirstAction(); gotoArmed = false }
      else if (e.key === 'e') { showToast('Gehe zu E‑Mails'); markFirstAction(); gotoArmed = false }
      else if (e.key === 'v') { e.preventDefault(); window.location.href = '/templates'; showToast('Gehe zu Vorlagen'); markFirstAction(); gotoArmed = false }
    }
  })

  // Chip clicks
  $$('[data-chip]')?.forEach(chip => {
    chip.addEventListener('click', () => {
      const type = chip.getAttribute('data-chip')
      if (type === 'vorlagen') { window.location.href = '/templates'; showToast('Gehe zu Vorlagen') }
      if (type === 'faelle') { showToast('Gehe zu Fälle') }
      if (type === 'dokumente') { showToast('Gehe zu Dokumente') }
      if (type === 'emails') { showToast('Gehe zu E‑Mails') }
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

  // Continue bar logic
  ;(function initContinueBar() {
    const dismissed = localStorage.getItem('continueBarDismissed') === '1'
    const bar = $('#continueBar')
    if (bar && !dismissed) { bar.classList.remove('hidden') }
    $('#btnContinueClose')?.addEventListener('click', () => { bar?.classList.add('hidden'); localStorage.setItem('continueBarDismissed', '1') })
    $('#btnContinueOpen')?.addEventListener('click', () => { markFirstAction(); showToast('Dokument geöffnet: Klageentwurf Schmidt') })
    // relative days demo
    const today = new Date('2025-08-21')
    const due = new Date('2025-08-23')
    const diff = Math.ceil((Number(due) - Number(today)) / (1000 * 60 * 60 * 24))
    const rel = $('#relDays')
    if (rel) rel.textContent = String(diff)
  })()

  // Default sorts
  ;(function sortDeadlines() {
    const list = $('#deadlineList')
    if (!list) return
    const items = $$('.border-l-4', list)
    items.sort((a, b) => new Date(a.dataset.due) - new Date(b.dataset.due))
    items.forEach(el => list.appendChild(el))
  })()

  ;(function sortDocs() {
    const list = $('#docsList')
    if (!list) return
    const rows = $$('.bg-gray-50.rounded-lg', list)
    rows.forEach(el => list.appendChild(el))
  })()

  // Skeletons reveal
  window.addEventListener('load', () => {
    setTimeout(() => {
      $('#docsSkeleton')?.classList.add('hidden')
      $('#docsList')?.classList.remove('hidden')
      $('#activitySkeleton')?.classList.add('hidden')
      $('#activityBody')?.classList.remove('hidden')
    }, 600)
  })

  // KI progress demo to 65%
  ;(function kiProgress() {
    const bar = $('#kiProgress'); const label = $('#kiProgressLabel')
    if (!bar || !label) return
    let p = 0; const target = 65; const t = setInterval(() => {
      p += 5; if (p >= target) { p = target; clearInterval(t) }
      bar.style.width = p + '%'; label.textContent = p + '%'
    }, 120)
  })()

  // Details toggles
  $$('.toggle-details').forEach((btn, idx) => {
    btn.addEventListener('click', () => {
      const details = $$('.details')[idx]
      const expanded = btn.getAttribute('aria-expanded') === 'true'
      btn.setAttribute('aria-expanded', String(!expanded))
      details?.classList.toggle('hidden')
    })
  })

  // Button actions
  $('#btnNewDoc')?.addEventListener('click', () => { markFirstAction(); showToast('Neues Dokument erstellt') })
  $('#btnLogout')?.addEventListener('click', async () => {
    try { await fetch('/auth/logout', { method: 'POST', credentials: 'include', headers: { ...getAuthHeader() } }) } catch (_) {}
    clearAuth(); window.location.replace('/')
  })
  $$('[data-template]')?.forEach(btn => btn.addEventListener('click', () => { markFirstAction(); showToast(`Vorlage erstellt: ${btn.dataset.template}`) }))
  $$('[data-action]')?.forEach(btn => btn.addEventListener('click', () => markFirstAction()))
  // Update absolute + relative dates in next deadline card
  ;(function updateDeadlineCard() {
    const today = new Date('2025-08-21')
    const due = new Date('2025-08-28')
    const diff = Math.ceil((Number(due) - Number(today)) / (1000 * 60 * 60 * 24))
    const rel = $('#deadlineRel')
    if (rel) rel.textContent = `(in ${diff} Tagen)`
  })()
})

// Dummy data for "Aktuelle Dokumente"
const docs = ref([
  {
    id: 1,
    title: 'Klageentwurf Schmidt',
    updatedLabel: 'vor 2 Stunden',
    statusType: 'progress',
    progress: 80,
    details: 'Zuletzt geändert von M. Weber · Version 12 · Akte-Nr. 2025-01-093'
  },
  {
    id: 2,
    title: 'NDA‑Vorlage Kronos',
    updatedLabel: 'vor 5 Stunden',
    statusType: 'final',
    details: 'Freigegeben von Dr. M. Müller · Version 4 · Akte‑Nr. 2025‑02‑441'
  },
  {
    id: 3,
    title: 'Mahnung Müller KFZ',
    updatedLabel: 'gestern',
    statusType: 'review',
    details: 'Zahlungseingänge offen · Referenz 8842 · Akte‑Nr. 2025‑03‑118'
  }
])
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --primary: #5b7ce6;
  --primary-hover: #4a6cd4;
  --icon-bg: rgba(91, 124, 230, 0.12);
  --bg: #f8f9fa;
  --text: #2c3e50;
  --muted: #e8ecf3;
  --muted-hover: #d8dfe9;
  --success-bg: #e8f5e9;   --success: #16a34a;
  --warning-bg: #fff7e6;   --warning: #f59e0b;
  --danger-bg: #ffebee;    --danger: #ef4444;
}

body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }

.card { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.06); transition: box-shadow 0.2s; }
.card:hover { box-shadow: 0 4px 8px rgba(0,0,0,0.1); }

.btn-primary { background: var(--primary); color: white; padding: 10px 24px; border-radius: 8px; border: none; font-weight: 500; cursor: pointer; transition: background 0.2s; }
.btn-primary:hover { background: var(--primary-hover); }

.btn-secondary { background: var(--muted); color: var(--text); padding: 10px 24px; border-radius: 8px; border: none; font-weight: 500; cursor: pointer; transition: background 0.2s; }
.btn-secondary:hover { background: var(--muted-hover); }

.input-field { width: 100%; padding: 12px 16px; border: 1px solid #e0e6ed; border-radius: 8px; font-size: 14px; transition: border-color 0.2s; background: white; }
.input-field:focus { outline: none; border-color: var(--primary); }

.sidebar-link { display: flex; align-items: center; gap: 12px; padding: 12px 16px; border-radius: 8px; color: #64748b; text-decoration: none; transition: all 0.2s; font-size: 14px; }
.sidebar-link:hover { background: #f1f5f9; color: var(--text); }
.sidebar-link.active { background: var(--primary); color: white; }

.stat-card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.06); }

.badge { display: inline-block; padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 500; }
.badge-primary { background: rgba(91,124,230,0.12); color: var(--primary); }
.badge-success { background: var(--success-bg); color: var(--success); }
.badge-warning { background: var(--warning-bg); color: var(--warning); }
.badge-danger  { background: var(--danger-bg);  color: var(--danger);  }

.icon { border: 0; }
.icon-box { background: var(--icon-bg); color: var(--primary); }

.chip { border: 1px solid #e0e6ed; background: white; padding: 6px 10px; border-radius: 9999px; font-size: 12px; }

/* Skeletons */
.skeleton { position: relative; overflow: hidden; background: #eef1f6; }
.skeleton::after { content: ""; position: absolute; inset: 0; transform: translateX(-100%); background: linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent); animation: shimmer 1.2s infinite; }
@keyframes shimmer { 100% { transform: translateX(100%); } }

/* Toast */
#toast { background: #111827; color: #fff; padding: 12px 16px; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }

/* Tour */
.tour-overlay { position: fixed; inset: 0; background: rgba(17,24,39,0.55); z-index: 50; display: none; }
.tour-step { position: absolute; background: #fff; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); padding: 16px; width: 320px; z-index: 51; }
.tour-arrow { width: 0; height: 0; border-left: 8px solid transparent; border-right: 8px solid transparent; border-top: 8px solid #fff; position: absolute; top: -8px; left: 24px; }

/* Continue bar */
.continue-bar { background: #ffffff; border: 1px solid #eef1f6; border-radius: 12px; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; }

/* Progress */
.progress { width: 100px; height: 6px; background: #e5e7eb; border-radius: 9999px; overflow: hidden; }
.progress > div { height: 100%; background: var(--primary); width: 0%; }

/* Deterministic search icon alignment */
.input-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #9CA3AF; /* gray-400 */
  pointer-events: none;
  z-index: 10;
}

/* Ensure neat height and text centering */
#globalSearch { height: 44px; line-height: 44px; }
#btnStartTour{display:none!important}
.tour-overlay{display:none!important}
#tourStep{display:none!important}
  /* force remove tour */
  #btnStartTour{display:none!important}
  .tour-overlay{display:none!important}
  #tourStep{display:none!important}
  .tour-step{display:none!important}

</style>

/* tour removed */
#btnStartTour{display:none!important}
.tour-overlay{display:none!important}
#tourStep{display:none!important}
