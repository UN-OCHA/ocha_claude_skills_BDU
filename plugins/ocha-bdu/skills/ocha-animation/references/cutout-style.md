# Cut-out — the style

**Paper cut-outs in one continuous world.** Flat OCHA shapes and icons cut from paper — a hand-cut
edge, a hard shadow — moving in stop-motion, while the voiceover’s words land on paper labels as they
are spoken.

**The reference is the SG Awards 2026 Dataviz animation:**
[watch it](https://www.dropbox.com/scl/fi/a7a1kd3fhx60f35xyecl2/sg_awards_2026_film_1920x1080.mp4?rlkey=xm4o8g38esx4a94jsmyvms8aq&dl=0).
“Cut-out”, “the cut-out style”, “paper cut-out” or “like the SG Awards Dataviz animation” all mean
this. The kit (`templates/cutout/`) is that film’s engine; start every cut-out film from it
(`scripts/new_cutout_film.py`). The process, script to export: `cutout-process.md`.

**For:** voice-led explainers and data films of one to two minutes, told through icons, charts and a
few words. **Not for:** a principal’s statement or real footage — that is `ocha-video`.

Every value below was set by a review comment on the SG film, noted where it matters, so a change is
made knowing why the value is what it is.

## 1 · The world

- **One continuous world, no cuts.** A single warm ground (`#EDEAE6`, the Slate Grey ramp) with a faint
  dot grid (48 px); every piece floats on it; the camera glides from place to place through it.
- A few faint circles, squares and crosses drift behind, with less parallax than the world: depth.
- **The end is a sheet of paper wiping in** — a light-blue sign-off sheet with the names and the OCHA
  logo, then a black sheet a second after the last word. A wipe, never a fade.

## 2 · The paper

- **Every piece is paper:** a round white badge holding a humanitarian icon, a label under each word, a
  chart, a screen, a person.
- **The paper look is one SVG filter:** a hand-cut edge (a turbulence displacement of 2.5–5 px) and a
  hard shadow, offset 6 / 8 px at 17 % (people: 3 / 4 px at 10 %). Five variants each, so the edge can
  “boil” — change from pose to pose.
- **Letters stay crisp:** on a word label only the paper (its `::before`) takes the cut edge.
- **Materials** (`MAT` in `world.js`) — how much each kind of piece moves:

  | Material | Wobble | Edge | Moves at | Boils at | Why |
  |---|---|---|---|---|---|
  | badge | 1.1 px, 0.5° | rough | 12 / 10 poses/s | 12 / 10 / 8 | icons — calmed from 1.6 px (“too much shaking when the camera zooms out”) |
  | word | 0.8 px, 0.45° | finer | 12 | 8 / 7 / 6 | the words: calmer still |
  | num | 1.0 px, 0.5° | none | 12 / 10 | 10 / 8 | numbers |
  | chart | 0 | finest | 12 | — | **charts sit perfectly still**: the tool’s clean result (“the shake of the center chart”) |
  | person | 0.5 px, 0.25° | small, soft shadow | 12 | 5 / 4 | people: calm (“people are shaking too much”) |
  | device | 1.2 px, 0.45° | fine, **fixed** | 12 / 10 | 8 / 7 | screens, reports, phones: a visible wobble, but the big outline never crawls |
  | line | 0 | none | 12 / 10 | 8 | the background drawings |

- **Charts and maps are wireframes:** shapes only — no real data, no real geography (`wireframes.js`).
  A map is the real world super-simplified (level E, land only, no borders) on white paper, like a
  poster: bare land didn’t hold up next to the charts.
- **Icons:** official OCHA Humanitarian Icons only (`icons.py`), never drawn. Their colour tells the
  story: red for a crisis, blue once answered or helped, grey for what hasn’t happened yet.
- **Colour:** OCHA palette only. Words on white labels; **dark red** (`#A71F36`) labels for a crisis and
  its questions; **OCHA blue** (`#009EDB`) for the tool and what helps. Bright OCHA red (`#ED1847`) is
  for shapes only, never behind words.
- **The OCHA logo:** the official file on a white paper card with its clear space — never cut,
  wobbled or shadowed.
- **Never photo collage.** The feel is the Vox paper-collage explainer, made of flat vectors.

## 3 · The motion — the shaking

- **Every piece keeps its own paper clock.** It moves in poses (holds of 1/12 or 1/10 s), wobbles a
  little between poses, and its edge boils. Its rates come from its id and its phase from its cue, so
  it lands exactly on its cue and no two pieces tick together — “the wobble must be independent for
  every object, more natural” (Javier). `check_sync.mjs` measures it: the share of pieces changing
  pose on the same frame should stay near a quarter.
- **Entrances pop:** from 40 % size with a slight overshoot, on the pose clock. **Exits are the
  entrance in reverse.** Several at once arrive 0.06–0.16 s apart.
- **The camera is continuous, never stepped:** keyframes eased in and out, a slow breath (±14 px drift,
  ±1.2 % zoom), and it leans toward what the voice names. A travel starts before a sentence ends and
  lands a word or two into the next; about 1.5 s for a screen’s width — “all these camera movements
  are too fast” was the first round’s note.
- **What rides a camera move moves smoothly.** Badges carried along a long zoom on the stepped clock
  juddered against the camera; their drift runs on the smooth clock, only their wobble stays stepped.
- **A slow sway is never seen:** the camera leaves a place ~1.5 s after it settles. Devices got a
  stepped wobble at 7–8 poses a second on a fixed edge (“wobble effect not visible”).
- **Dotted links** run centre to centre, draw on and draw off.
- **Numbers** use tabular figures; changing digits step on the number’s own clock (the SG film’s
  numbers kept changing while the typing sounded, and all locked as it stopped).

## 4 · The words

- **The voiceover’s words appear as they are spoken, one paper label per word**, one frame before the
  sound. They are the captions and part of the design at once.
- Their times are measured from the voice to a frame (`word_timings.py`: Whisper, then the audio
  decides). `check_sync.mjs` fails the build if a word is late or more than a frame early.
- Bottom-left, 80 px bold Roboto. A line over ten words splits at a sentence end; a unit holds 1.3 s
  after its last word; a dash in the script is a pause for the voice, never shown.
- Colour runs by phrase (`words.js`). The last line may land bigger; the sign-off line is the title,
  at the top of the sheet.

## 5 · Background drawings

- **Faint line drawings on the ground, each cued by a word:** a seismic line on “earthquake”, a swirl on
  “hurricane”, waves on “floods”, a burst on “armed conflict”, a clock on “every minute counts”,
  ripples, streaks for speed.
- **Drawn, not paper:** no cut edge, no shadow, one step darker than the dot grid; blue for the tool’s
  moments, red for questions no one can answer yet. They draw on and off on the stop-motion clock, and
  may keep moving smoothly while held — “subtle and smooth”.

## 6 · Sound

The rules are shared with every OCHA video: `ocha-video` → `references/sound-voice-music.md` (three
layers at constant levels, the voice on top; one thing appearing, one sound, on its frame). The kit’s
palette is the SG film’s, approved sound by sound: a card laid down for each badge, a laptop-style
error for a question mark, a “blop” for each graph, a soft tin tap for a blue icon, a paper flick for a
name label, a paper slide and a whoosh for a sheet, a shuffle of cards for a crowd, a chime flourish when
people turn blue — and beds for context: a distant storm, a siren far off, typing, people talking, a
clock, a radio, a truck.

## 7 · Never

A fade · a typewriter reveal for reading text (the words land as spoken) · photo collage · a drawn icon ·
an effect on the logo · real data in a wireframe · a bright red behind words · ducking in the mix.
