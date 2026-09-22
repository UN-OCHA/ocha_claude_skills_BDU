#!/usr/bin/env python3
"""Audition sound options in the film itself, before one goes in.

For one sound KIND (or a few that share a recording), this builds the effects track once per
candidate recording, mixes it exactly like the film (mix.py: the film's music + effects, no voice),
and cuts a short clip of the moment that kind plays — so the options are compared on the real
picture, at the real level, with nothing else changed. The person picks by ear; nothing changes in
the film until they do ("suggest it here first before adding": Javier, SG Awards film, 21 Sept 2026).
Then set PALETTE, TRIM and LEVEL in sfx_mix.py to what they heard.

    python3 sfx_audition.py chime                                   # one set from AUDITIONS below
    python3 sfx_audition.py chime --picture previews/<name>_film_v07.mp4

Clips go to previews/auditions/<set>_<option>.mp4 (a subfolder: the review tool doesn't list them).
The film's own effects track is rebuilt exactly as it was at the end.
"""
import argparse
import json
import pathlib
import subprocess
import sys

BUILD = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(BUILD))
import sfx_mix as X  # noqa: E402
import mix as M      # noqa: E402  (the shared mixer: ocha-video's scripts/audio/mix.py, copied in by new_cutout_film.py)

PREVIEWS = BUILD / "previews"
OUT_DIR = PREVIEWS / "auditions"
FILM = json.loads((BUILD / "film.json").read_text(encoding="utf-8"))

# Each set: the kinds it swaps, their level (dB under the voice), the options {name: (recordings, trim s)}
# and, if needed, the clip (start, end) — by default from 0.6 s before the kind's first cue to 2 s after.
# Search candidates in the library's BoomBox/boombox_index.csv; check each is ONE strike first (python3 sfx_mix.py --strikes "Title|Pack").
# The example is the SG film's second round for its blue-icon sound: Javier picked T1.
AUDITIONS = {
    "chime": {
        "kinds": ("chime",), "level": {"chime": 17},
        "options": {
            "P1_paper_flap":    ([("Paper Flap 02", "Tactile Feelings")], 0.3),
            "P3_cardboard_tap": ([("Cardboard Canister - Tap with Hand 03", "Impact Catalogue")], 0.2),
            "T1_tin_foil_box":  ([("Tin Foil Box - Hit", "Tactile Feelings")], 0.36),
            "T3_pan_lid":       ([("Pan Lid - Hit 02", "Essentials")], 0.21),
        },
    },
}


def latest_render():
    renders = sorted(PREVIEWS.glob("*.mp4"), key=lambda p: p.stat().st_mtime)
    if not renders:
        sys.exit("No render in previews/ to cut the clips from: render the film first, or pass --picture.")
    return renders[-1]


def main():
    ap = argparse.ArgumentParser(description="Clips of one moment with each candidate sound.")
    ap.add_argument("which", choices=sorted(AUDITIONS))
    ap.add_argument("--picture", help="the render to cut from (default: the newest in previews/)")
    a = ap.parse_args()
    A = AUDITIONS[a.which]
    kinds, level, options = A["kinds"], A["level"], A["options"]
    picture = pathlib.Path(a.picture) if a.picture else latest_render()
    cues = X.get_cues()
    times = [c["t"] for c in cues if c["kind"] in kinds]
    if not times:
        sys.exit(f"The score (score.js) has no cue of {kinds}.")
    clip = A.get("clip") or (max(0.0, times[0] - 0.6), times[0] + 2.0)
    music = FILM.get("music", {})
    track = BUILD.parents[1] / music["file"] if music.get("file") else None   # relative to the job folder
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    keep = {k: (X.PALETTE[k], X.TRIM.get(k), X.LEVEL[k]) for k in kinds}
    stem, full, out0 = OUT_DIR / "_stem.wav", OUT_DIR / "_full.mp4", X.OUT
    try:
        for name, (recordings, trim) in options.items():
            for k in kinds:
                X.PALETTE[k], X.TRIM[k], X.LEVEL[k] = recordings, trim, level[k]
            X.OUT = stem
            X.build(cues, write=True)
            M.mix(picture, full, music=track, sfx=stem, music_db=music.get("db", M.MUSIC_DB),
                  music_offset=music.get("offset", 0.0))
            out = OUT_DIR / f"{a.which}_{name}.mp4"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{clip[0]}", "-to", f"{clip[1]}", "-i", str(full),
                            "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p"] + M.audio_encoder() +
                           ["-movflags", "+faststart", str(out)], check=True)
            print(out.relative_to(BUILD))
    finally:   # the film's own track, exactly as it was
        for k, (pal, trim, lvl) in keep.items():
            X.PALETTE[k] = pal
            if trim is None:
                X.TRIM.pop(k, None)
            else:
                X.TRIM[k] = trim
            X.LEVEL[k] = lvl
        X.OUT = out0
        X.build(cues, write=True)
        for f in (stem, full):
            f.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
