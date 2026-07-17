# Infrastructure and Deployment

## Topology (Docker Compose)

| Service | Container | Image/Build | Port (host → container) |
|---|---|---|---|
| `db` | `painel_db` | `postgres:15-alpine` | `127.0.0.1:${DATABASE_SECRET_PORT}` → 5432 |
| `backend` | `painel_backend` | `backend/Dockerfile` (arg `PDF_ENGINE`) | `${BACKEND_SECRET_PORT}` → 8000 |
| `frontend` | `painel_frontend` | `frontend/Dockerfile` (Nginx) | `${FRONTEND_SECRET_PORT}` → 80 |

Rules:

1. The PostgreSQL port is **always** bound to `127.0.0.1` on the host — the database is never exposed to the internet.
2. The backend runs `uvicorn src.main:app --reload` with the code mounted as a volume (hot reload in development).
3. Database data persists in the named volume `postgres_data`.
4. Ports are parameterized by `*_SECRET_PORT` variables in `.env` (defaults from `.env.example`: frontend 8000, backend 3000, db 5533).

## Environment variables (`.env`, see `.env.example`)

| Variable | Use |
|---|---|
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_USE_SSL` | asyncpg connection (read by `Settings` via pydantic-settings) |
| `PDF_ENGINE` | PDF engine (`playwright` — the only enabled value) |
| `FRONTEND_SECRET_PORT`, `BACKEND_SECRET_PORT`, `DATABASE_SECRET_PORT` | Host port mapping |

The `.env` file lives at the **repository root** (the backend reads it via `BACKEND_DIR.parent / ".env"`). Never commit it; `.env.example` is the contract.

## Operational commands (Makefile)

- `make run` — brings everything up with rebuild (`docker compose up --build -d`)
- `make start` / `make stop` / `make restart`
- `make logs`, `make logs-backend`, `make logs-frontend`
- `make shell-backend` / `make shell-frontend` / `make shell-db`

## Deployment

- Current production: AWS (IP in `ALLOWED_ORIGINS` in `main.py`, frontend on port 5530).
- `deploy.sh` runs the deployment flow; `erase_docker.sh` cleans up the local Docker environment.
- CI/CD: `.github/workflows/deploy.yml`.
- **CORS**: new production origins must be added explicitly to `ALLOWED_ORIGINS` (`backend/src/main.py`).

## Batch scripts (`scripts/`)

| Script | Function |
|---|---|
| `download_report.sh` | Downloads the full report for one municipality |
| `download_reports_range.sh` / `download_reports_parallel.sh` | Downloads a range of `county_id`s / in parallel |
| `download_reports_by_page*.sh` | Downloads individual pages (with a missing-fix variant) |
| `merge_pages_range.sh` | Merges pages downloaded in isolation |
| `verificar_nao_baixados.py` / `verifica_porcentagem.py` | Download completeness audit (uses `tabela_completa.csv`) |

Requirement: scripts depend only on the public API (`/api/v1/...`) — they never access the database directly.

## Versioning

- Backend version in `backend/pyproject.toml` (`version`), exposed on `/health`. Increment on each release (current pattern: patch bump within `0.1.X`).
- Commits: messages **in English** with semantic tags (`feat:`, `fix:`, `style:`, `chore:` …).
