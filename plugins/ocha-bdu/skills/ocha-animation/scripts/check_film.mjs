/**
 * Automatic checks on a pure-function-of-time HTML animation, run BEFORE the contact sheet.
 *
 *   node --experimental-websocket check_film.mjs --page film.html [--step 0.1] [--loop]
 *        [--min-type 22] [--still 3] [--persist 0.2] [--report check_report.txt]
 *
 * It seeks the page through the whole film and measures what can be measured, so the person's
 * review rounds are spent on taste instead of mistakes:
 *
 *   OVERLAP     two pieces of visible text cover each other (different blocks, both mostly opaque)
 *   OFF-FRAME   visible text runs past the edge of the frame
 *   SMALL TYPE  settled text drawn smaller than --min-type px on the 1920×1080 stage
 *               (transforms included), too small for a washed-out meeting-room screen
 *   LOOP SEAM   with --loop: the last frame differs from the first, so the loop pops
 *   STILL       a stretch of --still seconds or more where the picture does not change. Not an
 *               error: a headline held to be read is a still on purpose. Report it so a dead
 *               moment is a decision, not an accident. The cut-out style's shake can hide one.
 *
 * Text that overlaps on purpose (a cloud of numbers, a decorative glyph) is marked in the page with
 * a data-check-skip attribute on it or on a parent; it is then left out of the text checks.
 * Findings are grouped into time windows, with a few examples each, so one busy scene does not
 * bury the rest of the report.
 *
 * Findings that last less than --persist seconds are left out: a crossfade at a scene cover
 * puts two scenes' text on screen for a few frames by design (rule 8 in motion-rules.md is
 * about the wipe, and is checked on the handover stills).
 *
 * Only HTML/SVG text is measured; text drawn on a canvas is invisible to the text checks
 * (the STILL and LOOP checks still see it). Exit code 1 when an error-type finding remains.
 * Same page contract and no-npm DevTools client as render_frames.mjs; needs ffmpeg for the
 * picture comparisons.
 *
 * Maintained by: OCHA Brand and Design Unit (BDU) — ochavisual@un.org
 */

import { spawn, spawnSync } from "node:child_process";
import { mkdir, rm, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import os from "node:os";

const argv = process.argv.slice(2);
const arg = (name, fallback) => {
  const i = argv.indexOf("--" + name);
  return i === -1 ? fallback : argv[i + 1];
};
const PAGE = path.resolve(arg("page", "film.html"));
const STEP = Number(arg("step", 0.1));
const MIN_TYPE = Number(arg("min-type", 22));
const STILL = Number(arg("still", 3));
const PERSIST = Number(arg("persist", 0.3));
const LOOP = argv.includes("--loop");
const FPS = Number(arg("fps", 30));
const WIDTH = Number(arg("width", 1920));
const HEIGHT = Number(arg("height", 1080));
const REPORT = arg("report", null);
const PORT = 9323 + (Number(process.env.CDP_PORT_OFFSET) || 0);
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
// Mean absolute difference (0–255) on a 64×36 grey thumbnail below which two pictures count as
// the same. Calibrated so a 1 px rise on a headline still counts as movement.
const SAME = 0.35;

if (!existsSync(PAGE)) { console.error(`No page at ${PAGE}`); process.exit(1); }
if (!existsSync(CHROME)) { console.error(`Chrome not found at ${CHROME} — set CHROME=/path/to/chrome`); process.exit(1); }

class CDP {
  constructor(ws) {
    this.ws = ws; this.id = 0; this.pending = new Map();
    ws.addEventListener("message", ev => {
      const msg = JSON.parse(ev.data);
      const p = this.pending.get(msg.id);
      if (!p) return;
      this.pending.delete(msg.id);
      msg.error ? p.reject(new Error(JSON.stringify(msg.error))) : p.resolve(msg.result);
    });
  }
  send(method, params = {}, sessionId) {
    const id = ++this.id, msg = { id, method, params };
    if (sessionId) msg.sessionId = sessionId;
    this.ws.send(JSON.stringify(msg));
    return new Promise((resolve, reject) => this.pending.set(id, { resolve, reject }));
  }
  static async attach(url) {
    const ws = new WebSocket(url);
    await new Promise((res, rej) => { ws.addEventListener("open", res, { once: true }); ws.addEventListener("error", rej, { once: true }); });
    return new CDP(ws);
  }
}

const sleep = ms => new Promise(r => setTimeout(r, ms));
async function fetchJSON(url, tries = 60) {
  for (let i = 0; i < tries; i++) {
    try { const r = await fetch(url); if (r.ok) return await r.json(); } catch {}
    await sleep(250);
  }
  throw new Error(`Chrome did not answer on ${url}`);
}

// Runs inside the page at each sample. Measures text by its glyph boxes (a Range over each text
// node), not by its element box: a full-width paragraph box would "overlap" everything beside it.
const MEASURE = `(() => {
  const W = ${WIDTH}, H = ${HEIGHT};
  const opacityOf = el => { let o = 1; for (let e = el; e && e.nodeType === 1; e = e.parentElement) o *= parseFloat(getComputedStyle(e).opacity); return o; };
  const blockOf = el => { for (let e = el; e; e = e.parentElement) { const d = getComputedStyle(e).display; if (!d.startsWith("inline") && d !== "contents") return e; } return document.body; };
  const nameOf = (el, text) => (el.id ? "#" + el.id : el.tagName.toLowerCase() + (el.classList[0] ? "." + el.classList[0] : "")) + ' "' + text.slice(0, 40) + '"';
  const items = [];
  const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = walk.nextNode(); n; n = walk.nextNode()) {
    const text = n.textContent.replace(/\\s+/g, " ").trim();
    if (!text) continue;
    const el = n.parentElement;
    if (!el || el.closest("[data-check-skip]") || getComputedStyle(el).visibility !== "visible") continue;
    const op = opacityOf(el);
    if (op < 0.6) continue;
    const r = document.createRange(); r.selectNodeContents(n);
    const rects = [...r.getClientRects()].filter(b => b.width > 1 && b.height > 1);
    if (!rects.length) continue;
    // Drawn size = font size × the element's transform scale (bounding box over layout box).
    const fs = parseFloat(getComputedStyle(el).fontSize);
    const lay = el.offsetHeight, box = el.getBoundingClientRect().height;
    const scale = lay > 0 ? box / lay : 1;
    items.push({ name: nameOf(el, text), block: blockOf(el), op, size: fs * scale, rects });
  }
  const over = [], off = [], small = [];
  for (const it of items) {
    for (const b of it.rects) {
      if (b.left < -1 || b.top < -1 || b.right > W + 1 || b.bottom > H + 1) { off.push(it.name); break; }
    }
    if (it.op >= 0.95 && it.size < ${MIN_TYPE}) small.push(it.name + " " + it.size.toFixed(1) + "px");
  }
  for (let i = 0; i < items.length; i++) for (let j = i + 1; j < items.length; j++) {
    const a = items[i], c = items[j];
    if (a.block === c.block || a.block.contains(c.block) || c.block.contains(a.block)) continue;
    hit: for (const p of a.rects) for (const q of c.rects) {
      const w = Math.min(p.right, q.right) - Math.max(p.left, q.left);
      const h = Math.min(p.bottom, q.bottom) - Math.max(p.top, q.top);
      if (w > 3 && h > 0.25 * Math.min(p.height, q.height)) { over.push(a.name + " × " + c.name); break hit; }
    }
  }
  return { over, off, small };
})()`;

const profile = path.join(os.tmpdir(), `ocha-animation-check-${process.pid}`);
const thumbs = path.join(os.tmpdir(), `ocha-animation-thumbs-${process.pid}`);
const chrome = spawn(CHROME, [
  "--headless=new", `--remote-debugging-port=${PORT}`, "--remote-allow-origins=*",
  "--hide-scrollbars", "--disable-gpu", "--force-device-scale-factor=1",
  `--window-size=${WIDTH},${HEIGHT}`, "--no-first-run", "--no-default-browser-check",
  `--user-data-dir=${profile}`, "about:blank",
], { stdio: "ignore" });

// Grey 64×36 thumbnails of every sample, decoded in one ffmpeg call.
function greyThumbs(dir, count) {
  const out = spawnSync("ffmpeg", ["-v", "error", "-start_number", "0", "-i", path.join(dir, "%05d.jpg"),
    "-vf", "scale=64:36,format=gray", "-f", "rawvideo", "-"], { maxBuffer: 1 << 30 });
  if (out.status !== 0) throw new Error("ffmpeg could not read the thumbnails: " + out.stderr);
  const px = 64 * 36, frames = [];
  for (let i = 0; i < count; i++) frames.push(out.stdout.subarray(i * px, (i + 1) * px));
  return frames;
}
const diff = (a, b) => { let s = 0; for (let i = 0; i < a.length; i++) s += Math.abs(a[i] - b[i]); return s / a.length; };

// Turn per-sample hits into time ranges that last at least `minLen` seconds.
function ranges(hitsBySample, times, minLen) {
  const open = new Map(), done = [];
  const close = (key, end) => { const s = open.get(key); open.delete(key); if (end - s >= minLen - 1e-9) done.push({ key, from: s, to: end }); };
  times.forEach((t, i) => {
    const now = new Set(hitsBySample[i]);
    for (const k of now) if (!open.has(k)) open.set(k, t);
    for (const k of [...open.keys()]) if (!now.has(k)) close(k, t);
  });
  const last = times[times.length - 1] + STEP;
  for (const k of [...open.keys()]) close(k, last);
  return done.sort((a, b) => a.from - b.from);
}
const fmt = s => s.toFixed(2) + "s";

let cdp, failed = false;
const lines = [];
const say = s => { lines.push(s); console.log(s); };
try {
  const version = await fetchJSON(`http://127.0.0.1:${PORT}/json/version`);
  cdp = await CDP.attach(version.webSocketDebuggerUrl);
  const { targetId } = await cdp.send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await cdp.send("Target.attachToTarget", { targetId, flatten: true });
  const call = (m, p) => cdp.send(m, p, sessionId);
  const evaluate = async expr => (await call("Runtime.evaluate", { expression: expr, returnByValue: true })).result.value;

  await call("Page.enable");
  await call("Runtime.enable");
  await call("Emulation.setDeviceMetricsOverride", { width: WIDTH, height: HEIGHT, deviceScaleFactor: 1, mobile: false });
  await call("Page.navigate", { url: "file://" + PAGE + "?t=0" });
  for (let i = 0; i < 80; i++) {
    if (await evaluate("document.readyState==='complete' && document.fonts.status==='loaded' && typeof window.seek==='function'")) break;
    await sleep(250);
  }
  await sleep(400);

  const dur = await evaluate("window.DURATION");
  if (!(dur > 0)) throw new Error("The page must set window.DURATION (seconds).");
  const times = [];
  for (let t = 0; t < dur - 1e-9; t += STEP) times.push(Math.round(t * 1000) / 1000);
  const lastFrame = (Math.round(dur * FPS) - 1) / FPS;

  await rm(thumbs, { recursive: true, force: true });
  await mkdir(thumbs, { recursive: true });
  const shoot = async (t, name) => {
    await evaluate(`window.seek(${t})`);
    const shot = await call("Page.captureScreenshot", { format: "jpeg", quality: 80, clip: { x: 0, y: 0, width: WIDTH, height: HEIGHT, scale: 0.125 } });
    await writeFile(path.join(thumbs, name), Buffer.from(shot.data, "base64"));
  };

  console.log(`Checking ${path.basename(PAGE)}: ${dur}s, a sample every ${STEP}s (${times.length} samples)`);
  const over = [], off = [], small = [];
  for (let i = 0; i < times.length; i++) {
    await shoot(times[i], String(i).padStart(5, "0") + ".jpg");
    const m = await evaluate(MEASURE);
    over.push(m.over); off.push(m.off); small.push(m.small);
  }

  console.log("");
  const report = (title, found) => {
    if (!found.length) { say(`✓ ${title}: none`); return; }
    failed = true;
    // Merge findings whose times touch into one window, so a busy scene reads as one line.
    const windows = [];
    for (const r of found) {
      const w = windows[windows.length - 1];
      if (w && r.from <= w.to + 1e-9) { w.to = Math.max(w.to, r.to); w.keys.add(r.key); }
      else windows.push({ from: r.from, to: r.to, keys: new Set([r.key]) });
    }
    say(`✗ ${title}: ${windows.length} window${windows.length > 1 ? "s" : ""}`);
    for (const w of windows) {
      const keys = [...w.keys];
      say(`    ${fmt(w.from)}–${fmt(w.to)}  ${keys.slice(0, 3).join("  |  ")}${keys.length > 3 ? `  (+${keys.length - 3} more)` : ""}`);
    }
  };
  report("OVERLAP (text on text)", ranges(over, times, PERSIST));
  report("OFF-FRAME (text past the edge)", ranges(off, times, PERSIST));
  report(`SMALL TYPE (settled text under ${MIN_TYPE}px)`, ranges(small, times, PERSIST));

  const grey = greyThumbs(thumbs, times.length);
  if (LOOP) {
    await shoot(0, "first.jpg"); await shoot(lastFrame, "last.jpg");
    const pair = spawnSync("ffmpeg", ["-v", "error", "-i", path.join(thumbs, "first.jpg"), "-i", path.join(thumbs, "last.jpg"),
      "-filter_complex", "[0][1]concat=n=2:v=1,scale=64:36,format=gray", "-f", "rawvideo", "-"], { maxBuffer: 1 << 24 });
    const px = 64 * 36, d = diff(pair.stdout.subarray(0, px), pair.stdout.subarray(px, 2 * px));
    if (d <= SAME) say(`✓ LOOP SEAM: last frame (${fmt(lastFrame)}) matches the first`);
    else { failed = true; say(`✗ LOOP SEAM: last frame (${fmt(lastFrame)}) differs from the first (difference ${d.toFixed(2)})`); }
  }

  const stills = [];
  let start = 0;
  for (let i = 1; i <= grey.length; i++) {
    if (i === grey.length || diff(grey[i], grey[i - 1]) > SAME) {
      const from = times[start], to = i === grey.length ? dur : times[i];
      if (to - from >= STILL) stills.push(`    ${fmt(from)}–${fmt(to)}  (${(to - from).toFixed(1)}s without change)`);
      start = i;
    }
  }
  say(stills.length ? `• STILL stretches of ${STILL}s or more — on purpose? ${stills.length}` : `✓ STILL stretches of ${STILL}s or more: none`);
  stills.forEach(s => say(s));
  if (REPORT) await writeFile(path.resolve(REPORT), lines.join("\n") + "\n");
} finally {
  try { await cdp?.send("Browser.close"); } catch {}
  chrome.kill("SIGTERM");
  await rm(profile, { recursive: true, force: true }).catch(() => {});
  await rm(thumbs, { recursive: true, force: true }).catch(() => {});
}
process.exit(failed ? 1 : 0);
