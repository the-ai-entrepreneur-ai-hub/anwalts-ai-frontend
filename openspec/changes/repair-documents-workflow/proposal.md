## Why
- Document generation endpoints currently reject legitimate browser requests because they still depend on the strict `HTTPBearer` flow instead of the flexible cookie/Bearer authentication used by the assistant endpoints, leading to 401/403 responses on `/api/templates`, `/api/ai/generate-document`, `/api/documents/*` (`backend-main.py:1378-2166`).
- The Nuxt documents page (`anwalts-frontend-new/pages/documents.vue:244-711`) hardcodes templates and clause metadata, bypassing the backend catalog and making the UI appear unresponsive when API calls fail.
- `/api/ai/generate-document-simple` swallows Together API failures and emits the generic copy “Ich konnte die Antwort …” (`backend-main.py:2487-2533`), so users see “nothing happens” instead of actionable errors and the system silently stores useless drafts.
- Template persistence APIs are inconsistent (`backend-main.py:1406-1459` vs `database.py:448-520`), so even authenticated requests will fail once enabled.

## What Changes
- Extend authentication parity: refactor document-related FastAPI routes to use `get_current_user_flexible`, and add Nuxt server-side proxies so browser requests automatically attach backend tokens when available (mirroring `server/api/ai/complete.post.ts`).
- Replace the hard-coded template and clause seed data on the documents page with data fetched from the backend (with graceful fallback messaging) and surface loading/error states tied to actual API calls.
- Tighten Together API handling: surface non-2xx responses as HTTP errors, avoid returning fallback prose as “documents”, and include Together metadata in successful responses for preview annotations.
- Reconcile template persistence models so REST payloads use `title` consistently and responses include `document_type`, `created_at`, and `updated_at` in the shape expected by the frontend.
- Add basic health telemetry (console + toast) for upload sanitization, template fetch, document generation, and submission flows so failures are observable end-to-end.

## Impact
- Requires coordinated updates in both `backend-main.py` and `anwalts-frontend-new/pages/documents.vue`, plus supporting utilities under `anwalts-frontend-new/server/api`.
- Minimal migration risk: database schema stays the same, but we must ensure `documents.status` column auto-heal still works.
- Deployment needs backend + frontend rebuild/restart; no new infrastructure dependencies.
