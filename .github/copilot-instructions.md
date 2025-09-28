# Copilot Instructions for ZgrWise

## Project Overview
ZgrWise is a multi-component knowledge management system for collecting, organizing, searching, and reviewing highlights from diverse sources (web, PDF, YouTube, RSS, newsletters, Kindle). It uses FastAPI (Python) for backend, Next.js (TypeScript) for frontend, and integrates AI (Gemini API) for summarization/tagging and vector search.

## Architecture & Key Components
- **Backend** (`apps/api/`): FastAPI app, SQLAlchemy models, Alembic migrations, routes in `app/routes/`, models in `app/models.py`.
- **Worker** (`apps/worker/`): Python RQ background tasks, embedding, RSS, PDF, and other processing. Tasks in `worker/tasks/`.
- **Frontend** (`apps/web/`): Next.js 14 (App Router), TypeScript, Tailwind CSS, React Query. Pages in `app/`, shared UI in `components/`.
- **Extensions**: Chrome MV3 web clipper (`apps/extension/`), Obsidian sync plugin (`apps/obsidian-plugin/`).
- **Shared Schemas**: Common types in `packages/shared/`.
- **Database**: PostgreSQL 16 + pgvector, migrations via Alembic, initialization SQL in `tools/db/init/`.
- **Service Orchestration**: Docker Compose (`docker-compose.yml`), Makefile for dev commands.

## Developer Workflows
- **Start/Stop Services**: `make up` / `make down` (or `docker compose up -d`)
- **Run Migrations**: `make migrate` or `docker compose exec api alembic upgrade head`
- **View Logs**: `make logs`, `make api-logs`, `make worker-logs`, `make web-logs`
- **Health Check**: `make health`
- **Clean Up**: `make clean`
- **Access DB**: `docker compose exec db psql -U zgr -d zgrwise`

## Patterns & Conventions
- **API Security**: All endpoints require `X-API-Key` header (see `.env`)
- **Environment Variables**: Copy `env.example` to `.env` and configure keys (Gemini, DB, Redis, etc.)
- **Routes**: Add new API endpoints in `apps/api/app/routes/`
- **Tasks**: Add background jobs in `apps/worker/worker/tasks/`
- **Models**: Update `apps/api/app/models.py` and run migrations for DB changes
- **Frontend**: Add new pages in `apps/web/app/`, use React Query for API calls
- **Obsidian Export**: Path configured via `OBSIDIAN_EXPORT_PATH` in `.env`
- **AI Integration**: Gemini API key required, model set via `AI_MODEL` in `.env`
- **Embeddings**: Model and dimension set via `EMB_MODEL` and `EMB_DIM` in `.env`

## Integration Points
- **Chrome Extension**: Communicates with API, configured in extension options
- **Obsidian Plugin**: Pulls highlights via API, configured in plugin settings
- **RSS**: Feeds managed via web UI or API (`/api/rss/feeds`)
- **Background Tasks**: Worker processes heavy/async jobs (embeddings, RSS, PDF)

## External Dependencies
- **Gemini API**: For AI summarization/tagging
- **pgvector**: For vector search in PostgreSQL
- **Redis**: For caching and worker queue

## Examples
- Add a new API route: `apps/api/app/routes/your_route.py`
- Add a background task: `apps/worker/worker/tasks/your_task.py`
- Add a frontend page: `apps/web/app/your_page/`

## Troubleshooting
- Check logs with `make logs`
- Verify `.env` configuration for keys and endpoints
- Use health checks (`make health`) to confirm service status

---
For more details, see the README.md and comments in key files. If anything is unclear, ask for clarification or review the Makefile for supported commands.
