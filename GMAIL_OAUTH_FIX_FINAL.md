# Gmail OAuth Flow Fix

## Bug Summary
- Gmail linking redirects were proxied without forwarding backend `Set-Cookie` headers, so `/auth/google/authorize` cookies (`oauth_flow_mode`, `email_link_uid`) never reached browsers.
- Callback fell back to login mode because the cookies were missing, replacing the signed-in session with the Gmail account.

## Root Cause Analysis
- `proxyBackendRedirect` in `server/utils/oauthProxy.ts` created a redirect response via `sendRedirect` but attempted to copy cookies onto the returned value.
- `sendRedirect` returns a `Promise<void>` (no headers API), so the forwarded cookies were silently dropped and the browser never stored the flow markers.

## Implemented Changes
- Forward `Set-Cookie` headers from the backend response directly onto the current H3 event using `appendResponseHeader` before issuing the redirect.
- Normalize mixed header formats (`getSetCookie()` array vs. comma-separated string) via `splitCookiesString` to ensure every cookie is forwarded intact.

## Verification Steps
1. `npx nuxi typecheck` *(fails: repository has no tsconfig.json)*.
2. Manual reasoning: confirmed redirect proxy now appends cookies to the event before `sendRedirect`, ensuring Gmail linking callbacks receive `oauth_flow_mode=gmail` and remain in the linking branch.
3. Pending manual E2E validation of Gmail OAuth (requires Google consent flow and environment secrets).

## Next Actions
- Run Nuxt build + Docker rebuild to deploy once manual Gmail linking test passes.
- Add automated OAuth flow coverage when feasible (Playwright/Vitest) to prevent regressions.
