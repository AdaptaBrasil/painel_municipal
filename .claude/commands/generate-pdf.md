---
description: Generates a test PDF (single page or full report) and checks the result
argument-hint: [pagina0..pagina8|full] [county_id]
allowed-tools: Bash(curl *), Bash(pdfinfo *), Bash(ls *), Read
---

Generate a test PDF from the application using the arguments: $ARGUMENTS

1. Confirm the backend is up: `curl -s http://localhost:3000/api/v1/health` (check `database_status: connected`). If it is not, suggest running `make run`.
2. If the first argument is `full` (or empty), download the whole report:
   `curl -s -o /tmp/report.pdf "http://localhost:3000/api/v1/reports/pdf/{county_id}"`
   Otherwise, download the single page:
   `curl -s -o /tmp/report.pdf "http://localhost:3000/api/v1/reports/pdf/{page_name}/{county_id}/"`
   (default county_id: 1)
3. Validate the result: file starts with `%PDF`, size > 0 and, if `pdfinfo` is available, report the page count and dimensions.
4. Report the generated file path and any HTTP error (the `ERR_*` key from the response body).
