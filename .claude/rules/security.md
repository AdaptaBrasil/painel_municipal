# Security Requirements

- **Secrets**: credentials only in `.env` (never committed; `.env.example` is the contract). Do not read or print `.env` contents in logs or responses.
- **SQL**: only parameterized queries via asyncpg (`$1`…); interpolating user input into SQL is forbidden.
- **Database**: PostgreSQL port bound to `127.0.0.1` on the host (docker-compose) — never expose it externally.
- **API**: keep rate limiting (SlowAPI, 200/min per IP) on PDF endpoints; CORS restricted to the `ALLOWED_ORIGINS` list in `main.py` (add origins explicitly, never `*`); only `GET`/`OPTIONS` verbs.
- **Errors**: never expose stack traces or infrastructure details to the client; use stable `ERR_*` keys.
- **Playwright**: the `--disable-web-security --allow-file-access-from-files` flags exist only to render local template assets; never load untrusted external URLs in that context.
- **Input**: validate route parameters (e.g. `county_id` int `gt=0`; `page_name` against the configured page list).
