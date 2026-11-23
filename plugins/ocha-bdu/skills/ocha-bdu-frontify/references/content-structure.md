# How brand-site pages are organised

Apply these every time without asking.

## Hierarchy

| Level | What | How it’s built | In the page’s side menu? |
|---|---|---|---|
| **Section** | Major area (Logo, Colours, Fonts) | Frontify **Heading** element | Yes |
| **Subsection** | Topic inside a section (Primary, Accent colours) | **Text block** (app `2044620`) holding only a `heading3` title | No |

Headings fill the side menu. Subtitles inside text blocks structure the page without cluttering it.

## Main brand or sub-brand

- **Main brand** (OCHA Visual Identity): one page per area. Colours is a page, Fonts is a page.
- **Sub-brand** (IASC, HNPW): all areas on one page, using sections, subsections and dividers.

## Separators (Divider block, app `405579`)

| Style | Where |
|---|---|
| **Dashed** | Between subsections inside a section |
| **Solid** | Between sections: after the last subsection, before the next heading |

## Order inside a subsection

1. Text block with the subtitle only, no paragraph
2. The content (colour block, reference, image)
3. Dashed divider, if another subsection follows

The last subsection in a section ends with a solid divider.

## Example: IASC page, Colours section

```
Intro text block
Heading "Colours"
  Text block: subtitle "Primary color"
  Colour block
  --- dashed ---
  Text block: subtitle "Accent colours"
  Reference to the OCHA accent palette
  --- dashed ---
  Text block: subtitle "Colour ramps"
  Colour block, then references to the other ramps
=== solid ===
Heading "Fonts"
```

Good blocks to copy settings from, on the IASC page (`4243684`): subtitle text `12101216`, dashed divider `12101218`, solid divider `12101220`.

## Text content

The Text block’s `content` is a Slate JSON string. A subtitle is:

```json
[{"type":"heading3","children":[{"text":"Primary color","textStyle":"heading3"}]}]
```

Older pages use native text blocks (“Text (legacy)”), which hold HTML. New ones can’t be created any more; existing ones can be edited with `update_block_html_content`. They keep `h2`, `h3`, `p`, `strong`, `em`, `ol`, `ul`, `li` and `a`, and strip `img`. Links need `class="link"` or they show as grey chips:

```html
<a class="link" href="URL" target="_blank">LABEL</a>
```

Read a block’s content first and change only what you need. Don’t re-author the markup.

Changes can take about 10 seconds to appear: hard refresh if you don’t see them.
