AnwaltsAI Live Application Index (2025-10-06)

Scope
- Covers the live containers, code locations, and runtime wiring currently active on this host.
- Read-only index: no services restarted; only inspection and file listings were collected.

Where To Find The Collected Index
- Container + code snapshots: `/root/live-app-index/20251006-202704`
- Running containers list: `/root/live-app-index/20251006-202704/containers_running.tsv`
- Per-container details: `/root/live-app-index/20251006-202704/containers/<container-name>/`
- Host code snapshots: `/root/live-app-index/20251006-202704/host-code/`
- Supabase config snapshot: `/root/live-app-index/20251006-202704/supabase/config.toml`

High-Level Architecture
- Frontend (`anwalts_frontend`)
  - Nuxt 3 app, runs Node at port `3000`.
  - Uses server API routes to proxy auth and selected backend calls.
  - Source: `./anwalts-frontend-new` (built into image).
- Backend (`anwalts_backend`)
  - FastAPI (Uvicorn), primary API on port `8000` (+ 8010 exposed).
  - Uses Postgres (pgvector) and Redis. Handles auth, templates, files, document generation, notifications.
  - Entry module: `backend-main:app` (code in image; host source present).
- Data Stores
  - Postgres (`anwalts_postgres`): `pgvector/pgvector:pg15`, port `5432`, volume `postgres_data`.
  - Redis (`anwalts_redis`): `redis:7-alpine`, port `6379`, volume `redis_data`.
- Supabase (local stack for dev/ops)
  - Multiple `supabase_*_anwalts-frontend-new` containers active (Studio 54323, Kong 54321, DB 54322, etc.).
  - Project config: `anwalts-frontend-new/supabase/config.toml`.
- Nginx
  - Defined in compose, not currently running. Dev config under `./nginx`.

Container Inventory (live)
- See full TSV: `/root/live-app-index/20251006-202704/containers_running.tsv`
- Core:
  - `anwalts_frontend` (image `root-frontend`) → host `:3000`
  - `anwalts_backend` (image `root-backend`) → host `:8000`, `:8010`
  - `anwalts_postgres` (pgvector) → host `:5432`
  - `anwalts_redis` (redis:7-alpine) → host `:6379`
- Supabase local:
  - `supabase_kong_anwalts-frontend-new` → `:54321`
  - `supabase_studio_anwalts-frontend-new` → `:54323`
  - `supabase_db_anwalts-frontend-new` → `:54322`
  - Plus realtime, storage, auth, pg_meta, etc. (see TSV)

Ports and Public Paths
- Frontend: `http://<host>:3000`
- Backend: `http://<host>:8000`
- Postgres: `localhost:5432` (service DB for backend)
- Redis: `localhost:6379`
- Supabase:
  - Kong Gateway: `http://localhost:54321`
  - Studio: `http://localhost:54323`
  - Supabase DB: `localhost:54322`

Volumes and Binds
- Backend service (binds):
  - `/root/models` → `/app/models`
  - `/root/legal-corpus` → `/app/legal-corpus`
  - `/root/data` → `/app/data`
- Postgres volume: `/var/lib/docker/volumes/root_postgres_data/_data`
- Redis volume: `/var/lib/docker/volumes/root_redis_data/_data`

Entrypoints and WorkDirs
- Frontend: WorkDir `/app`, Entrypoint `docker-entrypoint.sh`, Cmd `node .output/server/index.mjs`
- Backend: WorkDir `/app`, Cmd `uvicorn backend-main:app --host 0.0.0.0 --port 8000`

Source Code Locations (host)
- Backend (Python/FastAPI):
  - Main: `/root/backend-main.py`
  - Support: `/root/auth_service.py`, `/root/ai_service.py`, `/root/cache_service.py`, `/root/database.py`, `/root/models.py`
  - Dependencies: `/root/requirements.txt`
  - Compose + Dockerfile: `/root/docker-compose.yml`, `/root/Dockerfile.backend`
- Frontend (Nuxt 3): `./anwalts-frontend-new`
  - Config: `nuxt.config.ts`, `package.json`, server API under `server/api/*`
  - Supabase project: `supabase/config.toml`

Backend API Surface (extracted)
- Extracted route list at: `/root/live-app-index/20251006-202704/host-code/backend_routes.txt`
- Examples (non-exhaustive):
  - Auth: `/auth/login`, `/auth/register`, `/auth/forgot-password`, `/auth/reset-password`, `/auth/logout`, `/auth/google/*`
  - User: `/api/user/profile`, `/api/user/settings`, `/api/tokens`, `/api/aliases`
  - Content: `/api/templates`, `/api/clauses`, `/api/clipboard`, `/api/files/*`, `/api/documents/*`
  - AI: `/api/ai/complete`, `/api/ai/generate-document`, `/api/rag/test`
  - Health: `/health`

Frontend → Backend Integration
- Nuxt server routes proxy to backend using `BACKEND_BASE` or `http://backend:8000`:
  - `server/api/auth/google/authorize.get.ts`
  - `server/api/auth/google/callback.get.ts`
- Client pages use `/api/*` routes that the Nuxt server proxies to the backend with cookies.

Secrets and Environment
- Service env vars for each container are saved to: `/root/live-app-index/20251006-202704/containers/<name>/env.list` (permissions can be restricted if needed).
- Do not paste these values externally; treat as sensitive.

Operational Notes
- Postgres uses pgvector (vector search) and init script at `./scripts/init-db.sql` mounted into the container.
- Redis configured with AOF, 512MB maxmemory, `allkeys-lru` policy.
- Nginx defined but not running; traffic currently served directly on `:3000` and `:8000`.
- Supabase local stack is active; project id `anwalts-frontend-new` with site_url `https://portal-anwalts.ai`.

Safe Change Workflow (recommended)
- Backend changes
  - Edit host source under `/root/*.py` as needed.
  - Rebuild only the backend service: `docker compose build backend && docker compose up -d backend`
  - Verify `/health` and key endpoints; review logs.
- Frontend changes
  - Edit under `./anwalts-frontend-new`.
  - Rebuild frontend: `docker compose build frontend && docker compose up -d frontend`
  - Validate Nuxt server routes and client flows.
- Database migrations
  - Use migrations via `scripts/init-db.sql` or dedicated migration tool; test on Supabase local DB if applicable.

Next Steps (if desired)
- Lock down env snapshot files with `chmod 600`.
- Add a minimal ARCHITECTURE.md to each repo with the key components and flows.
- Set up a staging compose profile to validate changes before touching the live services.

