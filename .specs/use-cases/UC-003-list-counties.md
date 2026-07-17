# UC-003 — List Available Municipalities

## Description
Provide the list of municipalities with available data to populate the frontend selector.

## Actors
- **Primary**: Frontend (initial page load).

## Preconditions
- Database reachable; `painel_municipal.adapta_data` table populated.

## Trigger
`GET /api/v1/counties` (fired on the frontend's `DOMContentLoaded`).

## Main flow
1. System executes `SELECT DISTINCT county_id, geocode, county, region, state, CONCAT(county, ' - ', state) AS display ... ORDER BY display`.
2. Each record is validated as a `County` entity.
3. Response `200` with the list ordered alphabetically by `display`.
4. Frontend populates the `<select>` using `county_id` as value and `display` as label, and enables the download button once an item is selected.

## Alternative flows / exceptions
- **A1 — Empty list or query error**: repository raises `ERR_DATA_RETRIEVAL_FAILED` → `500`; the frontend shows "Erro ao carregar os municípios" in the selector.

## Business rules
- `display` is always derived in SQL as `{county} - {state}`; the frontend concatenates nothing.
- The list must contain only municipalities with a record in `adapta_data` (the source of truth for availability).

## References
- `backend/src/infrastructure/repository.py` (`CountyRepository.get_counties`)
- `frontend/js/app.js`
