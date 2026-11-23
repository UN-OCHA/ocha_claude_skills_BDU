"""Merge the per-slide .ai files into ONE Illustrator file with one artboard per slide.

Each slide's layers keep their names, prefixed with the slide number ("03 Text", "03 Lettering
(replace)"), and their artwork moves to its own artboard, left to right with a gap.
Live text stays live (items are duplicated, not flattened).

Run:  python3 <skill>/scripts/export_ai/merge_ai.py slide1.ai ... slide5.ai -o <job>/<name>.ai
(Make each page's .ai with export_ai.py into a temporary folder first, then merge.)
Needs Adobe Illustrator 2024+ (driven through osascript, like export_ai.py).
"""
import argparse
import glob
import json
import os
import subprocess
import tempfile

GAP = 100  # points between artboards

JSX = r"""
(function () {
var A = ARGS;
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var base = app.open(new File(A.files[0]));
var ab0 = base.artboards[0].artboardRect;           // [left, top, right, bottom]
var W = ab0[2] - ab0[0];
function prefixLayers(doc, n) {
  for (var i = 0; i < doc.layers.length; i++) {
    var L = doc.layers[i]; L.locked = false; L.visible = true;
    L.name = n + " " + L.name;
  }
}
prefixLayers(base, "01");
base.artboards[0].name = "01";
for (var k = 1; k < A.files.length; k++) {
  var n = (k + 1 < 10 ? "0" : "") + (k + 1);
  var dx = k * (W + A.gap);
  var ab = base.artboards.add([ab0[0] + dx, ab0[1], ab0[2] + dx, ab0[3]]);
  ab.name = n;
  var src = app.open(new File(A.files[k]));
  var sab = src.artboards[0].artboardRect;
  var shift = ab0[0] + dx - sab[0];
  // bottom layer first, so each new layer is created above the previous one: stacking kept
  for (var i = src.layers.length - 1; i >= 0; i--) {
    var SL = src.layers[i]; SL.locked = false; SL.visible = true;
    var TL = base.layers.add(); TL.name = n + " " + SL.name;
    var items = [];
    for (var j = 0; j < SL.pageItems.length; j++) items.push(SL.pageItems[j]);
    for (var j = 0; j < items.length; j++) {        // top item first, each placed at the end: order kept
      if (items[j].locked) items[j].locked = false;
      var d = items[j].duplicate(TL, ElementPlacement.PLACEATEND);
      d.translate(shift, ab0[1] - sab[1]);
    }
  }
  src.close(SaveOptions.DONOTSAVECHANGES);
}
var opts = new IllustratorSaveOptions();
opts.pdfCompatible = true;
base.saveAs(new File(A.out), opts);
var info = {artboards: base.artboards.length, layers: base.layers.length};
base.close(SaveOptions.DONOTSAVECHANGES);
var f = new File(A.result); f.encoding = "UTF-8"; f.open("w"); f.write(info.toSource()); f.close();
})();
"ok";
"""


def illustrator_app():
    apps = sorted(glob.glob("/Applications/Adobe Illustrator 20*/Adobe Illustrator.app"))
    return os.environ.get("ILLUSTRATOR") or apps[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("-o", "--output", required=True)
    a = ap.parse_args()
    files = [os.path.abspath(f) for f in a.files]
    out = os.path.abspath(a.output)
    stage = tempfile.mkdtemp(prefix="merge_ai_")
    result = os.path.join(stage, "result.txt")
    path = os.path.join(stage, "merge.jsx")
    with open(path, "w", encoding="utf-8") as f:
        f.write("var ARGS = " + json.dumps({"files": files, "out": out, "gap": GAP, "result": result}) + ";\n" + JSX)
    r = subprocess.run(["osascript", "-e",
                        f'tell application "{illustrator_app()}" to do javascript (POSIX file "{path}" as alias)'],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit("Illustrator stopped with: " + r.stderr.strip())
    print(open(result, encoding="utf-8").read() if os.path.exists(result) else "no result written")
    print("AI:", out)


if __name__ == "__main__":
    main()
