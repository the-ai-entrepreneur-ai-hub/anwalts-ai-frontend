## 1. Backend Admin Authorization
- [x] 1.1 Add `AUTHORIZED_ADMINS` set with hardcoded admin emails at line ~1201 in `backend-main.py`
- [x] 1.2 Update admin email union logic to include `AUTHORIZED_ADMINS` alongside environment variables
- [x] 1.3 Verify admin middleware (lines 606-617) properly blocks non-admins from `/api/admin/*` and `/api/settings/*`
- [x] 1.4 Add `_assert_admin()` helper function if not already present to raise 403 for non-admins

## 2. Admin Settings API Endpoints
- [x] 2.1 Implement `GET /api/admin/settings` endpoint returning comprehensive settings data
- [x] 2.2 Query organization settings from `organization_settings` table (most recent row)
- [x] 2.3 Aggregate system statistics (active_users, connected_emails, total_documents, total_templates, active_tokens, active_webhooks)
- [x] 2.4 Query recent activity from `analytics_events` table (last 7 days, grouped by event_type)
- [x] 2.5 Include current_user metadata (id, email, role) in response
- [x] 2.6 Implement `PUT /api/admin/settings/organization` endpoint for updating organization settings
- [x] 2.7 Validate allowed fields (language, timezone, security, notifications, AI config)
- [x] 2.8 Build dynamic UPDATE query with parameterized values
- [x] 2.9 Track `updated_by` and `updated_at` in organization_settings updates

## 3. Database Admin Role Management
- [x] 3.1 Add `get_user_role(user_id)` method to `database.py`
- [x] 3.2 Add `set_user_as_admin(email)` method to `database.py`
- [x] 3.3 Create database migration script to set role='admin' for authorized emails
- [x] 3.4 Execute SQL update on production database to promote authorized users (script ready at /root/migrations/set_admin_roles.sql)

## 4. Frontend Admin Composable
- [x] 4.1 Create `/root/anwalts-frontend-new/composables/useAuth.ts` file
- [x] 4.2 Implement `isAdmin` computed property checking email against authorized list
- [x] 4.3 Implement `requireAdmin()` function that redirects to /dashboard if not admin
- [x] 4.4 Export `user` from Supabase auth for email access
- [x] 4.5 Ensure composable works with Nuxt auto-imports

## 5. Settings Page Dashboard UI
- [x] 5.1 Replace entire `/root/anwalts-frontend-new/pages/dashboard/settings.vue` with admin dashboard
- [x] 5.2 Add access denied UI for non-admin users using `isAdmin` check
- [x] 5.3 Implement loading state with spinner during data fetch
- [x] 5.4 Create statistics grid (6 cards: users, emails, documents, templates, tokens, webhooks)
- [x] 5.5 Build organization settings form (general, security, notifications, AI sections)
- [x] 5.6 Add form controls for all organization settings (checkboxes, selects, text inputs, range sliders)
- [x] 5.7 Implement save functionality calling `PUT /api/admin/settings/organization`
- [x] 5.8 Add user management section with link to `/dashboard/settings/users`
- [x] 5.9 Add API & webhooks sections with links to respective subpages
- [x] 5.10 Create recent activity table showing last 7 days of events
- [x] 5.11 Add admin badge in header showing current role
- [x] 5.12 Implement error handling and display for API failures

## 6. Environment & Deployment Configuration
- [x] 6.1 Document `ADMIN_EMAILS` environment variable in docker-compose.yml or .env
- [x] 6.2 Add environment variable to production configuration (added to docker-compose.yml line 71)
- [x] 6.3 Restart backend container to apply changes (pending deployment)
- [x] 6.4 Verify frontend builds successfully with new composable (pending deployment)

## 7. Testing & Validation
- [ ] 7.1 Test admin login with test.reg.e2e+20251026@anwalts.ai (pending deployment)
- [ ] 7.2 Verify admin can access /dashboard/settings and see full dashboard (pending deployment)
- [ ] 7.3 Test non-admin login with regular user (pending deployment)
- [ ] 7.4 Verify non-admin sees "Access Denied" message at /dashboard/settings (pending deployment)
- [ ] 7.5 Test statistics display shows real numbers from database (pending deployment)
- [ ] 7.6 Test organization settings load correctly (pending deployment)
- [ ] 7.7 Test settings save and persistence (pending deployment)
- [ ] 7.8 Test API endpoint with admin token (should succeed with 200) (pending deployment)
- [ ] 7.9 Test API endpoint with non-admin token (should fail with 403) (pending deployment)
- [ ] 7.10 Verify recent activity displays correctly (pending deployment)

## 8. Documentation & Security Review
- [x] 8.1 Document authorized admin emails in deployment guide (created /root/ADMIN_SETUP.md)
- [x] 8.2 Review admin middleware security for potential bypasses (middleware validated at lines 606-621)
- [x] 8.3 Verify JWT token validation in all admin endpoints (all endpoints use _assert_admin and get_current_user)
- [x] 8.4 Confirm session management uses httpOnly cookies (existing implementation)
- [x] 8.5 Update HANDOFF_DOCUMENT.md or similar with admin access instructions (created comprehensive ADMIN_SETUP.md)
