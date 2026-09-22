/**
 * Ask the film page a question at given moments, and print the answer.
 *
 *   node --experimental-websocket assets/build/probe.mjs --times 5.9,6.4,6.9 \
 *        --expr "document.querySelectorAll('#decor path').length"
 *
 * Why this exists: a still only shows what a fixed crop of the SCREEN contains, and the camera
 * moves, so comparing two stills pixel by pixel compares two different parts of the world. This
 * reads the painted values themselves (a trim, a computed style, a bounding box) at an exact time,
 * which is what "test the result, not the instruction" needs. Same headless-Chrome/DevTools
 * approach as stills.mjs, so the page is in exactly the state a rendered frame would be in.
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
const TIMES = (arg("times", "") || "").split(",").filter(Boolean).map(Number);
const EXPR = arg("expr", "null");
const QUERY = arg("query", "");
const PORT = 9332;
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
if (!existsSync(PAGE)) { console.error(`No page at ${PAGE}`); process.exit(1); }
if (!TIMES.length) { console.error("--times is required"); process.exit(1); }

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

const profile = path.join(os.tmpdir(), `ocha-probe-${process.pid}`);
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
  await call("Page.navigate", { url: "file://" + PAGE + "?t=0" + (QUERY ? "&" + QUERY : "") });
  for (let i = 0; i < 80; i++) {
    const r = await call("Runtime.evaluate", { expression: "document.readyState==='complete' && document.fonts.status==='loaded' && typeof window.seek==='function'", returnByValue: true });
    if (r.result.value) break; await sleep(250);
  }
  await sleep(400);
  for (const t of TIMES) {
    await call("Runtime.evaluate", { expression: `window.seek(${t})`, returnByValue: true });
    await sleep(60);
    const r = await call("Runtime.evaluate", { expression: `JSON.stringify((() => (${EXPR}))())`, returnByValue: true });
    console.log(`t=${t.toFixed(2)}  ${r.result.value}`);
  }
} finally {
  try { await cdp?.send("Browser.close"); } catch {}
  chrome.kill("SIGTERM");
  await rm(profile, { recursive: true, force: true }).catch(() => {});
}
