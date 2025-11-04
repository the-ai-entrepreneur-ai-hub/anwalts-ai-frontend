## Why
- Admin dashboard shows critical errors: "Overview could not be loaded", "Users could not be loaded", "Settings could not be loaded"
- The `/api/admin/settings` endpoint queries database tables that don't exist in production
- Missing tables: `organization_settings`, `analytics_events`, `api_tokens`, `webhooks`
- Admin functionality is completely broken without these tables
- Users cannot access any admin features despite authentication working

## What Changes
- Create complete database schema for all admin-related tables
- Add `organization_settings` table with default configuration
- Add `analytics_events` table for system activity tracking
- Add `api_tokens` table for API key management
- Add `webhooks` table for webhook management  
- Add indexes for query performance
- Seed default organization settings on table creation
- Ensure endpoints handle missing tables gracefully (already implemented)

**CRITICAL**: This fix is required for admin dashboard to function at all.

## Impact
- **Affected specs**: `admin-database` (new spec for admin database schema)
- **Affected code**:
  - New file: `/root/migrations/create_admin_tables.sql` - Complete schema
  - Backend already has graceful error handling (lines 5702-5757 in backend-main.py)
- **Database impact**: Creates 4 new tables with proper indexes
- **User impact**: Admin dashboard will start working immediately after migration
- **No breaking changes**: Only adds new tables, doesn't modify existing ones
