#!/usr/bin/env python3
"""Word and line timings for the film's voiceover, aligned to the script text.

Run with QuickVid's venv, which has faster-whisper and numpy (QuickVid is installed by the
ocha-video skill; `render_social_video.py --check` there says where it is):
    "<ocha_quick_vid>/.venv/bin/python" assets/build/word_timings.py
The script text: one script line per text line (a line may hold several short sentences: "An
earthquake. A hurricane. Floods."), exactly as sent to the voice ("Ocha", not "OCHA"); blank lines skipped.
Reads  assets/voice/voiceover.mp3 and assets/voice/voiceover_tts_plain.txt
Writes assets/voice/voiceover_timings.json

Words pop on screen as they are spoken, so their times must match the voice to a frame.
Whisper alone is not that precise: measured against the audio (19 Sept 2026), its word starts
were off by up to 0.3 s, both ways, in both models. So Whisper only says roughly where each word
is, and the audio says exactly where:
  1. every pause in the voice is matched to the word boundary it falls on; the word after a
     pause starts where the sound starts again (to 5 ms), the word before it ends where the
     sound stops ("pause");
  2. inside a phrase, the gaps between words are dips in the voice's loudness — but so are the
     stop consonants inside words ("humani-t-arian"). So each dip near Whisper's estimate is
     put to Whisper as a listener: a word starts at the first dip where the voice after it is
     heard starting with that word and the voice before it ending with the previous word
     ("heard"). This beat reading the loudness by eye: it placed "teams" after the /t/ inside
     "humanitarian", where the eye had placed it before;
  3. short words ("a", "the", "at") are too brief for the listener to hear at the edge of a
     clip, so they take the clearest dip between their neighbours near the estimate ("dip"),
     or the estimate itself ("estimate"). The estimate is the mean of the two models, which
     lean opposite ways (small early, medium late), less their remaining shared lean as
     measured on the words found in steps 1 and 2.
Each word keeps both Whisper estimates ("whisper") and how its start was found ("how").
"""
import difflib, json, re, subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
AUDIO = ROOT / "assets/voice/voiceover.mp3"
TEXT = ROOT / "assets/voice/voiceover_tts_plain.txt"
OUT = ROOT / "assets/voice/voiceover_timings.json"
import shutil
# found on this Mac (Apple silicon: /opt/homebrew/bin; Intel: /usr/local/bin), never assumed
FFMPEG, FFPROBE = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg", shutil.which("ffprobe") or "/opt/homebrew/bin/ffprobe"

SR = 16000
MODELS = ("small", "medium")  # both cached locally; their errors lean opposite ways, so their mean is the better guess
HOP, WIN = 0.0025, 0.010      # loudness: a 10 ms window every 2.5 ms
SILENT_DB = -50.0             # the voice's noise floor is about -88 dBFS; speech sits between -35 and -5
LOUD_DB = -32.0               # a real word gets this loud; a breath or a click stays quieter
MIN_PAUSE = 0.040             # quieter stretches shorter than this are stop consonants, not pauses
PHRASE_PAUSE = 0.100          # only pauses this long may split phrases; shorter ones are tested like dips
MIN_WORD = 0.060              # no word is shorter than this
DIP_DB = 4.0                  # a loudness dip must be this deep to count as a gap between words
SEARCH = 0.300                # dips this far from Whisper's estimate are put to the listener
TRIES = 5                     # at most this many dips per word, strongest and nearest first
CONTEXT = 2.5                 # the listener hears this much voice on each side of a dip
SHORT = 3                     # words of this many letters or fewer skip the listener
DIP_REACH = 0.080             # without the listener's say-so, a start moves at most this far to a dip


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


# ---------- Whisper: rough word times, aligned to the script ----------
def whisper_times(wav, model_name, script):
    from faster_whisper import WhisperModel
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segs, _ = model.transcribe(str(wav), language="en", beam_size=5, word_timestamps=True)
    heard = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]

    a, b = [norm(w) for _, w in script], [norm(w) for w, _, _ in heard]
    times, said, mismatches = [None] * len(script), [None] * len(script), []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                times[i1 + k] = heard[j1 + k][1:]
                said[i1 + k] = heard[j1 + k][0]
        elif tag == "replace":
            # spread the heard span evenly over the script words it stands for
            s0, s1 = heard[j1][1], heard[j2 - 1][2]
            step = (s1 - s0) / (i2 - i1)
            for k in range(i2 - i1):
                times[i1 + k] = (s0 + k * step, s0 + (k + 1) * step)
                said[i1 + k] = " ".join(w for w, _, _ in heard[j1:j2]) if k == 0 else "…"
            mismatches.append({"model": model_name, "script": " ".join(w for _, w in script[i1:i2]),
                               "heard": " ".join(w for w, _, _ in heard[j1:j2]),
                               "start": round(s0, 2), "end": round(s1, 2)})
        elif tag == "delete":
            mismatches.append({"model": model_name, "script": " ".join(w for _, w in script[i1:i2]),
                               "heard": "(nothing)"})
        elif tag == "insert":
            mismatches.append({"model": model_name, "script": "(nothing)",
                               "heard": " ".join(w for w, _, _ in heard[j1:j2]), "start": round(heard[j1][1], 2)})
    # words the voice skipped get the gap between their neighbours
    for i, t in enumerate(times):
        if t is None:
            prev = next((times[k][1] for k in range(i - 1, -1, -1) if times[k]), 0.0)
            nxt = next((times[k][0] for k in range(i + 1, len(times)) if times[k]), prev)
            times[i] = (prev, nxt)
    return times, said, mismatches, len(heard)


# ---------- the audio: loudness, pauses, dips ----------
def load_audio():
    pcm = subprocess.run([FFMPEG, "-loglevel", "error", "-i", str(AUDIO), "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(pcm, dtype=np.float32)


def loudness(x):
    h, w = round(HOP * SR), round(WIN * SR)
    n = (len(x) - w) // h + 1
    c = np.concatenate([[0.0], np.cumsum(x.astype(np.float64) ** 2)])
    i = np.arange(n) * h
    return 20 * np.log10(np.sqrt((c[i + w] - c[i]) / w) + 1e-9)


def at(i):
    return i * HOP + WIN / 2   # a frame's time is the middle of its window


def voice_runs(db):
    """Stretches of voice as (start, end) seconds. Sounds closer than MIN_PAUSE belong together;
    a stretch that never gets LOUD_DB loud (a breath, a click) is not voice."""
    s = (db >= SILENT_DB).astype(np.int8)
    d = np.diff(np.concatenate([[0], s, [0]]))
    runs = list(zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1)))   # frames [a, b)
    groups = []
    for a, b in runs:
        if groups and at(a) - at(groups[-1][1]) < MIN_PAUSE:
            groups[-1][1] = b
        else:
            groups.append([a, b])
    voice = [(a, b) for a, b in groups if db[a:b].max() >= LOUD_DB]
    return [(at(a) - HOP / 2, at(b) - HOP / 2) for a, b in voice]


def dips(db):
    """Dips in loudness, as (time, depth dB): a local minimum over ±20 ms that sits DIP_DB below
    the loudest point on each side within 60 ms."""
    sm = np.convolve(db, np.ones(5) / 5, mode="same")
    near, side = round(0.020 / HOP), round(0.060 / HOP)
    out = []
    for i in range(side, len(sm) - side):
        if sm[i] > sm[i - near:i + near + 1].min() or (out and at(i) - out[-1][0] < 0.02):
            continue
        depth = min(sm[i - side:i].max(), sm[i + 1:i + side + 1].max()) - sm[i]
        if depth >= DIP_DB:
            out.append((at(i), float(depth)))
    return out


# ---------- matching pauses to word boundaries ----------
def match_pauses(pauses, est_s, est_e, punct):
    """Pair pauses with word boundaries by dynamic programming, in order. Boundary i is the start
    of word i (1..K-1). A pause may pair with no boundary (a stop consonant inside a word), and a
    boundary with no pause (words run together) — each at a cost. Returns {boundary: pause}."""
    K, P = len(est_s), len(pauses)
    INF = float("inf")

    def match(k, i):
        a, b = pauses[k]
        if abs(b - est_s[i]) > 0.7 or b - a < PHRASE_PAUSE:
            return INF
        cost = (abs(b - est_s[i]) + 0.5 * abs(a - est_e[i - 1])) / 0.08
        return cost - (4.0 if punct[i - 1] == 2 else 2.0 if punct[i - 1] == 1 else 0.0)

    def skip_pause(k):
        a, b = pauses[k]
        return 30.0 * max(0.0, (b - a) - MIN_PAUSE)

    def skip_boundary(i):
        return 5.0 if punct[i - 1] == 2 else 1.5 if punct[i - 1] == 1 else 0.0

    # D[k][i]: best cost using the first k pauses and the first i boundaries (boundaries 1..i)
    D = np.full((P + 1, K), INF)
    move = np.zeros((P + 1, K), dtype=np.int8)   # 1 skip pause, 2 skip boundary, 3 match
    D[0][0] = 0.0
    for k in range(P + 1):
        for i in range(K):
            if k == 0 and i == 0:
                continue
            best, how = INF, 0
            if k > 0 and D[k - 1][i] + skip_pause(k - 1) < best:
                best, how = D[k - 1][i] + skip_pause(k - 1), 1
            if i > 0 and D[k][i - 1] + skip_boundary(i) < best:
                best, how = D[k][i - 1] + skip_boundary(i), 2
            if k > 0 and i > 0:
                c = D[k - 1][i - 1] + match(k - 1, i)
                if c < best:
                    best, how = c, 3
            D[k][i], move[k][i] = best, how
    pairs, k, i = {}, P, K - 1
    while k > 0 or i > 0:
        m = move[k][i]
        if m == 3:
            pairs[i] = k - 1
            k, i = k - 1, i - 1
        elif m == 1:
            k -= 1
        else:
            i -= 1
    return pairs


def listener(x):
    """Whisper as an ear: the text it hears in a clip of the voice, letters and digits only."""
    from faster_whisper import WhisperModel
    model, cache = WhisperModel("small", device="cpu", compute_type="int8"), {}

    def heard(a, b):
        key = (round(a, 3), round(b, 3))
        if key not in cache:
            segs, _ = model.transcribe(x[max(0, int(a * SR)):int(b * SR)], language="en", beam_size=1,
                                       without_timestamps=True, condition_on_previous_text=False)
            cache[key] = "".join(norm(s.text) for s in segs)
        return cache[key]
    return heard


def splits_here(heard, t, before, word):
    """Does the voice pass from `before` to `word` at t? The voice after t must be heard starting
    with `word`, and the voice before t ending with `before`. A dip inside a word fails: one
    side starts or ends with half a word. Whisper drops or mishears a short word at the very
    end of a clip ("An" → "and"), so a short `before` is not asked about."""
    if not heard(t - 0.005, t + CONTEXT).startswith(norm(word)[:4]):
        return False
    return len(norm(before)) <= SHORT or heard(max(0.0, t - CONTEXT), t + 0.005).endswith(norm(before)[-4:])


def align(script, est_s, est_e, x, db):
    K = len(script)
    voice = voice_runs(db)
    pauses = [(voice[n][1], voice[n + 1][0]) for n in range(len(voice) - 1)]
    punct = [2 if re.search(r"[.?!]$", w) else 1 if re.search(r"[,;:—–]$", w) else 0 for _, w in script]
    pairs = match_pauses(pauses, est_s, est_e, punct)

    start, end, how = [None] * K, [None] * K, [None] * K
    start[0], how[0], end[K - 1] = voice[0][0], "pause", voice[-1][1]
    for i, k in pairs.items():
        start[i], how[i], end[i - 1] = pauses[k][1], "pause", pauses[k][0]

    # inside each phrase (the words between two pauses), find where each word starts
    used = set(pairs.values())
    candidates = sorted(dips(db) + [(pauses[k][1], 40.0) for k in range(len(pauses)) if k not in used])
    heads = [i for i in range(K) if start[i] is not None] + [K]
    phrases = list(zip(heads, heads[1:]))

    def room(m, nxt, E):   # the earliest and latest start that leave every word MIN_WORD
        p = max(k for k in range(m) if start[k] is not None)
        q = min([k for k in range(m + 1, nxt) if start[k] is not None] + [nxt])
        return start[p] + MIN_WORD * (m - p), (start[q] if q < nxt else E) - MIN_WORD * (q - m)

    heard = listener(x)   # pass 1: words the listener can judge
    for h, nxt in phrases:
        for m in range(h + 1, nxt):
            if len(norm(script[m][1])) <= SHORT:
                continue
            lo, hi = room(m, nxt, end[nxt - 1])
            guess = min(max(est_s[m], lo), hi)
            near = [c for c in candidates if lo <= c[0] <= hi and abs(c[0] - guess) <= SEARCH]
            near.sort(key=lambda c: -c[1] * (1 - abs(c[0] - guess) / (SEARCH * 1.5)))
            t = next((t for t, _ in near[:TRIES] if splits_here(heard, t, script[m - 1][1], script[m][1])), None)
            if t is not None:
                start[m], how[m] = t, "heard"

    # pass 2: the rest take the clearest dip near the estimate, less the models' shared lean
    lean = float(np.median([est_s[n] - start[n] for n in range(K) if start[n] is not None]))
    for h, nxt in phrases:
        for m in range(h + 1, nxt):
            if start[m] is None:
                lo, hi = room(m, nxt, end[nxt - 1])
                guess = min(max(est_s[m] - lean, lo), hi)
                close = [c for c in candidates if lo <= c[0] <= hi and abs(c[0] - guess) <= DIP_REACH]
                start[m], how[m] = ((max(close, key=lambda c: c[1] * (1 - abs(c[0] - guess) / (DIP_REACH * 1.5)))[0], "dip")
                                    if close else (guess, "estimate"))
        for m in range(h + 1, nxt):
            end[m - 1] = start[m]
    print(f"Whisper's mean leans {1000 * lean:+.0f} ms against the words found by pause and listener")
    for n in range(K):   # a failed alignment must stop the build, not ship wrong timings
        if not start[n] < end[n] or (n and start[n] < end[n - 1] - 1e-6):
            raise SystemExit(f"alignment broke at word {n} {script[n][1]!r}: {start[n]:.3f}–{end[n]:.3f}")
    return start, end, how, len(pauses), len(pairs)


def main():
    lines = [l.strip() for l in TEXT.read_text(encoding="utf-8").splitlines() if l.strip()]
    script = [(li, w) for li, l in enumerate(lines) for w in l.split() if norm(w)]

    wav = OUT.with_suffix(".16k.wav")
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(AUDIO), "-ac", "1", "-ar", str(SR), str(wav)], check=True)
    runs = {m: whisper_times(wav, m, script) for m in MODELS}
    wav.unlink()

    est_s = [float(np.mean([runs[m][0][n][0] for m in MODELS])) for n in range(len(script))]
    est_e = [float(np.mean([runs[m][0][n][1] for m in MODELS])) for n in range(len(script))]
    dur = float(subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(AUDIO)], capture_output=True, text=True).stdout)
    x = load_audio()
    start, end, how, n_pauses, n_paired = align(script, est_s, est_e, x, loudness(x))

    said = runs[MODELS[-1]][1]
    words = [{"line": li + 1, "word": w, "said": said[n], "start": round(start[n], 3), "end": round(end[n], 3),
              "how": how[n], "whisper": {m: [round(runs[m][0][n][0], 3), round(runs[m][0][n][1], 3)] for m in MODELS}}
             for n, (li, w) in enumerate(script)]
    line_rows = []
    for li, text in enumerate(lines):
        ws = [w for w in words if w["line"] == li + 1]
        line_rows.append({"line": li + 1, "text": text, "start": ws[0]["start"], "end": ws[-1]["end"]})
    mismatches = [x for m in MODELS for x in runs[m][2]]
    OUT.write_text(json.dumps({"audio": AUDIO.name, "duration": round(dur, 3), "lines": line_rows,
                               "words": words, "mismatches": mismatches},
                              ensure_ascii=False, indent=1), encoding="utf-8")

    for r in line_rows:
        print(f'{r["line"]:>2}  {r["start"]:6.2f}–{r["end"]:6.2f}  {r["text"]}')
    counts = {h: sum(w["how"] == h for w in words) for h in ("pause", "heard", "dip", "estimate")}
    moved = [abs(w["start"] - np.mean([w["whisper"][m][0] for m in MODELS])) for w in words]
    print(f"\naudio {dur:.2f}s · {len(words)} script words · heard {', '.join(f'{m} {runs[m][3]}' for m in MODELS)}")
    print(f"{n_pauses} pauses, {n_paired} of them on word boundaries · word starts from: {counts}")
    print(f"moved from Whisper's mean by: median {1000 * np.median(moved):.0f} ms, max {1000 * max(moved):.0f} ms")
    print("mismatches:", json.dumps(mismatches, ensure_ascii=False, indent=1) if mismatches else "none")


if __name__ == "__main__":
    main()
