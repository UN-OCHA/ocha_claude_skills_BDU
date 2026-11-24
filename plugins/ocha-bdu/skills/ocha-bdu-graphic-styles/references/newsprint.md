# Newsprint: recipe and values

All values are in the starter, `templates/newsprint/newsprint_example_drf_platform.html` (a half-page graphic,
486 × 366 pt page, 456 × 336 pt artwork). Copy that file, keep its CSS and filters, and replace the content.

## Palette

| Token | Value | Use |
|---|---|---|
| `--ground` | #FAF8F3 | the paper |
| `--paper` | #FBF9F4 | paper pieces: badges, cards, the example sheet |
| `--ink` | #232120 | text, label strips, arrows, the blast (lifted black, never #000) |
| `--ink-2` | #45423E | secondary text |
| `--blue` | #009EDB | OCHA blue: icons, dashed boxes, inverted badges |
| `--blue-text` | #0074B7 | blue text (entity names) |
| `--marker` | #F58220 | OCHA Orange marker, at 92% opacity (reads like ink on newsprint) |
| group circle | #EDF6FB, multiply | the light blue grouping circle |
| “Agree on funding” money | #64BDEA | OCHA light blue, for money set aside but not paid |

## The ground (layers, bottom to top)

1. `background-color: --ground`.
2. Off-centre stains: radial gradients of rgba(110,85,55,0.03–0.035), one large at the top right, one tall at the
   lower left, plus a faint diagonal light-to-warm shading. Asymmetric on purpose.
3. Graph-paper grid: 0.5 pt lines every 12 pt, rgba(35,33,32,0.032).
4. Grain: fractal noise (baseFrequency 0.85) at alpha 0.04, plus fibres (baseFrequency 0.02 × 0.6) at alpha 0.05.
5. Crumple: low-frequency noise lit from the top left (feDiffuseLighting, surfaceScale 5), multiplied at 7%.

Open areas should measure about 240–245 on the 0–255 scale; if it reads grey, lower layers 4 and 5 first.

## Paper pieces

The ::before of each piece carries the paper and the filter, so letters and icons stay crisp. Filter `cut0–4`
(five seeds): fractal noise baseFrequency 0.09, displacement 1.8 (labels 1.3), then a hard shadow offset
0.6 / 0.9 pt, #3A2E22 at 20%. Pieces are never rotated.

## Type

Roboto only (no serif, user decision). Title: Roboto Black 20 pt / 22 pt, sentence case, two or three lines, on the
paper with no strip. Labels: Roboto Bold 8 pt, white on a black strip (`.w`). Example text 7–8 pt.

## Ink and marker

- Icons: OCHA Humanitarian Icons only, with the `ink` filter (fine speckle, baseFrequency 2.2).
- Marker (`.mk`): orange band behind the words, skewed −6°, its edge displaced by stretched noise (`marker`
  filter) so it looks hand-swiped. One or two per graphic.
- Events: a black eight-point blast on the edge of the thing it hits.

## The process that worked (first job, 24 Nov 2026)

1. Start from the sketch and the source wording, flat OCHA version first; agree the flow.
2. Explore styles side by side, PNG only, one export folder per style; archive the rest by style.
3. Refine in small steps from the client’s eye: each change archived first, then re-rendered and checked at
   full size and in close crops.
4. Once chosen, the style’s file becomes the single final (no style name), and the editable .ai is made last from
   `make_ai_source.py`’s vector copy.

## Known traps

- `data-ai-name` on elements made the .ai exporter drop them (arrows, side badges, label strips). The vector copy
  strips them.
- Layer containers with no size: the exporter can’t place their contents. Give `.art > div` the artwork size.
- An element above the title in the DOM flips the .ai layer order: put background shapes first in the artwork.
- Anything with an SVG filter prints as an image; that is why the .ai is built from the vector copy.
