#!/usr/bin/env python3
"""Start a cut-out film in a job folder: the kit, the shared tools, and a demo that builds at once.

    python3 <ocha-animation skill>/scripts/new_cutout_film.py "<job folder>" --title "Film title"

Copies into <job>/assets/build/:
  - this skill's templates/cutout/ (the engine, the demo film, the build tools)
  - from the ocha-video skill beside this one: scripts/audio/mix.py and voice_clarity.py (the mix and
    the voice check, shared by every OCHA video) and scripts/review/ (the review tool) as review/
and, if the job has no voice timings yet, the demo's into assets/voice/voiceover_timings.json, so the
demo film builds before any voice exists. NEVER overwrites a file that is already there: re-running it
on a job only adds what is missing. The job keeps its own copy of every tool (assets/ = what is needed
to rebuild the work: ocha-files-and-folders).
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT = HERE.parent / "templates" / "cutout"
VIDEO = HERE.parents[1] / "ocha-video"   # the sibling skill, wherever the skills are installed


def copy_tree(src, dst, skip=()):
    added = kept = 0
    for f in sorted(src.rglob("*")):
        rel = f.relative_to(src)
        if f.is_dir() or rel.parts[0] in skip or f.name.startswith(".") or "__pycache__" in rel.parts:
            continue
        out = dst / rel
        if out.exists():
            kept += 1
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(f, out)   # the content only (like cp -X: no Dropbox tag carried over)
        added += 1
    return added, kept


def main():
    ap = argparse.ArgumentParser(description="Start a cut-out film in a job folder.")
    ap.add_argument("job", help="the job folder (ocha-files-and-folders: Projects/<year>/<office>/<job_name>)")
    ap.add_argument("--title", help="the film's title (default: from the folder name)")
    a = ap.parse_args()
    job = Path(a.job).expanduser().resolve()
    build = job / "assets" / "build"
    if not KIT.exists():
        sys.exit(f"The cut-out kit is missing: {KIT}")
    shared = {VIDEO / "scripts/audio/mix.py": build / "mix.py",
              VIDEO / "scripts/audio/voice_clarity.py": build / "voice_clarity.py"}
    if not all(p.exists() for p in shared) or not (VIDEO / "scripts/review/review_server.py").exists():
        sys.exit(f"The ocha-video skill's shared tools were not found next to this skill ({VIDEO}). "
                 "Install or update the OCHA skills, then run this again.")

    added, kept = copy_tree(KIT, build, skip=("demo",))
    for src, dst in shared.items():
        if dst.exists():
            kept += 1
        else:
            shutil.copyfile(src, dst); added += 1
    a2, k2 = copy_tree(VIDEO / "scripts/review", build / "review")
    added, kept = added + a2, kept + k2

    cfg_path = build / "film.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    if cfg.get("name") == "cutout_demo":   # a fresh copy: make it this job's
        cfg["name"] = job.name
        cfg["title"] = a.title or job.name.replace("_", " ").capitalize()
        cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    voice = job / "assets" / "voice" / "voiceover_timings.json"
    demo_voice = not voice.exists()
    if demo_voice:
        voice.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(KIT / "demo" / "voiceover_timings.json", voice)
    for d in (job / "info" / "review", build / "previews", build / "audio"):
        d.mkdir(parents=True, exist_ok=True)

    print(f"Cut-out film set up in {job}")
    print(f"  {added} files added, {kept} already there (left as they were)")
    if demo_voice:
        print("  the DEMO's word timings are in assets/voice/ until the real voice replaces them")
    print(f"Next: python3 \"{build / 'timeline.py'}\", then open \"{build / 'film' / 'world.html'}\" in Chrome.")
    print("The whole process: the ocha-animation skill → references/cutout-process.md")


if __name__ == "__main__":
    main()
