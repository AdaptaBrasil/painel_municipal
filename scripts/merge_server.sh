#!/usr/bin/env bash
#
# merge_server.sh
#
# Thin wrapper around merge_pages_range.sh for the folder layout used on the
# server, where each page lives in a directory named pagina{N}-{slug}:
#
#   pagina0-capa/pagina0/{geocode}.pdf     <- per-municipality pages (nested)
#   pagina1-intro/file.pdf                 <- page shared by every municipality
#   pagina2-adapta/pagina2/{geocode}.pdf
#   ...
#   pagina11-fechamento-2/file.pdf
#
# For each page the script resolves the folder automatically:
#   - if pagina{N}-{slug}/pagina{N}/ exists, that nested folder is used
#     (per-municipality {geocode}.pdf files);
#   - otherwise pagina{N}-{slug}/ itself is used (single shared file.pdf).
#
# Usage:
#   ./merge_server.sh [-d base_dir] [-n num_files] [--geocodes-from-file file] [-j workers] [-p] [output_dir]
#
# Arguments:
#   -d base_dir   Optional. Root folder holding the pagina{N}-* directories.
#                 Default: current directory.
#   -n num_files  Optional. Process only the first num_files geocodes.
#   --geocodes-from-file file
#                 Optional (short form: -g). Merge only the geocodes listed in
#                 file, one per line (blank lines, '#' comments and a trailing
#                 '.pdf' are accepted). Use it to reprocess only the
#                 municipalities missing from a previous run. Applied before -n.
#   -j workers    Optional (--jobs). Merge up to workers municipalities in
#                 parallel. Default: 1 (sequential). Try -j "$(nproc)"; on
#                 network/Drive-mounted folders the bottleneck is I/O, so
#                 higher values stop helping.
#   -p            Optional. Stamp sequential page numbers on the merged PDFs
#                 (the pagina0 cover stays unnumbered).
#   output_dir    Optional. Destination folder. Default: paginas_completas/
#
# Options may appear before or after output_dir.
#
# Example:
#   ./merge_server.sh                      # merge everything into paginas_completas/
#   ./merge_server.sh -p                   # same, with page numbering
#   ./merge_server.sh -n 5 -p /tmp/saida   # dry run with 5 municipalities
#   ./merge_server.sh -d /data/fichas -p
# Exemplo com output_dir:
#   ./merge_server.sh -d /data/fichas -p /tmp/saida
# Exemplo remerge apenas dos faltantes:
#   ./merge_server.sh -d /data/fichas -p /tmp/saida --geocodes-from-file missing.txt
# Exemplo em paralelo (8 workers):
#   ./merge_server.sh -d /data/fichas -p -j 8 /tmp/saida
#
# All options are forwarded to merge_pages_range.sh, which does the actual
# merge (pdfunite) and writes execution_time_range.log.

set -uo pipefail

# ---- Configuration ----------------------------------------------------------

# Pages to merge, in document order.
FIRST_PAGE=0
LAST_PAGE=11

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# The merge script sits next to this one; prefer a copy in the current
# directory when present (e.g. when running from the server working folder).
MERGE_SCRIPT="${SCRIPT_DIR}/merge_pages_range.sh"
[[ -f "merge_pages_range.sh" ]] && MERGE_SCRIPT="./merge_pages_range.sh"

# ---- Argument parsing -------------------------------------------------------

USAGE="Usage: $0 [-d base_dir] [-n num_files] [--geocodes-from-file file] [-j workers] [-p] [output_dir]"

BASE_DIR="."
PASSTHROUGH=()
POSITIONAL=()

while (( $# > 0 )); do
  case "$1" in
    -d)
      BASE_DIR="${2:-}"
      if [[ -z "$BASE_DIR" ]]; then
        echo "Error: -d requires a directory." >&2
        exit 1
      fi
      shift 2
      ;;
    -n)
      if [[ -z "${2:-}" ]]; then
        echo "Error: -n requires a value." >&2
        exit 1
      fi
      PASSTHROUGH+=(-n "$2")
      shift 2
      ;;
    -j|--jobs)
      if [[ -z "${2:-}" ]]; then
        echo "Error: $1 requires a value." >&2
        exit 1
      fi
      PASSTHROUGH+=(-j "$2")
      shift 2
      ;;
    -g|--geocodes-from-file)
      if [[ -z "${2:-}" ]]; then
        echo "Error: $1 requires a file path." >&2
        exit 1
      fi
      if [[ ! -f "$2" ]]; then
        echo "Error: geocode list '$2' does not exist or is not a file." >&2
        exit 1
      fi
      PASSTHROUGH+=(-g "$2")
      shift 2
      ;;
    -p)
      PASSTHROUGH+=(-p)
      shift
      ;;
    -h|--help)
      sed -n '2,54p' "${BASH_SOURCE[0]}"
      exit 0
      ;;
    --)
      shift
      POSITIONAL+=("$@")
      break
      ;;
    -*)
      echo "Error: unknown option '$1'." >&2
      echo "$USAGE" >&2
      exit 1
      ;;
    *)
      POSITIONAL+=("$1")
      shift
      ;;
  esac
done

if (( ${#POSITIONAL[@]} > 1 )); then
  echo "Error: expected at most one output_dir, got ${#POSITIONAL[@]} argument(s): ${POSITIONAL[*]}" >&2
  echo "$USAGE" >&2
  exit 1
fi

OUTPUT_DIR="${POSITIONAL[0]:-}"

# ---- Validation -------------------------------------------------------------

if [[ ! -f "$MERGE_SCRIPT" ]]; then
  echo "Error: merge_pages_range.sh not found (looked for '${MERGE_SCRIPT}')." >&2
  exit 1
fi

if [[ ! -d "$BASE_DIR" ]]; then
  echo "Error: base directory '${BASE_DIR}' does not exist or is not a directory." >&2
  exit 1
fi

# ---- Folder resolution ------------------------------------------------------

FOLDERS=()
missing_pages=()

for (( page = FIRST_PAGE; page <= LAST_PAGE; page++ )); do
  # Match pagina{N}-{slug}. The hyphen keeps pagina1-* from matching pagina10-*.
  mapfile -t candidates < <(find "$BASE_DIR" -mindepth 1 -maxdepth 1 -type d \
    -name "pagina${page}-*" | sort)

  if (( ${#candidates[@]} == 0 )); then
    missing_pages+=("pagina${page}")
    continue
  fi

  if (( ${#candidates[@]} > 1 )); then
    echo "Error: more than one folder matches 'pagina${page}-*': ${candidates[*]}" >&2
    exit 1
  fi

  parent="${candidates[0]}"

  # Per-municipality pages sit in a nested pagina{N}/ folder; shared pages
  # (a single file.pdf) sit directly in the pagina{N}-{slug} folder.
  if [[ -d "${parent}/pagina${page}" ]]; then
    resolved="${parent}/pagina${page}"
  else
    resolved="$parent"
  fi

  if ! find "$resolved" -maxdepth 1 -type f -name '*.pdf' -print -quit | grep -q .; then
    echo "Error: no PDF files found in '${resolved}'." >&2
    exit 1
  fi

  FOLDERS+=("$resolved")
  echo "pagina${page}: ${resolved}"
done

if (( ${#missing_pages[@]} > 0 )); then
  echo "Error: folder(s) not found under '${BASE_DIR}': ${missing_pages[*]}" >&2
  exit 1
fi

# ---- Merge ------------------------------------------------------------------

echo
echo "Merging ${#FOLDERS[@]} page folder(s) via $(basename "$MERGE_SCRIPT")..."
echo

CMD=(bash "$MERGE_SCRIPT" "${PASSTHROUGH[@]}" "${#FOLDERS[@]}" "${FOLDERS[@]}")
[[ -n "$OUTPUT_DIR" ]] && CMD+=("$OUTPUT_DIR")

"${CMD[@]}"
