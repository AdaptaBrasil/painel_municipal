#!/usr/bin/env bash
#
# download_reports_by_page.sh
#
# Download a single page of a municipal adaptation-plan report (PDF) from the API.
#
# Usage:
#   ./download_reports_by_page.sh <base_url> <page_name> <county_id> [output_dir]
#
# Arguments:
#   base_url     Base URL of the API, e.g. http://localhost:3000
#   page_name    Name of the report page, e.g. pagina1, pagina2, pagina3 ...
#   county_id    Natural positive integer (> 0)
#   output_dir   Optional. Destination folder. Default: output/reports/
#
# Example:
#   ./download_reports_by_page.sh http://localhost:3000 pagina2 1
#   ./download_reports_by_page.sh http://localhost:3000 pagina3 42 my/custom/folder
#
# The file is saved with the same name provided by the server
# (Content-Disposition header), e.g.:
#   {geocode}_{page_name}.pdf

set -euo pipefail

# ---- Argument parsing -------------------------------------------------------

if [[ $# -lt 3 || $# -gt 4 ]]; then
  echo "Usage: $0 <base_url> <page_name> <county_id> [output_dir]" >&2
  exit 1
fi

BASE_URL="$1"
PAGE_NAME="$2"
COUNTY_ID="$3"
OUTPUT_DIR="${4:-output/reports}"

# ---- Execution time log -----------------------------------------------------

COMMAND_LINE="$0 $*"
LOG_FILE="execution_time.log"

# Returns the elapsed time (in seconds, 2 decimals) since the given timestamp.
elapsed_since() {
  awk -v s="$1" -v e="$(date +%s.%N)" 'BEGIN { printf "%.2f", e - s }'
}

# Appends an entry to LOG_FILE (and echoes it to the terminal) with date,
# time, script name, command used, result and execution time.
# Each appended entry is followed by 2 blank lines.
log_result() {
  local result="$1" elapsed="$2" entry
  entry="[$(date '+%Y-%m-%d %H:%M:%S')] Script: $(basename "$0")
Command: ${COMMAND_LINE}
Result: ${result}
Execution time: ${elapsed} s"
  echo
  echo "$entry"
  printf '%s\n\n\n' "$entry" >> "$LOG_FILE"
}

# ---- Validation -------------------------------------------------------------

# page_name must be a simple identifier (letters, digits, underscore, dash).
if ! [[ "$PAGE_NAME" =~ ^[A-Za-z0-9_-]+$ ]]; then
  echo "Error: page_name must contain only letters, digits, underscore or dash. Got: '$PAGE_NAME'" >&2
  exit 1
fi

# county_id must be a natural positive integer (> 0), no leading zeros, no sign.
if ! [[ "$COUNTY_ID" =~ ^[1-9][0-9]*$ ]]; then
  echo "Error: county_id must be a natural positive integer greater than zero. Got: '$COUNTY_ID'" >&2
  exit 1
fi

# Strip a trailing slash from base_url to avoid building a double slash.
BASE_URL="${BASE_URL%/}"

# ---- Download ---------------------------------------------------------------

# Create the output directory (and parents) if it does not exist.
mkdir -p "$OUTPUT_DIR"

URL="${BASE_URL}/api/v1/reports/pdf/${PAGE_NAME}/${COUNTY_ID}/"

echo "Downloading page '${PAGE_NAME}' for county_id=${COUNTY_ID} ..."
echo "  URL: ${URL}"

# Download into a temporary directory so curl can save the file with the
# server-provided name (-OJ), then move it to the output directory.
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

# -f  : fail (non-zero exit) on HTTP errors like 404/500
# -S  : show error message when -s is used
# -s  : silent (no progress meter)
# -L  : follow redirects
# -O  : save with remote name
# -J  : use the filename from the Content-Disposition header
START_TIME="$(date +%s.%N)"
if (cd "$TMP_DIR" && curl -fSsL -X GET "$URL" -H 'accept: application/json' -OJ); then
  ELAPSED="$(elapsed_since "$START_TIME")"
  downloaded_file="$(find "$TMP_DIR" -maxdepth 1 -type f | head -n 1)"
  if [[ -z "$downloaded_file" ]]; then
    echo "Error: download succeeded but no file was saved." >&2
    log_result "ERROR: page '${PAGE_NAME}', county_id=${COUNTY_ID} - download succeeded but no file was saved" "$ELAPSED"
    exit 1
  fi
  filename="$(basename "$downloaded_file")"
  mv -f "$downloaded_file" "${OUTPUT_DIR}/${filename}"
  echo "Done: ${OUTPUT_DIR}/${filename}"
  log_result "SUCCESS: page '${PAGE_NAME}', county_id=${COUNTY_ID} - saved ${OUTPUT_DIR}/${filename}" "$ELAPSED"
else
  status=$?
  ELAPSED="$(elapsed_since "$START_TIME")"
  echo "Failed to download page '${PAGE_NAME}' for county_id=${COUNTY_ID} (curl exit code ${status})." >&2
  log_result "ERROR: page '${PAGE_NAME}', county_id=${COUNTY_ID} - download failed (curl exit code ${status})" "$ELAPSED"
  exit "$status"
fi
