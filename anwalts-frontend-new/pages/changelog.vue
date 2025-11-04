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
        <h1 class="text-4xl font-bold text-white mb-6">Changelog</h1>
        <div class="text-white/90 space-y-8">
          
          <!-- Version 1.0.7 -->
          <div class="border-l-4 border-blue-500 pl-6">
            <div class="flex items-center gap-3 mb-2">
              <h2 class="text-2xl font-semibold text-white">Version 1.0.7</h2>
              <span class="bg-green-500/20 text-green-400 px-3 py-1 rounded-full text-sm">Latest</span>
            </div>
            <p class="text-sm text-white/70 mb-4">Released: January 2025</p>
            <ul class="list-disc list-inside space-y-2">
              <li>🔧 Fixed authentication flow and removed external dependencies</li>
              <li>✨ Improved glassmorphism design across all pages</li>
              <li>🛡️ Enhanced security and data protection</li>
              <li>🚀 Performance optimizations</li>
            </ul>
          </div>
          
          <!-- Version 1.0.6 -->
          <div class="border-l-4 border-gray-500 pl-6">
            <h2 class="text-2xl font-semibold text-white mb-2">Version 1.0.6</h2>
            <p class="text-sm text-white/70 mb-4">Released: December 2024</p>
            <ul class="list-disc list-inside space-y-2">
              <li>📄 Enhanced document analysis capabilities</li>
              <li>🤖 Improved AI assistant responses</li>
              <li>🎨 UI/UX improvements</li>
            </ul>
          </div>
          
          <!-- Version 1.0.5 -->
          <div class="border-l-4 border-gray-500 pl-6">
            <h2 class="text-2xl font-semibold text-white mb-2">Version 1.0.5</h2>
            <p class="text-sm text-white/70 mb-4">Released: November 2024</p>
            <ul class="list-disc list-inside space-y-2">
              <li>⚖️ Extended legal database coverage</li>
              <li>🔍 Improved search functionality</li>
              <li>📊 Added analytics dashboard</li>
            </ul>
          </div>
          
          <!-- Version 1.0.4 -->
          <div class="border-l-4 border-gray-500 pl-6">
            <h2 class="text-2xl font-semibold text-white mb-2">Version 1.0.4</h2>
            <p class="text-sm text-white/70 mb-4">Released: October 2024</p>
            <ul class="list-disc list-inside space-y-2">
              <li>🔐 Enhanced user authentication</li>
              <li>💾 Improved data storage and backup</li>
              <li>🐛 Various bug fixes and improvements</li>
            </ul>
          </div>
          
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