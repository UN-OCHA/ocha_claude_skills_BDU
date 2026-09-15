---
name: ocha-files-and-folders
description: >
  The OCHA BDU standard for organising job folders, naming files and choosing export formats. Applies to every
  BDU job: videos, maps, charts, infographics, reports, logo packages, social posts,
  presentations. Use whenever saving, exporting or delivering anything, creating or
  tidying a job folder, naming a file, handling draft versions, archiving old versions,
  or finishing a job. Trigger on "save this", "export", "where should this go", "name
  the file", "folder structure", "organise the folder", "clean up the folder", "final
  version", "archive", "we're done", "PNG or JPEG", "which format", "file too big". The other OCHA skills point here for every file and
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

## 2. Inside every job: the same folders

```
<job_name>/
  source/    what we received: footage, data, documents, with their original names
  info/      brief, approvals, feedback, transcripts, notes
  assets/    what is needed to rebuild the work: .ai / .indd / .aep masters, logos,
             fonts, cleaned data, scripts
  export/    the finals only, one file per deliverable
  archive/   optional: older versions worth keeping
  README.md  what it is, who asked for it, how it was made, how to edit it
```

- Create only the folders the job needs. Nothing else at the top level.
- Recurring outputs (a weekly email, a monthly update) get a dated folder inside
  `export/`: `export/2026-09-14_priorities/`.

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

## 4. Versions

- **While working:** drafts are `_v01`, `_v02`, `_v03`. Two digits, so they sort in order.
- **When delivered:** the final drops its version number and is the only copy in
  `export/`. `sdn_humanitarian_snapshot_a4_v03.pdf` becomes
  `sdn_humanitarian_snapshot_a4.pdf`, so nobody has to guess which one is final.
- **Older versions:** ask the user whether to delete them or move them to `archive/`.
  Never decide on your own.
- **A job that reopens:** move the current final into `archive/` before making the next
  version.

## 5. Export formats

Aim for the best quality at the smallest file size.

| The graphic | Export as |
|---|---|
| Can stay vector, and the destination accepts it | **SVG** for web and Illustrator, **PDF** for print |
| Flat colour, text, icons, charts, maps — no photos or raster effects | **PNG** |
| Needs a transparent background | **PNG** — JPEG can’t do transparency |
| Photos, grain, textures, blur, soft shadows | **JPEG**, quality 80–85 |
| A photo with crisp text on top | JPEG at higher quality, or PNG if the size stays reasonable — compare both |

- **Don’t rasterise what can stay vector.** PNG and JPEG are for destinations that need an
  image: social media, slides, email, some web tools.
- **Flat graphics can often go smaller** with a reduced colour palette (8-bit PNG) and no
  visible change. Check smooth gradients afterwards: a reduced palette can make them band.
- **JPEG above quality 90 buys almost nothing** but makes the file much bigger.
- **Export at the size the destination shows it** (twice that only when a high-density
  version is asked for). An oversized image is the most common reason a file is heavy.
- **When unsure, export both** and keep the smaller one that looks identical at full size.

## 6. Closing a job

When the work is delivered, go through this before calling it done:

1. `export/` holds only the finals, named to §3, in the format §5 calls for, with no version numbers. No templates,
   asset folders, scripts or intermediate renders (see “Generated work” in §2).
2. The top level holds only `source/`, `info/`, `assets/`, `export/`, `archive/` and
   `README.md`. Tooling folders such as `build/` move into `assets/`.
3. Older versions: ask whether to delete them or move them to `archive/`.
4. Delete what nobody will open again: tests, previews, logs, temporary renders, one-off
   scripts. Scripts needed to rebuild the work stay, in `assets/`.
5. Delete your own throwaway files without asking. Ask before deleting anything someone
   else made, or anything you’re not sure about.
6. If you moved build files or rebuilt anything, run the build once more and confirm it
   still writes the final into `export/`. Then compare the new file with the previous
   final: a browser or tool update can change the output even when nothing else did.
7. Update `README.md` so it describes the folders as they now are.
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
