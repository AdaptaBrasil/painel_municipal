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
#   ./merge_pages_range.sh [-n num_files] [-p] <num_folders> <folder1> <folder2> ... <folderN> [output_dir]
#
# Arguments:
#   -n num_files  Optional. Process only the first num_files geocodes
#                 (sorted order). Default: process all of them.
#   -p            Optional. After merging, stamp a sequential page number on
#                 every page of each output PDF (bottom-right corner). The
#                 number reflects the page position in the document (1, 2, 3
#                 ...). Requires a Python with pypdf (see PYTHON_BIN below);
#                 links in the report are preserved (overlay, not re-render).
#   num_folders   Natural positive integer (> 0), number of page folders
#   folder1..N    Folders with the page PDFs, in merge order,
#                 e.g. pagina1 pagina2 pagina3 ...
#   output_dir    Optional. Destination folder. Default: paginas_completas/
#
# Environment:
#   PYTHON_BIN    Interpreter used for the -p numbering step. It must have pypdf
#                 installed (the project already depends on it). If unset, the
#                 script auto-detects one, trying in order: ./.venv/bin/python,
#                 ../.venv/bin/python, python3, python. Set it explicitly to
#                 override, e.g. PYTHON_BIN=/path/to/poetry/venv/bin/python ...
#                 The numbering can also be run separately on the output folder:
#                 .venv/bin/python add_page_numbers.py paginas_completas/
#
# Example:
#   ./merge_pages_range.sh 4 pagina2 pagina3 pagina4 pagina5
#   ./merge_pages_range.sh -p 4 pagina2 pagina3 pagina4 pagina5
#   ./merge_pages_range.sh -n 10 -p 4 pagina2 pagina3 pagina4 pagina5
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
ADD_PAGE_NUMBERS=0
while [[ "${1:-}" == -* ]]; do
  case "$1" in
    -n)
      MAX_FILES="${2:-}"
      if ! [[ "$MAX_FILES" =~ ^[1-9][0-9]*$ ]]; then
        echo "Error: -n requires a natural positive integer greater than zero. Got: '${MAX_FILES}'" >&2
        exit 1
      fi
      shift 2
      ;;
    -p)
      ADD_PAGE_NUMBERS=1
      shift
      ;;
    *)
      echo "Error: unknown option '$1'." >&2
      echo "Usage: $0 [-n num_files] [-p] <num_folders> <folder1> <folder2> ... <folderN> [output_dir]" >&2
      exit 1
      ;;
  esac
done

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 [-n num_files] [-p] <num_folders> <folder1> <folder2> ... <folderN> [output_dir]" >&2
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

# Page-numbering helper (only when -p is used). The numbering script sits next
# to this one; prefer a copy in the current directory when present (e.g. when
# running from an outputs/ working folder).
NUMBER_SCRIPT="$(dirname "$0")/add_page_numbers.py"
[[ -f "add_page_numbers.py" ]] && NUMBER_SCRIPT="add_page_numbers.py"

# When the merge starts with pagina0, keep that cover page unnumbered and start
# numbering from the following page.
SKIP_FIRST_PAGE=0
if [[ $(basename "${FOLDERS[0]}") == "pagina0" ]]; then
  SKIP_FIRST_PAGE=1
fi

# Resolve a Python with pypdf. Honour an explicit PYTHON_BIN; otherwise probe a
# nearby virtualenv (common in the outputs/ folder) before falling back to a
# system interpreter, so the -p flag works without extra configuration.
if [[ -n "${PYTHON_BIN:-}" ]]; then
  PYTHON_CANDIDATES=("$PYTHON_BIN")
else
  PYTHON_CANDIDATES=(".venv/bin/python" "../.venv/bin/python" "python3" "python")
fi

if (( ADD_PAGE_NUMBERS )); then
  if [[ ! -f "$NUMBER_SCRIPT" ]]; then
    echo "Error: -p requested but 'add_page_numbers.py' was not found." >&2
    exit 1
  fi
  PYTHON_BIN=""
  for candidate in "${PYTHON_CANDIDATES[@]}"; do
    if $candidate -c 'import pypdf' >/dev/null 2>&1; then
      PYTHON_BIN="$candidate"
      break
    fi
  done
  if [[ -z "$PYTHON_BIN" ]]; then
    echo "Error: -p requires a Python with pypdf, none was found." >&2
    echo "       Tried: ${PYTHON_CANDIDATES[*]}" >&2
    echo "       Install it (pip install 'pypdf>=4,<5') or set PYTHON_BIN to an" >&2
    echo "       interpreter that has it (see the header of this script)." >&2
    exit 1
  fi
  echo "Page numbering enabled (using: ${PYTHON_BIN})."
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
    if (( ADD_PAGE_NUMBERS )); then
      number_args=(--in-place)
      if (( SKIP_FIRST_PAGE )); then
        number_args+=(--skip-first)
      fi
      if ! $PYTHON_BIN "$NUMBER_SCRIPT" "${number_args[@]}" "${OUTPUT_DIR}/${geocode}.pdf" >/dev/null; then
        echo "[${geocode}] FAILED (page numbering error)." >&2
        rm -f "${OUTPUT_DIR}/${geocode}.pdf" 2>/dev/null
        (( ++failed ))
        failed_geocodes+=("$geocode")
        continue
      fi
    fi
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
