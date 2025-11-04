# Email Sync Capability

## ADDED Requirements

### Requirement: Server provides Gmail message and label APIs using stored refresh tokens
The backend MUST surface Gmail data through authenticated APIs without exposing refresh tokens to the client.
#### Scenario: Connected user fetches inbox
- GIVEN a user has completed Gmail OAuth with stored refresh token
- WHEN the client calls GET /api/email/list without filters
- THEN the backend exchanges the refresh token for an access token, fetches messages from Gmail (max 25 by default), normalizes sender/subject/snippet/label/flags/timestamps, and returns success:true with emails[] and nextPageToken (if provided by Gmail)

#### Scenario: Token missing or refresh fails
- GIVEN the user has no valid Gmail refresh token or Google returns invalid_grant
- WHEN GET /api/email/list is invoked
- THEN the backend responds 401 with error code token_refresh_failed and does not attempt to call Gmail again on the same request

#### Scenario: Label metadata requested
- GIVEN a connected user
- WHEN the client calls GET /api/email/labels
- THEN the backend returns normalized Gmail labels including id, name, type, unread count (if present), and timestamps the response for logging

### Requirement: Frontend email view consumes backend APIs
The email UI MUST call the new backend endpoints and reflect their responses in tabs, counts, and message lists.
#### Scenario: Inbox loads real messages after consent
- GIVEN a user completes Gmail consent via the existing flow and is redirected back to /email
- WHEN the page initializes
- THEN it calls /api/user/gmail/status, detects connected, fetches labels + inbox via the backend proxies, replaces placeholder data with live results, and renders counts in all tabs

#### Scenario: Load more and search use backend pagination
- GIVEN additional Gmail pages exist or the user enters a search query
- WHEN the user clicks Load more or submits search
- THEN the frontend forwards pageToken/label/query params to the backend, appends new results to the UI, and updates the load more affordance until nextPageToken is empty

#### Scenario: Token revocation requires reconnection
- GIVEN Google revoked the refresh token and the backend returns token_refresh_failed
- WHEN the frontend receives the 401 response
- THEN it surfaces a reconnect Gmail CTA, returns to consent view, and does not display stale mock emails as if they were current data
