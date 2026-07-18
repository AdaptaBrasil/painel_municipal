# REST API Specification

Base path: **`/api/v1`** — defined in `backend/src/application/router.py`.
All endpoints are `GET`. CORS restricted to the origins configured in `main.py`; allowed verbs: `GET`, `OPTIONS`.

## GET /api/v1/health

Service diagnostics.

**Response 200** (example):
```json
{
  "backend": {"status": "ok", "message": "Service is running"},
  "pdf_engine": "playwright",
  "pages_dir": ["..."],
  "project": {"name": "backend", "version": "0.1.7", "description": "Fichas Municipais Backend API"},
  "database_status": "connected"
}
```

Rules:
- A failure to read `pyproject.toml` or to test the database **does not** bring the endpoint down; the corresponding field is omitted or marked `disconnected`.

## GET /api/v1/counties

Lists all available municipalities.

**Response 200**: `List[County]`
```json
[{"county_id": 1, "geocode": 3305158, "county": "São José do Vale do Rio Preto", "state": "RJ", "region": "Sudeste", "display": "São José do Vale do Rio Preto - RJ"}]
```

Rules:
- Ordered by `display` (alphabetical).
- Query errors → HTTP 500 with `ERR_DATA_RETRIEVAL_FAILED`.

## GET /api/v1/reports/pdf/{county_id}

Generates the **full report** (all pages merged).

- **Rate limit**: 200 requests/minute per IP (HTTP 429 when exceeded).
- **Parameter**: `county_id` (int).
- **Response 200**: `application/pdf`, header `Content-Disposition: attachment; filename="{geocode}.pdf"` — the file name is the **IBGE geocode** taken from the climate projection (fallback: `county_{county_id}.pdf`).
- **Errors**:
  - 404 with a specific key when any required dataset is missing: `ERR_COUNTY_NOT_FOUND`, `ERR_RISK_FACTOR_NOT_FOUND`, `ERR_MUNICIPAL_REPORT_NOT_FOUND`, `ERR_MUNICIPAL_RESILIENCE_PROFILE_NOT_FOUND`, `ERR_CLIMATE_PROJECTION_NOT_FOUND`, `ERR_MUNICIPAL_HEALTH_NOT_FOUND`.
  - 500 when PDF generation fails (`ERR_PDF_GENERATION_FAILED` in logs; `detail` carries the exception message).

## GET /api/v1/reports/pdf/{page_name}/{county_id}/

Generates the PDF of a **single report page**.

- **Rate limit**: 200 requests/minute per IP.
- **Parameters**: `page_name` (str — `pagina0`…`pagina8`), `county_id` (int, `gt=0`).
- **Validation**: `page_name` must exist in `settings.pages_dir` **and** in `settings.page_context_records`; otherwise 404 `ERR_PAGE_NOT_FOUND`.
- **Conditional data fetching**: queries only the repositories listed in `page_context_records[page_name]`. The climate projection is always queried (file name).
- **Response 200**: `application/pdf`, same `{geocode}.pdf` naming.
- **Errors**: 404 for missing data (same keys as the full endpoint) or unknown page; 500 on generation failure.

## Error conventions

- Error keys are stable and defined in `ErrorKeys` (`backend/src/core/constants.py`), `ERR_SNAKE_CASE` format. Clients must handle the key, not the message.
- Never expose stack traces to the client; detailed logs go to the backend stdout.

## Compatibility

- Contract changes require a new version prefix (`/api/v2`); the `/api/v1` prefix must not receive breaking changes.
