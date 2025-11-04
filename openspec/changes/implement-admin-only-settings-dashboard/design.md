## Context
The Anwalts AI platform currently lacks a functional administrative interface for system management. The settings page at `/dashboard/settings` shows only placeholder text. Administrators need access to real-time system metrics, organization configuration controls, and user management capabilities. This design establishes a secure, admin-only settings dashboard with multi-layer authorization.

### Background
- **Current State**: Settings page is non-functional placeholder
- **Stakeholders**: System administrators (2 authorized users initially)
- **Constraints**:
  - Must integrate with existing Supabase authentication
  - Must work within FastAPI backend and Nuxt frontend architecture
  - Admin authorization must be enforceable at multiple layers (backend middleware, API endpoints, frontend routing)
  - Must display real data from PostgreSQL database

## Goals / Non-Goals

### Goals
- Provide admin-only access to system statistics and organizational settings
- Implement secure authorization using hardcoded admin list + environment variables
- Display real-time data from production database
- Enable organization settings persistence and management
- Create extensible foundation for future admin features (user management, API tokens, webhooks)

### Non-Goals
- User-level settings (personal preferences, notifications for non-admins)
- Role-based access control (RBAC) beyond simple admin/non-admin distinction
- Audit logging of admin actions (defer to future change)
- Multi-tenant organization support (single organization assumed)
- Real-time WebSocket updates (polling/manual refresh acceptable)

## Decisions

### Decision 1: Three-Layer Authorization
**What**: Enforce admin access at three layers: backend middleware, API endpoint, and frontend composable.

**Why**:
- **Defense in depth**: Multiple security layers prevent bypass
- **Backend middleware** (lines 606-617): Blocks all `/api/admin/*` and `/api/settings/*` requests from non-admins
- **API endpoint checks**: Each endpoint calls `_assert_admin(current_user)` for explicit verification
- **Frontend guard**: `useAuth()` composable prevents UI rendering and redirects non-admins

**Alternatives considered**:
- Single-layer backend-only authorization: Less secure, allows UI leakage
- JWT claims-based roles: Requires Supabase JWT customization, added complexity
- Database-only role checks: Higher latency, doesn't prevent unauthorized API exploration

**Trade-off**: More code duplication across layers, but significantly improved security posture.

### Decision 2: Hardcoded Admin List in Code
**What**: Maintain `AUTHORIZED_ADMINS` set directly in `backend-main.py` at line ~1201, merged with environment variable list.

**Why**:
- **Fail-safe**: Guarantees access even if environment variables are misconfigured
- **Code review visibility**: Admin changes go through version control
- **No external dependencies**: Doesn't require database schema changes for bootstrap
- **Environment override**: `ADMIN_EMAILS` env var provides additional flexibility

**Alternatives considered**:
- Environment variables only: Risk of lockout if misconfigured
- Database-only admin list: Chicken-egg problem during initial setup
- OAuth provider groups: Requires Google Workspace or external IdP integration

**Trade-off**: Requires code deployment to change admin list, but provides guaranteed access.

### Decision 3: Single Organization Settings Model
**What**: Use `organization_settings` table with single row for global configuration, updated via `PUT /api/admin/settings/organization`.

**Why**:
- **Simplicity**: System currently supports single organization (no multi-tenancy)
- **Fast reads**: Latest settings retrieved with `ORDER BY updated_at DESC LIMIT 1`
- **Audit trail**: Keep historical rows for `updated_at` and `updated_by` tracking
- **Schema flexibility**: JSONB columns can store additional settings without migrations

**Alternatives considered**:
- Key-value settings store: More flexible but requires complex querying
- Environment variables for all settings: Requires container restart, poor UX
- Multi-tenant organization table: Over-engineering for current single-org use case

**Trade-off**: Single-row approach may need refactoring for multi-tenancy, but meets current needs.

### Decision 4: Nuxt Composable for Frontend Auth
**What**: Create `composables/useAuth.ts` with `isAdmin` computed property and `requireAdmin()` guard.

**Why**:
- **Nuxt pattern**: Follows Vue 3 Composition API and Nuxt auto-import conventions
- **Reactivity**: Computed property automatically updates on auth state changes
- **Reusability**: Composable can be used across multiple admin pages
- **Type safety**: TypeScript provides compile-time checking

**Alternatives considered**:
- Middleware-only approach: Less flexible, harder to use in components
- Pinia store: Unnecessary state management overhead for simple auth check
- Plugin-based: Over-complicates simple email comparison logic

**Trade-off**: Must keep admin email list synchronized between backend and frontend code.

### Decision 5: Comprehensive Dashboard Page Structure
**What**: Single-page dashboard with statistics cards, settings form, and navigation links to sub-sections.

**Why**:
- **Information density**: Admins see overview and key controls on one screen
- **Progressive disclosure**: Links to detailed management pages (users, API, webhooks) keep main page uncluttered
- **Familiar pattern**: Matches common admin dashboard UX (stats at top, sections below)
- **Mobile responsive**: Grid layout adapts to smaller screens using Tailwind breakpoints

**Alternatives considered**:
- Tabbed interface: More navigation clicks, slower workflow
- Multi-page wizard: Inappropriate for settings management
- Sidebar navigation: Requires layout changes to PortalShell component

**Trade-off**: Large single file (~300 lines), but maintains cohesive user experience.

## Data Flow

### Admin Access Flow
```
1. User authenticates via Supabase → JWT issued
2. Frontend checks email in useAuth() composable → isAdmin computed
3. If admin: Page renders, calls GET /api/admin/settings
4. Backend middleware verifies JWT → extracts user
5. Endpoint calls _assert_admin(user) → checks email/domain
6. If admin: Query database → return statistics + settings
7. Frontend hydrates UI with data → display dashboard
8. If non-admin: Show "Access Denied" message
```

### Settings Update Flow
```
1. Admin modifies form → clicks "Save Changes"
2. Frontend calls PUT /api/admin/settings/organization with new values
3. Backend validates allowed fields → builds dynamic UPDATE query
4. Execute UPDATE with parameterized values → record updated_by/updated_at
5. Return updated settings to frontend
6. Show success notification → reload page or refetch data
```

### Security Checks at Each Layer
| Layer | Check | Failure Action |
|-------|-------|----------------|
| Frontend Route | `isAdmin` in useAuth | Redirect to /dashboard + error message |
| Backend Middleware | Email in admin lists | Return 403 Forbidden |
| API Endpoint | `_assert_admin(user)` | Raise HTTPException(403) |
| Database | `role = 'admin'` | (Optional validation) |

## Database Schema Impact

### New/Modified Tables

**`organization_settings`** (existing, used):
- `id` - Primary key
- `language` - VARCHAR (de, en)
- `timezone` - VARCHAR (Europe/Berlin, etc.)
- `require_two_factor` - BOOLEAN
- `enable_sso` - BOOLEAN
- `password_min_length` - INTEGER
- `password_require_special` - BOOLEAN
- `password_require_numbers` - BOOLEAN
- `email_notifications` - BOOLEAN
- `browser_notifications` - BOOLEAN
- `ai_updates` - BOOLEAN
- `ai_model` - VARCHAR
- `ai_creativity` - INTEGER (0-100)
- `auto_save` - BOOLEAN
- `updated_at` - TIMESTAMP
- `updated_by` - UUID (foreign key to users.id)

**`users`** (modified):
- Ensure `role` column exists (VARCHAR: 'admin', 'user', 'assistant')
- Update rows: Set `role = 'admin'` where email in authorized list

**Queries Required**:
```sql
-- Set admin roles
UPDATE users 
SET role = 'admin' 
WHERE LOWER(email) IN (
  'test.reg.e2e+20251026@anwalts.ai',
  'angelageneralao.1997@gmail.com'
);

-- Statistics query (in endpoint)
SELECT 
  (SELECT COUNT(*) FROM users WHERE is_active = true) as active_users,
  (SELECT COUNT(*) FROM email_accounts WHERE revoked_at IS NULL) as connected_emails,
  (SELECT COUNT(*) FROM documents) as total_documents,
  (SELECT COUNT(*) FROM templates) as total_templates,
  (SELECT COUNT(*) FROM api_tokens WHERE revoked_at IS NULL) as active_tokens,
  (SELECT COUNT(*) FROM webhooks WHERE is_active = true) as active_webhooks;

-- Recent activity (assumes analytics_events table exists)
SELECT 
  event_type, 
  COUNT(*) as count,
  MAX(created_at) as last_occurrence
FROM analytics_events
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY event_type
ORDER BY count DESC
LIMIT 10;
```

## API Contract

### GET /api/admin/settings

**Request**:
```
GET /api/admin/settings
Authorization: Bearer <jwt_token>
```

**Response (200 OK)**:
```json
{
  "organization": {
    "id": "...",
    "language": "de",
    "timezone": "Europe/Berlin",
    "require_two_factor": false,
    "enable_sso": false,
    "password_min_length": 8,
    "password_require_special": true,
    "password_require_numbers": true,
    "email_notifications": true,
    "browser_notifications": false,
    "ai_updates": true,
    "ai_model": "qwen_legal_q4_k_m",
    "ai_creativity": 70,
    "auto_save": true,
    "updated_at": "2025-11-02T10:30:00Z",
    "updated_by": "..."
  },
  "statistics": {
    "active_users": 42,
    "connected_emails": 18,
    "total_documents": 1337,
    "total_templates": 56,
    "active_tokens": 3,
    "active_webhooks": 2
  },
  "recent_activity": [
    {
      "event_type": "document_generated",
      "count": 145,
      "last_occurrence": "2025-11-02T09:15:00Z"
    }
  ],
  "current_user": {
    "id": "...",
    "email": "test.reg.e2e+20251026@anwalts.ai",
    "role": "admin"
  }
}
```

**Response (403 Forbidden)**:
```json
{
  "detail": "Admin access required"
}
```

### PUT /api/admin/settings/organization

**Request**:
```
PUT /api/admin/settings/organization
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "language": "en",
  "timezone": "Europe/Vienna",
  "require_two_factor": true,
  "ai_creativity": 80
}
```

**Response (200 OK)**:
```json
{
  "id": "...",
  "language": "en",
  "timezone": "Europe/Vienna",
  "require_two_factor": true,
  "ai_creativity": 80,
  "updated_at": "2025-11-02T10:45:00Z",
  "updated_by": "..."
}
```

**Response (400 Bad Request)**:
```json
{
  "detail": "No valid fields to update"
}
```

**Response (403 Forbidden)**:
```json
{
  "detail": "Admin access required"
}
```

## Frontend Component Structure

### useAuth Composable
```typescript
// composables/useAuth.ts
export const useAuth = () => {
  const user = useSupabaseUser()
  
  const isAdmin = computed(() => {
    const email = user.value?.email?.toLowerCase()
    const adminEmails = [
      'test.reg.e2e+20251026@anwalts.ai',
      'angelageneralao.1997@gmail.com'
    ]
    return email && adminEmails.includes(email)
  })
  
  const requireAdmin = () => {
    if (!isAdmin.value) {
      navigateTo('/dashboard')
      throw new Error('Admin access required')
    }
  }
  
  return { isAdmin, requireAdmin, user }
}
```

### Settings Page Structure
```
pages/dashboard/settings.vue
├── PortalShell (layout wrapper)
│   ├── Header (with back link + admin badge)
│   └── Main Content
│       ├── Access Denied (if !isAdmin)
│       ├── Loading State (if loading)
│       ├── Error Display (if error)
│       └── Admin Dashboard (if isAdmin && !loading && !error)
│           ├── System Statistics Grid (6 cards)
│           ├── Organization Settings Card
│           │   ├── General Settings (language, timezone)
│           │   ├── Security Settings (2FA, SSO, passwords)
│           │   ├── Notification Settings (email, browser, AI updates)
│           │   ├── AI Configuration (model, creativity, auto-save)
│           │   └── Save Button
│           ├── User Management Card (link to subpage)
│           ├── API & Webhooks Cards (links to subpages)
│           └── Recent Activity Table
```

## Risks / Trade-offs

### Risk: Admin Lockout
**Description**: If both hardcoded list and environment variables are misconfigured, no one can access admin functions.

**Mitigation**:
- Hardcoded list in code provides fail-safe
- Database has `role` column as backup verification
- Document admin credentials in secure location (password manager, ops docs)
- Emergency access via direct database role update

### Risk: Admin Email List Desynchronization
**Description**: Frontend and backend admin lists could diverge if updated independently.

**Mitigation**:
- Document in code comments that both lists must match
- Consider future refactoring to single source of truth (environment variable read by both)
- Add integration test that verifies frontend and backend lists match

### Risk: Non-Existent Database Tables
**Description**: Queries assume `organization_settings`, `analytics_events`, and other tables exist with expected schema.

**Mitigation**:
- Add defensive checks: `if not row: return default_values`
- Gracefully handle missing tables with empty statistics
- Document required schema in migration script
- Test on production database structure before deployment

### Risk: Performance Degradation
**Description**: Statistics query with multiple subqueries could slow down with large datasets.

**Mitigation**:
- Use COUNT queries which are optimized by PostgreSQL
- Add database indexes on frequently queried columns (users.is_active, documents.created_at, etc.)
- Consider caching statistics for 1-5 minutes using Redis
- Future: Pre-compute statistics in background job

### Trade-off: Single Organization Assumption
**Description**: Design assumes single organization; multi-tenancy would require significant refactoring.

**Impact**: Acceptable for current scope. If multi-tenancy needed:
- Add `organization_id` to all tables
- Update queries to filter by organization
- Add organization selector to admin UI
- Modify authorization to check org membership

## Migration Plan

### Step 1: Backend Changes
1. Update `backend-main.py` line ~1201: Add `AUTHORIZED_ADMINS` set
2. Verify admin middleware at lines 606-617 is active
3. Add `GET /api/admin/settings` endpoint at line ~5700
4. Add `PUT /api/admin/settings/organization` endpoint
5. Verify `_assert_admin()` helper exists or create it

### Step 2: Database Updates
1. Run SQL update to set admin roles:
   ```bash
   docker exec -i anwalts_postgres psql -U anwalts_user -d anwalts_ai <<EOF
   UPDATE users SET role = 'admin' 
   WHERE LOWER(email) IN (
     'test.reg.e2e+20251026@anwalts.ai',
     'angelageneralao.1997@gmail.com'
   );
   EOF
   ```
2. Verify organization_settings table exists or create it
3. Add indexes if needed for performance

### Step 3: Frontend Changes
1. Create `composables/useAuth.ts` with admin checks
2. Replace `pages/dashboard/settings.vue` with new dashboard
3. Build frontend: `cd anwalts-frontend-new && npm run build`
4. Test locally before deployment

### Step 4: Deployment
1. Deploy backend changes: `docker restart anwalts_backend`
2. Deploy frontend changes: `docker restart anwalts_frontend`
3. Verify nginx routes correctly: `docker exec anwalts_nginx nginx -s reload`

### Step 5: Validation
1. Login as admin user (test.reg.e2e+20251026@anwalts.ai)
2. Navigate to `/dashboard/settings`
3. Verify statistics display correctly
4. Test settings save functionality
5. Login as non-admin user
6. Verify "Access Denied" message appears

### Rollback Plan
If issues occur:
1. Revert `backend-main.py` changes: `git revert <commit>`
2. Restore previous `settings.vue` from git history
3. Remove `useAuth.ts` composable
4. Restart containers: `docker-compose restart`
5. Database changes (role updates) can remain; they don't break functionality

## Open Questions

1. **Should regular users have their own settings page?**
   - Current design makes settings admin-only
   - Consider separate `/dashboard/profile` for user preferences in future

2. **What analytics_events schema is expected?**
   - Assumed columns: event_type, created_at, count
   - Need to verify actual table structure

3. **Should admin role changes trigger notifications?**
   - Consider email notification when user promoted to admin
   - Audit log for role changes (future enhancement)

4. **How should organization settings affect runtime behavior?**
   - Current design only stores settings
   - Future: Auth service should check require_two_factor, password policies, etc.

5. **Should admin access be audit logged?**
   - Not included in current scope
   - Recommend future enhancement to track admin actions with timestamps

## Future Enhancements

1. **User Management Subpage**: Implement `/dashboard/settings/users` with full CRUD
2. **API Token Management**: Implement `/dashboard/settings/api` with token lifecycle
3. **Webhook Management**: Implement `/dashboard/settings/webhooks` with CRUD + testing
4. **Audit Logging**: Track all admin actions in database table
5. **Role-Based Access Control**: Expand beyond binary admin/non-admin
6. **Real-Time Updates**: WebSocket for live statistics updates
7. **Settings History**: Show previous organization settings with diff view
8. **Bulk User Operations**: Import/export users, bulk role changes
9. **Custom Dashboards**: Allow admins to configure which statistics to display
10. **Performance Analytics**: Add page load times, API latency percentiles
