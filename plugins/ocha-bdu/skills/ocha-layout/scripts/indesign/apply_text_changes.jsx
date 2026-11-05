// Apply literal text find/change pairs from a JSON list, case-sensitive, masters included.
// Plain-text change keeps each match's own formatting. Args: src, changes (JSON path), log.
// Logs every replaced occurrence: page, paragraph style, before -> after.
#target indesign
#include "lib.jsxinc"
(function () {
    var src = app.scriptArgs.getValue("src");
    var f = File(app.scriptArgs.getValue("changes")); f.encoding = "UTF-8"; f.open("r");
    var list = eval("(" + f.read() + ")"); f.close();
    var doc = openOriginal(src, true), LOG = { document: File(src).name, changes: [] };
    var o = app.findChangeTextOptions;
    o.includeMasterPages = true; o.includeLockedLayersForFind = true; o.includeLockedStoriesForFind = true;
    o.caseSensitive = true; o.wholeWord = false;
    for (var i = 0; i < list.length; i++) {
        // "grep": true -> GREP pattern (for text with special spaces/breaks); otherwise literal text.
        var G = !!list[i].grep;
        app.findTextPreferences = NothingEnum.NOTHING; app.changeTextPreferences = NothingEnum.NOTHING;
        app.findGrepPreferences = NothingEnum.NOTHING; app.changeGrepPreferences = NothingEnum.NOTHING;
        if (G) { var g = app.findChangeGrepOptions; g.includeMasterPages = true; g.includeLockedLayersForFind = true; g.includeLockedStoriesForFind = true;
                 app.findGrepPreferences.findWhat = list[i].find; }
        else app.findTextPreferences.findWhat = list[i].find;
        var hits = G ? doc.findGrep() : doc.findText(), where = [];
        for (var h = 0; h < hits.length; h++) where.push({ page: pageOf(hits[h]), style: safe(function () { return hits[h].appliedParagraphStyle.name; }, ""), text: String(hits[h].contents) });
        if (G) app.changeGrepPreferences.changeTo = list[i].change; else app.changeTextPreferences.changeTo = list[i].change;
        var n = (G ? doc.changeGrep() : doc.changeText()).length;
        app.findGrepPreferences = NothingEnum.NOTHING; app.changeGrepPreferences = NothingEnum.NOTHING;
        LOG.changes.push({ before: list[i].find, after: list[i].change, why: list[i].why, count: n, where: where });
    }
    app.findTextPreferences = NothingEnum.NOTHING; app.changeTextPreferences = NothingEnum.NOTHING;
    LOG.overset = 0; for (i = 0; i < doc.stories.length; i++) if (doc.stories[i].overflows) LOG.overset++;
    saveInPlace(doc, src); doc.close(SaveOptions.NO);
    writeText(app.scriptArgs.getValue("log"), ser(LOG)); return "ok";
})();
