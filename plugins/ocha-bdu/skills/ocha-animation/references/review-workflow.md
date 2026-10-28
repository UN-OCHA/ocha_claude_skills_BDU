# Review workflow

Render time is expensive and a full render hides mistakes in motion. Show exact frames,
get approval, then render once.

## Before showing anything: check it yourself

The person's review rounds are for taste. Mistakes that can be found without them should never
reach them.

1. **Run the automatic checks** on the page (each format, if there are several):

   ```bash
   node --experimental-websocket scripts/check_film.mjs --page film.html [--loop]
   # a vertical or square version: add --width 1080 --height 1920 (or 1080 1080)
   ```

   It seeks through the whole film and reports, as time windows: **text on text**, **text past
   the edge**, **settled type under 22 px**, with `--loop` a **loop seam** that pops, and
   **stills** of 3 s or more. Fix every error. A still is a question, not an error: a headline
   held to be read is fine, a stretch where nothing happens is not. Text that overlaps on purpose
   (a cloud of numbers, decorative shapes) gets a `data-check-skip` attribute in the page, so the
   report stays readable; mark only what is truly decoration.
2. **Critique the contact sheet.** Look at it as a reviewer would, scene by scene, and write down
   what is wrong before fixing anything:
   - text that is hard to read: too small, low contrast, on a busy background, cut by an edge;
   - two things arriving at once (rule 10), or a move with no reason to be there;
   - an element that slides with no easing, or an exit that is not its entrance reversed (rule 1);
   - type that looks soft or blurred because it was scaled up;
   - a scene where the eye does not know where to look first;
   - anything left behind a transition (rule 8).
3. **Fix the three worst**, re-run the checks, then build the sheet for approval. Say in a line what
   was found and fixed, so the person knows the sheet has been checked.

## Before any full render

- [ ] **Stills for approval on one contact sheet.** Key frames of every scene, fully settled,
      using `?t=` on the page. Label each with its time.
- [ ] **Handover frames.** For every scene change: just before, at the middle and just after.
      Check nothing is left behind a wipe (rule 8) and nothing pops.
- [ ] **Mid-move frames** for any new or changed move: halfway through an entrance and
      halfway through its exit. The exit must look like the entrance in reverse (rule 1).
- [ ] **Close-ups at true proportions.** Crop, never stretch, when judging a highlight, a mark
      or a line position — a resized crop distorts exactly what you are judging.
- [ ] **Measure, don't eyeball, alignment.** For marker highlights, probe the text baseline
      in the browser and report the offset in pixels (see `alignMarkers()`).
- [ ] **Contrast.** Compute the ratio for every grey used for text against its background and
      against any fill it sits on. Aim for 7:1.

## If the film shows live figures

- [ ] Pull the data fresh and state its date.
- [ ] Every statement still holds ("More than half", "More than $9B", a named rank).
- [ ] Rankings unchanged since the version that was approved; flag any change before
      rendering, never silently.
- [ ] Nothing changes a figure someone else supplied without asking.

## After the render

- [ ] Resolution and frame count as expected (`ffprobe`).
- [ ] **Pull frames from the encoded file** (`ffmpeg -ss T -frames:v 1`), not from the page, at
      the same times as the approval stills and at every handover.
- [ ] Look at them before sending.

## Showing work

- One contact sheet per question, options labelled A / B / C with what differs in words.
- Recommend one option and say why in a line.
- Previews live with the tooling, not with the deliverables.
- **Review rounds on renders go through the review tool** — comments pinned to exact frames, each
  answered with the version that fixed it: `ocha-video` → `references/review-tool.md`.
- **After a re-render, prove only the asked-for frames changed:** hash every frame against the previous
  render's; any other frame that differs is a finding, not noise.
