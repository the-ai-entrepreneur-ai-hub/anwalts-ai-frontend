# Dynamize Dashboard Data

## Change ID
`dynamize-dashboard-data`

## Why

The dashboard page currently displays hard-coded, static values that do not reflect the actual logged-in user's data. This creates a misleading user experience where:
- Stats show fictional numbers (42 cases, 156 documents, 389 emails) regardless of the user
- Documents list displays dummy data with fake names ("Schmidt", "Kronos", "M?ller")
- Deadlines are static and don't reflect real upcoming tasks
- Templates are hard-coded rather than pulled from the database
- Recent activity shows placeholder entries that never change
- Welcome message is generic instead of personalized with the user's name
- Dates are hard-coded to specific 2025 dates instead of being relative to today

This violates the fundamental principle that a dashboard should provide personalized, real-time insights specific to each user. Users cannot trust the information they see, and the dashboard fails to serve its primary purpose of providing an overview of their actual work.

## What Changes

This proposal removes ALL hard-coded values from the dashboard and replaces them with dynamic, user-specific data from the database. Specifically:

### Frontend Changes
1. **Remove all hard-coded data** from `/pages/dashboard.vue`:
   - Stats cards (lines 65, 78, 91, 104)
   - Dummy documents array (lines 592-615)
   - Static deadlines (lines 174-190)
   - Static templates (lines 207-289)
   - Static recent activity (lines 324-353)
   - Hard-coded dates in JavaScript (lines 520-525, 582-588)

2. **Integrate dashboard store** (`/stores/dashboard.ts`):
   - Use existing `useDashboardStore` to fetch data
   - Connect reactive data to UI components
   - Handle loading and error states properly

3. **Personalize welcome message**:
   - Use `usePortalUser()` to get current user's name
   - Display "Willkommen zur?ck, [Name]" instead of generic greeting

4. **Implement real-time date calculations**:
   - Replace hard-coded dates with `new Date()` and relative date logic
   - Calculate "today", "tomorrow", "in X days" dynamically

### Backend Changes

1. **Expand `/server/api/dashboard/summary.get.ts`** to return:
   - **Stats**: Real counts from database tables (cases, documents, emails)
   - **Recent documents**: Query user's 3 most recent documents with actual progress
   - **Upcoming deadlines**: Query user's next 3 deadlines from database
   - **Recent activity**: Query user's latest 3 activities (emails, uploads, calls)
   - **User info**: Full name for personalized greeting

2. **Create new API endpoints** as needed:
   - `/server/api/dashboard/documents.get.ts` - Get user's recent documents
   - `/server/api/dashboard/deadlines.get.ts` - Get user's upcoming deadlines  
   - `/server/api/dashboard/activity.get.ts` - Get user's recent activity
   - `/server/api/dashboard/continue.get.ts` - Get "continue working on" suggestion

3. **Database queries** (in `database.py`):
   - `get_user_dashboard_stats(user_id)` - Count cases, documents, emails
   - `get_user_recent_documents(user_id, limit=3)` - Get latest docs with metadata
   - `get_user_upcoming_deadlines(user_id, limit=3)` - Get next deadlines sorted by date
   - `get_user_recent_activity(user_id, limit=3)` - Get latest events (emails, calls, uploads)
   - `get_user_continue_suggestion(user_id)` - Get in-progress document with highest completion

### Database Schema Changes

**New Tables** (if not already present):
- `cases` - Store user cases with metadata
- `deadlines` - Store task deadlines with due dates and descriptions
- `activities` - Store activity log (email, upload, call events)

**Existing Tables to Query**:
- `documents` - Already exists, add `user_id`, `progress`, `status` columns if missing
- `templates` - Already exists, continue using for template list
- `users` - Already exists, use for user name

### Templates Section

The templates section will remain **mostly static** for now, as templates are typically organization-wide resources rather than user-specific. However, we will:
- Fetch templates from the database via existing `/api/templates` endpoint
- Display real template metadata (last update dates, version numbers)
- Mark templates as "favorites" per user (if that feature is added later)

## Impact

### Affected Files
**Frontend:**
- `/anwalts-frontend-new/pages/dashboard.vue` - Major refactoring to use dynamic data
- `/anwalts-frontend-new/stores/dashboard.ts` - Already exists, will be properly integrated
- `/anwalts-frontend-new/composables/usePortalUser.ts` - Already exists, will be used for personalization

**Backend:**
- `/server/api/dashboard/summary.get.ts` - Expand to return comprehensive dashboard data
- `/server/api/dashboard/documents.get.ts` - NEW: Recent documents endpoint
- `/server/api/dashboard/deadlines.get.ts` - NEW: Upcoming deadlines endpoint
- `/server/api/dashboard/activity.get.ts` - NEW: Recent activity endpoint
- `/server/api/dashboard/continue.get.ts` - NEW: Continue suggestion endpoint
- `/database.py` - Add dashboard-specific query methods
- `/models.py` - Add response models for dashboard data structures

**Database:**
- `migrations/create_dashboard_tables.sql` - NEW: Create cases, deadlines, activities tables if missing

### User Experience Impact
- **Positive**: Users see their actual data, personalized experience, trustworthy metrics
- **Positive**: Dashboard becomes useful for real work instead of demo placeholder
- **Positive**: Users can make decisions based on real-time information
- **Neutral**: No breaking changes to existing functionality
- **Risk**: If database is empty for a user, dashboard may look sparse (mitigated by empty states)

### Performance Impact
- Additional database queries per dashboard load (~5-7 queries)
- Queries are simple and indexed, expected response time <100ms total
- Frontend already has loading skeletons in place
- Can add caching later if needed (not required for MVP)

### Admin Users
This change applies to all users including admins. Admins `angelageneralao.1997@gmail.com` and `test.reg.e2e+20251026@anwalts.ai` will see their personal dashboards, not system-wide stats.

If system-wide admin analytics are needed, that should be a separate admin dashboard (not this proposal's scope).

## Compatibility

- **No breaking changes**: Dashboard page continues to render, just with real data instead of fake data
- **Backward compatible**: Works with existing auth system and database schema
- **Graceful degradation**: Empty states already exist in UI for missing data
- **Data migration**: No migration needed; hard-coded data is simply replaced with queries

## Dependencies

- Requires database tables: `documents`, `users` (already exist)
- Requires auth system: `usePortalUser()` composable (already exists)
- Requires API layer: Nuxt server routes (already set up)
- May create new tables: `cases`, `deadlines`, `activities` (as needed)

## Success Criteria

1. ? No hard-coded numbers remain in dashboard UI code
2. ? Dashboard displays different data for different logged-in users
3. ? Welcome message shows user's actual name
4. ? Dates are calculated relative to current date/time
5. ? Empty states gracefully handle users with no data
6. ? Dashboard loads in <2 seconds with real data
7. ? All sections (stats, docs, deadlines, activity) show user-specific data

## Testing Plan

1. **Manual Testing**:
   - Log in as Angela (admin) - see Angela's data
   - Log in as test user - see test user's data
   - Verify stats match actual database counts
   - Verify documents match user's recent documents
   - Verify dates are calculated correctly relative to today

2. **Edge Cases**:
   - New user with empty dashboard - verify empty states show
   - User with 1 document - verify no errors
   - User with 100+ documents - verify pagination/limiting works

3. **Performance Testing**:
   - Measure dashboard load time with real queries
   - Ensure no N+1 query problems
   - Verify acceptable response times (<2s)

## Rollout Plan

1. **Phase 1**: Backend API expansion (new endpoints, database methods)
2. **Phase 2**: Frontend integration (connect dashboard to APIs)
3. **Phase 3**: Testing with real users (Angela and test accounts)
4. **Phase 4**: Deploy to production
5. **Phase 5**: Monitor for errors and performance issues

## Notes

- This is a **pure refactoring** - no new features added, just replacing fake data with real data
- The UI/UX remains identical - only the data source changes
- This aligns with user expectations that a dashboard shows "their" data
- This is a prerequisite for future dashboard enhancements (analytics, insights, recommendations)
