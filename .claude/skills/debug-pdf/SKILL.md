---
name: debug-pdf
description: Diagnosis of PDF generation problems (blank page, broken layout, 500 error, missing image, wrong font). Use when a generated PDF comes out different from expected.
---

# PDF Generation Debugging

Pipeline: Jinja2 → temp HTML → Chromium (Playwright, `file://`, `networkidle`) → `page.pdf()` → pypdf merge. Details: `.specs/architecture/03-pdf-generation.md`.

## Diagnostic playbook

1. **Reproduce in isolation**: generate only the problematic page —
   `curl -s -o /tmp/p.pdf "http://localhost:3000/api/v1/reports/pdf/{page}/{county_id}/"` and inspect the body on error (`ERR_*` key).
2. **404 with `ERR_*_NOT_FOUND`**: data missing in the database for that `county_id` — confirm in the corresponding table (map in `.specs/architecture/02-data-model.md`).
3. **500 error**: check `make logs-backend`. Common causes: template referencing a variable missing from the context (check `page_context_records` in `core/config.py`), missing static `file.pdf`, Chromium not installed in the container.
4. **Page renders but the layout is broken**:
   - Missing image → wrong relative path (assets resolve via `base_url` = the page directory; use `./imgs/...`).
   - Wrong font → `shared/css/fonts.css` not referenced or an unwanted local `@font-face`.
   - Misplaced element → check geometry (842×595 viewport; horizontal center at 421px).
   - Clipped content → it overflowed the viewport; shrink the element, never enlarge the page.
5. **Quick visual debugging**: open the template in a browser with a fake context — render the Jinja2 manually or replace the variables with sample values — before regenerating the PDF.
6. **Merge with a wrong/missing page**: order and presence come from `settings.pages_dir`; check the entry and the suffix (`.html` × `.pdf`).

## What not to do

- Do not change the standard dimensions (842×595) to "fix" a page.
- Do not add value formatting in the template as a workaround — the fix belongs in the domain.
