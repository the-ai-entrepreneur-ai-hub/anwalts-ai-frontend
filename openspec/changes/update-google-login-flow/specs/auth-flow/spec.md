## ADDED Requirements
### Requirement: Separate Google OAuth Modes
The system MUST separate Google login and Gmail-connection OAuth flows so users only grant mailbox access when explicitly connecting email.

#### Scenario: Login Without Gmail Consent
- **WHEN** a user starts Google login without specifying a Gmail mode
- **THEN** the authorize endpoint builds a Google OAuth URL with only `openid email profile` scopes
- **AND** it uses `access_type=online` and `prompt=select_account`
- **AND** the callback completes without requesting Gmail modify permissions

#### Scenario: Gmail Connect Requests Mailbox Scopes
- **WHEN** the email workspace initiates `/api/auth/google/authorize?mode=gmail`
- **THEN** the authorize endpoint adds `gmail.readonly` and `gmail.modify` scopes
- **AND** it uses `access_type=offline` and `prompt=consent`
- **AND** the callback receives a refresh token that is stored for Gmail access

#### Scenario: Query Parameters Propagate Through Proxies
- **WHEN** the frontend authorize request includes additional query parameters
- **THEN** the frontend proxies forward those parameters to the backend authorize endpoint
- **AND** the backend redirect preserves them when constructing the Google OAuth URL
