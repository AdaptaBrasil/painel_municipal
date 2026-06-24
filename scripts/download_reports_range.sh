#!/usr/bin/env bash
#
# download_reports_range.sh
#
# Download a range of municipal adaptation-plan reports (PDF) from the API,
# looping from county_id_init to county_id_final (inclusive).
#
# Usage:
#   ./download_reports_range.sh <base_url> <county_id_init> <county_id_final> [output_dir]
#
# Arguments:
#   base_url          Base URL of the API, e.g. http://localhost:3000
#   county_id_init    Natural positive integer (> 0), first id in the range
#   county_id_final   Natural positive integer (> 0), last id in the range
#                     (must be >= county_id_init)
#   output_dir        Optional. Destination folder. Default: output/reports/
#
# Example:
#   ./download_reports_range.sh http://localhost:3000 1 50
#   ./download_reports_range.sh http://localhost:3000 1 50 my/custom/folder
#
# Each saved file follows the format:
#   {county_id}_relatorio_municipal_Plano_Adaptacao.pdf

set -uo pipefail

# ---- Argument parsing -------------------------------------------------------

if [[ $# -lt 3 || $# -gt 4 ]]; then
  echo "Usage: $0 <base_url> <county_id_init> <county_id_final> [output_dir]" >&2
  exit 1
fi

BASE_URL="$1"
COUNTY_ID_INIT="$2"
COUNTY_ID_FINAL="$3"
OUTPUT_DIR="${4:-output/reports}"

# ---- Validation -------------------------------------------------------------

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

total=$(( COUNTY_ID_FINAL - COUNTY_ID_INIT + 1 ))
success=0
failed=0
failed_ids=()

echo "Downloading ${total} report(s) for county_id ${COUNTY_ID_INIT}..${COUNTY_ID_FINAL}"
echo "Output directory: ${OUTPUT_DIR}"
echo

for (( county_id = COUNTY_ID_INIT; county_id <= COUNTY_ID_FINAL; county_id++ )); do
  url="${BASE_URL}/api/v1/reports/pdf/${county_id}"
  output_file="${OUTPUT_DIR}/${county_id}_relatorio_municipal_Plano_Adaptacao.pdf"

  echo "[${county_id}] Downloading ${url}"

  if curl -fSsL -X GET "$url" \
       -H 'accept: application/json' \
       -o "$output_file"; then
    echo "[${county_id}] Saved: ${output_file}"
    (( ++success ))
  else
    status=$?
    echo "[${county_id}] FAILED (curl exit code ${status})." >&2
    rm -f "$output_file"
    (( ++failed ))
    failed_ids+=("$county_id")
  fi
done

# ---- Summary ----------------------------------------------------------------

echo
echo "Finished. ${success} succeeded, ${failed} failed (out of ${total})."

if (( failed > 0 )); then
  echo "Failed county_id(s): ${failed_ids[*]}" >&2
  exit 1
fi
