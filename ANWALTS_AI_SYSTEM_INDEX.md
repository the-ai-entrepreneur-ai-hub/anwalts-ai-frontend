# Anwalts-AI System Index & Architecture Overview

**Generated:** 2025-10-17  
**Purpose:** Comprehensive system documentation for rapid development

---

## System Overview

Anwalts-AI is a legal AI assistant platform that provides German legal document generation, legal research, and email processing capabilities using a fine-tuned Qwen legal model with RAG (Retrieval Augmented Generation).

---

## Architecture Components

### 1. Frontend (Nuxt.js/Vue 3)
- **Container:** `frontend` (anwalts-frontend:gmail-fix)
- **Port:** 3000 (external) → 3000 (internal)
- **Location:** `/root/anwalts-frontend-new/`
- **Framework:** Nuxt 4.0.3 with TypeScript
- **Key Features:**
  - Server-side rendering (SSR)
  - Supabase authentication integration
  - API proxy middleware
  - Real-time legal assistant chat

**Main Pages:**
- `/assistant` - AI legal assistant chat interface
- `/dashboard` - User dashboard with case statistics
- `/email` - Email integration and processing
- `/documents` - Document management
- `/templates` - Legal document templates
- `/settings` - User settings

**Key Components:**
- `PortalShell.vue` - Main layout wrapper
- `GlassmorphismAuthModal.vue` - Authentication modal
- `GoogleSignInButton.vue` - Google OAuth integration

**Composables:**
- `useSupabaseAuth.ts` - Supabase authentication
- `useAuthModal.ts` - Auth modal management
- `usePortalUser.ts` - User profile management

---

### 2. Backend (FastAPI)
- **Primary Container:** `backend-canary` (anwalts-backend:latest)
- **Primary Port:** 18000 (external) → 8000 (internal)
- **Proxy Container:** `backend` (alpine/socat) - Port 8000 (forwards to backend-canary)
- **Location:** `/root/backend-main.py`
- **Framework:** FastAPI with Python 3.12+

**Core Services:**
- **ai_service.py** - AI completion service (communicates with legal-rag-api)
- **auth_service.py** - JWT authentication and token management
- **database.py** - PostgreSQL database operations
- **cache_service.py** - Redis caching layer
- **smtp_utils.py** - Email sending utilities

**Key Endpoints:**

*Authentication:*
- `POST /auth/login` - User login with email/password
- `POST /auth/register` - New user registration
- `GET /auth/google/authorize` - OAuth flow start
- `GET /auth/google/callback` - OAuth callback handler
- `GET /auth/me` - Get current user info

*AI & Assistant:*
- `POST /api/assistant/chat` - Main chat endpoint (conversation-aware)
- `POST /api/ai/generate-document` - Legal document generation
- `POST /api/ai/complete-test` - Test AI completion endpoint

*Email Processing:*
- `POST /api/email/process` - Process email with AI categorization
- `GET /api/email/list` - List user emails
- `GET /api/email/labels` - Get Gmail labels

*Documents & Files:*
- `GET /api/documents` - List user documents
- `POST /api/files/upload` - File upload
- `GET /api/templates` - Get document templates

*Admin & Monitoring:*
- `GET /health` - Health check endpoint
- `GET /api/admin/*` - Admin-only routes (role-based access)

---

### 3. Legal RAG API
- **Container:** `legal-rag-api` (legal-rag-api:latest)
- **Port:** 9000 (external) → 9000 (internal)
- **Framework:** FastAPI
- **Purpose:** RAG-based legal question answering

**Model Stack:**
- **Retriever:** Fine-tuned SentenceTransformer (`outputs/retriever-legal-ft`)
- **Generator:** google/mt5-small (T5 model)
- **Vector Store:** FAISS index with German legal corpus
- **Documents:** Located in `datasets/processed/rag/`

**Endpoints:**
- `GET /healthz` - Health check
- `POST /v1/legal/answer` - Legacy answer endpoint
- `POST /v1/legal/answer_v2` - Enhanced answer endpoint with structured output

**How it works:**
1. User question → Embedded with retriever model
2. FAISS search for top-K relevant legal documents
3. Context + question → T5 generator
4. Response with citations and sources

---

### 4. Database Layer

**PostgreSQL (Supabase)**
- **Container:** `supabase_db_anwalts-frontend-new`
- **Port:** 54322 (external) → 5432 (internal)
- **Image:** public.ecr.aws/supabase/postgres:17.6.1.011

**Main Tables:**
- `users` - User accounts
- `profiles` - User profile data (Supabase)
- `documents` - Generated legal documents
- `templates` - Document templates
- `assistant_messages` - Chat conversation history
- `assistant_conversations` - Conversation metadata
- `email_messages` - Processed emails
- `files` - Uploaded file metadata

**Redis Cache**
- **Container:** `anwalts_redis` (currently stopped)
- **Port:** 6379
- **Usage:** AI response caching, rate limiting

---

### 5. Supabase Services

**Authentication Service**
- **Container:** `supabase_auth_anwalts-frontend-new`
- **Port:** 9999 (internal)
- **Features:** JWT tokens, OAuth providers, user management

**Kong API Gateway**
- **Container:** `supabase_kong_anwalts-frontend-new`
- **Port:** 54321 (external) → 8000 (internal)
- **Purpose:** API routing and authentication proxy

**Supabase Studio**
- **Container:** `supabase_studio_anwalts-frontend-new`
- **Port:** 54323 (external) → 3000 (internal)
- **Purpose:** Database management UI

**Other Supabase Services:**
- `supabase_rest_anwalts-frontend-new` - PostgREST API
- `supabase_realtime_anwalts-frontend-new` - Real-time subscriptions
- `supabase_storage_anwalts-frontend-new` - File storage
- `supabase_vector_anwalts-frontend-new` - Vector embeddings
- `supabase_pg_meta_anwalts-frontend-new` - Metadata service

---

### 6. Supporting Services

**MailHog**
- **Container:** `688d541f3681_anwalts_mailhog`
- **SMTP Port:** 1025
- **Web UI Port:** 8025
- **Purpose:** Development email testing

---

## Communication Flow

### User Authentication Flow
```
1. User clicks "Login with Google" on frontend
2. Frontend → GET /api/auth/google/authorize (Nuxt server route)
3. Nuxt server → Redirects to Google OAuth
4. Google → Redirects back to /api/auth/google/callback
5. Backend receives OAuth code → Exchanges for tokens
6. Backend creates/updates user in PostgreSQL
7. Backend generates JWT token
8. Backend sets cookies (sid, sat) and redirects to /dashboard
9. Frontend reads cookies and establishes session
```

### AI Chat Flow
```
1. User sends message in /assistant page
2. Frontend → POST /api/assistant/chat with Bearer token
3. Nuxt server (middleware checks route) → Proxies to backend
4. Backend (/api/assistant/chat endpoint):
   - Verifies JWT token
   - Retrieves conversation context from PostgreSQL
   - Calls ai_service.generate_completion()
5. ai_service.py → POST to legal-rag-api:9000/v1/legal/answer_v2
6. legal-rag-api:
   - Embeds question with retriever model
   - Searches FAISS index for relevant legal docs
   - Generates answer with T5 model
   - Returns answer with citations
7. Backend saves messages to PostgreSQL
8. Backend returns response to frontend
9. Frontend displays AI response to user
```

### Document Generation Flow
```
1. User fills out document form on frontend
2. Frontend → POST /api/ai/generate-document
3. Backend → ai_service.generate_document()
4. ai_service → POST to legal-rag-api with document prompt
5. legal-rag-api generates document content
6. Backend saves document to PostgreSQL
7. Backend returns document to frontend
8. User can download/export document
```

### Email Processing Flow
```
1. User connects Gmail via OAuth
2. Backend stores refresh token in PostgreSQL
3. User triggers email import
4. Backend → Fetches emails via Gmail API
5. For each email:
   - Backend → POST to legal-rag-api for AI categorization
   - Backend stores email with category in PostgreSQL
6. Frontend displays categorized emails
```

---

## Environment Configuration

### Key Environment Variables

**Backend (backend-canary):**
```bash
DATABASE_URL=postgresql://anwalts_user:<REDACTED_DB_PASSWORD>@postgres:5432/anwalts_ai
REDIS_URL=redis://redis:6379
CORS_ORIGIN=https://portal-anwalts.ai
API_BASE_URL=https://portal-anwalts.ai

# Google OAuth
GOOGLE_CLIENT_ID=<REDACTED_GOOGLE_CLIENT_ID>
GOOGLE_CLIENT_SECRET=<REDACTED_GOOGLE_SECRET>
GOOGLE_REDIRECT_URI=https://portal-anwalts.ai/api/auth/google/callback

# Supabase
SUPABASE_URL=https://portal-anwalts.ai/supabase
SUPABASE_SERVICE_ROLE_KEY=<REDACTED_SUPABASE_SERVICE_ROLE_KEY>
DASHBOARD_SERVICE_KEY=<REDACTED_DASHBOARD_SERVICE_KEY>

# AI Model
LOCAL_AI_KIND=sidecar
LOCAL_AI_URL=https://portal-anwalts.ai  # Proxies to legal-rag-api:9000
LOCAL_AI_MODEL=qwen_legal_q4_k_m

# Email
SMTP_HOST=mailhog
SMTP_PORT=1025
SMTP_TLS=0

# Features
FEEDBACK_V1=true
DEBUG_PASSWORD_RESET=1
```

**Frontend (frontend):**
```bash
BACKEND_BASE=http://backend:8000  # Internal Docker network
NUXT_PUBLIC_API_BASE=/api
NODE_OPTIONS=--max_old_space_size=3072

# Supabase
SUPABASE_URL=https://portal-anwalts.ai/supabase
SUPABASE_ANON_KEY=sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH
SUPABASE_SERVICE_ROLE_KEY=<REDACTED_SUPABASE_SERVICE_ROLE_KEY>

# Google OAuth
GOOGLE_CLIENT_ID=<REDACTED_GOOGLE_CLIENT_ID>
GOOGLE_CLIENT_SECRET=<REDACTED_GOOGLE_SECRET>
GOOGLE_REDIRECT_URI=https://portal-anwalts.ai/api/auth/google/callback
```

**Legal RAG API:**
```bash
INDEX_PATH=datasets/processed/rag/index.faiss
META_PATH=datasets/processed/rag/meta.jsonl
RETRIEVER_PATH=outputs/retriever-legal-ft
GENERATOR=google/mt5-small
TOP_K=6
```

---

## Network Architecture

### Docker Network: `anwalts-frontend-new_default` (172.18.0.0/16)

**Container IPs:**
- frontend: 172.18.0.17
- backend-canary: 172.18.0.15
- legal-rag-api: 172.18.0.16

### External Access Points

**Production Domain:** `portal-anwalts.ai`

**Ports:**
- 80/443 → Nginx (reverse proxy)
- 3000 → Frontend (development)
- 8000 → Backend proxy (socat → backend-canary:8000)
- 18000 → Backend canary (direct access)
- 9000 → Legal RAG API
- 54321 → Supabase Kong API Gateway
- 54322 → Supabase PostgreSQL
- 54323 → Supabase Studio
- 54324 → Supabase Inbucket (email)
- 54327 → Supabase Analytics
- 8025 → MailHog Web UI
- 1025 → MailHog SMTP

---

## File Structure

```
/root/
├── anwalts-frontend-new/          # Frontend Nuxt.js application
│   ├── pages/                     # Vue pages (routes)
│   │   ├── assistant.vue          # AI chat interface
│   │   ├── dashboard.vue          # Main dashboard
│   │   ├── email.vue              # Email management
│   │   ├── documents.vue          # Document management
│   │   └── ...
│   ├── components/                # Vue components
│   │   ├── PortalShell.vue        # Main layout
│   │   ├── GlassmorphismAuthModal.vue
│   │   └── ...
│   ├── composables/               # Vue composables
│   │   ├── useSupabaseAuth.ts
│   │   └── ...
│   ├── server/                    # Nuxt server routes
│   │   ├── api/                   # API routes
│   │   │   ├── auth/              # Auth endpoints
│   │   │   ├── dashboard/         # Dashboard endpoints
│   │   │   └── email/             # Email endpoints
│   │   ├── middleware/            # Server middleware
│   │   │   └── api-proxy.ts       # Backend API proxy
│   │   └── utils/                 # Server utilities
│   ├── nuxt.config.ts             # Nuxt configuration
│   ├── package.json               # Frontend dependencies
│   └── Dockerfile                 # Frontend Docker build
│
├── backend-main.py                # Main FastAPI backend (3152 lines)
├── ai_service.py                  # AI service integration
├── auth_service.py                # JWT authentication
├── database.py                    # PostgreSQL operations
├── cache_service.py               # Redis caching
├── smtp_utils.py                  # Email utilities
├── models.py                      # Pydantic models
├── requirements.txt               # Backend dependencies
├── Dockerfile.backend             # Backend Docker build
│
├── docker-compose.yml             # Main orchestration file
├── nginx/                         # Nginx reverse proxy config
│   ├── nginx-dev.conf
│   └── sites-dev/
│
├── data/                          # ML training data and datasets
│   ├── datasets/                  # Legal corpus
│   │   └── processed/
│   │       └── rag/               # FAISS index & metadata
│   └── outputs/
│       └── retriever-legal-ft/    # Fine-tuned retriever
│
├── models/                        # ML model storage
├── legal-corpus/                  # Legal document corpus
│
└── openspec/                      # Change proposals & specs
    ├── AGENTS.md
    └── changes/
        ├── connect-gmail-integration/
        └── connect-assistant-chat/
```

---

## Development Workflow

### Starting the System
```bash
# Start all services
docker-compose up -d

# Check status
docker ps

# View logs
docker logs -f frontend
docker logs -f backend-canary
docker logs -f legal-rag-api
```

### Making Changes

**Frontend Changes:**
```bash
cd /root/anwalts-frontend-new
# Edit files in pages/, components/, or server/
# Changes hot-reload automatically (dev mode)
# Rebuild for production:
docker-compose up -d --build frontend
```

**Backend Changes:**
```bash
# Edit backend-main.py or service files
# Restart backend:
docker-compose restart backend-canary
# Or rebuild:
docker-compose up -d --build backend
```

**Database Changes:**
```bash
# Connect to PostgreSQL
docker exec -it supabase_db_anwalts-frontend-new psql -U postgres -d postgres
# Or use Supabase Studio at http://localhost:54323
```

### Testing

**Health Checks:**
```bash
# Backend
curl http://localhost:18000/health

# Legal RAG API
curl http://localhost:9000/healthz

# Frontend
curl http://localhost:3000
```

**API Testing:**
```bash
# Test AI completion (requires auth token)
curl -X POST http://localhost:18000/api/assistant/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Was ist § 823 BGB?", "max_tokens": 500}'

# Test legal RAG directly
curl -X POST http://localhost:9000/v1/legal/answer_v2 \
  -H "Content-Type: application/json" \
  -d '{"question": "Was ist Schadensersatz?", "k": 6}'
```

---

## Key Technologies & Libraries

### Frontend
- **Nuxt.js 4.0.3** - Vue 3 meta-framework with SSR
- **@supabase/supabase-js** - Supabase client
- **Tailwind CSS** - Utility-first CSS
- **Pinia** - Vue state management
- **@nuxt/ui** - UI component library

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for PostgreSQL
- **asyncpg** - Async PostgreSQL driver
- **redis** - Redis client for caching
- **httpx** - Async HTTP client
- **PyJWT** - JWT token handling
- **bcrypt** - Password hashing
- **supabase-py** - Supabase Python client

### AI/ML Stack
- **SentenceTransformers** - Embedding models
- **FAISS** - Vector similarity search
- **Transformers** - HuggingFace models
- **PyTorch** - Deep learning framework
- **google/mt5-small** - T5 generator model

---

## Common Operations

### Adding a New API Endpoint

**Backend (backend-main.py):**
```python
@app.post("/api/my-endpoint")
async def my_endpoint(
    request_data: MyRequestModel,
    current_user: UserInDB = Depends(get_current_user)
):
    # Implementation
    return {"result": "success"}
```

**Frontend (server/api/):**
```typescript
// server/api/my-endpoint.post.ts
export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  // Either handle here or proxy to backend
  return { result: "success" }
})
```

### Adding a New Page

```bash
cd /root/anwalts-frontend-new/pages
# Create new-page.vue
```

```vue
<template>
  <PortalShell>
    <div>Your content</div>
  </PortalShell>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })
</script>
```

### Updating the AI Model

The legal RAG API uses a fine-tuned model located in `/root/anwalts-frontend-new/rag_llamacpp/` or mounted data volumes.

To update:
1. Replace model files in `outputs/retriever-legal-ft/`
2. Update FAISS index in `datasets/processed/rag/`
3. Restart legal-rag-api container

---

## Security Considerations

### Authentication
- JWT tokens expire after 24 hours
- HttpOnly cookies prevent XSS attacks
- CSRF tokens required for state-changing operations
- Password hashing with bcrypt

### Authorization
- Role-based access control (admin, user)
- `/api/admin/*` routes protected by middleware
- User-scoped data queries (can't access other users' data)

### API Security
- CORS restricted to `portal-anwalts.ai`
- Rate limiting on sensitive endpoints
- Input validation with Pydantic models
- SQL injection prevention with parameterized queries

---

## Monitoring & Debugging

### Logs
```bash
# Backend logs
docker logs -f backend-canary

# Frontend logs
docker logs -f frontend

# Legal RAG API logs
docker logs -f legal-rag-api

# Database logs
docker logs -f supabase_db_anwalts-frontend-new
```

### Performance Monitoring
- Backend health endpoint: `/health`
- Response includes DB, cache, and AI service status
- Generation time tracking for AI responses
- Token usage logging

### Common Issues

**Issue: Frontend can't reach backend**
- Check api-proxy middleware configuration
- Verify BACKEND_BASE environment variable
- Check Docker network connectivity

**Issue: AI responses are slow**
- Check legal-rag-api logs for model loading
- FAISS index may need optimization
- Increase max_tokens parameter

**Issue: Authentication fails**
- Verify JWT_SECRET_KEY matches between services
- Check Supabase connection
- Verify Google OAuth credentials

---

## Recent Changes & Features

### Gmail Integration
- OAuth 2.0 flow for Gmail access
- Email fetching and categorization
- AI-powered email processing
- Refresh token storage for offline access

### Assistant Chat
- Conversation history tracking
- Context-aware responses
- Message feedback system
- Real-time typing indicators

### Document Generation
- Multiple legal document types
- Template-based generation
- Variable interpolation
- Export to PDF/DOCX (planned)

---

## Next Development Tasks

Based on openspec proposals:
1. **Email Integration Enhancement** - Improve categorization accuracy
2. **Document Export** - Add PDF/DOCX export functionality
3. **Template Editor** - Visual template creation interface
4. **Admin Dashboard** - User management and analytics
5. **Multi-language Support** - Extend beyond German

---

## Quick Reference Commands

```bash
# System Status
docker ps
docker-compose ps

# Restart Services
docker-compose restart frontend backend-canary legal-rag-api

# View Real-time Logs
docker-compose logs -f

# Database Access
docker exec -it supabase_db_anwalts-frontend-new psql -U postgres

# Redis CLI
docker exec -it anwalts_redis redis-cli

# Clean Rebuild
docker-compose down
docker-compose up -d --build

# Check Disk Usage
du -sh /root/anwalts-frontend-new
du -sh /root/data

# Network Inspection
docker network inspect anwalts-frontend-new_default
```

---

**End of System Index**

This document should be updated as the system evolves. Last updated: 2025-10-17
