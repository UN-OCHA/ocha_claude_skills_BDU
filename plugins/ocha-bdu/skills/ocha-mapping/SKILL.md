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
  "choropleth", "bubble map". For general brand colours / logo rules use
  `ocha-visual-identity`. For charts/infographics (non-map) use
  `ocha-dataviz`.
---

# OCHA Mapping

Single source of truth for all style values: **`references/ocha_map_styles_data.js`**
(mirrored from `~/OCHA DMU Dropbox/<your-name>/Maps/map_style_guidance/`).

Baseline is **A4 (794 × 1123 px at 96 dpi)**. All stroke weights and point sizes scale
from A4 — see §16.

---

## 1. Is a map even the right answer?

Ask before building. If geography isn't adding meaning, a chart, table or a sentence
communicates better. Never use a map as decoration.

## 2. Three foundations

**Data** — verified, current. Fix topology (gaps/overlaps between admin polygons) before
publishing. **Story** — the map must carry a message. **Design** — the conventions below.

Decide audience and medium first: expert vs. novice; print vs. web vs. slide; page size;
colour vs. B&W.

## 3. Output type — full layout or map only

Establish which is wanted before building:

- **Full layout** — map plus title, logo, legend, disclaimer, source, narrative (§6, §8).
- **Map only** — just the mapped geography, no surrounding furniture. For dropping into a
  report, slide, dashboard or someone else's layout.

Default to **map only** when the map goes inside something else, **full layout** when it's
a standalone product. If ambiguous, ask.

## 4. The map style spec

All values at the A4 baseline.

### Boundaries — polyline features only, never polygon fills

| Element | Hex | CMYK | Stroke (pt, A4) | Dash | Cap | Notes |
|---|---|---|---|---|---|---|
| International boundary | `#8A8C8E` | 0, 0, 0, 55 | 1.3 | solid | butt | — |
| Disputed boundary | `#77787B` | 0, 0, 0, 55 | 1.0 | `[0, 2]` dots | round | **Check §7 before drawing** |
| 1st admin level | `#C7C8CA` | 0, 0, 0, 23 | 0.8 | `[2.3, 2.3]` | butt | — |
| Coastline / water edge | `#64BEEB` | 55, 8, 0, 0 | 0.5 | solid | butt | — |
| Water feature (river) | `#64BEEB` | 55, 8, 0, 0 | 0.5 | solid | butt | — |

Polygon fills with borders double the stroke at shared edges — always use the `polbndl`
(line) layers, not the outline of `polbnda` (area) layers.

Weight hierarchy: International > Admin 1 > Admin 2 > Admin 3.

> ⚠️ Unresolved: the palette below lists international boundaries as `#737373` while the
> table above says `#8A8C8E`. Both values are in `ocha_map_styles_data.js`. Awaiting
> cartographer sign-off — flag it to the user if it matters to the output.

### Area fills

| Element | Hex | CMYK |
|---|---|---|
| Neighbouring country / land mass | `#E6E6E6` | 0, 0, 0, 10 |
| Featured country | `#FFFFFF` | 0, 0, 0, 0 |
| Ocean / sea | `#E1E8F6` | 10, 2, 0, 0 |

### Point symbols

| Element | Symbol | Size (pt, A4) | Fill | Stroke |
|---|---|---|---|---|
| Capital city | Black circle + white star | 8.5 | `#231F20` | — |
| Admin 1 capital | White circle, dark stroke | 6.2 | `#FFFFFF` | `#4D4D4F` @ 1.0pt |
| Town | Solid circle | 4.0 | `#4D4D4F` | — |

Symbol SVGs ship in **`symbols/`** — `Capital.svg`, `Adm1_capital.svg`, `Town.svg`.
That set is incomplete; if a map needs a symbol that isn't there, ask rather than drawing one.

### Labels

| Element | Font | Style | Size (pt, A4) | Colour | Tracking | Case |
|---|---|---|---|---|---|---|
| Featured country | Roboto | Bold | 14 | `#262626` | 300 | UPPER |
| Neighbouring country | Roboto | Regular | 12.5 | `#999999` | 200 | UPPER |
| Admin 1 region | Roboto | Regular | 9.5 | `#666666` | 0 | UPPER |
| Capital | Roboto | Regular | 12.5 | `#999999` | 100 | Title |
| Admin 1 capital | Roboto Condensed | Regular | 9.5 | `#262626` | 0 | Title |
| Town | Roboto Condensed | Regular | 8 | `#4D4D4D` | 0 | Title |
| Ocean | Crimson Pro | Italic | 10 | `#009EDB` | 300 | UPPER |
| Sea / water feature | Crimson Pro | Italic | 8 | `#009EDB` | 100 | Title |
| River | Crimson Pro | Italic | 8 | `#009EDB` | 100 | Title |

Water labels are UN Blue italic. Never blue text on a blue fill of similar value.

### Palette

| Role | Hex | CMYK |
|---|---|---|
| UN Blue — ocean/water labels, rivers | `#009EDB` | 80, 20, 0, 0 |
| Ocean / sea fill | `#E1E8F6` | 10, 2, 0, 0 |
| Coastline stroke | `#64BEEB` | 55, 8, 0, 0 |
| Black 100% — capital symbol | `#000000` | 0, 0, 0, 100 |
| Black 85% — featured country + admin capital labels | `#262626` | 0, 0, 0, 85 |
| Black 70% — town labels and symbols | `#4D4D4D` | 0, 0, 0, 70 |
| Black 60% — admin 1 region labels | `#666666` | 0, 0, 0, 60 |
| Black 55% — international boundaries | `#737373` | 0, 0, 0, 55 |
| Black 40% — neighbouring country + capital labels | `#999999` | 0, 0, 0, 40 |
| Black 23% — admin 1 boundary lines | `#C7C8CA` | 0, 0, 0, 23 |
| Black 10% — neighbour fill / land mass | `#E6E6E6` | 0, 0, 0, 10 |
| White — featured country fill | `#FFFFFF` | 0, 0, 0, 0 |

## 5. Data visualization on maps

- **Proportional circles** → whole numbers (people in need, partners, events, cases).
- **Choropleth** → rates, percentages, densities. Never raw counts.
- **Direct-label** values on bubbles where space allows — often removes the legend.

**Class breaks** — natural increments, e.g.
`<10,000 | 10,000–50,000 | 50,001–150,000 | 150,001–300,000 | >300,000`. Never
machine-generated breaks like `47,382`.

**Bubbles** scale by area (π × r²), not radius. Legend with 2–3 representative sizes.
**Choropleth** uses a sequential ramp (UN Blue ramp — see `ocha-visual-identity`), darker
= higher, capped at 5–7 classes.

## 6. Required map elements (full layout)

| Element | When |
|---|---|
| Title | Always |
| OCHA logo | Always — see `ocha-visual-identity` for clear space |
| Disclaimer | Always. Italic, `#A7A9AC`. |
| Source + "as of" date | Always |
| Locator globe / inset | When the country's global position isn't obvious |
| North arrow | Only if needed. Subdued, never ornate. |
| Scale bar | Only if needed. Natural increments. Subdued. |
| Legend | Only if symbols aren't self-explanatory. Prefer direct labelling. |
| Narrative / summary text | Strongly encouraged |

## 7. Country and place naming

- Country names from **UNTERM** — https://conferences.unite.un.org/unterm
- Spell out acronyms; if space is tight use an asterisk and a footnote.

### Disputed and sensitive territories — always check the guidance

OCHA's rules for representing disputed territories are **deliberately not written into
this skill.** The skill is distributed publicly; that guidance is internal.

Whenever a map involves a disputed or sensitive territory, boundary, or place name:

**1. Look for the guidance PDF locally.** It ships in the DMU Dropbox:

```
~/OCHA DMU Dropbox/<your-name>/Design/Visual_identity/visual_identity_guidance/2017_2018/chapters/pdf/99_representing_territories.pdf
```

The personal-folder segment differs per person — if that exact path misses, search the
DMU Dropbox for `99_representing_territories.pdf`. Read it and follow it.

> ⛔ **`40_maps.pdf` sits in that same folder. Do not use it.** It's from the 2017/18
> visual identity stylebook and is superseded — the colours and fonts in it are wrong.
> The current map styling is §4 of this skill. Take only the territories chapter from
> that folder, nothing else.

**2. If it isn't on their machine, ask them to attach it.** Explain why, and reassure
them about where it goes:

> This map involves a disputed territory, and OCHA has specific rules for how those are
> shown. That guidance is internal, so it's deliberately not built into this skill.
> Could you drop `99_representing_territories.pdf` into the chat? It's in the DMU
> Dropbox under Visual identity → visual identity guidance. I'll use it only for this
> map — it isn't saved into the skill or published anywhere.

**3. Never guess.** If the guidance can't be obtained, say so plainly and stop. A wrong
disputed boundary is a political problem, not a design one — an unfinished map is far
better than a confidently wrong one.

The same applies to politically sensitive country labels: follow the internal
country-label guidance, and ask BDU (ochavisual@un.org) when unclear.

## 8. Layout and composition

Five pillars: alignment, proximity, white space, clear title, correct metadata.

- **Portrait** for publication / tall countries. **Landscape** for presentation / wide ones.
- Start from an OCHA template, not a blank page.
- **Inset maps to one side** — never floating mid-composition.
- **No island effect** — always show neighbouring countries (§10).
- **Clean topology** — no gaps or overlaps between adjacent admin units.
- **Layer order (bottom → top):** ocean fill → neighbour fill → featured fill →
  choropleth/bubbles → water features → admin boundaries (3→2→1) → international boundary
  → coastline → points → labels → disclaimer/logo.

---

## 9. Geodata — where it is and how to read it

**Check §17 first.** A finished location map may already exist for
this country — rebuilding it from geodata will not match the published one.

**`~/OCHA DMU Dropbox/<your-name>/data/Geodatabase/vector/`**

~147 Esri file geodatabases, one per country, ISO3-named (`afg.gdb`, `sdn.gdb`, `yem.gdb`…),
plus regional sets (`afr.gdb`, `asi.gdb`, `eur.gdb`) and the world set `wrl.gdb`.

### GDAL is required — find it, or install it

Everything below needs GDAL's `ogr2ogr`. Resolve it in this order and use the first
one that works:

1. `/opt/homebrew/bin/ogr2ogr` — Homebrew install, newest version
2. `ogr2ogr` on `PATH`
3. `/Applications/QGIS*.app/Contents/MacOS/bin/ogr2ogr` — **QGIS bundles GDAL.** Most
   OCHA mappers already have QGIS, so always check here before installing anything.
   It ships an older GDAL but it reads `.gdb` and writes GeoJSON fine.
4. Windows: `C:\Program Files\QGIS *\bin\ogr2ogr.exe`

**If none of those exist, install it. Do not work around it.** Never fall back to asking
the user to hand-export layers from QGIS or ArcGIS — that is the dead end this skill
exists to remove, and a non-technical colleague will simply stop there.

#### Always ask before installing anything

Never install silently. Say what's missing, what it's for in plain language, how long it
takes, and whether it needs their password — then **wait for a yes**. Something like:

> Making this map needs **GDAL**, the toolkit that reads OCHA's geodatabase files. It's
> not on your machine yet. It takes about 10 minutes to install and won't ask for your
> password. Shall I install it?

If they say no, stop and explain what can't be done without it — don't quietly fall back
to a worse method.

**macOS, Homebrew present** — once they've said yes:

```bash
brew install gdal
```

**macOS, no Homebrew** — this is the one step the user has to run themselves, because
Homebrew's installer prompts for their password. Give them this line, wait for them to
confirm, then run `brew install gdal` yourself:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Windows, no QGIS** — have them install QGIS rather than OSGeo4W alone. It bundles GDAL
and it's software a mapper wants anyway: https://qgis.org/download/

### Reading the data

```bash
# list layers in a country geodatabase
/opt/homebrew/bin/ogrinfo "$GDB/sdn.gdb"

# extract one layer to GeoJSON
/opt/homebrew/bin/ogr2ogr -f GeoJSON out.geojson "$GDB/sdn.gdb" sdn_polbndl_adm1_1m_ocha

# extract and reproject in one step (see §11 for the .prj)
/opt/homebrew/bin/ogr2ogr -f GeoJSON -t_srs "$PRJ/sdn/sdn_ocha.prj" \
  out.geojson "$GDB/sdn.gdb" sdn_polbnda_adm1_1m_ocha
```

Tell the user to make only the country they need available offline in Dropbox — the whole
folder is far too heavy to sync.

### Layer naming convention

| Fragment | Meaning |
|---|---|
| `polbnda` | Political boundary, **area** (polygon) — use for fills |
| `polbndl` | Political boundary, **line** (polyline) — **use for boundary strokes** |
| `int` | International |
| `adm1` / `adm2` / `adm3` | Admin level |
| `pplp` / `capp` | Populated places / capitals (point) |
| `watcrsl` / `watcrsa` | Watercourse line / area |
| `lakeresa` | Lake and reservoir (area) |
| `coastl` | Coastline (line) |
| `rdsl` / `rlwl` | Roads / railways (line) |
| `airdrmp` / `bdgep` / `prtp` | Aerodromes / bridges / ports (point) |
| `50k` `250k` `1m` `15m` `25m` | Source scale |
| `sim` / `simple` / `xsimple` | Generalised geometry |
| trailing `ocha` `uncs` `gaul` `fao` `wfp` `esri` `ne` | Data source |

`uncs` = **UN Cartographic Section** — the authoritative boundary source. Prefer it for
international boundaries.

Example: `sdn_polbndl_adm3_250k_sim` = Sudan, admin-3 boundary lines, 1:250k, simplified.

### Country geodatabases are not uniform

Contents vary — always run `ogrinfo` first, never assume a layer name. Observed variation:

- Sudan has both `250k` and `1m_ocha` families, **plus `_2024` versions** — prefer the
  most recent (`sdn_polbnda_adm1_1m_ocha_2024`).
- Yemen has `_govt` and `_govt_Union` layers — the `_Union` is dissolved and matches
  world boundaries better.
- Afghanistan and Chad have neither of those patterns.

## 10. Border matching — never map a country alone

**Every OCHA map shows its neighbours.** A country floating on white is wrong (the "island
effect"). That means every map combines **country data + world data**, and the two must
line up along the shared border.

**The matching rule: use the same scale family for both.** Country data at `1m` pairs with
world layers at `1m`. Mixing scales (a `1m` country against a `15m` world) produces visible
slivers, gaps and offset borders along the shared edge.

### World layers — `wrl.gdb`, all from `uncs`

| Layer | Use |
|---|---|
| `wrl_polbnda_int_1m_uncs` | Country polygons → neighbouring-country fills |
| `wrl_polbndl_int_1m_uncs` | International boundary lines |
| `wrl_coastl_1m_uncs` | Coastlines |

Also available at `15m` (`wrl_polbnda_int_15m_uncs` etc.) for small-scale regional and world
maps, and in `simple` / `xsimple` generalised versions for very small output.

**Pick one family and use it for all three world layers.** Never mix `1m` boundaries with
`15m` coastlines.

### Standard country-map recipe

1. `ogrinfo` the country `.gdb` — see what's actually there.
2. Featured country admin polygons + boundary lines from the country `.gdb`, newest version.
3. Neighbour fills, international boundaries and coastline from `wrl.gdb` at the **matching
   scale family**.
4. Reproject everything to the country's `.prj` (§11).
5. Style per §4, order layers per §8.

## 11. Projections

**`~/OCHA DMU Dropbox/<your-name>/Maps/location_maps_2024/`**

242 `.prj` files, plain text, read directly:

- **Per country:** `{iso3}/{iso3}_ocha.prj` — e.g. `sdn/sdn_ocha.prj`, `yem/yem_ocha.prj`
- **Regional globes:** `0_GLOBES/` — Africa, Americas, Asia, Europe, Middle East, North
  America, Oceania, Pacific, plus proj4 text variants
- **World:** `World Robinson 11 deg.prj` in the Geodatabase `vector/` folder

Use the country's own `.prj` for a single-country map. These are *not* duplicated in the
Geodatabase folder.

The same folder also holds the **finished location maps and the globe artwork** — §17.

## 12. Export formats

| Format | Use | How |
|---|---|---|
| **SVG** | Primary output. Editable in Illustrator. | Generated directly |
| **PDF** | Print. Stays vector. | `cairosvg.svg2pdf()` |
| **PNG** | Slides, web, previews. Any DPI. | `cairosvg.svg2png(dpi=…)` |

| **GeoJSON** | Editable data for QGIS / ArcGIS | Generated directly / `ogr2ogr` |
| **Shapefile / GeoPackage** | Traditional GIS handoff | `ogr2ogr -f "ESRI Shapefile"` / `-f GPKG` |
| **QGIS style (`.qml`)** | Styling to accompany the data | XML, written directly |
| **ArcGIS style (`.lyrx`)** | Styling to accompany the data | JSON, written directly |

Illustrator needs no special format — it opens SVG as live editable vector art.

PDF and PNG conversion needs `cairosvg`. If it's missing, offer to install it
(`pip3 install cairosvg`) rather than telling the user to convert the SVG themselves —
asking first, as in §9.

**"Editable in ESRI/QGIS" means data + styling, not a picture.** Deliver two files:
geometry as GeoJSON (or shapefile/GeoPackage) and styling as `.qml` (QGIS) or `.lyrx`
(ArcGIS Pro), generated to match §4 exactly.

## 13. Tooling

- **Illustrator** — the OCHA DataViz plugin's **Map Maker** builds choropleth and bubble
  maps directly on the artboard. See `ocha-dataviz-release` for plugin architecture.
- **Datawrapper** — preferred for web-embedded maps on unocha.org (Drupal).
- **Ready-made maps** — `Maps/Illustrator_ready_to_use_maps/`, `Maps/location_maps_2024/`.

## 14. Critique checklist

1. Title clear?
2. OCHA logo present, correct clear space?
3. Disclaimer present?
4. Locator globe / inset needed?
5. Source + "as of" date?
6. Acronyms spelled out?
7. Country names from UNTERM?
7b. Any disputed territory checked against the internal guidance (§7)?
8. Boundaries from `polbndl` line layers, not polygon outlines?
9. Boundary hierarchy correct (international heaviest)?
10. Topology clean, borders matching between country and world data?
11. Right data type — bubbles for counts, choropleth for rates?
12. Class breaks natural?
13. Could values be direct-labelled instead of a legend?
14. North arrow / scale bar subdued, and only if needed?
15. Narrative text present?
16. Neighbouring countries shown (no island effect)?
17. Label hierarchy clear — capital vs admin capital vs town?
18. No blue text on blue water?
19. No busy patterns, 3D, heavy ornaments?
20. Export crisp, vector throughout?

## 15. Common pitfalls

- Polygon outlines instead of `polbndl` lines → doubled borders.
- **Mismatched scale families** between country and world data → slivers along the border.
- Counts shown as choropleth → use proportional circles.
- Assuming a layer name without running `ogrinfo` first.
- Using an outdated layer version when a `_2024` one exists.
- Blue labels on blue water fills.
- Busy hatching; too much detail for the map scale.
- Missing locator, logo, disclaimer or source.
- Machine-generated class breaks.
- Ornate north arrows and scale bars.
- Island effect — country alone on white.
- Using a map where a chart would communicate better.

## 16. Scaling to other page sizes

| Size | Dimensions | Width (px) | Factor vs A4 |
|---|---|---|---|
| A4 | 210 × 297 mm | 794 | 1.00 |
| A5 | 148 × 210 mm | 559 | 0.70 |
| A3 | 297 × 420 mm | 1123 | 1.41 |
| Instagram | 1080 × 1080 | 1080 | 1.36 |
| Twitter/X | 1200 × 628 | 1200 | 1.51 |
| HD 16:9 | 1920 × 1080 | 1920 | 2.42 |
| Web | 800 × 600 | 800 | 1.01 |

Multiply strokes (round to 0.1pt) and point/font sizes (round to 0.5pt) by the factor.
Dash patterns scale too. For scripted generation use
`references/ocha_map_styles_data.js` as the source of truth.

## 17. Ready-made location maps and globes — check here before building one

**`~/OCHA DMU Dropbox/<your-name>/Maps/location_maps_2024/`**

This folder is not only the projection library (§11) — it is OCHA’s finished location map
set. **123 country folders**, each holding a built map. Opening one is almost always the
right move: rebuilding the same map from the geodatabase is wasted work and the result
will not match the published version.

| What | Where |
|---|---|
| Country location map | `{iso3}/{iso3}_ocha.{ai,svg,pdf,png,mxd}` |
| Locator globes | `0_GLOBES/globes.ai` — the artwork; the 8 regional `.prj` files sit beside it |
| Multi-country regions | `0_regions/` — Caribbean, Central America, Horn of Africa, Sahel |
| Projections | `{iso3}/{iso3}_ocha.prj`, plus `0_prj_files/` and `0_wkt_files/` (§11) |

### Three things that will trip you up

- **The casing is inconsistent.** Both `sdn_ocha.svg` and `caf_OCHA.svg` exist. Always
  match case-insensitively (`find … -iname`, or `ls | grep -i`) — an exact lowercase path
  silently misses roughly a dozen countries and looks like "no map exists".
- **Coverage is not uniform across formats.** No SVG for `ecu`, `gnq`, `ita`, `kir`,
  `mdv`, `mhl`, `niu`, `tuv`; no Illustrator file for `ita`. Check what is actually in the
  folder before promising a format.
- **Ignore the `_old` variants** (e.g. `mdv/mdv_ocha_old.ai`) and the `0_SCRAP/` folder.

### Which format for which job

- **SVG** — web, artifacts, anything that must scale or be restyled in code.
- **AI** — the editable master. Restyle here when the map needs real changes (§4).
- **PDF / PNG** — drop straight into a report or slide when nothing needs changing.
- **MXD** — the ArcGIS project, for re-deriving the map from live data.

Build from the geodatabase (§9) only when no country map exists, when the geography needed
isn’t a whole country, or when the data being mapped changes the base map itself.

---

## Contacts

- **Team:** OCHA Brand and Design Unit (BDU) — **ochavisual@un.org**
- **Focal point:** Javier Cueto — **cuetoj@un.org**
