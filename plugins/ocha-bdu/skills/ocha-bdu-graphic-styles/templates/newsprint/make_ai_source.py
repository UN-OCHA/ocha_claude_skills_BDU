"""Make the source for the editable .ai from the final template.

  python3 tools/make_ai_source.py
    -> tools/ai_layers/*.png              the paper texture, and one image per paper piece (badge, card, label strip,
                                          marker, circle, example sheet) with its torn edge, shadow and inked icon
    -> tools/un_drf_platform_ai.html      the vector page the .ai is exported from
  then: ocha-bdu-files-and-folders export_ai on tools/un_drf_platform_ai.html -> un_drf_platform.ai

Rules (user, 25 Nov 2026):
- What isn't vector goes into the .ai as images, so the .ai looks like the final and everything vector stays editable.
- Each raster piece is its own image, not one sheet.
- Layers follow meaning, not type: Background, Heading, 6 UN entities, Risk assessment, Agree on funding, Trigger met,
  Funding released, CERF example. Each holds its text, its vector lines and its paper images. No groups.

How: the Newsprint look uses raster SVG filters and blend modes, which Chrome prints as images. So the pieces are
rendered on their own (transparent background), cropped one by one, and placed as <img> under the vector parts.
Every element carries its section as its own data-ai-layer, because the exporter puts an object in the smallest
tagged box that holds it: tagging each element itself means nothing can fall into a neighbour's layer.

Load-bearing: no data-ai-name anywhere. With named groups the exporter dropped arrows, badges and label strips from
the .ai (24 Nov 2026, ~22,000 pixel differences).
"""
import json, re, sys, pathlib, subprocess
from PIL import Image

root = pathlib.Path(__file__).resolve().parent
SRC = root / (sys.argv[1] if len(sys.argv) > 1 else "un_drf_platform.html")
OUT = root / (sys.argv[2] if len(sys.argv) > 2 else SRC.stem + "_ai.html")
LAYERS = root / "ai_layers"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PX = 3.125                      # PNG pixels per CSS pixel (2025 x 1525 for a 648 x 488 page)
MARGIN = 4                      # CSS px around each piece: room for the torn edge and the shadow
s = SRC.read_text()

GRAIN = re.compile(r'<svg class="grain".*?</svg>\n?', re.S)
CRUMPLE = re.compile(r'<svg width="486pt" height="366pt" style="position:absolute;left:0;top:0;pointer-events:none;'
                     r'mix-blend-mode:multiply;opacity:[\d.]+">.*?</svg>\n?', re.S)
GRID = re.compile(r', linear-gradient\(var\(--grid-line\) 0\.5pt, transparent 0\.5pt\), linear-gradient\(90deg, '
                  r'var\(--grid-line\) 0\.5pt, transparent 0\.5pt\)')
for name, rx in (("grain", GRAIN), ("crumple", CRUMPLE), ("grid", GRID)):
    assert rx.search(s), f"anchor for the {name} layer not found: the template changed, update this script"

PIECES = ".blob, .ent, .badge, .card, .sheet, .w, .mk, svg.raster"
# Vector drawings that carry a filter (the blasts' torn edge, the ink on the CERF bars and money) are pieces too:
# without the filter they would come out flat in the .ai.
RASTER_SVG = re.compile(r'<svg class="gfx"((?:(?!</svg>).)*?filter="url\(#(?:(?!</svg>).)*?</svg>)', re.S)
# Which section each element belongs to, decided in the page from what it is and the text near it.
SECTION_JS = r"""
const MAIN = { "6 UN entities": "6 UN entities", "Risk assessment": "Risk assessment",
               "Agree on funding": "Agree on funding", "Trigger met": "Trigger met", "Funding released": "Funding released" };
function section(el) {
  if (el.closest('[data-ai-layer="CERF example"]')) return "CERF example";
  if (el.matches("h1.title, h1.title *")) return "Heading";
  if (el.matches(".blob, .ent")) return "6 UN entities";
  const t = (el.closest("p") || el).textContent.trim();
  if (MAIN[t]) return MAIN[t];
  if (el.matches(".badge.side")) return "Risk assessment";
  if (el.matches(".badge")) return "Funding released";
  if (el.matches(".card")) return "Agree on funding";
  const svg = el.closest("svg.gfx"), name = svg && svg.getAttribute("data-ai-name");
  if (name === "Risk assessment arrow") return "Risk assessment";
  if (name === "Funding released arrows") return "Funding released";
  if (svg && svg.querySelector("polygon")) return "Trigger met";
  return null;
}
"""


def chrome(html, *, png=None, dump=False, transparent=False):
    tmp = root / "_ai_tmp.html"          # in tools/, so relative paths resolve as in the template
    tmp.write_text(html)
    args = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
            "--force-device-scale-factor=3.125", "--window-size=648,488"]
    if png:
        args.append(f"--screenshot={png}")
    if dump:
        args += ["--dump-dom", "--virtual-time-budget=3000"]
    if transparent:
        args.append("--default-background-color=00000000")
    r = subprocess.run(args + [tmp.as_uri()], check=True, capture_output=True, text=True)
    tmp.unlink()
    return r.stdout


def with_css(html, css):
    return html.replace("</style>", css + "\n</style>", 1)


def with_script(html, js):
    return html.replace("</body>", f"<script>{js}</script>\n</body>", 1)


LAYERS.mkdir(exist_ok=True)
for old in LAYERS.glob("*.png"):
    old.unlink()

# 1. Background texture: the page with no grid and nothing on it.
chrome(with_css(GRID.sub("", s), "  .art { visibility: hidden; }"), png=LAYERS / "background_paper.png")

# 2. Where each paper piece is, and its section.
flat = RASTER_SVG.sub(r'<svg class="gfx raster"\1', CRUMPLE.sub("", GRAIN.sub("", s)))
assert "gfx raster" in flat
measured = chrome(with_script(flat, SECTION_JS + r"""
  const out = [...document.querySelectorAll('""" + PIECES + r"""')].map((el, i) => {
    const r = el.getBoundingClientRect();
    return { i, sect: section(el), cls: el.className, box: [r.left, r.top, r.right, r.bottom] };
  });
  const pre = document.createElement("pre"); pre.id = "measured"; pre.textContent = JSON.stringify(out);
  document.body.appendChild(pre);
"""), dump=True)
pieces = json.loads(re.search(r'<pre id="measured">(.*?)</pre>', measured, re.S).group(1)
                    .replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&amp;", "&"))
assert pieces and all(p["sect"] for p in pieces), [p for p in pieces if not p["sect"]]

# 3. Render the pieces on a transparent page: the circle alone, the example sheet alone, then everything else,
#    so no crop picks up a neighbour sitting under it. Text, arrows and the ground are hidden.
HIDE_REST = """  html, body { background: none !important; }
  .art, .art * { color: transparent !important; }
  .gfx { visibility: hidden !important; }
  svg.raster { visibility: visible !important; }"""
sheets = {
    # The circle is multiplied into the paper in the final. On its own it would come out flat and hide the grid:
    # a half-transparent tint that gives the same colour over the paper (#D6E6EB at 50%) keeps the grid visible.
    "blob": "  .art * { visibility: hidden !important; } .blob { visibility: visible !important; "
            "background: rgba(214,230,235,0.5) !important; mix-blend-mode: normal !important; }",
    "sheet": "  .art * { visibility: hidden !important; } .sheet { visibility: visible !important; }",
    "rest": "  .blob, .sheet { visibility: hidden !important; }",
}
for key, css in sheets.items():
    chrome(with_css(flat, HIDE_REST + "\n" + css), png=LAYERS / f"_sheet_{key}.png", transparent=True)
crops = {}
for p in pieces:
    key = "blob" if "blob" in p["cls"] else "sheet" if "sheet" in p["cls"] else "rest"
    l, t, r, b = p["box"]
    box = (max(0, l - MARGIN), max(0, t - MARGIN), min(648, r + MARGIN), min(488, b + MARGIN))
    sect = re.sub(r"[^a-z0-9]+", "_", p["sect"].lower()).strip("_")
    name = f"{sect}_{p['i']:02d}.png"
    Image.open(LAYERS / f"_sheet_{key}.png").crop(tuple(round(c * PX) for c in box)).save(LAYERS / name)
    crops[p["i"]] = (name, box, p["sect"])
for tmp in LAYERS.glob("_sheet_*.png"):
    tmp.unlink()

# 4. The vector page: filters, blends and names stripped, paper pieces drawn by the images instead.
v = flat
v = re.sub(r'background-image: radial-gradient[^;]*;', '', v, count=1, flags=re.S)
v = re.sub(r'\n\s*background-size: 100% 100%[^;]*;', '', v, count=1)
v = re.sub(r' filter="url\(#[a-z0-9]+\)"', '', v)
v = re.sub(r'filter: url\(#[a-z]+\);?', '', v)
v = v.replace('filter: var(--cut);', '').replace('mix-blend-mode: multiply;', '')
# No page clipping: with body { overflow: hidden } Chrome clips every image to the page and they all read as
# page-sized to the exporter.
v = v.replace("position: relative; overflow: hidden;", "position: relative;", 1)
v = with_css(v, """  .badge::before, .ent::before, .card::before, .sheet::before, .w::before, .mk::before { display: none !important; }
  .badge > svg, .card > svg, .blob, svg.raster { visibility: hidden !important; }""")
imgs = [{"src": f"ai_layers/{n}", "box": [round(c * 0.75, 2) for c in box], "sect": sect} for n, box, sect in crops.values()]
grid = ("".join(f'<line x1="10" y1="{y}" x2="476" y2="{y}"/>' for y in range(12, 355, 12)) +
        "".join(f'<line x1="{x}" y1="10" x2="{x}" y2="356"/>' for x in range(12, 475, 12)))
built = chrome(with_script(v, SECTION_JS + r"""
  const art = document.querySelector(".art");
  // Background: the paper texture and the grid, under everything.
  const bg = document.createElement("div");
  bg.innerHTML = '<img src="ai_layers/background_paper.png" data-ai-layer="Background" ' +
    'style="position:absolute;left:0;top:0;width:486pt;height:366pt">' +
    '<svg data-ai-layer="Background" width="466pt" height="346pt" viewBox="10 10 466 346" ' +
    'style="position:absolute;left:10pt;top:10pt"><g stroke="#232120" stroke-opacity="0.032" stroke-width="0.5">""" + grid + r"""</g></svg>';
  // The paper pieces, each its own image in its section, under the vector parts.
  for (const p of """ + json.dumps(imgs) + r""") {
    const im = document.createElement("img"), [l, t, r, b] = p.box;
    im.src = p.src; im.setAttribute("data-ai-layer", p.sect);
    im.style.cssText = `position:absolute;left:${l}pt;top:${t}pt;width:${r - l}pt;height:${b - t}pt`;
    bg.appendChild(im);
  }
  while (bg.firstChild) document.body.insertBefore(bg.firstChild, art);
  // Vector shapes and text: each element carries its own section.
  for (const el of art.querySelectorAll("svg.gfx, h1.title, p, .ent")) {
    if (el.closest('[data-ai-layer="CERF example"]')) continue;
    const sect = section(el);
    if (!sect) throw new Error("no section for " + el.outerHTML.slice(0, 80));
    if (el.matches("svg")) el.setAttribute("data-ai-layer", sect); else el.setAttribute("data-ai-text-layer", sect);
  }
  // CERF example: its vector shapes and text, whatever they are.
  const cerf = art.querySelector('[data-ai-layer="CERF example"]');
  cerf.setAttribute("data-ai-text-layer", "CERF example");
  for (const el of cerf.querySelectorAll("svg.gfx")) el.setAttribute("data-ai-layer", "CERF example");
  // The old wrapper layers would tie with each other: remove them.
  for (const w of art.querySelectorAll(":scope > div[data-ai-layer]")) w.removeAttribute("data-ai-layer");
  for (const w of art.querySelectorAll(":scope > div[data-ai-text-layer]"))
    if (w !== cerf) w.removeAttribute("data-ai-text-layer");
  for (const el of document.querySelectorAll("[data-ai-name]")) el.removeAttribute("data-ai-name");
  document.currentScript.remove();
"""), dump=True)
assert "data-ai-name" not in built and 'filter="url(' not in built and "background_paper.png" in built
OUT.write_text("<!doctype html>\n" + built)
print(f"{OUT.relative_to(root.parent)}  ({len(imgs)} paper images)")
