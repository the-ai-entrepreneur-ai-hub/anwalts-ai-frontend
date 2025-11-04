## 1. Discovery & Analysis
- [x] 1.1 Trace every data source used on `pages/settings.vue` and document where placeholder values remain (overview KPIs, system health, preferences defaults, user list pagination).
- [x] 1.2 Review backend services (`backend-main.py`, `database.py`, `models.py`) to confirm which metrics are real versus derived constants and list the gaps.
- [x] 1.3 Audit responsive behavior at 360px, 768px, 1024px, and 1440px, noting components that overflow or collapse incorrectly (KPI grid, tables, toolbars, modals).

## 2. Backend Improvements
- [x] 2.1 Implement real uptime/latency aggregation for PostgreSQL, Redis, AI, and web server entries returned by `/api/settings/overview`.
- [x] 2.2 Expose canonical totals (users, documents, templates, integrations) through overview and companion endpoints so KPI cards reconcile with downstream lists.
- [x] 2.3 Add caching/ batching safeguards to prevent new metrics queries from generating hot paths under production traffic.
- [x] 2.4 Extend unit/integration tests covering the new aggregations and reconciliation helpers.

## 3. Frontend Enhancements
- [x] 3.1 Introduce a hydration gate (skeletons + disabled controls) that keeps settings actions inactive until their API calls resolve, and re-hydrates after mutations succeed.
- [x] 3.2 Replace remaining hard-coded defaults with reactive data providers/composables that subscribe to backend responses.
- [x] 3.3 Rework responsive layout for analytics cards, KPI grids, tables, and modals to support stacking or horizontal scroll on small breakpoints without visual regressions.
- [x] 3.4 Update settings-specific Pinia/composables (if any) to emit events when data refreshes so the overview and detail tabs stay in sync.
- [ ] 3.5 Expand Playwright coverage to exercise admin flows on narrow (≤414px) and wide (≥1280px) viewports, asserting live metrics and responsive layout markers.

## 4. Verification & Rollout
- [x] 4.1 Run the full pytest suite plus new backend tests; address failures.
- [ ] 4.2 Execute the updated Playwright specs against a Nuxt preview with responsive viewports.
- [ ] 4.3 Update deployment/runbooks to describe the new metrics sources, caching expectations, and responsive testing steps.
- [ ] 4.4 Rebuild and redeploy backend/frontend containers, confirming migrations (if any) and basic smoke checks post-deploy.
