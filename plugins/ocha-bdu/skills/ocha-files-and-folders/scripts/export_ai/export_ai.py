"""Export an HTML page or an SVG as an editable Adobe Illustrator file (.ai).

    python3 export_ai.py page.html  [-o page.ai] [--no-check]
    python3 export_ai.py chart.svg  [-o chart.ai]

What you get: the page's vector artwork exactly as Chrome draws it, with
  - live text: one text object per block (heading, paragraph, label...), in the real fonts,
    sizes, colours, tracking and leading, bold runs kept, aligned left / right / centre as on
    the page, so text grows the right way when edited;
  - layers: from data-ai-* tags in the source (see SKILL.md), otherwise Text / Graphics /
    Background.

How: Chrome lays the page out once; from that one layout it prints a PDF (artwork and text
positions) and reports the page's structure (which letters form a block, alignment, tags).
Illustrator opens the PDF - which on its own gives one text box per letter - and this script
replaces those letters with real text blocks and sorts the artwork into layers. Every letter
is matched against the page's text; anything that can't be matched is left as it was imported
and reported, never dropped. The result is then checked letter by letter against the PDF.

Needs: macOS, Google Chrome, Adobe Illustrator (2024 or later) and the page's fonts installed.
Python standard library only (the optional pixel check uses Pillow + numpy if present).

Tests, after changing anything here - each should report no solid pixel differences:
    python3 export_ai.py tests/bar_chart.svg -o /tmp/bar_chart.ai     (SVG, tags, rotated label)
    python3 export_ai.py tests/features.html -o /tmp/features.ai      (untagged page: centred,
        letter-spaced, justified, text round floats, bullets, forced line break)
"""
import argparse, glob, json, os, re, shutil, statistics, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from chrome import Chrome  # noqa: E402

LIGATURES = {"\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl", "\ufb03": "ffi", "\ufb04": "ffl"}
LINE_BREAK = "\u0003"        # Illustrator's forced line break: the block stays one paragraph
SPACES = " \u00a0\n\t"


def fail(msg):
    sys.exit("export_ai: " + msg)


# ------------------------------------------------------------------------------ Illustrator ---
def illustrator_app():
    if os.environ.get("ILLUSTRATOR"):
        return os.environ["ILLUSTRATOR"]
    apps = sorted(glob.glob("/Applications/Adobe Illustrator 20*/Adobe Illustrator.app"))
    if not apps:
        fail("Adobe Illustrator not found - set ILLUSTRATOR=/path/to/Adobe Illustrator.app")
    return apps[-1]


def run_jsx(stage, name, args=None, code=None):
    """Run jsx/<name>.jsx (or `code`) in Illustrator with ARGS; return what it wrote as JSON."""
    result = os.path.join(stage, name + "_result.json")
    body = code if code is not None else (open(os.path.join(HERE, "jsx", "lib.jsx"), encoding="utf-8").read()
                                          + "\n" + open(os.path.join(HERE, "jsx", name + ".jsx"), encoding="utf-8").read())
    path = os.path.join(stage, name + ".jsx")
    with open(path, "w", encoding="utf-8") as f:
        # Illustrator keeps a script's global variables alive between runs (a leftover `R` once
        # made a later run skip its work and report stale data), so each script gets its own scope.
        f.write("(function () {\nvar ARGS = " + json.dumps(dict(args or {}, result=result)) + ";\n"
                + body + "\n})();\n\"ok\";\n")
    r = subprocess.run(["osascript", "-e",
                        f'tell application "{illustrator_app()}" to do javascript (POSIX file "{path}" as alias)'],
                       capture_output=True, text=True)
    if r.returncode:
        fail("Illustrator stopped with: " + r.stderr.strip().replace("\r", " "))
    if code is not None:
        return r.stdout.strip()
    return json.load(open(result, encoding="utf-8"))


def illustrator_ready(stage, out):
    """Wait until Illustrator answers scripts (it may be starting), and make sure the output isn't open."""
    code = ('var o = []; for (var i = 0; i < app.documents.length; i++) '
            '{ try { o.push(app.documents[i].fullName.fsName); } catch (e) {} } o.join("\\n");')
    for _ in range(40):
        path = os.path.join(stage, "ping.jsx")
        open(path, "w").write(code)
        r = subprocess.run(["osascript", "-e",
                            f'tell application "{illustrator_app()}" to do javascript (POSIX file "{path}" as alias)'],
                           capture_output=True, text=True)
        if r.returncode == 0:
            if os.path.abspath(out) in [os.path.abspath(p) for p in r.stdout.strip().split("\n") if p]:
                fail(f"{os.path.basename(out)} is open in Illustrator - close it first, then run again.")
            return
        time.sleep(5)
    fail("Illustrator isn't answering. Open it, close any dialog it shows, and run again.")


# ----------------------------------------------------------------------------------- Chrome ---
SVG_PAGE = """<!doctype html><html><head><meta charset="utf-8"><base href="{base}">
<style>html,body{{margin:0;padding:0;background:transparent}}svg{{display:block}}</style>
</head><body>{svg}</body></html>"""


def svg_size(svg):
    root = re.search(r"<svg\b[^>]*>", svg, re.S).group(0)

    def attr(name):
        m = re.search(rf'\b{name}\s*=\s*["\']([^"\']+)["\']', root)
        return m.group(1) if m else None

    def px(v):
        m = re.fullmatch(r"\s*([\d.]+)\s*(px|pt|mm|cm|in)?\s*", v or "")
        if not m:
            return None
        return float(m.group(1)) * {"px": 1, None: 1, "pt": 4 / 3, "mm": 96 / 25.4, "cm": 96 / 2.54, "in": 96}[m.group(2)]

    w, h = px(attr("width")), px(attr("height"))
    if not (w and h) and attr("viewBox"):
        _, _, w, h = [float(v) for v in re.split(r"[\s,]+", attr("viewBox").strip())]
    if not (w and h):
        fail("the SVG has no width/height or viewBox")
    return w, h


def lay_out(src, stage):
    """Lay the page out in Chrome; return (pdf path, structure, px-to-pt scale)."""
    measure = open(os.path.join(HERE, "measure.js"), encoding="utf-8").read()
    with Chrome() as chrome:
        if src.lower().endswith(".svg"):
            # SVG: 1 SVG px = 1 pt, as when Illustrator opens an SVG itself.
            svg = open(src, encoding="utf-8").read()
            svg = re.sub(r"<\?xml[^>]*\?>|<!DOCTYPE[^>]*>", "", svg, flags=re.I)
            w, h = svg_size(svg)
            page = os.path.join(stage, "page.html")
            open(page, "w", encoding="utf-8").write(
                SVG_PAGE.format(base="file://" + os.path.dirname(os.path.abspath(src)) + "/", svg=svg))
            chrome.load("file://" + page)
            pdf = chrome.pdf(printBackground=True, preferCSSPageSize=False, scale=4 / 3,
                             paperWidth=w / 72, paperHeight=h / 72,
                             marginTop=0, marginBottom=0, marginLeft=0, marginRight=0)
            scale, vw, vh = 1.0, w, h
        else:
            # HTML: CSS px to pt at 0.75, so a 210mm page stays 210mm.
            chrome.load("file://" + os.path.abspath(src))
            pdf = chrome.pdf(printBackground=True, preferCSSPageSize=True)
            box = re.search(rb"/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\]", pdf)
            if not box:
                fail("couldn't read the page size of Chrome's PDF")
            scale = 0.75
            vw, vh = float(box.group(3)) / scale, float(box.group(4)) / scale
        pages = len(re.findall(rb"/Type\s*/Page\b(?!s)", pdf))
        if pages != 1:
            fail(f"the page prints as {pages} pages - export_ai handles one page at a time")
        # Measure the same layout the PDF was printed from: print media, one page wide.
        chrome.call("Emulation.setEmulatedMedia", media="print")
        chrome.call("Emulation.setDeviceMetricsOverride", width=round(vw), height=round(vh),
                    deviceScaleFactor=1, mobile=False)
        structure = json.loads(chrome.evaluate(measure))
    path = os.path.join(stage, "page.pdf")
    open(path, "wb").write(pdf)
    return path, structure, scale


# ---------------------------------------------------------------------------- text matching ---
def text_space(f):
    """A fragment in its own reading direction: x along the baseline, y up. None if the angle
    isn't a multiple of 90 degrees (left as imported)."""
    q = round(f["angle"] / 90) * 90
    if abs(f["angle"] - q) > 0.5:
        return None
    q %= 360
    (ax, ay), b = f["anchor"], f["bounds"]
    w = b[2] - b[0] if q in (0, 180) else b[1] - b[3]
    x, y = {0: (ax, ay), 90: (ay, -ax), 180: (-ax, -ay), 270: (-ay, ax)}[q]
    return q, x, y, w


def to_world(q, x, y):
    return {0: (x, y), 90: (-y, x), 180: (-x, -y), 270: (y, -x)}[q]


def pieces_from(frames):
    """Fragments -> pieces: runs of fragments on one baseline with no wide gap."""
    ts = []
    for i, f in enumerate(frames):
        if f["kind"] != "TextType.POINTTEXT":
            continue
        t = text_space(f)
        if t is None:
            continue
        q, x, y, w = t
        ts.append(dict(i=i, q=q, x=x, y=y, right=x + w, size=f["size"], font=f["font"], colour=f["colour"],
                       text="".join(LIGATURES.get(c, c) for c in f["text"])))
    ts.sort(key=lambda t: (t["q"], -round(t["y"], 1), t["x"]))
    pieces = []
    for t in ts:
        p = pieces[-1] if pieces else None
        if (p and p["q"] == t["q"] and abs(p["y"] - t["y"]) < 0.05
                and t["x"] - p["frames"][-1]["right"] < 1.0 * max(p["size"], t["size"])):
            p["frames"].append(t)
            p["size"] = max(p["size"], t["size"])
        else:
            pieces.append(dict(q=t["q"], y=t["y"], size=t["size"], frames=[t]))
    for p in pieces:
        ink = [t for t in p["frames"] if t["text"].strip()] or p["frames"]
        p["left"], p["right"] = min(t["x"] for t in ink), max(t["right"] for t in ink)
        p["stripped"] = "".join(re.sub(r"\s", "", t["text"]) for t in p["frames"])
    return [p for p in pieces if p["stripped"]] , [p for p in pieces if not p["stripped"]]


def strip(s):
    return re.sub(r"\s", "", s)


def match_blocks(blocks, pieces):
    """Group pieces into the page's text blocks. Returns [(block, lines)], unmatched pieces."""
    todo = {}
    for bi, b in enumerate(blocks):
        todo.setdefault(strip(b["text"]), []).append(bi)
    keys = list(todo)

    def prefix(s):
        return any(k.startswith(s) for k in keys if todo[k])

    free = sorted(pieces, key=lambda p: (p["q"], -p["y"], p["left"]))
    matched, unmatched = [], []
    while free:
        start = free[0]
        lines, got, used, best = [[start]], start["stripped"], [start], None
        if todo.get(got):
            best = ([list(l) for l in lines], list(used))
        while prefix(got):
            line = lines[-1]
            lo = min(p["left"] for l in lines for p in l) - lines[0][0]["size"]
            hi = max(p["right"] for l in lines for p in l) + lines[0][0]["size"]
            same = [p for p in free if p not in used and p["q"] == start["q"] and abs(p["y"] - line[0]["y"]) < 0.05
                    and 0 <= p["left"] - line[-1]["right"] + 0.5 < 4 * p["size"] and prefix(got + p["stripped"])]
            below = [p for p in free if p not in used and p["q"] == start["q"]
                     and 0.3 * p["size"] < line[0]["y"] - p["y"] < 2.2 * max(p["size"], line[0]["size"])
                     and p["right"] > lo and p["left"] < hi and prefix(got + p["stripped"])]
            if same:
                nxt = min(same, key=lambda p: p["left"])
                line.append(nxt)
            elif below:
                top = max(p["y"] for p in below)
                nxt = min((p for p in below if abs(p["y"] - top) < 0.05), key=lambda p: p["left"])
                lines.append([nxt])
            else:
                break
            used.append(nxt)
            got += nxt["stripped"]
            if todo.get(got):
                best = ([list(l) for l in lines], list(used))
        if best:
            blines, bused = best
            key = "".join(p["stripped"] for l in blines for p in l)
            matched.append((blocks[todo[key].pop(0)], blines))
            for p in bused:
                free.remove(p)
        else:
            unmatched.append(free.pop(0))
    missing = [blocks[i] for k in keys for i in todo[k]]
    return matched, unmatched, missing


class NoFit(Exception):
    pass


def lay_chars(block, lines):
    """Pair every character of the block's text with a fragment; mark line breaks and gaps."""
    tokens = []
    for n, line in enumerate(lines):
        prev = None
        for piece in line:
            for f in piece["frames"]:
                for j, c in enumerate(f["text"]):
                    tokens.append(dict(c=c, f=f, line=n, gap=(f["x"] - prev["right"]) if (j == 0 and prev) else None))
                prev = f
    chars, k = [], 0

    def brk(f):
        if not chars or chars[-1]["c"] != LINE_BREAK:
            chars.append(dict(c=LINE_BREAK, f=f, gap=None, word_gap=None, add=0.0))

    for s in block["text"]:
        if s in SPACES:
            if k < len(tokens) and tokens[k]["c"].isspace():            # a space Chrome drew
                edge = ((k > 0 and tokens[k]["line"] != tokens[k - 1]["line"])
                        or (k + 1 < len(tokens) and tokens[k + 1]["line"] != tokens[k]["line"]))
                if edge:
                    brk(tokens[k]["f"])
                else:
                    chars.append(dict(c=s if s != "\n" else " ", f=tokens[k]["f"], gap=tokens[k]["gap"], word_gap=None, add=0.0))
                k += 1
            elif 0 < k < len(tokens) and tokens[k]["line"] != tokens[k - 1]["line"]:
                brk(tokens[k - 1]["f"])
            elif 0 < k < len(tokens) and tokens[k]["gap"] is not None:  # a space that is only a gap
                chars.append(dict(c=s if s != "\n" else " ", f=tokens[k - 1]["f"], gap=None, word_gap=tokens[k]["gap"], add=0.0))
                tokens[k]["gap"] = None
            else:
                raise NoFit("no space in the PDF where the page has one")
            continue
        while k < len(tokens) and tokens[k]["c"].isspace():             # a drawn space the text doesn't have
            k += 1
        if k >= len(tokens) or tokens[k]["c"] != s:
            raise NoFit(f"letter mismatch: page {s!r}, PDF {tokens[k]['c'] if k < len(tokens) else 'nothing'!r}")
        if k and tokens[k]["line"] != tokens[k - 1]["line"] and (not chars or chars[-1]["c"] != LINE_BREAK):
            brk(tokens[k - 1]["f"])                                       # a word broken across lines
        chars.append(dict(c=s, f=tokens[k]["f"], gap=tokens[k]["gap"], word_gap=None, add=0.0))
        k += 1
    if any(not t["c"].isspace() for t in tokens[k:]):
        raise NoFit("the PDF has more text than the page")
    return chars


def plan_text(matched, scale):
    """Turn matched blocks into text objects for build.jsx. Returns (plans, unconverted pieces)."""
    laid, failed = [], []
    word_gaps = {}
    for block, lines in matched:
        try:
            chars = lay_chars(block, lines)
        except NoFit as e:
            failed.append((block, lines, str(e)))
            continue
        for i, ch in enumerate(chars):
            sz = round(ch["f"]["size"], 2)
            if ch["word_gap"] is not None:
                word_gaps.setdefault(sz, []).append(ch["word_gap"])
        laid.append((block, lines, chars))
    space = {s: statistics.median(g) for s, g in word_gaps.items()}

    plans = []
    for block, lines, chars in laid:
        # Letter-spacing comes from the page's CSS: the gaps in the PDF can't give it, because
        # Chrome only starts a new fragment where kerning or spacing moves a letter.
        tr = block.get("letterSpacing", 0) * scale
        # Gaps wider than normal are layout, not type (e.g. padding round a highlight): they go
        # on as extra tracking on the letter before. Kerning makes gaps narrower, never 0.5pt wider.
        # Justified text stretches every space a little, so there every gap is carried exactly.
        least = 0.02 if block["align"] == "justify" else 0.5
        for i, ch in enumerate(chars):
            sz = round(ch["f"]["size"], 2)
            if ch["word_gap"] is not None and ch["word_gap"] - space[sz] > least:
                ch["add"] += ch["word_gap"] - space[sz]
            elif ch["gap"] is not None and i and chars[i - 1]["c"] != LINE_BREAK and ch["gap"] - tr > least:
                chars[i - 1]["add"] += ch["gap"] - tr
        sizes = [ch["f"]["size"] for ch in chars if ch["c"] not in SPACES + LINE_BREAK]
        q = lines[0][0]["q"]
        geo = [dict(y=l[0]["y"], left=min(p["left"] for p in l), right=max(p["right"] for p in l)) for l in lines]
        label = block["name"] or re.sub(r"\s+", " ", block["text"])[:40]
        layer = block["layer"] or "Text"
        align = block["align"]
        leads = [a["y"] - b["y"] for a, b in zip(geo, geo[1:])]

        def make(seg, x, y, indent, just, leading, lab, group=None):
            wx, wy = to_world(q, x, y)
            return dict(label=lab, layer=layer, group=group, x=wx, y=wy, angle=q, just=just, indent=indent,
                        leading=leading, runs=runs_of(seg, tr))

        fits, x, indent = True, None, 0.0
        if leads and max(leads) - min(leads) > 1.0:
            fits = False
        elif align in ("left", "justify"):
            rest = [g["left"] for g in geo[1:]] or [geo[0]["left"]]
            fits = max(rest) - min(rest) < 0.3
            x = min(rest)
            indent = geo[0]["left"] - x
        elif align == "right":
            r = [g["right"] for g in geo]
            fits, x = max(r) - min(r) < 0.3, max(r)
        else:
            c = [(g["left"] + g["right"]) / 2 for g in geo]
            fits, x = max(c) - min(c) < 0.3, statistics.mean(c)
        just = "left" if align == "justify" else align
        if fits:
            # Leading: Chrome snaps each line to whole pixels, so its spacing wobbles round the CSS
            # line-height (12.75/12.0 for 12.6). Of the CSS value and the measured average, keep
            # whichever puts the lines closer to where Chrome drew them (the CSS one on a near-tie).
            leading = 0
            if leads:
                ys = [g["y"] for g in geo]

                def worst(L):
                    return max(abs(ys[0] - n * L - y) for n, y in enumerate(ys))
                css = (block.get("lineHeight") or 0) * scale
                leading = statistics.mean(leads)
                if css and worst(css) <= worst(leading) + 0.05:
                    leading = css
            plans.append(make(chars, x, geo[0]["y"], indent, just, round(leading, 3), label))
        else:
            # Lines that don't share an edge (text wrapped round something, uneven spacing):
            # one text object per line, grouped under the block's name.
            segs, cur = [], []
            for ch in chars:
                if ch["c"] == LINE_BREAK:
                    segs.append(cur)
                    cur = []
                else:
                    cur.append(ch)
            segs.append(cur)
            for n, (seg, g) in enumerate(zip(segs, geo)):
                sx = {"right": g["right"], "center": (g["left"] + g["right"]) / 2}.get(align, g["left"])
                plans.append(make(seg, sx, g["y"], 0.0, just, 0, f"{label} (line {n + 1})", group=label))
    unconverted = [p for block, lines, _ in failed for l in lines for p in l]
    return plans, unconverted, failed


def runs_of(chars, tr):
    """Style runs. Tracking is in 1/1000 em of each run's own size: the page's letter-spacing,
    plus any extra room after that letter."""
    runs = []
    for ch in chars:
        f = ch["f"]
        style = (f["font"], round(f["size"], 2), f["colour"], round((tr + ch["add"]) / f["size"] * 1000))
        if runs and runs[-1]["style"] == style:
            runs[-1]["text"] += ch["c"]
        else:
            runs.append(dict(style=style, text=ch["c"]))
    return [dict(font=r["style"][0], size=r["style"][1], colour=r["style"][2], tracking=r["style"][3], text=r["text"])
            for r in runs]


# ------------------------------------------------------------------------------------ layers ---
def calibrate(matched, page_h, scale):
    """Offset from the page's CSS px to the PDF's points, from where each block's first letter is."""
    dx, dy = [], []
    for block, lines in matched:
        f = lines[0][0]["frames"][0]
        if lines[0][0]["q"] or not block.get("first"):
            continue
        l, t, r, b = block["first"]
        size = block["size"] * scale
        dx.append(lines[0][0]["left"] - l * scale)
        dy.append((page_h - f["y"]) - ((t + b) / 2 * scale + 0.34 * size))
    return (statistics.median(dx), statistics.median(dy)) if dx else (0.0, 0.0)


def assign_layers(dump, structure, matched_frames, frame_layer, plans_layers, scale, offset):
    page = dump["page"]
    page_h, page_area = page[1] - page[3], (page[2] - page[0]) * (page[1] - page[3])
    dx, dy = offset
    tags = []
    for t in structure["tags"]:
        for l, top, r, b in t["rects"]:
            box = [l * scale + dx, page_h - (top * scale + dy), r * scale + dx, page_h - (b * scale + dy)]
            tags.append((box, (box[2] - box[0]) * (box[1] - box[3]), t["layer"], t["group"]))
    assign, where = [], []
    for s, it in enumerate(dump["items"]):
        b = it["bounds"]
        if it["type"] == "TextFrame":
            if it["text"] in matched_frames:
                assign.append(None)
                where.append((frame_layer[it["text"]], s, b))
            else:
                assign.append(["Text (not converted)", None])
                where.append(("Text (not converted)", s, b))
            continue
        # The smallest tagged area that holds the whole object; failing that, its centre.
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        hits = [t for t in tags if t[0][0] - 1 <= b[0] and b[2] <= t[0][2] + 1 and t[0][3] - 1 <= b[3] and b[1] <= t[0][1] + 1]
        if not hits:
            hits = [t for t in tags if t[0][0] - 0.5 <= cx <= t[0][2] + 0.5 and t[0][3] - 0.5 <= cy <= t[0][1] + 0.5]
        if hits:
            _, _, layer, group = min(hits, key=lambda t: t[1])
            layer = layer or "Graphics"
        else:
            ix = max(0, min(b[2], page[2]) - max(b[0], page[0])) * max(0, min(b[1], page[1]) - max(b[3], page[3]))
            layer, group = ("Background" if ix >= 0.9 * page_area else "Graphics"), None
        assign.append([layer, group])
        where.append((layer, s, b))

    # Order the layers so that wherever two objects overlap, the one that was on top stays on top.
    votes = {}
    ws = sorted(where, key=lambda w: w[2][0])
    for i, (la, sa, ba) in enumerate(ws):
        for lb, sb, bb in ws[i + 1:]:
            if bb[0] >= ba[2]:
                break
            if la == lb or min(ba[1], bb[1]) - max(ba[3], bb[3]) <= 0.01 or min(ba[2], bb[2]) - bb[0] <= 0.01:
                continue
            up, down = (la, lb) if sa < sb else (lb, la)
            votes[(up, down)] = votes.get((up, down), 0) + 1
    names = sorted({w[0] for w in where} | set(plans_layers))
    median = {n: statistics.median([w[1] for w in where if w[0] == n] or [0]) for n in names}
    # Net evidence only (a few underlines drawn over a few letters shouldn't outvote hundreds the
    # other way); with nothing forcing it, text layers go on top, then the original stacking.
    order, left = [], set(names)
    while left:
        best = min(left, key=lambda n: (sum(max(0, votes.get((m, n), 0) - votes.get((n, m), 0)) for m in left if m != n),
                                         0 if n in plans_layers else 1, median[n]))
        order.append(best)
        left.remove(best)
    clashes = {f"{a} over {b}": v for (a, b), v in votes.items() if order.index(a) > order.index(b)}
    return assign, order, clashes


# ------------------------------------------------------------------------------------- check ---
def check(stage, pdf, out):
    got = run_jsx(stage, "outline", dict(pdf=pdf, ai=out))
    a, b = got["pdf"], got["ai"]
    offs = []
    for g in a:
        h = min(b, key=lambda h: abs(h[0] - g[0]) + abs(h[1] - g[1]) + abs(h[2] - g[2]) + abs(h[3] - g[3])) if b else None
        offs.append(max(abs(h[0] - g[0]), abs(h[1] - g[1])) if h else 99)
    report = dict(letters_pdf=len(a), letters_ai=len(b),
                  median=statistics.median(offs) if offs else 0, worst=max(offs) if offs else 0,
                  over_half_pt=sum(o > 0.5 for o in offs))
    try:
        from PIL import Image, ImageChops, ImageFilter
        import numpy as np
        for f in (pdf, out):
            subprocess.run(["qlmanage", "-t", "-s", "2400", "-o", stage, f], capture_output=True)
        pa = Image.open(os.path.join(stage, os.path.basename(pdf) + ".png")).convert("L")
        pb = Image.open(os.path.join(stage, os.path.basename(out) + ".png")).convert("L").resize(pa.size)
        d = np.asarray(ImageChops.difference(pa, pb)) > 90
        blobs = Image.fromarray((d * 255).astype("uint8")).filter(ImageFilter.MinFilter(9))
        report["solid_differences"] = int((np.asarray(blobs) > 0).sum())
        if report["solid_differences"]:
            over = pa.convert("RGB")
            over.paste(Image.new("RGB", pa.size, (255, 0, 0)), mask=blobs.filter(ImageFilter.MaxFilter(25)))
            report["diff_image"] = os.path.splitext(out)[0] + "_differences.png"
            over.save(report["diff_image"])
    except ImportError:
        report["solid_differences"] = "not checked (needs Pillow and numpy)"
    return report


# -------------------------------------------------------------------------------------- main ---
def main():
    ap = argparse.ArgumentParser(description="Export an HTML page or SVG as an editable Illustrator file.")
    ap.add_argument("input")
    ap.add_argument("-o", "--output")
    ap.add_argument("--no-check", action="store_true", help="skip the letter-by-letter check")
    a = ap.parse_args()
    src = os.path.abspath(a.input)
    if not os.path.exists(src) or not os.path.getsize(src):
        fail(f"{src} is missing or 0 bytes (a Dropbox online-only file? Make it available offline).")
    out = os.path.abspath(a.output or os.path.splitext(src)[0] + ".ai")
    stage = tempfile.mkdtemp(prefix="export_ai_")
    try:
        illustrator_ready(stage, out)
        pdf, structure, scale = lay_out(src, stage)
        dump = run_jsx(stage, "dump", dict(pdf=pdf))
        page_h = dump["page"][1] - dump["page"][3]
        pieces, _blank = pieces_from(dump["frames"])
        matched, unmatched, missing = match_blocks(structure["blocks"], pieces)
        plans, unconverted, failed = plan_text(matched, scale)
        ok_blocks = [(b, l) for b, l in matched if not any(b is fb for fb, _, _ in failed)]
        matched_frames, frame_layer = set(), {}
        for block, lines in ok_blocks:
            for l in lines:
                for p in l:
                    for f in p["frames"]:
                        matched_frames.add(f["i"])
                        frame_layer[f["i"]] = block["layer"] or "Text"
        # Fragments that are only a space draw nothing: remove them with the matched text.
        text_layers = sorted({p["layer"] for p in plans}) or ["Text"]
        for p in _blank:
            for f in p["frames"]:
                matched_frames.add(f["i"])
                frame_layer[f["i"]] = "Text" if "Text" in text_layers else text_layers[0]
        offset = calibrate(ok_blocks, page_h, scale)
        assign, order, clashes = assign_layers(dump, structure, matched_frames, frame_layer,
                                               {p["layer"] for p in plans}, scale, offset)
        res = run_jsx(stage, "build", dict(pdf=pdf, out=out, items=[i["bounds"] for i in dump["items"]],
                                           assign=assign, layers=order, texts=plans))
        print(f"AI: {out}")
        print("Layers (objects): " + ", ".join(res["layers"]))
        print(f"Text: {len(ok_blocks)} blocks as {len(plans)} text objects")
        if unmatched or unconverted:
            n = sum(len(p["frames"]) for p in unmatched) + sum(len(p["frames"]) for p in unconverted)
            print(f"  NOT converted, left as imported ({n} fragments, layer 'Text (not converted)'):")
            for p in unmatched[:8]:
                print(f"    - {p['stripped'][:50]!r} (not in the page's text: generated content, list bullet?)")
            for b, _, why in failed[:8]:
                print(f"    - {b['text'][:50]!r}: {why}")
        if missing:
            print(f"  {len(missing)} text block(s) of the page not in the PDF (hidden or clipped): "
                  + "; ".join(repr(b["text"][:30]) for b in missing[:5]))
        clash_note = ("where these overlap, the stacking changed (was " +
                      ", ".join(f"{k} x{v}" for k, v in clashes.items()) + ")") if clashes else ""
        if clash_note and a.no_check:
            print(f"  Warning: {clash_note}. Run without --no-check to see if it shows.")
        if not a.no_check:
            r = check(stage, pdf, out)
            print(f"Check: {r['letters_ai']} letters vs {r['letters_pdf']} in the PDF; median offset "
                  f"{r['median']:.2f}pt, worst {r['worst']:.2f}pt, {r['over_half_pt']} over 0.5pt; "
                  f"solid pixel differences: {r['solid_differences']}")
            if r.get("diff_image"):
                print(f"  Differences marked in red: {r['diff_image']}")
                if clash_note:
                    print(f"  Likely cause: {clash_note}. Tag those elements into one layer.")
    finally:
        shutil.rmtree(stage, ignore_errors=True)


if __name__ == "__main__":
    main()
