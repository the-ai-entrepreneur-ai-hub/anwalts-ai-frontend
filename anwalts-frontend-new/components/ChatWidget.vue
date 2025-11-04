<template>
  <div class="chat-widget" aria-live="polite">
    <button
      class="chat-widget__toggle"
      type="button"
      :aria-expanded="isOpen"
      aria-controls="chatWidgetPanel"
      @click="toggleWidget"
    >
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.77 9.77 0 01-3.53-.64L3 20l1.12-3.09A7.82 7.82 0 013 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
        />
      </svg>
      <span class="sr-only">Chat öffnen</span>
    </button>

    <Transition name="chat-slide">
      <div
        v-if="isOpen"
        id="chatWidgetPanel"
        class="chat-widget__panel"
      >
        <header class="chat-widget__header">
          <div>
            <h2 class="chat-widget__title">ANWALTS KI-Assistent</h2>
            <p class="chat-widget__subtitle">Stellen Sie Fragen oder lassen Sie sich Inhalte erklären.</p>
          </div>
          <button type="button" class="chat-widget__close" @click="toggleWidget">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span class="sr-only">Chat schließen</span>
          </button>
        </header>

        <div ref="scrollRef" class="chat-widget__messages">
          <div
            v-for="(message, index) in messages"
            :key="`${message.role}-${index}-${message.timestamp}`"
            :class="['chat-message', `chat-message--${message.role}`]"
          >
            <div class="chat-message__bubble">
              <strong class="chat-message__role">
                {{ message.role === 'user' ? 'Sie' : 'Assistent' }}
              </strong>
              <p class="chat-message__content">{{ message.content }}</p>
            </div>
          </div>
          <div v-if="isLoading" class="chat-widget__typing">
            <span class="typing-indicator">
              <span></span><span></span><span></span>
            </span>
            <span>Der Assistent denkt …</span>
          </div>
        </div>

        <p v-if="errorMessage" class="chat-widget__error" role="alert">
          {{ errorMessage }}
        </p>

        <form class="chat-widget__form" @submit.prevent="handleSubmit">
          <textarea
            ref="inputRef"
            v-model="draft"
            class="chat-widget__input"
            placeholder="Fragen Sie nach Dokumentzusammenfassungen, Recherche oder Formulierungen …"
            :disabled="isLoading"
            rows="3"
          ></textarea>
          <div class="chat-widget__actions">
            <button
              type="submit"
              class="chat-widget__send"
              :disabled="isLoading || !draft.trim()"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              Senden
            </button>
            <button
              type="button"
              class="chat-widget__reset"
              @click="resetConversation"
              :disabled="isLoading || messages.length === 0"
            >
              Zurücksetzen
            </button>
          </div>
        </form>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, nextTick } from 'vue'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

const isOpen = ref(false)
const messages = ref<ChatMessage[]>([])
const sessionId = ref<string | null>(null)
const draft = ref('')
const isLoading = ref(false)
const errorMessage = ref('')
const scrollRef = ref<HTMLDivElement | null>(null)
const inputRef = ref<HTMLTextAreaElement | null>(null)

const portalAssistantContext = `Du bist der fest integrierte KI-Assistent im Portal ANWALTS.AI. Hilf Nutzerinnen und Nutzern dabei, sich innerhalb der Anwendung zurechtzufinden, technische Funktionen zu verstehen und rechtliche Aufgaben zu erledigen. Leite freundlich und proaktiv an – lehne Navigations- oder Funktionsfragen nicht ab. Wenn du eine Handlung selbst nicht ausführen kannst (z. B. E-Mail-Konto verknüpfen), erkläre Schritt für Schritt, wie der Nutzer dies erledigt.

Wisse über folgende Hauptbereiche Bescheid:
- Dashboard: Überblick über Fälle, Dokumente, E-Mails und Schnellzugriffe.
- Dokumente: Juristische Dokumente anzeigen, generieren (per "Neues Dokument"), exportieren (DOCX/PDF) und Details im rechten Overlay prüfen.
- Vorlagen: Vorlagenbibliothek verwalten, importieren, bearbeiten, Klauseln speichern.
- E-Mails: Gmail- oder Domain-Konten verbinden (über "E-Mail verbinden" oder Domain-Wizard), Synchronisationsstatus prüfen, manuelle Syncs auslösen.
- Fälle: (falls sichtbar) Überblick über laufende Mandate.
- Einstellungen (nur Admin): Benutzer verwalten, API-Tokens, Webhooks, Rollen.
- KI-Assistent (diese Seite): Vollbild-Chat mit erweiterten Analysen.

Weitere Hinweise zur Navigation:
- Die linke Seitenleiste enthält alle Bereiche (Übersicht, KI-Assistent, Dokumente, Vorlagen, E-Mails, ggf. Einstellungen).
- Oben rechts im Portal können Nutzer ihr Profilbild/Profilmenü öffnen, um sich abzumelden oder Angaben anzupassen.
- Viele Ansichten verwenden schwebende Paneele/Overlays (z. B. "Details" und "Alle anzeigen" auf dem Dashboard) – erinnere daran, dass sie per Schließen-Button oder ESC geschlossen werden können.
- Bei technischen Fragen (z. B. "Warum sehe ich keine Dokumente?", "Wie verbinde ich meine Domain-E-Mails?") gib präzise Klickpfade, beschreibe erwartete Stati ("Verbunden", "Synchronisiert") und schlage ggf. einen Refresh oder erneutes Einloggen vor.

Antwortstil: Sei freundlich, präzise, erkläre konkrete Klickpfade (z. B. "Gehe zu Vorlagen → Neue Vorlage") und biete bei Bedarf rechtliche Einschätzungen (Hinweis: keine echte Rechtsberatung). Frage nach der gewünschten Aufgabe, wenn unklar.`

const resolveAuthHeaders = (extra: Record<string, string> = {}) => {
  if (!process.client) {
    return { ...extra }
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
      const cookies = document.cookie
        .split(';')
        .map(entry => entry.trim())
        .filter(Boolean)
      for (const pair of cookies) {
        const [rawKey, ...rest] = pair.split('=')
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
    return { ...extra }
  }

  let cleaned = decodeURIComponent(token)
  cleaned = cleaned.trim()
  if ((cleaned.startsWith('"') && cleaned.endsWith('"')) || (cleaned.startsWith("'") && cleaned.endsWith("'"))) {
    cleaned = cleaned.slice(1, -1)
  }
  const bearer = cleaned.startsWith('Bearer ') ? cleaned : `Bearer ${cleaned}`

  return {
    ...extra,
    Authorization: bearer,
    'X-Portal-Auth': bearer
  }
}

const scrollToBottom = async () => {
  await nextTick()
  if (scrollRef.value) {
    scrollRef.value.scrollTop = scrollRef.value.scrollHeight
  }
}

const toggleWidget = async () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    errorMessage.value = ''
    await nextTick()
    inputRef.value?.focus()
  }
}

const resetConversation = () => {
  if (isLoading.value) return
  messages.value = []
  sessionId.value = null
  draft.value = ''
  errorMessage.value = ''
}

const handleSubmit = async () => {
  const message = draft.value.trim()
  if (!message || isLoading.value) return

  messages.value.push({
    role: 'user',
    content: message,
    timestamp: new Date().toISOString()
  })

  draft.value = ''
  errorMessage.value = ''
  isLoading.value = true
  await scrollToBottom()

  try {
    const conversationHistory = messages.value.slice(0, -1).map(msg => ({
      role: msg.role,
      content: msg.content
    }))

    const payloadMessages = [
      {
        role: 'system',
        content: portalAssistantContext
      },
      ...conversationHistory,
      {
        role: 'user',
        content: message
      }
    ]

    const response: any = await $fetch('/api/chat', {
      method: 'POST',
      body: {
        session_id: sessionId.value,
        title: messages.value[0]?.content?.slice(0, 80) || 'Chat',
        messages: payloadMessages,
        temperature: 0.6
      },
      headers: resolveAuthHeaders({ 'Content-Type': 'application/json' }),
      credentials: 'include'
    })

    sessionId.value = response?.session_id || sessionId.value

    messages.value.push({
      role: 'assistant',
      content: response?.content || 'Ich konnte gerade keine Antwort formulieren. Bitte versuchen Sie es erneut.',
      timestamp: new Date().toISOString()
    })
    await scrollToBottom()
  } catch (error: any) {
    console.error('[ChatWidget] API error', error)
    let messageText = 'Der Assistent ist vorübergehend nicht erreichbar. Bitte versuchen Sie es erneut.'
    if (error?.data?.detail) {
      messageText = error.data.detail
    } else if (error?.status === 401 || error?.statusCode === 401) {
      messageText = 'Ihre Sitzung ist abgelaufen. Bitte melden Sie sich erneut an.'
    } else if (error?.status === 429) {
      messageText = 'Sie haben das Nachrichtenlimit erreicht. Bitte warten Sie einen Moment.'
    }
    errorMessage.value = messageText
    await scrollToBottom()
  } finally {
    isLoading.value = false
  }
}

const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'k' && event.metaKey) {
    event.preventDefault()
    toggleWidget()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
.chat-widget {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.75rem;
}

.chat-widget__toggle {
  width: 3.25rem;
  height: 3.25rem;
  border-radius: 999px;
  border: none;
  background: linear-gradient(135deg, #5b7ce6 0%, #4a6cd4 100%);
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 25px rgba(91, 124, 230, 0.35);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.chat-widget__toggle:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 32px rgba(91, 124, 230, 0.4);
}

.chat-widget__panel {
  width: min(360px, calc(100vw - 2rem));
  max-height: calc(100vh - 6rem);
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 24px 70px rgba(15, 23, 42, 0.25);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-widget__header {
  padding: 1.25rem 1.25rem 1rem;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  border-bottom: 1px solid rgba(15, 23, 42, 0.08);
  background: linear-gradient(135deg, rgba(91, 124, 230, 0.12), rgba(74, 108, 212, 0.06));
}

.chat-widget__title {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
}

.chat-widget__subtitle {
  margin-top: 0.25rem;
  font-size: 0.8125rem;
  color: #6b7280;
}

.chat-widget__close {
  background: transparent;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
  transition: color 0.2s ease;
}

.chat-widget__close:hover {
  color: #111827;
}

.chat-widget__messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 1.25rem;
  background: #f8f9ff;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.chat-message {
  display: flex;
}

.chat-message--user {
  justify-content: flex-end;
}

.chat-message__bubble {
  max-width: 80%;
  border-radius: 14px;
  padding: 0.75rem;
  background: #fff;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
}

.chat-message--user .chat-message__bubble {
  background: linear-gradient(135deg, #5b7ce6, #4a6cd4);
  color: #fff;
  box-shadow: 0 10px 24px rgba(91, 124, 230, 0.35);
}

.chat-message__role {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  margin-bottom: 0.35rem;
  opacity: 0.8;
  text-transform: uppercase;
}

.chat-message__content {
  font-size: 0.875rem;
  line-height: 1.45;
  white-space: pre-wrap;
}

.chat-widget__typing {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: #6b7280;
}

.typing-indicator {
  display: inline-flex;
  gap: 0.2rem;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  display: block;
  background: #5b7ce6;
  animation: typing 1.2s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 80%, 100% {
    opacity: 0.2;
    transform: translateY(0);
  }
  40% {
    opacity: 1;
    transform: translateY(-2px);
  }
}

.chat-widget__error {
  margin: 0 1.25rem;
  padding: 0.65rem 0.75rem;
  font-size: 0.8125rem;
  background: rgba(239, 68, 68, 0.08);
  color: #b91c1c;
  border-radius: 10px;
}

.chat-widget__form {
  padding: 1rem 1.25rem 1.25rem;
  border-top: 1px solid rgba(15, 23, 42, 0.08);
  background: #fff;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.chat-widget__input {
  width: 100%;
  border: 1px solid rgba(15, 23, 42, 0.12);
  border-radius: 12px;
  padding: 0.75rem;
  font-size: 0.875rem;
  resize: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.chat-widget__input:focus {
  border-color: #5b7ce6;
  box-shadow: 0 0 0 3px rgba(91, 124, 230, 0.15);
  outline: none;
}

.chat-widget__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chat-widget__send {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: linear-gradient(135deg, #5b7ce6, #4a6cd4);
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 0.55rem 1.1rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.chat-widget__send:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.chat-widget__send:not(:disabled):hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(91, 124, 230, 0.35);
}

.chat-widget__reset {
  background: transparent;
  border: none;
  color: #6b7280;
  font-size: 0.8125rem;
  cursor: pointer;
  transition: color 0.2s ease;
}

.chat-widget__reset:hover {
  color: #1f2937;
}

.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.chat-slide-enter-from,
.chat-slide-leave-to {
  opacity: 0;
  transform: translateY(12px);
}

@media (max-width: 640px) {
  .chat-widget {
    right: 1rem;
    bottom: 1rem;
  }

  .chat-widget__panel {
    width: calc(100vw - 2rem);
    max-height: calc(100vh - 4rem);
  }
}
</style>
