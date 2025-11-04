## Context

### Background

The Anwalts AI platform uses a dual authentication system:
1. **Supabase Auth** - For user registration, OAuth flows, and session management
2. **Custom JWT Tokens** - For API authentication via FastAPI backend

The Admin Settings page was implemented using `useSupabaseSession()` to retrieve access tokens, but this approach causes a critical authentication failure because:

- **Frontend Issue**: `useSupabaseSession()` is not defined in the codebase, or returns Supabase-specific JWT tokens
- **Backend Issue**: The FastAPI backend (`auth_service.py` lines 64-79) validates only custom JWT tokens created by `auth_service.create_access_token()`
- **Token Storage**: Custom JWT tokens are stored in cookies (`auth_token`, `sid`, `sat`) and managed by `useSupabaseAuth()` composable
- **Validation Logic**: Backend expects 3-part JWT structure (header.payload.signature) signed with `JWT_SECRET_KEY`

### Current State

**Production Server (148.251.195.222):**
- Backend `/api/admin/settings` endpoint exists and is functional
- Database schema is complete (users, organization_settings, analytics_events tables)
- Database contains data: 13 users, 1 email account, 15 analytics events
- Admin guard middleware is active (lines 606-624 in backend-main.py)
- Admin emails: `test.reg.e2e+20251026@anwalts.ai`, `angelageneralao.1997@gmail.com`

**Frontend (settings.vue):**
- Line 249: Calls `const supabaseSession = useSupabaseSession()`
- Lines 293-305: Uses `supabaseSession.value?.access_token` in Authorization header
- Results in 403 Forbidden responses from backend

**Backend Logs Show:**
```
Error verifying token: 401: Invalid token format
403 Forbidden - Admin access denied
```

### Stakeholders

- **Admin Users**: Need access to system statistics and organization settings
- **Developers**: Need clear authentication flow documentation
- **DevOps**: Need reliable authentication without breaking other pages

## Goals / Non-Goals

### Goals

1. **Fix Admin Settings authentication** - Enable admin users to access settings page without 403 errors
2. **Use correct token format** - Ensure custom JWT tokens from `useSupabaseAuth()` are used
3. **Maintain backward compatibility** - Don't break other pages using authentication
4. **Add clear error messages** - Help users and developers diagnose authentication issues
5. **Document authentication flow** - Clarify token types and when to use each

### Non-Goals

1. **Refactor entire authentication system** - Keep existing dual auth approach (Supabase + custom JWT)
2. **Implement new admin features** - Only fix authentication, not add new settings functionality
3. **Change backend JWT validation** - Backend logic is correct, frontend needs to match it
4. **Migrate away from Supabase** - Keep Supabase for OAuth and user management

## Decisions

### Decision 1: Use useSupabaseAuth() Instead of useSupabaseSession()

**Choice**: Replace `useSupabaseSession()` with `useSupabaseAuth()` throughout settings.vue

**Rationale**:
- `useSupabaseAuth()` is the canonical composable in the codebase (`composables/useSupabaseAuth.ts`)
- It provides `session.value` with the correct custom JWT `access_token`
- Tokens are stored in cookies and automatically synced with backend
- Already used successfully in other protected pages

**Alternatives Considered**:
1. **Create useSupabaseSession() wrapper** - Adds unnecessary abstraction layer
2. **Use cookie-based auth only** - Works but less explicit, harder to debug
3. **Change backend to accept Supabase tokens** - Breaking change, affects all endpoints

**Code Change**:
```typescript
// BEFORE (BROKEN)
const supabaseSession = useSupabaseSession()
const response = await $fetch('/api/admin/settings', {
  headers: {
    Authorization: `Bearer ${supabaseSession.value?.access_token}`
  }
})

// AFTER (FIXED - Option A: Explicit header)
const { session } = useSupabaseAuth()
const response = await $fetch('/api/admin/settings', {
  headers: session.value?.access_token ? {
    Authorization: `Bearer ${session.value.access_token}`
  } : {}
})

// AFTER (FIXED - Option B: Cookie-based, simpler)
const response = await $fetch('/api/admin/settings', {
  credentials: 'include' // Automatic cookie transmission
})
```

### Decision 2: Prefer Explicit Authorization Header Over Cookie-Only

**Choice**: Use explicit `Authorization: Bearer {token}` header with conditional inclusion

**Rationale**:
- Makes authentication explicit and visible in network debugging
- Easier to trace token flow in browser DevTools
- Consistent with REST API best practices
- Fallback to cookies still works if header is missing

**Trade-offs**:
- Slightly more code than relying on automatic cookies
- Must handle cases where `session.value` is null/undefined
- Requires accessing nested `session.value?.access_token`

**Implementation**:
```typescript
async function loadSettings() {
  const { session } = useSupabaseAuth()
  
  const response = await $fetch('/api/admin/settings', {
    headers: session.value?.access_token ? {
      Authorization: `Bearer ${session.value.access_token}`
    } : {}
  })
  
  // ... handle response
}
```

### Decision 3: Create Optional useSupabaseSession() Wrapper

**Choice**: Only create wrapper if needed elsewhere in codebase

**Rationale**:
- Current search shows only `settings.vue` uses it
- Adding unnecessary abstractions increases maintenance burden
- Direct use of `useSupabaseAuth()` is clearer
- Can add wrapper later if multiple files need it

**Implementation (if needed)**:
```typescript
// composables/useSupabaseSession.ts
export const useSupabaseSession = () => {
  const { session } = useSupabaseAuth()
  return session
}
```

### Decision 4: Enhanced Error Logging Strategy

**Choice**: Add comprehensive debug logging for authentication failures

**Rationale**:
- Current errors are vague ("Failed to load settings")
- Need to distinguish between 401 (invalid token), 403 (not admin), 500 (server error)
- Developers need token format visibility without compromising security
- Existing `errorDebug` state from previous fixes is perfect for this

**Implementation**:
```typescript
catch (e) {
  console.error('? Failed to load settings:', e)
  
  errorDebug.value = {
    message: e.message,
    status: e.status,
    statusText: e.statusText,
    data: e.data,
    tokenPreview: session.value?.access_token?.substring(0, 20) + '...', // First 20 chars
    timestamp: new Date().toISOString()
  }
  
  if (e.status === 403) {
    throw new Error('Access denied: Admin privileges required')
  } else if (e.status === 401) {
    throw new Error('Authentication failed: Please login again')
  } else if (e.status === 500) {
    throw new Error('Server error: Please contact administrator')
  } else {
    throw new Error(`Failed to load settings: ${e.message || 'Unknown error'}`)
  }
}
```

## Risks / Trade-offs

### Risk 1: Token Expiry During Session

**Risk**: User's token expires while on settings page

**Impact**: Settings fail to load or save

**Mitigation**:
- Existing retry button allows manual reload
- Future: Add automatic token refresh logic
- Future: Show "Session expired, please login" prompt

**Trade-off**: Accepting temporary UX issue for faster fix delivery

### Risk 2: Cookie Domain/SameSite Issues

**Risk**: Cookies might not be sent due to domain mismatch or SameSite restrictions

**Impact**: Authentication fails even with correct token format

**Mitigation**:
- Verify `SESSION_DOMAIN=portal-anwalts.ai` matches deployment
- Confirm `COOKIE_SAMESITE=none` for cross-origin requests
- Test with explicit Authorization header as primary method
- Cookies are fallback, not primary authentication method

**Trade-off**: Relying on explicit headers reduces cookie configuration complexity

### Risk 3: Breaking Other Pages Using useSupabaseSession()

**Risk**: If other pages use `useSupabaseSession()`, they might break

**Impact**: Undefined errors or authentication failures elsewhere

**Mitigation**:
- Search codebase for all `useSupabaseSession()` usage
- Create wrapper if multiple files depend on it
- Test authentication flow on other protected pages
- Settings page is isolated, unlikely to affect others

**Trade-off**: Focused fix on settings page vs full codebase refactor

### Risk 4: Backend Admin Email List Desync

**Risk**: User's email not in backend admin list despite frontend showing admin badge

**Impact**: Frontend thinks user is admin, backend denies access

**Mitigation**:
- Verify both frontend `useAuth.ts` and backend `backend-main.py` have same admin emails
- Current admin emails: `test.reg.e2e+20251026@anwalts.ai`, `angelageneralao.1997@gmail.com`
- Both systems checked and match ?
- Admin check happens server-side, frontend badge is informational only

**Trade-off**: Trust backend as source of truth for authorization

## Migration Plan

### Phase 1: Code Changes (30 minutes)

1. Update `settings.vue` line 249:
   ```typescript
   // Remove: const supabaseSession = useSupabaseSession()
   // Add: const { session } = useSupabaseAuth()
   ```

2. Update `loadSettings()` function lines 291-305:
   ```typescript
   const response = await $fetch('/api/admin/settings', {
     headers: session.value?.access_token ? {
       Authorization: `Bearer ${session.value.access_token}`
     } : {}
   })
   ```

3. Update `saveSettings()` function lines 366-380:
   ```typescript
   await $fetch('/api/admin/settings/organization', {
     method: 'PUT',
     headers: session.value?.access_token ? {
       Authorization: `Bearer ${session.value.access_token}`
     } : {},
     body: orgSettings.value
   })
   ```

4. Add debug logging to error handling (lines 326-347):
   ```typescript
   errorDebug.value = {
     message: e.message,
     status: e.status,
     statusText: e.statusText,
     data: e.data,
     timestamp: new Date().toISOString()
   }
   ```

### Phase 2: Testing (1 hour)

1. **Local Testing**:
   - Build frontend: `npm run build`
   - Start dev server: `npm run dev`
   - Login as admin user
   - Navigate to `/dashboard/settings`
   - Verify data loads without 403 errors

2. **Network Inspection**:
   - Open browser DevTools Network tab
   - Check Authorization header contains JWT token
   - Verify token format (3 parts separated by dots)
   - Confirm 200 OK response

3. **Backend Log Verification**:
   - Check backend logs for successful requests
   - Confirm no "Invalid token format" errors
   - Verify admin middleware logs show access granted

### Phase 3: Deployment (30 minutes)

1. **Backup Current Code**:
   ```bash
   cp /root/anwalts-frontend-new/pages/settings.vue /root/settings.vue.backup
   ```

2. **Build and Deploy**:
   ```bash
   cd /root/anwalts-frontend-new
   npm run build
   docker build -t anwalts-frontend .
   docker stop anwalts_frontend
   docker rm anwalts_frontend
   docker-compose up -d frontend
   ```

3. **Verify Deployment**:
   ```bash
   docker ps | grep anwalts_frontend
   docker logs anwalts_frontend --tail 50
   curl -I https://portal-anwalts.ai/dashboard/settings
   ```

4. **Smoke Test**:
   - Login to production as admin
   - Access https://portal-anwalts.ai/dashboard/settings
   - Verify statistics display
   - Check browser console for errors

### Phase 4: Rollback (If Needed)

1. **Restore Backup**:
   ```bash
   cp /root/settings.vue.backup /root/anwalts-frontend-new/pages/settings.vue
   ```

2. **Rebuild and Restart**:
   ```bash
   cd /root/anwalts-frontend-new
   npm run build
   docker build -t anwalts-frontend .
   docker stop anwalts_frontend
   docker rm anwalts_frontend
   docker-compose up -d frontend
   ```

3. **Document Issue**:
   - Record what went wrong
   - Update OpenSpec proposal with findings
   - Plan alternative approach

## Open Questions

### Q1: Should we create useSupabaseSession() wrapper for consistency?

**Status**: To be decided after checking all usages

**Options**:
- A) Create wrapper now for future-proofing
- B) Only create if multiple files need it
- C) Never create, standardize on useSupabaseAuth()

**Recommendation**: Option B - Create only if search reveals multiple usages

### Q2: Should we use explicit Authorization header or rely on cookies?

**Status**: Decided - Use explicit Authorization header

**Rationale**: Better for debugging, more explicit, follows REST conventions

### Q3: Should we add automatic token refresh?

**Status**: Deferred to future enhancement

**Rationale**: 
- Current fix focuses on authentication format issue
- Token refresh is separate feature
- Retry button provides manual workaround
- Can be added in phase 2 after core fix is stable

### Q4: Should backend accept both Supabase and custom JWT tokens?

**Status**: Deferred - Out of scope

**Rationale**:
- Would require backend changes and testing
- Risk of breaking existing authentication
- Current architecture uses custom JWTs consistently
- Supabase tokens are for OAuth flow only

## Success Metrics

### Primary Metrics

1. **Zero 403 Errors** - No Forbidden responses when admin loads settings page
2. **Zero 401 Errors** - No Invalid token format errors in backend logs
3. **200 OK Responses** - All `/api/admin/settings` requests succeed
4. **Data Displays** - Statistics, settings, and activity all render correctly

### Secondary Metrics

1. **Error Message Clarity** - Users understand what went wrong and how to fix
2. **Debug Information** - Developers can diagnose issues from error panel
3. **Consistent Auth Flow** - Settings page uses same auth pattern as other pages
4. **Documentation Completeness** - Future developers understand token flow

### Validation Checklist

- [ ] Admin user can access `/dashboard/settings` without errors
- [ ] System statistics show correct counts (13 users, 1 email, etc.)
- [ ] Organization settings form loads with data
- [ ] Recent activity displays analytics events
- [ ] Browser console shows no authentication errors
- [ ] Backend logs show "Admin access granted" messages
- [ ] Network tab shows 200 OK responses
- [ ] Authorization header contains valid JWT token
- [ ] Error messages are specific and helpful (401, 403, 500)
- [ ] Retry button successfully reloads settings
- [ ] Other protected pages still work (documents, templates, email)
- [ ] Non-admin users see "Access Denied" message
