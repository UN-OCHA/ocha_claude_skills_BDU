/* OCHA Animation — motion helpers for a pure-function-of-time page.
 *
 * Paste into the page's script (or load it before your render code). Everything here is
 * stateless: pass the time, get the frame. See references/motion-rules.md for the why.
 *
 * Maintained by: OCHA Brand and Design Unit (BDU) — ochavisual@un.org
 */

/* ---------- easing ---------- */
const clamp01 = v => (v < 0 ? 0 : v > 1 ? 1 : v);
const outCubic = p => 1 - Math.pow(1 - p, 3);
const outQuint = p => 1 - Math.pow(1 - p, 5);
const inOutCubic = p => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2);
const linear = p => p;
const lerp = (a, b, p) => a + (b - a) * p;

/* ---------- the one move, forwards and backwards (rule 1) ----------
 * life(tau, start, duration, out, ease) -> q in [0, 1]
 *   tau   time since the scene started
 *   out   0..1 progress of the scene's exit (0 while the scene holds)
 * The entrance eases in over [start, start + duration]; during the exit the same easing runs
 * in reverse, so every element leaves by undoing exactly how it arrived. */
function life(tau, start, duration, out, ease) {
  const e = ease || outCubic;
  const q = e(clamp01((tau - start) / duration));
  return out > 0 ? Math.min(q, e(1 - clamp01(out))) : q;
}

/* Scene window helpers: a scene arrives over ARRIVE and exits over EXIT, ending at `end`. */
const ARRIVE = 0.32, EXIT = 0.5;
const sceneAlpha = (t, start, end) => (t < start || t > end ? 0 : clamp01((t - start) / ARRIVE));
const sceneExit = (t, end) => clamp01((t - (end - EXIT)) / EXIT);

/* ---------- apply a state to an element ---------- */
function rise(el, q, dist) {                 // text: fades up `dist` px; exit sinks
  el.style.opacity = q.toFixed(3);
  el.style.transform = "translateY(" + ((1 - q) * dist).toFixed(2) + "px)";
}
function scaleIn(el, q, from = 0.45) {       // icons: set transform-origin in CSS (rule 3)
  el.style.opacity = q.toFixed(3);
  el.style.transform = "scale(" + (from + (1 - from) * q).toFixed(4) + ")";
}
function growX(el, q) {                      // bars: transform-origin: 0 50%
  el.style.transform = "scaleX(" + q.toFixed(4) + ")";
}
function slideX(el, q, dist = 40) {          // tags that slide in from the right
  el.style.opacity = q.toFixed(3);
  el.style.transform = "translateX(" + ((1 - q) * dist).toFixed(1) + "px)";
}
function drawLine(svgLine, q, reverse = false) {   // needs data-len="<length>" on the element
  const len = +svgLine.dataset.len;
  svgLine.style.strokeDasharray = len;
  svgLine.style.strokeDashoffset = ((reverse ? -1 : 1) * len * (1 - clamp01(q))).toFixed(1);
}
function typeOn(el, text, q) {               // short mono labels only, never reading text
  const v = text.slice(0, Math.round(text.length * clamp01(q)));
  if (el.textContent !== v) el.textContent = v;
}

/* ---------- numbers ---------- */
// Count with the same q that drives its bar (rule 5); counting back down is the exit.
const countTo = (value, q) => value * q;
// Tabular figures in CSS stop the digits jittering: font-variant-numeric: tabular-nums.

/* ---------- wipe transitions (rule 8) ----------
 * A full-frame panel moving translateY(100% -> -100%) with outCubic over `duration` seconds
 * from `start` covers the whole frame when outCubic(p) = 0.5. End the outgoing scene there:
 *   sceneEnd = Math.min(sceneEnd, wipeCoverTime(start, duration)); */
const wipeCoverTime = (start, duration) => start + duration * (1 - Math.cbrt(0.5));
function wipePanel(el, t, start, duration) {
  const p = clamp01((t - start) / duration);
  const y = p <= 0 ? 100 : p >= 1 ? -100 : 100 - 200 * outCubic(p);
  el.style.transform = "translateY(" + y.toFixed(2) + "%)";
}

/* ---------- marker highlight on the text, not the box ----------
 * A band behind big figures whose bottom edge sits `drop` x font-size below the real text
 * baseline (7% reads natural; flush reads stiff). A fixed percentage of the element box
 * drifts with line-height, so measure: a zero-size inline-block probe sits on the baseline.
 * Call once after document.fonts.ready, before the first render. Elements must be laid out
 * (visibility:hidden is fine, display:none is not). */
function alignMarkers(selector, { band = 0.24, drop = 0.07, color = "#FFC800" } = {}) {
  document.querySelectorAll(selector).forEach(el => {
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    const probe = document.createElement("span");
    probe.style.cssText = "display:inline-block;width:0;height:0;vertical-align:baseline";
    el.appendChild(probe);
    const base = probe.getBoundingClientRect().top;
    probe.remove();
    const fs = parseFloat(cs.fontSize), h = el.offsetHeight;   // unscaled layout height
    const bottom = (base - r.top) / r.height * 100 + drop * fs / h * 100;
    const top = bottom - band * fs / h * 100;
    el.style.backgroundImage = `linear-gradient(transparent ${top.toFixed(2)}%, ${color} ${top.toFixed(2)}%, ` +
      `${color} ${bottom.toFixed(2)}%, transparent ${bottom.toFixed(2)}%)`;
  });
}
// CSS for the marked element: display:inline-block; padding:0 .05em;
