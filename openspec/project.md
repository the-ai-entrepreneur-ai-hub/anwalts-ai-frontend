# Project Context

## Purpose
Anwalts AI is a legal document generation system designed for lawyers in the German market. The platform uses AI-powered document creation, retrieval-augmented generation (RAG), and template management to help legal professionals generate, manage, and customize legal documents efficiently.

**Core Goals:**
- Provide AI-assisted legal document generation with context-aware suggestions
- Streamline legal workflows through template management and automation
- Deliver a professional, user-friendly interface for legal practitioners
- Ensure secure authentication and document management

## Tech Stack

### Frontend
- **Framework**: Nuxt.js 4.x (Vue 3, SSR/SSG)
- **UI Libraries**: Nuxt UI, Tailwind CSS 4.x
- **State Management**: Pinia
- **Authentication**: Supabase Auth (@supabase/ssr, @supabase/supabase-js)
- **Language**: TypeScript (composables, server routes, middleware)
- **Build Tool**: Vite
- **Testing**: Playwright, Vitest
- **Additional**: Unframer (design integration), React 19 (embedded components)

### Backend
- **Framework**: FastAPI 0.118+ (Python), Uvicorn 0.37+ (ASGI server)
- **Database**: PostgreSQL with pgvector extension (asyncpg, SQLAlchemy 2.0)
- **Authentication**: JWT (PyJWT), bcrypt, Supabase
- **AI Integration**: Custom Qwen legal model via FastAPI sidecar (`LOCAL_AI_URL`)
- **RAG System**: llama.cpp for legal document retrieval and context enhancement
- **Caching**: Redis (cachetools wrapper, direct redis client for rate limiting)
- **HTTP Client**: httpx (async), requests
- **Validation**: Pydantic 2.x
- **Testing**: pytest, pytest-mock
- **Additional Features**: Feedback system (V1) with rate limiting, upload processor subsystem

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx (reverse proxy for routing and SSL termination)
- **Database Extensions**: pgvector for PostgreSQL (vector similarity search)
- **Cache**: Redis 7 (Alpine) with persistence and LRU eviction
- **Email Testing**: MailHog (development SMTP server with web UI)
- **Deployment**: Linux (Ubuntu/Debian)
- **Environment**: python-dotenv for configuration

### AI & ML
- **Primary AI**: Custom-trained Qwen legal model (qwen_legal_q4_k_m) hosted via FastAPI sidecar
- **Sidecar URL**: Configured via `LOCAL_AI_URL` (default: https://portal-anwalts.ai)
- **RAG**: Custom llama.cpp integration for legal corpus retrieval
- **Model Format**: Quantized Q4_K_M for performance optimization
- **Inference**: Remote sidecar handles all AI generation requests
- **Use Cases**: Legal document generation, context-aware suggestions, German legal text generation
- **Note**: No external AI APIs (Together AI, OpenAI) - all inference is self-hosted

## Project Conventions

### Code Style

#### Frontend (TypeScript/Vue)
- **File Naming**: kebab-case for components, pages, and composables (`use-auth-modal.ts`, `glassmorphism-auth-modal.vue`)
- **Component Naming**: PascalCase for component exports (`GlassmorphismAuthModal`)
- **Composables**: Prefix with `use` (e.g., `useAuthModal`, `usePortalUser`, `useSupabaseAuth`)
- **Formatting**: Nuxt/Vue standard formatting with Prettier-style conventions
- **Imports**: Auto-imports enabled for Nuxt composables and components
- **CSS**: Tailwind utility-first approach; scoped styles when necessary

#### Backend (Python)
- **File Naming**: snake_case for all Python files (`auth_service.py`, `cache_service.py`)
- **Class Naming**: PascalCase for classes
- **Function Naming**: snake_case for functions and methods
- **Formatting**: PEP 8 compliance
- **Type Hints**: Use Pydantic models for validation and type safety
- **Async**: Prefer async/await for I/O operations (database, HTTP requests)

### Architecture Patterns

#### Frontend Architecture
- **Pages**: Route-based pages in `/pages` directory using Nuxt file-based routing
- **Components**: Reusable Vue components in `/components` with single responsibility
- **Composables**: Business logic and state management in `/composables`
- **Middleware**: Route guards in `/middleware` for authentication and authorization
- **Server Routes**: API routes in `/server/api` for server-side logic
- **Layouts**: Shared layouts in `/layouts` (default, framer)
- **State**: Pinia stores in `/stores` for global state management
- **Plugins**: Vue/Nuxt plugins in `/plugins` for initialization logic

#### Backend Architecture
- **Main Server**: `backend-main.py` serves as the FastAPI application entry point
- **Services**: Modular service files (`auth_service.py`, `ai_service.py`, `cache_service.py`)
- **Database**: SQLAlchemy ORM with async support (`database.py`, `models.py`)
- **RAG System**: Isolated in `/rag_llamacpp` for legal document processing
- **API Design**: RESTful endpoints with clear resource naming
- **Error Handling**: Consistent error responses with appropriate HTTP status codes

#### Design Patterns
- **Separation of Concerns**: Clear boundaries between presentation, business logic, and data layers
- **Composable Pattern**: Frontend logic encapsulated in reusable composables
- **Service Layer**: Backend business logic isolated in service modules
- **Repository Pattern**: Database access abstracted through SQLAlchemy models
- **Middleware Pattern**: Request/response interceptors for auth, logging, error handling

### Testing Strategy

#### Frontend Testing
- **E2E Tests**: Playwright for end-to-end user flows
- **Unit Tests**: Vitest for composables, utilities, and components
- **Browser Automation**: Puppeteer for additional testing scenarios
- **HTML Parsing**: Cheerio for DOM manipulation and validation in tests
- **Test Files**: Co-located with source files or in `/tests` directory
- **Coverage**: Focus on critical user paths (authentication, document generation, template management)

#### Backend Testing
- **Unit Tests**: pytest for service layer and business logic
- **Mocking**: pytest-mock for external dependencies (AI APIs, database)
- **Test Organization**: Tests mirror source structure
- **Coverage**: Aim for critical paths (auth, AI generation, RAG system)

#### Testing Philosophy
- Test behavior, not implementation
- Focus on user-facing functionality
- Mock external services (AI APIs, Supabase)
- Maintain fast test execution

### Git Workflow
- **Branch Strategy**: Feature branches from main (e.g., `feature/oauth-google`, `fix/auth-redirect`)
- **Commit Messages**: Descriptive, present-tense (e.g., "Add Google OAuth support", "Fix authentication redirect loop")
- **Pull Requests**: Required for changes; include description and impact
- **Auto-Sync**: Server commits automatically push to GitHub; manual sync from GitHub via `/root/sync-from-github.sh`

## Domain Context

### Legal Domain Knowledge
- **Target Audience**: German-speaking lawyers and legal professionals
- **Document Types**: Legal contracts, templates, forms, and correspondence
- **Language**: Primarily German (de) with some English in technical components
- **Legal Corpus**: Custom legal document database used for RAG context enhancement
- **Compliance**: Must handle sensitive legal information securely

### Business Context
- **B2B SaaS**: Professional tool for law firms and individual practitioners
- **Document Generation**: AI-assisted creation with human review and editing
- **Template Library**: Pre-built legal document templates for common use cases
- **Email Integration**: Portal for professional communication and document delivery

## Important Constraints

### Technical Constraints
- **Database**: Must use PostgreSQL with pgvector extension for production reliability
- **Authentication**: Supabase Auth required for user management
- **AI Sidecar**: Custom Qwen model sidecar must be available at `LOCAL_AI_URL`
- **AI Latency**: Document generation must complete within 120s timeout
- **RAG Performance**: Legal corpus search must complete within acceptable latency
- **Rate Limiting**: Redis-backed rate limiting for feedback and API endpoints
- **SSR Requirements**: Server-side rendering for SEO and performance on public pages
- **Docker Deployment**: Must run in containerized environment with Nginx

### Security Constraints
- **Authentication**: JWT tokens with secure refresh mechanisms
- **Password Storage**: bcrypt hashing required for all passwords
- **OAuth**: Google OAuth with proper redirect URI validation
- **API Keys**: Environment variables only; never commit secrets
- **HTTPS**: All production traffic must use TLS
- **Session Management**: Secure cookie handling with httpOnly flags

### Business Constraints
- **German Market**: UI/UX must cater to German legal professionals
- **Data Residency**: Consider EU data protection requirements (GDPR)
- **Availability**: High uptime expected for professional users
- **Performance**: Fast document generation (<5s for typical requests)

### Regulatory Constraints
- **GDPR Compliance**: Handle personal data in accordance with EU regulations
- **Legal Document Integrity**: Generated documents must be accurate and reliable
- **Audit Trail**: Track document creation and modifications for compliance

## External Dependencies

### AI Services
- **Qwen Legal Model Sidecar**: Custom-trained FastAPI service for legal document generation
  - `LOCAL_AI_URL`: URL to the sidecar service (default: https://portal-anwalts.ai)
  - `LOCAL_AI_MODEL`: Model identifier (default: qwen_legal_q4_k_m)
  - `LOCAL_AI_KIND`: Deployment type (default: sidecar)
- **Note**: No external commercial AI APIs used; all inference is self-hosted

### Authentication & Database
- **Supabase**: Authentication, user management, and database hosting
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`
  - `SUPABASE_SERVICE_ROLE_KEY`
- **PostgreSQL**: Primary database (via Supabase or standalone)

### OAuth Providers
- **Google OAuth**:
  - `GOOGLE_CLIENT_ID`
  - `GOOGLE_CLIENT_SECRET`
  - `GOOGLE_REDIRECT_URI`

### Infrastructure
- **Nginx**: Reverse proxy for routing and SSL termination
- **Docker**: Container orchestration for deployment
- **Redis**: Required caching and rate limiting layer
  - `REDIS_URL`: Connection string (default: redis://redis:6379)
  - Configuration: 512MB maxmemory, allkeys-lru eviction policy
- **PostgreSQL with pgvector**: Vector database extension for similarity search
  - `DATABASE_URL`: Connection string
  - Extensions: pgvector for embedding-based retrieval

### Development Tools
- **Playwright**: Browser automation for E2E testing
- **Vitest**: Fast unit testing framework
- **pytest**: Python testing framework
- **Puppeteer**: Node library for headless browser testing
- **Cheerio**: Fast HTML parsing and manipulation for tests
- **MailHog**: Development SMTP server (ports 1025 SMTP, 8025 Web UI)
- **Tailwind CSS**: Utility-first CSS framework (CDN and npm)

### Monitoring & Logging
- **Backend Logging**: Python logging module for FastAPI
- **Frontend Logging**: Console-based logging with potential integration for production monitoring
- **Error Tracking**: (To be configured) Consider Sentry or similar for production error tracking

## Environment Configuration

### Required Environment Variables

#### Database & Cache
```bash
# PostgreSQL configuration
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_DB=anwalts_ai
POSTGRES_USER=anwalts_user
POSTGRES_PASSWORD=<REDACTED_DB_PASSWORD>
DATABASE_URL=postgresql://anwalts_user:<REDACTED_DB_PASSWORD>@127.0.0.1:5432/anwalts_ai

# Redis configuration
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL=redis://127.0.0.1:6379/0
```

#### Authentication & Security
```bash
# JWT & security keys
SECRET_KEY=<64-char-hex-string>
JWT_SECRET_KEY=<64-char-hex-string>
SESSION_SECRET=<64-char-hex-string>
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Session & cookies
SESSION_COOKIE_NAME=sid
PUBLIC_SESSION_COOKIE=sat
SESSION_DOMAIN=portal-anwalts.ai
COOKIE_SAMESITE=none

# Dashboard access
DASHBOARD_SERVICE_KEY=<secure-dashboard-key>
```

#### OAuth Providers
```bash
# Google OAuth
GOOGLE_CLIENT_ID=<google-client-id>
GOOGLE_CLIENT_SECRET=<google-client-secret>
GOOGLE_REDIRECT_URI=https://portal-anwalts.ai/api/auth/google/callback
GOOGLE_REDIRECT_PATH=/api/auth/google/callback
```

#### Supabase (Optional/Alternative Auth)
```bash
SUPABASE_URL=https://portal-anwalts.ai/supabase
SUPABASE_ANON_KEY=<supabase-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<supabase-service-role-key>
```

#### Application URLs
```bash
# CORS & API configuration
CORS_ORIGIN=https://portal-anwalts.ai
API_BASE_URL=https://portal-anwalts.ai
PUBLIC_BASE_URL=https://portal-anwalts.ai
```

#### AI Services
```bash
# Local AI sidecar configuration
LOCAL_AI_KIND=sidecar
LOCAL_AI_URL=https://portal-anwalts.ai
LOCAL_AI_MODEL=qwen_legal_q4_k_m
```

#### Email & SMTP
```bash
# SMTP configuration (MailHog for dev, real SMTP for prod)
SMTP_HOST=127.0.0.1  # or mailhog in Docker
SMTP_PORT=1025       # 1025 for MailHog, 587/465 for production
SMTP_TLS=0           # 1 for production SMTP
SMTP_FROM=no-reply@anwalts.ai
DEBUG_PASSWORD_RESET=1  # Enable for development
```

#### Feature Flags
```bash
# Optional feature toggles
FEEDBACK_V1=true  # Enable feedback system
```

#### Frontend-Specific (Nuxt)
```bash
# Backend connection
BACKEND_BASE=http://backend:8000  # or http://localhost:8000 for dev
NUXT_PUBLIC_API_BASE=/api

# Nitro server
NITRO_HOST=0.0.0.0
NITRO_PORT=3000
NODE_OPTIONS=--max_old_space_size=3072
```

### Port Configuration

| Service | Internal Port | External Port | Purpose |
|---------|--------------|---------------|---------|
| Frontend (Nuxt) | 3000 | 3000 | SSR application server |
| Backend (FastAPI) | 8000 | 8000 | API server |
| Backend (AI Sidecar) | 8010 | 8010 | AI inference endpoint |
| PostgreSQL | 5432 | 5432 | Database |
| Redis | 6379 | 6379 | Cache and rate limiting |
| MailHog SMTP | 1025 | 1025 | Development email (SMTP) |
| MailHog Web UI | 8025 | 8025 | Email testing interface |
| Nginx | 80 | 80 | HTTP reverse proxy |
| Nginx | 443 | 443 | HTTPS reverse proxy |

### Docker Service Configuration

#### Service Details

**postgres** (`anwalts_postgres`)
- Image: `pgvector/pgvector:pg15`
- Extensions: pgvector for vector similarity search
- Health check: `pg_isready -U anwalts_user -d anwalts_ai`
- Volumes: `postgres_data:/var/lib/postgresql/data`, init scripts
- Restart: unless-stopped

**redis** (`anwalts_redis`)
- Image: `redis:7-alpine`
- Configuration: 512MB maxmemory, allkeys-lru eviction, AOF persistence
- Health check: `redis-cli ping`
- Volumes: `redis_data:/data`
- Restart: unless-stopped

**mailhog** (`anwalts_mailhog`)
- Image: `mailhog/mailhog:v1.0.1`
- Ports: 1025 (SMTP), 8025 (Web UI)
- Purpose: Development email testing
- Restart: unless-stopped

**backend** (`anwalts_backend`)
- Build: `Dockerfile.backend` in root directory
- Ports: 8000 (API), 8010 (AI sidecar)
- Depends on: postgres, redis (with health checks)
- Volumes: `./models`, `./legal-corpus`, `./data`
- Health check: `curl -f http://localhost:8000/health`
- Restart: unless-stopped

**frontend** (`anwalts_frontend`)
- Build: `Dockerfile` in `./anwalts-frontend-new`
- Port: 3000
- Depends on: backend (with health check)
- Health check: Node.js HTTP GET on port 3000
- Restart: unless-stopped

**nginx** (`anwalts_nginx`)
- Image: `nginx:alpine`
- Ports: 80, 443
- Volumes: nginx config, Let's Encrypt certificates
- Extra hosts: `host.docker.internal:host-gateway`
- Depends on: frontend, backend
- Health check: `curl -f http://localhost`
- Restart: unless-stopped

#### Volume Mounts

**Backend Container:**
- `/app/models` - AI model files (qwen_legal_q4_k_m)
- `/app/legal-corpus` - Legal document corpus for RAG
- `/app/data` - Application data and uploads

**PostgreSQL Container:**
- `/var/lib/postgresql/data` - Database files (persistent)
- `/docker-entrypoint-initdb.d/init-db.sql` - Initialization scripts

**Redis Container:**
- `/data` - Redis AOF and RDB files (persistent)

**Nginx Container:**
- `/etc/nginx/nginx.conf` - Main nginx configuration
- `/etc/nginx/conf.d` - Site-specific configurations
- `/etc/letsencrypt` - SSL certificates (read-only)

## Project Structure

### Frontend Directory Structure

```
anwalts-frontend-new/
├── pages/                    # Route-based pages (Nuxt auto-routing)
│   ├── index.vue            # Landing page (public)
│   ├── assistant.vue        # AI document generator (protected)
│   ├── documents.vue        # Document management (protected)
│   ├── email.vue            # Email portal (protected)
│   ├── templates.vue        # Template library (protected)
│   ├── settings.vue         # User settings (protected)
│   ├── dashboard.vue        # Dashboard overview (protected)
│   ├── register.vue         # User registration
│   ├── simple-login.vue     # Login page
│   └── dashboard/           # Dashboard sub-pages
│       ├── cases.vue
│       ├── research.vue
│       └── settings.vue
├── components/              # Reusable Vue components
│   ├── GlassmorphismAuthModal.vue
│   ├── PortalShell.vue      # Main navigation wrapper
│   └── ...
├── composables/             # Vue 3 composables (business logic)
│   ├── useAuthModal.ts      # Authentication modal state
│   ├── usePortalUser.ts     # User profile management
│   └── useSupabaseAuth.ts   # Supabase auth integration
├── server/                  # Nuxt server routes (SSR API)
│   ├── api/                 # API endpoints
│   │   ├── auth/            # Authentication endpoints
│   │   ├── dashboard/       # Dashboard data
│   │   ├── email/           # Email operations
│   │   └── debug/           # Debug endpoints
│   ├── routes/              # Custom server routes
│   │   └── post-auth.get.ts # OAuth callback handler
│   ├── middleware/          # Server middleware
│   └── utils/               # Server utilities
├── middleware/              # Route middleware (client & server)
│   ├── auth.ts              # Authentication guard
│   └── ...
├── stores/                  # Pinia state management
│   └── dashboard.ts         # Dashboard state
├── layouts/                 # Page layouts
│   ├── default.vue          # Default layout
│   └── framer.vue           # Framer integration layout
├── plugins/                 # Nuxt plugins
│   └── ...
├── assets/                  # Static assets & styles
│   └── css/
│       ├── tailwind.css     # Tailwind imports
│       └── main.css         # Custom global styles
├── public/                  # Public static files (served as-is)
│   ├── favicon.png
│   └── shared/
│       └── gbutton.js       # Google button script
├── tests/                   # Playwright & Vitest tests
├── nuxt.config.ts           # Nuxt configuration
├── tailwind.config.ts       # Tailwind configuration
├── package.json             # Node dependencies
├── Dockerfile               # Frontend container build
└── requirements.txt         # Python deps (for testing)
```

### Backend Directory Structure

```
/root/                       # Backend root
├── backend-main.py          # Main FastAPI application entry point
├── auth_service.py          # Authentication service layer
├── ai_service.py            # AI integration service
├── cache_service.py         # Redis caching service
├── database.py              # SQLAlchemy database setup
├── models.py                # Database models (User, Template, etc.)
├── smtp_utils.py            # Email sending utilities
├── requirements.txt         # Python dependencies
├── Dockerfile.backend       # Backend container build
├── docker-compose.yml       # Multi-service orchestration
├── .env                     # Environment variables
├── backend/                 # Backend utilities
│   └── ...
├── rag_llamacpp/            # RAG system implementation
│   └── ...
├── models/                  # AI model files
│   └── qwen_legal_q4_k_m    # Quantized Qwen model
├── legal-corpus/            # Legal document corpus for RAG
│   └── ...
├── data/                    # Application data (uploads, exports)
│   └── ...
├── scripts/                 # Database initialization scripts
│   └── init-db.sql
└── nginx/                   # Nginx configuration
    ├── nginx-dev.conf       # Main nginx config
    └── sites-dev/           # Site-specific configs
```

### Key Backend Modules

**`backend-main.py`** - Main FastAPI application with all route handlers:
- Authentication routes: `/auth/*`, `/api/auth/*`
- User profile: `/api/user/profile`
- Template management: `/api/templates`
- Document operations: `/api/documents/*`, `/api/files/*`
- AI completion: `/api/ai/complete`, `/api/ai/generate-document`
- Assistant features: `/api/assistant/feedback`, `/api/assistant/edit`
- Clipboard & clauses: `/api/clipboard`, `/api/clauses`
- Dashboard: `/internal/dashboard-summary/{user_id}`
- OAuth callbacks: `/auth/google/callback`, `/api/auth/google/callback`

**Service Modules:**
- `auth_service.py` - User authentication, JWT handling, password management
- `ai_service.py` - AI model integration, prompt management
- `cache_service.py` - Redis caching layer, rate limiting
- `database.py` - Database connection pool, session management
- `models.py` - SQLAlchemy ORM models for all database tables

## Development Workflow

### Local Development Setup

#### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.12+ (for backend development)
- Git

#### Initial Setup

1. **Clone the repository:**
```bash
cd /root
git clone <repository-url> anwalts-frontend-new
```

2. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start infrastructure services:**
```bash
docker-compose up -d postgres redis mailhog
```

4. **Install frontend dependencies:**
```bash
cd anwalts-frontend-new
npm install
```

5. **Install backend dependencies:**
```bash
cd /root
pip install -r requirements.txt
```

#### Running Development Servers

**Frontend (Nuxt with HMR):**
```bash
cd /root/anwalts-frontend-new
npm run dev
# Runs on http://localhost:3000
```

**Backend (FastAPI with auto-reload):**
```bash
cd /root
python backend-main.py
# Runs on http://localhost:8000
# API docs at http://localhost:8000/docs
```

**Access MailHog:**
- Web UI: http://localhost:8025
- SMTP: localhost:1025

### Production Deployment

#### Full Stack Deployment

1. **Build and start all services:**
```bash
cd /root
docker-compose up -d --build
```

2. **Verify services are healthy:**
```bash
docker-compose ps
docker-compose logs -f
```

3. **Access the application:**
- Production: https://portal-anwalts.ai
- Nginx status: http://localhost

#### Frontend-Only Deployment

When only frontend changes are made:

```bash
cd /root/anwalts-frontend-new
npm run build                    # Build Nuxt app
docker build -t anwalts-frontend .
docker stop anwalts_frontend
docker rm anwalts_frontend
docker-compose up -d frontend
docker exec anwalts_nginx nginx -s reload
```

#### Backend-Only Deployment

When only backend changes are made:

```bash
cd /root
docker build -t anwalts-backend -f Dockerfile.backend .
docker stop anwalts_backend
docker rm anwalts_backend
docker-compose up -d backend
```

#### Hot Reload (Development)

For rapid iteration without container rebuilds:

**Frontend:**
```bash
# Run Nuxt dev server outside Docker
cd /root/anwalts-frontend-new
BACKEND_BASE=http://localhost:8000 npm run dev
```

**Backend:**
```bash
# Run FastAPI with auto-reload
cd /root
uvicorn backend-main:app --reload --host 0.0.0.0 --port 8000
```

### Testing Workflow

#### Frontend Tests

**Unit Tests (Vitest):**
```bash
cd /root/anwalts-frontend-new
npm run test
```

**E2E Tests (Playwright):**
```bash
cd /root/anwalts-frontend-new
npx playwright test
npx playwright test --ui  # Interactive mode
```

#### Backend Tests

**Unit Tests (pytest):**
```bash
cd /root
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html
```

### Database Management

**Access PostgreSQL:**
```bash
docker exec -it anwalts_postgres psql -U anwalts_user -d anwalts_ai
```

**Run migrations (manual):**
```bash
# Currently manual SQL migrations in scripts/init-db.sql
# Future: Consider Alembic for automated migrations
```

**Backup database:**
```bash
docker exec anwalts_postgres pg_dump -U anwalts_user anwalts_ai > backup.sql
```

**Restore database:**
```bash
cat backup.sql | docker exec -i anwalts_postgres psql -U anwalts_user -d anwalts_ai
```

### Redis Management

**Access Redis CLI:**
```bash
docker exec -it anwalts_redis redis-cli
```

**Clear cache:**
```bash
docker exec anwalts_redis redis-cli FLUSHALL
```

**Monitor Redis:**
```bash
docker exec anwalts_redis redis-cli MONITOR
```

### Nginx Configuration

**Reload configuration:**
```bash
docker exec anwalts_nginx nginx -s reload
```

**Test configuration:**
```bash
docker exec anwalts_nginx nginx -t
```

**View logs:**
```bash
docker logs anwalts_nginx -f
```

### Git Workflow

**Auto-sync (Server → GitHub):**
- Commits on the server automatically push to GitHub
- Configured via git hooks

**Manual sync (GitHub → Server):**
```bash
/root/sync-from-github.sh
```

**Branch workflow:**
```bash
# Create feature branch
cd /root/anwalts-frontend-new
git checkout -b feature/new-feature

# Make changes, commit
git add .
git commit -m "Add new feature"

# Push to remote
git push -u origin feature/new-feature
```

## API Endpoint Reference

### Authentication Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/register-full` | Register with full profile |
| POST | `/auth/login` | Login with credentials |
| POST | `/auth/logout` | Logout current user |
| GET | `/auth/me` | Get current user info |
| GET | `/auth/validate` | Validate JWT token |
| POST | `/auth/forgot-password` | Request password reset |
| POST | `/auth/reset-password` | Reset password with token |
| POST | `/auth/change-password` | Change password (authenticated) |

### OAuth Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/auth/google/authorize` | Initiate Google OAuth flow |
| GET | `/auth/google/callback` | Google OAuth callback |
| GET | `/api/auth/google/callback` | Alternative OAuth callback |

### User Profile

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/user/profile` | Get user profile |
| POST | `/api/user/profile` | Update user profile |

### Templates

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/templates` | List all templates |
| POST | `/api/templates` | Create new template |
| PUT | `/api/templates/{id}` | Update template |
| DELETE | `/api/templates/{id}` | Delete template |

### Documents

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/ai/generate-document` | Generate document with AI |
| POST | `/api/documents/save` | Save document |
| GET | `/api/documents/{id}/export` | Export document (PDF/DOCX) |
| POST | `/api/documents/{id}/status` | Update document status |
| POST | `/api/documents/status` | Batch status update |

### File Management

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/files` | List uploaded files |
| POST | `/api/files/upload` | Upload file |
| GET | `/api/files/{id}/content` | Get file content |
| GET | `/api/files/{id}/metadata` | Get file metadata |
| DELETE | `/api/files/{id}` | Delete file |
| POST | `/api/files/{id}/process` | Process uploaded file |

### AI & Assistant

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/ai/complete` | AI text completion |
| POST | `/api/assistant/feedback` | Submit feedback (rate limited) |
| POST | `/api/assistant/edit` | Request AI edit |
| POST | `/api/assistant/abuse` | Report abuse |
| GET | `/api/rag/test` | Test RAG system |

### Clauses & Clipboard

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/clauses` | List saved clauses |
| POST | `/api/clauses` | Save new clause |
| GET | `/api/clipboard` | List clipboard items |
| POST | `/api/clipboard` | Save to clipboard |

### Dashboard

| Method | Path | Description |
|--------|------|-------------|
| GET | `/internal/dashboard-summary/{user_id}` | Get user dashboard data |

## Data Persistence & Backup

### Persistent Data Locations

**Docker Volumes:**
- `postgres_data` - PostgreSQL database files
- `redis_data` - Redis AOF and RDB files

**Bind Mounts (Host → Container):**
- `/root/models` → `/app/models` - AI model files (~4GB)
- `/root/legal-corpus` → `/app/legal-corpus` - Legal documents for RAG
- `/root/data` → `/app/data` - User uploads, generated documents

### Backup Strategy

**Database Backup:**
```bash
# Create backup
docker exec anwalts_postgres pg_dump -U anwalts_user -Fc anwalts_ai > backup_$(date +%Y%m%d).dump

# Restore from backup
docker exec -i anwalts_postgres pg_restore -U anwalts_user -d anwalts_ai < backup_20241016.dump
```

**Application Data Backup:**
```bash
# Backup models, legal corpus, and user data
tar -czf data_backup_$(date +%Y%m%d).tar.gz /root/models /root/legal-corpus /root/data
```

**Redis Backup:**
```bash
# Trigger save
docker exec anwalts_redis redis-cli BGSAVE

# Copy RDB file
docker cp anwalts_redis:/data/dump.rdb redis_backup_$(date +%Y%m%d).rdb
```

**Full System Backup:**
```bash
# Stop services
docker-compose down

# Backup volumes
docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
docker run --rm -v redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis_backup.tar.gz /data

# Restart services
docker-compose up -d
```

### Disaster Recovery

1. **Restore from backup files**
2. **Recreate Docker volumes** if necessary
3. **Restore database** using pg_restore
4. **Restore application data** from tar archives
5. **Verify environment variables** in `.env`
6. **Start services** with `docker-compose up -d`
7. **Run health checks** on all services
