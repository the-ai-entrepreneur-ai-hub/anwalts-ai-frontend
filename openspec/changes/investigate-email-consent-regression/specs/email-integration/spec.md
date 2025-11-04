## ADDED Requirements
### Requirement: Email Inbox Must Remain Accessible After OAuth Link
Authenticated users MUST remain on the inbox view after completing the Gmail consent flow, and the email proxy MUST forward requests to the backend using whatever authentication artefact (Authorization header, portal cookie, or Supabase session) the client provides.

#### Scenario: OAuth Redirect Returns To Inbox
- **GIVEN** a logged-in portal user with no linked mailbox
- **AND** the user grants Gmail access via the consent screen
- **WHEN** the OAuth callback completes
- **THEN** the documents/email page switches to the inbox view
- **AND** the initial call to `/api/email/list` succeeds with live Gmail messages

#### Scenario: Proxy Accepts Forwarded Authorization Header
- **GIVEN** the SPA still holds a valid portal access token in local storage
- **WHEN** `email.vue` calls the Nuxt proxy with `Authorization: Bearer <token>`
- **THEN** `resolveBackendAuthHeader` accepts the forwarded header
- **AND** the proxy forwards the authenticated request to FastAPI without emitting a 401

#### Scenario: Proxy Falls Back To Auth Cookies
- **GIVEN** the browser only has the secure `auth_token` cookie after OAuth completes
- **WHEN** `email.vue` calls the Nuxt proxy without an Authorization header
- **THEN** the helper mints/forwards a backend token derived from the cookie
- **AND** the proxy call succeeds without forcing the user back to the consent card
