# Developer Handoff - Auth & Documents Page Issues

## Current Status: BROKEN AUTH FLOW

**Date:** 2025-10-18  
**System:** portal-anwalts.ai  
**Critical Issues:** 
1. ❌ OAuth login broken (502 Bad Gateway on callback)
2. ⚠️ Documents page endpoints were 404, attempted fix may have broken auth

---

## System Architecture

### Services (Docker Compose)
```
- anwalts_postgres (port 5432) - PostgreSQL with pgvector
- anwalts_redis (port 6379) - Redis cache
- anwalts_backend (port 8000) - FastAPI Python backend
- anwalts_frontend (port 3000) - Nuxt 3 frontend
- anwalts_nginx (ports 80/443) - Nginx reverse proxy
- Supabase stack (Kong gateway on port 54321)
```

**Files:**
- Docker Compose: `/root/docker-compose.yml`
- Backend Code: `/root/anwalts-frontend-new/backend-main.py`
- Frontend Code: `/root/anwalts-frontend-new/`
- Nginx Config: `/root/nginx/sites-dev/portal-anwalts.ai.conf`
- Backup Config: `/root/nginx/sites-dev/portal-anwalts.ai.conf.backup`

---

## Problem Summary

### Original Issue
User reported Documents page showing "No templates found" and "No clauses found". Investigation revealed:
- Frontend was calling `/api/documents/templates` and `/api/documents/clauses`
- Backend actually has routes at `/api/templates` and `/api/clauses`
- Nginx was stripping `/api/` prefix from ALL requests

### What Was Attempted
1. Modified nginx config to add specific location blocks for auth routes
2. Changed general `/api/` block to keep the prefix (for documents endpoints)
3. Updated frontend `nuxt.config.ts` to call correct endpoints
4. Rebuilt and restarted containers multiple times

### Current Problem
**Auth flow is broken:**
```
1. User clicks login ✅ Works
2. Redirects to Google OAuth ✅ Works (307)
3. Google redirects back to /api/auth/google/callback ❌ 502 Bad Gateway
4. Error in backend: "Missing code verifier" (PKCE flow broken)
```

**Root Cause:** Backend can't retrieve PKCE code_verifier from Redis during callback, causing OAuth to fail.

---

## Current Nginx Configuration

**File:** `/root/nginx/sites-dev/portal-anwalts.ai.conf`

```nginx
# Auth endpoints - strip /api prefix (ORDER MATTERS - must come FIRST)
location ~ ^/api/auth/ {
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto $scheme;
  rewrite ^/api/(.*) /$1 break;
  proxy_pass http://backend:8000;
}

# Health check endpoints - strip /api prefix
location ~ ^/api/health {
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto $scheme;
  rewrite ^/api/(.*) /$1 break;
  proxy_pass http://backend:8000;
}

# All other /api/ requests - keep /api prefix (for documents, files, etc)
location /api/ {
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto $scheme;
  proxy_pass http://backend:8000;
}
```

---

## Backend Route Mapping

**File:** `/root/anwalts-frontend-new/backend-main.py`

### Auth Routes (WITHOUT /api prefix expected):
```python
@app.get("/auth/google/authorize")           # Main route
@app.get("/api/auth/google/authorize")       # Alias (line 373)
@app.get("/auth/google/callback")            # Main callback
@app.get("/api/auth/google/callback")        # Alias callback
```

### Document Routes (WITH /api prefix expected):
```python
@app.get("/api/templates")
@app.post("/api/templates")
@app.get("/api/clauses")
@app.post("/api/clauses")
@app.post("/api/documents/save")
@app.post("/api/files/upload")
```

### Other Routes:
```python
@app.get("/health")                          # NO /api prefix
@app.get("/api/health")                      # Alias
```

---

## What Needs To Be Fixed

### Option 1: Standardize Backend Routes (RECOMMENDED)
**Make backend consistent - either all routes have `/api/` or none do.**

Current inconsistency:
- Auth routes expect: `/auth/*` (no /api)
- Document routes expect: `/api/templates`, `/api/clauses` (with /api)
- Health can handle both

**Fix:** Modify backend to accept both patterns OR standardize on one.

```python
# Either add duplicate routes:
@app.get("/api/auth/google/callback")  # Already exists
@app.get("/auth/google/callback")       # Already exists

# OR use router prefix:
auth_router = APIRouter(prefix="/api/auth")
```

### Option 2: Fix Nginx Routing
**Current problem:** Can't make nginx satisfy both:
- Auth needs `/api/auth/*` → `/auth/*` (strip prefix)
- Documents need `/api/templates` → `/api/templates` (keep prefix)

**Possible solution:**
```nginx
# Option A: Route auth to backend with /api prefix intact
location ~ ^/api/auth/ {
  proxy_pass http://backend:8000;  # No rewrite, backend handles /api/auth/*
}

# Option B: More specific auth rewrite
location = /api/auth/google/authorize {
  rewrite ^/api/(.*) /$1 break;
  proxy_pass http://backend:8000;
}
location = /api/auth/google/callback {
  rewrite ^/api/(.*) /$1 break;
  proxy_pass http://backend:8000;
}
```

---

## Testing Commands

```bash
# Check container health
docker ps --format "{{.Names}}: {{.Status}}" | grep anwalts

# Check backend logs
docker logs anwalts_backend --tail 50

# Check nginx logs
docker logs anwalts_nginx --tail 50

# Test health endpoint
curl -s https://portal-anwalts.ai/api/health

# Test auth authorize (should return 307)
curl -I https://portal-anwalts.ai/api/auth/google/authorize

# Test templates endpoint (should return 403 if auth works, not 404)
curl -I https://portal-anwalts.ai/api/templates

# Check Redis connectivity from backend
docker exec anwalts_backend redis-cli -h redis ping

# Check Postgres connectivity from backend
docker exec anwalts_backend pg_isready -h postgres -U anwalts_user
```

---

## Frontend Configuration

**File:** `/root/anwalts-frontend-new/nuxt.config.ts`

```typescript
apiEndpoints: {
  generate: '/api/ai/generate-document',
  generateSimple: '/api/ai/generate-document-simple',
  process: '/api/documents/process',
  templates: '/api/templates',           // Changed from /api/documents/templates
  clauses: '/api/clauses',               // Changed from /api/documents/clauses
  upload: '/api/files/upload',
  save: '/api/documents/save',
  exportBase: '/api/documents',
  status: '/api/documents/status'
}
```

---

## Known Working State (Before Changes)

**Backup file exists:** `/root/nginx/sites-dev/portal-anwalts.ai.conf.backup`

Original config had:
```nginx
location /api/ {
  rewrite ^/api/(.*) /$1 break;  # Stripped /api from EVERYTHING
  proxy_pass http://backend:8000;
}
```

This worked for auth BUT broke documents page (404s).

---

## Recommended Fix Strategy

1. **Restore nginx backup first to get auth working:**
```bash
cp /root/nginx/sites-dev/portal-anwalts.ai.conf.backup /root/nginx/sites-dev/portal-anwalts.ai.conf
docker restart anwalts_nginx
```

2. **Then fix backend routes to be consistent:**
   - Either make ALL routes accept `/api/*` prefix
   - Or add middleware to handle both patterns
   - Or use FastAPI router prefixes properly

3. **Test thoroughly:**
   - Login flow (complete OAuth)
   - Documents page (templates/clauses load)
   - Health checks
   - File uploads

---

## Environment Variables

**Backend (.env or docker-compose.yml):**
```
DATABASE_URL=postgresql://anwalts_user:<REDACTED_DB_PASSWORD>@postgres:5432/anwalts_ai
REDIS_URL=redis://redis:6379
GOOGLE_CLIENT_ID=<REDACTED_GOOGLE_CLIENT_ID>
GOOGLE_CLIENT_SECRET=<REDACTED_GOOGLE_SECRET>
GOOGLE_REDIRECT_URI=https://portal-anwalts.ai/api/auth/google/callback
```

---

## Contact & Access

**System:** Production server at portal-anwalts.ai  
**Access:** Root SSH access required  
**Current State:** Auth broken, documents page also broken  
**Priority:** HIGH - Users cannot login

---

## Next Steps for New Developer

1. ✅ Read this document thoroughly
2. ✅ Check current container status: `docker ps`
3. ✅ Review backend logs: `docker logs anwalts_backend --tail 100`
4. ✅ Test current endpoints (use commands above)
5. ✅ Decide on fix strategy (Option 1 or Option 2)
6. ✅ Implement fix
7. ✅ Test complete user flow: login → documents page → CRUD operations
8. ✅ Document final working configuration

**Good luck! The system is close to working - just needs routing consistency.**
