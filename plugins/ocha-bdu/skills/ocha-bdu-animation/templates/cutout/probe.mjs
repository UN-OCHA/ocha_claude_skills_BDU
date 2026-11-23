/**
 * Ask the film page a question at given moments, and print the answer.
 *
 *   node --experimental-websocket tools/probe.mjs --times 5.9,6.4,6.9 \
 *        --expr "document.querySelectorAll('#decor path').length"
 *
 * Why this exists: a still only shows what a fixed crop of the SCREEN contains, and the camera
 * moves, so comparing two stills pixel by pixel compares two different parts of the world. This
 * reads the painted values themselves (a trim, a computed style, a bounding box) at an exact time,
 * which is what "test the result, not the instruction" needs. Same headless Chrome as
 * stills.mjs (headless_chrome.mjs, beside this file), so the page is in exactly the state a rendered frame would be in.
 */
import path from "node:path";
import { fileURLToPath } from "node:url";
import { openFilm, sleep } from "./headless_chrome.mjs";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const arg = (n, f) => { const i = argv.indexOf("--" + n); return i === -1 ? f : argv[i + 1]; };
const PAGE = path.resolve(HERE, arg("page", "film/world.html"));
const TIMES = (arg("times", "") || "").split(",").filter(Boolean).map(Number);
const EXPR = arg("expr", "null");
const QUERY = arg("query", "");
if (!TIMES.length) { console.error("--times is required"); process.exit(1); }

let film;
try {
  film = await openFilm({ page: PAGE, query: QUERY });
  for (const t of TIMES) {
    await film.evaluate(`window.seek(${t})`);
    await sleep(60);
    // Per moment: an element missing at one time must not lose the answers at the others.
    try { console.log(`t=${t.toFixed(2)}  ${await film.evaluate(`JSON.stringify((() => (${EXPR}))())`)}`); }
    catch (e) { console.log(`t=${t.toFixed(2)}  error: ${e.message.split("\n")[0]}`); process.exitCode = 1; }
  }
} catch (e) {
  console.error(e.message);
  process.exitCode = 1;   // not process.exit(): on Windows that can cut off the last lines of piped output
} finally {
  await film?.close();
}
