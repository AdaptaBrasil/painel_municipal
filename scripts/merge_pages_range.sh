#!/usr/bin/env bash
#
# merge_pages_range.sh
#
# Merge the per-page PDFs of each municipality into a single complete PDF.
# Each input folder holds one page per municipality, named {geocode}.pdf.
# The script picks the same {geocode}.pdf in every folder (in the order the
# folders are given) and merges them into output_dir/{geocode}.pdf.
#
# Usage:
#   ./merge_pages_range.sh [-n num_files] <num_folders> <folder1> <folder2> ... <folderN> [output_dir]
#
# Arguments:
#   -n num_files  Optional. Process only the first num_files geocodes
#                 (sorted order). Default: process all of them.
#   num_folders   Natural positive integer (> 0), number of page folders
#   folder1..N    Folders with the page PDFs, in merge order,
#                 e.g. pagina1 pagina2 pagina3 ...
#   output_dir    Optional. Destination folder. Default: paginas_completas/
#
# Example:
#   ./merge_pages_range.sh 4 pagina2 pagina3 pagina4 pagina5
#   ./merge_pages_range.sh -n 10 4 pagina2 pagina3 pagina4 pagina5
#   ./merge_pages_range.sh 2 pagina2 pagina3 my/custom/folder
#
# Each merged file is saved as {geocode}.pdf. A geocode is only merged when
# its PDF exists in every input folder; missing ones are reported at the end.
#
# Special case: a folder whose only PDF is a single file named file.pdf holds
# a page shared by every municipality (e.g. pagina1, pagina6). That file.pdf
# is used for all geocodes instead of a per-geocode PDF.

set -uo pipefail

# ---- Argument parsing -------------------------------------------------------

COMMAND_LINE="$0 $*"

MAX_FILES=0
if [[ "${1:-}" == "-n" ]]; then
  MAX_FILES="${2:-}"
  if ! [[ "$MAX_FILES" =~ ^[1-9][0-9]*$ ]]; then
    echo "Error: -n requires a natural positive integer greater than zero. Got: '${MAX_FILES}'" >&2
    exit 1
  fi
  shift 2
fi

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 [-n num_files] <num_folders> <folder1> <folder2> ... <folderN> [output_dir]" >&2
  exit 1
fi

NUM_FOLDERS="$1"
shift

if ! [[ "$NUM_FOLDERS" =~ ^[1-9][0-9]*$ ]]; then
  echo "Error: num_folders must be a natural positive integer greater than zero. Got: '$NUM_FOLDERS'" >&2
  exit 1
fi

if [[ $# -lt $NUM_FOLDERS || $# -gt $((NUM_FOLDERS + 1)) ]]; then
  echo "Error: expected $NUM_FOLDERS folder(s) plus an optional output_dir, got $# argument(s)." >&2
  exit 1
fi

FOLDERS=("${@:1:$NUM_FOLDERS}")
OUTPUT_DIR="${*:$((NUM_FOLDERS + 1)):1}"
OUTPUT_DIR="${OUTPUT_DIR:-paginas_completas}"

# ---- Execution time log -----------------------------------------------------

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
Average time per merge: ${avg_elapsed} s"
  echo
  echo "$entry"
  printf '%s\n\n\n' "$entry" >> "$LOG_FILE"
}

# ---- Validation -------------------------------------------------------------

if ! command -v pdfunite >/dev/null 2>&1; then
  echo "Error: pdfunite not found. Install it with: sudo apt install poppler-utils" >&2
  exit 1
fi

for folder in "${FOLDERS[@]}"; do
  if [[ ! -d "$folder" ]]; then
    echo "Error: folder '$folder' does not exist or is not a directory." >&2
    exit 1
  fi
done

# ---- Merge loop -------------------------------------------------------------

# Create the output directory (and parents) if it does not exist.
mkdir -p "$OUTPUT_DIR"

# Folders whose only PDF is a single file.pdf hold a page shared by every
# municipality: that same file.pdf is merged for all geocodes.
declare -A SHARED_PDF=()
for folder in "${FOLDERS[@]}"; do
  mapfile -t folder_pdfs < <(find "$folder" -maxdepth 1 -type f -name '*.pdf' -printf '%f\n')
  if (( ${#folder_pdfs[@]} == 1 )) && [[ "${folder_pdfs[0]}" == "file.pdf" ]]; then
    SHARED_PDF["$folder"]=1
    echo "Folder '${folder}' has a single shared file.pdf; it will be used for every geocode."
  fi
done

# Union of all geocodes found across the input folders (sorted, unique).
# Shared-PDF folders do not define geocodes, so file.pdf is left out.
mapfile -t GEOCODES < <(
  for folder in "${FOLDERS[@]}"; do
    [[ -n "${SHARED_PDF[$folder]:-}" ]] && continue
    find "$folder" -maxdepth 1 -type f -name '*.pdf' ! -name 'file.pdf' -printf '%f\n'
  done | sed 's/\.pdf$//' | sort -u
)

if (( ${#GEOCODES[@]} == 0 )); then
  echo "Error: no PDF files found in the given folder(s)." >&2
  exit 1
fi

# Keep only the first MAX_FILES geocodes when -n was given.
if (( MAX_FILES > 0 && MAX_FILES < ${#GEOCODES[@]} )); then
  GEOCODES=("${GEOCODES[@]:0:MAX_FILES}")
fi

total=${#GEOCODES[@]}
success=0
failed=0
failed_geocodes=()

echo "Merging ${total} municipality PDF(s) from ${NUM_FOLDERS} folder(s): ${FOLDERS[*]}"
echo "Output directory: ${OUTPUT_DIR}"
echo

START_TIME="$(date +%s.%N)"

for geocode in "${GEOCODES[@]}"; do
  parts=()
  missing_in=()

  for folder in "${FOLDERS[@]}"; do
    if [[ -n "${SHARED_PDF[$folder]:-}" ]]; then
      parts+=("${folder}/file.pdf")
      continue
    fi
    part="${folder}/${geocode}.pdf"
    if [[ -f "$part" ]]; then
      parts+=("$part")
    else
      missing_in+=("$folder")
    fi
  done

  if (( ${#missing_in[@]} > 0 )); then
    echo "[${geocode}] FAILED (missing in: ${missing_in[*]})." >&2
    (( ++failed ))
    failed_geocodes+=("$geocode")
    continue
  fi

  if pdfunite "${parts[@]}" "${OUTPUT_DIR}/${geocode}.pdf"; then
    echo "[${geocode}] Saved: ${OUTPUT_DIR}/${geocode}.pdf"
    (( ++success ))
  else
    status=$?
    echo "[${geocode}] FAILED (pdfunite exit code ${status})." >&2
    rm -f "${OUTPUT_DIR}/${geocode}.pdf" 2>/dev/null
    (( ++failed ))
    failed_geocodes+=("$geocode")
  fi
done

# ---- Summary ----------------------------------------------------------------

TOTAL_ELAPSED="$(elapsed_since "$START_TIME")"
AVG_ELAPSED="$(awk -v t="$TOTAL_ELAPSED" -v n="$total" 'BEGIN { printf "%.2f", t / n }')"

echo
echo "Finished. ${success} succeeded, ${failed} failed (out of ${total})."

if (( failed > 0 )); then
  echo "Failed geocode(s): ${failed_geocodes[*]}" >&2
  log_result "ERROR: merge of ${NUM_FOLDERS} folder(s) (${FOLDERS[*]}) - ${success} succeeded, ${failed} failed (out of ${total}) - failed geocode(s): ${failed_geocodes[*]}" "$TOTAL_ELAPSED" "$AVG_ELAPSED"
  exit 1
fi

log_result "SUCCESS: merge of ${NUM_FOLDERS} folder(s) (${FOLDERS[*]}) - ${success} succeeded, ${failed} failed (out of ${total})" "$TOTAL_ELAPSED" "$AVG_ELAPSED"
