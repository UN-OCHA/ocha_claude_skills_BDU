# Motion rules — with the reasons

Each rule below was a correction on a real OCHA film. The reason matters more than the rule:
when a new situation doesn't fit, reason from it.

---

## 1. An exit is its entrance played backwards

**Rule.** Give every element exactly one move. It enters by playing that move forward and
leaves by playing the same move in reverse, with the same easing mirrored.

| Entrance | Exit |
|---|---|
| Rises up and fades in | Sinks down and fades out |
| Scales up from its anchor | Scales down to its anchor |
| Line or rule draws on | Draws off |
| Bar grows from its left edge | Shrinks back to its left edge |
| Number counts up | Counts back down |
| Label types on | Deletes |
| Slides in from the right | Slides back out to the right |

**Why.** A generic fade-out on something that scaled in looks like a mistake: the viewer's eye
expects the move to resolve the way it started. It also makes the whole film read as one
system instead of a pile of effects.

**How.** Compute a single state `q` (0 = gone, 1 = in place) and drive the element from it.
During the scene exit, `q = min(entrance, ease(1 − exitProgress))`. `life()` in
`scripts/motion.js` does exactly this.

## 2. Text rises in, line by line

**Rule.** Reading text enters by fading up a short distance, each line on its own beat (about
0.12 s apart). Split multi-line text into explicit lines so each can have its beat.

**Avoid.** Typewriter reveals for reading text (fine for a short mono label or URL); mask or
clip wipes on text (they read as a glitch); whole paragraphs arriving as one slab.

## 3. Icons scale from their own anchor

**Rule.** Icons scale up with a fade, from their bottom centre for figures that "stand up", or
their centre for emblems and badges. Set `transform-origin` accordingly.

**The trap.** An icon inside a full-width block has its "bottom centre" far to the right of the
icon, so it grows out of empty space. Make the box hug the icon (`width: fit-content`).

**Avoid.** Mask reveals on icons and logos. A logo made of an emblem and a wordmark animates in
two beats: emblem scales from its centre, then the wordmark rises like text.

## 4. Transform, don't replace

**Rule.** When a value changes meaning in the same place ("$23B needed" becomes "More than
$13B funded"), don't remove one and bring in another. Keep the element: slide it to make room
for any new words and count it to the new value.

**Why.** Two separate slides for one idea break the viewer's thread. A single object changing
explains the relationship between the two numbers without words.

The same goes for charts: a bar that shows the requirement and then the funding is **one** bar,
drawn once, filling in place.

## 5. A chart arrives with its number

**Rule.** The bar grows while its figure counts, with the same easing and timing, so the full
bar *is* the figure. A legend rises with — or right after — the graphic it explains.

**Why.** A bar that appears before or after its number asks the viewer to connect them.

## 6. Follow-ups arrive on a real moment

**Rule.** Secondary labels ("More than half funded", "still needed") arrive when something
visible happens — typically when the fill is half done — one after another.

**How.** Use an in-out ease for fills (`inOutCubic`) so the halfway point in time is the
halfway point on screen. With ease-out, "half filled" happens in the first 15% of the time.

A label that was only there to name the empty chart ("requirements") stays until just before
the follow-ups arrive, then leaves by reversing its entrance.

## 7. Secondary text comes in early and fast

**Rule.** Sources, footers and chrome labels appear right after the frame draws (about 0.9 s
in) and complete quickly (about 0.5 s). They are there to be found, not watched.

## 8. Nothing is left behind a transition

**Rule.** When a panel wipes across the frame to change scene, the outgoing scene's content must
be completely gone at the instant the panel covers the whole frame — and not a frame later.

**Why.** The moment the panel starts to leave, it uncovers the frame again. Anything still
there shows through behind it. On a real film, flags and figures reappeared behind a rising
panel because the scene's exit was set to end a quarter of a second too late.

**How.** Compute the cover instant from the wipe's own easing and end the outgoing scene there.
For a panel moving `100% → −100%` with `outCubic` over `D` seconds from `A`, it covers fully
when `outCubic(p) = 0.5`, i.e. `A + D × (1 − ∛0.5)`. `wipeCoverTime()` in `scripts/motion.js`.
Never hand-tune the number: it goes stale the next time anyone retimes the wipe.

## 9. Loops are seamless

**Rule.** For a looping film, the last frame and the first frame must be the same (usually an
empty frame with the chrome retracted). Everything, including persistent rules and labels,
leaves in the reverse order it arrived, finishing exactly at the loop point.

**Why.** A rule that is fully drawn on the last frame and absent on the first pops on every loop.

## 10. One thing at a time

**Rule.** Stagger arrivals so the eye has one new thing to read at a time: headline, then its
qualifier lines, then the supporting graphic. Grids of icons or flags arrive as a wave
(diagonal stagger), not all at once.

---

## Timing (1920×1080, 30 fps)

| Move | Duration | Easing | Distance / scale |
|---|---|---|---|
| Scene cover (next scene arrives) | 0.3 s | linear opacity | — |
| Scene exit window | 0.5 s, ending at scene end | mirrored entrance | — |
| Headline rise | 0.8 s | outCubic | 40–46 px |
| Text line rise | 0.7 s, lines 0.12 s apart | outCubic | 24–36 px |
| Small label rise | 0.6 s | outCubic | 12–20 px |
| Icon scale-in | 0.5 s | outQuint | from 45% |
| Grid wave (icons, flags) | 0.45 s each, 0.055 s per step | outQuint | from 45–82% |
| Number count-up | 1.9 s | outQuint | — |
| Bar or fill (with a meaningful midpoint) | 2.6 s | inOutCubic | — |
| Bar grow with its count | same as the count | same as the count | — |
| Rule / line draw-on | 0.6–0.95 s | outQuint | — |
| Chrome label type / delete | 0.4 s | linear | — |
| Footer / sources type-on | 0.55 s, starting ~0.9 s | linear | — |
| Wipe panel through the frame | 1.45 s | outCubic | 100% → −100% |

Easings: `outCubic = 1 − (1 − p)³`, `outQuint = 1 − (1 − p)⁵`,
`inOutCubic = p < .5 ? 4p³ : 1 − (−2p + 2)³ / 2`.
