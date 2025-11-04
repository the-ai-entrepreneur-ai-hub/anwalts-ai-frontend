# Tasks: add-template-import-workflow

- [x] Restyle the template modal (desktop + mobile) to match design tokens and ensure inputs remain accessible.
- [x] Implement frontend import workflow: file picker, loading state, API call to `/api/templates/import`, success/error handling, catalogue refresh.
- [x] Add Nuxt server proxy route and FastAPI endpoint that ingests the upload, calls AI to draft the template, and stores the result.
- [x] Cover the new flow with automated tests (Playwright + backend unit tests) and update docs/messages as needed.
