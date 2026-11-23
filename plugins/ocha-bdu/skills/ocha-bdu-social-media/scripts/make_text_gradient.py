"""Make the BDU text gradients: black, transparent at the top, smoothstep to a max opacity at the bottom.

Two strengths are used on social cards:
  strong (80 %) — text over people or busy colour
  subtle (45 %) — text over sky, a wall or the ground

The ready-made 1080x900 files are in ../assets/. Run this only to make another size.
Usage: python3 make_text_gradient.py <width> <height> <max_opacity 0-1> <out.png>
Flip vertically in Canva for text at the top of a card.
"""
import sys

import numpy as np
from PIL import Image


def main():
    w, h, amax, out = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    t = np.linspace(0, 1, h)
    a = amax * (t * t * (3 - 2 * t))  # smoothstep: no visible hard edge
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., 3] = np.repeat((a * 255).astype(np.uint8)[:, None], w, axis=1)
    Image.fromarray(rgba, "RGBA").save(out)
    print(out)


if __name__ == "__main__":
    main()
