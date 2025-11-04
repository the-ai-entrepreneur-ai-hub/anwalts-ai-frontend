## 1. Backend Foundations
- [x] 1.1 Create migration/DDL that adds `organization_settings`, `webhooks`, `webhook_logs`, `api_request_metrics`, and `users.is_active`.
- [x] 1.2 Extend database layer with CRUD helpers for settings, metrics aggregation, webhook registry, and API token lifecycle updates.
- [x] 1.3 Add FastAPI middleware to record per-endpoint request metrics into `api_request_metrics` with batching to avoid hot paths.

## 2. Settings API Surface
- [x] 2.1 Implement `/api/settings/overview` (KPIs, charts, system health) backed by live aggregations.
- [x] 2.2 Implement `/api/settings/api` endpoints for token list/create/revoke and endpoint metrics.
- [x] 2.3 Implement `/api/settings/webhooks` CRUD + test trigger, persisting logs.
- [x] 2.4 Implement `/api/settings/users` endpoints for listing, role change, activation toggle, and invite placeholder.
- [x] 2.5 Implement `/api/settings/preferences` GET/POST for general/security settings and enforce disabled-user login guard.
- [x] 2.6 Implement `/api/settings/export` routes for CSV and JSON snapshots.

## 3. Frontend Integration
- [x] 3.1 Add composables/services to call new settings APIs with proper auth handling.
- [x] 3.2 Replace static state in `pages/settings.vue` with reactive data from backend while preserving layout.
- [x] 3.3 Render analytics charts using SVG-based components fed by overview data.
- [x] 3.4 Wire buttons (refresh, test webhook, exports, toggles, API key lifecycle) to real actions with feedback toasts.

## 4. Validation & Release
- [ ] 4.1 Add backend unit tests for aggregations, settings persistence, webhook lifecycle, and API token security.
- [ ] 4.2 Extend Playwright coverage for settings admin flows (analytics refresh, API key create/revoke, webhook CRUD, user toggle, export download).
- [ ] 4.3 Update documentation/ops notes and verify docker image rebuild + migrations run cleanly.
