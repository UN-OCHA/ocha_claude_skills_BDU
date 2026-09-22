/* The SOUND SCORE: which kind of sound plays WHEN. It plays nothing: it fills window.SFX, and
   sfx_mix.py turns it into the effects track (which recording each kind uses, how loud).
     cue(t, kind, label)          a one-off: the sound STARTS exactly on t (the frame its thing appears)
     bed(t0, t1, kind, label)     an ambience from t0 to t1, faded in and out
   Every time is read from the SAME timing the picture uses (FILM.pos, FILM.pieces, the voice's words),
   never retyped, so a sound can never drift from what it belongs to.
   The house rules (ocha-video → references/sound-voice-music.md): a few sounds that carry meaning,
   never one per element; one thing appearing = one sound, on its frame; always under the voice.
   The kinds and their recordings are in sfx_mix.py (PALETTE): the SG Awards film's approved set. */
(function () {
  const F = window.FILM;
  if (F.V1) return;
  const { line, W, pos } = F;
  const cues = [];
  const r3 = t => Math.round(t * 1000) / 1000;
  const cue = (t, kind, label) => { if (Number.isFinite(t)) cues.push({ t: r3(t), kind, label }); };
  const bed = (t0, t1, kind, label) => { if (Number.isFinite(t0) && Number.isFinite(t1) && t1 > t0) cues.push({ t: r3(t0), until: r3(t1), kind, label }); };

  // ================= THE FILM'S SCORE (the demo's: replace it with the film's) =================
  pos.crises.forEach((c, i) => cue(c.at, "pop", `crisis ${i + 1} appears`));      // a card laid down, once per badge
  cue(pos.question.at, "error", "the question appears");                           // a question mark: "the typical error sound on a laptop"
  cue(pos.chart.at, "blop", "the chart appears");                                  // a "blop" for each graph
  cue(pos.answer.at, "chime", "the answer appears, blue");                         // a soft tin tap for a blue icon
  cue(pos.crowd.at, "crowdin", "the people appear");                               // many paper people landing at once
  cue(pos.crowd.litAt, "peopleblue", "the people turn blue");                      // positive
  cue(pos.blackAt, "sheet", "the black sheet slides in");
  // A bed runs under a stretch: bed(W(1)[2].start, line(1).end, "siren", "far off"). The SG film had a
  // distant storm, a siren, typing, people talking, a clock, a radio, a truck and a murmur of people.

  cues.sort((a, b) => a.t - b.t);
  window.SFX = cues;
})();
