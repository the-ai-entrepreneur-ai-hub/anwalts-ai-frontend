<template>
  <Transition name="popup-fade">
    <div v-if="isOpen" class="profile-popup-backdrop" @click="closePopup">
      <Transition name="popup-slide">
        <div v-if="isOpen" class="profile-popup" @click.stop>
          <div class="profile-popup__header">
            <h2>Mein Profil</h2>
            <button class="close-btn" @click="closePopup" aria-label="Schließen">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          <div class="profile-popup__body">
            <!-- Avatar Section -->
            <div class="avatar-section">
              <div class="avatar-large">
                <img v-if="profilePicture" :src="profilePicture" alt="Profilbild" />
                <span v-else class="avatar-initials">{{ getInitials(user?.name) }}</span>
              </div>
              <div class="avatar-actions">
                <button class="btn-upload" @click="triggerFileUpload" :disabled="uploading">
                  <span v-if="uploading">Lädt...</span>
                  <span v-else>Foto hochladen</span>
                </button>
                <button 
                  v-if="profilePicture" 
                  class="btn-remove" 
                  @click="removeProfilePicture"
                  :disabled="uploading"
                >
                  Foto entfernen
                </button>
              </div>
              <input 
                ref="fileInput" 
                type="file" 
                accept="image/jpeg,image/png,image/webp" 
                @change="handleFileUpload"
                style="display: none;"
              />
            </div>

            <!-- User Info Section -->
            <div class="user-info-section">
              <div class="info-row">
                <label>Name</label>
                <p>{{ user?.name || 'Nicht angegeben' }}</p>
              </div>
              <div class="info-row">
                <label>E-Mail</label>
                <p>{{ user?.email || 'Nicht angegeben' }}</p>
              </div>
              <div class="info-row">
                <label>Rolle</label>
                <p>{{ capitalize(user?.role || 'Benutzer') }}</p>
              </div>
            </div>

            <!-- Status Messages -->
            <Transition name="fade">
              <div v-if="statusMessage" :class="['status-message', statusMessage.type]">
                <svg v-if="statusMessage.type === 'success'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span>{{ statusMessage.text }}</span>
              </div>
            </Transition>
          </div>

          <div class="profile-popup__footer">
            <button class="btn-signout" @click="signOut">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
              </svg>
              Abmelden
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { usePortalUser } from '~/composables/usePortalUser'
import { useRouter } from '#imports'

const props = defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

const { user, loadUser } = usePortalUser()
const router = useRouter()

const fileInput = ref<HTMLInputElement | null>(null)
const uploading = ref(false)
const profilePicture = ref<string | null>(null)
const statusMessage = ref<{ type: 'success' | 'error', text: string } | null>(null)

const resolveAuthToken = (): string | null => {
  if (!process.client) return null
  const keys = ['auth_token', 'anwalts_auth_token', 'access_token', 'token', 'sat']
  for (const key of keys) {
    try {
      const value = localStorage.getItem(key)
      if (value) return value
    } catch (_) {
      // storage access can fail in private modes
    }
  }
  return null
}

const getInitials = (name: string | undefined) => {
  if (!name) return '?'
  const words = name.trim().split(' ')
  return words[0].charAt(0).toUpperCase()
}

const capitalize = (str: string) => {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}

const closePopup = () => {
  emit('close')
}

const triggerFileUpload = () => {
  fileInput.value?.click()
}

const showStatus = (type: 'success' | 'error', text: string) => {
  statusMessage.value = { type, text }
  setTimeout(() => {
    statusMessage.value = null
  }, 3000)
}

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return

  // Validate file size (2MB)
  if (file.size > 2 * 1024 * 1024) {
    showStatus('error', 'Datei zu groß. Maximum 2MB.')
    return
  }

  // Validate file type
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
    showStatus('error', 'Ungültiges Format. Nur JPEG, PNG, WebP erlaubt.')
    return
  }

  uploading.value = true

  try {
    const formData = new FormData()
    formData.append('file', file)

    const headers: Record<string, string> = {}
    const token = resolveAuthToken()
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }

    const response = await fetch('/api/user/profile/picture', {
      method: 'POST',
      headers,
      body: formData,
      credentials: 'include'
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Upload fehlgeschlagen')
    }

    const data = await response.json()
    profilePicture.value = data.profile_picture
    showStatus('success', 'Profilbild erfolgreich hochgeladen')
    
    // Reload user data to update avatar in sidebar
    await loadUser()
  } catch (error: any) {
    showStatus('error', error.message || 'Upload fehlgeschlagen. Bitte erneut versuchen.')
  } finally {
    uploading.value = false
    // Clear file input
    if (target) target.value = ''
  }
}

const removeProfilePicture = async () => {
  uploading.value = true

  try {
    const token = resolveAuthToken()
    const headers: Record<string, string> = { 'Content-Type': 'application/json' }
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }

    const response = await fetch('/api/user/profile/picture', {
      method: 'DELETE',
      headers,
      credentials: 'include'
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Löschen fehlgeschlagen')
    }

    profilePicture.value = null
    showStatus('success', 'Profilbild entfernt')
    
    // Reload user data to update avatar in sidebar
    await loadUser()
  } catch (error: any) {
    showStatus('error', error.message || 'Fehler beim Löschen des Profilbilds')
  } finally {
    uploading.value = false
  }
}

const signOut = async () => {
  try {
    const token = resolveAuthToken()
    try {
      const headers: Record<string, string> = {}
      if (token) {
        headers.Authorization = `Bearer ${token}`
      }
      await fetch('/auth/logout', {
        method: 'POST',
        headers: Object.keys(headers).length ? headers : undefined,
        credentials: 'include'
      })
    } catch (logoutError) {
      console.warn('Backend logout request failed', logoutError)
    }

    // Clear local storage
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('auth_token')
    localStorage.removeItem('anwalts_auth_token')
    localStorage.removeItem('user_id')
    localStorage.removeItem('user_email')
    localStorage.removeItem('user_name')
    localStorage.removeItem('user_role')
    localStorage.removeItem('auth_user')
    localStorage.removeItem('anwalts_user')
    
    try {
      sessionStorage.removeItem('oauth_processed')
      sessionStorage.removeItem('oauth_processed_state')
      sessionStorage.removeItem('gmail_oauth_return')
    } catch (_) {
      // session storage might be unavailable
    }
    
    // Redirect to landing page
    await router.push('/')
  } catch (error) {
    console.error('Sign out error:', error)
  }
}

const handleEscKey = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && props.isOpen) {
    closePopup()
  }
}

onMounted(async () => {
  window.addEventListener('keydown', handleEscKey)
  
  // Load profile picture if exists
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
    // Profile picture doesn't exist, show initials
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleEscKey)
})
</script>

<style scoped>
.profile-popup-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: transparent;
  z-index: 9999;
}

.profile-popup {
  position: fixed;
  bottom: 90px;
  left: 24px;
  background: #ffffff;
  border-radius: 16px;
  width: 300px;
  max-height: 500px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 24px rgba(31, 44, 79, 0.15), 0 2px 8px rgba(31, 44, 79, 0.08);
  border: 1px solid rgba(35, 49, 89, 0.08);
}

.profile-popup__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(35, 49, 89, 0.08);
}

.profile-popup__header h2 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2c4f;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(107, 114, 128, 0.1);
  color: #1f2c4f;
}

.profile-popup__body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(35, 49, 89, 0.08);
}

.avatar-large {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(113, 134, 255, 0.2), rgba(113, 134, 255, 0.45));
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  overflow: hidden;
  clip-path: circle(50%);
}

.avatar-large img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.avatar-initials {
  font-size: 1.6rem;
  font-weight: 600;
  color: #4f63de;
}

.avatar-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.btn-upload,
.btn-remove {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  width: 100%;
}

.btn-upload {
  background: linear-gradient(135deg, #6c7eff 0%, #4f63de 100%);
  color: #ffffff;
}

.btn-upload:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(108, 126, 255, 0.3);
}

.btn-upload:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-remove {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.btn-remove:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.2);
}

.user-info-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.info-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-row label {
  font-size: 0.7rem;
  font-weight: 600;
  color: rgba(31, 44, 79, 0.6);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-row p {
  font-size: 0.9rem;
  color: #1f2c4f;
  margin: 0;
}

.status-message {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 500;
  margin-top: 16px;
}

.status-message.success {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
}

.status-message.error {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.profile-popup__footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(35, 49, 89, 0.08);
  display: flex;
  justify-content: stretch;
}

.btn-signout {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 500;
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
}

.btn-signout:hover {
  background: rgba(239, 68, 68, 0.2);
}

/* Animations */
.popup-fade-enter-active,
.popup-fade-leave-active {
  transition: opacity 0.25s ease;
}

.popup-fade-enter-from,
.popup-fade-leave-to {
  opacity: 0;
}

.popup-slide-enter-active,
.popup-slide-leave-active {
  transition: all 0.2s ease-out;
}

.popup-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.popup-slide-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .profile-popup {
    bottom: 16px;
    left: 16px;
    right: 16px;
    width: auto;
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .popup-fade-enter-active,
  .popup-fade-leave-active,
  .popup-slide-enter-active,
  .popup-slide-leave-active,
  .fade-enter-active,
  .fade-leave-active {
    transition: none;
  }

  .popup-slide-enter-from,
  .popup-slide-leave-to {
    transform: none;
  }
}
</style>
