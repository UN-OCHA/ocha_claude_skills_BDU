#!/usr/bin/env python3
"""Turn the film's sound-effect score into sound: one film-long stem, 48 kHz stereo.

The score is film/score.js — WHEN, and which KIND. This file decides which recording each kind
uses and how loud, then places every cue on the film clock:

    python3 sfx_mix.py            # writes audio/sfx_track.wav + audio/sfx_cues.json, prints the cue sheet
    python3 sfx_mix.py --list     # only prints the cue sheet
    python3 sfx_mix.py --strikes  # checks every appearance sound is ONE strike (one icon, one sound)
    python3 sfx_mix.py --strikes "Paper Flap 02|Tactile Feelings"   # …or candidates, before one goes in

The recordings come from the BDU sound library in Dropbox (Design/Resources/SFX: BoomBox, by pack
and title through BoomBox/boombox_index.csv, and the older collections by path), READ IN PLACE:
the raw files are never copied into the job, only the mixed track is written. (BoomBox is licensed
per seat: for BDU members with a seat.) House rules: ocha-video → references/sound-voice-music.md.

Two sorts of cue (see score.js):
  one-off   placed so the recording STARTS (its first sample above 10 % of its peak) exactly on the
            cue's time — the frame its thing appears. Only sweeps and whooshes that build into a
            moment (ALIGN_PEAK) put their peak there instead.
  bed       an ambience from t to `until`: taken from SRC_OFFSET into its recording (looped if
            short), faded in and out.

How loud — every level is set AGAINST THE VOICE, so the numbers mean something:
  one-offs  LEVEL = how many dB their PEAK sits under the voice's typical peak
  beds      LEVEL = how many dB their RMS sits under the voice's typical speech RMS
Javier wants these subtle ("don't overdo it"), so they start well under. Nothing is ducked: voice,
effects and music are three layers at constant levels (mix.py), the effects above the music.
"""

import argparse
import csv
import functools
import json
import math
import os
import pathlib
import subprocess
import sys

import numpy as np

BUILD = pathlib.Path(__file__).resolve().parent
OUT = BUILD / "audio" / "sfx_track.wav"
CUES_OUT = BUILD / "audio" / "sfx_cues.json"   # what plays when, for voice_clarity.py --cues
VOICE = BUILD / "audio" / "voice_track.wav"
RATE = 48000
# Before the voice exists, levels are set against a typical OCHA voiceover: the SG film's (its typical
# peak and speech RMS, measured). Rebuild once the voice track is there.
NOMINAL_VOICE = (-4.4, -18.7)


@functools.lru_cache(maxsize=None)
def lib():
    """The BDU sound library (Dropbox: Design/Resources/SFX), wherever this person's Dropbox keeps it.
    OCHA_SFX=/path/to/SFX overrides."""
    if os.environ.get("OCHA_SFX"):
        return pathlib.Path(os.environ["OCHA_SFX"]).expanduser()
    hits = sorted(pathlib.Path.home().glob("OCHA DMU Dropbox/*/Design/Resources/SFX"))
    if not hits:
        sys.exit("The BDU sound library was not found (Dropbox: Design/Resources/SFX). Set OCHA_SFX=/path/to/SFX.")
    return hits[0]


def film_length():
    return float(json.loads((BUILD / "timeline.json").read_text(encoding="utf-8"))["duration"])

# kind -> recordings. Each is (title, BoomBox pack) or ("file", path inside the SFX library). A kind with
# several recordings cycles through them, so repeats are never one sample pasted. Titles and paths, not
# ids, so the choice reads here; resolved at build time (and it stops if one has gone).
# This PALETTE is the SG Awards film's, sound by sound as approved by ear over seven rounds: a proven
# starting set for the cut-out style. Change a kind's recording only by auditioning (sfx_audition.py).
PALETTE = {
    # ---- one-offs ----
    "gust":  [("Wind - Fragment 01", "Essentials")],
    "water": [("Submerge - Splashy", "Liquid Contact")],   # floods: a real splash, quick start, settled in ~1 s (measured)
    # conflict: a heavy, dark impact as the icon lands; ~390 Hz, above the bomb's sub rumble, so they do not blur
    "hit":   [("Gwarb Hit, Muted 01", "Call To Action")],
    "glass": [("file", "sound_effects/Sonotheque - Sound Fx/Miscellaneous/Window Break 01.mp3")],   # crisp: sharp start, gone in ~0.6 s (measured)
    # "Armed conflict" (Javier asked for BoomBox's bomb hit). The MUTED version: its own cue point is the
    # hit (225 ms), two thirds of its energy is under 200 Hz, and it trails a long rumble — a distant
    # explosion, not a cinematic blast in the room.
    "bomb":  [("A-Bomb Hit, Muted 01", "Call To Action")],
    # EVERY appearance sound is a SINGLE strike: one icon, one sound, on its frame (Javier, v15). Measured on the
    # recordings (distinct strikes in a 5 ms envelope): "Paper Set Down" was 2–3 hits, "Beefy Click Error" 2–4,
    # "Board Game - Place Card" 2 — so icons were getting two to four sounds each. These are all one strike.
    "pop":   [("Board Game - Lay Card 01", "Props"), ("Board Game - Lay Card 02", "Props")],   # a card laid down, once
    # "the typical error sound on a laptop": the single-strike errors closest in brightness to the Beefy Click ones
    # Javier accepted (Catgut Error 02: 3,016 Hz vs 2,945 Hz — measured)
    "error": [("Catgut Error 02", "Mobile Engagement"), ("Catgut Error 01", "Mobile Engagement")],
    "click": [("Mouse Click Single", "Essentials")],
    # the rows form: a short, sleek processing sound. Javier picked it by ear from four calmer options (21 Sept 2026,
    # R3 in sfx_audition.py); Rotodata - Processing 03, until v17, was bright (~3.3 kHz) and busy (~17 events a second)
    "rows":  [("Luxury Spaceship UI - Processing Complete", "Mech Tech")],
    "blop":  [("Bloop Alert 01", "Essentials"), ("Bloop Alert 02", "Essentials")],                       # "a 'blop' appear sound for each graph"
    # ONE soft tin tap per blue icon (teams, answers, aid; the dots turning blue). Javier picked it by ear on 21 Sept
    # 2026 (T1 in sfx_audition.py): the High Triangle "ting" of v16–v17 was "too disturbing" (bright, ~7.3 kHz), and
    # he asked for a papery or a tin sound. It must be a single strike: the "Simple Tri - Confirmation" used until
    # v15 is a three-note jingle (strikes at 0, 0.2, 0.3 s, measured), so five icons played fifteen chimes (Javier,
    # v15: "5 icons … only 5 sounds, one per icon at the exact time of appearance"). The kind keeps the name "chime";
    # its tail is cut short (TRIM) so one icon is one tap.
    "chime": [("Tin Foil Box - Hit", "Tactile Feelings")],
    "dotchime": [("Tin Foil Box - Hit", "Tactile Feelings")],
    # coordination: a pen drawing one line, from the older collections ("connecting lines, drawing lines")
    "drawline": [("file", "sound_effects/Sonotheque - Sound Fx/People/Acciones humanas/escribir una línea.mp3")],
    "reveal": [("Glisten Sweep 03", "Semi-Charmed")],                                                   # "like revealing": a bright sweep that peaks on the burst
    "coins": [("Coin Drop 01", "Mograph Machine")],
    "transmit": [("Bloop Transmit 01", "Essentials"), ("Bloop Transmit 02", "Essentials")],               # the megaphone's message going out
    "crowdin": [("Playing Cards - Shuffle on Table", "Props")],                                           # many paper people landing at once
    "peopleblue": [("Round Chimes - Flourish 01", "Semi-Charmed")],
    "hop":   [("Candy Notes - Lift 01", "Semi-Charmed")],
    "paper": [("Playing Cards - Flick Card 01", "Props"), ("Playing Cards - Flick Card 02", "Props")],
    "pullout": [("Parchment Paper - Pull Out 01", "Tactile Feelings"), ("Parchment Paper - Pull Out 02", "Tactile Feelings"), ("Parchment Paper - Pull Out 03", "Tactile Feelings")],
    "whoosh": [("Feather Whoosh 01", "Essentials"), ("Feather Whoosh 02", "Essentials")],
    "slide": [("Paper Slide", "Tactile Feelings")],
    # ---- beds ----
    "storm":  [("Summer Storm - Distant Thunder + Approaching Storm", "Places")],
    # a real police patrol siren, from Javier's AKAI collection (he asked for "ambulance/police"). BoomBox's
    # own is a hand-cranked civil-defence siren (Crank Siren 01, Golden Age pack — tagged "cartoon", which is
    # why a first search that filtered out "cartoon" missed it); the police siren is closer to his brief.
    "siren":  [("file", "sound_effects/AKAI soundeffects/ALARM/18 Police Patrol Wagon Siren.aiff")],
    "typing": [("Laptop - Typing 01", "Props")],
    "talk":   [("file", "sound_effects/Sonotheque - Sound Fx/Background/Amb gente hablando.MP3")],                      # people discussing, behind the decision makers
    "clock":  [("file", "sound_effects/Sonotheque - Sound Fx/Electronic/ClockTick.wav")],                               # tic-tac
    # advocacy: a radio on the air. The stretch used is the most static-like in the recording (spectral flatness,
    # measured: 0.4–0.7 all through — static and tuning, no voice to fight the narrator)
    "radio":  [("file", "sound_effects/Sonotheque - Sound Fx/Electronic/RadioTuner.wav")],
    "truck":  [("Rural Highway, Near Perspective - Semi Pass-By", "Places")],
    "walla":  [("Family Crowd - Walla 01", "Crowds")],
}
# Files in the library can be ONLINE-ONLY on a given Mac (Dropbox placeholders of 0 bytes: on 21 Sept 2026
# almost all of the older collections were). A kind whose own file is not downloaded falls back to these
# BoomBox recordings, and says so in the cue sheet; once the folder is made available offline (Dropbox:
# right-click → Make available offline), the next build uses the real file with no change here.
FALLBACK = {
    "siren":   [("Crank Siren 01", "Golden Age")],          # a hand-cranked emergency siren
    "talk":    [("Concert Crowd - Talking", "Crowds")],
    "clock":   "pattern",                                     # tick-tock built from two clicks (PATTERN)
}
# a bed built from one-offs repeating: (kind of recording, time in the cycle s), cycle length s
PATTERN = {"clock": ([("click1", 0.0), ("click2", 0.5)], 1.0)}
PALETTE["click1"] = [("Clothespin Click 01", "Essentials")]
PALETTE["click2"] = [("Clothespin Click 02", "Essentials")]
# kinds built from layers of other kinds: (layer kind, offset of its hit from the cue in s, dB)
LAYERS = {
    "snap":  [("pop", 0.0, 0.0), ("whoosh", -0.12, -4.0)],   # the chart swooshes into place and lands
    "sheet": [("slide", 0.05, 0.0), ("whoosh", 0.0, -3.0)],   # a full-screen sheet slides over the picture
    # "a sort of papery build-up" as the chart's bars grow: three paper pulls, each a little louder
    "paperbuild": [("pullout", 0.0, -6.0), ("pullout", 0.28, -3.0), ("pullout", 0.56, 0.0)],
}
BEDS = {"storm", "siren", "typing", "talk", "clock", "radio", "truck", "walla"}
# where in its recording a bed starts (s). The storm opens on its thunder roll (measured 0.5–6 s),
# which is why it starts at 0: the roll then lands on "An earthquake".
SRC_OFFSET = {"storm": 0.0, "siren": 0.0, "typing": 0.0, "talk": 2.0, "radio": 1.25, "clock": 0.0, "truck": 0.0, "walla": 3.0}
FADE = {"storm": (0.2, 2.2), "siren": (0.8, 3.0), "typing": (0.4, 0.8), "radio": (0.3, 0.5), "talk": (0.8, 1.0), "clock": (0.3, 0.4),
        "truck": (0.6, 1.2), "walla": (1.2, 1.6)}   # (in, out) s
# Per-kind processing before placing.
FILTER = {
    # far off: a distant sound loses its top and bottom and picks up the space around it
    "siren": "highpass=f=260,lowpass=f=2300,aecho=0.8:0.6:70|150:0.22|0.14",
    "bomb": "lowpass=f=2200",
    "glass": "lowpass=f=6500",   # a touch of distance, so it sits in the storm rather than in the room
    # people discussing in the BACKGROUND: blurred so no word can be followed over the narrator's
    "talk": "highpass=f=200,lowpass=f=1600",
    # typing takes are very spiky (a hard keystroke ~30 dB above the average, measured): soften the keystrokes
    # so the bed can sit at its level without one transient setting the peak (crest 30 → 20 dB)
    "typing": "acompressor=threshold=0.02:ratio=12:attack=0.1:release=60:makeup=1",
    "radio": "highpass=f=350,lowpass=f=3200",   # through a small speaker
    "rows": "lowpass=f=4000",   # softened: v15's was "too loud … find a subtler one or turn it down" (Javier). The
    # sound that replaced it (R3) was auditioned and picked WITH this filter, so it stays
}
BED_PEAK_UNDER = 8    # no ambience bed may peak closer than this (dB) to the voice's typical peak
# one-offs cut to this length (s), with a 40 ms fade: a single tap, not a long tail overlapping the next icon's
TRIM = {"chime": 0.36, "dotchime": 0.35, "hit": 0.9,   # hit: its long echo cut, a hit not a tail
        "rows": 0.9}                                    # rows: its first 0.9 s, exactly as auditioned
# the same kind closer together than this (s) plays once: the decision makers' question marks arrive 0.08 s apart
MIN_GAP = {"error": 0.05, "chime": 0.05, "blop": 0.05, "dotchime": 0.09}   # every question mark has its own error
# (round 6: "error sound 3 times, at the same time as each red ?"); only the dots' cascade is thinned, so fifty
# dots turning blue in ~2 s read as a run of chimes, not a smear
LEVEL = {   # dB under the voice (peak for one-offs, RMS for beds). Bigger = quieter.
    # Checked AS HEARD (full mix minus the same mix without effects, after the ducking): at v09 typing landed
    # 26 dB under the voice and the tool's snap 19 dB under — both lost — so they were lifted.
    "snap": 5, "bomb": 9, "sheet": 11, "click": 11, "paperbuild": 12,
    "peopleblue": 13, "hop": 13, "blop": 14,
    "pop": 15, "coins": 11, "error": 16, "gust": 16, "glass": 12, "water": 13, "hit": 11, "transmit": 13, "crowdin": 16,
    "reveal": 12, "rows": 22, "paper": 17, "drawline": 13,
    "chime": 17, "dotchime": 19,   # were 14 / 17 until v17: "subtler chim sound" (three comments on v16); 17 / 19 is what the auditions played
    "storm": 14, "truck": 16, "siren": 20, "typing": 17, "radio": 18, "clock": 18, "walla": 18, "talk": 18,   # walla/talk were 21/22: at or under the music once nothing is ducked — the effects sit ABOVE the music (Javier: voice, then effects, then music)
    # siren: 17 until v19 — on v19 Javier asked for "the siren even a bit more" [down] than the rest of the effects
}
# The whole effects layer, on top of every LEVEL above (Javier on v18, 21 Sept 2026: "I feel the sfx need to go a bit
# lower, they are slightly loud"). ONE gain for all of them, so the balance between the effects, approved sound by
# sound over seven rounds, stays exactly as it is. The cue sheet's levels include it.
# −3 in v19; −5 from v20 (Javier on v19: "lower the sfx slightly down"). The kit starts from −5 — the SG
# film's final, approved balance — so a new film starts where that one ended, not where it began.
EFFECTS_DB = -5


def get_cues():
    """Ask the film page for its score (window.SFX), with the same headless browser as probe.mjs."""
    r = subprocess.run(["node", "--experimental-websocket", str(BUILD / "probe.mjs"), "--times", "0",
                        "--expr", "window.SFX"], capture_output=True, text=True, check=True)
    line = next(l for l in r.stdout.splitlines() if l.startswith("t="))
    cues = json.loads(line.split("  ", 1)[1])   # probe.mjs prints the JSON as-is
    if not cues:
        sys.exit("the page returned no cues: is score.js loaded in world.html?")
    return cues


def catalogue():
    """BoomBox's sounds in the library, from its index (pack, title, file, seconds, tags) — the copy in
    Dropbox keeps each sound under its pack and name (SFX/BoomBox/update_boombox_copy.py made it)."""
    idx = lib() / "BoomBox" / "boombox_index.csv"
    if not idx.exists():
        sys.exit(f"No BoomBox index at {idx}. Is the whole SFX library in this Dropbox (Design/Resources/SFX)?")
    with open(idx, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def resolve(cat, title, pack):
    """(recording info, its file) — or (None, file) if Dropbox has it online-only on this Mac."""
    if title == "file":   # a recording elsewhere in the library: (path inside it)
        import unicodedata
        want = unicodedata.normalize("NFC", pack)
        path = lib() / pack
        if not path.exists():   # accents: macOS may store the name decomposed (NFD)
            hits = [p for p in (lib() / pathlib.Path(pack).parent).glob("*") if unicodedata.normalize("NFC", p.name) == unicodedata.normalize("NFC", pathlib.Path(pack).name)]
            if not hits:
                sys.exit(f"not found in the SFX library: {pack}")
            path = hits[0]
        if path.stat().st_size == 0:   # a Dropbox online-only placeholder: not on this Mac yet
            return None, path
        return {"id": "file:" + want, "title": pathlib.Path(pack).stem, "cuePoints": []}, path
    hits = [r for r in cat if r["pack"] == pack and r["title"].lower().startswith(title.lower())]
    if not hits:
        sys.exit(f"The library has no '{title}' in BoomBox pack '{pack}'. Search BoomBox/boombox_index.csv and pick another in PALETTE.")
    r = sorted(hits, key=lambda r: len(r["title"]))[0]
    path = lib() / "BoomBox" / r["file"]
    if not path.exists():
        sys.exit(f"'{title}' is in the index but not in the folder: {path}")
    if path.stat().st_size == 0:   # online-only on this Mac
        return None, path
    # no cue point in the copy: ALIGN_PEAK kinds use the loudest point, which is what BoomBox's cue marked
    return {"id": "boombox:" + r["file"], "title": r["title"], "cuePoints": []}, path


def decode(path, af=None):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path)] + (["-af", af] if af else []) +
                         ["-ac", "2", "-ar", str(RATE), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()


def peak_db(a):
    return 20 * math.log10(max(1e-9, float(np.abs(a).max())))


def rms_db(a, floor=-60):
    """RMS over the parts that are actually sounding (50 ms windows above `floor` dBFS)."""
    n = int(0.05 * RATE)
    m = a[: len(a) // n * n].reshape(-1, n, 2)
    w = np.sqrt((m ** 2).mean(axis=(1, 2)))
    w = w[w > 10 ** (floor / 20)]
    return 20 * math.log10(max(1e-9, float(np.sqrt((w ** 2).mean())) if len(w) else 1e-9))


# Which point of a recording lands on its cue. BoomBox's cuePoints sit at a sound's PEAK, not where it starts:
# for a paper set-down the rustle starts ~150 ms before its peak, so peak-on-cue made the sound START before its
# icon appeared — 35 of 40 one-offs were 80–245 ms early (measured on v13; Javier: "review sounds to coordinate
# with exact appearance of icons"). So an APPEARANCE lines up where the sound starts (onset: the first sample over
# 10 % of its peak), exactly on the frame its thing appears. Only sounds that build INTO a moment keep their peak
# on it: a sweep that swells to the reveal, a whoosh that peaks mid-travel.
ALIGN_PEAK = {"reveal", "whoosh"}


def hit_point(s, a, kind):
    env = np.abs(a).max(axis=1)
    if kind in ALIGN_PEAK:
        cp = s.get("cuePoints") or []
        return max(0, int(round(cp[0] / 1000 * RATE))) if cp else int(np.argmax(env))
    over = np.nonzero(env > 0.1 * env.max())[0]
    return int(over[0]) if len(over) else 0


def voice_levels():
    """The voice's typical peak (90th percentile of its 50 ms peaks) and its speech RMS, PER CHANNEL.
    (An ffmpeg mono downmix sums the channels and reads ~6 dB hot.)"""
    if not VOICE.exists():   # said out loud, never silent: the levels are only right once the real voice is in
        print(f"No voice track yet ({VOICE.relative_to(BUILD)}): levels set against a typical OCHA voiceover "
              f"(peak {NOMINAL_VOICE[0]} dBFS, speech {NOMINAL_VOICE[1]} dBFS). Rebuild once voice_track.py has run.")
        return NOMINAL_VOICE
    v = decode(VOICE)
    n = int(0.05 * RATE)
    peaks = np.abs(v[: len(v) // n * n]).reshape(-1, n * 2).max(axis=1)
    speech = peaks[peaks > 10 ** (-40 / 20)]
    return 20 * math.log10(float(np.percentile(speech, 90))), rms_db(v, floor=-40)


def fade(a, fin, fout):
    n = len(a)
    i, o = min(n, int(fin * RATE)), min(n, int(fout * RATE))
    if i: a[:i] *= np.linspace(0, 1, i, dtype=np.float32)[:, None]
    if o: a[n - o:] *= np.linspace(1, 0, o, dtype=np.float32)[:, None]
    return a


def build(cues, write=True):
    cat = catalogue()
    sounds, stand_ins = {}, {}
    for k, v in PALETTE.items():
        got = [resolve(cat, t, p) for t, p in v]
        if all(s is not None for s, _ in got):
            sounds[k] = got
            continue
        missing = [str(p.relative_to(lib())) for s, p in got if s is None]
        fb = FALLBACK.get(k)
        if fb is None:
            sys.exit(f"'{k}': not downloaded from Dropbox and no stand-in: {missing}")
        stand_ins[k] = missing
        sounds[k] = [] if fb == "pattern" else [resolve(cat, t, p) for t, p in fb]
    cache = {}
    def rec(kind, n):
        s, path = sounds[kind][n % len(sounds[kind])]
        key = (s["id"], kind)                     # the same recording can be processed differently per kind
        if key not in cache:
            a = decode(path, FILTER.get(kind))
            if kind in TRIM:   # cut the ring short, with a 40 ms fade
                n_ = min(len(a), int(TRIM[kind] * RATE)); a = a[:n_].copy(); f_ = min(n_, int(0.04 * RATE))
                a[n_ - f_:] *= np.linspace(1, 0, f_, dtype=np.float32)[:, None]
            cache[key] = (s, a, hit_point(s, a, kind))
        return cache[key]

    vpeak, vrms = voice_levels()
    FILM = film_length()   # the film's length, from timeline.json
    buf = np.zeros((int(FILM * RATE) + RATE, 2), dtype=np.float32)
    count, sheet = {}, []

    def place(a, start):
        a0 = max(0, -start); start = max(0, start)
        seg = a[a0:][: len(buf) - start]
        buf[start: start + len(seg)] += seg

    last = {}
    for c in cues:
        kind, t = c["kind"], c["t"]
        if t - last.get(kind, -9) < MIN_GAP.get(kind, 0):
            sheet.append((t, None, kind, c["label"] + "  (merged with the one just before)", "—", 0, "")); continue
        last[kind] = t
        n = count.get(kind, 0); count[kind] = n + 1
        if kind in BEDS:
            length = int((c["until"] - t) * RATE)
            if kind in stand_ins and FALLBACK[kind] == "pattern":    # e.g. tick-tock from two clicks
                hits, cycle = PATTERN[kind]
                src = np.zeros((int(cycle * RATE), 2), dtype=np.float32); title = []
                for hk, at in hits:
                    s, a, hp = rec(hk, 0)
                    b0 = max(0, int(at * RATE) - hp); seg0 = a[: len(src) - b0]
                    src[b0: b0 + len(seg0)] += seg0; title.append(s["title"])
                title = "tick-tock from " + " + ".join(title)
            else:
                s, a, _ = rec(kind, n)
                src = a[int(SRC_OFFSET.get(kind, 0) * RATE):]; title = s["title"]
            reps = int(math.ceil(length / max(1, len(src))))
            seg = np.concatenate([src] * max(1, reps))[:length].copy()
            # its RMS LEVEL dB under the voice's — but never a PEAK above BED_PEAK_UNDER dB under the voice's
            # peak. A spiky recording (one hard keystroke in a quiet take) has a low RMS, so RMS alone
            # would push that one transient to full scale: v12's coordination typing hit −0.2 dBFS, the
            # anti-clip safeguard then pulled the whole stem down ~5 dB and buried three other sounds.
            g_rms = ((vrms - LEVEL[kind]) - rms_db(seg))
            g_peak = ((vpeak - BED_PEAK_UNDER) - peak_db(seg))
            seg *= 10 ** (min(g_rms, g_peak) / 20)
            place(fade(seg, *FADE[kind]), int(round(t * RATE)))
            if kind in stand_ins:
                title += "   ← STAND-IN: yours is online-only in Dropbox"
            sheet.append((t, c["until"], kind, c["label"], title, vrms - LEVEL[kind] + EFFECTS_DB, "rms"))
        else:
            layers = LAYERS.get(kind, [(kind, 0.0, 0.0)])
            names = []
            for li, (lk, off, lg) in enumerate(layers):
                s, a, hp = rec(lk, n + li)   # each layer its own variant: three paper pulls, not one pull three times
                g = 10 ** (((vpeak - LEVEL[kind] + lg) - peak_db(a)) / 20)   # its peak, LEVEL dB under the voice's
                place(a * g, int(round((t + off) * RATE)) - hp)
                names.append(s["title"] + ("   ← STAND-IN: yours is online-only in Dropbox" if lk in stand_ins else ""))
            sheet.append((t, None, kind, c["label"], " + ".join(names), vpeak - LEVEL[kind] + EFFECTS_DB, "peak"))

    buf *= 10 ** (EFFECTS_DB / 20)         # the whole layer down together (EFFECTS_DB), before the anti-clip check
    peak = float(np.abs(buf).max())
    if peak > 0.98:                        # never clip: pull the whole stem down if it must — and SAY so,
        at = int(np.argmax(np.abs(buf).max(axis=1))) / RATE   # because it quietly lowers every other sound too
        print(f"WARNING: the effects stem peaked at {20 * math.log10(peak):+.1f} dBFS at {at:.2f} s and was pulled down "
              f"{20 * math.log10(peak / 0.98):.1f} dB — every effect is now quieter than its LEVEL. Fix that sound's level.")
        buf *= 0.98 / peak
    buf = buf[: int(round(FILM * RATE))]
    if write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(RATE), "-ac", "2", "-i", "-",
                        "-c:a", "pcm_s24le", str(OUT)], input=buf.tobytes(), check=True)
        if OUT == BUILD / "audio" / "sfx_track.wav":   # the film's own track (not an audition's): its cue sheet too
            CUES_OUT.write_text(json.dumps([{"t": t, **({"until": u} if u else {}), "kind": k, "label": lb, "sound": sn}
                                            for t, u, k, lb, sn, _, _ in sheet if sn != "—"], ensure_ascii=False, indent=1), encoding="utf-8")
    return sheet, vpeak, vrms


def strikes(a):
    """How many separate strikes a recording has — the SG film's counter, which found the multi-note sounds
    (a 3-note "confirmation" chime, 2–4-note errors, 2–3-hit paper set-downs) and passed the singles Javier
    then approved by ear. Peaks of the 5 ms envelope within 20 dB of the loudest; two count apart only if the
    sound dips more than 6 dB below the smaller of them in between AND they are at least 60 ms apart —
    without the 60 ms, the ripple in one sound's own tail reads as extra hits. One icon = one strike."""
    env = np.abs(a).max(axis=1); w = int(0.005 * RATE); e = env[: len(env) // w * w].reshape(-1, w).max(axis=1)
    d = 20 * np.log10(np.maximum(e, 1e-6)); top = d.max()
    peaks = [i for i in range(1, len(d) - 1) if d[i] >= d[i - 1] and d[i] > d[i + 1] and d[i] > top - 20]
    out = []
    for i in peaks:
        if not out:
            out.append(i); continue
        j = out[-1]
        if d[j:i + 1].min() < min(d[j], d[i]) - 6 and i - j >= 12:
            out.append(i)
        elif d[i] > d[j]:
            out[-1] = i
    return len(out)


# The kinds that mark ONE thing appearing (an icon, a graph, a label): the single-strike rule applies to them.
# Event sounds (a splash, breaking glass, a rumble, wind, a pen) and runs (processing, coins, a shuffle) are
# naturally several strikes; the check lists them for information only.
APPEARANCE = ("pop", "error", "blop", "chime", "dotchime", "paper")


def check_strikes(candidates=()):
    """Every appearance sound as the film plays it (filter and trim applied) — or candidates ("Title|Pack",
    before one goes into PALETTE): one strike each?"""
    cat, bad = catalogue(), 0
    if candidates:
        for c in candidates:
            title, _, pack = c.partition("|")
            s, path = resolve(cat, title.strip(), pack.strip())
            k = strikes(decode(path)) if s else None
            print(f"  {s['title'] if s else c:<48} {'online-only, not checked' if k is None else f'{k} strike' + ('s' if k != 1 else '')}")
        return
    for kind, recs in PALETTE.items():
        if kind in BEDS or kind in ("click1", "click2"):
            continue
        for t, p in recs:
            s, path = resolve(cat, t, p)
            if s is None:
                print(f"  {kind:<10} {t if t != 'file' else p}: online-only on this Mac, not checked"); continue
            a = decode(path, FILTER.get(kind))
            if kind in TRIM: a = a[: int(TRIM[kind] * RATE)]
            k = strikes(a); flag = kind in APPEARANCE and k != 1; bad += flag
            print(f"  {kind:<10} {s['title'][:44]:<44} {k} strike{'s' if k != 1 else ''}"
                  + ("   ← an icon would get several sounds" if flag else "" if kind in APPEARANCE else "   (event or run: several is fine)"))
    print(f"appearance sounds ({', '.join(APPEARANCE)}) with more than one strike: {bad or 'none'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="print the cue sheet without writing the stem")
    ap.add_argument("--strikes", nargs="*", metavar="TITLE|PACK",
                    help="check the appearance sounds are single strikes (or these candidates, before choosing one)")
    a = ap.parse_args()
    if a.strikes is not None:
        return check_strikes(a.strikes)
    sheet, vpeak, vrms = build(get_cues(), write=not a.list)
    print(f"{len(sheet)} sounds · voice: typical peak {vpeak:.1f} dBFS, speech RMS {vrms:.1f} dBFS")
    for t, until, kind, label, snd, lvl, how in sheet:
        span = f"{int(t) // 60}:{t % 60:05.2f}" + (f"–{int(until) // 60}:{until % 60:05.2f}" if until else " " * 8)
        print(f"  {span}  {kind:<6} {label[:44]:<44} {lvl:6.1f} dBFS {how:<4}  {snd}")
    if not a.list:
        print(f"wrote {OUT.relative_to(BUILD)}")


if __name__ == "__main__":
    main()
