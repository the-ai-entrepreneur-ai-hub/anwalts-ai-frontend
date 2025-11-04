## 1. Frontend Authentication Fix

### 1.1 Update settings.vue Authentication
- [x] 1.1.1 Remove `useSupabaseSession()` import and usage (line 249)
- [x] 1.1.2 Replace with `useSupabaseAuth()` to access `session.value`
- [x] 1.1.3 Update `loadSettings()` to use correct token from session (lines 293-305)
- [x] 1.1.4 Add conditional Authorization header only when token exists

### 1.2 Add Authentication Debug Logging
- [x] 1.2.1 Log the token being sent to backend (first 20 chars only for security)
- [x] 1.2.2 Log response status and headers in error handling
- [x] 1.2.3 Add specific error messages for token authentication failures
- [x] 1.2.4 Maintain existing errorDebug state for detailed error info

### 1.3 Test Token Fallback Strategy
- [x] 1.3.1 Verify explicit Authorization header approach works
- [ ] 1.3.2 Test cookie-based authentication without explicit header
- [x] 1.3.3 Document which approach is used and why

## 2. Create Missing Composable (Optional)

### 2.1 Create useSupabaseSession Wrapper
- [x] 2.1.1 Create `/root/anwalts-frontend-new/composables/useSupabaseSession.ts` - NOT NEEDED (no other usages found)
- [x] 2.1.2 Import and use `useSupabaseAuth()` internally - NOT NEEDED
- [x] 2.1.3 Export `session` from `useSupabaseAuth()` for compatibility - NOT NEEDED
- [x] 2.1.4 Add TypeScript types matching Supabase Session type - NOT NEEDED

### 2.2 Update Documentation
- [x] 2.2.1 Document the relationship between `useSupabaseSession()` and `useSupabaseAuth()` - Documented in design.md
- [x] 2.2.2 Add code comments explaining token flow - Added inline in code
- [x] 2.2.3 Note that backend expects custom JWT tokens, not Supabase tokens - Added to error logging

## 3. Testing & Verification

### 3.1 Local Testing
- [ ] 3.1.1 Login as admin user (authorized email)
- [ ] 3.1.2 Navigate to `/dashboard/settings` page
- [ ] 3.1.3 Verify no 403 Forbidden errors in browser console
- [ ] 3.1.4 Confirm statistics show correct counts (13 users, 1 email, etc.)
- [ ] 3.1.5 Verify organization settings load and populate form
- [ ] 3.1.6 Check that recent activity displays correctly

### 3.2 Backend Verification
- [ ] 3.2.1 Monitor backend logs for successful `/api/admin/settings` requests
- [ ] 3.2.2 Confirm 200 OK responses (no 401 or 403 errors)
- [ ] 3.2.3 Verify no "Invalid token format" errors in logs
- [ ] 3.2.4 Check that admin guard middleware accepts requests

### 3.3 Error Handling Testing
- [ ] 3.3.1 Test behavior with expired token
- [ ] 3.3.2 Test behavior with missing token
- [ ] 3.3.3 Verify retry button works correctly
- [ ] 3.3.4 Confirm error messages are helpful and specific

### 3.4 Cross-Browser Testing
- [ ] 3.4.1 Test in Chrome
- [ ] 3.4.2 Test in Firefox
- [ ] 3.4.3 Test in Safari (if available)
- [ ] 3.4.4 Verify cookie handling works consistently

## 4. Production Deployment

### 4.1 Pre-Deployment
- [ ] 4.1.1 Backup current `settings.vue` file
- [ ] 4.1.2 Create rollback script if needed
- [ ] 4.1.3 Verify admin user list is correct in backend

### 4.2 Deploy Frontend Changes
- [x] 4.2.1 Build frontend with changes: `npm run build` - Build successful (4.65 MB)
- [ ] 4.2.2 Rebuild frontend Docker container
- [ ] 4.2.3 Restart `anwalts_frontend` container
- [ ] 4.2.4 Verify container health check passes

### 4.3 Post-Deployment Verification
- [ ] 4.3.1 Login as admin and access settings page
- [ ] 4.3.2 Verify data loads correctly
- [ ] 4.3.3 Check browser console for any errors
- [ ] 4.3.4 Monitor backend logs for authentication success
- [ ] 4.3.5 Verify organization settings save functionality works

### 4.4 Rollback Plan (If Needed)
- [ ] 4.4.1 Restore backed-up `settings.vue` file
- [ ] 4.4.2 Rebuild and restart frontend container
- [ ] 4.4.3 Remove created `useSupabaseSession.ts` if added
- [ ] 4.4.4 Document what went wrong for future fixes

## 5. Documentation

### 5.1 Update Technical Documentation
- [ ] 5.1.1 Document the authentication flow for admin endpoints
- [ ] 5.1.2 Explain the difference between Supabase and custom JWT tokens
- [ ] 5.1.3 Add troubleshooting guide for 401/403 errors
- [ ] 5.1.4 Document which composables to use for authentication

### 5.2 Add Code Comments
- [ ] 5.2.1 Comment why specific token approach is used
- [ ] 5.2.2 Add note about backend JWT validation requirements
- [ ] 5.2.3 Document the session object structure expected

## 6. Future Improvements (Post-Fix)

### 6.1 Unify Authentication Approach
- [ ] 6.1.1 Consider standardizing on one token type throughout app
- [ ] 6.1.2 Evaluate if backend should accept Supabase tokens
- [ ] 6.1.3 Or ensure all frontend code uses custom JWT tokens consistently

### 6.2 Add Token Refresh Logic
- [ ] 6.2.1 Implement automatic token refresh before expiry
- [ ] 6.2.2 Add user-friendly re-authentication prompt on token expiry
- [ ] 6.2.3 Handle token refresh errors gracefully

### 6.3 Improve Admin Role Management
- [ ] 6.3.1 Consider database-driven admin roles vs hardcoded emails
- [ ] 6.3.2 Add admin role assignment UI
- [ ] 6.3.3 Implement role-based access control (RBAC) system
