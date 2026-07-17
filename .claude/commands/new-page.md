---
description: Guides the creation of a new PDF report page following the project pattern
argument-hint: <page-name> [content description]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(ls *)
---

Create the structure for a new report page: $ARGUMENTS

Follow the checklist from `.specs/architecture/03-pdf-generation.md`:

1. Create `backend/src/static/report/{name}/` with `index.html`, `styles.css`, `data.js` and `imgs/`, using an existing page (e.g. `pagina0`) as a structural reference (842×595 px, fonts from `../shared/css/fonts.css`, `window.PAGE_DATA` in `data.js`).
2. Register the page in `backend/src/core/config.py`:
   - new member in the `Settings.PageName` enum;
   - entry in `pages_dir` at the desired position in the final PDF;
   - records it uses in `page_context_records` (see `.specs/architecture/03-pdf-generation.md` for the valid names).
3. If the page needs new database data, follow the flow in `.specs/architecture/01-architecture.md` (entity → interface → repository → dependencies → router).
4. At the end, indicate how to validate: `GET /api/v1/reports/pdf/{name}/{county_id}/` and update `.specs/business-rules/02-report-pages.md` with the new page's rules.
