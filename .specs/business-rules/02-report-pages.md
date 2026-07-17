# Business Rules — Report Pages

Each page lives in `backend/src/static/report/paginaN/` and follows the pattern described in [`../architecture/03-pdf-generation.md`](../architecture/03-pdf-generation.md). Designs come from Penpot boards; the exported CSS is adapted (no local `@font-face` — fonts come from `shared/css/fonts.css`, main family **Roboto**).

## Rules common to all pages

1. Fixed size **842×595 px** (landscape); no content may overflow the viewport.
2. Dynamic texts come from the Jinja2 context (`county_record`, `*_record`); fixed texts and design tokens live in `data.js` (`window.PAGE_DATA`).
3. Municipality identification: `{{ county_record.county }} - {{ county_record.state }}` (displayed in uppercase via CSS `text-transform: uppercase`).
4. Values arrive already formatted from the backend — the template performs no calculation or formatting.
5. Risk indicator colors come from the database (`color`, `current_value_color`, `future_color`, `{detail}_color`) and are applied inline.
6. All report content visible to the reader (titles, labels, units) is written in **Brazilian Portuguese**.

## pagina0 — Cover

- "Fichas Municipais" title and background figure (`figura-mapa-quadrados-coloridos.png`) covering the page.
- Municipality box (`.rectangle-*`): horizontally centered (the box center must match `842/2 = 421px`), with the `municipality - state` name centered inside it. Current width: 360px (`left: 241px`).
- Data: `county_record` only.

## pagina1 — Institutional (static PDF)

- `file.pdf` provided by the design team; explains the AdaptaBrasil methodology ("flor de risco", indicator logic, INPE/AdaptaBrasil/GIZ/Plano Clima logos).
- No dynamic data. Replacement = swap the `file.pdf`.

## pagina2 — Climate Risk Factors

- Transposed risk table: one row per risk (`risk_id`), columns Ameaça/Exposição/Vulnerabilidade/Sensibilidade/Capacidade adaptativa, current and future values with their colors.
- Row order: `current_value` descending (most critical risks first), then `sep_id`, `risk`, `detail`.
- "Flor de risco" iconography.

## pagina3 — Municipal Indicators

- Blocks: territorial characterization, population characteristics, socioeconomic conditions, infrastructure and services, mobility.
- Rendered with `scale: 1.50` (page-specific config in `pages_dir`).
- Thematic icons (water, sewage, energy, waste).

## pagina4 — Municipal Resilience Profile

- Municipal plans displayed with a visual badge: `POSSUI` / `NÃO POSSUI` / `AUSENTE` (images in `imgs/`).
- Disaster history (counts) and total damages in short-scale currency.
- Municipality map when available; fallback: `imagem-sem-mapa-do-municipio.png`.

## pagina5 — Climate Projections

- Injects the full record into the template: `{{ climate_projection_record | tojson | safe }}` (consumed by the page's JS).
- Each climate variable shows: observed value + three scenarios (trend, optimistic, pessimistic) **with explicit sign** (`+`/`−`).
- Per-variable icons (mean/max/min temperature, dry days, rainy days, extreme rain, intensity, sea level).

## pagina6 — Municipal Health

- Epidemiological profile (incidence per 100k inhabitants), health resources (per 1k inhabitants), per-capita expenses and vaccine coverage (overall, under-2s, influenza 60+).

## pagina7 / pagina8 — Institutional (static PDF)

- Same treatment as pagina1.

## Design update flow

1. The design is edited in Penpot and exported.
2. The export is placed in `local_data/src-atualizado/src/paginaN/` for review.
3. After visual validation, the files are adapted and copied to `backend/src/static/report/paginaN/` (remove `@font-face`, point fonts to `shared/`, convert fixed texts into Jinja2 variables when they are dynamic).
4. Validate the result by generating the page in isolation: `GET /api/v1/reports/pdf/paginaN/{county_id}/`.
