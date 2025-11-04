# Proposal: Stabilize Email Connection & State Handling

- Change ID: stabilize-email-connection
- Owners: Platform Email / Fullstack
- Status: Proposed
- Created: 2025-11-04

## Problem

Field feedback (2025-11-04) shows the email workspace is still unusable: the Gmail status probe returns HTTP 500 and once it recovers the inbox renders messages from the previously linked Google account even after signing in with a different app user. The latest deployment already included JSON guards, but `/api/user/gmail/status` keeps crashing before the guard activates. The frontend also keeps a global `localStorage` connection flag, so the inbox view flashes “connected” while the backend errors, creating the perception that nothing changed.

Specific gaps:

- **Backend status serialization still brittle** – `backend-main.py:2069-2141` reshapes the result from `db.get_gmail_connection_status`. When the DB layer returns raw `asyncpg.Record` instances (for example after warm boots) the code tries to access `.get` on a record and explodes before `_json_safe` runs, yielding a 500 (`Failed to load resource: the server responded with a status of 500` reproduced 2025-11-04). There is no instrumentation capturing the offending payload so regressions reappear after every container rebuild.
- **Cross-user bleed and consent flash** – `anwalts-frontend-new/pages/email.vue:1996-2050` reads a shared `localStorage` key `anwalt.email.connected` to preselect the inbox for any subsequent visitor on the same browser. When user B signs in after user A, the UI briefly renders user A’s inbox while `syncEmails()` is still firing with B’s token. Because `uiReady` is toggled only after the failing status fetch resolves, a consent flash still occurs even when the account is connected.
- **Cookie cleanup is incomplete on session change** – the frontend clears `active_email_account` on mount, but the backend never purges per-user cached Gmail state when a new Supabase session is established. After a container rebuild the FastAPI instance reuses Redis caches and the `active_account` pointer, so `/api/user/gmail/status` reports `connected: true` for the new user until another revoke occurs.
- **Lack of regression coverage** – there is no automated test verifying that switching users or rebuilding containers keeps the status endpoint healthy and the UI in sync. Manual smoke tests miss the stale-state scenario.

## Goals

1. Make `/api/user/gmail/status` deterministic: sanitize DB output before mutation, guarantee successful JSON serialisation, and surface diagnostics for any mismatch.
2. Eliminate cross-user leakage in the SPA by namespacing connection state with the authenticated user ID and clearing it whenever Supabase session changes.
3. Ensure consent state persists without flashing the consent screen once a user has granted access.
4. Provide automated coverage (backend + Playwright) for the regressions so future builds do not reintroduce them.

## Non-Goals

- Replacing the Gmail integration with a different provider.
- Redesigning the email UI beyond the state fixes and consent flash removal.
- Implementing message sending or multi-account switching (covered elsewhere).

## High-Level Approach

1. **Backend hardening**
   - Wrap `db.get_gmail_connection_status` in a dataclass serializer that converts asyncpg records to plain dicts before any `.get` usage (`database.py:1050`).
   - Extend `_json_safe` to handle `asyncpg.Record`, `datetime`, `UUID`, and `Decimal` explicitly and add structured debug logging (with user id and account id) behind a feature flag.
   - Add unit tests for the serializer covering mixed data shapes and cached records.
   - Reset cached Gmail state (`active_email_account`, Redis cache entries) when Supabase session tokens change or logout executes.

2. **Frontend state isolation**
   - Replace the global `anwalt.email.connected` key with a user-scoped variant (`anwalt.email.connected:<userId>`). Derive `userId` from the Supabase session that the page already reads for auth tokens.
   - Prevent pre-emptive `currentView = 'inbox'` until the status request resolves successfully; keep the skeleton visible until then to avoid consent flash.
   - On mount, reconcile cached connection state with the backend response and purge stale entries when the authenticated user ID changes.

3. **Session change detection**
   - Add a backend hook that invalidates the Gmail cache when `/auth/login` issues a session for a different user on the same client (compare new `sub` against any cookie-stored `active_email_account` user id).
   - Add a frontend watcher tied to `useSupabaseAuth()` so logging out or logging in as another user clears all Gmail localStorage entries and cancels outstanding fetch intervals.

4. **Regression coverage and observability**
   - Backend pytest: verify `/api/user/gmail/status` gracefully handles empty DB results, asyncpg records, and cache hits.
   - Playwright: scenario covering “user A links Gmail → logout → user B logs in → sees consent screen, no residual emails”, and a container-rebuild smoke test using seeded fixtures.
   - Emit new metric counters for status errors and stale-state resets, exposed via `/api/settings/overview`.

## Acceptance Criteria

- `/api/user/gmail/status` never returns 500 for any reachable data shape; when data is missing it responds with a well-formed 200 and `connected: false`.
- Signing out and logging in as another user always shows the consent screen until that user links Gmail; no prior inbox content is rendered.
- The consent view no longer flashes for already linked users; inbox skeleton transitions directly into the message list.
- Automated tests described above run in CI and pass locally.
- Deployment checklist executed (docker compose build backend/frontend, restart nginx) and recorded in the change tasks.

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Serializer changes hide legitimate errors | Add debug logging with sampling, and raise alerts if sanitised payloads exceed threshold |
| Clearing caches aggressively causes reconnect prompts | Scope resets to authenticated user changes only; keep existing consent for same user |
| Additional Playwright scenarios lengthen CI time | Gate tests behind tag and run in nightly suite plus pre-deploy smoke |

## Rollout

1. Implement and unit test backend serializer changes.
2. Patch frontend state handling, run Playwright suite (`npx playwright test tests/e2e/email.spec.ts`).
3. Build/redeploy backend and frontend containers, restart nginx, capture smoke results.
4. Update runbooks with new diagnostic logs and storage keys.
