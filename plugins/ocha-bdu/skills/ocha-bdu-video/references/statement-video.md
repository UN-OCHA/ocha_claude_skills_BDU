# Statement video — the pipeline

A short social video of a UN/OCHA **principal** (USG, ASG, Deputy, Director…) delivering
official remarks, cut from a long broadcast or a piece-to-camera recording.

Read this together with the house rules in `SKILL.md` — they are not repeated here.

> **The standard case is SELF-SERVICE in QuickVid** (since 2026-07-10): the app's **Edit tab →
> Statement clip** wizard runs this whole pipeline with the user clicking the choices (engine
> required — `ocha_quick_vid` repo, port 17870). **Point Javi or staff at the tool first.**
> Claude does it by hand when the job needs what the tool doesn't do: translated captions,
> room-cutaway inserts, bespoke editorial judgment, unusual formats, or the packaged 4-folder
> hand-off. The engine modules (`engine/webtv.py`, `engine/social_brand.py`,
> `engine/statement.py`) are the fastest building blocks for hand-driven jobs — prefer them
> over re-deriving ffmpeg by hand.

## Four flavours

- **Security Council briefing** — UN Web TV, SC chamber. Multi-camera broadcast (close ↔ wide).
- **Member-states briefing** — same, other UN rooms.
- **Noon briefing guest** — the principal joins the Spokesperson's noon briefing, usually
  **remote, on the screen in the briefing room**. Single podium camera plus room cutaways; the
  room is often half empty by then. (WHD, Aug 2026.)
- **Piece to camera (PTC)** — a message the principal recorded; Javi hands you the file.

## Statement-only default

**Location strip: NO.** The where and when goes in the post copy. Only add one if Javi asks.
(On a field film the opposite is true — there a location strip earns its place.)

---

## 1 · Get the source

- **SC / member-states / noon briefing** →
  `video_editing/tools/un-webtv-download.sh <webtv-url> floor 1080`. Floor = the principal's
  own voice.
  - **Same-day meeting:** the single-file MP4s aren't encoded yet, so pull the **live-DVR HLS**
    and use the **"Interlingua" (ina)** audio channel — that is the floor.
  - **Live streams mux audio into the video** (no separate `TYPE=AUDIO` track like a VOD) — the
    downloader must grab a single input, not try to mux a missing audio track.
  - **NOT a meeting:** the 24/7 live-channel page ("24 Hour Live and pre-recorded Programming")
    resolves to a rolling entry with a ~30s DVR window and a bogus 0-width MP4 flavor. Use the
    **meeting's own** page (its own title / `1_xxxx` entry). QuickVid detects this and refuses.
- **PTC** → Javi provides the file; skip the download.

Then run the two source checks in `SKILL.md` §5 (renditions, live picture area).

## 2 · Sync the audio

UN feeds often run the **audio a few frames ahead of picture** — invisible in a still, obvious
the moment lips move.

- Render a few 5-second candidates on a close-up with the audio nudged (±2f / ±3f / ±4f) and
  eyeball lip-sync. **Hand Javi the labelled candidates and let him pick** — this is a framing-
  sheet-style decision, not one to settle alone.
- Bake the chosen offset once:
  `ffmpeg -i in.mp4 -c:v copy -af "adelay=Nms|Nms" -c:a aac synced.mp4`.
  (Ukraine SC was **+0.133 s / +4 frames**.) All later timecodes are on this synced master.
- PTC recordings are usually already in sync — still spot-check.

## 3 · Locate and transcribe

Find the principal (the President or Spokesperson hands them the floor), then transcribe that
window with `scripts/transcribe.py` (faster-whisper, **word timestamps**) for precise cut
points. When a passage transcribes oddly, re-transcribe a narrow window around it in isolation
— a wide window can smear a word across a boundary.

## 4 · Script

Select the sentences that carry the message. If Javi supplies key messages or a statement doc,
they are the authority for priorities and exact words. Target the destination's length
(≈60–90s; longer if he asks). Keep his own words.

**Keep the selection chronological.** Never reorder passages to front-load a theme, however
much the brief asks for that theme up top. Javi is explicit: "don't put things that are from
the end before."

## 5 · Clean cut — this is the craft

Cut on the **words**, then hide each speech edit with a shot change. Portrait crops of the
feed's own shots:

- **Close-up** ≈ `crop=405:720:X:Y` (≈1.5×) · **general/medium** ≈ `crop=608:1080:X:Y` (full
  source height) · **wide/room** ≈ `crop=608:1080:470:0` — all `scale=<canvas>,setsar=1`.
  Centre each crop on the speaker.
- **Punch-in** = a hard cut between general and close on a speech edit — no motion, no
  transition, reads as a second camera. **Cut only on speech edits**; no gratuitous changes.
- **Punch-in spec: concentric, ~13% tighter.** Same centre as the wide, so nothing drifts
  sideways — a punch that also moves reads as a different camera. Under ~10% it reads as a
  wobble rather than a cut; much beyond ~20% is jarring on a talking head.
- **Follow the feed's own cuts** where you can — broadcasts cut between close and wide
  themselves, and those are free, motivated shot changes.
- **Consecutive sentences = ONE continuous take.** Keep the speaker's natural pauses; never
  re-cut inside continuous speech (per-sentence cuts read as bumps and rob the breathing).
  Punch in ONLY when jumping to a later passage (>~1.5s skipped), and prefix the resuming
  caption with **"[...]"** attached to the sentence, not standalone, so viewers see words were
  skipped. (ASG Yemen, Jul 2026.)
- **A room cutaway** breaks a long stretch — use it sparingly, once or twice.
- **A cutaway must sit inside ONE camera shot in the source.** Check for the feed's own cuts
  inside your chosen window, or your 2-second cutaway contains a camera change.
- **Watch what the room looks like.** A briefing room empties as the session runs on, and a
  late room shot can read as "nobody came". Not a hard no — a half-full room is often fine and
  it depends on the story — but in general avoid it, or crop tight enough that it doesn't read
  as empty.
- **Ending on a word: judge it on frames, not the waveform.** The mouth starts moving
  150–250 ms before the next word is audible, so cutting at the next word's audio onset already
  shows him starting to speak. Step through frames and take the last one where nothing has
  started.
- **Check the last frame of the ACTUAL render** — for a blink, for a half-closed eye.

### If Javi flags a noise

Not a routine step — only when he raises it. His description is usually enough to find it
("Steph turning a page, loudest around 11–12"). Treat only that window so nothing else moves:

```
highshelf=f=2800:g=-11:enable='between(t,10.20,14.65)'
```

for a broadband HF rustle in speech gaps. Then **verify the audio outside the window is
bit-identical** to before — if it isn't, the filter is wider than you think.

## 6 · Brand

→ `references/branding.md`. Captions (his words, chunked short, boxed or clean per
destination, lifting over the lower third while it's up), the lower third, the logo ending.

## 7 · Thumbnail

Offer it (see the defaults in `SKILL.md`). When yes: **9:16, 1080×1920, whatever shape the
video is** — it is an Instagram cover. Cut it from the **ORIGINAL broadcast frame**
(`crop=608:1080:X:0,scale=1080:1920`), never from a square or landscape export, which has no
width left to give. General framing, not zoomed; head in the **3:4** area; **mouth closed**; no
branding, captions or lower third. → `export/`. [[ocha-video-thumbnail]]

## 8 · Package

→ `SKILL.md` §7. `info/` also takes the transcript and any statement or key-message docs.

---

## Reference build

`…/ocha_quick_vid/video_editing/asg_sc_ukraine/` — the ASG Ratwatte Ukraine SC clip
(9 Jul 2026), portrait 1080×1920, 1:45. Its root `README.md` has the exact rebuild commands and
every timecode; its `assets/` has the recipe (`fg_v6_full.txt` + `branding_job.json`). Copy that
folder as the template.

Second reference, for the noon-briefing flavour and the square + blurred-reel pair: the WHD
Fletcher clip (19 Aug 2026) under `Projects/2026/OUSG/briefings/`.

## Other standing facts

- Broadcast sync: UN Web TV feeds usually need **+4 frames (133 ms)** audio delay — verify on
  lips, never assume.
- Fonts render as real Raleway via cairosvg. [[cairosvg-renders-real-raleway]]
- Caption preferences: [[javi-video-caption-preferences]]
- The omission marker `[...]` means sentences were removed, not that time passed.
  [[quickvid-omission-marker]]
