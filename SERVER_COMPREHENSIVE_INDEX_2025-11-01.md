# Server Comprehensive Index - November 1, 2025

## Server Information
- **IP Address**: 148.x.x.222
- **Hostname**: anwalts-ai-production-1.0
- **OS**: Linux 6.8.0-85-generic (Ubuntu)
- **Uptime**: 28 days, 2:33 hours
- **Load Average**: 0.79, 0.91, 0.68
- **Memory**: 124GB total, 8.5GB used, 60GB free, 56GB buffer/cache
- **Disk**: 1.8TB total, 194GB used, 1.5TB available (12% usage)

## Critical Issues Identified

### 1. **TOGETHER_API_KEY Not Configured** ⚠️
- **Status**: CRITICAL - AI service degraded
- **Location**: Backend container environment
- **Impact**: AI completions failing every 30 seconds
- **Error**: `TOGETHER_API_KEY not configured`
- **Solution Required**: Set TOGETHER_API_KEY environment variable

### 2. **Frontend OAuth Proxy Error** ⚠️
- **Status**: ERROR - Authentication partially broken
- **Error**: `TypeError: Cannot read properties of undefined (reading 'append')`
- **Location**: Frontend Nuxt server at `/app/.output/server/chunks/nitro/nitro.mjs:6654:38`
- **Impact**: OAuth redirect failures for Gmail authorization
- **Frequency**: Intermittent but recurring

### 3. **Legal RAG API Health Check Mismatch** ⚠️
- **Status**: WARNING - Health endpoint inconsistency
- **Issue**: Legal RAG API expects `/healthz` but other services use `/health`
- **Impact**: Monitoring inconsistency

## Running Docker Containers

### Production Services (Healthy)
1. **anwalts_frontend** (59f79a8f1a33)
   - Image: root_frontend
   - Port: 3000:3000
   - Status: Up 5 days (healthy)
   - Purpose: Nuxt.js SSR frontend
   
2. **anwalts_backend** (b262188ec1e4)
   - Image: root_backend
   - Ports: 8000:8000, 8010:8010
   - Status: Up 5 days (healthy)
   - Purpose: FastAPI Python backend
   
3. **anwalts_nginx** (bf0ea9f14e95)
   - Image: nginx:alpine
   - Ports: 80:80, 443:443
   - Status: Up 5 days (healthy)
   - Purpose: Reverse proxy with SSL termination
   
4. **cfafb1fc6f43_anwalts_postgres** (cfafb1fc6f43)
   - Image: pgvector/pgvector:pg15
   - Port: 5432:5432
   - Status: Up 13 days (healthy)
   - Purpose: PostgreSQL database with vector support
   
5. **5821c4fa806e_anwalts_redis** (5821c4fa806e)
   - Image: redis:7-alpine
   - Port: 6379:6379
   - Status: Up 13 days (healthy)
   - Purpose: Redis cache and session storage

6. **legal-rag-api** (2e17f6c694c2)
   - Image: legal-rag-api:latest
   - Port: 9000:9000
   - Status: Up 2 weeks
   - Purpose: Legal document RAG (Retrieval-Augmented Generation) service

### Stopped/Exited Containers
- tender_beaver (64d0db5f24ce) - Exited 2 weeks ago
- amazing_noyce (48efe96080a1) - Exited 2 weeks ago

## Network Architecture

### External Ports (Public)
- **80/443** → Nginx (HTTPS with Let's Encrypt SSL)
- **3000** → Frontend (Nuxt.js)
- **5432** → PostgreSQL
- **6379** → Redis
- **8000** → Backend API
- **8010** → Backend secondary port
- **9000** → Legal RAG API
- **8080** → Python HTTP server (test/dev)

### Internal Ports (Localhost)
- **33511** → Cursor/Trae server
- **33861** → Cline host
- **51000-51009** → Trae helper services
- **14881** → MCP Linear integration
- **127.0.0.54:53** → systemd-resolved DNS

### Domain Configuration
- **Domain**: portal-anwalts.ai
- **SSL**: Let's Encrypt certificates at `/etc/letsencrypt/live/portal-anwalts.ai/`
- **SSL Protocols**: TLSv1.2, TLSv1.3

## Nginx Routing Configuration

### Frontend Routes
- `/` → Frontend SSR (Nuxt.js at frontend:3000)
- `/api/auth/*` → Frontend auth middleware (handles OAuth flow)
- `/auth/google/*` → Frontend OAuth endpoints

### Backend Routes
- `/api/*` → Backend API (backend:8000)
- `/api/health` → Backend health check

### External Services
- `/supabase/*` → Supabase at host.docker.internal:54321
- `/supabase/realtime/v1/*` → Supabase realtime WebSocket

## Environment Configuration

### Backend Environment
```bash
AI_PROVIDER=together
TOGETHER_API_KEY=  # ⚠️ EMPTY - NEEDS TO BE SET
TOGETHER_BASE=https://api.together.xyz/v1
TOGETHER_MODEL=deepcogito/cogito-v2-preview-llama-405B
DATABASE_URL=postgresql://anwalts_user:anwalts_password@postgres:5432/anwalts_ai
REDIS_URL=redis://redis:6379
CORS_ORIGIN=https://portal-anwalts.ai
API_BASE_URL=https://portal-anwalts.ai
JWT_SECRET_KEY=dev-only-jwt-secret
GOOGLE_CLIENT_ID=[REDACTED - see secrets manager]
GOOGLE_CLIENT_SECRET=[REDACTED - see secrets manager]
GOOGLE_REDIRECT_URI=https://portal-anwalts.ai/api/auth/google/callback
LOCAL_AI_KIND=sidecar
LOCAL_AI_URL=https://portal-anwalts.ai
LOCAL_AI_MODEL=qwen_legal_q4_k_m
SMTP_HOST=mailhog
SMTP_PORT=1025
SMTP_FROM=no-reply@anwalts.ai
```

### Frontend Environment
```bash
BACKEND_BASE=http://backend:8000
NUXT_PUBLIC_API_BASE=/api
NITRO_HOST=0.0.0.0
NITRO_PORT=3000
NODE_OPTIONS=--max_old_space_size=3072
JWT_SECRET_KEY=dev-only-jwt-secret
GOOGLE_CLIENT_ID=[REDACTED - see secrets manager]
GOOGLE_CLIENT_SECRET=[REDACTED - see secrets manager]
SUPABASE_URL=https://portal-anwalts.ai/supabase
SUPABASE_ANON_KEY=sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH
```

## Running Processes (Top 10 by Memory)

1. **Uvicorn (RAG API)** - 2.7GB - PID 969245
   - `/usr/local/bin/python3.10 /usr/local/bin/uvicorn app:app --host 0.0.0.0 --port 9000`
   
2. **Docker Daemon** - 1.6GB - PID 1291
   - Core container orchestration
   
3. **Cursor Agent** - 708MB - PID 3793472
   - Active AI coding assistant
   
4. **Trae Server** - 377MB - PID 3792866
   - AI completion server
   
5. **Trae Server (Extension Host)** - 361MB - PID 3792337
   - Extension hosting

6. **Cursor Worker Server** - 345MB - PID 3795954
   - Cursor background worker

7. **Trae File Watcher** - 183MB - PID 3792380
   - File system monitoring

8. **Uvicorn (Backend)** - 162MB - PID 594560
   - `/usr/local/bin/python3.12 /usr/local/bin/uvicorn backend-main:app --host 0.0.0.0 --port 8000`

9. **Frontend Nuxt** - 86MB - PID 608932
   - `node .output/server/index.mjs`

10. **systemd-journald** - 108MB - PID 709
    - System logging service

## System Services (systemd)

### Active Services
- containerd.service - Container runtime
- docker.service - Docker engine
- nginx (not systemd, runs in container)
- ssh.service - OpenSSH server
- systemd-resolved.service - DNS resolution
- systemd-networkd.service - Network management
- cron.service - Scheduled tasks
- rsyslog.service - System logging

## Database Information

### PostgreSQL
- **Version**: PostgreSQL 15 with pgvector extension
- **Database**: anwalts_ai
- **User**: anwalts_user
- **Port**: 5432
- **Status**: Healthy, running 13 days
- **Volume**: postgres_data (persistent)

### Redis
- **Version**: Redis 7 Alpine
- **Port**: 6379
- **Status**: Healthy, running 13 days
- **Configuration**: 
  - Append-only file enabled
  - Max memory: 512MB
  - Eviction policy: allkeys-lru
- **Volume**: redis_data (persistent)

## Application Stack

### Backend (FastAPI/Python)
- **Framework**: FastAPI with Uvicorn
- **Python Version**: 3.12.11
- **Key Services**:
  - AI Service (Together AI integration)
  - Auth Service (Google OAuth)
  - Cache Service (Redis)
  - Database Service (PostgreSQL)
  - RAG Service (Legal document retrieval)
  - Upload Processor
  - Email/SMTP utilities

### Frontend (Nuxt.js)
- **Framework**: Nuxt 3
- **Node Version**: 20.19.5
- **Mode**: SSR (Server-Side Rendering)
- **Features**:
  - OAuth flow handling
  - API proxy middleware
  - Session management
  - Supabase integration

### Legal RAG Service
- **Framework**: FastAPI/Python 3.10
- **Port**: 9000
- **Features**:
  - Legal document search and retrieval
  - T5-based model for legal question answering
  - Vector embeddings for semantic search
- **Active Endpoint**: `/v1/legal/answer_v2`

## Security Configuration

### Nginx Security Headers
```
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self' https:; script-src 'self' 'unsafe-inline' https://accounts.google.com...
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### SSL/TLS Configuration
- Certificate: Let's Encrypt
- Session cache: 10MB shared
- Session timeout: 1 day
- Protocols: TLSv1.2, TLSv1.3

### OAuth Configuration
- **Provider**: Google OAuth 2.0
- **Client ID**: [REDACTED - see secrets manager]
- **Redirect URI**: https://portal-anwalts.ai/api/auth/google/callback

## File System Structure

### Key Directories
- `/root/` - Main application directory
- `/root/anwalts-frontend-new/` - Frontend source (669 files)
- `/root/anwalts-backend-venv/` - Python virtual environment (4955 files)
- `/root/data/` - Application data (24,037 files)
- `/root/models/` - AI models
- `/root/legal-corpus/` - Legal documents for RAG
- `/root/nginx/` - Nginx configuration
- `/root/routes/` - Backend routes (5 Python files)
- `/root/services/` - Backend services

### Key Files
- `docker-compose.yml` - Container orchestration
- `Dockerfile.backend` - Backend container definition
- `.env` - Environment variables
- `backend-main.py` - Backend entry point (230KB)
- `database.py` - Database ORM (98KB)
- `ai_service.py` - AI integration (21KB)
- `auth_service.py` - Authentication (12KB)

## Docker Volumes

### Persistent Data
- `postgres_data` - PostgreSQL database files
- `redis_data` - Redis persistence
- Mounted volumes:
  - `./models:/app/models` - AI model files
  - `./legal-corpus:/app/legal-corpus` - Legal documents
  - `./data:/app/data` - Application data
  - `/etc/letsencrypt:/etc/letsencrypt:ro` - SSL certificates

## Health Check Status

### Service Health
- ✅ **Backend**: Healthy - `{"status":"healthy","services":{"database":"healthy","cache":"healthy","ai_service":{"status":"degraded"}}}`
- ⚠️ **AI Service**: Degraded - TOGETHER_API_KEY not configured
- ✅ **Frontend**: Healthy - Responding on port 3000
- ✅ **Nginx**: Healthy - SSL working, routing configured
- ✅ **PostgreSQL**: Healthy - Accepting connections
- ✅ **Redis**: Healthy - Responding to PING
- ✅ **Legal RAG API**: Operational - Processing requests

## Recent Activity

### Container Restarts
- Frontend: Restarted 5 days ago
- Backend: Restarted 5 days ago
- Nginx: Restarted 5 days ago

### Log Patterns
- Regular health checks every 30 seconds
- Intermittent OAuth redirect errors
- Continuous TOGETHER_API_KEY warnings
- Active legal document queries to RAG service
- Security scanning attempts (blocked by nginx)

## Required Actions

### Immediate Fixes Needed

1. **Set TOGETHER_API_KEY**
   - Location: `docker-compose.yml` or `.env` file
   - Impact: Restore AI completion functionality
   - Priority: **CRITICAL**

2. **Fix Frontend OAuth Proxy**
   - Location: `/root/anwalts-frontend-new/.output/server/chunks/nitro/nitro.mjs`
   - Error: Headers append issue in proxy redirect
   - Priority: **HIGH**

3. **Standardize Health Endpoints**
   - Legal RAG API: Change `/healthz` to `/health` or vice versa
   - Priority: **LOW**

### Configuration Improvements

1. **Security**
   - Change JWT_SECRET_KEY from dev default
   - Rotate database passwords
   - Review Google OAuth credentials

2. **Monitoring**
   - Add comprehensive health monitoring
   - Set up alerting for service degradation
   - Monitor TOGETHER_API_KEY usage

3. **Performance**
   - Review Redis memory usage (512MB limit)
   - Monitor database connection pool
   - Optimize Nginx caching

## Development Tools Active

- **Cursor AI Agent**: Active (3 processes)
- **Trae Server**: Active (code intelligence)
- **Cline Host**: Active on port 33861
- **MCP Linear Integration**: Active on port 14881
- **Python HTTP Server**: Running on port 8080

## Backup Status

- Backup directory exists: `/root/backup/`
- Archive present: `anwalts-complete-recovery.tar.gz` (79KB)
- Multiple documentation files present

---

**Generated**: November 1, 2025, 14:05 UTC
**Server Uptime**: 28 days
**Health Status**: OPERATIONAL (with degraded AI service)
