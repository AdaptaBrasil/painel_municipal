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

Font: the stamp uses Inter, the same family as the report pages
(static/report/paginaN, family "Inter" in shared/css/fonts.css). A small
Latin-1 subset of Inter Regular is bundled at scripts/assets and embedded into
every stamped page as a TrueType FontFile2, so the number renders in Inter even
where the system has no Inter installed. Advance widths and the font descriptor
are read straight from that bundled TTF (stdlib only), so metrics can never
drift from the embedded outlines.

Size: the default is 9pt, matching the report body text. The report is 12px in
CSS and Playwright renders it at 96 dpi, then the merged PDF is scaled to 72 dpi
points (see PlaywrightPdfService._page_size_in_points), i.e. px * 72/96. So the
12px body line becomes 12 * 0.75 = 9pt in the merged PDF this script stamps.

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
  --margin-right PT       Right margin in points (default: 22).
  --margin-bottom PT      Bottom margin in points (default: 18).
  --font-size PT          Font size in points (default: 9, i.e. the report's
                          12px body text after the 96->72 dpi scale).
  --gray G                Text gray level 0=black .. 1=white (default: 0.2).

Examples:
  add_page_numbers.py paginas_completas/                 # number every PDF, in place
  add_page_numbers.py --format "{n}/{total}" report.pdf  # "1/9", "2/9" ...
  add_page_numbers.py --skip-first --output-dir out/ a.pdf b.pdf
"""

from __future__ import annotations

import argparse
import io
import struct
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
        "  docker exec fichas_backend python /path/to/add_page_numbers.py ...\n"
    )
    sys.exit(1)

# Bundled Inter Regular subset (Latin-1). Same family as the report pages; a
# subset keeps the per-page embedded font a few KB instead of the full ~800KB.
_FONT_PATH = Path(__file__).resolve().parent / "assets" / "Inter-Regular-subset.ttf"
# PostScript name of the bundled subset (see the /name renaming at build time).
_FONT_PSNAME = "Inter-Regular"
# The stamp encodes labels as WinAnsi (a Latin-1 superset), so every character
# is a single byte and text width is a straight table lookup.
_FIRST_CHAR, _LAST_CHAR = 32, 255


class _Font:
    """Metrics and raw bytes of the embedded TrueType font, all in 1/1000 em.

    Everything a PDF simple TrueType font needs (widths, descriptor, FontFile2)
    is derived here from the bundled TTF so the stamp is self-contained.
    """

    def __init__(self, path: Path) -> None:
        data = path.read_bytes()
        self.data = data

        tables = self._table_directory(data)
        head_off = tables["head"][0]
        units_per_em = struct.unpack(">H", data[head_off + 18:head_off + 20])[0]
        x_min, y_min, x_max, y_max = struct.unpack(">4h", data[head_off + 36:head_off + 44])

        hhea_off = tables["hhea"][0]
        ascent, descent = struct.unpack(">2h", data[hhea_off + 4:hhea_off + 8])
        num_hmetrics = struct.unpack(">H", data[hhea_off + 34:hhea_off + 36])[0]

        advances = self._advance_widths(data, tables["hmtx"][0], num_hmetrics)
        cmap = self._unicode_cmap(data, tables["cmap"][0])

        scale = 1000.0 / units_per_em

        def advance_of(gid: int) -> int:
            adv = advances[gid] if gid < len(advances) else advances[-1]
            return round(adv * scale)

        # Width per byte code (WinAnsi ~ cp1252 -> Unicode -> glyph -> advance).
        self.width_by_code: dict[int, int] = {}
        self.width_by_char: dict[str, int] = {}
        for code in range(_FIRST_CHAR, _LAST_CHAR + 1):
            ch = bytes([code]).decode("cp1252", "ignore")
            gid = cmap.get(ord(ch)) if ch else None
            width = advance_of(gid) if gid else 0
            self.width_by_code[code] = width
            if ch:
                self.width_by_char[ch] = width
        self._default_width = self.width_by_char.get("0", 600)

        cap_height = self._cap_height(data, tables)
        self.bbox = tuple(round(v * scale) for v in (x_min, y_min, x_max, y_max))
        self.ascent = round(ascent * scale)
        self.descent = round(descent * scale)
        self.cap_height = round(cap_height * scale) if cap_height else self.ascent

    @staticmethod
    def _table_directory(data: bytes) -> dict[str, tuple[int, int]]:
        num_tables = struct.unpack(">H", data[4:6])[0]
        tables: dict[str, tuple[int, int]] = {}
        pos = 12
        for _ in range(num_tables):
            tag, _, off, length = struct.unpack(">4sIII", data[pos:pos + 16])
            tables[tag.decode("latin-1")] = (off, length)
            pos += 16
        return tables

    @staticmethod
    def _advance_widths(data: bytes, hmtx_off: int, num_hmetrics: int) -> list[int]:
        return [
            struct.unpack(">H", data[hmtx_off + i * 4:hmtx_off + i * 4 + 2])[0]
            for i in range(num_hmetrics)
        ]

    @staticmethod
    def _unicode_cmap(data: bytes, cmap_off: int) -> dict[int, int]:
        """Return a Unicode -> glyph-id map from the best BMP cmap subtable."""
        n_sub = struct.unpack(">H", data[cmap_off + 2:cmap_off + 4])[0]
        best: tuple[int, int] | None = None
        for i in range(n_sub):
            pid, eid, sub_off = struct.unpack(
                ">HHI", data[cmap_off + 4 + i * 8:cmap_off + 4 + i * 8 + 8]
            )
            score = {(3, 1): 3, (0, 3): 2, (0, 4): 2, (3, 0): 1}.get((pid, eid), 0)
            if score and (best is None or score > best[0]):
                best = (score, cmap_off + sub_off)
        if best is None:
            return {}

        sub = best[1]
        fmt = struct.unpack(">H", data[sub:sub + 2])[0]
        cmap: dict[int, int] = {}
        if fmt != 4:  # the bundled subset uses format 4; nothing else is expected
            return cmap

        seg_x2 = struct.unpack(">H", data[sub + 6:sub + 8])[0]
        seg = seg_x2 // 2
        pos = sub + 14
        end = struct.unpack(">%dH" % seg, data[pos:pos + seg_x2]); pos += seg_x2 + 2
        start = struct.unpack(">%dH" % seg, data[pos:pos + seg_x2]); pos += seg_x2
        delta = struct.unpack(">%dh" % seg, data[pos:pos + seg_x2]); pos += seg_x2
        idro_pos = pos
        idro = struct.unpack(">%dH" % seg, data[pos:pos + seg_x2])
        for i in range(seg):
            for c in range(start[i], end[i] + 1):
                if c == 0xFFFF:
                    continue
                if idro[i] == 0:
                    gid = (c + delta[i]) & 0xFFFF
                else:
                    addr = idro_pos + i * 2 + idro[i] + (c - start[i]) * 2
                    gid = struct.unpack(">H", data[addr:addr + 2])[0]
                    if gid:
                        gid = (gid + delta[i]) & 0xFFFF
                if gid:
                    cmap[c] = gid
        return cmap

    @staticmethod
    def _cap_height(data: bytes, tables: dict[str, tuple[int, int]]) -> int | None:
        """sCapHeight from OS/2 (version >= 2); None if unavailable."""
        entry = tables.get("OS/2")
        if not entry:
            return None
        off, length = entry
        version = struct.unpack(">H", data[off:off + 2])[0]
        if version < 2 or length < 90:
            return None
        return struct.unpack(">h", data[off + 88:off + 90])[0]

    def text_width(self, text: str, size: float) -> float:
        """Rendered width of `text` in points at `size`."""
        units = sum(self.width_by_char.get(ch, self._default_width) for ch in text)
        return units / 1000.0 * size

    def widths_array(self) -> str:
        """The /Widths entries for codes _FIRST_CHAR.._LAST_CHAR."""
        return " ".join(str(self.width_by_code[c])
                        for c in range(_FIRST_CHAR, _LAST_CHAR + 1))


_FONT: _Font | None = None


def _font() -> _Font:
    """Load and cache the bundled Inter subset."""
    global _FONT
    if _FONT is None:
        if not _FONT_PATH.exists():
            raise FileNotFoundError(
                f"Bundled font not found: {_FONT_PATH}. It ships with the repo "
                "under scripts/assets/."
            )
        _FONT = _Font(_FONT_PATH)
    return _FONT


def _escape_pdf_text(text: str) -> str:
    """Escape characters special inside a PDF literal string."""
    return text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def _build_stamp(page_w: float, page_h: float, text: str, x: float, y: float,
                 size: float, gray: float) -> bytes:
    """Return a one-page PDF (bytes) that draws `text` at (x, y) baseline.

    Inter (embedded TrueType, WinAnsiEncoding) so accented labels (e.g.
    "Página") render even without a system Inter.
    """
    font = _font()

    body = (
        f"BT /F1 {size:.2f} Tf {gray:.3f} {gray:.3f} {gray:.3f} rg "
        f"{x:.2f} {y:.2f} Td ({_escape_pdf_text(text)}) Tj ET"
    ).encode("latin-1")

    ttf = font.data
    bbox = " ".join(str(v) for v in font.bbox)
    font_obj = (
        f"<< /Type /Font /Subtype /TrueType /BaseFont /{_FONT_PSNAME} "
        f"/FirstChar {_FIRST_CHAR} /LastChar {_LAST_CHAR} /Widths 6 0 R "
        f"/FontDescriptor 7 0 R /Encoding /WinAnsiEncoding >>"
    ).encode("latin-1")
    widths_obj = ("[ " + font.widths_array() + " ]").encode("latin-1")
    descriptor_obj = (
        f"<< /Type /FontDescriptor /FontName /{_FONT_PSNAME} /Flags 32 "
        f"/FontBBox [{bbox}] /ItalicAngle 0 /Ascent {font.ascent} "
        f"/Descent {font.descent} /CapHeight {font.cap_height} /StemV 88 "
        f"/FontFile2 8 0 R >>"
    ).encode("latin-1")
    fontfile_obj = (
        b"<< /Length " + str(len(ttf)).encode() + b" /Length1 "
        + str(len(ttf)).encode() + b" >>\nstream\n" + ttf + b"\nendstream"
    )

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            f"<< /Type /Page /Parent 2 0 R /MediaBox "
            f"[0 0 {page_w:.2f} {page_h:.2f}] "
            f"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"
        ).encode("latin-1"),
        b"<< /Length " + str(len(body)).encode() + b" >>\nstream\n" + body + b"\nendstream",
        font_obj,
        widths_obj,
        descriptor_obj,
        fontfile_obj,
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
    font = _font()

    for index, page in enumerate(reader.pages):
        if args.skip_first and index == 0:
            writer.add_page(page)
            continue

        counted = index + (0 if args.skip_first else 1)  # 1-based logical page
        number = args.start + (counted - 1)
        label = args.format.format(n=number, total=total)

        box = page.mediabox
        page_w, page_h = float(box.width), float(box.height)
        text_w = font.text_width(label, args.font_size)
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
                        help="Right (or left) margin in points (default: 22).")
    parser.add_argument("--margin-bottom", type=float, default=18.0,
                        help="Bottom margin in points (default: 18).")
    parser.add_argument("--font-size", type=float, default=8.0,
                        help="Font size in points (default: 9, the report's 12px "
                             "body text after the 96->72 dpi scale).")
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
