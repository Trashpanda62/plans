#!/usr/bin/env python3
"""build_assets.py — Signage dashboard asset normalizer.

Every signage item is emitted as a matched PDF + PNG pair into ./assets/, so the
dashboard can show a PNG preview and offer both a PDF and a PNG download for each.

Sources (masters), in priority order:
  1. C:/Users/Steve/Downloads/Tapestry Acres/**  (the real masters: PDFs, PNGs, JPGs, DOCX signs)
  2. existing ./assets/ files already curated into the dashboard

Rules:
  - PDF master           -> keep PDF, rasterize page 1 -> PNG preview (150 dpi)
  - PNG/JPG master       -> keep/convert to PNG, wrap -> single-page PDF (fit to page)
  - DOCX sign            -> SKIPPED here (needs a render step); listed in report for manual export
  - JPG that duplicates a PNG/PDF of the same stem is de-duped (PDF+PNG pair wins)

Output naming: <slug>.pdf + <slug>.png  (slug = kebab of the master stem)

Requires: PyMuPDF (fitz), Pillow. No network.
"""
from __future__ import annotations
import re, sys, json
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
DOWNLOADS = Path(r"C:/Users/Steve/Downloads/Tapestry Acres")

PREVIEW_DPI = 150
IMG_EXTS = {".png", ".jpg", ".jpeg"}


def slug(stem: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")
    return s or "item"


def png_from_pdf(pdf: Path, out_png: Path) -> None:
    doc = fitz.open(pdf)
    page = doc[0]
    zoom = PREVIEW_DPI / 72.0
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    pix.save(out_png)
    doc.close()


def pdf_from_img(img: Path, out_pdf: Path) -> None:
    im = Image.open(img)
    if im.mode in ("RGBA", "P", "LA"):
        bg = Image.new("RGB", im.size, "white")
        bg.paste(im, mask=im.convert("RGBA").split()[-1] if im.mode != "P" else None)
        im = bg
    else:
        im = im.convert("RGB")
    im.save(out_pdf, "PDF", resolution=150.0)


def norm_png(img: Path, out_png: Path) -> None:
    im = Image.open(img)
    if img.suffix.lower() == ".png" and img.resolve() == out_png.resolve():
        return
    im = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
    im.save(out_png, "PNG")


def collect_masters() -> dict[str, Path]:
    """stem-slug -> best master path (PDF preferred, then PNG, then JPG)."""
    rank = {".pdf": 0, ".png": 1, ".jpeg": 2, ".jpg": 3}
    best: dict[str, Path] = {}
    roots = [DOWNLOADS, ASSETS]
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            ext = p.suffix.lower()
            if ext not in ({".pdf"} | IMG_EXTS):
                continue
            s = slug(p.stem)
            if s not in best or rank.get(ext, 9) < rank.get(best[s].suffix.lower(), 9):
                best[s] = p
    return best


def main() -> int:
    ASSETS.mkdir(parents=True, exist_ok=True)
    masters = collect_masters()
    report = {"pairs": [], "docx_todo": [], "errors": []}

    # DOCX signs need a manual/LibreOffice render — list them so nothing is silently dropped.
    for root in (DOWNLOADS,):
        if root.exists():
            for d in root.rglob("*.docx"):
                report["docx_todo"].append(str(d))

    for s, master in sorted(masters.items()):
        out_pdf = ASSETS / f"{s}.pdf"
        out_png = ASSETS / f"{s}.png"
        try:
            ext = master.suffix.lower()
            if ext == ".pdf":
                if master.resolve() != out_pdf.resolve():
                    out_pdf.write_bytes(master.read_bytes())
                png_from_pdf(out_pdf, out_png)
            elif ext in IMG_EXTS:
                norm_png(master, out_png)
                pdf_from_img(out_png, out_pdf)
            report["pairs"].append({"slug": s, "master": str(master),
                                    "pdf": out_pdf.name, "png": out_png.name})
        except Exception as e:  # noqa
            report["errors"].append({"slug": s, "master": str(master), "err": str(e)[:200]})

    (HERE / "assets-manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"pairs: {len(report['pairs'])}  docx_todo: {len(report['docx_todo'])}  errors: {len(report['errors'])}")
    for e in report["errors"]:
        print("  ERR", e["slug"], e["err"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
