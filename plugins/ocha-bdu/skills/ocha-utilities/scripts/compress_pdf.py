#!/usr/bin/env python3
"""Compress an image-heavy PDF (typically a Canva export) without visible loss.

Re-encodes every image as JPEG at full resolution and keeps each image's
colour space exactly as it was. See ../references/compress-pdf.md.

Usage:
    python3 compress_pdf.py input.pdf [output.pdf] [--quality 95] [--max-ppi N]

Output defaults to "<input>_compressed.pdf" next to the input. The original
is never changed. Needs PyMuPDF (fitz), Pillow and numpy.
"""
import argparse
import io
import os
import sys

import fitz  # PyMuPDF
import numpy as np
from PIL import Image


def compress(src, dst, quality=95, max_ppi=None):
    doc = fitz.open(src)
    done = set()
    for page in doc:
        for info in page.get_images(full=True):
            xref = info[0]
            if xref in done:
                continue
            done.add(xref)
            # Leave soft masks (transparency) and odd colour spaces untouched.
            if info[1] != 0:
                continue
            # RGB or grey only, untagged or ICC-tagged. The colour space entry
            # itself is never touched, so the tag (or its absence) stays as it was.
            # Indexed, CMYK and spot-colour images are left alone.
            cs_type, cs = doc.xref_get_key(xref, "ColorSpace")
            if cs_type == "xref":
                cs = doc.xref_object(int(cs.split()[0]), compressed=True)
            if not ("/DeviceRGB" in cs or "/DeviceGray" in cs or "/ICCBased" in cs):
                continue
            pix = fitz.Pixmap(doc, xref)
            if pix.alpha or pix.n not in (1, 3) or pix.n != pix.colorspace.n:
                continue
            mode = "RGB" if pix.n == 3 else "L"
            im = Image.frombytes(mode, (pix.width, pix.height), pix.samples)

            if max_ppi:
                # Shrink only if the image is shown denser than max_ppi.
                rects = page.get_image_rects(xref)
                if rects:
                    shown_in = max(r.width for r in rects) / 72
                    ppi = pix.width / shown_in
                    if ppi > max_ppi:
                        scale = max_ppi / ppi
                        im = im.resize((round(im.width * scale), round(im.height * scale)),
                                       Image.LANCZOS)

            buf = io.BytesIO()
            # subsampling=0 (4:4:4 chroma) keeps text and edges on photos crisp.
            im.save(buf, "JPEG", quality=quality, subsampling=0, optimize=True)
            data = buf.getvalue()
            if len(data) >= len(doc.xref_stream_raw(xref)):
                continue  # already smaller than our JPEG would be

            # Write the JPEG into the SAME image object and keep its original
            # colour space. Do NOT use page.replace_image(): it tags the image
            # with an sRGB ICC profile, and on wide-gamut Mac screens photos then
            # look visibly flatter than the original (untagged DeviceRGB).
            doc.update_stream(xref, data, compress=False)
            doc.xref_set_key(xref, "Filter", "/DCTDecode")
            doc.xref_set_key(xref, "DecodeParms", "null")
            doc.xref_set_key(xref, "Width", str(im.width))
            doc.xref_set_key(xref, "Height", str(im.height))
    doc.save(dst, garbage=4, deflate=True)


def check(src, dst):
    """Print size and a per-page similarity score (PSNR, dB) at 150 dpi."""
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
    if os.path.abspath(out) == os.path.abspath(a.input):
        sys.exit("Output must differ from input; the original is never overwritten.")
    compress(a.input, out, a.quality, a.max_ppi)
    check(a.input, out)
    print(out)


if __name__ == "__main__":
    main()
