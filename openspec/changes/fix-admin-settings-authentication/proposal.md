## Why

The Admin Settings page (`/dashboard/settings`) is currently non-functional due to a critical authentication token mismatch. The frontend attempts to use `useSupabaseSession()` to retrieve access tokens, but this composable:
1. Is not defined in the codebase (returns undefined)
2. Returns Supabase JWT tokens incompatible with the backend's custom JWT validation

The backend (`auth_service.py` lines 64-79) expects custom JWT tokens created by `auth_service.create_access_token()`, which are stored in cookies (`auth_token`, `sid`, `sat`). Backend logs show "Error verifying token: 401: Invalid token format" followed by 403 Forbidden responses, preventing the Admin Settings page from loading any data despite having a functional `/api/admin/settings` endpoint with correct database schema.

This is a critical blocker for admin users who need access to system statistics, organization settings, and administrative controls.

## What Changes

### Frontend Authentication Fix
- **Remove `useSupabaseSession()` usage** in `pages/settings.vue` (line 249, 293)
- **Use `useSupabaseAuth()` composable** to access the correct session format via `session.value?.access_token`
- **Alternative: Remove explicit Authorization header** and rely on automatic cookie transmission via `$fetch`
- **Add comprehensive error logging** to track token types, response status, and authentication errors

### Create Missing Composable (Optional)
- **Create `composables/useSupabaseSession.ts`** as a wrapper if `useSupabaseSession()` is needed elsewhere
- Export session from `useSupabaseAuth()` to maintain API compatibility

### Enhanced Error Handling
- **Improve error messages** with specific guidance for 401, 403, and 500 status codes
- **Add token debugging** to log the token being sent and response headers
- **Maintain existing error display** with retry functionality from previous fixes

### Verification
- **Backend endpoints are confirmed functional** (`/api/admin/settings` exists, database schema correct)
- **Admin role verification** is working correctly (lines 606-624 in backend-main.py)
- **No database changes required** (13 users, 1 email, 15 analytics events, organization_settings populated)

## Impact

### Affected Specs
- `admin-settings` - Fix authentication token handling in settings page data loading
- `authentication` - Document correct composable usage for JWT token access

### Affected Code
- `/root/anwalts-frontend-new/pages/settings.vue` - Lines 249, 293-305 (authentication)
- `/root/anwalts-frontend-new/composables/useSupabaseSession.ts` - New file (optional wrapper)
- `/root/anwalts-frontend-new/composables/useSupabaseAuth.ts` - Reference for correct session access

### Risk Assessment
- **Low Risk**: Changes are isolated to settings page authentication
- **No Database Changes**: All schema is verified correct on production server
- **Backward Compatible**: Won't affect other pages using `useSupabaseAuth()`
- **Easy Rollback**: Keep backup of `settings.vue` before changes

### Success Criteria
1. Admin Settings page loads without 403 Forbidden errors
2. System statistics display correctly (13 users, 1 email, etc.)
3. Organization settings form populates with data
4. Recent activity displays analytics events
5. Backend logs show successful 200 OK responses for `/api/admin/settings`
6. No authentication token format errors in backend logs

### Related Changes
- Builds on `implement-admin-only-settings-dashboard` (43/53 tasks)
- Addresses authentication issues identified after initial implementation
- No breaking changes to existing authentication flow
