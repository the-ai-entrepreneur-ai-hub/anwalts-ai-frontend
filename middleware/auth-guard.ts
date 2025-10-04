export default defineNuxtRouteMiddleware(async (to) => {
  // Allow public pages
  const PUBLIC = new Set<string>(['/', '/privacy', '/terms', '/contact', '/changelog', '/test-login', '/test-auth'])
  if (PUBLIC.has(to.path)) return

  // Server-side: skip redirect to let client check auth after hydration
  if (process.server) {
    return
  }

  // Client-side guard
  try {
    // Check backend auth directly via Nginx-mapped route
    const res: any = await $fetch('/auth/validate', { credentials: 'include' })
    if (res && res.authenticated) return
  } catch (_) {}

  const target = new URL(window.location.href)
  if (!target.searchParams.has('auth')) target.searchParams.set('auth', 'required')
  window.history.replaceState({}, document.title, target.toString())
  return navigateTo('/?auth=required')
})
