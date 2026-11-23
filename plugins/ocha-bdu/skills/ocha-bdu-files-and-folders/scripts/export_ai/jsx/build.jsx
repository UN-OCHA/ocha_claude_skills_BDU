// Build the editable .ai: open the Chrome PDF, unwrap it exactly as dump.jsx did, move every
// object into the layer and group export_ai.py chose, replace the matched text fragments with
// one text object per block, and save.

var doc = openPdf(ARGS.pdf), summary = [];
try {
  // Fonts first: stop before touching anything if one isn't installed.
  var fonts = {}, missing = [];
  for (var p = 0; p < ARGS.texts.length; p++)
    for (var r = 0; r < ARGS.texts[p].runs.length; r++) fonts[ARGS.texts[p].runs[r].font] = 1;
  for (var name in fonts) {
    try { fonts[name] = app.textFonts.getByName(name); } catch (e) { missing.push(name); }
  }
  if (missing.length) throw "Fonts not installed on this Mac: " + missing.join(", ") + ". Install them and run again.";

  nameTextFrames(doc);
  unwrapPageGroups(doc);
  var items = snapshot(doc);
  if (items.length != ARGS.items.length) throw "Illustrator unwrapped the PDF differently this time (" + items.length + " objects, expected " + ARGS.items.length + ")";
  for (var i = 0; i < items.length; i += 7) {
    var a = seenBounds(items[i]), b = ARGS.items[i];
    for (var k = 0; k < 4; k++) if (Math.abs(a[k] - b[k]) > 0.05) throw "object " + i + " moved between reading and building the PDF";
  }
  var oldLayers = [];
  for (var l = 0; l < doc.layers.length; l++) oldLayers.push(doc.layers[l]);

  // Layers, added bottom first so the Layers panel reads in ARGS.layers order.
  var layers = {};
  for (var l = ARGS.layers.length - 1; l >= 0; l--) {
    var ly = doc.layers.add();
    ly.name = ARGS.layers[l];
    layers[ARGS.layers[l]] = ly;
  }

  // Artwork: top of the stack first, each appended to the end of its layer or group, which
  // keeps the original order. A group is placed where its first object was.
  var groups = {}, doomed = [];
  for (var s = 0; s < items.length; s++) {
    var it = items[s], to = ARGS.assign[s];
    if (to === null) { doomed.push(it); continue; }
    var layer = layers[to[0]], target = layer;
    if (to[1]) {
      var key = to[0] + "|" + to[1];
      if (!groups[key]) {
        groups[key] = layer.groupItems.add();
        groups[key].name = to[1];
        groups[key].move(layer, ElementPlacement.PLACEATEND);
      }
      target = groups[key];
    }
    it.move(target, ElementPlacement.PLACEATEND);
    if (it.typename == "TextFrame") it.name = "Not converted: " + it.contents;
  }
  for (var i = 0; i < doomed.length; i++) doomed[i].remove();
  for (var l = 0; l < oldLayers.length; l++) {
    if (oldLayers[l].pageItems.length) throw oldLayers[l].pageItems.length + " objects left in the original layer";
    oldLayers[l].remove();
  }

  // Text, last block first so each layer lists its blocks top to bottom.
  var textGroups = {};
  for (var p = ARGS.texts.length - 1; p >= 0; p--) {
    var P = ARGS.texts[p], home = layers[P.layer];
    if (P.group) {
      var gk = P.layer + "|" + P.group;
      if (!textGroups[gk]) { textGroups[gk] = home.groupItems.add(); textGroups[gk].name = P.group; }
      home = textGroups[gk];
    }
    var text = "";
    for (var r = 0; r < P.runs.length; r++) text += P.runs[r].text;
    var tf = home.textFrames.pointText([P.x, P.y]);
    tf.contents = text;
    tf.name = P.label;
    var all = tf.textRange;
    // A plain lookup: a nested ?: here set right-aligned text to CENTER in Illustrator 2026.
    var JUST = { left: Justification.LEFT, right: Justification.RIGHT, center: Justification.CENTER };
    all.paragraphAttributes.justification = JUST[P.just];
    if (all.paragraphAttributes.justification != JUST[P.just]) throw P.label + ": alignment didn't take";
    all.paragraphAttributes.firstLineIndent = P.indent;
    all.paragraphAttributes.hyphenation = false;
    var at = 0;
    for (var r = 0; r < P.runs.length; r++) {
      var R = P.runs[r], rg = all.characters[at];
      if (R.text.charAt(0) != "\u0003" && rg.contents != R.text.charAt(0))
        throw P.label + ": run " + r + " starts on '" + rg.contents + "', expected '" + R.text.charAt(0) + "'";
      rg.length = R.text.length;
      var ca = rg.characterAttributes;
      ca.textFont = fonts[R.font];
      ca.size = R.size;
      ca.fillColor = makeColour(R.colour);
      ca.ligature = true;
      ca.autoLeading = !P.leading;
      if (P.leading) ca.leading = P.leading;
      // Letter-spacing plus any extra room after a letter (e.g. padding round a highlight), as
      // tracking: Illustrator ignores a scripted kerning value while auto kerning is on.
      ca.tracking = R.tracking;
      at += R.text.length;
    }
    if (all.characters.length != text.length) throw P.label + ": " + all.characters.length + " characters, expected " + text.length;
    if (P.angle) {
      tf.rotate(P.angle);
      var an = tf.anchor;
      tf.translate(P.x - an[0], P.y - an[1]);
    }
  }

  var s = new IllustratorSaveOptions();
  s.pdfCompatible = true;
  s.embedICCProfile = false;
  doc.saveAs(new File(ARGS.out), s);
  for (var l = 0; l < doc.layers.length; l++) summary.push(doc.layers[l].name + " " + doc.layers[l].pageItems.length);
} finally { doc.close(SaveOptions.DONOTSAVECHANGES); }
writeResult({ layers: summary });
"ok";
