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

    <div class="bg-white text-black/80 w-full overflow-hidden rounded-2xl border border-gray-200 h-[calc(100vh-12rem)]">
      <!-- Header -->
      <div class="flex flex-col gap-3 border-b border-gray-200 p-6 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 class="text-2xl font-medium tracking-tight">KI-Assistent</h1>
          <p class="mt-1 text-sm text-gray-600 md:text-base">
            Ihr deutscher Rechtsassistent mit KI-Unterstützung
          </p>
        </div>
        <div class="flex items-center gap-2">
          <button 
            @click="clearChat"
            class="h-10 px-4 rounded-xl border border-[#5b7ce6] bg-white text-[#5b7ce6] hover:bg-[#5b7ce6]/10 transition-colors flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
            Löschen
          </button>
        </div>
      </div>

      <!-- Chat Messages Area -->
      <div class="flex-1 overflow-y-auto p-6" style="height: calc(100% - 180px);" ref="messagesContainer">
        <div v-if="messages.length === 0" class="flex items-center justify-center h-full text-gray-500">
          <div class="text-center">
            <svg class="w-16 h-16 mx-auto mb-4 text-[#5b7ce6]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.959 8.959 0 01-4.906-1.481L3 21l2.519-5.094A8.959 8.959 0 013 12c0-4.418 3.582-8 8-8s8 3.582 8 8z"></path>
            </svg>
            <h3 class="text-lg font-medium text-gray-900 mb-2">Willkommen beim KI-Assistenten</h3>
            <p class="text-sm text-gray-600">Stellen Sie rechtliche Fragen oder bitten Sie um Hilfe bei Dokumenten.</p>
          </div>
        </div>

        <div v-else class="space-y-6">
          <div v-for="(message, index) in messages" :key="index" class="flex gap-4" :class="{ 'flex-row-reverse': message.role === 'user' }">
            <div class="flex-shrink-0">
              <div v-if="message.role === 'assistant'" class="w-8 h-8 bg-[#5b7ce6] rounded-full flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                </svg>
              </div>
              <div v-else class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
              </div>
            </div>
            <div class="flex-1 max-w-3xl">
              <div 
                class="rounded-2xl px-4 py-3 text-sm"
                :class="message.role === 'user' ? 'bg-[#5b7ce6] text-white' : 'bg-gray-100 text-gray-900'"
              >
                <div v-html="formatMessage(message.content)"></div>
              </div>
              <div class="mt-1 text-xs text-gray-500" :class="{ 'text-right': message.role === 'user' }">
                {{ formatTime(message.timestamp) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Loading indicator -->
        <div v-if="isLoading" class="flex gap-4 mt-6">
          <div class="w-8 h-8 bg-[#5b7ce6] rounded-full flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
            </svg>
          </div>
          <div class="flex-1 max-w-3xl">
            <div class="bg-gray-100 rounded-2xl px-4 py-3 text-sm">
              <div class="flex items-center gap-2">
                <div class="animate-pulse flex space-x-1">
                  <div class="w-2 h-2 bg-[#5b7ce6] rounded-full animate-bounce"></div>
                  <div class="w-2 h-2 bg-[#5b7ce6] rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                  <div class="w-2 h-2 bg-[#5b7ce6] rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                </div>
                <span class="text-gray-600">KI-Assistent denkt nach...</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="border-t border-gray-200 p-6">
        <form @submit.prevent="sendMessage" class="flex gap-3">
          <input
            v-model="currentMessage"
            :disabled="isLoading"
            placeholder="Stellen Sie eine rechtliche Frage..."
            class="flex-1 px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-[#5b7ce6] focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            :disabled="isLoading || !currentMessage.trim()"
            class="px-6 py-3 bg-[#5b7ce6] text-white rounded-xl hover:bg-[#4a6cd4] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
            </svg>
            Senden
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'

// Reactive state
const messages = ref<Array<{ role: 'user' | 'assistant', content: string, timestamp: Date }>>([])
const currentMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement>()

// Format message content with basic markdown support
const formatMessage = (content: string) => {
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

// Format timestamp
const formatTime = (timestamp: Date) => {
  return new Intl.DateTimeFormat('de-DE', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(timestamp)
}

// Scroll to bottom of messages
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// Send message to AI
const sendMessage = async () => {
  if (!currentMessage.value.trim() || isLoading.value) return

  const userMessage = currentMessage.value.trim()
  currentMessage.value = ''

  // Add user message
  messages.value.push({
    role: 'user',
    content: userMessage,
    timestamp: new Date()
  })

  scrollToBottom()
  isLoading.value = true

  try {
    // Call AI API
    const response = await $fetch('/api/ai/complete', {
      method: 'POST',
      body: {
        prompt: userMessage,
        context_type: 'legal_assistant',
        max_tokens: 1000,
        temperature: 0.7
      }
    })

    // Add AI response
    messages.value.push({
      role: 'assistant',
      content: response.content || 'Entschuldigung, ich konnte keine Antwort generieren.',
      timestamp: new Date()
    })
  } catch (error) {
    console.error('Error calling AI API:', error)
    messages.value.push({
      role: 'assistant',
      content: 'Entschuldigung, es gab einen Fehler bei der Verarbeitung Ihrer Anfrage. Bitte versuchen Sie es später erneut.',
      timestamp: new Date()
    })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

// Clear chat
const clearChat = () => {
  messages.value = []
}
</script>

<style scoped>
/* Custom scrollbar for messages */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #5b7ce6;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #4a6cd4;
}
</style>