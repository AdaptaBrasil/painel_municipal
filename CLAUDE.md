# Fichas Municipais — AdaptaBrasil (INPE)

Generates municipal PDF report cards with socioclimatic indicators. Full specifications in `.specs/`.

## Stack
- Backend: Python 3.12+, FastAPI, asyncpg (PostgreSQL, schema `painel_municipal`), Jinja2, Playwright, pypdf, Poetry.
- Frontend: HTML/CSS/Vanilla JS served by Nginx. Orchestration: Docker Compose (`make run`, `make logs-backend`).

## Architecture (Clean Architecture — `backend/src/`)
- `domain/` (entities + interfaces, framework-free) ← `application/` (router + DI) ← `infrastructure/` (DB, PDF).
- Config centralized in `core/config.py` (`.env` at repo root); standardized errors in `core/constants.py` (`ERR_*`).
- Report templates in `static/report/paginaN/` (842×595 px; page order in `settings.pages_dir`).

## Conventions
- All source code and documentation in **English**; user-facing texts and UI/UX content (frontend + PDF report) in Brazilian Portuguese.
- Commits: English, with semantic tags (`feat:`, `fix:`, `style:`, `docs:`, `chore:`).
- pt-BR number formatting only in the domain (`CommonBusinessRules`); missing value = `"—"`. Never format in JS/Jinja2.
- API versioned at `/api/v1` — no breaking changes.
- Detailed rules in `.claude/rules/`; backend version in `backend/pyproject.toml` (bump each release).
