"""S7 (plan c-000926) — measure the farm map's real transferred image+video
bytes at a 390px-wide phone profile.

Parses index.html for every asset a 390px viewport would actually load:
  - the #farm <img>'s srcset/sizes -> picks the same candidate a browser's
    srcset-selection algorithm would pick at this width
  - the opener <video>'s <source media="..."> -> only counted if its media
    query matches at this width (S7 gated it to desktop, so a phone should
    match none); the poster image is always counted, since <video poster>
    loads regardless of whether any <source> matches
  - any other static <img src="..."> with no srcset (always loaded)
  - any CSS background-image:url(local-path) that isn't a data: URI
      (S7's RICH/backdrop-filter gating doesn't remove any image url()s,
      only the inline feTurbulence noise data: URI, which has zero network
      cost by definition and is correctly excluded here)

Local mode (default) reads asset sizes off disk relative to this repo.
--url mode fetches the live page + assets over HTTP instead, for verifying
the deployed GitHub Pages site (S7's last row).

Usage:
  py -3.12 scripts/measure_map.py                       # local index.html
  py -3.12 scripts/measure_map.py --url https://trashpanda62.github.io/plans/
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUDGET_BYTES = 600 * 1024  # 600 KB
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}
VIDEO_EXT = {".mp4", ".webm", ".mov"}


def _read_html(url: str | None) -> tuple[str, str]:
    """Return (html_text, base) where base is either a local dir Path-as-str
    or the HTTP base URL, used to resolve relative asset paths."""
    if url:
        with urllib.request.urlopen(url, timeout=20) as r:
            return r.read().decode("utf-8", "replace"), url
    return (REPO / "index.html").read_text(encoding="utf-8"), str(REPO)


def _asset_size(path_or_url: str, base: str, is_url: bool) -> int | None:
    if is_url:
        full = urllib.parse.urljoin(base if base.endswith("/") else base + "/", path_or_url)
        try:
            req = urllib.request.Request(full, method="HEAD")
            with urllib.request.urlopen(req, timeout=20) as r:
                cl = r.headers.get("Content-Length")
                if cl is not None:
                    return int(cl)
        except Exception:
            pass
        try:
            with urllib.request.urlopen(full, timeout=20) as r:
                return len(r.read())
        except Exception:
            return None
    p = Path(base) / path_or_url
    return p.stat().st_size if p.is_file() else None


# --- srcset/sizes selection (mirrors the browser's picture-source algorithm,
# density=1x, close enough for a byte-budget check at a fixed viewport) -----

_SIZES_COND = re.compile(r"\(max-width:\s*(\d+)px\)\s*([\d.]+)vw")


def _slot_width(sizes: str, viewport: int) -> int:
    for m in _SIZES_COND.finditer(sizes):
        cutoff, vw = int(m.group(1)), float(m.group(2))
        if viewport <= cutoff:
            return round(viewport * vw / 100)
    m = re.search(r"([\d.]+)vw\s*$", sizes.strip())
    if m:
        return round(viewport * float(m.group(1)) / 100)
    return viewport


def _pick_srcset(srcset: str, sizes: str, viewport: int) -> str:
    slot = _slot_width(sizes, viewport)
    candidates = []
    for part in srcset.split(","):
        part = part.strip()
        m = re.match(r"(\S+)\s+(\d+)w", part)
        if m:
            candidates.append((m.group(1), int(m.group(2))))
    if not candidates:
        return ""
    candidates.sort(key=lambda c: c[1])
    for url, w in candidates:
        if w >= slot:
            return url
    return candidates[-1][0]  # nothing big enough -> largest available


_MEDIA_MINW = re.compile(r"\(min-width:\s*(\d+)px\)")
_MEDIA_MAXW = re.compile(r"\(max-width:\s*(\d+)px\)")


def _media_matches(media: str, viewport: int) -> bool:
    ok = True
    mn = _MEDIA_MINW.search(media)
    if mn:
        ok = ok and viewport >= int(mn.group(1))
    mx = _MEDIA_MAXW.search(media)
    if mx:
        ok = ok and viewport <= int(mx.group(1))
    return ok


def find_assets(html: str, viewport: int) -> list[tuple[str, str]]:
    """Returns [(kind, path)] for every asset a `viewport`-wide load fetches."""
    out: list[tuple[str, str]] = []

    farm = re.search(r'<img id="farm"[^>]*>', html)
    if farm:
        tag = farm.group(0)
        src = re.search(r'\bsrc="([^"]+)"', tag)
        srcset = re.search(r'\bsrcset="([^"]+)"', tag)
        sizes = re.search(r'\bsizes="([^"]+)"', tag)
        if srcset and sizes:
            picked = _pick_srcset(srcset.group(1), sizes.group(1), viewport)
            out.append(("image", picked or (src.group(1) if src else "")))
        elif src:
            out.append(("image", src.group(1)))

    vid = re.search(r"<video\b[^>]*>.*?</video>", html, re.S)
    if vid:
        vtag = vid.group(0)
        poster = re.search(r'\bposter="([^"]+)"', vtag)
        if poster:
            out.append(("image", poster.group(1)))  # <video poster> always loads
        for smatch in re.finditer(r"<source\b([^>]*)>", vtag):
            attrs = smatch.group(1)
            srcm = re.search(r'\bsrc="([^"]+)"', attrs)
            mediam = re.search(r'\bmedia="([^"]+)"', attrs)
            if not srcm:
                continue
            if mediam and not _media_matches(mediam.group(1), viewport):
                continue  # gated out at this viewport (S7 row: phones skip the clip)
            out.append(("video", srcm.group(1)))

    for imgm in re.finditer(r"<img\b([^>]*)>", html):
        attrs = imgm.group(1)
        if 'id="farm"' in attrs:
            continue  # already handled above
        srcm = re.search(r'\bsrc="([^"]+)"', attrs)
        if srcm and not srcm.group(1).startswith(("data:", "http")):
            out.append(("image", srcm.group(1)))

    for bgm in re.finditer(r"background(?:-image)?:\s*url\(([^)]+)\)", html):
        ref = bgm.group(1).strip("'\"")
        if not ref.startswith("data:"):
            out.append(("image", ref))

    # de-dup, keep order
    seen = set()
    deduped = []
    for kind, ref in out:
        if ref and ref not in seen:
            seen.add(ref)
            deduped.append((kind, ref))
    return deduped


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=None, help="live base URL (e.g. Pages site); default = local index.html")
    ap.add_argument("--width", type=int, default=390, help="phone viewport width to simulate")
    ap.add_argument("--out", default=str(REPO / "scratchpad" / "map-perf.json"))
    args = ap.parse_args()

    html, base = _read_html(args.url)
    assets = find_assets(html, args.width)

    rows = []
    total = 0
    for kind, ref in assets:
        size = _asset_size(ref, base, is_url=bool(args.url))
        rows.append({"kind": kind, "path": ref, "bytes": size})
        if size:
            total += size

    result = {
        "phone_width": args.width,
        "mode": "live" if args.url else "local",
        "base": base,
        "assets": rows,
        "total_bytes": total,
        "budget_bytes": BUDGET_BYTES,
        "pass": total <= BUDGET_BYTES,
    }
    if args.url:
        result["live_url"] = args.url

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
