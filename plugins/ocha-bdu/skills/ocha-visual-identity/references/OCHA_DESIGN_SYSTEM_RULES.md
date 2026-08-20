# OCHA Design System — Common Design Rules

> Drop this file into your project to make AI tools (Copilot, Claude, ChatGPT) follow the OCHA design system.
>
> - **GitHub Copilot:** save as `.github/copilot-instructions.md`
> - **Claude Code:** save as `CLAUDE.md`
> - **ChatGPT / other:** paste into Custom Instructions or system prompt
>
> Source: https://un-ocha.github.io/ocha-common-design-system-BDU/
> Maintained by: OCHA Brand and Design Unit (BDU) — ochavisual@un.org

---

## Principles

1. **Universal adaptability** — the system flexes to fit any OCHA mission or product. No exceptions.
2. **Impact driven** — practicality first. Fast, clear solutions for urgent contexts. The product works well where it matters most.
3. **Inclusive** — leave no one behind. Accessible by default. WCAG 2.1 AA minimum.

---

## Brand colours

Primary colour is **UN Blue `#009EDB`** (Pantone 2925). Use it for fills, backgrounds, and brand moments.

For **text on white backgrounds**, use the accessible variant `#0077B8` (WCAG AA). Never use `#009EDB` for body text — it fails contrast.

```
Primary fill:        #009EDB  (--brand-primary)
Primary text on white: #0077B8  (--brand-primary--text)
Primary dark/hover:  #004987  (--brand-primary--dark)
Primary light fill:  #64BDEA  (--brand-primary--light)

Highlight/CTA:       #ED1847  (--brand-highlight)
Success:             #27833A  (--brand-success)
Warning:             #CF3F0B  (--brand-warning)
Error:               #EB0045  (--brand-error)
Info:                #0077B8  (--brand-info)

Body text:           #4D4D4D  (--brand-default-text-color)
Muted text:          #737373  (--brand-grey--text)
Surface:             #F2F2F2  (--brand-grey)
Border:              #BFBFBF  (--brand-grey--border)

Black:               #000000
White:               #FFFFFF
```

### Accent colours (supplementary — use sparingly)

```
Green:    #72BF44   (Green AA text: #27833A)
Yellow:   #FFC800
Orange:   #F58220   (Orange AA text: #CF3F0B)
Red:      #ED1847   (Red AA text: #EB0045, Red AAA: #AB1D37)
Purple:   #A05FB4   (Purple AA text: #9A58AF, Purple AAA: #733D96)
```

> **Resist the temptation to add more colours.** Most OCHA products work with just blue, grey, and black.

---

## Typography

- **Primary font:** Roboto (body, UI, general)
- **Headings:** Roboto or Roboto Slab
- **Infographics:** Roboto Condensed (saves space)
- **Code / credits:** Roboto Mono
- **Print long-form:** Crimson Pro (serif)
- **Fallback:** Arial (common users, collaborative docs)
- **Arabic titles/display:** Almarai. **Arabic body/longer text:** Noto Sans Arabic
- **Chinese:** Noto Sans CJK SC
- **Russian:** Noto Sans

### Type scale

```
Display:   46px / 2.875rem  (--cd-font-size--2xlarge)
H1:        38px / 2.375rem  (--cd-font-size--2xmedium)
H2:        30px / 1.875rem  (--cd-font-size--2xbase)
H3:        26px / 1.625rem  (--cd-font-size--large)
H4:        22px / 1.375rem  (--cd-font-size--medium)
Body:      18px / 1.125rem  (--cd-font-size--base)
Reference: 16px / 1rem      (--cd-font-size--ref)
Small:     14px / 0.875rem  (--cd-font-size--small)
Tiny:      12px / 0.75rem   (--cd-font-size--tiny)
```

### Do NOT use these fonts
- Arial Narrow
- Avenir (replaced by Roboto)
- Minion Pro (replaced by Crimson Pro)
- Crimson Text (use Crimson Pro)

---

## Components — use these, don't invent new ones

All components use the `cd-` prefix with BEM naming. When building HTML, use these exact class names:

### Button
```html
<button class="cd-button" type="button">
  <span class="cd-button__text">Primary action</span>
</button>

<!-- Variants: cd-button--outline, cd-button--small, cd-button--danger, cd-button--export, cd-button--light (dark bg) -->
```

### Alert
```html
<div class="cd-alert cd-alert--error">
  <div role="alert">
    <div class="cd-alert__message"><p>Error message here.</p></div>
  </div>
</div>

<!-- Variants: (default = info), cd-alert--error, cd-alert--warning, cd-alert--status -->
```

### Card
```html
<div class="cd-card">
  <div class="cd-card__content">
    <h3 class="cd-card__title"><a href="#">Card title</a></h3>
    <p class="cd-card__body">Card description text.</p>
  </div>
</div>
```

### Table
```html
<table class="cd-table">
  <thead><tr><th>Column A</th><th>Column B</th></tr></thead>
  <tbody><tr><td>Data</td><td>Data</td></tr></tbody>
</table>
```

### Hero
```html
<div class="cd-hero">
  <div class="cd-hero__content">
    <h1 class="cd-hero__title">Page title</h1>
    <p class="cd-hero__subtitle">Supporting description.</p>
  </div>
</div>
```

### Page title / Block title
```html
<h1 class="cd-page-title">Page title</h1>
<h2 class="cd-block-title">Section title</h2>
```

### Teaser
```html
<article class="cd-teaser">
  <h3 class="cd-teaser__title"><a href="#">Teaser title</a></h3>
  <p class="cd-teaser__body">Short description.</p>
  <div class="cd-teaser__meta">Meta</div>
</article>
```

### Article
```html
<article class="cd-article">
  <h1 class="cd-article__title">Article title</h1>
  <div class="cd-article__content">
    <p>Long-form content paragraphs.</p>
  </div>
</article>
```

### Banner
```html
<div class="cd-banner">
  <img class="cd-banner__image" src="banner.jpg" alt="">
  <div class="cd-banner__overlay">
    <h2 class="cd-banner__title">Banner heading</h2>
  </div>
</div>
```

### Form
```html
<form class="cd-form">
  <div class="cd-form__item">
    <label class="cd-form__label" for="name">Name</label>
    <input class="cd-form__input" id="name" type="text">
  </div>
</form>
```

### Search
```html
<form class="cd-search" role="search">
  <label class="cd-search__label" for="q">Search</label>
  <input class="cd-search__input" id="q" type="search">
  <button class="cd-search__submit" type="submit">Search</button>
</form>
```

### Tabs
```html
<div class="cd-tabs">
  <ul class="cd-tabs__list" role="tablist">
    <li class="cd-tabs__item"><a href="#t1" role="tab" aria-selected="true">Tab 1</a></li>
    <li class="cd-tabs__item"><a href="#t2" role="tab">Tab 2</a></li>
  </ul>
</div>
```

### Pagination
```html
<nav class="cd-pagination" aria-label="Pagination">
  <ul class="cd-pagination__list">
    <li><a class="cd-pagination__link" href="#" aria-current="page">1</a></li>
    <li><a class="cd-pagination__link" href="#">2</a></li>
  </ul>
</nav>
```

### Grid
```html
<div class="cd-grid">
  <div class="cd-grid__item">…</div>
  <div class="cd-grid__item">…</div>
  <div class="cd-grid__item">…</div>
</div>
```

### Byline / Date
```html
<p class="cd-byline">By <span class="cd-byline__author">Author</span></p>
<time class="cd-date" datetime="2026-04-15">15 April 2026</time>
```

### Caption
```html
<figure>
  <img src="…" alt="…">
  <figcaption class="cd-caption">Photo credit / caption text.</figcaption>
</figure>
```

### Styled list / Bullet list
```html
<ul class="cd-styled-list">
  <li>Item one</li>
  <li>Item two</li>
</ul>

<ul class="cd-bullet-list">
  <li>Highlighted bullet</li>
  <li>Highlighted bullet</li>
</ul>
```

### Link list
```html
<ul class="cd-link-list">
  <li><a href="#">Link one</a></li>
  <li><a href="#">Link two</a></li>
</ul>
```

### Read more
```html
<a class="cd-read-more" href="#">Read more <span class="visually-hidden">about X</span></a>
```

### Table of contents (ToC)
```html
<nav class="cd-toc" aria-label="Table of contents">
  <h2 class="cd-toc__title">On this page</h2>
  <ul class="cd-toc__list">
    <li><a href="#section-1">Section 1</a></li>
  </ul>
</nav>
```

### Disclosure (accordion)
```html
<details class="cd-disclosure">
  <summary class="cd-disclosure__summary">Question</summary>
  <div class="cd-disclosure__content"><p>Answer.</p></div>
</details>
```

### Dropdown
```html
<div class="cd-dropdown">
  <button class="cd-dropdown__toggle" aria-expanded="false">Menu</button>
  <ul class="cd-dropdown__menu" hidden>
    <li><a href="#">Option 1</a></li>
  </ul>
</div>
```

### Flow (vertical rhythm utility)
```html
<!-- Adds consistent spacing between direct children -->
<div class="cd-flow">
  <h2>Heading</h2>
  <p>Paragraph with proper spacing above/below.</p>
  <p>Next paragraph.</p>
</div>
```

---

## Layout rules

```
Max body width:    1400px  (--cd-max-body-width)
Max layout width:  1220px  (--cd-max-width)
Max content width: 820px   (--cd-max-content-width)

Mobile padding:    12px    (--cd-container-padding)
Tablet padding:    24px    (--cd-container-padding-tablet)
Desktop padding:   40px    (--cd-container-padding-xlarge)
```

### Breakpoints
```
Small:     576px   (--cd-bp--sm)
Medium:    768px   (--cd-bp--md)
Large:     1024px  (--cd-bp--lg)
XL:        1200px  (--cd-bp--xl)
XXL:       1400px  (--cd-bp--xxl)
```

Always use **mobile-first** CSS: base styles for mobile, `@media (min-width: ...)` for larger screens.

---

## Accessibility — mandatory

- **WCAG 2.1 AA minimum** for all components
- Use the `--brand-*--text` colour variants for text on white (they pass AA contrast)
- Every interactive element must be **keyboard navigable** via Tab
- Focus indicator: `outline: 3px solid var(--brand-primary--light)`
- Use semantic HTML: `<button>` not `<div onclick>`, `<nav>` not `<div class="nav">`
- Images need `alt` text. Decorative images use `alt=""`
- SVG icons: `aria-hidden="true" focusable="false"`
- Support RTL: use `margin-inline-start` / `padding-inline-end` instead of `margin-left` / `padding-right`

---

## Logo rules

- OCHA logo minimum width: **57px horizontal**, **28px vertical**
- Clear space around logo: half the UN globe diameter on all sides
- Blue logo on light backgrounds, white logo on dark backgrounds
- **Never** alter, recolour, distort, add office names, or translate "OCHA"

---

## What NOT to do

- Do NOT use hex colours directly — use `--brand-*` CSS custom properties
- Do NOT invent new component class names — use existing `cd-*` components
- Do NOT use `#009EDB` for body text (fails WCAG AA) — use `#0077B8`
- Do NOT use Arial Narrow, Avenir, Minion Pro, or Crimson Text
- Do NOT place the logo on busy backgrounds or below minimum size
- Do NOT add more accent colours beyond the defined palette

---

## Reference

Full component library, live examples, and props:
**https://un-ocha.github.io/ocha-common-design-system-BDU/**

When in doubt, open the relevant component's page there and match the HTML markup exactly.
