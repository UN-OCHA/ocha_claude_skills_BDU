/**
 * Check the film page against the voice, frame by frame, on what is actually painted.
 *
 *   node --experimental-websocket tools/check_sync.mjs [--page film/world.html] [--fps 30]
 *
 * 1. Sync: every spoken word must be painted (visible, mostly opaque, full size) on the first
 *    frame at or after (its voice start - one frame), and never after its voice start. Voice
 *    starts come from the page's own window.TIMELINE (word_timings.py → timeline.py).
 * 2. Independence: pieces of paper must not all change pose on the same frame. Reports, over
 *    frames with at least 8 pieces on screen, the share of them that changed together.
 * Exits 1 if a word is late or more than one frame early, so a broken sync fails loudly.
 */
import path from "node:path";
import { fileURLToPath } from "node:url";
import { openFilm } from "./headless_chrome.mjs";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const arg = (n, f) => { const i = argv.indexOf("--" + n); return i === -1 ? f : argv[i + 1]; };
const PAGE = path.resolve(HERE, arg("page", "film/world.html"));
const FPS = +arg("fps", 30);


// runs inside the page: returns the measurements
const PROBE = `((FPS) => {
  const TL = window.TIMELINE;
  const nodes = [...document.querySelectorAll("#words .unit .w")];
  const spoken = TL.words.filter(w => w.start < window.DURATION);
  if (nodes.length !== spoken.length) return { error: nodes.length + " words on the page, " + spoken.length + " spoken" };
  const painted = el => { const s = getComputedStyle(el), u = getComputedStyle(el.closest(".unit"));
    return s.visibility === "visible" && u.visibility === "visible" && +s.opacity * +u.opacity > 0.5; };
  const pieces = [...document.querySelectorAll(".qb, .num-w, .float-w, .gbar, .globe, #words .unit .w")];
  const pose = el => el.style.transform + "|" + el.style.filter + "|" + el.style.getPropertyValue("--cut");
  const first = nodes.map(() => null), prev = new Map(), together = [];
  const last = Math.floor(window.DURATION * FPS);
  for (let n = 0; n <= last; n++) {
    window.seek(n / FPS);
    nodes.forEach((el, i) => { if (first[i] === null && painted(el)) first[i] = n; });
    let on = 0, moved = 0;
    for (const el of pieces) {
      const s = getComputedStyle(el);
      if (s.visibility !== "visible" || +s.opacity < 0.05) { prev.delete(el); continue; }
      const p = pose(el);
      if (prev.has(el)) { on++; if (prev.get(el) !== p) moved++; }
      prev.set(el, p);
    }
    if (on >= 8) together.push(moved / on);
  }
  return { words: spoken.map((w, i) => ({ word: w.word, start: w.start, frame: first[i] })), together };
})(${FPS})`;

let film, failed = false;
try {
  film = await openFilm({ page: PAGE });
  if (!(film.duration > 0)) throw new Error("The page must set window.DURATION (seconds).");
  const r = await film.evaluate(PROBE);
  if (r.error) throw new Error(r.error);

  const frame = 1 / FPS, rows = r.words.map(w => ({ ...w, lead: w.frame === null ? null : w.start - w.frame / FPS }));
  const never = rows.filter(w => w.lead === null), late = rows.filter(w => w.lead !== null && w.lead < -1e-6),
        early = rows.filter(w => w.lead !== null && w.lead > frame + 1e-6);
  const leads = rows.filter(w => w.lead !== null).map(w => w.lead * 1000);
  console.log(`sync: ${rows.length} words · painted ${Math.min(...leads).toFixed(0)}–${Math.max(...leads).toFixed(0)} ms before their sound (one frame = ${(1000 * frame).toFixed(0)} ms)`);
  for (const [name, list] of [["never painted", never], ["LATE", late], ["more than a frame early", early]])
    if (list.length) { failed = true; console.log(`  ${name}: ` + list.map(w => `${w.word}@${w.start.toFixed(2)}${w.lead === null ? "" : ` (${(1000 * w.lead).toFixed(0)} ms)`}`).join(", ")); }
  const tg = r.together.sort((a, b) => a - b), q = p => tg[Math.min(tg.length - 1, Math.floor(p * tg.length))];
  console.log(`independence: over ${tg.length} busy frames, the share of on-screen pieces changing pose together is median ${(100 * q(0.5)).toFixed(0)}%, 95th percentile ${(100 * q(0.95)).toFixed(0)}%, max ${(100 * tg[tg.length - 1]).toFixed(0)}%`);
  console.log(failed ? "FAILED" : "ok");
} catch (e) {
  console.error(e.message);
  failed = true;
} finally {
  await film?.close();
}
if (failed) process.exitCode = 1;   // not process.exit(): on Windows that can cut off piped output
