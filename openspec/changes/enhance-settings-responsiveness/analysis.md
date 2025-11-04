# Settings Baseline Analysis

## Data Source Trace (Task 1.1)
- **Overview API (`backend-main.py:3780-3983`)**: Totals for users/documents/cases/api calls are live SQL counts, but `system_health` returns hard-coded uptime values and assumes Redis/webserver success; AI latency catches errors but still defaults uptime to 98.0.
- **Frontend defaults (`anwalts-frontend-new/pages/settings.vue:687-701`)**: Preference form seeds with `DEFAULT_ORG_SETTINGS` values and renders immediately, so toggles display "enabled" even if actual backend is `false` until hydration completes. `users`/`apiKeys` arrays also render instantly (no skeleton/disabled state).
- **User list (`settings.vue:318-407`)**: Uses computed `filteredUsers`; when fetch fails, UI still shows stale data with `Noch nie` placeholder.
- **API tokens (`settings.vue:160-212`)**: Display values rely on `loadApiTokens`, but refresh after mutation is manual (not triggered on revoke success), risking stale counts.

## Backend Metric Gaps (Task 1.2)
- **Uptime telemetry**: `system_health` uptime percentages are static; no aggregation from `api_request_metrics` or external monitoring.
- **API endpoint reconciliation**: KPI "API-Aufrufe" pulls sum of `api_request_metrics`, but there is no cross-check with `/api/settings/api/endpoints`; totals may diverge.
- **Integrations/templates**: Overview lacks counts for templates/webhooks even though UI cards imply platform breadth; data available via `/api/templates` et al. but not aggregated.
- **Caching safeguards**: Each overview request repeats ~10 queries without caching; heavy admin usage could stress DB.

## Responsive Audit (Task 1.3)
- **Header/Tabs (`settings.vue:7-69`)**: `responsive-stack` helper collapses at 768px, but on 360px the combined button row (`Aktualisieren` + timestamp) still overflows horizontally.
- **KPI Grid (`settings.vue:32-74`)**: Uses CSS grid with `xl:grid-cols-4`; below 640px cards stretch full-width but padding is tight; no skeleton states, causing jump.
- **Charts (`settings.vue:80-138`)**: Fixed `h-80` makes mobile view require excessive scroll; SVG lacks responsive container adjustments.
- **User Table (`settings.vue:338-407`)**: `min-w-full` table forces horizontal scroll on ≤414px with no visible indication; action buttons wrap awkwardly.
- **Modals (`settings.vue:465-560`)**: `showConfirmModal` uses fixed width without breakpoint adjustments; on small screens the modal nearly touches edges.

These findings align with user reports of non-responsive design and fabricated metrics. Next steps: implement telemetry-backed health data, add hydration gates/loading states, and refactor responsive layouts per proposal.
