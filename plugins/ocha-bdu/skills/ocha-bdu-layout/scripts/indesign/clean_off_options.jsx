// Clean styles: no switched-off option may hold a leftover colour.
// A switched-off option (rule above/below, shading, border, underline, strikethrough) still stores a colour, tint and
// gap colour. Leftovers from old templates kept odd swatches alive (an old orange, a GHO grey, a spot yellow) and would
// show if anyone ticked the box. This resets the colour settings of every switched-off option, in every paragraph and
// character style, to InDesign's own defaults, read from a fresh document's [Basic Paragraph] (Text Color, auto tint,
// gap None; shading Black 20%). Nothing on the page changes: the options stay off.
// Args: src, log, dry ("1" = list only, on a copy, nothing saved).
#target indesign
#include "lib.jsxinc"
(function () {
    var src = app.scriptArgs.getValue("src"), dry = app.scriptArgs.getValue("dry") === "1", log = { changed: [] };
    app.scriptPreferences.userInteractionLevel = UserInteractionLevels.NEVER_INTERACT;
    // [switch, colour, tint, gap colour, gap tint] per option. Shading has no gap.
    var OPT = [["ruleAbove", "ruleAboveColor", "ruleAboveTint", "ruleAboveGapColor", "ruleAboveGapTint"],
               ["ruleBelow", "ruleBelowColor", "ruleBelowTint", "ruleBelowGapColor", "ruleBelowGapTint"],
               ["paragraphShadingOn", "paragraphShadingColor", "paragraphShadingTint", null, null],
               ["paragraphBorderOn", "paragraphBorderColor", "paragraphBorderTint", "paragraphBorderGapColor", "paragraphBorderGapTint"],
               ["underline", "underlineColor", "underlineTint", "underlineGapColor", "underlineGapTint"],
               ["strikeThru", "strikeThroughColor", "strikeThroughTint", "strikeThroughGapColor", "strikeThroughGapTint"]];
    function key(v) { return (typeof v === "string" || typeof v === "number") ? String(v) : safe(function () { return v.name; }, String(v)); }
    function defined(v) { return v !== NothingEnum.NOTHING && v !== null && v !== undefined; }
    // InDesign's defaults: colours by name (a swatch, or the string "Text Color"), tints as numbers.
    var DEF = {}, fresh = app.documents.add(false);
    try {
        var b = fresh.paragraphStyles.itemByName("[Basic Paragraph]");
        for (var o = 0; o < OPT.length; o++) for (var k = 1; k < 5; k++) if (OPT[o][k]) { var v = safe(function () { return b[OPT[o][k]]; }); if (defined(v)) DEF[OPT[o][k]] = key(v); }
    } finally { fresh.close(SaveOptions.NO); }
    log.defaults = DEF;
    var doc = dry ? app.open(File(src), false, OpenOptions.OPEN_COPY) : openOriginal(src, false);
    try {
        function value(p) { var d = DEF[p]; if (/Color$/.test(p) && d !== "Text Color") return doc.swatches.itemByName(d); return /Tint$/.test(p) ? Number(d) : d; }
        function clean(st, kind) {
            for (var o = 0; o < OPT.length; o++) {
                var p = OPT[o];
                if (safe(function () { return st[p[0]]; }) === true) continue;     // option in use: leave it
                var f = [];
                for (var k = 1; k < 5; k++) {
                    var prop = p[k]; if (!prop || DEF[prop] === undefined) continue;
                    var cur = safe(function () { return st[prop]; });
                    if (!defined(cur) || key(cur) === DEF[prop]) continue;          // undefined in a character style = clean
                    f.push(prop + " " + key(cur) + " -> " + DEF[prop]);
                    if (!dry) st[prop] = value(prop);
                }
                if (f.length) log.changed.push(kind + " “" + st.name + "” (" + p[0] + " off): " + f.join(", "));
            }
        }
        var ps = doc.allParagraphStyles, cs = doc.allCharacterStyles, all = [];
        for (var i = 1; i < ps.length; i++) all.push([ps[i], "para"]);   // 0 = [No Paragraph Style], read only
        for (var i = 1; i < cs.length; i++) all.push([cs[i], "char"]);
        // A child style with an option ON can take its colour from a parent where the option is OFF: cleaning the
        // parent would then change the child on the page. So note every switched-on colour/tint first and put back
        // any that moved.
        var onVals = [];
        for (var i = 0; i < all.length; i++) for (var o = 0; o < OPT.length; o++) {
            var st = all[i][0], p = OPT[o]; if (safe(function () { return st[p[0]]; }) !== true) continue;
            for (var k = 1; k < 5; k++) { var prop = p[k]; if (!prop) continue; var v = safe(function () { return st[prop]; }); if (defined(v)) onVals.push([st, prop, v, key(v)]); }
        }
        for (var i = 0; i < all.length; i++) clean(all[i][0], all[i][1]);
        if (!dry) for (var i = 0; i < onVals.length; i++) {
            var r = onVals[i], now = safe(function () { return r[0][r[1]]; });
            if (key(now) !== r[3]) { r[0][r[1]] = r[2]; log.changed.push("kept \u201C" + r[0].name + "\u201D " + r[1] + " = " + r[3] + " (inherited from a cleaned parent)"); }
        }
        if (dry) doc.close(SaveOptions.NO); else { saveInPlace(doc, src); doc.close(SaveOptions.NO); }
    } catch (e) { doc.close(SaveOptions.NO); log.error = String(e) + " line " + e.line; }
    writeText(app.scriptArgs.getValue("log"), ser(log)); return log.error ? "error" : "ok";
})();
