## Why
- The settings page surfaces fabricated metrics, hard-coded API data, and placeholder system health information that do not reflect production usage.
- Critical admin flows (API key lifecycle, webhook management, user role toggles, exports) are non-functional, blocking operations and audit readiness.
- Security toggles and platform preferences do not persist anywhere, so admins cannot control enforcement baselines (2FA, SSO, password policy, language/timezone).

## What Changes
- Introduce a structured settings service in the backend that exposes live analytics, system health, user management, webhook registry, API token lifecycle, and export endpoints.
- Persist organization-wide preferences (locale, timezone, enforcement toggles, password policy) and update authentication flows to respect disabled users.
- Capture per-endpoint request metrics via middleware so the admin UI can display real API usage and latency charts.
- Replace the hard-coded Vue state on `pages/settings.vue` with composables that hydrate from the new endpoints while keeping the existing layout.
- Implement CSV/JSON export generation for core entities (users, documents, templates, webhooks) with streaming responses suitable for audit download.

## Impact
- Database migration adds `organization_settings`, `webhooks`, `webhook_logs`, `api_request_metrics` tables and an `is_active` column on `users`.
- New FastAPI routes under `/api/settings/*` plus middleware may increase baseline query traffic; ensure indexes on date columns.
- Frontend gains new composables/stores and lightweight SVG chart rendering; bundle impact must stay minimal.
- Requires new unit/integration tests for analytics aggregation, API token lifecycle, webhook CRUD, and Playwright coverage for admin flows.
