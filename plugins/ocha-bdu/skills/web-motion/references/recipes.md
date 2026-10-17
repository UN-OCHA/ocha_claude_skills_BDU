# Web motion: recipes

Working code for the system in `SKILL.md`, adapted from a production web app (plain CSS and
JavaScript, no framework). Class and function names are generic; keep them, so every app moves
the same way. Put the tokens (SKILL.md §1) in the shared tokens file first: everything here reads
them.

---

## 1. Screen and layer moves (CSS)

```css
@keyframes m-in-forward { from { opacity: 0; transform: translateX(var(--move)); } }
@keyframes m-in-back    { from { opacity: 0; transform: translateX(calc(var(--move) * -1)); } }
@keyframes m-in-fade    { from { opacity: 0; } }
@keyframes m-in-rise    { from { opacity: 0; transform: translateY(var(--move-layer)); } }
@keyframes m-out-sink   { to   { opacity: 0; transform: translateY(calc(var(--move-layer) / 2)); } }
@keyframes m-out-fade   { to   { opacity: 0; } }
@keyframes m-settle     { 40%  { transform: scale(1.12); } }
@keyframes m-drop       { from { opacity: 0; transform: translateY(-8px) scale(.98); } }

.m-forward, .m-back           { --move: var(--move-page); }
.m-step-forward, .m-step-back { --move: var(--move-step); }
/* backwards, not both: a held end state would override the next inline transform */
.m-forward, .m-step-forward { animation: m-in-forward var(--dur-enter) var(--ease-enter) backwards; }
.m-back, .m-step-back       { animation: m-in-back    var(--dur-enter) var(--ease-enter) backwards; }
.m-fade  { animation: m-in-fade var(--dur-leave) var(--ease-enter) backwards; }
.m-rise  { animation: m-in-rise var(--dur-enter) var(--ease-enter) backwards; }
.m-leave { animation: m-out-sink var(--dur-leave) var(--ease-in) forwards; pointer-events: none; }
/* will-change only while the move plays; the class comes off after */
.m-forward, .m-back, .m-step-forward, .m-step-back, .m-rise { will-change: transform, opacity; }
.m-bump       { animation: m-settle var(--dur-enter) var(--ease-enter); }
.m-bump-block { display: inline-block; }     /* a transform does nothing to an inline box */
.menu.is-open { animation: m-drop var(--dur-leave) var(--ease-out) backwards; transform-origin: top right; }
```

## 2. Reduced motion (CSS)

```css
/* In the shared tokens file: everything collapses by default, including anything added later. */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .01ms !important; animation-iteration-count: 1 !important;
    transition-duration: .01ms !important;
  }
}
/* Next to the motion classes: moves that carry meaning come back as a short fade.
   !important on the class beats the global rule above. */
@media (prefers-reduced-motion: reduce) {
  .m-forward, .m-back, .m-step-forward, .m-step-back, .m-fade, .m-rise {
    animation: m-in-fade .15s linear backwards !important;
  }
  .m-leave { animation: m-out-fade .12s linear forwards !important; }
  .m-bump  { animation: none !important; }
  .timer-ring circle { transition-duration: .95s !important; }   /* a sweep that tells time stays */
}
```

## 3. Presses (CSS)

```css
body { -webkit-tap-highlight-color: transparent; }   /* our :active states replace it */

:where(.btn, .iconbtn, .thumb) { transition: transform var(--dur-press) var(--ease-out); }
:where(.btn, .iconbtn, .thumb):active { transform: scale(.97); }

/* Cards press more gently: a card is big, so .97 would look like a jump. */
:where(.card--tap) { transition: transform var(--dur-press) var(--ease-out), filter var(--dur-press) var(--ease-out); }
:where(.card--tap):active { transform: scale(.985); }

/* Hover only where there is a real pointer: on touch, :hover sticks after a tap. */
@media (hover: hover) and (pointer: fine) {
  .btn:hover { /* … */ }
}

/* A small icon with a 44px hit area */
.iconbtn { position: relative; }
.iconbtn::after { content: ""; position: absolute; inset: 50% auto auto 50%;
                  width: 44px; height: 44px; transform: translate(-50%, -50%); }
```

## 4. `enter`, `leave`, `bump` (JavaScript)

Every move goes through these three, so classes are always removed and nothing gets stuck.

```js
var ENTER = { forward: "m-forward", back: "m-back", fade: "m-fade", rise: "m-rise",
              stepForward: "m-step-forward", stepBack: "m-step-back" };

/* Plays one arrival, then removes its class. The timer is the fallback for a phone that
   drops animationend: a screen must never be left half-faded. */
function enter(el, kind) {
  var cls = ENTER[kind];
  if (!el || !cls) return;
  Object.keys(ENTER).forEach(function (k) { el.classList.remove(ENTER[k]); });
  void el.offsetWidth;                                   // restart, even the same kind
  el.classList.add(cls);
  var t = setTimeout(clear, 700);
  function clear(e) {
    if (e && e.target !== el) return;                    // a child's own animation
    clearTimeout(t); el.removeEventListener("animationend", clear); el.classList.remove(cls);
  }
  el.addEventListener("animationend", clear);
}

/* Sinks and fades el, then calls done (which removes it). */
function leave(el, done) {
  if (!el) { if (done) done(); return; }
  var over = false, t = setTimeout(finish, 450);
  function finish(e) {
    if ((e && e.target !== el) || over) return;
    over = true; clearTimeout(t); el.removeEventListener("animationend", finish);
    if (done) done();
  }
  el.classList.add("m-leave");
  el.addEventListener("animationend", finish);
}

/* Settles a value that just changed. */
function bump(el) {
  if (!el) return;
  var inline = getComputedStyle(el).display === "inline";
  el.classList.remove("m-bump", "m-bump-block"); void el.offsetWidth;
  el.classList.add("m-bump");
  if (inline) el.classList.add("m-bump-block");
  setTimeout(function () { el.classList.remove("m-bump", "m-bump-block"); }, 700);
}
```

**Choosing the move for a new screen.** Keep a depth for each route and compare:

```js
var DEPTH = { home: 0, history: 0, week: 1, day: 2, settings: 1 };   // example
function moveFor(from, to) {
  if (from == null || DEPTH[from] === DEPTH[to]) return "fade";
  return DEPTH[to] > DEPTH[from] ? "forward" : "back";
}
```

Play it on the **first real render**: if the screen draws “Loading…” first, hold the move and play
it when the real content arrives; a second redraw within about a second gets only `"fade"`, and a
move nobody played expires after a few seconds. Call `scrollTo(0, 0)` when a new screen arrives.

## 5. Overlay: one for every layer (JavaScript)

```js
/* Dialog role, Escape, and focus back to the opener. Returns release(). */
function overlay(el, label, close) {
  el.setAttribute("role", "dialog"); el.setAttribute("aria-modal", "true");
  if (label) el.setAttribute("aria-label", label);
  if (!el.hasAttribute("tabindex")) el.setAttribute("tabindex", "-1");
  var prevFocus = document.activeElement;
  function onKey(e) { if (e.key === "Escape") { e.preventDefault(); close(); } }
  document.addEventListener("keydown", onKey, true);
  document.body.appendChild(el);
  // Focus the layer, not its first button: focusing "Close" draws a ring on it on iPhone.
  el.focus({ preventScroll: true, focusVisible: false });
  return function release() {
    document.removeEventListener("keydown", onKey, true);
    if (prevFocus && prevFocus.focus && document.contains(prevFocus)) {
      prevFocus.focus({ preventScroll: true, focusVisible: false });
    }
  };
}
```

## 6. Bottom sheet (CSS and JavaScript)

```css
.sheet-back {
  position: fixed; inset: 0; z-index: 60;
  display: flex; align-items: flex-end; justify-content: center;
  padding: 16px 16px calc(env(safe-area-inset-bottom) + 16px);
  background: #0008; opacity: 0; transition: opacity var(--dur-leave) var(--ease-out);
  box-shadow: 0 0 0 100vmax #0008;       /* bleed: an installed iPhone app can stop inset:0 short */
}
.sheet-back.in { opacity: 1; }
.sheet {
  width: 100%; max-width: 480px;
  transform: translateY(var(--move-layer));
  transition: transform var(--dur-enter) var(--ease-enter);
}
.sheet-back.in .sheet { transform: none; }
```

```js
function openSheet(back, label, onCancel) {
  var closing = false, release;
  function close() {
    if (closing) return; closing = true;                 // never close twice
    back.classList.remove("in");
    release();
    setTimeout(function () { back.remove(); }, 180);     // --dur-leave
  }
  release = overlay(back, label, function () { close(); if (onCancel) onCancel(); });
  back.addEventListener("click", function (e) { if (e.target === back) { close(); if (onCancel) onCancel(); } });
  requestAnimationFrame(function () { back.classList.add("in"); });   // let the start state paint
  return close;
}
```

For a destructive choice, focus the **safe** button, not the destructive one. Never `confirm()`.

## 7. Swipe between pages, as a carousel (CSS and JavaScript)

```css
.swipe-page { touch-action: pan-y; position: relative; }        /* anchors the neighbours */
.swipe-page.is-swiping  { transition: none; }
.swipe-page.is-settling { transition: transform var(--dur-release) var(--ease-out), opacity var(--dur-release) var(--ease-out); }
.swipe-page.is-leaving  { transition: transform var(--dur-release) var(--ease-out), opacity var(--dur-leave) var(--ease-in); }
.swipe-side { position: absolute; top: 0; width: 100%; height: 100%; overflow: hidden; pointer-events: none; }
.swipe-page img { -webkit-touch-callout: none; -webkit-user-drag: none; }
@media (prefers-reduced-motion: reduce) {
  .swipe-page.is-settling, .swipe-page.is-leaving { transition: none; }
}
```

```js
/* A copy of page markup that the live code can never find, click, focus or read. */
function inertCopy(html) {
  var tpl = document.createElement("template");
  tpl.innerHTML = html;
  Array.prototype.slice.call(tpl.content.querySelectorAll("*")).forEach(function (node) {
    Array.prototype.slice.call(node.attributes).forEach(function (a) {
      if (a.name === "id" || a.name === "for" || a.name === "aria-controls" || a.name.indexOf("data-") === 0) {
        node.removeAttribute(a.name);
      }
    });
  });
  return tpl.content;
}

/* opts: { next(dir, seamless), prev(dir, seamless), peek(dir) → markup of the neighbour }.
   next/prev are null when there is no page that way. Returns { go(dir) } for the arrow buttons,
   so arrows and swipes play the same move. */
function swipePages(el, opts) {
  var THRESHOLD = 80, OUT_MS = 260, GAP = 16;           // px, --dur-release, px
  var x0 = 0, y0 = 0, dx = 0, active = false, horizontal = null, sides = {};
  function reduced() { return matchMedia("(prefers-reduced-motion: reduce)").matches; }

  function side(dir) {                                   // the neighbouring page, beside this one
    if (sides[dir] !== undefined) return sides[dir];
    var html = opts.peek && (dir > 0 ? opts.next : opts.prev) && !reduced() ? opts.peek(dir) : null;
    if (!html) return (sides[dir] = null);
    var pane = document.createElement("div");
    pane.className = "swipe-side"; pane.setAttribute("aria-hidden", "true"); pane.inert = true;
    pane.style.left = dir > 0 ? "calc(100% + " + GAP + "px)" : "calc(-100% - " + GAP + "px)";
    pane.appendChild(inertCopy(html));
    el.appendChild(pane);
    return (sides[dir] = pane);
  }
  function dropSides() { Object.keys(sides).forEach(function (k) { if (sides[k]) sides[k].remove(); }); sides = {}; }
  function settle() {
    el.classList.remove("is-swiping"); el.classList.add("is-settling");
    el.style.transform = ""; el.style.opacity = "";
    setTimeout(function () { el.classList.remove("is-settling"); dropSides(); }, OUT_MS);
  }
  function leave(dir) {                                  // dir 1 = next (page leaves to the left)
    var go = dir > 0 ? opts.next : opts.prev;
    if (!go) { settle(); return; }
    var pane = side(dir);
    void el.offsetWidth;                                 // an arrow tap starts from rest
    el.classList.remove("is-swiping"); el.classList.add("is-leaving");
    if (pane) {                                          // carousel: the neighbour lands in place
      el.style.transform = "translateX(calc(" + (dir > 0 ? "-100% - " : "100% + ") + GAP + "px))";
    } else {
      el.style.transform = "translateX(" + (dir > 0 ? -100 : 100) + "%)"; el.style.opacity = "0";
    }
    setTimeout(function () { go(dir, !!pane); }, reduced() ? 0 : OUT_MS);   // seamless: don't animate again
  }

  el.addEventListener("touchstart", function (e) {
    horizontal = null; dx = 0;
    if (e.touches.length !== 1 || e.target.closest("input, textarea, select")) { active = false; return; }
    x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; active = true;
  }, { passive: true });
  el.addEventListener("touchmove", function (e) {
    if (!active) return;
    var mx = e.touches[0].clientX - x0, my = e.touches[0].clientY - y0;
    if (horizontal === null && (Math.abs(mx) > 8 || Math.abs(my) > 8)) horizontal = Math.abs(mx) > Math.abs(my) * 1.3;
    if (!horizontal) return;
    if (e.cancelable) e.preventDefault();                // a sideways drag never also scrolls
    var dir = mx < 0 ? 1 : -1, can = dir > 0 ? opts.next : opts.prev;
    dx = can ? mx : mx / 4;                              // resistance where there's nowhere to go
    var pane = can ? side(dir) : null;
    el.classList.add("is-swiping");
    el.style.transform = "translateX(" + dx + "px)";
    el.style.opacity = pane || !can ? "" : String(1 - Math.min(Math.abs(dx) / (el.offsetWidth || 1), 1) * 0.6);
  }, { passive: false });                                // non-passive, or preventDefault is ignored
  el.addEventListener("touchend", function () {
    if (!active) return;
    active = false;
    if (!horizontal) return;
    if (Math.abs(dx) >= THRESHOLD) leave(dx < 0 ? 1 : -1); else settle();
  });
  el.addEventListener("touchcancel", function () { active = false; if (horizontal) settle(); });
  el.addEventListener("click", function (e) {            // a drag never also taps what it started on
    if (horizontal) { e.preventDefault(); e.stopPropagation(); }
  }, true);
  return { go: leave };
}
```

When `next`/`prev` renders the new page: if `seamless` is true, the neighbour already slid into
place, so render without an arrival move; otherwise play `enter(page, dir > 0 ? "forward" : "back")`.

## 8. Timers (JavaScript)

```js
/* Wall-clock countdown: survives a frozen tab, never drifts. */
function countdown(seconds, onTick, onDone) {
  var deadline = Date.now() + seconds * 1000, left = seconds * 1000, timer = null;
  function tick() {
    left = Math.max(0, deadline - Date.now());
    onTick(Math.ceil(left / 1000));
    if (left === 0) { stop(); onDone(); }
  }
  function start() { deadline = Date.now() + left; if (!timer) timer = setInterval(tick, 100); tick(); }
  function stop()  { clearInterval(timer); timer = null; }
  document.addEventListener("visibilitychange", function () { if (!document.hidden && timer) tick(); });
  start();
  return { pause: function () { stop(); left = Math.max(0, deadline - Date.now()); }, resume: start, stop: stop };
}
```

A ring: move `stroke-dashoffset` once a second with `transition: stroke-dashoffset .95s linear`.
To start a new interval, set `transition: none`, reset the offset, force a reflow
(`void el.getBoundingClientRect()`), then restore the transition.

## 9. Count up (JavaScript)

```js
function countUp(el, to, done) {
  var steps = 18, i = 0;
  var t = setInterval(function () {
    i++; el.textContent = Math.round(to * i / steps);
    if (i >= steps) { clearInterval(t); bump(el); if (done) done(); }
  }, 40);
}
```

## 10. Anchors and loading content (CSS and JavaScript)

```css
@media (prefers-reduced-motion: no-preference) {
  html { scroll-behavior: smooth; }          /* in-page anchors glide; reduced motion jumps */
}
html { scroll-padding-top: calc(var(--header-h, 64px) + 16px); }  /* headings clear a sticky header */

/* Skeleton: real size, subtle pulse from top left to bottom right */
.skeleton {
  background: linear-gradient(120deg, var(--skel) 30%, var(--skel-hi) 50%, var(--skel) 70%);
  background-size: 300% 100%;
  animation: skel 1.6s linear infinite;
  border-radius: 8px;
}
@keyframes skel { from { background-position: 100% 0; } to { background-position: 0 0; } }
@media (prefers-reduced-motion: reduce) { .skeleton { animation: none; } }

/* Content that arrives later fades in over the skeleton: opacity only, all at once */
.is-loading .content { opacity: 0; }
.content { transition: opacity var(--dur-leave) var(--ease-enter); }
/* Reserve image space: give every <img> width and height attributes; browsers turn them
   into its aspect ratio, so nothing shifts when it arrives. */
```

```js
// New screen in an app: jump to the top, don't glide (smooth scrolling is on for anchors)
window.scrollTo({ top: 0, behavior: "instant" });

// Swap a skeleton for content once the data is ready
async function load(box, fetchData, render) {
  box.classList.add("is-loading");
  render(box, await fetchData());           // renders under the skeleton, invisible
  requestAnimationFrame(() => box.classList.remove("is-loading"));  // fades in, all together
}
```

