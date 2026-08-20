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

# --- Locate the QuickVid engine -----------------------------------------------------
# Never hardcode one path: this skill is shared, and the engine lives in a DIFFERENT
# place for a normal user than for a QuickVid developer.
#   - Normal install (install.sh) -> ~/Library/Application Support/OCHA QuickVid/app
#   - Developer                   -> a git clone, often synced via Dropbox
# A candidate only counts if it has BOTH the engine AND a built venv. A Dropbox-synced
# clone often has the code but no .venv (virtualenvs contain absolute paths and compiled
# binaries, so they never sync usefully) — picking that would fail at run time.
def _find_quickvid():
    home = os.path.expanduser("~")
    support = os.path.join(home, "Library", "Application Support", "OCHA QuickVid")

    candidates = []
    if os.environ.get("QUICKVID_HOME"):                 # explicit override wins
        candidates.append(os.environ["QUICKVID_HOME"])
    relocated = os.path.join(support, "home")           # install.sh supports relocation
    if os.path.isfile(relocated):
        try:
            candidates.append(io.open(relocated, encoding="utf-8").read().strip())
        except OSError:
            pass
    candidates.append(os.path.join(support, "app"))     # standard install
    # NOTE: a Dropbox-synced clone is deliberately NOT probed. Dropbox ignores
    # .gitignore, so a shared repo carries the OWNER's .venv — present on disk but
    # pointing at their Homebrew Python. It would pass an existence check and then
    # fail at run time with a confusing error. Developers set QUICKVID_HOME instead.

    for c in candidates:
        if not c:
            continue
        engine = os.path.join(c, "engine", "social_brand.py")
        venv = os.path.join(c, ".venv", "bin", "python3")
        if os.path.exists(engine) and os.path.exists(venv):
            return c, engine, venv
    return None, None, None


QUICKVID, ENGINE, VENV_PY = _find_quickvid()


def main(cfgpath):
    if not ENGINE:
        sys.exit(
            "OCHA QuickVid engine not found.\n\n"
            "This skill renders through the QuickVid engine. Install it once "
            "(~10 min, no admin password):\n\n"
            "  curl -fsSL https://raw.githubusercontent.com/UN-OCHA/quickvid_BDU/main/install.sh | bash\n\n"
            "Already installed somewhere unusual? Point at it directly:\n"
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
