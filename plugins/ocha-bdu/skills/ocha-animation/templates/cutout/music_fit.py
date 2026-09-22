#!/usr/bin/env python3
"""Measure a music track's loudness envelope and line it up with the film's scenes.

The shortlist was picked by LOOKING at Flippermusic's waveform pictures. This
measures the real audio instead, so the claims ("builds into 0:39", "calm from
1:03") are checked rather than eyeballed.

    python3 music_fit.py                      # every track in audio/music/
    python3 music_fit.py --offset 3.0 FILE    # as if the track started 3 s late

Prints, per track: the level every second (dB relative to the track's own peak
second), where the biggest rises and drops are, and what sits at each scene
boundary of the film.
"""

import argparse
import array
import math
import pathlib
import subprocess
import sys
import wave

BUILD = pathlib.Path(__file__).resolve().parent
MUSIC = BUILD / "audio" / "music"

# The film's length and scene starts, read from timeline.json (timeline.py) — never retyped here, so a
# change of pacing is measured against the film as it now is.
_TL = __import__("json").loads((BUILD / "timeline.json").read_text(encoding="utf-8"))
FILM = float(_TL["duration"])
SCENES = [(float(s["start"]), s["title"]) for s in _TL["scenes"]]

STEP = 0.5  # seconds per measurement


def envelope(path, step=STEP):
    """RMS per step, in dB relative to the loudest step. Decodes via ffmpeg."""
    cmd = ["ffmpeg", "-v", "error", "-i", str(path),
           "-ac", "1", "-ar", "8000", "-f", "wav", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    # ffmpeg streams to stdout with an unknown length in the header; the wave
    # module copes as long as we hand it a seekable buffer.
    import io
    with wave.open(io.BytesIO(raw), "rb") as w:
        rate = w.getframerate()
        frames = w.readframes(w.getnframes())
    samples = array.array("h")
    samples.frombytes(frames[: len(frames) // 2 * 2])
    n = int(rate * step)
    out = []
    for i in range(0, len(samples) - n, n):
        chunk = samples[i: i + n]
        rms = math.sqrt(sum(s * s for s in chunk) / len(chunk)) or 1.0
        out.append(20 * math.log10(rms))
    if not out:
        return [], step
    peak = max(out)
    return [v - peak for v in out], step


def bar(db, width=34):
    """A -40..0 dB bar."""
    filled = max(0, min(width, round((db + 40) / 40 * width)))
    return "█" * filled + "·" * (width - filled)


def moves(env, step, window=3.0):
    """The biggest rises and drops, as (time, change in dB)."""
    k = max(1, int(window / step))
    out = []
    for i in range(k, len(env) - k):
        before = sum(env[i - k:i]) / k
        after = sum(env[i:i + k]) / k
        out.append((i * step, after - before))
    return out


def report(path, offset=0.0):
    env, step = envelope(path)
    if not env:
        print(f"{path.name}: no audio")
        return
    print(f"\n{'=' * 78}\n{path.stem}  ({len(env) * step:.0f} s"
          + (f", started {offset:+.1f} s into the film" if offset else "") + ")")
    print(f"{'=' * 78}")

    m = moves(env, step)
    ups = sorted((x for x in m if x[1] > 0), key=lambda x: -x[1])[:4]
    downs = sorted((x for x in m if x[1] < 0), key=lambda x: x[1])[:4]
    def fmt(t):
        return f"{int(t) // 60}:{t % 60:04.1f}"
    print("  biggest rises: " + ", ".join(f"{fmt(t + offset)} ({d:+.1f} dB)" for t, d in ups))
    print("  biggest drops: " + ", ".join(f"{fmt(t + offset)} ({d:+.1f} dB)" for t, d in downs))

    print(f"\n  film time        level (dB below this track's peak)")
    scene_at = {}
    for start, name in SCENES:
        scene_at[round(start / step)] = name
    for i, db in enumerate(env):
        t = i * step + offset
        if t > FILM + 1:
            break
        if t < 0:
            continue
        tag = scene_at.get(round((t) / step), "")
        mark = f"  ◀ {tag}" if tag else ""
        if i % 2 == 0 or tag:  # one line per second, plus any scene start
            print(f"  {fmt(t):>7}  {db:6.1f}  {bar(db)}{mark}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="mp3/wav files (default: audio/music/*.mp3)")
    ap.add_argument("--offset", type=float, default=0.0,
                    help="seconds into the film at which the track starts")
    a = ap.parse_args()
    paths = [pathlib.Path(f) for f in a.files] or sorted(MUSIC.glob("*.mp3"))
    if not paths:
        sys.exit(f"no tracks found in {MUSIC}")
    for p in paths:
        report(p, a.offset)


if __name__ == "__main__":
    main()
