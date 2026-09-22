#!/usr/bin/env python3
"""Does the voice stand out over the music and effects? Measured word by word.

    python3 voice_clarity.py --voice voice.wav --music track.wav --sfx sfx.wav --words timeline.json
    python3 voice_clarity.py --voice voice.wav --music track.wav            # no word list: finds the speech itself
    python3 voice_clarity.py ... --floor 12 --cues audio/sfx_cues.json      # stricter; name the effects under each word

Javier, SG Awards film, 21 September 2026: "make sure voice stands out over sfx and music clearly".
This is the test for that. For every word (or, without a word list, every stretch of speech) it
measures the loudness of the voice and of everything under it, and reports the MARGIN: how many LU
the voice sits above the rest. Loudness is K-weighted as in EBU R128 / ITU-R BS.1770 (how loud it
sounds, not how big the waveform is), so a bright hiss and a deep rumble are not scored the same.

Aim for every word at least 10 LU above the music and effects (--floor). On the SG film, 44 of 170
words missed that at first; lowering the whole effects layer 5 dB (and the siren 3 dB more) brought
it to 24, the worst under a bomb and a hit on "Armed conflict" — a choice the director made by ear.

It reads the LAYERS, not an encoded film, so it measures the mix itself, not the codec. The music is
processed exactly as mix.py does (same function), so pass the same --music-db / --music-offset.
Word lists: an animation's timeline.json ({"words": [...]}), or any JSON list of {start, end, word|text}.
"""

import argparse
import json
import pathlib
import subprocess
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mix import FADE_IN, FADE_OUT, MUSIC_DB, duration, music_chain  # noqa: E402  (the same music as the mix)

RATE = 48000
# BS.1770 K-weighting at 48 kHz: a high shelf (+4 dB above ~1.5 kHz, the head) and a high-pass (~38 Hz)
K_WEIGHT = ("biquad=b0=1.53512485958697:b1=-2.69169618940638:b2=1.19839281085285:a0=1:a1=-1.69065929318241:a2=0.73248077421585,"
            "biquad=b0=1:b1=-2:b2=1:a0=1:a1=-1.99004745483398:a2=0.99007225036621")


def layer(path, length, chain=None):
    """A layer, K-weighted, in double precision, as long as the film."""
    chain = chain or f"aresample={RATE},aformat=sample_fmts=fltp:channel_layouts=stereo,apad,atrim=0:{length}"
    af = f"{chain},aformat=sample_fmts=dbl:channel_layouts=stereo,{K_WEIGHT}"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-af", af, "-f", "f64le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float64).reshape(-1, 2)


def lufs(k, a, b):
    """Loudness of a K-weighted stretch [a, b) s (BS.1770: the channels' mean squares summed)."""
    seg = k[int(a * RATE): int(b * RATE)]
    return -0.691 + 10 * np.log10(max(1e-12, float((seg ** 2).mean(axis=0).sum()))) if len(seg) else -120.0


def integrated(k):
    """BS.1770 integrated loudness (gated): here only to prove the K-weighting matches ffmpeg's own meter."""
    W, H = int(0.4 * RATE), int(0.1 * RATE)
    p = (k ** 2).sum(axis=1); c = np.concatenate([[0], np.cumsum(p)])
    s = np.arange(0, len(p) - W, H); z = (c[s + W] - c[s]) / W
    L = -0.691 + 10 * np.log10(np.maximum(z, 1e-12))
    z = z[L > -70]; rel = -0.691 + 10 * np.log10(z.mean()) - 10
    return -0.691 + 10 * np.log10(z[-0.691 + 10 * np.log10(z) > rel].mean())


def speech_stretches(voice, min_len=0.15, gap=0.15):
    """No word list: the stretches where the voice is speaking — 50 ms blocks within 25 LU of its
    loudest, joined across gaps under 150 ms. Reported by time instead of by word."""
    blk = int(0.05 * RATE); n = len(voice) // blk
    L = np.array([lufs(voice, i * blk / RATE, (i + 1) * blk / RATE) for i in range(n)])
    on = L > (np.percentile(L, 99) - 25)
    out, start, last = [], None, None
    for i, v in enumerate(on):
        t = i * 0.05
        if v and start is None: start = t
        if v: last = t + 0.05
        if start is not None and not v and t - last >= gap:
            if last - start >= min_len: out.append({"start": start, "end": last, "word": "(speech)"})
            start = None
    if start is not None and last - start >= min_len:
        out.append({"start": start, "end": last, "word": "(speech)"})
    return out


def main():
    ap = argparse.ArgumentParser(description="How far the voice sits above the music and effects, word by word.")
    ap.add_argument("--voice", required=True, help="the narrator, on the film's clock")
    ap.add_argument("--music"); ap.add_argument("--music-db", type=float, default=MUSIC_DB)
    ap.add_argument("--music-offset", type=float, default=0.0)
    ap.add_argument("--fade-in", type=float, default=FADE_IN); ap.add_argument("--fade-out", type=float, default=FADE_OUT)
    ap.add_argument("--sfx", help="the sound-effects track, on the film's clock")
    ap.add_argument("--words", help="timeline.json, or a JSON list of {start, end, word|text}")
    ap.add_argument("--cues", help="optional: the effects' cue sheet (JSON list of {t, until?, kind}) to name what sounds under a word")
    ap.add_argument("--length", type=float, help="seconds (default: the voice track's length)")
    ap.add_argument("--floor", type=float, default=10.0, help="list the words the rest comes within this many LU of")
    a = ap.parse_args()

    if not (a.music or a.sfx):
        sys.exit("give --music and/or --sfx: there is nothing to measure the voice against")
    length = a.length or duration(a.voice)
    voice = layer(a.voice, length)
    rest = np.zeros_like(voice); music = fx = None
    if a.music:   # processed exactly as the mix processes it (mix.music_chain), then measured
        music = layer(a.music, length, music_chain(length, a.music_db, a.music_offset, a.fade_in, a.fade_out))
    if a.sfx:
        fx = layer(a.sfx, length)
    n = min(len(x) for x in (voice, music, fx) if x is not None)
    voice = voice[:n]; rest = rest[:n]
    if music is not None: music = music[:n]; rest = rest + music      # K-weighting is linear: the sum of the
    if fx is not None: fx = fx[:n]; rest = rest + fx                  # weighted layers is the weighted mix

    # self-check: the K-weighting here must read the voice as ffmpeg's EBU R128 meter does
    err = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", str(a.voice), "-af",
                          f"aresample={RATE},aformat=channel_layouts=stereo,atrim=0:{length},ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    ref, mine = float(err.rsplit("I:", 1)[1].split("LUFS")[0]), integrated(voice)
    print(f"voice: {mine:.1f} LUFS integrated (ffmpeg's meter: {ref:.1f})" + ("" if abs(mine - ref) < 0.3 else "  ← MISMATCH: do not trust this run"))

    if a.words:
        d = json.loads(pathlib.Path(a.words).read_text(encoding="utf-8"))
        words = [{"start": w["start"], "end": w["end"], "word": w.get("word") or w.get("text", "")}
                 for w in (d["words"] if isinstance(d, dict) else d)]
    else:
        words = speech_stretches(voice)
        print(f"no word list: {len(words)} stretches of speech found in the voice")
    cues = json.loads(pathlib.Path(a.cues).read_text(encoding="utf-8")) if a.cues else []

    rows = []
    for w in words:
        s, e = w["start"], max(w["end"], w["start"] + 0.12)   # very short words: at least 120 ms, or one click decides it
        Lv = lufs(voice, s, e)
        m_all = Lv - lufs(rest, s, e)
        m_mus = Lv - lufs(music, s, e) if music is not None else float("inf")
        m_fx = Lv - lufs(fx, s, e) if fx is not None else float("inf")
        near = sorted({c["kind"] for c in cues if c["t"] < e and c.get("until", c["t"] + 0.8) > s})
        rows.append((w, m_all, m_mus, m_fx, near))
    q = lambda v: (f"median {np.median(v):4.1f} · worst 5 % {np.percentile(v, 5):4.1f} · worst {np.min(v):4.1f} LU"
                   if len(v) and np.isfinite(v).all() else "—")
    unit = "words" if a.words else "stretches"
    print(f"{len(rows)} {unit}. Voice above music + effects: {q(np.array([r[1] for r in rows]))}")
    if music is not None: print(f"{' ' * (len(str(len(rows))) + len(unit) + 2)} above the music alone:   {q(np.array([r[2] for r in rows]))}")
    if fx is not None: print(f"{' ' * (len(str(len(rows))) + len(unit) + 2)} above the effects alone: {q(np.array([r[3] for r in rows]))}")
    low = [r for r in rows if r[1] < a.floor]
    print(f"{len(low)} of {len(rows)} {unit} have music + effects within {a.floor:g} LU of the voice:")
    fmt = lambda v: "  —  " if not np.isfinite(v) else f"{v:5.1f}"
    for w, m_all, m_mus, m_fx, near in low:
        print(f"  {w['start']:6.2f} s  {w['word'][:14]:<14} {m_all:5.1f} LU  (music {fmt(m_mus)} · effects {fmt(m_fx)})  {', '.join(near)}")


if __name__ == "__main__":
    main()
