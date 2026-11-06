#!/usr/bin/env python3
"""Find the beats and the tempo (BPM) of a music track, so cuts and moves can land on the beat.

    python3 beats.py track.wav                          # prints the tempo and the first beats
    python3 beats.py track.wav --out beats.json         # every beat, in seconds, for the film to read
    python3 beats.py track.wav --offset 3.0 --out …     # the music starts 3 s into the film: times on
                                                        # the film's clock instead of the track's
    python3 beats.py track.wav --click check.wav        # the track with a click on every beat (a higher
                                                        # click on each bar start): listen before trusting
    python3 beats.py track.wav --meter 3                # a waltz: 3 beats to the bar (default 4)

Any audio or video file ffmpeg can read works. Use it on the music alone, not on a mix: the voice and
the effects hide the beat. The JSON holds:
    bpm         the tempo, from the spacing of the beats found
    period      seconds between beats (60 / bpm)
    pulse       0–1, how clear the beat is. Under ~0.3 the music has no steady pulse (ambient, rubato):
                don't cut to these beats without listening
    beats       every beat, in seconds (plus --offset)
    bars        where each bar starts (its "ONE", the strongest beat), in seconds: the best moments for a cut
    meter       beats per bar (4 unless --meter says otherwise)
    bar_clarity 0–1, how sure the bar starts are. Under ~0.2 it is a guess: check by ear (the higher click)

How it works (the standard method, built here on numpy so nothing new has to be installed):
  1. how much new sound starts in each 12 ms slice (spectral flux on a mel spectrum, in dB)
  2. the tempo: the spacing at which that pattern repeats best (autocorrelation), with a gentle
     preference for 120 BPM so a track is not read at half or double its speed
  3. the beats: the chain of onsets that best fits that tempo (dynamic programming, Ellis 2007 —
     the same method as librosa's beat_track)
  4. the bar starts: of the 4 (or --meter) ways to group the beats, the one whose first beats carry the
     most kick drum and the most change in sound (chords and sections change on the ONE)
A tool can still land on half or double the tempo a person would tap, or put the ONE on the wrong beat
(the bars assume the meter stays the same through the track). The click track settles both.

Needs numpy and ffmpeg. Run it with any Python that has numpy; without one, it runs itself again with
OCHA QuickVid's Python (which has numpy, and ffmpeg through static_ffmpeg). QuickVid is found the
same way as in ocha-utilities' video_reference.py.

Maintained by: OCHA Brand and Design Unit (BDU) — ochavisual@un.org
"""

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
import wave

HOME = os.path.expanduser("~")
SR = 22050          # analysis sample rate: the beat lives well under 11 kHz
HOP = 256           # 11.6 ms per slice: well under a 30 fps frame (33 ms)
N_FFT = 2048
N_MELS = 64
PRIOR_BPM = 120.0   # centre of the tempo preference (one octave either side is still likely)
TIGHTNESS = 100.0   # how strictly beats keep the tempo in step 3 (librosa's default)


def quickvid_python():
    """QuickVid's Python, wherever it is installed. None if QuickVid is not on this computer.
    Mirrors ocha-utilities/scripts/video_reference.py: change both together."""
    places = [os.environ["QUICKVID_HOME"]] if os.environ.get("QUICKVID_HOME") else []
    supports = [os.path.join(HOME, "Library", "Application Support", "OCHA QuickVid")]
    if os.environ.get("LOCALAPPDATA"):
        supports.append(os.path.join(os.environ["LOCALAPPDATA"], "OCHA QuickVid"))
    for s in supports:
        moved = os.path.join(s, "home")   # QuickVid writes this file if it was relocated
        if os.path.isfile(moved):
            with open(moved, encoding="utf-8") as fh:
                places.append(fh.read().strip())
        places.append(os.path.join(s, "app"))
    for p in places:
        for py in (os.path.join(p, ".venv", "bin", "python3"), os.path.join(p, ".venv", "Scripts", "python.exe")):
            if os.path.isfile(py):
                return py
    return None


try:
    import numpy as np
except ImportError:
    py = quickvid_python()
    if not py or os.path.realpath(py) == os.path.realpath(sys.executable):
        sys.exit("beats.py needs numpy. Install OCHA QuickVid (it brings numpy), or run it with a Python that has numpy.")
    sys.exit(subprocess.call([py, os.path.abspath(__file__)] + sys.argv[1:]))


def find_ffmpeg():
    """Same search order as find_ffmpeg() in ocha-utilities/scripts/video_reference.py: change both together."""
    found = (os.environ.get("FFMPEG") or shutil.which("ffmpeg")
             or next((p for p in ("/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg")   # not on PATH in every session
                      if os.path.isfile(p)), None))
    if found:
        return found
    try:   # QuickVid's portable ffmpeg
        from static_ffmpeg import run
        return run.get_or_fetch_platform_executables_else_raise()[0]
    except Exception:
        sys.exit("ffmpeg not found: install it, set FFMPEG=/path/to/ffmpeg, or install OCHA QuickVid.")


def decode(ffmpeg, path, rate, channels):
    raw = subprocess.run([ffmpeg, "-v", "error", "-i", str(path), "-vn", "-ac", str(channels), "-ar", str(rate),
                          "-f", "f32le", "-"], capture_output=True)
    if raw.returncode != 0:
        sys.exit(f"ffmpeg could not read {path}: {raw.stderr.decode(errors='replace').strip()}")
    x = np.frombuffer(raw.stdout, dtype=np.float32)
    return x.reshape(-1, channels) if channels > 1 else x


def mel_filters():
    """A triangular mel filterbank (Slaney-style), so numpy alone is enough."""
    mel = lambda f: 2595.0 * np.log10(1.0 + f / 700.0)
    hz = lambda m: 700.0 * (10 ** (m / 2595.0) - 1.0)
    edges = hz(np.linspace(mel(30.0), mel(SR / 2), N_MELS + 2))
    bins = np.fft.rfftfreq(N_FFT, 1.0 / SR)
    fb = np.zeros((N_MELS, bins.size))
    for i in range(N_MELS):
        lo, mid, hi = edges[i], edges[i + 1], edges[i + 2]
        fb[i] = np.clip(np.minimum((bins - lo) / (mid - lo), (hi - bins) / (hi - mid)), 0, None)
        fb[i] *= 2.0 / (hi - lo)
    return fb


def onset_envelope(x):
    """Step 1: how much new sound starts in each slice. Also returns the mel spectrum (dB) for step 4."""
    if x.size < N_FFT * 4:
        sys.exit("The track is too short to find a beat (under half a second).")
    pad = np.pad(x, N_FFT // 2, mode="reflect")
    n = 1 + (pad.size - N_FFT) // HOP
    frames = np.lib.stride_tricks.as_strided(pad, (n, N_FFT), (pad.strides[0] * HOP, pad.strides[0]))
    # In blocks of slices: the whole spectrum of a 3-minute track at once would take ~0.5 GB.
    win, fb = np.hanning(N_FFT), mel_filters().T
    mel = np.concatenate([(np.abs(np.fft.rfft(frames[i:i + 2048] * win, axis=1)) ** 2) @ fb
                          for i in range(0, n, 2048)])
    db = 10 * np.log10(np.maximum(mel, 1e-10))
    db = np.maximum(db, db.max() - 80.0)
    flux = np.maximum(0.0, np.diff(db, axis=0)).mean(axis=1)
    env = np.concatenate([[0.0], flux])
    # Take away the slow swell (a crescendo is not a beat): subtract a 1 s moving average.
    w = int(round(SR / HOP))
    env = np.maximum(0.0, env - np.convolve(env, np.ones(w) / w, mode="same"))
    return env / (env.std() or 1.0), db


def tempo(env):
    """Step 2: the beat period in slices (a float), and how clear the pulse is (0–1)."""
    fps = SR / HOP
    e = env - env.mean()
    ac = np.correlate(e, e, mode="full")[e.size - 1:]
    ac = ac / (ac[0] or 1.0)
    lags = np.arange(ac.size)
    lo, hi = int(fps * 60 / 240), min(int(fps * 60 / 40), ac.size - 1)   # 40–240 BPM
    bpm = 60.0 * fps / lags[lo:hi]
    prior = np.exp(-0.5 * (np.log2(bpm / PRIOR_BPM)) ** 2)
    # Score each period by its own peak and its multiples: a true beat repeats at 2× and 4× too.
    comb = lambda p: sum(np.interp(k * p, lags, ac) / k for k in (1, 2, 4))
    score = np.array([comb(p) for p in lags[lo:hi]]) * prior
    best = lags[lo + int(np.argmax(score))]
    fine = np.arange(best - 1.0, best + 1.0, 0.01)   # refine to a hundredth of a slice
    period = fine[int(np.argmax([comb(p) for p in fine]))]
    pulse = float(np.clip(np.interp(period, lags, ac), 0.0, 1.0))
    return period, pulse


def track(env, period):
    """Step 3: the beats, as slice indices (Ellis 2007)."""
    p = int(round(period))
    win = np.exp(-0.5 * (np.arange(-p, p + 1) * 32.0 / p) ** 2)
    local = np.convolve(env, win, mode="same")
    score = local.copy()
    back = np.full(env.size, -1)
    offsets = np.arange(-2 * p, -int(round(p / 2)) + 1)
    cost = -TIGHTNESS * np.log(-offsets / period) ** 2
    for i in range(env.size):
        lo = i + offsets
        ok = lo >= 0
        if not ok.any():
            continue
        cand = score[lo[ok]] + cost[ok]
        k = int(np.argmax(cand))
        if cand[k] > 0:
            score[i] += cand[k]
            back[i] = lo[ok][k]
    # Last beat: the latest local peak of the score that is reasonably strong.
    peaks = [i for i in range(1, env.size - 1) if score[i - 1] <= score[i] > score[i + 1]]
    floor = 0.5 * np.median(score[peaks]) if peaks else 0.0
    strong = [i for i in peaks if score[i] >= floor]
    i = strong[-1] if strong else int(np.argmax(score))
    beats = []
    while i >= 0:
        beats.append(i)
        i = back[i]
    beats = np.array(beats[::-1])
    # Drop the weak beats the chain adds in a silent intro or tail.
    keep = local[beats] >= 0.2 * np.sqrt(np.mean(local[beats] ** 2))
    if not keep.any():
        return beats[:0]
    return beats[np.argmax(keep):beats.size - np.argmax(keep[::-1])]


def bar_starts(db, beats, meter):
    """Step 4: which beat of each group of `meter` is the ONE. Returns (index of the first ONE, clarity 0–1).
    Two signs of a bar start, each scaled to its own median so neither drowns the other:
      kick    a burst of low sound (under ~150 Hz) on the beat
      change  how different the sound of the next two beats is from the last two (new chord, new section)"""
    if beats.size < 2 * meter:
        return 0, 0.0
    low = np.maximum(0.0, np.diff(db[:, :6], axis=0)).mean(axis=1)   # the lowest mel bands: the kick
    kick = np.array([low[max(0, b - 3):b + 3].max() for b in beats])
    edges = np.concatenate([beats, [db.shape[0]]])
    per_beat = np.array([db[edges[i]:max(edges[i + 1], edges[i] + 1)].mean(axis=0) for i in range(beats.size)])
    change = np.zeros(beats.size)
    for i in range(2, beats.size - 1):
        change[i] = np.linalg.norm(per_beat[i:i + 2].mean(axis=0) - per_beat[i - 2:i].mean(axis=0))
    sign = kick / (np.median(kick) or 1.0) + change / (np.median(change[2:-1]) or 1.0)
    score = np.array([sign[k::meter].mean() for k in range(meter)])
    order = np.sort(score)[::-1]
    clarity = float(np.clip((order[0] - order[1]) / (order[0] - order[-1] or 1.0), 0.0, 1.0))
    return int(np.argmax(score)), clarity


def write_click(ffmpeg, src, beat_times, bar_times, out):
    """The track with a short click on every beat and a higher, louder one on every bar start,
    as a 16-bit stereo WAV, to check by ear."""
    rate = 44100
    x = decode(ffmpeg, src, rate, 2).astype(np.float64)
    t = np.arange(int(0.03 * rate)) / rate
    tick = lambda hz, gain: gain * np.sin(2 * np.pi * hz * t) * np.exp(-t / 0.006)
    beat, one = tick(1500, 0.5), tick(2500, 0.8)
    bar_set = {int(round(b * rate)) for b in bar_times}
    for b in beat_times:
        i = int(round(b * rate))
        if 0 <= i < len(x):
            seg = (one if i in bar_set else beat)[: len(x) - i]
            x[i:i + seg.size] += seg[:, None]
    x = np.clip(x * 0.8, -1, 1)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes((x * 32767).astype("<i2").tobytes())


def main():
    ap = argparse.ArgumentParser(description="Find the beats and tempo of a music track.")
    ap.add_argument("track", type=pathlib.Path, help="the music (any audio or video file ffmpeg reads)")
    ap.add_argument("--out", type=pathlib.Path, help="write the beats here as JSON")
    ap.add_argument("--offset", type=float, default=0.0,
                    help="seconds to add to every time: where the music starts on the film's clock")
    ap.add_argument("--click", type=pathlib.Path,
                    help="write the track with a click on every beat, a higher one on each bar start (WAV)")
    ap.add_argument("--meter", type=int, default=4, help="beats per bar: 4 (default), 3 for a waltz, 2, 6…")
    a = ap.parse_args()
    if not a.track.is_file():
        sys.exit(f"No file at {a.track}")
    if a.meter < 2:
        sys.exit("--meter must be 2 or more")

    ffmpeg = find_ffmpeg()
    env, db = onset_envelope(decode(ffmpeg, a.track, SR, 1).astype(np.float64))
    period, pulse = tempo(env)
    idx = track(env, period)
    times = idx * HOP / SR
    if times.size < 2:
        sys.exit("No steady beat found in this track.")
    # The tempo from a straight line through all the beats: exact for library music, which keeps
    # one tempo. (The median gap between beats rounds to whole slices: 129.2 instead of 131.)
    step = float(np.polyfit(np.arange(times.size), times, 1)[0])
    bpm = 60.0 / step
    first_one, clarity = bar_starts(db, idx, a.meter)
    bars = times[first_one::a.meter]

    print(f"{a.track.name}: {bpm:.1f} BPM (a beat every {step:.3f} s), {times.size} beats "
          f"from {times[0]:.2f} s to {times[-1]:.2f} s, pulse {pulse:.2f}"
          + ("  — weak: listen before cutting to these beats" if pulse < 0.3 else ""))
    print(f"  {bars.size} bars of {a.meter} (a bar every {step * a.meter:.3f} s), first bar start at "
          f"{bars[0]:.2f} s on the track, bar clarity {clarity:.2f}"
          + ("  — a guess: listen for the higher click" if clarity < 0.2 else ""))
    # On the film's clock. A negative offset cuts the track's start: beats before 0 are not in the film.
    film = times + a.offset
    film = film[film >= 0]
    film_bars = bars + a.offset
    film_bars = film_bars[film_bars >= 0]
    print("  first beats" + (f" (film clock, {a.offset:+g} s)" if a.offset else "") + ": "
          + ", ".join(f"{t:.3f}" for t in film[:8]) + " …")
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps({
            "track": a.track.name, "bpm": round(bpm, 2), "period": round(step, 4), "pulse": round(pulse, 2),
            "offset": a.offset, "beats": [round(float(t), 3) for t in film],
            "meter": a.meter, "bar_clarity": round(clarity, 2), "bars": [round(float(t), 3) for t in film_bars],
        }, indent=1) + "\n", encoding="utf-8")
        print(f"  wrote {a.out}")
    if a.click:
        write_click(ffmpeg, a.track, times, bars, a.click)
        print(f"  wrote {a.click} — listen: every click should sit on the beat, the higher one on each ONE")


if __name__ == "__main__":
    main()
