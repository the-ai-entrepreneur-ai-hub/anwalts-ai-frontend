## MODIFIED Requirements

### Requirement: Admin Settings Page Authentication

The Admin Settings page SHALL use the correct authentication token format when making API requests to protected admin endpoints. The frontend MUST access session tokens via the `useSupabaseAuth()` composable, which provides custom JWT tokens stored in browser cookies (`auth_token`, `sid`, `sat`) that are compatible with the backend's JWT validation logic in `auth_service.py`.

The page SHALL NOT use `useSupabaseSession()` directly, as this composable is either undefined or returns Supabase-specific JWT tokens that are incompatible with the backend's custom JWT format validation (3-part dot-separated structure expected by `auth_service.create_access_token()`).

#### Scenario: Admin loads settings page successfully

- **GIVEN** a user with admin role and valid JWT token stored in cookies
- **WHEN** the user navigates to `/dashboard/settings`
- **AND** the frontend calls `useSupabaseAuth()` to retrieve the session
- **AND** the frontend includes the session access token in the Authorization header
- **THEN** the API request to `/api/admin/settings` SHALL succeed with 200 OK
- **AND** system statistics SHALL be displayed (active users, connected emails, documents, templates)
- **AND** organization settings SHALL be loaded into the form
- **AND** recent activity SHALL be displayed
- **AND** no authentication errors SHALL appear in browser console or backend logs

#### Scenario: Settings page handles missing composable gracefully

- **GIVEN** `useSupabaseSession()` is not defined in the codebase
- **WHEN** the settings page attempts to use this composable
- **THEN** the application SHALL provide a fallback using `useSupabaseAuth()`
- **OR** a wrapper composable `useSupabaseSession()` SHALL be created that internally uses `useSupabaseAuth()`
- **AND** the application SHALL not crash or throw undefined errors

#### Scenario: Settings page handles invalid token format

- **GIVEN** a token that does not match the backend's expected JWT format
- **WHEN** the frontend sends this token in the Authorization header
- **THEN** the backend SHALL respond with 401 Unauthorized or 403 Forbidden
- **AND** the frontend SHALL display a specific error message: "Authentication failed: Please login again"
- **AND** the frontend SHALL log detailed debug information including token format (first 20 chars), status code, and error response
- **AND** a retry button SHALL be displayed to reload settings

#### Scenario: Cookie-based authentication as fallback

- **GIVEN** valid JWT tokens stored in browser cookies (`auth_token`, `sid`, or `sat`)
- **WHEN** the frontend makes API requests without explicit Authorization header
- **THEN** the `$fetch` utility SHALL automatically send cookies with the request
- **AND** the backend SHALL validate tokens from cookies
- **AND** the request SHALL succeed if tokens are valid
- **AND** this approach SHALL be documented as an alternative to explicit Authorization headers

#### Scenario: Debug logging for authentication troubleshooting

- **GIVEN** an authentication failure occurs
- **WHEN** the error is caught in the frontend
- **THEN** the application SHALL log the following information:
  - Token type being used (Supabase vs custom JWT)
  - First 20 characters of token (for security)
  - HTTP response status code (401, 403, 500, etc.)
  - Response headers (if available)
  - Error message from backend
- **AND** this debug information SHALL be available in the error details panel
- **AND** the information SHALL help developers diagnose token format issues

## ADDED Requirements

### Requirement: useSupabaseSession Composable Wrapper

If the `useSupabaseSession()` composable is used elsewhere in the codebase or is expected to be available, a wrapper composable SHALL be created at `composables/useSupabaseSession.ts` that internally uses `useSupabaseAuth()` and exports the session object.

#### Scenario: useSupabaseSession returns compatible session

- **GIVEN** `useSupabaseSession()` is called in any component
- **WHEN** the composable is invoked
- **THEN** it SHALL internally call `useSupabaseAuth()`
- **AND** it SHALL return the `session` value from `useSupabaseAuth()`
- **AND** the returned session SHALL contain `access_token` that is a custom JWT token
- **AND** the returned session SHALL be compatible with backend authentication

#### Scenario: Type safety for session objects

- **GIVEN** the `useSupabaseSession()` wrapper is implemented
- **WHEN** TypeScript compilation occurs
- **THEN** the composable SHALL export proper TypeScript types
- **AND** the types SHALL match Supabase Session type structure
- **AND** the `access_token` field SHALL be typed as string | undefined

### Requirement: Authentication Error Messages

The Admin Settings page SHALL provide clear, actionable error messages when authentication fails, with different messages for different failure scenarios.

#### Scenario: 401 Unauthorized error

- **GIVEN** the backend returns 401 status code
- **WHEN** the error is caught in the frontend
- **THEN** the error message SHALL be: "Authentication failed: Please login again"
- **AND** the user SHALL be advised to re-authenticate

#### Scenario: 403 Forbidden error

- **GIVEN** the backend returns 403 status code (admin check fails)
- **WHEN** the error is caught in the frontend
- **THEN** the error message SHALL be: "Access denied: Admin privileges required"
- **AND** the user SHALL understand they lack admin permissions

#### Scenario: 500 Server error

- **GIVEN** the backend returns 500 status code
- **WHEN** the error is caught in the frontend
- **THEN** the error message SHALL be: "Server error: Please contact administrator"
- **AND** the user SHALL understand this is a backend issue, not a client issue

#### Scenario: Token format validation error

- **GIVEN** the backend logs show "Invalid token format" error
- **WHEN** this occurs due to Supabase JWT being sent instead of custom JWT
- **THEN** the frontend error SHALL indicate authentication failure
- **AND** the debug panel SHALL show the token type mismatch
- **AND** developers SHALL be able to identify the root cause from logs
