<template>
  <div class="space-y-6 animate-pulse">
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <div v-for="index in 4" :key="index" class="card p-6">
        <div class="flex items-center justify-between">
          <div class="space-y-2">
            <div class="h-3 w-24 rounded bg-gray-200" />
            <div class="h-8 w-20 rounded bg-gray-200" />
            <div class="h-3 w-32 rounded bg-gray-100" />
          </div>
          <div class="h-12 w-12 rounded-lg bg-gray-100" />
        </div>
      </div>
    </div>
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
      <div v-for="index in 2" :key="`chart-${index}`" class="card p-6">
        <div class="h-5 w-48 rounded bg-gray-200 mb-4" />
        <div class="h-64 rounded bg-gray-100" />
      </div>
    </div>
    <div class="card p-6">
      <div class="h-5 w-40 rounded bg-gray-200 mb-4" />
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div v-for="index in 3" :key="`status-${index}`" class="p-4 rounded-lg border border-gray-200 bg-gray-50">
          <div class="h-4 w-24 rounded bg-gray-200 mb-2" />
          <div class="h-3 w-16 rounded bg-gray-100 mb-1" />
          <div class="h-3 w-20 rounded bg-gray-100" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>
