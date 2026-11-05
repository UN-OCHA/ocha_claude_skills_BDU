// Read only: which frames differ from their object style, and in what. For each frame, reads its object style and,
// for each category that style switches on (fill, stroke, corners, text frame options, baseline, auto-size, text
// wrap), compares the frame's own value with the style's. Changes NOTHING, not even on the copy.
// Never replace this with "clear overrides and compare": clearObjectStyleOverrides on some text frames in these
// files sends InDesign's text engine into an endless loop (hung twice and crashed once, 29 October 2026).
// Opens a COPY. Args: src, log.
#target indesign
#include "lib.jsxinc"
(function () {
    var t0 = new Date().getTime();
    app.scriptPreferences.userInteractionLevel = UserInteractionLevels.NEVER_INTERACT;
    var doc = app.open(File(app.scriptArgs.getValue("src")), false, OpenOptions.OPEN_COPY), out = [], styles = {};
    function v(o, k) { return safe(function () { var x = o[k]; if (x === null || x === undefined) return "null"; if (x instanceof Array) { var a = []; for (var i = 0; i < x.length; i++) a.push(typeof x[i] === "number" ? Math.round(x[i] * 100) / 100 : x[i]); return a.join(","); } if (typeof x === "object") return "@" + safe(function () { return x.name; }, String(x)); return typeof x === "number" ? String(Math.round(x * 100) / 100) : String(x); }, "?"); }
    // category switch on the object style -> [where to read, property names]
    var CATS = [
        ["enableFill", "", ["fillColor", "fillTint"]],
        ["enableStroke", "", ["strokeColor", "strokeTint"]],
        ["enableStrokeAndCornerOptions", "", ["strokeWeight", "strokeType", "strokeAlignment", "topLeftCornerOption", "topLeftCornerRadius"]],
        ["enableTextFrameGeneralOptions", "tf", ["insetSpacing", "textColumnCount", "textColumnGutter", "verticalJustification", "ignoreWrap"]],
        ["enableTextFrameBaselineOptions", "tf", ["firstBaselineOffset", "minimumFirstBaselineOffset"]],
        ["enableTextFrameAutoSizingOptions", "tf", ["autoSizingType", "autoSizingReferencePoint"]],
        ["enableTextWrapAndOthers", "wrap", ["textWrapMode", "textWrapOffset"]]
    ];
    function part(o, w) { return w === "tf" ? safe(function () { return o.textFramePreferences; }) : w === "wrap" ? safe(function () { return o.textWrapPreferences; }) : o; }
    var KEEP = { TextFrame: 1, Rectangle: 1, Oval: 1, Polygon: 1, GraphicLine: 1, Group: 1 }, all = doc.allPageItems;
    for (var i = 0; i < all.length; i++) {
        var it = all[i], type = it.constructor.name;
        if (!KEEP[type]) continue;
        var os = safe(function () { return it.appliedObjectStyle; }), osn = os ? os.name : "?", diffs = [];
        styles[osn] = (styles[osn] || 0) + 1;
        if (os && osn !== "[None]") {
            for (var c = 0; c < CATS.length; c++) {
                if (!safe(function () { return os[CATS[c][0]]; }, false)) continue;
                if (CATS[c][1] === "tf" && type !== "TextFrame") continue;
                var a = part(it, CATS[c][1]), b = part(os, CATS[c][1]);
                if (!a || !b) continue;
                for (var p = 0; p < CATS[c][2].length; p++) {
                    var k = CATS[c][2][p], av = v(a, k), bv = v(b, k);
                    if (av !== bv && av !== "?" && bv !== "?") diffs.push(k + ": " + av + " (style " + bv + ")");
                }
            }
        }
        out.push({ page: safe(function () { var pg = it.parentPage; return pg ? ((pg.parent.constructor.name === "MasterSpread") ? "master " + pg.parent.name : pg.name) : "pasteboard/inline"; }, "?"),
            type: type, layer: safe(function () { return it.itemLayer.name; }, "?"), label: safe(function () { return it.label; }, ""), objectStyle: osn,
            bounds: v(it, "geometricBounds"),
            text: type === "TextFrame" ? safe(function () { return String(it.parentStory.contents).replace(/[\r\n]/g, " ").substring(0, 40); }, "") : "",
            diffs: diffs });
    }
    doc.close(SaveOptions.NO);
    writeText(app.scriptArgs.getValue("log"), ser({ seconds: (new Date().getTime() - t0) / 1000, frames: out.length, byObjectStyle: styles, list: out }));
    return "ok " + out.length;
})();
