# Tasks – Gmail Status Sync Reliability

## 1. Diagnose & Guard Status Serialisation
- [ ] 1.1 Capture failing payload from `/api/user/gmail/status` and document fields containing raw `datetime` objects (see `backend-main.py:2090+`).
- [ ] 1.2 Extend status shaping logic to ISO-format every datetime (top-level + nested accounts) and add backend unit coverage to prevent regressions.

## 2. Implement Reliable Sync Trigger
- [ ] 2.1 Extract a reusable Gmail fetch helper that handles label/folder resolution, pagination, and error mapping (to be reused by GET `/api/email/list` and the manual trigger).
- [ ] 2.2 Add POST `/api/user/gmail/sync` with rate limiting, response payload `{success, synced, emails?, nextPageToken}` and ensure it leverages the helper.
- [ ] 2.3 Fire `_initial_gmail_sync` from the OAuth callback once refresh tokens are persisted; log success/failure without blocking redirects.

## 3. Persist Draft Mode & Frontend Trigger
- [ ] 3.1 Update `database.py:set_gmail_refresh_token` (and related consent paths) to set `draft_only_mode = FALSE` when both OAuth + AI read consent are true, preserving explicit user preferences otherwise.
- [ ] 3.2 Adjust `/api/user/gmail/status` to surface the stored `draft_only_mode` flag, and update `pages/email.vue` to call the new sync endpoint as soon as a connected status is received.
- [ ] 3.3 Ensure the Nuxt email page refreshes lists after manual syncs and gracefully handles 429/401 error messages.

## 4. Validation & Deployment
- [ ] 4.1 Add/refresh unit + Playwright coverage for consent→status→sync flow (including the new endpoint and draft-mode flag).
- [ ] 4.2 Rebuild backend/frontend containers, redeploy, and capture smoke-test evidence (`/api/user/gmail/status`, `/api/user/gmail/sync`, inbox load).
- [ ] 4.3 Update ops notes/runbook with the new sync endpoint, rate limiting, and draft-only behaviour adjustments.
