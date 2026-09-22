/**
 * Check the film page against the voice, frame by frame, on what is actually painted.
 *
 *   node --experimental-websocket assets/build/check_sync.mjs [--page film/world.html] [--fps 30]
 *
 * 1. Sync: every spoken word must be painted (visible, mostly opaque, full size) on the first
 *    frame at or after (its voice start - one frame), and never after its voice start. Voice
 *    starts come from the page's own window.TIMELINE (word_timings.py → timeline.py).
 * 2. Independence: pieces of paper must not all change pose on the same frame. Reports, over
 *    frames with at least 8 pieces on screen, the share of them that changed together.
 * Exits 1 if a word is late or more than one frame early, so a broken sync fails loudly.
 */
import { spawn } from "node:child_process";
import { rm } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const arg = (n, f) => { const i = argv.indexOf("--" + n); return i === -1 ? f : argv[i + 1]; };
const PAGE = path.resolve(HERE, arg("page", "film/world.html"));
const FPS = +arg("fps", 30), PORT = 9332;
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
if (!existsSync(PAGE)) { console.error(`No page at ${PAGE}`); process.exit(1); }

class CDP {
  constructor(ws) {
    this.ws = ws; this.id = 0; this.pending = new Map();
    ws.addEventListener("message", ev => {
      const m = JSON.parse(ev.data), p = this.pending.get(m.id);
      if (!p) return; this.pending.delete(m.id);
      m.error ? p.reject(new Error(JSON.stringify(m.error))) : p.resolve(m.result);
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
async function fetchJSON(url) {
  for (let i = 0; i < 60; i++) { try { const r = await fetch(url); if (r.ok) return await r.json(); } catch {} await sleep(250); }
  throw new Error(`Chrome did not answer on ${url}`);
}

// runs inside the page: returns the measurements
const PROBE = `(async (FPS) => {
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

const profile = path.join(os.tmpdir(), `ocha-sync-${process.pid}`);
const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${PORT}`, "--remote-allow-origins=*",
  "--hide-scrollbars", "--disable-gpu", "--force-device-scale-factor=1", "--window-size=1920,1080",
  "--no-first-run", "--no-default-browser-check", `--user-data-dir=${profile}`, "about:blank"], { stdio: "ignore" });
let cdp, failed = false;
try {
  const v = await fetchJSON(`http://127.0.0.1:${PORT}/json/version`);
  cdp = await CDP.attach(v.webSocketDebuggerUrl);
  const { targetId } = await cdp.send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await cdp.send("Target.attachToTarget", { targetId, flatten: true });
  const call = (m, p) => cdp.send(m, p, sessionId);
  await call("Page.enable"); await call("Runtime.enable");
  await call("Emulation.setDeviceMetricsOverride", { width: 1920, height: 1080, deviceScaleFactor: 1, mobile: false });
  await call("Page.navigate", { url: "file://" + PAGE + "?t=0" });
  for (let i = 0; i < 80; i++) {
    const r = await call("Runtime.evaluate", { expression: "document.readyState==='complete' && document.fonts.status==='loaded' && typeof window.seek==='function'", returnByValue: true });
    if (r.result.value) break; await sleep(250);
  }
  await sleep(400);
  const r = (await call("Runtime.evaluate", { expression: PROBE, awaitPromise: true, returnByValue: true })).result.value;
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
} finally {
  try { await cdp?.send("Browser.close"); } catch {}
  chrome.kill("SIGTERM");
  await rm(profile, { recursive: true, force: true }).catch(() => {});
}
process.exit(failed ? 1 : 0);
