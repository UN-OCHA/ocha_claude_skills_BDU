// No empty folders in any panel. Deletes every empty folder.
// folder in the Swatches, Paragraph, Character, Object, Table and Cell Styles panels. Runs until none is left, because
// deleting a folder can leave its parent empty. A folder holding anything is never touched. Args: src, log.
#target indesign
#include "lib.jsxinc"
(function () {
    var src = app.scriptArgs.getValue("src"), log = { deleted: [], left: [] };
    app.scriptPreferences.userInteractionLevel = UserInteractionLevels.NEVER_INTERACT;
    var doc = openOriginal(src, false);
    try {
        var KINDS = [["paragraph", "paragraphStyleGroups", "paragraphStyles"], ["character", "characterStyleGroups", "characterStyles"],
                     ["object", "objectStyleGroups", "objectStyles"], ["table", "tableStyleGroups", "tableStyles"], ["cell", "cellStyleGroups", "cellStyles"]];
        // Folders can nest, so walk down from the document.
        function sweep(parent, kind, groupsProp, stylesProp) {
            var n = 0, g = parent[groupsProp].everyItem().getElements();
            for (var i = 0; i < g.length; i++) {
                n += sweep(g[i], kind, groupsProp, stylesProp);
                if (g[i][stylesProp].length === 0 && g[i][groupsProp].length === 0) { log.deleted.push(kind + ": " + g[i].name); g[i].remove(); n++; }
                else log.left.push(kind + ": " + g[i].name + " (" + g[i][stylesProp].length + " styles)");
            }
            return n;
        }
        for (var k = 0; k < KINDS.length; k++) sweep(doc, KINDS[k][0], KINDS[k][1], KINDS[k][2]);
        var cg = doc.colorGroups.everyItem().getElements();
        for (var i = 0; i < cg.length; i++) if (cg[i].name !== "[Root Color Group]" && cg[i].colorGroupSwatches.length === 0) { log.deleted.push("swatches: " + cg[i].name); cg[i].remove(); }
        saveInPlace(doc, src); doc.close(SaveOptions.NO);
    } catch (e) { doc.close(SaveOptions.NO); log.error = String(e) + " line " + e.line; }
    writeText(app.scriptArgs.getValue("log"), ser(log)); return log.error ? "error" : "ok";
})();
