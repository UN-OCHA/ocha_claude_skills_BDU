#!/usr/bin/env python3
"""Find the beats and the tempo (BPM) of a music track, so cuts and moves can land on the beat.

    python3 beats.py track.wav                          # prints the tempo and the first beats
    python3 beats.py track.wav --out beats.json         # every beat, in seconds, for the film to read
    python3 beats.py track.wav --offset 3.0 --out …     # the music starts 3 s into the film: times on
                                                        # the film's clock instead of the track's
    python3 beats.py track.wav --click check.wav        # the track with a click on every beat: listen
                                                        # to it before trusting the beats

Any audio or video file ffmpeg can read works. Use it on the music alone, not on a mix: the voice and
the effects hide the beat. The JSON holds:
    bpm         the tempo, from the spacing of the beats found
    period      seconds between beats (60 / bpm)
    pulse       0–1, how clear the beat is. Under ~0.3 the music has no steady pulse (ambient, rubato):
                don't cut to these beats without listening
    beats       every beat, in seconds (plus --offset)

How it works (the standard method, built here on numpy so nothing new has to be installed):
  1. how much new sound starts in each 12 ms slice (spectral flux on a mel spectrum, in dB)
  2. the tempo: the spacing at which that pattern repeats best (autocorrelation), with a gentle
     preference for 120 BPM so a track is not read at half or double its speed
  3. the beats: the chain of onsets that best fits that tempo (dynamic programming, Ellis 2007 —
     the same method as librosa's beat_track)
A tool can still land on half or double the tempo a person would tap. The click track settles it.

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
    """Step 1: how much new sound starts in each slice."""
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
    return env / (env.std() or 1.0)


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


def write_click(ffmpeg, src, beat_times, out):
    """The track with a short click on every beat, as a 16-bit stereo WAV, to check by ear."""
    rate = 44100
    x = decode(ffmpeg, src, rate, 2).astype(np.float64)
    n = int(0.03 * rate)
    t = np.arange(n) / rate
    click = 0.5 * np.sin(2 * np.pi * 1500 * t) * np.exp(-t / 0.006)
    for b in beat_times:
        i = int(round(b * rate))
        if 0 <= i < len(x):
            seg = click[: len(x) - i]
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
    ap.add_argument("--click", type=pathlib.Path, help="write the track with a click on every beat (WAV)")
    a = ap.parse_args()
    if not a.track.is_file():
        sys.exit(f"No file at {a.track}")

    ffmpeg = find_ffmpeg()
    env = onset_envelope(decode(ffmpeg, a.track, SR, 1).astype(np.float64))
    period, pulse = tempo(env)
    idx = track(env, period)
    times = idx * HOP / SR
    if times.size < 2:
        sys.exit("No steady beat found in this track.")
    # The tempo from a straight line through all the beats: exact for library music, which keeps
    # one tempo. (The median gap between beats rounds to whole slices: 129.2 instead of 131.)
    step = float(np.polyfit(np.arange(times.size), times, 1)[0])
    bpm = 60.0 / step

    print(f"{a.track.name}: {bpm:.1f} BPM (a beat every {step:.3f} s), {times.size} beats "
          f"from {times[0]:.2f} s to {times[-1]:.2f} s, pulse {pulse:.2f}"
          + ("  — weak: listen before cutting to these beats" if pulse < 0.3 else ""))
    # On the film's clock. A negative offset cuts the track's start: beats before 0 are not in the film.
    film = times + a.offset
    film = film[film >= 0]
    print("  first beats" + (f" (film clock, {a.offset:+g} s)" if a.offset else "") + ": "
          + ", ".join(f"{t:.3f}" for t in film[:8]) + " …")
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps({
            "track": a.track.name, "bpm": round(bpm, 2), "period": round(step, 4), "pulse": round(pulse, 2),
            "offset": a.offset, "beats": [round(float(t), 3) for t in film],
        }, indent=1) + "\n", encoding="utf-8")
        print(f"  wrote {a.out}")
    if a.click:
        write_click(ffmpeg, a.track, times, a.click)
        print(f"  wrote {a.click} — listen: every click should sit on the beat")


if __name__ == "__main__":
    main()
