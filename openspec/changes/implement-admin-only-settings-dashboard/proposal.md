## Why
- The settings page at `/dashboard/settings` currently shows only placeholder text with no functional admin controls
- System administrators need secure, authenticated access to view real-time system statistics, manage organization settings, and control user access
- Admin authorization is currently scattered across environment variables without a unified access control strategy
- Security requires that only explicitly authorized administrators can access sensitive system data and administrative functions

## What Changes
- **Backend Admin Authorization**: Consolidate admin email verification in `backend-main.py` with hardcoded authorized admins plus environment variable support
- **Admin-Only API Endpoints**: Create `/api/admin/settings` and `/api/admin/settings/organization` endpoints protected by admin middleware
- **Frontend Admin Guard**: Implement `useAuth()` composable with `isAdmin` computed property and `requireAdmin()` guard function
- **Settings Dashboard UI**: Replace placeholder settings page with comprehensive admin dashboard displaying:
  - Real-time system statistics (users, emails, documents, templates, tokens, webhooks)
  - Organization settings form (language, timezone, security, notifications, AI configuration)
  - Links to user management, API tokens, and webhooks subpages
  - Recent system activity log (last 7 days of analytics events)
- **Database Admin Roles**: Ensure `users.role` column is set to 'admin' for authorized email addresses
- **Access Denial UI**: Non-admin users see "Access Denied" message when attempting to access settings

**BREAKING**: This change restricts `/dashboard/settings` to admin-only access. Regular users will no longer have any settings page access.

## Impact
- **Affected specs**: `settings-admin` (admin authorization, settings API, admin dashboard UI)
- **Affected code**:
  - `/root/backend-main.py` - Lines ~1200 (admin config), ~606-617 (admin middleware), ~5700 (new endpoints)
  - `/root/anwalts-frontend-new/pages/dashboard/settings.vue` - Complete rewrite
  - `/root/anwalts-frontend-new/composables/useAuth.ts` - New file
  - `/root/database.py` - New admin role management methods
  - Database: `users` table role updates for authorized admins
- **Security impact**: Introduces strict admin-only access control for sensitive system data
- **User impact**: Non-admin users lose access to settings page (no user-level settings currently implemented)
- **Related changes**: Extends `update-settings-live-data` with specific admin authorization requirements
