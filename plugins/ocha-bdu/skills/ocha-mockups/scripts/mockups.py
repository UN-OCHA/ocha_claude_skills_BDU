#!/usr/bin/env python3
"""OCHA mockups engine: put a design into a Photoshop mockup template. No Photoshop needed.

The template's own layers are composited by psd-tools' rendering engine (blend modes,
opacity, masks, clipping, layer effects, adjustment layers). The only thing changed is
what the template's smart object shows: its pixels are swapped for the design, warped
to the smart object's placement (flat or in perspective).

Commands
  ready    [KEY ...]             are the templates on this computer? (asks for 'Make available offline')
  templates                      list the catalogued templates and their status
  inspect  TEMPLATE              show the template's design slots (smart objects), sizes and warnings
  check    TEMPLATE              how faithfully this engine renders the template (vs Photoshop's preview)
  render   TEMPLATE --design ... make mockups: PNG/JPG for one, or one PDF with a page per design
  selftest                       render every catalogued template with a test card and check it
  setup    --folder PATH         remember where the templates folder is (only if not auto-found)

TEMPLATE is a catalogue key (see `templates`) or a path to any .psd, .psdt or .psb file.

Exit codes: 0 done, 2 a problem to fix (message says what), 3 templates are online-only in
Dropbox: ask the person to make them available offline, wait, then run again.

Needs: python3 with psd-tools[composite], numpy, Pillow, PyMuPDF
       (python3 -m pip install "psd-tools[composite]" pymupdf)
"""
import argparse
import glob
import io
import json
import os
import re
import sys
import warnings
from dataclasses import dataclass, field

import numpy as np
from PIL import Image, ImageCms, ImageDraw, ImageFont, ImageOps

warnings.filterwarnings("ignore")          # psd-tools is chatty about deprecated properties
Image.MAX_IMAGE_PIXELS = None               # mockup canvases are legitimately huge

HERE = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.join(HERE, "templates.json")
CONFIG = os.path.join(os.path.expanduser("~"), ".claude", "ocha-mockups.json")
ENV_FOLDER = "OCHA_MOCKUPS_FOLDER"
# The curated templates sit in the BDU skills folder in the OCHA DMU Dropbox. That folder is
# also the public GitHub repo, and mockups/ is git-ignored there: the PSDs are licensed.
FOLDER_TAIL = os.path.join("Design", "Resources", "ocha_claude_skills_BDU", "mockups")


class MockupError(Exception):
    """A problem the person can act on. Printed without a traceback (exit code 2)."""
    code = 2


class OnlineOnly(MockupError):
    """Template files exist but Dropbox keeps them in the cloud only (exit code 3)."""
    code = 3


# ---------------------------------------------------------------------------------------
# Finding the templates folder and the template file
# ---------------------------------------------------------------------------------------

def _config():
    try:
        with open(CONFIG, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def folder_candidates(explicit=None):
    """Where the templates folder may be, in priority order: flag, env var, setting, auto."""
    out = []
    if explicit:
        out.append(("--folder", explicit))
    if os.environ.get(ENV_FOLDER):
        out.append((ENV_FOLDER, os.environ[ENV_FOLDER]))
    if _config().get("folder"):
        out.append((CONFIG, _config()["folder"]))
    home = os.path.expanduser("~")
    # The OCHA DMU team Dropbox shows each member's own name as the second folder, so the
    # same shared Design folder sits at a different path on every computer. Glob, never
    # hardcode a name. Newer Macs keep Dropbox under ~/Library/CloudStorage.
    patterns = [
        os.path.join(home, "OCHA DMU Dropbox", "*", FOLDER_TAIL),
        os.path.join(home, "Library", "CloudStorage", "*", "*", FOLDER_TAIL),
        os.path.join(home, "Library", "CloudStorage", "*", FOLDER_TAIL),
        os.path.join(home, "Dropbox*", "*", FOLDER_TAIL),
    ]
    for pat in patterns:
        for p in sorted(glob.glob(pat)):
            out.append(("auto-detect", p))
    return out


def find_folder(explicit=None, required=True):
    tried = []
    for source, path in folder_candidates(explicit):
        path = os.path.expanduser(path)
        if os.path.isdir(path):
            return path
        if source != "auto-detect":
            # A place someone chose on purpose must not be silently replaced by a guess.
            how = {"--folder": "the --folder given", ENV_FOLDER: f"the {ENV_FOLDER} environment variable",
                   CONFIG: f"the saved setting in {CONFIG}"}[source]
            raise MockupError(f"The mockup templates folder set by {how} does not exist:\n  {path}\n"
                              "Fix that setting (python3 mockups.py setup --folder \"/path/to/mockups\"), "
                              "or remove it to use the standard Dropbox location.")
        tried.append(f"  {source}: {path}  (not found)")
    if not required:
        return None
    raise MockupError(
        "Can't find the OCHA mockup templates folder in Dropbox.\n"
        "It normally lives at  ~/OCHA DMU Dropbox/<your-name>/Design/Resources/ocha_claude_skills_BDU/mockups\n"
        + ("Tried:\n" + "\n".join(tried) + "\n" if tried else "")
        + "Fix it one of these ways:\n"
        "  - Make sure the OCHA DMU Dropbox is syncing on this computer and you can see that\n"
        "    folder. If you can't, ask ochavisual@un.org for access.\n"
        "  - If it is somewhere else on this computer, remember that place once:\n"
        "      python3 mockups.py setup --folder \"/path/to/mockups\"\n"
        f"  - Or set the {ENV_FOLDER} environment variable to that folder."
    )


def load_catalog():
    with open(CATALOG, encoding="utf-8") as f:
        return json.load(f)


def online_only(path):
    """True when Dropbox keeps the file in the cloud only (nothing to read on disk yet)."""
    st = os.stat(path)
    SF_DATALESS = 0x40000000                 # macOS File Provider placeholder
    if getattr(st, "st_flags", 0) & SF_DATALESS:
        return True
    # Classic Dropbox Smart Sync placeholders read as 0 bytes (and carry a
    # com.dropbox.placeholder attribute). No real PSD is empty.
    return st.st_size == 0


def offline_ask(folders):
    """What to tell the person when templates are online-only. Plain words, no jargon."""
    folders = sorted(set(folders))
    where = "\n".join(f"  {f}" for f in folders)
    return ("ASK THE PERSON: the mockup template is only in the cloud (Dropbox 'online-only'), so\n"
            "it can't be opened yet. Please, in Finder:\n"
            f"  1. Go to this folder:\n{where}\n"
            "  2. Right-click it and choose 'Make available offline'.\n"
            "  3. Wait for the green tick next to it (big templates take a few minutes).\n"
            "  4. Tell me when it's done, and I'll carry on.")


def resolve_template(ref, folder=None):
    """Catalogue key or file path -> (absolute path, catalogue entry or None)."""
    entry = None
    if os.path.splitext(ref)[1].lower() in (".psd", ".psdt", ".psb"):
        path = os.path.abspath(os.path.expanduser(ref))
    else:
        cat = load_catalog()["templates"]
        if ref not in cat:
            close = [k for k in cat if ref.lower() in k or k in ref.lower()]
            raise MockupError(f"No template called '{ref}'."
                              + (f" Did you mean: {', '.join(close)}?" if close else "")
                              + " Run `mockups.py templates` for the list, or pass a .psd path.")
        entry = dict(cat[ref], key=ref)
        path = os.path.join(find_folder(folder), entry["path"])
    if not os.path.exists(path):
        raise MockupError(f"Template file not found: {path}\n"
                          "If Dropbox is still syncing, wait a minute and try again.")
    if online_only(path):
        raise OnlineOnly(offline_ask([os.path.dirname(path)]))
    return path, entry


# ---------------------------------------------------------------------------------------
# Reading the template: smart objects grouped into slots
# ---------------------------------------------------------------------------------------

DESIGN_WORDS = re.compile(r"edit|your|design|cover|artwork|replace|screen|page|place|here|image|"
                          r"front|back|left|right|spread|insert|logo|poster|flyer|card",
                          re.IGNORECASE)
BACKGROUND_WORDS = re.compile(r"background|\bbg\b|backdrop|texture|noise|grain|surface|floor|"
                              r"table|wall|wood|concrete|light|shadow|perspective bg|edge|stack",
                              re.IGNORECASE)


@dataclass
class Instance:
    layer: object
    quad: np.ndarray            # 4x2 corners in canvas pixels: TL, TR, BR, BL of the content
    content: tuple              # (width, height) of the smart object's content, its own pixels
    renders: bool               # visible and not fully transparent, parents included
    warp: str                   # Photoshop warp style: 'warpNone', or 'warpCustom' (mesh below)
    smart_filters: bool
    mesh: np.ndarray = None     # 4x4x2 Bezier control points of a custom warp (row = v, col = u)

    @property
    def area(self):
        x, y = self.quad[:, 0], self.quad[:, 1]
        return 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

    @property
    def flat(self):
        """Axis-aligned rectangle (no perspective, rotation or skew)."""
        q = self.quad
        return (abs(q[0, 1] - q[1, 1]) < 1 and abs(q[3, 1] - q[2, 1]) < 1
                and abs(q[0, 0] - q[3, 0]) < 1 and abs(q[1, 0] - q[2, 0]) < 1)


@dataclass
class Slot:
    key: str
    name: str
    instances: list = field(default_factory=list)
    role: str = "design"        # 'design' gets the person's design; 'background' is left alone
    area: tuple = None          # (x0, y0, x1, y1) part of the content the design fills, content px
    number: int = 0

    @property
    def active(self):
        return any(i.renders for i in self.instances)

    @property
    def main(self):
        """The largest instance that actually renders: it decides size and label position."""
        live = [i for i in self.instances if i.renders] or self.instances
        return max(live, key=lambda i: i.area)

    @property
    def aspect(self):
        x0, y0, x1, y1 = self.area
        return (x1 - x0) / (y1 - y0)


def _walk(group):
    for layer in group:
        yield layer
        if layer.is_group():
            yield from _walk(layer)


def _renders(layer):
    node = layer
    while node is not None and hasattr(node, "opacity"):
        if not node.visible or node.opacity == 0:
            return False
        node = node.parent
    return True


def _placed(layer):
    blocks = layer.tagged_blocks
    for key in (b"SoLd", b"SoLE"):
        data = blocks.get_data(key)
        if data is not None:
            return data.data
    return None


def read_slots(psd, entry=None):
    """Smart objects grouped by linked content. `entry` (a catalogue entry) may name the
    design slots explicitly, which beats the name-based guess."""
    slots = {}
    for layer in _walk(psd):
        if layer.kind != "smartobject":
            continue
        pl = _placed(layer)
        if pl is None:
            continue
        # nonAffineTransform holds the real corners once a perspective or distort is applied;
        # Trnf alone is only the affine part.
        corners = pl.get(b"nonAffineTransform") or pl.get(b"Trnf")
        size = pl.get(b"Sz  ")
        if corners is None or size is None:
            continue
        warp = pl.get(b"warp")
        style = warp[b"warpStyle"].enum.decode() if warp is not None and b"warpStyle" in warp else "warpNone"
        mesh = _read_mesh(warp) if style == "warpCustom" else None
        if style == "warpCustom" and mesh is None:
            style = "warpUnreadable"
        elif style == "warpCustom":
            style = "warpNone" if _mesh_is_flat(mesh) else "warpCustom"
            mesh = None if style == "warpNone" else mesh
        inst = Instance(
            layer=layer,
            quad=np.array(list(corners), dtype=np.float64).reshape(4, 2),
            content=(float(size[b"Wdth"]), float(size[b"Hght"])),
            renders=_renders(layer),
            warp=style,
            smart_filters=b"filterFX" in pl,
            mesh=mesh,
        )
        key = str(pl.get(b"Idnt") or id(layer))      # same Idnt = same linked content
        slot = slots.setdefault(key, Slot(key=key, name=layer.name))
        slot.instances.append(inst)

    canvas = psd.width * psd.height
    for slot in slots.values():
        names = [i.layer.name for i in slot.instances]
        # Name the slot after the instance a designer is told to edit, if there is one.
        slot.name = next((n for n in names if re.search(r"edit|your|replace|here", n, re.I)), names[0])
        designish = any(DESIGN_WORDS.search(n) for n in names)
        bgish = any(BACKGROUND_WORDS.search(n) for n in names)
        if (bgish and not re.search(r"edit|your|design|cover|artwork|screen", " ".join(names), re.I)) \
                or (not designish and slot.main.area > 0.9 * canvas):
            slot.role = "background"
        w, h = slot.main.content
        slot.area = (0.0, 0.0, w, h)
    if entry and entry.get("design_slots"):
        chosen = set(entry["design_slots"])
        for slot in slots.values():
            hit = any(i.layer.name in chosen for i in slot.instances)
            slot.role = "design" if hit else "background"

    ordered = sorted((s for s in slots.values()),
                     key=lambda s: (not s.active, s.role != "design",
                                    round(s.main.quad[:, 0].mean() / 50), s.main.quad[:, 1].mean()))
    for n, s in enumerate(ordered, 1):
        s.number = n
    return ordered


def _read_mesh(warp):
    """The 4x4 Bezier mesh of a Photoshop custom warp, or None if it is not one we know.

    Photoshop keeps the 16 control points as two flat lists (x then y), row by row from the
    top. They live in their own coordinate space; the smart object's four corners then place
    the BOUNDING BOX OF THE CONTROL POINTS on the canvas (checked against Photoshop's own
    pixels: 99.8-99.95% overlap on flat, curled and perspective pages).
    """
    try:
        if int(warp.get(b"uOrder", 4)) != 4 or int(warp.get(b"vOrder", 4)) != 4:
            return None
        env = warp[b"customEnvelopeWarp"]
        if b"quiltSliceX" in env or b"quiltSliceY" in env:
            return None                     # split warps: not used by any template we have
        mp = env[b"meshPoints"]
        xs = np.array([float(v) for v in mp[b"Hrzn"].values], dtype=np.float64)
        ys = np.array([float(v) for v in mp[b"Vrtc"].values], dtype=np.float64)
        if xs.size != 16 or ys.size != 16:
            return None
        return np.stack([xs.reshape(4, 4), ys.reshape(4, 4)], axis=-1)
    except Exception:
        return None


def _mesh_is_flat(mesh):
    """A mesh whose control points sit on an even grid bends nothing."""
    x0, y0 = mesh.reshape(-1, 2).min(axis=0)
    x1, y1 = mesh.reshape(-1, 2).max(axis=0)
    t = np.array([0, 1 / 3, 2 / 3, 1])
    grid = np.stack(np.meshgrid(x0 + t * (x1 - x0), y0 + t * (y1 - y0)), axis=-1)
    return np.abs(mesh - grid).max() < 0.002 * max(x1 - x0, y1 - y0)


def _bernstein(t):
    t = np.asarray(t, dtype=np.float64)[..., None]
    return np.concatenate([(1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t ** 2 * (1 - t), t ** 3], axis=-1)


def mapper(inst):
    """f(u, v) -> canvas xy, for u, v in [0, 1] across the smart object's content."""
    unit = [(0, 0), (1, 0), (1, 1), (0, 1)]
    if inst.mesh is None:
        H = homography(unit, inst.quad)
        return lambda u, v: apply_h(H, np.stack([np.ravel(u), np.ravel(v)], axis=-1))
    P = inst.mesh
    x0, y0 = P.reshape(-1, 2).min(axis=0)
    x1, y1 = P.reshape(-1, 2).max(axis=0)
    H = homography([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], inst.quad)

    def f(u, v):
        pts = np.einsum("ni,nj,jik->nk", _bernstein(np.ravel(u)), _bernstein(np.ravel(v)), P)
        return apply_h(H, pts)
    return f


def design_slots(slots):
    return [s for s in slots if s.active and s.role == "design"]


# ---------------------------------------------------------------------------------------
# Geometry: content rectangle -> canvas quad
# ---------------------------------------------------------------------------------------

def homography(src, dst):
    """3x3 matrix mapping the 4 src points onto the 4 dst points."""
    a, b = [], []
    for (x, y), (u, v) in zip(src, dst):
        a.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        a.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    h = np.linalg.solve(np.array(a, dtype=np.float64), np.array(b, dtype=np.float64))
    return np.append(h, 1).reshape(3, 3)


def apply_h(h, pts):
    pts = np.asarray(pts, dtype=np.float64)
    p = np.c_[pts, np.ones(len(pts))] @ h.T
    return p[:, :2] / p[:, 2:3]


def area_quad(inst, area):
    """Canvas corners of a sub-rectangle (content px) of an instance's content."""
    w, h = inst.content
    x0, y0, x1, y1 = area
    return mapper(inst)(np.array([x0, x1, x1, x0]) / w, np.array([y0, y0, y1, y1]) / h)


def detect_area(inst):
    """Which part of the smart object's content the design should fill.

    Most templates want the whole content. Some (e.g. a4_simple_mockup) embed a scene-
    sized artboard with the page in the middle: there the layer's own pixels cover only
    part of the content. Back-project those pixels into content space and take their box.
    """
    w, h = inst.content
    full = (0.0, 0.0, w, h)
    layer = inst.layer
    if layer.width == 0 or layer.height == 0 or inst.mesh is not None:
        return full
    shape = layer.numpy("shape")
    if shape is None:
        return full
    scale = min(1.0, 600 / max(w, h))
    ow, oh = max(1, round(w * scale)), max(1, round(h * scale))
    # Map output (content space, scaled) -> layer pixel space.
    H = homography([(0, 0), (ow, 0), (ow, oh), (0, oh)], inst.quad - [layer.left, layer.top])
    alpha = Image.fromarray((shape[..., 0] * 255).astype(np.uint8), "L")
    back = np.asarray(alpha.transform((ow, oh), Image.PERSPECTIVE, _pil_coeffs(H), Image.BILINEAR))
    ys, xs = np.nonzero(back > 128)
    if len(xs) == 0:
        return full
    box = (xs.min() / scale, ys.min() / scale, (xs.max() + 1) / scale, (ys.max() + 1) / scale)
    if (box[2] - box[0]) > 0.95 * w and (box[3] - box[1]) > 0.95 * h:
        return full
    # Only a solid page-shaped block counts. A sample design that is partly transparent
    # (text on nothing) must not shrink the area: then the design fills the whole object.
    solid = (back[ys.min():ys.max() + 1, xs.min():xs.max() + 1] > 128).mean()
    if solid < 0.97:
        return full
    return tuple(float(v) for v in box)


def _pil_coeffs(h):
    """PIL's PERSPECTIVE wants the 8 coefficients of the output->input mapping, normalised."""
    h = h / h[2, 2]
    return tuple(h.flatten()[:8])


# ---------------------------------------------------------------------------------------
# Loading designs
# ---------------------------------------------------------------------------------------

def parse_design(spec):
    """'file.pdf#3' -> ('file.pdf', 3). Pages count from 1."""
    m = re.match(r"^(.*?)(?:#(\d+))?$", spec)
    path, page = m.group(1), int(m.group(2) or 1)
    path = os.path.abspath(os.path.expanduser(path))
    if not os.path.exists(path):
        raise MockupError(f"Design file not found: {path}")
    if online_only(path):
        raise OnlineOnly(offline_ask([os.path.dirname(path)]).replace(
            "the mockup template is only", "the design file is only"))
    return path, page


def pdf_page_count(path):
    import fitz
    with fitz.open(path) as doc:
        return doc.page_count


def pdf_page_aspect(path, page, bleed=False):
    import fitz
    with fitz.open(path) as doc:
        p = doc[page - 1]
        r = p.rect if bleed else p.trimbox
        return r.width / r.height


def design_aspect(path, page, bleed=False):
    if path.lower().endswith(".pdf"):
        return pdf_page_aspect(path, page, bleed)
    with Image.open(path) as im:
        w, h = ImageOps.exif_transpose(im).size
    return w / h


def load_design(path, page, longest, bleed=False):
    """The design as an RGBA image whose longest side is about `longest` pixels."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        import fitz
        with fitz.open(path) as doc:
            if page > doc.page_count:
                raise MockupError(f"{os.path.basename(path)} has {doc.page_count} pages; page {page} asked.")
            p = doc[page - 1]
            # Exports from InDesign often carry bleed: show the trimmed page, as printed.
            clip = p.rect if bleed else p.trimbox
            zoom = longest / max(clip.width, clip.height)
            pix = p.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip, alpha=False)
            return Image.frombytes("RGB", (pix.width, pix.height), pix.samples).convert("RGBA")
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    icc = im.info.get("icc_profile")
    if icc and im.mode in ("RGB", "RGBA", "CMYK"):
        # Bring photos in AdobeRGB, or CMYK exports, to sRGB with their own profile.
        try:
            src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            alpha = im.getchannel("A") if im.mode == "RGBA" else None
            im = ImageCms.profileToProfile(im.convert("RGB") if im.mode == "RGBA" else im, src,
                                           ImageCms.createProfile("sRGB"), outputMode="RGB")
            if alpha is not None:
                im.putalpha(alpha)
        except Exception:
            pass
    return im.convert("RGBA")


def fit_design(img, aspect, mode, focus):
    """Make the design match the slot's aspect. Returns (image, note or None)."""
    w, h = img.size
    a = w / h
    diff = a / aspect - 1
    if mode == "auto":
        mode = "stretch" if abs(diff) <= 0.02 else "fill"
    if mode == "stretch" or abs(diff) < 1e-4:
        note = None if abs(diff) <= 0.02 else f"stretched {abs(diff):.0%} to fit"
        return img.resize((w, round(w / aspect)) if a < aspect else (round(h * aspect), h), Image.LANCZOS), note
    fx, fy = focus
    if mode == "fill":
        if a > aspect:                       # too wide: crop the sides
            nw = round(h * aspect)
            left = min(max(round(fx * w - nw / 2), 0), w - nw)
            out = img.crop((left, 0, left + nw, h))
            lost = 1 - nw / w
        else:                                # too tall: crop top and bottom
            nh = round(w / aspect)
            top = min(max(round(fy * h - nh / 2), 0), h - nh)
            out = img.crop((0, top, w, top + nh))
            lost = 1 - nh / h
        return out, f"cropped {lost:.0%} of the design to fill the slot (aspect {a:.3f} vs {aspect:.3f})"
    # fit: letterbox on white paper
    if a > aspect:
        canvas = Image.new("RGBA", (w, round(w / aspect)), (255, 255, 255, 255))
        canvas.paste(img, (0, (canvas.height - h) // 2), img)
    else:
        canvas = Image.new("RGBA", (round(h * aspect), h), (255, 255, 255, 255))
        canvas.paste(img, ((canvas.width - w) // 2, 0), img)
    return canvas, f"fitted inside the slot with white margins (aspect {a:.3f} vs {aspect:.3f})"


# ---------------------------------------------------------------------------------------
# Swapping a smart object's pixels
# ---------------------------------------------------------------------------------------

def warp_into(design, inst, area):
    """Place an RGBA design on an instance's area. Returns (bbox, color, shape) as floats.

    Flat and perspective placements are one exact projective transform. A custom warp is
    drawn as a fine grid of small projective pieces following the Bezier mesh.
    """
    if inst.mesh is not None:
        return _warp_mesh(design, inst, area)
    quad = area_quad(inst, area)
    x0, y0 = np.floor(quad.min(axis=0)).astype(int)
    x1, y1 = np.ceil(quad.max(axis=0)).astype(int)
    bw, bh = x1 - x0, y1 - y0
    # Supersample 2x for clean, anti-aliased edges, unless that would be very large.
    ss = 2 if bw * bh * 4 <= 60e6 else 1
    dw, dh = design.size
    pad = 2
    # Replicate the edge pixels outward, so partly covered edge pixels keep the design's
    # own colour instead of fading to black.
    rgb = np.asarray(design.convert("RGB"))
    rgb = Image.fromarray(np.pad(rgb, ((pad, pad), (pad, pad), (0, 0)), mode="edge"))
    alpha = Image.fromarray(np.pad(np.asarray(design.getchannel("A")), pad, constant_values=0))
    src = [(pad, pad), (pad + dw, pad), (pad + dw, pad + dh), (pad, pad + dh)]
    dst = (quad - [x0, y0]) * ss
    H = homography(dst, src)                  # output pixel -> design pixel
    size = (bw * ss, bh * ss)
    col = rgb.transform(size, Image.PERSPECTIVE, _pil_coeffs(H), Image.BICUBIC)
    shp = alpha.transform(size, Image.PERSPECTIVE, _pil_coeffs(H), Image.BILINEAR)
    if ss > 1:
        col = col.reduce(ss)
        shp = shp.reduce(ss)
    return (int(x0), int(y0), int(x0 + col.width), int(y0 + col.height)), \
        np.asarray(col, dtype=np.float32) / 255, np.asarray(shp, dtype=np.float32)[..., None] / 255


def _warp_mesh(design, inst, area):
    w, h = inst.content
    ax0, ay0, ax1, ay1 = area
    f = mapper(inst)
    corners = area_quad(inst, area)
    side = max(np.linalg.norm(corners[1] - corners[0]), np.linalg.norm(corners[3] - corners[0]))
    n = int(np.clip(side / 40, 8, 48))       # cells per side: about 40 px each, 8 to 48
    t = np.linspace(0, 1, n + 1)
    uu, vv = np.meshgrid(ax0 / w + t * (ax1 - ax0) / w, ay0 / h + t * (ay1 - ay0) / h)
    G = f(uu, vv).reshape(n + 1, n + 1, 2)   # G[row, col] = canvas point
    x0, y0 = np.floor(G.reshape(-1, 2).min(axis=0)).astype(int) - 1
    x1, y1 = np.ceil(G.reshape(-1, 2).max(axis=0)).astype(int) + 1
    bw, bh = x1 - x0, y1 - y0
    ss = 2 if bw * bh * 4 <= 60e6 else 1
    dw, dh = design.size
    pad = 2
    rgb = Image.fromarray(np.pad(np.asarray(design.convert("RGB")), ((pad, pad), (pad, pad), (0, 0)), mode="edge"))
    alpha = Image.fromarray(np.pad(np.asarray(design.getchannel("A")), pad, constant_values=0))
    col = Image.new("RGB", (bw * ss, bh * ss))
    shp = Image.new("L", (bw * ss, bh * ss))
    D = (G - [x0, y0]) * ss
    for j in range(n):
        for i in range(n):
            dst = np.array([D[j, i], D[j, i + 1], D[j + 1, i + 1], D[j + 1, i]])
            src = [(pad + dw * i / n, pad + dh * j / n), (pad + dw * (i + 1) / n, pad + dh * j / n),
                   (pad + dw * (i + 1) / n, pad + dh * (j + 1) / n), (pad + dw * i / n, pad + dh * (j + 1) / n)]
            cx0, cy0 = np.floor(dst.min(axis=0)).astype(int)
            cx1, cy1 = np.ceil(dst.max(axis=0)).astype(int) + 1
            size = (int(cx1 - cx0), int(cy1 - cy0))
            try:
                H = homography(dst - [cx0, cy0], src)
            except np.linalg.LinAlgError:
                continue                     # a cell folded to nothing
            piece = rgb.transform(size, Image.PERSPECTIVE, _pil_coeffs(H), Image.BICUBIC)
            apiece = alpha.transform(size, Image.PERSPECTIVE, _pil_coeffs(H), Image.BILINEAR)
            # The cell's own outline, drawn 1 px fat so neighbouring cells overlap: no seams.
            m = Image.new("L", size)
            ImageDraw.Draw(m).polygon([tuple(p) for p in dst - [cx0, cy0]], fill=255, outline=255)
            col.paste(piece, (int(cx0), int(cy0)), m)
            shp.paste(apiece, (int(cx0), int(cy0)), m)
    if ss > 1:
        col, shp = col.reduce(ss), shp.reduce(ss)
    return (int(x0), int(y0), int(x0 + col.width), int(y0 + col.height)), \
        np.asarray(col, dtype=np.float32) / 255, np.asarray(shp, dtype=np.float32)[..., None] / 255


def swap_pixels(layer, bbox, color, shape):
    """Make psd-tools see `color`/`shape` as this smart object's pixels, at `bbox`.

    The layer keeps its blend mode, opacity, mask, clipping and effects; only its pixels and
    box change. A per-instance subclass overrides the geometry properties, because a smart
    object's stored box can be empty or smaller than its placement (e.g. an empty preview).
    """
    base = type(layer)
    l, t, r, b = bbox
    rgba = np.concatenate([color, shape], axis=2)

    def numpy(self, channel=None, real_mask=True):
        if channel == "color":
            return color
        if channel in ("shape", "alpha"):
            return shape
        if channel is None:
            return rgba
        return base.numpy(self, channel, real_mask=real_mask)

    layer.__class__ = type("Swapped" + base.__name__, (base,), {
        "left": property(lambda self: l), "top": property(lambda self: t),
        "right": property(lambda self: r), "bottom": property(lambda self: b),
        "width": property(lambda self: r - l), "height": property(lambda self: b - t),
        "bbox": property(lambda self: (l, t, r, b)),
        "has_pixels": lambda self: True,
        "numpy": numpy,
    })


# ---------------------------------------------------------------------------------------
# Smart filters
# ---------------------------------------------------------------------------------------
# Photoshop stores a smart object's filters as a list; we redo the ones mockups use for
# shadows and softening. Identified by their four-letter ID, never their name: the name is
# in the language of the Photoshop that saved the file.

def _fourcc(n):
    try:
        return int(n).to_bytes(4, "big").decode("ascii")
    except (ValueError, OverflowError, UnicodeDecodeError):
        return ""


def smart_filters(layer):
    """[(id, label, params, opacity 0-1, blend mode)] for the enabled smart filters, in order."""
    pl = _placed(layer)
    fx = pl.get(b"filterFX") if pl is not None else None
    if not fx or not fx.get(b"enab", True):
        return []
    out = []
    for f in fx.get(b"filterFXList", []):
        if not f.get(b"enab", True):
            continue
        name = f.get(b"Nm  ", "filter")
        label = str(getattr(name, "value", name)).rstrip("\x00").rstrip(".").strip()
        bo = f.get(b"blendOptions") or {}
        mode = bo.get(b"Md  ")
        mode = mode.enum.decode() if hasattr(mode, "enum") else "Nrml"
        out.append((_fourcc(f.get(b"filterID", 0)), label, f.get(b"Fltr") or {},
                    float(bo.get(b"Opct", 100.0)) / 100, mode))
    return out


def _master_lightness(params):
    adjs = params.get(b"Adjs") or []
    if params.get(b"Clrz") or not adjs:
        return None
    m = adjs[0]
    if m.get(b"H   ", 0) or m.get(b"Strt", 0):
        return None
    return float(m.get(b"Lght", 0))


def is_silhouette(layer, filters):
    """True when this copy ends up one flat colour, whatever the design inside it."""
    if layer.width == 0 or layer.height == 0:
        return False                         # nothing stored to keep
    for fid, _, params, opacity, mode in filters:
        if fid == "HStr" and opacity == 1 and mode == "Nrml" and \
                abs(_master_lightness(params) or 0) == 100:
            return True
    if layer.has_effects():
        for e in layer.effects:
            if type(e).__name__ == "ColorOverlay" and e.enabled and float(e.opacity) >= 100 \
                    and str(e.blend_mode).endswith("NORMAL"):
                return True
    return False


def apply_smart_filters(filters, bbox, color, shape):
    """Apply the smart filters we can reproduce. Returns (bbox, color, shape, skipped labels)."""
    skipped = []
    for fid, label, params, opacity, mode in filters:
        if mode != "Nrml":
            skipped.append(label)
            continue
        before = (bbox, color, shape)
        if fid == "GsnB":
            r = float(params.get(b"Rds ", 0))
            bbox, color, shape = _blur(bbox, color, shape, gaussian=r)
        elif fid == "MtnB":
            bbox, color, shape = _blur(bbox, color, shape, motion=(float(params.get(b"Angl", 0)),
                                                                   float(params.get(b"Dstn", 0))))
        elif fid == "HStr" and _master_lightness(params) is not None:
            lt = _master_lightness(params) / 100
            color = color * (1 + lt) if lt < 0 else color + (1 - color) * lt
        else:
            skipped.append(label)
            continue
        if opacity < 1:                      # the filter's own opacity: mix with what it started from
            bbox0, color0, shape0 = before
            color0, shape0 = _pad_to(bbox0, bbox, color0), _pad_to(bbox0, bbox, shape0)
            color = color0 * (1 - opacity) + color * opacity
            shape = shape0 * (1 - opacity) + shape * opacity
    return bbox, color.astype(np.float32), shape.astype(np.float32), skipped


def _pad_to(small, big, arr):
    l, t = small[0] - big[0], small[1] - big[1]
    out = np.zeros((big[3] - big[1], big[2] - big[0], arr.shape[2]), dtype=np.float32)
    out[t:t + arr.shape[0], l:l + arr.shape[1]] = arr
    return out


def _blur(bbox, color, shape, gaussian=0.0, motion=None):
    from scipy import ndimage
    reach = int(np.ceil(3 * gaussian)) if gaussian else int(np.ceil(motion[1] / 2)) + 1
    if reach <= 0:
        return bbox, color, shape
    big = (bbox[0] - reach, bbox[1] - reach, bbox[2] + reach, bbox[3] + reach)
    color, shape = _pad_to(bbox, big, color), _pad_to(bbox, big, shape)
    # Blur premultiplied colour, so transparent pixels do not darken the edges.
    pre = np.concatenate([color * shape, shape], axis=2)
    if gaussian:
        # Photoshop's Gaussian Blur radius is close to the standard deviation.
        pre = ndimage.gaussian_filter(pre, sigma=(gaussian, gaussian, 0))
    else:
        angle, dist = motion
        steps = max(2, min(64, int(round(dist))))
        dx, dy = np.cos(np.radians(angle)), -np.sin(np.radians(angle))
        acc = np.zeros_like(pre)
        for k in np.linspace(-dist / 2, dist / 2, steps):
            acc += ndimage.shift(pre, (k * dy, k * dx, 0), order=1, mode="constant")
        pre = acc / steps
    s = pre[..., 3:4]
    col = np.divide(pre[..., :3], s, out=np.zeros_like(pre[..., :3]), where=s > 1e-6)
    return big, np.clip(col, 0, 1), np.clip(s, 0, 1)


def doc_profile(psd):
    from psd_tools.constants import Resource
    try:
        data = psd.image_resources.get_data(Resource.ICC_PROFILE)
        return ImageCms.ImageCmsProfile(io.BytesIO(data)) if data else None
    except Exception:
        return None


def to_doc_space(img, profile):
    """Designs are sRGB; the template may work in another RGB space (e.g. Adobe RGB)."""
    if profile is None:
        return img
    try:
        alpha = img.getchannel("A")
        out = ImageCms.profileToProfile(img.convert("RGB"), ImageCms.createProfile("sRGB"),
                                        profile, outputMode="RGB")
        out.putalpha(alpha)
        return out
    except Exception:
        return img


# ---------------------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------------------

def open_psd(path):
    from psd_tools import PSDImage
    from psd_tools.constants import ColorMode
    psd = PSDImage.open(path)
    if psd.color_mode != ColorMode.RGB:
        raise MockupError(f"This template is in {psd.color_mode.name} colour mode. Only RGB templates "
                          "are supported; open it in Photoshop once and convert it to RGB.")
    return psd


def background_layer(psd):
    """The template's plain colour background, if it has one we can recolour."""
    first = psd[0] if len(psd) else None
    if first is not None and first.kind == "solidcolorfill" and first.opacity == 255 \
            and str(first.blend_mode).endswith("NORMAL") and not first.has_mask() \
            and first.bbox == (0, 0, psd.width, psd.height):
        return first
    return None


def parse_color(value):
    v = value.strip().lstrip("#")
    if re.fullmatch(r"[0-9a-fA-F]{6}", v):
        return tuple(int(v[i:i + 2], 16) / 255 for i in (0, 2, 4))
    if re.fullmatch(r"\d{1,3}", v):
        return (int(v) / 255,) * 3
    raise MockupError(f"Can't read the colour '{value}'. Use a hex code like #D6D6D6.")


def hide_layers(psd, entry):
    """Hide what a template should not show in OCHA work: the template author's credit text,
    or an old sample design pasted as a plain layer over the smart object. Named per
    template in the catalogue (`hide_layers`); a name that is not found is an error, so a
    changed template can't silently show its credit again."""
    names = set((entry or {}).get("hide_layers", []))
    if not names:
        return
    found = set()
    for layer in psd.descendants():
        if layer.name in names:
            layer.visible = False
            found.add(layer.name)
    missing = names - found
    if missing:
        raise MockupError(f"Template changed: layer(s) {', '.join(sorted(missing))} to hide not found. "
                          "Update hide_layers in templates.json.")


# ---------------------------------------------------------------------------------------
# Reshaping a scene (optional, per template)
# ---------------------------------------------------------------------------------------
# To show a design whose shape differs from the template's object (an A4 cover on a square
# poster), cut one straight strip out of the WHOLE scene - wall, paper, shadows, masks and
# the design's placement alike - so the object becomes the design's shape and everything
# stays consistent. It only looks right where the strip crosses plain, repeating things
# (blank paper, textured wall, plain backdrop), never a hand, a clip or a device. That safe
# zone is recorded per template in the catalogue after checking it by eye, or given by hand
# with --reshape x=1000:1700 to experiment. Cutting only the object leaves a ghost of the old
# one on the wall: tried and rejected.

def parse_reshape(value, entry):
    """--reshape [x=A:B | y=A:B] -> {'x': (A, B), 'y': (A, B)}, or None when not asked."""
    if value is None:
        return None
    if value == "catalogue":
        zones = (entry or {}).get("reshape")
        if not zones:
            raise MockupError("This template has no checked reshape zone. It may still work: try one "
                              "by hand with --reshape x=LEFT:RIGHT (canvas pixels of a plain strip "
                              "through the object), and look hard at the result.")
        return {k: tuple(v) for k, v in zones.items()}
    m_ = re.fullmatch(r"\s*([xy])\s*=\s*(\d+)\s*:\s*(\d+)\s*", value)
    if not m_:
        raise MockupError("--reshape takes x=LEFT:RIGHT or y=TOP:BOTTOM (canvas pixels), or nothing "
                          "to use the template's checked zone.")
    a, b = int(m_.group(2)), int(m_.group(3))
    return {m_.group(1): (min(a, b), max(a, b))}


def _extent(inst, axis):
    """The object's size along an axis, measured across its middle (canvas px)."""
    f = mapper(inst)
    if axis == "x":
        pts = f(np.array([0.0, 1.0]), np.array([0.5, 0.5]))
    else:
        pts = f(np.array([0.5, 0.5]), np.array([0.0, 1.0]))
    return float(np.linalg.norm(pts[1] - pts[0]))


def plan_reshape(zones, slot, design_aspect):
    """Which strip to cut so the slot takes the design's shape: (axis, c0, c1, new aspect)."""
    a = slot.aspect
    if abs(design_aspect / a - 1) < 0.01:
        return None
    axis = "x" if design_aspect < a else "y"    # narrower design: cut width; wider: cut height
    if axis not in zones:
        other = "narrower" if axis == "x" else "less tall"
        raise MockupError(f"This template can't be made {other} here (no reshape zone along {axis}). "
                          "Use --fit fill or fit, or another template.")
    z0, z1 = zones[axis]
    size = _extent(slot.main, axis)
    keep = size * (design_aspect / a if axis == "x" else a / design_aspect)
    cut = int(round(size - keep))
    centre = (z0 + z1) / 2
    c0, c1 = int(round(centre - cut / 2)), int(round(centre - cut / 2)) + cut
    # The cut is cross-faded over a band just before it, and that band must stay inside the
    # checked zone too (else it blends in the object's edge: tried, it ghosts). Centred is
    # best for symmetric lighting; slide the strip along the zone when the band needs room.
    want = int(min(cut, max(160, 0.5 * cut), 450))
    if c0 - z0 < want:
        c0 = max(c0, min(z0 + want, z1 - cut))
        c1 = c0 + cut
    band = max(0, min(want, c0 - z0))
    if c0 < z0 or c1 > z1:
        most = (size - (z1 - z0)) / size
        limit = a * most if axis == "x" else a / most
        raise MockupError(f"The design is too different in shape for this template: it can be reshaped "
                          f"to an aspect of {limit:.2f} at most (design {design_aspect:.2f}). "
                          "Use --fit fill or fit, or another template.")
    new_aspect = a * (keep / size) if axis == "x" else a * (size / keep)
    return axis, c0, c1, new_aspect, band


class _MaskView:
    """A layer's mask seen through a cut: same mask, new box."""
    def __init__(self, orig, bbox):
        self._orig, self._bbox = orig, bbox

    def __getattr__(self, name):
        return getattr(self._orig, name)

    bbox = property(lambda self: self._bbox)
    left = property(lambda self: self._bbox[0])
    top = property(lambda self: self._bbox[1])
    right = property(lambda self: self._bbox[2])
    bottom = property(lambda self: self._bbox[3])
    width = property(lambda self: self._bbox[2] - self._bbox[0])
    height = property(lambda self: self._bbox[3] - self._bbox[1])
    size = property(lambda self: (self.width, self.height))


def reshape_scene(psd, slots, axis, c0, c1, band):
    """Remove canvas columns (x) or rows (y) c0..c1 from every layer, cross-fading over `band`
    pixels before the strip. Returns the new canvas size."""
    d = c1 - c0
    k = 0 if axis == "x" else 1

    def nmap(v):
        return v if v < c0 else (c0 if v < c1 else v - d)

    def box_after(box, kept):
        b = list(box)
        b[k] = nmap(box[k])
        b[k + 2] = b[k] + kept
        return tuple(b)


    def cut(arr, start):
        """Remove the strip. Where the layer covers both sides, cross-fade the last `band`
        pixels before the strip into the last ones inside it: a light gradient across the cut
        (lamp, vignette) then joins smoothly instead of leaving a visible step."""
        ax = 1 - k
        n = arr.shape[ax]
        coords = np.arange(start, start + n)
        keep = (coords < c0) | (coords >= c1)
        i0, i1 = c0 - start, c1 - start
        if band == 0 or i0 - band < 0 or i1 > n:
            return (arr[:, keep] if axis == "x" else arr[keep]), int(keep.sum())
        a = np.take(arr, range(i0 - band, i0), axis=ax).astype(np.float32)
        b = np.take(arr, range(i1 - band, i1), axis=ax).astype(np.float32)
        t = np.linspace(0, 1, band, dtype=np.float32)
        t = t[None, :, None] if axis == "x" else t[:, None, None]
        if arr.ndim == 2:
            t = t[..., 0]
        mixed = (a * (1 - t) + b * t).astype(arr.dtype)
        out = np.concatenate([np.take(arr, range(0, i0 - band), axis=ax), mixed,
                              np.take(arr, range(i1, n), axis=ax)], axis=ax)
        return out, out.shape[ax]

    def crosses(box):
        return box[k + 2] > c0 and box[k] < c1 or box[k] >= c1

    for layer in psd.descendants():
        if not layer.is_visible():
            continue
        box = layer.bbox
        if layer.has_mask() and not layer.mask.disabled and crosses(layer.mask.bbox):
            m_arr = layer.numpy("mask", real_mask=True)
            mb = layer.mask.bbox
            if m_arr is not None and mb[2] > mb[0] and mb[3] > mb[1]:
                arr, kept = cut(m_arr, mb[k])
                new_mb = box_after(mb, kept)
                orig_view = _MaskView(layer.mask, new_mb)
                layer._mask = orig_view
                base = type(layer)

                def numpy(self, channel=None, real_mask=True, _arr=arr, _base=base):
                    return _arr if channel == "mask" else _base.numpy(self, channel, real_mask=real_mask)
                layer.__class__ = type("Cut" + base.__name__, (base,), {"numpy": numpy})
        if layer.has_vector_mask() and not layer.vector_mask.disabled and crosses(box) and box != (0, 0, 0, 0):
            raise MockupError(f"Can't reshape: layer '{layer.name}' is drawn from a vector shape that the "
                              "strip would cut. Choose a strip that misses it, or don't reshape.")
        if layer.is_group() or box == (0, 0, 0, 0) or not crosses(box):
            continue
        if layer.has_pixels():
            color, shape = layer.numpy("color"), layer.numpy("shape")
            if color is None:
                continue
            if shape is None:
                shape = np.ones(color.shape[:2] + (1,), np.float32)
            color, kept = cut(color, box[k])
            shape, _ = cut(shape, box[k])
            swap_pixels(layer, box_after(box, kept), color, shape)
        else:
            # A fill without stored pixels is painted over its box: just make the box smaller.
            lo, hi = box[k], box[k + 2]
            kept = sum(1 for v in range(lo, hi) if v < c0 or v >= c1)
            nb = box_after(box, kept)
            base = type(layer)
            layer.__class__ = type("Moved" + base.__name__, (base,), {
                "left": property(lambda self, b=nb: b[0]), "top": property(lambda self, b=nb: b[1]),
                "right": property(lambda self, b=nb: b[2]), "bottom": property(lambda self, b=nb: b[3]),
                "width": property(lambda self, b=nb: b[2] - b[0]),
                "height": property(lambda self, b=nb: b[3] - b[1]),
                "bbox": property(lambda self, b=nb: b)})
    for slot in slots:
        for inst in slot.instances:
            inst.quad = np.array([[nmap(x), y] if axis == "x" else [x, nmap(y)] for x, y in inst.quad])
    w, h = psd.width, psd.height
    return (w - d, h) if axis == "x" else (w, h - d)


def render_one(path, assignments, background=None, entry=None, warn=print, reshape=None):
    """assignments: {slot number: (RGBA design, fit mode, focus, area)}. Returns RGB PIL image.

    reshape: zones from parse_reshape(); the first design's shape decides the cut."""
    psd = open_psd(path)
    hide_layers(psd, entry)
    slots = read_slots(psd, entry)
    profile = doc_profile(psd)
    by_number = {s.number: s for s in slots}
    for number, (img, mode, focus, area) in assignments.items():
        if area is not None:
            by_number[number].area = area
    size, aspects, cut = (psd.width, psd.height), {}, None
    if reshape:
        first = next(iter(assignments))
        img0 = assignments[first][0]
        plan = plan_reshape(reshape, by_number[first], img0.width / img0.height)
        if plan and (entry or {}).get("reshape_hide"):
            # Features a straight cut can't cross cleanly (a diagonal gloss streak): off when reshaping.
            hide_layers(psd, {"hide_layers": entry["reshape_hide"]})
        if plan:
            axis, c0, c1, new_aspect, band = plan
            size = reshape_scene(psd, slots, axis, c0, c1, band)
            aspects[first] = new_aspect
            cut = (axis, c0, c1)
            warn(f"  reshaped: removed a {c1 - c0} px strip ({'columns' if axis == 'x' else 'rows'} "
                 f"{c0}-{c1}) so the object matches the design. Look closely at the result.")
    for number, (img, mode, focus, area) in assignments.items():
        slot = by_number[number]
        fitted, note = fit_design(img, aspects.get(number, slot.aspect), mode, focus)
        if note:
            warn(f"  slot {number} ({slot.name}): {note}")
        fitted = to_doc_space(fitted, profile)
        opaque = fitted.getchannel("A").getextrema()[0] == 255
        for inst in slot.instances:
            if not inst.renders:
                continue                     # hidden handles ("Edit This" at 0%) draw nothing
            if inst.warp not in ("warpNone", "warpCustom"):
                warn(f"  slot {number}: layer '{inst.layer.name}' uses a Photoshop warp we can't read "
                     f"({inst.warp}); placed flat on its corners instead")
            filters = smart_filters(inst.layer)
            if opaque and is_silhouette(inst.layer, filters):
                # This copy is turned solid black (or one colour) by its filters/effects, e.g. a
                # shadow made from the artwork. It depends only on the page's outline, which an
                # opaque design does not change, so Photoshop's own rendering stays exact.
                continue
            quad = area_quad(inst, slot.area)
            # Scale the design to the size it will be drawn at before warping (sharper and faster).
            target = max(np.linalg.norm(quad[1] - quad[0]), np.linalg.norm(quad[2] - quad[1]) *
                         fitted.width / fitted.height, 8) * 1.5
            d = fitted
            if fitted.width > target:
                d = fitted.resize((round(target), max(1, round(target * fitted.height / fitted.width))),
                                  Image.LANCZOS)
            bbox, color, shape = warp_into(d, inst, slot.area)
            bbox, color, shape, skipped = apply_smart_filters(filters, bbox, color, shape)
            for name in skipped:
                warn(f"  slot {number}: layer '{inst.layer.name}': smart filter '{name}' is not "
                     "reproduced (the rest of the mockup is)")
            swap_pixels(inst.layer, bbox, color, shape)

    layer_filter = None
    color, alpha = 1.0, 0.0
    if background is not None:
        bg = background_layer(psd)
        if bg is None:
            warn("  --background ignored: this template has no plain colour background to change")
        else:
            color, alpha = parse_color(background), 1.0
            layer_filter = lambda l: l is not bg and l.is_visible()   # noqa: E731
    # ignore_preview: otherwise psd-tools returns the preview Photoshop saved, without our swap.
    out = psd.composite(viewport=(0, 0, *size), ignore_preview=True, color=color, alpha=alpha,
                        layer_filter=layer_filter)
    if out.mode == "RGBA":
        flat = Image.new("RGB", out.size, (255, 255, 255))
        flat.paste(out, mask=out.getchannel("A"))
        out = flat
    render_one.last_cut = cut                    # for crop boxes given in template pixels
    return out.convert("RGB"), psd, slots


def label_font(size):
    home = os.path.expanduser("~")
    names = ["Roboto-BoldItalic.ttf", "Roboto-Bold-Italic.ttf", "RobotoBoldItalic.ttf"]
    dirs = ["/Library/Fonts/Roboto", "/Library/Fonts", os.path.join(home, "Library", "Fonts"),
            os.path.join(home, "Library", "Fonts", "Roboto"), "/System/Library/Fonts/Supplemental",
            os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts")]
    for d in dirs:
        for n in names:
            p = os.path.join(d, n)
            if os.path.isfile(p):
                return ImageFont.truetype(p, size), p
    for p in glob.glob("/Library/Fonts/**/Roboto*Bold*Italic*.ttf", recursive=True) + \
            glob.glob(os.path.join(home, "Library", "Fonts", "**", "Roboto*Bold*Italic*.ttf"), recursive=True):
        return ImageFont.truetype(p, size), p
    for fallback in ("/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf",
                     os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "arialbi.ttf")):
        if os.path.isfile(fallback):
            return ImageFont.truetype(fallback, size), fallback
    return ImageFont.load_default(size), None


def label_position(img_size, slots, entry, text, override=None, offset=(0, 0)):
    """Baseline-left point and size for the label.

    First choice: just above the design's top-left corner (as on the approved cover options).
    If that would sit on top of a design (several cards in a scene), the top-left corner of
    the image, then the bottom-left. Sizes are in the template's own pixels.
    """
    w, h = img_size
    size = round(h * 0.0196)                 # 56 px on the 2854 px magazine, as approved
    if override:
        x, y = (float(v) for v in override.split(","))
        return (x * w if x <= 1 else x, y * h if y <= 1 else y), size
    if entry and entry.get("label"):
        x, y = entry["label"]
        return (x * w, y * h), size
    live = design_slots(slots)
    # offset: where a crop starts, so design positions match the cropped image.
    quads = [area_quad(i, s.area) - np.asarray(offset, dtype=np.float64)
             for s in live for i in s.instances if i.renders]
    # Where the designs are, drawn small: a label must not cover any of them.
    k = 8
    taken = Image.new("L", (max(1, w // k), max(1, h // k)), 0)
    draw = ImageDraw.Draw(taken)
    for q in quads:
        draw.polygon([tuple(p) for p in (q / k)], fill=255)
    font, _ = label_font(size)
    tw = draw.textlength(text, font=font) if hasattr(draw, "textlength") else size * len(text) * 0.6

    def free(x, base):
        box = (int(x // k), int((base - size) // k), int((x + tw) // k) + 1, int(base // k) + 1)
        if box[0] < 0 or box[1] < 0 or box[2] > taken.width or box[3] > taken.height:
            return False
        return taken.crop(box).getextrema()[1] == 0

    candidates = []
    if quads:
        allq = np.vstack(quads)
        top = allq[:, 1].min()
        main = live[0].main if live else None
        left = (area_quad(main, live[0].area)[:, 0].min() - offset[0]) if main is not None else allq[:, 0].min()
        candidates.append((max(left, w * 0.04), top - h * 0.028))
    candidates += [(w * 0.04, h * 0.04 + size), (w * 0.04, h * 0.96)]
    for x, base in candidates:
        if free(x, base):
            return (x, base), size
    return candidates[-2], size


def draw_label(img, text, point, size, color=None):
    font, _ = label_font(size)
    d = ImageDraw.Draw(img)
    if color is None:
        # Black on light backgrounds, white on dark: sample where the text will sit.
        x, y = point
        box = (int(max(0, x)), int(max(0, y - size)), int(min(img.width, x + size * 10)), int(min(img.height, y)))
        lum = np.asarray(img.crop(box).convert("L")).mean() if box[2] > box[0] and box[3] > box[1] else 255
        color = (0, 0, 0) if lum > 110 else (255, 255, 255)
    d.text(point, text, font=font, fill=color, anchor="ls")
    return img


# ---------------------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------------------

def _status(folder, entry):
    p = os.path.join(folder, entry["path"])
    if not os.path.exists(p):
        return "missing", p
    return ("online-only" if online_only(p) else "ready"), p


def cmd_templates(args):
    cat = load_catalog()
    folder = find_folder(args.folder, required=False)
    print(f"Templates folder: {folder or 'NOT FOUND (see `mockups.py setup`)'}\n")
    for key, e in cat["templates"].items():
        status = _status(folder, e)[0] if folder else "?"
        print(f"{key:24} {status:12} {e['title']}  [{e['format']}]")


def cmd_ready(args):
    """Check templates are on this computer before using them; ask for offline if not."""
    cat = load_catalog()["templates"]
    folder = find_folder(args.folder)
    keys = args.keys or list(cat)
    unknown = [k for k in keys if k not in cat]
    if unknown:
        raise MockupError(f"Unknown template(s): {', '.join(unknown)}. See `mockups.py templates`.")
    cloud, missing = [], []
    for k in keys:
        status, p = _status(folder, cat[k])
        print(f"{k:24} {status}")
        if status == "online-only":
            cloud.append(os.path.dirname(p))
        elif status == "missing":
            missing.append(p)
    if missing:
        raise MockupError("Not in the templates folder (Dropbox may still be syncing, or the folder\n"
                          "is incomplete; tell ochavisual@un.org if it persists):\n  "
                          + "\n  ".join(missing))
    if cloud:
        # Asking for the whole templates folder is one click and covers every template.
        whole = len(cloud) > 2 or not args.keys
        raise OnlineOnly(offline_ask([folder] if whole else cloud))
    print("\nAll ready.")


def describe(slots, psd):
    print(f"Canvas {psd.width} x {psd.height} px, {psd.depth}-bit {psd.color_mode.name}")
    for s in slots:
        m = s.main
        state = "ACTIVE" if s.active else "hidden"
        x0, y0, x1, y1 = s.area
        part = "" if (x0, y0, x1, y1) == (0, 0, *m.content) else f"  design area {round(x1 - x0)}x{round(y1 - y0)} at ({round(x0)},{round(y0)})"
        shape = "flat" if m.flat else "perspective"
        print(f"\nslot {s.number}: '{s.name}'  [{s.role}, {state}, {shape}]")
        print(f"  content {round(m.content[0])} x {round(m.content[1])} px, aspect {s.aspect:.3f} "
              f"({_aspect_name(s.aspect)}){part}")
        for i in s.instances:
            q = ", ".join(f"({x:.0f},{y:.0f})" for x, y in i.quad)
            flags = [f for f, on in (("renders", i.renders), ("curved (mesh warp)", i.warp == "warpCustom"),
                                      (f"warp {i.warp} NOT reproduced!", i.warp not in ("warpNone", "warpCustom"))) if on]
            fl = smart_filters(i.layer)
            if fl:
                kind = "kept as Photoshop drew it" if is_silhouette(i.layer, fl) else \
                    ", ".join(f"{lbl} ({'redone' if fid in ('GsnB', 'MtnB') or (fid == 'HStr' and _master_lightness(p) is not None) else 'NOT redone'})"
                              for fid, lbl, p, _, _ in fl)
                flags.append(f"smart filters: {kind}")
            print(f"   - layer '{i.layer.name}'  {str(i.layer.blend_mode).replace('BlendMode.', '').lower()} "
                  f"{round(i.layer.opacity / 2.55)}%  corners {q}  {' '.join(flags)}")


def _aspect_name(a):
    named = {"A-series portrait (A4/A5)": 1 / 2 ** 0.5, "A-series landscape": 2 ** 0.5,
             "US Letter portrait": 8.5 / 11, "US Letter landscape": 11 / 8.5, "square": 1.0,
             "A-series spread (2 pages)": 2 / 2 ** 0.5, "16:9": 16 / 9, "9:16": 9 / 16,
             "4:5": 0.8, "3.5x2 in card": 1.75, "2x3 poster": 2 / 3, "3:4": 0.75}
    name, val = min(named.items(), key=lambda kv: abs(kv[1] / a - 1))
    return name if abs(val / a - 1) < 0.015 else "custom"


def cmd_inspect(args):
    path, entry = resolve_template(args.template, args.folder)
    psd = open_psd(path)
    slots = read_slots(psd, entry)
    for s in slots:
        if s.active and s.role == "design":
            s.area = detect_area(s.main)
    if entry and entry.get("area"):
        for s in design_slots(slots):
            s.area = tuple(entry["area"])
    print(path)
    describe(slots, psd)
    live = design_slots(slots)
    print(f"\n{len(live)} design slot(s) will take a design: " +
          ", ".join(f"{s.number} '{s.name}'" for s in live) if live else "\nNo design slots found.")


def cmd_check(args):
    """Render the untouched template and compare with the preview Photoshop saved in the file."""
    path, _ = resolve_template(args.template, args.folder)
    psd = open_psd(path)
    if not psd.has_preview():
        print("No Photoshop preview saved in this file (saved without 'Maximize compatibility'); "
              "can't compare. Check the render by eye.")
        return
    ours = np.asarray(psd.composite(ignore_preview=True).convert("RGB"), dtype=np.int16)
    theirs = np.asarray(psd.topil().convert("RGB"), dtype=np.int16)
    diff = np.abs(ours - theirs).max(axis=2)
    mean, p99 = diff.mean(), np.percentile(diff, 99)
    # A small even shift (p99 low) is invisible; a high p99 means something is drawn differently.
    verdict = "faithful" if mean < 8 and p99 < 15 else ("close" if mean < 10 and p99 < 40 else "DIFFERS")
    print(f"{os.path.basename(path)}: mean difference {mean:.2f}/255, 99th percentile {p99:.0f}/255 -> {verdict}")
    if args.out:
        side = Image.new("RGB", (ours.shape[1] * 2, ours.shape[0]))
        side.paste(Image.fromarray(ours.astype(np.uint8)), (0, 0))
        side.paste(Image.fromarray(theirs.astype(np.uint8)), (ours.shape[1], 0))
        side.thumbnail((2400, 2400))
        side.save(args.out)
        print("Side by side (ours | Photoshop):", args.out)


def build_jobs(args, slots, entry):
    """Turn --design/--label or --spec into [(label, {slot number: (path, page, half)})]."""
    live = design_slots(slots)
    if not live:
        raise MockupError("This template has no active design slot (no visible smart object to replace).")
    by_name = {s.name.lower(): s for s in slots}

    def slot_ref(ref):
        if str(ref).isdigit() and int(ref) in {s.number for s in slots}:
            return int(ref)
        hits = [s for n, s in by_name.items() if str(ref).lower() in n]
        if len(hits) != 1:
            raise MockupError(f"Slot '{ref}' matches {len(hits)} slots. Use the number from `inspect`.")
        return hits[0].number

    jobs = []
    if args.spec:
        with open(args.spec, encoding="utf-8") as f:
            spec = json.load(f)
        for item in spec:
            assign = {slot_ref(k): (*parse_design(v), None) for k, v in item["slots"].items()}
            jobs.append((item.get("label"), assign))
        return jobs
    if not args.design:
        raise MockupError("Give at least one --design (a PDF page, PNG or JPG), or a --spec file.")
    labels = args.label or []
    if labels and len(labels) != len(args.design):
        raise MockupError(f"{len(args.design)} designs but {len(labels)} labels: give one label per design.")
    for n, spec in enumerate(args.design):
        path, page = parse_design(spec)
        assign = {}
        if len(live) == 1:
            assign[live[0].number] = (path, page, None)
        elif len(live) == 2 and abs(design_aspect(path, page, args.bleed) / (2 * live[0].aspect) - 1) < 0.03:
            # One spread-shaped page (InDesign often exports spreads as single wide pages) on
            # a two-page template: its left half goes left, its right half goes right.
            assign[live[0].number] = (path, page, "left")
            assign[live[1].number] = (path, page, "right")
            print(f"  {os.path.basename(path)} page {page} is a spread: split across slots "
                  f"{live[0].number} and {live[1].number}")
        elif path.lower().endswith(".pdf"):
            # Consecutive single pages fill the design slots left to right.
            for k, s in enumerate(live):
                assign[s.number] = (path, page + k, None)
        else:
            raise MockupError(
                f"This template has {len(live)} design slots ("
                + ", ".join(f"{s.number} '{s.name}'" for s in live)
                + "). Pass a PDF (consecutive pages fill them left to right) or use --spec to say "
                  "which image goes where.")
        jobs.append((labels[n] if labels else None, assign))
    return jobs


def cmd_render(args):
    path, entry = resolve_template(args.template, args.folder)
    entry = entry or {}
    out = os.path.abspath(os.path.expanduser(args.out))
    ext = os.path.splitext(out)[1].lower()
    if ext not in (".pdf", ".png", ".jpg", ".jpeg"):
        raise MockupError("--out must end in .pdf, .png or .jpg")

    psd = open_psd(path)
    slots = read_slots(psd, entry)
    jobs = build_jobs(args, slots, entry)
    if ext != ".pdf" and len(jobs) > 1:
        raise MockupError("Several designs make several pages: use a .pdf --out (or render one at a time).")

    focus = tuple(float(v) for v in args.focus.split(",")) if args.focus else (0.5, 0.5)
    background = args.background if args.background is not None else entry.get("background")
    if background in ("keep", "template"):
        background = None
    area_override = tuple(entry["area"]) if entry.get("area") else None
    if args.area == "full":
        area_override = "full"

    print(f"Template: {os.path.basename(path)}")
    pages = []
    for label, assign in jobs:
        psd = open_psd(path)                     # fresh copy: swapping changes the layers
        slots = read_slots(psd, entry)
        by_number = {s.number: s for s in slots}
        designs = {}
        for number, (dpath, page, half) in assign.items():
            slot = by_number[number]
            if area_override == "full":
                area = (0.0, 0.0, *slot.main.content)
            elif area_override:
                area = area_override
            else:
                area = detect_area(slot.main)
            slot.area = area
            q = area_quad(slot.main, area)
            longest = max(np.linalg.norm(q[1] - q[0]), np.linalg.norm(q[3] - q[0])) * 1.5
            if half:
                whole = load_design(dpath, page, longest * 2, args.bleed)
                mid = whole.width // 2
                img = whole.crop((0, 0, mid, whole.height) if half == "left" else (mid, 0, whole.width, whole.height))
            elif dpath.lower().endswith(".pdf"):
                n_pages = pdf_page_count(dpath)
                if page > n_pages:
                    raise MockupError(f"{os.path.basename(dpath)} has {n_pages} pages; page {page} needed "
                                      f"for slot {number}.")
                page_aspect = pdf_page_aspect(dpath, page, args.bleed)
                spread = args.spread or entry.get("spread")
                if spread and abs(slot.aspect / (2 * page_aspect) - 1) < 0.03 and page < n_pages:
                    # A one-slot spread template and a PDF of single pages: put two side by side.
                    # Only when asked: a landscape A-poster has the same shape as two A-pages.
                    left = load_design(dpath, page, longest, args.bleed)
                    right = load_design(dpath, page + 1, longest, args.bleed)
                    img = Image.new("RGBA", (left.width + right.width, max(left.height, right.height)))
                    img.paste(left, (0, 0)); img.paste(right, (left.width, 0))
                    print(f"  slot {number}: pages {page}-{page + 1} side by side as a spread")
                else:
                    img = load_design(dpath, page, longest, args.bleed)
            else:
                img = load_design(dpath, page, longest)
            designs[number] = (img, args.fit, focus, area)
        img, _, slots_used = render_one(path, designs, background, entry,
                                        reshape=parse_reshape(args.reshape, entry))
        crop = parse_crop(args.crop, entry, (img.width, img.height), render_one.last_cut)
        if crop:
            # Some scenes carry a lot of empty room (e.g. long poster wires): keep the part
            # that matters. Template pixels, set per template in the catalogue.
            img = img.crop(crop)
        if label:
            # Before any scaling: the label is placed in the template's own pixel coordinates.
            point, size = label_position(img.size, slots_used, entry, label, args.label_pos,
                                         offset=crop[:2] if crop else (0, 0))
            draw_label(img, label, point, size, parse_color(args.label_color) if args.label_color else None)
        if args.width and args.width < img.width:
            img = img.resize((args.width, round(img.height * args.width / img.width)), Image.LANCZOS)
        pages.append(img)
        print(f"  page {len(pages)}: {label or os.path.basename(next(iter(assign.values()))[0])}")

    os.makedirs(os.path.dirname(out), exist_ok=True)
    if ext == ".pdf":
        import fitz
        doc = fitz.open()
        for img in pages:
            buf = io.BytesIO()
            img.save(buf, "JPEG", quality=90, optimize=True)
            pw, ph = img.width * 72 / 150, img.height * 72 / 150      # 150 ppi page size
            page = doc.new_page(width=pw, height=ph)
            page.insert_image(page.rect, stream=buf.getvalue())
        doc.save(out, garbage=4, deflate=True)
    elif ext == ".png":
        pages[0].save(out, optimize=True)
    else:
        pages[0].save(out, "JPEG", quality=92, optimize=True)
    print("Saved", out)


def _test_card(aspect, longest=1600, label="TEST"):
    """Blue card, yellow top-left square, red frame: orientation and placement are obvious."""
    w, h = (longest, round(longest / aspect)) if aspect >= 1 else (round(longest * aspect), longest)
    im = Image.new("RGB", (w, h), (0, 158, 219))
    d = ImageDraw.Draw(im)
    step = max(w, h) // 12
    for x in range(0, w, step):
        d.line([(x, 0), (x, h)], fill=(255, 255, 255), width=3)
    for y in range(0, h, step):
        d.line([(0, y), (w, y)], fill=(255, 255, 255), width=3)
    d.rectangle([0, 0, w // 4, w // 4], fill=(255, 220, 0))
    d.rectangle([0, 0, w - 1, h - 1], outline=(237, 28, 36), width=max(4, w // 80))
    font, _ = label_font(max(w, h) // 12)
    d.text((w // 2, h // 2), label, font=font, anchor="mm", fill=(0, 0, 0))
    return im.convert("RGBA")


def cmd_selftest(args):
    """Render every catalogued template that is on this computer with a test card, and check
    the result: blue where the design's middle should be, yellow near its top-left corner."""
    cat = load_catalog()["templates"]
    folder = find_folder(args.folder)
    keys = args.only or list(cat)
    sheet, failed = [], []
    for key in keys:
        entry = dict(cat[key], key=key)
        path = os.path.join(folder, entry["path"])
        if not os.path.exists(path) or online_only(path):
            print(f"{key:24} SKIPPED (missing or online-only: run `ready`)")
            continue
        # The plain render, plus one reshaped render for templates with a checked reshape zone:
        # a narrower design where the zone allows it, else a wider one.
        variants = [("", None, 1.0)]
        if entry.get("reshape"):
            variants.append((" reshaped", {k: tuple(v) for k, v in entry["reshape"].items()},
                             0.8 if "x" in entry["reshape"] else 1.25))
        for suffix, zones, factor in variants:
            psd = open_psd(path)
            slots = read_slots(psd, entry)
            live = design_slots(slots)
            assign = {}
            for s in live:
                s.area = tuple(entry["area"]) if entry.get("area") else detect_area(s.main)
                assign[s.number] = (_test_card(s.aspect * factor, label=key[:12]), "stretch", (0.5, 0.5), s.area)
            img, _, used = render_one(path, assign, entry.get("background"), entry, warn=lambda m: None,
                                      reshape=zones)
            px = np.asarray(img, dtype=np.int16)
            problems = []
            for s in [u for u in used if u.number in assign]:
                q = area_quad(s.main, s.area)
                def at(u, v):
                    return (1 - u) * (1 - v) * q[0] + u * (1 - v) * q[1] + u * v * q[2] + (1 - u) * v * q[3]

                def sample(pt):
                    xi, yi = int(np.clip(pt[0], 0, img.width - 1)), int(np.clip(pt[1], 0, img.height - 1))
                    return px[max(0, yi - 3):yi + 4, max(0, xi - 3):xi + 4].reshape(-1, 3).mean(axis=0)

                # Blue somewhere in the lower half, clear of the card's label in the middle. Several
                # points, because in a scene another object may cover part of a design.
                blue = [sample(at(u, v)) for u, v in ((0.5, 0.75), (0.25, 0.7), (0.75, 0.7), (0.8, 0.9))]
                if not any(b > r + 40 for r, g, b in blue):
                    problems.append(f"slot {s.number}: design not found where expected")
                # 4% in from the top-left corner along the diagonal: inside the yellow square.
                r, g, b = sample(q[0] + 0.04 * (q[2] - q[0]))
                if not (r > b + 40 and g > b + 40):
                    problems.append(f"slot {s.number}: top-left is not yellow (upside down or mirrored?)")
            name = key + suffix
            print(f"{name:24} {'OK' if not problems else 'FAIL  ' + '; '.join(problems)}")
            if problems:
                failed.append(name)
            crop = parse_crop(None, entry, img.size, render_one.last_cut)
            thumb = img.crop(crop) if crop else img.copy()
            thumb.thumbnail((800, 800))
            sheet.append((name, thumb))
    if args.out and sheet:
        cols = 3
        rows = (len(sheet) + cols - 1) // cols
        out = Image.new("RGB", (cols * 820, rows * 860), (255, 255, 255))
        d = ImageDraw.Draw(out)
        font, _ = label_font(28)
        for n, (key, t) in enumerate(sheet):
            x, y = (n % cols) * 820 + 10, (n // cols) * 860 + 10
            d.text((x, y + 30), key, font=font, fill=(0, 0, 0), anchor="ls")
            out.paste(t, (x, y + 45))
        out.save(args.out, quality=88)
        print("Contact sheet:", args.out)
    if failed:
        sys.exit(1)


def parse_crop(value, entry, size, cut=None):
    """--crop x0,y0,x1,y1 | none, else the catalogue's crop, else no crop.
    `cut` (axis, c0, c1) moves a crop given in template pixels onto a reshaped scene."""
    if value and value.lower() == "none":
        return None
    box = [float(v) for v in value.split(",")] if value else (entry or {}).get("crop")
    if not box:
        return None
    if len(box) != 4:
        raise MockupError("--crop needs four numbers: left,top,right,bottom (template pixels).")
    if cut:
        axis, c0, c1 = cut
        i = (0, 2) if axis == "x" else (1, 3)
        box = list(box)
        for j in i:
            box[j] = box[j] if box[j] < c0 else (c0 if box[j] < c1 else box[j] - (c1 - c0))
    w, h = size
    x0, y0, x1, y1 = (int(round(v)) for v in box)
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(w, x1), min(h, y1)
    if x1 - x0 < 50 or y1 - y0 < 50:
        raise MockupError(f"The crop {box} leaves almost nothing of the {w}x{h} template.")
    return (x0, y0, x1, y1)


def cmd_setup(args):
    path = os.path.abspath(os.path.expanduser(args.folder))
    if not os.path.isdir(path):
        raise MockupError(f"Not a folder: {path}")
    cfg = _config()
    cfg["folder"] = path
    os.makedirs(os.path.dirname(CONFIG), exist_ok=True)
    with open(CONFIG, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    print(f"Saved. The mockup templates folder is {path}\n(setting stored in {CONFIG})")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--folder", help="the mockup templates folder (overrides the saved setting)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("ready", parents=[common], help="are the templates on this computer?")
    p.add_argument("keys", nargs="*", help="catalogue keys (default: all)")

    sub.add_parser("templates", parents=[common], help="list catalogued templates")
    p = sub.add_parser("inspect", parents=[common], help="show a template's slots"); p.add_argument("template")
    p = sub.add_parser("check", parents=[common], help="compare our render with Photoshop's preview")
    p.add_argument("template"); p.add_argument("--out", help="save a side-by-side comparison image")
    p = sub.add_parser("selftest", parents=[common], help="render every catalogued template with a test card")
    p.add_argument("--only", nargs="+", help="just these catalogue keys")
    p.add_argument("--out", help="save a contact sheet of the results (.jpg)")
    p = sub.add_parser("setup", help="remember the templates folder")
    p.add_argument("--folder", required=True)

    p = sub.add_parser("render", parents=[common], help="make mockups")
    p.add_argument("template")
    p.add_argument("--design", action="append", help="PDF page (file.pdf#3), PNG or JPG; repeat for several pages")
    p.add_argument("--label", action="append", help="label for each design, in the same order")
    p.add_argument("--spec", help="JSON list: [{\"label\": ..., \"slots\": {\"1\": \"a.pdf#2\", \"2\": \"b.png\"}}]")
    p.add_argument("--out", required=True, help=".pdf (one page per design), .png or .jpg")
    p.add_argument("--fit", default="auto", choices=["auto", "fill", "fit", "stretch"],
                   help="when the design's shape differs from the slot (auto: stretch up to 2%%, else fill)")
    p.add_argument("--focus", help="crop centre for --fit fill, as x,y from 0 to 1 (default 0.5,0.5)")
    p.add_argument("--background", help="recolour the template's plain background (#D6D6D6), or 'keep'")
    p.add_argument("--area", choices=["auto", "full"], default="auto",
                   help="full: the design fills the whole smart object, skipping area detection")
    p.add_argument("--bleed", action="store_true", help="show a PDF's bleed instead of trimming to the page")
    p.add_argument("--reshape", nargs="?", const="catalogue", metavar="x=A:B",
                   help="cut a plain strip out of the scene so the object takes the design's shape "
                        "(templates with a checked zone; or give one: x=LEFT:RIGHT / y=TOP:BOTTOM). "
                        "Works only on some templates: always look at the result")
    p.add_argument("--spread", action="store_true",
                   help="one-slot spread template: put this PDF page and the next side by side")
    p.add_argument("--width", type=int, help="scale the result down to this many pixels wide")
    p.add_argument("--crop", help="keep only left,top,right,bottom of the scene (template pixels), "
                                  "or 'none' to undo the template's own crop")
    p.add_argument("--label-pos", help="label baseline-left as x,y (pixels, or 0-1 fractions)")
    p.add_argument("--label-color", help="label colour, e.g. #000000 (default: black or white by background)")

    args = ap.parse_args(argv)
    try:
        {"templates": cmd_templates, "inspect": cmd_inspect, "check": cmd_check,
         "render": cmd_render, "setup": cmd_setup, "selftest": cmd_selftest,
         "ready": cmd_ready}[args.cmd](args)
    except MockupError as e:
        print(f"\n{e}", file=sys.stderr)
        sys.exit(e.code)


if __name__ == "__main__":
    main()
