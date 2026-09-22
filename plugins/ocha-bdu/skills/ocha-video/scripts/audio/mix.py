#!/usr/bin/env python3
"""Lay the voice, the music and the sound effects under a picture: three layers at constant levels.

    python3 mix.py --picture film.mp4 --voice voice.wav --music track.wav --sfx sfx.wav --out film_v07.mp4
    python3 mix.py ... --no-voice --out film_v07_no_voice.mp4    # the same mix without the narrator, to judge
                                                                 # the effects and music (a review copy)

The picture is copied untouched (never re-encoded); only the sound is built, so a new mix takes seconds.
Any layer can be left out (no --music, no --sfx). The output runs as long as the picture, or --length.

THE MIX RULE (Javier, SG Awards film review, 21 September 2026): "think of voice / sound effects / music
as 3 layers with constant volume, with voice being louder, sound effects mid and music lower" · "even the
voice shouldn't push music down or up. Music is there on the background, same volume always."
So nothing ducks anything. Until then the music was ducked under the voice (ratio 6, 15 ms / 350 ms): it
followed the words, dropping up to 15 dB on a loud one — it pumped. The only level changes left are the
music's fade in at its start and fade out at the end.

  voice    at its own level (make it stand out: check with voice_clarity.py)
  effects  as built (their levels are set against the voice when the effects track is made)
  music    MUSIC_DB = −24 dB on a typical library track: its loudness then sits ~21 dB under the voice's
           speech (measured on the SG film), clearly behind the voice and under the effects

Audio encoder: Apple's AAC at 320k (see audio_encoder()).
"""

import argparse
import json
import pathlib
import subprocess
import sys

MUSIC_DB = -24
FADE_IN = 1.5
FADE_OUT = 3.0
FMT = "aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo"


def audio_encoder():
    """ffmpeg's own AAC at 192k smeared sharp sounds: on the SG film's typing its error was as loud as
    the sound itself (−15 dBFS error on a −16 dBFS keystroke, measured against the uncompressed mix,
    21 Sept 2026). Apple's AAC (AudioToolbox, macOS) at 320k: that error −48 dBFS; ffmpeg's own at 320k
    still −26 dBFS. ~3 MB for a 1:20 film either way. Where Apple's encoder is missing (not a Mac): the
    next best, and it says so. Its stream can run up to one AAC frame (~21 ms) past the picture —
    silence after the end, harmless; the START is sample-aligned with the picture (measured)."""
    have = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
    if " aac_at " in have:
        return ["-c:a", "aac_at", "-aac_at_mode", "cbr", "-b:a", "320k"]
    print("WARNING: Apple's AAC encoder (aac_at) is not in this ffmpeg — using ffmpeg's own AAC at 320k, which "
          "blurs sharp sounds (typing, taps) more. Export the final on a Mac.", file=sys.stderr)
    return ["-c:a", "aac", "-b:a", "320k"]


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(json.loads(out)["format"]["duration"])


def music_chain(length, db=MUSIC_DB, offset=0.0, fade_in=FADE_IN, fade_out=FADE_OUT):
    """The music layer's filters, in order (voice_clarity.py measures with exactly these): level, start
    offset (positive delays the track, negative trims its head), fade in at its start, fade out at the end."""
    head = f"adelay={int(offset * 1000)}|{int(offset * 1000)}" if offset >= 0 else f"atrim=start={-offset},asetpts=PTS-STARTPTS"
    start = max(0.0, offset)
    return (f"{FMT},{head},volume={db}dB,afade=t=in:st={start:.3f}:d={fade_in},"
            f"afade=t=out:st={length - fade_out:.3f}:d={fade_out},apad,atrim=0:{length}")


def mix(picture, out, voice=None, music=None, sfx=None, length=None, music_db=MUSIC_DB, music_offset=0.0,
        fade_in=FADE_IN, fade_out=FADE_OUT):
    picture, out = pathlib.Path(picture), pathlib.Path(out)
    layers = [(p, n) for p, n in ((voice, "voice"), (music, "music"), (sfx, "sfx")) if p]
    for p in [picture] + [pathlib.Path(p) for p, _ in layers]:
        if not pathlib.Path(p).exists():
            sys.exit(f"missing: {p}")
    if out.resolve() == picture.resolve():   # ffmpeg would read and write the same file
        sys.exit(f"refusing to write the mix over its own picture: {out}")
    if not layers:
        sys.exit("nothing to mix: give at least one of --voice, --music, --sfx")
    length = length or duration(picture)
    inputs, chain, heard = ["-i", str(picture)], "", []
    for i, (p, name) in enumerate(layers, start=1):
        inputs += ["-i", str(p)]
        if name == "music":
            chain += f"[{i}:a]{music_chain(length, music_db, music_offset, fade_in, fade_out)}[{name}];"
        else:
            chain += f"[{i}:a]{FMT},apad,atrim=0:{length}[{name}];"
        heard.append(f"[{name}]")
    # every layer padded and cut to the exact length first: "duration=first" would follow whichever
    # input came first, and the encoded audio once came out ~70 ms short of the picture
    chain += f"{''.join(heard)}amix=inputs={len(heard)}:normalize=0:duration=longest,apad,atrim=0:{length}[a]"
    cmd = (["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", chain, "-map", "0:v", "-map", "[a]",
           "-c:v", "copy"] + audio_encoder() + ["-movflags", "+faststart", "-t", f"{length}", str(out)])
    subprocess.run(cmd, check=True)
    return out


def main():
    ap = argparse.ArgumentParser(description="Voice, music and effects under a picture, at constant levels.")
    ap.add_argument("--picture", required=True, help="the video whose picture is kept (copied, never re-encoded)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--voice", help="the narrator, on the film's clock (one WAV as long as the film)")
    ap.add_argument("--no-voice", action="store_true", help="leave the voice out: a review copy to judge effects and music")
    ap.add_argument("--music", help="the music track (the licensed WAV once bought)")
    ap.add_argument("--music-db", type=float, default=MUSIC_DB, help=f"music level in dB (default {MUSIC_DB})")
    ap.add_argument("--music-offset", type=float, default=0.0, help="seconds into the film the track starts (negative trims its head)")
    ap.add_argument("--fade-in", type=float, default=FADE_IN)
    ap.add_argument("--fade-out", type=float, default=FADE_OUT)
    ap.add_argument("--sfx", help="the sound-effects track, on the film's clock")
    ap.add_argument("--length", type=float, help="seconds (default: the picture's length)")
    a = ap.parse_args()
    out = mix(a.picture, a.out, voice=None if a.no_voice else a.voice, music=a.music, sfx=a.sfx, length=a.length,
              music_db=a.music_db, music_offset=a.music_offset, fade_in=a.fade_in, fade_out=a.fade_out)
    print(f"{out}  ({out.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
