---
name: ocha-dataviz
description: >
  Apply OCHA's data-visualization principles and rules when building charts,
  infographics, dashboards, or any data-driven graphic for humanitarian
  products. Use this skill whenever the user asks to "make a chart", "pick a
  chart type", "design an infographic", "visualize data" for OCHA/HNRP/Flash
  Appeal/GHO products, or asks for OCHA dataviz rules (bar/line/pie/stacked/
  donut/matrix/icon). Trigger on phrases like "OCHA chart", "OCHA dataviz",
  "humanitarian dataviz", "dataviz rules", "which chart should I use", or
  "infographic guidelines". For the Illustrator plugin RELEASE workflow, use
  `ocha-dataviz-release`. For map-making specifically, use `ocha-mapping`. For
  logo / brand colours / design system only, use `ocha-visual-identity`.
---

# OCHA Data Visualization

The foundation of every OCHA dataviz product is: **data + story + design**.
All three must be present. Good data + good design without a clear message is
worthless; a good message + good design with bad data is misleading.

---

## 1. Core design principles

### Simplification — progressive reduction
Apply in this order to declutter any chart:

1. Remove background colours
2. Remove redundant labels
3. Remove borders
4. Reduce the colour count
5. Remove special effects — **no 3D, no drop shadows, ever**
6. Remove gridlines; prefer **direct labelling**
7. Round numbers (k / M / B — see §5)
8. Adjust text size / weight
9. Change to a brand font
10. Adjust spacing

### Visual hierarchy
The most important information must be the most visually prominent. You have
three levers only:
- **Size** — larger is seen first
- **Contrast** — hue and intensity pull the eye
- **Position** — top-left is read first; follow the **"Z" path** (upper-left → upper-right → diagonal → lower-right)

### Layout
- **12-column grid** as the base; subdivide into 2, 3, 4-column or combinations (3+6+3).
- **Minimum margins**: 1 cm on all sides for print.
- **Alignment**: every element must line up against something — never placed randomly.
- **Proximity**: related items close; unrelated separated (by space or a subtle divider).
- **Enclosure**: the eye groups enclosed items. Use a light box to say "these belong together".
- **Connection**: connected items read as a group.
- **Consistency**: styles repeat within the piece. Not boring — consistent.
- **White space is required.** Neither cluttered nor empty.

---

## 2. OCHA product-family styles

When building charts, pick the product-family style first. Each has its own
primary colour and palette; other OCHA rules (typography, layout, rounding,
direct labelling) are shared.

| Family | Key | Primary | Typical use |
|---|---|---|---|
| OCHA (general) | `ocha` | `#009EDB` UN Blue | General OCHA products, Situation Reports |
| HNRP (Humanitarian Needs & Response Plans) | `hnrp` | `#F58220` Orange | Country HNRP documents |
| Flash Appeal | `flash` | `#ED1847` Red | Flash Appeal documents |
| GHO (Global Humanitarian Overview) | `gho` | `#FFC800` Gold | GHO flagship report |

Within a style, use the full 7-step **colour ramp** (see `ocha-visual-identity`
for ramps) for sequential / tint-based colour coding. Reserve accent colours
for true highlights.

---

## 3. Typography (dataviz-specific)

- **Titles, labels, UI text**: Roboto (advanced users) or Arial (collaborative docs).
- **Tight spaces / compact infographics**: Roboto Condensed — infographic-only.
- **Captions, photo credits, small meta text**: Roboto Mono.
- **Long-form body text in a print report**: Crimson Pro.
- **Numbers**: right-align. Round using k / M / B. No unnecessary decimals.

**Body text rules**:
- Left-align (right-ragged). Never justify.
- Column width 40–80 characters, ~12 words per line.
- Do not use Arial Narrow, Avenir, Minion Pro, or Crimson Text.

---

## 4. Chart selection — pick the right type

### Text (most underrated dataviz type)
- For **key figures**, oversized typography IS the dataviz. Don't jump to a chart for a single number.
- Round and abbreviate: "2.3M people" not "2,347,829 people".

### Tables
- Universally accessible. Don't dismiss — good for exact values and small multiples.

### Bar chart (horizontal or vertical)
- The default chart for category comparisons. Most common in humanitarian work.
- **Y-axis MUST start at zero. No exceptions.** Clipping the axis to exaggerate differences is dishonest.
- **Direct label** bars; no gridlines if direct-labelled.
- If gridlines are needed, use discreet grey lines.
- **No rotated X-axis labels** — switch to horizontal bars when labels are long.
- Sort bars by value (largest first) unless there's a categorical reason not to.
- Title must state **location, time increments, and units**. Footer: **source + date**.
- **Sharp rectangular corners** — no rounded corners on bars/columns.

### Stacked bar / column
- For comparing totals with breakdowns.
- **Maximum ~3 categories** before it becomes unreadable on print. Interactive charts can handle more.
- Sort by total. Legend must be visible.

### 100% stacked bar
- For breakdown analysis where the total = 100%.
- Up to **3 categories** because equal bar lengths help the eye compare.
- Useful when absolute values vary greatly (small categories stay visible).

### Line chart
- Best for **time-series trends**.
- Y-axis **does not** need to start at zero (unlike bar charts). Pick the scale that makes the trend readable.
- Use natural increments: 0, 5, 10, 20, 30 or 0, 25, 50, 75, 100 — divisible by 1, 2, or 5.
- Line weight: thick enough to stand out over gridlines, thin enough not to obscure shape.
- No legend for single-series — label the line directly.
- Show points only when spacing allows and they highlight specific values. Don't show when density would hide the trend.

### Multiple-line chart
- **Maximum 4 lines.** Fewer if they cross a lot.
- More than 4 series → group into "Others", switch to bars, or use small multiples.
- Label next to each line, not in a legend.

### Small multiples
- The antidote to "spaghetti charts". Easier to compare than 5+ overlapping lines.

### Pie chart — use sparingly
- Popular but usually not optimal. Takes a lot of space for little info; humans are bad at comparing angles.
- If you must use one:
  - **Maximum 5 slices** (top 4 + "Others").
  - Must sum to 100%.
  - Largest slice starts at **12 o'clock**, then clockwise, largest → smallest.
  - Use a **colour ramp (tints)**, not distinct colours.
  - With direct labels + values, tints aren't needed — just highlight the key slice.
- **Never** 3D, never multi-pie comparisons, never >5 slices.

### Donut chart
- A pie with a hole in the middle. Use the hole for the total / key figure.
- Good for **binary data only** (funded vs unfunded, yes vs no). For length comparisons use a bar.

### Bubble / surface-area charts
- Good for **maps** (communication only; simple, no scale needed).
- Poor for analysis — comparing 2D areas is harder than comparing 1D lengths.
- Area = π × r². Scale by area, not radius.

### Matrix
- Condensed 3-variable display: 2 categorical × 1 numerical/categorical.
- Great for "who, what, where" (e.g., organisations × sectors × locations).
- Sort axes so the most important value is **top-left**.
- Use humanitarian icons in row/column headers. Add small locator maps.
- Data labels over coloured cells need white shadow / outline to read on both dark and light fills.
- Warning: may be too complex for unfamiliar audiences.

### Icon / pictogram chart
- For emphasis of headline figures. Always pair with a clear number.
- Use the **Humanitarian Icons v2** set from **brand.unocha.org**.
- Ship with OCHA blue `#009EDB` by default; may recolour to the active family accent.

### Sankey
- For flow data (source → target).
- Node width 15–40 (default 20), padding 5–40 (default 15), link opacity 20–80% (default 40%).
- Label modes: Name+Value / Name only / Value only / None.
- Single colour (default, using active family primary) or multicolour.

### Illustration
- Great for storytelling. Don't be too literal — suggest rather than depict.

---

## 5. Number rules

- **Round numbers and abbreviate**: `2.3M`, `450k`, `1.2B`.
  Real precision implies certainty we rarely have in humanitarian contexts.
- **Right-align** all numeric columns in tables and lists.
- **Don't use decimals** unless the decimal carries meaning.
- **Axis labels**: natural increments (1, 2, 5, 10, 25, 50, 100, 250, 500, 1000…).

---

## 6. Titles, sources, credits

Every chart needs:
- **Title**: states *what* (the subject), *where* (location), *when* (time window), *units*.
  Example: "People in need of humanitarian assistance, Sudan, Jan–Dec 2025 (millions)".
- **Source line** (footer): "Source: OCHA, HNRP 2025 — as of 15 Dec 2024"
- **Data date** — always include the "as of" date.
- **Footnotes for acronyms** — avoid acronyms in labels; if unavoidable, mark with `*` and footnote.

---

## 7. OCHA Humanitarian DataViz plugin (Illustrator)

For Illustrator-based work, the BDU's **OCHA Humanitarian DataViz** plugin
generates brand-compliant SVG charts directly on the artboard.

- **Source:** `~/OCHA DMU Dropbox/<your-name>/Design/Resources/ocha_dataviz_tool/`
- **Chart types** (14 in the picker tile grid): hbar, vbar, stacked-bar, stacked-col, cluster, line, pie, donut, bubble, icon, table, sankey, keyfigures, timeline. (Map exists internally but is hidden on `main`; see `project_mapmaker.md`.)
- **Styles**: `ocha` / `hnrp` / `flash` / `gho` — each with full palette, icon palette, and humanitarian-accent logic.
- **AI-assisted import** (shipped v2026.0.16): the plugin can ingest JSON produced by an AI assistant (Copilot / ChatGPT / Claude / Gemini). All 14 picker chart types are supported. Single chart or batch (up to 20 charts in one click). Two batch layout modes: **One per artboard** (multi-page deliverable) or **Grid** (one-pager, multiple charts packed onto each artboard with auto-cell-size — ~9 on A4 portrait, ~4 on A5, ~16 on A0). Tables, timelines and sankey diagrams span 2 cells in grid mode. Per-chart selection in the batch review modal. Pause-on-error with skip/stop UX and one-click "Copy fix prompt" for AI-fixable errors. State and architecture documented in `project_ai_import.md`.
- **Release workflow** is a separate skill: `ocha-dataviz-release`.
- **Project rule** (from the plugin's own `CLAUDE.md`): cross-tool changes to shared concerns (brand colours, style IDs, chart keys, number formatting, chart data shapes) need explicit confirmation before being applied to the sibling **online dashboard editor** in `ocha_dataviz_online/`.

### 7.1 Maintainer rule when adding a new chart type to the plugin

**A new chart type is not finished until the AI feature accepts it.**
Adding a renderer (`ChartRegistry.register(id, name, renderFn)`) is
only step 1 of 4. The full checklist:

1. **Renderer + picker tile** — register with `ChartRegistry`, add the
   tile to the chart-type grid in `client/index.html` + styles.
2. **AI import — `client/ai-import.js`**:
   - Add the type id to `SUPPORTED_TYPES`.
   - If multi-column: add to `MULTI_VALUE_TYPES`.
     If custom data shape (not generic label+value): add to
     `SPECIAL_SCHEMA_TYPES` and write branches in
     `validateSpecialSchema()` and `expand()`.
   - Add common name variants to `ALIAS_TABLE` (e.g.
     `"alluvial" → sankey`, `"doughnut" → donut`).
3. **AI primer — `client/ai-prompt-template.js`**:
   - Add the type id to the `chartType` enum.
   - Add a one-paragraph selection rule (when to pick this type).
   - Add a tie-breaker bullet.
   - Add a worked data-shape example with `headers` + `rows`.
4. **Test** — there's a headless validate/expand test scaffold at
   `/tmp/test_ai_import_phase_b.js` (regeneratable). Add a fixture
   for the new type and confirm green before declaring "done".

A maintainer-warning comment block lives at the top of
`client/chart-registry.js` (just above `registry.register`) and
mirrors this checklist so the requirement is visible at the canonical
add-a-chart-type site.

### 7.2 Maintainer rule when changing look-and-feel or adding a chart setting (NOT a new chart type)

The rendering pipeline is shared — manual UI and AI import both flow
through `DataStore` → `ChartBuilder` → SVG. So **most visual changes
propagate to AI-imported charts automatically**. The exception is
when a new tweakable knob is added.

- **Pure visual / layout / styling / default change** (margins,
  palette, fonts, default behaviour, breakpoint presets) →
  **automatic**. No AI work needed. Both manual and AI-imported
  charts pick up the change on next reload.
- **New optional config field the user can tweak** (new checkbox,
  slider, dropdown) → after wiring it through `DataStore.toConfig`
  / `loadFromConfig`, also add the field name to the **`passthrough`**
  list in `ai-import.js`'s `expand()`. One line. Without it, even
  if the AI sends the field, the plugin silently drops it. *Optional:*
  also mention the field in `ai-prompt-template.js` if you want the
  AI to actively choose values (otherwise defaults apply, which is
  fine for many settings).
- **Renaming or removing an existing field** → update `DataStore`
  (round-trip), the `passthrough` list, AND any reference in the AI
  primer. Re-run the headless tests in
  `/tmp/test_ai_import_phase_b.js` (regeneratable from
  `project_ai_import.md`).

Maintainer-warning comments live next to `store.loadFromConfig` in
`client/data-store.js` (canonical add-a-setting site) and next to
the `passthrough` list in `ai-import.js` so the rule is visible
from both ends.

---

## 8. Do / Don't cheat sheet

**DO**
- Round numbers, use k/M/B.
- Direct-label over legends whenever possible.
- Zero baseline on every bar chart.
- Give every chart a title with location + time + units.
- Include data source and "as of" date.
- Use the 12-column grid, 1cm minimum margins.
- Pick the style family (OCHA/HNRP/Flash/GHO) before picking colours.
- Use small multiples instead of cramming 5+ lines into one chart.
- Sort data by value (bars, pie slices, matrix axes) unless a categorical order is required.
- Use white space generously.

**DON'T**
- 3D charts. Drop shadows. Drop shadows on 3D. Ever.
- Pie with >5 slices, unsorted, or multi-pie comparisons.
- Clipped Y-axis on a bar chart.
- Rotated X-axis labels (switch to horizontal bars).
- More than 4 lines on one chart.
- Justified body text (use left-align).
- Arial Narrow, Avenir, Minion Pro, or Crimson Text.
- Random placement — every element must align, group, or separate deliberately.
- Overfill the page — leave breathing room.
- Invent new accent colours beyond the defined palette.

---

## 9. Decision aids

- **What chart should I use?** datavizproject.com · ferdio.com/notebook
- **OCHA brand / icon / template assets**: https://brand.unocha.org
- **Humanitarian icons v2**: brand.unocha.org → icons section
- **Design system (for web products)**: use the `ocha-visual-identity` skill

---

## Contacts

- **Team:** OCHA Brand and Design Unit (BDU) — **ochavisual@un.org**
- **Focal point:** Javier Cueto — **cuetoj@un.org**
