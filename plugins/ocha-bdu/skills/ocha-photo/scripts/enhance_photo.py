"""Default photo enhancement for BDU social media graphics (prototype, 12 Oct 2026).

A conservative, repeatable edit for documentary photos: tone and colour only, never content.
Steps, in order:
  1. Levels: black and white points from luminance percentiles, applied equally to all channels
     (so the edit never introduces a colour cast).
  2. Gentle S-curve for contrast.
  3. Slight shadow lift, so faces in backlight or under headscarves open up.
  4. Vibrance: boosts muted colours more than already-saturated ones (protects skin and bright fabrics).
  5. Mild unsharp mask at full resolution.
The ICC profile and EXIF of the original are kept.

Usage: python3 enhance_photo.py <input.jpg> [<input2.jpg> ...] --out <folder>
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

# Strength settings. Keep them modest: these photos are evidence, not adverts.
BLACK_PCT, WHITE_PCT = 0.3, 99.7   # levels clipping, in percent of pixels
CONTRAST = 0.10                     # S-curve strength, 0 = none
SHADOW_LIFT = 0.06                  # 0 = none
VIBRANCE = 0.15                     # 0 = none
SHARPEN = dict(radius=1.2, percent=40, threshold=2)


def enhance(img: Image.Image) -> Image.Image:
    rgb = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0

    # 1. Levels on luminance, same mapping for R, G and B.
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    lo, hi = np.percentile(lum, [BLACK_PCT, WHITE_PCT])
    rgb = np.clip((rgb - lo) / max(hi - lo, 1e-3), 0, 1)

    # 2. S-curve: blend towards a smoothstep curve.
    smooth = rgb * rgb * (3 - 2 * rgb)
    rgb = rgb + CONTRAST * (smooth - rgb)

    # 3. Shadow lift: raise the darkest tones, fading out by the midtones.
    rgb = rgb + SHADOW_LIFT * (1 - rgb) ** 3 * rgb * 4

    # 4. Vibrance.
    mx, mn = rgb.max(axis=2, keepdims=True), rgb.min(axis=2, keepdims=True)
    sat = (mx - mn) / np.maximum(mx, 1e-3)
    mean = rgb.mean(axis=2, keepdims=True)
    rgb = mean + (rgb - mean) * (1 + VIBRANCE * (1 - sat))

    out = Image.fromarray((np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    # 5. Sharpen.
    return out.filter(ImageFilter.UnsharpMask(**SHARPEN))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    for p in map(Path, args.inputs):
        src = Image.open(p)
        result = enhance(src)
        kwargs = {"quality": 95, "subsampling": 0}
        if src.info.get("icc_profile"):
            kwargs["icc_profile"] = src.info["icc_profile"]
        if src.info.get("exif"):
            kwargs["exif"] = src.info["exif"]
        dest = out_dir / p.name
        result.save(dest, "JPEG", **kwargs)
        print(dest)


if __name__ == "__main__":
    main()
