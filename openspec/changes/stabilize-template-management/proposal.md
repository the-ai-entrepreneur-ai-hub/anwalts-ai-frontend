## Why
- The Templates page never calls the real backend: `loadTemplates()` fetches `/api/auth/proxy.get` and then splices in eight hard-coded sample records, so authenticated users still see static data and CRUD operations silently fail (`anwalts-frontend-new/pages/templates.vue:412-676`).
- Actions such as create/duplicate/delete do not invoke REST endpoints (e.g. `deleteTemplate` only shows a toast and reloads the in-memory list), leaving the template library unusable (`templates.vue:604-678`).
- Highlight metrics, suggestions, and clause rails are hard-coded arrays, so the UI misrepresents usage and cannot reflect production activity (`templates.vue:414-454`).
- On the Documents page the inline quick-pick list shares stale state: after using a template, clearing, or returning from the Templates page, the next selection can fail because the store is not refreshed or reconciled with backend updates (`documents.vue:745-787`, `documents.vue:1248-1266`).

## What Changes
- Replace ad-hoc proxy calls with Nuxt server APIs that call `/api/templates` and `/api/clauses`, remove baked-in sample data, and surface loading/empty/error states that reflect real backend responses.
- Implement full template CRUD wiring on the frontend (list/create/update/delete/duplicate) using the existing FastAPI endpoints, including optimistic locking on `updated_at` and client-side cache invalidation.
- Add backend support for template insights (active count, recent updates, top categories, recommended templates) and expose them via a dedicated `GET /api/templates/insights` endpoint so all prominent UI cards render dynamic content.
- Harden the Documents workflow so template selection is idempotent: whenever a user applies, clears, or imports a template, the inline list refreshes from the catalog, maintains selection state, and allows immediate reuse.
- Back the changes with integration and Playwright coverage for “load → apply → clear → reapply” flows and template CRUD success/error cases.

## Impact
- Touches both frontend (`anwalts-frontend-new/pages/templates.vue`, shared composables/stores, documents page) and backend (`backend-main.py`, `database.py`, potential migrations for template metadata).
- Requires new server API routes under `anwalts-frontend-new/server/api/templates/*` to proxy insights and CRUD calls with proper auth.
- Demands coordinated deployment of backend and frontend containers; no external services change, but new tests will target `/api/templates` and `/api/templates/insights`.
