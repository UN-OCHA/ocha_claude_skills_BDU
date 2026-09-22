/* The DEMO film of the cut-out kit — two lines, about 9 seconds. Replace it with the film.
   A crisis, the questions it raises, and the data that answers them, built only from the engine's
   pieces so it shows the vocabulary: badges that pop on their word, dotted links, a still chart cut
   from paper, a camera that travels and leans, people who turn blue, the black sheet that ends it.
   Every time is cued from the voice (line / word), never written as seconds, so the film follows
   the voice when it changes. x, y are world coordinates of a piece's CENTRE; the camera puts the
   world point it looks at in the middle of the upper frame (the words take the bottom third). */
(function () {
  const F = window.FILM;
  const { I, WF, line, scene, W, clamp, outCubic, outBack, prog, life, MAT, paper, stage, world, el, setXY,
          link, cam, focus, add, piece, badge } = F;
  const L1 = W(1), L2 = W(2);

  // ---------- the camera: [time, x, y, zoom]. Travels start before a sentence ends and land a word into the next ----------
  cam(0, 0, -40, 1.08);
  cam(line(1).end - 0.4, 40, -40, 1.02);                 // a slow drift while the questions arrive
  cam(L2[0].start + 0.5, 1480, -20, 1.0);                // → the data (SG review round 1: never faster than this)
  cam(scene(3).end, 1520, -20, 1.03);                    // it just rests under the black sheet
  focus({ from: L1[4].start, to: line(1).end + 0.3, x: 330, y: -80, amount: 0.12 });   // lean toward what is named

  // ---------- 1 · "When a crisis hits, questions come first." ----------
  const crises = [["Earthquake", -560, -110], ["Flood", -250, -250], ["Cyclone", -300, 70]]
    .map(([icon, x, y], i) => badge(icon, x, y, L1[2].start - 0.05 + i * 0.12, line(1).end + 0.9));   // on "crisis", one after another
  const q = badge("Help", 330, -80, L1[4].start - 0.03, line(1).end + 0.9, "lg on-red");              // on "questions"
  crises.forEach((c, i) => link(c.x, c.y, q.x, q.y, L1[4].start + 0.1 + i * 0.08, line(1).end + 0.7));

  // ---------- 2 · "Data turns them into answers everyone can see." ----------
  const chart = piece(WF.hbar(), "float-w cut", 1600, -90, L2[0].start - 0.05, null,
                      { w: 560, mat: MAT.chart, from: 0.3 });                                  // on "Data": perfectly still, the clean result
  const answer = badge("Help", 1130, -250, L2[4].start - 0.03, null, "answered");              // on "answers": the question, answered (blue)
  link(answer.x, answer.y, chart.x - 200, chart.y - 60, L2[4].start + 0.15, null);
  const KINDS = ["Person-1", "Children", "Elderly", "Person-2", "Pregnant", "Infant", "People-with-physical-impairments"];
  const crowd = KINDS.map((k, i) => {
    const x = 1240 + i * 100, n = el("div", "person cut", world, I[k]); setXY(n, x, 150);
    return { n, x, id: 700 + i, at: L2[5].start - 0.05 + i * 0.07, litAt: L2[7].start - 0.05 + i * 0.05 };   // on "everyone"; blue on "see"
  });
  add(t => {
    for (const p of crowd) {
      const s = paper(p.id, t, p.at, MAT.person), k = life(s.t, p.at, null, 0.4, outBack);
      p.n.style.visibility = k > 0.001 ? "visible" : "hidden";
      p.n.style.opacity = clamp(k * 1.6);
      p.n.style.transform = `translate(calc(-50% + ${s.dx}px), calc(-50% + ${s.dy}px)) rotate(${s.r}deg) scale(${0.4 + 0.6 * k})`;
      p.n.style.color = s.t >= p.litAt ? "var(--blue)" : "var(--stone)";
      if (k > 0.001) p.n.style.filter = s.filter;
    }
  });

  // ---------- the end: a black sheet of paper wipes over everything, words included. Never a fade (house rule) ----------
  const black = el("div", "end-black", stage), blackPaper = el("div", "end-paper", black), blackAt = scene(3).start;
  add(t => {
    const s = paper(651, t, blackAt, MAT.badge), k = outCubic(prog(s.t, blackAt, 0.55));
    black.style.visibility = t >= blackAt ? "visible" : "hidden";
    black.style.transform = `translate(${(1 - k) * 112}%, 0) rotate(${(1 - k) * -4}deg)`;
    blackPaper.style.filter = s.filter;
  });

  // ---------- shared with decor.js and score.js: where and when things happen (never retyped there) ----------
  Object.assign(F.pos, {
    crises: crises.map(c => ({ x: c.x, y: c.y, at: c.at })),
    crisesOff: line(1).end + 0.6,
    question: { x: q.x, y: q.y, at: q.at },
    chart: { x: chart.x, y: chart.y, at: chart.at },
    answer: { x: answer.x, y: answer.y, at: answer.at },
    crowd: { x: 1540, y: 150, at: Math.min(...crowd.map(p => p.at)), litAt: Math.min(...crowd.map(p => p.litAt)) },
    blackAt,
  });
  Object.assign(F.KEYS, { a: line(1).end - 0.1, b: L2[4].end + 0.3, c: scene(2).end - 0.2 });   // approval stills (stills.mjs)
})();
