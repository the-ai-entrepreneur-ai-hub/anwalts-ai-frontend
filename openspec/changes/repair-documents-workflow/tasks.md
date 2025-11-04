ng!!!
## 1. Backend alignment
- [x] 1.1 Switch document/template routes to `get_current_user_flexible`
- [x] 1.2 Normalize template CRUD payloads & DB return fields (title/type/created_at/updated_at)
- [x] 1.3 Update `/api/ai/generate-document(-simple)` to surface Together failures as HTTP errors and return structured metadata on success

## 2. Frontend integration
- [x] 2.1 Add Nuxt server API proxies for document/template calls with cookie/Bearer fallback
- [x] 2.2 Replace hard-coded template/clause data with backend-driven state + UX for loading/failure
- [x] 2.3 Surface generation/upload/save status banners tied to real responses

## 3. Validation
- [x] 3.1 Unit/integration tests covering template fetch, document generation error path, and flexible auth cookie flow
- [x] 3.2 Manual QA plan for uploads, generation, save/export, and clause toggles
