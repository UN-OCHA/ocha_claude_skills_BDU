// Read only: every paragraph, character, object, table and cell style with its group, "based on", how often it is
// used, and the key settings that tell near-twins apart. For the style simplification review. Opens a COPY.
// Args: src, log.
#target indesign
#include "lib.jsxinc"
(function () {
    app.scriptPreferences.userInteractionLevel = UserInteractionLevels.NEVER_INTERACT;
    var doc = app.open(File(app.scriptArgs.getValue("src")), false, OpenOptions.OPEN_COPY), R = { paragraph: [], character: [], object: [], table: [], cell: [] };
    function v(o, k) { return safe(function () { var x = o[k]; if (x === null || x === undefined) return ""; if (typeof x === "object") return safe(function () { return x.name; }, String(x)); return typeof x === "number" ? Math.round(x * 100) / 100 : x; }, ""); }
    function group(s) { var p = [], g = s.parent; while (g && g.constructor.name.indexOf("Group") >= 0) { p.unshift(g.name); g = g.parent; } return p.join("/"); }
    var useP = {}, useC = {}, useO = {}, layerP = {};
    var st = doc.stories;
    for (var s = 0; s < st.length; s++) {
        var r = st[s].textStyleRanges.everyItem().getElements();
        var tablesRanges = [];
        var tb = st[s].tables; for (var t = 0; t < tb.length; t++) { var cr = tb[t].cells.everyItem().textStyleRanges.everyItem().getElements(); for (var k = 0; k < cr.length; k++) tablesRanges.push(cr[k]); }
        r = r.concat(tablesRanges);
        var lay = safe(function () { return st[s].textContainers[0].itemLayer.name; }, "?");
        for (var i = 0; i < r.length; i++) {
            var pid = safe(function () { return r[i].appliedParagraphStyle.id; }), cid = safe(function () { return r[i].appliedCharacterStyle.id; });
            if (pid !== null) { useP[pid] = (useP[pid] || 0) + 1; layerP[pid] = layerP[pid] || {}; layerP[pid][lay] = 1; }
            if (cid !== null) useC[cid] = (useC[cid] || 0) + 1;
        }
    }
    var it = doc.allPageItems; for (var i = 0; i < it.length; i++) { var oid = safe(function () { return it[i].appliedObjectStyle.id; }); if (oid !== null) useO[oid] = (useO[oid] || 0) + 1; }
    var ps = doc.allParagraphStyles;
    for (var i = 0; i < ps.length; i++) { var s = ps[i], L = []; for (var l in (layerP[s.id] || {})) L.push(l);
        R.paragraph.push({ name: s.name, group: group(s), basedOn: v(s, "basedOn"), uses: useP[s.id] || 0, layers: L.join(","),
            font: v(s, "appliedFont") + " " + v(s, "fontStyle"), size: v(s, "pointSize"), leading: v(s, "leading"), color: v(s, "fillColor"), tint: v(s, "fillTint"),
            caps: v(s, "capitalization"), tracking: v(s, "tracking"), before: v(s, "spaceBefore"), after: v(s, "spaceAfter"), align: v(s, "justification"),
            start: v(s, "startParagraph"), ruleAbove: v(s, "ruleAbove"), ruleBelow: v(s, "ruleBelow"), next: v(s, "nextStyle") }); }
    var cs = doc.allCharacterStyles;
    for (var i = 0; i < cs.length; i++) { var s = cs[i]; R.character.push({ name: s.name, group: group(s), uses: useC[s.id] || 0, font: v(s, "appliedFont") + " " + v(s, "fontStyle"), size: v(s, "pointSize"), color: v(s, "fillColor") }); }
    var os = doc.allObjectStyles;
    for (var i = 0; i < os.length; i++) { var s = os[i]; R.object.push({ name: s.name, group: group(s), basedOn: v(s, "basedOn"), uses: useO[s.id] || 0 }); }
    var ts = doc.allTableStyles; for (var i = 0; i < ts.length; i++) R.table.push({ name: ts[i].name });
    var ce = doc.allCellStyles; for (var i = 0; i < ce.length; i++) R.cell.push({ name: ce[i].name });
    doc.close(SaveOptions.NO);
    writeText(app.scriptArgs.getValue("log"), ser(R)); return "ok";
})();
