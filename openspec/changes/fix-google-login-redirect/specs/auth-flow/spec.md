## ADDED Requirements
### Requirement: Google Login Redirects to Dashboard
The system MUST send users to the dashboard after a successful Google OAuth login when no Gmail consent was requested.

#### Scenario: Landing Modal Login Goes To Dashboard
- **WHEN** a user starts Google OAuth from the landing modal without `mode=gmail`
- **THEN** the callback clears any stored Gmail return marker
- **AND** it redirects the browser to `/dashboard`
- **AND** no email consent screen is shown.

#### Scenario: Stale Gmail Return State Is Ignored
- **GIVEN** `gmail_oauth_return` is still stored from a previous Gmail-connect attempt
- **WHEN** the user completes a normal Google login
- **THEN** the callback discards the stale marker
- **AND** the user lands on `/dashboard`.

### Requirement: Gmail Consent Flow Is Explicit
The Gmail consent experience MUST only run when the OAuth flow was explicitly started in Gmail mode.

#### Scenario: Gmail Connect Returns To Email Workspace
- **WHEN** the email workspace launches `/api/auth/google/authorize?mode=gmail`
- **THEN** the authorize endpoint marks the flow as `gmail`
- **AND** the callback preserves the stored Gmail return path
- **AND** it redirects to `/email` after storing Gmail tokens.

#### Scenario: Login Flow Avoids Gmail Consent
- **WHEN** a user starts Google OAuth without Gmail mode
- **THEN** the authorize endpoint does not request Gmail scopes
- **AND** the callback does not show or trigger the email consent UI
- **AND** no Gmail refresh token is written.

### Requirement: Gmail Flow State Is Session Scoped
Markers that control Gmail-only redirects MUST expire when the browser session ends.

#### Scenario: Gmail Return Marker Uses Session Storage
- **WHEN** Gmail connect is initiated from the email workspace
- **THEN** the frontend stores the return destination in a session-scoped location
- **AND** the marker is removed immediately after the callback completes.
