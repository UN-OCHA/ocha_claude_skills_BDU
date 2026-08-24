// build_template.jsx — starting point for an unattended Illustrator export.
// ---------------------------------------------------------------
// Copy into the project, fill in the CONFIG block, delete what you do not need.
// Run headless (Illustrator must already be running):
//
//   osascript -e 'tell application "Adobe Illustrator" to do javascript file "/abs/path/build.jsx"'
//
// Silent by design: no alert(), no confirm(). Both block forever on an
// unattended run. Everything goes to the log file, which the caller reads.
// Every step is written to be a no-op once applied, so re-running is safe.
// ---------------------------------------------------------------

#target illustrator

(function () {

    // ===================== CONFIG =====================
    // Hardcoded on purpose: $.fileName resolves only for `do javascript file`,
    // not when the script body is passed as a string. Do not "simplify" this away.
    var BASE     = "/absolute/path/to/project";
    var MASTER   = BASE + "/master.ai";
    var PNG_DIR  = BASE + "/export/PNG";
    var SVG_DIR  = BASE + "/export/SVG";
    var LOG_FILE = BASE + "/build.log";

    var REQUIRED_FONTS = ["Roboto-Medium"];      // PostScript names, not menu names

    // Illustrator default artboard names -> the filenames you want.
    var MAP = {
        // "Artboard 1": "PRODUCT_EN",
    };

    // Artboards that exist but are not deliverables. Anything containing "_dup"
    // is skipped too. Without this, every rebuild reinstates files someone
    // deliberately deleted.
    var SKIP_EXPORT = {
        // "PRODUCT_overview": true
    };

    // Brand colours to pin, as exact RGB. Get the values from ocha-visual-identity.
    var BRAND = {
        // yellow: [255, 200, 0],
        black: [0, 0, 0],
        white: [255, 255, 255]
    };
    // ==================================================

    var log = [];
    function say(s) { log.push(s); }
    function flush() {
        var f = new File(LOG_FILE);
        f.open("w"); f.encoding = "UTF-8"; f.lineFeed = "Unix";
        f.write(log.join("\n") + "\n");
        f.close();
    }

    app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
    say("=== build ===");

    try {

        // ---------- 1. fonts, before anything else ----------
        // Illustrator substitutes a missing font silently and still reports
        // success. The .ai keeps the right reference, so only the exported
        // pixels are wrong. Refuse to run rather than ship that.
        function fontInstalled(psName) {
            for (var i = 0; i < app.textFonts.length; i++) {
                if (app.textFonts[i].name === psName) { return true; }
            }
            return false;
        }
        var missing = [];
        for (var f = 0; f < REQUIRED_FONTS.length; f++) {
            if (!fontInstalled(REQUIRED_FONTS[f])) { missing.push(REQUIRED_FONTS[f]); }
        }
        if (missing.length > 0) { say("ABORT missing fonts: " + missing.join(", ")); flush(); return; }
        say("fonts ok: " + REQUIRED_FONTS.join(", "));

        // ---------- 2. open ----------
        var fh = new File(MASTER);
        if (!fh.exists) { say("ABORT master not found: " + MASTER); flush(); return; }
        var doc = app.open(fh);
        app.activeDocument = doc;

        // Unlock to work, but REMEMBER visibility. Forcing every layer visible
        // switches on guide and working layers, which then reach the export.
        var wasVisible = {};
        for (var L = 0; L < doc.layers.length; L++) {
            wasVisible[doc.layers[L].name] = doc.layers[L].visible;
            doc.layers[L].locked = false;
            doc.layers[L].visible = true;
        }

        // ---------- 3. text edits ----------
        // Change only the characters that change. Replacing tf.contents wholesale
        // resets per-character styling and kerning across the whole frame.
        // Example — roll a year forward, and do nothing if it is already correct:
        var edits = 0;
        for (var t = 0; t < doc.textFrames.length; t++) {
            var tf = doc.textFrames[t];
            var idx = tf.contents.indexOf("2026"), guard = 0;
            while (idx !== -1 && guard < 50) {
                try { tf.characters[idx + 3].contents = "7"; }
                catch (e) { tf.contents = tf.contents.replace(/2026/g, "2027"); }
                edits++; idx = tf.contents.indexOf("2026"); guard++;
            }
        }
        say("text edits this run: " + edits);

        // ---------- 4. name the artboards ----------
        var renamed = 0, unmatched = [];
        for (var a = 0; a < doc.artboards.length; a++) {
            var nm = doc.artboards[a].name;
            if (MAP[nm] !== undefined) { doc.artboards[a].name = MAP[nm]; renamed++; }
            else if (MAP[nm] === undefined && nm.indexOf("Artboard") === 0) { unmatched.push(nm); }
        }
        say("artboards renamed this run: " + renamed);
        if (unmatched.length > 0) { say("UNRECOGNISED artboards: " + unmatched.join(", ")); }

        // ---------- 5. pin the brand colours ----------
        // Classify on well-separated traits, never exact values: a converted
        // colour never lands exactly where you expect. Log what changed so a
        // wrong classifier shows up here instead of silently shipping.
        function rgb(v) {
            var c = new RGBColor();
            c.red = v[0]; c.green = v[1]; c.blue = v[2];
            return c;
        }
        function targetFor(c) {
            if (!c || c.typename !== "RGBColor") { return null; }
            var mx = Math.max(c.red, Math.max(c.green, c.blue));
            var mn = Math.min(c.red, Math.min(c.green, c.blue));
            if (mn >= 245) { return BRAND.white; }
            if (mx <= 45)  { return BRAND.black; }
            // add your own branches here, e.g.
            // if (c.red >= 200 && c.green >= 150 && c.green <= 235 && c.blue <= 90) { return BRAND.yellow; }
            return null;
        }
        var pinned = 0;
        for (var p = 0; p < doc.pathItems.length; p++) {
            var pi = doc.pathItems[p];
            if (!pi.filled) { continue; }
            var tgt = targetFor(pi.fillColor);
            if (!tgt) { continue; }
            if (Math.abs(pi.fillColor.red - tgt[0]) < 0.5 &&
                Math.abs(pi.fillColor.green - tgt[1]) < 0.5 &&
                Math.abs(pi.fillColor.blue - tgt[2]) < 0.5) { continue; }
            pi.fillColor = rgb(tgt);
            pinned++;
        }
        say("brand colours pinned: " + pinned);

        // restore visibility before saving or exporting
        for (var L2 = 0; L2 < doc.layers.length; L2++) {
            var n2 = doc.layers[L2].name;
            if (wasVisible[n2] !== undefined) { doc.layers[L2].visible = wasVisible[n2]; }
        }
        doc.save();
        say("master saved");

        // ---------- 6. export ----------
        var pngFolder = new Folder(PNG_DIR), svgFolder = new Folder(SVG_DIR);
        if (!pngFolder.exists) { pngFolder.create(); }
        if (!svgFolder.exists) { svgFolder.create(); }

        var indices = [], exported = [], skipped = [];
        for (var b = 0; b < doc.artboards.length; b++) {
            var abName = doc.artboards[b].name;
            if (abName.indexOf("_dup") !== -1 || SKIP_EXPORT[abName] === true) {
                skipped.push(abName);
                continue;
            }
            indices.push(b + 1);                     // exportForScreens is 1-based
            exported.push(abName);
        }

        var what = new ExportForScreensItemToExport();
        what.artboards = indices.join(",");
        what.document = false;

        var pngOpts = new ExportForScreensOptionsPNG24();
        pngOpts.transparency = true;
        pngOpts.scaleType = ExportForScreensScaleType.SCALEBYWIDTH;
        pngOpts.scaleTypeValue = 1024;
        pngOpts.antiAliasing = AntiAliasingMethod.ARTOPTIMIZED;
        pngOpts.interlaced = false;
        doc.exportForScreens(pngFolder, ExportForScreensType.SE_PNG24, pngOpts, what, "");

        var svgOpts = new ExportForScreensOptionsWebOptimizedSVG();
        svgOpts.fontType = SVGFontType.OUTLINEFONT;   // no font dependency in the SVG
        svgOpts.coordinatePrecision = 3;
        svgOpts.svgMinify = false;
        svgOpts.svgResponsive = false;
        doc.exportForScreens(svgFolder, ExportForScreensType.SE_SVG, svgOpts, what, "");

        say("exported " + indices.length + " artboards x (PNG + SVG)" +
            " | not exported (" + skipped.length + "): " + skipped.join(", "));
        say("exported names: " + exported.join(", "));

        doc.close(SaveOptions.SAVECHANGES);
        say("OK done");

    } catch (err) {
        say("ERROR line " + err.line + ": " + err);
    }

    app.userInteractionLevel = UserInteractionLevel.DISPLAYALERTS;
    flush();

})();
