---
name: web-motion
description: >
  Motion and interaction for websites and web apps: how screens arrive and leave, swipes and
  gestures, press feedback, values that settle, sheets, menus and overlays, timers and sounds,
  reduced motion, and the iPhone and installed-app (PWA) quirks that break all of these. A small
  motion system with tested values, learned the hard way building a production workout app. Use
  whenever building or fixing interaction in a web app or site, OCHA or personal: "add a
  transition", "make it feel like an iPhone", "it feels abrupt / slippery / jumpy / janky",
  "swipe between pages", "carousel", "drag", "bottom sheet", "modal animation", "press state",
  "tap feedback", "animate the number", "countdown", "timer ring", "sound on iPhone", "reduce
  motion", "PWA", "iOS Safari", "home screen app", "scroll bar flashes", "the page scrolls
  sideways", "smooth scroll", "anchor link", "jump to section", "page load animation", "fade in
  on load", "skeleton loader". For landing-page choreography and scroll-linked effects use `hallmark`; for films
  rendered to video use `ocha-animation`; for colours, type and OCHA components use
  `ocha-visual-identity`.
---

# Web motion and interaction

Motion in an app is not decoration. It tells people where they came from, where they went and
that their tap landed. Get it wrong and the app feels **abrupt** (things jump), **slippery**
(things fly off) or **sickly** (too much travel). Get it right and nobody notices it.

This skill is one small system plus the lessons behind it. Use the system as it is; don’t invent
new durations or curves. The code is in `references/recipes.md`, the iPhone and installed-app
traps are in `references/ios-and-pwa.md`.

---

## 1. The system: three durations, three distances, three curves

```css
:root {
  --dur-press:   120ms;  /* a press answers */
  --dur-leave:   180ms;  /* anything leaving; crossfades, backdrops */
  --dur-enter:   320ms;  /* anything arriving; layers rising; a value settling */
  --dur-release: 260ms;  /* a dragged page finishing its move after the finger lifts */

  --move-page:  16%;     /* a whole screen's travel */
  --move-step:  10%;     /* a step inside a flow: dense screens, less travel */
  --move-layer: 24px;    /* a layer rises this far, and sinks back half of it */

  --ease-enter: cubic-bezier(0.05, 0.7, 0.1, 1);  /* every arrival: gentle start, soft landing */
  --ease-out:   cubic-bezier(0.22, 1, 0.36, 1);   /* responses to the finger: presses, drag release, menus, toasts */
  --ease-in:    cubic-bezier(0.55, 0, 1, 0.45);   /* exits */
}
```

- **Leaving is faster than arriving.** People wait for what comes, not for what goes.
- **Arrivals use `--ease-enter`, never `--ease-out`.** `--ease-out` covers 80% of the distance in
  its first 90ms, so an arriving screen reads as a snap and then a crawl, which people described
  as “speedy” and “bumpy”.
- **Travel little.** A screen moves 16% of its width, not 100%. That’s enough to say “from the
  right” without the whole world sliding past, which is what causes motion sickness.
- **Never a bounce or an overshoot on UI, and never the browser’s default `ease`.** The one
  exception is a value settling (§4), which grows to 1.12 and comes back.
- **Nothing moves on its own.** Motion answers something the person did.
- **Declare every token you use.** An undeclared `var()` voids the whole declaration without any
  error, and the move just doesn’t happen.

## 2. Which move for which change

| What happens | Move |
|---|---|
| Going **deeper** (list → item) | New screen arrives from the right, `--move-page`, `--dur-enter` |
| Going **back** | Arrives from the left |
| A **sibling** at the same depth (tab to tab), or the first screen | Crossfade, `--dur-leave` |
| A **step** inside a flow (next exercise, next question) | Same as deeper/back but `--move-step`; only the body moves: the header and progress bar stay still, so it reads as one place |
| A **layer** (sheet, preview, pause screen) opens | Rises `--move-layer` and fades in, `--dur-enter` |
| A layer **closes** | Sinks half as far and fades out, `--dur-leave`, `--ease-in` |
| A **menu** opens | Drops from its anchor: from `translateY(-8px) scale(.98)`, `transform-origin` at the anchor |
| A **value** changes (±, +30 sec, reset, a count ends) | Settles: scale to 1.12 at 40%, back, `--dur-enter` |
| A swipe already moved the page | Nothing more: the gesture owns that move |

Write the depth of each screen down once (a small route map) and let one function pick the move.
Don’t decide per screen.

### When a page or its content loads

Google’s Material 3 transitions are the reference here, and they agree with the rules above.

- **A page whose content is already there appears as it is.** No fade-in on load, no elements
  rising one by one. Hiding content until a script runs delays what people came for, and leaves a
  blank page when the script fails. Staggered reveals on scroll are a marketing-site habit, not
  a standard; use them only when someone asks for them.
- **Content that arrives later** (fetched data, a slow image) gets a **skeleton** if the wait can
  pass ~300ms: grey shapes where the content will sit, at its real size, with a subtle pulse that
  runs from the top left to the bottom right. Under reduced motion the skeleton stays still.
- **When it’s ready, the content fades in over the skeleton,** all at once: opacity only, no
  movement, `--dur-leave`. Reserve the space first (`width` and `height` on every image), so
  nothing shifts.
- Code: `references/recipes.md` § 10.

## 3. Presses

- **Answer in the first frame.** `:active` with `transform: scale(.97)` over `--dur-press`.
  Cards press more gently, **`.985`**: a card is big, so `.97` looks like it jumped.
- **No hover styles on touch screens.** `:hover` stays stuck after a tap. Put every hover rule
  in one `@media (hover: hover) and (pointer: fine)` block.
- **Confirm the main action before moving on.** On “Done”, settle its ✓, wait **110ms** (under the
  point where a tap feels delayed), then move. Block a second tap while it’s busy, or a double
  tap skips two steps.
- **Hit targets:** 44px is the floor. Controls hit mid-task get more (52px). If the icon must
  stay small, grow the hit area with an `::after`, not the icon.
- Wrap press rules in `:where()` so components can still override them.

## 4. Values that change

- **Settle the value** that changed (see `bump()` in the recipes). A transform does nothing to an
  inline element, so give an inline `<span>` `display: inline-block` for the length of the settle.
- **Count up in steps, then settle** (18 steps × 40ms), not a long tween.
- **Timers run on the wall clock,** not by adding up `setTimeout`s: store the deadline, redraw
  every 100ms, re-read the clock on `visibilitychange`. On pause keep the time left; on resume
  move the deadline. Skip the cues a frozen phone missed; don’t play them late.
- **Ring timers:** move `stroke-dashoffset` once a second with a `.95s linear` transition, for a
  continuous sweep. When a new interval starts, reset the ring with the transition switched off
  for one frame, or it visibly refills backwards.
- **Digits:** `font-variant-numeric: tabular-nums`, so they don’t jitter. `role="timer"`, and no
  `aria-live` on the app, or a screen reader reads every second.

## 5. Swipes and gestures

The full, working pager is in `references/recipes.md`. The rules it follows:

- **Decide the direction once, then commit.** After 8px of movement, the drag is sideways if
  `|dx| > |dy| × 1.3`. From then on, `preventDefault()` in a **non-passive** `touchmove`, so the
  page can’t also scroll a few pixels (a finger is never level: the scroll bar flashes). Set
  `touch-action: pan-y` on the element.
- **Distance, not speed: 80px.** A flick that doesn’t travel doesn’t count. This matched an
  earlier swipe app people already knew, and matching what users know beat a cleverer version.
- **Resist where there’s nowhere to go:** the page follows at a quarter of the finger (`dx / 4`)
  and settles back.
- **Carousel, not a fade.** The next page is already there beside the current one, 16px away, as
  an inert copy built by the same code as the real page. On release the page slides one width
  plus the gap, so the copy lands exactly where the real page renders; then swap in the real one
  without animating again.
- **The inert copy must be invisible to the live code:** strip `id`, `for`, `aria-controls` and
  `data-*`, and set `inert` and `aria-hidden`.
- **A drag never also taps** what it started on: a capture-phase `click` guard cancels the click
  when the drag was sideways. Then a swipe can start anywhere, on images and buttons included
  (`-webkit-touch-callout: none; -webkit-user-drag: none` on images).
- **Arrows and swipes share one motion:** the buttons call the same `go(dir)`.
- **Keep it for moving between pages.** A swipe between steps of a task (next exercise) was built
  with tilt, fly-out and a peek underneath, and removed: “messy, let’s keep it simple”. Buttons
  won.

## 6. Layers: sheets, previews, menus

- **One overlay function** gives every layer the dialog role, `aria-modal`, Escape to close, and
  focus back to what opened it. Don’t hand-roll a second one.
- **Focus the layer itself, not its first button,** with `{ focusVisible: false }`. Focusing
  “Close” draws a focus ring on it the first time on iPhone.
- **Guard against closing twice** (a `closing` flag).
- **Sheets:** add the “in” class inside a `requestAnimationFrame` so the start state paints; the
  backdrop fades over `--dur-leave`, the sheet rises from `translateY(24px)`. Remove it after the
  leave finishes. A tap on the backdrop cancels; a destructive choice gets focus on the **safe**
  button. Never `confirm()` or `alert()`.
- **Full-screen layers bleed their colour** past their edges (`box-shadow: 0 0 0 100vmax
  <colour>`): an installed iPhone app can stop a `fixed; inset: 0` box short of the bottom.
- **Write down the stacking order** (for example: preview 50, sheet 60, toast 70) in one place.
- **Keep `[hidden]` next to the `display` rule** of anything you hide: an author `display` beats
  the browser’s `[hidden]`, and a menu was painted open on every load while the tests said
  hidden.

## 7. Scrolling

- **`html, body { overflow-x: clip }`, never `hidden`.** Safari counts a transformed element
  (a screen arriving from the right) as scrollable, so the page flashes a sideways scroll.
  `hidden` turns the body into a scroll box and breaks `position: sticky`.
- **`svh`, not `dvh`,** for full-height screens: with `dvh` the bottom button moves with the
  collapsing browser bar just as the thumb reaches for it.
- `overscroll-behavior: none` on the page, `contain` on layers that scroll themselves.
- Hide scroll bars only on touch screens (`@media (hover: none) and (pointer: coarse)`), never by
  turning the page into a scroll box.
- Each new screen starts at the top with `scrollTo({ top: 0, behavior: "instant" })`. With smooth
  scrolling switched on, a plain `scrollTo(0, 0)` glides up the whole page instead of jumping.
- **In-page anchors glide** (“Projects”, “Contact”, a table of contents): `scroll-behavior:
  smooth` on `html`, inside `@media (prefers-reduced-motion: no-preference)` so it jumps for
  people who reduce motion. Let the browser handle plain `<a href="#id">` links: it also updates
  the address bar and moves focus. Don’t replace them with JavaScript.
- **Leave room for a sticky header:** `scroll-padding-top` on `html`, equal to the header’s height
  plus a little air. Without it the section’s heading lands hidden under the header.
- **Don’t smooth the whole page’s scrolling** with a library (Lenis and the like) by default. It
  takes over the browser’s own scrolling, lags on iPhone and annoys keyboard and trackpad users.
  Only on a landing page or portfolio whose scroll-linked choreography needs it, and only when
  asked.
- Long grids: `content-visibility: auto`, and filter by hiding items, not rebuilding the grid on
  every keystroke.

## 8. Reduced motion

- **One global opt-out** in the tokens file collapses every animation and transition, so anything
  new is reduced by default.
- **Put back motion that carries meaning, as a short fade:** screen moves become a `.15s linear`
  fade, leaves a `.12s` fade, settles are off, a timer ring keeps its sweep. This needs
  `!important` on the class to beat the global rule.
- **JavaScript-driven motion checks** `matchMedia("(prefers-reduced-motion: reduce)")`: no
  neighbour pane, no leave delay.

## 9. Making it reliable

- **Remove every motion class once it has played,** with a timer fallback (700ms for arrivals,
  450ms for leaves): a phone that drops `animationend` must never leave a screen half-faded. A
  leftover `transform` also makes `position: fixed` children position against that element.
- **`animation-fill-mode: backwards`, not `both`,** on arrivals: a held end state overrides the
  inline transform, and the next swipe won’t move the page.
- **Play the move on the first real render.** Many screens draw twice (“Loading…”, then the
  data); play the pending move on the real one, give a quick second redraw only a fade, and let a
  move nobody played expire.
- **`will-change` only while moving,** on the motion class. A permanent `will-change` keeps a GPU
  layer and blurred timer digits on iPhone.
- **Don’t animate blur per frame** over moving images. Keep it constant during a drag.
- **Looping previews:** animated WebP in a plain `<img>`, not `<video autoplay>`, which phones
  block.

## 10. Check it like a user would

- **Look at the move, not the class.** Assert what is painted (`getComputedStyle`, a screenshot
  mid-move), not that a class was added.
- **Slow it down:** Chrome DevTools → Animations panel at 10% shows a snap, a jump or a double move
  that full speed hides.
- **Test with Reduce Motion on** (macOS or iPhone Settings → Accessibility → Motion).
- **Test on a real iPhone,** installed to the home screen when it’s an app. The traps in
  `references/ios-and-pwa.md` don’t show up in a desktop browser.
- **Resize the window,** not a container, to check every width.

## 11. OCHA products

- **Decided (Javier, 13 Oct 2026): this system is the OCHA standard**, so every OCHA app moves the
  same way. It belongs in the App Kit (`ocha-app-kit.css`), not in each app.
- The App Kit **doesn’t have it yet**: no motion tokens, no reduced-motion rules. Adding it is a
  planned change, to be tested in an OCHA product first; don’t add it to the kit as a side effect of
  other work. When it’s added, follow the design-system repository’s own CLAUDE.md: values as
  aliases in the kit, `sync.py`, the changelog and a handoff for the design-system session.
- Until then, an OCHA product that needs motion uses these exact token names and values, so it
  moves to the kit unchanged later.
- Colours, type, focus rings and components come from `ocha-visual-identity` (`cd-*`, App Kit).
  This skill only decides how they move.
- The same system works for personal projects as is. Keep the token names, so every app moves
  the same way.

## What this skill leaves out on purpose

App-specific choices that don’t generalise: a mode that colours the whole screen (rest, count-in),
a count-in sequence, specific sound designs and frequencies, and points and levels animations.
The general patterns behind them are above.

---

## Project Owner

Javier Cueto, Head of Brand and Design Unit

## Maintained by

**OCHA Brand and Design Unit (BDU)**
- Team: ochavisual@un.org
- Focal point: Javier Cueto (cuetoj@un.org)
