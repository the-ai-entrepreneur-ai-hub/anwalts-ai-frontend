# Gmail Status Sync Reliability Proposal

## Why
- Live OAuth consent completes but the inbox view frequently falls back to the consent screen because `/api/user/gmail/status` raises `TypeError: Object of type datetime is not JSON serializable` (see `backend-main.py:2090+`). The endpoint serialises account records but not top-level fields, so `consent_timestamp`, `last_connected_at`, and other datetime values leak into the JSON payload and break the client.
- Even when status succeeds, the first inbox load depends on the user manually reloading. We do not trigger a server-side sync after consent, and the Nuxt page has no guaranteed follow-up call to `/api/user/gmail/sync`, leaving new accounts with empty email lists.
- The database keeps `draft_only_mode` at its default `TRUE` for freshly linked accounts, which prevents full-message retrieval even when the user granted AI read access. We need explicit logic to flip the flag once both consents are captured and ensure subsequent status responses reflect the change.
- Without these fixes, users experience a "consent success" loop that never surfaces real emails, the Gmail status endpoint intermittently 500s, and downstream AI summary flows never see live data.

## What
- Harden `/api/user/gmail/status` to apply ISO 8601 conversion to every datetime in the response (status dict and nested accounts) and add regression tests so non-serialisable values cannot reach FastAPI.
- Introduce a reusable Gmail sync helper that exchanges the refresh token, fetches messages and labels, and is callable by both the existing GET `/api/email/list` logic and a new POST `/api/user/gmail/sync` trigger endpoint (with label + pagination parameters and rate limiting).
- Kick off an initial background sync at the end of the Gmail OAuth callback (`backend-main.py:1310+`) so new accounts have headers cached before redirecting back to `/email`; log sync outcomes for observability.
- Update the frontend (`pages/email.vue`) to call the new sync endpoint immediately after status reports `connected`, handle progress UI, and only fall back to seeded mocks when the API explicitly indicates the account is unlinked.
- Ensure `database.py:set_gmail_refresh_token` / consent persistence toggles `draft_only_mode` to `FALSE` whenever both OAuth and AI read consents are active, and surface the persisted flag in status payloads so the UI accurately reflects read permissions.

## Impact
- **Backend:** `backend-main.py` (status serialisation, new sync helper/endpoint, OAuth callback task), `database.py` (draft-only toggle + helper), potential additions in `email_sync` utilities if present.
- **Frontend:** `anwalts-frontend-new/pages/email.vue` (post-consent sync trigger, success handling) and possibly related composables.
- **Tests:** FastAPI unit tests for status serialisation + sync helper, Playwright/Vitest coverage for consent→sync flow.
- **Ops:** Requires backend rebuild/redeploy; no schema migrations expected but we must verify new env logging toggles.

## Risks & Mitigations
- *Background sync failures* could slow OAuth redirects; mitigate by running sync in an `asyncio.create_task` with logging and letting redirect succeed even on failure.
- *Rate-limit overrun* if sync endpoint is spammed; enforce a conservative limiter (`gmail_sync`) that returns 429 with clear messaging.
- *Draft mode regression* if we flip the flag incorrectly; add tests confirming only fully consented accounts have draft-only disabled.

## Validation Strategy
1. Unit tests covering Gmail status serialisation (datetime fields) and sync helper token exchange error paths.
2. Manual QA: run through Gmail consent, observe `/api/user/gmail/status`, ensure the inbox populates automatically, and verify `draft_only_mode` reflects consent toggles.
3. Playwright scenario that links a test Gmail account (mocked locally), hits `/api/user/gmail/sync`, and confirms the inbox list renders emails while `nextPageToken` drives load more.
