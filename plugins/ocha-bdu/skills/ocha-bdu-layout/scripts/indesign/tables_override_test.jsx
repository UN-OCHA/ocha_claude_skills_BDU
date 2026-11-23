// Read only: proves a table has no table- or cell-style overrides. On a COPY, snapshots every property of each
// table and cell, clears all table and cell style overrides, snapshots again and reports what changed.
// Nothing changed = nothing was overridden. Args: src, log, plant (optional "1": self-check).
#target indesign
#include "lib.jsxinc"
(function () {
    app.scriptPreferences.userInteractionLevel = UserInteractionLevels.NEVER_INTERACT;
    var doc = app.open(File(app.scriptArgs.getValue("src")), false, OpenOptions.OPEN_COPY), out = [];
    var SKIP = { parent: 1, index: 1, id: 1, contents: 1, texts: 1, properties: 1, cells: 1, rows: 1, columns: 1, isValid: 1, label: 1, storyOffset: 1 };
    function snap(o) {
        var p = o.properties, r = {};
        for (var k in p) {
            if (SKIP[k]) continue;
            var v = p[k];
            if (v === null || v === undefined) r[k] = "null";
            else if (typeof v === "object") r[k] = safe(function () { return v.name !== undefined ? "@" + v.name : String(v); }, "?");
            else r[k] = typeof v === "number" ? String(Math.round(v * 1000) / 1000) : String(v);
        }
        return r;
    }
    var st = doc.stories, tables = [];
    for (var s = 0; s < st.length; s++) for (var t = 0; t < st[s].tables.length; t++) tables.push(st[s].tables[t]);
    // Self-check: plant=1 adds two known overrides to the first table, which the test must report.
    if (app.scriptArgs.getValue("plant") === "1") { tables[0].cells[1].leftEdgeStrokeWeight = 2; tables[0].cells[0].topInset = 9; }
    for (var i = 0; i < tables.length; i++) {
        var T = tables[i], c = T.cells.everyItem().getElements(), before = { table: snap(T), cells: [] }, diffs = [];
        for (var k = 0; k < c.length; k++) before.cells.push(snap(c[k]));
        T.clearTableStyleOverrides();
        // true = clear through the root cell style: also catches local lines and fills the cell style leaves to the
        // table style (false misses them; the self-check proved it).
        // A deep clear also re-applies the cell style's paragraph style to all the cell's text; put each paragraph's
        // style back (text overrides are find_plus.jsx's job), so only real cell/table overrides show up here.
        for (var k = 0; k < c.length; k++) {
            var ps = c[k].paragraphs.everyItem().getElements(), keep = [];
            for (var q = 0; q < ps.length; q++) keep.push(ps[q].appliedParagraphStyle);
            c[k].clearCellStyleOverrides(true);
            ps = c[k].paragraphs.everyItem().getElements();
            for (var q = 0; q < ps.length; q++) if (ps[q].appliedParagraphStyle !== keep[q]) ps[q].appliedParagraphStyle = keep[q];
        }
        var a = snap(T); for (var p in a) if (a[p] !== before.table[p]) diffs.push("table " + p + ": " + before.table[p] + " -> " + a[p]);
        for (var k = 0; k < c.length; k++) { var b = snap(c[k]); for (var p in b) if (b[p] !== before.cells[k][p]) diffs.push("cell " + c[k].name + " " + p + ": " + before.cells[k][p] + " -> " + b[p]); }
        out.push({ page: safe(function () { return pageOf(T.storyOffset); }, "?"), tableStyle: T.appliedTableStyle.name, propertiesChecked: c.length + " cells", changes: diffs });
    }
    doc.close(SaveOptions.NO);
    writeText(app.scriptArgs.getValue("log"), ser(out)); return "ok";
})();
