# Fichas Municipais - AdaptaBrasil

**Fichas Municipais** is a web application built on **Clean Architecture** principles that generates municipal PDF report cards with socioclimatic indicators, supporting decision-making on public policies and climate resilience.

## 📋 Table of Contents
- [Fichas Municipais - AdaptaBrasil](#fichas-municipais---adaptabrasil)
  - [📋 Table of Contents](#-table-of-contents)
  - [✨ Features](#-features)
  - [🏗 Project Architecture](#-project-architecture)
  - [🛠 Technologies Used](#-technologies-used)
  - [🚀 Quick Start (Docker - Recommended)](#-quick-start-docker---recommended)
  - [💻 Running the Application](#-running-the-application)
    - [Docker Commands (Makefile)](#docker-commands-makefile)
    - [Running Locally Without Docker](#running-locally-without-docker)
  - [🌐 API Overview](#-api-overview)
  - [📂 Directory Structure](#-directory-structure)
  - [📄 PDF Generation Architecture](#-pdf-generation-architecture)
  - [📚 Project Documentation (.specs and .claude)](#-project-documentation-specs-and-claude)
  - [🤝 Contributing](#-contributing)
  - [📋 Roadmap](#-roadmap)
  - [📄 License](#-license)
  - [👥 Authors](#-authors)
  - [🔗 Useful Links](#-useful-links)

## ✨ Features
- **Municipal report generation (PDF)**: multi-page report (cover + indicators + static institutional pages) rendered per page and merged into a single file.
- **Single-page export**: any report page can be generated individually (`/reports/pdf/{page_name}/{county_id}/`) for debugging and batch workflows.
- **Fast RESTful API**: FastAPI + PostgreSQL (asyncpg), with per-IP rate limiting (SlowAPI) and restricted CORS.
- **Brazilian number formatting**: all values are formatted in the domain layer (pt-BR conventions, truncation, `—` for missing data).
- **Clean Architecture**: clear separation between Domain, Application, Infrastructure and Core layers.

## 🏗 Project Architecture
- **Backend (Python)** — Clean Architecture (`backend/src/`):
  - **Domain**: Pydantic entities, business/formatting rules and repository interfaces (no framework dependencies)
  - **Application**: FastAPI routers and dependency injection
  - **Infrastructure**: PostgreSQL access (asyncpg), PDF rendering (Playwright) and merging (pypdf)
  - **Core**: Pydantic settings (`.env`), report page registry and error constants (`ERR_*`)
- **Frontend (HTML/CSS/Vanilla JS)**: static page served by Nginx — selects a municipality and downloads its report.

Full specifications live in [`.specs/`](.specs/README.md).

## 🛠 Technologies Used
- **Language**: Python 3.12+ 🐍 (Poetry)
- **API**: FastAPI + Uvicorn
- **Database**: PostgreSQL 15 (asyncpg, schema `painel_municipal`)
- **PDF**: Jinja2 templates + Playwright (Chromium) + pypdf merge
- **Frontend**: HTML5, CSS3, Vanilla JavaScript ⚡️ (Nginx)
- **Infra**: Docker & Docker Compose, Makefile, GitHub Actions

## 🚀 Quick Start (Docker - Recommended)

```bash
git clone https://github.com/AdaptaBrasil/painel_municipal.git
cd painel_municipal
cp .env.example .env   # then edit database credentials and ports
make run
```

`.env` (see `.env.example` for defaults):
```dotenv
PDF_ENGINE=playwright

DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=adaptabrasil
DB_USER=your_db_user
DB_PASSWORD=your_secure_password
DB_USE_SSL=False

FRONTEND_SECRET_PORT=8000
BACKEND_SECRET_PORT=3000
DATABASE_SECRET_PORT=5533
```

With the default ports, the application is available at:
- **Frontend**: `http://localhost:8000`
- **Backend API**: `http://localhost:3000`
- **API Documentation (Swagger UI)**: `http://localhost:3000/docs`

## 💻 Running the Application

### Docker Commands (Makefile)

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make build` | Build Docker images without starting containers |
| `make run` | Build and start all containers in the background (full stack) |
| `make start` / `make stop` / `make restart` | Manage containers without rebuilding |
| `make logs` / `make logs-backend` / `make logs-frontend` | Stream container logs |
| `make ps` | List running containers |
| `make shell-backend` / `make shell-frontend` / `make shell-db` | Open a shell inside a container |

### Running Locally Without Docker

Requires Python 3.12+, Poetry, PostgreSQL 15+ and Chromium (installed by Playwright).

```bash
# Backend
cd backend
poetry env use 3.12
poetry install
poetry run playwright install chromium
uvicorn src.main:app --reload --port 3000

# Frontend (new terminal, from the project root)
python -m http.server 8080 -d frontend
```

The frontend resolves the API URL automatically: on `localhost` it targets `http://localhost:3000/api/v1` (override with `window.APP_CONFIG.API_BASE_URL` if needed).

## 🌐 API Overview

Base path `/api/v1` — full contract in [`.specs/api/01-rest-api.md`](.specs/api/01-rest-api.md):

| Endpoint | Description |
|---|---|
| `GET /health` | Service, project and database status |
| `GET /counties` | List of available municipalities |
| `GET /reports/pdf/{county_id}` | Full merged report (downloads as `{geocode}.pdf`) |
| `GET /reports/pdf/{page_name}/{county_id}/` | Single report page (`pagina0`…`pagina8`) |

## 📂 Directory Structure

```text
painel_municipal/
├── .specs/                       # Technical specifications (architecture, API, business rules, use cases)
├── .claude/                      # Claude Code configuration (rules, commands, agents, skills)
├── CLAUDE.md                     # Project manual for AI-assisted development
├── .env.example                  # Template for environment configuration
├── docker-compose.yml            # Docker Compose for db, backend and frontend
├── Makefile                      # Docker operation shortcuts
├── deploy.sh                     # Deployment script
├── backend/                      # FastAPI Backend (Clean Architecture)
│   ├── Dockerfile
│   ├── pyproject.toml            # Dependencies and project version (Poetry)
│   ├── src/
│   │   ├── main.py               # App entry point (CORS, rate limiting, routes)
│   │   ├── application/          # Routers and dependency injection
│   │   ├── core/                 # Settings (.env), page registry, error constants
│   │   ├── domain/               # Entities, formatting rules and interfaces
│   │   ├── infrastructure/       # Database, repositories, PDF/image/project-info services
│   │   ├── helpers/              # Pure utilities (number formatting)
│   │   └── static/report/        # Report page templates
│   │       ├── pagina0/          # Cover (index.html, styles.css, data.js, imgs/)
│   │       ├── pagina1/          # Static institutional page (file.pdf)
│   │       ├── pagina2..pagina6/ # Data-driven pages (risks, indicators, resilience, climate, health)
│   │       ├── pagina7..pagina8/ # Static institutional pages (file.pdf)
│   │       └── shared/           # Shared fonts, images and JS
│   └── tests/                    # Test suite (pytest)
├── frontend/                     # Static Frontend (Vanilla JS + Nginx)
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js                 # Municipality selector + PDF download
├── scripts/                      # Batch download/merge/audit scripts for reports
└── local_data/                   # Staging area for Penpot design exports (not deployed)
```

## 📄 PDF Generation Architecture

The report uses a **multi-page merge strategy** (details in [`.specs/architecture/03-pdf-generation.md`](.specs/architecture/03-pdf-generation.md)):

1. **Page registry**: each page is declared in `backend/src/core/config.py` (`pages_dir`) with its own print configuration; the declaration order is the final PDF order.
2. **Isolated rendering**: HTML pages (842×595 px) are rendered with Jinja2 and printed by Playwright/Chromium; static pages (`file.pdf`) are appended as-is, rescaled to the standard size.
3. **Per-page data fetching**: `page_context_records` maps each page to the database records its template actually uses, so single-page requests only query what is needed.
4. **In-memory merge**: all pages are merged with pypdf and returned as a single download named `{geocode}.pdf`.

## 📚 Project Documentation (.specs and .claude)

- **[`.specs/`](.specs/README.md)** — the source of truth for requirements: system architecture, data model, REST API contract, business rules (Brazilian number formatting, report page rules) and use cases (UC-001…UC-004). New features should start from these documents and keep them updated.
- **[`.claude/`](.claude/)** — Claude Code configuration for AI-assisted development: modular guidelines in `rules/` (code style, git workflow, testing, security), custom slash commands in `commands/` (`/generate-pdf`, `/review-changes`, `/release`, `/new-page`), specialized subagents in `agents/` and reusable skills in `skills/`. [`CLAUDE.md`](CLAUDE.md) is the concise project manual loaded in every session.

## 🤝 Contributing

1. **Fork** and clone the repository, create a feature branch (`git checkout -b feature/your-feature-name`).
2. **Implement** your changes following the project guidelines:
   - Source code (identifiers, comments, docstrings, logs) written in **English**; UI/report texts in Brazilian Portuguese.
   - Python: PEP 8, type hints, Clean Architecture boundaries (see `.claude/rules/code-style.md`).
   - Frontend: Vanilla JavaScript only, no frameworks or CDN dependencies.
   - Keep `.specs/` in sync with behavior changes.
3. **Commit** in English using semantic tags (`feat:`, `fix:`, `style:`, `docs:`, `chore:`…).
4. **Push** and open a Pull Request.

## 📋 Roadmap

### Version 0.1.X (Current)
- [x] Backend API with FastAPI and PostgreSQL
- [x] Static Frontend with Vanilla JS/HTML/CSS
- [x] Multi-page PDF export with merge functionality (Playwright)
- [x] Clean Architecture backend structure
- [x] Docker containerization
- [x] Technical specifications (`.specs/`) and AI-assisted development setup (`.claude/`)
- [x] CI/CD Pipeline (GitHub Actions)
- [ ] Unit and Integration Tests suite
- [ ] Security audit and hardening

### Version 0.2.X (Planned)
- [ ] Additional PDF engines (Puppeteer, WeasyPrint, WkHtmlToPdf)
- [ ] Advanced data filtering and analytics
- [ ] Enhanced PDF export templates
- [ ] User authentication and authorization
- [ ] Audit logging

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Pedro Andrade** - *Coordinator* - [Email](mailto:pedro.andrade@inpe.br) | [GitHub](https://github.com/pedro-andrade-inpe)
- **Mário de Araújo Carvalho** - *Contributor & Developer* - [GitHub](https://github.com/MarioCarvalhoBr)
- **Mauro Assis** - *Contributor* - [GitHub](https://github.com/assismauro)
- **Miguel Gastelumendi** - *Contributor* - [GitHub](https://github.com/miguelGastelumendi)

## 🔗 Useful Links

- **Organization**: [AdaptaBrasil GitHub](https://github.com/AdaptaBrasil/)
- **Repository**: [painel_municipal](https://github.com/AdaptaBrasil/painel_municipal)
- **Issues & Bug Reports**: [Issue Tracker](https://github.com/AdaptaBrasil/painel_municipal/issues)
- **API Reference**: `http://localhost:3000/docs` (Swagger UI) when running

---

**Developed with ❤️ by the AdaptaBrasil team**
