#!/usr/bin/env python3
"""Labelled contact sheet of an export folder, composited on mid grey.

Mid grey is the point: white-on-transparent variants are invisible against both a
white and a black page, so a sheet on grey is the only way to see a whole set at
once. Generating it is not the check -- looking at it is.

    python3 contact_sheet.py <folder> <out.png> [glob]
"""
import os
import sys
import glob
from PIL import Image, ImageDraw, ImageFont

folder, out_path = sys.argv[1], sys.argv[2]
pattern = sys.argv[3] if len(sys.argv) > 3 else "*.png"
files = sorted(glob.glob(os.path.join(folder, pattern)))
if not files:
    sys.exit(f"no files matching {pattern!r} in {folder}")

COLS, TILE_W, PAD, LABEL_H = 3, 600, 18, 30
GREY = (128, 128, 128)

font = ImageFont.load_default()
for candidate in ("/Library/Fonts/Roboto/Roboto-Medium.ttf",
                  "/System/Library/Fonts/Supplemental/Arial.ttf"):
    try:
        font = ImageFont.truetype(candidate, 20)
        break
    except OSError:
        continue

thumbs = []
for f in files:
    im = Image.open(f).convert("RGBA")
    h = max(1, round(im.height * TILE_W / im.width))
    im = im.resize((TILE_W, h), Image.LANCZOS)
    plate = Image.new("RGB", (TILE_W, h), GREY)
    plate.paste(im, (0, 0), im)
    thumbs.append((os.path.basename(f)[:-4], plate))

rows = (len(thumbs) + COLS - 1) // COLS
row_h = [max(t[1].height for t in thumbs[r * COLS:(r + 1) * COLS]) + LABEL_H
         for r in range(rows)]
W = COLS * TILE_W + PAD * (COLS + 1)
H = sum(row_h) + PAD * (rows + 1)

sheet = Image.new("RGB", (W, H), (34, 34, 34))
d = ImageDraw.Draw(sheet)
y = PAD
for r in range(rows):
    x = PAD
    for c in range(COLS):
        i = r * COLS + c
        if i >= len(thumbs):
            break
        name, plate = thumbs[i]
        d.text((x, y), name, fill=(255, 255, 255), font=font)
        sheet.paste(plate, (x, y + LABEL_H))
        x += TILE_W + PAD
    y += row_h[r] + PAD
sheet.save(out_path)
print(f"{len(thumbs)} tiles -> {out_path} ({sheet.width}x{sheet.height})")
