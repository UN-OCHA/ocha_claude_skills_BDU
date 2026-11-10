---
name: ocha-layout
description: >
  Lay out or build OCHA reports and page templates in InDesign or Word: grid, alignment, styles
  and overrides, key figures, tables, chart frames, toolkit pages, tips, translated versions and
  template checks. Learned building the HNRP 2027 templates, which are the reference for OCHA
  report layouts. Use whenever someone asks to "lay out a report", "build an InDesign template",
  "make a Word template", "fix overrides", "clean up the styles", "tidy the template", "put this
  on the grid", "key figures", "at a glance page", "Flash Appeal template", "HNRP template",
  "toolkit pages", or "make a French version of the template". For the yearly HNRP update, this
  skill plus the HNRP playbook in the HPC templates folder. For colours, type and logos use
  `ocha-visual-identity`; for chart design `ocha-dataviz`; for maps `ocha-mapping`; for wording
  `ocha-editorial-style`; for folders and file names `ocha-files-and-folders`.
---

# OCHA layout

Rules and tools for OCHA page layouts, in InDesign and Word. Online products are not covered:
each online platform has its own limits.

**Read the guide for your tool before working:**
- InDesign: `references/indesign.md`
- Word: `references/word.md`
- Any translated version: `references/languages.md`

## The reference

**The HNRP template is the reference for OCHA report layouts.** A new report template, or an
update to an older one such as the Flash Appeal, is a version of it: same grid, style logic and
common parts, keeping only what that report needs. Report types differ, so take the parts that
fit and don’t force the rest.

- InDesign package (HNRP 2027): https://www.dropbox.com/scl/fo/v7cjjkjis6h81ezpn5a4j/AFujFBqyxyHiAM19-YM0Dl8?rlkey=pa2m6wpri2p7pu2t4ycfy7yep&dl=1
- Word template (HNRP 2027): https://www.dropbox.com/scl/fi/i3imgef168lmbjvulm0qs/HNRP_2027_Word_Template_EN.dotx?rlkey=h3acjlqj8je6vtd3a80dova70&dl=1
- Common parts to reuse: at a glance, key-figure rows, figure tables, chart and map frames with
  titles, boxes, quotes, buttons, toolkit pages.

When a reference file has layers, only what is visible on top counts. Render it (PowerPoint to
PDF) and never extract hidden images from it.

## Layout rules, any tool

- **Left-aligned, always.** Every block starts on grid column 1 unless told otherwise. Never centre
  a block on the page or mix alignments on one page.
- **Stick to the grid.** Size frames, charts and table columns in whole grid columns.
- **Resize by grid columns, don’t rebuild.** When a chart is too tight, give it one more column and
  take one from its neighbour.
- **Key-figure rows:** a thin separator line between the figures only, never on the outer edges.
- **Big figures:** grey by default, with colour added by character style or on the figure: OCHA blue
  = in need, OCHA orange = targeted, OCHA red = prioritized. Requirements and partners stay grey.
- **Tables:** text in the first column starts on the margin, so it lines up with the body text.
- **Print charts are made in the Humanitarian DataViz Tool.** Datawrapper is for online products. Plan
  a chart once, and expect to build it once per medium.
- **Prioritized bars are solid red,** with no hatching, also in key swatches. Whether a table gets
  separate small bars per column is decided case by case (`ocha-dataviz`).
- **QR code + button, where used:** one position on every page, on the grid. QR codes can be an
  exception to “no QR codes” in Word when the audience can manage them.
- **Roboto Slab appears only on the cover, back cover and quotes,** with exceptions when a design
  needs them.
- **Colours are named OCHA,** never UN: in swatches, styles, tips and notes.
- **Icons:** OCHA Humanitarian Icons only, chosen by picture rather than name (`humanitarian-icons`).

## Styles and overrides, any tool

- **Every text format is a style.** No local overrides.
- **As few styles as possible,** so designers aren’t overwhelmed. Delete unused ones and merge
  near-twins.
- **A style must itself say how its text looks.** No patches on top of a base style. Nested styles
  only for real automation, such as a bold lead-in.
- **Names:** sentence case, thing + variant, one level of folders. Boxes and similar are named by
  look (“Box text blue”), not by concept. In Word, every style starts with the template’s prefix.

## How to work

1. **Copy, don’t touch.** Back up before any change, and never save into last year’s folder.
2. **Compare the brief with the current template** and list what really changed. Change only that.
3. **One change at a time, with proof.** Export before and after, pixel-compare them and look at every
   changed page. When asking about layout, send page images of the current state and the proposal.
4. **Style or structure changes reflow text.** A template with one main story can shift a whole
   section, so check every page after them.
5. **Check in the real output:** charts in a PDF exported from InDesign, not only in the browser;
   Word templates in real Windows Word.
6. **Run the checks before calling it done** (each guide lists them), then ask a person to open the
   file: scripts can’t confirm everything a designer will see.

## Scripts

`scripts/indesign/` holds the reusable InDesign tools, listed in `references/indesign.md`. Copy them
to the job’s own scripts folder, or call them from here. They take paths as arguments and hold no
job-specific names.

## Project Owner

Javier Cueto, Head of Brand and Design Unit

## Maintained by

**OCHA Brand and Design Unit (BDU)**
- Team: ochavisual@un.org
- Focal point: Javier Cueto (cuetoj@un.org)

<!-- bdu-suggest-change:start -->
**Suggesting a change to this skill.** If the person corrects you or states a rule that would apply to other jobs too, or you find this skill is wrong or missing something, say so once, at the end of your reply. Don’t do this for changes that only concern the current job, and don’t edit the skill yourself, because the next update would overwrite it. Leave out anything confidential from the job. Say:

> This could be worth adding to the OCHA BDU skills. If you agree, copy this message and send it to Javi:
> **Skill:** ocha-layout
> **Proposed rule:** [the rule, in one or two sentences]
> **Why:** [what happened, with one example]
<!-- bdu-suggest-change:end -->
