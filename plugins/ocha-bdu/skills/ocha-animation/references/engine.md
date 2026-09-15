# The engine — frame-accurate HTML animation

## The page contract

Build the film as one self-contained HTML page (1920×1080 stage) that exposes:

```js
window.DURATION = 75;                 // seconds; the renderer reads it
window.seek = t => { render(t); return true; };
```

and renders nothing on its own when opened with `?t=` (freeze one instant), but plays on a
loop in a normal browser for preview:

```js
const frozen = new URLSearchParams(location.search).get("t");
document.fonts.ready.then(() => {
  if (frozen !== null) return render(parseFloat(frozen));
  const t0 = performance.now();
  (function loop(now) { render((now - t0) / 1000); requestAnimationFrame(loop); })(t0);
});
```

## `render(t)` rules

- **Every animated property is set from `t`.** No CSS transitions or animations, no timers,
  no state kept between calls. Calling `render(40)` then `render(3)` must give the same frame
  as `render(3)` alone.
- **Scenes are windows on the timeline.** Keep a list of `[start, end]` per scene; a scene is
  visible only inside its window, arrives over ~0.3 s and runs its exit over the last 0.5 s.
- **Hide with `visibility`, not `display: none`.** Layout stays measurable (you will need it
  for slides-to-a-slot and marker baselines).
- **Wait for fonts** (`document.fonts.ready`) before the first render; measurements taken
  before fonts load are wrong.
- **Load fonts the page needs** (Google Fonts link or embedded), so headless Chrome renders the
  real typefaces.
- **Canvas is fine for large fields of dots**; draw them every frame from `t`.

Helpers for all of this are in `scripts/motion.js`.

## Rendering

```bash
node --experimental-websocket scripts/render_frames.mjs --page film.html --out frames --fps 30
bash scripts/encode.sh frames film_1920x1080.mp4 30
```

- `render_frames.mjs` launches the Chrome already on the machine in headless mode, calls
  `seek(t)` for every frame and saves a PNG. No npm install. Set `CHROME` if Chrome is not in
  the standard macOS location. `--scale 2` gives 3840×2160 frames.
- `encode.sh` makes an H.264 MP4 (CRF 16, yuv420p, BT.709, fast-start) that plays everywhere.
- **Default 1920×1080.** Use `--scale 2` for 4K only when the user reports HD is not sharp
  enough on their screens.
- The frame folder is large and scratch: delete it after encoding.
