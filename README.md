# OCHA BDU skills for Claude Code

Brand, design and video skills used by the OCHA Brand and Design Unit, packaged so any
OCHA colleague can install them into **Claude Code** in one step.

## Install

In Claude Code, add this marketplace and install the plugin:

```
/plugin marketplace add UN-OCHA/ocha_claude_skills_BDU
/plugin install ocha-bdu@ocha-bdu
```

That's it. The skills load automatically when they're relevant — ask for an OCHA chart,
a map, a logo rule, a caption, and the right one fires. You can also call one directly,
e.g. `/ocha-bdu:ocha-visual-identity`.

To update later, re-run the `marketplace add` command (or use `/plugin`).

## What's included

| Skill | What it covers |
|---|---|
| `ocha-visual-identity` | Brand colours, typography, logo rules, clear space, the `cd-*` Common Design System |
| `ocha-dataviz` | Chart selection and OCHA data-visualization rules |
| `ocha-mapping` | Cartographic standards — boundaries, symbology, disclaimers |
| `humanitarian-icons` | The 389 OCHA Humanitarian Icons |
| `ocha-editorial-style` | OCHA house style — numbers, dates, currency, capitalization, acronyms |
| `ocha-design` | Umbrella: loads visual identity + dataviz + mapping together |
| `ocha-statement-video` | End-to-end pipeline for a branded statement video (SC / member-states / noon briefing / PTC) |
| `ocha-video-branding` | Branding a finished clip — captions, lower third, location strip, logo ending |

## Extra setup for the two video skills

The video skills render through the **OCHA QuickVid** engine. Install it once
(~10 minutes, no admin password needed):

```
curl -fsSL https://raw.githubusercontent.com/UN-OCHA/quickvid_BDU/main/install.sh | bash
```

The skills find it automatically afterwards. If you keep QuickVid somewhere unusual,
point at it explicitly:

```
export QUICKVID_HOME="/path/to/ocha_quick_vid"
```

The other six skills need no setup.

## A note on file paths

Some skills reference shared resources in the OCHA DMU Dropbox, written as:

```
~/OCHA DMU Dropbox/<your-name>/Design/...
```

Replace `<your-name>` with your own member folder — it's whatever
`~/OCHA DMU Dropbox/` contains on your Mac. You need access to the relevant team folders
for those references to resolve.

## Requirements

- **Claude Code** (the Mac desktop app or CLI). These are skills — they do **not** work
  in Cowork sessions.
- Dropbox access to the OCHA DMU team folders, for the skills that point at shared assets.

## Project Owner

Javier Cueto, Head of Brand and Design Unit

## Maintained by

**OCHA Brand and Design Unit (BDU)**
- Team: ochavisual@un.org
- Focal point: Javier Cueto (cuetoj@un.org)
