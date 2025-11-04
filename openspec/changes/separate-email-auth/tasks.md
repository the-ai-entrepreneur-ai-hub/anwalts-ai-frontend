## 1. Planning
- [ ] 1.1 Review current Gmail flow (`backend-main.py` + Nuxt server routes) to document assumptions.
- [ ] 1.2 Confirm migration path for existing `user_profiles.data` Gmail fields.

## 2. Data Model & Migration
- [ ] 2.1 Design new `email_accounts` (and supporting) tables; draft SQL migration.
- [ ] 2.2 Implement asyncpg helpers in `database.py` for CRUD and selection.
- [ ] 2.3 Write migration/backfill script for existing Gmail tokens into new tables.

## 3. Backend Integration
- [ ] 3.1 Update Gmail OAuth endpoints to target the new data model.
- [ ] 3.2 Refactor email reading endpoints to require explicit account selection.
- [ ] 3.3 Adjust auth/session handling so logout clears selected email account.
- [ ] 3.4 Extend tests (pytest) for the new flows.

## 4. Frontend Integration
- [ ] 4.1 Update Nuxt server routes to work with account selection and fallback.
- [ ] 4.2 Add UI prompts / state to pick or connect an email account.
- [ ] 4.3 Cover new behavior with Playwright/Vitest tests.

## 5. Documentation
- [ ] 5.1 Update `docs/data-model.md` with the new entities and diagrams.
- [ ] 5.2 Document migration and rollback steps in RELEASE_NOTES / ops docs.
