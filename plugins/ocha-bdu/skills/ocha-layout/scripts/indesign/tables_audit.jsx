// Read only: inventory of every native table (and the frames holding them) for the table review.
// For each table: page, size, table style, and per cell the cell style plus the properties that
// differ from that cell style (fill, tint, insets, vertical justification, edge strokes).
// InDesign has no "overridden" flag for cells, so overrides are found by comparing each cell
// with its applied cell style (a style that leaves a property unset counts as "no opinion").
// Opens a COPY. Args: src, log.
#target indesign
#include "lib.jsxinc"
(function () {
    app.scriptPreferences.userInteractionLevel = UserInteractionLevels.NEVER_INTERACT;
    var doc = app.open(File(app.scriptArgs.getValue("src")), false, OpenOptions.OPEN_COPY), out = [];
    function nm(o) { return safe(function () { return o.name; }, String(o)); }
    var PROPS = ["fillColor", "fillTint", "topInset", "bottomInset", "leftInset", "rightInset", "verticalJustification",
        "topEdgeStrokeWeight", "bottomEdgeStrokeWeight", "leftEdgeStrokeWeight", "rightEdgeStrokeWeight",
        "topEdgeStrokeColor", "bottomEdgeStrokeColor", "leftEdgeStrokeColor", "rightEdgeStrokeColor",
        "topEdgeStrokeTint", "bottomEdgeStrokeTint", "topEdgeStrokeType", "bottomEdgeStrokeType"];
    function val(v) { if (v === null || v === undefined) return null; if (typeof v === "object") return nm(v); return typeof v === "number" ? Math.round(v * 100) / 100 : String(v); }
    function diff(cell, cs) {
        var d = {};
        for (var i = 0; i < PROPS.length; i++) {
            var p = PROPS[i], cv = safe(function () { return val(cell[p]); }), sv = safe(function () { return val(cs[p]); });
            // Unset in the style ("Nothing"/ignore) means the table style or cell decides: not an override of the cell style.
            if (sv === null || sv === "Nothing" || sv === "NOTHING" || sv === "-9999") continue;
            if (String(cv) !== String(sv)) d[p] = cv + " (style " + sv + ")";
        }
        return d;
    }
    var st = doc.stories;
    for (var s = 0; s < st.length; s++) {
        var tb = st[s].tables;
        for (var t = 0; t < tb.length; t++) {
            var T = tb[t], c = T.cells.everyItem().getElements(), cells = {}, styles = {}, n = 0;
            for (var k = 0; k < c.length; k++) {
                var cs = c[k].appliedCellStyle, csn = nm(cs), d = diff(c[k], cs), keys = [];
                styles[csn] = (styles[csn] || 0) + 1;
                for (var key in d) if (d.hasOwnProperty(key)) keys.push(key + "=" + d[key]);
                if (keys.length) { n++; var sig = csn + " | " + keys.join("; "); cells[sig] = (cells[sig] || []); cells[sig].push(c[k].name); }
            }
            var frame = safe(function () { return T.parent; });
            out.push({
                page: safe(function () { return pageOf(T.storyOffset); }, "?"),
                frameLabel: safe(function () { return frame.label; }, ""),
                firstText: safe(function () { return String(T.cells[0].contents).substring(0, 40); }, ""),
                rows: T.rows.length, columns: T.columns.length,
                width: safe(function () { return Math.round(T.width * 10) / 10; }),
                tableStyle: nm(T.appliedTableStyle),
                columnWidths: safe(function () { var w = [], col = T.columns; for (var i = 0; i < col.length; i++) w.push(Math.round(col[i].width * 10) / 10); return w.join(" + "); }),
                cellStyles: styles, cellsWithOverrides: n, overrides: cells
            });
        }
    }
    doc.close(SaveOptions.NO);
    writeText(app.scriptArgs.getValue("log"), ser({ document: File(app.scriptArgs.getValue("src")).name, tables: out.length, items: out }));
    return "ok " + out.length;
})();
