<template>
  <div class="font-sans antialiased">
    <!-- Global Styles -->
    <style scoped>
      :root {
        --accent: rgba(0, 0, 0, 0.8);
        --primary: #5b7ce6;
        --primary-hover: #4a6cd4;
        --text-primary: #202124;
        --text-secondary: #5f6368;
        --border-color: #dadce0;
        --hover-bg: #f1f3f4;
        --selected-bg: #e8f0fe;
      }
      
      * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
      }
      
      input[type="checkbox"] {
        accent-color: var(--primary);
      }
      
      /* Responsive Container Padding */
      @media (min-width: 1440px) {
        .max-w-\[1440px\] {
          padding-left: 2rem;
          padding-right: 2rem;
        }
      }
      
      @media (min-width: 1024px) and (max-width: 1439px) {
        .max-w-\[1440px\] {
          max-width: 95%;
          padding-left: 1.5rem;
          padding-right: 1.5rem;
        }
      }
      
      @media (min-width: 768px) and (max-width: 1023px) {
        .max-w-\[1440px\] {
          max-width: 95%;
          padding-left: 1rem;
          padding-right: 1rem;
        }
      }
      
      @media (max-width: 767px) {
        .max-w-\[1440px\] {
          padding-left: 0.75rem;
          padding-right: 0.75rem;
        }
      }

      @media (max-width: 768px) {
        .grid-cols-4 {
          grid-template-columns: repeat(2, 1fr);
          gap: 0.75rem;
        }
        
        table {
          font-size: 0.875rem;
        }
        
        .max-w-4xl {
          max-width: 100%;
        }
        
        .inbox-table-responsive {
          overflow-x: auto;
        }
        
        .inbox-table-responsive table {
          min-width: 600px;
        }
        
        .toolbar-responsive {
          flex-direction: column;
          gap: 1rem;
        }
        
        .toolbar-responsive .toolbar-right {
          width: 100%;
          justify-content: space-between;
          flex-wrap: wrap;
          gap: 0.5rem;
        }
      }
      
      @media (max-width: 640px) {
        .grid-cols-4 {
          grid-template-columns: 1fr;
        }
        
        .toolbar-responsive .toolbar-right {
          flex-direction: column;
        }
        
        .toolbar-responsive .toolbar-right input,
        .toolbar-responsive .toolbar-right select,
        .toolbar-responsive .toolbar-right button {
          width: 100%;
        }
      }
    </style>

    <!-- Consent Screen -->
    <div v-if="currentView === 'consent'" class="min-h-screen bg-white flex items-center justify-center p-4 sm:p-6 lg:p-8 relative">
      <!-- Back to Dashboard Button -->
      <NuxtLink 
        to="/dashboard" 
        class="absolute top-4 left-4 sm:top-6 sm:left-6 inline-flex items-center text-gray-600 hover:text-[#5b7ce6] focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 rounded-md px-3 py-2 transition-colors z-10"
        aria-label="Zurück zum Dashboard"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
        </svg>
        <span class="text-sm font-medium">Übersicht</span>
      </NuxtLink>

      <div class="max-w-sm sm:max-w-md w-full mx-auto">
        <div class="text-center mb-6 sm:mb-8">
          <div class="inline-flex items-center justify-center w-12 h-12 sm:w-16 sm:h-16 bg-gray-100 rounded-2xl mb-4">
            <!-- Briefcase Icon -->
            <svg class="w-6 h-6 sm:w-8 sm:h-8 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H8a2 2 0 01-2-2V8a2 2 0 012-2V6"/>
            </svg>
          </div>
          <h1 class="text-xl sm:text-2xl font-semibold text-gray-900 mb-2">E-Mail verbinden</h1>
          <p class="text-gray-600 text-sm sm:text-base">Verbinden Sie sicher Ihr professionelles E-Mail-Konto</p>
        </div>

        <div class="space-y-3 mb-6">
          <button
            @click="handleOAuthConnect('gmail')"
            :disabled="!consents.oauth || !consents.aiReading"
            class="w-full flex items-center justify-center gap-3 px-4 py-3 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base"
          >
            <!-- Gmail Icon -->
            <svg class="w-5 h-5 text-gray-700" viewBox="0 0 24 24" fill="currentColor">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            <span class="font-medium text-gray-700">Weiter mit Gmail</span>
          </button>
          
          <button
            @click="handleOAuthConnect('outlook')"
            :disabled="!consents.oauth || !consents.aiReading"
            class="w-full flex items-center justify-center gap-3 px-4 py-3 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm sm:text-base"
          >
            <!-- Microsoft Icon -->
            <svg class="w-5 h-5 text-gray-700" viewBox="0 0 24 24" fill="currentColor">
              <path d="M11.4 24H0V12.6h11.4V24zM24 24H12.6V12.6H24V24zM11.4 11.4H0V0h11.4v11.4zM24 11.4H12.6V0H24v11.4z"/>
            </svg>
            <span class="font-medium text-gray-700">Weiter mit Outlook / Microsoft 365</span>
          </button>
        </div>

        <div class="bg-gray-50 rounded-xl p-4 space-y-3 mb-6">
          <label class="flex items-start gap-3 cursor-pointer">
            <input
              type="checkbox"
              v-model="consents.oauth"
              class="mt-0.5 w-4 h-4 rounded border-gray-300"
            />
            <span class="text-sm text-gray-700 flex-1">
              Ich stimme zu, meine E-Mail über OAuth 2.0 sichere Authentifizierung zu verbinden
            </span>
          </label>
          
          <label class="flex items-start gap-3 cursor-pointer">
            <input
              type="checkbox"
              v-model="consents.aiReading"
              class="mt-0.5 w-4 h-4 rounded border-gray-300"
            />
            <span class="text-sm text-gray-700 flex-1">
              Ich stimme zu, dass die KI meine E-Mails liest, um Zusammenfassungen vorzuschlagen und Antworten zu entwerfen. Die KI wird niemals ohne meine Überprüfung senden.
            </span>
          </label>
        </div>

        <div class="flex items-center justify-center gap-4 text-sm">
          <a href="/privacy" class="text-gray-600 hover:text-gray-900 underline">Datenschutz</a>
          <span class="text-gray-300">•</span>
          <a href="/terms" class="text-gray-600 hover:text-gray-900 underline">Datennutzung</a>
          <span class="text-gray-300">•</span>
          <a href="#" class="text-gray-600 hover:text-gray-900 underline">Zugriff widerrufen</a>
        </div>

        <div v-if="loading" class="mt-6 flex items-center justify-center">
          <svg class="w-5 h-5 animate-spin text-gray-600" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span class="ml-2 text-gray-600">Sichere Verbindung wird hergestellt...</span>
        </div>
      </div>
    </div>

    <!-- Inbox View -->
    <div v-if="currentView === 'inbox'" class="min-h-screen bg-white">
      <header class="border-b border-gray-200 py-3 bg-white">
        <div class="max-w-[1440px] mx-auto px-3 md:px-4 lg:px-6 xl:px-8">
          <div class="flex items-center justify-between flex-wrap gap-3">
            <div class="flex items-center gap-2 sm:gap-4 min-w-0 flex-1">
              <button 
                @click="currentView = 'consent'"
                class="flex items-center gap-1 sm:gap-2 text-gray-600 hover:text-gray-900 transition-colors flex-shrink-0"
              >
                <!-- ChevronLeft Icon -->
                <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                </svg>
                <span class="text-xs sm:text-sm font-medium">Zurück</span>
              </button>
              <div class="flex items-center gap-2 sm:gap-3 min-w-0">
                <!-- Briefcase Icon -->
                <svg class="w-5 h-5 sm:w-6 sm:h-6 text-gray-700 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H8a2 2 0 01-2-2V8a2 2 0 012-2V6"/>
                </svg>
                <h1 class="text-lg sm:text-xl font-medium text-gray-900 truncate">E-Mail Portal</h1>
              </div>
              <span class="hidden sm:inline text-xs sm:text-sm text-gray-500 flex-shrink-0">{{ formatSyncTime() }}</span>
            </div>
            <div class="flex items-center gap-2 sm:gap-3 flex-shrink-0">
              <span class="sm:hidden text-xs text-gray-500">{{ formatSyncTime() }}</span>
              <button class="px-3 sm:px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-1 sm:gap-2 text-xs sm:text-sm">
                <!-- ScrollText Icon -->
                <svg class="w-3 h-3 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                <span class="hidden sm:inline">Massenverarbeitung</span>
                <span class="sm:hidden">Masse</span>
              </button>
              <button 
                @click="showSettings = true"
                class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <!-- Settings Icon -->
                <svg class="w-4 h-4 sm:w-5 sm:h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div class="py-3 border-b border-gray-200 bg-gray-50">
        <div class="max-w-[1440px] mx-auto px-3 md:px-4 lg:px-6 xl:px-8">
          <div class="toolbar-responsive flex items-center gap-3 flex-wrap">
            <div class="flex items-center gap-1 sm:gap-2 flex-wrap">
              <button
                v-for="filter in filterTabs"
                :key="filter.key"
                @click="activeFilter = filter.key"
                :class="[
                  'px-3 sm:px-4 py-1.5 rounded-md text-xs sm:text-sm font-medium transition-all',
                  activeFilter === filter.key
                    ? 'bg-blue-50 text-blue-700 border border-blue-200'
                    : 'text-gray-700 hover:bg-gray-100'
                ]"
              >
                {{ filter.label }}
              </button>
            </div>
            
            <div class="toolbar-right flex items-center gap-2 sm:gap-3 ml-auto">
              <div class="relative flex-1 sm:flex-none min-w-0">
                <!-- Search Icon -->
                <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                </svg>
                <input
                  type="text"
                  placeholder="Suchen (⌘K)"
                  v-model="searchQuery"
                  @keydown="handleKeydown"
                  class="w-full sm:w-48 pl-9 pr-3 py-1.5 bg-white border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <button class="flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-1.5 bg-white border border-gray-300 rounded-lg text-xs sm:text-sm hover:bg-gray-50 whitespace-nowrap text-gray-700">
                <!-- Filter Icon -->
                <svg class="w-3 h-3 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/>
                </svg>
                <span class="hidden sm:inline">Filter</span>
                <!-- ChevronDown Icon -->
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                </svg>
              </button>
              
              <button class="flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-1.5 bg-white border border-gray-300 rounded-lg text-xs sm:text-sm hover:bg-gray-50 whitespace-nowrap text-gray-700">
                <span class="hidden sm:inline">Sort: Newest</span>
                <span class="sm:hidden">Sort</span>
                <!-- ChevronDown Icon -->
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="py-4 bg-white">
        <div class="max-w-[1440px] mx-auto px-3 md:px-4 lg:px-6 xl:px-8">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 mb-6">
            <div class="bg-white rounded-lg border border-gray-200 p-3 sm:p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs sm:text-sm text-gray-600">This Week</span>
                <!-- Mail Icon -->
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                </svg>
              </div>
              <div class="text-xl sm:text-2xl font-semibold text-black">{{ emails.length }}</div>
              <div class="text-xs text-green-600">+12% vs last week</div>
            </div>
            
            <div class="bg-white rounded-lg border border-gray-200 p-3 sm:p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs sm:text-sm text-gray-600">Avg Response</span>
                <!-- Clock Icon -->
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <div class="text-xl sm:text-2xl font-semibold text-black">2.4h</div>
              <div class="text-xs text-gray-500">Professional standard</div>
            </div>
            
            <div class="bg-white rounded-lg border border-gray-200 p-3 sm:p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs sm:text-sm text-gray-600">AI Suggestions</span>
                <!-- Shield Icon -->
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <div class="text-xl sm:text-2xl font-semibold text-black">{{ getAIPendingCount() }}</div>
              <div class="text-xs text-gray-500">85% acceptance</div>
            </div>
            
            <div class="bg-white rounded-lg border border-gray-200 p-3 sm:p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs sm:text-sm text-gray-600">Follow-ups</span>
                <!-- Calendar Icon -->
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
              </div>
              <div class="text-xl sm:text-2xl font-semibold text-black">5</div>
              <div class="text-xs text-orange-600">2 due today</div>
            </div>
          </div>

          <div v-if="loading" class="space-y-3">
            <div v-for="i in 3" :key="i" class="bg-gray-100 rounded-lg h-16 animate-pulse"></div>
          </div>
          
          <div v-else-if="filteredEmails.length === 0" class="bg-white border border-gray-200 rounded-lg p-12 text-center">
            <svg class="w-12 h-12 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
            <p class="text-gray-500">Keine E-Mails in dieser Kategorie gefunden</p>
          </div>
          
          <div v-else class="bg-white rounded-lg shadow-sm overflow-hidden">
            <div class="inbox-table-responsive overflow-x-auto">
              <table class="w-full">
                <thead>
                  <tr class="border-b border-gray-200 bg-gray-50">
                    <th class="text-left px-3 sm:px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Sender</th>
                    <th class="text-left px-3 sm:px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Subject</th>
                    <th class="text-left px-3 sm:px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider hidden sm:table-cell">Date</th>
                    <th class="text-left px-3 sm:px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider hidden lg:table-cell">Type</th>
                    <th class="text-left px-3 sm:px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th class="text-left px-3 sm:px-4 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="email in filteredEmails"
                    :key="email.id"
                    class="border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors"
                    @click="selectedEmail = email"
                  >
                    <td class="px-3 sm:px-4 py-3">
                      <div class="flex items-center gap-2 sm:gap-3">
                        <div v-if="email.status === 'Ungelesen'" class="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0"></div>
                        <div class="w-6 h-6 sm:w-8 sm:h-8 bg-gray-200 rounded-full flex items-center justify-center text-xs font-medium text-gray-700 flex-shrink-0">
                          {{ email.sender.initials }}
                        </div>
                        <div class="min-w-0">
                          <div class="text-xs sm:text-sm font-semibold text-black truncate">{{ email.sender.name }}</div>
                          <div class="text-xs text-gray-500 truncate hidden sm:block">{{ email.sender.email }}</div>
                        </div>
                      </div>
                    </td>
                    <td class="px-3 sm:px-4 py-3">
                      <div class="min-w-0">
                        <div class="text-xs sm:text-sm font-semibold text-black flex items-center gap-2">
                          <span class="truncate">{{ email.subject }}</span>
                          <!-- FileText Icon for attachment -->
                          <svg v-if="email.hasAttachment" class="w-3 h-3 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                          </svg>
                        </div>
                        <div class="text-xs text-gray-500 truncate max-w-xs sm:max-w-md">{{ email.snippet }}</div>
                        <!-- Mobile: Show date and type inline -->
                        <div class="sm:hidden flex items-center gap-2 mt-1">
                          <span class="text-xs text-gray-400">{{ formatDate(email.date) }}</span>
                          <span class="px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded text-xs">{{ email.type }}</span>
                        </div>
                      </div>
                    </td>
                    <td class="px-3 sm:px-4 py-3 hidden sm:table-cell">
                      <div class="text-xs sm:text-sm text-gray-600">
                        {{ formatDate(email.date) }}
                        <div class="text-xs text-gray-400">
                          {{ email.date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) }}
                        </div>
                      </div>
                    </td>
                    <td class="px-3 sm:px-4 py-3 hidden lg:table-cell">
                      <span class="px-2 py-1 bg-gray-100 text-gray-700 rounded-lg text-xs font-medium">
                        {{ email.type }}
                      </span>
                    </td>
                    <td class="px-3 sm:px-4 py-3">
                      <span :class="['px-1.5 sm:px-2 py-1 rounded-lg text-xs font-medium', getStatusColor(email.status)]">
                        {{ email.status }}
                      </span>
                    </td>
                    <td class="px-3 sm:px-4 py-3">
                      <div class="flex items-center gap-1" @click.stop="">
                        <button 
                          class="p-1 sm:p-1.5 hover:bg-gray-100 rounded-lg transition-colors" 
                          title="View"
                          @click="selectedEmail = email"
                        >
                          <!-- Eye Icon -->
                          <svg class="w-3 h-3 sm:w-4 sm:h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                          </svg>
                        </button>
                        <button 
                          class="p-1 sm:p-1.5 hover:bg-gray-100 rounded-lg transition-colors" 
                          title="Als gelesen markieren"
                          @click="markAsRead(email.id)"
                        >
                          <!-- Check Icon -->
                          <svg class="w-3 h-3 sm:w-4 sm:h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                          </svg>
                        </button>
                        <button 
                          class="p-1 sm:p-1.5 hover:bg-gray-100 rounded-lg transition-colors hidden sm:block" 
                          title="KI generieren"
                          :disabled="!settings.aiReadAccess"
                          @click="generateAI(email.id)"
                        >
                          <!-- Shield Icon -->
                          <svg class="w-3 h-3 sm:w-4 sm:h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2m0 0l4-4m-6 2a9 9 0 1118 0 9 9 0 01-18 0z"/>
                          </svg>
                        </button>
                        <button class="p-1 sm:p-1.5 hover:bg-gray-100 rounded-lg transition-colors" title="Mehr">
                          <!-- MoreVertical Icon -->
                          <svg class="w-3 h-3 sm:w-4 sm:h-4 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"/>
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div class="px-4 py-3 border-t border-gray-200 bg-gray-50">
              <button class="w-full py-2 text-sm text-gray-600 hover:text-gray-900 font-medium transition-colors">
                Mehr laden
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Email Detail Modal -->
    <div v-if="selectedEmail" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-2xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div class="p-6 border-b border-gray-200">
          <div class="flex items-start justify-between mb-4">
            <h2 class="text-xl font-semibold text-black">{{ selectedEmail.subject }}</h2>
            <button
              @click="selectedEmail = null"
              class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          
          <div class="flex items-center gap-4 text-sm text-gray-600">
            <div class="flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
              <span>From: {{ selectedEmail.sender.name }} ({{ selectedEmail.sender.email }})</span>
            </div>
            <div class="flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span>{{ selectedEmail.date.toLocaleString() }}</span>
            </div>
            <span :class="['px-2 py-1 rounded-lg text-xs font-medium', getStatusColor(selectedEmail.status)]">
              {{ selectedEmail.status }}
            </span>
            <span v-if="selectedEmail.priority === 'High'" class="px-2 py-1 rounded-lg text-xs font-medium bg-red-100 text-red-800">
              High Priority
            </span>
          </div>
        </div>
        
        <div class="p-6 overflow-y-auto" style="max-height: calc(90vh - 250px)">
          <div class="prose max-w-none">
            <p class="text-gray-700 leading-relaxed">{{ selectedEmail.snippet }}</p>
            <p class="text-gray-700 leading-relaxed mt-4">
              This matter requires your immediate attention. The following items need to be addressed:
            </p>
            <ul class="mt-4 space-y-2">
              <li>Alle vertraglichen Verpflichtungen überprüfen und Einhaltung sicherstellen</li>
              <li>Notwendige Unterlagen für die Einreichung vorbereiten</li>
              <li>Mit relevanten Parteien für Unterschriften koordinieren</li>
              <li>Sicherstellen, dass alle Fristen gemäß Gerichtsanforderungen eingehalten werden</li>
            </ul>
            <p class="text-gray-700 leading-relaxed mt-4">
              Bitte beachten Sie, dass Verzögerungen den Fallzeitplan und die Kundenerwartungen beeinflussen können.
            </p>
          </div>
          
          <div v-if="settings.aiReadAccess" class="mt-6 p-4 bg-gray-50 rounded-xl">
            <div class="flex items-center gap-2 mb-3">
              <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2m0 0l4-4m-6 2a9 9 0 1118 0 9 9 0 01-18 0z"/>
              </svg>
              <span class="text-sm font-medium text-gray-700">KI-Zusammenfassung</span>
            </div>
            <p class="text-sm text-gray-600">
              <span v-if="selectedEmail.type === 'Contracts'">Vertragsüberprüfung erforderlich mit Fokus auf Haftung und Zahlungsbedingungen.</span>
              <span v-if="selectedEmail.type === 'Reminders'">Terminaktualisierung - Aktion erforderlich zur Bestätigung der Verfügbarkeit.</span>
              <span v-if="selectedEmail.type === 'Terminations'">Arbeitsvertragsauflösung bereit zur abschließenden Überprüfung und Genehmigung.</span>
              <span v-if="selectedEmail.type === 'All'">Gerichtseinreichungsbestätigung erhalten - Verhandlungstermin geplant.</span>
            </p>
            <div class="mt-3 flex flex-wrap gap-2">
              <span class="px-2 py-1 bg-white rounded text-xs text-gray-600">Frist: 3 Tage</span>
              <span class="px-2 py-1 bg-white rounded text-xs text-gray-600">Aktion: Überprüfen</span>
              <span class="px-2 py-1 bg-white rounded text-xs text-gray-600">Priorität: {{ selectedEmail.priority }}</span>
            </div>
          </div>
        </div>
        
        <div class="p-6 border-t border-gray-200 bg-gray-50 flex items-center gap-3">
          <button 
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            :disabled="!settings.aiReadAccess"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3"/>
            </svg>
            KI-Antwort generieren
          </button>
          <button class="px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            In Dokument konvertieren
          </button>
          <button class="px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
            Schedule Follow-up
          </button>
        </div>
      </div>
    </div>

    <!-- Settings Modal -->
    <div v-if="showSettings" class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-2xl shadow-xl max-w-md w-full">
        <div class="p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-6">E-Mail Einstellungen</h2>
          
          <div class="space-y-4">
            <label class="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                v-model="settings.aiReadAccess"
                class="w-4 h-4 rounded border-gray-300"
              />
              <span class="text-sm text-gray-700">KI-Lesezugriff erlauben</span>
            </label>
            
            <label class="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                v-model="settings.draftOnlyMode"
                class="w-4 h-4 rounded border-gray-300"
              />
              <span class="text-sm text-gray-700">Nur-Entwurf-Modus</span>
            </label>
            
            <div class="pt-4 space-y-2">
              <p class="text-xs text-gray-500">
                Zustimmungszeitpunkt: {{ settings.consentTimestamp ? settings.consentTimestamp.toLocaleString('de-DE') : '—' }}
              </p>
              <p class="text-xs text-gray-500">
                Letzte Synchronisation: {{ lastSyncTime.toLocaleDateString('de-DE') }} {{ lastSyncTime.toLocaleTimeString('de-DE') }}
              </p>
            </div>
            
            <button
              @click="handleRevokeAccess"
              class="w-full mt-4 px-4 py-2 text-sm text-red-600 hover:text-red-700 font-medium"
            >
              Zugriff widerrufen
            </button>
          </div>
        </div>
        
        <div class="p-4 border-t border-gray-200 bg-gray-50">
          <button
            @click="showSettings = false"
            class="w-full px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Schließen
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
definePageMeta({ layout: 'authenticated' })

// Reactive state
const currentView = ref('consent')
const selectedEmail = ref(null)
const activeFilter = ref('All')
const searchQuery = ref('')
const emails = ref([])
const loading = ref(false)
const showSettings = ref(false)
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

// Mock email data with legal/professional context
const mockEmails = [
  {
    id: 1,
    sender: { name: 'Sarah Mitchell', email: 'smitchell@lawfirm.com', initials: 'SM' },
    subject: 'Contract Review - Henderson Case',
    snippet: 'Please review the attached settlement agreement for the Henderson matter. Key terms include confidentiality clauses, payment schedules, and liability waivers...',
    date: new Date('2025-09-12T10:30:00'),
    type: 'Contracts',
    status: 'Ungelesen',
    priority: 'High',
    hasAttachment: true
  },
  {
    id: 2,
    sender: { name: 'James Chen', email: 'jchen@corporate.com', initials: 'JC' },
    subject: 'Deposition Schedule Update',
    snippet: 'The deposition scheduled for next Tuesday has been moved to Thursday at 2 PM. All parties have been notified...',
    date: new Date('2025-09-11T15:45:00'),
    type: 'Reminders',
    status: 'Read',
    priority: 'Normal',
    hasAttachment: false
  },
  {
    id: 3,
    sender: { name: 'Emily Rodriguez', email: 'erodriguez@client.com', initials: 'ER' },
    subject: 'Termination Agreement - Final Draft',
    snippet: 'Attached is the final draft of the employment termination agreement with all requested revisions including severance terms...',
    date: new Date('2025-09-11T09:15:00'),
    type: 'Terminations',
    status: 'AI Draft',
    priority: 'High',
    hasAttachment: true
  },
  {
    id: 4,
    sender: { name: 'Court Clerk', email: 'clerk@court.gov', initials: 'CC' },
    subject: 'Filing Confirmation - Case 2025-CV-1842',
    snippet: 'Your motion has been successfully filed. The hearing is scheduled for September 25th at 10:00 AM in Courtroom 3B...',
    date: new Date('2025-09-10T14:20:00'),
    type: 'All',
    status: 'Read',
    priority: 'Normal',
    hasAttachment: false
  },
  {
    id: 5,
    sender: { name: 'Michael Thompson', email: 'mthompson@opposing.com', initials: 'MT' },
    subject: 'Discovery Request - Johnson v. Smith',
    snippet: 'Please provide all documents related to the incident of March 15, 2025. Response due within 30 days...',
    date: new Date('2025-09-10T11:00:00'),
    type: 'Contracts',
    status: 'Ungelesen',
    priority: 'High',
    hasAttachment: true
  },
  {
    id: 6,
    sender: { name: 'Legal Assistant', email: 'assistant@lawfirm.com', initials: 'LA' },
    subject: 'Client Meeting Reminder - Tomorrow 3 PM',
    snippet: 'Reminder: You have a client meeting scheduled for tomorrow at 3 PM. Conference room B is reserved...',
    date: new Date('2025-09-09T16:30:00'),
    type: 'Reminders',
    status: 'AI Pending',
    priority: 'Normal',
    hasAttachment: false
  }
]

// Computed properties
const filterTabs = computed(() => [
  { key: 'All', label: 'Alle' },
  { key: 'Unread', label: `Ungelesen (${getUnreadCount()})` },
  { key: 'Reminders', label: 'Erinnerungen' },
  { key: 'Contracts', label: 'Verträge' },
  { key: 'Terminations', label: 'Kündigungen' },
  { key: 'AI Pending', label: `KI Ausstehend (${getAIPendingCount()})` }
])

const filteredEmails = computed(() => {
  let filtered = emails.value

  if (activeFilter.value === 'Unread') {
    filtered = filtered.filter(e => e.status === 'Ungelesen')
  } else if (activeFilter.value === 'AI Pending') {
    filtered = filtered.filter(e => e.status === 'AI Pending' || e.status === 'AI Draft')
  } else if (activeFilter.value !== 'All') {
    filtered = filtered.filter(e => e.type === activeFilter.value)
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

const formatDate = (date) => {
  const now = new Date()
  const diff = now - date
  const hours = Math.floor(diff / 3600000)
  
  if (hours < 1) return 'Just now'
  if (hours < 24) return `${hours}h ago`
  if (hours < 48) return 'Yesterday'
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const formatSyncTime = () => {
  const now = new Date()
  const diff = now - lastSyncTime.value
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  
  if (seconds < 10) return 'Gerade synchronisiert'
  if (seconds < 60) return `Vor ${seconds}s synchronisiert`
  if (minutes < 60) return `Vor ${minutes}m synchronisiert`
  return `Vor ${Math.floor(minutes / 60)}h synchronisiert`
}

const getStatusColor = (status) => {
  const colors = {
    'Ungelesen': 'bg-blue-100 text-blue-700',
    'Read': 'bg-gray-100 text-gray-600',
    'AI Draft': 'bg-purple-100 text-purple-700',
    'AI Pending': 'bg-yellow-100 text-yellow-700',
    'High Priority': 'bg-red-100 text-red-700'
  }
  return colors[status] || 'bg-gray-100 text-gray-600'
}

const getUnreadCount = () => {
  return emails.value.filter(e => e.status === 'Ungelesen').length
}

const getAIPendingCount = () => {
  return emails.value.filter(e => e.status === 'AI Pending' || e.status === 'AI Draft').length
}

const markAsRead = (emailId) => {
  const email = emails.value.find(e => e.id === emailId)
  if (email) {
    email.status = 'Read'
  }
}

const generateAI = (emailId) => {
  if (settings.value.aiReadAccess) {
    const email = emails.value.find(e => e.id === emailId)
    if (email) {
      email.status = 'AI Draft'
    }
  }
}

const handleRevokeAccess = () => {
  if (confirm('Are you sure you want to revoke email access? You will need to reconnect to use this feature.')) {
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

const handleKeydown = (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault()
    e.target.focus()
  }
}

// Watchers and lifecycle
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

// Auto-refresh every 30 seconds
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