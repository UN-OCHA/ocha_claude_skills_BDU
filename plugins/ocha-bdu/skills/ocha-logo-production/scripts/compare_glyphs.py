#!/usr/bin/env python3
"""Stack two exports for glyph-level comparison, to catch a font substitution.

Trims each image to its artwork, scales both to the same height and stacks them
on mid grey, so letterforms can be compared directly. Run it against the PREVIOUS
version of the same asset: shapes must match, with only the characters you
actually changed differing. A substituted font shows up as a different stroke
weight, different letterforms, or different line breaks -- none of which appear
in any log.

Keep a copy of the previous export before rebuilding, or there is nothing to
compare against.

    python3 compare_glyphs.py OLD.png NEW.png out.png
"""
import sys
from PIL import Image
import numpy as np

H = 160
GREY = (128, 128, 128)


def trim(path):
    im = Image.open(path).convert("RGBA")
    a = np.array(im)
    ys, xs = np.nonzero(a[:, :, 3] > 40)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def on_grey(im, height):
    w = max(1, round(im.width * height / im.height))
    im = im.resize((w, height), Image.LANCZOS)
    out = Image.new("RGB", (w, height), GREY)
    out.paste(im, (0, 0), im)
    return out


old_path, new_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
A, B = on_grey(trim(old_path), H), on_grey(trim(new_path), H)

PAD = 16
canvas = Image.new("RGB", (max(A.width, B.width), H * 2 + PAD * 3), GREY)
canvas.paste(A, (0, PAD))
canvas.paste(B, (0, H + PAD * 2))
canvas.save(out_path)

print(f"old {old_path}: {trim(old_path).size} -> {A.size}")
print(f"new {new_path}: {trim(new_path).size} -> {B.size}")
print(f"width ratio new/old = {B.width / A.width:.4f}  (near 1.00 = same proportions)")
print(f"-> {out_path}   now LOOK at it")
