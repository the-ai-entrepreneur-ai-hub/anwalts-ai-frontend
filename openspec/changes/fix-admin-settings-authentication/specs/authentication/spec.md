## ADDED Requirements

### Requirement: JWT Token Format Compatibility

The frontend authentication system SHALL use custom JWT tokens created by `auth_service.create_access_token()` for all API requests to protected endpoints. These tokens SHALL be stored in browser cookies (`auth_token`, `sid`, `sat`) and SHALL be accessible via the `useSupabaseAuth()` composable.

The system SHALL NOT mix Supabase JWT tokens with custom JWT tokens, as they have different validation logic in the backend (`auth_service.py` lines 64-79).

#### Scenario: Custom JWT token structure validation

- **GIVEN** a user successfully authenticates
- **WHEN** the backend creates an access token
- **THEN** the token SHALL be in standard JWT format (3 parts separated by dots: header.payload.signature)
- **AND** the token SHALL be created by `auth_service.create_access_token()`
- **AND** the token SHALL be stored in one or more cookies: `auth_token`, `sid`, or `sat`
- **AND** the token SHALL be retrievable via `useSupabaseAuth().session.value.access_token`

#### Scenario: Frontend accesses session tokens correctly

- **GIVEN** a protected page needs to make an authenticated API request
- **WHEN** the page retrieves authentication credentials
- **THEN** it SHALL use `const { session } = useSupabaseAuth()`
- **AND** it SHALL access the token via `session.value?.access_token`
- **AND** it SHALL NOT use `useSupabaseSession()` unless a wrapper exists
- **AND** the token SHALL be sent in the Authorization header as `Bearer {token}`

#### Scenario: Backend validates custom JWT format

- **GIVEN** a request with Authorization header is received
- **WHEN** the backend validates the token in `auth_service.py`
- **THEN** it SHALL check the token has exactly 3 parts separated by dots
- **AND** it SHALL decode the token using the `JWT_SECRET_KEY`
- **AND** it SHALL reject tokens that don't match this format with 401 status
- **AND** it SHALL log "Invalid token format" if the structure is wrong

#### Scenario: Cookie-based authentication flow

- **GIVEN** valid JWT tokens are stored in browser cookies
- **WHEN** a frontend API request is made via `$fetch`
- **THEN** cookies SHALL be automatically sent with `credentials: 'include'`
- **AND** the backend SHALL read tokens from cookies if Authorization header is absent
- **AND** the backend SHALL validate the token using the same logic as header tokens
- **AND** the request SHALL succeed if cookie tokens are valid

#### Scenario: Token type mismatch detection

- **GIVEN** a Supabase JWT token is sent to the backend instead of a custom JWT
- **WHEN** the backend attempts to validate the token
- **THEN** the validation SHALL fail due to different signing key or structure
- **AND** the backend SHALL return 401 Unauthorized status
- **AND** the backend SHALL log "Error verifying token: 401: Invalid token format"
- **AND** the frontend SHALL receive clear error response

### Requirement: Composable Authentication Interface

The frontend SHALL provide a consistent composable interface for accessing authentication state and tokens across all components and pages.

#### Scenario: useSupabaseAuth provides complete session

- **GIVEN** any Vue component or page needs authentication data
- **WHEN** it calls `const { session, user, profile } = useSupabaseAuth()`
- **THEN** `session.value` SHALL contain the current session object with `access_token`
- **AND** `user.value` SHALL contain the current user object
- **AND** `profile.value` SHALL contain the user profile data
- **AND** all values SHALL be reactive and update when authentication state changes

#### Scenario: useSupabaseSession wrapper exists

- **GIVEN** `useSupabaseSession()` is referenced in the codebase
- **WHEN** it is called from any component
- **THEN** it SHALL internally delegate to `useSupabaseAuth()`
- **AND** it SHALL return only the `session` value for backwards compatibility
- **AND** the session SHALL contain the same `access_token` as from `useSupabaseAuth()`

#### Scenario: Admin composable provides role checking

- **GIVEN** a page needs to verify admin access
- **WHEN** it calls `const { isAdmin, requireAdmin } = useAuth()`
- **THEN** `isAdmin.value` SHALL be a computed boolean indicating admin status
- **AND** `requireAdmin()` SHALL throw an error if user is not admin
- **AND** the admin check SHALL compare user email against authorized admin list
- **AND** authorized admins SHALL include hardcoded emails plus environment variable emails

### Requirement: Authentication Error Handling

The authentication system SHALL provide detailed error information when token validation fails, enabling developers to diagnose token format issues and other authentication problems.

#### Scenario: Token validation error logging

- **GIVEN** a token fails validation on the backend
- **WHEN** the error occurs in `auth_service.py`
- **THEN** the backend SHALL log the error with format: "Error verifying token: {status}: {message}"
- **AND** the backend SHALL include the reason for failure (format, expiry, signature, etc.)
- **AND** the backend SHALL return appropriate HTTP status (401 for invalid, 403 for insufficient privileges)

#### Scenario: Frontend error debug information

- **GIVEN** an authentication error occurs in the frontend
- **WHEN** the error is caught in the catch block
- **THEN** the frontend SHALL create an `errorDebug` object containing:
  - `message`: Human-readable error description
  - `status`: HTTP status code
  - `statusText`: HTTP status text
  - `data`: Raw error response data
  - `timestamp`: ISO timestamp of the error
- **AND** this debug information SHALL be displayed in a collapsible debug panel
- **AND** the debug panel SHALL help developers identify root cause

#### Scenario: Backend admin middleware logging

- **GIVEN** a request to an admin-protected endpoint
- **WHEN** the admin middleware validates the user
- **THEN** successful admin checks SHALL be logged as: "Admin access granted for {email}"
- **AND** failed admin checks SHALL be logged as: "Admin access denied for {email}"
- **AND** missing authentication SHALL be logged with 401 status
- **AND** logs SHALL include the endpoint path and user identifier
