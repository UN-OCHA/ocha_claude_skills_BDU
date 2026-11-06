/**
 * Frame-accurate renderer for a pure-function-of-time HTML animation.
 *
 *   node --experimental-websocket render_frames.mjs --page film.html [--out frames] [--fps 30]
 *        [--scale 1] [--workers N] [--warmup 5]
 *
 * The page must expose window.seek(t) and window.DURATION (seconds). This script launches the
 * Chrome already installed on the machine in headless mode (headless_chrome.mjs, beside it), calls
 * seek(t) for every frame and saves a PNG. Because the page is a pure function of time the output
 * is deterministic: a slow machine cannot drop or duplicate a frame.
 *
 * Several Chromes work at once (--workers, default: half this computer's cores): each takes one
 * stretch of the film, in order. That is safe because every frame depends on t alone — but Chrome's
 * drawing does not quite: a word that scales in keeps the raster quality of the moment that Chrome
 * first drew it (the kit's words carry will-change: transform, and Chrome promotes moving layers on
 * its own too). So a Chrome that jumps into the middle of the film draws a few anti-aliased edges
 * differently from one that played up to that point — invisible, but it breaks the frame-hash proof
 * that a re-render changed only what was asked. Hence --warmup: before its stretch, each Chrome draws
 * and throws away the seconds before it, and reaches its first frame in the state a single Chrome
 * would. On the SG Awards film (2,391 frames, November 2026) 2 s left 121 frames different and 5 s
 * none: every frame byte-identical to a --workers 1 render, in 62 s instead of 285 s on 8 Chromes.
 * Every run checks this itself: each Chrome also draws the first frames of the next stretch, as a
 * continuous render would, and the run warns if they differ from what the next Chrome drew there
 * (then raise --warmup).
 *
 * Where the time goes: seek ≈ 1 ms, the screenshot ≈ 150 ms (Chrome drawing the 1920×1080 frame
 * in software). Faster PNG encoding saved 5 % and JPEG loses quality, so frames stay plain PNG;
 * the speed comes from the workers.
 *
 * No npm install. Set CHROME to the browser binary if it is not in a standard install place.
 * --scale 2 renders 3840x2160 frames from a 1920x1080 page (use only if HD is not sharp enough).
 *
 * Maintained by: OCHA Brand and Design Unit (BDU) — ochavisual@un.org
 */

import { mkdir, rm, writeFile } from "node:fs/promises";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import path from "node:path";
import os from "node:os";
import { openFilm } from "./headless_chrome.mjs";

const argv = process.argv.slice(2);
const arg = (name, fallback) => {
  const i = argv.indexOf("--" + name);
  return i === -1 ? fallback : argv[i + 1];
};
const PAGE = path.resolve(arg("page", "film.html"));
const OUT = path.resolve(arg("out", "frames"));
const FPS = Number(arg("fps", 30));
const SCALE = Number(arg("scale", 1));
const WIDTH = Number(arg("width", 1920));
const HEIGHT = Number(arg("height", 1080));
// Half the cores leaves room for each Chrome's own helper processes and for the rest of the
// computer; one Chrome per GB of memory keeps a small laptop from swapping.
const DEFAULT_WORKERS = Math.max(1, Math.min(Math.floor(os.availableParallelism() / 2), Math.floor(os.totalmem() / 2 ** 30)));
const WORKERS = Math.max(1, Math.floor(Number(arg("workers", DEFAULT_WORKERS))));
const WARMUP = Math.max(0, Number(arg("warmup", 5)));   // seconds each Chrome rehearses before its stretch (see above)

const fail = msg => { console.error(msg); process.exit(1); };
if (!existsSync(PAGE)) fail(`No page at ${PAGE}`);
if (![FPS, SCALE, WIDTH, HEIGHT, WORKERS, WARMUP].every(Number.isFinite) || FPS <= 0 || SCALE <= 0)
  fail("--fps, --scale, --width, --height, --workers and --warmup take numbers.");
// The frame folder is emptied before each render: refuse one that holds anything but frames, so a
// mistyped --out (".", a job folder) can never be wiped.
if (existsSync(OUT) && readdirSync(OUT).some(n => !/^\d{5}\.png$/.test(n)))
  fail(`${OUT} holds files other than frames — give --out an empty or frames-only folder.`);

let films = [];
try {
  // Start every Chrome at once; each loads the page and reports the film's length.
  const opened = await Promise.allSettled(Array.from({ length: WORKERS },
    () => openFilm({ page: PAGE, width: WIDTH, height: HEIGHT, scale: SCALE })));
  films = opened.filter(r => r.status === "fulfilled").map(r => r.value);
  const failure = opened.find(r => r.status === "rejected");
  if (failure) throw failure.reason;

  const dur = films[0].duration;
  if (films.some(f => f.duration !== dur)) throw new Error("The workers read different window.DURATION values — the page is not deterministic.");
  const frames = Math.round(dur * FPS);

  await rm(OUT, { recursive: true, force: true });
  await mkdir(OUT, { recursive: true });
  console.log(`Rendering ${frames} frames (${dur}s @ ${FPS}fps, ${WIDTH * SCALE}x${HEIGHT * SCALE}) with ${WORKERS} Chrome${WORKERS > 1 ? "s" : ""} -> ${OUT}`);

  // Each Chrome takes one stretch of the film, in order, after rehearsing the WARMUP seconds before it.
  const started = Date.now();
  let done = 0, stop = false;
  // The seam check: each Chrome also draws the first SEAM frames of the next stretch, as it would
  // playing on. They must match what the next Chrome drew there after its warm-up — if not, the
  // warm-up was too short for this film, and the run says so.
  const SEAM = 10, seams = [];
  const sha = buf => createHash("sha256").update(buf).digest("hex");
  const work = async (film, w) => {
    const from = Math.round(w * frames / films.length), to = Math.round((w + 1) * frames / films.length);
    const end = Math.min(frames, to + SEAM);
    for (let f = Math.max(0, from - Math.round(WARMUP * FPS)); f < end && !stop; f++) {
      await film.evaluate(`window.seek(${f / FPS})`);
      const shot = await film.call("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
      if (f < from) continue;   // a warm-up frame: drawn, not kept
      if (f >= to) { seams.push([f, sha(Buffer.from(shot.data, "base64"))]); continue; }
      await writeFile(path.join(OUT, String(f).padStart(5, "0") + ".png"), Buffer.from(shot.data, "base64"));
      if (++done % 60 === 0 || done === frames) {
        process.stdout.write(`\r  ${done}/${frames}  ${(done / ((Date.now() - started) / 1000)).toFixed(1)} fps  `);
      }
    }
  };
  // One failed worker stops them all: a frame folder with holes must never reach encode.sh.
  // Wait for every worker to stop before deleting, so no frame is written after the cleanup.
  const results = await Promise.allSettled(films.map((f, w) => work(f, w).catch(e => { stop = true; throw e; })));
  const failed = results.find(r => r.status === "rejected");
  if (failed) {
    await rm(OUT, { recursive: true, force: true });
    throw failed.reason;
  }
  process.stdout.write(`\n  done in ${((Date.now() - started) / 1000).toFixed(1)} s\n`);
  const off = seams.filter(([f, h]) => sha(readFileSync(path.join(OUT, String(f).padStart(5, "0") + ".png"))) !== h).map(([f]) => f);
  if (off.length) console.warn(`WARNING: ${off.length} frame(s) at the joins between Chromes differ from a continuous render `
    + `(${off.slice(0, 5).join(", ")}${off.length > 5 ? " …" : ""}). Invisible, but a frame-hash comparison will show them: `
    + `render again with a longer --warmup (now ${WARMUP} s), or --workers 1.`);
  else if (films.length > 1) console.log(`  joins checked: ${seams.length} frames identical to a continuous render`);
} catch (e) {
  console.error(e.message);   // a plain message for the person running it, not a stack trace
  process.exitCode = 1;
} finally {
  await Promise.all(films.map(f => f.close()));
}
