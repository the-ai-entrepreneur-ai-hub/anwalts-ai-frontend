# Design: stabilize-email-connection

## 1. Backend hardening

### 1.1 Dedicated serializer
- Add `serialize_email_status(status: dict, user_id: uuid.UUID)` in `backend-main.py` (near `_json_safe`) that:
  - Accepts raw result from `db.get_gmail_connection_status`.
  - Converts any `asyncpg.Record` or custom objects to dicts before field access.
  - Normalises timestamps to ISO strings and UUIDs to strings.
- Call this helper before any `.get` usage in `/api/user/gmail/status`, so even malformed payloads never raise.

### 1.2 Database layer adjustments
- Update `database.py:get_gmail_connection_status` to ensure it returns plain dicts (`dict(record)` for `active_account` and each account).
- When user context changes (new login or logout), call `clear_active_email_account` and delete Redis cache keys (`email:status:<user_id>` if present).

### 1.3 Observability
- Introduce `logger.warning` entry with structured fields `{user_id, account_id, issue}` when sanitising an unexpected shape.
- Surface a counter via existing metrics table for status sanitisation events; reuse `record_api_metric`.

### 1.4 Tests
- Extend `tests/backend/test_email_accounts.py` with fixtures covering:
  - asyncpg.Record mocks (dict-like) passed into serializer.
  - Empty account list and status fallback.
  - Cache reset on login (simulate new token).

## 2. Frontend isolation

### 2.1 Auth-aware storage key
- Acquire Supabase user ID via `useSupabaseUser()` or existing composable.
- Replace `localStorage.getItem('anwalt.email.connected')` with a helper:
  - `const storageKey = \`anwalt.email.connected:${userId}\``.
  - When user ID changes, remove all `anwalt.email.connected:*` keys belonging to previous users.

### 2.2 View gating
- Keep `currentView` default `'consent'`. Do not set `'inbox'` until a 200 status with `connected: true` returns.
- Display skeleton until both `uiReady` and `statusResolved` flags are true.
- If status returns 401/500, clear timers and ensure mock inbox is not rendered.

### 2.3 Logout/login watcher
- Subscribe to Supabase auth state (`supabase.auth.onAuthStateChange`) to clear intervals, storage keys, and cookies when the session user changes.
- Re-run `syncEmails` only when the authenticated user remains unchanged.

### 2.4 Tests
- Add `tests/e2e/email.spec.ts` scenarios:
  - `user-switch` scenario verifying consent screen.
  - `container-restart` stub by resetting fixtures and repeating status fetch.
- Add Vitest unit test for new storage helper to ensure correct key derivation.

## 3. Deployment steps

- `npm run lint` / `npm run build` in `anwalts-frontend-new`.
- `pytest tests/backend/test_email_accounts.py -k email_status`.
- `docker compose build backend frontend --no-cache`.
- `docker compose up -d --no-deps backend frontend`.
- `docker compose restart nginx`.
- Smoke: `curl -k https://portal-anwalts.ai/api/user/gmail/status` (authenticated token) and verify Playwright scenario.
