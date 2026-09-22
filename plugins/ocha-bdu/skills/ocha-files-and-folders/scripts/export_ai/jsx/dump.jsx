// Read the Chrome PDF as Illustrator imports it: every text fragment (text, baseline, width,
// font, size, colour, angle) and every other object after unwrapping (visible bounds, stack order).
// Only whole-fragment attributes are read: looping over every letter's attributes crashes
// Illustrator 2026 (22 Sept 2026).

function readPdf() {
  var doc = openPdf(ARGS.pdf), R = { frames: [], items: [] };
  try {
    R.page = round2(doc.artboards[0].artboardRect);
    for (var i = 0; i < doc.textFrames.length; i++) {
      var t = doc.textFrames[i], ca = t.textRange.characterAttributes, m = t.matrix;
      R.frames.push({ text: t.contents, kind: String(t.kind), anchor: round2(t.anchor), bounds: round2(t.geometricBounds),
                      font: ca.textFont.name, size: ca.size, colour: colourKey(ca.fillColor),
                      angle: Math.atan2(m.mValueB, m.mValueA) * 180 / Math.PI });
    }
    nameTextFrames(doc);
    unwrapPageGroups(doc);
    var items = snapshot(doc);
    for (var i = 0; i < items.length; i++) {
      var it = items[i];
      R.items.push({ type: it.typename, text: it.typename == "TextFrame" ? +it.name.substr(3) : null,
                     bounds: round2(seenBounds(it)) });
    }
  } finally { doc.close(SaveOptions.DONOTSAVECHANGES); }
  return R;
}

// Illustrator 2026 sometimes fails the first text read after opening a document ("MRAP"
// parameter error, about every other run); opening it again and re-reading works.
var R, err;
for (var attempt = 0; attempt < 3 && !R; attempt++) { try { R = readPdf(); } catch (e) { err = e; } }
if (!R) throw err;
writeResult(R);
"ok";
