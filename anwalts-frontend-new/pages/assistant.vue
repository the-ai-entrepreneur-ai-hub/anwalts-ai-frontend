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
                <div
                  v-if="message.role === 'assistant'"
                  class="assistant-action-bar"
                >
                  <button
                    type="button"
                    class="assistant-action-button"
                    :class="{ 'assistant-action-button--active': copiedMessageIndex === index }"
                    aria-label="Antwort kopieren"
                    @click="copyMessage(index, message.content)"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                    </svg>
                    <span>{{ copiedMessageIndex === index ? 'Kopiert' : 'Kopieren' }}</span>
                  </button>
                  <button
                    type="button"
                    class="assistant-action-button"
                    :class="{ 'assistant-action-button--positive': feedbackStates[index] === 'positive' }"
                    aria-label="Antwort war hilfreich"
                    @click="handleFeedback(index, 'positive')"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                      <path d="M7 10v12"></path>
                      <path d="M15 21h4a2 2 0 0 0 2-2v-5a1 1 0 0 0-1-1h-5.28a1 1 0 0 1-.96-.74L12.4 6a1 1 0 0 0-1.95.38V10"></path>
                      <path d="M7 21H3a1 1 0 0 1-1-1v-9a1 1 0 0 1 1-1h4"></path>
                    </svg>
                    <span>Hilfreich</span>
                  </button>
                  <button
                    type="button"
                    class="assistant-action-button"
                    :class="{ 'assistant-action-button--negative': feedbackStates[index] === 'negative' }"
                    aria-label="Antwort war unpräzise"
                    @click="handleFeedback(index, 'negative')"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                      <path d="M7 14V2"></path>
                      <path d="M15 3h4a2 2 0 0 1 2 2v5a1 1 0 0 1-1 1h-5.28a1 1 0 0 0-.96.74L12.4 18a1 1 0 0 1-1.95-.38v-4.62"></path>
                      <path d="M7 3H3a1 1 0 0 0-1 1v9a1 1 0 0 0 1 1h4"></path>
                    </svg>
                    <span>Unpräzise</span>
                  </button>
                  <button
                    type="button"
                    class="assistant-action-button assistant-action-button--primary"
                    :disabled="isLoading"
                    aria-label="Antwort neu analysieren"
                    @click="retryPrompt(index)"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                      <path d="M21 3v5h-5"></path>
                      <path d="M3 21v-5h5"></path>
                      <path d="M21 8a9 9 0 0 0-15.5-6.36L3 5"></path>
                      <path d="M3 16a9 9 0 0 0 15.5 6.36L21 19"></path>
                    </svg>
                    <span>Erneut analysieren</span>
                  </button>
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
              class="send-button px-6 py-3 bg-[#5b7ce6] text-white text-sm font-medium rounded-lg hover:bg-[#4a6cd4] focus:outline-none focus:ring-2 focus:ring-[#5b7ce6] focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              <svg class="send-button__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="m22 2-11 11"></path>
                <path d="M22 2 15 22 11 13 2 9 22 2"></path>
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
import { ref, nextTick, onBeforeUnmount, watch } from 'vue'
import PortalShell from '~/components/PortalShell.vue'

definePageMeta({ layout: false })

const resolveAuthHeaders = () => {
  if (!process.client) {
    return {}
  }

  const storageKeys = ['auth_token', 'anwalts_auth_token', 'access_token', 'token', 'sat']
  let token: string | null = null

  for (const key of storageKeys) {
    try {
      const value = localStorage.getItem(key)
      if (value) {
        token = value
        break
      }
    } catch (_) {
      token = null
    }
  }

  if (!token && typeof document !== 'undefined') {
    try {
      const entries = document.cookie
        .split(';')
        .map(entry => entry.trim())
        .filter(Boolean)
      for (const item of entries) {
        const [rawKey, ...rest] = item.split('=')
        if (storageKeys.includes(rawKey)) {
          token = decodeURIComponent(rest.join('=') || '')
          break
        }
      }
    } catch (_) {
      token = null
    }
  }

  if (!token) {
    return {}
  }

  let cleaned = decodeURIComponent(token)
  cleaned = cleaned.trim()
  if ((cleaned.startsWith('"') && cleaned.endsWith('"')) || (cleaned.startsWith("'") && cleaned.endsWith("'"))) {
    cleaned = cleaned.slice(1, -1)
  }
  const bearer = cleaned.startsWith('Bearer ') ? cleaned : `Bearer ${cleaned}`

  return {
    Authorization: bearer,
    'X-Portal-Auth': bearer
  }
}

// Reactive state
const messages = ref<Array<{ role: 'user' | 'assistant', content: string, timestamp: Date }>>([])
const currentMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement>()
const messageInput = ref<HTMLInputElement>()
const currentConversationId = ref<string | null>(null)
const copiedMessageIndex = ref<number | null>(null)
const feedbackStates = ref<Record<number, 'positive' | 'negative'>>({})

let copyResetTimeout: ReturnType<typeof setTimeout> | null = null

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
  currentMessage.value = ''
  sendMessage(prompt)
  nextTick(() => {
    if (messageInput.value) {
      messageInput.value.focus()
    }
  })
}

// Build context from conversation history
const buildContext = () => {
  if (messages.value.length === 0) return ''
  
  // Take last 5 messages for context
  const recentMessages = messages.value.slice(-5)
  return recentMessages.map(msg => {
    const role = msg.role === 'user' ? 'Benutzer' : 'Assistent'
    return `${role}: ${msg.content}`
  }).join('\n\n')
}

// Send message to AI
const sendMessage = async (overrideMessage?: string | Event) => {
  if (overrideMessage instanceof Event) {
    overrideMessage = undefined
  }

  const messageText = (typeof overrideMessage === 'string' ? overrideMessage : currentMessage.value).trim()
  if (!messageText || isLoading.value) return

  currentMessage.value = ''

  // Add user message
  messages.value.push({
    role: 'user',
    content: messageText,
    timestamp: new Date()
  })

  scrollToBottom()
  isLoading.value = true

  try {
    // Call AI chat endpoint with Together integration
    const response = await $fetch('/api/chat', {
      method: 'POST',
      body: {
        session_id: currentConversationId.value,
        title: messages.value[0]?.content?.slice(0, 80) || 'Gespräch',
        messages: [
          {
            role: 'user',
            content: messageText
          }
        ],
        temperature: 0.7
      },
      headers: resolveAuthHeaders({ 'Content-Type': 'application/json' }),
      credentials: 'include'
    })

    currentConversationId.value = response.session_id || currentConversationId.value

    // Add AI response
    messages.value.push({
      role: 'assistant',
      content: response.content || 'Ich konnte die Antwort gerade nicht fertigstellen. Bitte stellen Sie Ihre Frage gleich noch einmal – ich helfe sofort weiter.',
      timestamp: new Date()
    })
  } catch (error: any) {
    console.error('Error calling AI API:', error)
    
    let errorMessage = 'Ich konnte die Antwort gerade nicht fertigstellen. Bitte stellen Sie Ihre Frage gleich noch einmal – ich helfe sofort weiter.'
    
    if (error?.status === 401 || error?.statusCode === 401) {
      errorMessage = 'Ihre Sitzung ist abgelaufen. Bitte melden Sie sich erneut an.'
      setTimeout(() => { 
        navigateTo('/')
      }, 2000)
    } else if (error?.status === 429 || error?.statusCode === 429) {
      errorMessage = 'Sie haben das Nachrichtenlimit überschritten. Bitte warten Sie einen Moment.'
    } else if (error?.data?.detail) {
      errorMessage = error.data.detail
    } else if (error?.statusMessage) {
      errorMessage = error.statusMessage
    }
    
    messages.value.push({
      role: 'assistant',
      content: errorMessage,
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
    currentConversationId.value = null
    feedbackStates.value = {}
    copiedMessageIndex.value = null
  }
}

const copyMessage = async (index: number, content: string) => {
  try {
    await navigator.clipboard.writeText(content)
    copiedMessageIndex.value = index
    if (copyResetTimeout) {
      clearTimeout(copyResetTimeout)
    }
    copyResetTimeout = setTimeout(() => {
      if (copiedMessageIndex.value === index) {
        copiedMessageIndex.value = null
      }
    }, 2000)
  } catch (error) {
    console.error('Kopieren fehlgeschlagen:', error)
  }
}

const handleFeedback = (index: number, sentiment: 'positive' | 'negative') => {
  const current = feedbackStates.value[index]
  if (current === sentiment) {
    const { [index]: _, ...rest } = feedbackStates.value
    feedbackStates.value = { ...rest }
  } else {
    feedbackStates.value = { ...feedbackStates.value, [index]: sentiment }
  }
}

const retryPrompt = (index: number) => {
  if (isLoading.value) return
  const previousUserMessage = [...messages.value]
    .slice(0, index)
    .reverse()
    .find((msg) => msg.role === 'user')

  const retryContent = previousUserMessage?.content || messages.value[index]?.content
  if (!retryContent) return

  sendMessage(retryContent)
}

onBeforeUnmount(() => {
  if (copyResetTimeout) {
    clearTimeout(copyResetTimeout)
  }
})

watch(
  () => messages.value.length,
  () => {
    const last = messages.value[messages.value.length - 1]
    if (last?.role === 'assistant') {
      copiedMessageIndex.value = null
    }
  }
)
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

.assistant-action-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
  padding: 0.35rem 0.5rem 0.25rem;
  border-top: 1px solid #e5e7eb;
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.9) 0%, rgba(255, 255, 255, 0.95) 100%);
  border-radius: 0 0 0.75rem 0.75rem;
  animation: toolbar-enter 0.28s ease-out;
}

.assistant-action-button {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.75rem;
  line-height: 1rem;
  padding: 0.38rem 0.8rem;
  border-radius: 9999px;
  border: 1px solid #dce4ff;
  background-color: #ffffff;
  color: #4b5563;
  transition: color 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
}

.assistant-action-button svg {
  width: 16px;
  height: 16px;
  transition: transform 0.18s ease;
}

.assistant-action-button:hover {
  border-color: #5b7ce6;
  color: #4a6cd4;
  box-shadow: 0 4px 12px rgba(91, 124, 230, 0.12);
  transform: translateY(-1px);
}

.assistant-action-button:active {
  transform: translateY(0);
}

.assistant-action-button:hover svg {
  transform: translateY(-1px);
}

.assistant-action-button--primary {
  color: #5b7ce6;
  border-color: #dce4ff;
}

.assistant-action-button--primary:hover {
  background-color: #f4f6ff;
  border-color: #5b7ce6;
}

.assistant-action-button--active {
  border-color: #4a6cd4;
  background-color: #eef2ff;
  color: #4a6cd4;
}

.assistant-action-button--positive {
  border-color: #bbf7d0;
  background-color: #ecfdf5;
  color: #047857;
}

.assistant-action-button--negative {
  border-color: #fecaca;
  background-color: #fef2f2;
  color: #b91c1c;
}

.assistant-action-button--positive:hover {
  border-color: #059669;
  color: #047857;
}

.assistant-action-button--negative:hover {
  border-color: #dc2626;
  color: #b91c1c;
}

.assistant-action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.send-button {
  transition: transform 0.18s ease, box-shadow 0.18s ease;
  box-shadow: 0 8px 16px rgba(76, 97, 185, 0.15);
}

.send-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 12px 20px rgba(76, 97, 185, 0.2);
}

.send-button:active:not(:disabled) {
  transform: translateY(0);
}

.send-button__icon {
  width: 18px;
  height: 18px;
  transition: transform 0.2s ease;
}

.send-button:hover:not(:disabled) .send-button__icon {
  transform: translateX(2px);
}

.send-button:disabled .send-button__icon {
  transform: none;
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

@keyframes toolbar-enter {
  0% {
    opacity: 0;
    transform: translateY(6px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
