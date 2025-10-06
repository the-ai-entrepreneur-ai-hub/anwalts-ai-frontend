import { ref } from 'vue'
import { defineStore } from 'pinia'

type DashboardSummary = {
  newCases: number
  documents: number
  emails: number
  nextDeadline: string | null
}

type DashboardResponse = {
  stats: DashboardSummary
  warnings?: string[]
  profile?: Record<string, any> | null
}

export const useDashboardStore = defineStore('dashboard', () => {
  const stats = ref<DashboardSummary | null>(null)
  const warnings = ref<string[]>([])
  const isLoading = ref(false)
  const error = ref<Error | null>(null)

  const fetchSummary = async () => {
    if (isLoading.value) {
      return stats.value ? { stats: stats.value, warnings: warnings.value } : undefined
    }

    isLoading.value = true
    error.value = null
    warnings.value = []

    try {
      const { $fetch } = useNuxtApp()
      const response = await $fetch<DashboardResponse>('/api/dashboard/summary', {
        credentials: 'include'
      })

      stats.value = response.stats
      warnings.value = response.warnings ?? []
      return response
    } catch (err: any) {
      error.value = err instanceof Error ? err : new Error('Unbekannter Fehler')
      stats.value = null
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    stats,
    warnings,
    isLoading,
    error,
    fetchSummary
  }
})
