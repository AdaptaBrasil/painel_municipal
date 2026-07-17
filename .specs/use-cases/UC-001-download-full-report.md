# UC-001 — Download Full PDF Report

## Description
The user obtains the complete municipal report card (pages 0–8 merged) for a municipality as a single PDF file.

## Actors
- **Primary**: End user (via frontend) or batch script (`scripts/download_reports_*.sh`).
- **System**: FastAPI backend, PostgreSQL, Playwright/Chromium.

## Preconditions
- Municipality exists in the `painel_municipal.adapta_data` table.
- All data tables have a record for the requested `county_id`.
- Backend has Chromium installed (the Docker image provisions it).

## Trigger
`GET /api/v1/reports/pdf/{county_id}` (in the frontend: clicking "Download" after selecting the municipality).

## Main flow
1. System validates the rate limit (200/min per IP).
2. System fetches, in sequence: county, risk factors, municipal indicators, resilience profile, climate projection and municipal health.
3. System applies the Brazilian formatting rules to each dataset (`*Report` wrappers).
4. System builds the single context and calls `generate_pdf_merged`:
   - HTML pages are rendered via Jinja2 + Playwright;
   - static pages (`file.pdf`) are appended with normalized scaling;
   - everything is merged in the order of `settings.pages_dir`.
5. System responds `200` with `application/pdf` and `Content-Disposition: attachment; filename="{geocode}.pdf"`.

## Alternative flows / exceptions
- **A1 — Missing data**: any empty dataset → `404` with the matching `ERR_*_NOT_FOUND` key; no PDF is generated.
- **A2 — Rendering failure** (missing template, Chromium error, missing static PDF): `500` with the exception detail.
- **A3 — Rate limit exceeded**: `429` (SlowAPI default handler).
- **A4 — Geocode unavailable**: file name falls back to `county_{county_id}.pdf`.

## Postconditions
- No persisted state; generation is stateless (temp files are removed).

## Non-functional requirements
- Pages rendered at high resolution (`device_scale_factor=3`).
- The endpoint must remain stateless to allow parallelization by batch scripts.

## References
- `backend/src/application/router.py` (`download_report_pdf`)
- [`../architecture/03-pdf-generation.md`](../architecture/03-pdf-generation.md)
