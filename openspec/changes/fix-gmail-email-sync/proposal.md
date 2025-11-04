# Gmail Email Sync Fix Proposal

## Why
- After Google OAuth login the email view still shows seeded placeholder messages because the Nuxt server endpoints call Gmail directly using a gmail_rt cookie that is not set for most sessions.
- Backend already persists Gmail refresh tokens in Postgres, but no backend REST endpoints surface real Gmail content to the UI, so the frontend cannot hydrate inbox/labels/search with actual data even when consent exists.
- Users expect that once they grant consent the live Gmail inbox, labels, counts, search, and pagination operate inside the existing UI without manual refreshes or mock data fallbacks.

## What
- Introduce authenticated backend APIs (GET /api/email/list, GET /api/email/labels, POST /api/email/modify, optional search/pagination params) that refresh Google access tokens server-side using the stored refresh token, call Gmail REST APIs, and normalize responses for the UI.
- Update Nuxt server routes to proxy to the backend instead of contacting Google directly, eliminating the brittle dependence on the gmail_rt cookie and aligning error handling.
- Extend the frontend email page logic to:
  - Query /api/user/gmail/status on mount and after OAuth callback to detect consent.
  - Fetch real emails via the new backend endpoints, mapping tabs, counts, search, pagination, and load-more UX to Gmail data.
  - Remove hard-coded mock dataset once Gmail returns results while keeping graceful fallback UX when no messages exist.
- Ensure Gmail OAuth runs with the correct scopes (readonly, modify) and stores refresh tokens; handle reconnection prompts when refresh tokens are missing or expired.

## Impact
- **Backend:** backend-main.py (new Gmail list/labels/modify endpoints, shared Gmail API helper), database.py (supporting helpers if required).
- **Frontend server API:** anwalts-frontend-new/server/api/email/*.ts, server/api/user/gmail/*.ts (proxy adjustments, status handling).
- **Frontend page:** anwalts-frontend-new/pages/email.vue (state management, data binding, load more/search integration, error UX, consent flow wiring).
- **Testing/ops:** ensure Docker image rebuild for backend/frontend so new endpoints deploy.

## Risks & Mitigations
- *OAuth scope changes* already deployed; ensure the prompt still requests an offline refresh token when reconnecting.
- *Token refresh failure* must surface an actionable reconnect CTA; add logging and 401 handling.
- *API quota & latency* mitigated with pagination (maxResults, pageToken) and caching headers where possible.
- *Security* keep refresh tokens server-side; do not leak them via cookies or client responses.

## Validation Strategy
1. Run backend unit coverage (if present) for new Gmail helpers; add targeted tests/mocks where feasible.
2. Manual QA: login via Google, land on /email, verify Gmail content, folder counts, search, label filtering, load more, modify actions (star/read) propagate back to Gmail.
3. Regression: ensure the existing dashboard/login flow is unaffected; logout and reconnect flows cleanly revoke tokens.
