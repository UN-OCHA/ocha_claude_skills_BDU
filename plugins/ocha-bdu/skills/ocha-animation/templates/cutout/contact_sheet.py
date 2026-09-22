#!/usr/bin/env python3
"""Storyboard contact sheet for approval: every still on one page, labelled with its moment.

    node --experimental-websocket assets/build/stills.mjs       # one still per named moment (FILM.KEYS)
    python3 assets/build/contact_sheet.py
Reads  assets/build/stills/*.png
Writes info/<name>_storyboard.png (name from film.json)

Stills are exact frames of the film (the page at ?t=), so what is approved is what will render.
LABELS names a still by its key (FILM.KEYS in scenes.js); otherwise its key shows.
"""
import json, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FILM = json.loads((HERE / "film.json").read_text(encoding="utf-8"))
OUT = HERE.parents[1] / f"info/{FILM['name']}_storyboard.png"
LABELS = {   # key → what the still shows (the demo's)
    "a": "1 · A crisis, and its questions",
    "b": "2 · The data answers them",
    "c": "2 · For everyone to see",
}
COLS, TW, GAP, PAD, LABEL_H = 3, 640, 28, 56, 70
TH = TW * 9 // 16


def font(weight, size):
    """Roboto, OCHA's font, when installed; the default face otherwise (the sheet still works)."""
    for f in (f"/Library/Fonts/Roboto/Roboto-{weight}.ttf", f"/Library/Fonts/Roboto-{weight}.ttf",
              str(Path.home() / f"Library/Fonts/Roboto-{weight}.ttf")):
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default(size)


f_title, f_label, f_time = font("Black", 40), font("Medium", 24), font("Regular", 20)
stills = sorted((HERE / "stills").glob("*.png"))
if not stills:
    raise SystemExit("No stills in assets/build/stills: run stills.mjs first.")
rows = -(-len(stills) // COLS)
W = PAD * 2 + COLS * TW + (COLS - 1) * GAP
H = PAD + 90 + rows * (TH + LABEL_H + GAP)
sheet = Image.new("RGB", (W, H), "#FFFFFF")
d = ImageDraw.Draw(sheet)
d.text((PAD, PAD - 8), f"{FILM['title']} · storyboard", font=f_title, fill="#1B1B1A")
d.text((PAD, PAD + 44), "Exact frames of the film. One continuous world: everything floats and pops in; "
       "the words appear as they are spoken.", font=f_time, fill="#6E6259")
for i, p in enumerate(stills):
    m = re.match(r"\d+_(.+)_t([\d.]+)\.png$", p.name)
    key, t = (m.group(1), float(m.group(2))) if m else (p.stem, 0.0)
    x = PAD + (i % COLS) * (TW + GAP)
    y = PAD + 90 + (i // COLS) * (TH + LABEL_H + GAP)
    sheet.paste(Image.open(p).convert("RGB").resize((TW, TH), Image.LANCZOS), (x, y))
    d.rectangle([x, y, x + TW - 1, y + TH - 1], outline="#DDDAD7")
    d.text((x, y + TH + 12), LABELS.get(key, key), font=f_label, fill="#1B1B1A")
    d.text((x, y + TH + 42), f"{int(t // 60)}:{t % 60:04.1f}", font=f_time, fill="#6E6259")
OUT.parent.mkdir(parents=True, exist_ok=True)
sheet.save(OUT, optimize=True)
print(f"{OUT.relative_to(HERE.parents[1])} · {W}x{H} · {len(stills)} stills")
