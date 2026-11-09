/**
 * Render approval stills from the film page: one settled frame per scene window.
 *
 *   node --experimental-websocket tools/stills.mjs [--page film/index.html] [--out stills]
 *
 * Reads window.WINDOWS from the page and grabs each scene 0.35 s before its window ends,
 * when everything in it has arrived. Same headless Chrome as the ocha-animation skill's
 * render_frames.mjs (headless_chrome.mjs, beside this file), so a still is an exact frame of the film.
 */
import { mkdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { openFilm, sleep } from "./headless_chrome.mjs";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const arg = (n, f) => { const i = argv.indexOf("--" + n); return i === -1 ? f : argv[i + 1]; };
const PAGE = path.resolve(HERE, arg("page", "film/world.html"));
const OUT = path.resolve(HERE, arg("out", "stills"));
const SETTLE = 0.35;
const VARIANTS = (arg("variants", "") || "").split(",").filter(Boolean);   // extra renders of every key, one per query string
const ONLY = (arg("keys", "") || "").split(",").filter(Boolean);
const TIMES = (arg("times", "") || "").split(",").filter(Boolean).map(Number);   // --times 68.5,68.9: any moments, instead of the named ones
const EXTRA = VARIANTS.length ? [] : [["s1", "pills=word"]];

let film;
try {
  film = await openFilm({ page: PAGE });
  const { call, evaluate, load } = film;
  const err = await evaluate("window.__errors || null");
  if (err) console.log("page errors:", err);
  const keys = await evaluate("window.KEYS || null");
  const wins = await evaluate("window.WINDOWS");
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
      await load(query); current = query;
    }
    const t = +t0.toFixed(2);
    await evaluate(`window.seek(${t})`);
    await sleep(60);
    const shot = await call("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
    const file = `${String(++n).padStart(2, "0")}_${id}_t${t.toFixed(2)}.png`;
    await writeFile(path.join(OUT, file), Buffer.from(shot.data, "base64"));
    console.log(file);
  }
} catch (e) {
  console.error(e.message);   // a plain message for the person running it, not a stack trace
  process.exitCode = 1;   // not process.exit(): on Windows that can cut off the last lines of piped output
} finally {
  await film?.close();
}
