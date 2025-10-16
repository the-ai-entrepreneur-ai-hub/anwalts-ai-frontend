<template>
  <div ref="shellRef" class="portal-shell">
    <div class="portal-shell__frame">
      <aside class="portal-sidebar">
        <div class="portal-sidebar__header">
          <div class="portal-brand">
            <div class="portal-brand__mark">A</div>
            <span class="portal-brand__name">ANWALTS.AI</span>
          </div>
        </div>

        <nav class="portal-nav" aria-label="Portal Navigation">
          <a href="/assistant" id="linkAssistant" class="sidebar-link" title="KI-Assistent öffnen">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
            </svg>
            <span>KI-Assistent</span>
          </a>

          <a href="/documents" id="linkDocuments" class="sidebar-link" title="Dokumente öffnen">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            <span>Dokumente</span>
          </a>
          <a href="/templates" id="linkTemplates" class="sidebar-link" title="Vorlagen öffnen">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h10M7 11h10M7 15h6M5 5a2 2 0 012-2h10a2 2 0 012 2v14a2 2 0 01-2 2H7a2 2 0 01-2-2V5z"></path>
            </svg>
            <span>Vorlagen</span>
          </a>
          <a href="/email" id="linkEmails" class="sidebar-link" title="E-Mails öffnen">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
            </svg>
            <span>E‑Mails</span>
          </a>
          <a href="/settings" id="linkSettings" class="sidebar-link" title="Einstellungen öffnen">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
            <span>Einstellungen</span>
          </a>
        </nav>

        <footer class="portal-sidebar__footer" aria-label="Angemeldeter Benutzer">
          <div class="portal-user">
            <div class="portal-user__avatar" aria-hidden="true"></div>
            <div class="portal-user__meta">
              <p class="portal-user__name">{{ user?.name || user?.email || 'Benutzer' }}</p>
              <p class="portal-user__role">{{ user?.role ? capitalize(user.role) : 'Angemeldet' }}</p>
            </div>
          </div>
        </footer>
      </aside>

      <div class="portal-main">
        <div class="portal-main__header">
          <slot name="header" />
        </div>
        <main class="portal-main__scroll">
          <slot />
        </main>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRoute } from '#imports'
import { usePortalUser } from '~/composables/usePortalUser'

const shellRef = ref<HTMLElement | null>(null)
const route = useRoute()
const { user, loadUser } = usePortalUser()

const capitalize = (value: string) => {
  if (!value) return ''
  return value.charAt(0).toUpperCase() + value.slice(1)
}

const normalizePath = (value: string) => {
  return value.split('?')[0].split('#')[0].replace(/\/$/, '') || '/'
}

const setActiveLink = (path: string) => {
  if (!process.client) return
  const root = shellRef.value
  if (!root) return
  const normalizedPath = normalizePath(path)
  const links = root.querySelectorAll<HTMLAnchorElement>('.sidebar-link')
  links.forEach(link => {
    const href = link.getAttribute('href') || ''
    const normalizedHref = normalizePath(href)
    let active = normalizedPath === normalizedHref
    if (!active && normalizedHref !== '/' && normalizedPath.startsWith(`${normalizedHref}/`)) {
      active = true
    }
    link.classList.toggle('active', active)
  })
}

onMounted(() => {
  loadUser()
  nextTick(() => setActiveLink(route.path))
})

watch(() => route.path, (path) => {
  nextTick(() => setActiveLink(path))
})
</script>

<style scoped>
.portal-shell {
  min-height: 100vh;
  background: linear-gradient(180deg, #f2f4fb 0%, #f7f8fc 40%, #ffffff 100%);
  color: #1f2c4f;
}

.portal-shell__frame {
  display: flex;
  min-height: 100vh;
}

.portal-sidebar {
  width: clamp(15rem, 16vw + 6rem, 19rem);
  background: #ffffff;
  border-right: 1px solid rgba(35, 49, 89, 0.08);
  display: flex;
  flex-direction: column;
  padding: 28px 24px;
}

.portal-sidebar__header {
  margin-bottom: 24px;
}

.portal-brand {
  display: flex;
  align-items: center;
  gap: 14px;
}

.portal-brand__mark {
  width: 44px;
  height: 44px;
  border-radius: 16px;
  background: linear-gradient(135deg, #6c7eff 0%, #4f63de 100%);
  color: #ffffff;
  display: grid;
  place-items: center;
  font-weight: 600;
  font-size: 18px;
  letter-spacing: 0.04em;
}

.portal-brand__name {
  font-size: 1.06rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: #1f2c4f;
}

.portal-nav {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 24px;
}

.portal-sidebar__footer {
  margin-top: auto;
  padding-top: 22px;
  border-top: 1px solid rgba(35, 49, 89, 0.08);
}

.portal-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.portal-user__avatar {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(113, 134, 255, 0.2), rgba(113, 134, 255, 0.45));
}

.portal-user__meta {
  display: flex;
  flex-direction: column;
}

.portal-user__name {
  font-size: 0.9rem;
  font-weight: 600;
  color: #243153;
}

.portal-user__role {
  font-size: 0.72rem;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  color: rgba(36, 49, 83, 0.6);
}

.portal-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.portal-main__header {
  position: sticky;
  top: 0;
  z-index: 30;
}

.portal-main__scroll {
  flex: 1;
  overflow-y: auto;
  background: transparent;
}

@media (max-width: 960px) {
  .portal-shell__frame {
    flex-direction: column;
  }

  .portal-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid rgba(35, 49, 89, 0.08);
    padding-bottom: 16px;
  }

  .portal-main__scroll {
    min-height: calc(100vh - 240px);
  }
}

/* Match Overview page active state */
.sidebar-link.active {
  background-color: #eff6ff !important;
  color: #2563eb !important;
  box-shadow: none !important;
  transform: none !important;
}

.sidebar-link:hover {
  background: rgba(37, 99, 235, 0.08) !important;
  color: #1e40af !important;
}
</style>
