# Overview — Folha Municipal (AdaptaBrasil)

## Purpose

**Folha Municipal** is a web application that generates **municipal PDF report cards** ("fichas municipais") with socioclimatic indicators for Brazilian municipalities, in the context of the AdaptaBrasil (INPE) project. Its goal is to support decision-making on climate adaptation public policies and municipal resilience.

## Functional scope

1. **Municipality listing** — the user selects a municipality from a list loaded from the database.
2. **Full PDF report generation** — multi-page report (pages 0 to 8), landscape A4-like format (842×595 px), merged into a single file.
3. **Single-page PDF generation** — any report page can be generated in isolation (used for debugging, partial downloads and batch scripts).
4. **Health check** — diagnostic endpoint with service status, PDF engine, configured pages and database connectivity.

## Out of scope (version 0.1.x)

- User authentication/authorization (the API is public, protected only by rate limiting and CORS).
- Data editing by users (the database is read-only for the application).
- Alternative PDF engines (WeasyPrint, WkHtmlToPdf, Puppeteer are anticipated in the `PdfEngineType` enum, but only Playwright is enabled).

## Components

| Component | Technology | Responsibility |
|---|---|---|
| Backend | Python 3.12+, FastAPI, asyncpg, Jinja2, Playwright, pypdf | REST API, data access, PDF rendering and merging |
| Frontend | HTML/CSS/Vanilla JS + Nginx | Municipality selection and PDF download trigger |
| Database | PostgreSQL 15 (schema `painel_municipal`) | Stores the consolidated municipal indicators |
| Scripts | Bash/Python (`scripts/`) | Batch report downloads, completeness checks, page merging |

## Report structure (pages)

| Page | Source | Content | Dynamic data |
|---|---|---|---|
| pagina0 | HTML template | Cover ("Fichas Municipais") | `county_record` |
| pagina1 | Static PDF | Institutional page (logos, methodology) | — |
| pagina2 | HTML template | Climate risk factors ("flor de risco") | `county_record`, `risks_record` |
| pagina3 | HTML template | Municipal indicators (territory, population, socioeconomics) | `county_record`, `municipal_report_record` |
| pagina4 | HTML template | Municipal resilience profile (plans, disasters) | `county_record`, `municipal_resilience_profile_record` |
| pagina5 | HTML template | Climate projections (observed/optimistic/pessimistic scenarios) | `county_record`, `climate_projection_record` |
| pagina6 | HTML template | Municipal health (epidemiological profile, vaccine coverage) | `county_record`, `municipal_health_record` |
| pagina7 | Static PDF | Institutional page | — |
| pagina8 | Static PDF | Institutional page | — |

## Related documents

- Architecture: [`architecture/01-architecture.md`](architecture/01-architecture.md)
- API: [`api/01-rest-api.md`](api/01-rest-api.md)
- Business rules: [`business-rules/`](business-rules/)
- Use cases: [`use-cases/`](use-cases/)
