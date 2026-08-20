---
name: ocha-statement-video
description: >
  End-to-end process for an OCHA "statement video" — a short, branded social video of a UN/OCHA
  principal delivering official remarks. Four flavours: a UN Security Council briefing, a
  member-states briefing, a guest slot at the Spokesperson's noon briefing, or a
  piece-to-camera (PTC) video message. Use whenever Javi says
  "make a statement video", "make a statement clip" (the older name for the same thing),
  "cut the USG/ASG's Security Council briefing", "turn this UN Web TV
  briefing into a social clip", "clip this member-states briefing", "cut the noon briefing", "video message from
  [principal]", or hands over a webtv.un.org link / a piece-to-camera recording of an OCHA
  principal to turn into a captioned, OCHA-branded clip. Covers the full pipeline: download
  (UN Web TV) → sync audio → locate + transcribe → script → clean cut (punch-ins) → brand
  (captions + lower third + OCHA logo ending) → thumbnail → 4-folder package. Format + caption
  style depend on the DESTINATION. Runs fully local; the branding render is the
  `ocha-video-branding` skill. Reference build: the ASG Ukraine SC clip (July 2026).
---

# OCHA Statement Video

A short social video of a UN/OCHA **principal** (USG, ASG, Deputy, Director…) delivering official
remarks — cut from a long broadcast or a PTC recording into a captioned, OCHA‑branded clip.

> **The standard case is now SELF-SERVICE in QuickVid** (since 2026-07-10): the app's
> **Edit tab → Statement clip** wizard runs this whole pipeline with the user clicking the
> choices (engine required — `ocha_quick_vid` repo, port 17870). **Point Javi (or staff) to the
> tool first.** Claude does it by hand when the job needs what the tool doesn't do:
> **translated captions** (e.g. UN Spanish), room-cutaway inserts, bespoke editorial judgment,
> unusual formats, or the packaged 4-folder + README hand-off. The engine modules
> (`engine/webtv.py`, `engine/social_brand.py`, `engine/statement.py`) are also the fastest
> building blocks for hand-driven jobs — prefer them over re-deriving ffmpeg by hand.

**Three sources / flavours:**
- **SC briefing** — from UN Web TV (Security Council chamber). Multi-camera broadcast (close-up ↔ wide).
- **Member-states briefing** — same, other UN rooms.
- **Noon briefing guest** — the principal joins the Spokesperson's noon briefing, usually **remote,
  on the screen in the briefing room**. Single podium camera plus room cutaways; the room is often
  half empty by then. (WHD, Aug 2026.)
- **Piece to camera (PTC)** — a video message the principal recorded; Javi hands you the file (no download).

Everything runs locally with `ffmpeg` + `cairosvg` + `faster-whisper`. The footage never leaves the machine.

---

## Step 0 — destination first (it sets format + caption style)

**Always confirm the destination before rendering** — it drives two things:

| Deliverable / destination | Format (canvas) | Captions |
|---|---|---|
| **Social** — Reels / TikTok / Stories (default) | **9:16** 1080×1920 | **Boxed** (grey rounded box, Raleway) |
| Social — IG / FB feed | 4:5 1080×1350 | **Boxed** |
| Social — **square** post | **1:1** 1080×1080 | **Clean** — see the note below |
| **Event** — screening / a cleaner broadcast look | usually **16:9** 1920×1080 (landscape) | **Clean** — white text over a subtle **bottom gradient** |

Destination decides; if unsure, ask. In the `ocha-video-branding` job set `canvas` and
`subtitle.box`: `true` = boxed, `false` = clean (an auto dark bottom-gradient gives the
contrast — NEVER a text outline).

> **Square changed on 2026-08-06.** 1:1 used to be boxed; the video team's standard is
> **clean**, same as 16:9. Reels and 4:5 keep the box — that is the muted-scroll case it
> exists for. The web app and the plugin both apply this now; if any older note says square
> is boxed, it is stale.

---

## Standing defaults (Javi, 2026-08-19 / 08-20 — don't re-ask these)

| | Default | Notes |
|---|---|---|
| **Lower third for USG Tom Fletcher** | `TOM FLETCHER` / **`UN Relief Chief`** | The short form. Fits one line at every format; it is what a social audience recognises. Use it unless he names another title for a specific job. |
| **Location strip** | **NO** | Not on statement videos. The where/when goes in the post copy. Only add one if he asks for it. |
| **Approval** | **Unbranded cut FIRST** | Always send the plain cut — no captions, no lower third, no logo — and get the edit signed off before branding. Standard procedure, not a per-job question. |
| **Lower third SIZE** | square: **name 54 / title 36** on a 1080 canvas | The engine default (33 / 22) is too small for social — lower thirds have been coming out undersized. 54/36 keeps the standard 0.66 title-to-name ratio, so it is a clean scale-up, not a new proportion. Approved 2026-08-20. Until `brand-lt.json` is raised, set `name_size` / `org_size` explicitly in the job. |
| **Reel format** | **Full-frame 9:16** | The default for the ASG and everyone else. **The USG does not like full-size reels** — for his clips build the blurred-fill version instead (`ocha-video-branding`). Either way, if the source is only 1080 tall, say so up front: a full-frame 9:16 crop then costs a ~1.8× upscale, and blurred fill keeps the picture at native size. |
| **Thumbnail** | **Offer it — don't assume** | A standard deliverable, but ASK; it was declined on 2026-08-19. When yes: **1080×1920 even when the video is square**, because it is an Instagram COVER and covers are 9:16 there. Cut it from the ORIGINAL broadcast frame, never from a square export (which has no width left to give). |
| **Clean master for translation** | **Offer it — don't assume** | Same rule as the thumbnail. When yes, see "Clean masters" in `ocha-video-branding`. |
| **Vignette** | **YES — apply it by default** | Add `vignette` at the end of the video chain, at ffmpeg's default strength — a slight darkening of the corners so the face reads first. Approved as standard 2026-08-20. **Say in your report that it has been added**, so Javi knows it is there and can ask for it off; do not apply it silently. |

Still worth asking per job: the destination/format, the length, and anything about the
content itself.

---

## Before you cut: the framing sheet  (Javi, 2026-08-20 — a default step, not a fallback)

**Never render a cut before Javi has picked the framing.** The subject is rarely centred in
the broadcast frame and the right crop needs a human eye — this cannot be settled from a
rule or a preset.

Build ONE contact sheet showing **each shot type the edit will use** — wide, punch-in,
room/cutaway — with **two or three crop alternatives each**, side by side, clearly labelled
(A / B / C), and send it. He picks; then you build the cut.

- Label every panel and say what each option **costs** where it costs something — upscale
  factor, a caption safe-area risk, a person entering frame. An option sheet that hides the
  trade-off is worse than no sheet.
- Include a reference panel of the shot it will cut FROM, so the size change can be judged.
- Sample each option at a moment **later in the clip too** — a crop that frames him well at
  0:05 can be wrong at 0:50 once he has shifted in his seat.
- The same applies to the branding once the cut is approved: lower-third size and height,
  caption height, the drop while the LT is up — all decided from real rendered frames
  (`brand_preview`), never from preset numbers.

## The pipeline

### 1 · Get the source
- **SC / member-states** → `video_editing/tools/un-webtv-download.sh <webtv-url> floor 1080`.
  Floor = the principal's own voice. **Gotcha:** for a *same-day* meeting the single-file MP4s aren't
  encoded yet, so pull the **live-DVR HLS** and use the **"Interlingua" (ina)** audio channel = floor.
  (See the download tool + `ocha-video-branding` memory.)
  - **Live streams: audio is muxed into the video** (no separate `TYPE=AUDIO` track like a VOD) —
    the downloader must grab a single input, not try to mux a missing audio track.
  - **NOT a meeting:** the **24/7 live-channel** page ("24 Hour Live and pre-recorded Programming")
    resolves to a rolling entry with a ~30s DVR window and a bogus 0-width MP4 flavor — it is *not*
    a specific statement. Use the **meeting's own** webtv.un.org page (its own title / `1_xxxx` entry).
    QuickVid detects this by name and refuses with clear guidance.
- **PTC** → Javi provides the file; skip download.

**Two checks on the source before you promise a format or set a single crop:**
- **What renditions exist.** UN Web TV held only 1080/720/480 for the Aug 2026 noon briefing —
  there was no sharper master to re-cut from, which is exactly what makes a full-frame 9:16
  reel an upscale. Check first, then offer formats.
  ```python
  import sys; sys.path.insert(0, f"{REPO}/engine"); import webtv
  m = webtv.resolve(URL)
  fl = webtv._api("flavorasset/action/getByEntryId", ks=m["ks"], entryId=m["recorded"])
  sorted({(f.get("height"), f.get("width")) for f in fl if f.get("status") == 2}, reverse=True)
  ```
- **Where the live picture actually is.** Broadcast masters often carry dead black rows or
  columns at the frame edge — the UN Web TV noon briefing has **three dead rows at the bottom
  and one column at the right** of its 1920×1080. A crop that runs to the edge drags them in:
  barely visible along the bottom of a square, but a hard black line across the middle once
  that square is inset into a reel. Measure the live area once, then keep every crop inside it.
  ```python
  # first/last row and column whose mean brightness clears ~6
  ```

### 2 · Sync the audio  (broadcast feeds usually run ~2–4 frames off)
UN feeds often have the **audio a few frames ahead of picture**. Verify and correct — a slip is
invisible in a still but obvious the moment lips move:
- Render a few 5-sec candidates on a close-up with the audio nudged (±2f/±3f/±4f) and eyeball lip-sync.
- Bake the chosen offset once: `ffmpeg -i in.mp4 -c:v copy -af "adelay=Nms|Nms" -c:a aac synced.mp4`.
  (Ukraine SC was **+0.133 s / +4 frames**.) All later timecodes are on this synced master.
- PTC recordings are usually already in sync — still spot-check.

### 3 · Locate + transcribe
- For a broadcast, find the principal (the President hands them the floor). Transcribe the window with
  `ocha-video-branding/scripts/transcribe.py` (faster-whisper, **word timestamps**) → precise cut points.

### 4 · Script
- Select the sentences that carry the message. If Javi supplies key messages / a statement doc, they are
  authority for the priorities and the exact words. Target the destination's length (≈ 60–90 s; can run
  longer if he asks). Keep his own words.

### 5 · Clean cut  (this is the craft)
Cut on the **words**, then hide each speech-edit with a shot change. Portrait crops of the feed's OWN shots:
- **Close-up** ≈ `crop=405:720:X:Y` (≈1.5×), **general/medium** ≈ `crop=608:1080:X:Y` (full source height),
  **wide/room** ≈ `crop=608:1080:470:0` — all `scale=`canvas`,setsar=1`. Centre each crop on the speaker.
- **Punch-in** = cut between the general and the close on a speech-edit (no motion, no transition — a hard
  cut that reads as a second camera). **Cut only on speech edits** — don't add gratuitous shot changes.
- Broadcasts cut between close and wide themselves — **follow the feed's own cuts** where you can; they
  give free, motivated shot changes (e.g. the wide as the principal is introduced / finishes).
- A **wide room cutaway** breaks a long stretch — use it **sparingly** (once or twice).
- **No fade in / no fade out** — hard cut in and out (a few frames of handle if it feels abrupt).
- **Vignette by default.** Close the video chain with `vignette` (ffmpeg defaults — do not
  parameterise it unless asked). Standard on every statement video; **tell Javi it is on**.
  Colour grading is NOT standard: the WHD clip took `eq=saturation=0.85` because the face was
  over-saturated, but that was a per-job call, so leave saturation alone unless he raises it.
  ```
  [vcat]vignette[v];                       # standard
  [vcat]eq=saturation=0.85,vignette[v];    # only when he asks for a grade too
  ```
  The **Premiere plugin** has a vignette element of its own (a MOGRT, with a Strength knob) —
  use that one when the job is being cut in Premiere. The **web app engine has no vignette
  yet**, so a web-app job cannot add one; that gap is a known backlog item.
- **Deliver an unbranded cut first for approval, then branding** — standing procedure, always,
  not a per-job question (Javi, 2026-08-19).
- Frame-accurate cuts: build the whole cut in ONE `ffmpeg` filtergraph (`concat` filter) — a stream-copy
  concat of separate clips can silently truncate. See the reference `fg_v6_full.txt`.

**Rules that cost us a round trip each (WHD noon briefing, Aug 2026):**
- **Keep the selection chronological.** Never reorder passages to front-load a theme, however
  much the brief asks for that theme up top. Javi is explicit: "don't put things that are from
  the end before."
- **Every shot-size change lands on a real edit.** A punch-in starts ON a speech edit or a
  camera cut and **holds until the next one**. Returning to wide in the middle of a continuous
  shot is unmotivated — nothing justifies it, so it reads as a mistake, not as an edit. If the
  block between two edits is 25 seconds, stay in the punch-in for 25 seconds.
- **Punch-in spec: concentric, ~13% tighter.** Same centre as the wide, so nothing drifts
  sideways — a punch that also moves reads as a different camera. Under ~10% it reads as a
  wobble rather than a cut; much more than ~20% is jarring on a talking head.
- **A cutaway must sit inside ONE camera shot in the source.** Check for the feed's own cuts
  inside your chosen window, or your 2-second cutaway contains a camera change.
- **Watch what the room looks like.** A briefing room empties as the session runs on, and a
  late room shot can read as "nobody came". Not a hard no — a half-full room is often fine and
  it depends on the story — but in general avoid it, or crop tight enough that it does not read
  as empty.
- **Ending on a word: judge it on frames, not the waveform.** The mouth starts moving
  150–250 ms before the next word is audible, so cutting at the next word's audio onset already
  shows him starting to speak. Step through frames and take the last one where nothing has
  started.
- **Check the last frame of the ACTUAL render** — for a blink, for a half-closed eye. Twice on
  this job the fix was half a second.
- **Duration bookkeeping.** The video chain total and the audio `apad=whole_dur` must match. If
  you shorten the ending, change BOTH — otherwise the file ends on a frozen frame or a black
  tail and nothing warns you. Verify with `ffprobe` on the export, not on the recipe.

**If Javi flags a noise** (not a routine step — only when he raises it):
Work from his description, which is usually enough to find it ("Steph turning a page, loudest
around 11–12"). Treat only that window so nothing else is touched:
`highshelf=f=2800:g=-11:enable='between(t,10.20,14.65)'` for a broadband HF rustle in speech
gaps. Then **verify the audio outside the window is bit-identical** to before — if it is not,
the filter is wider than you think.

### 6 · Brand  (→ the `ocha-video-branding` skill)
Fill a `job.json` and run `render_social_video.py`:
- **Captions** — his words, chunked short; **boxed or no-box** per destination; they **lift** above the
  lower third while it's up.
- **Lower third** — OCHA style, centred (or left), name + short title (e.g. "UN Relief Chief").
- **Logo ending** — OCHA logo over footage (the principal's face, or a general/room shot) or over black;
  **NEVER a scrim/layer behind the logo**; modest, centred; **snap on (no fade) + the OCHA click** on the
  snap; logo **rasterized from the SVG** at render time.

### 7 · Thumbnail
Always make one (standard — see the defaults above). **9:16, 1080×1920, whatever shape the video
is**: it is an Instagram cover. Cut it from the **ORIGINAL broadcast frame**
(`crop=608:1080:X:0,scale=1080:1920`), NOT from a square/landscape export, which has no width left
to give. **General framing (not zoomed)**, subject's head in the **3:4** area, **mouth closed**,
**no branding/captions/lower third** → into `export/`.

### 8 · Package into 4 folders + root README
```
export/   final video + thumbnail
info/     transcript (+ statement / key-message docs)
source/   the FULL original, audio-synced
assets/   render scripts (copied from the skill), the exact recipe (fg + job.json), logo SVG,
          word timings, reference stills, the download tool
README.md (root) — what it is, the layout, how it was made (commands + timecodes), and how to
          prompt an AI agent to edit it
```
Do the moves/deletes in Python (allowlisted) to avoid the bash rm-guard; delete regenerable
intermediates. Convert relative dates to absolute in the README.

---

## House rules (non-negotiable)
- No fade in/out ([[no-fade-in-out-on-videos]]). · Cut only on speech edits; punch-in to hide them.
- **Consecutive sentences = ONE continuous take** — keep the speaker's natural pauses; never re-cut
  inside continuous speech (per-sentence cuts read as bumps and rob the breathing). Punch-in ONLY when
  jumping to a later passage (>~1.5s skipped), and prefix the resuming caption with **"[...]"**
  (attached to the sentence, not standalone) so viewers see words were skipped. (ASG Yemen, Jul 2026.)
- Logo ending: no layer behind the logo; modest (**0.055·H**, clear of the face); snap + click; from SVG
  ([[ocha-ending-logo-rules]], [[logos-always-svg]]). **Ending tail:** footage keeps rolling under the
  logo but the sound **fades to mute** right after the last kept word — the next speaker in the room is
  never heard. If the principal closes with "I thank you", keep it so it's heard.
- Captions: Raleway; **boxed** (grey rounded box) for social/feed, **no-box** (plain white over a subtle
  bottom gradient) for events — per destination ([[javi-video-caption-preferences]]).
- Captions carry the **exact words SAID** (transcript) — never the speechwriter script (principals
  deviate); the script only chooses WHICH sentences. **Max 2 lines**, balanced wrap (no orphan word),
  fuller blocks held ~2.5–5s. Constant caption height when the canvas has room (reels/4:5); lift over
  the LT only where they truly collide (square/event).
- Broadcast sync: UN Web TV feeds usually need **+4 frames (133 ms) audio delay** — verify on lips.
- Fonts render as real Raleway via cairosvg ([[cairosvg-renders-real-raleway]]).
- 4-folder package + root README ([[video-job-folder-structure]]); export/ holds the finals
  ([[always-export-folder-for-finals]]); thumbnail spec ([[ocha-video-thumbnail]]).
- Video stays local — never upload. After building any new function/standard, update the docs + this
  skill + memory ([[keep-video-editing-docs-updated]]).

## Reference build
`…/ocha_quick_vid/video_editing/asg_sc_ukraine/` — the ASG Ratwatte Ukraine SC clip (9 Jul 2026),
portrait 1080×1920, 1:45. Its root `README.md` has the exact rebuild commands + every timecode; its
`assets/` has the recipe (`fg_v6_full.txt` + `branding_job.json`). Copy that folder as the template.

## Beyond captions + lower third

The branding step can also place, in the same pass: the **location strip** (top-left place +
date), **text on screen** (up to 3 lines, readability band added automatically), the **OCHA
logo watermark**, and a **footage look**. A location strip earns its place on a briefing clip
— it says where and when without spending a caption on it. Full spec in the
`ocha-video-branding` skill.

## Doing it without Claude

If Javi (or a colleague) wants to run one of these themselves, the **QuickVid web app**
(`un-ocha.github.io/quickvid_BDU`) does the whole Edit path — transcribe, pick the sentences,
cut, brand — with previews of each element on their own footage. Same engine, same output.
This skill is the version where Claude does the craft: the scripting, the punch-in choices
and the packaging.

## Components this skill pulls together
- **Download:** `video_editing/tools/un-webtv-download.sh`
- **Branding renderer:** `ocha-video-branding` skill (`render_social_video.py` + `transcribe.py`)
- **Brand assets:** the `ocha_quick_vid` repo — OCHA logo SVGs (`assets/`), the click .mov + `brand.json`,
  Raleway at `/Library/Fonts/Raleway/static/`.

— OCHA Brand and Design Unit (BDU) · ochavisual@un.org
