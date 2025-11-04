# Anwalts-AI Complete System Index
*Generated: 2025-10-17*

## 🎯 Executive Summary

Anwalts-AI is a full-stack legal AI assistant application running on a German-language legal corpus with RAG (Retrieval-Augmented Generation) capabilities. The system provides:
- 24/7 AI-powered legal consultation
- Document management and generation
- Email integration with Gmail
- User authentication via Google OAuth and Supabase
- Real-time chat interface with legal AI model

---

## 🏗️ System Architecture

### Core Components

1. **Frontend (Nuxt 3)** - Port 3000
2. **Backend (FastAPI)** - Port 8000, 8010
3. **Legal RAG API** - Port 9000
4. **PostgreSQL Database** - Port 5432
5. **Redis Cache** - Port 6379
6. **Supabase Stack** - Ports 54321-54327
7. **Nginx (Reverse Proxy)** - Ports 80, 443

### Infrastructure Stack

```
                    ┌─────────────────┐
                    │  HTTPS Traffic  │
                    │   (Nginx TBD)   │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼─────┐      ┌──────▼──────┐      ┌─────▼──────┐
   │ Frontend │      │   Backend   │      │  RAG API   │
   │  :3000   │◄────►│   :8000     │◄────►│   :9000    │
   │ (Nuxt 3) │      │  (FastAPI)  │      │  (FastAPI) │
   └────┬─────┘      └──────┬──────┘      └────────────┘
        │                   │
        │            ┌──────┴──────┬──────────────┐
        │            │             │              │
        │      ┌─────▼─────┐ ┌────▼────┐  ┌──────▼──────┐
        │      │ PostgreSQL│ │  Redis  │  │  Supabase   │
        │      │   :5432   │ │  :6379  │  │  :54321+    │
        │      └───────────┘ └─────────┘  └─────────────┘
        │
        └──────► (Static Assets & Pages)
```

---

## 📦 Running Containers

### Active Containers (docker ps)

| Container Name | Image | Ports | Status | Purpose |
|---------------|-------|-------|--------|---------|
| `anwalts_backend` | root-backend | 8000, 8010 | healthy | Main FastAPI backend |
| `anwalts_frontend` | root-frontend | 3000 | healthy | Nuxt 3 frontend |
| `legal-rag-api` | legal-rag-api:latest | 9000 | running | RAG AI service |
| `anwalts_postgres` | pgvector/pgvector:pg15 | 5432 | healthy | PostgreSQL + pgvector |
| `anwalts_redis` | redis:7-alpine | 6379 | healthy | Cache & sessions |
| `anwalts_mailhog` | mailhog/mailhog:v1.0.1 | 1025, 8025 | running | Email testing |
| `anwalts_nginx` | nginx:alpine | 80, 443 | created | Reverse proxy (not started) |
| `supabase_*` | Supabase stack | 54321-54327 | healthy | Auth & DB management |

### Docker Compose Configuration

**Location:** `/root/docker-compose.yml`

**Services:**
1. **postgres** - pgvector/pgvector:pg15
   - Database: `anwalts_ai`
   - User: `anwalts_user`
   - Volume: postgres_data

2. **redis** - redis:7-alpine
   - Max memory: 512MB
   - Policy: allkeys-lru
   - Persistence: AOF enabled

3. **backend** - Built from `Dockerfile.backend`
   - Main entry: `backend-main.py`
   - Healthcheck: `/health` endpoint

4. **frontend** - Built from `anwalts-frontend-new/Dockerfile`
   - Main entry: Nuxt 3 server
   - Proxy to backend via `BACKEND_BASE`

5. **nginx** - nginx:alpine (for production)
   - Config: `/root/nginx/nginx-dev.conf`

---

## 🔧 Backend Architecture

### Main File: `/root/backend-main.py` (3180 lines)

#### Key Services Integration

```python
# Global Services
db: Database              # PostgreSQL connection pool
ai_service: AIService     # AI/RAG service client
cache_service: CacheService  # Redis cache
auth_service: AuthService    # JWT authentication
```

#### Core API Endpoints

##### Authentication & Users
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - Email/password login
- `POST /api/auth/logout` - Logout & token revoke
- `GET /api/auth/google/authorize` - Google OAuth start
- `GET /api/auth/google/callback` - Google OAuth callback
- `GET /api/user/profile` - Get user profile
- `PATCH /api/user/profile` - Update profile
- `POST /api/user/profile/picture` - Upload profile picture

##### AI & Chat
- `POST /api/ai/complete` - AI chat completion (main endpoint)
- `POST /api/ai/generate-document` - Document generation
- `GET /api/ai/models` - List available models

##### Email Integration
- `GET /api/user/gmail/status` - Check Gmail connection
- `GET /api/email/list` - List emails
- `GET /api/email/labels` - Get email labels
- `POST /api/email/modify` - Modify email labels

##### Documents & Templates
- `GET /api/documents` - List user documents
- `POST /api/documents/save` - Save document
- `GET /api/templates` - List templates
- `POST /api/templates` - Create template

##### Feedback System (V1)
- `POST /api/feedback` - Submit message feedback
- `POST /api/edit` - Submit message edit

##### Health & Monitoring
- `GET /health` - Health check
- `GET /api/dashboard/summary` - Dashboard statistics

#### AI Service: `/root/ai_service.py`

**Provider Configuration:**
```python
AI_PROVIDER = "sidecar"  # or "together"
LOCAL_AI_URL = "https://portal-anwalts.ai"
LOCAL_AI_MODEL = "qwen_legal_q4_k_m"
```

**Communication Flow:**
```
Backend → POST /v1/legal/answer_v2 → RAG API (port 9000)
         ← JSON response with answer & sources
```

**Key Methods:**
- `generate_completion()` - Main completion method
- `_generate_sidecar_completion()` - Calls RAG API at port 9000
- `_generate_together_completion()` - Together AI API (optional)
- `generate_document()` - Document generation with context

#### Authentication: `/root/auth_service.py`

**JWT Configuration:**
```python
JWT_SECRET_KEY = env("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = 1440 minutes (24h)
```

**Features:**
- bcrypt password hashing
- JWT token generation/verification
- Token blacklisting
- Refresh tokens
- API tokens
- Password reset tokens

#### Database: `/root/database.py`

**Connection:**
```python
postgresql://anwalts_user:<REDACTED_DB_PASSWORD>@postgres:5432/anwalts_ai
```

**Key Tables:**
- `users` - User accounts
- `user_profiles` - Extended profile data
- `assistant_messages` - Chat history
- `assistant_conversations` - Conversation metadata
- `documents` - User documents
- `templates` - Document templates
- `email_threads` - Gmail integration
- `analytics_events` - Usage tracking

**Features:**
- asyncpg connection pooling (1-10 connections)
- Health check endpoint
- Profile picture storage (base64)
- Gmail token storage

#### Cache Service: `/root/cache_service.py`

**Redis Configuration:**
```python
REDIS_URL = "redis://redis:6379"
```

**Features:**
- Session management
- Rate limiting
- Query result caching
- TTL-based expiration

---

## 🎨 Frontend Architecture

### Location: `/root/anwalts-frontend-new/`

### Technology Stack
- **Framework:** Nuxt 3
- **UI Library:** @nuxt/ui (Tailwind CSS)
- **State Management:** Pinia
- **Authentication:** Supabase Auth + Google OAuth

### Key Pages

| Route | File | Purpose |
|-------|------|---------|
| `/` | `pages/index.vue` | Landing page (Framer design) |
| `/assistant` | `pages/assistant.vue` | Main AI chat interface |
| `/dashboard` | `pages/dashboard.vue` | User dashboard |
| `/email` | `pages/email.vue` | Gmail integration |
| `/documents` | `pages/documents.vue` | Document management |
| `/templates` | `pages/templates.vue` | Template library |
| `/settings` | `pages/settings.vue` | User settings |

### Main AI Chat Interface: `/assistant`

**File:** `pages/assistant.vue` (522 lines)

**Features:**
- Real-time chat with AI
- Context-aware conversations (last 5 messages)
- Markdown formatting support
- Code block rendering
- Loading states with animations
- Quick prompt examples
- Auto-scroll to bottom

**API Call:**
```typescript
const response = await $fetch('/api/ai/complete', {
  method: 'POST',
  body: {
    prompt: userMessage,
    context: buildContext(),  // Last 5 messages
    max_tokens: 1000,
    temperature: 0.7
  }
})
```

### Server API Routes: `/server/api/`

**AI Endpoints:**
- `ai/complete.post.ts` - Proxy to backend AI completion

**Auth Endpoints:**
- `auth/login.post.ts` - Login handler
- `auth/register.post.ts` - Registration handler
- `auth/google/authorize.get.ts` - Google OAuth start
- `auth/google/callback.get.ts` - Google OAuth callback
- `auth/status.get.ts` - Check auth status

**Email Endpoints:**
- `email/list.get.ts` - List emails
- `email/labels.get.ts` - Get labels
- `email/modify.post.ts` - Modify labels

**Utils:**
- `server/utils/backend.ts` - Backend URL resolution
- `server/utils/sessionCookie.ts` - Session management
- `server/utils/supabase.ts` - Supabase client

### Components

| Component | Purpose |
|-----------|---------|
| `PortalShell.vue` | Main layout wrapper with sidebar |
| `GlassmorphismAuthModal.vue` | Login/signup modal |
| `GoogleSignInButton.vue` | Google OAuth button |
| `ProfilePopup.vue` | User profile dropdown |
| `FramerLanding.vue` | Landing page component |

### Composables

- `useAuthModal.ts` - Auth modal state management
- `usePortalUser.ts` - User state management
- `useSupabaseAuth.ts` - Supabase auth helpers
- `useTour.ts` - Product tour functionality

### Configuration: `nuxt.config.ts`

```typescript
export default defineNuxtConfig({
  modules: ['@nuxt/ui', '@pinia/nuxt'],
  runtimeConfig: {
    backendBase: 'http://backend:8000',
    public: {
      supabaseUrl: process.env.SUPABASE_URL,
      apiBase: '/api'
    }
  },
  ssr: true,
  vite: {
    server: {
      host: '0.0.0.0',
      port: 3000
    }
  }
})
```

---

## 🤖 Legal RAG API

### Container: `legal-rag-api` (Port 9000)

**Main File:** `/app/app.py` (running inside container)

**Technology Stack:**
- **Framework:** FastAPI
- **Retrieval:** FAISS vector index + SentenceTransformers
- **Generation:** mT5 (google/mt5-small) or custom fine-tuned model
- **Embeddings:** sentence-transformers retriever

### Data Files (in container)

```
/app/rag/
├── index.faiss        (9.2 MB)  - Vector index
├── meta.jsonl         (62.8 MB) - Document metadata
/app/sft-legal-mt5-small/        - Fine-tuned generator
/app/retriever/                  - Embedding model
```

### API Endpoints

#### 1. Health Check
```bash
GET /healthz
```

Response:
```json
{
  "ok": true,
  "index": "/app/rag/index.faiss",
  "meta": "/app/rag/meta.jsonl",
  "generator": "/app/sft-legal-mt5-small",
  "retriever": "/app/retriever"
}
```

#### 2. Answer V1 (Legacy)
```bash
POST /v1/legal/answer
```

Request:
```json
{
  "question": "string",
  "k": 6,  // optional, number of docs to retrieve
  "max_new_tokens": 256  // optional
}
```

Response:
```json
{
  "answer": "string",
  "citations": ["[source:id]", ...],
  "retrieved": [
    {
      "score": 0.85,
      "text": "...",
      "source": "BGB",
      "id": "123",
      "parent_id": "123"
    }
  ]
}
```

#### 3. Answer V2 (Current)
```bash
POST /v1/legal/answer_v2
```

Request: Same as V1

Response:
```json
{
  "answer": "string (plain text, no citations in text)",
  "sources": [
    {
      "source": "BGB",
      "id": "123",
      "parent_id": "123",
      "score": 0.85
    }
  ],
  "used_k": 6
}
```

### RAG Pipeline

```
1. Question → Retriever (SentenceTransformer)
              ↓
2. Query Embedding → FAISS Search (top-k documents)
              ↓
3. Retrieved Docs + Question → Prompt Construction
              ↓
4. Prompt → mT5 Generator
              ↓
5. Generated Answer → Post-processing
              ↓
6. Return: {answer, sources, used_k}
```

### Special Features

**Greeting Detection:**
- Detects casual greetings (hi, hallo, hey)
- Returns helpful prompt instead of trying to answer

**Fallback Strategy:**
- If fine-tuned model produces JSON/artifacts → retry with base mT5
- If no good match found (score < 0.35) → return helpful error
- If answer too short → construct from retrieved excerpts

**Answer Quality Control:**
- Remove T5 artifacts (`<extra_id_*>`)
- Remove JSON blocks
- Limit to 6 sentences max
- Keyword matching between query and answer

---

## 🔐 Authentication Flow

### Dual Authentication System

The application uses **two parallel authentication systems**:

#### 1. Supabase Auth (Primary)
- Used for frontend authentication
- Google OAuth integration
- Session management via cookies
- JWT tokens

#### 2. Backend JWT (Secondary)
- FastAPI native JWT authentication
- Used for API access
- Compatible with frontend auth via token minting

### Google OAuth Flow

```
1. User clicks "Sign in with Google"
   ↓
2. Frontend → GET /api/auth/google/authorize
   ↓
3. Backend generates OAuth URL with state
   ↓
4. User redirected to Google consent screen
   ↓
5. Google → GET /api/auth/google/callback?code=...
   ↓
6. Backend exchanges code for tokens
   ↓
7. Backend fetches user info from Google
   ↓
8. Backend creates/updates user in database
   ↓
9. Backend stores Gmail refresh token (if granted)
   ↓
10. Backend sets session cookies (sid, sat)
   ↓
11. User redirected to /email or appropriate page
```

### Session Cookies

| Cookie Name | Type | Purpose |
|------------|------|---------|
| `sid` | HttpOnly | Primary session token (secure) |
| `sat` | Public | Public session token (JS accessible) |
| `auth_token` | HttpOnly | Backend JWT token |
| `gmail_refresh_token` | HttpOnly | Gmail API refresh token |

### Token Minting for Backend

**File:** `server/api/ai/complete.post.ts`

When frontend calls backend API:
1. Read Supabase session from cookie
2. Verify Supabase token
3. Mint backend-compatible JWT with user ID
4. Send as `Authorization: Bearer <token>`

---

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    role VARCHAR(50),
    password_hash VARCHAR(255),
    created_at TIMESTAMP,
    gmail_refresh_token TEXT,
    gmail_connected_at TIMESTAMP
);
```

### User Profiles
```sql
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    data JSONB,  -- stores profile_picture, phone, address, etc.
    updated_at TIMESTAMP
);
```

### Assistant Messages
```sql
CREATE TABLE assistant_messages (
    id UUID PRIMARY KEY,
    conversation_id UUID,
    user_id UUID REFERENCES users(id),
    role VARCHAR(20),  -- 'user' or 'assistant'
    content TEXT,
    model VARCHAR(100),
    message_hash VARCHAR(64),
    created_at TIMESTAMP
);
```

### Documents
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    title VARCHAR(255),
    content TEXT,
    document_type VARCHAR(100),
    status VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## 🌐 Environment Variables

### Backend Environment

```bash
# Database
DATABASE_URL=postgresql://anwalts_user:<REDACTED_DB_PASSWORD>@postgres:5432/anwalts_ai
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=anwalts_ai
POSTGRES_USER=anwalts_user
POSTGRES_PASSWORD=<REDACTED_DB_PASSWORD>

# Redis
REDIS_URL=redis://redis:6379

# JWT & Auth
JWT_SECRET_KEY=<REDACTED_JWT_SECRET>
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Google OAuth
GOOGLE_CLIENT_ID=<REDACTED_GOOGLE_CLIENT_ID>
GOOGLE_CLIENT_SECRET=<REDACTED_GOOGLE_SECRET>
GOOGLE_REDIRECT_URI=https://portal-anwalts.ai/api/auth/google/callback

# Supabase
SUPABASE_URL=https://portal-anwalts.ai/supabase
SUPABASE_SERVICE_ROLE_KEY=<REDACTED_SUPABASE_SERVICE_ROLE_KEY>

# AI Provider
AI_PROVIDER=sidecar
LOCAL_AI_URL=https://portal-anwalts.ai
LOCAL_AI_MODEL=qwen_legal_q4_k_m

# Optional: Together AI
TOGETHER_BASE=https://api.together.xyz/v1
TOGETHER_MODEL=deepcogito/cogito-v2-preview-llama-405B
TOGETHER_API_KEY=

# SMTP (MailHog)
SMTP_HOST=mailhog
SMTP_PORT=1025
SMTP_TLS=0
SMTP_FROM=no-reply@anwalts.ai

# Application
CORS_ORIGIN=https://portal-anwalts.ai
API_BASE_URL=https://portal-anwalts.ai
DASHBOARD_SERVICE_KEY=<REDACTED_DASHBOARD_SERVICE_KEY>
FEEDBACK_V1=true
```

### Frontend Environment

```bash
# Backend
BACKEND_BASE=http://backend:8000

# Supabase
SUPABASE_URL=https://portal-anwalts.ai/supabase
SUPABASE_ANON_KEY=sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH
SUPABASE_SERVICE_ROLE_KEY=<REDACTED_SUPABASE_SERVICE_ROLE_KEY>

# Google OAuth
GOOGLE_CLIENT_ID=<REDACTED_GOOGLE_CLIENT_ID>
GOOGLE_CLIENT_SECRET=<REDACTED_GOOGLE_SECRET>
GOOGLE_REDIRECT_URI=https://portal-anwalts.ai/api/auth/google/callback

# Node
NODE_OPTIONS=--max_old_space_size=3072
NITRO_HOST=0.0.0.0
NITRO_PORT=3000
```

---

## 🚀 Deployment

### Build & Run

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker logs legal-rag-api

# Restart specific service
docker-compose restart backend

# Rebuild after code changes
docker-compose up -d --build backend
docker-compose up -d --build frontend
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000/

# RAG API health
curl http://localhost:9000/healthz

# Database health
docker exec anwalts_postgres pg_isready -U anwalts_user

# Redis health
docker exec anwalts_redis redis-cli ping
```

---

## 🔍 Request Flow Examples

### Example 1: AI Chat Request

```
1. User types message in /assistant page
   ↓
2. Frontend: POST /api/ai/complete
   {
     prompt: "Was sind die Pflichten eines Vermieters?",
     context: "...(previous conversation)",
     max_tokens: 1000,
     temperature: 0.7
   }
   ↓
3. Nuxt API Handler (server/api/ai/complete.post.ts):
   - Reads Supabase session cookie
   - Verifies user with Supabase
   - Mints backend JWT token
   ↓
4. Proxy to Backend: POST http://backend:8000/api/ai/complete
   Headers: Authorization: Bearer <backend_jwt>
   ↓
5. Backend (backend-main.py):
   - Verifies JWT token
   - Extracts user_id
   - Calls ai_service.generate_completion()
   ↓
6. AI Service (ai_service.py):
   - Builds prompt with context
   - POST http://legal-rag-api:9000/v1/legal/answer_v2
   {
     question: "Was sind die Pflichten eines Vermieters?",
     k: 6
   }
   ↓
7. RAG API (app.py):
   - Encodes question to vector
   - Searches FAISS index (top-6)
   - Retrieves relevant documents
   - Constructs prompt with context
   - Generates answer with mT5
   - Returns: {answer, sources, used_k}
   ↓
8. AI Service:
   - Returns AIResponse(content=answer, model=..., usage=...)
   ↓
9. Backend:
   - Logs analytics event
   - Returns: {content: "...", model: "...", usage: {...}}
   ↓
10. Frontend:
   - Displays answer in chat UI
   - Scrolls to bottom
   - Shows timestamp
```

### Example 2: Google OAuth Login

```
1. User clicks "Sign in with Google"
   ↓
2. Frontend: GET /api/auth/google/authorize
   ↓
3. Backend:
   - Generates random state token
   - Stores in session
   - Builds Google OAuth URL with scopes:
     * email, profile
     * gmail.readonly, gmail.modify
   - Returns: {url: "https://accounts.google.com/o/oauth2/v2/auth?..."}
   ↓
4. Frontend redirects user to Google
   ↓
5. User consents on Google
   ↓
6. Google redirects: /api/auth/google/callback?code=xxx&state=yyy
   ↓
7. Backend:
   - Verifies state token
   - Exchanges code for tokens (access_token, refresh_token)
   - Fetches user info from Google
   - Checks if user exists in database
   - Creates user if new, updates if existing
   - Stores gmail_refresh_token
   - Generates JWT token
   - Sets cookies: sid, sat, auth_token, gmail_refresh_token
   - Redirects to /email (if Gmail connected) or /dashboard
   ↓
8. User lands on dashboard, authenticated
```

---

## 🐛 Common Issues & Debugging

### Issue: AI responses not working

**Check:**
1. RAG API is running: `docker ps | grep legal-rag-api`
2. RAG API health: `curl http://localhost:9000/healthz`
3. Backend can reach RAG: `docker exec anwalts_backend curl http://host.docker.internal:9000/healthz`
4. Check logs: `docker logs legal-rag-api -f`

**Common causes:**
- RAG API container not running
- Model files missing in container
- Port 9000 not exposed
- Wrong `LOCAL_AI_URL` in backend environment

### Issue: Authentication errors

**Check:**
1. JWT_SECRET_KEY matches between backend and frontend
2. Supabase credentials are correct
3. Google OAuth credentials are valid
4. Session cookies are being set

**Debug:**
```bash
# Check backend logs for auth errors
docker logs anwalts_backend | grep -i "auth"

# Check if cookies are set
# (Use browser DevTools → Application → Cookies)
```

### Issue: Database connection errors

**Check:**
1. PostgreSQL is healthy: `docker ps | grep postgres`
2. Database exists: `docker exec anwalts_postgres psql -U anwalts_user -d anwalts_ai -c '\dt'`
3. Connection string is correct

**Fix:**
```bash
# Restart PostgreSQL
docker-compose restart postgres

# Check logs
docker logs anwalts_postgres
```

### Issue: Frontend not connecting to backend

**Check:**
1. `BACKEND_BASE` environment variable
2. Backend is healthy: `curl http://localhost:8000/health`
3. Network connectivity between containers

**Debug:**
```bash
# Test from frontend container
docker exec anwalts_frontend curl http://backend:8000/health

# Check environment
docker exec anwalts_frontend env | grep BACKEND
```

---

## 📝 File Structure

```
/root/
├── docker-compose.yml              # Main orchestration
├── Dockerfile.backend              # Backend container
├── .env                            # Environment variables
│
├── Backend Python Files
├── backend-main.py                 # FastAPI main (3180 lines)
├── ai_service.py                   # AI/RAG client (271 lines)
├── auth_service.py                 # JWT auth (281 lines)
├── database.py                     # PostgreSQL (878 lines)
├── cache_service.py                # Redis cache
├── models.py                       # Pydantic models
├── smtp_utils.py                   # Email utilities
├── rag_service.py                  # RAG helpers
├── requirements.txt                # Python dependencies
│
├── Frontend Directory
├── anwalts-frontend-new/
│   ├── nuxt.config.ts              # Nuxt configuration
│   ├── package.json                # Node dependencies
│   ├── Dockerfile                  # Frontend container
│   │
│   ├── pages/                      # Nuxt pages
│   │   ├── index.vue               # Landing page
│   │   ├── assistant.vue           # AI chat (522 lines)
│   │   ├── dashboard.vue           # Dashboard (708 lines)
│   │   ├── email.vue               # Email integration
│   │   ├── documents.vue           # Document management
│   │   ├── templates.vue           # Template library
│   │   └── settings.vue            # User settings
│   │
│   ├── components/                 # Vue components
│   │   ├── PortalShell.vue         # Main layout
│   │   ├── GlassmorphismAuthModal.vue
│   │   ├── GoogleSignInButton.vue
│   │   └── ProfilePopup.vue
│   │
│   ├── server/                     # Nuxt server API
│   │   ├── api/
│   │   │   ├── ai/
│   │   │   │   └── complete.post.ts
│   │   │   ├── auth/
│   │   │   │   ├── login.post.ts
│   │   │   │   ├── register.post.ts
│   │   │   │   └── google/
│   │   │   │       ├── authorize.get.ts
│   │   │   │       └── callback.get.ts
│   │   │   └── email/
│   │   │       ├── list.get.ts
│   │   │       └── labels.get.ts
│   │   │
│   │   └── utils/
│   │       ├── backend.ts          # Backend URL helpers
│   │       ├── sessionCookie.ts    # Session management
│   │       └── supabase.ts         # Supabase client
│   │
│   ├── composables/                # Vue composables
│   │   ├── useAuthModal.ts
│   │   ├── usePortalUser.ts
│   │   └── useSupabaseAuth.ts
│   │
│   └── rag_llamacpp/               # RAG Python modules
│       ├── llama_client.py
│       ├── retrieval.py
│       ├── assistant.py
│       └── config.py
│
├── nginx/
│   └── nginx-dev.conf              # Nginx configuration
│
├── data/                           # Application data
├── models/                         # AI model files
└── legal-corpus/                   # Legal documents
```

---

## 🔗 Key URLs & Ports

### Local Development

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Main application |
| Backend API | http://localhost:8000 | FastAPI backend |
| Backend Docs | http://localhost:8000/docs | Swagger UI |
| RAG API | http://localhost:9000 | Legal AI service |
| RAG Health | http://localhost:9000/healthz | RAG status |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Cache |
| MailHog UI | http://localhost:8025 | Email testing |
| Supabase Studio | http://localhost:54323 | DB management |
| Supabase API | http://localhost:54321 | Supabase gateway |

### Production

| URL | Purpose |
|-----|---------|
| https://portal-anwalts.ai | Main site |
| https://portal-anwalts.ai/api | Backend API |
| https://portal-anwalts.ai/supabase | Supabase services |

---

## 📊 Performance & Monitoring

### Metrics to Monitor

1. **Response Times**
   - Backend /api/ai/complete: ~2-5s (RAG dependent)
   - RAG /v1/legal/answer_v2: ~1-3s (generation time)
   - Database queries: <100ms
   - Redis cache: <10ms

2. **Resource Usage**
   - Backend RAM: ~200MB
   - Frontend RAM: ~150MB
   - RAG API RAM: ~2.5GB (model loaded)
   - PostgreSQL RAM: ~100MB
   - Redis RAM: max 512MB

3. **Connection Pools**
   - PostgreSQL: 1-10 connections
   - Redis: 10 connections default

### Health Check Endpoints

```bash
# All services health
for port in 3000 8000 9000; do
  echo "Port $port:"
  curl -s http://localhost:$port/health 2>/dev/null || curl -s http://localhost:$port/healthz || echo "N/A"
done
```

---

## 🛠️ Development Workflow

### Making Changes

1. **Backend Changes**
   ```bash
   # Edit backend-main.py, ai_service.py, etc.
   
   # Rebuild and restart
   docker-compose up -d --build backend
   
   # Watch logs
   docker logs -f anwalts_backend
   ```

2. **Frontend Changes**
   ```bash
   # Edit files in anwalts-frontend-new/
   
   # Rebuild and restart
   docker-compose up -d --build frontend
   
   # Watch logs
   docker logs -f anwalts_frontend
   ```

3. **Database Schema Changes**
   ```bash
   # Connect to database
   docker exec -it anwalts_postgres psql -U anwalts_user -d anwalts_ai
   
   # Run migrations
   # (or add to scripts/init-db.sql for new deployments)
   ```

### Testing AI Responses

```bash
# Direct RAG API test
curl -X POST http://localhost:9000/v1/legal/answer_v2 \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Was sind die Pflichten eines Vermieters?",
    "k": 6
  }'

# Backend API test (requires auth)
TOKEN="your_jwt_token"
curl -X POST http://localhost:8000/api/ai/complete \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Was sind die Pflichten eines Vermieters?",
    "max_tokens": 1000
  }'
```

---

## 📚 Additional Documentation

- `ANWALTS_AI_SYSTEM_INDEX.md` - Previous system analysis
- `AI_SERVICE_DIAGNOSIS_AND_FIX.md` - AI service troubleshooting
- `DEPLOYMENT_COMPLETE.md` - Deployment notes
- `QUICK_REFERENCE.md` - Quick commands reference

---

## 🎯 Summary

**Anwalts-AI** is a production-ready legal AI assistant with:

✅ **Full-stack architecture** - Nuxt 3 frontend + FastAPI backend
✅ **RAG-powered AI** - FAISS retrieval + mT5 generation
✅ **Authentication** - Dual auth system (Supabase + JWT)
✅ **Email integration** - Gmail API with OAuth2
✅ **Document management** - Generate and store legal documents
✅ **Real-time chat** - Context-aware conversations
✅ **Scalable infrastructure** - Docker Compose orchestration
✅ **Monitoring** - Health checks and logging

**Key Technologies:**
- Frontend: Nuxt 3, Vue 3, Tailwind CSS, Pinia
- Backend: FastAPI, asyncpg, Redis, JWT
- AI: FAISS, SentenceTransformers, mT5
- Database: PostgreSQL with pgvector
- Auth: Supabase, Google OAuth
- Deployment: Docker Compose

---

*End of System Index*
