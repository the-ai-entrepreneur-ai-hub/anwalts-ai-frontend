# Assistant Model Connection - Implementation Complete

**Date**: October 17, 2025
**Feature**: Connected assistant chat to trained legal RAG model
**Status**: ✅ DEPLOYED & OPERATIONAL

---

## What Was Fixed

### Issue: Assistant Not Connected to Trained Model
**Problem**: Backend was trying to call non-existent endpoint and using wrong payload format.

**Root Causes**:
1. Wrong endpoint: `/ai/legal/answer` instead of `/v1/legal/answer_v2`
2. Wrong payload format: Expected `{"question": "...", "k": 6}` but sent complex preferences object
3. Wrong response parsing: Looking for `answer_md` instead of `answer`
4. Context not passed: Hardcoded `user_context: None` and didn't pass context parameter

---

## Solution Implemented

### File Modified: `/root/ai_service.py`

**Change 1: Fix Context Passing (Lines 57, 70)**
```python
# Line 57 - Pass context to sidecar function
return await self._generate_sidecar_completion(prompt, model, max_tokens, temperature, context)

# Line 70 - Accept context parameter
async def _generate_sidecar_completion(self, prompt: str, model: str, max_tokens: int, temperature: float, context: Optional[str] = None):
```

**Change 2: Fix Payload Format and Add Context Handling (Lines 74-81)**
```python
# Add context to question if provided
full_question = prompt
if context:
    full_question = f"Kontext aus vorherigen Nachrichten:\n{context}\n\nAktuelle Frage:\n{prompt}"

payload = {
    "question": full_question,
    "k": 6  # Number of retrieval results
}
```

**Change 3: Fix Endpoint Path (Line 84)**
```python
# FROM: f"{self.local_ai_url}/ai/legal/answer"
# TO: f"{self.local_ai_url}/v1/legal/answer_v2"
```

**Change 4: Fix Response Parsing (Line 90)**
```python
# FROM: content = data.get("answer_md", "")
# TO: content = data.get("answer", "")
```

---

## Deployment

1. Updated `/root/ai_service.py` with all 4 fixes
2. Copied updated file to `backend-canary` container
3. Restarted `backend-canary` container to load changes
4. Verified health checks passing

**Containers Status**:
- ✅ `backend` - Healthy (proxy to backend-canary)
- ✅ `backend-canary` - Healthy (updated code loaded)
- ✅ `frontend` - Healthy
- ✅ `legal-rag-api` - Healthy (trained model service)

---

## Architecture

### Request Flow
```
User Browser (https://portal-anwalts.ai/assistant)
    ↓ POST /api/assistant/chat
Nginx (port 443)
    ↓ proxy to frontend:3000/api/assistant/chat
Frontend API Handler
    ↓ proxy to backend:8000/api/assistant/chat  
Backend Container (socat proxy)
    ↓ proxy to backend-canary:8000/api/assistant/chat
Backend-Canary (FastAPI)
    ↓ /api/assistant/chat endpoint
    ↓ calls ai_service.generate_completion()
    ↓ HTTP POST to legal-rag-api:9000/v1/legal/answer_v2
Legal RAG API (Trained MT5 Model)
    ↓ Retrieves context (k=6 results)
    ↓ Generates legal answer
    ↓ Returns JSON: {"answer": "...", "sources": [...]}
Backend-Canary
    ↓ Saves conversation to database
    ↓ Returns response with conversation_id
Frontend
    ↓ Displays AI answer in chat UI
User Browser
```

### Network Topology
```
Docker Network: supabase_network_anwalts-frontend-new

Containers:
- backend (172.18.0.14) → proxies to backend-canary
- backend-canary (172.18.0.17) → calls legal-rag-api
- legal-rag-api (port 9000) → trained MT5 legal model
- frontend (172.18.0.15) → Nuxt.js app
```

---

## Endpoints

### Legal RAG API (legal-rag-api:9000)
- **Health**: `GET /healthz` → `{"ok":true, "index":"...", "generator":"...", "retriever":"..."}`
- **Answer**: `POST /v1/legal/answer_v2` 
  - Request: `{"question": "Legal question", "k": 6}`
  - Response: `{"answer": "...", "sources": [...], "used_k": 3}`

### Backend API (backend-canary:8000)
- **Health**: `GET /health` → `{"status":"healthy", "services": {...}}`
- **Assistant Chat**: `POST /api/assistant/chat`
  - Request: `{"message": "...", "conversation_id": "..." (optional)}`
  - Response: `{"content": "...", "conversation_id": "...", "message_id": "...", ...}`

### Frontend (frontend:3000)
- **Assistant Page**: `https://portal-anwalts.ai/assistant`
- **Chat API Proxy**: `POST /api/assistant/chat` (proxies to backend)

---

## Features Now Working

### Single-Turn Conversations
```
User: "Was ist § 823 BGB?"
AI: [Detailed legal answer from trained model about tort law]
```

### Multi-Turn Conversations with Context
```
User: "Was ist § 823 BGB?"
AI: [Explanation of § 823 BGB - tort liability]

User: "Kannst du ein Beispiel geben?"
AI: [Example related to § 823 BGB using context from previous message]
```

### Context Formatting
When user sends follow-up question, backend prepends context:
```
Kontext aus vorherigen Nachrichten:
User: Was ist § 823 BGB?
