#!/usr/bin/env python3
"""Measure a reference logo so it can be rebuilt with live fonts.

PDF (a guideline, an old export):
    python3 reference_geometry.py guide.pdf PAGE [x0 y0 x1 y1]
  Prints every text span (font name, size, colour, baseline origin, ink bbox,
  per-letter x) and every filled vector shape (colour, bbox) inside the clip
  rectangle, in PDF points with y going DOWN. Live text names its font; outlined
  text shows up as one shape per letter, so letter heights and edges can still
  be read off.

PNG / JPG (a logo someone sent):
    python3 reference_geometry.py logo.png
  Prints the artwork bbox and every separate blob (letter, dot, mark) as
  x0 y0 x1 y1 in pixels, left to right. A PNG never names its font: identify it
  first (see SKILL.md section 3), then use these numbers for cap height, widths
  and gaps. Accuracy is about +-1 px, so a 200 px logo gives only rough values.

Next step: fit_type.py turns cap height + ink width into font size + tracking.
"""
import sys


def pdf(path, page, clip):
    import fitz
    p = fitz.open(path)[page - 1]
    r = fitz.Rect(*clip) if clip else p.rect
    print(f"page {page}  size {p.rect.width:.2f} x {p.rect.height:.2f} pt  clip {tuple(round(v, 2) for v in r)}")
    print("\nTEXT SPANS")
    for b in p.get_text("rawdict", clip=r)["blocks"]:
        for line in b.get("lines", []):
            for s in line["spans"]:
                txt = "".join(c["c"] for c in s["chars"])
                if not txt.strip():
                    continue
                xs = [round(c["origin"][0], 2) for c in s["chars"]]
                print(f"  {txt!r}  {s['font']}  {s['size']:.3f}pt  #{s['color']:06x}  "
                      f"baseline ({s['origin'][0]:.2f}, {s['origin'][1]:.2f})  bbox {[round(v, 2) for v in s['bbox']]}  x {xs}")
    print("\nFILLED SHAPES (colour, x0 y0 x1 y1)")
    for d in p.get_drawings():
        if not d.get("fill") or not d["rect"].intersects(r):
            continue
        rr, g, bb = (int(v * 255) for v in d["fill"][:3])
        print(f"  #{rr:02x}{g:02x}{bb:02x}  {[round(v, 2) for v in d['rect']]}")


def image(path):
    import numpy as np
    from PIL import Image
    from scipy import ndimage
    im = Image.open(path).convert("RGBA")
    a = np.array(im)
    if a[:, :, 3].min() < 250:
        ink = a[:, :, 3] > 128                      # transparent background
    else:
        lum = a[:, :, :3].mean(axis=2)              # opaque: ink = far from the corner colour
        ink = np.abs(lum - lum[0, 0]) > 64
    lab, n = ndimage.label(ink)
    boxes = ndimage.find_objects(lab)
    ys, xs = np.nonzero(ink)
    print(f"{path}  {im.width}x{im.height}px  artwork bbox {xs.min()} {ys.min()} {xs.max() + 1} {ys.max() + 1}")
    print(f"{n} blobs, left to right (x0 y0 x1 y1  w x h):")
    for sl in sorted(boxes, key=lambda s: (s[1].start, s[0].start)):
        y, x = sl
        print(f"  {x.start:5d} {y.start:5d} {x.stop:5d} {y.stop:5d}   {x.stop - x.start} x {y.stop - y.start}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0].lower().endswith(".pdf") or a[0].lower().endswith(".ai"):
        pdf(a[0], int(a[1]) if len(a) > 1 else 1, [float(v) for v in a[2:6]] if len(a) >= 6 else None)
    else:
        image(a[0])
