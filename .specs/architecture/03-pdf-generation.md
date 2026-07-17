# PDF Generation Pipeline

## Overview

The report is composed of independent pages defined in `settings.pages_dir` (`backend/src/core/config.py`). Each page is either:

- **HTML template** (`paginaN/index.html`) — rendered with Jinja2 and converted to PDF by Playwright (headless Chromium); or
- **Static PDF** (`paginaN/file.pdf`) — appended directly, scaled to the standard size.

The order of `pages_dir` entries **is the page order in the final PDF**.

## Page specification

Each `pages_dir` entry maps `template Path → print config`:

```python
{template_dir / "pagina0" / "index.html": {
    "width": "842px", "height": "595px",
    "print_background": True, "landscape": False,
    "margin": {"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"},
    # optional: "scale": 1.50 (used by pagina3)
}}
```

Requirements:

1. Standard page size: **842×595 px** (A4 landscape at 96 dpi). Conversion to PDF points: `px × 72 / 96` (`_page_size_in_points`).
2. `device_scale_factor=3` in Chromium for high rendering resolution.
3. `prefer_css_page_size=True` is applied by default.
4. Chromium is launched with `--disable-web-security --allow-file-access-from-files` to allow local assets (`file://`).

## Rendering flow (HTML page)

1. The context receives `base_url` = absolute URI of the page directory (to resolve `imgs/`, `styles.css`, `data.js`).
2. The template is rendered with Jinja2 (`FileSystemLoader` rooted at the page directory).
3. The resulting HTML is written to a temp file and opened via `file://` with `wait_until="networkidle"` (ensures fonts and images load before printing).
4. `page.pdf(**config)` produces the bytes; the temp file is removed in `finally`.

## Merge flow (`generate_pdf_merged`)

1. Iterates `pages_dir` in declared order.
2. `.pdf` page: validates existence, applies `scale_to` to the standard size and appends via pypdf.
3. `.html` page: generates the individual PDF and appends all of its pages.
4. Writes the consolidated result to memory (`io.BytesIO`) and returns the bytes.

## Single page (`generate_pdf_page`)

Finds the `pages_dir` entry whose parent directory is `page_name`; applies the same treatment (static × rendered). An unknown `page_name` raises `KeyError` → HTTP 404 (`ERR_PAGE_NOT_FOUND`).

## Per-page context optimization

`settings.page_context_records` declares which records each template actually uses. The single-page endpoint queries **only** the required repositories. Exception: **the climate projection is always queried**, because its `geocode` names the downloaded file (`{geocode}.pdf`).

| Page | Required records |
|---|---|
| pagina0 | `county_record` |
| pagina1 | — (static PDF) |
| pagina2 | `county_record`, `risks_record` |
| pagina3 | `county_record`, `municipal_report_record` |
| pagina4 | `county_record`, `municipal_resilience_profile_record` |
| pagina5 | `county_record`, `climate_projection_record` |
| pagina6 | `county_record`, `municipal_health_record` |
| pagina7 / pagina8 | — (static PDF) |

## Page directory structure

```
static/report/paginaN/
├── index.html   # Jinja2 template (or file.pdf for a static page)
├── styles.css   # CSS extracted from the design (Penpot), no local @font-face
├── data.js      # window.PAGE_DATA: design tokens and default texts
└── imgs/        # Page-local assets
```

Shared resources live in `static/report/shared/` (fonts in `shared/css/fonts.css`, common images, utility JS). Reference designs are exported from Penpot; the working copy sits in `local_data/src-atualizado/` before being integrated into the backend.

## Requirements for adding a new page

1. Create `static/report/paginaX/` with `index.html` (+ `styles.css`, `data.js`, `imgs/`) **or** `file.pdf`.
2. Register the page in the `Settings.PageName` enum and in `pages_dir` at the desired position.
3. Declare the records it uses in `page_context_records`.
4. If new data is needed, follow the flow described in [`01-architecture.md`](01-architecture.md#requirements-for-new-features).
