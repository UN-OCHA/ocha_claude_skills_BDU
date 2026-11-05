// Set the columns of every table containing a given text to whole units of the page's column grid.
// Args: src, contains (text inside the table), spans (comma list of grid columns per table column,
// e.g. "2,2,3"), log. A column spanning k grid columns = k*col + (k-1)*gutter, plus one gutter when
// another column follows, so every table column starts exactly on a grid column. Saves in place.
#target indesign
#include "lib.jsxinc"
(function () {
    var src = app.scriptArgs.getValue("src"), doc = openOriginal(src, true);
    var spans = app.scriptArgs.getValue("spans").split(","), LOG = { document: File(src).name, spans: spans.join("+"), tables: [], errors: [] };
    doc.viewPreferences.horizontalMeasurementUnits = MeasurementUnits.POINTS;
    app.findTextPreferences = NothingEnum.NOTHING; app.findTextPreferences.findWhat = app.scriptArgs.getValue("contains");
    var hits = doc.findText(); app.findTextPreferences = NothingEnum.NOTHING;
    var done = {};
    for (var i = 0; i < hits.length; i++) {
        var cell = hits[i].parent; if (cell.constructor.name !== "Cell") continue;
        var tb = cell.parent; if (done[tb.id]) continue; done[tb.id] = true;
        var pg = hits[i].parentTextFrames[0].parentPage, m = pg.marginPreferences;
        var colW = (doc.documentPreferences.pageWidth - m.left - m.right - (m.columnCount - 1) * m.columnGutter) / m.columnCount;
        if (tb.columns.length !== spans.length) { LOG.errors.push("page " + pg.name + ": table has " + tb.columns.length + " columns, spans give " + spans.length); continue; }
        var before = tb.columns.everyItem().width, after = [];
        for (var c = 0; c < spans.length; c++) {
            var k = parseInt(spans[c], 10), w = k * colW + (k - 1) * m.columnGutter + (c < spans.length - 1 ? m.columnGutter : 0);
            tb.columns[c].width = w; after.push(Math.round(w * 100) / 100);
        }
        var lines = 0; for (var r = 0; r < tb.cells.length; r++) lines = Math.max(lines, tb.cells[r].lines.length);
        LOG.tables.push({ page: pg.name, grid: m.columnCount + " cols × " + colW.toFixed(2) + " pt, gutter " + m.columnGutter,
            before: before.join(" / "), after: after.join(" / "), maxLinesInAnyCell: lines });
    }
    LOG.overset = 0; for (i = 0; i < doc.stories.length; i++) if (doc.stories[i].overflows) LOG.overset++;
    saveInPlace(doc, src); doc.close(SaveOptions.NO);
    writeText(app.scriptArgs.getValue("log"), ser(LOG)); return "ok";
})();
