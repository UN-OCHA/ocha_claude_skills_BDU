/**
 * Frame-accurate renderer for a pure-function-of-time HTML animation.
 *
 *   node --experimental-websocket render_frames.mjs --page film.html [--out frames] [--fps 30] [--scale 1]
 *
 * The page must expose window.seek(t) and window.DURATION (seconds). This script launches the
 * Chrome already installed on the machine in headless mode, drives it over the DevTools
 * protocol, calls seek(t) for every frame and saves a PNG. Because the page is a pure function
 * of time the output is deterministic: a slow machine cannot drop or duplicate a frame.
 *
 * No npm install: the DevTools client below is ~40 lines over Node 20+'s WebSocket.
 * Set CHROME to the browser binary if it is not in the standard macOS location.
 * --scale 2 renders 3840x2160 frames from a 1920x1080 page (use only if HD is not sharp enough).
 *
 * Maintained by: OCHA Brand and Design Unit (BDU) — ochavisual@un.org
 */

import { spawn } from "node:child_process";
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
const OUT = path.resolve(arg("out", "frames"));
const FPS = Number(arg("fps", 30));
const SCALE = Number(arg("scale", 1));
const WIDTH = Number(arg("width", 1920));
const HEIGHT = Number(arg("height", 1080));
const PORT = 9223 + (Number(process.env.CDP_PORT_OFFSET) || 0);
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

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

const profile = path.join(os.tmpdir(), `ocha-animation-chrome-${process.pid}`);
const chrome = spawn(CHROME, [
  "--headless=new", `--remote-debugging-port=${PORT}`, "--remote-allow-origins=*",
  "--hide-scrollbars", "--disable-gpu", "--force-device-scale-factor=1",
  `--window-size=${WIDTH},${HEIGHT}`, "--no-first-run", "--no-default-browser-check",
  `--user-data-dir=${profile}`, "about:blank",
], { stdio: "ignore" });

let cdp;
try {
  const version = await fetchJSON(`http://127.0.0.1:${PORT}/json/version`);
  cdp = await CDP.attach(version.webSocketDebuggerUrl);
  const { targetId } = await cdp.send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await cdp.send("Target.attachToTarget", { targetId, flatten: true });
  const call = (m, p) => cdp.send(m, p, sessionId);

  await call("Page.enable");
  await call("Runtime.enable");
  await call("Emulation.setDeviceMetricsOverride", { width: WIDTH, height: HEIGHT, deviceScaleFactor: SCALE, mobile: false });
  await call("Page.navigate", { url: "file://" + PAGE + "?t=0" });

  // Wait for fonts and the seek hook before the first grab: frames taken earlier use
  // fallback fonts and wrong measurements.
  for (let i = 0; i < 80; i++) {
    const r = await call("Runtime.evaluate", {
      expression: "document.readyState==='complete' && document.fonts.status==='loaded' && typeof window.seek==='function'",
      returnByValue: true,
    });
    if (r.result.value) break;
    await sleep(250);
  }
  await sleep(400);

  const dur = (await call("Runtime.evaluate", { expression: "window.DURATION", returnByValue: true })).result.value;
  if (!(dur > 0)) throw new Error("The page must set window.DURATION (seconds).");
  const frames = Math.round(dur * FPS);

  await rm(OUT, { recursive: true, force: true });
  await mkdir(OUT, { recursive: true });
  console.log(`Rendering ${frames} frames (${dur}s @ ${FPS}fps, ${WIDTH * SCALE}x${HEIGHT * SCALE}) -> ${OUT}`);
  const started = Date.now();
  for (let f = 0; f < frames; f++) {
    await call("Runtime.evaluate", { expression: `window.seek(${f / FPS})`, returnByValue: true });
    const shot = await call("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
    await writeFile(path.join(OUT, String(f).padStart(5, "0") + ".png"), Buffer.from(shot.data, "base64"));
    if (f % 60 === 0 || f === frames - 1) {
      process.stdout.write(`\r  ${f + 1}/${frames}  ${((f + 1) / ((Date.now() - started) / 1000)).toFixed(1)} fps  `);
    }
  }
  process.stdout.write("\n");
} finally {
  try { await cdp?.send("Browser.close"); } catch {}
  chrome.kill("SIGTERM");
  await rm(profile, { recursive: true, force: true }).catch(() => {});
}
