// Read only: a second, independent look for overrides, beyond InDesign's own flag (find_plus.jsx) and frames_audit.jsx.
// Compares every text run and paragraph with its styles, property by property; every frame with its object style for the
// categories frames_audit leaves out; every table with its table style; and lists page items overridden from a parent page.
// Changes NOTHING: never clear overrides to compare (see frames_audit.jsx). Opens a COPY. Args: src, log.
#target indesign
#include "lib.jsxinc"
(function () {
    app.scriptPreferences.userInteractionLevel = UserInteractionLevels.NEVER_INTERACT;
    var doc = app.open(File(app.scriptArgs.getValue("src")), false, OpenOptions.OPEN_COPY);
    var text = {}, frames = [], tables = [], parent = [];
    function nm(o) { return safe(function () { return o.name; }, String(o)); }
    function val(x) { if (x === null || x === undefined) return null; if (x instanceof Array) return x.length; if (typeof x === "object") return nm(x); return typeof x === "number" ? Math.round(x * 100) / 100 : String(x); }
    function unset(v) { return v === null || v === "Nothing" || v === "NOTHING" || v === "NothingEnum.NOTHING" || v === "" ; }
    var RUN = ["appliedFont", "fontStyle", "pointSize", "leading", "kerningMethod", "tracking", "capitalization", "position", "underline", "strikeThru", "fillColor", "fillTint", "strokeColor", "horizontalScale", "verticalScale", "baselineShift", "skew", "appliedLanguage", "noBreak", "ligatures"];
    var PARA = ["justification", "leftIndent", "rightIndent", "firstLineIndent", "lastLineIndent", "spaceBefore", "spaceAfter", "alignToBaseline", "keepLinesTogether", "keepWithNext", "keepAllLinesTogether", "keepFirstLines", "keepLastLines", "startParagraph", "hyphenation", "composer", "balanceRaggedLines", "ruleAbove", "ruleBelow", "dropCapCharacters", "dropCapLines", "bulletsAndNumberingListType", "spanColumnType", "spanSplitColumnCount", "tabStops"];
    function note(page, key, sample, pstyle) {
        var k = page + " | " + pstyle + " | " + key;
        if (!text[k]) text[k] = { n: 0, sample: sample }; text[k].n++;
    }
    function lookPara(p) {
        var ps = p.appliedParagraphStyle, psn = ps.name, pg = safe(function () { return pageOf(p.characters[0]); }, "?"), sample = String(p.contents).replace(/[\r\u0016]/g, "").substring(0, 40);
        for (var i = 0; i < PARA.length; i++) { var a = safe(function () { return val(p[PARA[i]]); }), b = safe(function () { return val(ps[PARA[i]]); }); if (a !== null && String(a) !== String(b)) note(pg, PARA[i] + ": " + a + " (style " + b + ")", sample, psn); }
        var r = p.textStyleRanges;
        for (var q = 0; q < r.length; q++) {
            var cs = r[q].appliedCharacterStyle, none = nm(cs) === "[None]";
            for (var j = 0; j < RUN.length; j++) {
                var k = RUN[j], av = safe(function () { return val(r[q][k]); }), cv = none ? null : safe(function () { return val(cs[k]); }), sv = unset(cv) ? safe(function () { return val(ps[k]); }) : cv;
                if (av !== null && String(av) !== String(sv)) note(pg, k + ": " + av + " (style " + sv + ")" + (none ? "" : " [" + nm(cs) + "]"), String(r[q].contents).replace(/[\r\u0016]/g, "").substring(0, 30), psn);
            }
        }
    }
    var st = doc.stories;
    for (var s = 0; s < st.length; s++) {
        var ps = st[s].paragraphs; for (var i = 0; i < ps.length; i++) if (ps[i].characters.length) lookPara(ps[i]);
        var tb = st[s].tables;
        for (var t = 0; t < tb.length; t++) {
            var T = tb[t], c = tb[t].cells, ts = T.appliedTableStyle, d = [];
            var TP = ["topBorderStrokeWeight", "bottomBorderStrokeWeight", "leftBorderStrokeWeight", "rightBorderStrokeWeight", "topBorderStrokeColor", "bottomBorderStrokeColor", "spaceBefore", "spaceAfter", "columnFillPriority", "startRowFillColor", "endRowFillColor", "startRowStrokeWeight", "endRowStrokeWeight", "startColumnStrokeWeight", "endColumnStrokeWeight", "startColumnStrokeColor", "endColumnStrokeColor"];
            for (var x = 0; x < TP.length; x++) { var a = safe(function () { return val(T[TP[x]]); }), b = safe(function () { return val(ts[TP[x]]); }); if (a !== null && !unset(b) && String(a) !== String(b)) d.push(TP[x] + ": " + a + " (style " + b + ")"); }
            if (d.length) tables.push({ page: safe(function () { return pageOf(T.cells[0].paragraphs[0].characters[0]); }, "?"), style: nm(ts), diffs: d });
            for (var k2 = 0; k2 < c.length; k2++) { var cp = c[k2].paragraphs; for (var q2 = 0; q2 < cp.length; q2++) if (cp[q2].characters.length) lookPara(cp[q2]); }
        }
    }
    var CATS = [
        ["enableTransparency", "tr", ["opacity", "blendMode"]],
        ["enableStrokeAndCornerOptions", "", ["strokeWeight", "strokeType", "endCap", "endJoin", "miterLimit", "gapColor", "topRightCornerOption", "bottomLeftCornerOption", "bottomRightCornerOption", "topRightCornerRadius", "bottomLeftCornerRadius", "bottomRightCornerRadius"]],
        ["enableTextFrameGeneralOptions", "tf", ["columnRule", "useFlexibleColumnWidth", "textColumnFixedWidth", "verticalBalanceColumns", "ignoreWrap"]],
        ["enableTextFrameAutoSizingOptions", "tf", ["useMinimumHeightForAutoSizing", "useMinimumWidthForAutoSizing", "useNoLineBreaksForAutoSizing", "minimumHeightForAutoSizing"]],
        ["enableFrameFittingOptions", "ff", ["fittingOnEmptyFrame", "fittingAlignment", "autoFit", "topCrop", "bottomCrop", "leftCrop", "rightCrop"]],
        ["enableStoryOptions", "so", ["opticalMarginAlignment", "opticalMarginSize"]],
        ["enableTextWrapAndOthers", "wrap", ["textWrapSide", "applyToMasterPageOnly"]],
        ["enableAnchoredObjectOptions", "ao", ["anchoredPosition", "spineRelative", "lockPosition"]]
    ];
    function part(o, w) { return safe(function () { return w === "tf" ? o.textFramePreferences : w === "wrap" ? o.textWrapPreferences : w === "ff" ? o.frameFittingOptions : w === "so" ? o.storyPreference : w === "tr" ? o.transparencySettings.blendingSettings : w === "ao" ? o.anchoredObjectSettings : o; }); }
    var KEEP = { TextFrame: 1, Rectangle: 1, Oval: 1, Polygon: 1, GraphicLine: 1, Group: 1 }, all = doc.allPageItems;
    for (var i2 = 0; i2 < all.length; i2++) {
        var it = all[i2], type = it.constructor.name; if (!KEEP[type]) continue;
        var pg = safe(function () { var p = it.parentPage; return p ? ((p.parent.constructor.name === "MasterSpread") ? "master " + p.parent.name : p.name) : "pasteboard/inline"; }, "?");
        if (safe(function () { return it.overridden; }, false)) parent.push({ page: pg, type: type, text: type === "TextFrame" ? String(it.parentStory.contents).substring(0, 30) : "" });
        var os = safe(function () { return it.appliedObjectStyle; }), n = os ? os.name : "?", diffs = [];
        if (os && n !== "[None]") for (var c2 = 0; c2 < CATS.length; c2++) {
            if (!safe(function () { return os[CATS[c2][0]]; }, false)) continue;
            if ((CATS[c2][1] === "tf" || CATS[c2][1] === "so") && type !== "TextFrame") continue;
            var a2 = part(it, CATS[c2][1]), b2 = part(os, CATS[c2][1]); if (!a2 || !b2) continue;
            for (var p2 = 0; p2 < CATS[c2][2].length; p2++) { var k3 = CATS[c2][2][p2], av2 = safe(function () { return val(a2[k3]); }), bv2 = safe(function () { return val(b2[k3]); }); if (av2 !== null && bv2 !== null && String(av2) !== String(bv2)) diffs.push(k3 + ": " + av2 + " (style " + bv2 + ")"); }
        }
        if (diffs.length) frames.push({ page: pg, type: type, style: n, text: type === "TextFrame" ? String(it.parentStory.contents).replace(/\r/g, " ").substring(0, 30) : "", diffs: diffs });
    }
    doc.close(SaveOptions.NO);
    writeText(app.scriptArgs.getValue("log"), ser({ document: File(app.scriptArgs.getValue("src")).name, text: text, frames: frames, tables: tables, overriddenFromParent: parent }));
    return "ok";
})();
