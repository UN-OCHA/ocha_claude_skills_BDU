// Read-only: list the document's fonts and status, opened with a window as the user would. Args: src.
#target indesign
#include "lib.jsxinc"
(function(){ var d=openOriginal(app.scriptArgs.getValue("src"),true),o=[];
  for(var i=0;i<d.fonts.length;i++) o.push(d.fonts[i].name.replace("\t"," ")+" = "+String(d.fonts[i].status));
  d.close(SaveOptions.NO); return o.join("\n"); })();
