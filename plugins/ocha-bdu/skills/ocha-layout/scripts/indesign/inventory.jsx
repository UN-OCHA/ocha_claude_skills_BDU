// Read-only inventory of an InDesign document or template.
// Usage (from Claude, via osascript): set app.scriptArgs "src" (file to inspect) and "out" (JSON path).
// Opens the file WITHOUT a window, collects structure, closes WITHOUT saving.
// A .indt opens as an untitled copy, so the template on disk can never be modified.
#target indesign

(function () {
    var src = app.scriptArgs.getValue("src");
    var out = app.scriptArgs.getValue("out");

    // ExtendScript has no JSON object: minimal serializer.
    function q(s) {
        return '"' + String(s).replace(/\\/g, "\\\\").replace(/"/g, '\\"')
            .replace(/\r/g, "\\r").replace(/\n/g, "\\n").replace(/\t/g, "\\t")
            .replace(/[\u0000-\u001f]/g, " ") + '"';
    }
    function ser(v) {
        if (v === null || v === undefined) return "null";
        if (typeof v === "number" || typeof v === "boolean") return String(v);
        if (typeof v === "string") return q(v);
        if (v instanceof Array) { var a = []; for (var i = 0; i < v.length; i++) a.push(ser(v[i])); return "[" + a.join(",") + "]"; }
        var p = []; for (var k in v) if (v.hasOwnProperty(k)) p.push(q(k) + ":" + ser(v[k])); return "{" + p.join(",") + "}";
    }
    function safe(f, d) { try { return f(); } catch (e) { return d === undefined ? null : d; } }
    function groupPath(st) {
        var path = [], p = safe(function () { return st.parent; });
        while (p && safe(function () { return p.constructor.name; }) &&
               String(p.constructor.name).indexOf("Group") > -1) {
            path.unshift(p.name); p = safe(function () { return p.parent; });
        }
        return path.join(" / ");
    }

    var oldUI = app.scriptPreferences.userInteractionLevel;
    app.scriptPreferences.userInteractionLevel = UserInteractionLevels.NEVER_INTERACT;
    var doc = app.open(File(src), false);
    var R = { source: src, errors: [] };
    try {
        var dp = doc.documentPreferences;
        R.document = {
            pages: doc.pages.length, spreads: doc.spreads.length,
            pageWidth: dp.pageWidth, pageHeight: dp.pageHeight, facingPages: dp.facingPages,
            units: String(doc.viewPreferences.horizontalMeasurementUnits),
            bleedTop: dp.documentBleedTopOffset, language: safe(function () { return doc.textDefaults.appliedLanguage.name; })
        };
        R.layers = []; for (var i = 0; i < doc.layers.length; i++) { var L = doc.layers[i]; R.layers.push({ name: L.name, visible: L.visible, locked: L.locked }); }

        R.masters = [];
        for (i = 0; i < doc.masterSpreads.length; i++) {
            var m = doc.masterSpreads[i];
            R.masters.push({ name: m.name, pages: m.pages.length,
                basedOn: safe(function () { return m.appliedMaster ? m.appliedMaster.name : null; }) });
        }

        R.sections = [];
        for (i = 0; i < doc.sections.length; i++) { var s = doc.sections[i];
            R.sections.push({ name: s.name, marker: s.marker, start: s.pageStart.name, numbering: s.continueNumbering ? "continue" : s.pageNumberStart }); }

        R.pages = [];
        for (i = 0; i < doc.pages.length; i++) {
            var pg = doc.pages[i], texts = [], tf = pg.textFrames, overset = 0;
            for (var t = 0; t < tf.length; t++) {
                if (tf[t].overflows) overset++;
                var c = safe(function () { return tf[t].contents; }, "");
                if (c && texts.join(" ").length < 220) texts.push(String(c).replace(/\s+/g, " ").substring(0, 90));
            }
            R.pages.push({ n: pg.name, master: safe(function () { return pg.appliedMaster ? pg.appliedMaster.name : "[None]"; }),
                items: pg.pageItems.length, frames: tf.length, graphics: pg.allGraphics.length, overset: overset,
                text: texts.join(" | ").substring(0, 220) });
        }

        function styles(coll, kind) {
            var a = [];
            for (var i = 0; i < coll.length; i++) {
                var st = coll[i], o = { name: st.name, group: groupPath(st) };
                if (kind === "para" || kind === "char") {
                    o.font = safe(function () { var f = st.appliedFont; return (typeof f === "string") ? f : f.name; });
                    o.fontStyle = safe(function () { return st.fontStyle; });
                    o.size = safe(function () { return st.pointSize; });
                    o.leading = safe(function () { var l = st.leading; return (typeof l === "number") ? l : String(l); });
                    o.color = safe(function () { return st.fillColor.name; });
                    o.basedOn = safe(function () { var b = st.basedOn; return (typeof b === "string") ? b : b.name; });
                }
                a.push(o);
            }
            return a;
        }
        R.paragraphStyles = styles(doc.allParagraphStyles, "para");
        R.characterStyles = styles(doc.allCharacterStyles, "char");
        R.objectStyles = styles(doc.allObjectStyles, "obj");
        R.tableStyles = styles(doc.allTableStyles, "table");
        R.cellStyles = styles(doc.allCellStyles, "cell");

        R.swatches = [];
        for (i = 0; i < doc.swatches.length; i++) {
            var sw = doc.swatches[i], o2 = { name: sw.name, type: sw.constructor.name };
            if (sw.constructor.name === "Color") {
                o2.model = String(sw.model); o2.space = String(sw.space);
                o2.value = safe(function () { return sw.colorValue; });
            }
            R.swatches.push(o2);
        }

        R.fonts = [];
        for (i = 0; i < doc.fonts.length; i++) { var f = doc.fonts[i];
            R.fonts.push({ name: f.name, status: String(f.status) }); }

        R.links = [];
        for (i = 0; i < doc.links.length; i++) { var lk = doc.links[i];
            R.links.push({ name: lk.name, status: String(lk.status), path: safe(function () { return lk.filePath; }),
                page: safe(function () { return lk.parent.parentPage ? lk.parent.parentPage.name : "pasteboard/master"; }) }); }

        R.tocStyles = []; for (i = 0; i < doc.tocStyles.length; i++) R.tocStyles.push(doc.tocStyles[i].name);
        R.textVariables = []; for (i = 0; i < doc.textVariables.length; i++) R.textVariables.push(doc.textVariables[i].name);
        R.hyperlinks = doc.hyperlinks.length;
        R.storiesOverset = 0; for (i = 0; i < doc.stories.length; i++) if (doc.stories[i].overflows) R.storiesOverset++;
    } catch (e) {
        R.errors.push(String(e) + " line " + e.line);
    } finally {
        doc.close(SaveOptions.NO);
        app.scriptPreferences.userInteractionLevel = oldUI;
    }
    var fo = File(out); fo.encoding = "UTF-8"; fo.open("w"); fo.write(ser(R)); fo.close();
    return "ok";
})();
