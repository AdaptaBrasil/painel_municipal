#!/usr/bin/env python3
"""
add_page_numbers.py

Stamp a sequential page number onto every page of a merged municipality PDF
(or every PDF in a directory). The number reflects the page's position in the
document (1, 2, 3 ...), not the source page identity.

The number is drawn as an overlay on top of the existing page, so the original
content -- including clickable link annotations (the InfoMS dashboard links) --
is preserved untouched. This is why Ghostscript's pdfwrite is deliberately not
used here: it rebuilds the PDF and drops those link annotations.

Only pypdf (already a backend dependency) plus the standard library are used;
the numbering stamp is a hand-built minimal PDF, so reportlab is not required.

Usage:
  add_page_numbers.py [options] <pdf_or_dir> [<pdf_or_dir> ...]

Common options:
  --in-place              Overwrite each input PDF (default when a directory is
                          given). For single files, default is to write a copy.
  --output-dir DIR        Write results into DIR (keeps original file names).
  --suffix SUFFIX         Append SUFFIX to the file name when not in-place
                          (default: "_numbered").
  --start N               Number of the first page (default: 1).
  --skip-first            Do not number the first page (e.g. a cover), and start
                          counting from the second page.
  --format FMT            Label format; supports {n} and {total}
                          (default: "{n}", e.g. "{n}/{total}" or "Pagina {n}").
  --position POS          bottom-right (default) | bottom-center | bottom-left.
  --margin-right PT       Right margin in points (default: 40).
  --margin-bottom PT      Bottom margin in points (default: 18).
  --font-size PT          Font size in points (default: 11).
  --gray G                Text gray level 0=black .. 1=white (default: 0.2).

Examples:
  add_page_numbers.py paginas_completas/                 # number every PDF, in place
  add_page_numbers.py --format "{n}/{total}" report.pdf  # "1/9", "2/9" ...
  add_page_numbers.py --skip-first --output-dir out/ a.pdf b.pdf
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:  # pragma: no cover - environment guard
    sys.stderr.write(
        "Error: pypdf is required but not installed.\n"
        "Install it (pip install 'pypdf>=4,<5') or run this script with a\n"
        "Python that has it, e.g.:\n"
        "  PYTHON_BIN=python3 ...            (set an interpreter with pypdf)\n"
        "  docker exec painel_backend python /path/to/add_page_numbers.py ...\n"
    )
    sys.exit(1)

# Standard-14 Helvetica advance widths (1/1000 em) for the glyphs we actually
# draw; anything else falls back to 556 so alignment stays sensible.
_HELV_WIDTHS = {
    " ": 278, "/": 278,
    "0": 556, "1": 556, "2": 556, "3": 556, "4": 556, "5": 556,
    "6": 556, "7": 556, "8": 556, "9": 556,
    "P": 667, "a": 556, "g": 556, "i": 222, "n": 556, "á": 556,
}


def _text_width(text: str, size: float) -> float:
    """Approximate rendered width of `text` in points for Helvetica at `size`."""
    units = sum(_HELV_WIDTHS.get(ch, 556) for ch in text)
    return units / 1000.0 * size


def _escape_pdf_text(text: str) -> str:
    """Escape characters special inside a PDF literal string."""
    return text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def _build_stamp(page_w: float, page_h: float, text: str, x: float, y: float,
                 size: float, gray: float) -> bytes:
    """Return a one-page PDF (bytes) that draws `text` at (x, y) baseline.

    Helvetica with WinAnsiEncoding so accented labels (e.g. "Página") render.
    """
    body = (
        f"BT /F1 {size:.2f} Tf {gray:.3f} {gray:.3f} {gray:.3f} rg "
        f"{x:.2f} {y:.2f} Td ({_escape_pdf_text(text)}) Tj ET"
    ).encode("latin-1")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            f"<< /Type /Page /Parent 2 0 R /MediaBox "
            f"[0 0 {page_w:.2f} {page_h:.2f}] "
            f"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"
        ).encode("latin-1"),
        b"<< /Length " + str(len(body)).encode() + b" >>\nstream\n" + body + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
        b"/Encoding /WinAnsiEncoding >>",
    ]

    out = io.BytesIO()
    out.write(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(out.tell())
        out.write(f"{i} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref_pos = out.tell()
    out.write(f"xref\n0 {len(objects) + 1}\n".encode())
    out.write(b"0000000000 65535 f \n")
    for off in offsets:
        out.write(f"{off:010d} 00000 n \n".encode())
    out.write(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode()
        + f"startxref\n{xref_pos}\n%%EOF".encode()
    )
    return out.getvalue()


def _stamp_position(pos: str, page_w: float, text_w: float,
                    margin_right: float, margin_bottom: float) -> tuple[float, float]:
    """Compute the text baseline (x, y) for the requested position."""
    y = margin_bottom
    if pos == "bottom-left":
        x = margin_right  # reuse the same margin value as a left inset
    elif pos == "bottom-center":
        x = (page_w - text_w) / 2.0
    else:  # bottom-right (default)
        x = page_w - margin_right - text_w
    return x, y


def number_pdf(src: Path, dst: Path, args: argparse.Namespace) -> int:
    """Write `src` to `dst` with page numbers. Returns the page count."""
    reader = PdfReader(str(src))
    writer = PdfWriter()
    total = len(reader.pages)

    for index, page in enumerate(reader.pages):
        if args.skip_first and index == 0:
            writer.add_page(page)
            continue

        counted = index + (0 if args.skip_first else 1)  # 1-based logical page
        number = args.start + (counted - 1)
        label = args.format.format(n=number, total=total)

        box = page.mediabox
        page_w, page_h = float(box.width), float(box.height)
        text_w = _text_width(label, args.font_size)
        x, y = _stamp_position(
            args.position, page_w, text_w, args.margin_right, args.margin_bottom
        )

        stamp = PdfReader(
            io.BytesIO(_build_stamp(page_w, page_h, label, x, y,
                                    args.font_size, args.gray))
        ).pages[0]
        page.merge_page(stamp)  # overlay on top; keeps base page /Annots (links)
        writer.add_page(page)

    dst.parent.mkdir(parents=True, exist_ok=True)
    # Write to a temp file first so an interrupted run never truncates the input
    # (matters for --in-place).
    tmp = dst.with_suffix(dst.suffix + ".tmp")
    with open(tmp, "wb") as fh:
        writer.write(fh)
    tmp.replace(dst)
    return total


def _resolve_targets(paths: list[str]) -> list[Path]:
    """Expand directories into their *.pdf files; keep files as given."""
    targets: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            targets.extend(sorted(f for f in p.glob("*.pdf") if f.is_file()))
        elif p.is_file():
            targets.append(p)
        else:
            sys.stderr.write(f"Warning: '{raw}' is not a file or directory; skipped.\n")
    return targets


def _output_path(src: Path, args: argparse.Namespace, had_dir_input: bool) -> Path:
    if args.output_dir:
        return Path(args.output_dir) / src.name
    if args.in_place or had_dir_input:
        return src
    return src.with_name(f"{src.stem}{args.suffix}{src.suffix}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Stamp sequential page numbers onto merged municipality PDFs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("paths", nargs="+", help="PDF file(s) and/or directory(ies).")
    parser.add_argument("--in-place", action="store_true",
                        help="Overwrite inputs (default when a directory is given).")
    parser.add_argument("--output-dir", default=None,
                        help="Write results here, keeping original file names.")
    parser.add_argument("--suffix", default="_numbered",
                        help="Suffix for output files when not in-place.")
    parser.add_argument("--start", type=int, default=1,
                        help="Number of the first counted page (default: 1).")
    parser.add_argument("--skip-first", action="store_true",
                        help="Leave the first page unnumbered and start on page 2.")
    parser.add_argument("--format", default="{n}",
                        help="Label format with {n} and {total} (default: '{n}').")
    parser.add_argument("--position", default="bottom-right",
                        choices=["bottom-right", "bottom-center", "bottom-left"],
                        help="Where to place the number (default: bottom-right).")
    parser.add_argument("--margin-right", type=float, default=22.0,
                        help="Right (or left) margin in points (default: 32).")
    parser.add_argument("--margin-bottom", type=float, default=18.0,
                        help="Bottom margin in points (default: 18).")
    parser.add_argument("--font-size", type=float, default=11.0,
                        help="Font size in points (default: 11).")
    parser.add_argument("--gray", type=float, default=0.2,
                        help="Text gray level, 0=black..1=white (default: 0.2).")
    args = parser.parse_args(argv)

    had_dir_input = any(Path(p).is_dir() for p in args.paths)
    targets = _resolve_targets(args.paths)
    if not targets:
        sys.stderr.write("Error: no PDF files to process.\n")
        return 1

    ok = 0
    for src in targets:
        dst = _output_path(src, args, had_dir_input)
        try:
            pages = number_pdf(src, dst, args)
        except Exception as exc:  # keep going over a batch, report at the end
            sys.stderr.write(f"[{src.name}] FAILED: {exc}\n")
            continue
        where = "in place" if dst == src else str(dst)
        print(f"[{src.name}] numbered {pages} page(s) -> {where}")
        ok += 1

    print(f"\nDone. {ok}/{len(targets)} PDF(s) numbered.")
    return 0 if ok == len(targets) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
