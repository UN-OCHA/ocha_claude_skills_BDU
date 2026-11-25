"""Make the source for the editable .ai from the final template.

  python3 tools/make_ai_source.py
    -> tools/ai_layers/paper_texture.png        the ground: paper colour, stains, grain, fibres, crumple (no grid)
    -> tools/ai_layers/paper_edges_shadows.png  torn edges, shadows and ink of the paper pieces, transparent background
    -> tools/un_drf_platform_ai.html            the vector page: the two images on their own layers at the bottom,
                                                the grid as real lines, then the vector parts: all text, arrows,
                                                dashed lines, the blue circle, blasts and the CERF chart
  then: ocha-bdu-files-and-folders export_ai on tools/un_drf_platform_ai.html -> un_drf_platform.ai

Rule (user, 25 Nov 2026): what isn't vector goes into the .ai as images, each on its own layer, so the .ai looks like
the final and everything vector stays editable.

The Newsprint look uses raster SVG filters and blend modes. Chrome prints any element with a filter as an image, so
the vector page strips them and the images carry that look instead.

Load-bearing: the vector page also strips every data-ai-name. With named groups the exporter dropped the arrows, the
side badges, the trigger burst and two label strips from the .ai (24 Nov 2026, ~22,000 pixel differences).
"""
import re, sys, pathlib, subprocess

root = pathlib.Path(__file__).resolve().parent
SRC = root / (sys.argv[1] if len(sys.argv) > 1 else "un_drf_platform.html")
OUT = root / (sys.argv[2] if len(sys.argv) > 2 else SRC.stem + "_ai.html")
LAYERS = root / "ai_layers"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
s = SRC.read_text()

GRAIN = re.compile(r'<svg class="grain".*?</svg>\n?', re.S)
CRUMPLE = re.compile(r'<svg width="486pt" height="366pt" style="position:absolute;left:0;top:0;pointer-events:none;'
                     r'mix-blend-mode:multiply;opacity:[\d.]+">.*?</svg>\n?', re.S)
GRID = re.compile(r', linear-gradient\(var\(--grid-line\) 0\.5pt, transparent 0\.5pt\), linear-gradient\(90deg, '
                  r'var\(--grid-line\) 0\.5pt, transparent 0\.5pt\)')
for name, rx in (("grain", GRAIN), ("crumple", CRUMPLE), ("grid", GRID)):
    assert rx.search(s), f"anchor for the {name} layer not found: the template changed, update this script"


def render(html, png, transparent=False):
    tmp = LAYERS / "_render.html"
    tmp.write_text(html)
    args = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=3.125",
            "--window-size=648,488", f"--screenshot={png}"]
    if transparent:
        args.append("--default-background-color=00000000")
    subprocess.run(args + [tmp.as_uri()], check=True, capture_output=True)
    tmp.unlink()
    assert png.exists() and png.stat().st_size > 0, f"{png.name} was not rendered"


LAYERS.mkdir(exist_ok=True)

# 1. Paper texture: the page with no grid and nothing on it.
texture = GRID.sub("", s).replace("</style>", "  .art { visibility: hidden; }\n</style>", 1)
render(texture, LAYERS / "paper_texture.png")

# 2. Paper edges, shadows and ink: only the paper pieces and the ink-speckled icons, on a transparent page.
#    Text, arrows, the flat circle and the ground are hidden; the vector layers above carry them.
edges = CRUMPLE.sub("", GRAIN.sub("", s))
edges = edges.replace("</style>", """  html, body { background: none !important; }
  .art, .art * { color: transparent !important; }
  .gfx { visibility: hidden !important; }
  .w::before, .mk::before { visibility: visible; }
</style>""", 1)
render(edges, LAYERS / "paper_edges_shadows.png", transparent=True)

# 3. The vector page.
v = CRUMPLE.sub("", GRAIN.sub("", s))
v = re.sub(r'background-image: radial-gradient[^;]*;', '', v, count=1, flags=re.S)
v = re.sub(r'\n\s*background-size: 100% 100%[^;]*;', '', v, count=1)
v = re.sub(r' filter="url\(#[a-z0-9]+\)"', '', v)
v = re.sub(r'filter: url\(#[a-z]+\);?', '', v)
v = v.replace('filter: var(--cut);', '').replace('mix-blend-mode: multiply;', '')
v = re.sub(r' data-ai-name="[^"]*"', '', v)
# The blue circle is in the edges image too: as a vector on its own layer it was stacked over the label text.
v = re.sub(r'<div class="blob"[^>]*></div>[^\n]*\n?', '', v, count=1)
# No page clipping: with body { overflow: hidden } Chrome clips every image to the page, both images read as
# page-sized and the exporter put them in the same layer.
v = v.replace("position: relative; overflow: hidden;", "position: relative;", 1)
# The paper pieces (badges, cards, label strips, marker, example sheet) and the icons on them live only in the
# edges image: as flat vector copies on top they would hide its torn edges, shadows and ink (user, 25 Nov 2026).
v = v.replace("</style>", """  .badge::before, .ent::before, .card::before, .sheet::before, .w::before, .mk::before { display: none !important; }
  .badge > svg, .card > svg { visibility: hidden !important; }
</style>""", 1)
# Each image/grid layer gets its own box, nested by size, because the exporter puts an object in the SMALLEST tagged
# box that holds it: page-sized boxes all tie and everything fell into the first layer (25 Nov 2026).
#   texture: the page (486 x 366)  >  grid: 10-476 x 10-356  >  edges: 12.5-473.5 x 12.5-353.5  >  artwork layers (15-471 x 15-351)
# The exporter allows 1pt of slack, so the boxes must differ by more than 1pt: with the edges box at 14-472 the image
# fell into the artwork layer. The grid lines run to 10 and 476, outside the edges box.
PX = 2025 / 486                                   # PNG pixels per point
from PIL import Image
E = (12.5, 12.5, 473.5, 353.5)
Image.open(LAYERS / "paper_edges_shadows.png").crop(tuple(round(c * PX) for c in E)).save(LAYERS / "paper_edges_shadows.png")
lines = "".join(f'<line x1="10" y1="{y}" x2="476" y2="{y}"/>' for y in range(12, 355, 12)) + \
        "".join(f'<line x1="{x}" y1="10" x2="{x}" y2="356"/>' for x in range(12, 475, 12))
box = lambda l, t, r, b: f"position:absolute;left:{l}pt;top:{t}pt;width:{r - l}pt;height:{b - t}pt"
images = (
    f'<div data-ai-layer="Paper texture (image)" style="{box(0, 0, 486, 366)}">'
    f'<img src="ai_layers/paper_texture.png" style="{box(0, 0, 486, 366)}"></div>\n'
    f'<div data-ai-layer="Grid" style="{box(10, 10, 476, 356)}">'
    '<svg width="466pt" height="346pt" viewBox="10 10 466 346" style="position:absolute;left:0;top:0">'
    f'<g stroke="#232120" stroke-opacity="0.032" stroke-width="0.5">{lines}</g></svg></div>\n'
    f'<div data-ai-layer="Paper edges and shadows (image)" style="{box(*E)}">'
    f'<img src="ai_layers/paper_edges_shadows.png" style="{box(0, 0, E[2] - E[0], E[3] - E[1])}"></div>\n')
v = v.replace('<div class="art">', images + '<div class="art">', 1)
assert 'filter="url(' not in v and 'data-ai-name' not in v and 'paper_texture.png' in v
OUT.write_text(v)
print(OUT.relative_to(root.parent))
