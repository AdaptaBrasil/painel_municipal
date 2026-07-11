#!/usr/bin/env bash
#
# download_reports_by_page_range.sh
#
# Download a single page of the municipal adaptation-plan reports (PDF) from
# the API, looping from county_id_init to county_id_final (inclusive).
#
# Usage:
#   ./download_reports_by_page_range.sh <base_url> <page_name> <county_id_init> <county_id_final> [output_dir]
#
# Arguments:
#   base_url          Base URL of the API, e.g. http://localhost:3000
#   page_name         Name of the report page, e.g. pagina1, pagina2, pagina3 ...
#   county_id_init    Natural positive integer (> 0), first id in the range
#   county_id_final   Natural positive integer (> 0), last id in the range
#                     (must be >= county_id_init)
#   output_dir        Optional. Destination folder. Default: output/reports/
#
# Example:
#   ./download_reports_by_page_range.sh http://localhost:3000 pagina2 1 50
#   ./download_reports_by_page_range.sh http://localhost:3000 pagina3 1 50 my/custom/folder
#
# Each file is saved with the same name provided by the server
# (Content-Disposition header), e.g.:
#   {geocode}_{page_name}.pdf

set -uo pipefail

# ---- Argument parsing -------------------------------------------------------

if [[ $# -lt 4 || $# -gt 5 ]]; then
  echo "Usage: $0 <base_url> <page_name> <county_id_init> <county_id_final> [output_dir]" >&2
  exit 1
fi

BASE_URL="$1"
PAGE_NAME="$2"
COUNTY_ID_INIT="$3"
COUNTY_ID_FINAL="$4"
OUTPUT_DIR="${5:-output/reports}"

# ---- Execution time log -----------------------------------------------------

COMMAND_LINE="$0 $*"
LOG_FILE="execution_time_range.log"

# Returns the elapsed time (in seconds, 2 decimals) since the given timestamp.
elapsed_since() {
  awk -v s="$1" -v e="$(date +%s.%N)" 'BEGIN { printf "%.2f", e - s }'
}

# Appends an entry to LOG_FILE (and echoes it to the terminal) with date,
# time, script name, command used, results and execution times.
# Each appended entry is followed by 2 blank lines.
log_result() {
  local result="$1" total_elapsed="$2" avg_elapsed="$3" entry
  entry="[$(date '+%Y-%m-%d %H:%M:%S')] Script: $(basename "$0")
Command: ${COMMAND_LINE}
Result: ${result}
Total execution time: ${total_elapsed} s
Average time per download: ${avg_elapsed} s"
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

# Both ids must be natural positive integers (> 0).
if ! [[ "$COUNTY_ID_INIT" =~ ^[1-9][0-9]*$ ]]; then
  echo "Error: county_id_init must be a natural positive integer greater than zero. Got: '$COUNTY_ID_INIT'" >&2
  exit 1
fi

if ! [[ "$COUNTY_ID_FINAL" =~ ^[1-9][0-9]*$ ]]; then
  echo "Error: county_id_final must be a natural positive integer greater than zero. Got: '$COUNTY_ID_FINAL'" >&2
  exit 1
fi

if (( COUNTY_ID_FINAL < COUNTY_ID_INIT )); then
  echo "Error: county_id_final ($COUNTY_ID_FINAL) must be >= county_id_init ($COUNTY_ID_INIT)." >&2
  exit 1
fi

# Strip a trailing slash from base_url to avoid building a double slash.
BASE_URL="${BASE_URL%/}"

# ---- Download loop ----------------------------------------------------------

# Create the output directory (and parents) if it does not exist.
mkdir -p "$OUTPUT_DIR"

# Temporary directory so curl can save each file with the server-provided
# name (-OJ) before moving it to the output directory.
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

total=$(( COUNTY_ID_FINAL - COUNTY_ID_INIT + 1 ))
success=0
failed=0
failed_ids=()

echo "Downloading page '${PAGE_NAME}' of ${total} report(s) for county_id ${COUNTY_ID_INIT}..${COUNTY_ID_FINAL}"
echo "Output directory: ${OUTPUT_DIR}"
echo

START_TIME="$(date +%s.%N)"

for (( county_id = COUNTY_ID_INIT; county_id <= COUNTY_ID_FINAL; county_id++ )); do
  url="${BASE_URL}/api/v1/reports/pdf/${PAGE_NAME}/${county_id}/"

  echo "[${county_id}] Downloading ${url}"

  # -O : save with remote name; -J : use Content-Disposition filename
  if (cd "$TMP_DIR" && curl -fSsL -X GET "$url" -H 'accept: application/json' -OJ); then
    downloaded_file="$(find "$TMP_DIR" -maxdepth 1 -type f | head -n 1)"
    if [[ -z "$downloaded_file" ]]; then
      echo "[${county_id}] FAILED (download succeeded but no file was saved)." >&2
      (( ++failed ))
      failed_ids+=("$county_id")
      continue
    fi
    filename="$(basename "$downloaded_file")"
    mv -f "$downloaded_file" "${OUTPUT_DIR}/${filename}"
    echo "[${county_id}] Saved: ${OUTPUT_DIR}/${filename}"
    (( ++success ))
  else
    status=$?
    echo "[${county_id}] FAILED (curl exit code ${status})." >&2
    rm -f "$TMP_DIR"/* 2>/dev/null
    (( ++failed ))
    failed_ids+=("$county_id")
  fi
done

# ---- Summary ----------------------------------------------------------------

TOTAL_ELAPSED="$(elapsed_since "$START_TIME")"
AVG_ELAPSED="$(awk -v t="$TOTAL_ELAPSED" -v n="$total" 'BEGIN { printf "%.2f", t / n }')"

echo
echo "Finished. ${success} succeeded, ${failed} failed (out of ${total})."

if (( failed > 0 )); then
  echo "Failed county_id(s): ${failed_ids[*]}" >&2
  log_result "ERROR: page '${PAGE_NAME}', range ${COUNTY_ID_INIT}..${COUNTY_ID_FINAL} - ${success} succeeded, ${failed} failed (out of ${total}) - failed county_id(s): ${failed_ids[*]}" "$TOTAL_ELAPSED" "$AVG_ELAPSED"
  exit 1
fi

log_result "SUCCESS: page '${PAGE_NAME}', range ${COUNTY_ID_INIT}..${COUNTY_ID_FINAL} - ${success} succeeded, ${failed} failed (out of ${total})" "$TOTAL_ELAPSED" "$AVG_ELAPSED"
