export function safeLocationAssign(path: string) {
  try {
    if (typeof window !== 'undefined') {
      // Avoid double navigation loops
      if (window.location.pathname !== path) {
        window.location.assign(path)
      }
    }
  } catch (_) {
    // ignore
  }
}

