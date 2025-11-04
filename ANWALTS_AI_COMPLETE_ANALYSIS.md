# Anwalts-AI Complete System Analysis

**Generated:** 2025-10-17  
**Status:** Critical Authentication Issue Identified

---

## 🎯 Executive Summary

The Anwalts-AI application is a legal AI assistant system with the following architecture:
- **Frontend:** Nuxt.js application (port 3000)
- **Backend:** FastAPI Python backend (ports 8000, 8010)
- **AI Service:** Legal RAG API (port 9000) - **Working correctly**
- **Databases:** PostgreSQL + Redis
- **Reverse Proxy:** Nginx

### 🔴 CRITICAL ISSUE FOUND

**API calls to `/api/ai/complete` are failing with 403 Forbidden errors** due to authentication issues. The AI service itself is working perfectly, but the frontend cannot communicate with it.

---

## 📊 System Architecture

### Running Containers

```
✅ anwalts_frontend      - Port 3000 (Healthy)
✅ anwalts_backend       - Ports 8000, 8010 (Healthy)
✅ legal-rag-api         - Port 9000 (Healthy, Working)
✅ anwalts_postgres      - Port 5432 (Healthy)
✅ anwalts_redis         - Port 6379 (Healthy)
✅ anwalts_nginx         - Ports 80, 443
   + Multiple Supabase services (auth, storage, etc.)
```

### Communication Flow

```
Frontend (Nuxt.js)
    ↓ /api/ai/complete
Backend (FastAPI) - backend-main.py
    ↓ Authentication Layer (FAILING HERE ❌)
    ↓ ai_service.py
    ↓ HTTP POST to /v1/legal/answer_v2
Legal RAG API (legal-rag-api container)
    ↓ FAISS retrieval + mT5 generation
    ↓ Returns answer + sources
```

---

## 🔍 AI Service Implementation

### Backend AI Service (`/root/ai_service.py`)

**Configuration:**
- Default Model: `qwen_legal_q4_k_m`
- AI URL: `https://portal-anwalts.ai`
- Endpoint: `/v1/legal/answer_v2`

**Implementation Details:**
```python
class AIService:
    async def generate_completion(self, prompt, model, max_tokens, temperature, context):
        # Calls the legal-rag-api sidecar
        response = await client.post(
            f"{self.local_ai_url}/v1/legal/answer_v2",
            json={"question": full_question, "k": 6},
            timeout=120.0
        )
```

### Legal RAG API (`legal-rag-api` container)

**Status:** ✅ **WORKING CORRECTLY**

**Endpoints:**
- `/healthz` - Health check (✅ OK)
- `/v1/legal/answer` - Legacy answer endpoint
- `/v1/legal/answer_v2` - Main answer endpoint (✅ Working, 200 OK responses)

**Model Configuration:**
```
INDEX_PATH: /app/rag/index.faiss ✅ (exists)
META_PATH: /app/rag/meta.jsonl ✅ (exists)
RETRIEVER_PATH: /app/retriever ✅ (loaded)
GENERATOR: /app/sft-legal-mt5-small ✅ (loaded)
```

**Models:**
- **Retriever:** SentenceTransformer for embedding generation
- **Generator:** Fine-tuned mT5-small model for German legal text
- **Index:** FAISS vector database with legal documents

**Logs show successful operations:**
```
INFO: POST /v1/legal/answer_v2 HTTP/1.1 200 OK ✅
```

---

## ❌ CRITICAL PROBLEM: 403 Forbidden Errors

### Error Evidence

**Backend Logs:**
```
INFO: 172.19.0.7:40672 - "POST /api/ai/complete HTTP/1.1" 403 Forbidden ❌
INFO: 172.19.0.7:60148 - "POST /api/ai/complete HTTP/1.1" 403 Forbidden ❌
```

### Root Cause Analysis

**Location:** `/root/backend-main.py` lines 1624-1627

```python
@app.post("/api/ai/complete", response_model=AIResponse)
async def ai_complete(
    request_data: AIRequest,
    current_user: UserInDB = Depends(get_current_user_flexible)  # ⚠️ Authentication required
):
```

**The Problem:**
1. The endpoint requires authentication via `get_current_user_flexible`
2. This function checks for:
   - `Authorization: Bearer <token>` header
   - `auth_token` cookie
   - `sid` cookie
   - `sat` cookie
3. If none are present or valid → **403 Forbidden**

### Frontend Call

**File:** `/root/anwalts-frontend-new/pages/assistant.vue:263`

```javascript
const response = await $fetch('/api/ai/complete', {
    method: 'POST',
    body: {
        prompt: userMessage,
        context: context,
        max_tokens: 1000,
        temperature: 0.7
    }
    // ⚠️ Missing authentication headers/credentials
})
```

**Problem:** The frontend is not sending authentication tokens with the request.

---

## 🔧 Missing Components & Issues

### 1. ❌ Empty Models Directory
```bash
/root/models/  # Empty directory
```
**Status:** This is OK - models are correctly located in the legal-rag-api container.

### 2. ✅ RAG Index Files Present
```bash
/root/data/kaggle_kernel_outputs3/minimal_bundle/datasets/processed/rag/
  - index.faiss ✅
  - meta.jsonl ✅
```

### 3. ❌ Authentication Flow Broken
- OAuth login works (Google Sign-in successful)
- Session cookies are created
- But frontend API calls are not including authentication

---

## 🎯 Required Fixes

### Priority 1: Fix Authentication for `/api/ai/complete`

**Option A: Frontend Fix (Recommended)**
Update the frontend to include credentials:

```javascript
// In assistant.vue
const response = await $fetch('/api/ai/complete', {
    method: 'POST',
    credentials: 'include',  // ⭐ ADD THIS
    body: {
        prompt: userMessage,
        context: context,
        max_tokens: 1000,
        temperature: 0.7
    }
})
```

**Option B: Add Authorization Header**
```javascript
const token = useCookie('sid').value  // or 'sat' or 'auth_token'
const response = await $fetch('/api/ai/complete', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`
    },
    body: { /* ... */ }
})
```

**Option C: Backend Fix (Less Recommended)**
Remove authentication requirement (NOT RECOMMENDED for production):
```python
@app.post("/api/ai/complete", response_model=AIResponse)
async def ai_complete(request_data: AIRequest):  # Remove Depends()
    # But you'd need to handle user tracking differently
```

### Priority 2: Verify Session Cookie Domain

Check that cookies are set for the correct domain:
```python
# In backend-main.py line 139
cookie_domain = os.getenv("SESSION_DOMAIN", "portal-anwalts.ai")
```

Make sure frontend is accessing from the same domain.

---

## 📋 System Health Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Frontend Container | ✅ Healthy | Running on port 3000 |
| Backend Container | ✅ Healthy | Running on ports 8000, 8010 |
| Legal RAG API | ✅ Working | Successfully answering queries |
| PostgreSQL | ✅ Healthy | Database operational |
| Redis | ✅ Healthy | Cache operational |
| RAG Models | ✅ Loaded | mT5-small + SentenceTransformer |
| RAG Index | ✅ Present | FAISS index with metadata |
| OAuth Login | ✅ Working | Google authentication successful |
| AI Endpoint Auth | ❌ **BROKEN** | 403 Forbidden errors |

---

## 🔬 Technical Details

### Authentication Flow (Current State)

```
1. User logs in via Google OAuth ✅
   └─ Backend: /auth/google/callback
   └─ Creates session tokens
   └─ Sets cookies: sid, sat, auth_token

2. User navigates to /assistant page ✅
   └─ Frontend loads assistant.vue
   └─ User sends message

3. Frontend calls /api/ai/complete ❌
   └─ Request sent WITHOUT credentials
   └─ Backend checks authentication
   └─ No valid token found
   └─ Returns 403 Forbidden

4. AI service never reached ✅
   └─ legal-rag-api is working fine
   └─ Just not being called due to auth failure
```

### API Request Chain (When Working)

```
POST /api/ai/complete
  ↓ [Backend validates user token]
  ↓ AIService.generate_completion()
  ↓ POST https://portal-anwalts.ai/v1/legal/answer_v2
  ↓ {question: "...", k: 6}
  ↓ [legal-rag-api processes]
  ↓   - Embeds question with retriever
  ↓   - Searches FAISS index
  ↓   - Retrieves top-k documents
  ↓   - Generates answer with mT5
  ↓ Returns {answer: "...", sources: [...]}
  ↓ [Backend caches in Redis]
  ↓ [Backend returns to frontend]
```

---

## 🚀 Recommended Action Plan

### Immediate Actions

1. **Fix Frontend Authentication** (15 minutes)
   - Add `credentials: 'include'` to $fetch call
   - Test with authenticated user
   - Verify cookies are sent

2. **Test API Connection** (5 minutes)
   ```bash
   # Get a valid token from browser dev tools
   curl -X POST http://localhost:8000/api/ai/complete \
     -H "Authorization: Bearer <TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Was ist Mietrecht?", "max_tokens": 1000}'
   ```

3. **Monitor Logs** (ongoing)
   ```bash
   docker logs -f anwalts_backend
   docker logs -f legal-rag-api
   ```

### Verification Steps

1. Check that 403 errors are resolved
2. Verify AI responses are returned to frontend
3. Confirm legal-rag-api receives requests
4. Test with multiple users/sessions

---

## 📝 Configuration Summary

### Environment Variables (Backend)

```env
DATABASE_URL=postgresql://anwalts_user:<REDACTED_DB_PASSWORD>@postgres:5432/anwalts_ai
REDIS_URL=redis://redis:6379
LOCAL_AI_KIND=sidecar
LOCAL_AI_URL=https://portal-anwalts.ai
LOCAL_AI_MODEL=qwen_legal_q4_k_m
JWT_SECRET_KEY=<REDACTED_JWT_SECRET>
SESSION_DOMAIN=portal-anwalts.ai
FEEDBACK_V1=true
```

### Model Information

- **Model Type:** RAG (Retrieval-Augmented Generation)
- **Retriever:** SentenceTransformer (embeddings)
- **Generator:** Fine-tuned mT5-small (German legal)
- **Index Type:** FAISS vector database
- **Documents:** German legal corpus
- **Retrieval Count:** 6 documents per query

---

## 🎓 Key Insights

1. **The AI service is NOT broken** - it's working perfectly
2. **The problem is authentication** - frontend can't reach backend
3. **Models are present and loaded** - in the correct container
4. **RAG pipeline is functional** - confirmed by successful API calls from other sources
5. **Quick fix available** - just need to pass credentials from frontend

---

## 📞 Next Steps

To resolve the issue quickly:

1. Open `/root/anwalts-frontend-new/pages/assistant.vue`
2. Find line 263 (the $fetch call)
3. Add `credentials: 'include'` to the request options
4. Rebuild and restart the frontend container
5. Test with an authenticated user

This should immediately resolve the 403 errors and allow the AI assistant to function correctly.
