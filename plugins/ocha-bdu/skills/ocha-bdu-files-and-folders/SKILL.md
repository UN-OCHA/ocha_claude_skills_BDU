---
name: ocha-bdu-files-and-folders
description: >
  The OCHA BDU standard for organising job folders, naming files and choosing export formats. Applies to every
  BDU job: videos, maps, charts, infographics, reports, logo packages, social posts,
  presentations. Use whenever saving, exporting or delivering anything, creating or
  tidying a job folder, naming a file, handling draft versions, archiving old versions,
  or finishing a job. Trigger on "save this", "export", "where should this go", "name
  the file", "folder structure", "organise the folder", "clean up the folder", "final
  version", "archive", "we're done", "PNG or JPEG", "which format", "file too big", "re-export", "update the file", "review round", "before and after", "page to comment on",
  "pick up this job", "take over this job", "hand this over", "where does this stand", "make available offline", "online only", "file is empty", "README", "CLAUDE.md", "project notes",
  "document this", "editable .ai", "Illustrator file", "export to Illustrator", "send it to the
  designer", "they want to edit it". Also use when starting a job or coming back to one: every job keeps a
  README.md and a CLAUDE.md. The other OCHA skills point here for every file and
  folder rule.
---

# OCHA BDU files and folders

One standard for every BDU job. Other skills add what is specific to their work — the
video skill’s thumbnail, the logo skill’s artboards — but they follow these rules.

---

## 1. Where a job lives

`Projects/<year>/<office>/<job_name>/`

- `<office>` is the requesting unit: `CO/SDN`, `FOD/PFB`, `HSD/ISS`, `OASG`, `OUSG`, `CRD`,
  `Partners/WFP`, or an event such as `UNGA81`.
- `<job_name>` is short and lowercase, with words joined by `_`: `humanifesto`,
  `hl_dashboard`.
- Save everything into the job folder. Never into a temporary folder, where it gets lost.

### Files from the BDU Dropbox

> **OCHA BDU internal content.** These folders are in the OCHA BDU Dropbox, which only the OCHA Brand and Design Unit can open. For more information, contact ochavisual@un.org.

The OCHA skills point to shared folders in the BDU Dropbox: logos, icons, geodata, the sound library,
ready-made maps. Dropbox often keeps folders online only, so a file can look present but be empty or fail
to open.

- **Before a job that needs a Dropbox folder** (one of those, or the job folder itself), tell the user
  which folder and ask them to right-click it and choose **Make available offline**. Only that folder,
  not the whole Dropbox: some are large.
- **On a Mac, check first when you can:** online-only files show as `dataless` in `ls -lO`, or (older
  Dropbox setups) as **0 bytes** with a `com.dropbox.placeholder` attribute in `xattr -l`. No real
  design file is 0 bytes.
- **If a file reads as empty, won’t open, or a folder looks incomplete,** stop and ask for the same thing.
  Never work around it with a copy from elsewhere or a download from the web.

## 2. Inside every job: the same folders

```
<job_name>/
  source/    what we received: footage, data, documents, with their original names
  info/      brief, approvals, feedback, transcripts, notes
  assets/    what a designer places by hand: logos, fonts, images, cleaned data, voice
             recordings (and .indd / .aep masters)
  tools/     what produces the finals: scripts, HTML templates and the files they link
             to, film pages, previews and intermediate renders
  export/    the finals only, one file per deliverable
  archive/   optional: older versions worth keeping
  <name>.ai  the editable master of a design job sits at the TOP level, not in assets/ or export/
  README.md  for people: what it is, who asked for it, where the finals are, how to edit them
  CLAUDE.md  for Claude: decisions, sources, how to rebuild, what is still open
  .claude/   throwaway only (a hidden folder): scratch/ for tests and previews, emptied
             when the job closes, plus the app’s own settings
```

- Create only the folders the job needs. Nothing else at the top level except the editable master.
- **Editable master at the top level** (Javier, 11 Nov 2026): a design job’s `.ai` (one file, one
  artboard per page or slide) sits next to `README.md`, named like the finals without page number,
  date or pixel size: `ebola_funding_carousel_1080x1440.ai`.
- Recurring outputs (a weekly email, a monthly update) get a dated folder inside
  `export/`: `export/2026-09-14_priorities/`.

### Notes for next time: `README.md` and `CLAUDE.md`

Every job has a `README.md` and a `CLAUDE.md`, both at the top level. They are
what the next session, a colleague or another computer starts from. A conversation stays on one computer, and over a
long session its early parts get condensed; the notes keep the details.

- **`README.md`, for people:** what it is, who asked for it, where the finals are, how to
  edit them.
- **`CLAUDE.md`, for Claude:** what was decided and why, the cleared wording and where
  the figures came from, how to rebuild each final, what is still open, and who is working on
  it now. Handoffs and session summaries go in it too, not in separate files. Keep ONE
  `CLAUDE.md`.
- **Nothing worth keeping goes in `.claude/`.** It is hidden in Finder: copying a folder’s
  contents leaves it behind, and sharing the folder sends it along unseen. Only throwaway work
  (test renders, previews, logs) goes there, in `.claude/scratch/`. `info/` is for what people
  gave you (brief, approvals, feedback), not Claude’s own notes.
- **An older job with `CLAUDE.md` or notes inside `.claude/`:** when you work on it, move
  `CLAUDE.md` to the top level, fold any notes into it, and say so in one line.
- **`CLAUDE.md` travels with the folder.** Before a job folder is shared outside BDU (with a
  client, a partner, another agency), read it and remove anything they shouldn’t see:
  internal discussion, people’s names, rejected wording.

- **Create both when the job starts,** without being asked.
- **Update them before the end of every working session,** not only when the job closes.
  A session can end at any point; the notes should never be behind the work.
- **Picking up an existing job:** read both before changing anything, then say in plain
  words where it stands. Open the job folder itself in Claude Code and its `CLAUDE.md` is
  read automatically at the start of every session.
- Write down decisions, not a diary. Use full dates, never “yesterday” or “last week”.
- Never put a password or token in them: job folders are shared.

### Ready for someone else to take over

Any BDU colleague must be able to open a job folder, start Claude there and carry on, with
nothing from the first person’s computer or conversation. Check this every time the notes are
updated:

- **The job is in the shared BDU Dropbox**, under `Projects/<year>/…`, never on a Desktop, in
  Downloads or in a private folder. A colleague can only connect what they can open.
- **Tools are named, not pointed to.** When a final was made with a skill’s script, the notes
  name the skill and the step (“`ocha-bdu-mockups`, the 85×200 cm roll-up template”), never a path
  into one person’s skill folder: installed skills sit in a different place on every computer.
- **Tools made for this job live in the job, where people can see them:** scripts, templates
  and their linked files go in `tools/`, never only in `.claude/`.
  `.claude/` is hidden in Finder and its `scratch/` is emptied when the job closes, so a tool
  kept there is invisible to a colleague and gets deleted.
- **The notes say how to run each tool:** the one command, run from the job folder, and what it
  needs installed (Illustrator, ffmpeg, the QuickVid engine).
- **Sign-ins are listed, never stored.** Name every service the job depends on (ElevenLabs,
  Flippermusic, MediaValet, Datawrapper…) and say whether to use your own account or ask BDU.
- **Nothing lives only in the conversation.** If the next person would have to ask “why is it
  like this?”, the answer belongs in `CLAUDE.md`.

### Generated work: the tools live in `tools/`, only the result goes to `export/`

When a final is produced by something else — an HTML page printed to PDF, an SVG rendered
to PNG, a script that draws a chart — everything doing the producing is **build
material**, not a final:

- HTML and CSS templates, the logos and images they link to, scripts and intermediate
  renders all live in `tools/`, at the top of the job where a colleague will find them.
  Hand-made masters and source material the tools read stay in `assets/`.
- Build from `tools/` and write **only the final file** into `export/`. Never render from
  inside `export/`: a template there pulls its linked files in beside it.
- A template that links to local files by relative path keeps those files next to it,
  **inside `tools/`**.
- The README lists each tool with the one command that runs it, from the job folder.
- **Older jobs** may keep their tools in `assets/build/` or `assets/scripts/`. Leave them
  there: their notes and commands point to that place, and moving them breaks both.
- If a web page *is* the deliverable (something that will be hosted), make it
  self-contained, with images and styles embedded, so it goes into `export/` as one file
  with no folder beside it.

The test: if you would have to explain to the requester why a file is in `export/`, it
doesn’t belong there.

## 3. Naming files

For every file BDU produces:

`<subject>_<detail>_<format>_<version>_<language>.<ext>`

Use only the parts that apply, always in that order.

| Rule | Example |
|---|---|
| All lowercase, words joined by `_`. No spaces, accents or brackets. | `humanitarian_snapshot` |
| Countries as three-letter ISO codes, from `ocha-bdu-country-names` | `sdn`, `ukr`, `pse` |
| Format as page size or pixels | `a4`, `1080x1920` |
| **No dates in final file names** (Javier, 11 Nov 2026). A date goes in only for a dated folder of recurring outputs (`export/2026-09-14_priorities/`), as year-month-day | — |
| Language last, two letters — **only when the job comes in more than one language** | `_en`, `_fr`, `_es`, `_ar`, `_ru`, `_zh` |
| Never `final`, `new`, `latest` or `copy` | — |

Country codes rather than names, because names change — Türkiye, Occupied Palestinian
Territory — and codes don’t. OCHA geodata and location maps already use them.

The year-month-day format is for file names only. Dates written in text follow
`ocha-bdu-editorial-style`.

A job produced in a single language gets no language code at all. Add codes only when the
same deliverable exists in two or more languages, and then give every language its code.

**Style names follow the same logic** (Javier, 23 Nov 2026). While a job has several styles
side by side (a flat and a cut-out version, say), name each by its style: `_flat`, `_cutout`.
Once one is chosen and it is the only version in `export/`, drop the style name from the
final. The versions that weren’t chosen keep theirs in `archive/`, so the two can’t be mixed up.

Examples:

- `sdn_humanitarian_snapshot_a4.pdf` — one language, no code, no date
- `ukr_asg_security_council_1080x1920.mp4` — one language, no code
- `gho2026_funding_by_sector_chart_en.svg` and `gho2026_funding_by_sector_chart_fr.svg` —
  the same chart in two languages, so both carry a code

### Leave these names alone

- **Anything in `source/`.** Renaming a file breaks its link to the email or message it
  came in with.
- **Names set by an outside system:** Humanitarian Icons (`Water-source.svg`),
  geodatabase layers (`sdn_polbndl_adm1_1m_ocha`), GitHub repositories (`<name>_BDU`) and
  their internal layout, plugin release files.
- **Published brand assets with established names**, such as the OCHA logo package.
- **Finished projects.** Apply this standard to new work; don’t rename old jobs.

## 4. Versions and re-exports

**Re-export over the same file by default.** When a file is updated, export it with exactly
the same name to the same place, so the new file replaces the old one. A Dropbox link
belongs to the file: replacing it in place keeps every link already shared working, and the
link now shows the new content. Saving under a new name creates a new file, and the old
link keeps showing the old one. Let the export write over the file — don’t delete the old
file first and then save, or Dropbox can treat it as a new file and the link breaks.

**When a script writes over the file, on a Mac, copy with `cp -X`, never a plain `cp`.**
A plain `cp` onto an existing file removes the hidden tag Dropbox uses to recognise it.
Dropbox then sometimes treats it as a new file, and the shared link stops working with no
warning. This happened 3 times in 10 renders of one film. `cp -X` keeps the tag. In Python,
open the existing file and write the new bytes into it. Use `-X` on archive copies too, so
the copy doesn’t carry the original’s tag.

- **Make an additional version only when one is needed** — the user asks to keep the
  previous one, or two options have to exist side by side. Then number them `_v01`, `_v02`,
  `_v03`: two digits, so they sort in order.
- **When delivered:** the final carries no version number and is the only copy in
  `export/`. If drafts were numbered, `sdn_humanitarian_snapshot_a4_v03.pdf` becomes
  `sdn_humanitarian_snapshot_a4.pdf`, so nobody has to guess which one is final.
- **Older versions:** ask the user whether to delete them or move them to `archive/`.
  Never decide on your own.
- **A job that reopens:** replace the final in place. If the previous final is worth
  keeping, ask, then **copy** it into `archive/` first — never move it. A moved file takes
  its Dropbox link with it, so the shared link would keep showing the old version.
- **After replacing a file that has been shared,** check Dropbox’s version history shows a
  new version of the same file rather than a new file: the file id must be unchanged. The
  file on the Mac staying the same proves nothing; only Dropbox’s id does.

### Review rounds: offer a page people can comment on

For any product with changes to approve (a carousel, an infographic, a map, a report, a video), offer a
**private review page** that shows the proposal: each slide, page or frame, with the current version
next to it when there is one. People comment straight on the page.

- Build the proposal on a **working copy**, never on the live file or design. Change the live version
  only once the comments are settled, all in one go.
- Afterwards, delete the working copy yourself (a Canva copy goes to the Bin through Chrome:
  File → Move to Bin). Never ask the person to clean it up.
- Videos: the review tool in `ocha-bdu-video` does the same job with comments on the timeline.

### Shared Word files on OneDrive or SharePoint (review documents)

A Word file that several people comment on is co-authored in the cloud. Changing the copy on
the Mac (swapping images, marking comments resolved) works only until someone who has it open
saves again: their Word writes its own version back over yours, minutes later, with no warning.
On the Ebola carousel (Nov 2026) this undid an update twice while every check right after
writing passed.

1. **Before editing,** check for Word’s lock file next to the document (`~$` + the name). If it
   is there, ask the person to close the file first. Other people’s open copies can’t be seen
   from the Mac: say so.
2. **Edit in place,** keeping everything else: swap the image data inside the file, never
   rebuild the document, so comments, replies and resolved marks survive. Write into the
   existing file (don’t delete and recreate it), so OneDrive keeps it as the same file.
3. **After editing,** wait for OneDrive to sync and check again a few minutes later, not only
   right after writing. If the change was overwritten, say so; never report it as updated.
4. **While a review is active** (several people commenting), don’t replace content from
   outside Word. Hand the person the new image to put in with Word’s own **Change Picture**
   (right-click the image → Change Picture → From a File), which goes through co-authoring
   and can’t be overwritten.

## 5. Export formats

Aim for the best quality at the smallest file size.

| The graphic | Export as |
|---|---|
| Can stay vector, and the destination accepts it | **SVG** for web and Illustrator, **PDF** for print |
| Flat colour, text, icons, charts, maps — no photos or raster effects | **PNG** |
| Needs a transparent background | **PNG** — JPEG can’t do transparency |
| Photos, grain, textures, blur, soft shadows | **JPEG**, quality 80–85 |
| A photo with crisp text on top | JPEG at higher quality, or PNG if that is lighter — test both, deliver one |

- **One raster file per image.** Never deliver a PNG and a JPEG of the same thing: deliver the lighter
  one at the highest quality. Pick the format from the table. When it’s a close call, test both in
  `.claude/scratch/`, keep the lighter one that looks identical at full size, and delete the test. Only the
  winner goes into `export/`.
- **Don’t rasterise what can stay vector.** PNG and JPEG are for destinations that need an
  image: social media, slides, email, some web tools.
- **Flat graphics can often go smaller** with a reduced colour palette (8-bit PNG) and no
  visible change. Check smooth gradients afterwards: a reduced palette can make them band.
- **JPEG above quality 90 buys almost nothing** but makes the file much bigger.
- **PDF too heavy** (a Canva export is often 100 MB+)? Compress it with the `ocha-bdu-utilities` PDF tool. It
  keeps full resolution and the original colours.
- **Raster finals at 2x** (Javier, 11 Nov 2026): twice the size the destination shows, so they stay sharp
  on high-density screens (a 1080×1440 post exports as 2160×2880). The file name carries the real pixel
  size. Make the photos inside at 2x too, from the original, not an upscaled working copy.

### Always deliver an editable version

Someone without Claude must be able to change the work. So every final goes out with a version a
designer can open and edit in ordinary software: for a design job, one master at the top of the job
folder (§2); otherwise next to the final in `export/`, under the same name.
Make it every time, without being asked: the person who would ask often forgets.

| Final | Editable version |
|---|---|
| Poster, chart, map, infographic, social graphic, short document made in code | **`.ai`**: see below |
| Long report | **`.indd`**: build it in InDesign from a template from the start, so the `.indd` is the master. There is no export from HTML to InDesign: turning an HTML report into an `.indd` is a rebuild, so say so |
| Slides | **`.pptx`** |
| The data behind a chart | **`.xlsx`** |
| Video | No true equivalent: a clean version without burned-in text, plus the subtitle files |
| Animation built in code | No tested equivalent yet: the video and stills. Say plainly that changing it needs the code |
| Website or web app | The source files are the editable version |

- **Check it before calling it done.** Open what was made and compare it with the final. A file that
  only looks editable (text turned to outlines, a single flattened image) is a failure, not a deliverable.
- **If it can't be made,** deliver the final anyway and say what is missing and why, for example when
  the software isn't on this computer. Never skip it silently, and never hold up the final for it.
- **On Windows,** the `.ai` export below can't run today: it drives Illustrator with a Mac-only script,
  and so does the scripted route into InDesign. Say so, and ask a colleague on a Mac to make the file.
- The README says where the editable version is and what opens it. It can be left out on request, case by case.

### Editable Illustrator file (.ai)

Anything built as a page (HTML one-pager, infographic, poster, slide) or as an SVG (chart, map)
can also go out as an **editable .ai**: the same artwork, with live text and named layers.

```bash
python3 <skill>/scripts/export_ai/export_ai.py page.html -o export/<name>.ai
python3 <skill>/scripts/export_ai/export_ai.py chart.svg -o export/<name>.ai
```

`<skill>` is the folder this file is in.

**Several pages or slides → one .ai, one artboard each.** Export each page into a temporary folder,
then merge them into the master at the top of the job folder (layers are prefixed with the page number,
live text stays live):

```bash
python3 <skill>/scripts/export_ai/merge_ai.py /tmp/x/01.ai /tmp/x/02.ai … -o <job>/<name>.ai
```

**What you get:** the artwork exactly as Chrome draws it. The text is live, one text object per
block (heading, paragraph, label), in the real fonts, sizes, colours and spacing, with bold
words kept and each block aligned as on the page (left, right or centred), so it grows the right
way when edited. Layers come from tags in the source:

| Attribute | Put it on | What it does |
|---|---|---|
| `data-ai-layer="Globes"` | any element | Artwork inside it goes to that layer. When tags nest, the smallest area wins. |
| `data-ai-name="3 Afghanistan"` | any element | Groups its artwork under that name, and names the text inside it (“3 Afghanistan - ask”). |
| `data-ai-text-layer="Labels"` | any element | Text inside it goes to that layer. Default: Text. |

Untagged work still exports, into Text, Graphics and Background (anything covering the page).
The tags don’t change how the page looks, so add them to the build template once.

**Rules**
- **Never open the PDF in Illustrator and save it as .ai.** That gives one text box per letter.
  Use the script.
- **Read the report it prints.** “Check” compares every letter with the PDF: expect a median
  offset around 0.1pt and no solid pixel differences. Anything listed as “NOT converted” stays as
  imported letters in the layer “Text (not converted)”. Nothing is ever dropped.
- **The pixel comparison needs Pillow and numpy.** Without them the report says “NOT CHECKED” and
  ends with a warning: the letter check alone can’t see text hidden under another layer. Offer to
  install them (`python3 -m pip install --user Pillow numpy`, a minute, no password) and run the
  export again. Never treat a report without the pixel comparison as a pass.
- Close the `.ai` in Illustrator before exporting over it. It needs macOS, Chrome, Illustrator
  (2024 or later) and the fonts installed, so it can’t run in a Cowork cloud session.
- One page per export: set `@page { size: <width>px <height>px; margin: 0 }` in the page, or
  it may print as two pages and stop.
- **Build the page so it converts** (lessons from the Ebola carousel, 11 Nov 2026):
  - **Fonts installed locally, static TTF** (in `/Library/Fonts/<Family>/`), and the page uses them by
    name. Never load them from Google Fonts: the print starts before they arrive and the text goes
    missing. OTF (CFF) fonts print as Type 3 and none of their text converts.
  - **Inter:** turn off contextual alternates (`font-feature-settings: "calt" 0`), or “(” and “*”
    print as alternate glyphs and those lines stay unconverted.
  - **No `text-shadow`** (the text prints twice), **no outline or box-shadow borders** (use `border`),
    and **no CSS gradient over a photo**: bake the gradient into the photo, or the stacking breaks.
  - **Backgrounds in document order,** each in its own tagged `div`, never pushed back with a negative
    `z-index` (the tags are then ignored and the background lands above the text).
  - **Keep separate text blocks at least one font size apart** on a line (e.g. two table columns):
    closer ones merge into one fragment and don’t convert.
- **The .ai looks like the final, and is organised by meaning** (Javier, 25 Nov 2026):
  - Whatever isn’t vector (textures, filters and effects, torn edges, shadows, photos) goes in as images (PNG or
    JPEG), **one image per piece**, never one flattened sheet, so each piece can still be moved.
  - **Layers follow meaning, not type:** a background layer, a heading layer, then one layer per section or part of
    the design (for example “6 UN entities”, “Funding released”, “CERF example”). Each holds that part’s live text,
    vector shapes and images. No groups.
  - Tag each element itself with its layer (`data-ai-layer`, and `data-ai-text-layer` for text), not only a wrapper:
    the exporter puts an object in the smallest tagged box that holds it, and same-sized wrappers tie. The DRF
    Platform graphic (`ocha-bdu-graphic-styles`, Newsprint) has a script that does all of this
    (`templates/newsprint/make_ai_source.py`).
- **Check the merged file:** export each artboard from Illustrator back to PNG and compare it with the
  finals. Only anti-aliasing should differ.
- **Known limits.** CSS gradients arrive as pattern fills. Underlines and highlights are separate
  shapes, so move them with the text. Text at angles other than 0, 90, 180 or 270 degrees stays as
  imported letters. Large headings may sit up to about 1pt off, because Illustrator kerns slightly
  differently. Ligatures such as “ffi” may be set as separate letters.
- The PDF stays the approved deliverable. The `.ai` is the editable copy of it.

## 6. Closing a job

When the work is delivered, go through this before calling it done:

1. `export/` holds only the finals, named to §3, in the one format §5 calls for (never a PNG and a JPEG of the same image), with no version numbers. No templates,
   asset folders, scripts or intermediate renders (see “Generated work” in §2).
2. The top level holds only `source/`, `info/`, `assets/`, `tools/`, `export/`, `archive/`,
   `.claude/`, `README.md`, `CLAUDE.md` and the editable master (`<name>.ai`). Stray tooling folders such as `build/` move into `tools/`;
   `.claude/` holds nothing worth keeping.
3. Older versions: ask whether to delete them or move them to `archive/`.
4. Empty `.claude/scratch/`. Delete what nobody will open again: tests, previews, logs,
   temporary renders, one-off scripts. Tools needed to rebuild the work stay, in `tools/`.
5. Delete your own throwaway files without asking. Ask before deleting anything someone
   else made, or anything you’re not sure about.
6. If you moved build files or rebuilt anything, run the build once more and confirm it
   still writes the final into `export/`. Then compare the new file with the previous
   final: a browser or tool update can change the output even when nothing else did.
7. Update `README.md` and `CLAUDE.md` so they describe the job as it now stands: the
   folders, what was decided, and anything left open. If the folder will be shared outside
   BDU, read `CLAUDE.md` and remove anything the recipient shouldn’t see.
8. **Look before calling it done.** List the job folder and `export/`, and check what is
   actually there against this list. Having followed the steps is not the same as the
   folder being right.

---

## Project Owner

Javier Cueto, Head of Brand and Design Unit

## Maintained by

**OCHA Brand and Design Unit (BDU)**
- Team: ochavisual@un.org
- Focal point: Javier Cueto (cuetoj@un.org)

<!-- bdu-suggest-change:start -->
**Suggesting a change to this skill.** If the person corrects you or states a rule that would apply to other jobs too, or you find this skill is wrong or missing something, say so once, at the end of your reply. Don’t do this for changes that only concern the current job, and don’t edit the skill yourself, because the next update would overwrite it. Leave out anything confidential from the job. Say:

> This could be worth adding to the OCHA BDU skills. If you agree, copy this message and send it to Javi:
> **Skill:** ocha-bdu-files-and-folders
> **Proposed rule:** [the rule, in one or two sentences]
> **Why:** [what happened, with one example]
<!-- bdu-suggest-change:end -->
