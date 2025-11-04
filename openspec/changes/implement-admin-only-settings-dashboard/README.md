# Admin-Only Settings Dashboard Implementation

**Change ID**: `implement-admin-only-settings-dashboard`  
**Status**: Awaiting approval  
**Created**: 2025-11-02

## Overview
Transform the placeholder settings page into a fully functional admin-only dashboard with real system data, accessible only by authorized administrators.

## Authorized Admin Emails
- test.reg.e2e+20251026@anwalts.ai
- angelageneralao.1997@gmail.com

## Quick Links
- [Proposal](./proposal.md) - Why this change is needed and what will change
- [Design](./design.md) - Technical decisions, architecture, and trade-offs
- [Tasks](./tasks.md) - Step-by-step implementation checklist (45 tasks)
- [Spec](./specs/settings-admin/spec.md) - Detailed requirements with scenarios

## Key Features
1. **Three-Layer Authorization**: Admin access enforced at backend middleware, API endpoints, and frontend
2. **Real-Time Statistics**: Display active users, connected emails, documents, templates, API tokens, and webhooks
3. **Organization Settings Management**: Configure language, timezone, security, notifications, and AI parameters
4. **Recent Activity Log**: Show last 7 days of system events grouped by type
5. **Access Control**: Non-admins see "Access Denied" message

## Implementation Highlights

### Backend Changes
- **File**: `/root/backend-main.py`
- **Lines**: ~1201 (admin config), ~606-617 (middleware), ~5700 (new endpoints)
- **Endpoints**:
  - `GET /api/admin/settings` - Comprehensive settings data
  - `PUT /api/admin/settings/organization` - Update organization settings

### Frontend Changes
- **New File**: `/root/anwalts-frontend-new/composables/useAuth.ts`
- **Replaced File**: `/root/anwalts-frontend-new/pages/dashboard/settings.vue`
- **Features**: Admin composable, statistics grid, settings form, activity table

### Database Changes
- **Table**: `users` - Set `role='admin'` for authorized emails
- **Table**: `organization_settings` - Store and retrieve organization preferences
- **Queries**: Statistics aggregation, recent activity from `analytics_events`

## Security Architecture

### Authorization Layers
1. **Backend Middleware** (lines 606-617): Blocks all `/api/admin/*` requests from non-admins
2. **API Endpoint**: Each endpoint calls `_assert_admin(current_user)` for explicit verification  
3. **Frontend Guard**: `useAuth()` composable prevents UI rendering and redirects non-admins

### Admin Identification
```python
# Backend (backend-main.py ~1201)
AUTHORIZED_ADMINS = {
    "test.reg.e2e+20251026@anwalts.ai",
    "angelageneralao.1997@gmail.com"
}
admin_emails = admin_emails.union(AUTHORIZED_ADMINS)
```

```typescript
// Frontend (composables/useAuth.ts)
const isAdmin = computed(() => {
  const email = user.value?.email?.toLowerCase()
  const adminEmails = [
    'test.reg.e2e+20251026@anwalts.ai',
    'angelageneralao.1997@gmail.com'
  ]
  return email && adminEmails.includes(email)
})
```

## Task Summary
- **45 total tasks** across 8 sections
- **Backend Admin Authorization** (4 tasks)
- **Admin Settings API Endpoints** (9 tasks)
- **Database Admin Role Management** (4 tasks)
- **Frontend Admin Composable** (5 tasks)
- **Settings Page Dashboard UI** (12 tasks)
- **Environment & Deployment Configuration** (4 tasks)
- **Testing & Validation** (10 tasks)
- **Documentation & Security Review** (5 tasks)

## Testing Plan

### Access Control Tests
1. Login as admin user → should see full dashboard
2. Login as regular user → should see "Access Denied"
3. API call with admin token → should return 200 OK
4. API call with non-admin token → should return 403 Forbidden

### Data Display Tests
1. Verify statistics show real database counts
2. Verify organization settings load correctly
3. Verify recent activity displays events
4. Verify settings persist after save

### Security Tests
1. Attempt to bypass frontend guard via direct URL
2. Attempt to call admin API without admin privileges
3. Verify JWT validation on all endpoints
4. Verify middleware blocks unauthorized requests

## Deployment Steps

1. **Backend**: Update `backend-main.py` with admin config and endpoints
2. **Database**: Run SQL to set admin roles for authorized emails
3. **Frontend**: Create `useAuth.ts` and replace `settings.vue`
4. **Environment**: Add `ADMIN_EMAILS` to `.env` or `docker-compose.yml`
5. **Deploy**: Restart backend and frontend containers
6. **Test**: Verify admin access works, non-admin denied

## Related Changes
- **Extends**: `update-settings-live-data` (13/16 tasks complete)
- **Adds**: Specific admin authorization requirements not in original change

## Breaking Changes
⚠️ **BREAKING**: This change restricts `/dashboard/settings` to admin-only access. Regular users will no longer have any settings page access. Consider implementing separate user profile/preferences page in future.

## Validation
✅ OpenSpec validation passed with `--strict` flag

## Next Steps
1. Review this proposal for accuracy and completeness
2. Get stakeholder approval
3. Begin implementation following [tasks.md](./tasks.md) checklist
4. Mark tasks complete as implementation progresses
5. After deployment, archive this change using `openspec archive implement-admin-only-settings-dashboard`
