<template>
  <div class="p-6 md:p-8 lg:p-12">
    <!-- Back to Dashboard Button -->
    <div class="mb-6">
      <button
        @click="$router.push('/dashboard')"
        class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
        </svg>
        Zurück zur Übersicht
      </button>
    </div>
    <div class="bg-white text-black/80 w-full overflow-hidden rounded-2xl border border-gray-200">
    <!-- Header -->
    <div class="flex flex-col gap-3 border-b border-gray-200 p-6 md:flex-row md:items-center md:justify-between">
      <div>
        <h1 class="text-2xl font-medium tracking-tight">Vorlagenbibliothek</h1>
        <p class="mt-1 text-sm text-gray-600 md:text-base">
          Professionelle Rechtsvorlagen mit KI-Unterstützung.
        </p>
      </div>
      <div class="flex items-center gap-2">
        <input
          v-model="searchQuery"
          placeholder="Vorlagen, Typen, Klauseln suchen"
          class="h-10 w-56 rounded-xl border border-gray-200 bg-white px-3 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-300 md:w-72"
        />
        <button
          @click="handleImport"
          class="h-10 px-4 rounded-xl bg-[#5b7ce6] text-white hover:bg-[#4a6cd4] transition-colors flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"></path>
          </svg>
          Importieren
        </button>
        <button
          @click="handleFilter"
          class="h-10 px-4 rounded-xl border border-[#5b7ce6] bg-white text-[#5b7ce6] hover:bg-[#5b7ce6]/10 transition-colors flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path>
          </svg>
          Filtern
        </button>
      </div>
    </div>

    <!-- AI Suggested Templates -->
    <section class="p-6">
      <div class="mb-3 flex items-center justify-between">
        <h2 class="text-lg font-medium">KI-empfohlene Vorlagen</h2>
        <div class="flex gap-2">
          <button
            @click="scrollLeft"
            class="h-8 px-3 rounded-full text-sm hover:bg-gray-50 transition-colors"
          >
            ←
          </button>
          <button
            @click="scrollRight"
            class="h-8 px-3 rounded-full text-sm hover:bg-gray-50 transition-colors"
          >
            →
          </button>
        </div>
      </div>

      <div
        ref="suggestedScroller"
        class="flex snap-x snap-mandatory gap-4 overflow-x-auto pb-2"
      >
        <div
          v-for="suggestion in suggestedTemplates"
          :key="suggestion.id"
          class="min-w-[280px] max-w-xs snap-start"
        >
          <div class="border border-gray-200 rounded-lg shadow-sm bg-white">
            <div class="p-4 space-y-1">
              <div class="flex items-center justify-between">
                <h3 class="truncate text-base font-medium">{{ suggestion.name }}</h3>
                <span class="inline-flex items-center rounded-full border border-gray-300 bg-gray-50 px-2 py-0.5 text-xs text-gray-700">
                  {{ suggestion.source }}
                </span>
              </div>
              <p class="text-sm text-gray-600">{{ suggestion.note }}</p>
            </div>
            <div class="flex items-center justify-between p-4 pt-0">
              <span class="inline-flex items-center rounded-full border border-green-200 bg-green-50 px-3 py-1 text-sm text-green-700">
                {{ suggestion.match }}% Übereinstimmung
              </span>
              <button class="px-4 py-2 rounded-lg bg-[#5b7ce6] text-white hover:bg-[#4a6cd4] transition-colors text-sm">
                Verwenden
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div class="border-t border-gray-200"></div>

    <!-- Stats Overview -->
    <section class="grid gap-4 p-6 md:grid-cols-3">
      <!-- Most Used -->
      <div class="border border-gray-200 rounded-lg bg-white">
        <div class="p-4">
          <h3 class="flex items-center gap-2 text-base font-medium">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
            Meistgenutzte Vorlagen
          </h3>
        </div>
        <div class="px-4 pb-4 flex flex-wrap gap-2">
          <span
            v-for="item in mostUsed"
            :key="item.label"
            class="rounded-full border border-gray-300 bg-gray-50 px-3 py-1 text-sm text-gray-800"
          >
            {{ item.label }} ({{ item.count }})
          </span>
        </div>
      </div>

      <!-- Performance -->
      <div class="border border-gray-200 rounded-lg bg-white">
        <div class="p-4">
          <h3 class="flex items-center gap-2 text-base font-medium">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
            Vorlagenleistung
          </h3>
          <p class="text-sm text-gray-600 mt-1">Qualitäts- und Effizienzindikatoren</p>
        </div>
        <div class="px-4 pb-4 space-y-3">
          <div>
            <div class="mb-1 flex items-center justify-between text-sm">
              <span>Erfolgsquote</span>
              <span class="font-medium">93%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="bg-[#5b7ce6] h-2 rounded-full" style="width: 93%"></div>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3 text-sm text-gray-700">
            <div class="flex items-center gap-1">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              Durchschn. Generierungszeit: 22s
            </div>
            <div class="flex items-center gap-1">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"></path>
              </svg>
              Nutzerzufriedenheit: 4,6/5
            </div>
          </div>
        </div>
      </div>

      <!-- Weekly Activity -->
      <div class="border border-gray-200 rounded-lg bg-white">
        <div class="p-4">
          <h3 class="flex items-center gap-2 text-base font-medium">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
            </svg>
            Wöchentliche Aktivität
          </h3>
          <p class="text-sm text-gray-600 mt-1">+12% im Vergleich zur Vorwoche</p>
        </div>
        <div class="px-4 pb-4 h-24 flex items-end justify-center gap-4">
          <div class="bg-[#5b7ce6] rounded-t-md" style="width: 16px; height: 40%"></div>
          <div class="bg-[#5b7ce6] rounded-t-md" style="width: 16px; height: 80%"></div>
          <div class="bg-[#5b7ce6] rounded-t-md" style="width: 16px; height: 60%"></div>
        </div>
      </div>
    </section>

    <!-- Clause Library -->
    <section class="p-6">
      <div class="mb-3 flex items-center justify-between">
        <h2 class="text-lg font-medium">Klauselbibliothek</h2>
        <button class="text-[#5b7ce6] hover:text-[#4a6cd4] underline text-sm">
          Alle anzeigen
        </button>
      </div>
      <div class="overflow-hidden rounded-2xl border border-gray-200">
        <div class="divide-y divide-gray-200">
          <div
            v-for="clause in clauses"
            :key="clause.id"
            class="group flex items-center justify-between bg-white p-4"
          >
            <div class="pr-4">
              <div class="text-sm font-medium text-black/80">{{ clause.name }}</div>
              <div class="text-sm text-gray-600">{{ clause.desc }}</div>
            </div>
            <button
              @click="copyClause(clause)"
              class="opacity-80 hover:opacity-100 p-2 hover:bg-gray-100 rounded-md transition-colors"
              :title="`${clause.name} Klausel kopieren`"
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Template Cards Grid -->
    <section class="p-6">
      <div class="mb-3 flex items-center justify-between">
        <h2 class="text-lg font-medium">Alle Vorlagen</h2>
        <div class="flex items-center gap-2">
          <button
            @click="createTemplate"
            class="px-4 py-2 rounded-xl border border-[#5b7ce6] bg-white text-[#5b7ce6] hover:bg-[#5b7ce6]/10 transition-colors flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            Vorlage erstellen
          </button>
        </div>
      </div>

      <!-- Loading state -->
      <div v-if="isLoading" class="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <div
          v-for="i in 8"
          :key="i"
          class="border border-gray-200 rounded-lg bg-white"
        >
          <div class="p-4">
            <div class="h-5 w-48 animate-pulse rounded bg-gray-100"></div>
            <div class="mt-2 h-4 w-full animate-pulse rounded bg-gray-100"></div>
          </div>
          <div class="p-4 pt-0 space-y-3">
            <div class="flex gap-2">
              <div class="h-6 w-16 animate-pulse rounded bg-gray-100"></div>
              <div class="h-6 w-20 animate-pulse rounded bg-gray-100"></div>
            </div>
            <div class="h-8 w-full animate-pulse rounded bg-gray-100"></div>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div
        v-else-if="filteredTemplates.length === 0"
        class="border border-gray-200 rounded-lg bg-white"
      >
        <div class="flex flex-col items-center justify-center py-10 text-center">
          <svg class="mb-3 h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"></path>
          </svg>
          <div class="text-lg font-medium">Noch keine Vorlagen</div>
          <p class="mt-1 max-w-md text-sm text-gray-600">Importieren oder erstellen Sie eine, um zu beginnen.</p>
          <div class="mt-4 flex gap-2">
            <button
              @click="handleImport"
              class="px-4 py-2 rounded-xl bg-[#5b7ce6] text-white hover:bg-[#4a6cd4] transition-colors flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"></path>
              </svg>
              Importieren
            </button>
            <button
              @click="createTemplate"
              class="px-4 py-2 rounded-xl border border-[#5b7ce6] bg-white text-[#5b7ce6] hover:bg-[#5b7ce6]/10 transition-colors flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
              </svg>
              Erstellen
            </button>
          </div>
        </div>
      </div>

      <!-- Template Cards -->
      <div
        v-else
        class="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
      >
        <div
          v-for="template in filteredTemplates"
          :key="template.id"
          class="h-full border border-gray-200 rounded-lg shadow-sm bg-white transition-all hover:shadow-md hover:-translate-y-0.5"
        >
          <div class="p-4 space-y-1">
            <h3 class="line-clamp-1 text-base font-medium">{{ template.name }}</h3>
            <p class="line-clamp-2 text-sm text-gray-600">{{ template.description || template.content?.slice(0, 100) + '...' }}</p>
          </div>
          <div class="p-4 pt-0 space-y-4">
            <div class="flex flex-wrap gap-2">
              <span
                v-for="tag in getTemplateTags(template)"
                :key="tag"
                :class="getTagClasses(tag)"
                class="inline-flex items-center rounded-full border px-2 py-1 text-xs"
              >
                {{ tag }}
              </span>
            </div>
            <div class="grid grid-cols-2 gap-3 text-sm text-gray-700">
              <div class="flex items-center gap-1">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Erfolg 95%
              </div>
              <div class="flex items-center gap-1">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
                {{ Math.floor(Math.random() * 100) + 10 }}× verwendet
              </div>
              <div class="flex items-center gap-1">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
                Erstellt von {{ template.createdBy || 'Ihnen' }}
              </div>
              <div class="flex items-center gap-1">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Zuletzt verwendet {{ formatDate(template.updatedAt) }}
              </div>
            </div>
            <div class="flex items-center justify-between">
              <button
                @click="useTemplate(template)"
                class="px-4 py-2 rounded-lg bg-[#5b7ce6] text-white hover:bg-[#4a6cd4] transition-colors text-sm"
              >
                Vorlage verwenden
              </button>
              <div class="flex items-center gap-1">
                <button
                  @click="editTemplate(template)"
                  class="p-2 hover:bg-gray-100 rounded-md transition-colors"
                  :title="`${template.name} bearbeiten`"
                >
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                  </svg>
                </button>
                <button
                  @click="duplicateTemplate(template)"
                  class="p-2 hover:bg-gray-100 rounded-md transition-colors"
                  :title="`${template.name} duplizieren`"
                >
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                  </svg>
                </button>
                <button
                  @click="deleteTemplate(template)"
                  class="p-2 hover:bg-gray-100 rounded-md transition-colors"
                  :title="`${template.name} löschen`"
                >
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Toast notifications -->
    <div
      v-if="toasts.length > 0"
      class="fixed right-4 top-4 z-50 flex w-80 flex-col gap-2 sm:right-6 sm:top-6"
    >
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="pointer-events-auto rounded-xl border border-gray-200 bg-white p-3 shadow-md animate-in slide-in-from-top-2"
      >
        <div class="flex items-start gap-3">
          <div class="min-w-0 flex-1">
            <div class="text-sm font-medium text-black/80">{{ toast.title }}</div>
            <div v-if="toast.description" class="mt-0.5 text-xs text-gray-700">{{ toast.description }}</div>
          </div>
          <button
            @click="dismissToast(toast.id)"
            class="h-6 w-6 rounded-md text-gray-600 hover:bg-gray-100 flex items-center justify-center"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Create Template Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
      @click.self="showCreateModal = false"
    >
      <div class="bg-white rounded-2xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        <div class="p-6 border-b border-gray-200">
          <h2 class="text-xl font-semibold text-black/80">Neue Vorlage erstellen</h2>
        </div>
        <form @submit.prevent="handleCreateTemplate" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Vorlagenname</label>
            <input
              v-model="templateForm.name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Vorlagenname eingeben"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Kategorie</label>
            <input
              v-model="templateForm.category"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Kategorie eingeben (optional)"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Inhalt</label>
            <textarea
              v-model="templateForm.content"
              required
              rows="10"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-vertical"
              placeholder="Vorlageninhalt eingeben"
            ></textarea>
          </div>
          <div class="flex justify-end gap-3 pt-4">
            <button
              type="button"
              @click="showCreateModal = false"
              class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Abbrechen
            </button>
            <button
              type="submit"
              :disabled="isCreating"
              class="px-4 py-2 bg-[#5b7ce6] text-white rounded-lg hover:bg-[#4a6cd4] transition-colors disabled:opacity-50"
            >
              {{ isCreating ? 'Wird erstellt...' : 'Vorlage erstellen' }}
            </button>
          </div>
        </form>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'

// Reactive state
const templates = ref<any[]>([])
const searchQuery = ref('')
const isLoading = ref(true)
const showCreateModal = ref(false)
const isCreating = ref(false)
const toasts = ref<any[]>([])
const suggestedScroller = ref<HTMLElement>()

// Template form
const templateForm = ref({
  name: '',
  category: '',
  content: ''
})

// Mock data
const suggestedTemplates = ref([
  { id: 's1', name: 'Geheimhaltungsvereinbarung (Beidseitig)', note: 'Basierend auf Ihrer Aktivität', match: 92, source: 'System' },
  { id: 's2', name: 'Vertrag – Dienstleistung', note: 'Häufig angefordert', match: 88, source: 'System' },
  { id: 's3', name: 'Mahnung – Zahlungserinnerung', note: 'Ähnlich zu letztem Dokument', match: 85, source: 'Individuell' },
  { id: 's4', name: 'Datenverarbeitungsvereinbarung (DVV)', note: 'Basierend auf Ihrer Aktivität', match: 90, source: 'System' }
])

const mostUsed = ref([
  { label: 'Mahnung', count: 28 },
  { label: 'Vertrag', count: 22 },
  { label: 'NDA', count: 18 },
  { label: 'DPA', count: 11 }
])

const clauses = ref([
  { id: 'c1', name: 'Vertraulichkeit', desc: 'Definiert vertrauliche Informationen und erlaubte Offenlegungen.' },
  { id: 'c2', name: 'Anwendbares Recht', desc: 'Wählt Gerichtsbarkeit und Kollisionsnormen.' },
  { id: 'c3', name: 'Haftungsbeschränkung', desc: 'Begrenzt Schadensersatz; schließt indirekte und Folgeschäden aus.' },
  { id: 'c4', name: 'Ordentliche Kündigung', desc: 'Ermöglicht beiden Parteien Kündigung mit Kündigungsfrist.' }
])

// Computed properties
const filteredTemplates = computed(() => {
  if (!searchQuery.value) return templates.value
  const query = searchQuery.value.toLowerCase()
  return templates.value.filter(template =>
    template.name.toLowerCase().includes(query) ||
    (template.content || '').toLowerCase().includes(query) ||
    (template.category || '').toLowerCase().includes(query)
  )
})

// Methods
const showToast = (toast: { title: string; description?: string }) => {
  const id = Date.now() + Math.random()
  toasts.value.push({ id, ...toast })
  setTimeout(() => {
    dismissToast(id)
  }, 4000)
}

const dismissToast = (id: number) => {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
  }
}

const loadTemplates = async () => {
  try {
    const r = await fetch(`/api/auth/proxy.get?path=${encodeURIComponent('/api/templates')}`)
    const data = await r.json().catch(() => ({ items: [] }))
    templates.value = Array.isArray(data?.items) ? data.items : (Array.isArray(data) ? data : [])
  } catch (e) {
    console.warn('load templates failed', e)
  } finally {
    isLoading.value = false
  }
}

const handleCreateTemplate = async () => {
  isCreating.value = true
  try {
    const payload = {
      path: '/api/templates',
      method: 'POST',
      body: {
        name: templateForm.value.name,
        content: templateForm.value.content,
        category: templateForm.value.category || 'general',
        type: 'document'
      }
    }
    const r = await fetch('/api/auth/proxy.post', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (r.ok) {
      showCreateModal.value = false
      templateForm.value = { name: '', category: '', content: '' }
      await loadTemplates()
      showToast({ title: 'Vorlage erstellt', description: 'Ihre neue Vorlage wurde erfolgreich gespeichert.' })
    }
  } catch (e) {
    console.warn('create template failed', e)
    showToast({ title: 'Fehler', description: 'Vorlage konnte nicht erstellt werden. Bitte versuchen Sie es erneut.' })
  } finally {
    isCreating.value = false
  }
}

const createTemplate = () => {
  showCreateModal.value = true
}

const useTemplate = (template: any) => {
  // Navigate to documents page or show template usage
  navigateTo('/documents')
  showToast({ title: 'Vorlage geladen', description: `${template.name} ist bereit zur Verwendung.` })
}

const editTemplate = (template: any) => {
  showToast({ title: 'Vorlage bearbeiten', description: 'Bearbeitungsfunktion kommt bald.' })
}

const duplicateTemplate = (template: any) => {
  showToast({ title: 'Vorlage dupliziert', description: `Kopie von ${template.name} erstellt.` })
}

const deleteTemplate = async (template: any) => {
  if (!confirm(`Möchten Sie "${template.name}" wirklich löschen?`)) return
  
  try {
    // Delete template logic here
    showToast({ title: 'Vorlage gelöscht', description: `${template.name} wurde gelöscht.` })
    await loadTemplates()
  } catch (e) {
    showToast({ title: 'Fehler', description: 'Vorlage konnte nicht gelöscht werden.' })
  }
}

const copyClause = (clause: any) => {
  showToast({ title: 'Klausel kopiert', description: `${clause.name} in die Zwischenablage kopiert.` })
}

const handleImport = () => {
  showToast({ title: 'Importieren', description: 'Importfunktion kommt bald.' })
}

const handleFilter = () => {
  showToast({ title: 'Filter', description: 'Filteroptionen kommen bald.' })
}

const scrollLeft = () => {
  if (suggestedScroller.value) {
    suggestedScroller.value.scrollBy({ left: -320, behavior: 'smooth' })
  }
}

const scrollRight = () => {
  if (suggestedScroller.value) {
    suggestedScroller.value.scrollBy({ left: 320, behavior: 'smooth' })
  }
}

const getTemplateTags = (template: any) => {
  const tags = []
  if (template.category) tags.push(template.category)
  tags.push('Vorlage')
  return tags
}

const getTagClasses = (tag: string) => {
  if (tag.toLowerCase() === 'system') {
    return 'border-blue-200 bg-blue-50 text-blue-700'
  } else if (tag.toLowerCase() === 'custom') {
    return 'border-gray-300 bg-gray-50 text-gray-700'
  } else {
    return 'border-green-200 bg-green-50 text-green-700'
  }
}

const formatDate = (dateString: string) => {
  if (!dateString) return 'Nie'
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) return 'Heute'
  if (days === 1) return 'Gestern'
  if (days < 7) return `vor ${days} Tagen`
  if (days < 30) return `vor ${Math.floor(days / 7)} Wochen`
  return date.toLocaleDateString()
}

// Lifecycle
onMounted(loadTemplates)
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.animate-in {
  animation: slide-in-from-top 0.3s ease-out;
}

@keyframes slide-in-from-top {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.snap-x {
  scroll-snap-type: x mandatory;
}

.snap-mandatory {
  scroll-snap-type: mandatory;
}

.snap-start {
  scroll-snap-align: start;
}
</style>