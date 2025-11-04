## Tasks
- [x] 1. Encode the OAuth flow mode in the authorize + callback handlers and default redirects to `/dashboard` when the flow is plain login.
- [x] 2. Strip or ignore stale Gmail return markers during login and only keep them for explicit Gmail consent flows.
- [x] 3. Update frontend Gmail connect helpers to use session-scoped markers and verify dashboard redirect on standard Google login.
- [x] 4. Run `openspec validate fix-google-login-redirect --strict` and smoke-test Google login + Gmail connect manually.
