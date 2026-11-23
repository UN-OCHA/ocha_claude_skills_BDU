#!/usr/bin/env python3
"""Lists every local text override in an IDML export: anything set directly on a paragraph or character range,
beyond its applied styles. This is what InDesign's Style Override Highlighter shows; `styleOverridden` misses some.
Usage: overrides_idml_audit.py file.idml [...]. Read only. Export with export_idml_copy.jsx."""
import collections, re, sys, zipfile
import xml.etree.ElementTree as ET
SKIP = {"AppliedParagraphStyle", "AppliedCharacterStyle", "ParagraphBreakType", "Self", "AppliedConditions"}
def clean(s): return s.split("/")[-1].replace("%3a", ":").replace("$ID", "")
def props(el):
    out = {k: v for k, v in el.attrib.items() if k not in SKIP}
    p = el.find("Properties")
    if p is not None:
        for c in p: out[c.tag] = (c.text or "").strip() or "(set)"
    return out
for path in sys.argv[1:]:
    z = zipfile.ZipFile(path); found = []
    for n in z.namelist():
        if not n.startswith("Stories/"): continue
        root = ET.fromstring(z.read(n))
        for psr in root.iter("ParagraphStyleRange"):
            ps = clean(psr.get("AppliedParagraphStyle", "?")); pp = props(psr)
            text = "".join((c.text or "") for c in psr.iter("Content"))[:45]
            if pp: found.append((ps, "paragraph", tuple(sorted(pp.items())), text))
            for csr in psr.findall("CharacterStyleRange"):
                cp = props(csr)
                if cp: found.append((ps, "run:" + clean(csr.get("AppliedCharacterStyle", "?")), tuple(sorted(cp.items())), "".join((c.text or "") for c in csr.iter("Content"))[:45]))
    print(f"\n## {path.split('/')[-1]}: {len(found)} ranges")
    by = collections.defaultdict(list)
    for ps, kind, pr, t in found: by[(ps, kind, pr)].append(t)
    for (ps, kind, pr), ts in sorted(by.items(), key=lambda x: (-len(x[1]), x[0][0])):
        print(f"{len(ts):4} {ps} | {kind} | {dict(pr)} | e.g. {ts[0]!r}")
