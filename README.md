# OCHA BDU skills for Claude

Brand, design and video know-how from the OCHA Brand and Design Unit, packaged so any
OCHA colleague can add it to Claude in about a minute.

Once installed, Claude follows OCHA brand rules by default — the right colours, the right
logo behaviour, house editorial style, the video pipeline — without you having to explain
them each time.

---

## What you need first

The **Claude desktop app** for Mac, with **Claude Code**. If you can open Claude and type
in a chat box, you're ready.

> **These are skills, so they work in Claude Code — not in Cowork sessions.**

---

## Install — 2 lines, no Terminal

**Everything below goes in the Claude chat box**, exactly where you would type a normal
message. This is *not* Terminal.

**1.** Type this and press return:

```
/plugin marketplace add UN-OCHA/ocha_claude_skills_BDU
```

**2.** Then type this and press return:

```
/plugin install ocha-bdu@ocha-bdu
```

Done. Claude confirms each step.

### Check it worked

Type this in the chat box:

> what OCHA skills do I have now?

You should see seven, listed below.

---

## Using them — just ask normally

You don't invoke anything. Ask for the work and the right skill loads itself:

> *"Make a bar chart of funding by sector, OCHA style"*
> *"Where's the OCHA logo, and how much clear space does it need?"*
> *"Proofread this paragraph for our house style"*
> *"Add subtitles and the OCHA ending to this clip"*

If you'd rather be explicit, type `/ocha-bdu:` and pick from the list.

---

## What you get

| Skill | What it covers |
|---|---|
| `ocha-visual-identity` | Brand colours, typography, logo rules, clear space, the `cd-*` Common Design System |
| `ocha-dataviz` | Which chart to use, and OCHA's data-visualization rules |
| `ocha-mapping` | Map standards — boundaries, symbology, disclaimers |
| `humanitarian-icons` | The 389 OCHA Humanitarian Icons |
| `ocha-editorial-style` | House style — numbers, dates, currency, capitalization, acronyms |
| `ocha-design` | Umbrella: loads visual identity + dataviz + mapping together |
| `ocha-video` | Everything video — cutting, captions, lower third, logo ending, packaging |

Six of the seven need **no setup at all**. Only video needs one extra step.

---

## Extra step — only if you do video

Video rendering runs through the **OCHA QuickVid** engine. Install it once
(about 10 minutes, no admin password).

**Easiest way — ask Claude to do it.** In the chat box:

> install OCHA QuickVid for me

**Or run it yourself in Terminal** (Applications → Utilities → Terminal), paste and press
return:

```bash
curl -fsSL https://raw.githubusercontent.com/UN-OCHA/quickvid_BDU/main/install.sh | bash
```

The video skill finds it automatically afterwards — nothing to configure.

Already have QuickVid somewhere unusual? Tell Claude where, or set:

```bash
export QUICKVID_HOME="/path/to/ocha_quick_vid"
```

---

## Keeping up to date

New versions don't arrive on their own. In the Claude chat box:

```
/plugin marketplace update ocha-bdu
```

---

## Dropbox files

Some skills point at shared resources in the OCHA DMU Dropbox, written like this:

```
~/OCHA DMU Dropbox/<your-name>/Design/...
```

`<your-name>` is your own member folder — whatever `~/OCHA DMU Dropbox/` shows on your
Mac. You need access to the relevant team folders for those to open.

---

## Something not working?

- **The `/plugin` commands do nothing** → you're probably in a Cowork session. Skills only
  work in Claude Code.
- **Claude says the QuickVid engine isn't found** → run the video install step above.
- **A Dropbox path won't open** → you likely don't have access to that team folder yet.

Still stuck: **ochavisual@un.org**

---

## Project Owner

Javier Cueto, Head of Brand and Design Unit

## Maintained by

**OCHA Brand and Design Unit (BDU)**
- Team: ochavisual@un.org
- Focal point: Javier Cueto (cuetoj@un.org)
