---
name: ocha-bdu-design
description: >
  Umbrella skill that loads the full OCHA design toolkit — visual identity,
  data visualization, and mapping — all at once. Use this skill whenever the
  user says "OCHA design skills", "OCHA design", "bring OCHA design",
  "load OCHA design", "OCHA design context", "OCHA BDU skills", "activate
  OCHA design", "I need all the OCHA skills", or any phrase that asks for
  OCHA brand / dataviz / mapping knowledge together. Also trigger when the
  user is starting work that will clearly touch more than one of the three
  (e.g. an infographic that includes a map, a branded report with charts, a
  dashboard with maps and charts). For a single-domain request, prefer the
  specific skill (`ocha-bdu-visual-identity`, `ocha-bdu-dataviz`, or `ocha-bdu-mapping`).
---

# OCHA Design — Umbrella

This skill is a loader. It exists so the user can bring all three OCHA design
skills into context with a single phrase. There is no standalone content
here — everything lives in the three sibling skills.

## What to do when triggered

**Read all three sibling SKILL.md files in parallel, then confirm to the user.**

Use the Read tool on:
1. `ocha-bdu-visual-identity/SKILL.md`
2. `ocha-bdu-dataviz/SKILL.md`
3. `ocha-bdu-mapping/SKILL.md`

Fire all three Read calls in a single message (they're independent — don't
sequence them).

After loading, reply with a short confirmation listing the three domains
you now have in context and asking what they want to work on. Example:

> OCHA design toolkit loaded:
> - **Visual identity** — brand colours, typography, logo, `cd-*` design system
> - **Data visualization** — chart selection, infographic rules, HNRP/Flash/GHO styles
> - **Mapping** — full cartographic spec, symbology, critique checklist
>
> What are we building?

Do NOT paraphrase or summarise the skill contents in that confirmation. The
user already knows what's in them — the point of loading is that you have
the details ready for the real task that follows.

## Figma connector — which one to use

- **Figma can appear more than once in Connectors.** Use the one with the Figma logo: that’s the
  claude.ai connector. Plain-letter “F” entries come with installed plugins (the Figma plugin and its
  `figma:` skills) or the Figma desktop app. One asking to “Authenticate” isn’t needed; ignore it.
- **If Figma calls start failing partway through a session**, turn the Figma connector off and on in the
  session’s connector settings, or start a new session. Don’t work around it.
- Canva has the same double entry: see `ocha-bdu-social-media` §0.

## When NOT to use this skill

- Single-domain questions — the relevant specific skill will auto-trigger and is lighter.
- The user is asking *about* the skills themselves (e.g. "how are my OCHA skills structured?") rather than asking to *use* them.

## Relationship to other skills

| Trigger | Skill |
|---|---|
| "OCHA design skills" / multi-domain task | **this one** (→ loads the three below) |
| Brand colours / logo / fonts / `cd-*` / design system only | `ocha-bdu-visual-identity` |
| Charts / infographics only | `ocha-bdu-dataviz` |
| Maps only | `ocha-bdu-mapping` |
| Saving, naming files, export formats, versions, closing a job | `ocha-bdu-files-and-folders` |
| Photos — MediaValet downloads, enhancement, photo credits | `ocha-bdu-photo` |
| Mockups — a cover or page on a magazine, poster, card, roll-up, laptop or phone; cover options | `ocha-bdu-mockups` |

<!-- bdu-suggest-change:start -->
**Suggesting a change to this skill.** If the person corrects you or states a rule that would apply to other jobs too, or you find this skill is wrong or missing something, say so once, at the end of your reply. Don’t do this for changes that only concern the current job, and don’t edit the skill yourself, because the next update would overwrite it. Leave out anything confidential from the job. Say:

> This could be worth adding to the OCHA BDU skills. If you agree, copy this message and send it to Javi:
> **Skill:** ocha-bdu-design
> **Proposed rule:** [the rule, in one or two sentences]
> **Why:** [what happened, with one example]
<!-- bdu-suggest-change:end -->
