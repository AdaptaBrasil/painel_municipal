# UC-004 — Check Service Health

## Description
Expose a diagnostic endpoint for monitoring and troubleshooting: backend status, active PDF engine, configured pages, project version and database connectivity.

## Actors
- **Primary**: Operator/DevOps, external monitoring, developer.

## Trigger
`GET /api/v1/health`

## Main flow
1. System builds the base response: `{"backend": {"status": "ok", ...}}`.
2. Adds `pdf_engine` (value of `settings.pdf_engine`) and `pages_dir` (configured pages).
3. Attempts to read the project metadata (`ProjectInfoService` → `pyproject.toml`: name, version, description) and aggregates it under `project`.
4. Attempts to open/close a database connection (`test_connection`) and aggregates `database_status: "connected" | "disconnected"`.
5. Responds `200` whenever the process is up.

## Business rules
- **Resilience**: a failure in any partial check (metadata, database) **does not** bring the endpoint down — the error is logged and the field omitted/degraded. HTTP 200 only means "process alive"; the real database health must be read from `database_status`.

## Monitoring requirements
- Monitoring systems must alert when `database_status != "connected"`, even with HTTP 200.

## References
- `backend/src/application/router.py` (`health_check`)
- `backend/src/infrastructure/project_info_service.py`
