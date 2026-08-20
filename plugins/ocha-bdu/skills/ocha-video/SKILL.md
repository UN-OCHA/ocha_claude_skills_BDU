---
name: ocha-video
description: >
  Everything OCHA video: cutting, branding and packaging any video for OCHA. Use whenever
  Javi hands over footage or a webtv.un.org link, or asks to "brand this clip", "add
  subtitles/captions", "burn in subtitles", "translate this video's subtitles" (any language),
  "add a lower third / name strip", "add a location strip / pin", "add text on screen", "add
  the OCHA logo / ending / click", "make a reel version of this square", "give me a clean
  version for translation", "make a statement video" (or the older "statement clip"), "cut the
  USG/ASG's Security Council briefing", "clip this member-states briefing", "cut the noon
  briefing", "video message from [principal]", or wants a bespoke piece cut — a mission wrap-up,
  a field film, an event recap. Carries the house rules that hold for EVERY OCHA video (no
  fades, vignette, ending logo, caption standard per format, approval flow, 4-folder package)
  and routes to the deep procedure for the job in hand. Runs fully local (ffmpeg + cairosvg/resvg
  + faster-whisper); footage never leaves the Mac.
---

# OCHA Video

One skill for any OCHA video job. This file holds what is true **every time**; the deep
procedure for a particular kind of job lives in `references/` and is read on demand.

Everything runs locally with `ffmpeg` + `cairosvg`/`resvg` + `faster-whisper`. **The footage
never leaves the machine.**

---

## 1 · What kind of video is this?

Ask (or infer) before anything else, because it decides which reference you open:

| The job | What to do |
|---|---|
| **A statement** — a principal delivering official remarks: Security Council, member-states briefing, a guest slot at the Spokesperson's noon briefing, or a piece to camera | Read **`references/statement-video.md`**. It has the whole pipeline: UN Web TV download, audio sync, transcribe, script, word-driven cutting with punch-ins. |
| **A bespoke piece** — mission wrap-up, field film, event recap, anything assembled from several clips | **No recipe, and don't invent one.** Every one is different. Use the rules on this page, build the edit to the material, and check `references/bespoke-edits.md` for the mechanics of multi-clip assembly. |
| **Branding only** — the clip is already cut and at final size | Read **`references/branding.md`**: the one command, the `job.json` schema, every element. |
| **A reel from a finished square** | `references/branding.md` → "Making a 9:16 reel from a square". |

A statement job needs the statement reference **and** the branding one. Most jobs end in
branding, whatever the front half was.

### Should Claude be doing this at all?

| Route | Use it when |
|---|---|
| **QuickVid web app** (`un-ocha.github.io/quickvid_BDU`) | A colleague is doing it themselves, or it is a standard job. GUI, no code, previews each element on their own footage. Also cuts from a transcript. |
| **Premiere plugin** (OCHA QuickVid panel) | The video is already being edited in Premiere, or it needs real editorial craft. Places the same elements as live MOGRTs. |
| **This skill** | Claude does the craft: bespoke jobs, translated captions, odd formats, batch runs, the packaged hand-off. |

Same engine in all three, so the output is identical. If someone asks "how do I do this
myself", point them at the web app.

---

## 2 · Destination first — it sets format and caption style

**Confirm the destination before rendering anything.**

| Deliverable / destination | Format (canvas) | Captions |
|---|---|---|
| **Social** — Reels / TikTok / Stories (default) | **9:16** 1080×1920 | **Boxed** (grey rounded box, Raleway) |
| Social — IG / FB feed | 4:5 1080×1350 | **Boxed** |
| Social — **square** post | **1:1** 1080×1080 | **Clean** |
| **Event** — screening, cleaner broadcast look | **16:9** 1920×1080 | **Clean** — white over a soft bottom gradient |

In the job set `canvas` and `subtitle.box`: `true` = boxed, `false` = clean (an auto dark
bottom-gradient gives the contrast — **never** a text outline).

> **Square moved to clean on 2026-08-06** — the video team's standard, not a preference. The
> box exists for muted scrolling feeds, which is why reels and 4:5 keep it. The web app
> (`OchaCaptions.styleFor()`) and the engine (`PRESETS[*].sub.box`) both apply this; if you
> change it, change both. Anything that still says square is boxed is stale.

---

## 3 · Standing defaults — don't re-ask these

| | Default | Notes |
|---|---|---|
| **Approval** | **Unbranded cut FIRST** | Always send the plain cut — no captions, no lower third, no logo — and get the edit signed off before branding. Standing procedure, not a per-job question. |
| **Vignette** | **YES — apply it by default** | Close the video chain with `vignette` at ffmpeg's default strength, so the face reads first. Standard since 2026-08-20. **Say in your report that it has been added** — never apply it silently. Colour grading is NOT a default: leave saturation alone unless Javi raises it. |
| **Lower third for USG Tom Fletcher** | `TOM FLETCHER` / **`UN Relief Chief`** | The short form. Fits one line at every format and is what a social audience recognises. Use it unless he names another title. |
| **Lower third SIZE** | **automatic — name 54 / title 36** on any 1080-class canvas | Fixed at source 2026-08-20: `brand-lt.json` now sizes the name off the frame's **short side** (`name_short_ratio` 0.05) instead of a per-orientation ratio of its height, so every format gets the same reading size. No `name_size` / `org_size` in the job unless you deliberately want to override. [[lower-third-too-small]] |
| **Reel format** | **Full-frame 9:16** | The default for the ASG and everyone else. **The USG does not like full-size reels** — build him the blurred fill instead. Either way, if the source is only 1080 tall say so up front: full-frame then costs a ~1.8× upscale. |
| **Thumbnail** | **Offer it — don't assume** | A standard deliverable, but ASK. When yes: **1080×1920 even when the video is square** (it is an Instagram cover), cut from the ORIGINAL frame, general framing, head in the 3:4 area, mouth closed, no branding. |
| **Clean master for translation** | **Offer it — don't assume** | Same rule as the thumbnail. Spec in `references/branding.md`. |

Still worth asking per job: destination and format, length, and anything about the content.

---

## 4 · How we work with Javi

- **Show a framing sheet before you render a cut.** Each shot type the edit will use, with
  two or three crop alternatives each, side by side, labelled A / B / C. The subject is
  rarely centred in the frame and the right crop needs a human eye — it cannot be settled
  from a rule. He picks, then you build.
- **Every option sheet states what each option costs** where it costs something: upscale
  factor, a caption landing under the platform's UI, a person entering frame. A sheet that
  hides the trade-off is worse than no sheet.
- **Sample options at more than one moment** — a crop that frames him well at 0:05 can be
  wrong at 0:50 once he has shifted in his seat.
- **Positions come from a real rendered frame, never from a preset.** Lower-third size and
  height, caption height, the drop while the LT is up — all of it decided on stills of the
  actual footage (`brand_preview`, in `references/branding.md`).
- **Verify the export, not the recipe.** Check the finished file with `ffprobe` and by
  looking at real frames — especially the last one.

---

## 5 · Before you touch the source

- **What renditions exist**, before promising a format. UN Web TV held only 1080/720/480 for
  the Aug 2026 noon briefing, which is exactly what made a full-frame 9:16 reel an upscale.
  ```python
  import sys; sys.path.insert(0, f"{REPO}/engine"); import webtv
  m = webtv.resolve(URL)
  fl = webtv._api("flavorasset/action/getByEntryId", ks=m["ks"], entryId=m["recorded"])
  sorted({(f.get("height"), f.get("width")) for f in fl if f.get("status") == 2}, reverse=True)
  ```
- **Where the live picture actually is**, before setting a single crop. Broadcast masters
  often carry dead black rows or columns at the frame edge — the UN Web TV noon briefing has
  **three dead rows at the bottom and one column at the right** of its 1920×1080. A crop that
  runs to the edge drags them in: barely visible along the bottom of a square, a hard black
  line across the middle once that square is inset into a reel. Measure the live area once
  (first and last row/column whose mean brightness clears ~6), then keep every crop inside it.

---

## 6 · House rules for any OCHA video

**Cutting**
- **No fade in, no fade out** — hard cut both ends (a few frames of handle if it feels
  abrupt). [[no-fade-in-out-on-videos]]
- **Build the whole cut in ONE ffmpeg filtergraph** (`concat` filter). A stream-copy concat of
  separate clips can silently truncate.
- **Duration bookkeeping.** The video chain total and the audio `apad=whole_dur` must match.
  Shorten the ending and you change BOTH — otherwise the file ends on a frozen frame or a
  black tail and nothing warns you.
- **Every shot-size change lands on a real edit** — a speech edit or a camera cut — and holds
  until the next one. Changing size in the middle of a continuous shot is unmotivated and
  reads as a mistake.
- **Vignette closes the chain**, at ffmpeg's defaults — do not parameterise it unless asked:
  ```
  [vcat]vignette[v];                       # standard
  [vcat]eq=saturation=0.85,vignette[v];    # only when he asks for a grade too
  ```
  The **Premiere plugin** has a vignette element of its own (a MOGRT with a Strength knob) —
  use that when the job is being cut in Premiere. The **web app engine has no vignette yet**,
  so a web-app job cannot add one: a known backlog item, and worth saying out loud if a
  colleague asks why their own export looks different.

**Branding**
- **Captions carry the exact words SAID**, from the transcript — never the speechwriter
  script; principals deviate. **Max 2 lines**, balanced wrap with no orphan word, fuller
  blocks held ~2.5–5s. Captions **hard-cut, never fade**.
- **Ending = OCHA logo over footage or black**: modest (**0.055·H**), centred, clear of the
  face, **snap on with no fade**, plus the OCHA click on the snap, **never a scrim or layer
  behind it**. [[ocha-ending-logo-rules]]
- **Ending tail:** footage keeps rolling under the logo but the sound **fades to mute** right
  after the last kept word — the next speaker in the room is never heard. If the principal
  closes with "I thank you", keep it so it is heard.
- **Logos are always SVG**, rasterised at render time. Never ship a PNG. [[logos-always-svg]]
- **NEVER re-implement a branding element.** Every number lives in the engine and in
  `browser/brand-lt.json` / `brand-pin.json`. Do not redraw one in SVG/HTML/CSS to "preview"
  it either — render a real still. Two implementations of one element have already drifted.

**Always**
- Video stays local — never upload.
- Curly quotes and apostrophes in caption text and in anything written for a human.
- After building any new function or standard, update this skill + `docs/decisions.md` +
  memory. [[keep-video-editing-docs-updated]]

---

## 7 · Package: four folders + a root README

```
export/   the finished videos (+ thumbnail, + clean_for_translation/ if made)
info/     transcript, statement or key-message docs, the sheets used for approvals
source/   the FULL original, audio-synced
assets/   the exact recipe (filtergraph + job.json), word timings, reference stills
README.md what it is, the layout, how it was made (commands + timecodes), what was learned
```

[[video-job-folder-structure]] · [[always-export-folder-for-finals]]. Do moves and deletes in
Python to avoid the bash rm-guard; delete regenerable intermediates. Convert relative dates to
absolute in the README.

---

## References

- **`references/statement-video.md`** — the statement pipeline, end to end.
- **`references/branding.md`** — the render contract: one command, `job.json` schema, every
  element, the blurred-fill reel, clean masters, Spanish glossary.
- **`references/bespoke-edits.md`** — multi-clip assembly for mission films and recaps.

## Assets

- QuickVid repo (`brand_repo` in the render config, default path baked in):
  `brand/brand.json` → `ending.asset` (the click .mov);
  `assets/OCHA_logo_horizontal_white.svg`; Raleway at `/Library/Fonts/Raleway/static/`.
- Download tool: `video_editing/tools/un-webtv-download.sh` in the same repo.
- Scripts ship with this skill: `scripts/render_social_video.py`, `scripts/transcribe.py`.

— OCHA Brand and Design Unit (BDU) · ochavisual@un.org
