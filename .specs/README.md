# .specs — Fichas Municipais Technical Specifications

Central repository of technical specifications and requirements for the **Fichas Municipais — AdaptaBrasil (INPE)** project.
This folder documents use cases, business rules and detailed technical definitions to guide the development of new features.

## Structure

| Folder / File | Content |
|---|---|
| [`00-overview.md`](00-overview.md) | Project overview, goals and scope |
| [`architecture/`](architecture/) | System architecture (Clean Architecture, data model, PDF pipeline) |
| [`api/`](api/) | REST endpoint specification |
| [`business-rules/`](business-rules/) | Business rules (Brazilian number formatting, report page rules) |
| [`use-cases/`](use-cases/) | Detailed use cases (UC-XXX) |
| [`frontend/`](frontend/) | Static frontend specification |
| [`infrastructure/`](infrastructure/) | Deployment, Docker, environment variables and operational scripts |
| [`templates/`](templates/) | Templates for writing new specifications |

## Conventions

- **Use cases** follow the `UC-NNN-short-name.md` numbering and the template in [`templates/use-case-template.md`](templates/use-case-template.md).
- **New specifications** must start from [`templates/spec-template.md`](templates/spec-template.md).
- Specifications describe the **intended behavior**; when the code diverges from a spec, treat the divergence as a bug or update the spec explicitly (in a dedicated commit).
- Code references use paths relative to the repository root (e.g. `backend/src/application/router.py`).

## Project state (reference)

- Current backend version: **0.1.7** (`backend/pyproject.toml`)
- Stack: FastAPI + PostgreSQL (asyncpg) + Jinja2 + Playwright + pypdf; Vanilla JS frontend served by Nginx; orchestrated with Docker Compose.
