/* The CUT-OUT engine (ocha-animation, cut-out style): ONE WORLD. Time, paper, camera, links and
   the spoken words. The look: flat OCHA geometry as paper cut-outs (hand-cut edges, hard shadows,
   stop-motion wobble), a camera that glides through one world, words that land as they are spoken.
   Made for the SG Awards 2026 Dataviz film (locked 19 Sept 2026); the notes below say which review
   comment set each value, so a change is made knowing why it is what it is.
   A film is: words.js (which words sit on colour, per-line options), scenes.js (the pieces, cued
   from the voice), decor.js (the background drawings), score.js (the sound score). Each registers
   its drawing with FILM.add(fn) and its camera moves with FILM.cam(); world.html loads them, then
   calls FILM.start(). Change the film in those files; change this one only to change the engine.
   Pure function of time (ocha-animation engine): render(t) sets everything from t.
   ?style=v1 shows a flat look (no paper, no leans); ?text=pill|marker the other two word treatments. */
(function () {
  const TL = window.TIMELINE, I = window.ICONS, WF = window.WF;
  const line = n => TL.lines.find(l => l.line === n);
  const scene = n => TL.scenes.find(s => s.id === n);
  const W = n => TL.words.filter(w => w.line === n);
  const params = new URLSearchParams(location.search);
  const STYLE = params.get("style") || "cutout";       // cutout (locked) | v1 (the first test: flat, no paper, no leans)
  const V1 = STYLE === "v1";
  const TEXT = params.get("text") || (V1 ? "pill" : "cutout");   // cutout | pill | marker
  const WOBBLE = !V1 && params.get("wobble") !== "0";
  const END = TL.duration;   // the whole film, its ending included

  // ---------- motion helpers (ocha-animation/references/motion-rules.md) ----------
  const clamp = v => (v < 0 ? 0 : v > 1 ? 1 : v);
  const outCubic = p => 1 - Math.pow(1 - p, 3);
  const outQuint = p => 1 - Math.pow(1 - p, 5);
  const inOutCubic = p => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2);
  const outBack = p => { const c = 1.3; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); };
  const prog = (t, a, d) => clamp((t - a) / d);
  const lerp = (a, b, p) => a + (b - a) * p;
  const seeded = seed => () => ((seed = (seed * 9301 + 49297) % 233280) / 233280);
  const life = (t, tIn, tOut, d, ease) => Math.min(ease(prog(t, tIn, d)), tOut == null ? 1 : ease(1 - prog(t, tOut, d)));
  const hash = (a, b) => { let h = (a * 374761393 + b * 668265263) | 0; h = (h ^ (h >>> 13)) * 1274126177; h = h ^ (h >>> 16); return ((h >>> 0) % 10000) / 5000 - 1; };
  const unit01 = (id, salt) => (hash(id, salt) + 1) / 2;

  // ---------- stop motion: every piece of paper keeps its own clock ----------
  // A piece moves on holds (poses), and between poses it wobbles and its cut edge "boils". Its
  // rates come from its id and its phase from its cue, so it lands exactly on its cue and no two
  // pieces tick together (Javier, 19 Sept 2026: the wobble must be independent for every object,
  // "more natural"). The camera stays continuous. Per material: amp px and rot deg of the wobble,
  // the cut-edge filter, poses per second of its moves (step) and of its wobble (boil).
  const MAT = {
    badge: { amp: 1.1, rot: 0.5, edge: "cut", step: [12, 10], boil: [12, 10, 8] },   // calmed from 1.6/0.7 (review round 3: "too much shaking when the camera zooms out")
    word: { amp: 0.8, rot: 0.45, edge: "cutw", step: [12], boil: [8, 7, 6] },      // calmer than v02 (19 Sept)
    num: { amp: 1.0, rot: 0.5, edge: null, step: [12, 10], boil: [10, 8] },
    chart: { amp: 0, rot: 0, edge: "cutc", step: [12], boil: [] },             // charts sit perfectly still, the tool's clean result (review round 1: "the shake of the center chart")
    person: { amp: 0.5, rot: 0.25, edge: "cutp", step: [12], boil: [5, 4] },   // the crowd: calm, soft shadows (review round 1: "people are shaking too much")
    line: { amp: 0, rot: 0, edge: null, step: [12, 10], boil: [8] },           // lines drawn on the background
    // the screen, report and phone in "advocacy": the film's own stop-motion wobble, like every other
    // piece, but on a FIXED edge. History: at badge strength with a boiling 5 px edge (v06) their big
    // outlines crawled — "too shaky"; perfectly still (v07) looked dead; smooth sine sways (v08, v09)
    // were never seen, because the camera leaves these devices ~1.5 s after they settle — a 1.7 s
    // cycle is one slow lean in that time (measured on the painted frames of v10). Round 4: "wobble shaky
    // effect not visible on 3 devices. Apply it". So: pose changes 7–8 times a second (visible at
    // once), a little calmer than a badge, and `fixedEdge` so the outline itself never crawls.
    device: { amp: 1.2, rot: 0.45, edge: "cutc", step: [12, 10], boil: [8, 7], fixedEdge: true },
  };
  const rateOf = (list, id, salt) => list[Math.min(list.length - 1, Math.floor(unit01(id, salt) * list.length))];
  function paper(id, t, cue, m) {
    if (V1) return { t, dx: 0, dy: 0, r: 0, filter: "none" };   // v1 moved continuously, flat
    const sr = rateOf(m.step, id, 3);
    // each pose shows the move as it stands at the END of the pose, so the first pose of an entrance
    // is already visible on its cue — a word lands on its sound, never a hold late
    const st = t < cue ? t : cue + (Math.floor((t - cue) * sr + 1e-6) + 1) / sr;
    const w = WOBBLE ? 1 : 0;
    // wobble poses, on a phase of their own; no boil rates = one pose for ever (a still piece)
    const b = m.boil.length ? Math.floor((t - cue) * rateOf(m.boil, id, 5) + unit01(id, 9) + 1e-6) : 0;
    // fixedEdge: the piece wobbles from pose to pose but its cut edge keeps one seed (no crawl round a big outline)
    const seed = m.fixedEdge ? id : b + id;
    return { t: st, dx: w * m.amp * hash(id, b), dy: w * m.amp * hash(id + 7, b), r: w * m.rot * hash(id + 13, b),
             filter: m.edge ? `url(#${m.edge}${((seed % 5) + 5) % 5})` : "none" };
  }

  const stage = document.getElementById("stage");
  // the paper filters: a hand-cut edge (displacement) and a hard offset shadow, five seeds to boil
  // between; badges cut roughest, word labels a little finer, charts finest so they read as steady;
  // people small and soft-shadowed. [name, edge displacement px, shadow dx, dy, shadow opacity]
  const NS = "http://www.w3.org/2000/svg";
  const defs = document.createElementNS(NS, "svg");
  defs.setAttribute("width", "0"); defs.setAttribute("height", "0"); defs.style.position = "absolute";
  defs.innerHTML = [["cut", 5, 6, 8, 0.17], ["cutw", 4, 6, 8, 0.17], ["cutc", 2.5, 6, 8, 0.17], ["cutp", 2.5, 3, 4, 0.1]].map(([name, scale, dx, dy, op]) => [0, 1, 2, 3, 4].map(i =>
    `<filter id="${name}${i}" x="-25%" y="-25%" width="150%" height="150%" color-interpolation-filters="sRGB">
      <feTurbulence type="fractalNoise" baseFrequency="0.045" numOctaves="2" seed="${11 + i * 7}" result="n"/>
      <feDisplacementMap in="SourceGraphic" in2="n" scale="${scale}" xChannelSelector="R" yChannelSelector="G" result="cut"/>
      <feOffset in="cut" dx="${dx}" dy="${dy}" result="off"/>
      <feFlood flood-color="#1B1B1A" flood-opacity="${op}" result="fl"/>
      <feComposite in="fl" in2="off" operator="in" result="sh"/>
      <feMerge><feMergeNode in="sh"/><feMergeNode in="cut"/></feMerge></filter>`).join("")).join("");
  stage.appendChild(defs);
  const backdrop = document.createElement("div"); backdrop.id = "backdrop"; stage.appendChild(backdrop);
  const world = document.createElement("div"); world.id = "world"; stage.appendChild(world);
  const el = (tag, cls, parent, html) => {
    const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html;
    (parent || world).appendChild(e); return e;
  };
  const svgEl = (tag, attrs, parent) => {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  };
  const setXY = (n, x, y) => { n.style.left = x + "px"; n.style.top = y + "px"; };
  // pop in, stepped, with wobble; the exit is the entrance in reverse. p = paper(...)
  const popStyle = (n, q, p, from = 0.4) => {
    n.style.opacity = clamp(q * 1.6);
    n.style.transform = `translate(calc(-50% + ${p.dx}px), calc(-50% + ${p.dy}px)) rotate(${p.r}deg) scale(${from + (1 - from) * q})`;
    n.style.visibility = q <= 0.001 ? "hidden" : "visible";
    if (q > 0.001) n.style.filter = p.filter;
  };

  // ---------- pieces: paper that pops in on a cue, wobbles on its own clock, and may leave again ----------
  // piece(html, cls, x, y, at, until, opts) — x, y are its CENTRE in the world; at / until are film times,
  // always read from the voice (W(line)[word].start), never typed as seconds. opts: w, h (px); mat (default
  // MAT.badge); from (the size it pops from, 0.4); parent (default the world); label (a text label: the
  // paper — ::before — takes the cut edge, the letters stay crisp); twin (move exactly with another piece,
  // on the same clock: a monitor's stand must not sway on its own and open a gap at the joint).
  // badge(icon, …) is a piece holding a humanitarian icon on a round white paper badge (.qb).
  const pieces = [];
  let pid = 600;
  const piece = (html, cls, x, y, at, until, opts = {}) => {
    const n = el("div", cls, opts.parent || world, html); setXY(n, x, y);
    if (opts.w) n.style.width = opts.w + "px";
    if (opts.h) n.style.height = opts.h + "px";
    const p = { n, x, y, at, until, cls, mat: opts.mat || MAT.badge, from: opts.from != null ? opts.from : 0.4, label: !!opts.label, id: opts.twin ? opts.twin.id : pid++ };
    pieces.push(p); return p;
  };
  const badge = (icon, x, y, at, until, cls = "", opts = {}) => piece(`<span class="icon">${I[icon]}</span>`, "qb cut " + cls, x, y, at, until, opts);
  function renderPieces(t) {
    for (const p of pieces) {
      const s = paper(p.id, t, p.at, p.mat), q = life(s.t, p.at, p.until, 0.5, outBack);
      if (!p.label) { popStyle(p.n, q, s, p.from); continue; }
      popStyle(p.n, q, { ...s, filter: "none" }, p.from);   // a text label: the paper takes the cut edge, the letters stay crisp
      p.n.style.setProperty("--cut", s.filter);
    }
  }

  // ---------- the camera: keyframes from the scene files, leans, and a gentle breath ----------
  const S = 960, SY = 460, CAM = [], FOCUS = [];
  const cam = (t, x, y, z) => CAM.push([t, x, y, z]);
  const focus = f => FOCUS.push(f);   // {from, to, x, y, amount, ease}: lean toward what is being named
  function camera(t) {
    let k = 0;
    while (k < CAM.length - 2 && t >= CAM[k + 1][0]) k++;
    const [t0, x0, y0, z0] = CAM[k], [t1, x1, y1, z1] = CAM[k + 1];
    const p = inOutCubic(clamp((t - t0) / Math.max(0.001, t1 - t0)));
    let x = lerp(x0, x1, p), y = lerp(y0, y1, p), z = Math.exp(lerp(Math.log(z0), Math.log(z1), p));
    if (V1) return { x, y, z };
    for (const f of FOCUS) {   // lean toward a point: ease in, ease out (default 0.9 s each)
      const e = f.ease || 0.9, a = inOutCubic(prog(t, f.from, e)) * (1 - inOutCubic(prog(t, f.to, e)));
      if (a <= 0) continue;
      x += (f.x - x) * f.amount * a; y += (f.y - y) * f.amount * a;
    }
    // breathing: a slow drift and a slow zoom, small enough to feel like a hand-held dolly
    x += 14 * Math.sin(t * 0.55) + 6 * Math.sin(t * 1.3 + 1); y += 10 * Math.cos(t * 0.43) ;
    z *= 1 + 0.012 * Math.sin(t * 0.37 + 0.6);
    return { x, y, z };
  }

  // ---------- background life: faint shapes with parallax ----------
  const Rb = seeded(21), bgs = [];
  for (let i = 0; i < (V1 ? 0 : 46); i++) {
    const kind = ["", "", "sq", "x"][Math.floor(Rb() * 4)], n = el("div", "bg " + kind, backdrop, kind === "x" ? "+" : "");
    const size = 18 + Rb() * 54;
    if (kind !== "x") { n.style.width = n.style.height = size + "px"; }
    bgs.push({ n, x: -1600 + Rb() * 5600, y: -900 + Rb() * 2600, ph: Rb() * 6.28, sp: 0.08 + Rb() * 0.12, amp: 20 + Rb() * 40 });
  }
  function renderBackdrop(t) {
    for (const b of bgs) setXY(b.n, b.x + b.amp * Math.sin(t * b.sp + b.ph), b.y + b.amp * 0.6 * Math.cos(t * b.sp * 0.8 + b.ph));
  }

  // ---------- connecting lines (drawn on the world, under every piece) ----------
  const lines = svgEl("svg", { width: 1, height: 1 });
  lines.id = "lines"; lines.style.overflow = "visible"; world.appendChild(lines);
  const linkEls = [];
  const link = (x1, y1, x2, y2, at, until, color = "#AEA29A") => {
    const p = svgEl("line", { x1, y1, x2, y2, stroke: color, "stroke-width": 4, "stroke-linecap": "round", pathLength: 1, "stroke-dasharray": "0.0125 0.0875" }, lines);
    linkEls.push({ p, at, until, x1, y1, x2, y2, id: 500 + linkEls.length });
  };
  function renderLinks(t) {
    for (const l of linkEls) {
      const q = V1 ? 0 : life(paper(l.id, t, l.at, MAT.badge).t, l.at, l.until, 0.7, outCubic);   // a line draws on, and draws off (rule 1)
      l.p.style.visibility = q > 0.001 ? "visible" : "hidden";
      l.p.setAttribute("x2", lerp(l.x1, l.x2, q)); l.p.setAttribute("y2", lerp(l.y1, l.y2, q));
    }
  }

  // ---------- the spoken words ----------
  // Word times come from word_timings.py, matched to the voice to 5 ms at pauses. A word lands one
  // frame before its sound: on screen it can never be late, and 1/30 s early reads as in sync.
  const WORD_LEAD = 1 / 30;
  const HOLD = 1.3;
  // Which words sit on colour, and per-line options: the FILM's choices, in words.js
  // (window.WORDS = ({ line, scene }) => ({ em, line })). em: {line: [pattern, "red" | "blue"]} — the
  // pattern runs over the whole line, so a phrase colours every word in it ("how many"). Dark red for
  // a crisis and its questions (bright OCHA red is for shapes), OCHA blue for what helps.
  // line: {line: {cls, nosplit, holdTo, sub}} — a size or place of its own (cls: "big" for the last
  // line, "signoff" for the sign-off title), one unit however long (nosplit), held until (holdTo),
  // everything after the first sentence set smaller (sub: a sign-off's "Made by…" byline).
  const WCFG = window.WORDS ? window.WORDS({ line, scene }) : {};
  const EM = WCFG.em || {};
  const LINE = WCFG.line || {};
  const words = el("div", "", stage); words.id = "words"; words.classList.add("text-" + TEXT);
  const units = [];
  for (const Ln of TL.lines) {
    if (Ln.start > END) break;
    const ws = TL.words.filter(w => w.line === Ln.line), disp = [];
    let wi = 0;
    Ln.text.split(/\s+/).forEach(tok => {
      if (/[A-Za-z0-9]/.test(tok)) { const w = ws[wi++]; disp.push({ text: tok.replace(/^Ocha(?=[’'])/, "OCHA"), start: w.start, end: w.end, appear: w.start - WORD_LEAD }); }
      // a dash is a pause for the voice, not something to read: "And that — saves lives." shows as
      // "And that saves lives." (Javier, review round 2). Other marks stay with the word before them.
      else if (disp.length && !/^[—–-]+$/.test(tok)) disp[disp.length - 1].text += " " + tok;
    });
    // colour: mark every word that a pattern match overlaps, across word boundaries
    const em = EM[Ln.line];
    if (em) {
      let pos = 0; const text = disp.map(d => { d.a = pos; pos += d.text.length + 1; d.b = d.a + d.text.length; return d.text; }).join(" ");
      for (const m of text.matchAll(em[0])) disp.forEach(d => { if (d.a < m.index + m[0].length && d.b > m.index) d.em = em[1]; });
    }
    let groups = [disp];
    if (disp.length > 10 && !(LINE[Ln.line] || {}).nosplit) {
      const ends = disp.map((d, i) => (/[.?!]$/.test(d.text) && i < disp.length - 1 ? i : -1)).filter(i => i >= 0);
      if (ends.length) { const mid = disp.length / 2, cut = ends.reduce((a, b) => (Math.abs(b + 1 - mid) < Math.abs(a + 1 - mid) ? b : a)); groups = [disp.slice(0, cut + 1), disp.slice(cut + 1)]; }
    }
    groups.forEach(g => units.push({ line: Ln.line, words: g }));
  }
  let wid = 1000;   // ids stay clear of every other piece's, so no word shares another's clock
  units.forEach((u, i) => {
    const next = units[i + 1], last = u.words[u.words.length - 1].end, opt = LINE[u.line] || {};
    const hold = opt.holdTo != null ? opt.holdTo : last + HOLD;
    u.start = u.words[0].start - 0.12;
    u.end = next ? Math.min(next.words[0].start - 0.12, hold) : Math.min(END, hold);
    u.node = el("div", "unit" + (opt.cls ? " " + opt.cls : ""), words);
    const isEm = w => !!w.em, endsS = w => /[.?!]$/.test(w.text);
    const nEnds = u.words.filter(endsS).length, firstEnd = u.words.findIndex(endsS);
    const sub = k => (opt.sub && firstEnd >= 0 && k > firstEnd ? " sub" : "");
    let k = 0;
    while (k < u.words.length) {
      if (isEm(u.words[k]) && TEXT === "pill") {
        const keep = el("span", "keep", u.node);
        do { const w = u.words[k]; w.node = el("span", "w em " + w.em + sub(k), keep, w.text); w.id = wid++; k++;
             if (k < u.words.length && isEm(u.words[k]) && !endsS(w)) keep.appendChild(document.createTextNode(" ")); else break; } while (true);
      } else { const w = u.words[k]; w.node = el("span", "w" + (isEm(w) ? " em " + w.em : "") + sub(k), u.node, w.text); w.id = wid++; k++; }
      if (k === u.words.length) break;
      if (nEnds === 2 && endsS(u.words[k - 1])) u.node.appendChild(document.createElement("br"));
      else u.node.appendChild(document.createTextNode(" "));
    }
  });
  function layoutText() {
    for (const u of units) {
      const fs = parseFloat(getComputedStyle(u.node).fontSize), rows = new Map();
      u.words.forEach(w => { w.box = { x: w.node.offsetLeft, y: w.node.offsetTop, w: w.node.offsetWidth, h: w.node.offsetHeight };
        const key = Math.round(w.box.y); if (!rows.has(key)) rows.set(key, []); rows.get(key).push(w); });
      u.lines = [];
      if (TEXT === "pill") u.lines = [...rows.values()].map(ws => {
        const pill = el("div", "pill", u.node), h = fs * 1.18, top = ws[0].box.y + (ws[0].box.h - h) / 2;
        pill.style.top = top + "px"; pill.style.height = h + "px";
        const runs = [];
        ws.forEach((w, k) => { if (!w.node.classList.contains("em")) return; const p = runs[runs.length - 1];
          if (p && p.to === k - 1 && !/[.?!]$/.test(ws[k - 1].text)) p.to = k; else runs.push({ from: k, to: k, red: w.node.classList.contains("red") }); });
        const emNodes = runs.map(r => { const n = el("div", "pill-em", u.node); if (r.red) n.style.background = "var(--red-text)";
          n.style.top = top + 7 + "px"; n.style.height = h - 14 + "px"; return { node: n, words: ws.slice(r.from, r.to + 1) }; });
        return { pill, ws, emNodes, pad: fs * 0.22 };
      });
      if (TEXT === "marker") u.words.forEach(w => {   // a marker band sits on the word, bottom edge 7% under the baseline
        if (!w.node.classList.contains("em")) return;
        const m = el("div", "mark", u.node); const h = fs * 0.62;
        m.style.left = w.box.x - fs * 0.06 + "px"; m.style.width = w.box.w + fs * 0.12 + "px";
        m.style.top = w.box.y + w.box.h * 0.5 - h * 0.62 + fs * 0.12 + "px"; m.style.height = h + "px";
        w.mark = m;
      });
    }
  }
  function renderWords(t) {
    for (const u of units) {
      const on = t >= u.start && t < u.end;
      u.node.style.visibility = on ? "visible" : "hidden";
      if (!on) continue;
      u.node.style.opacity = 1 - clamp((t - (u.end - 0.18)) / 0.18);
      u.words.forEach(w => {
        const p = paper(w.id, t, w.appear, MAT.word);
        const q = TEXT === "pill" ? outCubic(prog(t, w.appear, 0.22)) : outBack(prog(p.t, w.appear, 0.25));
        w.node.style.visibility = q > 0 ? "inherit" : "hidden";   // never "visible": see the storyboard bug of 19 Sept
        w.node.style.opacity = clamp(q * 1.5);
        if (TEXT === "cutout") {   // the paper label carries the cut edge (--cut, on ::before); the letters stay crisp
          const tilt = 2.2 * hash(w.id, 1);
          w.node.style.transform = `translate(${p.dx}px, ${p.dy}px) rotate(${tilt + p.r}deg) scale(${0.6 + 0.4 * q})`;
          if (q > 0) w.node.style.setProperty("--cut", p.filter);
        } else w.node.style.transform = `translateY(${(1 - q) * 22}px)`;
        if (w.mark) { const m = outCubic(prog(t, w.start + 0.05, 0.28)); w.mark.style.visibility = m > 0 ? "inherit" : "hidden"; w.mark.style.transform = `scaleX(${m})`; }
      });
      for (const L of u.lines) {
        const shown = L.ws.filter(w => t >= w.appear);
        L.pill.style.visibility = shown.length ? "inherit" : "hidden";
        if (shown.length) { const a = shown[0].box, b = shown[shown.length - 1].box; L.pill.style.left = a.x - L.pad + "px"; L.pill.style.width = b.x + b.w - a.x + 2 * L.pad + "px"; }
        L.emNodes.forEach(E => { const vis = E.words.filter(w => t >= w.appear); E.node.style.visibility = vis.length ? "inherit" : "hidden";
          if (vis.length) { const a = vis[0].box, b = vis[vis.length - 1].box; E.node.style.left = a.x - L.pad * 0.55 + "px"; E.node.style.width = b.x + b.w - a.x + L.pad * 1.1 + "px"; } });
      }
    }
  }

  // ---------- render ----------
  const parts = [];
  const add = fn => parts.push(fn);
  function render(t) {
    const c = camera(t);
    const tx = S - c.x * c.z, ty = SY - c.y * c.z;
    world.style.transform = `translate(${tx}px, ${ty}px) scale(${c.z})`;
    const pz = Math.pow(c.z, 0.7), px = S - c.x * pz * 0.7, py = SY - c.y * pz * 0.7;   // the backdrop moves less: depth
    backdrop.style.transform = `translate(${px}px, ${py}px) scale(${pz})`;
    const g = 48 * c.z;
    stage.style.backgroundSize = `${g}px ${g}px`;
    stage.style.backgroundPosition = `${((tx % g) + g) % g}px ${((ty % g) + g) % g}px`;
    renderBackdrop(t); renderLinks(t); renderPieces(t);   // pieces first: a scene's own drawing may then move them
    for (const f of parts) f(t);
    renderWords(t);
  }

  window.FILM = {
    TL, I, WF, line, scene, W, params, V1, TEXT, WOBBLE, END,
    MAP: params.get("map") || "E",   // how far the world map is simplified: A–F (worldmap.js). E, chunky, with the Mediterranean kept open (SG film, Javier, 20 Sept 2026)
    clamp, outCubic, outQuint, inOutCubic, outBack, prog, lerp, seeded, life, hash, unit01,
    MAT, paper, stage, world, backdrop, NS, el, svgEl, setXY, popStyle, link, cam, focus, add,
    piece, badge, pieces,   // pieces: every piece with its cue and class, so score.js can give each entrance its sound
    CAM,        // the camera keyframes [t, x, y, zoom]: score.js can hear the travels in them
    KEYS: {},   // named moments for approval stills (stills.mjs)
    pos: {},    // where and when things happen in the world, shared with decor.js and score.js
    start() {
      CAM.sort((a, b) => a[0] - b[0]);
      window.DURATION = END;
      window.seek = t => { render(t); return true; };
      window.KEYS = this.KEYS;
      const frozen = params.get("t");
      document.fonts.ready.then(() => {
        // OCHA's fonts must be INSTALLED on the Mac (Roboto, Roboto Condensed — free from Google Fonts):
        // without them every frame renders in a fallback face and nothing else would say so. Detected by
        // width (document.fonts.check cannot see installed fonts), and shown ON the picture, so a render
        // made without them can't be mistaken for a good one.
        const ctx = document.createElement("canvas").getContext("2d"), probe = "wwwwwwwwwwlli1WQ@#";
        const has = f => { ctx.font = "72px monospace"; const a = ctx.measureText(probe).width; ctx.font = `72px "${f}", monospace`; return ctx.measureText(probe).width !== a; };
        const missing = ["Roboto", "Roboto Condensed"].filter(f => !has(f));
        if (missing.length) {
          console.error("Missing fonts:", missing.join(", "));
          el("div", "", stage, `Not installed on this Mac: ${missing.join(" and ")}. Install OCHA's fonts before rendering.`).style.cssText =
            "position:absolute;left:0;right:0;top:0;padding:24px;background:#ED1847;color:#fff;font:700 36px sans-serif;z-index:99";
        }
        layoutText();
        if (frozen !== null) return render(parseFloat(frozen));
        const t0 = performance.now();
        (function loop(now) { render(((now - t0) / 1000) % window.DURATION); requestAnimationFrame(loop); })(t0);
      });
    },
  };
})();
