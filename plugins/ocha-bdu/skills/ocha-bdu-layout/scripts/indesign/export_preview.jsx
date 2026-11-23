// Read-only: export a low-res preview PDF of a document. Args: src, pdf. Closes without saving.
#target indesign
#include "lib.jsxinc"
(function () {
    var doc = openOriginal(app.scriptArgs.getValue("src"), true);
    try { exportPreview(doc, app.scriptArgs.getValue("pdf")); } finally { doc.close(SaveOptions.NO); }
    return "ok";
})();
