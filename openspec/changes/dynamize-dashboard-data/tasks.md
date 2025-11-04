# Implementation Tasks

## 1. Database Schema & Queries
- [x] 1.1 Review existing `documents` table schema - add `user_id`, `progress`, `status` columns if missing
- [x] 1.2 Create `cases` table with columns: `id`, `user_id`, `title`, `case_number`, `status`, `created_at`, `updated_at`
- [x] 1.3 Create `deadlines` table with columns: `id`, `user_id`, `title`, `description`, `due_date`, `priority`, `related_case_id`, `completed`, `created_at`
- [x] 1.4 Create `activities` table with columns: `id`, `user_id`, `activity_type`, `title`, `description`, `related_entity_type`, `related_entity_id`, `status`, `created_at`
- [x] 1.5 Write migration script `migrations/create_dashboard_tables.sql` with CREATE TABLE statements
- [x] 1.6 Add index on `user_id` for all dashboard tables for query performance
- [x] 1.7 Add dashboard query methods to `database.py`:
  - [x] 1.7.1 `get_user_dashboard_stats(user_id: uuid.UUID) -> Dict` - Count cases, documents, emails
  - [x] 1.7.2 `get_user_recent_documents(user_id: uuid.UUID, limit: int = 3) -> List[Dict]`
  - [x] 1.7.3 `get_user_upcoming_deadlines(user_id: uuid.UUID, limit: int = 3) -> List[Dict]`
  - [x] 1.7.4 `get_user_recent_activity(user_id: uuid.UUID, limit: int = 3) -> List[Dict]`
  - [x] 1.7.5 `get_user_continue_suggestion(user_id: uuid.UUID) -> Optional[Dict]`
- [x] 1.8 Test database queries in isolation with sample data

## 2. Backend API Models
- [x] 2.1 Add Pydantic models to `models.py`:
  - [x] 2.1.1 `DashboardStats` - Stats summary model
  - [x] 2.1.2 `DashboardDocument` - Recent document model
  - [x] 2.1.3 `DashboardDeadline` - Deadline model
  - [x] 2.1.4 `DashboardActivity` - Activity model
  - [x] 2.1.5 `DashboardContinueSuggestion` - Continue working model
  - [x] 2.1.6 `DashboardSummaryResponse` - Complete dashboard response
- [x] 2.2 Document model fields with descriptions and examples

## 3. Backend API Endpoints
- [x] 3.1 Expand `/server/api/dashboard/summary.get.ts`:
  - [x] 3.1.1 Get user ID from authentication (session/token)
  - [x] 3.1.2 Call Supabase queries for dashboard stats
  - [x] 3.1.3 Query recent documents from database
  - [x] 3.1.4 Query upcoming deadlines from database
  - [x] 3.1.5 Query recent activity from database
  - [x] 3.1.6 Query continue suggestion from database
  - [x] 3.1.7 Get user name from `useSupabaseServer()` or database
  - [x] 3.1.8 Return comprehensive DashboardSummaryResponse
  - [x] 3.1.9 Handle errors gracefully (return empty arrays if queries fail)
- [ ] 3.2 Create `/server/api/dashboard/documents.get.ts` (optional, if needed separately)
- [ ] 3.3 Create `/server/api/dashboard/deadlines.get.ts` (optional, if needed separately)
- [ ] 3.4 Create `/server/api/dashboard/activity.get.ts` (optional, if needed separately)
- [ ] 3.5 Create `/server/api/dashboard/continue.get.ts` (optional, if needed separately)
- [ ] 3.6 Add error handling and logging to all endpoints
- [ ] 3.7 Test endpoints with Postman/curl using valid auth tokens

## 4. Frontend Store Integration
- [ ] 4.1 Update `/stores/dashboard.ts`:
  - [ ] 4.1.1 Add `documents` ref for recent documents
  - [ ] 4.1.2 Add `deadlines` ref for upcoming deadlines
  - [ ] 4.1.3 Add `activity` ref for recent activity
  - [ ] 4.1.4 Add `continueSuggestion` ref for continue working suggestion
  - [ ] 4.1.5 Add `userName` ref for personalized greeting
  - [ ] 4.1.6 Update `fetchSummary()` to populate all new refs from API response
  - [ ] 4.1.7 Add individual fetch methods if separate endpoints created
- [ ] 4.2 Add TypeScript types for all dashboard data structures
- [ ] 4.3 Test store in browser console

## 5. Frontend Dashboard Refactoring
- [ ] 5.1 **Stats Section** (lines 55-107):
  - [ ] 5.1.1 Replace hard-coded `42` with `{{ stats?.newCases || 0 }}`
  - [ ] 5.1.2 Replace hard-coded `156` with `{{ stats?.documents || 0 }}`
  - [ ] 5.1.3 Replace hard-coded `389` with `{{ stats?.emails || 0 }}`
  - [ ] 5.1.4 Calculate next deadline dynamically from `stats?.nextDeadline`
  - [ ] 5.1.5 Calculate relative time ("in X days") using date-fns or native Date
  - [ ] 5.1.6 Calculate percentage changes from historical data (or remove if not available)
- [ ] 5.2 **Welcome Message** (line 49):
  - [ ] 5.2.1 Get user name from `usePortalUser()` composable
  - [ ] 5.2.2 Change "Willkommen zur?ck" to "Willkommen zur?ck, {{ userName }}"
  - [ ] 5.2.3 Fallback to generic greeting if name not available
- [ ] 5.3 **Continue Bar** (lines 34-43):
  - [ ] 5.3.1 Replace hard-coded "Klageentwurf Schmidt (80%)" with `continueSuggestion.title`
  - [ ] 5.3.2 Use `continueSuggestion.progress` for percentage
  - [ ] 5.3.3 Calculate relative deadline from `continueSuggestion.deadline`
  - [ ] 5.3.4 Hide bar if no continue suggestion exists
- [ ] 5.4 **Documents Section** (lines 112-164):
  - [ ] 5.4.1 Remove hard-coded `docs` array (lines 592-615)
  - [ ] 5.4.2 Replace with `documents` from dashboard store
  - [ ] 5.4.3 Use `v-for="doc in dashboardStore.documents"` in template
  - [ ] 5.4.4 Update data bindings to match API response structure
  - [ ] 5.4.5 Handle empty state when `documents.length === 0`
  - [ ] 5.4.6 Format dates/times properly ("vor 2 Stunden" ? use date library)
- [ ] 5.5 **Deadlines Section** (lines 167-192):
  - [ ] 5.5.1 Remove hard-coded deadline divs (lines 174-190)
  - [ ] 5.5.2 Replace with `v-for="deadline in dashboardStore.deadlines"`
  - [ ] 5.5.3 Calculate relative time ("Heute", "Morgen", "in 3 Tagen") dynamically
  - [ ] 5.5.4 Determine border color based on urgency (red=today, orange=tomorrow, green=later)
  - [ ] 5.5.5 Handle empty state when `deadlines.length === 0`
- [ ] 5.6 **Recent Activity Section** (lines 294-356):
  - [ ] 5.6.1 Remove hard-coded table rows (lines 324-353)
  - [ ] 5.6.2 Replace with `v-for="activity in dashboardStore.activity"`
  - [ ] 5.6.3 Render different badges based on `activity.type` (E-Mail, Telefon, Upload)
  - [ ] 5.6.4 Update subject, client, and status from activity data
  - [ ] 5.6.5 Handle empty state when `activity.length === 0`
  - [ ] 5.6.6 Remove or fix KI progress animation (only if relevant to actual activity)
- [ ] 5.7 **Date Calculations** (JavaScript section):
  - [ ] 5.7.1 Remove hard-coded dates "2025-08-21", "2025-08-23", "2025-08-28"
  - [ ] 5.7.2 Use `new Date()` for "today"
  - [ ] 5.7.3 Create helper function `getRelativeDateLabel(date)` for "Heute", "Morgen", "in X Tagen"
  - [ ] 5.7.4 Create helper function `formatRelativeTime(date)` for "vor 2 Stunden", "gestern"
  - [ ] 5.7.5 Update all date displays to use helper functions
- [ ] 5.8 **Templates Section** (lines 196-291):
  - [ ] 5.8.1 Keep static for now (templates are org-wide, not user-specific)
  - [ ] 5.8.2 Optional: Fetch from `/api/templates` and render dynamically
  - [ ] 5.8.3 Optional: Mark user's favorite templates (future enhancement)

## 6. Frontend Data Fetching
- [ ] 6.1 Import dashboard store in `<script setup>`: `const dashboardStore = useDashboardStore()`
- [ ] 6.2 Call `dashboardStore.fetchSummary()` in `onMounted()`
- [ ] 6.3 Handle loading state: Show skeletons while `dashboardStore.isLoading`
- [ ] 6.4 Handle error state: Display error message if `dashboardStore.error`
- [ ] 6.5 Use reactive data in template: `{{ dashboardStore.stats.newCases }}`
- [ ] 6.6 Ensure data updates when user changes (if multi-user app)

## 7. Testing
- [ ] 7.1 **Unit Tests** (Backend):
  - [ ] 7.1.1 Test database query methods with mock data
  - [ ] 7.1.2 Test API endpoints with mocked database
  - [ ] 7.1.3 Verify error handling for invalid user IDs
- [ ] 7.2 **Integration Tests** (Full Stack):
  - [ ] 7.2.1 Create test user with sample data in database
  - [ ] 7.2.2 Test dashboard API returns correct data for test user
  - [ ] 7.2.3 Test frontend displays data correctly
- [ ] 7.3 **Manual Testing** (QA):
  - [ ] 7.3.1 Log in as Angela (admin) - verify personalized dashboard
  - [ ] 7.3.2 Log in as test user - verify different data shown
  - [ ] 7.3.3 Test empty dashboard (new user with no data)
  - [ ] 7.3.4 Test dashboard with 1 document, 0 deadlines, etc.
  - [ ] 7.3.5 Verify dates are relative to today (not hard-coded 2025 dates)
  - [ ] 7.3.6 Verify welcome message shows correct user name
  - [ ] 7.3.7 Test on mobile view (responsive design)
- [ ] 7.4 **Performance Testing**:
  - [ ] 7.4.1 Measure dashboard load time (should be <2 seconds)
  - [ ] 7.4.2 Check database query performance (each query <50ms)
  - [ ] 7.4.3 Test with large dataset (100+ documents, 50+ deadlines)
  - [ ] 7.4.4 Verify no N+1 query issues

## 8. Deployment
- [x] 8.1 Run database migrations to create new tables
- [ ] 8.2 Seed database with sample data for testing (optional)
- [x] 8.3 Build frontend: `cd anwalts-frontend-new && npm run build`
- [x] 8.4 Deploy backend changes (restart services if needed)
- [x] 8.5 Deploy frontend changes (rebuild Docker image)
- [x] 8.6 Verify deployment with smoke test (load dashboard, check console for errors)
- [ ] 8.7 Monitor logs for errors in first 24 hours
- [x] 8.8 Rollback plan ready (revert to previous Docker image if critical issues)

## 9. Documentation
- [ ] 9.1 Update API documentation with new dashboard endpoints
- [ ] 9.2 Document database schema changes in migration file comments
- [ ] 9.3 Add comments to dashboard store explaining data flow
- [ ] 9.4 Create user guide: "Understanding Your Dashboard" (optional)
- [ ] 9.5 Update deployment checklist with dashboard testing steps

## 10. Cleanup
- [ ] 10.1 Remove commented-out hard-coded data
- [ ] 10.2 Remove unused dummy data constants
- [ ] 10.3 Remove hard-coded date constants ("2025-08-21")
- [ ] 10.4 Clean up console.log statements used for debugging
- [ ] 10.5 Run linter and fix any warnings
- [ ] 10.6 Review code for any remaining hard-coded values

## Notes
- Total estimated time: 8-12 hours of development work
- Can be split across multiple developers (backend, frontend, testing)
- Backend changes should be deployed first, frontend second
- Enable feature flag if gradual rollout desired (not required for this change)
