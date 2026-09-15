---
name: humanitarian-icons
description: >
  Find, reference, and use OCHA Humanitarian Icons — the official set of 389 single-colour
  SVG icons (OCHA blue #009edb) maintained by the Brand and Design Unit — and the separate
  set of OCHA country icons (small locator maps, one per country). Use this skill
  whenever the user asks for "an OCHA icon", "humanitarian icon", "an icon for X", the SVG
  or CDN URL of a specific icon, which icons exist for a topic (shelter, health, water,
  disasters, people/HPC, clusters, damage states), which icons are approved for wordmarks,
  or wants to build/design something that should use OCHA icons. Also trigger on "icon
  library", "icon inventory", "humanitarian iconography", "OCHA SVG", "cluster icon", "country icon", "icon for [country]", "locator icon", or
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

91 of the 389 icons are **approved for wordmarks** (`"wordmark": true` in metadata.json,
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

## Country icons — a separate set

BDU also makes **OCHA country icons**: 250 small locator maps, one per country or
territory, plus a few regions and world views. They are **not** part of the 389
humanitarian icons. They look different, live somewhere else and follow different rules.

| | |
|---|---|
| **What they are** | 40 × 40 locator maps in the OCHA map colours: the country in white, neighbours grey, sea pale blue |
| **Current set** | `~/OCHA DMU Dropbox/<your-name>/Design/Humanitarian_Icons/v2/Country_icons/2025/svg_2025/` |
| **Illustrator master** | `…/Country_icons/2025/2025_OCHA_country_icons.ai` |
| **Naming** | `Country_Name_ISO3.svg` — `Haiti_HTI.svg`, `New_Zealand_NZL.svg`. Regions and world views have no code: `1_Caribbean.svg`, `World_1.svg` |
| **Format** | SVG |

The personal-folder part of that path differs per person. If it misses, search the DMU
Dropbox for `svg_2025`. To find a country, match its ISO3 code case-insensitively
(`ls | grep -i '_hti\.svg'`) rather than guessing the exact name.

**Use them to** mark which country a card, chart, dashboard tile or report section is
about, or as a small locator inset.

**Rules**

- **Only the 2025 set.** Never use anything under `Country_icons/archive/` — the 2018 and
  2023 sets are outdated.
- **Use them exactly as they are.** Unlike the humanitarian icons, never recolour them —
  the colours are the map. Don’t redraw, crop, rename or relabel them.
- **Some show disputed or sensitive territories.** Use those exactly as provided, and
  before adding any label or caption follow the territories guidance in `ocha-mapping` §7.
- **They are internal to BDU.** They live only in the DMU Dropbox; there is deliberately
  no public link or CDN, so never publish one. If the folder isn’t on the user’s machine,
  tell them to ask BDU for the icon (ochavisual@un.org). Never draw a replacement country
  shape, and don’t substitute a flag unless the user asks for flags.

## Saving and naming files

Where files go, how they are named, draft versions and the end-of-job clean-up all
follow **`ocha-files-and-folders`**.
