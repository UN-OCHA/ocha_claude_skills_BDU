---
name: ocha-files-and-folders
description: >
  The OCHA BDU standard for organising job folders and naming files. Applies to every
  BDU job: videos, maps, charts, infographics, reports, logo packages, social posts,
  presentations. Use whenever saving, exporting or delivering anything, creating or
  tidying a job folder, naming a file, handling draft versions, archiving old versions,
  or finishing a job. Trigger on "save this", "export", "where should this go", "name
  the file", "folder structure", "organise the folder", "clean up the folder", "final
  version", "archive", "we're done". The other OCHA skills point here for every file and
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
| Language last, two letters | `_en`, `_fr`, `_es`, `_ar`, `_ru`, `_zh` |
| Never `final`, `new`, `latest` or `copy` | — |

Country codes rather than names, because names change — Türkiye, Occupied Palestinian
Territory — and codes don’t. OCHA geodata and location maps already use them.

The year-month-day format is for file names only. Dates written in text follow
`ocha-editorial-style`.

Examples:

- `sdn_humanitarian_snapshot_a4_2026-09-14_en.pdf`
- `ukr_asg_security_council_1080x1920_en.mp4`
- `gho2026_funding_by_sector_chart_fr.svg`

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
  `export/`. `sdn_humanitarian_snapshot_a4_v03_en.pdf` becomes
  `sdn_humanitarian_snapshot_a4_en.pdf`, so nobody has to guess which one is final.
- **Older versions:** ask the user whether to delete them or move them to `archive/`.
  Never decide on your own.
- **A job that reopens:** move the current final into `archive/` before making the next
  version.

## 5. Closing a job

When the work is delivered, go through this before calling it done:

1. `export/` holds only the finals, with no version numbers.
2. Older versions: ask whether to delete them or move them to `archive/`.
3. Delete what nobody will open again: tests, previews, logs, temporary renders, one-off
   scripts. Scripts needed to rebuild the work stay, in `assets/`.
4. Delete your own throwaway files without asking. Ask before deleting anything someone
   else made, or anything you’re not sure about.
5. Update `README.md`.

---

## Project Owner

Javier Cueto, Head of Brand and Design Unit

## Maintained by

**OCHA Brand and Design Unit (BDU)**
- Team: ochavisual@un.org
- Focal point: Javier Cueto (cuetoj@un.org)
