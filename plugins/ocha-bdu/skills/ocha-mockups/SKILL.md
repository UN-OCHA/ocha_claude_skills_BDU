---
name: ocha-mockups
description: >
  Put a cover, page, screenshot or design (a PDF page, PNG or JPG) into a Photoshop mockup
  template and export a finished mockup image or PDF, without Photoshop. Print (magazines,
  books, A4 pages, posters, business cards, roll-up banners) and screens (website on a laptop
  or desktop, app on a phone): flat front-facing or in perspective, one design or two (front
  and back). Also makes "cover options": several designs, one mockup per page, with labels,
  as one PDF. Use whenever someone asks for a "mockup", "magazine mockup", "book mockup",
  "report mockup", "cover mockup", "poster mockup", "business card mockup", "roll-up mockup",
  "website mockup", "phone mockup", "app mockup", "device mockup", "show the cover on a
  magazine", "put this on a poster/phone/laptop", "cover options", "compare covers", "how will
  it look printed", "mock it up", "PSD mockup" or "smart object".
---

# OCHA mockups

Turns a design into a realistic mockup by filling a Photoshop template’s smart object with it.
Everything runs in Python on the computer: **Photoshop is not needed**. The template’s own
shadows, reflections, lighting and blend modes are kept exactly; only the design changes.

`<skill>` below means this skill’s folder (the base directory shown when the skill loads).
`M=<skill>/scripts/mockups.py` in every command.

---

## 1. Every time: check the templates are on this computer

The templates are BDU’s curated set in the OCHA DMU Dropbox:
`~/OCHA DMU Dropbox/<your-name>/Design/Resources/ocha_claude_skills_BDU/mockups`.
Dropbox often keeps them **online-only**, and then they can’t be opened. So before the first
render in a session, check the template(s) you are about to use:

```bash
python3 $M ready magazine-a4-flat          # or several keys, or none for all
```

- **Exit code 0** (“All ready”): go on.
- **Exit code 3**: the template is online-only. The script prints a message starting
  `ASK THE PERSON`. Pass it on in plain words, then **stop and wait** for their reply. Don’t
  look for another copy, and don’t download it from anywhere else. When they say it’s done,
  run `ready` again: a big template can take a few minutes to arrive after the tick.
- **Exit code 2**: read the message. “Can’t find the folder” means Dropbox isn’t syncing it or
  the person has no access (ochavisual@un.org). If they keep it somewhere else, run
  `python3 $M setup --folder "/path/to/mockups"` once. The `OCHA_MOCKUPS_FOLDER` environment
  variable works too.

`render` makes the same check and gives the same exit codes, so a forgotten `ready` is caught.

**Python packages**, once per computer. If `python3 -c "import psd_tools, scipy, fitz"` fails:

```bash
python3 -m pip install "psd-tools[composite]" pymupdf
```

On a Mac where pip refuses with “externally managed environment”, add `--break-system-packages`.

**Licences.** The templates are bought or free-with-attribution files. They stay in that
Dropbox folder only. Never copy one into a job folder, a repository or this skill, and never
publish or send one. (The folder sits inside the skills repository, but git ignores it.)
Finished mockup images are fine to share: that is what the templates are for.

---

## 2. Make a mockup

```bash
python3 $M templates                       # the curated set, and which are ready here
python3 $M render magazine-a4-flat --design report.pdf#1 --out export/report_cover_mockup.png
```

- `--design` takes a PDF page (`file.pdf#3`; page 1 if omitted), a PNG or a JPG. PDFs are
  trimmed to the page (bleed hidden); `--bleed` keeps it. For screens, give a screenshot PNG
  at the screen’s shape (`inspect` shows it).
- `--out` ends in `.png`, `.jpg` or `.pdf`. Save into the job’s `export/` folder, named per
  `ocha-files-and-folders`.
- `--width 2000` scales the result down for email or slides. Default is the template’s size.
- **Look at the result** before handing it over: open it and check the design is where it
  should be, the right way up, and nothing important was cropped.

**Cover options** (the product approved for the OCHA Annual Report 2025): several designs,
one mockup per page, each with a label, in one PDF.

```bash
python3 $M render magazine-a4-flat \
  --design cover_current.pdf --label "Current cover" \
  --design cover_alt1.pdf    --label "Alternative 1: Ethiopia" \
  --design cover_alt2.pdf    --label "Alternative 2: Haiti" \
  --out export/OCHA_AR_2025_cover_options.pdf
```

Labels are Roboto Bold Italic, just above the design’s top-left corner (or a clear corner if
that would cover something), black or white depending on the background. Override with
`--label-pos x,y` (pixels, or 0–1 fractions) and `--label-color "#000000"`. Write labels in
OCHA style (`ocha-editorial-style`).

**Two designs in one template** (business card front and back, a spread): a PDF fills the
slots with consecutive pages, left to right (`--design card.pdf#1` puts page 1 in slot 1,
page 2 in slot 2). For images, or to choose, use a spec file:

```json
[{"label": "Front and back", "slots": {"1": "front.png", "2": "back.png"}}]
```

```bash
python3 $M render <key> --spec cards.json --out export/cards_mockup.png
```

A template whose **one** slot is a whole spread takes two consecutive single pages side by
side with `--spread` (or `"spread": true` in its catalogue entry). Not automatic: a landscape
A-size poster has the same shape as two pages.

**Cropping and label spot.** `--crop left,top,right,bottom` (template pixels) keeps part of
the scene; `--crop none` undoes a template’s own crop. A template whose default label spot
hits something (poster clips) has its own spot in the catalogue.

**When the shapes differ** (a 3:4 slot and an A4 cover): up to 2% is stretched invisibly;
beyond that the design is cropped to fill, and the script says how much. Choose what
survives with `--focus x,y` (0–1; `0.5,0.2` keeps the top), or use `--fit fit` (white
margins) or `--fit stretch`. Tell the person when something was cropped.

**Reshape: when the design’s shape differs from the object (some templates only).**
`--reshape` changes the poster or page itself to the design’s shape, instead of cropping the
design or adding margins: an A4 cover on the square poster makes the poster A4. It cuts one
straight strip out of the whole scene (paper, wall, shadows, lighting), cross-fades the join,
and fits the design to the new shape.

```bash
python3 $M render poster-square --design cover.pdf --reshape --out export/cover_poster.png
```

**It might not always work: it depends on the mockup.** It only looks right where the strip
crosses plain, repeating things (blank paper, a textured wall, a plain backdrop), never a
hand, a clip, a device or a diagonal light streak. So:
- It runs on templates with a **checked reshape zone** in the catalogue: today
  `poster-a-portrait`, `poster-a-landscape`, `poster-square` and `a4-page` (each tested with
  A4, A landscape, square, US Letter and 16:9 designs). Anywhere else it stops and says so.
- It can only cut, never add: an object gets narrower or shorter, by as much as its zone
  allows. Beyond that it stops and gives the limit; use `--fit` or another template.
- To try it on another template, give a strip by hand along x or y, in canvas pixels:
  `--reshape x=1000:1700`. **Always look closely at the result** (zoom on the join), and tell
  the person it was reshaped. If it looks right and will be reused, add the zone to the
  catalogue (`reshape`, plus `reshape_hide` for layers a straight cut can’t cross, such as
  a diagonal gloss).

**Background colour.** Templates with a plain colour background take another one with
`--background "#D6D6D6"`; `--background keep` uses the template’s own. Photo backgrounds
can’t be recoloured.

---

## 3. The curated templates

Every one was rendered with a test card and with a real OCHA design, and looked at, on
20 October 2026. Keys go straight into `ready` and `render`. Folder per type inside `mockups/`.

| Key | What it shows | Design shape | Notes |
|---|---|---|---|
| `magazine-a4-flat` | A4 magazine or report cover, flat, front-facing, light grey | A4 portrait | The approved cover-options look. Grey #D6D6D6 by default |
| `magazine-a4-spread` | A4 magazine open at a spread, front-facing | 2 × A4 portrait | See “Spreads” below |
| `magazine-a4-perspective` | A4 magazine cover on a stack, in perspective | A4 portrait | |
| `a4-page` | Single A4 page (flyer, letter, one-pager), soft shadow | A4 portrait | |
| `laptop-website` | Website on a laptop, in perspective | 16:10 screenshot | 16:9 loses ~10% at the sides |
| `phone-app` | App or mobile site on a phone held in a hand | 9:16 screenshot | Older iPhone model |
| `poster-a-portrait` | A-size poster hanging on a wall with clips | A-series portrait | Gentle paper curve; cropped to a short length of wire |
| `poster-a-landscape` | Same, landscape | A-series landscape | |
| `poster-square` | Same, square | Square | Reshapes well to A4 or landscape |
| `business-card-us` | One US-size card on a stone ledge, dark background | 3.5×2 in (1.75:1) | |
| `business-cards-us-front-back` | Card stack (front) and a leaning card (back) | 3.5×2 in, 2 designs | Slot 1 stack, slot 2 leaning card |
| `rollup-85x200` | Roll-up banner 85×200 cm, front view | 0.425:1 | Small canvas: screens and slides |
| `rollup-100x200` | Roll-up banner 100×200 cm, front view | 0.5:1 | Small canvas: screens and slides |

**Not covered yet:** European business cards (85×55 mm): the library has none, and a
US template crops an EU card by about 12%. Say so if asked, and suggest the US template
with `--fit fit` as a stopgap.

**Spreads.** Give the PDF and the spread’s first page: `--design report.pdf#4`. If page 4
is a single wide spread page (InDesign often exports spreads that way), its left and right
halves go on the two pages. If the PDF has single pages, pages 4 and 5 are used.

`references/library_survey.md` has the whole BDU library (105 templates), with what works,
what doesn’t, and why.

---

## 4. Any other template

The full BDU library (`Design/Resources/PS/mockup`, about 1.3 GB, mostly online-only) and any
RGB `.psd`, `.psdt` or `.psb` with a smart object also work, by path:

```bash
python3 $M inspect "/path/to/template.psd"      # its slots: name, size, shape, warnings
python3 $M check   "/path/to/template.psd"      # does this engine draw it like Photoshop?
python3 $M render  "/path/to/template.psd" --design design.pdf --out export/test.png
```

A file path skips the curated set but not the online-only check: exit code 3 means asking
for that template’s folder to be made available offline, as in §1.

- `inspect` numbers the slots left to right, marks which take a design and which are
  decoration (background textures, noise, card edges), and flags what can’t be reproduced.
- `check` renders the untouched template and compares it with the preview Photoshop saved in
  the file: **faithful** (indistinguishable), **close** (small colour differences) or
  **DIFFERS** (look hard before using it).
- To add a template to the curated set (BDU only): copy it into the right type folder in
  `mockups/` with its licence file, add an entry to `scripts/templates.json` (path relative to
  `mockups/`, a plain title, the slot shape, `design_slots` if `inspect` guessed wrong, and
  `hide_layers` for the template author’s credit text or an old sample pasted over the smart
  object), render a real design and look at it, then run `python3 $M selftest --only <key>`.

**What works:** every blend mode, opacity, masks, clipping, layer effects, adjustment layers,
flat and perspective placement (the smart object’s four corners), curved pages and bent
surfaces (Photoshop’s custom warp, checked against Photoshop’s own pixels), several copies of
one smart object, several smart objects, and the smart filters mockups use for shadows
(Gaussian Blur, Motion Blur, Hue/Saturation lightness). Shadow copies turned to a solid colour
are kept exactly as Photoshop drew them.

**What doesn’t:** other smart filters (noise, texture, Blur Gallery: left out, with a
warning), text layers that need re-rendering, and CMYK or Lab templates (open once in
Photoshop and convert to RGB; 16-bit RGB is fine). When a template relies on these, say so and
suggest another one.

**After a psd-tools update**, run `python3 $M selftest --out selftest.jpg`: it renders every
curated template with a test card and checks the design is there and the right way up.

---

## Project Owner

Javier Cueto, Head of Brand and Design Unit

## Maintained by

**OCHA Brand and Design Unit (BDU)**
- Team: ochavisual@un.org
- Focal point: Javier Cueto (cuetoj@un.org)
