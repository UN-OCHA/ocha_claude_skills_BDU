// Read only: where each colour swatch is used (page items, text, tables, paragraph/character/object/table/cell
// styles). For the swatch clean-up and renames. Opens a COPY. Args: src, log.
#target indesign
#include "lib.jsxinc"
(function () {
    app.scriptPreferences.userInteractionLevel = UserInteractionLevels.NEVER_INTERACT;
    var doc = app.open(File(app.scriptArgs.getValue("src")), false, OpenOptions.OPEN_COPY), U = {};
    function hit(c, where) { var n = safe(function () { return c.name; }, ""); if (!n || n === "None") return; if (!U[n]) U[n] = {}; U[n][where] = (U[n][where] || 0) + 1; }
    function props(o, keys, where) { for (var k = 0; k < keys.length; k++) { var key = keys[k]; hit(safe(function () { return o[key]; }), where + "." + key); } }
    var TXT = ["fillColor", "strokeColor", "underlineColor", "strikeThroughColor"], PAR = TXT.concat(["ruleAboveColor", "ruleBelowColor", "paragraphShadingColor", "paragraphBorderColor"]);
    var it = doc.allPageItems; for (var i = 0; i < it.length; i++) props(it[i], ["fillColor", "strokeColor"], "item " + safe(function () { return it[i].parentPage.name; }, "pb"));
    var st = doc.stories; for (var s = 0; s < st.length; s++) {
        var r = st[s].textStyleRanges.everyItem().getElements(); for (var i = 0; i < r.length; i++) props(r[i], PAR, "text");
        var tb = st[s].tables; for (var t = 0; t < tb.length; t++) { var c = tb[t].cells.everyItem().getElements(); for (var k = 0; k < c.length; k++) { props(c[k], ["fillColor", "topEdgeStrokeColor", "bottomEdgeStrokeColor", "leftEdgeStrokeColor", "rightEdgeStrokeColor"], "cell"); var cr = c[k].texts[0].textStyleRanges.everyItem().getElements(); for (var q = 0; q < cr.length; q++) props(cr[q], PAR, "cell text"); } }
    }
    var a = doc.allParagraphStyles; for (var i = 0; i < a.length; i++) props(a[i], PAR, "pstyle " + a[i].name);
    a = doc.allCharacterStyles; for (var i = 0; i < a.length; i++) props(a[i], TXT, "cstyle " + a[i].name);
    a = doc.allObjectStyles; for (var i = 0; i < a.length; i++) props(a[i], ["fillColor", "strokeColor"], "ostyle " + a[i].name);
    a = doc.allCellStyles; for (var i = 0; i < a.length; i++) props(a[i], ["fillColor", "topEdgeStrokeColor", "bottomEdgeStrokeColor", "leftEdgeStrokeColor", "rightEdgeStrokeColor"], "cellstyle " + a[i].name);
    var ms = doc.masterSpreads; for (var m = 0; m < ms.length; m++) { var mi = ms[m].allPageItems; for (var i = 0; i < mi.length; i++) props(mi[i], ["fillColor", "strokeColor"], "master " + ms[m].name); }
    var out = []; var c = doc.colors; for (var i = 0; i < c.length; i++) out.push({ name: c[i].name, value: safe(function () { return c[i].colorValue.join(","); }, ""), used: U[c[i].name] || {} });
    var tn = doc.tints; for (var i = 0; i < tn.length; i++) out.push({ tint: tn[i].name, used: U[tn[i].name] || {} });
    doc.close(SaveOptions.NO); writeText(app.scriptArgs.getValue("log"), ser(out)); return "ok";
})();
