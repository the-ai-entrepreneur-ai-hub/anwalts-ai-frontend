<template>
  <PortalShell>
    <template #header>
      <header class="bg-white shadow-sm border-b">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex justify-between h-16">
            <div class="flex items-center">
              <NuxtLink to="/dashboard" class="text-blue-600 hover:text-blue-700 mr-4">← Back</NuxtLink>
              <h1 class="text-xl font-bold text-blue-600">Legal Research</h1>
            </div>
          </div>
        </div>
      </header>
    </template>
    <div class="max-w-4xl mx-auto p-6">
      <h2 class="text-2xl font-bold mb-4">Legal Research</h2>
      <p class="text-gray-600">Advanced legal research tools coming soon...</p>
    </div>
  </PortalShell>
</template>

<script setup>
import PortalShell from '~/components/PortalShell.vue'

definePageMeta({ layout: false })
</script>
