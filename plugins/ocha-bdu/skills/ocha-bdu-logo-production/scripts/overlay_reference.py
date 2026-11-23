#!/usr/bin/env python3
"""Overlay a rebuilt logo on its reference and score the match.

    python3 overlay_reference.py REFERENCE.png REBUILT.png out.png

Both images are trimmed to their artwork and the rebuilt one is scaled to the
reference's width, so colours and file sizes don't matter, only shapes.
In out.png black = both agree, red = only in the reference, cyan = only in the
rebuild. Thin fringes are antialiasing; a whole red/cyan letter or a shifted
word is a real difference.

Prints the share of artwork pixels that differ. A good rebuild with the right
fonts scores about 2% at equal resolution and under 10% against a smaller PNG
(all edge fringe); a wrong font scores 40%+ (IASC, Oct 2026: 8.6% right fonts
vs 46.5% wrong fonts). Always look at out.png as well as the number. Also use it to pick the font for a PNG reference: render the
text in each candidate font and keep the one with the lowest score.

For a PDF reference, render the page first (pdftoppm -r 288 -png) and crop.
"""
import sys
import numpy as np
from PIL import Image


def ink(path):
    a = np.array(Image.open(path).convert("RGBA")).astype(float)
    if a[:, :, 3].min() < 250:
        m = a[:, :, 3] > 128
    else:
        lum = a[:, :, :3].mean(axis=2)
        m = np.abs(lum - lum[0, 0]) > 64
    ys, xs = np.nonzero(m)
    return Image.fromarray(m[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8) * 255)


def main(ref, new, out):
    r, n = ink(ref), ink(new)
    n = n.resize((r.width, round(n.height * r.width / n.width)), Image.LANCZOS)
    h = max(r.height, n.height)
    R = np.zeros((h, r.width), bool); R[:r.height] = np.array(r) > 128
    N = np.zeros((h, r.width), bool); N[:n.height] = np.array(n) > 128
    img = np.full((h, r.width, 3), 255, np.uint8)
    img[R & N] = (0, 0, 0)
    img[R & ~N] = (230, 0, 0)
    img[~R & N] = (0, 190, 220)
    Image.fromarray(img).save(out)
    diff = (R ^ N).sum() / max((R | N).sum(), 1) * 100
    hdiff = abs(r.height - n.height) / r.height * 100
    print(f"differing artwork pixels: {diff:.1f}%   height difference at same width: {hdiff:.1f}%   -> {out}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
