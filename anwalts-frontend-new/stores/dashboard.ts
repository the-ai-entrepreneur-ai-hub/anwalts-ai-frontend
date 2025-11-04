import { ref } from 'vue'
import { defineStore } from 'pinia'

type DashboardStats = {
  newCases: number
  documents: number
  emails: number
  nextDeadline: string | null
}

type DashboardDocument = {
  id: string
  title: string
  updated_at: string | null
  status: string
  progress: number
  statusType: string
  details: string
}

type DashboardDeadline = {
  id: string
  title: string
  description: string
  due_date: string
  priority: string
}

type DashboardActivity = {
  id: string
  type: string
  title: string
  description: string
  client: string
  status: string
  created_at: string
}

type DashboardContinueSuggestion = {
  id: string
  title: string
  progress: number
  deadline: string | null
}

type DashboardUser = {
  name: string
  email: string
}

type DashboardResponse = {
  stats: DashboardStats
  recentDocuments: DashboardDocument[]
  upcomingDeadlines: DashboardDeadline[]
  recentActivity: DashboardActivity[]
  continueSuggestion: DashboardContinueSuggestion | null
  user: DashboardUser
  warnings: string[]
}

export const useDashboardStore = defineStore('dashboard', () => {
  const resolveAuthHeaders = (): Record<string, string> => {
    if (typeof window === 'undefined') return {}
    const storageKeys = ['auth_token', 'anwalts_auth_token', 'token', 'access_token', 'sat']
    let token: string | null = null

    try {
      for (const key of storageKeys) {
        const value = window.localStorage?.getItem?.(key)
        if (value) {
          token = value
          break
        }
      }
    } catch (_) {
      token = null
    }

    if (!token && typeof document !== 'undefined') {
      try {
        const cookies = document.cookie?.split(';').map(part => part.trim()).filter(Boolean) || []
        for (const entry of cookies) {
          const [rawKey, ...rest] = entry.split('=')
          if (storageKeys.includes(decodeURIComponent(rawKey || ''))) {
            token = decodeURIComponent(rest.join('=') || '')
            if (token) break
          }
        }
      } catch (_) {
        token = null
      }
    }

    if (!token) return {}
    let cleaned = decodeURIComponent(token)
    cleaned = cleaned.trim()
    if (cleaned.startsWith('"') && cleaned.endsWith('"')) {
        cleaned = cleaned.slice(1, -1)
    }
    if (cleaned.startsWith("'") && cleaned.endsWith("'")) {
        cleaned = cleaned.slice(1, -1)
    }
    const bearer = cleaned.startsWith('Bearer ') ? cleaned : `Bearer ${cleaned}`
    return {
      Authorization: bearer,
      'X-Portal-Auth': bearer
    }
  }

  // Data refs
  const stats = ref<DashboardStats | null>(null)
  const documents = ref<DashboardDocument[]>([])
  const deadlines = ref<DashboardDeadline[]>([])
  const activity = ref<DashboardActivity[]>([])
  const continueSuggestion = ref<DashboardContinueSuggestion | null>(null)
  const userName = ref<string>('')
  const warnings = ref<string[]>([])
  
  // State refs
  const isLoading = ref(false)
  const error = ref<Error | null>(null)

  /**
   * Fetch complete dashboard summary from API
   */
  const fetchSummary = async () => {
    // Prevent duplicate requests
    if (isLoading.value) {
      return
    }

    isLoading.value = true
    error.value = null
    warnings.value = []

    try {
      const headers = resolveAuthHeaders()
      const response = await fetch('/api/dashboard/summary', {
        credentials: 'include',
        headers
      })

      if (!response.ok) {
        throw new Error(`Dashboard summary failed with status ${response.status}`)
      }

      const payload: DashboardResponse = await response.json()

      // Update all data from response
      stats.value = payload.stats
      documents.value = payload.recentDocuments || []
      deadlines.value = payload.upcomingDeadlines || []
      activity.value = payload.recentActivity || []
      continueSuggestion.value = payload.continueSuggestion || null
      userName.value = payload.user?.name || ''
      warnings.value = payload.warnings || []

      return payload
    } catch (err: any) {
      error.value = err instanceof Error ? err : new Error('Unbekannter Fehler')
      
      // Reset to empty state on error
      stats.value = null
      documents.value = []
      deadlines.value = []
      activity.value = []
      continueSuggestion.value = null
      userName.value = ''
      
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Refresh dashboard data (alias for fetchSummary)
   */
  const refresh = async () => {
    return fetchSummary()
  }

  return {
    // Data
    stats,
    documents,
    deadlines,
    activity,
    continueSuggestion,
    userName,
    warnings,
    
    // State
    isLoading,
    error,
    
    // Actions
    fetchSummary,
    refresh
  }
})
