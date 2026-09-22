#!/usr/bin/env python3
"""The voice, placed on the film clock: one WAV as long as the film.

    python3 assets/build/voice_track.py
Reads  assets/voice/voiceover.mp3, assets/voice/voiceover_timings.json, assets/build/timeline.json
Writes assets/build/audio/voice_track.wav (48 kHz stereo, the length of the film)

timeline.py places the voice in blocks (the lead-in, and a block after each beat: in the SG film,
the music-only beat after the tool and the held beat after "saves lives"). Each block is cut from
the recording in the middle of the pause that separates it from the next, so no breath or word is
clipped, and delayed to its place in the film. The mix (mix.py), later, lays music and effects under it.
"""
import json, shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VOICE = ROOT / "assets/voice/voiceover.mp3"
OUT = ROOT / "assets/build/audio/voice_track.wav"
FFMPEG = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"   # found on this Mac, never assumed (Intel Macs: /usr/local/bin)

T = json.loads((ROOT / "assets/build/timeline.json").read_text(encoding="utf-8"))
V = json.loads((ROOT / "assets/voice/voiceover_timings.json").read_text(encoding="utf-8"))
raw = {l["line"]: l for l in V["lines"]}
blocks = T["voice_blocks"]

# cut points in the recording: the file's ends, and the middle of each pause between blocks
cuts = [0.0]
for a, b in zip(blocks, blocks[1:]):
    cuts.append((raw[a["lines"][1]]["end"] + raw[b["lines"][0]]["start"]) / 2)
cuts.append(V["duration"])

chains, labels = [], []
for i, blk in enumerate(blocks):
    s, e, fade = cuts[i], cuts[i + 1], 0.01
    delay = round((s + blk["offset"]) * 1000)   # the block's first sample plays at its film time
    chains.append(f"[0:a]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS,"
                  f"afade=t=in:d={fade},afade=t=out:st={e - s - fade:.3f}:d={fade},adelay=delays={delay}:all=1[b{i}]")
    labels.append(f"[b{i}]")
# endless silence after the last word, cut by -t to the film's exact length (apad's whole_dur
# came out short here: the track ended with the last word, 6 s before the film)
graph = ";".join(chains) + f";{''.join(labels)}amix=inputs={len(blocks)}:normalize=0:dropout_transition=0,apad[v]"

OUT.parent.mkdir(parents=True, exist_ok=True)
subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(VOICE), "-filter_complex", graph, "-map", "[v]",
                "-t", f"{T['duration']:.3f}", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(OUT)], check=True)
dur = float(subprocess.run(["/opt/homebrew/bin/ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                            str(OUT)], capture_output=True, text=True).stdout)
for i, blk in enumerate(blocks):
    print(f"lines {blk['lines'][0]}–{blk['lines'][1]}: voice {cuts[i]:6.2f}–{cuts[i + 1]:6.2f}s → film {cuts[i] + blk['offset']:6.2f}s")
print(f"{OUT.relative_to(ROOT)}: {dur:.2f}s (film {T['duration']:.2f}s)")
