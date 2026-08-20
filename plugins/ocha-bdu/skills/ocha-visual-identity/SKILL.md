---
name: ocha-visual-identity
description: >
  Apply OCHA's visual identity — brand colours, typography, logo rules, and the
  OCHA Common Design System — to any product Javier or the BDU is making.
  Use this skill whenever the user asks about OCHA brand colours, UN Blue,
  colour ramps, the OCHA logo, Roboto/Crimson Pro/Arial font choices, design
  tokens, the `cd-*` component library, accessibility (WCAG) requirements for
  OCHA products, or when building/editing any OCHA-branded HTML, CSS, slide,
  document, poster, social media graphic, or web page. Trigger on phrases
  like "OCHA brand", "OCHA colours", "UN Blue", "brand guidelines", "design
  system", "use our brand", "OCHA logo", "clear space", "one OCHA". For
  specifically humanitarian maps, use `ocha-mapping`. For specifically charts
  and infographics, use `ocha-dataviz`. For the Illustrator dataviz plugin
  release process, use `ocha-dataviz-release`.
---

# OCHA Visual Identity

Authoritative source: **https://brand.unocha.org** and
**https://un-ocha.github.io/ocha-common-design-system-BDU/**

When editing an existing OCHA product, match the product's current tokens and
components before introducing anything new. Only introduce new colours / fonts
/ components when the existing ones genuinely can't do the job.

---

## 1. Brand colours

### Primary
The brand is **UN Blue** — use it predominantly. Most OCHA products work with
just blue, grey, black, and white. **Resist adding accent colours.**

| Role | Hex | RGB | CMYK | PMS |
|---|---|---|---|---|
| UN Blue (signature) | `#009EDB` | 0, 158, 219 | 80, 20, 0, 0 | 2925 |
| Black | `#000000` | 0, 0, 0 | 0, 0, 0, 100 | — |
| White | `#FFFFFF` | 255, 255, 255 | 0, 0, 0, 0 | — |

### Accessible text variants (WCAG AA / AAA on white)

`#009EDB` **fails WCAG AA for body text on white**. For text on white use:

| Original | AA text variant | AAA text variant |
|---|---|---|
| Blue `#009EDB` | `#0077B8` | `#005392` |
| Green `#72BF44` | `#27833A` | — |
| Orange `#F58220` | `#CF3F0B` | — |
| Red `#ED1847` | `#EB0045` | `#AB1D37` |
| Purple `#A05FB4` | `#9A58AF` | `#733D96` |
| Grey | `#7C7067` | — |

### Accent colours (use sparingly; supplementary only)

| Colour | Hex | RGB | CMYK |
|---|---|---|---|
| Green | `#72BF44` | 114, 191, 68 | 60, 0, 100, 0 |
| Yellow | `#FFC800` | 255, 200, 0 | 0, 20, 100, 0 |
| Orange | `#F58220` | 245, 130, 32 | 0, 60, 100, 0 |
| Red | `#ED1847` | 237, 24, 71 | 0, 100, 70, 0 |
| Purple | `#A05FB4` | 160, 95, 180 | 40, 70, 0, 0 |
| Slate Grey | `#AEA29A` | 174, 162, 154 | 10, 15, 20, 30 |
| Neutral Grey | `#999999` | 153, 153, 153 | 0, 0, 0, 40 |

### Colour ramps (7 steps: darkest → accent → lightest)

Use these for maps, choropleths, and data visualization tints. The named
accent sits in the middle slot (step 4 or 5 depending on the ramp).

**UN Blue** `#002E6E` · `#004987` · `#0074B7` · `#009EDB` · `#64BDEA` · `#C5DFEF` · `#E3EDF6`
**Red** `#520000` · `#780B20` · `#A71F36` · `#ED1847` · `#F3859B` · `#F9C0C5` · `#F7DFDF`
**Green** `#003425` · `#004D35` · `#006747` · `#338C46` · `#72BF44` · `#CEE3A0` · `#E6EFD0`
**Orange** `#70200C` · `#90371C` · `#C15025` · `#F58220` · `#F9A870` · `#FEDCBD` · `#FFEAD5`
**Purple** `#3E125B` · `#5B2C86` · `#763F98` · `#A05FB4` · `#BD8CBF` · `#D5B4D6` · `#E4D7E8`
**Yellow** `#815017` · `#B16D03` · `#CF9220` · `#FFC800` · `#FFDE2F` · `#F8E66B` · `#FAF0BB`
**Slate Grey** `#1B1B1A` · `#493F38` · `#6E6259` · `#AEA29A` · `#C5BFBA` · `#DDDAD7` · `#EDEAE6`
**Neutral Grey** `#262626` · `#4D4D4D` · `#737373` · `#999999` · `#BFBFBF` · `#E6E6E6` · `#F2F2F2`

### Humanitarian product-family colours

| Family | Key | Primary |
|---|---|---|
| OCHA (general) | `ocha` | `#009EDB` UN Blue |
| HNRP (Humanitarian Needs & Response Plans) | `hnrp` | `#F58220` Orange |
| Flash Appeal | `flash` | `#ED1847` Red |
| GHO (Global Humanitarian Overview) | `gho` | `#FFC800` Yellow/Gold |

---

## 2. Typography

### Font tier system (pick by audience, not by preference)

| User level | Primary | Secondary | Why |
|---|---|---|---|
| **Common users** (everyone) | **Arial** (Regular, Italic, Bold, Bold Italic, Black) | — | Ships with every OS. Use for anything collaborative or that will be edited by others. |
| **Advanced users** (designers) | **Roboto** (Thin → Black, with italics) | **Crimson Pro** (ExtraLight → Black, with italics) | Roboto for UI/body. Crimson Pro for long-form print reading. |
| **Infographics** (space-tight) | **Roboto Condensed** | — | Only for infographics; not for body text. |
| **Code / credits / captions** | **Roboto Mono** | — | — |
| **Display / headings (optional)** | **Roboto Slab** | — | Slab variant for headings when a distinct heading style is needed. |
| **Social media** | **Montserrat** (titles), **Raleway** (body), **Roboto Condensed** (photo credits) | — | — |
| **Arabic** | **Almarai** (titles and display), **Noto Sans Arabic** (body and longer text) | — | Adobe USA/EU mis-renders Arabic — use the conversion tool referenced on brand.unocha.org. Both fonts are on Google Fonts (Noto Kufi Arabic and Dubai were dropped from the 2026 hierarchy). |
| **Chinese** | **Noto Sans CJK SC** | — | — |
| **Russian** | **Noto Sans** | — | — |

### Do NOT use
- **Arial Narrow** — licensed with MS Office only, not universal.
- **Avenir / Avenir Next** — legacy primary, replaced by Roboto. Licensed.
- **Minion Pro** — legacy secondary, replaced by Crimson Pro. Licensed.
- **Crimson Text** — use **Crimson Pro** (more weights / styles).

### Type rules
- **Body text**: left-align, right-ragged. Never justified (hurts dyslexic readers).
- **Column width**: 40–80 characters (~12 words/line) for comfortable reading.
- **Numbers**: right-align. Round aggressively using k / M / B abbreviations in humanitarian contexts — precise figures imply certainty we usually don't have.

### Type scale (from the design system)

```
Display:   46px / 2.875rem   --cd-font-size--2xlarge
H1:        38px / 2.375rem   --cd-font-size--2xmedium
H2:        30px / 1.875rem   --cd-font-size--2xbase
H3:        26px / 1.625rem   --cd-font-size--large
H4:        22px / 1.375rem   --cd-font-size--medium
Body:      18px / 1.125rem   --cd-font-size--base
Reference: 16px / 1rem       --cd-font-size--ref
Small:     14px / 0.875rem   --cd-font-size--small
Tiny:      12px / 0.75rem    --cd-font-size--tiny
```

---

## 3. Logo

Two canonical SVG files ship with this skill under `references/` for quick use:
- `OCHA_logo_horizontal_blue.svg`
- `OCHA_logo_horizontal_white.svg`

### Where to find ALL logo files (2024 master set)

The complete, current logo package — every shape, colour, language, and format —
lives in Javier's Dropbox:

**Local path (canonical):**
`~/OCHA DMU Dropbox/<your-name>/Design/Logos/ocha_logo/2024/OCHA_logo_2024/`

**Dropbox link (public):**
https://www.dropbox.com/scl/fo/p8ii3zn8ixo99mjqr18ny/AGdbTBJZFDBdmxjjWbjmTjU?rlkey=rsoq8co6pzh09tcnf7xlgpmnm&dl=0

Folder structure:

| Folder | Contents |
|---|---|
| `1_Print_CMYK/` | EPS files for print, per language (EN, ES, FR, RU, ZH, AR, Acronym, Multilanguage), blue-on-white |
| `2_Web_RGB/main/` | Core SVGs: `OCHA_logo_{horizontal,vertical}_{blue,white}.svg` |
| `2_Web_RGB/full_text/` | Spelled-out SVGs (with the full "United Nations Office…" descriptor), per language × horizontal/vertical × blue/white |
| `3_Other_uses_RGB/main/` | PNG raster versions of the core logos |
| `3_Other_uses_RGB/full_text/` | PNG rasters of the spelled-out logos (per language × horizontal/vertical × blue/white) |

Rule of thumb: **SVG for web/digital, EPS for print, PNG only when SVG isn't accepted.**
Use `2_Web_RGB/main/` for almost all digital work; use `full_text/` only when the OCHA
acronym needs spelling out; match the language file to the product's language.

### Variants (4 shapes × 2 colours = 8 files on brand.unocha.org)

1. **Horizontal** — default, for most products.
2. **Vertical** — for tall, narrow spaces.
3. **Spelled-out horizontal** — with "United Nations Office for the Coordination of Humanitarian Affairs". Use when the OCHA acronym may not be recognised. Only at medium/large sizes so the descriptor is readable.
4. **Spelled-out vertical** — same purpose, vertical format.

Each is available in **positive (blue)** and **negative (white)**. Blue on
light backgrounds, white on dark backgrounds. Never recolour.

### Clear space
Minimum clear space = **½ the diameter of the UN globe emblem** on all four
sides. Nothing (text, photo, other logo) may enter that zone.

### Minimum size

| Variant | Print | Screen |
|---|---|---|
| Horizontal | 20 mm wide | 57 px wide |
| Vertical | 10 mm wide | 28 px wide |

Below this requires approval from the Design and Multimedia Unit.

### NEVER
- Alter, distort, recolour, stretch, or add effects to the logo.
- Translate the word "OCHA" — always keep the acronym. Only the spelled-out descriptor is translated.
- Add office / country / regional names beneath or beside the logo. This is the **"One OCHA"** rule — the logo represents the whole organisation. If you need to identify a regional office or country office, put that text in the product's header/footer, separately from the logo.
- Place on busy or low-contrast backgrounds.

### Co-branding (OCHA logo next to partner logos)
1. Match **orientation** first (both horizontal or both vertical).
2. Match the **emblem size** (UN globe vs partner's equivalent emblem element).
3. If that makes one logo disproportionate, match **type size** instead.
4. Exception: one partner may be enlarged if it needs extra recognition.
5. For complex cases: contact **ochavisual@un.org**.

### UN emblem authorisation
- UN System entities (including OCHA) don't need written authorisation for official use — see **ST/AI/189/Add.21**.
- Non-UN entities (governments, IGOs, NGOs, private sector) must request authorisation from the Office of Legal Affairs: **gld@un.org**.
- Textbook reproduction: **permissions@un.org**.
- Suppliers may not use the UN name/emblem to advertise a contractual relationship with the UN.

---

## 4. OCHA Common Design System (`cd-*`)

A framework-agnostic HTML/CSS component library used by OCHA's Drupal sites
and by other OCHA digital products.

- **Live reference:** https://un-ocha.github.io/ocha-common-design-system-BDU/
- **Local repo (canonical):** `~/OCHA DMU Dropbox/<your-name>/Design/Visual_identity/OCHA_design_system/ocha-common-design-system-BDU/`
- **Full component rules reference:** `references/OCHA_DESIGN_SYSTEM_RULES.md` in this skill folder — inline it into `CLAUDE.md` (or `.github/copilot-instructions.md`) for any new OCHA web project.

### Principles
1. **Universal adaptability** — the system flexes to fit any OCHA mission.
2. **Impact driven** — practicality first; fast, clear solutions for urgent contexts.
3. **Inclusive** — WCAG 2.1 AA minimum, always.

### Core tokens
```css
--brand-primary:          #009EDB;  /* fills / backgrounds / brand moments */
--brand-primary--text:    #0077B8;  /* text on white (AA) */
--brand-primary--dark:    #004987;  /* hover / dark accents */
--brand-primary--light:   #64BDEA;  /* tints, focus rings */

--brand-highlight:        #ED1847;  /* CTAs */
--brand-success:          #27833A;
--brand-warning:          #CF3F0B;
--brand-error:            #EB0045;
--brand-info:             #0077B8;

--brand-default-text-color: #4D4D4D;
--brand-grey--text:       #737373;
--brand-grey:             #F2F2F2;  /* surface */
--brand-grey--border:     #BFBFBF;
```

### Components (use these — do not invent new ones)

`cd-alert`, `cd-article`, `cd-banner`, `cd-block-title`, `cd-bullet-list`,
`cd-button` (variants: default, `--outline`, `--small`, `--danger`, `--export`, `--light`),
`cd-byline`, `cd-caption`, `cd-card`, `cd-date`, `cd-disclosure` (accordion),
`cd-dropdown`, `cd-event`, `cd-facets`, `cd-figure-list` (key stats), `cd-filter`,
`cd-flow` (vertical rhythm utility), `cd-form`, `cd-grid`, `cd-hero`,
`cd-image-grid`, `cd-link-list`, `cd-menu`, `cd-page-title`, `cd-pagination`,
`cd-read-more`, `cd-search`, `cd-search--inline`, `cd-social-links`,
`cd-styled-list`, `cd-table`, `cd-tabs`, `cd-tag`, `cd-teaser`,
`cd-title-list`, `cd-toc`, `cd-user-menu`.

Full HTML snippets for each are in `references/OCHA_DESIGN_SYSTEM_RULES.md`.
When in doubt, open the component's page on the live reference site and copy
the HTML markup exactly.

### Layout

```
Max body width:    1400px   --cd-max-body-width
Max layout width:  1220px   --cd-max-width
Max content width: 820px    --cd-max-content-width

Mobile padding:    12px     --cd-container-padding
Tablet padding:    24px     --cd-container-padding-tablet
Desktop padding:   40px     --cd-container-padding-xlarge
```

### Breakpoints (mobile-first)
```
Small:  576px    --cd-bp--sm
Medium: 768px    --cd-bp--md
Large:  1024px   --cd-bp--lg
XL:     1200px   --cd-bp--xl
XXL:    1400px   --cd-bp--xxl
```

### Accessibility (mandatory)
- WCAG 2.1 AA minimum for every component.
- Use `--brand-*--text` variants for text on white.
- Every interactive element must be keyboard-navigable via Tab.
- Focus: `outline: 3px solid var(--brand-primary--light)`.
- Semantic HTML: `<button>` not `<div onclick>`, `<nav>` not `<div class="nav">`.
- Images need `alt`. Decorative images use `alt=""`.
- SVG icons: `aria-hidden="true" focusable="false"`.
- Support RTL: use `margin-inline-start` / `padding-inline-end` instead of left/right.

---

## 5. Hard rules — what NOT to do

- Do not use `#009EDB` for body text on white — fails WCAG AA. Use `#0077B8`.
- Do not hardcode hex values in HTML/CSS for OCHA products — use `--brand-*` tokens.
- Do not invent new `cd-*` component class names — reuse existing ones.
- Do not use Arial Narrow, Avenir, Minion Pro, or Crimson Text.
- Do not place the logo on busy backgrounds, below minimum size, or with office names attached.
- Do not add accent colours beyond the defined palette. Most products need only blue + grey + black.
- Do not use drop shadows, 3D, or decorative effects on OCHA branded products.

---

## 6. Setting up a new OCHA web project

For any new HTML/CSS/JS product:

1. Copy `references/OCHA_DESIGN_SYSTEM_RULES.md` into the project as `CLAUDE.md`
   (or `.github/copilot-instructions.md` for Copilot users). This bakes the
   design rules into AI tool context.
2. Use `cd-*` components and CSS custom properties from day one.
3. Link to the live reference for anything not covered:
   https://un-ocha.github.io/ocha-common-design-system-BDU/

---

## Contacts

- **Team:** OCHA Brand and Design Unit (BDU) — **ochavisual@un.org**
- **Focal point:** Javier Cueto — **cuetoj@un.org**
