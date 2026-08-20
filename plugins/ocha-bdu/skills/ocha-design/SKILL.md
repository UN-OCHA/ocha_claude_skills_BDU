---
name: ocha-design
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
  specific skill (`ocha-visual-identity`, `ocha-dataviz`, or `ocha-mapping`).
---

# OCHA Design — Umbrella

This skill is a loader. It exists so the user can bring all three OCHA design
skills into context with a single phrase. There is no standalone content
here — everything lives in the three sibling skills.

## What to do when triggered

**Read all three sibling SKILL.md files in parallel, then confirm to the user.**

Use the Read tool on:
1. `ocha-visual-identity/SKILL.md`
2. `ocha-dataviz/SKILL.md`
3. `ocha-mapping/SKILL.md`

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

## When NOT to use this skill

- Single-domain questions — the relevant specific skill will auto-trigger and is lighter.
- The user is asking *about* the skills themselves (e.g. "how are my OCHA skills structured?") rather than asking to *use* them.
- Plugin release work — that's `ocha-dataviz-release`, a separate skill that is NOT loaded by this umbrella.

## Relationship to other skills

| Trigger | Skill |
|---|---|
| "OCHA design skills" / multi-domain task | **this one** (→ loads the three below) |
| Brand colours / logo / fonts / `cd-*` / design system only | `ocha-visual-identity` |
| Charts / infographics only | `ocha-dataviz` |
| Maps only | `ocha-mapping` |
| Illustrator plugin release / ZXP build | `ocha-dataviz-release` (unrelated to this umbrella) |
