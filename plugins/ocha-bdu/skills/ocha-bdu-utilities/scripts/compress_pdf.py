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
import zlib

import pikepdf
from pikepdf import Name, PdfImage
from PIL import Image, ImageChops, ImageFile, ImageStat

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


def _scan(stream_owner, resources, ctm, depth, found, page_w):
    """Track the current transformation matrix through a content stream and
    record, for each image drawn, the widest size it is shown at: in points,
    and as a share of its page's width."""
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
                _, pt, frac = found.get(key, (None, 0, 0))
                found[key] = (xo, max(width, pt), max(width / page_w if page_w else 0, frac))
            elif sub == Name.Form:
                m = tuple(float(v) for v in xo.get("/Matrix", [1, 0, 0, 1, 0, 0]))
                _scan(xo, xo.get("/Resources", resources), _mul(m, ctm), depth + 1, found, page_w)


def _images(pdf):
    """{objgen: (image, widest shown width in points, widest share of page width)}."""
    found = {}
    for page in pdf.pages:
        box = [float(v) for v in page.cropbox]
        _scan(page, page.obj.get("/Resources"), (1, 0, 0, 1, 0, 0), 0, found, abs(box[2] - box[0]))
    return found


def _shrunk_smask(sm, size):
    """An image's soft mask (its transparency) shrunk to the image's new size,
    as a greyscale picture, or None if the mask can't be read safely."""
    if "/Matte" in sm or int(sm.get("/BitsPerComponent", 0)) != 8:
        return None
    try:
        mask = PdfImage(sm).as_pil_image()
    except Exception:
        return None
    return mask.resize(size, Image.LANCZOS) if mask.mode == "L" else None


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


def compress(src, dst, quality=95, max_ppi=None, max_page_px=None, compare_page_px=None):
    """Write a compressed copy of src to dst. Returns one dict per image:
    {"old": bytes before, "new": bytes after or None if skipped, "db": PSNR}.

    max_ppi: shrink images shown denser than this many pixels per inch.
    max_page_px: shrink images to at most this many pixels across their
        page's width (2000 = a page shown 2000 px wide stays sharp). Unlike
        max_ppi it suits every page size: an A4 report and a square carousel
        both get enough pixels for the same screen.
    compare_page_px: fill "db", comparing each image before and after at the
        size it would have on a page shown this many pixels wide."""
    if os.path.abspath(src) == os.path.abspath(dst):
        raise ValueError("Output must differ from input; the original is never overwritten.")
    stats = []
    with pikepdf.open(src) as pdf:
        for img, shown_pt, page_frac in _images(pdf).values():
            old = len(img.read_raw_bytes())
            stat = {"old": old, "new": None, "db": None}
            stats.append(stat)
            # Images with a soft mask (transparency, common in Canva) are fine:
            # the mask stays a separate image. Hard masks and stencils are left
            # alone, because JPEG would break their exact colours.
            if "/Mask" in img or img.get("/ImageMask", False):
                continue
            smask = img.get("/SMask")
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
            if smask is not None and im.mode == mode + "A":
                # pikepdf applies the soft mask when decoding; keep only the
                # colour, as the mask stays in its own image.
                im = im.convert(mode)
            if im.mode != mode:
                continue
            im.info.pop("icc_profile", None)  # never embed a profile in the JPEG
            original = im

            # Shrink only if the image has more pixels than the target needs.
            targets = []
            if max_ppi and shown_pt:
                targets.append(max_ppi * shown_pt / 72)
            if max_page_px and page_frac:
                targets.append(max_page_px * page_frac)
            new_mask = None
            if targets and im.width > min(targets):
                scale = min(targets) / im.width
                size = (max(1, round(im.width * scale)), max(1, round(im.height * scale)))
                if smask is not None:
                    new_mask = _shrunk_smask(smask, size)
                if smask is None or new_mask is not None:  # else keep full size
                    im = im.resize(size, Image.LANCZOS)

            buf = io.BytesIO()
            # optimize=True needs the whole JPEG to fit Pillow's write buffer;
            # large detailed images otherwise fail with "Suspension not allowed here".
            ImageFile.MAXBLOCK = max(ImageFile.MAXBLOCK, im.width * im.height * len(im.mode))
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
            if new_mask is not None:
                # The mask shrinks with the image, so both stay the same size.
                smask.write(zlib.compress(new_mask.tobytes(), 9), filter=Name.FlateDecode)
                if "/DecodeParms" in smask:
                    del smask["/DecodeParms"]
                smask.Width, smask.Height = new_mask.size
            stat["new"] = len(data)
            if compare_page_px and page_frac:
                width = max(1, round(compare_page_px * page_frac))
                stat["db"] = _psnr(original, Image.open(io.BytesIO(data)), width)
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
    p.add_argument("--max-page-px", type=int, default=None,
                   help="shrink images to this many pixels across the page width "
                        "(e.g. 2000 for screens, any page size)")
    a = p.parse_args()
    out = a.output or os.path.splitext(a.input)[0] + "_compressed.pdf"
    try:
        compress(a.input, out, a.quality, a.max_ppi, a.max_page_px)
    except ValueError as e:
        sys.exit(str(e))
    check(a.input, out)
    print(out)


if __name__ == "__main__":
    main()
