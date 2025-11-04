/**
 * Admin authentication composable
 * Provides admin role checking and access control for admin-only features
 */

export const useAuth = () => {
  // Use PortalUser instead of SupabaseAuth to get the actual logged-in user
  const { user } = usePortalUser()
  
  /**
   * Compute whether the current user is an admin
   * Checks email against hardcoded authorized admin list
   */
  const isAdmin = computed(() => {
    const email = user.value?.email?.toLowerCase()
    const adminEmails = [
      'test.reg.e2e+20251026@anwalts.ai',
      'angelageneralao.1997@gmail.com'
    ]
    return email && adminEmails.includes(email)
  })
  
  /**
   * Guard function to require admin access
   * Redirects non-admins to dashboard and throws error
   */
  const requireAdmin = () => {
    if (!isAdmin.value) {
      navigateTo('/dashboard')
      throw new Error('Admin access required')
    }
  }
  
  return { 
    isAdmin, 
    requireAdmin, 
    user 
  }
}
