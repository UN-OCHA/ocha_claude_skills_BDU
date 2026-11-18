#!/usr/bin/env python3
"""Compress an image-heavy PDF (typically a Canva export) without visible loss.

Re-encodes every image as JPEG at full resolution and keeps each image's
colour space exactly as it was. See ../references/compress-pdf.md.

Usage:
    python3 compress_pdf.py input.pdf [output.pdf] [--quality 95] [--max-ppi N]

Output defaults to "<input>_compressed.pdf" next to the input. The original
is never changed.

Compression needs pikepdf and Pillow only. The similarity check printed by the
command line (check()) also needs PyMuPDF (fitz) and numpy.

Why pikepdf and not PyMuPDF: in Microsoft 365 Copilot's sandbox, PyMuPDF is a
slow build that needs 35-48 s just to read ONE Canva page image, so a carousel
times out. pikepdf decodes the same image in 1.6 s (18 November 2026). This
script is also copied into the Copilot "Compress PDF" agent; keep compress()
free of fitz and numpy.
"""
import argparse
import io
import math
import os
import sys

import pikepdf
from pikepdf import Name, PdfImage
from PIL import Image, ImageChops, ImageStat

GOOD_COLOUR_SPACES = {"/DeviceRGB": 3, "/DeviceGray": 1}


def _components(cs):
    """Number of colour components for a colour space we can safely re-encode,
    or None. RGB or grey only, untagged or ICC-tagged. Indexed, CMYK, Lab and
    spot-colour images are left alone."""
    if isinstance(cs, Name):
        return GOOD_COLOUR_SPACES.get(str(cs))
    if isinstance(cs, pikepdf.Array) and len(cs) == 2 and cs[0] == Name.ICCBased:
        n = int(cs[1].get("/N", 0))
        return n if n in (1, 3) else None
    return None


def _mul(m, n):
    a, b, c, d, e, f = m
    a2, b2, c2, d2, e2, f2 = n
    return (a * a2 + b * c2, a * b2 + b * d2,
            c * a2 + d * c2, c * b2 + d * d2,
            e * a2 + f * c2 + e2, e * b2 + f * d2 + f2)


def _scan(stream_owner, resources, ctm, depth, found):
    """Track the current transformation matrix through a content stream and
    record, for each image drawn, the widest size it is shown at (points)."""
    if depth > 8 or resources is None:
        return
    xobjects = resources.get("/XObject", {})
    stack = []
    try:
        ops = pikepdf.parse_content_stream(stream_owner)
    except Exception:
        return
    for operands, op in ops:
        op = str(op)
        if op == "q":
            stack.append(ctm)
        elif op == "Q":
            ctm = stack.pop() if stack else ctm
        elif op == "cm" and len(operands) == 6:
            ctm = _mul(tuple(float(v) for v in operands), ctm)
        elif op == "Do" and operands:
            xo = xobjects.get(str(operands[0]))
            if xo is None:
                continue
            sub = xo.get("/Subtype")
            if sub == Name.Image:
                width = math.hypot(ctm[0], ctm[1])  # unit square scaled by the CTM
                key = xo.objgen
                found[key] = (xo, max(width, found.get(key, (None, 0))[1]))
            elif sub == Name.Form:
                m = tuple(float(v) for v in xo.get("/Matrix", [1, 0, 0, 1, 0, 0]))
                _scan(xo, xo.get("/Resources", resources), _mul(m, ctm), depth + 1, found)


def _images(pdf):
    """{objgen: (image object, widest shown width in points)} for the whole PDF."""
    found = {}
    for page in pdf.pages:
        _scan(page, page.obj.get("/Resources"), (1, 0, 0, 1, 0, 0), 0, found)
    return found


def _psnr(a, b, width):
    """Similarity (PSNR, dB) of two images, both scaled to `width` pixels wide."""
    if a.size != b.size:
        b = b.resize(a.size, Image.LANCZOS)
    if width and a.width > width:
        size = (width, round(a.height * width / a.width))
        a, b = a.resize(size, Image.LANCZOS), b.resize(size, Image.LANCZOS)
    rms = ImageStat.Stat(ImageChops.difference(a, b)).rms
    mse = sum(v * v for v in rms) / len(rms)
    return 99.0 if mse == 0 else 10 * math.log10(255 ** 2 / mse)


def compress(src, dst, quality=95, max_ppi=None, compare_width=None):
    """Write a compressed copy of src to dst. Returns one dict per image:
    {"old": bytes before, "new": bytes after or None if skipped, "db": PSNR}.
    "db" is only filled when compare_width is given (pixels)."""
    if os.path.abspath(src) == os.path.abspath(dst):
        raise ValueError("Output must differ from input; the original is never overwritten.")
    stats = []
    with pikepdf.open(src) as pdf:
        for img, shown_pt in _images(pdf).values():
            old = len(img.read_raw_bytes())
            stat = {"old": old, "new": None, "db": None}
            stats.append(stat)
            # Leave transparency, masks and unusual images untouched.
            if "/SMask" in img or "/Mask" in img or img.get("/ImageMask", False):
                continue
            if "/Decode" in img or int(img.get("/BitsPerComponent", 0)) != 8:
                continue
            n = _components(img.get("/ColorSpace"))
            if n is None:
                continue
            try:
                im = PdfImage(img).as_pil_image()
            except Exception:
                continue
            mode = "RGB" if n == 3 else "L"
            if im.mode != mode:
                continue
            im.info.pop("icc_profile", None)  # never embed a profile in the JPEG
            original = im

            if max_ppi and shown_pt:
                # Shrink only if the image is shown denser than max_ppi.
                ppi = im.width / (shown_pt / 72)
                if ppi > max_ppi:
                    scale = max_ppi / ppi
                    im = im.resize((round(im.width * scale), round(im.height * scale)),
                                   Image.LANCZOS)

            buf = io.BytesIO()
            # subsampling=0 (4:4:4 chroma) keeps text and edges on photos crisp.
            im.save(buf, "JPEG", quality=quality, subsampling=0, optimize=True)
            data = buf.getvalue()
            if len(data) >= old:
                continue  # already smaller than our JPEG would be

            # Write the JPEG into the SAME image object and keep its original
            # colour space entry. Never tag it sRGB: on wide-gamut Mac screens
            # photos then look visibly flatter than the original (untagged
            # DeviceRGB, as Canva exports them).
            img.write(data, filter=Name.DCTDecode)
            if "/DecodeParms" in img:
                del img["/DecodeParms"]
            img.Width, img.Height = im.width, im.height
            stat["new"] = len(data)
            if compare_width:
                stat["db"] = _psnr(original, Image.open(io.BytesIO(data)), compare_width)
        pdf.save(dst, compress_streams=True,
                 object_stream_mode=pikepdf.ObjectStreamMode.generate)
    return stats


def check(src, dst):
    """Print size and a per-page similarity score (PSNR, dB) at 150 dpi.
    Needs PyMuPDF and numpy (local use only)."""
    import fitz
    import numpy as np
    a, b = fitz.open(src), fitz.open(dst)
    print(f"{os.path.getsize(src)/1e6:.1f} MB -> {os.path.getsize(dst)/1e6:.1f} MB")
    for i in range(len(a)):
        x = np.frombuffer(a[i].get_pixmap(dpi=150).samples, np.uint8).astype(float)
        y = np.frombuffer(b[i].get_pixmap(dpi=150).samples, np.uint8).astype(float)
        mse = ((x - y) ** 2).mean() if x.shape == y.shape else None
        score = "same size check skipped" if mse is None else (
            "identical" if mse == 0 else f"{10*np.log10(255**2/mse):.1f} dB")
        print(f"  page {i+1}: {score}")


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("input")
    p.add_argument("output", nargs="?")
    p.add_argument("--quality", type=int, default=95)
    p.add_argument("--max-ppi", type=int, default=None,
                   help="shrink images shown denser than this (e.g. 150 for screen only)")
    a = p.parse_args()
    out = a.output or os.path.splitext(a.input)[0] + "_compressed.pdf"
    try:
        compress(a.input, out, a.quality, a.max_ppi)
    except ValueError as e:
        sys.exit(str(e))
    check(a.input, out)
    print(out)


if __name__ == "__main__":
    main()
