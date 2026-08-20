# Branding — the render contract

Burns OCHA elements onto a **finished** clip that is already at its final canvas size:
captions, the animated lower third, the location strip, text on screen, the logo watermark, a
footage look, and the OCHA logo-click ending.

Everything is rendered as transparent PNG layers via **cairosvg** and composited with **ffmpeg
overlay** — this Mac's ffmpeg has no libfreetype so `drawtext` is unavailable, and PNG layers
are the better approach anyway (pixel-accurate Raleway, per-format re-layout). See the
`ocha_quick_vid` repo's `docs/decisions.md`.

> **Rendering is canonical in QuickVid** (2026-07-12): `render_social_video.py` is a thin shim
> that runs `ocha_quick_vid/engine/social_brand.py` — captions, lower third (look B; numbers in
> `browser/brand-lt.json`) and the logo-click ending all come from the one engine
> implementation. Old job.json files keep working (`ending.logo` is translated automatically).
> One behaviour change: the old auto-detection of a black tail is gone — pass `footage_end`
> explicitly for legacy clips with black tails; clips ending on footage need nothing.

## The one command

```bash
REPO="~/OCHA DMU Dropbox/<your-name>/Design/Resources/ocha_quick_vid"
"$REPO/.venv/bin/python" ~/.claude/skills/ocha-video/scripts/render_social_video.py job.json
```

`job.json` is the whole spec. Copy `examples/venezuela_usg.job.json` and edit. The `.venv`
gives you cairosvg + PIL + faster-whisper; ffmpeg is `/opt/homebrew/bin/ffmpeg`.

## Workflow

1. **Get the clean clip + transcript.** The clip must already be cut and at final size. If
   there is an official transcript (docx), it is the authority for the words. For TIMINGS,
   scaffold cues:
   ```bash
   "$REPO/.venv/bin/python" ~/.claude/skills/ocha-video/scripts/transcribe.py CLEAN.mp4 en
   ```
   It prints `[start-end] text` per segment plus a paste-ready `"cues": [...]` block (segment
   START = cue start; the render derives each end = next start). faster-whisper "small"
   segments are already close to social caption size.
2. **Chunk and translate the cues.** Keep the timings, replace the text. Short chunks — one
   line, or two short lines. For UN/OCHA Spanish use the humanitarian register (glossary below).
3. **Fill `job.json`** — `src`, `out`, `canvas`, `footage_end`, `cues`, `lower_thirds`, `ending`.
4. **Render.** ~10s for a 70s 1:1 clip.
5. **Verify.** Extract frames (`ffmpeg -ss T -i out.mp4 -frames:v 1 f.png`), montage with PIL;
   check caption text and accents, the LT wipe, and that the ending logo has **no caption under
   it**. Check the click lands on the snap-on by reading the output audio envelope (RMS per
   0.05s window) around `footage_end`.

## job.json schema

```jsonc
{
  "src": "…/CLEAN.mp4",              // finished clip, already at final canvas size
  "out": "…/OUT.mp4",
  "canvas": [1080, 1080],            // optional; defaults to the source size
  "fps": 30,                         // optional; defaults to source
  "footage_end": 69.97,              // where footage cuts to black + last caption ends.
                                     //   omit → blackdetect near the end, else full duration
  "subtitle": {                      // all optional; these are the locked defaults
    "size": 44, "max_w": 800,
    "box": true, "box_color": "#3F3F3F", "opacity": 0.75, "radius": 16,  // box:false → clean: white text over an auto dark bottom-gradient scrim; tune with gradient_h_frac / gradient_opacity
    "pad": [22, 14], "line_h": 1.28, "weight": 500,
    "bottom_hi": 806,                // caption BOTTOM-y while a lower third is on screen (lifted)
    "bottom_lo": 900                 // caption BOTTOM-y otherwise
  },
  "lower_thirds": [                  // 0..n; each animates in once
    { "name": "TOM FLETCHER",
      "titles": ["UN Relief Chief", "Coordinador del Socorro de Emergencia de la ONU"], // 1 or 2 lines
      "align": "center",             // "center" or "left"
      "in": 1.2, "hold": 3.4,        // appears at `in`; full total ≈ 0.76 + hold + 0.64
      "bottom": 972,                 // block BOTTOM-y (center); default = canvas_h*0.90
      "left": 64,                    // block LEFT-x (left align only); default = canvas_w*0.06
      "name_size": 54, "org_size": 36 }   // OPTIONAL override; omit and the engine
                                     //   sizes off the short side (54/36 on 1080)
  ],
  "cues": [ [0.0, "text…"], [5.08, "text…"] ],   // [start, text]; end = next start (hard cut)

  "pins": [                          // top-left LOCATION STRIP (place + date), animated
    { "on": true, "place": "GENEVA", "date": "8 July 2026",
      "icon": true,                  // the map-pin icon; off → the text shifts left
      "color": "red",                // "red" (#ED1847) or "blue" (#004987)
      "start": 4.0, "duration": 5.0 }
  ],
  "texts": [                         // TEXT ON SCREEN — up to 3 lines that rise in/out
    { "lines": ["First line", "Second line"],
      "start": 1.0, "duration": 5.0,
      "gradient": 80 }               // % opacity of the readability band placed behind it
  ],                                 //   automatically; omit for the 80% default
  "bug": { "on": false },            // small OCHA logo watermark, top-right, whole clip
  "look": { "preset": "none", "phone_fix": false },   // footage grade, UNDER every overlay
  "rtl": true,                       // right-to-left for the WHOLE video; omit = auto-detect Arabic

  "ending": { "style": "over_footage",   // "over_footage" | "over_black" | "none"
              "at": 69.9,                // logo snap time; default = footage_end
              "hold": 2.0, "click": true,
              "logo_y_frac": 0.5 }       // over_footage only; 0.5 = centred (the standard)
}
```

> The `subtitle` numbers above are the raw engine defaults. For a real job prefer the
> **per-format** ones in `engine/statement.py` `PRESETS[<fmt>]["sub"]` — they carry the right
> size, wrap width and caption row for each canvas, and `sub_config()` scales them if you
> export larger. Legacy `"ending": {"logo": true}` still works (auto-translated).

Caption look per format is in `SKILL.md` §2 — it is a standard, not a per-job choice.

## Making a 9:16 reel from a square (the blurred-fill build)

Two ways to get a reel. Which one depends on **who it is for** and **how tall the source is** —
not on the look you happen to prefer:

- **Full-frame** — crop the original 9:16 and fill the screen. **The default** for the ASG and
  everyone else. Costs an upscale whenever the source is shorter than 1920: a 1920×1080 master
  gives a 608×1080 slice, i.e. ~1.8×.
- **Blurred fill** — the square at native size, centred, with a blurred copy filling the frame.
  Nothing is upscaled, so the picture stays sharp. **The USG's preference** and the locked OCHA
  look (approved 2026-07-16). [[reel-blurred-bg-standard]]

Locked blur recipe — 1080² in, 1080×1920 out. Do not retune it:

```
[0:v]split[bg][fg];
[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,
    boxblur=luma_radius=60:luma_power=3:chroma_radius=30:chroma_power=2[bgb];
[fg]scale=1080:1080[fgs];
[bgb][fgs]overlay=(W-w)/2:(H-h)/2,setsar=1
```

**Build order: square first, then derive, then brand at 1080×1920.** Blur the UNBRANDED square
cut, then run branding on the result — never inset an already-branded square, or the captions
end up scaled and stranded inside the inset.

**Positions map by the inset, not by the preset.** The sharp square occupies y **420…1500**, so
every approved square-space position shifts **+420**: a lower third at 860 becomes 1280,
captions at 980/1008 become 1400/1428. Do NOT reach for `PRESETS["reels"]` — those numbers
assume footage that fills the frame and will put the lower third somewhere nobody approved.
Captions still switch to **boxed**: it is a reel.

## Clean masters for translation

**Offer this, don't assume it** — same rule as the thumbnail. When a language team will add
their own captions:

- `cues: []` and `lower_thirds: []`. **Keep** the cut, the grade and the OCHA logo ending — the
  logo carries no text.
- Put them in `export/clean_for_translation/`, suffixed `_CLEAN`.
- Ship the cue list **twice**, on the exact timings, so the translation drops onto the same cue
  points instead of being re-timed: a `.srt` for subtitle software, and a plain numbered `.txt`
  with a blank target-language line under each source line for anyone who doesn't work with
  SRT. **No header and no instructions on the txt** — straight into caption 1 (Javi, 2026-08-20).

## Element rules (do not silently change these)

- **Fonts = Raleway.** cairosvg renders the right weight via fontconfig — `font-family="Raleway"`
  + `font-weight` 700→Bold, 600→SemiBold, 500→Medium (verified by glyph-width match; no
  `@font-face` needed). Name = Bold caps; titles and captions = Medium.
- **Captions HARD-CUT, never fade.** The overlay uses a half-open interval
  `enable='gte(t,s)*lt(t,e)'` — an instant swap between cues. Javi is explicit about this.
- **Punctuation: capital after a sentence end.** Cues are fragments of running speech; when one
  ends in `.`/`?`/`!` the NEXT must start with a capital (watch `y…` → `Y…`, Spanish's most
  common trap). Lowercase after a `:` or a mid-sentence comma is correct.
- **Lower third = the locked motion.** No fade; left-anchored wipe reveal; NAME reveals first,
  ORG follows and pans slightly; exit is the exact reverse; cubic ease-in-out. Ported from
  `engine/lower_third.py`. It MUST be a **PNG sequence** — ffmpeg `enable=` can only hard-cut,
  so a static overlay cannot animate. The script renders the sequence for you.
- **Lower third SIZE is automatic** — `brand-lt.json` sizes the name off the frame's **short
  side** (`geometry.name_short_ratio` 0.05), so a 1080-class canvas gets **name 54 / title 36**
  at every format, and a 4K export scales with it. Before 2026-08-20 it was a per-orientation
  ratio of canvas HEIGHT, which gave 31px on 4:5 and 44px on 9:16 — same width, no design
  reason. Leave `name_size` / `org_size` out of the job unless you mean to override.
  [[lower-third-too-small]] · [[lt-standard-b-compact]]
- **Caption ↔ lower third.** Captions **lift to `bottom_hi`** while a lower third is on screen
  and sit at `bottom_lo` otherwise. The script computes this per cue from the LT window.
- **Ending = the OCHA logo snaps on (no fade) and holds**, then the OCHA logo-click. Engine
  standard from `brand.json → ending.asset` ("OCHA Logo click.mov", click peak @0.30s):
  `atrim=0:0.7`, `adelay=(footage_end−0.30)·1000` so the peak lands on the snap-on,
  `amix inputs=2:duration=first:normalize=0` so speech stays at full level. **No caption under
  the logo** — all cues end by `footage_end`.
- **Location strip = the pin locator.** Top-left, animated in and out, place over date. Numbers
  in `browser/brand-pin.json`, logic in `engine/pin_locator.py`. Place-only is fine; date-only
  is not (it is dropped). RTL moves it to the top-RIGHT and the logo watermark takes the corner
  it vacates. [[ocha-pin-locator]]
- **Text on screen** is up to **3 lines**, with a soft readability band placed behind it
  automatically — never add your own scrim. `engine/text_on.py`.
- **RTL is ONE decision for the whole video**, not per element: the watermark has no text to
  detect from, and a mixed-language video must mirror as one layout. Auto-detected from any
  Arabic in the copy; `rtl` overrides. [[quickvid-arabic-rtl]]

## Showing what it will look like

Render ONE real frame through the real graph — never a mock-up:

```python
import sys; sys.path.insert(0, f"{REPO}/engine")
import brand_preview as bp
bp.render("/path/clip.mp4", 12.0, spec, "/tmp/preview.jpg", width=540)
```

It pulls a frame at that time, runs the production overlay graph over it and returns a JPEG.
~1s. This is how the square boxed-vs-clean question was settled, and how every position on the
WHD clip was approved.

## UN/OCHA Spanish glossary (from the Venezuela job — reuse for consistency)

- USG Tom Fletcher's title → **"Coordinador del Socorro de Emergencia de la ONU"** (the English
  strip stayed **"UN Relief Chief"** to match the client's reference; the formal English is
  "UN Emergency Relief Coordinator").
- recovery/search team → **equipo de rescate** · emergency worker → **rescatista**
- retrieve people from the rubble → **rescatar a las personas de entre los escombros**
- any evidence of their children → **algún rastro de sus hijos** (warmer than "evidencia")
- is help coming? → **¿viene la ayuda?**

## Not this file

- **Cutting** raw footage from a transcript → `engine/statement.py` (the QuickVid Edit path), or
  the web app's Edit tab.
- **Reframing** to another aspect ratio → the Premiere plugin's **Turn into a reel** tool
  (square and 4:5 get a blurred fill, landscape is cropped and each clip can be reframed). Do it
  BEFORE branding; this contract assumes the input is already at final size.

> Stale-path note (2026-08-06): `engine/cut.py`, `engine/run.py` and `engine/reframe.py` were
> once referenced here and no longer exist. If a path in this file does not resolve, check the
> repo before trusting it.
