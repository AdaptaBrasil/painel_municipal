# UC-002 — Download a Single Report Page

## Description
Obtain the PDF of a single page of the municipal report card (e.g. only the cover or only the climate projections), without generating the whole report. Used for layout debugging, partial downloads and script-based composition (`scripts/download_reports_by_page*.sh`, `scripts/merge_pages_range.sh`).

## Actors
- **Primary**: Developer/designer validating a page; batch scripts.

## Preconditions
- `page_name` ∈ {`pagina0` … `pagina8`}, registered in `settings.pages_dir` **and** `settings.page_context_records`.
- The data required by the page exists for the `county_id`.

## Trigger
`GET /api/v1/reports/pdf/{page_name}/{county_id}/` (note: trailing slash required; `county_id > 0`).

## Main flow
1. System validates the rate limit (200/min per IP).
2. System validates `page_name` against the configured pages; invalid → `404 ERR_PAGE_NOT_FOUND`.
3. System queries **only** the repositories listed in `page_context_records[page_name]` (optimization: static pages query almost nothing).
4. The climate projection is **always** queried, to obtain the `geocode` that names the file.
5. System calls `generate_pdf_page(context, page_name)`:
   - static page → returns the rescaled `file.pdf`;
   - HTML page → renders only that template.
6. Response `200` with `application/pdf`, `filename="{geocode}.pdf"`.

## Alternative flows / exceptions
- **A1 — Unknown page** (validation or the service's `KeyError`): `404 ERR_PAGE_NOT_FOUND`.
- **A2 — Missing required data**: `404` with the missing dataset's `ERR_*_NOT_FOUND` key.
- **A3 — Rendering failure**: `500`.

## Business rules involved
- Page→records map: see [`../architecture/03-pdf-generation.md`](../architecture/03-pdf-generation.md#per-page-context-optimization).

## References
- `backend/src/application/router.py` (`download_report_page_pdf`)
- `backend/src/core/config.py` (`page_context_records`)
