# Voice, music and sound effects

For every OCHA video and animation. This guide is shared: `ocha-video` keeps it, `ocha-animation`
points here. Everything in it was learned on the SG Awards 2026 Dataviz film, the reference for how
an OCHA film should sound:
[watch it](https://www.dropbox.com/scl/fi/a7a1kd3fhx60f35xyecl2/sg_awards_2026_film_1920x1080.mp4?rlkey=xm4o8g38esx4a94jsmyvms8aq&dl=0).

## 1 · The mix: three layers at constant levels

> “Think of voice / sound effects / music as 3 layers with constant volume, with voice being louder,
> sound effects mid and music lower.” — Javier, 21 September 2026

- **Voice on top, effects in the middle, music lowest.** Each layer sits at one level for the whole
  film. **Nothing ducks anything**: no sidechain, no automation that dips the music under words. A
  ducked music bed follows the words and pumps; that was the first thing he heard and rejected.
- **The voice must stand out clearly** over the music and the effects on every word, not just on
  average. Test it with `scripts/audio/voice_clarity.py` (§6) before anything goes out.
- **Music at −24 dB** on a typical library track sits about 21 dB under the voice’s speech: behind it,
  and under the effects. Fade it in over 1.5 s where it starts and out over the last 3 s.
- **When the effects feel loud, turn the whole layer down together** rather than sound by sound: the
  balance between the effects, approved one by one, stays exactly as it was. (The SG film ended 5 dB
  under where it started, the siren 3 dB more.)

## 2 · Voice — ElevenLabs, on the free credits

- Voiceovers are made with **ElevenLabs** on its free credits. If the person doesn’t have an account,
  **ask them to create a free one** at elevenlabs.io and connect ElevenLabs to Claude (the Claude
  app’s connectors), then generate from here.
- **One generation at a time, each with the person’s go**: the free credits are few. Offer two or
  three voices from the voice library first, with a line of the real script, and let them pick by ear.
- **Write the text for the voice, not for the page:** “Ocha”, not “OCHA” (or the voice spells it
  out); numbers as they should be said; a dash where a pause should fall.
- Keep every take in the job (`assets/voice/`); the one used is named in the README with its voice,
  model and take. The SG film: library voice Olaniyi Victor, model v3, take 1.
- For an animation, the words then need timings to the frame: see `ocha-animation` → the cut-out
  process (word timings).

## 3 · Music — Flippermusic

- Music comes from **Flippermusic** (flippermusic.it), BDU’s subscription. **The login and password are
  on our Trello**: BDU work plan board → list “Design resources” → card “Music archive from Matteo +
  Flipper” (the card also links Matteo’s music archive). Never copy the login anywhere else.
- **Shortlist 4–6 tracks** that fit the script’s mood and pace; download previews only to judge them
  (ask before each download). Keep the shortlist in `info/` with why each fits.
- **Measure, don’t guess, where a track lifts:** the waveform pictures on the site mislead (one
  “lifts at 0:39” lifted at 0:24). For an animation, `music_fit.py` in the cut-out kit lines a
  track’s loudness up with the scenes.
- **Put two or three under the film and let the person pick by ear.** Offset a track so its lift
  lands on a moment of the film, not near it.
- **License and download the full-quality WAV** while the subscription is active, into
  `assets/audio/`; note the track’s title and code in the README. Previews are for judging only.

## 4 · Sound effects — the team library

**Where:** the BDU sound library in Dropbox, `~/OCHA DMU Dropbox/<your-name>/Design/Resources/SFX/`
(if the Design folder sits elsewhere in your Dropbox, search it for `Resources/SFX`):

| Folder | What |
|---|---|
| `BoomBox/` | 15,498 sounds in 46 packs (BoomBox by Mt. Mograph), each under its real name. **`BoomBox/boombox_index.csv`** lists every sound with its pack, length and tags — search the tags (“whoosh”, “paper”, “error”, “riser”). |
| `sound_effects/` | Older collections: AKAI, Sonotheque, Background Trax. Real sirens, clocks, crowds, a pen on paper. |
| the loose files | Single downloads (Freesound, Pixabay, Artlist…), named as they came. |

BoomBox is licensed per seat: the copy is for BDU members with a seat. Never pass the raw files
outside that group; mixed into a finished film they are fine.

**How to use them** — each rule cost a review round on the SG film:

1. **A few sounds that carry meaning, never one per element.** Context first: a siren far off under
   an emergency, a clock where time is short, people murmuring behind a crowd. “Don’t overdo it.”
2. **One thing appearing = one sound, on its frame.** Five icons, five sounds. Check a recording is a
   **single strike** before using it: many library “confirmation” and “error” sounds are 2–4 notes,
   and each icon then plays three sounds, two of them late.
3. **Line up where the sound starts, not its peak.** Library cue points mark the loudest point; set on
   the cue, sounds started 80–245 ms before their icon. Put the first sample above 10 % of the peak on
   the frame. Only a sweep or whoosh that builds into a moment keeps its peak on it.
4. **Soft timbres for repeated sounds.** A bright triangle “ting” on every blue icon was “too
   disturbing”; a soft tin tap replaced it. Bright (~7 kHz) and busy sounds tire fast.
5. **Levels are set against the voice:** a one-off’s peak so many dB under the voice’s typical peak; an
   ambience by its loudness under the speech, **with a peak ceiling** — one spiky keystroke in a typing
   bed once set the whole track’s peak and pulled every other effect down 5 dB without a word.
6. **Pick by ear from short clips.** For a sound that isn’t right, cut 2–3 s clips of that moment with
   each candidate (music and effects, no voice) and let the person choose; nothing changes in the film
   until they do. Set the level to what they heard.
7. **Review the effects without the voice too:** export a no-voice copy (`mix.py --no-voice`) with each
   round — it is where effects get judged.

## 5 · The formats that come out

- Audio **Apple AAC 320k** (`mix.py` does it): ffmpeg’s own AAC at 192k blurred sharp sounds — on the
  SG film its error on a keystroke was as loud as the keystroke. It falls back, loudly, off a Mac.
- 48 kHz stereo throughout; stems as WAV (24-bit) in `assets/build/audio/`.

## 6 · Tools — `scripts/audio/`

- **`mix.py`** — voice, music and effects under a picture, at constant levels; the picture is copied,
  never re-encoded. `--no-voice` for the review copy. Refuses to write over its own picture.
- **`voice_clarity.py`** — how far the voice sits above the rest, word by word (an animation’s
  `timeline.json`, or any word list), or phrase by phrase when there is no word list (coarser: use
  words when you have them). Aim for every word ≥ 10 LU; it lists the words that miss and, with
  `--cues`, the effects sounding under each. It checks its own meter against ffmpeg’s first.
- Measure a codec against the **uncompressed** mix, block by block (50 ms): a whole-film average hides
  a 50 ms defect.

For an animation, `ocha-animation`’s cut-out kit adds the rest: the sound score written from the
picture’s own timings, the effects track built from the library, and the audition clips.
