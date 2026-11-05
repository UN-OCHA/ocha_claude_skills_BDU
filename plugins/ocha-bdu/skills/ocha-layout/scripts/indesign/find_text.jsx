// Read-only: list every GREP match with page, paragraph style and surrounding text.
// Args: src, grep (one pattern), out (JSON). Masters and locked items included. Closes without saving.
#target indesign
#include "lib.jsxinc"
(function () {
    var doc = openOriginal(app.scriptArgs.getValue("src"), false), out = [];
    app.findChangeGrepOptions.includeMasterPages = true;
    app.findChangeGrepOptions.includeLockedLayersForFind = true;
    app.findChangeGrepOptions.includeLockedStoriesForFind = true;
    app.findChangeGrepOptions.includeHiddenLayers = true;
    app.findGrepPreferences = NothingEnum.NOTHING;
    app.findGrepPreferences.findWhat = app.scriptArgs.getValue("grep");
    var hits = doc.findGrep();
    for (var i = 0; i < hits.length; i++) {
        var h = hits[i];
        out.push({ page: pageOf(h), style: safe(function () { return h.appliedParagraphStyle.name; }, ""), match: h.contents,
            context: String(safe(function () { return h.paragraphs[0].contents; }, "")).replace(/\s+/g, " ").substring(0, 160) });
    }
    app.findGrepPreferences = NothingEnum.NOTHING;
    doc.close(SaveOptions.NO);
    writeText(app.scriptArgs.getValue("out"), ser(out)); return "ok";
})();
