<template>
  <div class="min-h-screen bg-gray-50">
    <div class="flex h-screen overflow-hidden">
      <!-- Sidebar: Hidden on mobile, visible md+ -->
      <aside class="relative w-64 bg-white border-r border-gray-200 flex-shrink-0 hidden md:flex md:flex-col">
        <!-- Logo -->
        <div class="p-6 border-b border-gray-200 flex-shrink-0">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center text-white font-bold shadow-sm">
              A
            </div>
            <div>
              <h1 class="font-semibold text-gray-900">ANWALTS.AI</h1>
              <p class="text-xs text-gray-500">Kanzlei-Dashboard</p>
            </div>
          </div>
        </div>

        <!-- Navigation -->
        <nav class="flex-1 p-4 overflow-y-auto">
          <NuxtLink
            v-for="link in navLinks"
            :key="link.id"
            :to="link.href"
            :class="[
              'flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200',
              isActive(link.href)
                ? 'bg-blue-50 text-blue-700'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            ]"
            :title="link.title"
          >
            <component :is="'svg'" class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="link.iconPath" />
            </component>
            <span>{{ link.label }}</span>
          </NuxtLink>
        </nav>

        <!-- User Profile -->
        <div class="p-4 border-t border-gray-200 flex-shrink-0">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-gradient-to-br from-gray-200 to-gray-300 rounded-full flex items-center justify-center text-gray-600 font-semibold text-sm">
              {{ userInitials }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">{{ userName }}</p>
              <p class="text-xs text-gray-500 truncate">{{ userRole }}</p>
            </div>
          </div>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="flex-1 overflow-auto">
        <!-- Header -->
        <header class="bg-white border-b border-gray-200 px-4 sm:px-6 lg:px-8 py-4 sticky top-0 z-10">
          <div class="flex items-center justify-between gap-4">
            <!-- Search -->
            <div class="flex-1 max-w-2xl">
              <div class="relative">
                <input
                  id="globalSearch"
                  type="search"
                  placeholder="Suche..."
                  class="w-full px-4 py-2.5 pl-10 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
                />
                <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex items-center gap-2 sm:gap-3">
              <button
                class="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                aria-label="Benachrichtigungen"
                title="Benachrichtigungen"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
              </button>
              <button
                id="btnNewDoc"
                class="hidden sm:inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all shadow-sm"
                title="Neues Dokument (n)"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                <span>Neues Dokument</span>
              </button>
              <button
                id="btnLogout"
                @click="handleLogout"
                class="px-4 py-2.5 bg-gray-100 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all"
                title="Abmelden"
              >
                Abmelden
              </button>
            </div>
          </div>
        </header>

        <!-- Page Content Slot -->
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthUser } from '~/composables/useAuthUser'

const route = useRoute()
const { userName, userRole, userInitials, loadUser, handleLogout } = useAuthUser()

// Navigation links
const navLinks = [
  {
    id: 'overview',
    href: '/dashboard',
    label: 'Übersicht',
    title: 'Übersicht öffnen',
    iconPath: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0h6'
  },
  {
    id: 'assistant',
    href: '/assistant',
    label: 'KI-Assistent',
    title: 'KI-Assistent öffnen',
    iconPath: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z'
  },
  {
    id: 'documents',
    href: '/documents',
    label: 'Dokumente',
    title: 'Dokumente öffnen',
    iconPath: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
  },
  {
    id: 'templates',
    href: '/templates',
    label: 'Vorlagen',
    title: 'Vorlagen öffnen',
    iconPath: 'M7 7h10M7 11h10M7 15h6M5 5a2 2 0 012-2h10a2 2 0 012 2v14a2 2 0 01-2 2H7a2 2 0 01-2-2V5z'
  },
  {
    id: 'email',
    href: '/email',
    label: 'E‑Mails',
    title: 'E-Mails öffnen',
    iconPath: 'M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z'
  },
  {
    id: 'settings',
    href: '/settings',
    label: 'Einstellungen',
    title: 'Einstellungen öffnen',
    iconPath: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065zM15 12a3 3 0 11-6 0 3 3 0 016 0z'
  }
]

const isActive = (href: string) => {
  return route.path === href
}

onMounted(async () => {
  await loadUser()
})
</script>

<style scoped>
/* Custom scrollbar for webkit browsers */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
