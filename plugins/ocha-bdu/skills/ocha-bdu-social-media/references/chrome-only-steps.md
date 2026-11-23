# Canva steps the connector cannot do — done in the Canva editor in Chrome

The Canva connector cannot change a font family or weight beyond normal/bold, add or clear guides,
set page transitions or page timing, or remove animations. These are done in the Canva editor, in
Claude in Chrome (the person’s own Chrome, signed in to Canva).

Ground rules:

- **Tell the person first** that these steps need Chrome, and why (the connector can’t do them).
- **Close any open connector edit on the same design first.** An open connector draft and Chrome
  edits on the same design can overwrite each other. Chrome edits save automatically.
- **Never type while the canvas has focus.** Canva’s keyboard shortcuts fire: “T” creates a text box.
  Type only into a field you have just clicked and confirmed. If a stray element appears, delete it
  straight away and check nothing else changed.
- **Click controls by their accessibility label** (`find`), not by guessed coordinates, wherever possible.
- Open a design: `https://www.canva.com/design/<DESIGN_ID>/edit`. Wait ~8 s for it to load.

## Guides (12-column grid with margins)

File → Rulers and guides → (if old guides exist: Clear guides, then reopen) → Add guides → Custom:

| Field | Value |
|---|---|
| Columns | 12 |
| Gap | 24 px |
| Margin | 72 px |
| Rows | 1 |
| Row margin | 72 px |

→ Add guides. Canva confirms “Guides added and locked”. Guides apply to every page.

**Gotcha:** a design copied *through the connector* (copy-design) does **not** keep its guides.
After copying a template with the connector, check File → Rulers and guides: if there is no
“Clear guides” option, the guides are missing — add them again.

## Transition and timing (video-ready)

1. Click the transition marker between page 1 and 2 thumbnails (accessibility label “Change transition”).
2. Choose **Dissolve**, duration **0.5**, then **Apply between all pages**.
3. Select a page, click the clock icon on the page toolbar, type **4** in the value field and press
   Return, then click the **Apply to all pages** button.

## Remove animations

Select a page → **Animate** (page toolbar) → **Remove all animations**. This works per page:
repeat on every page, then reopen the panel on each page to confirm nothing is selected.

## Font and weight

Social media uses **Inter**; photo credits stay in Roboto Condensed (Javier, 19 Oct 2026).

1. Select the text box, then click the font selector (accessibility label “Toggle font selector, current font: …”).
2. Click “Show the font styles for Inter”.
3. Pick the style by its accessibility label: Black = **“Heavy”**, ExtraBold = **“Ultra Bold”**, Bold = “Bold”.

**Bold on part of a text box** (e.g. “Another **$480 million** is needed…”): the connector can only bold a
whole box. In Chrome, select just those words and pick **Ultra Bold** in the font panel as above. **Never
Cmd+B:** on Inter SemiBold it removes the bold instead of adding it.

If the design uses another font: pick Inter in the font panel and use **Change all → All pages**
(“Change all Raleway → Inter”), then set weights per element. Afterwards re-read the design through
the connector: every text element’s fontRef should be `YAFdJvSyp_k,…` (Inter) — then re-check line
breaks, orphans and the 48 px gap above credits, because Inter sets wider than most fonts.

## Copy a mock-up into the live design (same link)

When changes were built in a copy of the design: open both designs in two tabs. Per page: in the copy,
click the grey area beside the page, Cmd+A, Cmd+C; in the live design, open the same page, click the grey
area, Cmd+A, Delete, Cmd+V. Check each page, then move the copy to the Bin when asked. The live link and
the page settings stay as they were.

## Delete a design

Open it → File → Move to Bin → confirm. It stays restorable in the Bin for 30 days. Only on explicit request.

## Rename a folder

Open the folder → title “More actions” (…) → Rename → select all, type, Enter.
