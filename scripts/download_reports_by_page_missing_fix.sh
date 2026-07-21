#!/usr/bin/env bash
#
# download_reports_by_page_missing_fix.sh
#
# Download a single page of the municipal adaptation-plan reports (PDF) from
# the API, but only for the county_id values listed in a file (one per line),
# instead of a full range. Useful to re-download only the ones that failed /
# are missing.
#
# Usage:
#   ./download_reports_by_page_missing_fix.sh <base_url> <page_name> <output_dir> --lista=<file> [--processos=<n>]
#
# Arguments:
#   base_url          Base URL of the API, e.g. http://localhost:3000
#   page_name         Name of the report page, e.g. pagina1, pagina2, pagina3 ...
#   output_dir        Destination folder for the downloaded PDFs, e.g. pagina4.
#                     Created (with parents) if it does not exist.
#   --lista=<file>    Required. Path to a text file with one county_id per line.
#   --processos=<n>   Optional. Number of parallel download processes.
#                     The list is split into <n> contiguous chunks and each
#                     chunk is downloaded by its own background process.
#                     Default: 1 (sequential).
#
# Example:
#   ./download_reports_by_page_missing_fix.sh http://localhost:3000 pagina3 pagina3 --lista=county_id_nao_baixados_pagina3.txt --processos=4
#
# Each file is saved with the same name provided by the server
# (Content-Disposition header), e.g.:
#   {geocode}.pdf

set -uo pipefail

# ---- Argument parsing -------------------------------------------------------

BASE_URL=""
PAGE_NAME=""
OUTPUT_DIR=""
LISTA_FILE=""
PROCESSES=1
POSITIONAL=()

USAGE="Usage: $0 <base_url> <page_name> <output_dir> --lista=<file> [--processos=<n>]"

for arg in "$@"; do
  case "$arg" in
    --lista=*)
      LISTA_FILE="${arg#--lista=}"
      ;;
    --processos=*)
      PROCESSES="${arg#--processos=}"
      ;;
    *)
      POSITIONAL+=("$arg")
      ;;
  esac
done

if [[ ${#POSITIONAL[@]} -ne 3 ]]; then
  echo "$USAGE" >&2
  exit 1
fi

BASE_URL="${POSITIONAL[0]}"
PAGE_NAME="${POSITIONAL[1]}"
OUTPUT_DIR="${POSITIONAL[2]}"

if [[ -z "$LISTA_FILE" ]]; then
  echo "Error: missing required --lista=<file> argument." >&2
  echo "$USAGE" >&2
  exit 1
fi

if ! [[ "$PROCESSES" =~ ^[1-9][0-9]*$ ]]; then
  echo "Error: --processos must be a positive integer. Got: '$PROCESSES'" >&2
  exit 1
fi

if [[ ! -f "$LISTA_FILE" ]]; then
  echo "Error: list file not found: '$LISTA_FILE'" >&2
  exit 1
fi

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

# Read county_ids from the list file, skipping blank lines, validating format.
COUNTY_IDS=()
while IFS= read -r line || [[ -n "$line" ]]; do
  line="$(echo -n "$line" | tr -d '[:space:]')"
  [[ -z "$line" ]] && continue
  if ! [[ "$line" =~ ^[1-9][0-9]*$ ]]; then
    echo "Error: invalid county_id in list file: '$line'" >&2
    exit 1
  fi
  COUNTY_IDS+=("$line")
done < "$LISTA_FILE"

if [[ ${#COUNTY_IDS[@]} -eq 0 ]]; then
  echo "Error: list file '$LISTA_FILE' is empty." >&2
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

total=${#COUNTY_IDS[@]}
success=0
failed=0
failed_ids=()

# Never spawn more processes than there are ids to download.
if (( PROCESSES > total )); then
  PROCESSES=$total
fi

echo "Downloading page '${PAGE_NAME}' of ${total} report(s) listed in '${LISTA_FILE}'"
echo "Output directory: ${OUTPUT_DIR}"
echo "Parallel processes: ${PROCESSES}"
echo

# Downloads a chunk of county_ids sequentially, using a private tmp dir so
# parallel workers never mix up each other's files. Writes its success count
# and failed ids to result files that the parent aggregates after wait.
download_worker() {
  local worker_id="$1"
  shift
  local tmp_dir="${TMP_DIR}/worker_${worker_id}"
  mkdir -p "$tmp_dir"
  local w_success=0
  local county_id url downloaded_file filename status

  : > "${TMP_DIR}/failed_${worker_id}.txt"

  for county_id in "$@"; do
    url="${BASE_URL}/api/v1/reports/pdf/${PAGE_NAME}/${county_id}/"

    echo "[P${worker_id}][${county_id}] Downloading ${url}"

    # -O : save with remote name; -J : use Content-Disposition filename
    if (cd "$tmp_dir" && curl -fSsL -X GET "$url" -H 'accept: application/json' -OJ); then
      downloaded_file="$(find "$tmp_dir" -maxdepth 1 -type f | head -n 1)"
      if [[ -z "$downloaded_file" ]]; then
        echo "[P${worker_id}][${county_id}] FAILED (download succeeded but no file was saved)." >&2
        echo "$county_id" >> "${TMP_DIR}/failed_${worker_id}.txt"
        continue
      fi
      filename="$(basename "$downloaded_file")"
      mv -f "$downloaded_file" "${OUTPUT_DIR}/${filename}"
      echo "[P${worker_id}][${county_id}] Saved: ${OUTPUT_DIR}/${filename}"
      (( ++w_success ))
    else
      status=$?
      echo "[P${worker_id}][${county_id}] FAILED (curl exit code ${status})." >&2
      rm -f "$tmp_dir"/* 2>/dev/null
      echo "$county_id" >> "${TMP_DIR}/failed_${worker_id}.txt"
    fi
  done

  echo "$w_success" > "${TMP_DIR}/success_${worker_id}.txt"
}

START_TIME="$(date +%s.%N)"

# Split COUNTY_IDS into PROCESSES contiguous chunks and launch one background
# worker per chunk.
chunk_size=$(( (total + PROCESSES - 1) / PROCESSES ))
worker_pids=()

for (( w = 0; w < PROCESSES; w++ )); do
  start=$(( w * chunk_size ))
  (( start >= total )) && break
  download_worker "$w" "${COUNTY_IDS[@]:start:chunk_size}" &
  worker_pids+=("$!")
done

wait "${worker_pids[@]}"

# Aggregate per-worker results.
for (( w = 0; w < PROCESSES; w++ )); do
  if [[ -f "${TMP_DIR}/success_${w}.txt" ]]; then
    (( success += $(cat "${TMP_DIR}/success_${w}.txt") ))
  fi
  if [[ -f "${TMP_DIR}/failed_${w}.txt" ]]; then
    while IFS= read -r fid; do
      [[ -z "$fid" ]] && continue
      (( ++failed ))
      failed_ids+=("$fid")
    done < "${TMP_DIR}/failed_${w}.txt"
  fi
done

# ---- Summary ----------------------------------------------------------------

TOTAL_ELAPSED="$(elapsed_since "$START_TIME")"
AVG_ELAPSED="$(awk -v t="$TOTAL_ELAPSED" -v n="$total" 'BEGIN { printf "%.2f", t / n }')"

echo
echo "Finished. ${success} succeeded, ${failed} failed (out of ${total})."

if (( failed > 0 )); then
  echo "Failed county_id(s): ${failed_ids[*]}" >&2
  log_result "ERROR: page '${PAGE_NAME}', list '${LISTA_FILE}' - ${success} succeeded, ${failed} failed (out of ${total}) - failed county_id(s): ${failed_ids[*]}" "$TOTAL_ELAPSED" "$AVG_ELAPSED"
  exit 1
fi

log_result "SUCCESS: page '${PAGE_NAME}', list '${LISTA_FILE}' - ${success} succeeded, ${failed} failed (out of ${total})" "$TOTAL_ELAPSED" "$AVG_ELAPSED"
