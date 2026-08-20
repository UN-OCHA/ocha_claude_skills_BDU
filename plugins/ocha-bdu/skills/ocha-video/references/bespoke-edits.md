# Bespoke edits — mission films, recaps, anything cut from several clips

**There is deliberately no recipe here, and you should not invent one.** A mission wrap-up, a
field film and an event recap are different every time; the narrative belongs to the material
and to Javi, not to a template. What this file holds is the *mechanics* that are the same
whenever an edit is assembled from more than one source — plus the questions worth asking
before any of it starts.

The house rules in `SKILL.md` apply in full. Branding goes through `references/branding.md`.

Written 2026-08-20, before the first one. **Thin on purpose — fill it in from the real job**,
and only with what turns out to repeat.

---

## What to establish before touching anything

A bespoke piece lives or dies on its inputs. Ask, and get real answers:

1. **What footage exists** — b-roll, interview or PTC, stills? Roughly how much, shot on what?
2. **Is there a script or key messages**, or are we building the narrative from the material?
3. **Destination and length.** Sets format and caption style exactly as it does anywhere else
   (`SKILL.md` §2).
4. **Music** — is a bed expected? If so it must be cleared, which is a separate problem, not a
   detail. Statement videos have no music at all, so there is no house standard to fall back on.
5. **Anything filmed with affected people** — consent and dignity constraints on who can appear
   and how. This is not a technical question and it outranks the edit.

Where a bespoke job differs from a statement video, expect these:

- **The narrative is deliberately re-ordered.** The chronological rule in
  `references/statement-video.md` is about not rearranging a person's argument — it does not
  apply here.
- **A location strip usually earns its place.** The statement default (no strip) is the
  opposite of what a field film wants.
- **Picture is cut to the words**, not the words trimmed to fit the picture.

---

## Multi-clip assembly mechanics

The engine and every recipe we have assume ONE input at final canvas size. For several
sources, build the assembly by hand and hand the finished cut to branding.

- **Normalise before you concat.** Every clip into the `concat` filter must match on
  resolution, pixel format, SAR and frame rate, or the filter fails or produces a mess. Give
  each input the same `scale=<canvas>,setsar=1`, and add `fps=<target>` where sources differ.
- **Still ONE filtergraph.** Same rule as anywhere: build the whole cut in a single ffmpeg
  filtergraph rather than concatenating rendered pieces.
- **Check every source's live picture area separately** (`SKILL.md` §5). Different cameras,
  different dead edges.
- **Audio levels will not match** across cameras and phones. Level the clips against each
  other before the concat, not after — and say what you did, since it is a judgement call.
- **Duration bookkeeping** matters more here, not less: with several video segments and a
  separate audio build, the two totals drift easily. Verify the export with `ffprobe`.

## Still true here

- Framing sheet before you render a cut (`SKILL.md` §4). With mixed footage there is more to
  choose from, not less.
- Unbranded cut for approval first.
- Vignette by default, and say so.
- No fades. Logo ending to the standard spec. Four folders and a README.
