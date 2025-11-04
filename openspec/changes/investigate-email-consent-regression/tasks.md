## 1. Discovery & Verification
- [x] 1.1 Reproduce the consent regression and capture network traces (status, payloads, cookies).
- [x] 1.2 Trace the OAuth → proxy → backend call chain and document available auth artefacts at each hop.
- [x] 1.3 Confirm backend state (email_accounts, user_email_preferences, ai consent flags) for affected users.

## 2. Proxy & Client Updates
- [x] 2.1 Extend `resolveBackendAuthHeader` to accept forwarded Authorization / `x-portal-auth` headers with validation.
- [x] 2.2 Update email API server routes to use the improved helper and emit structured diagnostics.
- [x] 2.3 Update frontend email calls to forward the SPA token via the agreed header while retaining cookie support.
- [x] 2.4 Ensure consent persistence keeps `ai_read_consent` in sync post-OAuth.

## 3. Testing & Instrumentation
- [x] 3.1 Add backend unit coverage for the new helper branches (Authorization header, cookie-only, Supabase session).
- [x] 3.2 Add Playwright coverage for the consent → inbox happy path and error handling.
- [ ] 3.3 Verify logging/metrics appear in container logs (proxy auth, email list success/failure).

## 4. Deployment & Documentation
- [x] 4.1 Rebuild backend and frontend images; restart nginx; document timestamps.
- [ ] 4.2 Run live smoke checks (email list, AI summary refresh) and record results.
- [ ] 4.3 Update runbooks with the new authentication hand-off and recovery steps.
- [ ] 4.4 Mark this checklist complete once all tasks are done.
