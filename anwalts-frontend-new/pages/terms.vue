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
        <h1 class="text-4xl font-bold text-white mb-6">Terms of Service</h1>
        <div class="text-white/90 prose prose-invert max-w-none">
          <p class="text-lg mb-6">Last updated: January 23, 2025</p>
          
          <p class="mb-6">Welcome to ANWALTS.AI ("we" or "us"). These Terms of Service govern your use of our website and related services.</p>
          
          <h2 class="text-2xl font-semibold text-white mt-8 mb-4">1. Information We Collect</h2>
          <p class="mb-4">We may collect personal information such as your name, email address, and other contact details when you register for an account or use our services.</p>
          
          <h2 class="text-2xl font-semibold text-white mt-8 mb-4">2. How We Use Your Information</h2>
          <ul class="list-disc list-inside mb-6 space-y-2">
            <li>Providing and maintaining our services</li>
            <li>Communicating with you about your account</li>
            <li>Improving our services and user experience</li>
            <li>Complying with legal obligations</li>
          </ul>
          
          <h2 class="text-2xl font-semibold text-white mt-8 mb-4">3. Data Protection</h2>
          <p class="mb-4">We implement appropriate security measures to protect your personal information in accordance with applicable data protection laws.</p>
          
          <h2 class="text-2xl font-semibold text-white mt-8 mb-4">4. Your Rights</h2>
          <p class="mb-4">You have the right to access, update, or delete your personal information. Contact us if you need assistance with your data rights.</p>
          
          <h2 class="text-2xl font-semibold text-white mt-8 mb-4">5. Contact Information</h2>
          <p class="mb-4">If you have any questions about these Terms of Service, please contact us through our website.</p>
          
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