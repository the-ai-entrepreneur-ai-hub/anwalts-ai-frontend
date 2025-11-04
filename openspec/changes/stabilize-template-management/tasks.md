## 1. Backend API
- [x] 1.1 Add `/api/templates/insights` FastAPI route plus corresponding database helper for counts, recency, and category tallies.
- [x] 1.2 Ensure template CRUD endpoints return `updated_at` and accept optimistic concurrency tokens.
- [x] 1.3 Extend database layer to track template usage (e.g., document generation with `template_id`) so insights have real data.

## 2. Nuxt Server & Frontend
- [x] 2.1 Introduce Nuxt server proxy routes for templates (list/detail/create/update/delete/insights) with auth propagation.
- [x] 2.2 Refactor `pages/templates.vue` to rely on the new APIs, remove hard-coded sample data, and wire loading/error/empty states.
- [x] 2.3 Implement edit/duplicate/delete flows with optimistic UI updates and cache invalidation.
- [x] 2.4 Update Documents page template integration to refresh catalog state after apply/clear/navigation and handle stale selections gracefully.

## 3. Quality
- [x] 3.1 Add Playwright coverage for template list CRUD plus the Documents “apply → clear → reapply” sequence.
- [x] 3.2 Add backend integration/unit tests for `GET /api/templates`, `/api/templates/insights`, and template usage tracking.
