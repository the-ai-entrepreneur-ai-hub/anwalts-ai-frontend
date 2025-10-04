import { ref } from 'vue'

// Simple shared state for auth modal visibility
const isOpen = ref(false)

export function useAuthModal() {
  function open() { isOpen.value = true }
  function close() { isOpen.value = false }

  return { isOpen, open, close }
}

