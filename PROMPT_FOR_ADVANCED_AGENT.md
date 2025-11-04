# CRITICAL BUG: Gmail OAuth Session Hijacking - Fix Required

## Problem Statement

**Symptom**: When a logged-in user (User A) tries to connect their Gmail account using a different email address (User B), the system logs out User A and logs in as User B instead of linking Gmail to User A's account.

**Expected Behavior**: User A should remain logged in, and User B's Gmail should be linked to User A's account (email section should be independent from login).

**Current Behavior**: User A gets logged out, User B gets logged in automatically (session hijacked).

---

## System Architecture

### Tech Stack
- **Backend**: FastAPI (Python) - `/root/backend-main.py`
- **Frontend**: Nuxt 3 (Node.js) - `/root/anwalts-frontend-new/`
- **Database**: PostgreSQL with `email_accounts` table
- **Deployment**: Docker Compose with 5 containers (nginx, frontend, backend, postgres, redis)
- **Site**: https://portal-anwalts.ai

### Key Files
1. **Backend OAuth Handler**: `/root/backend-main.py`
   - Line ~540: `google_authorize()` - Sets OAuth flow cookies and redirects to Google
   - Line ~694: `google_callback()` - Handles OAuth callback, detects flow mode

2. **Frontend OAuth Proxy**: `/root/anwalts-frontend-new/server/utils/oauthProxy.ts`
   - Proxies OAuth requests from browser to backend
   - Should forward cookies between backend and browser

3. **Database Layer**: `/root/database.py`
   - `set_gmail_refresh_token()` - Links Gmail account to user
   - `upsert_email_account()` - Creates/updates email account records

4. **Frontend Email Page**: `/root/anwalts-frontend-new/pages/email.vue`
   - User interface for Gmail linking

---

## OAuth Flow Design

### Gmail Linking Flow (What SHOULD Happen):
```
1. User A logged in → Browser has auth_token=TOKEN_A
2. User A clicks "Weiter mit Gmail" on /email page
3. Backend sets cookies:
   - oauth_flow_mode=gmail
   - email_link_uid=USER_A_ID
4. Redirect to Google OAuth
5. User authenticates with Gmail B
6. Google redirects back to /auth/google/callback
7. Backend reads cookies:
   - flow_mode=gmail (detects this is Gmail linking)
   - email_link_uid=USER_A_ID (knows which user to link to)
8. Backend links Gmail B to User A
9. User A stays logged in, Gmail B connected ✅
```

### Login Flow (What SHOULDN'T Happen for Gmail Linking):
```
1. User clicks "Login with Google"
2. Backend sets cookie: oauth_flow_mode=login
3. Redirect to Google OAuth
4. User authenticates with Google
5. Google redirects back to /auth/google/callback
6. Backend reads cookie: flow_mode=login
7. Backend creates/logs in as that Google account
8. New session created ✅ (This is correct for login)
```

---

## Recent Logs (Showing the Bug)

```
2025-10-27 13:18:34 - Login attempt for email: test.reg.e2e+20251026@anwalts.ai
2025-10-27 13:18:34 - JWT token created for user: 325cb3dc-e49e-4eb7-888a-f44ef9ff4faa
2025-10-27 13:18:34 - Session stored for user: 325cb3dc-e49e-4eb7-888a-f44ef9ff4faa

(User goes to /email, clicks "Weiter mit Gmail", authenticates with angelageneralao.1997@gmail.com)

2025-10-27 13:18:57 - Gmail refresh token stored for user angelageneralao.1997@gmail.com
2025-10-27 13:18:57 - Session stored for user 32c0e4e0-2c5d-4ad0-9729-57dbdf41c83e
2025-10-27 13:18:57 - OAuth login successful for: angelageneralao.1997@gmail.com
```

**Analysis**: The log says "OAuth login successful" which means it executed the LOGIN flow code path, not the Gmail linking flow!

---

## Your Task

**Investigate and fix the bug that causes Gmail linking to execute as login flow.**

### Investigation Guidelines:

1. **Start with the data flow**:
   - How does `oauth_flow_mode` cookie get from backend to browser?
   - Is the frontend proxy forwarding all headers correctly?
   - Are cookies being lost somewhere in the chain?

2. **Check cookie handling**:
   - Backend sets cookies in `/auth/google/authorize` response
   - Do those cookies reach the browser?
   - Are they sent back in `/auth/google/callback` request?

3. **Verify flow detection logic**:
   - How does `google_callback()` determine if it's Gmail linking vs login?
   - What happens if cookies are missing?
   - Are there default values that could cause wrong flow?

4. **Review recent fixes**:
   - Check git history or code comments for recent changes
   - Previous attempts may have addressed symptoms, not root cause
   - Look for TODO or FIXME comments

### Freedom to Explore:

- **Use any debugging approach**: Add logging, check network traces, review code
- **Question assumptions**: Previous fixes may be incomplete or wrong
- **Think critically**: The bug might be in an unexpected place
- **Verify end-to-end**: Don't assume intermediate layers work correctly

---

## Test Cases

### Test 1: Gmail Linking with Different Email ✅ PRIMARY TEST

**Steps**:
1. Login as `test.reg.e2e+20251026@anwalts.ai`
2. Verify logged in (check profile, see user name)
3. Navigate to `/email` page
4. Check both consent checkboxes
5. Click "Weiter mit Gmail" button
6. Authenticate with Google as `angelageneralao.1997@gmail.com`

**Expected Results**:
- ✅ Still logged in as `test.reg.e2e+20251026@anwalts.ai`
- ✅ Profile shows original user name (not Angela)
- ✅ Email page shows `angelageneralao.1997@gmail.com` in connected accounts
- ✅ Browser localStorage has original auth_token (unchanged)
- ✅ Backend logs: "Gmail account angelageneralao.1997@gmail.com linked to user 325cb3dc... - session preserved"

**Failure Indicators**:
- ❌ Logged in as Angela Generalao
- ❌ Profile shows "Angela Generalao"
- ❌ Browser localStorage has different auth_token
- ❌ Backend logs: "OAuth login successful for: angelageneralao.1997@gmail.com"

### Test 2: Gmail Linking with Same Email

**Steps**:
1. Login as `user@gmail.com`
2. Navigate to `/email` page
3. Click "Weiter mit Gmail"
4. Authenticate with Google as `user@gmail.com` (same email)

**Expected Results**:
- ✅ Still logged in as `user@gmail.com`
- ✅ Gmail linked to existing account
- ✅ No duplicate user created
- ✅ Session unchanged

### Test 3: Normal Google Login

**Steps**:
1. Logout completely
2. Navigate to `/login` or homepage
3. Click "Login with Google"
4. Authenticate with Google as `user@example.com`

**Expected Results**:
- ✅ Logged in as `user@example.com`
- ✅ New session created
- ✅ Redirected to `/dashboard`
- ✅ Backend logs: "OAuth login successful"

**This flow should NOT be affected by the fix!**

### Test 4: Cookie Verification (Debug Test)

**Steps**:
1. Login as User A
2. Open browser DevTools → Network tab
3. Click "Weiter mit Gmail"
4. Check the redirect response from `/auth/google/authorize`

**Expected Headers in Response**:
```
HTTP/1.1 302 Found
Location: https://accounts.google.com/o/oauth2/v2/auth?...
Set-Cookie: oauth_flow_mode=gmail; HttpOnly; Secure; SameSite=Lax; Max-Age=600; Path=/
Set-Cookie: email_link_uid=<USER_A_ID>; HttpOnly; Secure; SameSite=Lax; Max-Age=600; Path=/
```

**Verify**:
- ✅ Both Set-Cookie headers present in response
- ✅ Browser receives and stores cookies
- ✅ Cookies sent in subsequent request to `/auth/google/callback`

---

## Deployment Instructions

After fixing:

1. **Backend changes**:
   ```bash
   cd /root
   docker-compose build backend
   docker stop anwalts_backend && docker rm anwalts_backend
   docker-compose up -d backend
   ```

2. **Frontend changes**:
   ```bash
   cd /root/anwalts-frontend-new
   npm run build
   cd /root
   docker-compose build frontend
   docker stop anwalts_frontend && docker rm anwalts_frontend
   docker-compose up -d frontend
   ```

3. **Verify deployment**:
   ```bash
   docker ps --format "table {{.Names}}\t{{.Status}}"
   curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health
   ```

---

## Success Criteria

1. ✅ Test Case 1 passes (different email linking works)
2. ✅ Test Case 2 passes (same email linking works)
3. ✅ Test Case 3 passes (normal login still works)
4. ✅ Backend logs show "Gmail account linked" not "OAuth login successful"
5. ✅ User session is preserved during Gmail linking
6. ✅ No session hijacking occurs

---

## Hints (Read Only If Stuck)

<details>
<summary>Hint 1: Where to look first</summary>

The issue is likely in the communication between backend and browser. Check:
- Frontend OAuth proxy (`oauthProxy.ts`)
- How it forwards backend responses to browser
- Whether Set-Cookie headers are being forwarded

</details>

<details>
<summary>Hint 2: Common proxy issues</summary>

When proxying OAuth redirects, developers often:
- Extract only the Location header
- Forget to forward Set-Cookie headers
- Assume sendRedirect() automatically copies all headers (it doesn't!)

</details>

<details>
<summary>Hint 3: The exact problem</summary>

In `oauthProxy.ts`, the `proxyBackendRedirect()` function:
- Gets backend response with Location + Set-Cookie headers
- Calls `sendRedirect(event, location, status)`
- Returns redirect response WITHOUT copying Set-Cookie headers

Backend sets cookies → Frontend proxy doesn't forward them → Browser never gets cookies → Callback defaults to login flow

</details>

<details>
<summary>Hint 4: The fix</summary>

After creating the redirect response, you need to copy Set-Cookie headers from the backend response to the redirect response:

```typescript
const redirectResponse = sendRedirect(event, location, status)

// Forward Set-Cookie headers
const setCookieHeaders = response.headers.getSetCookie?.() || 
                          response.headers.get('set-cookie')
if (setCookieHeaders) {
  if (Array.isArray(setCookieHeaders)) {
    setCookieHeaders.forEach(cookie => {
      redirectResponse.headers.append('set-cookie', cookie)
    })
  } else if (typeof setCookieHeaders === 'string') {
    redirectResponse.headers.set('set-cookie', setCookieHeaders)
  }
}

return redirectResponse
```

</details>

---

## Documentation Requirements

After fixing, create:

1. **Fix Summary** (`/root/GMAIL_OAUTH_FIX_FINAL.md`):
   - What was the bug
   - Root cause analysis
   - What you changed
   - How to verify

2. **Test Results** (`/root/TEST_RESULTS.md`):
   - Results of all 4 test cases
   - Screenshots or logs proving it works
   - Any edge cases discovered

---

## Questions to Consider

1. Why would the backend cookies not reach the browser?
2. Is there an intermediate proxy layer that needs to forward headers?
3. How does the Nuxt server-side OAuth proxy work?
4. Are there other places where headers might be lost?
5. What happens if cookies are HttpOnly? (They should still work)
6. Could the issue be with cookie attributes (Path, Domain, SameSite)?

---

## Good Luck!

**Time Estimate**: 15-30 minutes for investigation + fix + testing

**Approach**: 
1. Read the code to understand the flow
2. Add debug logging if needed
3. Test cookie propagation
4. Fix the root cause
5. Verify with all test cases

**Remember**: Think critically. Don't assume previous fixes were correct. The bug might be simpler than it seems!
