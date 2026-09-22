# Cut-out kit

The engine and tools of the **cut-out** animation style, as they made the SG Awards 2026 Dataviz film
([watch it](https://www.dropbox.com/scl/fi/a7a1kd3fhx60f35xyecl2/sg_awards_2026_film_1920x1080.mp4?rlkey=xm4o8g38esx4a94jsmyvms8aq&dl=0)).
`new_cutout_film.py` (in the skill’s `scripts/`) copies it into a job’s `assets/build/` with the
shared tools; it ships with a 9-second demo film that builds before any voice exists.

The style: `references/cutout-style.md`. The whole process, script to export: `references/cutout-process.md`.

## The film page — `film/`

| File | What it is | Change it? |
|---|---|---|
| `world.html` | loads everything, in order | rarely |
| `world.js` | the engine: time, paper clocks (MAT), the cut edge, camera, links, pieces, the spoken words | only to change the engine |
| `film.css`, `world.css` | the look: tokens, badges, labels, devices, people, sheets | to add a component |
| `words.js` | which words sit on colour; the big last line, the sign-off title | **the film’s** |
| `scenes.js` | the pieces, cued from the voice; the camera | **the film’s** (the demo now) |
| `decor.js` | background drawings tied to words (+ the drawing tools) | **the film’s** drawings at the bottom |
| `score.js` | the sound score: which kind of sound plays when | **the film’s** |
| `wireframes.js`, `worldmap.js` | charts and maps as wireframes; the world map at six simplifications | no |
| `timeline.js`, `icons.js` | generated (`timeline.py`, `icons.py`) | never by hand |

Open `film/world.html` in Chrome to play it; `world.html?t=12.5` freezes a moment.

## The tools — run from the job folder

```bash
python3 assets/build/timeline.py              # voice timings → the film's timeline (scenes, beats, ending)
python3 assets/build/icons.py                 # the icons the film uses (NAMES at the top)
node --experimental-websocket assets/build/check_sync.mjs    # every word painted on its sound, or it fails
node --experimental-websocket assets/build/stills.mjs        # one still per named moment (FILM.KEYS)
python3 assets/build/contact_sheet.py         # the storyboard sheet → info/
node --experimental-websocket assets/build/probe.mjs --times 5.9 --expr "…"   # measure the page, don't eyeball it
python3 assets/build/voice_track.py           # the voice on the film's clock (once the voice exists)
python3 assets/build/sfx_mix.py               # the effects track from the score (+ --strikes to vet sounds)
python3 assets/build/sfx_audition.py <set>    # short clips of one moment, one per candidate sound
python3 assets/build/music_fit.py <track>     # where a track lifts, against the scenes
python3 assets/build/mix.py --picture … --voice … --music … --sfx … --out …   # voice, effects, music
python3 assets/build/voice_clarity.py --voice … --music … --sfx … --words assets/build/timeline.json
python3 assets/build/review/review_server.py --videos assets/build/previews --comments info/review/<name>_review.json --timeline assets/build/timeline.json --title "…"
```

Rendering: the ocha-animation skill’s `scripts/render_frames.mjs` and `scripts/encode.sh`.
Word timings for a real voice: `word_timings.py` (runs with QuickVid’s Python: see its header).

## Settings — `film.json`

`name` (file names start with it), `title`, and the `music` once chosen (`file` relative to the job,
`offset` s, `db`). `sfx_mix.py` holds the sound palette, levels and the whole-layer gain.

## Needs

Chrome, ffmpeg, Node, Python 3 with numpy and Pillow; Roboto and Roboto Condensed installed; the BDU
sound library in Dropbox (`Design/Resources/SFX`, or `OCHA_SFX=/path`) for the effects.
