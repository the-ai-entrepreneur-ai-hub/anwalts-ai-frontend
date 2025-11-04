# QUICK FIX - Choose One Approach

## 🔥 EMERGENCY: Get Auth Working NOW (Breaks Documents Page)

```bash
# Restore working auth config
cp /root/nginx/sites-dev/portal-anwalts.ai.conf.backup /root/nginx/sites-dev/portal-anwalts.ai.conf
docker restart anwalts_nginx

# Test auth
curl -I https://portal-anwalts.ai/api/auth/google/authorize
# Should return: 307 Temporary Redirect

# ⚠️ WARNING: Documents page will show 404s again
```

---

## ✅ PROPER FIX: Make Backend Consistent (Recommended)

The backend has inconsistent routing expectations. Fix it properly:

### Edit Backend File
```bash
nano /root/anwalts-frontend-new/backend-main.py
```

### Find These Lines (around line 373-375):
```python
@app.get("/api/auth/google/authorize")
async def google_authorize_api_alias():
    return await google_authorize()
```

### SOLUTION: Make Backend Accept BOTH Patterns

Add these routes to accept `/api/auth/*` directly:

```python
# Around line 595 (after existing callback routes)

@app.get("/api/auth/google/callback")
async def google_callback_api(request: Request, code: str, state: str):
    """API-prefixed callback - calls main callback handler"""
    return await google_callback(request, code, state)

# Make sure the main callback handler doesn't have /api prefix:
@app.get("/auth/google/callback")
async def google_callback(request: Request, code: str, state: str):
    # ... existing callback code ...
```

### Then Update Nginx (simpler config):
```bash
nano /root/nginx/sites-dev/portal-anwalts.ai.conf
```

Replace the auth/health/api blocks with:
```nginx
# Everything goes to backend with /api prefix intact
location /api/ {
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto $scheme;
  proxy_pass http://backend:8000;
}

# Health check without /api (optional direct access)
location /health {
  proxy_pass http://backend:8000;
}
```

### Restart Services:
```bash
cd /root
docker-compose restart backend
docker restart anwalts_nginx

# Wait 10 seconds
sleep 10

# Test everything
curl -I https://portal-anwalts.ai/api/auth/google/authorize
curl -I https://portal-anwalts.ai/api/templates
curl -s https://portal-anwalts.ai/api/health
```

---

## 🧪 Test Complete Flow

```bash
# 1. Auth works (307 redirect)
curl -I https://portal-anwalts.ai/api/auth/google/authorize | grep 307

# 2. Templates work (403 = needs auth, 200 = logged in, 404 = BROKEN)
curl -I https://portal-anwalts.ai/api/templates | grep -E "403|200"

# 3. Clauses work
curl -I https://portal-anwalts.ai/api/clauses | grep -E "403|200"

# 4. Health works
curl -s https://portal-anwalts.ai/api/health | grep healthy

# 5. Check backend logs for errors
docker logs anwalts_backend --tail 50 | grep ERROR
```

---

## 📋 Current State Summary

**What Works:**
- ✅ Health checks
- ✅ Backend is healthy (Redis + Postgres connected)
- ✅ Frontend is running

**What's Broken:**
- ❌ OAuth callback returns 502 Bad Gateway
- ❌ User cannot login
- ⚠️ Documents page might show 404s depending on nginx config

**Root Cause:**
Backend expects some routes without `/api/` prefix (auth) and others with it (documents). Nginx can't satisfy both requirements simultaneously with current config.

---

## 🎯 Success Criteria

After fix, ALL these should work:

```bash
# Auth flow (full test - try in browser)
1. Go to https://portal-anwalts.ai
2. Click login
3. Authenticate with Google
4. Should redirect back and be logged in ✅

# API endpoints
curl -I https://portal-anwalts.ai/api/auth/google/authorize  # 307 ✅
curl -I https://portal-anwalts.ai/api/templates             # 403 or 200 ✅
curl -I https://portal-anwalts.ai/api/clauses               # 403 or 200 ✅
curl -s https://portal-anwalts.ai/api/health                # {"status":"healthy"} ✅
```

---

## 📞 Files Modified During Troubleshooting

1. `/root/nginx/sites-dev/portal-anwalts.ai.conf` - Multiple changes to route handling
2. `/root/anwalts-frontend-new/nuxt.config.ts` - Fixed endpoint URLs (templates, clauses)
3. Frontend rebuilt and redeployed

**Backup available:** `/root/nginx/sites-dev/portal-anwalts.ai.conf.backup`

---

## 🚨 If Everything Fails - Nuclear Option

```bash
# Stop everything
cd /root
docker-compose down

# Restore original nginx
cp /root/nginx/sites-dev/portal-anwalts.ai.conf.backup /root/nginx/sites-dev/portal-anwalts.ai.conf

# Revert frontend changes
cd /root/anwalts-frontend-new
git diff nuxt.config.ts  # Check what changed
git checkout nuxt.config.ts  # Revert if needed
npm run build

# Start everything fresh
cd /root
docker-compose up -d

# Wait for healthy status
sleep 30
docker ps
```

This will restore the system to the state before troubleshooting (auth works, documents page broken).
