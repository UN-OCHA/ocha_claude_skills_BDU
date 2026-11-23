# iPhone Safari and installed web apps (PWA): the traps

None of these show up in a desktop browser. Check every one on a real iPhone, and on an installed
app (added to the home screen) when the product is one.

---

## Layout and scrolling

- **`html, body { overflow-x: clip }`, never `hidden`.** Safari counts a transformed element as
  scrollable overflow, so a screen arriving from the right flashes a sideways scroll. `hidden`
  makes the body a scroll box and breaks `position: sticky`.
- **`svh`, not `dvh`,** for full-height screens: with `dvh` the bottom button moves with the
  collapsing toolbar just as the thumb reaches for it.
- **Inputs at 16px or more,** or iOS zooms the page when a field gets focus.
- **`overscroll-behavior: none`** on the page; **`contain`** on layers that scroll themselves.
- **Hide scroll bars only on touch screens**, with `scrollbar-width: none` and
  `::-webkit-scrollbar { display: none }` inside `@media (hover: none) and (pointer: coarse)`.
  A mouse keeps its scroll bar.

## Installed app (home screen)

- **Status bar:** `apple-mobile-web-app-status-bar-style` `black-translucent`, then paint your own
  band behind the clock (`body::before`, the height of the safe area). With `default`, the Back
  button can end up under the clock, where taps are swallowed. Give the top safe area a floor
  (about 54px when installed) in case `env(safe-area-inset-top)` reports less.
- **`theme-color` equals the page background,** and change it at runtime when a full-screen mode
  changes the background colour.
- **Full-screen layers bleed their colour** (`box-shadow: 0 0 0 100vmax <colour>`): a
  `fixed; inset: 0` box can stop short of the bottom edge. The strip under the home indicator is
  painted by the page’s own background, so a full-screen mode colours `body` too.
- **After every change to the app’s files, bump the service worker’s cache name,** or phones keep
  the old app.
- **Testing a fix on the phone:** force a real reload (add `?r=<anything>` to the address). A
  change of only the `#hash` keeps the old JavaScript. When a fix “isn’t there”, fetch what the
  phone is actually served before changing any code.

## Sound (Web Audio)

- **Unlock audio inside the tap.** A capture-phase listener on `touchend`, `click` and `keydown`
  resumes the audio context, and the tap that starts sound-making asks for sound itself. Switched
  on later (after data loads), iOS keeps it silent.
- **`navigator.audioSession.type = "ambient"`, never `"playback"`.** Playback pauses the person’s
  music and podcasts. The cost: the silent switch mutes your cues. That’s the right trade.
- **Drop cues, never queue them,** when the context isn’t running or the page is hidden. iOS
  freezes the audio clock while locked, and every cue fired meanwhile plays at once on return.
- **Close the audio context** a moment after leaving the screen that uses it (suspending keeps the
  queue), and rebuild it on the next key tap.
- **Don’t trust `state === "running"`:** iOS can report it and play nothing. Rebuild on key taps,
  and give people a “Test sound” button that repairs and beeps in one tap.
- **One output chain:** gain about 0.8 → a low-pass around 3kHz → a limiter (`DynamicsCompressor`),
  so stacked or harsh cues can’t pierce headphones.
- **Distinct meanings get distinct sounds** (different pitches). Keep start-up sounds subtle.

## Haptics, screen and media

- **`navigator.vibrate` does nothing in iPhone web apps.** Treat vibration as an Android-only extra;
  never rely on it to confirm anything.
- **Keep the screen awake** during a task with the Screen Wake Lock API, and request it again when
  the page becomes visible (the lock is released when it’s hidden).
- **`playsinline`** on every embedded video, or it opens full screen.
- **Looping previews as animated WebP in `<img>`,** not `<video autoplay>`: phones block autoplay.
  Many large animated images decode slowly, so don’t rebuild a grid of them on every keystroke.

## Focus and accessibility on iPhone

- **Focus a layer itself, not its first button,** with `{ focusVisible: false }`, or the first
  button shows a focus ring when the layer opens.
- **No `aria-live` on the app root** when something counts every second: use `role="timer"`.
