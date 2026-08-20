---
name: ocha-mapping
description: >
  Apply OCHA's cartographic standards — map style, boundary conventions,
  symbology, typography, and critique rules — when producing humanitarian
  maps. Use this skill whenever the user asks to "make a map", "design a
  map", "style a map for OCHA", "critique this map", or asks about OCHA map
  symbology, boundary colours/weights, capital/town symbols, choropleth vs
  bubble maps, admin levels, disputed boundaries, locator globes, or map
  disclaimers. Trigger on phrases like "OCHA map", "humanitarian map",
  "reference map", "location map", "map style", "Illustrator map",
  "ArcGIS Pro style", ".stylx". For general brand colours / logo rules use
  `ocha-visual-identity`. For charts/infographics (non-map) use
  `ocha-dataviz`.
---

# OCHA Mapping

Authoritative style reference: **`~/OCHA DMU Dropbox/<your-name>/Maps/map_style_guidance/`**

That folder contains:
- `ocha_map_style_guidance.html` — live visual reference (print/PDF + .stylx export for ArcGIS Pro)
- `ocha_map_styles_data.js` — the single source of truth for all values (boundaries, fills, points, labels, colours). A copy ships with this skill at `references/ocha_map_styles_data.js`.
- `ocha_map_style_editor.html` — editor UI that writes back to `ocha_map_styles_data.js`

Baseline is **A4 (794 × 1123 px at 96 dpi)**. All stroke weights and point
sizes scale from A4. When producing maps at other sizes (A3, A5, Instagram
1080², Twitter 1200×628, HD 16:9, Web 800×600), sizes scale proportionally
(stroke rounded to nearest 0.1pt, point sizes to nearest 0.5pt).

---

## 1. Is a map even the right answer?

Ask this before building anything. If geography isn't adding meaning, a
chart, table, or paragraph of text will communicate better. Don't use a map
as decoration.

---

## 2. Three foundations

Same as all OCHA visual work: **data + story + design**.
- **Data** — verified, current, reliable. Fix topology (gaps/overlaps between admin polygons) before publishing.
- **Story** — the map must deliver a message. Coordinate with public information / reporting officers.
- **Design** — convert data + text into a visually stimulating product using the conventions below.

Decide audience and medium FIRST: expert vs. novice; web vs. print; A4 / A3 / A2 / social / slide; colour vs. B&W print.

---

## 3. OCHA Map Style — the authoritative spec

All values below are for the **A4 baseline**. Source: `references/ocha_map_styles_data.js`.

### Boundaries (polyline features only — NEVER polygon fills)

| Element | Hex | CMYK | Stroke (pt, A4) | Dash | Cap | Notes |
|---|---|---|---|---|---|---|
| International boundary | `#8A8C8E` | 0, 0, 0, 55 | **1.3** | solid | butt | — |
| Disputed boundary | `#77787B` | 0, 0, 0, 55 | **1.0** | `[0, 2]` (dots) | round | "Check with relevant authority" |
| 1st admin level boundary | `#C7C8CA` | 0, 0, 0, 23 | **0.8** | `[2.3, 2.3]` | butt | — |
| Coastline / water edge | `#64BEEB` | 55, 8, 0, 0 | **0.5** | solid | butt | — |
| Water feature (river) | `#64BEEB` | 55, 8, 0, 0 | **0.5** | solid | butt | — |

**Why polyline-only?** Polygon fills with borders produce doubled/thickened
strokes at shared edges. Polylines keep boundary weights consistent.

**Hierarchy of line weights**: International > Admin 1 > Admin 2 > Admin 3.
International is always the heaviest and darkest.

### Area fills (polygons)

| Element | Hex | CMYK | Notes |
|---|---|---|---|
| Neighbouring country / land mass | `#E6E6E6` | 0, 0, 0, 10 | — |
| Featured country | `#FFFFFF` | 0, 0, 0, 0 | White or choropleth for thematic overlays |
| Ocean / sea water | `#E1E8F6` | 10, 2, 0, 0 | — |

### Point symbols (A4 baseline)

| Element | Symbol | Size (pt) | Fill | Stroke | Notes |
|---|---|---|---|---|---|
| Capital city | Black circle + white star | **8.5** | `#231F20` | — | Use the `Capital.svg` symbol |
| Administrative 1 capital | White circle, dark stroke | **6.2** | `#FFFFFF` | `#4D4D4F` @ 1.0pt | Hollow circle |
| Town | Solid dark circle | **4.0** | `#4D4D4F` | — | — |

### Labels & typography

| Element | Font | Style | Size (pt, A4) | Colour | Tracking | Case |
|---|---|---|---|---|---|---|
| Featured country | Roboto | Bold | **14** | `#262626` | 300 | UPPERCASE |
| Neighbouring country | Roboto | Regular | **12.5** | `#999999` | 200 | UPPERCASE |
| Admin 1 region | Roboto | Regular | **9.5** | `#666666` | 0 | UPPERCASE |
| Capital label | Roboto | Regular | **12.5** | `#999999` | 100 | Title case |
| Admin 1 capital label | Roboto Condensed | Regular | **9.5** | `#262626` | 0 | Title case |
| Town label | Roboto Condensed | Regular | **8** | `#4D4D4D` | 0 | Title case |
| Ocean label | Crimson Pro | Italic | **10** | `#009EDB` | 300 | UPPERCASE |
| Sea / water feature | Crimson Pro | Italic | **8** | `#009EDB` | 100 | Title case |
| River label | Crimson Pro | Italic | **8** | `#009EDB` | 100 | Title case |

**Water-label rule**: water labels use UN Blue italic. Never use blue text on blue water fill of a similar value — check contrast. The ocean/sea label colour `#009EDB` on ocean fill `#E1E8F6` works because the fill is very pale.

### Full map colour palette (labels + fills + strokes)

| Role | Hex | CMYK |
|---|---|---|
| UN Blue (ocean labels, water features, rivers) | `#009EDB` | 80, 20, 0, 0 |
| Ocean / sea fill | `#E1E8F6` | 10, 2, 0, 0 |
| Coastline stroke | `#64BEEB` | 55, 8, 0, 0 |
| Black 100% (capital symbol) | `#000000` | 0, 0, 0, 100 |
| Black 85% (featured country label, admin capital label) | `#262626` | 0, 0, 0, 85 |
| Black 70% (town labels, town symbols) | `#4D4D4D` | 0, 0, 0, 70 |
| Black 60% (admin 1 region labels) | `#666666` | 0, 0, 0, 60 |
| Black 55% (international boundaries) | `#737373` | 0, 0, 0, 55 |
| Black 40% (neighbouring country / capital labels) | `#999999` | 0, 0, 0, 40 |
| Black 23% (admin 1 boundary lines) | `#C7C8CA` | 0, 0, 0, 23 |
| Black 10% (neighbour fill / land mass) | `#E6E6E6` | 0, 0, 0, 10 |
| White (featured country fill) | `#FFFFFF` | 0, 0, 0, 0 |

---

## 4. Data visualization on maps

### When to use what
- **Proportional circles (bubble maps)** → **whole numbers** (people in need, partners, events, cases).
- **Choropleth (filled polygons)** → **rates, percentages, densities**. Never for raw counts.
- **Direct-label values on bubbles** where space allows. Often removes the need for a legend.

### Class breaks
Use **natural, user-friendly increments**. Examples:
- `<10,000 | 10,000–50,000 | 50,001–150,000 | 150,001–300,000 | >300,000`

Avoid computer-generated breaks (e.g. `47,382 | 94,221 …`). Round to
human-readable numbers. Use the OCHA colour ramps (see `ocha-visual-identity`
skill or `brand.unocha.org`).

### Bubble (proportional circle) rules
- Scale by **area** (π × r²), not radius.
- Provide a tiny legend showing 2–3 representative sizes with their values.

### Choropleth rules
- Use a **sequential ramp** (e.g. UN Blue ramp). Darker = higher.
- Cap at **5–7 classes**. More classes are hard to distinguish.

---

## 5. Required map elements

| Element | When |
|---|---|
| **Title** | Always |
| **OCHA logo** | Always — see `ocha-visual-identity` for placement / clear space |
| **Disclaimer** | Always. Italic, `#A7A9AC` (grey). Required especially where boundaries are shown (disputed/non-recognised). |
| **Data source + "as of" date** | Always |
| **Locator globe / inset** | When the country's global position isn't obvious to the audience. |
| **North arrow** | Only when genuinely needed. Subdued — never ornate. |
| **Scale bar** | Only when genuinely needed. Natural increments. Subdued. |
| **Legend** | Only if symbols / fills aren't self-explanatory. Prefer direct labelling. |
| **Narrative / summary text** | Strongly encouraged — a short caption or intro headline on the map. |

---

## 6. Country / place naming

- **Country names**: use the spelling from the **UNTERM database** —
  https://conferences.unite.un.org/unterm
- **Politically sensitive cases**: follow OCHA's internal country-label guidance (ask the BDU if unclear).
- **Spell out acronyms** on the map. If space is tight, use an asterisk `*` and footnote with the full name.
- The "OCHA" word in the logo is **never translated** — only the spelled-out descriptor.

---

## 7. Layout & composition

Five pillars: **alignment, proximity, white space, clear title, correct metadata**.
- **Portrait** = publication / when the country shape is tall.
- **Landscape** = presentation / when the country shape is wide.
- Use an OCHA map template rather than starting from scratch.
- **Inset maps** to one side — don't float them mid-composition.
- **Island effect**: never show a featured country floating on a white void. Always include neighbouring countries (greyed out with `#E6E6E6` fill).
- **Topology must be clean**: no gaps, no overlapping polygons between adjacent admin units. Fix the GIS data before exporting.
- **Layer order** (bottom → top): ocean fill → neighbour fill → featured fill → choropleth / bubbles → water features → admin boundaries (3 → 2 → 1) → international boundary → coastline → points → labels → disclaimer/logo.

---

## 8. Critique checklist — run through these before shipping

1. Is the title clear?
2. Is the OCHA logo present and at correct clear space?
3. Is the disclaimer present?
4. Is a locator globe / inset needed for global context?
5. Is source + "as of" date present?
6. Are acronyms spelled out (or footnoted)?
7. Are country names from UNTERM?
8. Are boundaries polylines (not polygon fills)?
9. Is the boundary hierarchy correct (international heaviest, admin levels lighter)?
10. Is topology clean (no gaps / overlapping borders)?
11. Is the right data-type used — bubbles for counts, choropleth for rates?
12. Are class breaks natural (not computer-generated)?
13. Can values be direct-labelled instead of using a legend?
14. Are north arrow / scale bar subdued and only present if needed?
15. Is narrative / summary text present?
16. Is there neighbouring-country context (no "island" effect)?
17. Is label hierarchy clear (capital > admin capital > town distinct)?
18. No blue text on blue water?
19. No busy patterns, 3D effects, or heavy ornaments?
20. Is the export crisp (no blurry raster lines)?

---

## 9. Common pitfalls

- Polygon boundaries instead of polylines → doubled borders.
- Whole-number data shown as choropleth → use proportional circles.
- Blue labels on blue water fills.
- Busy hatching / stripe patterns. Use subtle fills or tints.
- Info overload for the map scale. Split into two maps or small multiples.
- Missing locator globe, logo, disclaimer, or source.
- Unspelled acronyms.
- Machine-generated class breaks (e.g. `47,382`).
- Ornate north arrows and scale bars dominating the composition.
- Blurry exports — export at proper resolution; use vector everywhere.
- Island effect (country floating in a white void).
- Missing summary/narrative text.
- Using a map when a chart would communicate better.

---

## 10. Tooling

### Illustrator
- Use the **OCHA Humanitarian DataViz** plugin's **Map Maker** for choropleth + bubble maps directly in Illustrator. Geodata is local (mapmaker-cache in the plugin). See `ocha-dataviz-release` skill for plugin architecture.
- Catalog of ready-to-use reference maps at `~/OCHA DMU Dropbox/<your-name>/Maps/Illustrator_ready_to_use_maps/` and location maps at `~/OCHA DMU Dropbox/<your-name>/Maps/location_maps_2024/`.

### ArcGIS Pro
- Download a scaled **.stylx** file from `ocha_map_style_guidance.html` (button in the toolbar). Select the page size first — the .stylx is pre-scaled for that size.
- The .stylx ships all OCHA boundaries, fills, points, and label styles.

### Datawrapper
- For web-embedded maps on unocha.org (Drupal), prefer Datawrapper — per the user's CLAUDE.md preference.

### Web maps
- Reference base styles in `~/OCHA DMU Dropbox/<your-name>/Maps/web_maps/`.

---

## 11. Scaling to other sizes

The style spec is defined at A4. For other page sizes:

| Size | Label | Width (px) | Scale factor vs A4 |
|---|---|---|---|
| A4 | A4 (210 × 297 mm) | 794 | 1.00 |
| A5 | A5 (148 × 210 mm) | 559 | 0.70 |
| A3 | A3 (297 × 420 mm) | 1123 | 1.41 |
| IG | Instagram (1080²) | 1080 | 1.36 |
| TW | Twitter/X (1200 × 628) | 1200 | 1.51 |
| HD | HD 16:9 (1920 × 1080) | 1920 | 2.42 |
| WEB | Web (800 × 600) | 800 | 1.01 |

Multiply all stroke widths (round to 0.1pt) and point sizes (round to 0.5pt)
by the scale factor. Font sizes scale the same way. Dash patterns scale too.

For scripted generation, use `ocha_map_styles_data.js` (ships at
`references/ocha_map_styles_data.js`) as the single source of truth.

---

## Contacts

- **Team:** OCHA Brand and Design Unit (BDU) — **ochavisual@un.org**
- **Focal point:** Javier Cueto — **cuetoj@un.org**
