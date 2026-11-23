// For the check: outline every text object of each file (in memory, never saved) and report
// the bounds of every letter, so export_ai.py can compare the .ai against the PDF letter by letter.

function letters(path, isPdf) {
  var doc = isPdf ? openPdf(path) : app.open(new File(path)), out = [];
  try {
    var frames = [];
    for (var i = 0; i < doc.textFrames.length; i++) frames.push(doc.textFrames[i]);
    for (var i = 0; i < frames.length; i++) {
      var g = frames[i].createOutline();
      for (var j = 0; j < g.pageItems.length; j++) out.push(round2(g.pageItems[j].geometricBounds));
    }
  } finally { doc.close(SaveOptions.DONOTSAVECHANGES); }
  return out;
}
writeResult({ pdf: letters(ARGS.pdf, true), ai: letters(ARGS.ai, false) });
"ok";
