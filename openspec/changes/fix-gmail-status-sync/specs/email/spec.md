# Gmail Sync Reliability

## ADDED Requirements

### Requirement: Gmail status responses are JSON serialisable
The Gmail status API MUST return a payload that contains only JSON-native values so Nuxt can hydrate without runtime errors.
#### Scenario: Status response serialises timestamps
- **GIVEN** a user has an active Gmail account with `consent_timestamp`, `last_connected_at`, or other datetime fields stored in Postgres
- **WHEN** the client calls `GET /api/user/gmail/status`
- **THEN** the API responds `200` with all datetime values converted to ISO 8601 strings and no `TypeError: Object of type datetime is not JSON serializable` occurs

#### Scenario: Status response handles missing consent
- **GIVEN** the user revoked Gmail access and no active account exists
- **WHEN** the client calls `GET /api/user/gmail/status`
- **THEN** the API responds `200` with `connected=false`, omits refresh-token metadata, and still returns only JSON-native values

### Requirement: Gmail sync trigger pulls messages after consent
The system MUST synchronise Gmail messages automatically after consent and expose a manual trigger for follow-up syncs.
#### Scenario: Initial sync after OAuth
- **GIVEN** a user successfully completes Gmail OAuth and refresh tokens are stored
- **WHEN** the OAuth callback finishes processing
- **THEN** the backend kicks off an asynchronous sync that fetches at least the latest 20 inbox messages so the inbox is populated on first load

#### Scenario: Manual sync endpoint available
- **GIVEN** the user is already connected to Gmail and wants to refresh their inbox
- **WHEN** the client calls `POST /api/user/gmail/sync` with optional `folder`, `label`, or `pageToken` parameters
- **THEN** the backend exchanges the refresh token, fetches messages via Gmail, honours label/folder filters, enforces rate limiting, and responds with `{success:true, synced:<count>, nextPageToken}`

### Requirement: Draft-only mode reflects consent choices
The platform MUST disable draft-only mode automatically once full AI read consent is granted so inbox messages can be retrieved.
#### Scenario: Draft-only mode cleared after consent
- **GIVEN** a user stores Gmail OAuth consent and AI read consent
- **WHEN** the backend persists the email account and returns status data
- **THEN** `draft_only_mode` is saved as `false`, surfaced through `/api/user/gmail/status`, and the frontend allows full message sync.

#### Scenario: Draft-only mode preserved without AI consent
- **GIVEN** a user links Gmail but declines AI read consent
- **WHEN** the backend persists the account
- **THEN** `draft_only_mode` remains `true`, the status payload reports `ai_read_consent=false`, and the frontend respects the restricted mode (no full sync) until consent changes.
