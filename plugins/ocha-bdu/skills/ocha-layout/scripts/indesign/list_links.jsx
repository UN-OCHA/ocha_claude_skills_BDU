// Read-only: list every placed link with its page, frame bounds (page coordinates), size in grid columns,
// scale and file path. Args: src, out (JSON). Closes without saving.
#target indesign
#include "lib.jsxinc"
(function () {
    var doc = openOriginal(app.scriptArgs.getValue("src"), false), out = [];
    var vp = doc.viewPreferences, old = vp.rulerOrigin;
    try {
        vp.rulerOrigin = RulerOrigin.PAGE_ORIGIN;
        vp.horizontalMeasurementUnits = MeasurementUnits.POINTS; vp.verticalMeasurementUnits = MeasurementUnits.POINTS;
        for (var i = 0; i < doc.links.length; i++) {
            var l = doc.links[i], g = l.parent, fr = safe(function () { return g.parent; });
            var pg = safe(function () { return fr.parentPage; });
            var b = safe(function () { return fr.geometricBounds; });
            var o = { name: l.name, path: l.filePath, status: String(l.status),
                page: pg ? pg.name : "pasteboard/master", bounds: b,
                hScale: safe(function () { return Math.round(g.horizontalScale * 10) / 10; }) };
            if (pg && b) {
                var m = pg.marginPreferences, pw = doc.documentPreferences.pageWidth;
                var cw = (pw - m.left - m.right - (m.columnCount - 1) * m.columnGutter) / m.columnCount, step = cw + m.columnGutter;
                o.cols = (Math.round((b[1] - m.left) / step) + 1) + "-" + Math.round((b[3] - m.left + m.columnGutter) / step);
            }
            out.push(o);
        }
    } finally { vp.rulerOrigin = old; doc.close(SaveOptions.NO); }
    writeText(app.scriptArgs.getValue("out"), ser(out));
    return "ok";
})();
