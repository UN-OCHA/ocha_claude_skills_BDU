/* The spoken words: which sit on colour, and per-line options. The FILM's choices (world.js reads them).
   em   — {line: [pattern, "red" | "blue"]}: the pattern runs over the whole line, so a phrase colours
          every word in it. Dark red labels for a crisis and its questions; OCHA blue for what helps.
          (Bright OCHA red is for shapes, never behind words: Javier, 19 Sept 2026.)
   line — {line: {cls, nosplit, holdTo, sub}}: cls "big" for a last line that should land hardest,
          "signoff" for a sign-off title at the top; nosplit keeps a long line as one unit; holdTo keeps
          it on screen until a time (e.g. scene(n).end); sub sets everything after its first sentence
          smaller (a byline: "Made by OCHA's Brand and Design Unit.").
   The SG Awards film coloured 12 of its 19 lines and set its last two with "big" and "signoff". */
window.WORDS = ({ line, scene }) => ({
  em: {
    1: [/\b(crisis|questions)\b/gi, "red"],
    2: [/\b(answers|everyone)\b/gi, "blue"],
  },
  line: {},
});
