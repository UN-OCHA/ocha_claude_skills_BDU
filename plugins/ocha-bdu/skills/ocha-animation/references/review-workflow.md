# Review workflow

Render time is expensive and a full render hides mistakes in motion. Show exact frames,
get approval, then render once.

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
