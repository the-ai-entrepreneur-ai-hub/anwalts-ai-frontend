End-to-End CI/CD and Local AI Setup (Free + Open Source)

Overview
- Push to main/master builds Nuxt, deploys via SSH to your server, and reloads with PM2.
- All free/open-source tooling (GitHub Actions, rsync/scp over SSH, PM2).
- Optional local AI stack using LocalAI (OpenAI API compatible) and Qdrant for code search.

Server Prerequisites
- A Linux VPS you control, with Node.js 20+ installed and SSH access.
- Reverse proxy (Nginx/Caddy) pointing your domain to port 3000 on the host.
- Create an app directory (example): /var/www/anwalts-frontend

GitHub Secrets (required)
- SSH_HOST: your.server.com
- SSH_USER: deploy or your user
- SSH_KEY: private key contents for the deploy user
- APP_DIR: e.g. /var/www/anwalts-frontend
- Optional: SSH_PORT (default 22), APP_NAME (default anwalts-frontend)
- Optional: BACKEND_BASE (e.g. https://api.yourdomain.com) – injected into .env

What the Pipeline Does
1) CI (build only): .github/workflows/ci.yml builds Nuxt on PRs and pushes.
2) Deploy: .github/workflows/deploy.yml
   - Builds Nuxt (.output)
   - Uploads artifact via SCP to /tmp on the server
   - Extracts into APP_DIR/releases/<timestamp>
   - Installs production deps (shared node_modules cache)
   - Atomically switches APP_DIR/current symlink
   - Starts/reloads via PM2 and prunes old releases

Rollback
- SSH to server: ln -sfn APP_DIR/releases/<older_ts> APP_DIR/current && pm2 reload anwalts-frontend

Local AI (Optional)
- Docker compose in ai/docker-compose.yml runs:
  - LocalAI (OpenAI-compatible endpoint at http://localhost:8080/v1)
  - Qdrant (vector DB at http://localhost:6333)
- Models config at ai/models.yaml: pulls a code LLM (Qwen2.5-Coder 7B Instruct) on first run.

Run Local AI
- cd anwalts-frontend-new/ai
- docker compose up -d
- Set in Codex CLI or tools:
  - OPENAI_BASE_URL=http://localhost:8080/v1
  - OPENAI_API_KEY=sk-local (any non-empty value)
  - Model name: abdel-coder

Code Indexing (Optional)
- Minimal Python utilities in tools/code-index to index/query your repo into Qdrant.
- Install: python3 -m venv .venv && source .venv/bin/activate && pip install -r tools/code-index/requirements.txt
- Index: python tools/code-index/index_code.py --root . --qdrant http://localhost:6333 --collection code-context
- Query: python tools/code-index/query_code.py --qdrant http://localhost:6333 --collection code-context --q "how do we handle google oauth?"

Notes
- Everything is open-source and free to run. LocalAI downloads models on first start.
- You can swap the model in ai/models.yaml for a larger/smaller variant.
- To trigger production deploys, push to main/master.

