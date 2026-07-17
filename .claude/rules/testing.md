# Testing Strategy

## Current state
- `backend/tests/` exists but is empty (only `__init__.py`). New tests must use **pytest** via Poetry (`poetry run pytest`), with `httpx` for FastAPI endpoint tests.

## Guidelines for new tests
- **Domain first**: formatting rules (`CommonBusinessRules`, `*Report` wrappers) are pure functions — covering them with unit tests is cheap and high value (truncation, em dash `—`, IDH ranges, explicit sign, Mi/Bi scale).
- **Repositories**: test with a fake `DatabaseInterface` (list of dicts), no real database.
- **Endpoints**: use `TestClient`/`httpx.AsyncClient` with overridden dependencies (`app.dependency_overrides`) — never depend on a live PostgreSQL in unit tests.
- **PDF**: smoke tests only (bytes start with `%PDF`, page count via pypdf); do not compare exact bytes.

## Mandatory manual validation
Visual changes to report pages require generating the real output for review:
```bash
curl -o /tmp/pagina.pdf "http://localhost:3000/api/v1/reports/pdf/{page_name}/{county_id}/"
```
