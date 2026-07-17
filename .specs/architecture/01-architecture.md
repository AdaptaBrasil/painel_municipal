# System Architecture

## Principle

The backend follows **Clean Architecture**: dependencies always point inward (Infrastructure → Application → Domain). The domain knows nothing about FastAPI, SQL or Playwright.

```
backend/src/
├── domain/           # Domain Layer (no framework dependencies)
│   ├── entities.py       # Pydantic entities + formatting rules (CommonBusinessRules)
│   └── interfaces.py     # Abstract contracts (ABC) for repositories and services
├── application/      # Application Layer
│   ├── router.py         # FastAPI endpoints (orchestrated use cases)
│   └── dependencies.py   # Dependency injection (Depends)
├── infrastructure/   # Infrastructure Layer (concrete implementations)
│   ├── database.py           # PostgresDatabase (asyncpg)
│   ├── repository.py         # SQL repositories per aggregate
│   ├── pdf_service.py        # PlaywrightPdfService (render + merge)
│   ├── image_service.py      # Image download as data URI
│   └── project_info_service.py  # Project metadata (pyproject.toml)
├── core/             # Global configuration
│   ├── config.py         # Settings (pydantic-settings, .env) + page registry
│   └── constants.py      # Enums: PdfEngineType, ErrorKeys
├── helpers/          # Pure utilities
│   └── common/formatting/number_formatting_processing.py
├── static/report/    # Report page templates (paginaN/)
└── main.py           # FastAPI bootstrap: CORS, rate limiting, routes
```

## Dependency rules

1. `domain/` **must not import** from `application/`, `infrastructure/` or FastAPI. It may use Pydantic, pandas and `helpers/`.
2. `application/` depends only on `domain/` (interfaces + entities) and `core/`. Concrete implementations are chosen **exclusively** in `application/dependencies.py`.
3. `infrastructure/` implements the interfaces from `domain/interfaces.py`. Every new external integration (database, browser, HTTP) goes here.
4. `core/config.py` is the **single source of truth** for configuration: `.env` variables, PDF engine, template directories, page dimensions (`pages_dir`) and the page→records map (`page_context_records`).

## Domain interfaces (contracts)

| Interface | Method(s) | Implementation |
|---|---|---|
| `DatabaseInterface` | `fetch_all(query, *args)`, `test_connection()` | `PostgresDatabase` |
| `CountyRepositoryInterface` | `get_counties()`, `get_county(id)` | `CountyRepository` |
| `RiskFactorRepositoryInterface` | `get_risk_factors_by_county_id(id)` | `RiskFactorRepository` |
| `MunicipalIndicatorsRepositoryInterface` | `get_municipal_report(id)` | `MunicipalIndicatorsRepository` |
| `MunicipalResilienceProfileRepositoryInterface` | `get_municipal_resilience_profile(id)` | `MunicipalResilienceProfileRepository` |
| `ClimateProjectionRepositoryInterface` | `get_climate_projection(id)` | `ClimateProjectionRepository` |
| `MunicipalHealthRepositoryInterface` | `get_municipal_health(id)` | `MunicipalHealthRepository` |
| `PdfServiceInterface` | `generate_single_page_pdf`, `generate_pdf_merged`, `generate_pdf_page` | `PlaywrightPdfService` |
| `ProjectInfoServiceInterface` | `get_project_info()` | `ProjectInfoService` |
| `ImageServiceInterface` | `fetch_as_data_uri(url)` | `ImageService` |

## Cross-cutting patterns

- **Rate limiting**: SlowAPI, keyed by remote IP (`get_remote_address`), `200/minute` limit on PDF endpoints. Excess returns HTTP 429.
- **CORS**: only origins listed in `main.py` (`ALLOWED_ORIGINS`), methods `GET` and `OPTIONS`.
- **Errors**: standardized keys in the `ErrorKeys` enum (`core/constants.py`), `ERR_*` format. Endpoints translate missing data into HTTP 404 with the matching key and internal failures into HTTP 500.
- **Number formatting**: centralized in `CommonBusinessRules` (`domain/entities.py`) — see [`../business-rules/01-number-formatting.md`](../business-rules/01-number-formatting.md).

## Requirements for new features

When adding a new piece of data to the report:

1. Create/extend the **entity** and its **Report wrapper** (with `formatted_data_dict`) in `domain/entities.py`.
2. Declare the repository **interface** in `domain/interfaces.py` and implement it in `infrastructure/repository.py` (query against the `painel_municipal` schema).
3. Register the provider in `application/dependencies.py` and inject it into the endpoint in `application/router.py`.
4. Update `page_context_records` in `core/config.py` if the data feeds a specific page.
5. Consume the record in the page's Jinja2 template (`static/report/paginaN/`).
