#!/usr/bin/env bash
#
# download_report.sh
#
# Download a single municipal adaptation-plan report (PDF) from the API.
#
# Usage:
#   ./download_report.sh <base_url> <county_id> [output_dir]
#
# Arguments:
#   base_url     Base URL of the API, e.g. http://localhost:3000
#   county_id    Natural positive integer (> 0)
#   output_dir   Optional. Destination folder. Default: output/reports/
#
# Example:
#   ./download_report.sh http://localhost:3000 1
#   ./download_report.sh http://localhost:3000 42 my/custom/folder
#
# The saved file follows the format:
#   {county_id}_relatorio_municipal_Plano_Adaptacao.pdf

set -euo pipefail

# ---- Argument parsing -------------------------------------------------------

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "Usage: $0 <base_url> <county_id> [output_dir]" >&2
  exit 1
fi

BASE_URL="$1"
COUNTY_ID="$2"
OUTPUT_DIR="${3:-output/reports}"

# ---- Validation -------------------------------------------------------------

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

URL="${BASE_URL}/api/v1/reports/pdf/${COUNTY_ID}"
OUTPUT_FILE="${OUTPUT_DIR}/${COUNTY_ID}_relatorio_municipal_Plano_Adaptacao.pdf"

echo "Downloading report for county_id=${COUNTY_ID} ..."
echo "  URL:  ${URL}"
echo "  File: ${OUTPUT_FILE}"

# -f  : fail (non-zero exit) on HTTP errors like 404/500
# -S  : show error message when -s is used
# -s  : silent (no progress meter)
# -L  : follow redirects
# -o  : output file
if curl -fSsL -X GET "$URL" \
     -H 'accept: application/json' \
     -o "$OUTPUT_FILE"; then
  echo "Done: ${OUTPUT_FILE}"
else
  status=$?
  echo "Failed to download report for county_id=${COUNTY_ID} (curl exit code ${status})." >&2
  # Remove the (possibly empty/partial) file so a failure does not leave junk behind.
  rm -f "$OUTPUT_FILE"
  exit "$status"
fi
