"""Make the vector source for the editable .ai from the final template.

  python3 tools/make_ai_source.py          -> tools/un_drf_platform_ai.html

The Newsprint look uses raster SVG filters (paper edges, ink speckle, marker swipe, grain, crumple) and blend modes.
Chrome prints any element with a filter as an image, so the .ai exporter turns them into pictures. This copy strips
them: same layout, live text, flat vector shapes. The paper texture is added back in Illustrator as a placed image
(the PNG) on its own locked layer, or simply left flat.

Load-bearing: it also strips every data-ai-name. With named groups the exporter dropped the arrows, the side badges,
the trigger burst and two label strips from the .ai (24 Nov 2026, ~22,000 pixel differences); without them: 0.
"""
import re, pathlib, sys
# usage: python3 make_ai_source.py <template.html> [<out.html>]  (defaults: the job template next to this script)
SRC = sys.argv[1] if len(sys.argv) > 1 else "un_drf_platform.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else SRC.replace(".html", "_ai.html")
root = pathlib.Path(__file__).resolve().parent
s = (root / SRC).read_text()
s = re.sub(r'<svg class="grain".*?</svg>\n?', '', s, flags=re.S)
s = re.sub(r'<svg width="486pt" height="366pt" style="position:absolute;left:0;top:0;pointer-events:none;mix-blend-mode:multiply;opacity:[\d.]+">.*?</svg>\n?', '', s, flags=re.S)
s = re.sub(r'background-image: radial-gradient[^;]*;', '', s, count=1, flags=re.S)
s = re.sub(r'\n\s*background-size: 100% 100%[^;]*;', '', s, count=1)
s = re.sub(r' filter="url\(#[a-z0-9]+\)"', '', s)
s = re.sub(r'filter: url\(#[a-z]+\);?', '', s)
s = s.replace('filter: var(--cut);', '').replace('mix-blend-mode: multiply;', '')
s = re.sub(r' data-ai-name="[^"]*"', '', s)
assert 'filter="url(' not in s and 'data-ai-name' not in s
(root / OUT).write_text(s)
print(OUT)
