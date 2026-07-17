# Code Style

## Language
- **All generated source code must be in English**: variable, function and class names, comments, docstrings and log messages.
- **Exceptions (must remain in Brazilian Portuguese)**: user-facing texts and UI/UX content (frontend interface and PDF report content — titles, labels, unit suffixes), and domain terms coming from the database (e.g. columns `Ameaça`, `Capacidade adaptativa`).

## Python (backend)
- Follow the existing Clean Architecture: `domain/` does not import from `application/`, `infrastructure/` or FastAPI. Concrete implementations only enter through `application/dependencies.py`.
- Entities are Pydantic models with `Optional` fields defaulting to `None`; each aggregate has a `*Report` wrapper with `formatted_data_dict`.
- SQL queries are always parameterized (`$1`, `$2`…), `SELECT` only, against the `painel_municipal` schema.
- Naming: snake_case for functions/variables, PascalCase for classes, enums for constants (`ErrorKeys`, `PdfEngineType`).
- New errors: add an `ERR_*` key to `core/constants.py`; never loose error strings.
- Flow logs with `print` follow the existing pattern (`--- message ---`); do not introduce a logging framework without a decision recorded in `.specs/`.

## Frontend (Vanilla JS)
- No frameworks and no CDN dependencies.
- Every API call uses the `API_BASE_URL` resolved in `app.js`; never a hardcoded URL at the call site.
- Interface texts in Brazilian Portuguese.

## Report templates (`backend/src/static/report/`)
- Fixed size 842×595 px; nothing may overflow the viewport.
- CSS extracted from Penpot without local `@font-face` (fonts in `shared/css/fonts.css`).
- Dynamic data arrives formatted via the Jinja2 context; the template neither calculates nor formats values.
- Header comments in `styles.css`/`data.js` reference the source Penpot board — keep them up to date.
