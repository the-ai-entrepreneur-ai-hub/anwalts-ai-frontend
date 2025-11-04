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
        <h1 class="text-4xl font-bold text-white mb-6">Kontakt</h1>
        <div class="text-white/90">
          <p class="text-lg mb-8">Haben Sie Fragen zu ANWALTS.AI? Wir helfen Ihnen gerne weiter!</p>
          
          <!-- Contact Form -->
          <form @submit.prevent="handleSubmit" class="space-y-6">
            <div class="grid md:grid-cols-2 gap-6">
              <div>
                <label class="block text-white mb-2">Name *</label>
                <input 
                  v-model="form.name" 
                  type="text" 
                  required
                  class="w-full bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg px-4 py-3 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ihr Name"
                />
              </div>
              <div>
                <label class="block text-white mb-2">E-Mail *</label>
                <input 
                  v-model="form.email" 
                  type="email" 
                  required
                  class="w-full bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg px-4 py-3 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="ihre@email.com"
                />
              </div>
            </div>
            
            <div>
              <label class="block text-white mb-2">Betreff</label>
              <input 
                v-model="form.subject" 
                type="text"
                class="w-full bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg px-4 py-3 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Worum geht es?"
              />
            </div>
            
            <div>
              <label class="block text-white mb-2">Nachricht *</label>
              <textarea 
                v-model="form.message" 
                rows="6" 
                required
                class="w-full bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg px-4 py-3 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ihre Nachricht..."
              ></textarea>
            </div>
            
            <button 
              type="submit" 
              :disabled="loading"
              class="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg disabled:opacity-50"
            >
              {{ loading ? 'Wird gesendet...' : 'Nachricht senden' }}
            </button>
          </form>
          
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

const form = reactive({
  name: '',
  email: '',
  subject: '',
  message: ''
})

const loading = ref(false)

const handleSubmit = async () => {
  loading.value = true
  try {
    // TODO: Implement actual contact form submission
    console.log('Contact form submitted:', form)
    alert('Vielen Dank für Ihre Nachricht! Wir melden uns bald bei Ihnen.')
    
    // Reset form
    Object.keys(form).forEach(key => form[key] = '')
  } catch (error) {
    console.error('Contact form error:', error)
    alert('Es gab ein Problem beim Senden. Bitte versuchen Sie es später noch einmal.')
  } finally {
    loading.value = false
  }
}
</script>