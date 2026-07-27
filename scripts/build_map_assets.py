#!/usr/bin/env python3
"""Emit responsive WebP variants of the storybook world map + a size report.

Reads world-map.jpg at the repo root, writes art/world-map-{1280,2048,3200}.webp
(quality 80, method=6) and scratchpad/map-sizes.json. Run with py -3.12 (PIL
installed there). The 1280 variant carries the phone budget: if it lands over
300 KB the caller re-runs at quality 72 (this script takes --quality).
"""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "world-map.jpg"
ART = REPO / "art"
REPORT = REPO / "scratchpad" / "map-sizes.json"
WIDTHS = (1280, 2048, 3200)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quality", type=int, default=80)
    a = ap.parse_args()
    if not SRC.is_file():
        print(f"source missing: {SRC}", file=sys.stderr)
        return 2
    ART.mkdir(exist_ok=True)
    REPORT.parent.mkdir(exist_ok=True)
    img = Image.open(SRC).convert("RGB")
    sizes = {"source": {"px": list(img.size), "bytes": SRC.stat().st_size},
             "quality": a.quality, "variants": {}}
    for w in WIDTHS:
        h = round(img.height * w / img.width)
        out = ART / f"world-map-{w}.webp"
        img.resize((w, h), Image.LANCZOS).save(
            out, "WEBP", quality=a.quality, method=6)
        sizes["variants"][str(w)] = {"px": [w, h], "bytes": out.stat().st_size}
        print(f"  {out.name}: {out.stat().st_size} bytes")
    REPORT.write_text(json.dumps(sizes, indent=1), encoding="utf-8")
    print(f"report -> {REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
