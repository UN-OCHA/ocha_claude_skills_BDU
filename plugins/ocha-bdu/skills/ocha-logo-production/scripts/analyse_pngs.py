#!/usr/bin/env python3
"""Read-only analysis of exported PNGs: size, alpha coverage, art bbox, dominant opaque colours."""
import sys, os
from collections import Counter
from PIL import Image
import numpy as np

folder = sys.argv[1]
names = sorted(os.listdir(folder))
print(f"{'file':<42} {'size':>10} {'opaque%':>8}  {'art bbox (x0,y0,x1,y1)':<26} top opaque colours")
print("-" * 140)
for n in names:
    if not n.lower().endswith(".png"):
        continue
    p = os.path.join(folder, n)
    im = Image.open(p).convert("RGBA")
    a = np.array(im)
    alpha = a[:, :, 3]
    opaque = alpha > 200
    pct = 100.0 * opaque.mean()
    if opaque.any():
        ys, xs = np.nonzero(opaque)
        bbox = f"{xs.min()},{ys.min()},{xs.max()},{ys.max()}"
    else:
        bbox = "(empty)"
    px = a[opaque][:, :3]
    cnt = Counter(map(tuple, px))
    top = "  ".join(f"#{r:02X}{g:02X}{b:02X}:{100.0*c/len(px):.0f}%" for (r, g, b), c in cnt.most_common(4))
    print(f"{n:<42} {im.width:>4}x{im.height:<5} {pct:>7.1f}%  {bbox:<26} {top}")
