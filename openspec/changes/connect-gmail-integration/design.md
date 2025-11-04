# Gmail Integration Design

## Context

The portal currently has a fully-designed email UI (email.vue) that displays mock data and includes consent screens for OAuth connection. Gmail API routes exist in the frontend (`/api/email/list`, `/api/email/modify`, `/api/email/labels`) but are not connected to the authentication flow. The legal-rag-api AI model is deployed and functional for assistant chat.

**Constraints:**
- Must use existing Google OAuth credentials (Client ID: <REDACTED_GOOGLE_CLIENT_ID>)
- Must preserve existing email UI design
- Must not break current profile authentication flow
- Gmail API already enabled in Google Cloud Console
- Backend uses FastAPI, frontend uses Nuxt 3

**Stakeholders:**
- Legal professionals needing email management
- Users already authenticated via Google OAuth for profile access

## Goals / Non-Goals

**Goals:**
- Enable users to connect Gmail and view real emails with existing UI
- Process emails with AI for summaries, categorization, and draft responses
- Maintain security with encrypted token storage
- Handle Gmail API rate limits and errors gracefully

**Non-Goals:**
- Email sending functionality (read-only for now, modify for labels only)
- Support for non-Gmail email providers (Outlook, etc.)
- Email search/filtering beyond Gmail API labels
- Real-time email notifications (polling-based refresh only)

## Decisions

### 1. OAuth Scope Addition
**Decision:** Add Gmail API scopes to existing Google OAuth flow with `access_type=offline` and `prompt=consent`

**Rationale:**
- OAuth flow already configured and working for profile authentication
- `offline` access type provides refresh token for persistent API access
- `prompt=consent` ensures users see and approve Gmail access explicitly
- Refresh tokens don't expire unless revoked, reducing re-authentication friction

**Scopes to add:**
- `https://www.googleapis.com/auth/gmail.readonly` - Read emails, threads, labels
- `https://www.googleapis.com/auth/gmail.modify` - Modify labels (star, read/unread, archive)

**Implementation:**
```python
# backend-main.py line 356
scope = urllib.parse.quote("openid email profile https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.modify")
```

### 2. Refresh Token Storage
**Decision:** Store Gmail refresh token in user_profiles JSONB data field, encrypted at rest

**Rationale:**
- Refresh tokens are long-lived credentials requiring secure storage
- JSONB field allows flexible schema without migration
- Encryption prevents token leakage from database dumps
- Per-user storage enables multi-account support later

**Schema:**
```python
# database.py
user_profiles.data['gmail_refresh_token'] = encrypted_token
user_profiles.data['gmail_consent_timestamp'] = timestamp
user_profiles.data['gmail_connected'] = True
```

**Alternatives considered:**
- Cookie storage (`gmail_rt`) - REJECTED: Security risk, size limits, client-side exposure
- Separate table - REJECTED: Overkill for single field, complicates queries
- Environment variable - REJECTED: Not per-user, doesn't scale

### 3. Frontend-Backend Token Flow
**Decision:** Backend stores refresh token in database, frontend receives connection status via /api/user/profile

**Rationale:**
- Refresh tokens never exposed to frontend JavaScript
- Frontend only needs to know connection state (boolean)
- Backend handles token refresh transparently
- Reduces attack surface for token theft

**Flow:**
1. User clicks "Connect Gmail" → Frontend redirects to backend OAuth authorize endpoint
2. User approves Gmail scopes → Google redirects to backend callback
3. Backend exchanges code for tokens → Stores refresh token in database → Sets session cookie
4. Backend redirects to /email → Frontend checks connection status
5. Frontend calls /api/email/list → Backend uses stored refresh token → Returns emails

### 4. Email Data Mapping
**Decision:** Map Gmail API response to existing email.vue data structure without UI changes

**Existing UI expects:**
```typescript
{
  id: string,
  sender: { name: string, email: string, initials: string },
  subject: string,
  snippet: string,
  date: Date,
  type: string, // 'Contracts', 'Terminations', 'Reminders', etc.
  status: string, // 'Ungelesen', 'Read', 'AI Draft', 'AI Pending'
  priority: string, // 'High', 'Normal'
  hasAttachment: boolean,
  starred: boolean
}
```

**Gmail API provides:**
```json
{
  "id": "msg_id",
  "threadId": "thread_id",
  "labelIds": ["INBOX", "UNREAD", "STARRED"],
  "payload": {
    "headers": [{"name": "From", "value": "..."}],
    "parts": [...]
  },
  "snippet": "...",
  "internalDate": "1234567890"
}
```

**Mapping logic** (already implemented in `/api/email/list.get.ts`):
- Extract sender from `From` header
- Parse name/email with regex
- Generate initials from sender name
- Map UNREAD label → status
- Detect subject keywords for type classification
- IMPORTANT label → High priority

### 5. AI Processing Architecture
**Decision:** Create `/api/email/process` endpoint that calls legal-rag-api synchronously with 30s timeout

**Rationale:**
- legal-rag-api already deployed and tested with assistant chat
- Synchronous processing simplifies error handling
- 30s timeout prevents UI hangs
- Processing results cached in database to avoid re-processing

**Endpoint design:**
```python
@app.post("/api/email/process")
async def process_email(request: ProcessEmailRequest):
    # 1. Verify user has Gmail connected
    # 2. Fetch full email body from Gmail API
    # 3. Extract text content from HTML/plain parts
    # 4. Call legal-rag-api with: {"question": email_content, "k": 6}
    # 5. Parse response for summary, categories, draft
    # 6. Store in database: email_processing_results table
    # 7. Return processed data to frontend
```

**AI Prompts:**
- **Summary:** "Summarize this legal email in 2-3 sentences: {email_body}"
- **Categorization:** Keyword detection + AI classification (contract, termination, reminder, general)
- **Draft response:** "Generate a professional legal response draft to: {email_body}"

**Alternatives considered:**
- Async processing with job queue - REJECTED: Adds complexity, user expects immediate results
- Batch processing all emails - REJECTED: Rate limits, high latency, unnecessary for unused emails
- Client-side AI calls - REJECTED: Exposes model endpoint, CORS issues, no caching

### 6. Rate Limiting Strategy
**Decision:** Implement per-user rate limiting with Redis (if available) or in-memory fallback

**Gmail API Quotas:**
- 1 billion quota units/day per user
- List messages: 5 units
- Get message: 5 units
- Modify message: 5 units
- ~200 million requests/day theoretical max

**Portal Rate Limits:**
- Email list: 60 requests/hour/user (enough for auto-refresh every minute)
- Email process: 20 requests/hour/user (AI processing expensive)
- Email modify: 100 requests/hour/user (star, read/unread actions)

**Implementation:**
```python
@rate_limit(requests=60, window=3600, resource="email_list")
async def list_emails():
    ...
```

**Error handling:**
- 429 Too Many Requests → Show "Rate limit exceeded, try again in X minutes"
- Exponential backoff: 1s, 2s, 4s, 8s, 16s
- Log rate limit hits for monitoring

### 7. Token Refresh Mechanism
**Decision:** Transparent token refresh in Gmail API middleware

**Flow:**
1. Frontend calls /api/email/list
2. Backend retrieves stored refresh token
3. Backend checks if access token cached (15min TTL)
4. If expired, exchange refresh token for new access token
5. Cache new access token in Redis/memory
6. Make Gmail API call
7. Return results

**Refresh token expiry handling:**
- Refresh tokens can be revoked by user or expire after 6 months of inactivity
- On 401 Unauthorized from token refresh → Clear stored token → Return `{error: 'not_linked'}`
- Frontend detects `not_linked` → Show re-authentication prompt
- User clicks reconnect → OAuth flow repeats

**Advantages:**
- No frontend changes needed for token refresh
- Single source of truth for token state (backend database)
- Graceful degradation on token expiry

## Risks / Trade-offs

### Risk: OAuth Scope Creep Alarm
**Problem:** Users who already authenticated may be alarmed by new Gmail permission request

**Mitigation:**
- Explicit consent screen in email.vue explaining what access is needed and why
- Clear privacy policy link
- "I agree" checkboxes for OAuth and AI reading
- Separate email connection from main authentication (optional feature)

### Risk: Gmail API Rate Limit Exhaustion
**Problem:** Heavy users or bugs could exhaust daily quota

**Mitigation:**
- Per-user rate limiting enforced by backend
- Pagination limits (max 25 emails per request)
- Cache email metadata (refresh every 5 minutes max)
- Monitor quota usage in Google Cloud Console
- Implement backoff on 429 errors

### Risk: Refresh Token Theft
**Problem:** Database compromise could expose refresh tokens

**Mitigation:**
- Encrypt tokens at rest using Fernet encryption
- Encryption key stored in environment variable (JWT_SECRET reused)
- Database column access auditing
- Automatic token revocation on password reset
- Short-lived access tokens (15min cache only)

### Risk: AI Processing Hallucination
**Problem:** Legal-rag-api might generate incorrect summaries or draft responses

**Mitigation:**
- Display AI outputs with clear "AI-generated" labels
- Never send AI-drafted emails automatically (review required)
- User setting: "AI read access" can be disabled
- Log all AI processing for quality review
- Add confidence scores if model supports it

### Trade-off: Read-Only vs Full Access
**Decision:** Request both `gmail.readonly` and `gmail.modify` scopes

**Rationale:**
- Users expect to star emails, mark as read, archive
- Modify scope doesn't include sending (requires `gmail.send` scope)
- Future functionality (archive, delete) requires modify access
- Better to request once than re-prompt later

**Downside:** Slightly broader permission request, but scope is still limited to metadata modification

## Migration Plan

### Phase 1: OAuth Enhancement (Non-Breaking)
1. Update backend OAuth scope string
2. Add refresh token storage in database
3. Deploy backend (existing users unaffected)
4. Test OAuth flow in development

**Rollback:** Revert scope string, no data migration needed

### Phase 2: Frontend Integration
1. Update email.vue to connect consent screen to OAuth
2. Replace mock data with API calls
3. Deploy frontend
4. Monitor error logs for API failures

**Rollback:** Revert frontend to mock data, OAuth changes remain

### Phase 3: AI Processing (Optional Feature)
1. Deploy AI processing endpoint
2. Enable AI summary display in UI
3. Monitor processing success rate
4. Adjust prompts based on quality feedback

**Rollback:** Remove AI UI elements, disable endpoint

### Success Metrics
- 80% of users successfully connect Gmail within first session
- <1% OAuth error rate
- <5s median email list load time
- >90% AI summary accuracy (manual review sample)
- Zero refresh token leaks

## Open Questions

1. **Email Attachment Handling:** Should we download and display attachment previews, or just show metadata?
   - **Proposal:** Metadata only (filename, size) with "Open in Gmail" link to avoid storage costs

2. **Multiple Email Account Support:** Should users be able to connect multiple Gmail accounts?
   - **Proposal:** Defer to v2, single account sufficient for MVP

3. **Email Search:** Should we implement search beyond Gmail's label filtering?
   - **Proposal:** Use Gmail API's `q` parameter for server-side search, defer advanced filters to v2

4. **Offline Mode:** Should we cache emails locally for offline viewing?
   - **Proposal:** No offline mode, require internet connection (legal context requires real-time accuracy)

5. **Email Threading:** Should we display threaded conversations or individual messages?
   - **Proposal:** Individual messages for MVP, threading adds UI complexity
