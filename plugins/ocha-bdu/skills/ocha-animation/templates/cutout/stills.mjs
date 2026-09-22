/**
 * Render approval stills from the film page: one settled frame per scene window.
 *
 *   node --experimental-websocket assets/build/stills.mjs [--page film/index.html] [--out stills]
 *
 * Reads window.WINDOWS from the page and grabs each scene 0.35 s before its window ends,
 * when everything in it has arrived. Same headless-Chrome/DevTools approach as the
 * ocha-animation skill's render_frames.mjs, so a still is an exact frame of the film.
 */
import { spawn } from "node:child_process";
import { mkdir, rm, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import os from "node:os";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const arg = (n, f) => { const i = argv.indexOf("--" + n); return i === -1 ? f : argv[i + 1]; };
const PAGE = path.resolve(HERE, arg("page", "film/world.html"));
const OUT = path.resolve(HERE, arg("out", "stills"));
const SETTLE = 0.35, PORT = 9331;
const VARIANTS = (arg("variants", "") || "").split(",").filter(Boolean);   // extra renders of every key, one per query string
const ONLY = (arg("keys", "") || "").split(",").filter(Boolean);
const TIMES = (arg("times", "") || "").split(",").filter(Boolean).map(Number);   // --times 68.5,68.9: any moments, instead of the named ones
const EXTRA = VARIANTS.length ? [] : [["s1", "pills=word"]];
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

const profile = path.join(os.tmpdir(), `ocha-stills-${process.pid}`);
const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${PORT}`, "--remote-allow-origins=*",
  "--hide-scrollbars", "--disable-gpu", "--force-device-scale-factor=1", "--window-size=1920,1080",
  "--no-first-run", "--no-default-browser-check", `--user-data-dir=${profile}`, "about:blank"], { stdio: "ignore" });
let cdp;
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
  const err = (await call("Runtime.evaluate", { expression: "window.__errors || null", returnByValue: true })).result.value;
  if (err) console.log("page errors:", err);
  const keys = (await call("Runtime.evaluate", { expression: "window.KEYS || null", returnByValue: true })).result.value;
  const wins = (await call("Runtime.evaluate", { expression: "window.WINDOWS", returnByValue: true })).result.value;
  if (!keys && !wins) throw new Error("The page must expose window.KEYS or window.WINDOWS.");
  // KEYS names the settled moment of each cluster; without it, take each window's end
  const shots = keys ? Object.entries(keys).map(([id, t]) => [id, t, ""])
    : Object.entries(wins).filter(([id]) => id !== "s8").map(([id, [a, b]]) => [id, b - SETTLE, ""]);
  for (const [id, query] of EXTRA) if (keys?.[id] != null) shots.splice(shots.findIndex(s => s[0] === id) + 1, 0, [id + "_optionB", keys[id], query]);
  if (ONLY.length) shots.splice(0, shots.length, ...shots.filter(s => ONLY.includes(s[0])));
  if (TIMES.length) shots.splice(0, shots.length, ...TIMES.map(t => ["at", t, ""]));
  for (const v of VARIANTS) for (const s of [...shots].filter(s => !s[2])) shots.push([s[0] + "_" + v.replace(/[^a-z0-9]+/gi, "-"), s[1], v]);
  await rm(OUT, { recursive: true, force: true }); await mkdir(OUT, { recursive: true });
  let n = 0, current = "";
  for (const [id, t0, query] of shots) {
    if (query !== current) {   // a variant is the same page with one more URL parameter
      await call("Page.navigate", { url: "file://" + PAGE + "?t=0" + (query ? "&" + query : "") });
      for (let i = 0; i < 80; i++) {
        const r = await call("Runtime.evaluate", { expression: "document.readyState==='complete' && document.fonts.status==='loaded' && typeof window.seek==='function'", returnByValue: true });
        if (r.result.value) break; await sleep(250);
      }
      await sleep(400); current = query;
    }
    const t = +t0.toFixed(2);
    await call("Runtime.evaluate", { expression: `window.seek(${t})`, returnByValue: true });
    await sleep(60);
    const shot = await call("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
    const file = `${String(++n).padStart(2, "0")}_${id}_t${t.toFixed(2)}.png`;
    await writeFile(path.join(OUT, file), Buffer.from(shot.data, "base64"));
    console.log(file);
  }
} finally {
  try { await cdp?.send("Browser.close"); } catch {}
  chrome.kill("SIGTERM");
  await rm(profile, { recursive: true, force: true }).catch(() => {});
}
