---
name: ocha-files-and-folders
description: >
  The OCHA BDU standard for organising job folders, naming files and choosing export formats. Applies to every
  BDU job: videos, maps, charts, infographics, reports, logo packages, social posts,
  presentations. Use whenever saving, exporting or delivering anything, creating or
  tidying a job folder, naming a file, handling draft versions, archiving old versions,
  or finishing a job. Trigger on "save this", "export", "where should this go", "name
  the file", "folder structure", "organise the folder", "clean up the folder", "final
  version", "archive", "we're done", "PNG or JPEG", "which format", "file too big", "re-export", "update the file",
  "pick up this job", "where does this stand", "make available offline", "online only", "file is empty", "README", "CLAUDE.md", "project notes",
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

The OCHA skills point to shared folders in the BDU Dropbox: logos, icons, geodata, the sound library,
ready-made maps. Dropbox often keeps folders online only, so a file can look present but be empty or fail
to open.

- **Before a job that needs a Dropbox folder** (one of those, or the job folder itself), tell the user
  which folder and ask them to right-click it and choose **Make available offline**. Only that folder,
  not the whole Dropbox: some are large.
- **On a Mac, check first when you can:** online-only files show as `dataless` in `ls -lO`.
- **If a file reads as empty, won’t open, or a folder looks incomplete,** stop and ask for the same thing.
  Never work around it with a copy from elsewhere or a download from the web.

## 2. Inside every job: the same folders

```
<job_name>/
  source/    what we received: footage, data, documents, with their original names
  info/      brief, approvals, feedback, transcripts, notes
  assets/    what is needed to rebuild the work: .ai / .indd / .aep masters, logos,
             fonts, cleaned data, scripts
  export/    the finals only, one file per deliverable
  archive/   optional: older versions worth keeping
  README.md  for people: what it is, who asked for it, where the finals are, how to edit them
  CLAUDE.md  for Claude: decisions, sources, how to rebuild, what is still open
```

- Create only the folders the job needs. Nothing else at the top level.
- Recurring outputs (a weekly email, a monthly update) get a dated folder inside
  `export/`: `export/2026-09-14_priorities/`.

### Notes for next time: `README.md` and `CLAUDE.md`

Every job folder has two notes files at the top level. They are what the next session, a
colleague or another computer starts from. A conversation stays on one computer, and over a
long session its early parts get condensed; the notes keep the details.

- **`README.md`, for people:** what it is, who asked for it, where the finals are, how to
  edit them.
- **`CLAUDE.md`, for Claude:** what was decided and why, the cleared wording and where the
  figures came from, how to rebuild each final, what is still open, and who is working on
  it now.

- **Create both when the job starts,** without being asked.
- **Update them before the end of every working session,** not only when the job closes.
  A session can end at any point; the notes should never be behind the work.
- **Picking up an existing job:** read both before changing anything, then say in plain
  words where it stands. Open the job folder itself in Claude Code and its `CLAUDE.md` is
  read automatically at the start of every session.
- Write down decisions, not a diary. Use full dates, never “yesterday” or “last week”.
- Never put a password or token in them: job folders are shared.

### Generated work: build files stay in `assets/`, only the result goes to `export/`

When a final is produced by something else — an HTML page printed to PDF, an SVG rendered
to PNG, a script that draws a chart — everything doing the producing is **build
material**, not a final:

- HTML and CSS templates, the logos and images they link to, scripts, data and
  intermediate renders all live in `assets/`. A subfolder such as `assets/build/` is fine.
- Build from `assets/` and write **only the final file** into `export/`. Never render from
  inside `export/`: a template there pulls its linked files in beside it.
- A template that links to local files by relative path keeps those files next to it,
  **inside `assets/`**.
- If a web page *is* the deliverable (something that will be hosted), make it
  self-contained, with images and styles embedded, so it goes into `export/` as one file
  with no folder beside it.

The test: if you would have to explain to the requester why a file is in `export/`, it
doesn’t belong there.

## 3. Naming files

For every file BDU produces:

`<subject>_<detail>_<format>_<date or version>_<language>.<ext>`

Use only the parts that apply, always in that order.

| Rule | Example |
|---|---|
| All lowercase, words joined by `_`. No spaces, accents or brackets. | `humanitarian_snapshot` |
| Countries as three-letter ISO codes | `sdn`, `ukr`, `pse` |
| Format as page size or pixels | `a4`, `1080x1920` |
| Dates as year-month-day | `2026-09-14` |
| Language last, two letters — **only when the job comes in more than one language** | `_en`, `_fr`, `_es`, `_ar`, `_ru`, `_zh` |
| Never `final`, `new`, `latest` or `copy` | — |

Country codes rather than names, because names change — Türkiye, Occupied Palestinian
Territory — and codes don’t. OCHA geodata and location maps already use them.

The year-month-day format is for file names only. Dates written in text follow
`ocha-editorial-style`.

A job produced in a single language gets no language code at all. Add codes only when the
same deliverable exists in two or more languages, and then give every language its code.

Examples:

- `sdn_humanitarian_snapshot_a4_2026-09-14.pdf` — one language, no code
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

## 5. Export formats

Aim for the best quality at the smallest file size.

| The graphic | Export as |
|---|---|
| Can stay vector, and the destination accepts it | **SVG** for web and Illustrator, **PDF** for print |
| Flat colour, text, icons, charts, maps — no photos or raster effects | **PNG** |
| Needs a transparent background | **PNG** — JPEG can’t do transparency |
| Photos, grain, textures, blur, soft shadows | **JPEG**, quality 80–85 |
| A photo with crisp text on top | JPEG at higher quality, or PNG if that is lighter — test both, deliver one |
| Someone will edit it in Illustrator (a designer, a partner, a country office) | An **editable .ai** as well, next to the PDF or SVG — see below |

- **One raster file per image.** Never deliver a PNG and a JPEG of the same thing: deliver the lighter
  one at the highest quality. Pick the format from the table. When it’s a close call, test both in
  `assets/`, keep the lighter one that looks identical at full size, and delete the test. Only the
  winner goes into `export/`.
- **Don’t rasterise what can stay vector.** PNG and JPEG are for destinations that need an
  image: social media, slides, email, some web tools.
- **Flat graphics can often go smaller** with a reduced colour palette (8-bit PNG) and no
  visible change. Check smooth gradients afterwards: a reduced palette can make them band.
- **JPEG above quality 90 buys almost nothing** but makes the file much bigger.
- **Export at the size the destination shows it** (twice that only when a high-density
  version is asked for). An oversized image is the most common reason a file is heavy.

### Editable Illustrator file (.ai)

Anything built as a page (HTML one-pager, infographic, poster, slide) or as an SVG (chart, map)
can also go out as an **editable .ai**: the same artwork, with live text and named layers.

```bash
python3 <skill>/scripts/export_ai/export_ai.py page.html -o export/<name>.ai
python3 <skill>/scripts/export_ai/export_ai.py chart.svg -o export/<name>.ai
```

`<skill>` is the folder this file is in. Give the `.ai` the same name as the PDF or SVG it goes
with, in `export/`.

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
- Close the `.ai` in Illustrator before exporting over it. It needs macOS, Chrome, Illustrator
  (2024 or later) and the fonts installed, so it can’t run in a Cowork cloud session.
- One page per export.
- **Known limits.** CSS gradients arrive as pattern fills. Underlines and highlights are separate
  shapes, so move them with the text. Text at angles other than 0, 90, 180 or 270 degrees stays as
  imported letters. Large headings may sit up to about 1pt off, because Illustrator kerns slightly
  differently. Ligatures such as “ffi” may be set as separate letters.
- The PDF stays the approved deliverable. The `.ai` is the editable copy of it.

## 6. Closing a job

When the work is delivered, go through this before calling it done:

1. `export/` holds only the finals, named to §3, in the one format §5 calls for (never a PNG and a JPEG of the same image), with no version numbers. No templates,
   asset folders, scripts or intermediate renders (see “Generated work” in §2).
2. The top level holds only `source/`, `info/`, `assets/`, `export/`, `archive/`,
   `README.md` and `CLAUDE.md`. Tooling folders such as `build/` move into `assets/`.
3. Older versions: ask whether to delete them or move them to `archive/`.
4. Delete what nobody will open again: tests, previews, logs, temporary renders, one-off
   scripts. Scripts needed to rebuild the work stay, in `assets/`.
5. Delete your own throwaway files without asking. Ask before deleting anything someone
   else made, or anything you’re not sure about.
6. If you moved build files or rebuilt anything, run the build once more and confirm it
   still writes the final into `export/`. Then compare the new file with the previous
   final: a browser or tool update can change the output even when nothing else did.
7. Update `README.md` and `CLAUDE.md` so they describe the job as it now stands: the
   folders, what was decided, and anything left open.
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
