// Read only: finds styles that are patched rather than built properly. For every paragraph style: (1) nested, GREP and line
// styles, with what their character style changes; (2) in-use styles whose text looks different from what the style itself
// says (size, font, leading or colour), which means something else is drawing it; (3) use counts. For every character style:
// where it is used. Opens a COPY. Args: src, log.
#target indesign
#include "lib.jsxinc"
(function () {
    app.scriptPreferences.userInteractionLevel = UserInteractionLevels.NEVER_INTERACT;
    var d = app.open(File(app.scriptArgs.getValue("src")), false, OpenOptions.OPEN_COPY), R = { para: [], chars: [] };
    try {
        function nm(v) { if (typeof v === "string") return v; return safe(function () { return v.name; }, String(v)); }   // a character style's font can be a plain string
        function look(x) { return { size: x.pointSize, font: nm(x.appliedFont), leading: String(x.leading), color: nm(x.fillColor) }; }
        function cdesc(c) { var o = []; var K = ["fontStyle", "pointSize", "leading", "capitalization", "position", "tracking", "horizontalScale", "verticalScale", "skew"]; for (var i = 0; i < K.length; i++) { var v = safe(function () { return c[K[i]]; }); if (v !== null && v !== NothingEnum.NOTHING && v !== undefined) o.push(K[i] + "=" + String(v)); } var f = safe(function () { return c.fillColor; }); if (f && f !== NothingEnum.NOTHING) o.push("fill=" + nm(f)); var a = safe(function () { return c.appliedFont; }); if (a && a !== NothingEnum.NOTHING && nm(a)) o.push("font=" + nm(a)); return o.join(", "); }
        var use = {}, charUse = {}, st = d.stories, samples = {};
        function seen(p) { var n = safe(function () { return p.appliedParagraphStyle.name; }, ""); if (!n) return; use[n] = (use[n] || 0) + 1; if (p.length > 1) { var c = p.characters[0], l = look(c); (samples[n] = samples[n] || []); if (samples[n].length < 40) samples[n].push(l); } var r = p.textStyleRanges.everyItem().getElements(); for (var i = 0; i < r.length; i++) { var cn = r[i].appliedCharacterStyle.name; if (cn !== "[None]") charUse[cn] = (charUse[cn] || 0) + 1; } }
        for (var s = 0; s < st.length; s++) { var ps = st[s].paragraphs.everyItem().getElements(); for (var i = 0; i < ps.length; i++) seen(ps[i]); var tb = st[s].tables; for (var t = 0; t < tb.length; t++) { var cp = tb[t].cells.everyItem().paragraphs.everyItem().getElements(); for (var i = 0; i < cp.length; i++) seen(cp[i]); } }
        var a = d.allParagraphStyles;
        for (var i = 1; i < a.length; i++) { var x = a[i], o = { name: x.name, group: x.parent.name, base: safe(function () { return x.basedOn.name; }, ""), uses: use[x.name] || 0, own: look(x), nested: [], grep: [], line: [], differs: [] };
            var n = x.nestedStyles; for (var k = 0; k < n.length; k++) o.nested.push(nm(n[k].appliedCharacterStyle) + " until " + String(n[k].delimiter) + " x" + n[k].repetition + " {" + cdesc(n[k].appliedCharacterStyle) + "}");
            var g = x.nestedGrepStyles; for (var k = 0; k < g.length; k++) o.grep.push(nm(g[k].appliedCharacterStyle) + " on " + g[k].grepExpression + " {" + cdesc(g[k].appliedCharacterStyle) + "}");
            var l = x.nestedLineStyles; for (var k = 0; k < l.length; k++) o.line.push(nm(l[k].appliedCharacterStyle) + " {" + cdesc(l[k].appliedCharacterStyle) + "}");
            var sm = samples[x.name] || [], seenD = {}; for (var k = 0; k < sm.length; k++) for (var p in o.own) if (String(sm[k][p]) !== String(o.own[p])) { var key = p + ": style " + o.own[p] + " / text " + sm[k][p]; if (!seenD[key]) { seenD[key] = 1; o.differs.push(key); } }
            R.para.push(o); }
        var c = d.allCharacterStyles; for (var i = 1; i < c.length; i++) R.chars.push({ name: c[i].name, group: c[i].parent.name, direct: charUse[c[i].name] || 0, does: cdesc(c[i]) });
    } catch (e) { R.error = String(e) + " line " + e.line; }
    d.close(SaveOptions.NO); writeText(app.scriptArgs.getValue("log"), ser(R)); return "ok";
})();
