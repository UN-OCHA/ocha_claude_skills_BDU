---
name: humanitarian-icons
description: >
  Find, reference, and use OCHA Humanitarian Icons — the official set of 389 single-colour
  SVG icons (OCHA blue #009edb) maintained by the Brand and Design Unit. Use this skill
  whenever the user asks for "an OCHA icon", "humanitarian icon", "an icon for X", the SVG
  or CDN URL of a specific icon, which icons exist for a topic (shelter, health, water,
  disasters, people/HPC, clusters, damage states), which icons are approved for wordmarks,
  or wants to build/design something that should use OCHA icons. Also trigger on "icon
  library", "icon inventory", "humanitarian iconography", "OCHA SVG", "cluster icon", or
  when matching a concept/keyword to an icon (e.g. "I need a 'communication' or 'noise'
  icon" → Advocacy). For general OCHA brand colours/logo use `ocha-visual-identity`; for
  charts use `ocha-dataviz`; for maps use `ocha-mapping`.
---

# OCHA Humanitarian Icons

The official OCHA Humanitarian Icons: **389 single-colour SVG icons** in OCHA blue
(`#009edb`), maintained by the Brand and Design Unit (BDU). Licensed **CC BY 4.0**.

## Where everything lives

| Thing | Location |
|---|---|
| **GitHub repo** | https://github.com/UN-OCHA/humanitarian-icons-2026-BDU |
| **Local working copy** | `~/OCHA DMU Dropbox/<your-name>/Design/Humanitarian_Icons/v2/Humanitarian_Icons_2026/humanitarian-icons-2026` |
| **Live tools (GitHub Pages)** | https://un-ocha.github.io/humanitarian-icons-2026-BDU/ |
| **Frontify library** | https://brand.unocha.org/brands/168519/icon-libraries/251023 |
| **Font Awesome (2021 subset)** | https://fontawesome.com/icons/categories/humanitarian |

## How to give someone an icon

Icons are `svg/{Icon-name}.svg`. Filenames are **Hyphen-Case with a leading capital**
(`Water-source.svg`, `Health-facility.svg`). The display name in metadata is sentence
case (`Water source`).

**CDN (jsDelivr) — best for web embeds:**
```
https://cdn.jsdelivr.net/gh/UN-OCHA/humanitarian-icons-2026-BDU@main/svg/{Icon-name}.svg
```
**GitHub Pages:**
```
https://un-ocha.github.io/humanitarian-icons-2026-BDU/svg/{Icon-name}.svg
```
**Raw GitHub:**
```
https://raw.githubusercontent.com/UN-OCHA/humanitarian-icons-2026-BDU/main/svg/{Icon-name}.svg
```

All SVGs are monochrome — recolour via CSS `fill` or `filter`, don't add gradients.

## How to find the right icon

1. **Exact/known name** → build the CDN URL directly from the Hyphen-Case filename.
2. **By topic or family** → read `reference/inventory.md` (full list grouped by the 19
   families: Activities strategy, Camp, Clusters, Damage, Disasters/hazards/crises, Food
   and non-food items, General infrastructure, Health, Lockdown, Logistics, Other sectors,
   People, Physical barriers, Product type, Security and incident, Socioeconomic and
   development, Telecommunications and technology, UX UI, Water sanitation and hygiene).
3. **By concept/keyword** (icon depicts more than its name — e.g. "noise" or
   "communication" → Advocacy, which is a bullhorn) → read `reference/tags.json` or the
   `tags` field in `metadata.json`, which map each icon to 3–4 visual concepts.
4. **If the local copy may be stale**, fetch the latest `metadata.json` from the repo raw
   URL before answering — it is the single source of truth.

## Naming patterns to know

- **Damage-state variants:** many infrastructure icons have `-affected`, `-destroyed`,
  `-not-affected` (e.g. `Bridge-affected`, `School-destroyed`, `House-not-affected`).
- **Alternate versions:** some concepts have a `-2` variant (`People-targeted-2`).
- **HPC people set:** `People-in-need`, `People-targeted`, `People-reached`,
  `People-covered`, `People-affected` — the Humanitarian Programme Cycle categories.
- **Clusters** are the 11 IASC clusters (Health, Shelter, WASH, Protection, etc.).

## Wordmark eligibility

98 of the 389 icons are **approved for wordmarks** (`"wordmark": true` in metadata.json,
flagged with ✎ in the inventory). Only these should be offered when someone is building a
wordmark. There is a dedicated wordmark generator at
`word-mark-generator/` (live at the GitHub Pages URL above) with a BDU approval workflow.

## metadata.json — the single source of truth

Every icon in `metadata.json` carries: `name`, `family`, `tags` (concept keywords),
`wordmark` (bool), `wordmark_valign`, `font_codepoint` (for the icon font), and
`date_added` (authoritative creation date — use this, not file timestamps, for "which
icons are new since X").

## Repo conventions (as of mid-2026)

- **`icon-manager/`** — browser tool for managing/curating icons (formerly `curator/`).
- **Publishing is automated**: pushing to `main` triggers GitHub Actions that sync icons
  to Frontify and rebuild the `output/` exports (Excel, PPTX, font, grid). Don't run the
  generator scripts manually unless CI is unavailable — just commit SVG + metadata changes.
- **Wordmark generator** lives in `word-mark-generator/` with a Google-Sheets approval
  backend; see its `APPROVAL_SETUP.md`.

## Reference files (load on demand)

- `reference/inventory.md` — all 389 icons by family, with filename, display name,
  wordmark flag, and concept tags. Read this to answer "what icons exist for X".
- `reference/tags.json` — compact concept-tag map for keyword/semantic matching.

These reference files are a snapshot. If precision matters or the set may have changed,
fetch `metadata.json` fresh from
`https://raw.githubusercontent.com/UN-OCHA/humanitarian-icons-2026-BDU/main/metadata.json`.
