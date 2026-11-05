# InDesign guide

## Template rules

- **Nothing anchored (recommendation, not a hard rule).** Text goes in first, then charts, maps, QR
  codes and buttons as free frames with text wrap. Anchoring caused many problems in the HNRP
  template. Inline icons inside buttons are fine.
- **Object styles for frames,** set as the document’s defaults for new frames: main text, other text
  (ignores wrap), photo/graphic frame (Jump Object wrap), table frame, logo/QR frame, graphic title
  frame.
- **Every table has a table style and cell styles,** with paragraph and character styles inside and no
  overrides. A few table styles by type are fine. Lines between columns belong in the table style.
- **Styles must be clean:** no switched-off option (rule, shading, border, underline, strikethrough)
  holding a leftover colour, and no empty folders in any panel.
- **Swatches are OCHA colours only,** plus a non-printing tips colour.
- **Boxes use paragraph shading.**
- **Groups:** only real units stay grouped (title + map, the shapes of one icon). Never group pieces
  for convenience.
- **Keep character styles,** even if used only in the toolkit.
- **Tips sit on a non-printing layer** (layer “Printable” off), short, and only covering what designers
  can’t work out alone. A tip starts level with its element, and tips use their own styles.
- **The template stays clean.** Toolkit pages, showing all paragraph, character and object styles, live
  only in the sample file, and a tip points to them. Examples get their grey from a box behind them.
- **Contents:** icons beside headings are positioned graphics, never inline, or they get copied into
  the contents. “Remove Forced Line Break” only works through the Update Table of Contents command;
  `doc.createTOC()` ignores it.
- **Charts:** one Illustrator graphics file works well: A4 artboards on the InDesign grid, each chart at
  its page position and editable with the DataViz plugin. InDesign frames show the page’s artboard
  placed full-page. After updating a link, check the chart hasn’t shifted inside its frame.

## Driving InDesign by script

- `run_jsx.sh <script.jsx> key=value …` runs a script. Arguments go through a generated file, so quotes
  and GREP patterns are safe. Set `INDESIGN_APP` for another version (default “Adobe InDesign 2026”).
  `run_ai.sh` does the same for Illustrator (`ILLUSTRATOR_APP`).
- Set `UserInteractionLevels.NEVER_INTERACT`, so no dialog blocks the script.
- **Before any changing script,** check nobody has the file open:
  `osascript -e 'tell application "Adobe InDesign 2026" to get name of documents'`.
  A changing script would save and close their window.
- **Only close documents your own script opened.** Wrap changing scripts in try/catch that closes that
  document unsaved on error, and never loop over `app.documents`.
- Opening a `.indt` gives an untitled copy unless you use `OpenOptions.OPEN_ORIGINAL` (`openOriginal` in
  `lib.jsxinc`).
- **Non-ASCII text in `.jsx` must be `\uXXXX`** (`escape_jsx.py`): scripts are read in the system encoding.
- New text frames: set a single column and auto-height, then stack blocks from their real heights. Set
  `doc.activeLayer`, or new items land on the tips layer.
- **Never write back fonts read from text ranges:** they report the effective font, including nested
  styles, and writing it hard-codes it.
- **Font names can’t be changed by scripting:** use an IDML round-trip.
- **Exported PDFs don’t prove fonts are fine.** Run `check_fonts.jsx` and have a person open the file.
- Paragraphs forced onto a new page report their insertion point on the previous page: use
  `characters[0]` to find the page.
- An inline group in a line that holds a table won’t release, with no error. Copy it out instead.
- Never `clearOverrides` on a paragraph holding a table, and never use `clearObjectStyleOverrides` in bulk.
- Before deleting a character style, dump every property it sets: deleting one can silently remove a
  font or width elsewhere.
- **`[None]` on a chart group froze InDesign three times (cause unknown).** It has worked on lines and
  rectangles. Test on a copy first.
- Keep document text and chart text apart: a placed chart is not searchable text.

## Checks before calling a template done

| Check | Script | Clean means |
|---|---|---|
| Text overrides | `export_idml_copy.jsx`, then `overrides_idml_audit.py` | Only page-number variables remain. This matches InDesign’s Style Override Highlighter; `find_plus.jsx` and `styleOverridden` miss some, such as language |
| Frame overrides | `frames_audit.jsx`, `overrides_full_audit.jsx` | None. Nested and GREP style effects are not overrides |
| Table and cell overrides | `tables_audit.jsx`, `tables_override_test.jsx` | None (`plant=1` is the self-check) |
| Patches in styles | `style_patch_audit.jsx` | Its list has no in-use style drawn differently from what the style says; only real automation is nested |
| Leftovers in styles | `clean_off_options.jsx dry=1` | Lists nothing |
| Empty panel folders | `delete_empty_folders.jsx` | None left |
| Fonts | `check_fonts.jsx` | All installed; opens without a dialog |
| Links | `list_links.jsx`, `relink.jsx` | All inside the package |
| Swatches | `swatch_usage.jsx` | OCHA colours only, all used |

**Other tools:** `inventory.jsx` (structure), `style_census.jsx`, `style_full_dump.jsx` (compare two files:
styles must be identical across a template and its sample), `find_text.jsx`, `apply_text_changes.jsx`,
`export_preview.jsx`, `set_table_columns_grid.jsx`, `svg_ink.swift` (real size of a chart SVG).
