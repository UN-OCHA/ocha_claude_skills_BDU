---
name: ocha-bdu-graphic-styles
description: >
  The named graphic styles of the OCHA Brand and Design Unit, for static graphics as much as for films: what each
  looks like, its recipe and values, a starter template, the rules learned from feedback, and its limits. Two styles
  so far: NEWSPRINT (cream printed paper, grain, ink-speckled OCHA icons, black caption strips, an orange marker swipe
  on the key idea; inspired by Vox documentary infographics) and CUT-OUT (paper cut-outs with a hand-cut edge and a
  hard shadow; the SG Awards Dataviz film). Use whenever someone asks for a graphic, diagram, infographic, card or
  slide "in the newsprint style", "newsy", "like a newspaper", "editorial look", "like Vox", "Vox style", "documentary
  infographic", "paper texture", "marker highlight", "cut-out", "paper cut-out", "like the SG Awards Dataviz
  animation", "like the 16 Days cards", or wants to know which named styles BDU has. For how a cut-out FILM moves
  (shaking, timing, voice, render), use `ocha-bdu-animation`; for OCHA colours, type and logos, `ocha-bdu-visual-identity`.
---

# OCHA BDU graphic styles

A named style is a whole look with a recipe, so anyone can ask for it by name and get the same result. Each one
below says what it is, where to start, the rules that came from real feedback, and what it can’t do yet.

These are defaults, not laws. The designer can set any rule aside for a job; say which and why.

| Style | Feel | Good for | Starter |
|---|---|---|---|
| **Newsprint** | Sober, editorial, “in the news” | Explainers, process diagrams, one-pagers, social cards that must feel serious | `templates/newsprint/` |
| **Cut-out** | Tactile, crafted, a bit playful | Voice-led films and data stories | `ocha-bdu-animation` → `templates/cutout/` |

---

## Newsprint

Cream printed paper with a fine grain, OCHA icons printed in ink, black caption strips, and one hand-swiped
orange marker on the key idea. It should look printed, not designed on a screen.

**Where it comes from** (keep this; it is easy to forget): Vox documentary infographics and Vox-style templates.
References: Highlight by Vox (behance.net/gallery/247926671/Highlight-by-Vox), Vox Documentary Infographics
(behance.net/gallery/234671675/Vox-Documentary-Infographics), Documentary Motion Template – Vox Style
(behance.net/gallery/254406133/Documentary-Motion-Template-Vox-Style), US Election explainer by Tom Bradshaw
(dribbble.com/shots/24370875-US-Election-explainer), and the sober cut-out 16 Days of Activism cards (BDU, Nov 2026).
We call it Newsprint so the name isn’t another brand’s.

**First job:** the UN Disaster Risk Financing Platform diagram (FOD/CIS, 24 Nov 2026). Its template is the starter:
`templates/newsprint/newsprint_example_drf_platform.html`, result in `newsprint_example_drf_platform.png`.

The recipe, every value and why: **`references/newsprint.md`**. The short version:

- **Ground:** near-white cream paper (#FAF8F3), a faint graph-paper grid, very faint grain, fibres and crumple,
  and off-centre stains (heavier in two opposite corners). Subtle: it should read as paper, never as grey.
- **Paper pieces:** badges, cards and the example sheet are off-white paper (#FBF9F4) with a torn, rough edge and a
  small warm shadow. Nothing is tilted.
- **Type:** Roboto only. Title in Roboto Black, sentence case, on two or three lines, straight on the paper.
  Labels are black strips with white letters. No serif.
- **Ink:** OCHA blue icons with a light ink speckle. Blacks are lifted (#232120), never pure.
- **Marker:** an OCHA Orange (#F58220) hand-swiped marker behind one or two key words only, e.g. the trigger.
- **Accents:** a black “blast” for an event; OCHA blue badges with light icons (“inverted”) for side actions and for
  the people at the end of a flow; a flat light blue circle (multiply) to group things, which may overlap neighbours.

### Rules learned on the first job

- Sober and newsy, not happy: nothing tilted, no bouncy shapes, no bright backgrounds. A blue ground was “too blue”;
  a grey one too dark. Keep the ground near white.
- Groupings are geometric (circles, rounded shapes). Irregular hand-drawn outlines looked wrong: the paper edges and
  textures already carry the hand-made feel.
- Use blend modes so added colour sits *in* the paper (the grid shows through), not on it.
- Graphics like this one don’t need a sources line unless the client asks.
- Background details (lines, numbers, graphs) only as faint fragments multiplied into the ground with faded edges,
  never as a separate scrap of paper.

### Photos and archive material: the Public Domain Image Archive

For photos, engravings, old charts, maps and diagrams, use the **Public Domain Image Archive**
(pdimagearchive.org, from The Public Domain Review). Everything there is out of copyright, so **no credit is
needed**. Check the image page’s rights line (“Public Domain Worldwide” or “Not in Copyright”) before using it.
Mostly black and white, so it sits naturally on newsprint.

- Use black-and-white photo cut-outs or faint details blended into the ground.
- Search by tag (`/galleries/tags/<tag>`): graphs, charts, statistics, mathematics, maps, weather, money, finance.
  The gallery loads its images with JavaScript, so browse it in a browser; the full image is on each image page.
- Avoid images of death, plague counts, victims or suffering behind humanitarian content (the 1665 bills of
  mortality were rejected for that). Old disaster photos read as history, not as today.
- For people and current crises, OCHA’s own photos (`ocha-bdu-photo`, MediaValet) are usually better than archive.

### Limits

- **Editable .ai:** the textures are raster filters, so the exporter can’t keep them. Build the .ai from a vector
  copy: `templates/newsprint/make_ai_source.py` strips the filters, blend modes and `data-ai-name` tags (named
  groups made the exporter drop arrows and labels), then run `ocha-bdu-files-and-folders` export_ai on the copy.
  The .ai has live text and flat shapes; add the paper texture in Illustrator as a placed image if needed.
- Layer containers in the template must span the artwork (`.art > div` with the artwork’s width and height), or the
  exporter loses track of which layer things belong to.
- Exports are PNG while styles are explored; the editable .ai only for the chosen style, at the end.

---

## Cut-out

Paper cut-outs in one continuous world: flat OCHA shapes and icons cut from paper, with a hand-cut edge and a hard
shadow. The reference is the SG Awards 2026 Dataviz animation. The full look, the materials table, the kit and the
film process live in `ocha-bdu-animation` (`references/cutout-style.md`, `references/cutout-process.md`,
`templates/cutout/`). For a **static** cut-out graphic, use the same paper filter and colours without the motion.

A sober variant (16 Days of Activism cards, BDU, Nov 2026): no shaking, nothing tilted, darker tight shadows,
black label strips, torn and scorched edges for conflict content. Newsprint grew out of it.

---

## Adding a style

When a job produces a look worth repeating, add it here: a short section (feel, references, recipe, rules learned,
limits), a `references/<style>.md` with the values, and the job’s cleaned template under `templates/<style>/`.

## Saving and naming files

Folders, names, exports and the editable version follow **`ocha-bdu-files-and-folders`**.

---

## Project Owner
Javier Cueto, Head of Brand and Design Unit

## Maintained by
**OCHA Brand and Design Unit (BDU)**
- Team: ochavisual@un.org
- Focal point: Javier Cueto (cuetoj@un.org)

<!-- bdu-suggest-change:start -->
**Suggesting a change to this skill.** If the person corrects you or states a rule that would apply to other jobs too, or you find this skill is wrong or missing something, say so once, at the end of your reply. Don’t do this for changes that only concern the current job, and don’t edit the skill yourself, because the next update would overwrite it. Leave out anything confidential from the job. Say:

> This could be worth adding to the OCHA BDU skills. If you agree, copy this message and send it to Javi:
> **Skill:** ocha-bdu-graphic-styles
> **Proposed rule:** [the rule, in one or two sentences]
> **Why:** [what happened, with one example]
<!-- bdu-suggest-change:end -->
