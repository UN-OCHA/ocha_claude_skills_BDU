#!/usr/bin/env python3
"""
OCHA social render — thin shim over the CANONICAL renderer.

This script used to carry its own copy of the caption / lower-third / ending
code. Since 2026-07-12 the one canonical implementation lives in the QuickVid
repo (engine/social_brand.py + engine/lower_third.py, numbers in
browser/brand-lt.json — look B). This shim keeps the old CLI working
(`render_social_video.py job.json`) and simply translates the job spec and
runs the engine, so direct-chat edits and the QuickVid app can never drift
apart again.

Spec translation (old skill format -> engine format):
  ending: {logo: true, ...}  ->  ending: {style: "over_footage", ...}
  ending: {logo: false}      ->  ending: {style: "none"}
  (an explicit ending.style passes through untouched;
   brand_repo is ignored — the engine uses its own bundled assets)

Note: the old script could auto-detect a black tail to place the logo; the
engine expects `footage_end` (seconds) in the spec for that case. Clips that
end on footage (the current OCHA standard) need nothing.
"""
import json
import os
import io
import subprocess
import sys
import tempfile

# --- Locate the QuickVid engine ----------------------------------------------------
# Never hardcode one path: this skill is shared, and the engine lives in a DIFFERENT
# place for a normal user than for a QuickVid developer.
#   - Mac install     -> ~/Library/Application Support/OCHA QuickVid/app
#   - Windows install -> %LocalAppData%\OCHA QuickVidpp
#   - Developer       -> set QUICKVID_HOME
# A candidate counts only if it has BOTH the engine AND a built venv. The venv
# interpreter differs by platform: .venv/bin/python3 vs .venv\Scripts\python.exe.
def _find_quickvid():
    candidates = []
    if os.environ.get("QUICKVID_HOME"):
        candidates.append(os.environ["QUICKVID_HOME"])

    supports = [os.path.join(os.path.expanduser("~"), "Library",
                             "Application Support", "OCHA QuickVid")]
    if os.environ.get("LOCALAPPDATA"):
        supports.append(os.path.join(os.environ["LOCALAPPDATA"], "OCHA QuickVid"))

    for support in supports:
        relocated = os.path.join(support, "home")   # written if QuickVid was relocated
        if os.path.isfile(relocated):
            try:
                candidates.append(io.open(relocated, encoding="utf-8").read().strip())
            except OSError:
                pass
        candidates.append(os.path.join(support, "app"))
    # NOTE: a Dropbox-synced clone is deliberately NOT probed. Dropbox ignores
    # .gitignore, so a shared repo carries the OWNER's .venv — present on disk but
    # pointing at their Python. It would pass an existence check, then fail at run time.

    for c in candidates:
        if not c:
            continue
        engine = os.path.join(c, "engine", "social_brand.py")
        if not os.path.exists(engine):
            continue
        for venv in (os.path.join(c, ".venv", "bin", "python3"),
                     os.path.join(c, ".venv", "Scripts", "python.exe")):
            if os.path.exists(venv):
                return c, engine, venv
    return None, None, None


QUICKVID, ENGINE, VENV_PY = _find_quickvid()


def main(cfgpath):
    if not ENGINE:
        sys.exit(
            "OCHA QuickVid engine not found.\n\n"
            "Install it once - about 10 min, no admin rights. Open this page in CHROME:\n\n"
            "  https://un-ocha.github.io/quickvid_BDU/\n\n"
            "  Mac     - copy the line it shows, paste it into Terminal.\n"
            "  Windows - download the installer it offers and double-click it.\n\n"
            "Already installed but misbehaving (asks to restart, reports an old version)?\n"
            "Delete the OCHA QuickVid app, then use Help and reinstall at the bottom of\n"
            "that page. Restarting alone does not fix a stale install.\n\n"
            "Kept somewhere unusual? Point at it directly:\n"
            "  export QUICKVID_HOME=\"/path/to/ocha_quick_vid\""
        )
    # encoding="utf-8" is NOT optional: job.json carries Spanish accents and Arabic,
    # and Python's default is the PLATFORM's — cp1252 on Windows, which has neither.
    # Works by luck on this Mac; the repo's CLAUDE.md has the full story.
    with open(cfgpath, encoding="utf-8") as fh:
        cfg = json.load(fh)
    end = cfg.get("ending") or {}
    if "style" not in end:                      # old skill format -> engine style enum
        end = {**end, "style": ("over_footage" if end.get("logo", True) else "none")}
        end.pop("logo", None)
    cfg["ending"] = end
    cfg.pop("brand_repo", None)                 # engine bundles its own logo/click/fonts

    fd, spec = tempfile.mkstemp(suffix="_social_spec.json")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2, ensure_ascii=False)
    py = VENV_PY if os.path.exists(VENV_PY) else sys.executable
    print("Rendering via the canonical QuickVid engine (look B)…", flush=True)
    r = subprocess.run([py, ENGINE, "--spec", spec])
    os.unlink(spec)
    sys.exit(r.returncode)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: render_social_video.py job.json")
        sys.exit(1)
    main(sys.argv[1])
