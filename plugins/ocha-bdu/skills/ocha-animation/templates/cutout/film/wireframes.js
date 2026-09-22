/* Wireframes: the tool's charts and maps drawn as simple shapes, never real data or real
   geography. Marks are OCHA blue, text is suggested by grey bars, maps are loose shapes.
   Every function returns an SVG string with a viewBox, free-floating (no background). */
(function () {
  const C = { mark: "#009EDB", ramp: ["#004987", "#0074B7", "#009EDB", "#64BDEA"], title: "#493F38",
              text: "#AEA29A", axis: "#C5BFBA", need: "#ED1847", blob: "#DDDAD7" };
  const pill = (x, y, w, h, fill) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${h / 2}" fill="${fill}"/>`;
  const head = w => pill(0, 0, w * 0.42, 18, C.title) + pill(0, 32, w * 0.26, 11, C.text);
  const svg = (w, h, body) => `<svg viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" aria-hidden="true">${body}</svg>`;
  const rand = seed => () => ((seed = (seed * 9301 + 49297) % 233280) / 233280);
  const WF = {};

  WF.hbar = (fracs = [0.92, 0.74, 0.66, 0.48, 0.4, 0.3], w = 760, h = 440, titled = true) => {
    const top = titled ? 76 : 0, rowH = (h - top) / fracs.length, x0 = 190, maxW = w - x0 - 70;
    let b = titled ? head(w) : "";
    fracs.forEach((f, i) => {
      const cy = top + i * rowH + rowH / 2, bh = rowH * 0.58;
      b += pill(40, cy - 6, 130, 12, C.text);
      b += `<rect x="${x0}" y="${cy - bh / 2}" width="${maxW * f}" height="${bh}" fill="${C.mark}"/>`;
      b += pill(x0 + maxW * f + 14, cy - 6, 40, 12, C.title);
    });
    return svg(w, h, b);
  };

  WF.vbar = (fracs = [0.35, 0.5, 0.62, 0.78, 0.95], w = 560, h = 420, titled = true) => {
    const top = titled ? 80 : 0, base = h - 34, gap = 22, n = fracs.length, cw = (w - gap * (n - 1)) / n;
    let b = titled ? head(w) : "";
    fracs.forEach((f, i) => {
      const x = i * (cw + gap), ch = (base - top - 30) * f;
      b += pill(x + cw / 2 - 16, base - ch - 26, 32, 12, C.title);
      b += `<rect x="${x}" y="${base - ch}" width="${cw}" height="${ch}" fill="${C.mark}"/>`;
      b += pill(x + cw / 2 - 20, base + 14, 40, 12, C.text);
    });
    return svg(w, h, b);
  };

  WF.donut = (parts = [0.46, 0.27, 0.16, 0.11], w = 640, h = 400, titled = true) => {
    const top = titled ? 70 : 0, r = Math.min((h - top) / 2 - 6, 150), cx = r + 10, cy = top + (h - top) / 2, rin = r * 0.58;
    let b = titled ? head(w) : "", a0 = -Math.PI / 2;
    parts.forEach((p, i) => {
      const a1 = a0 + p * Math.PI * 2, large = p > 0.5 ? 1 : 0;
      const P = (rad, a) => `${cx + rad * Math.cos(a)} ${cy + rad * Math.sin(a)}`;
      b += `<path d="M ${P(r, a0)} A ${r} ${r} 0 ${large} 1 ${P(r, a1)} L ${P(rin, a1)} A ${rin} ${rin} 0 ${large} 0 ${P(rin, a0)} Z" fill="${C.ramp[i % 4]}"/>`;
      const ly = cy - 70 + i * 46;
      b += `<rect x="${cx + r + 60}" y="${ly}" width="22" height="22" fill="${C.ramp[i % 4]}"/>` + pill(cx + r + 96, ly + 5, 150 - i * 18, 12, C.text);
      a0 = a1;
    });
    return svg(w, h, b);
  };

  WF.line = (ys = [0.7, 0.55, 0.62, 0.4, 0.46, 0.22, 0.12], w = 560, h = 400, titled = true) => {
    const top = titled ? 80 : 10, base = h - 30, step = (w - 20) / (ys.length - 1);
    let b = (titled ? head(w) : "") + `<line x1="0" y1="${base}" x2="${w}" y2="${base}" stroke="${C.axis}" stroke-width="3"/>`;
    const pts = ys.map((v, i) => [10 + i * step, top + (base - top) * v]);
    b += `<polyline points="${pts.map(p => p.join(",")).join(" ")}" fill="none" stroke="${C.mark}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"/>`;
    pts.forEach(([x, y]) => { b += `<circle cx="${x}" cy="${y}" r="9" fill="${C.mark}"/>`; });
    return svg(w, h, b);
  };

  WF.keyfigs = (n = 3, w = 700, h = 200) => {
    const cw = w / n;
    let b = "";
    for (let i = 0; i < n; i++) {
      const x = i * cw + (i ? 28 : 0);
      if (i) b += `<line x1="${i * cw}" y1="20" x2="${i * cw}" y2="${h - 20}" stroke="${C.axis}" stroke-width="3"/>`;
      b += `<rect x="${x}" y="${h / 2 - 62}" width="${cw * 0.62}" height="62" rx="6" fill="${C.ramp[i === 0 ? 2 : 1]}"/>`;
      b += pill(x, h / 2 + 22, cw * 0.5, 14, C.title) + pill(x, h / 2 + 48, cw * 0.34, 11, C.text);
    }
    return svg(w, h, b);
  };

  // requirement vs funding, as two bars
  WF.funding = (funded = 0.38, w = 760, h = 300) => {
    const bh = 70;
    return svg(w, h, pill(0, 0, 260, 18, C.title) + `<rect x="0" y="36" width="${w}" height="${bh}" fill="${C.mark}"/>` +
      pill(0, 150, 320, 18, C.title) + `<rect x="0" y="186" width="${w}" height="${bh}" fill="${C.blob}"/>` +
      `<rect x="0" y="186" width="${w * funded}" height="${bh}" fill="${C.ramp[1]}"/>`);
  };

  // who does what, where: partners (rows) x places (columns)
  WF.matrix = (rows = 6, cols = 8, w = 760, h = 470, seed = 7) => {
    const r = rand(seed), top = 76, left = 170, cw = (w - left) / cols, rh = (h - top) / rows;
    let b = head(w);
    for (let c = 0; c < cols; c++) b += pill(left + c * cw + cw / 2 - 18, top - 4, 36, 10, C.text);
    for (let i = 0; i < rows; i++) {
      const cy = top + 30 + i * rh + rh / 2 - 14;
      b += pill(0, cy - 7, 130, 14, C.text);
      for (let c = 0; c < cols; c++) {
        const on = r() > 0.45;
        b += `<circle cx="${left + c * cw + cw / 2}" cy="${cy}" r="${on ? 16 : 6}" fill="${on ? C.ramp[i % 3 + 1] : C.axis}"/>`;
      }
    }
    return svg(w, h, b);
  };

  // A wireframe globe: an orthographic graticule with dots. No coastlines, no countries.
  WF.globe = ({ r = 280, lon0 = 20, lat0 = 14, n = 70, seed = 5, dot = C.need, stroke = C.axis } = {}) => {
    const d2r = Math.PI / 180, cp = Math.cos(lat0 * d2r), sp = Math.sin(lat0 * d2r), pad = 24, S = 2 * (r + pad);
    const proj = (lon, lat) => {
      const l = (lon - lon0) * d2r, p = lat * d2r;
      return [pad + r + r * Math.cos(p) * Math.sin(l), pad + r - r * (cp * Math.sin(p) - sp * Math.cos(p) * Math.cos(l)),
              sp * Math.sin(p) + cp * Math.cos(p) * Math.cos(l)];
    };
    const trace = pts => {
      let out = "", seg = [];
      const flush = () => { if (seg.length > 1) out += `<polyline points="${seg.map(q => q[0].toFixed(1) + "," + q[1].toFixed(1)).join(" ")}" fill="none" stroke="${stroke}" stroke-width="3" stroke-linecap="round"/>`; seg = []; };
      pts.forEach(q => { if (q[2] > 0) seg.push(q); else flush(); });
      flush();
      return out;
    };
    let b = `<circle cx="${pad + r}" cy="${pad + r}" r="${r}" fill="#fff" fill-opacity="0.55" stroke="${stroke}" stroke-width="4"/>`;
    for (let lat = -60; lat <= 60; lat += 30) { const pts = []; for (let lon = -180; lon <= 180; lon += 3) pts.push(proj(lon, lat)); b += trace(pts); }
    for (let lon = -180; lon < 180; lon += 30) { const pts = []; for (let lat = -90; lat <= 90; lat += 3) pts.push(proj(lon, lat)); b += trace(pts); }
    const R = rand(seed);
    for (let i = 0; i < n; i++) {
      const q = proj(R() * 360 - 180, R() * 120 - 50), s = [7, 9, 12][Math.floor(R() * 3)];
      if (q[2] < 0.2) continue;
      b += `<circle cx="${q[0]}" cy="${q[1]}" r="${s * 2.2}" fill="${dot}" fill-opacity="0.16"/><circle cx="${q[0]}" cy="${q[1]}" r="${s}" fill="${dot}"/>`;
    }
    return svg(S, S, b);
  };

  // The world, super-simplified (Javier, review round 1): land only, no borders, from world_map.py
  // (window.WORLD_LAND). level A light, B strong, C soft blobs, D rounder, E chunky, F cut with scissors.
  // Pins are [lon, lat] (Equal Earth) and come with the map: world_map.py checks each one is on land.
  const EE = (lon, lat) => {
    const [a1, a2, a3, a4] = [1.340264, -0.081106, 0.000893, 0.003796], l = lon * Math.PI / 180, p = lat * Math.PI / 180;
    const th = Math.asin(Math.sqrt(3) / 2 * Math.sin(p)), t2 = th * th, t6 = t2 * t2 * t2;
    return [2 * Math.sqrt(3) * l * Math.cos(th) / (3 * (9 * a4 * t6 * t2 + 7 * a3 * t6 + 3 * a2 * t2 + a1)), th * (a1 + a2 * t2 + t6 * (a3 + a4 * t2))];
  };
  WF.PINS = window.WORLD_LAND.pins;   // where people are affected, roughly — regions, never labelled
  // poster: the map as a map product — a sheet of white paper with a title, the map and a legend, so
  // it holds its own next to the charts (Javier, review round 2: bare land "doesn't look good by itself").
  WF.worldmap = ({ level = "C", pins = WF.PINS, pin = C.need, land = C.blob, poster = false } = {}) => {
    const M = window.WORLD_LAND, L = M.levels[level];
    const xy = (lon, lat) => { const [X, Y] = EE(lon, lat); return [(X - M.x0) * M.s, (M.y1 - Y) * M.s]; };
    let b = `<path d="${L.d}" fill="${poster ? C.axis : land}"/>`;   // on white paper the land goes one step darker
    pins.forEach(([lon, lat]) => { const [x, y] = xy(lon, lat); b += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="26" fill="${pin}" fill-opacity="0.18"/><circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="11" fill="${pin}"/>`; });
    if (!poster) return svg(M.w, M.h, b);
    const pad = 48, headH = 86, footH = 62, W = M.w + 2 * pad, H = M.h + headH + footH + 2 * pad, fy = pad + headH + M.h + 28;
    return svg(W, H, `<rect width="${W}" height="${H}" rx="10" fill="#fff"/><g transform="translate(${pad} ${pad})">${head(M.w)}</g>` +
      `<g transform="translate(${pad} ${pad + headH})">${b}</g>` +
      `<g transform="translate(${pad} ${fy})"><circle cx="13" cy="13" r="13" fill="${pin}"/>${pill(40, 5, 170, 16, C.text)}` +
      `<rect x="270" y="0" width="26" height="26" rx="4" fill="${C.axis}"/>${pill(310, 5, 130, 16, C.text)}</g>`);
  };

  // A wireframe map: loose land shapes and pins, not a real place (storyboard; the film uses WF.worldmap).
  WF.map = ({ w = 640, h = 420, seed = 3, pins = 9, pin = C.need } = {}) => {
    const R = rand(seed);
    const blob = (cx, cy, rad) => {
      const k = 10, pts = [];
      for (let i = 0; i < k; i++) { const a = i / k * Math.PI * 2, rr = rad * (0.72 + R() * 0.4); pts.push([cx + rr * Math.cos(a), cy + rr * 0.78 * Math.sin(a)]); }
      let d = "";
      for (let i = 0; i < k; i++) {
        const p0 = pts[(i - 1 + k) % k], p1 = pts[i], p2 = pts[(i + 1) % k], p3 = pts[(i + 2) % k];
        if (!i) d += `M ${p1[0]} ${p1[1]} `;
        d += `C ${p1[0] + (p2[0] - p0[0]) / 6} ${p1[1] + (p2[1] - p0[1]) / 6} ${p2[0] - (p3[0] - p1[0]) / 6} ${p2[1] - (p3[1] - p1[1]) / 6} ${p2[0]} ${p2[1]} `;
      }
      return `<path d="${d}Z" fill="${C.blob}"/>`;
    };
    const lands = [[w * 0.33, h * 0.42, w * 0.3], [w * 0.72, h * 0.36, w * 0.22], [w * 0.62, h * 0.78, w * 0.16]];
    let b = lands.map(l => blob(...l)).join("");
    for (let i = 0; i < pins; i++) {
      const L = lands[i % lands.length], a = R() * Math.PI * 2, d = R() * L[2] * 0.55;
      const x = L[0] + d * Math.cos(a), y = L[1] + d * 0.7 * Math.sin(a);
      b += `<circle cx="${x}" cy="${y}" r="24" fill="${pin}" fill-opacity="0.16"/><circle cx="${x}" cy="${y}" r="11" fill="${pin}"/>`;
    }
    return svg(w, h, b);
  };

  window.WF = WF;
})();
