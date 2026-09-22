// Shared helpers for the export_ai Illustrator scripts (ExtendScript = ES3: no JSON, no map).
// Each script gets its input as `ARGS`, set by the wrapper export_ai.py writes, and writes
// its result as JSON to ARGS.result.

app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;

function jstr(s) {
  s = String(s);
  var o = '"';
  for (var i = 0; i < s.length; i++) {
    var c = s.charAt(i), n = s.charCodeAt(i);
    if (c == '"' || c == "\\") o += "\\" + c;
    else if (n < 32 || n > 126) o += "\\u" + ("0000" + n.toString(16)).slice(-4);
    else o += c;
  }
  return o + '"';
}

function toJSON(v) {
  if (v === null || v === undefined) return "null";
  var t = typeof v;
  if (t == "number") return isFinite(v) ? String(v) : "null";
  if (t == "boolean") return String(v);
  if (t == "string") return jstr(v);
  if (v instanceof Array) {
    var a = [];
    for (var i = 0; i < v.length; i++) a.push(toJSON(v[i]));
    return "[" + a.join(",") + "]";
  }
  var p = [];
  for (var k in v) if (v.hasOwnProperty(k)) p.push(jstr(k) + ":" + toJSON(v[k]));
  return "{" + p.join(",") + "}";
}

function writeResult(value) {
  var f = new File(ARGS.result);
  f.encoding = "UTF-8";
  f.lineFeed = "Unix";
  f.open("w");
  f.write(toJSON(value));
  f.close();
}

function colourKey(c) {
  switch (c.typename) {
    case "RGBColor": return "rgb:" + Math.round(c.red) + "," + Math.round(c.green) + "," + Math.round(c.blue);
    case "CMYKColor": return "cmyk:" + [c.cyan, c.magenta, c.yellow, c.black].join(",");
    case "GrayColor": return "gray:" + c.gray;
    default: return "other:" + c.typename;
  }
}

function makeColour(key) {
  var kind = key.split(":")[0], v = key.split(":")[1].split(",");
  var c;
  if (kind == "rgb") { c = new RGBColor(); c.red = +v[0]; c.green = +v[1]; c.blue = +v[2]; }
  else if (kind == "cmyk") { c = new CMYKColor(); c.cyan = +v[0]; c.magenta = +v[1]; c.yellow = +v[2]; c.black = +v[3]; }
  else if (kind == "gray") { c = new GrayColor(); c.gray = +v[0]; }
  else throw "can't recreate colour " + key;
  return c;
}

function round2(b) {
  var o = [];
  for (var i = 0; i < b.length; i++) o.push(Math.round(b[i] * 100) / 100);
  return o;
}

// A clipping group's bounds include everything it hides; what you see is its clipping path.
function seenBounds(it) {
  if (it.typename == "GroupItem" && it.clipped)
    for (var k = 0; k < it.pageItems.length; k++) if (it.pageItems[k].clipping) return it.pageItems[k].geometricBounds;
  return it.geometricBounds;
}

// Chrome's PDFs wrap nearly everything in page-sized clipping groups. Unwrap them, keeping the
// stacking order, so every object stands on its own at the top of its layer.
function unwrapPageGroups(doc) {
  var page = doc.artboards[0].artboardRect;
  function isPage(b) { for (var k = 0; k < 4; k++) if (Math.abs(b[k] - page[k]) > 1) return false; return true; }
  for (var l = 0; l < doc.layers.length; l++) {
    var layer = doc.layers[l];
    for (var changed = true; changed; ) {
      changed = false;
      for (var i = layer.pageItems.length - 1; i >= 0; i--) {
        var g = layer.pageItems[i];
        if (g.typename != "GroupItem" || !isPage(seenBounds(g))) continue;
        while (g.pageItems.length) {
          var c = g.pageItems[0];
          if (c.clipping) c.remove(); else c.move(g, ElementPlacement.PLACEBEFORE);
        }
        g.remove();
        changed = true;
      }
    }
  }
}

// Every top-level object, top of the stack first. Text frames were named __t<index> beforehand.
function snapshot(doc) {
  var items = [];
  for (var l = 0; l < doc.layers.length; l++)
    for (var i = 0; i < doc.layers[l].pageItems.length; i++) items.push(doc.layers[l].pageItems[i]);
  return items;
}

function openPdf(path) {
  app.preferences.PDFFileOptions.pageToOpen = 1;
  return app.open(new File(path));
}

function nameTextFrames(doc) {
  for (var i = 0; i < doc.textFrames.length; i++) doc.textFrames[i].name = "__t" + i;
}
