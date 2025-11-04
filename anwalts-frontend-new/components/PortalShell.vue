<template>
  <div ref="shellRef" class="portal-shell">
    <!-- Mobile Menu Button -->
    <button 
      class="mobile-menu-btn" 
      @click="toggleMobileMenu"
      aria-label="Navigation öffnen"
      aria-expanded="false"
      :aria-expanded="isMobileMenuOpen"
    >
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path v-if="!isMobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
        <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
      </svg>
    </button>

    <!-- Mobile Menu Backdrop -->
    <div 
      class="mobile-menu-backdrop" 
      :class="{ active: isMobileMenuOpen }"
      @click="closeMobileMenu"
      aria-hidden="true"
    ></div>

    <div class="portal-shell__frame">
      <aside class="portal-sidebar" :class="{ 'mobile-open': isMobileMenuOpen }">
        <div class="portal-sidebar__header">
          <div class="portal-brand">
            <div class="portal-brand__mark">A</div>
            <span class="portal-brand__name">ANWALTS.AI</span>
          </div>
        </div>

        <nav class="portal-nav" aria-label="Portal Navigation">
          <a href="/dashboard" id="linkDashboard" class="sidebar-link" title="Übersicht öffnen" @click="handleNavClick">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
            </svg>
            <span>Übersicht</span>
          </a>

          <a href="/assistant" id="linkAssistant" class="sidebar-link" title="KI-Assistent öffnen" @click="handleNavClick">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
            </svg>
            <span>KI-Assistent</span>
          </a>

          <a href="/documents" id="linkDocuments" class="sidebar-link" title="Dokumente öffnen" @click="handleNavClick">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            <span>Dokumente</span>
          </a>
          <a href="/templates" id="linkTemplates" class="sidebar-link" title="Vorlagen öffnen" @click="handleNavClick">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h10M7 11h10M7 15h6M5 5a2 2 0 012-2h10a2 2 0 012 2v14a2 2 0 01-2 2H7a2 2 0 01-2-2V5z"></path>
            </svg>
            <span>Vorlagen</span>
          </a>
          <a href="/email" id="linkEmails" class="sidebar-link" title="E-Mails öffnen" @click="handleNavClick">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
            </svg>
            <span>E‑Mails</span>
          </a>
          <a v-if="isAdmin" href="/settings" id="linkSettings" class="sidebar-link" title="Einstellungen öffnen" @click="handleNavClick">
            <svg class="w-5 h-5 icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
            <span>Einstellungen</span>
          </a>
        </nav>

        <footer class="portal-sidebar__footer" aria-label="Angemeldeter Benutzer">
          <div class="portal-user" @click="openProfilePopup" role="button" tabindex="0" @keydown.enter="openProfilePopup" @keydown.space.prevent="openProfilePopup">
            <div class="portal-user__avatar" aria-hidden="true">
              <img v-if="profilePicture" :src="profilePicture" alt="Profilbild" />
              <span v-else class="avatar-initials">{{ getInitials(user?.name) }}</span>
            </div>
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
    
    <ProfilePopup :isOpen="showProfilePopup" @close="closeProfilePopup" />
    <ChatWidget />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick, computed } from 'vue'
import { useRoute } from '#imports'
import { usePortalUser } from '~/composables/usePortalUser'
import { useAuth } from '~/composables/useAuth'
import ProfilePopup from './ProfilePopup.vue'
import ChatWidget from '~/components/ChatWidget.vue'

const shellRef = ref<HTMLElement | null>(null)
const route = useRoute()
const { user, loadUser } = usePortalUser()
const { isAdmin } = useAuth()
const showProfilePopup = ref(false)
const profilePicture = ref<string | null>(null)
const isMobileMenuOpen = ref(false)

const capitalize = (value: string) => {
  if (!value) return ''
  return value.charAt(0).toUpperCase() + value.slice(1)
}

const getInitials = (name: string | undefined) => {
  if (!name) return '?'
  const words = name.trim().split(' ')
  return words[0].charAt(0).toUpperCase()
}

const openProfilePopup = () => {
  showProfilePopup.value = true
}

const closeProfilePopup = () => {
  showProfilePopup.value = false
  loadProfilePicture()
}

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
}

const handleNavClick = () => {
  // Close mobile menu when navigation link is clicked
  if (isMobileMenuOpen.value) {
    closeMobileMenu()
  }
}

const resolveAuthToken = (): string | null => {
  if (!process.client) return null
  const keys = ['auth_token', 'anwalts_auth_token', 'access_token', 'token', 'sat']
  for (const key of keys) {
    try {
      const value = localStorage.getItem(key)
      if (value) return value
    } catch (_) {
      // ignore storage access issues
    }
  }
  return null
}

const loadProfilePicture = async () => {
  try {
    const headers: Record<string, string> = {}
    const token = resolveAuthToken()
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }

    const response = await fetch('/api/user/profile/picture', {
      headers,
      credentials: 'include'
    })
    
    if (response.ok) {
      const data = await response.json()
      profilePicture.value = data.profile_picture
    }
  } catch (error) {
    // Profile picture doesn't exist
  }
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
  loadProfilePicture()
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
  cursor: pointer;
  padding: 8px;
  margin: -8px;
  border-radius: 12px;
  transition: background 0.2s ease;
}

.portal-user:hover {
  background: rgba(108, 126, 255, 0.05);
}

.portal-user:focus-visible {
  outline: 2px solid rgba(108, 126, 255, 0.4);
  outline-offset: 2px;
}

.portal-user__avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(113, 134, 255, 0.2), rgba(113, 134, 255, 0.45));
  overflow: hidden;
  clip-path: circle(50%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.portal-user__avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.avatar-initials {
  font-size: 1.1rem;
  font-weight: 600;
  color: #4f63de;
  user-select: none;
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

/* Mobile Menu Button */
.mobile-menu-btn {
  display: none;
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: 60;
  width: 48px;
  height: 48px;
  background: #ffffff;
  border: 1px solid rgba(35, 49, 89, 0.12);
  border-radius: 12px;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  color: #1f2c4f;
}

.mobile-menu-btn:hover {
  background: #f7f8fc;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.mobile-menu-btn:active {
  transform: scale(0.95);
}

.mobile-menu-btn .w-6 {
  width: 24px;
  height: 24px;
}

/* Mobile Menu Backdrop */
.mobile-menu-backdrop {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 40;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.mobile-menu-backdrop.active {
  display: block;
  opacity: 1;
}

@media (max-width: 960px) {
  .mobile-menu-btn {
    display: flex;
  }

  .portal-shell__frame {
    flex-direction: row;
  }

  .portal-sidebar {
    position: fixed;
    top: 0;
    left: -100%;
    height: 100vh;
    width: 280px;
    max-width: 85vw;
    z-index: 50;
    border-right: 1px solid rgba(35, 49, 89, 0.08);
    border-bottom: none;
    padding: 28px 24px;
    transition: left 0.3s ease;
    box-shadow: 2px 0 16px rgba(0, 0, 0, 0.2);
    overflow-y: auto;
  }

  .portal-sidebar.mobile-open {
    left: 0;
  }

  .portal-main {
    width: 100%;
  }

  .portal-main__scroll {
    min-height: 100vh;
  }
}

/* Sidebar Link Base Styles */
.sidebar-link {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 0.92rem;
  font-weight: 500;
  letter-spacing: 0.01em;
  color: #2a3553;
  background: transparent;
  border: 1px solid transparent;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.26s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-link .icon {
  width: 18px;
  height: 18px;
  color: currentColor;
  flex-shrink: 0;
}

.sidebar-link:hover {
  background: rgba(91, 115, 242, 0.12);
  color: #1f2645;
  border: 1px solid rgba(91, 115, 242, 0.26);
  transform: translateX(2px);
}

.sidebar-link.active {
  background-color: #eff6ff;
  color: #556cf0;
  border: 1px solid rgba(91, 115, 242, 0.2);
  box-shadow: none;
  transform: translateX(2px);
}
</style>
