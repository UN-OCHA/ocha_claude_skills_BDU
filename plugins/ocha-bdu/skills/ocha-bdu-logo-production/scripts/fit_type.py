#!/usr/bin/env python3
"""Font size and tracking that reproduce a measured line of a reference logo.

    python3 fit_type.py FONT.ttf "TEXT" CAP_HEIGHT INK_WIDTH

CAP_HEIGHT  height of a flat-topped capital (I, H, E) in the reference
INK_WIDTH   left edge of the first letter to right edge of the last
Both in the same unit (pt from a PDF, px from a PNG); the size comes out in it.

Size comes from the font's own cap height (OS/2 sCapHeight), tracking from the
width difference spread over the letter gaps, in Illustrator units (1/1000 em).
Kerning is not applied here, so treat the tracking as a first value: set it in
Illustrator with auto kerning on, measure the outlined width once, and correct
it in one step (width is linear in tracking: no search loop needed, and loops
that outline and measure repeatedly make osascript time out).
"""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen


def main(font, text, cap, width):
    f = TTFont(font)
    upm = f["head"].unitsPerEm
    cap_ratio = f["OS/2"].sCapHeight / upm
    size = cap / cap_ratio
    cmap, gs, hm = f.getBestCmap(), f.getGlyphSet(), f["hmtx"]
    x, x0, x1 = 0, None, None
    for ch in text:
        g = cmap[ord(ch)]
        bp = BoundsPen(gs)
        gs[g].draw(bp)
        if bp.bounds:
            x0 = x + bp.bounds[0] if x0 is None else x0
            x1 = x + bp.bounds[2]
        x += hm[g][0]
    ink = (x1 - x0) * size / upm
    tracking = (width - ink) / (len(text) - 1) / size * 1000
    print(f"{f['name'].getDebugName(6)}  cap height {cap_ratio:.4f} em")
    print(f"size      {size:.2f}")
    print(f"ink width at tracking 0: {ink:.2f}   target {width:.2f}")
    print(f"tracking  {tracking:+.0f}   (left side bearing of first letter: {x0 * size / upm:.2f})")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]))
