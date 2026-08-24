---
name: ocha-logo-production
description: >
  Produce and verify a logo or lockup package from an Adobe Illustrator master —
  every language and colour variant, exported to PNG and SVG with correct
  filenames, the right fonts and exact brand colours, driving Illustrator
  headlessly. Use this skill whenever the user wants to build or update a logo
  package, add a language or a colour variant, roll a dated logo forward to a new
  year, export artboards from an .ai file, or automate Illustrator. Trigger on
  "logo package", "multilingual logo", "export the logo", "update the 2027 logo",
  "add Arabic", "logo variants", "white version", "export artboards", "batch
  export", "exportForScreens", ".ai file", "JSX", "ExtendScript", and on symptoms
  like "the Arabic looks wrong", "the font changed", "the yellow is not right",
  "my export is cropped". For logo usage rules, clear space and brand colours use
  `ocha-visual-identity`; for charts `ocha-dataviz`; for maps `ocha-mapping`.
---

# OCHA logo production

How to turn an Illustrator master into a verified logo package — every language,
every colour variant, PNG and SVG — without touching the UI.

The techniques here are general to Illustrator automation, so they carry to any
multi-artboard export; the defaults and examples assume a logo or lockup.

**The one rule everything else serves: verify in pixels, never in logs.** Every
defect this skill exists to prevent produced a clean, successful log. A missing
font, a shifted colour, a cropped image and a stray guide layer all export
"successfully". Look at the output.

## 1. Drive Illustrator from the shell

Illustrator must already be running. Then:

```bash
osascript -e 'tell application "Adobe Illustrator" to do javascript file "/absolute/path/to/build.jsx"'
```

Four things will bite you, in this order:

- **`alert()` and `confirm()` block forever.** A script that is fine interactively
  hangs an automated run with no output. Set
  `app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS`, write a
  log file instead of showing dialogs, and read the log to find out what happened.
- **`$.fileName` only resolves for `do javascript file`**, not when the script
  body is passed as a string. Hardcode the base path in a constant near the top.
- **`osascript` can outlive your timeout while the script succeeds.** Don't
  conclude it failed. Launch it in the background and poll the log for a
  terminating marker:

  ```bash
  nohup osascript -e '…do javascript file "…/build.jsx"' >/dev/null 2>&1 &
  for i in $(seq 1 60); do grep -qE "OK done|ABORT|ERROR" build.log && break; sleep 5; done
  ```

- **Per-character loops are slow.** Reading `characterAttributes` for every
  character in a document takes minutes. Read the whole `textRange` instead, and
  only drop to characters when you must.

`scripts/build_template.jsx` is an annotated skeleton with all of this wired up.

## 2. Fonts — the trap that costs the most

**Illustrator silently substitutes a missing font and reports success.** The `.ai`
keeps the correct font reference, so the file looks fine afterwards; only the
exported pixels are wrong. This has shipped to production more than once.

Check fonts *before* doing anything, and abort if any are missing:

```javascript
function fontInstalled(psName) {
    for (var i = 0; i < app.textFonts.length; i++) {
        if (app.textFonts[i].name === psName) { return true; }
    }
    return false;
}
```

Use **PostScript names** (`Roboto-Medium`, `Dubai-Medium`), not menu names. Non-Latin
faces are the usual casualty because nobody notices the shapes are wrong —
especially Arabic, where a substituted face changes stroke weight and line breaks.

## 3. Artboards become filenames

`exportForScreens` names each file after its artboard, so **name the artboards and
the exports name themselves**. Do the renaming inside the `.ai` once and it holds
for every future run.

A workable convention is `<PRODUCT><YEAR>_<variant>_<LANG>` — variant first,
language last, so files group by variant when sorted.

Masters usually contain artboards that are not deliverables: duplicates left over
from design, overview or reference boards, working areas. Keep an explicit skip
list rather than exporting everything and deleting afterwards — otherwise every
rebuild reinstates the files someone deliberately removed.

```javascript
var SKIP_EXPORT = { "PRODUCT_overview": true };
for (var b = 0; b < doc.artboards.length; b++) {
    var nm = doc.artboards[b].name;
    if (nm.indexOf("_dup") !== -1 || SKIP_EXPORT[nm] === true) { continue; }
    indices.push(b + 1);              // exportForScreens is 1-based
}
```

Settings that match OCHA practice: PNG24, transparency on, scale by width to
1024 px, art-optimized anti-aliasing; SVG web-optimized with **text outlined**
(`SVGFontType.OUTLINEFONT`) so the file carries no font dependency.

**Preserve layer visibility.** Unlocking every layer to work on a document is
fine; forcing every layer *visible* is not — it switches on guide and working
layers. Record the original state and restore it before saving or exporting.

## 4. Colour across RGB and CMYK

Decide which space the master lives in, and generate the other from it rather than
maintaining two by hand.

- **Digital-first** (portal, social, web): keep the master RGB so the files carry
  the exact brand hex, and generate a CMYK copy for print.
- **Print-first**: the reverse.

**Converting colour space shifts every colour**, so re-pin the brand colours
immediately afterwards. Two specific traps:

- RGB `#000000` converts to a **rich black** around CMYK 75/68/67/90 — four plates
  of ink where you wanted one. Force it back to `0/0/0/100`.
- Classify colours on well-separated traits, not exact values. A near-neutral dark
  ground and a yellow can both carry a high yellow plate; **cyan** separates them,
  the yellow channel does not.

Log the values as converted *and* after pinning, so a wrong classifier is visible
in the log instead of silently leaving one object off-brand.

Get the target values from `ocha-visual-identity` — never retype a brand colour
from memory.

## 5. Editing text without wrecking it

To roll a year forward, or change one word, **edit only the characters that
change**. Replacing `textFrame.contents` wholesale resets per-character styling
and kerning across the whole frame.

```javascript
tf.characters[idx + 3].contents = "7";   // 2026 -> 2027, final digit only
```

Wrap it in `try/catch` with a full-string replace as the fallback, and make the
whole step a no-op when the text already reads correctly, so re-running is safe.

## 6. Verify — the battery that catches real defects

Bundled in `scripts/`, all Pillow-based:

```bash
python3 scripts/analyse_pngs.py <export-dir>              # size, alpha coverage, art bbox, dominant colours
python3 scripts/contact_sheet.py <export-dir> sheet.png    # labelled sheet composited on mid grey
python3 scripts/compare_glyphs.py OLD.png NEW.png cmp.png  # trims, normalises height, stacks for comparison
```

What each is for:

- **Contact sheet on mid grey** — the only way to see white-on-transparent variants
  at all. Look at it; do not just generate it.
- **Colour counts per file** — confirms each variant is what its name claims
  (yellow bar vs white bar, transparent vs baked background) and that brand colours
  landed exactly. Antialiased edge pixels will always sit between two brand
  colours; sample an interior pixel before calling a blend a defect.
- **Glyph comparison against last year's file** — the check that catches a font
  substitution. Shapes must match, with only the changed characters differing.
  **Keep a copy of the previous version's non-Latin export before rebuilding**, or
  there is nothing to compare against.

## 7. Handing the files onward

- Public download links → `dropbox-public-link`. Never the Dropbox MCP's
  `create_shared_link`.
- Brand portal → `frontify-operations`. Image/asset blocks are UI-only; text
  blocks are updatable, and anchors need `class="link"` or they render as grey chips.
- **Canva** has two traps worth knowing:
  - Frames **crop to fill**, so an image whose aspect differs from its frame loses
    its edges. Produce one image per frame, cut to that frame's exact ratio.
  - `update_fill` scales the new image up (~19% in practice) and clips it. Follow
    every replacement with `crop_media` resetting the image box to `top 0, left 0,
    width = frame width, height = frame height`.
  - Canva's fetcher does not follow redirects. A Dropbox `www.dropbox.com/…&dl=1`
    URL 302s and fails; `dl.dropboxusercontent.com/scl/fi/…?rlkey=…` returns the
    bytes directly.

**Publishing folders are load-bearing.** Once a folder is behind a public link on
a live page, renaming or recreating it breaks that page. Change files inside it
freely; leave the folder alone, and say so in the project README.

## 8. Leave the project rebuildable

A year later nobody remembers any of this. Ship with the assets:

- one idempotent build script — safe to re-run, reporting zeros when nothing changed
- the verification scripts
- a README naming the fonts, the colour values, what is published where (block ids,
  design ids), and which folders must not be moved

## Maintained by

**OCHA Brand and Design Unit (BDU)**
- Team: ochavisual@un.org
