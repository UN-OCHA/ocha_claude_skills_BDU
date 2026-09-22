# Cut-out — the process, script to export

How the SG Awards 2026 Dataviz animation was made
([watch it](https://www.dropbox.com/scl/fi/a7a1kd3fhx60f35xyecl2/sg_awards_2026_film_1920x1080.mp4?rlkey=xm4o8g38esx4a94jsmyvms8aq&dl=0)):
three days (19–21 September 2026), 21 versions, about 75 review comments over seven rounds. Follow
the same steps; each one lists what to hand the person and what to check. The look: `cutout-style.md`.

## 0 · Set up the job

- The job folder first: `ocha-files-and-folders` (`Projects/<year>/<office>/<job_name>`, with a README).
- Then the kit: `python3 <this skill>/scripts/new_cutout_film.py "<job>" --title "<Film title>"`. It copies
  the engine, the tools, the shared audio tools and the review tool into `assets/build/`, and a demo
  film that builds at once: open `assets/build/film/world.html` to see the style running.

## 1 · Script

- **Write for the ear.** About 130–150 words a minute: the SG film is 19 lines in 1:20.
- **One idea per line.** The lines are the film’s beats; a scene is one to five lines.
- **Mark the words that carry the story:** they will sit on colour (red for the crisis and its
  questions, blue for what helps).
- **Write the voice’s text separately** (`assets/voice/voiceover_tts_plain.txt`, one script line per
  text line): “Ocha” not “OCHA”, numbers as they are said, a dash where the voice should pause.
- **Lock it** (`info/`) before the voice is made: every change after costs a new take and new timings.

## 2 · Style inspiration

- Cut-out is the house style for these films; say so and show the reference film.
- For a new feel, gather 3–5 references first. The SG film’s: Vox explainers (paper collage), Ayuda en
  Acción’s 2014 report (Relajaelcoco), Zanussi 100 Years (Bill Porter), Airbnb’s curated restaurants.
- **Test on ONE real moment of the script**, two or three ways, as short renders (the SG film: v1 flat,
  v2 paper cut-out, v3 the one that was locked). Let the person choose and lock it in the README.
- **Every open choice gets one option sheet:** A / B / C, labelled with what differs in words, and a
  recommendation (the SG film’s: three word treatments, two reds, map simplifications A–F).

## 3 · Storyboard

- **Stills are exact frames of the film** (the page at `?t=`): name one settled moment per scene in
  `FILM.KEYS`, then `stills.mjs` and `contact_sheet.py` put them on one sheet in `info/`.
- The person approves the sheet **before** motion is finished. The scenes sit on the voice
  (`timeline.py`: lead-in, beats, the ending), so the storyboard is already on the film’s clock.

## 4 · Voice

- ElevenLabs on its free credits — the shared guide: `ocha-video` → `references/sound-voice-music.md`
  (a free account if they have none; one generation at a time, with their go; pick the voice by ear).
- Then the timings: `word_timings.py` (the words to a frame) → `timeline.py` → `voice_track.py` (the
  voice on the film’s clock). **`check_sync.mjs` must pass** before anything else is built on it.

## 5 · Build

- **Everything is cued from the words** — `W(line)[word].start`, never typed seconds — so when the voice
  or the pacing changes, the whole film moves with it.
- `scenes.js`: the pieces (`badge`, `piece`), links, the camera (`cam`, `focus`), the named moments.
  `decor.js`: the drawings on words. `words.js`: the colours. Share every position and time the sound
  or the drawings need through `FILM.pos` — never retype one.
- House rules: `motion-rules.md` (exits reverse entrances, one thing at a time); OCHA icons only; charts
  as wireframes; the logo untouched.
- **Measure, don’t eyeball:** `probe.mjs` reads the page at an exact time (a gap, an overlap, a word’s
  place). A fixed crop of two stills can’t be compared while the camera moves.

## 6 · Review rounds

- **Render** (`render_frames.mjs` → `encode.sh` → `mix.py`) into `previews/<name>_film_vNN.mp4`.
  A picture change needs a re-render (about 5 minutes for 1:20); a sound change copies the picture and
  takes seconds.
- **The review tool** (`ocha-video` → `references/review-tool.md`): the person comments on exact frames;
  Claude fixes, renders the next version, and answers every comment with it. Options first when the
  choice is theirs — nothing changes in the film until they pick.
- **Prove a re-render changed only what was asked:** compare its frames with the previous render’s
  (a hash per frame). The SG film’s last change touched 106 frames; the other 2,285 were byte-identical.

## 7 · Sound effects

- The score (`score.js`), from the picture’s own times; the track (`sfx_mix.py`), from the BDU library.
- A new sound: check candidates are single strikes (`sfx_mix.py --strikes "Title|Pack"`), cut clips of
  the moment (`sfx_audition.py`), and let the person pick by ear.
- Send a no-voice copy with every sound round (`mix.py --no-voice`).

## 8 · Music

- Flippermusic — the login and password are on our Trello (shared guide). Shortlist, measure the fit
  (`music_fit.py`), put two or three under the film, pick by ear, license and download the WAV.

## 9 · Mix and check

- `mix.py`: three layers at constant levels. `voice_clarity.py`: every word at least 10 LU above the
  music and effects. When the effects feel loud, lower the whole layer (`EFFECTS_DB` in `sfx_mix.py`)
  and keep their balance.

## 10 · Final and close

- Re-render, then check the file itself: frames match the render, **colour tags BT.709 throughout**
  (`encode.sh` warns if not), Apple AAC at 320k, the exact length.
- Export per `ocha-files-and-folders`: `export/<name>_1920x1080.mp4`, copied with `cp -X` (a re-export
  over it keeps its Dropbox link).
- Close the job: the draft renders go (the person decides: delete or archive); the comments file stays
  in `info/review/` as the record; the README says what was made, how, and why.
