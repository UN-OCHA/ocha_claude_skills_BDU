---
name: ocha-animation
description: >
  Motion craft for OCHA animated graphics and data films: smooth entrances and exits,
  transitions between scenes, timing and easing, counting numbers, animated charts and
  legends, seamless loops, and frame-accurate rendering to video. Use whenever the user
  asks to "animate" something, make a "motion graphic", an "animated chart" or "data
  animation", a "looping video for screens", an "explainer" or "top donors / funding"
  film, to "make this move", "add transitions", "fix the easing", "it looks jumpy / not
  smooth", "the exit looks odd", or to render an HTML/CSS animation to MP4. It covers HOW
  things move, not how they look: take colours, type and logos from `ocha-visual-identity`,
  chart rules from `ocha-dataviz`, and video branding, subtitles and packaging from
  `ocha-video`.
---

# OCHA Animation

How OCHA animated graphics should **move**. The look comes from the other OCHA skills; this
skill is about smoothness, sequencing, transitions and getting a frame-perfect file out.

Every rule here was learned the hard way on a real 75-second data film and corrected more
than once. Follow them by default; break one only when the user asks.

- `references/motion-rules.md` — every rule with the reason behind it, and a timing and
  easing table. **Read it before building any motion.**
- `references/review-workflow.md` — how to show work for approval and what to check before
  and after a render.
- `references/engine.md` — how to build an animation that renders frame-accurately.
- `scripts/motion.js` — drop-in helpers: reversible entrances and exits, counters, the marker
  highlight, the wipe-cover calculation.
- `scripts/render_frames.mjs` + `scripts/encode.sh` — capture every frame with headless
  Chrome, then encode with ffmpeg.

---

## 1 · The foundation: the page is a pure function of time

Build the animation as an HTML page with one function, `render(t)`, that sets **every**
animated property from the time `t` alone — no state carried between frames, no CSS
transitions, no `setTimeout` choreography. Then:

- `?t=12.5` freezes any instant, so stills for approval are exact frames of the film;
- the renderer seeks each frame and screenshots it, so the video can never drop or duplicate
  a frame, whatever the machine;
- the same input always produces the same file.

Details and the page contract are in `references/engine.md`.

## 2 · Motion rules (the short version)

1. **An exit is its entrance played backwards.** A scale-in leaves by scaling down, a rise by
   sinking, a wipe by un-wiping, a line that draws on draws off, a count counts back down.
   Never a generic fade-out.
2. **Text rises in, line by line.** Each line fades up on its own beat, about 0.12 s apart.
   No typewriter for reading text, no mask or wipe reveals on text or icons.
3. **Icons scale from their own anchor**, usually bottom centre, and the element's box must
   hug the icon — a full-width box makes it grow from empty space.
4. **Transform, don't replace.** A number that changes meaning slides into its new place and
   counts to its new value. A chart that carries across two phases is drawn once and changes
   in place.
5. **A chart arrives with its number.** The bar grows while the figure counts; a legend rises
   with the graphic it explains.
6. **Follow-ups arrive on a real moment**, for example when the bar is visibly half filled.
   Use an in-out ease for fills so the midpoint means something.
7. **Secondary text comes in early and fast** (sources, footers), so it never competes with
   the story.
8. **Nothing is left behind a transition.** Outgoing content is fully gone at the instant a
   wipe covers the frame. Calculate that instant from the wipe's own easing; never hand-set it.
9. **Loops are seamless.** The last frame equals the first. Persistent chrome (rules, labels)
   retracts in the reverse order it drew.
10. **One thing at a time.** Two elements arriving together compete; stagger them.

Durations, easings and distances: `references/motion-rules.md` §Timing.

## 3 · Legible on screens of unknown quality

Films run on meeting-room screens, projectors and laptops nobody has calibrated.

- **Contrast well above the minimum.** Aim for 7:1 for text greys, never under 4.5:1. Darken
  thin separator lines and "empty" states (unlit dots, empty bars) so they survive a washed-out
  projector.
- **Numbers in tabular figures** (`font-variant-numeric: tabular-nums`), so a counting value
  doesn't jitter sideways.
- **Marker highlights sit on the text, not on the box.** Measure the baseline and set the
  band's bottom edge 7% of the font size below it — flush reads stiff, a percentage of the
  element box drifts with line-height. `alignMarkers()` in `scripts/motion.js`.
- **Marks beside figures are superscripts**: ticks and alerts sit with their top level with
  the top of the figure.
- **Render at 1920×1080 by default. Offer 4K (3840×2160) only if the user finds HD not sharp
  enough** on their screens — it quadruples render time and file size.

## 4 · Workflow

1. **Script and storyboard as stills** before any motion — one frame per scene, approved.
2. **Build the motion**, following §2.
3. **Show stills for approval before any full render** — key frames, and frames just before,
   during and after every scene handover. Put them on one contact sheet.
4. **Check the data** if the film shows live figures: every statement still true, rankings
   unchanged since approval.
5. **Render**, then **verify frames pulled from the encoded file**, not from the page.

The checklist for each step: `references/review-workflow.md`.

---

## Project Owner
Javier Cueto, Head of Brand and Design Unit

## Maintained by
**OCHA Brand and Design Unit (BDU)**
- Team: ochavisual@un.org
- Focal point: Javier Cueto (cuetoj@un.org)
