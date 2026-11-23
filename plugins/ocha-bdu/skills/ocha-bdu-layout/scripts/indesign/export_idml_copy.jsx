// Read only: exports a COPY of a file to IDML, for overrides_idml_audit.py. Args: src, out.
#target indesign
(function () {
    app.scriptPreferences.userInteractionLevel = UserInteractionLevels.NEVER_INTERACT;
    var doc = app.open(File(app.scriptArgs.getValue("src")), false, OpenOptions.OPEN_COPY);
    doc.exportFile(ExportFormat.INDESIGN_MARKUP, File(app.scriptArgs.getValue("out")));
    doc.close(SaveOptions.NO); return "ok";
})();
