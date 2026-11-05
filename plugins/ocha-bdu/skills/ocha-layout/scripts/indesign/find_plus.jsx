// Read only: lists every place InDesign shows a “+” on a text style (Paragraph/TextStyleRange.styleOverridden),
// in story text and table cells. This is exactly the flag of the Paragraph Styles panel. Opens a COPY. Args: src, log.
#target indesign
#include "lib.jsxinc"
(function () {
    app.scriptPreferences.userInteractionLevel = UserInteractionLevels.NEVER_INTERACT;
    var doc = app.open(File(app.scriptArgs.getValue("src")), false, OpenOptions.OPEN_COPY), out = [];
    function look(p, kind) {
        var r = p.textStyleRanges, runs = [];
        for (var i = 0; i < r.length; i++) if (r[i].styleOverridden) runs.push(i + ":" + String(r[i].contents).replace(/\r/g, "\u00B6").substring(0, 20));
        if (p.styleOverridden || runs.length) out.push({ page: safe(function () { return pageOf(p.characters[0]); }, "?"), kind: kind, style: p.appliedParagraphStyle.name,
            text: String(p.contents).replace(/[\r\u0016]/g, "").substring(0, 50), paragraph: p.styleOverridden, runs: runs, startParagraph: String(p.startParagraph) });
    }
    var st = doc.stories;
    for (var s = 0; s < st.length; s++) {
        var ps = st[s].paragraphs; for (var i = 0; i < ps.length; i++) look(ps[i], "text");
        var tb = st[s].tables; for (var t = 0; t < tb.length; t++) { var c = tb[t].cells; for (var k = 0; k < c.length; k++) { var cp = c[k].paragraphs; for (var q = 0; q < cp.length; q++) look(cp[q], "cell"); } }
    }
    doc.close(SaveOptions.NO);
    writeText(app.scriptArgs.getValue("log"), ser({ document: File(app.scriptArgs.getValue("src")).name, count: out.length, items: out })); return "ok " + out.length;
})();
