---
name: ocha-social-media
description: >
  Produce OCHA social media graphics in Canva for the BDU: carousels, impact stories, static cards,
  video-ready slide sets. Covers the whole job: reading the brief and copy from the Trello card, getting
  photos (through ocha-photo), duplicating the right Canva template and filing it per the Canva
  SOP, building the slides to the BDU grid and type rules, making them video-ready, and handing the
  social media team a Canva link. Use whenever someone asks to "make a carousel", "create the social
  media graphics", "impact story", "social cards", "Instagram/LinkedIn/X post", "do the Canva for this
  Trello card", "use the carousel template", or shares a Trello card from the Socials Work Plan board, a
  MediaValet link or a Canva template link. Also use when asked to turn a post into a new Canva template.
---

# OCHA social media graphics (Canva)

The deliverable is **only the Canva design link**. The social media team reviews it, edits text if
needed and downloads the final JPEG themselves. BDU does not export PNG/JPEG unless asked (if ever
needed: JPEG, it is photo-based), so the job folder never needs an `export/` of finals.

Brand basics come from `ocha-visual-identity`, copy rules from `ocha-editorial-style`, photos (MediaValet,
enhancement, credits) from `ocha-photo`, job folders and file names from `ocha-files-and-folders`.

---

## 0. Before starting — check the tools, and tell the person what is missing

Check these **before** any work and tell the BDU colleague plainly if something is missing. Do not start
a job that will stall halfway.

1. **Canva connector** — required. If the Canva tools are not available, say:
   *“This needs the Canva connector. In the Claude app go to **Settings → Connectors → Canva → Connect**,
   and sign in with the BDU team’s shared Canva account, where the templates live (ask the BDU team if you
   don’t have it). Then start a new conversation.”*
2. **Claude in Chrome** — needed for the steps the connector cannot do (fonts, guides, transitions,
   animations; see §4). If it is not connected, ask them to install/enable the Claude in Chrome extension
   and sign in to the same Canva account in Chrome.
3. **Trello — or the pasted brief.** The brief and cleared copy live on the Trello card. Before anything
   else, ask for one of the two:
   - **Connect Trello:** in the Claude app, **Settings → Connectors → Trello → Connect**, signed in with an
     account that can see the BDU workspace (Socials Work Plan board); then share the card link.
   - **Or paste the brief** into the chat: the cleared copy per slide, the photo link(s) per slide, and
     any credits or notes from the comments.
   Don’t start building from a card you can’t read, and don’t guess copy.
4. **MediaValet** — photos come through the `ocha-photo` skill, which checks its one-time setup (the
   colleague asks Javier Cueto for the MediaValet keys) and falls back to the web app if needed.

Then tell the person, once, that **some Canva steps can’t be done through the connector and will be done
in their Chrome** (§4), so they’re not surprised when Chrome moves.

## What the Canva connector can and cannot do

| Can (connector) | Cannot (needs Chrome, see §4) |
|---|---|
| List/search folders, copy, move, rename designs | Change font family or set weights other than normal/bold |
| Replace text, resize/position elements, line height, size, alignment | Add or clear guides |
| Replace photos, crop/reframe media, opacity, layer order | Page transitions and page timing |
| Upload photos and other images | Remove or change animations |
| Insert images (e.g. gradients), speaker notes, delete elements | Delete a design (Move to Bin) |
| Export, comment, autofill Brand Templates | Rename a folder |

Text added through the connector always comes out in Canva’s default font, so it can’t be used to work
around the font limit. Using the Canva desktop app instead of Chrome does not change any of this.

---

## 1. Brief and copy

- Read the Trello card (description, checklist, comments, attachments) — or the brief the person pasted
  (§0). The **card description is the cleared copy**; comments often hold the edits already folded in. Never reword cleared copy, and never
  change figures — flag doubts instead.
- Note per slide: copy and photo link. Check the copy against `ocha-editorial-style` and **flag**
  (don’t fix) anything off.
- **Propose where the job lives — in Canva and in Dropbox — and get a yes before creating anything**
  (Javier, 19 Oct 2026). Don’t rely on a stored list of folders; they change. Scan them fresh each job:
  - **Canva:** list the folder tree of the shared account (`list-folder-items` from `root`, two levels deep,
    folders only) and look where similar recent posts live (`search-designs` for the country or topic).
  - **Dropbox:** follow `ocha-files-and-folders` (`Projects/<year>/<office>/<job_name>/`) and list the
    sibling jobs in that office folder (e.g. `Projects/2026/FOD/CB/PE/SM/`) to match how they are named.
  - Then show **one proposal** in a single question: the Canva file name + folder, and the Dropbox job
    folder path, each with a one-line reason (“other CBPF donor posts are here”). Offer the next-best
    alternative if two fit. Create, rename and move only after the person confirms.
- Then create the job folder per `ocha-files-and-folders` (`source/`, `info/`, `README.md`, `CLAUDE.md`).

## 2. Photos — use `ocha-photo`

Get, enhance and credit the photos with the **`ocha-photo`** skill:

- download the **originals** of each slide’s MediaValet link into `source/photos_mediavalet/`, with
  `credits.json`;
- **ask** whether to apply the BDU photo enhancement (the default) and, if yes, use the files in
  `source/photos_enhanced/`;
- write the credits in the OCHA format from `ocha-photo` (“Photo: UNOCHA/First Last”) and tell the
  requester when the MediaValet record differs.

## 3. Canva: template → copy → name → file → build

Follow the BDU Canva SOP: **make a copy of the template, rename it, move it to the right folder, then design.**

- Templates live in the Canva folder **Templates_DONT_CHANGE** (find it with a folder search). Never edit a
  template itself.
- **Carousel template:** `Generic_Carousel` (design `DAHYcodbDIk`, since 19 Oct 2026, based on the Nepal
  floods carousel) in `Templates_DONT_CHANGE/Carousel`. 7 slides, 1080×1440: cover (UN blue kicker + caps
  headline + OCHA mark), statement slides with text at the bottom or the top, and a centred call-to-action
  end slide. Delete the slides a post doesn’t need. Page 1 speaker notes hold the rules.
- **More slides than the template has:** duplicate the closest existing slide (statement with text at
  the top, or at the bottom) — never build a slide from a blank page, it would miss the gradients, grid
  positions and fonts. Duplicate in the Canva editor (Chrome): page thumbnail → **⋯ → Duplicate page**,
  then drag it into place; the connector cannot duplicate a page. Then swap photo, text and credit through
  the connector. After adding slides, check in Chrome that the new pages also have **Dissolve 0.5 s**, **4 s**
  timing and **no animation** (re-apply “Apply between all pages” / “Apply to all pages” if not), and keep
  the cover first and the call to action last. Guides apply to every page automatically.
- **Name:** `YYYYMM_Country_Title` (e.g. `202610_Chad_UNICEF-SAKHAL impact story`).
- **Folder:** the one the person confirmed in §1 (by subject, e.g. pooled-fund posts → Donor
  Visibility → **CBPF**). Move the copy there only after that confirmation.
- After copying through the connector, **re-add the guides in Chrome** — connector copies drop them (§4).

**If no template fits:** this is a new type of content — follow §7 first. Build from the closest existing
design (copy it first). When the post is final, the decision to turn it into a template is Javier’s (§7);
only when he says yes: copy the final design into
`Templates_DONT_CHANGE/<type folder>`, name it `Generic_<Type>`, make the country pill and credits generic
(“Country”, “Photo: Org/Photographer”), add the rules to page 1 speaker notes, and check guides, transitions
and timing in Chrome.

**Uploading photos:** `create-upload-url` → POST the raw bytes (`Content-Type: application/octet-stream`)
→ use the returned `mediaId` with `update_fill`. **Swapping a photo resets its crop** — re-apply the crop
afterwards.

**Saving:** when the person asks for an edit, **apply it and save (commit) in the same step**, then show
the result. Don’t ask “save?” separately. Connector edits are invisible in Canva until saved, and an open
edit expires after about an hour and is lost. Never leave an edit open while waiting for feedback.

**Previews:** the connector returns low-res page previews after each edit. Look at them every time; check
precise alignment by measuring the preview pixels, not by eye.

## 4. Steps done in Chrome (connector can’t)

Full click-by-click instructions: `references/chrome-only-steps.md`. Summary — every carousel needs:

- **Guides:** 12 columns, 24 px gap, 72 px margin; 1 row with 72 px margin.
- **Video-ready:** Dissolve **0.5 s** between all pages, **4 s** per page, **no animations** on any page
  or element (carousels are sometimes posted as video).
- **Inter** at the right weights (§5); photo credits stay in Roboto Condensed.
- **Animation panel trap:** the Animate panel covers the first page thumbnails. Close the panel before
  clicking a thumbnail, or the click lands on “Apply to all pages” and animates every page.

Before Chrome: close any open connector edit on that design. Never type with the canvas focused
(Canva’s “T” shortcut creates a text box).

## 5. Design rules (BDU, Oct 2026)

**Vertical spacing** (Javier, 19 Oct 2026) — measured on the visible letters, not the text boxes:
- Two text guides at **140** and **1271** (added by hand in the template). Headlines and supporting text
  stay between them; the 72 px margins are the hard limit for credits, logo and footnotes only.
- Top-aligned slides: headline capitals start on 140. Bottom-aligned slides: the last line's baseline sits on 1271.
- **56 px** from a headline baseline to the top of the text below (or text baseline to headline capitals);
  **40 px** from the blue kicker to the cover headline.
- Photo credit baseline on the **1368** margin (credit box top 1350).
- Inter offsets for placing boxes: Black 96 lh 1.0 → capitals start 21 px below the box top, baseline 24 px
  above the box bottom (104: 23 / 26). 40 px lh 1.35 → letters start 8 px down, baseline 10 px up.
  Roboto Condensed 20 → baseline 6 px above the box bottom. Check by exporting PNG and measuring.

**Grid** (1080×1440): 72 px margins all round; 12 columns of 56 px with 24 px gutters — column starts
72, 152, 232 … 952; a span of *n* columns is `80n − 24` px wide. Every position and gap on a **4 px scale**.
Place elements by what is *visible*: the kicker’s blue background sits inside a padded frame (in the
template: kicker text box at left 80, so the blue edge lands on the 72 px margin).

**Type — Inter, credits in Roboto Condensed.** Rounded sizes only.

| Role | Size | Font / weight | Line height |
|---|---|---|---|
| Cover headline | 104 | Inter Black, capitals | 1.0 |
| Statement headline (inside slides) | 96 | Inter Black, capitals | 1.0 |
| Kicker (line above the cover headline) | 32 | Inter Bold, capitals, white on UN blue `#009EDB` | 1.2 |
| Supporting text | 40 | Inter SemiBold | 1.35 |
| Photo credit (every slide with a photo) | 20 | Roboto Condensed Regular, not italic | 1.35 |

- Big capitals set at line height 1.0 (1.2 looks loose at this size).
- **Key words highlighted** (when wanted): white text on a UN blue box, never blue text on a photo
  (not enough contrast). Partial highlights need their own text box over a `#009EDB` rectangle
  (`insert_shape`, corner 4) — the connector can’t highlight part of a text box.
- **Left-aligned** text by default, credits included. Only the closing call to action may be centred.
- **Credits** at top 1340, left 72 (on the bottom margin). Text ends **≥ 48 px** above the credit.
- **No orphans.** Fix by choosing another column span for the text box — never by changing the copy.

**Photos and text placement**
- Put text over the most uniform part of the photo (sky, a wall, the ground). Reframe the photo (crop)
  so faces and busy areas sit away from the text.
- **Always a gradient behind text, subtle by default.** Over people or busy colour use the **strong**
  gradient; over sky/wall/ground the **subtle** one. Files: `assets/text_gradient_strong_1080x900.png`
  (80 %) and `assets/text_gradient_subtle_1080x900.png` (45 %). Upload them to Canva once per design
  (`create-upload-url`). Insert at top 540, 1080×900 for bottom text (flip for top
  text), then bring the text and credit layers to the front.
- Keep the gradient behind the OCHA logo subtle (≈30 % opacity).
- **Always ask the designer about legibility** (Javier, 19 Oct 2026). After building or changing a slide,
  show the preview and ask, per slide: *“Is the text easy to read here, or should the dark gradient be
  darker or lighter?”* Don’t decide it alone from the thumbnail — previews are small and photos vary.
  Adjust only the slides they name (gradient opacity, or switch strong ↔ subtle), save, and show again.
- Resizing a gradient element crops it instead of squashing it — use `crop_media` to rescale.

## 6. Hand-off

- Share the **Canva link** of the post (not the template). Mention anything flagged for the requester
  (credits, fund names, copy questions).
- Update the job `README.md` (links) and `CLAUDE.md` (decisions, open points).
- If the post was a new type of content, make sure the briefing for Javier has gone out (§7).
- **Clean up the job folder once the design is approved** (Javier, 15 Oct 2026). Keep only what the job
  really needs later: `README.md`, `CLAUDE.md`, `info/photos_and_credits.md`, the original and enhanced
  photos actually used in the final design, and any script or asset the job made. Remove the rest —
  draft previews, mockup previews, photo-search contact sheets, rejected photo downloads, test files.
  List what will be removed and ask before deleting; move to `archive/` instead if the person prefers.
  The Canva design itself holds the final; no export is kept.

## 7. New types of content — tell the person, brief Javier

This skill is built from **carousels** (template `Generic_Carousel`). Requests for anything else — a
single static card, a quote card, a stat/data card, a story or reel cover, a banner, a different size or
platform, a new layout — are **a new type of content**.

1. **Say so at the start**, before building:
   *“This is a new type of content for the BDU social media skill — there’s no template for it yet. I can
   still make it, using the carousel rules as the reference (grid, Inter, spacing, gradients, credits). Please
   check with Javi (Javier Cueto, cuetoj@un.org) whether it’s worth adding to the skills — I’ll prepare a
   short briefing you can send him.”*
2. **Still help.** Use the carousel rules as the starting point and adapt only what the format forces
   (size, number of pages, text amount). Note every decision that differs from the carousel rules.
3. **Write the briefing for Javi in the chat** (ready to paste into an email or Teams; don’t save it as a
   file), once the content is clear — and update it when the post is final:

   > **Subject:** New social media content type for the BDU skill — <type>
   >
   > Hi Javi,
   >
   > I made a <type> for <office / requester> with Claude. It isn’t covered by the BDU social media skill
   > or a template yet. Is it worth adding?
   >
   > - **What it is:** <one line, e.g. single static card announcing a CBPF allocation>
   > - **Platforms and size:** <e.g. Instagram + LinkedIn, 1080×1350>
   > - **How often we expect to make it:** <one-off / monthly / every allocation …>
   > - **Based on:** <template or design it started from>
   > - **What differs from the carousel rules:** <list: size, grid changes, type sizes, layout, elements>
   > - **Canva link:** <link to the post>
   > - **Open questions:** <anything we weren’t sure about>
   >
   > If yes, the post could become a template (e.g. `Generic_<Type>` in Templates_DONT_CHANGE) and the
   > skill could learn its rules.

4. **Don’t create a template or change this skill** unless Javier says yes. If he does, the template
   steps are in §3.

---

## Project Owner

Javier Cueto, Head of Brand and Design Unit

## Maintained by

**OCHA Brand and Design Unit (BDU)**
- Team: ochavisual@un.org
- Focal point: Javier Cueto (cuetoj@un.org)
