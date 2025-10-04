<template>
  <div class="min-h-screen bg-white">
    <div class="max-w-4xl mx-auto p-6">
      <h1 class="text-2xl font-semibold mb-4">E-Mail Posteingang</h1>
      <p class="text-gray-600 mb-6">Verbinden Sie Ihr Gmail-Konto, um E-Mails im Portal zu sehen.</p>
      <div class="flex gap-3">
        <NuxtLink to="/auth/google" class="px-4 py-2 bg-blue-600 text-white rounded-lg">Mit Google verbinden</NuxtLink>
        <NuxtLink to="/dashboard" class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg">Zurück zum Dashboard</NuxtLink>
      </div>
      <div class="mt-8">
        <p class="text-sm text-gray-500">Nach der Verbindung erscheinen hier Ihre neuesten E-Mails.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
definePageMeta({ layout: false, middleware: 'auth-guard' })
</script>

