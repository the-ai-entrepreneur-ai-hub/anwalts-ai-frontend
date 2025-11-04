<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
    <!-- Header -->
    <header class="bg-white/10 backdrop-blur-md border-b border-white/20">
      <div class="container mx-auto px-4 py-4 flex items-center justify-between">
        <NuxtLink to="/" class="text-2xl font-bold text-white">ANWALTS.AI</NuxtLink>
        <NuxtLink to="/" class="text-white/80 hover:text-white transition-colors">← Zurück</NuxtLink>
      </div>
    </header>

    <!-- Content -->
    <div class="container mx-auto px-4 py-12">
      <div class="max-w-4xl mx-auto bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 p-8">
        <h1 class="text-4xl font-bold text-white mb-6">Datenschutzerklärung</h1>
        <div class="text-white/90 prose prose-invert max-w-none">
          <p class="text-lg mb-6">Letzte Aktualisierung: 23. Januar 2025</p>
          
          <p class="mb-6">Willkommen bei ANWALTS.AI. Diese Datenschutzerklärung erklärt, wie wir Ihre persönlichen Daten sammeln, verwenden und schützen.</p>
          
          <h2 class="text-2xl font-semibold text-white mt-8 mb-4">1. Datenerfassung</h2>
          <p class="mb-4">Wir erfassen personenbezogene Daten wie Namen, E-Mail-Adressen und Kontaktdaten, wenn Sie sich registrieren oder unsere Dienste nutzen.</p>
          
          <h2 class="text-2xl font-semibold text-white mt-8 mb-4">2. Datenverwendung</h2>
          <ul class="list-disc list-inside mb-6 space-y-2">
            <li>Bereitstellung und Wartung unserer Dienste</li>
            <li>Kommunikation bezüglich Ihres Kontos</li>
            <li>Verbesserung unserer Dienste</li>
            <li>Einhaltung rechtlicher Verpflichtungen</li>
          </ul>
          
          <h2 class="text-2xl font-semibold text-white mt-8 mb-4">3. Datensicherheit</h2>
          <p class="mb-4">Wir implementieren angemessene Sicherheitsmaßnahmen zum Schutz Ihrer Daten gemäß den geltenden Datenschutzgesetzen.</p>
          
          <h2 class="text-2xl font-semibold text-white mt-8 mb-4">4. Ihre Rechte</h2>
          <p class="mb-4">Sie haben das Recht auf Zugang, Berichtigung oder Löschung Ihrer Daten. Kontaktieren Sie uns für Unterstützung bei Ihren Datenrechten.</p>
          
          <h2 class="text-2xl font-semibold text-white mt-8 mb-4">5. Kontakt</h2>
          <p class="mb-4">Bei Fragen zu dieser Datenschutzerklärung kontaktieren Sie uns über unsere Website.</p>
          
          <div class="mt-12 pt-6 border-t border-white/20">
            <NuxtLink to="/" class="inline-block bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all">
              Zurück zur Startseite
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
definePageMeta({
  layout: false
})
</script>