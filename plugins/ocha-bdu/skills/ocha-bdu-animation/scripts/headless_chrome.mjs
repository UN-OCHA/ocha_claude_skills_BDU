/**
 * Open a pure-function-of-time HTML film in the Chrome already installed on the machine, headless,
 * and drive it over the DevTools protocol. Shared by render_frames.mjs, check_film.mjs and the cut-out
 * kit's stills, probe and check_sync tools (new_cutout_film.py copies it into each job's tools/).
 *
 *   import { openFilm } from "./headless_chrome.mjs";
 *   const film = await openFilm({ page: "/abs/film.html", width: 1920, height: 1080 });
 *   await film.evaluate("window.seek(1.5)");
 *   const png = await film.call("Page.captureScreenshot", { format: "png" });
 *   await film.close();
 *
 * No npm install: the DevTools client below is ~30 lines over Node 20+'s WebSocket
 * (run node with --experimental-websocket on Node 20; Node 22+ has it built in).
 *
 * Why it is built this way (keep these when changing it):
 *   - Each Chrome gets its own temporary profile and port 0, and reports the port it chose in
 *     DevToolsActivePort. Several Chromes (render workers, a check while a render runs) can never
 *     collide on a port. The fixed ports used before (9223, 9323 + CDP_PORT_OFFSET) did.
 *   - --disable-gpu is load-bearing: software drawing gives byte-identical frames run after run.
 *     GPU drawing was twice as fast but not repeatable: 4 of 40 SG-film frames differed between
 *     two GPU runs (measured November 2026). Removing it breaks the frame-hash proof that a
 *     re-render changed only what was asked.
 *   - The page URL is built with pathToFileURL, so Windows paths (C:\…) and spaces work.
 *
 * Maintained by: OCHA Brand and Design Unit (BDU) — ochavisual@un.org
 */

import { spawn } from "node:child_process";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import os from "node:os";
import { pathToFileURL } from "node:url";

export const sleep = ms => new Promise(r => setTimeout(r, ms));

/** The Chrome binary: CHROME if set, otherwise the standard install places on macOS, Windows, Linux. */
function findChrome() {
  if (process.env.CHROME) return process.env.CHROME;
  const env = process.env, home = os.homedir();
  const places = {
    darwin: ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
             path.join(home, "Applications/Google Chrome.app/Contents/MacOS/Google Chrome")],
    win32: [env.PROGRAMFILES, env["PROGRAMFILES(X86)"], env.LOCALAPPDATA]
             .filter(Boolean).map(d => path.join(d, "Google", "Chrome", "Application", "chrome.exe")),
    linux: ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/usr/bin/chromium", "/usr/bin/chromium-browser"],
  }[process.platform] || [];
  return places.find(p => existsSync(p)) || places[0] || "";
}

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
    // If Chrome dies mid-render, fail every waiting call instead of hanging forever.
    ws.addEventListener("close", () => {
      for (const p of this.pending.values()) p.reject(new Error("Chrome closed the connection"));
      this.pending.clear();
    });
  }
  send(method, params = {}, sessionId) {
    const id = ++this.id, msg = { id, method, params };
    if (sessionId) msg.sessionId = sessionId;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify(msg));
    });
  }
  static async attach(url) {
    const ws = new WebSocket(url);
    await new Promise((res, rej) => { ws.addEventListener("open", res, { once: true }); ws.addEventListener("error", rej, { once: true }); });
    return new CDP(ws);
  }
}

/**
 * Launch Chrome, open the page and wait until it is ready to seek (fonts loaded, window.seek present).
 * `query` adds URL parameters ("pills=word"); load(query) reopens the same page with others.
 * Returns { call, evaluate, load, duration, close }; duration is window.DURATION, undefined if the page
 * has none (the tools that need it check). Always call close(), also on errors.
 */
export async function openFilm({ page, width = 1920, height = 1080, scale = 1, query = "" }) {
  const chromePath = findChrome();
  if (!existsSync(page)) throw new Error(`No page at ${page}`);
  if (!existsSync(chromePath)) throw new Error(`Chrome not found at ${chromePath} — set CHROME=/path/to/chrome`);

  const profile = await mkdtemp(path.join(os.tmpdir(), "ocha-animation-chrome-"));
  const chrome = spawn(chromePath, [
    "--headless=new", "--remote-debugging-port=0", "--remote-allow-origins=*",
    "--hide-scrollbars", "--disable-gpu", "--force-device-scale-factor=1",
    `--window-size=${width},${height}`, "--no-first-run", "--no-default-browser-check",
    `--user-data-dir=${profile}`, "about:blank",
  ], { stdio: "ignore" });
  const exited = new Promise(res => chrome.once("exit", res));
  let cdp;

  const close = async () => {
    try { await cdp?.send("Browser.close"); } catch {}
    if (chrome.exitCode === null) {
      // unref: a timer still waiting would hold the tool open for 5 s after Chrome has gone.
      const done = await Promise.race([exited.then(() => true), new Promise(r => setTimeout(r, 5000, false).unref())]);
      if (!done) { chrome.kill(); await exited; }
    }
    // Windows keeps the profile locked for a moment after Chrome exits: retry the delete.
    await rm(profile, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 }).catch(() => {});
  };

  try {
    // Chrome writes "<port>\n/devtools/browser/<id>" here once it listens.
    let endpoint;
    for (let i = 0; i < 120 && !endpoint; i++) {
      if (chrome.exitCode !== null) throw new Error(`Chrome exited at start (code ${chrome.exitCode})`);
      try {
        const [port, wsPath] = (await readFile(path.join(profile, "DevToolsActivePort"), "utf8")).split(/\r?\n/);
        if (port && wsPath) endpoint = `ws://127.0.0.1:${port}${wsPath}`;
      } catch {}
      if (!endpoint) await sleep(250);
    }
    if (!endpoint) throw new Error("Chrome did not start its DevTools port within 30 s");
    cdp = await CDP.attach(endpoint);

    const { targetId } = await cdp.send("Target.createTarget", { url: "about:blank" });
    const { sessionId } = await cdp.send("Target.attachToTarget", { targetId, flatten: true });
    const call = (m, p) => cdp.send(m, p, sessionId);
    // An exception in the page (a seek that throws) must stop the run, not pass as "undefined".
    const evaluate = async expression => {
      const r = await call("Runtime.evaluate", { expression, returnByValue: true });
      if (r.exceptionDetails) throw new Error(`The page failed on ${expression.slice(0, 60)}: ${r.exceptionDetails.exception?.description || r.exceptionDetails.text}`);
      return r.result.value;
    };

    await call("Page.enable");
    await call("Runtime.enable");
    await call("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: scale, mobile: false });
    // Wait for fonts and the seek hook before the first grab: frames taken earlier use
    // fallback fonts and wrong measurements.
    const load = async (params = "") => {
      // Ready only on a NEW document: on a reload the old page would answer "ready" just the same.
      const old = await evaluate("performance.timeOrigin");
      await call("Page.navigate", { url: pathToFileURL(page).href + "?t=0" + (params ? "&" + params : "") });
      let ready = false;
      for (let i = 0; i < 80 && !ready; i++) {
        ready = await evaluate(`performance.timeOrigin !== ${old} && document.readyState==='complete' && document.fonts.status==='loaded' && typeof window.seek==='function'`);
        if (!ready) await sleep(250);
      }
      if (!ready) throw new Error("The page was not ready after 20 s: fonts still loading, or no window.seek.");
      await sleep(400);
    };
    await load(query);

    const duration = await evaluate("window.DURATION");
    return { call, evaluate, load, duration, close };
  } catch (e) {
    await close();
    throw e;
  }
}
