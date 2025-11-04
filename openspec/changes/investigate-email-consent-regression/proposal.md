# Investigate Email Consent Regression

**Status**: Draft  
**Owner**: Codex Agent  
**Created**: 2025-11-01  
**Priority**: Critical  
**Risk**: Medium (auth/session touchpoints)

---

## Problem

After completing the Gmail consent flow the application immediately drops back to the consent screen and no inbox data loads. Production users cannot see their linked mailbox even though the OAuth redirect succeeds. We must map the end-to-end pipeline, identify the failing hand-off, and harden the integration before attempting another hotfix.

---

## Current Findings

1. **Frontend behaviour**  
   - `email.vue` detects `connected: true` only when `/api/user/gmail/status` succeeds.  
   - Subsequent calls to `/api/email/list` return `401`, triggering the fallback path that replaces live data with mock templates and reopens the consent card.  
   - Logs show the Nuxt server route never forwards the email list request to FastAPI (`docker compose logs backend | rg '/api/email/list'` returns nothing), confirming the failure happens inside the frontend proxy layer.

2. **Backend state**  
   - `db.get_gmail_connection_status` reports `connected: true` with a valid active account and refresh token (verified for user `32c0e4e0-2c5d-4ad0-9729-57dbdf41c83e`).  
   - Gmail refresh tokens are stored and the OAuth callback reports “session preserved”, so the link itself works.

3. **Proxy authentication gap**  
   - Nuxt’s `server/api/email/*.ts` routes build the backend `Authorization` header exclusively via `resolveBackendAuthHeader`.  
   - That helper requires either a Supabase session cookie or the legacy `auth_token` cookie. When Gmail OAuth preserves the session but the SPA only holds tokens in `localStorage`, the helper cannot mint a backend JWT and throws `401 Authentication required`.  
   - Because the request is rejected inside Nitro, the backend never sees the call and the inbox never renders.

4. **Secondary issues**  
   - Consent POSTs succeed but `ai_read_consent` often remains `false`, so AI summaries stay disabled.  
   - We lack instrumentation around the proxy failure, making the regression hard to diagnose from logs alone.

---

## Goal

Deliver an end-to-end fix that:
- Keeps users in the inbox after OAuth completes.
- Ensures the proxy layer can always forward authenticated requests (Authorization header, cookies, or fresh backend JWT).
- Captures meaningful telemetry for diagnosis.
- Verifies functionality through automated tests and live smoke checks.
- Documents and executes the required container rebuilds/restarts so production reflects the fix.

---

## Proposed Approach

1. **End-to-end mapping**  
   Document the full Gmail flow (consent page → OAuth redirect → callback → Nuxt proxy → FastAPI) and confirm which artefacts (cookies, storage tokens, query params) are available at each hop.

2. **Proxy authentication improvements**  
   - Extend `resolveBackendAuthHeader` to trust an incoming `Authorization` header when present, falling back to minting a backend JWT only when necessary.  
   - Add support for a dedicated `x-portal-auth` header so client code can hand off the SPA token without exposing it to other middleware.  
   - Gracefully downgrade to cookie-based auth if neither header nor Supabase session is available, and emit structured warnings instead of generic 401 responses.

3. **Client updates**  
   - Ensure `email.vue` (and other email API callers) always forward the stored token via the agreed header, while keeping `credentials: 'include'` for cookie scenarios.  
   - Preserve AI consent flags during the save/link flow so backend metadata stays in sync.

4. **Instrumentation & diagnostics**  
   - Add targeted logging around proxy authentication decisions and error paths, including correlation IDs that survive the round-trip.  
   - Capture failed attempts in Redis/Postgres for operational dashboards.

5. **Verification**  
   - Create automated regression coverage (e.g., Playwright scenario: consent → OAuth stub → inbox renders).  
   - Add backend unit tests ensuring proxy helper accepts Authorization/cookie inputs.  
   - Rebuild frontend + backend containers, restart nginx, and record live smoke results (inbox renders, emails list, AI summary toggle).

6. **Documentation**  
   - Update operational runbooks describing the new auth hand-off.  
   - Note expected environment variables and restart steps for future responders.

---

## Out of Scope

- UI redesign of the email experience (covered by `redesign-email-interface`).
- Migrating Gmail integration to a new provider or queue-based ingestion.
- Replacing the existing OAuth provider.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Forwarding SPA tokens may widen attack surface | Restrict accepted header names, validate JWT issuer/audience, keep TLS termination at nginx |
| Regression in other proxy routes | Add unit tests + feature flag to roll back to current behaviour |
| OAuth callback state inconsistencies | Preserve current session-preservation logic; add additional telemetry before rollout |

---

## Success Criteria

- Gmail consent flow lands the user in the inbox without flashing the consent card.  
- `/api/email/list` proxy calls reach FastAPI and return messages for linked accounts.  
- AI consent values persist correctly after the flow.  
- New logs/metrics exist for proxy authentication decisions.  
- Documented rebuild/restart steps executed and recorded.

