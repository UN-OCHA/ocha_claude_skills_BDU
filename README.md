# OCHA BDU skills for Claude

Adds OCHA brand knowledge to Claude — colours, logo rules, chart and map standards,
house writing style, and the full video pipeline.

Once installed, you just ask Claude for the work and it follows OCHA standards
automatically. You don't have to explain them every time.

> **These instructions are for the Claude Code desktop app** (Mac or Windows).

---

## ⚠️ Before you start — you need a paid Claude plan

**Claude Code is not available on the free plan.** You need **Claude Pro** (or higher —
Max, Team, Enterprise). Without it, the Claude Code tab won't be there and none of the
steps below will work.

Not sure which plan you're on, or need one? Email **ochavisual@un.org** and we'll point
you the right way.

---

**Setup takes about 5 minutes.** Follow the steps in order.

---

## Step 1 — Install Claude on your computer

Download it here: **https://claude.ai/download**

Install it like any other app, then open it and sign in.

> One app, **Mac or Windows**. Claude Code comes with it — there's nothing extra to
> download. If you already have the Claude app, skip to Step 2.

---

## Step 2 — Open Claude Code

In the Claude app, click the **Claude Code** icon in the left sidebar.

> **This matters.** The Claude app has several tabs — Claude, Claude Code and Cowork.
> **These skills only work on the Claude Code tab.**

### It asks you to choose a folder

A window opens asking you to pick a folder. **Pick `Desktop` and click Open.**

**This is not about the skills.** Claude Code can't open at all without a folder — it's
its own one-time setup. It just happens to appear now because this is your first time
using it.

- **Nothing is saved into that folder.** The skills install inside Claude itself.
- Picking `Desktop` here changes nothing and breaks nothing.

**Why Claude Code wants a folder at all:** it works *on files* — it makes charts, edits
videos, writes documents. The folder tells it **where to look for your files and where to
save what it makes.** That only starts to matter once you're doing real work, and you
pick the right folder then (see below).

### Say yes to the permission prompts

The first time you use Claude Code, it asks permission before doing things on your
computer — reading a file, running something. **Approve these when prompted**, or it
won't be able to do the work.

Tired of being asked every time? At the **bottom left** there's a **Bypass permissions**
option. It stops the prompts and lets Claude act without checking each time — faster, but
you lose that checkpoint, so only turn it on for work you trust. Approving prompts one by
one is the safer default.

---

## Step 3 — Add the OCHA skills

Copy this whole message, paste it into the **Claude Code chat box**, and press return:

> Please install the OCHA BDU skills. Clone
> https://github.com/UN-OCHA/ocha_claude_skills_BDU into a temp folder, copy all 7 skill
> folders from `plugins/ocha-bdu/skills/` into my `~/.claude/skills/` folder, then tell me
> which ones you installed.

Claude Code will ask permission for a couple of steps — approve them. It takes under a
minute, and it tidies up after itself.

You should see all seven listed when it finishes.

---

## Step 4 — Quit Claude and open it again

**This step is required.** Skills only load when Claude starts, so the new ones won't
appear until you restart.

Quit Claude completely, then open it again and go back to the **Claude Code** tab.

---

## Step 5 — Check it worked

Type this in the Claude Code chat box, like a normal question:

> **what OCHA skills do I have now?**

Claude should list seven skills. If it does, you're finished. 🎉

---

## How to use it

Nothing to remember. Just ask for what you need:

> *"Make a bar chart of funding by sector, OCHA style"*
> *"What are the OCHA brand colours?"*
> *"How much clear space does the OCHA logo need?"*
> *"Check this paragraph against our house style"*
> *"Add subtitles and the OCHA ending to this video"*

Claude picks the right skill by itself.

---

## 🎬 Only if you make videos — one more install

Skip this unless you edit video.

Video work uses the **OCHA QuickVid** engine. Install it once — about 10 minutes,
**no admin rights, no Terminal**:

1. Go to **https://un-ocha.github.io/quickvid_BDU/**
2. Click the button to download the installer (**Install OCHA QuickVid**)
3. Find it in your Downloads and double-click it

It sets itself up and starts when finished. Mac and Windows both.

> The first time you open it, your computer shows one security warning. This is normal
> for anything downloaded from the internet.
> **Mac:** right-click the file → Open → Open.
> **Windows:** More info → Run anyway.

Claude finds the engine on its own afterwards. Nothing to set up.

---

## What you get

| Skill | What it helps with |
|---|---|
| `ocha-visual-identity` | Brand colours, fonts, logo rules, clear space, the OCHA design system |
| `ocha-dataviz` | Which chart to use, and how OCHA charts should look |
| `ocha-mapping` | OCHA map standards — boundaries, symbols, disclaimers |
| `humanitarian-icons` | The 389 OCHA Humanitarian Icons |
| `ocha-editorial-style` | OCHA house style — numbers, dates, currency, capitalisation, acronyms |
| `ocha-design` | Loads visual identity + charts + maps together |
| `ocha-video` | Everything video — cutting, subtitles, lower third, logo ending, packaging |

---

## 🧠 What model should I use?

**Start with Sonnet.** Opus and Fable are more powerful but eat through your usage limits
much faster — and for most of this work they won't give you a better result.

Switch up only for the jobs that need real judgment:

| What you're doing | Model |
|---|---|
| Branding a finished clip — subtitles, lower third, logo ending | **Sonnet** |
| Charts, maps, icons, brand questions, packaging files | **Sonnet** |
| Choosing which 60 seconds to cut from a long briefing | **Opus** |
| Translating subtitles | **Opus** |
| Something broke and you need it debugged | **Opus** |

You can switch models in the middle of a session — the work carries over.

> **The one that matters:** if you're cutting a principal's words, use **Opus**. A weaker
> model's mistake there isn't a broken file — it's a clip that misrepresents what someone
> said.

---

## Keeping it up to date

We add and improve skills over time. To get the latest, paste the **same message from
Step 3** into Claude Code again — it overwrites the old versions with the current ones.
Quit and reopen Claude afterwards.

---

## If something doesn't work

**"I installed them but Claude doesn't know about them."**
You need to quit Claude and reopen it (Step 4). Skills only load at startup.

**"Claude says it can't find the QuickVid engine."**
You haven't done the video install yet — see the video step above.

**"Claude can't open a Dropbox file."**
Some skills point at shared files in the OCHA DMU Dropbox. You need access to that team
folder. Ask us and we'll sort it out.

**Anything else:** **ochavisual@un.org** — we'd rather help than have you stuck.

---

## Project Owner

Javier Cueto, Head of Brand and Design Unit

## Maintained by

**OCHA Brand and Design Unit (BDU)**
- Team: ochavisual@un.org
- Focal point: Javier Cueto (cuetoj@un.org)
