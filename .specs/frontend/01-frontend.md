# Frontend Specification

## Scope

Minimal static application (no framework): `frontend/index.html`, `frontend/css/style.css`, `frontend/js/app.js`, served by **Nginx** (`painel_frontend` container).

## Functionality

1. On load (`DOMContentLoaded`), fetches `GET {API}/counties` and populates `<select id="county-select">` with the placeholder "Selecione um município...".
2. The `#download-btn` button starts disabled; it is enabled when a municipality is selected.
3. Clicking the button opens `GET {API}/reports/pdf/{county_id}` in a new tab (`window.open`), which triggers the PDF download (due to `Content-Disposition: attachment`).

## API URL resolution

Precedence order in `resolveApiBaseUrl()`:

1. `window.APP_CONFIG.API_BASE_URL` (explicit override via injected configuration).
2. Local hostname (`localhost`, `127.0.0.1`, `0.0.0.0`) → `http://localhost:3000/api/v1` (local backend).
3. Otherwise → relative path `/api/v1` (production: Nginx proxies to the backend — see `frontend/nginx.conf`).

## Error handling

- Failure to load municipalities: the `<select>` shows the disabled option "Erro ao carregar os municípios" and the error is logged to the console.
- Click without a selection: silent guard clause (does nothing).

## Constraints

- No external dependencies (no CDN JS/CSS libraries).
- Interface texts in **Brazilian Portuguese** (UI/UX language rule).
- Any new API call must use the resolved `API_BASE_URL` — never a hardcoded URL at the call site.
