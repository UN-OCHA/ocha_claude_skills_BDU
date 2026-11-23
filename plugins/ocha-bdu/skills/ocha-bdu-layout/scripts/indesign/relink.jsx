// Point every link at this package's own Links folder (same relative path).
// Args: src, log. Saves in place. Logs each link before -> after. Changes nothing else.
#target indesign
#include "lib.jsxinc"
(function () {
    var src = app.scriptArgs.getValue("src"), logPath = app.scriptArgs.getValue("log");
    var doc = openOriginal(src, true), pkg = File(src).parent.fsName;
    var LOG = { document: File(src).name, links: [], errors: [] };
    for (var i = 0; i < doc.links.length; i++) {
        var lk = doc.links[i], before = String(lk.filePath), m = before.match(/\/Links\/(.+)$/);
        if (!m) { LOG.errors.push("link without /Links/: " + before); continue; }
        var target = File(pkg + "/Links/" + m[1]);
        if (before === target.fsName) continue;
        if (!target.exists) { LOG.errors.push("missing in package: " + m[1]); continue; }
        try { lk.relink(target); LOG.links.push({ name: lk.name, page: safe(function () { return lk.parent.parentPage.name; }, "?"), before: before, after: target.fsName }); }
        catch (e) { LOG.errors.push("relink failed " + lk.name + ": " + e); }
    }
    LOG.notNormalAfter = 0;
    for (i = 0; i < doc.links.length; i++) if (doc.links[i].status !== LinkStatus.NORMAL) LOG.notNormalAfter++;
    saveInPlace(doc, src); doc.close(SaveOptions.NO);
    writeText(logPath, ser(LOG)); return "ok";
})();
