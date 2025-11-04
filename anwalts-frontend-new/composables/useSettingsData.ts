import { computed, reactive, ref, type Ref } from 'vue'

interface PendingMap {
  overview: boolean
  apiKeys: boolean
  endpoints: boolean
  webhooks: boolean
  users: boolean
  preferences: boolean
}

interface HydrationState {
  pending: PendingMap
  errors: Partial<Record<keyof PendingMap, string>>
  busySegments: Ref<number>
  isHydrated: Ref<boolean>
  start(task: keyof PendingMap): void
  finish(task: keyof PendingMap): void
  fail(task: keyof PendingMap, message: string): void
  reset(): void
}

export function useSettingsHydration(): HydrationState {
  const pending = reactive<PendingMap>({
    overview: false,
    apiKeys: false,
    endpoints: false,
    webhooks: false,
    users: false,
    preferences: false
  })
  const errors = reactive<Partial<Record<keyof PendingMap, string>>>({})
  const busySegments = ref(0)

  const isHydrated = computed(() => busySegments.value === 0)

  const start = (task: keyof PendingMap) => {
    if (!pending[task]) {
      pending[task] = true
      busySegments.value += 1
    }
    errors[task] = undefined
  }

  const finish = (task: keyof PendingMap) => {
    if (pending[task]) {
      pending[task] = false
      busySegments.value = Math.max(0, busySegments.value - 1)
    }
  }

  const fail = (task: keyof PendingMap, message: string) => {
    errors[task] = message
  }

  const reset = () => {
    (Object.keys(pending) as Array<keyof PendingMap>).forEach((key) => {
      pending[key] = false
      errors[key] = undefined
    })
    busySegments.value = 0
  }

  return {
    pending,
    errors,
    busySegments,
    isHydrated,
    start,
    finish,
    fail,
    reset
  }
}
