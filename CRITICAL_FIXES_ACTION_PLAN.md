# Critical Fixes Action Plan
**Date**: November 1, 2025
**Server**: 148.x.x.222 (anwalts-ai-production-1.0)

## Summary of Critical Issues

Based on comprehensive system analysis, there are **4 CRITICAL** issues and **2 HIGH** priority issues that need immediate attention:

### Critical Issues
1. ⚠️ **TOGETHER_API_KEY Not Configured** - AI service completely degraded
2. ⚠️ **Frontend OAuth Proxy Error** - Authentication partially broken
3. ⚠️ **Mailhog Container Not Running** - Email functionality broken
4. ⚠️ **Insecure JWT Secret Key** - Security vulnerability

### High Priority Issues
5. 🔴 **Database Password Exposed** - Default credentials in use
6. 🔴 **Google OAuth Secrets in Frontend** - Security misconfiguration

---

## Issue #1: TOGETHER_API_KEY Not Configured

### Current Status
```
ERROR: TOGETHER_API_KEY not configured
Frequency: Every 30 seconds
Impact: All AI completions failing
Service Status: Degraded
```

### Root Cause
The backend container has `AI_PROVIDER=together` but `TOGETHER_API_KEY=` (empty string).

### Fix Steps

#### Option A: Set Together API Key (Recommended if you have the key)
```bash
# 1. Stop the containers
cd /root
docker-compose down

# 2. Edit docker-compose.yml and set the TOGETHER_API_KEY
nano docker-compose.yml
# OR edit the .env file
nano .env

# Add your actual API key:
TOGETHER_API_KEY=your_actual_api_key_here

# 3. Restart the services
docker-compose up -d

# 4. Verify the fix
docker logs -f anwalts_backend | grep -i together
```

#### Option B: Switch to Sidecar AI (If no Together key available)
```bash
# 1. Edit docker-compose.yml
nano docker-compose.yml

# 2. Change AI_PROVIDER from 'together' to 'sidecar'
# Find this line under backend environment:
AI_PROVIDER=sidecar

# 3. Restart backend
docker-compose restart backend

# 4. Verify
curl http://localhost:8000/health | jq
```

### Verification
```bash
# Check that AI service is healthy
curl -s http://localhost:8000/health | jq '.services.ai_service'

# Should return:
# {
#   "status": "healthy",
#   "provider": "together",
#   "model": "deepcogito/cogito-v2-preview-llama-405B"
# }
```

---

## Issue #2: Frontend OAuth Proxy Error

### Current Status
```
ERROR: TypeError: Cannot read properties of undefined (reading 'append')
Location: /app/.output/server/chunks/nitro/nitro.mjs:6654:38
Function: proxyBackendRedirect
Impact: Gmail OAuth authorization fails intermittently
```

### Root Cause
In `/root/anwalts-frontend-new/server/utils/oauthProxy.ts` at lines 147-148, the code attempts to append cookies without checking if `setCookies` is properly initialized. When the backend returns an error response, `setCookies` may be `undefined` or `null`.

### Fix Steps

```bash
# 1. Navigate to frontend directory
cd /root/anwalts-frontend-new

# 2. Edit the OAuth proxy file
nano server/utils/oauthProxy.ts
```

#### Code Fix Required

**Current Code (lines 142-151):**
```typescript
const setCookies =
  typeof response.headers.getSetCookie === 'function'
    ? response.headers.getSetCookie()
    : response.headers.get('set-cookie')

if (Array.isArray(setCookies)) {
  setCookies.forEach((cookie) => headersInit.append('set-cookie', cookie))
} else if (typeof setCookies === 'string') {
  headersInit.set('set-cookie', setCookies)
}
```

**Fixed Code:**
```typescript
const setCookies =
  typeof response.headers.getSetCookie === 'function'
    ? response.headers.getSetCookie()
    : response.headers.get('set-cookie')

if (Array.isArray(setCookies) && setCookies.length > 0) {
  setCookies.forEach((cookie) => {
    if (cookie && typeof cookie === 'string') {
      headersInit.append('set-cookie', cookie)
    }
  })
} else if (typeof setCookies === 'string' && setCookies.length > 0) {
  headersInit.set('set-cookie', setCookies)
}
```

#### Same Fix for proxyBackendRedirect (lines 89-99)

**Current Code:**
```typescript
const rawSetCookie = typeof response.headers.getSetCookie === 'function'
  ? response.headers.getSetCookie()
  : response.headers.get('set-cookie')
const setCookies = Array.isArray(rawSetCookie)
  ? rawSetCookie
  : typeof rawSetCookie === 'string'
    ? splitCookiesString(rawSetCookie)
    : []
for (const cookie of setCookies) {
  appendResponseHeader(event, 'set-cookie', cookie)
}
```

**Fixed Code:**
```typescript
const rawSetCookie = typeof response.headers.getSetCookie === 'function'
  ? response.headers.getSetCookie()
  : response.headers.get('set-cookie')
const setCookies = Array.isArray(rawSetCookie)
  ? rawSetCookie
  : typeof rawSetCookie === 'string'
    ? splitCookiesString(rawSetCookie)
    : []
for (const cookie of setCookies) {
  if (cookie && typeof cookie === 'string') {
    appendResponseHeader(event, 'set-cookie', cookie)
  }
}
```

#### Rebuild and Deploy
```bash
# 3. Rebuild the frontend container
cd /root
docker-compose build frontend

# 4. Restart the frontend
docker-compose up -d frontend

# 5. Monitor logs for errors
docker logs -f anwalts_frontend | grep -i oauth
```

### Verification
```bash
# Test OAuth flow
curl -I https://portal-anwalts.ai/auth/google/authorize?mode=gmail

# Should return 302 redirect without errors in logs
```

---

## Issue #3: Mailhog Container Not Running

### Current Status
```
Service: mailhog
Status: NOT RUNNING
Configured: YES (in docker-compose.yml)
Impact: Email/SMTP functionality broken
Backend Config: SMTP_HOST=mailhog, SMTP_PORT=1025
```

### Root Cause
Mailhog service is defined in `docker-compose.yml` but not currently running. This breaks all email functionality including password resets and notifications.

### Fix Steps

```bash
# 1. Check if mailhog container exists
docker ps -a | grep mailhog

# 2. Start mailhog service
docker-compose up -d mailhog

# 3. Verify it's running
docker ps | grep mailhog

# 4. Check logs
docker logs anwalts_mailhog

# 5. Access web UI
curl http://localhost:8025
# Or visit https://portal-anwalts.ai:8025 if exposed
```

### Configuration Check
```bash
# Verify backend can reach mailhog
docker exec anwalts_backend ping -c 3 mailhog

# Test SMTP connection
docker exec anwalts_backend python3 -c "
import smtplib
try:
    server = smtplib.SMTP('mailhog', 1025, timeout=5)
    server.quit()
    print('✓ SMTP connection successful')
except Exception as e:
    print(f'✗ SMTP connection failed: {e}')
"
```

### Verification
```bash
# Send test email through backend
curl -X POST http://localhost:8000/api/test-email \
  -H "Content-Type: application/json" \
  -d '{"to":"test@example.com","subject":"Test"}'

# Check mailhog web UI at http://localhost:8025
```

---

## Issue #4: Insecure JWT Secret Key

### Current Status
```
JWT_SECRET_KEY=dev-only-jwt-secret
Status: CRITICAL SECURITY VULNERABILITY
Exposure: Both backend and frontend containers
Impact: Anyone with this knowledge can forge authentication tokens
```

### Root Cause
Production system using default development JWT secret key that is publicly visible in configuration files.

### Fix Steps

```bash
# 1. Generate a strong secret key
NEW_JWT_SECRET=$(openssl rand -base64 64 | tr -d '\n')
echo "Generated JWT Secret: $NEW_JWT_SECRET"

# 2. Update .env file
cd /root
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# 3. Update the JWT_SECRET_KEY
sed -i "s/^JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$NEW_JWT_SECRET/" .env

# 4. Also update SESSION_SECRET if it exists
NEW_SESSION_SECRET=$(openssl rand -base64 64 | tr -d '\n')
sed -i "s/^SESSION_SECRET=.*/SESSION_SECRET=$NEW_SESSION_SECRET/" .env

# 5. Update docker-compose.yml to use environment variable
# Make sure docker-compose.yml has:
# JWT_SECRET_KEY=${JWT_SECRET_KEY}

# 6. Restart all services (this will invalidate all existing sessions)
docker-compose down
docker-compose up -d

# 7. Verify new secret is loaded
docker exec anwalts_backend env | grep JWT_SECRET_KEY
# Should NOT show dev-only-jwt-secret
```

### ⚠️ Important Notes
- This will **invalidate all existing user sessions**
- Users will need to log in again
- Coordinate this change with your team
- Keep a secure backup of the new secret key

---

## Issue #5: Database Password Exposed

### Current Status
```
POSTGRES_PASSWORD=anwalts_password
Status: Default/weak password
Exposure: Multiple configuration files
Risk: High - database accessible on public port 5432
```

### Root Cause
Default password being used for PostgreSQL database which is exposed on a public port.

### Fix Steps

⚠️ **CRITICAL**: This requires downtime and data backup

```bash
# 1. Backup the database FIRST
cd /root
mkdir -p backups/$(date +%Y%m%d)
docker exec cfafb1fc6f43_anwalts_postgres pg_dump -U anwalts_user anwalts_ai > \
  backups/$(date +%Y%m%d)/anwalts_ai_backup_$(date +%H%M%S).sql

# 2. Verify backup
ls -lh backups/$(date +%Y%m%d)/

# 3. Generate strong password
NEW_DB_PASSWORD=$(openssl rand -base64 32 | tr -d '/+=' | cut -c1-32)
echo "New DB Password: $NEW_DB_PASSWORD"
# SAVE THIS PASSWORD SECURELY!

# 4. Stop all services
docker-compose down

# 5. Update .env file
sed -i "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$NEW_DB_PASSWORD/" .env

# 6. Update docker-compose.yml to ensure it uses env var
# POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

# 7. Remove old postgres volume (ONLY if you have backup!)
# docker volume rm root_postgres_data

# 8. Restart services
docker-compose up -d

# 9. Wait for postgres to initialize
sleep 30

# 10. Restore database
cat backups/$(date +%Y%m%d)/anwalts_ai_backup_*.sql | \
  docker exec -i cfafb1fc6f43_anwalts_postgres psql -U anwalts_user anwalts_ai

# 11. Verify
docker exec cfafb1fc6f43_anwalts_postgres psql -U anwalts_user anwalts_ai -c "\dt"
```

### Alternative: Change Password Without Data Loss
```bash
# 1. Generate new password
NEW_DB_PASSWORD=$(openssl rand -base64 32 | tr -d '/+=' | cut -c1-32)

# 2. Change password in PostgreSQL
docker exec cfafb1fc6f43_anwalts_postgres psql -U anwalts_user -d anwalts_ai -c \
  "ALTER USER anwalts_user WITH PASSWORD '$NEW_DB_PASSWORD';"

# 3. Update .env
sed -i "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$NEW_DB_PASSWORD/" .env

# 4. Restart backend to use new password
docker-compose restart backend

# 5. Verify connection
docker exec anwalts_backend python3 -c "
from database import engine
with engine.connect() as conn:
    result = conn.execute('SELECT 1')
    print('✓ Database connection successful')
"
```

---

## Issue #6: Google OAuth Secrets in Frontend

### Current Status
```
Frontend Container Environment:
- GOOGLE_CLIENT_ID=[REDACTED - stored in secret manager]
- GOOGLE_CLIENT_SECRET=[REDACTED - stored in secret manager]
Risk: Client secret exposed in frontend (should be backend-only)
```

### Root Cause
Google OAuth client secret is unnecessarily exposed in the frontend container environment. Frontend should only have the client ID.

### Fix Steps

```bash
# 1. Edit docker-compose.yml
cd /root
nano docker-compose.yml

# 2. Remove GOOGLE_CLIENT_SECRET from frontend service
# Under frontend -> environment, REMOVE this line:
# - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET:-}

# Frontend should only have:
# - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID:-}
# - GOOGLE_REDIRECT_URI=https://portal-anwalts.ai/api/auth/google/callback

# 3. Ensure backend has the secret (it already does)
# Under backend -> environment, KEEP:
# - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID:-}
# - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET:-}

# 4. Restart frontend
docker-compose up -d frontend

# 5. Verify secret is removed from frontend
docker exec anwalts_frontend env | grep GOOGLE_CLIENT_SECRET
# Should return nothing

# 6. Verify backend still has it
docker exec anwalts_backend env | grep GOOGLE_CLIENT_SECRET
# Should return: GOOGLE_CLIENT_SECRET=[REDACTED - see secrets manager]
```

### Security Improvement: Rotate OAuth Credentials

If credentials have been compromised:
1. Go to Google Cloud Console
2. Navigate to APIs & Services > Credentials
3. Delete the old OAuth 2.0 Client ID
4. Create a new OAuth 2.0 Client ID
5. Update `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`
6. Restart all services

---

## Additional Recommendations

### 7. Standardize Health Check Endpoints

**Issue**: Legal RAG API uses `/healthz` while other services use `/health`

```bash
# Option A: Update nginx to support both
nano /root/nginx/sites-dev/portal-anwalts.ai.conf

# Add after existing health check location:
location ~ ^/(health|healthz) {
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_pass http://$backend_upstream;
}
```

### 8. Secure Redis

**Issue**: Redis exposed on public port without password

```bash
# 1. Edit docker-compose.yml
# Update redis command to include password:
command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru --requirepass YOUR_REDIS_PASSWORD

# 2. Update REDIS_URL in backend environment:
REDIS_URL=redis://:YOUR_REDIS_PASSWORD@redis:6379

# 3. Restart services
docker-compose restart redis backend
```

### 9. Close Unnecessary Public Ports

**Issue**: Multiple services exposed directly to internet

```bash
# Edit docker-compose.yml and change port mappings to localhost only:

# Before:
ports:
  - "5432:5432"  # PostgreSQL
  - "6379:6379"  # Redis
  - "8000:8000"  # Backend
  - "9000:9000"  # RAG API

# After (bind to localhost only):
ports:
  - "127.0.0.1:5432:5432"  # PostgreSQL
  - "127.0.0.1:6379:6379"  # Redis
  - "127.0.0.1:8000:8000"  # Backend
  - "127.0.0.1:9000:9000"  # RAG API

# Keep these public (through nginx):
ports:
  - "80:80"
  - "443:443"
  - "3000:3000"  # Frontend
```

---

## Execution Order

### Phase 1: Immediate Security Fixes (Do First)
1. ✅ Issue #4: Change JWT Secret Key
2. ✅ Issue #6: Remove OAuth secret from frontend
3. ✅ Issue #5: Change database password
4. ✅ Recommendation #9: Close unnecessary ports

### Phase 2: Functionality Fixes (Do Second)
5. ✅ Issue #1: Configure TOGETHER_API_KEY
6. ✅ Issue #3: Start Mailhog service
7. ✅ Issue #2: Fix OAuth proxy error

### Phase 3: Improvements (Do When Time Permits)
8. ✅ Recommendation #7: Standardize health checks
9. ✅ Recommendation #8: Secure Redis
10. ✅ Set up monitoring and alerting

---

## Rollback Procedures

### If something goes wrong:

#### Rollback Configuration
```bash
# Restore previous .env
cd /root
cp .env.backup.YYYYMMDD_HHMMSS .env
docker-compose restart
```

#### Rollback Database
```bash
# Restore from backup
cat backups/YYYYMMDD/anwalts_ai_backup_*.sql | \
  docker exec -i cfafb1fc6f43_anwalts_postgres psql -U anwalts_user anwalts_ai
```

#### Rollback Frontend Code
```bash
# If OAuth proxy fix causes issues
cd /root/anwalts-frontend-new
git checkout server/utils/oauthProxy.ts
docker-compose build frontend
docker-compose up -d frontend
```

---

## Post-Fix Verification Checklist

After completing all fixes, verify:

- [ ] Backend health check shows all services healthy
- [ ] AI completions working (no TOGETHER_API_KEY errors)
- [ ] OAuth login flow works without errors
- [ ] Email sending works (check mailhog UI)
- [ ] Database connections work
- [ ] Redis cache working
- [ ] No security secrets in frontend container
- [ ] All services restart successfully
- [ ] Nginx routing working correctly
- [ ] SSL certificates valid

### Verification Commands
```bash
# 1. Overall system health
curl -s https://portal-anwalts.ai/api/health | jq

# 2. Check all containers
docker-compose ps

# 3. Check logs for errors
docker-compose logs --tail=50 | grep -i error

# 4. Verify no exposed secrets
docker exec anwalts_frontend env | grep -E "(SECRET|PASSWORD)"
docker exec anwalts_backend env | grep -E "(SECRET|PASSWORD)"

# 5. Test OAuth flow
curl -I https://portal-anwalts.ai/auth/google/authorize

# 6. Check mailhog
curl http://localhost:8025

# 7. Test database connection
docker exec anwalts_backend python3 -c "from database import engine; engine.connect()"
```

---

## Monitoring Setup

After fixes, set up monitoring:

```bash
# 1. Create monitoring script
cat > /root/scripts/health-monitor.sh << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/anwalts-health.log"
echo "[$(date)] Starting health check..." >> $LOG_FILE

# Check all services
SERVICES="anwalts_frontend anwalts_backend anwalts_nginx cfafb1fc6f43_anwalts_postgres 5821c4fa806e_anwalts_redis anwalts_mailhog"

for service in $SERVICES; do
  if docker ps | grep -q $service; then
    echo "[$(date)] ✓ $service is running" >> $LOG_FILE
  else
    echo "[$(date)] ✗ $service is DOWN" >> $LOG_FILE
    # Send alert (implement your alerting mechanism)
  fi
done

# Check backend health
HEALTH=$(curl -s http://localhost:8000/health | jq -r '.status')
if [ "$HEALTH" = "healthy" ]; then
  echo "[$(date)] ✓ Backend health check passed" >> $LOG_FILE
else
  echo "[$(date)] ✗ Backend health check failed: $HEALTH" >> $LOG_FILE
fi
EOF

chmod +x /root/scripts/health-monitor.sh

# 2. Add to crontab (run every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /root/scripts/health-monitor.sh") | crontab -
```

---

**Document Created**: November 1, 2025
**Last Updated**: November 1, 2025
**Status**: Ready for execution
**Estimated Time**: 2-3 hours for all fixes
**Downtime Required**: ~10-15 minutes for database password change

⚠️ **IMPORTANT**: Always backup data before making changes!
