<template>
  <div class="min-h-screen bg-white">
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
          <a href="/dashboard" class="sidebar-link active" aria-current="page" title="Übersicht öffnen">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0h6"></path>
            </svg>
            <span>Übersicht</span>
          </a>
          
          <a href="/assistant" class="sidebar-link" title="KI-Assistent öffnen">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
            </svg>
            <span>KI-Assistent</span>
          </a>
          
          <a href="/documents" class="sidebar-link" title="Dokumente öffnen">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            <span>Dokumente</span>
          </a>
          
          <a href="/email/" class="sidebar-link" title="E-Mails öffnen">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
            </svg>
            <span>E-Mails</span>
          </a>
          
          <a href="/dashboard/settings" class="sidebar-link" title="Einstellungen öffnen">
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
              <p class="text-sm font-medium text-gray-900">Dr. Max Müller</p>
              <p class="text-xs text-gray-500">Senior Partner</p>
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
                <input type="search" placeholder="Suche..." class="w-full px-4 py-2 border border-gray-300 rounded-lg" aria-label="Suche" />
              </div>
            </div>
            
            <div class="flex items-center gap-3">
              <button class="px-4 py-2 bg-blue-600 text-white rounded-lg" aria-label="Neues Dokument erstellen">Neues Dokument</button>
              <a href="/api/auth/logout" class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg" role="button">Abmelden</a>
            </div>
          </div>
        </header>
        
        <!-- Dashboard Content -->
        <div class="p-8">
          <div class="mb-6">
            <h2 class="text-2xl font-semibold text-gray-900">Übersicht</h2>
            <p class="text-gray-500 mt-1">Willkommen zurück, Dr. Müller</p>
          </div>
          
          <!-- Stats Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div class="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
              <div class="text-2xl font-semibold text-gray-900">42</div>
              <div class="text-sm text-gray-500 mt-1">Neue Fälle</div>
            </div>
            <div class="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
              <div class="text-2xl font-semibold text-gray-900">156</div>
              <div class="text-sm text-gray-500 mt-1">Dokumente</div>
            </div>
            <div class="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
              <div class="text-2xl font-semibold text-gray-900">389</div>
              <div class="text-sm text-gray-500 mt-1">E-Mails</div>
            </div>
            <div class="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
              <div class="text-2xl font-semibold text-gray-900">28. Aug</div>
              <div class="text-sm text-gray-500 mt-1">Nächste Frist</div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
definePageMeta({ 
  layout: false,
  middleware: 'auth-guard'
})
</script>

<style>
.sidebar-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: #6b7280;
  text-decoration: none;
  border-radius: 0.5rem;
  transition: all 0.2s;
  margin-bottom: 0.25rem;
}

.sidebar-link:hover {
  background-color: #f3f4f6;
  color: #374151;
}

.sidebar-link.active {
  background-color: #eff6ff;
  color: #2563eb;
}
</style>