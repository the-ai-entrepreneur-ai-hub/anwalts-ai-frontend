<template>
  <PortalShell>
    <div class="flex flex-col h-full bg-gray-50">
      <!-- Professional Header -->
      <header class="bg-white border-b border-gray-200 px-6 py-4 flex-shrink-0">
        <div class="max-w-5xl mx-auto flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-semibold text-gray-900">Digitaler Rechtsbeistand</h1>
            <p class="text-sm text-gray-600 mt-1">Präzise Rechtsberatung mit KI-Expertise – verfügbar 24/7</p>
          </div>
          <button
            v-if="messages.length > 0"
            @click="clearChat"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Neue Anfrage
          </button>
        </div>
      </header>

      <!-- Chat Container -->
      <div class="flex-1 overflow-y-auto px-6 py-6" ref="messagesContainer">
        <div class="max-w-5xl mx-auto">
          <!-- Empty State -->
          <div v-if="messages.length === 0" class="flex flex-col items-center justify-center min-h-[500px] text-center px-4">
            <!-- Unique Animated Element -->
            <div class="relative mb-8">
              <div class="ai-orb">
                <div class="orb-core"></div>
                <div class="orb-ring orb-ring-1"></div>
                <div class="orb-ring orb-ring-2"></div>
                <div class="orb-ring orb-ring-3"></div>
              </div>
            </div>

            <h2 class="text-2xl font-semibold text-gray-900 mb-3">Sofortige Antworten auf komplexe Rechtsfragen</h2>
            <p class="text-gray-600 max-w-2xl mb-8 leading-relaxed">
              Nutzen Sie künstliche Intelligenz für präzise rechtliche Analysen.
              Von Vertragsgestaltung bis Compliance – erhalten Sie fundierte Beratung in Sekunden.
            </p>

            <!-- Example Prompts -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-3xl">
              <button
                @click="quickPrompt('Analysiere die rechtlichen Risiken eines befristeten Arbeitsvertrags mit Verlängerungsoption gemäß deutschem Arbeitsrecht.')"
                class="text-left p-4 bg-white border border-gray-200 rounded-lg hover:border-[#5b7ce6] hover:shadow-sm transition-all group"
              >
                <div class="font-medium text-gray-900 mb-1 group-hover:text-[#5b7ce6] transition-colors">Arbeitsrecht-Analyse</div>
                <div class="text-sm text-gray-600">Befristete Verträge & Verlängerungen</div>
              </button>
              <button
                @click="quickPrompt('Welche DSGVO-Anforderungen gelten für die Verarbeitung von Kundendaten in einem Online-Shop mit Sitz in Deutschland?')"
                class="text-left p-4 bg-white border border-gray-200 rounded-lg hover:border-[#5b7ce6] hover:shadow-sm transition-all group"
              >
                <div class="font-medium text-gray-900 mb-1 group-hover:text-[#5b7ce6] transition-colors">DSGVO-Compliance</div>
                <div class="text-sm text-gray-600">Datenschutz für E-Commerce</div>
              </button>
              <button
                @click="quickPrompt('Erstelle einen Überblick über die Fristen und Formvorschriften bei einer fristlosen Kündigung wegen Zahlungsverzug.')"
                class="text-left p-4 bg-white border border-gray-200 rounded-lg hover:border-[#5b7ce6] hover:shadow-sm transition-all group"
              >
                <div class="font-medium text-gray-900 mb-1 group-hover:text-[#5b7ce6] transition-colors">Kündigungsrecht</div>
                <div class="text-sm text-gray-600">Fristen & Formvorschriften</div>
              </button>
              <button
                @click="quickPrompt('Welche Haftungsrisiken bestehen bei der Gründung einer GmbH und wie können diese minimiert werden?')"
                class="text-left p-4 bg-white border border-gray-200 rounded-lg hover:border-[#5b7ce6] hover:shadow-sm transition-all group"
              >
                <div class="font-medium text-gray-900 mb-1 group-hover:text-[#5b7ce6] transition-colors">Gesellschaftsrecht</div>
                <div class="text-sm text-gray-600">GmbH-Gründung & Haftung</div>
              </button>
            </div>

            <p class="text-xs text-gray-500 mt-8 max-w-lg">
              Hinweis: Dieser Service ersetzt keine individuelle Rechtsberatung.
              Bei komplexen Fällen empfehlen wir die Konsultation eines Fachanwalts.
            </p>
          </div>

          <!-- Messages -->
          <div v-else class="space-y-6">
            <div
              v-for="(message, index) in messages"
              :key="index"
              class="flex gap-4 message-fade-in"
              :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
            >
              <!-- Assistant Avatar (left side) -->
              <div v-if="message.role === 'assistant'" class="flex-shrink-0">
                <div class="w-9 h-9 bg-[#5b7ce6] rounded-lg flex items-center justify-center">
                  <div class="w-3 h-3 bg-white rounded-sm"></div>
                </div>
              </div>

              <!-- Message Content -->
              <div class="flex flex-col" :class="message.role === 'user' ? 'items-end max-w-[75%]' : 'flex-1 max-w-[85%]'">
                <div
                  class="rounded-lg px-4 py-3"
                  :class="message.role === 'user'
                    ? 'bg-[#5b7ce6] text-white'
                    : 'bg-white text-gray-900 border border-gray-200'"
                >
                  <div
                    class="text-sm leading-relaxed"
                    :class="message.role === 'assistant' ? 'message-content' : ''"
                    v-html="formatMessage(message.content)"
                  ></div>
                </div>
                <div class="text-xs text-gray-500 mt-1.5 px-1">
                  {{ formatTime(message.timestamp) }}
                </div>
              </div>

              <!-- User Avatar (right side) -->
              <div v-if="message.role === 'user'" class="flex-shrink-0">
                <div class="w-9 h-9 bg-gray-300 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                  </svg>
                </div>
              </div>
            </div>

            <!-- Loading Indicator -->
            <div v-if="isLoading" class="flex gap-4 justify-start message-fade-in">
              <div class="flex-shrink-0">
                <div class="w-9 h-9 bg-[#5b7ce6] rounded-lg flex items-center justify-center">
                  <div class="w-3 h-3 bg-white rounded-sm pulse-animation"></div>
                </div>
              </div>
              <div class="flex-1 max-w-[85%]">
                <div class="bg-white border border-gray-200 rounded-lg px-4 py-3">
                  <div class="flex items-center gap-2">
                    <div class="flex space-x-1">
                      <div class="w-2 h-2 bg-[#5b7ce6] rounded-full typing-dot"></div>
                      <div class="w-2 h-2 bg-[#5b7ce6] rounded-full typing-dot" style="animation-delay: 0.2s"></div>
                      <div class="w-2 h-2 bg-[#5b7ce6] rounded-full typing-dot" style="animation-delay: 0.4s"></div>
                    </div>
                    <span class="text-sm text-gray-600">Analyse läuft...</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="border-t border-gray-200 bg-white px-6 py-4 flex-shrink-0">
        <div class="max-w-5xl mx-auto">
          <form @submit.prevent="sendMessage" class="flex gap-3">
            <input
              v-model="currentMessage"
              ref="messageInput"
              :disabled="isLoading"
              placeholder="Beschreiben Sie Ihren Rechtsfall oder stellen Sie eine Frage..."
              class="flex-1 px-4 py-3 bg-white border border-gray-300 rounded-lg text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#5b7ce6] focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed transition-shadow"
            />
            <button
              type="submit"
              :disabled="isLoading || !currentMessage.trim()"
              class="px-6 py-3 bg-[#5b7ce6] text-white text-sm font-medium rounded-lg hover:bg-[#4a6cd4] focus:outline-none focus:ring-2 focus:ring-[#5b7ce6] focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
              </svg>
              Analysieren
            </button>
          </form>
        </div>
      </div>
    </div>
  </PortalShell>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import PortalShell from '~/components/PortalShell.vue'

definePageMeta({ layout: false })

// Reactive state
const messages = ref<Array<{ role: 'user' | 'assistant', content: string, timestamp: Date }>>([])
const currentMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement>()
const messageInput = ref<HTMLInputElement>()

// Format message content with markdown support
const formatMessage = (content: string) => {
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/```([\s\S]*?)```/g, '<pre class="code-block"><code>$1</code></pre>')
    .replace(/`(.*?)`/g, '<code class="inline-code">$1</code>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
    .replace(/^(.+)$/, '<p>$1</p>')
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

// Quick prompt handler
const quickPrompt = (prompt: string) => {
  currentMessage.value = prompt
  nextTick(() => {
    if (messageInput.value) {
      messageInput.value.focus()
    }
  })
  sendMessage()
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
      content: 'Entschuldigung, es ist ein technischer Fehler aufgetreten. Bitte versuchen Sie es erneut.',
      timestamp: new Date()
    })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

// Clear chat
const clearChat = () => {
  if (confirm('Möchten Sie diese Konversation wirklich beenden und eine neue Anfrage starten?')) {
    messages.value = []
  }
}
</script>

<style scoped>
/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

/* Unique AI Orb Animation */
.ai-orb {
  position: relative;
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.orb-core {
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #5b7ce6 0%, #4a6cd4 100%);
  border-radius: 50%;
  box-shadow: 0 0 20px rgba(91, 124, 230, 0.4);
  animation: pulse-core 3s ease-in-out infinite;
}

.orb-ring {
  position: absolute;
  border: 2px solid;
  border-radius: 50%;
  opacity: 0;
  animation: expand-ring 3s ease-out infinite;
}

.orb-ring-1 {
  width: 40px;
  height: 40px;
  border-color: rgba(91, 124, 230, 0.6);
  animation-delay: 0s;
}

.orb-ring-2 {
  width: 60px;
  height: 60px;
  border-color: rgba(91, 124, 230, 0.4);
  animation-delay: 1s;
}

.orb-ring-3 {
  width: 80px;
  height: 80px;
  border-color: rgba(91, 124, 230, 0.2);
  animation-delay: 2s;
}

@keyframes pulse-core {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 20px rgba(91, 124, 230, 0.4);
  }
  50% {
    transform: scale(1.1);
    box-shadow: 0 0 30px rgba(91, 124, 230, 0.6);
  }
}

@keyframes expand-ring {
  0% {
    transform: scale(0.5);
    opacity: 0;
  }
  50% {
    opacity: 0.8;
  }
  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}

/* Typing animation */
@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.7;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

.typing-dot {
  animation: typing 1.4s infinite;
}

/* Pulse animation for loading avatar */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.pulse-animation {
  animation: pulse 1.5s ease-in-out infinite;
}

/* Message fade in animation */
@keyframes messageFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-fade-in {
  animation: messageFadeIn 0.4s ease-out;
}

/* Message content styling */
.message-content :deep(p) {
  margin: 0;
  line-height: 1.7;
}

.message-content :deep(p + p) {
  margin-top: 0.75rem;
}

.message-content :deep(strong) {
  font-weight: 600;
  color: #1f2937;
}

.message-content :deep(em) {
  font-style: italic;
}

.message-content :deep(.inline-code) {
  background: #f3f4f6;
  color: #1f2937;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 0.875em;
}

.message-content :deep(.code-block) {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 0.75rem;
  margin: 0.5rem 0;
  overflow-x: auto;
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 0.875rem;
  line-height: 1.5;
}

.message-content :deep(.code-block code) {
  background: transparent;
  padding: 0;
  color: #374151;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .max-w-\[75\%\] {
    max-width: 90%;
  }

  .max-w-\[85\%\] {
    max-width: 90%;
  }

  .ai-orb {
    width: 80px;
    height: 80px;
  }

  .orb-core {
    width: 20px;
    height: 20px;
  }
}
</style>
