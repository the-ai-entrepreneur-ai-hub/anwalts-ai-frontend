## Why
- Recent settings overhaul still leaks placeholder values. The overview API (`backend-main.py:3952-3974`) hard-codes uptime percentages and assumes services are "Betriebsbereit", so administrators still see fake health metrics.
- The Vue page seeds every preference toggle with optimistic defaults (`anwalts-frontend-new/pages/settings.vue:687-701`) and renders the user table immediately, making the UI show fabricated states until API calls finish or fail.
- Key layouts (analytics header, KPI grid, user table) rely on desktop spacing and lack mobile fallbacks. The user grid table (`settings.vue:338-407`) overflows on <768px, and status/toolbars do not collapse cleanly even with the current `.responsive-stack` helper, causing the "squeezed" appearance reported on phones.
- Customers need confidence that growth metrics really reflect production activity (e.g., "users who have created their account") and that every card/button interacts with live endpoints. We still need an explicit contract to reconcile KPI numbers with the downstream `/api/settings/users` and `/api/settings/api/*` payloads.

## What Changes
- Extend the settings backend to compute real service health (uptime, latency) instead of constants, and expose canonical counts for users, documents, templates, and active integrations so overview KPIs align with other endpoints.
- Add a hydration layer on the frontend that blocks interactivity until the corresponding API data arrives, supplies skeleton/loading states, and guarantees values stay in sync after mutations (API key revoke, webhook test, user toggle, preference save).
- Refactor responsive styles for header, KPI grid, charts, tables, and detail cards so the layout stacks gracefully from 320px–1440px. Introduce horizontal scroll or stacked cards where tabular data cannot collapse without loss.
- Instrument the UI and service layers with regression coverage: component/unit tests for hydration helpers, Playwright specs walking the admin flows on narrow and wide viewports, and backend tests verifying newly reported metrics.

## Impact
- Backend work may add lightweight queries against `api_request_metrics`, `webhook_logs`, or Redis to derive uptime/latency and will require defensive caching to avoid hot paths.
- Frontend changes will introduce additional composables/state management and possibly CSS utilities for breakpoint handling; we must keep bundle growth minimal.
- Expanded automated tests (pytest + Playwright) will lengthen CI runtime but are necessary to keep the settings surface stable.
- Deployment requires coordinated database migrations (if we add new aggregates) and a full frontend rebuild to ship the responsive layout updates.
