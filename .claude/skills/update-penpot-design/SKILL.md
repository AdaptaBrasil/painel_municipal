---
name: update-penpot-design
description: Flow for integrating a Penpot export as a report page. Use when a new page design (or revision) arrives from Penpot in local_data/.
---

# Penpot Design Integration

Established project flow (see `.specs/business-rules/02-report-pages.md`):

1. **Origin**: the Penpot export lands in `local_data/src-atualizado/src/{page}/` (`index.html`, `styles.css`, `data.js`, `imgs/`). Never edit `local_data/` directly — it is a staging area.
2. **Mandatory adaptations when copying to `backend/src/static/report/{page}/`**:
   - Remove every `@font-face` from the CSS — fonts come from `../shared/css/fonts.css` (Roboto).
   - Keep the header comment citing the source Penpot board (traceability).
   - Convert municipality-data texts into Jinja2 variables (`{{ county_record.county }}`, etc.); fixed texts and color tokens stay in `data.js` (`window.PAGE_DATA`). Reader-visible report texts remain in Brazilian Portuguese.
   - Assets with relative paths `./imgs/...` (resolved via `base_url`).
   - Check dimensions: 842×595 px page, zero margins.
3. **Penpot class names** (e.g. `.rectangle-54ff94c2cd22`): preserve the hash suffixes — they link the CSS to the board. When adjusting geometry manually, recompute centering (`left + width/2 = 421` for the horizontal center).
4. **Validation**: generate the real page and compare it visually with the board:
   `curl -o /tmp/p.pdf "http://localhost:3000/api/v1/reports/pdf/{page}/{county_id}/"`
5. **Documentation**: visual rule changes (new dynamic elements, new states) must be reflected in `.specs/business-rules/02-report-pages.md`.
6. **Commit**: in English with a semantic tag (e.g. `feat: Update pagina5 layout from Penpot board X` or `style:` for a purely visual adjustment).
