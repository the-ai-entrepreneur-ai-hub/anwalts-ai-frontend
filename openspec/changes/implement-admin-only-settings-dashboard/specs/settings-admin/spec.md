## ADDED Requirements

### Requirement: Admin Authorization Uses Hardcoded List and Environment Variables
The system SHALL authorize admin access using a union of hardcoded emails in code and environment variable emails.

#### Scenario: Admin identified from hardcoded list
- **GIVEN** `AUTHORIZED_ADMINS` set contains "test.reg.e2e+20251026@anwalts.ai"
- **WHEN** user with that email attempts admin access
- **THEN** the system grants admin privileges

#### Scenario: Admin identified from environment variable
- **GIVEN** `ADMIN_EMAILS` environment variable contains "admin@example.com"
- **WHEN** user with that email attempts admin access
- **THEN** the system grants admin privileges

#### Scenario: Non-admin denied access
- **GIVEN** user email is not in hardcoded list or environment variables
- **WHEN** user attempts to access `/api/admin/settings`
- **THEN** the system returns 403 Forbidden

### Requirement: Admin Middleware Blocks Unauthorized Access to Admin Routes
The system SHALL enforce admin-only access to all routes under `/api/admin/*` and `/api/settings/*` at the middleware level.

#### Scenario: Middleware blocks non-admin from admin route
- **GIVEN** user is authenticated but not an admin
- **WHEN** user sends request to `/api/admin/settings`
- **THEN** middleware returns 403 Forbidden before reaching endpoint handler

#### Scenario: Middleware allows admin access
- **GIVEN** user is authenticated admin
- **WHEN** user sends request to `/api/admin/settings`
- **THEN** middleware passes request to endpoint handler

### Requirement: Admin Settings Endpoint Returns Comprehensive System Data
The system SHALL provide a `GET /api/admin/settings` endpoint that returns organization settings, system statistics, recent activity, and current user information.

#### Scenario: Admin requests settings data
- **GIVEN** authenticated admin user
- **WHEN** admin calls `GET /api/admin/settings` with valid JWT
- **THEN** response includes organization settings (language, timezone, security, notifications, AI config)
- **AND** response includes system statistics (active_users, connected_emails, total_documents, total_templates, active_tokens, active_webhooks)
- **AND** response includes recent_activity array with event counts from last 7 days
- **AND** response includes current_user with id, email, and role

#### Scenario: Non-admin denied settings access
- **GIVEN** authenticated non-admin user
- **WHEN** user calls `GET /api/admin/settings`
- **THEN** response is 403 Forbidden with "Admin access required" message

#### Scenario: Statistics reflect real database counts
- **GIVEN** database has 42 active users, 18 email accounts, 1337 documents
- **WHEN** admin calls `GET /api/admin/settings`
- **THEN** response statistics.active_users is 42
- **AND** response statistics.connected_emails is 18
- **AND** response statistics.total_documents is 1337

### Requirement: Organization Settings Can Be Updated by Admins
The system SHALL provide a `PUT /api/admin/settings/organization` endpoint that updates allowed organization settings fields.

#### Scenario: Admin updates organization settings
- **GIVEN** authenticated admin user
- **WHEN** admin sends `PUT /api/admin/settings/organization` with {"language": "en", "require_two_factor": true}
- **THEN** system updates organization_settings table with new values
- **AND** system records updated_by as current admin user_id
- **AND** system records updated_at as current timestamp
- **AND** response includes updated settings object

#### Scenario: Invalid fields are rejected
- **GIVEN** authenticated admin user
- **WHEN** admin sends `PUT /api/admin/settings/organization` with {"invalid_field": "value"}
- **THEN** response is 400 Bad Request with "No valid fields to update"

#### Scenario: Only allowed fields are updated
- **GIVEN** allowed fields list: language, timezone, require_two_factor, enable_sso, password_min_length, password_require_special, password_require_numbers, email_notifications, browser_notifications, ai_updates, ai_model, ai_creativity, auto_save
- **WHEN** admin updates settings with mix of allowed and disallowed fields
- **THEN** only allowed fields are updated in database
- **AND** disallowed fields are silently ignored

### Requirement: Database User Roles Designate Administrators
The system SHALL use the `users.role` column to designate administrators, with role='admin' for authorized users.

#### Scenario: Authorized emails have admin role in database
- **GIVEN** user with email "test.reg.e2e+20251026@anwalts.ai" exists in database
- **WHEN** database is queried for that user
- **THEN** user.role is 'admin'

#### Scenario: Admin role can be programmatically set
- **GIVEN** email address of user to promote
- **WHEN** system calls `set_user_as_admin(email)`
- **THEN** users table is updated with role='admin' for that email

#### Scenario: Admin role can be queried
- **GIVEN** user_id of authenticated user
- **WHEN** system calls `get_user_role(user_id)`
- **THEN** returns 'admin' if user is administrator
- **AND** returns other role value or None if not admin

### Requirement: Frontend Admin Composable Controls Access
The system SHALL provide a `useAuth()` composable that determines admin status and guards admin routes.

#### Scenario: Composable identifies admin user
- **GIVEN** Supabase user with email "test.reg.e2e+20251026@anwalts.ai"
- **WHEN** component calls `useAuth()`
- **THEN** isAdmin computed property returns true

#### Scenario: Composable identifies non-admin user
- **GIVEN** Supabase user with email "regular.user@example.com"
- **WHEN** component calls `useAuth()`
- **THEN** isAdmin computed property returns false

#### Scenario: RequireAdmin guard redirects non-admins
- **GIVEN** non-admin user on settings page
- **WHEN** page calls `requireAdmin()`
- **THEN** user is redirected to /dashboard
- **AND** error message is thrown

### Requirement: Settings Page Displays Admin Dashboard for Authorized Users
The system SHALL display a comprehensive admin dashboard on `/dashboard/settings` for admin users and an access denied message for non-admins.

#### Scenario: Admin sees full dashboard
- **GIVEN** user with admin privileges
- **WHEN** user navigates to `/dashboard/settings`
- **THEN** page displays system statistics cards
- **AND** page displays organization settings form
- **AND** page displays links to user management, API tokens, and webhooks
- **AND** page displays recent activity table
- **AND** page displays admin badge in header

#### Scenario: Non-admin sees access denied
- **GIVEN** user without admin privileges
- **WHEN** user navigates to `/dashboard/settings`
- **THEN** page displays "Access Denied" message
- **AND** page does NOT display any admin data or controls

#### Scenario: Statistics display real numbers
- **GIVEN** admin user on settings page
- **WHEN** page loads and calls `GET /api/admin/settings`
- **THEN** statistics cards display active_users count
- **AND** statistics cards display connected_emails count
- **AND** statistics cards display total_documents count
- **AND** statistics cards display total_templates count
- **AND** statistics cards display active_tokens count
- **AND** statistics cards display active_webhooks count

#### Scenario: Organization settings form loads current values
- **GIVEN** organization_settings table has language='de', timezone='Europe/Berlin'
- **WHEN** admin views settings page
- **THEN** language dropdown shows 'de' selected
- **AND** timezone dropdown shows 'Europe/Berlin' selected
- **AND** all other settings reflect database values

#### Scenario: Settings form saves changes
- **GIVEN** admin modifies organization settings in form
- **WHEN** admin clicks "Save Changes" button
- **THEN** frontend calls `PUT /api/admin/settings/organization` with modified values
- **AND** success notification displays
- **AND** form remains populated with updated values

#### Scenario: Loading state displays during data fetch
- **GIVEN** settings page is loading
- **WHEN** API request is in flight
- **THEN** page displays loading spinner
- **AND** page displays "Loading settings..." message

#### Scenario: Error state displays on API failure
- **GIVEN** API request fails
- **WHEN** error response received
- **THEN** page displays error message with failure reason
- **AND** page does NOT display partial/stale data

### Requirement: Recent Activity Shows Last 7 Days of Events
The system SHALL display recent system activity from the last 7 days, grouped by event type with counts.

#### Scenario: Recent activity displays events
- **GIVEN** analytics_events table has 145 document_generated events, 67 user_login events in last 7 days
- **WHEN** admin views settings page
- **THEN** recent activity table shows "Document Generated" with count 145
- **AND** recent activity table shows "User Login" with count 67
- **AND** each row shows last occurrence timestamp

#### Scenario: Event types are formatted for display
- **GIVEN** event_type "document_generated" in database
- **WHEN** displayed in recent activity
- **THEN** shows as "Document Generated" (formatted with spaces and title case)

#### Scenario: No activity shows empty state
- **GIVEN** no events in last 7 days
- **WHEN** admin views recent activity
- **THEN** displays "No recent activity" message

### Requirement: Admin Badge Indicates Privileged Access
The system SHALL display an "Admin" badge in the settings page header for users with admin privileges.

#### Scenario: Admin badge visible to admins
- **GIVEN** user with admin privileges
- **WHEN** viewing settings page
- **THEN** header displays "Admin" badge with blue styling

#### Scenario: Admin badge not visible to non-admins
- **GIVEN** user without admin privileges
- **WHEN** viewing access denied message on settings page
- **THEN** no admin badge is displayed
