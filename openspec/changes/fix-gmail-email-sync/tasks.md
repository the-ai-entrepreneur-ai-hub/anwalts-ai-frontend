# Tasks – Gmail Email Sync Fix

1. Audit existing Gmail-related DB records and ensure seed users have refresh tokens; document any migrations required.
2. Implement backend Gmail client helper (token refresh + Gmail REST wrappers) and expose GET /api/email/labels and GET /api/email/list with pagination/search, plus POST /api/email/modify for label changes.
3. Add request/response schemas and permissions checks for the new endpoints; integrate rate limiting and detailed logging.
4. Update Nuxt server routes under server/api/email to proxy to the backend endpoints (remove direct Google token exchange).
5. Refactor pages/email.vue to consume real data: replace mock dataset on successful fetch, hook up load-more, search, and label tabs, and surface reconnect prompts on 401s.
6. Verify OAuth reconnect flow clears stale refresh tokens and replays consent persistence.
7. Add unit/integration tests (FastAPI + Vitest where feasible) covering happy path, token refresh failure, and unauthorized scenarios.
8. Manual QA on staging/live: login via Google, visit /email, confirm inbox/labels/search/modify actions reflect actual Gmail content, and check logging for errors.
