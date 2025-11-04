# Design Notes - Gmail Email Sync Fix

## Current State Observations
- Google OAuth callback persists the refresh token into user_profiles.data.gmail_refresh_token and optionally sets an httponly cookie gmail_rt.
- Nuxt server routes (server/api/email/*.ts) depend entirely on gmail_rt; they refresh access tokens client-side and call Gmail REST APIs directly.
- When the cookie is absent (common after Supabase-managed login or different subdomain), the routes return not_linked, causing the UI to revert to static mock data.
- Backend exposes /api/user/gmail/status|consent|revoke and /api/email/process but lacks endpoints to list, label, or modify Gmail messages.

## Proposed Architecture
1. Server-side Gmail Gateway
   - Add FastAPI helpers that accept current_user, read the encrypted refresh token via db.get_gmail_refresh_token, exchange it for an access token (with retry/backoff), and perform Gmail REST calls.
   - Normalize Gmail responses into lightweight DTOs consumed by the UI (id, threadId, sender, subject, snippet, labels, unread/starred flags, internal date, history id).
   - Provide pagination tokens and permit optional label, query, and max-result parameters. Persist the last sync timestamp when successful to support UX metrics.

2. Frontend API Proxy Simplification
   - Nuxt server routes become thin proxies to the backend endpoints, forwarding auth headers and query/body parameters while mapping backend errors to consistent JSON payloads.
   - Remove refresh-token handling, reducing surface area for leaks and inconsistent cookies.

3. UI Data Flow
   - On mount, email page calls /api/user/gmail/status; if connected, immediately fetch labels + inbox messages using backend APIs.
   - Replace mock data injection once real data arrives; keep placeholder only for disconnected state or empty inbox messaging.
   - Wire Load more to pass the pageToken returned by the backend, append results, and update counts. Search submits Gmail q queries. Folder tabs map to Gmail label IDs (INBOX, STARRED, SENT, DRAFT, IMPORTANT/SNOOZED etc.).
   - Maintain existing UI/UX while swapping underlying data sources; show spinners/error toasts when backend says not_linked or token_refresh_failed.

4. Reconnection and Token Failure
   - Backend returns 401/409 style responses when refresh token missing/expired; frontend interprets and prompts user to reconnect via OAuth (persisting consent and redirect).
   - Ensure revoke endpoint clears server token and cookies, forcing re-consent.

## Alternatives Considered
- Continue using H3 routes to talk to Gmail: rejected due to cookie fragility and token exposure.
- Proxy Gmail via the Nuxt server runtime: unnecessary; FastAPI already hosts user-context APIs and has DB/token access.
- Poll Gmail via a background worker: over-engineered for immediate fix.

## Open Questions / Follow-up
- Confirm Gmail API quotas to size pagination defaults (initially 25 messages).
- Consider caching label metadata per user to reduce repeated Gmail hits; out of scope but helpers should be extensible.

## Deployment Considerations
- Requires rebuilding backend image after merging due to route additions (no new Python dependencies anticipated).
- Frontend rebuild to ship proxy and UI updates.
