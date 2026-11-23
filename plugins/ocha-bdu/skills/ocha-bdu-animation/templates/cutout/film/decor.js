/* Background drawings tied to the voice (cut-out style; SG Awards film, Javier, 19 Sept 2026): faint
   lines drawn on the ground behind every piece — a seismic scribble on "earthquake", a clock on "every
   minute counts", bursts and ripples on the moments that land. They are
   drawings, not paper: no cut edge, no shadow, one step darker than the dot grid, and they move
   on stop-motion holds like everything else. Every cue is a word of the voiceover (W(line)[word]),
   every place comes from FILM.pos, so they follow the voice and the scenes if either changes. */
(function () {
  const F = window.FILM;
  if (F.V1) return;   // the first test had no background life
  const { line, scene, W, clamp, outCubic, inOutCubic, prog, lerp, hash, unit01, MAT, paper, world, svgEl, add, pos } = F;

  const svg = svgEl("svg", { width: 1, height: 1 });
  svg.id = "decor"; svg.style.overflow = "visible"; svg.style.position = "absolute"; svg.style.left = "0"; svg.style.top = "0";
  world.insertBefore(svg, world.firstChild);   // under everything, links included
  // a second layer on top of every piece, for the few lines that would be lost under the wall of numbers
  const svgTop = svgEl("svg", { width: 1, height: 1 });
  svgTop.id = "decor-top"; svgTop.style.overflow = "visible"; svgTop.style.position = "absolute"; svgTop.style.left = "0"; svgTop.style.top = "0";
  world.appendChild(svgTop);

  const INK = "#C3BAB2";                       // faint: one step darker than the dot grid
  const BLUE = "rgba(0, 158, 219, 0.45)";      // for the moments that belong to the tool
  const RED = "rgba(237, 24, 71, 0.75)";       // for the questions nobody can answer yet (bright red: a shape, not text)
  let did = 900;
  const items = [];
  const st = (id, t, cue) => paper(id, t, cue, MAT.line).t;   // stepped, on the decoration's own clock
  const line_ = (attrs, layer = svg) => svgEl("line", { stroke: INK, "stroke-width": 5, "stroke-linecap": "round", ...attrs }, layer);
  const hide = n => { n.style.visibility = "hidden"; };
  const show = n => { n.style.visibility = "visible"; };

  // ---------- primitives ----------
  // a path drawn on over dIn, held, then wiped away from its start over dOut
  // `d` is a path, or a FUNCTION of time that returns one: a line that keeps moving while it is on
  // screen (review round 3: "adding some movement to the lines while they are on screen rather than
  // stay static. Subtle and smooth"). The movement runs on the smooth clock (t), because he asked for
  // smooth; the draw-on and the wipe-off stay on the stop-motion clock like every other drawing.
  // pathLength=1 keeps the trim right however the shape changes. (A first try only breathed the trim
  // by 5% — it read as static, so the SHAPE moves now.)
  function stroke(d, at, until, { color = INK, width = 5, dIn = 0.45, dOut = 0.4 } = {}) {
    const moving = typeof d === "function";
    const id = did++, p = svgEl("path", { d: moving ? d(0) : d, fill: "none", stroke: color, "stroke-width": width, "stroke-linecap": "round", "stroke-linejoin": "round", pathLength: 1 }, svg);
    items.push(t => {
      const s = st(id, t, at), a = inOutCubic(prog(s, at, dIn)), b = until == null ? 0 : inOutCubic(prog(s, until, dOut));
      if (a - b < 0.002) return hide(p);
      if (moving) p.setAttribute("d", d(t - at));
      show(p); p.setAttribute("stroke-dasharray", `${a - b} 2`); p.setAttribute("stroke-dashoffset", `${-b}`);
    });
  }
  // rays that shoot out from a centre and fly off: the cartoon burst
  function burst(x, y, at, { n = 10, r0 = 90, r1 = 160, color = INK, width = 5, dur = 0.55, rot = 0, top = false } = {}) {
    const id = did++;
    const rays = [...Array(n)].map((_, i) => ({ a: rot + (i / n) * Math.PI * 2 + hash(id, i) * 0.14, k: 0.75 + 0.5 * unit01(id, i + 40), l: line_({ stroke: color, "stroke-width": width }, top ? svgTop : svg) }));
    items.push(t => {
      const s = st(id, t, at), p = prog(s, at, dur), on = s >= at && p < 1;
      for (const r of rays) {
        if (!on) { hide(r.l); continue; }
        show(r.l);
        const R1 = r0 + (r1 - r0) * r.k, ra = lerp(r0, R1, inOutCubic(clamp((p - 0.25) / 0.75))), rb = lerp(r0, R1, outCubic(clamp(p / 0.6)));
        r.l.setAttribute("x1", x + ra * Math.cos(r.a)); r.l.setAttribute("y1", y + ra * Math.sin(r.a));
        r.l.setAttribute("x2", x + rb * Math.cos(r.a)); r.l.setAttribute("y2", y + rb * Math.sin(r.a));
      }
    });
  }
  // ripples: circles that open out and fade
  function rings(x, y, at, { n = 3, r0 = 60, r1 = 260, gap = 0.16, dur = 0.9, color = INK, width = 4, top = false } = {}) {
    const id = did++, cs = [...Array(n)].map(() => svgEl("circle", { cx: x, cy: y, fill: "none", stroke: color, "stroke-width": width }, top ? svgTop : svg));
    items.push(t => {
      const s = st(id, t, at);
      cs.forEach((c, i) => {
        const p = prog(s, at + i * gap, dur);
        if (p <= 0 || p >= 1) return hide(c);
        show(c); c.setAttribute("r", lerp(r0, r1, outCubic(p))); c.setAttribute("stroke-opacity", (1 - p).toFixed(2));
      });
    });
  }
  // streaks passing through, along a direction
  function speed(x, y, at, { n = 8, w = 1600, h = 700, dir = Math.PI, dur = 0.55, color = INK, width = 5 } = {}) {
    const id = did++, ux = Math.cos(dir), uy = Math.sin(dir), nx = -uy, ny = ux;
    const ls = [...Array(n)].map((_, i) => ({ l: line_({ stroke: color, "stroke-width": width }), off: hash(id, i) * h / 2, len: 140 + 200 * unit01(id, i + 20), delay: 0.22 * unit01(id, i + 60) }));
    items.push(t => {
      const s = st(id, t, at);
      for (const k of ls) {
        const p = prog(s, at + k.delay, dur);
        if (p <= 0 || p >= 1) { hide(k.l); continue; }
        show(k.l);
        const c = lerp(-w / 2, w / 2, p), L = k.len * Math.sin(Math.PI * p), cx = x + nx * k.off + ux * c, cy = y + ny * k.off + uy * c;
        k.l.setAttribute("x1", cx - ux * L / 2); k.l.setAttribute("y1", cy - uy * L / 2);
        k.l.setAttribute("x2", cx + ux * L / 2); k.l.setAttribute("y2", cy + uy * L / 2);
      }
    });
  }
  // a clock face: the circle draws on, the ticks pop round, one hand ticks forward pose by pose
  // Every measurement is a FRACTION of r, so a small clock and a big one are the same drawing at two
  // sizes. They used to be fixed pixels (ticks 20 px, hand r−34), which on the little r=60 face made
  // the ticks reach a third of the way in and the hand a stub — two clocks that looked unrelated
  // (review round 3: "a consistent look for all the clocks"). The fractions below are the r=150
  // clock's own proportions, so the big one is unchanged and the small one now matches it.
  const TICK_OUT = 0.933, TICK_IN_BIG = 0.8, TICK_IN_SMALL = 0.867, HAND = 0.773, HUB = 0.053;
  // Each clock also says WHEN it is on screen (F.clocks[key]: drawn on at `at`, gone at `until`), so its tick in sfx.js
  // reads the picture's own timing instead of a retyped copy of it.
  F.clocks = {};
  function clock(x, y, r, at, until, { turns = 1, color = INK, width = Math.max(3, r / 30), key = null } = {}) {
    stroke(`M ${x} ${y - r} a ${r} ${r} 0 1 1 -0.01 0`, at, until, { color, width, dIn: 0.5 });
    const id = did++;
    const ticks = [...Array(12)].map((_, i) => {
      const a = (i / 12) * Math.PI * 2 - Math.PI / 2, big = i % 3 === 0, inner = r * (big ? TICK_IN_BIG : TICK_IN_SMALL);
      return { at: at + 0.18 + i * 0.03, l: line_({ stroke: color, "stroke-width": big ? width + 1 : width - 1,
        x1: x + inner * Math.cos(a), y1: y + inner * Math.sin(a), x2: x + r * TICK_OUT * Math.cos(a), y2: y + r * TICK_OUT * Math.sin(a) }) };
    });
    const hand = line_({ stroke: color, "stroke-width": width + 1, x1: x, y1: y }), hub = svgEl("circle", { cx: x, cy: y, r: Math.max(3, r * HUB), fill: color }, svg);
    const t1 = until != null ? until : at + 3;
    if (key) F.clocks[key] = { at, until: t1 + 0.1 };   // its ticks and hand hide at t1 + 0.1 (below)
    items.push(t => {
      const s = st(id, t, at), gone = s >= t1 + 0.1;
      ticks.forEach(k => (s >= k.at && !gone ? show(k.l) : hide(k.l)));
      if (s < at + 0.3 || gone) { hide(hand); hide(hub); return; }
      show(hand); show(hub);
      const a = -Math.PI / 2 + turns * Math.PI * 2 * clamp((s - at - 0.3) / (t1 - at - 0.3));
      hand.setAttribute("x2", x + r * HAND * Math.cos(a)); hand.setAttribute("y2", y + r * HAND * Math.sin(a));
    });
  }
  // path makers. The last argument is the moving part: 0 draws the still shape.
  // zigzag: given a time `tt`, each peak swells and settles in a wave that travels along the line
  const zigzag = (x, y, w, amp, k, tt = null) => { let d = `M ${x - w / 2} ${y}`; for (let i = 1; i <= k; i++) { const shake = tt == null ? 1 : 1 + TREMOR * Math.sin(TREMOR_SPEED * tt - i * 0.9); d += ` L ${x - w / 2 + (w * i) / k} ${y + (i === k ? 0 : (i % 2 ? -amp : amp) * (0.55 + 0.45 * Math.sin(i * 1.7) ** 2) * shake)}`; } return d; };
  // wave: `phase` slides the crests along, so the water flows. The path STARTS on the sine curve: it used to
  // start at the baseline and jump to the curve's first point, which put a little hook on the left tip once
  // the phase moved (review round 3: "the tip of the floods lines seems deformed"). The last point lands
  // exactly on the right end, so both tips are clean.
  const wave = (x, y, w, amp, len, phase = 0) => {
    const at = u => `${x - w / 2 + u} ${y + amp * Math.sin((u / len) * Math.PI * 2 + phase)}`;
    let d = `M ${at(0)}`; for (let u = 6; u < w; u += 6) d += ` L ${at(u)}`; return d + ` L ${at(w)}`;
  };
  // spiral: `rot` turns the whole swirl about its centre
  const spiral = (x, y, r0, r1, turns, rot = 0) => { let d = ""; const n = 70; for (let i = 0; i <= n; i++) { const f = i / n, a = f * turns * Math.PI * 2 + rot, r = lerp(r0, r1, f); d += `${i ? " L" : "M"} ${x + r * Math.cos(a)} ${y + r * Math.sin(a)}`; } return d; };
  // How much the crisis lines move while held — small on purpose ("subtle and smooth"): the waves drift
  // about 18 px a second, the swirl turns about 25° a second, the tremor swells the peaks by ±20 %.
  const FLOW = 2.0, SWIRL = 0.45, TREMOR = 0.2, TREMOR_SPEED = 2.6;
  const arc = (x, y, r, a0, a1) => `M ${x + r * Math.cos(a0)} ${y + r * Math.sin(a0)} A ${r} ${r} 0 0 1 ${x + r * Math.cos(a1)} ${y + r * Math.sin(a1)}`;
  // An arrowhead at (x2, y2), built FROM the direction of the segment that arrives there, so both
  // barbs are the same length and sit symmetrically about the line. Hand-written coordinates had
  // one barb 42° out and the tip off the line's end (review round 3: "the tip of the arrow looks odd").
  const arrowHead = (x1, y1, x2, y2, len = 52, spread = 0.42) => {
    const a = Math.atan2(y2 - y1, x2 - x1);
    return `M ${x2 - len * Math.cos(a - spread)} ${y2 - len * Math.sin(a - spread)} L ${x2} ${y2} L ${x2 - len * Math.cos(a + spread)} ${y2 - len * Math.sin(a + spread)}`;
  };

  // the drawing tools, for scenes.js too (a scene can draw its own line on a cue)
  F.draw = { stroke, burst, rings, speed, clock, zigzag, wave, spiral, arc, arrowHead, INK, BLUE, RED };

  // ================= THE FILM'S DRAWINGS (the demo's: replace them with the film's) =================
  // Each is cued from FILM.pos, which scenes.js fills from the voice, so a drawing can never drift from
  // the piece it belongs to. The SG film had, among others: a seismic line on "earthquake", a turning
  // swirl on "hurricane", flowing waves on "floods", a burst on "armed conflict", ripples round the globe
  // on "everywhere", a clock on "every minute counts", streaks on "fast", a rising line on "fundraising".
  const [quake] = pos.crises;
  stroke(tt => zigzag(quake.x, quake.y + 128, 230, 26, 11, tt), quake.at + 0.1, pos.crisesOff, { dIn: 0.35 });   // "crisis": a seismic line that keeps trembling
  burst(pos.question.x, pos.question.y, pos.question.at + 0.08, { n: 11, r0: 140, r1: 215, color: RED });          // "questions": a red burst
  rings(pos.answer.x, pos.answer.y, pos.answer.at + 0.05, { n: 2, r0: 110, r1: 250, color: BLUE });              // "answers": blue ripples
  rings(pos.crowd.x, pos.crowd.y, pos.crowd.at - 0.1, { n: 3, r0: 180, r1: 720, gap: 0.18, dur: 1.1 });           // "everyone"

  add(t => { for (const f of items) f(t); });
})();
