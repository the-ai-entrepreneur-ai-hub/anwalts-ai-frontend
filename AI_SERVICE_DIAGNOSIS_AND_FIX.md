# 🔍 Anwalts-AI Service Complete Diagnosis & Fix

**Date:** 2025-10-17  
**Status:** ✅ ROOT CAUSE IDENTIFIED  
**Priority:** 🔴 CRITICAL - Service is non-functional

---

## 🎯 Executive Summary

**PROBLEM:** Users cannot communicate with the AI service. All requests to `/api/ai/complete` return `403 Forbidden`.

**ROOT CAUSE:** Middleware routing conflict causing authentication bypass.

**SOLUTION:** One-line fix in middleware configuration.

---

## 🔴 The Problem

### Observed Symptoms

```bash
# Backend logs showing 403 errors
INFO: 172.19.0.7:40672 - "POST /api/ai/complete HTTP/1.1" 403 Forbidden
INFO: 172.19.0.7:60148 - "POST /api/ai/complete HTTP/1.1" 403 Forbidden
```

### User Experience
- User logs in successfully via Google OAuth ✅
- User navigates to /assistant page ✅
- User sends a message ✅
- Frontend calls /api/ai/complete ❌
- **Gets 403 Forbidden error** ❌
- AI never responds ❌

---

## 🔬 Root Cause Analysis

### Architecture Overview

```
Frontend (Browser)
    ↓ POST /api/ai/complete
    ↓
Nuxt Server (Frontend Container)
    ├─ Middleware: api-proxy.ts ⚠️ PROBLEM HERE
    │   └─ Proxies directly to backend
    │       └─ Forwards cookies (but not properly translated)
    │
    └─ Server Route: /server/api/ai/complete.post.ts ⭐ SHOULD USE THIS
        └─ Handles Supabase auth
        └─ Translates to Backend JWT
        └─ Proxies to backend with proper auth
```

### The Bug

**File:** `/root/anwalts-frontend-new/server/middleware/api-proxy.ts`

```typescript
// Line 16-34: Routes that should NOT be proxied
const nuxtHandledRoutes = [
    '/api/profile',
    '/api/dashboard/summary'
    // ❌ MISSING: '/api/ai/complete'
]

const nuxtAuthRoutes = [
    '/api/auth/signin',
    '/api/auth/signup',
    // ... other auth routes
    // ❌ /api/ai/complete NOT listed here either
]

// Line 39: Check if route should skip proxy
const shouldSkip = isNuxtAuthRoute || nuxtHandledRoutes.some(route => path.startsWith(route))

if (shouldSkip) {
    return // Let Nuxt handle these routes
}

// ⚠️ Because /api/ai/complete is NOT in the skip list,
// it gets proxied directly to backend, bypassing the
// proper authentication handler!
```

### What Should Happen

There's a dedicated handler at `/server/api/ai/complete.post.ts` that:

1. ✅ Reads Supabase session cookies
2. ✅ Validates the user with Supabase
3. ✅ Mints a Backend-compatible JWT token
4. ✅ Proxies to backend with proper Authorization header
5. ✅ Returns the AI response

**But this handler is NEVER reached** because the middleware intercepts it first!

### Why Backend Returns 403

When the middleware proxies directly:
1. It forwards cookies from the browser
2. But these are Supabase cookies, not backend cookies
3. Backend's `get_current_user_flexible()` checks for:
   - `Authorization: Bearer` header ❌ (not sent)
   - `auth_token` cookie ❌ (not present)
   - `sid` cookie ❌ (not present)
   - `sat` cookie ❌ (not present)
4. **No valid auth found → 403 Forbidden**

---

## ✅ THE FIX

### Option 1: Add Route to Skip List (RECOMMENDED)

**File:** `/root/anwalts-frontend-new/server/middleware/api-proxy.ts`

**Change line 16-19 from:**
```typescript
const nuxtHandledRoutes = [
    '/api/profile',
    '/api/dashboard/summary'
]
```

**To:**
```typescript
const nuxtHandledRoutes = [
    '/api/profile',
    '/api/dashboard/summary',
    '/api/ai/complete'  // ⭐ ADD THIS LINE
]
```

**That's it!** This one line fixes the entire issue.

### Why This Works

1. Middleware will now skip `/api/ai/complete`
2. Nuxt's own handler `/server/api/ai/complete.post.ts` will take over
3. That handler properly translates Supabase auth → Backend JWT
4. Backend receives valid authentication
5. AI service works! ✅

---

## 🔧 Implementation Steps

### Step 1: Edit the Middleware

```bash
nano /root/anwalts-frontend-new/server/middleware/api-proxy.ts
```

Add `/api/ai/complete` to the `nuxtHandledRoutes` array (line ~18).

### Step 2: Rebuild Frontend Container

```bash
cd /root
docker compose restart frontend
```

Or if you need a full rebuild:
```bash
docker compose down frontend
docker compose up -d --build frontend
```

### Step 3: Test

```bash
# Watch the logs
docker logs -f anwalts_frontend
docker logs -f anwalts_backend

# In another terminal, test the endpoint
# (After logging in via the UI)
```

### Expected Results

**Before Fix:**
```
[API Proxy] Proxying /api/ai/complete to http://backend:8000/api/ai/complete
Backend: INFO: "POST /api/ai/complete HTTP/1.1" 403 Forbidden
```

**After Fix:**
```
[AI] Proxying AI complete request to backend
[AI] Authenticated via Supabase: user@example.com (uuid)
[AI] Complete request successful
Backend: INFO: "POST /api/ai/complete HTTP/1.1" 200 OK
```

---

## 🎨 Alternative Solutions

### Option 2: Remove the Middleware Proxy (NOT RECOMMENDED)

You could remove the catch-all proxy middleware entirely and add specific proxies for each endpoint. But this requires more work and maintenance.

### Option 3: Fix the Middleware to Handle Auth (COMPLEX)

You could enhance the middleware to:
1. Detect if Supabase cookies are present
2. Translate them to Backend JWT
3. Forward with proper Authorization header

But this duplicates logic already in `/server/api/ai/complete.post.ts`.

---

## 📊 System Health (After Investigation)

| Component | Status | Details |
|-----------|--------|---------|
| **Frontend Container** | ✅ Running | Port 3000, Nuxt.js |
| **Backend Container** | ✅ Running | Ports 8000, 8010, FastAPI |
| **Legal RAG API** | ✅ **WORKING PERFECTLY** | Port 9000, processing requests successfully |
| **PostgreSQL** | ✅ Running | User database operational |
| **Redis** | ✅ Running | Cache operational |
| **OAuth (Google)** | ✅ Working | Users can log in |
| **AI Models** | ✅ Loaded | mT5-small + retriever |
| **RAG Index** | ✅ Present | FAISS + metadata |
| **AI Endpoint** | ❌ **BLOCKED** | 403 due to routing issue |

---

## 🔍 Technical Deep Dive

### AI Service Stack

```
┌─────────────────────────────────────────────┐
│  User sends message in /assistant page     │
└─────────────────┬───────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────┐
│  Frontend calls: POST /api/ai/complete     │
│  Body: { prompt, context, max_tokens }     │
└─────────────────┬───────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────┐
│  Nuxt Server (SHOULD use ai/complete.post) │
│  1. Reads Supabase session                  │
│  2. Validates with Supabase                 │
│  3. Gets user: email, id                    │
│  4. Creates Backend JWT                     │
│  5. Proxies to backend with JWT             │
└─────────────────┬───────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────┐
│  Backend: POST /api/ai/complete             │
│  1. Validates JWT token                     │
│  2. Checks cache (Redis)                    │
│  3. Calls ai_service.generate_completion()  │
└─────────────────┬───────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────┐
│  ai_service.py: _generate_sidecar_completion│
│  POST https://portal-anwalts.ai/v1/legal/answer_v2 │
└─────────────────┬───────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────┐
│  Legal RAG API (legal-rag-api container)    │
│  1. Embeds question (SentenceTransformer)   │
│  2. Searches FAISS index (k=6 docs)         │
│  3. Retrieves legal texts                   │
│  4. Generates answer (mT5-small)            │
│  5. Returns { answer, sources, used_k }     │
└─────────────────┬───────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────┐
│  Response flows back through stack          │
│  Backend caches in Redis (TTL: 1 day)       │
│  Frontend displays answer to user           │
└─────────────────────────────────────────────┘
```

### Legal RAG API Details

**Health Check:**
```bash
$ curl http://localhost:9000/healthz
{
  "ok": true,
  "index": "/app/rag/index.faiss",
  "meta": "/app/rag/meta.jsonl",
  "generator": "/app/sft-legal-mt5-small",
  "retriever": "/app/retriever"
}
```

**Models:**
- **Retriever:** SentenceTransformer (embedding model)
- **Generator:** Fine-tuned mT5-small (German legal text generation)
- **Index:** FAISS version 1.8.0
- **Documents:** German legal corpus (meta.jsonl)

**Current Status:**
✅ Processing requests successfully
✅ Returning 200 OK responses
✅ Models loaded and functioning
✅ No errors in logs

---

## 📝 Complete Fix Code

```typescript
// File: /root/anwalts-frontend-new/server/middleware/api-proxy.ts
// Lines 16-19

const nuxtHandledRoutes = [
    '/api/profile',
    '/api/dashboard/summary',
    '/api/ai/complete'  // ⭐ ADD THIS LINE
]
```

---

## ✅ Verification Checklist

After applying the fix:

- [ ] Edit middleware file
- [ ] Add `/api/ai/complete` to skip list
- [ ] Save file
- [ ] Restart frontend container
- [ ] Log in to the application
- [ ] Navigate to /assistant
- [ ] Send a test message
- [ ] Verify response is received
- [ ] Check logs for `[AI] Complete request successful`
- [ ] Verify no 403 errors in backend logs
- [ ] Test with multiple messages
- [ ] Verify context awareness (conversation memory)

---

## 🎯 Summary

**The AI service is NOT broken.** Everything is working perfectly:
- ✅ Models are loaded
- ✅ RAG system is functional
- ✅ Backend can generate responses
- ✅ Legal corpus is accessible

**The ONLY problem** is a routing configuration issue that causes authentication to be bypassed. The fix is literally adding one line to a configuration file.

**Estimated fix time:** 2 minutes  
**Testing time:** 3 minutes  
**Total downtime:** < 5 minutes

---

## 📞 Next Actions

1. Apply the one-line fix to `api-proxy.ts`
2. Restart the frontend container
3. Test with an authenticated user
4. Verify AI responses are working
5. Monitor logs for any other issues

The AI service will be fully operational immediately after this fix is applied.
