---
name: ocha-editorial-style
description: >
  Apply OCHA house editorial style to any text written for OCHA — reports, appeals,
  web copy, brand-portal text, captions, emails, social posts, headings, alt text.
  Covers numbers, dates, currency, capitalization, acronyms, quotation marks vs
  italics, punctuation, job titles, and plain-language rules. Use whenever writing
  or editing OCHA-facing copy, or when the user asks about OCHA style, UN style,
  "how do we write X", capitalization of a term, whether something takes italics or
  quotes, how to format a number/date/currency, or asks to proofread or copy-edit
  OCHA text. Source: OCHA Editorial Style Guide, 3rd edition (bundled). For brand
  colours/logo use `ocha-visual-identity`; for charts `ocha-dataviz`; for maps
  `ocha-mapping`.
---

# OCHA editorial style

House style for anything OCHA-facing. Source of truth: **OCHA Editorial Style Guide,
3rd edition** — bundled at `references/OCHA_Editorial_Style_Guide_3rd_ed.pdf` (66 pp).

This file distils the rules that come up constantly. **The guide's exhaustive A–Z
spelling list and acronym list are NOT reproduced here** — open the PDF for those
(spelling list ≈ p.30, acronyms ≈ p.37+).

## Non-negotiables

- **Curly quotes and apostrophes, always** (`'` → `’`, `"…"` → `“…”`). This is a global
  rule in `~/.claude/CLAUDE.md` — applies to everything, OCHA or not. Apply silently;
  don't announce it.
- **UN spelling**: `Organization` with a **z**, not s. Also `programme`, `centre`,
  `labour` (UK forms otherwise).
- **Never start a sentence with a numeral.** Use "A total of 3 million people…" to get
  around it — this is the one legitimate use of that otherwise-banned phrase.

## Numbers, dates, currency

- **Ages** → numerals. Hyphenate only before a noun: *a 98-year-old man* / *the man is
  98 years old*. Under-fives: *the under-five mortality rate* (before noun) / *children
  under age 5*.
- **Fractions** → spell out simple ones (*two thirds of the population*, never *2/3*).
  Use percentages or decimals for complex figures.
- **Distance** → spell out when no specific number (*several kilometres away*); use `km`
  with a space when there is one, and use numerals even for one–nine: *9 km from the
  border*.
- **Currency** → US dollar is the reference. First mention `US$`, thereafter `$`, **no
  space** before the number. Headlines use `$` (not `US$`). Keyboards without `$` → `USD`.

## Capitalization

The guide's principle: **capitalize the specific, lower-case the generic.**

| Lower-case (generic) | Upper-case (specific) |
|---|---|
| the clusters have been activated | the Nutrition Cluster, the WASH Cluster |
| a seminar for ambassadors | Ambassador [name] |
| finance ministers | the Minister of Finance of Japan |
| an OCHA humanitarian affairs officer | OCHA Humanitarian Affairs Officer Rita Singh |
| the regional commissions | the Commission (specific reference) |
| annex, the report's annexes | Annex II |
| OCHA headquarters | United Nations Headquarters |

- **Government** takes upper-case G when it represents a State or Non-Self-Governing
  Territory (including transitional administrations).
- **Headings**: initial capital on the first word and proper nouns only — not title case.
- Full A–Z of contested words is in the PDF's Capitalization section (≈ p.24).

## Quotation marks vs italics vs neither

Three-way distinction the guide is strict about:

| “Double quotes” | ‘Single quotes’ | *Italics* | Neither |
|---|---|---|---|
| Verbatim quotes | Article / chapter titles | Official UN publications | Award names |
| A word referring to its own meaning | Conference / meeting names | Books, periodicals, newspapers, films, TV/radio | Lecture names |
| | Database names, definitions | Foreign words **not** in the Oxford English Dictionary | Peace agreements |
| | Draft documents, interview titles | Court cases, foreign laws/decrees | Programme / project names |
| | Press-release titles, speech titles | Ship and aircraft names | UN resolutions, conventions, treaties |
| | Web-page headings | Foreign seasonal names (e.g. *deyr*) | Numbered UN documents; non-English org names; words after *so-called* |

## Acronyms and abbreviations

- Full name on first mention, acronym in brackets — **only if used again**.
- Use sparingly; don't clutter the page with capitals.
- **No full stops inside** them: `UNDP`, not `U.N.D.P`.
- **No "the"** as part of the name: `WFP` not `the WFP`; `CERF` not `the CERF`.
- `a` vs `an` follows **pronunciation**: *a NATO decision*, *an NGO conference*, *an MSF
  programme*, *an L3 emergency*.
- Avoid in titles and headings where possible.
- **Always expand acronyms in anything that will be translated** — translators may not
  know OCHA/UN terminology.
- Note: *the CERF secretariat*, not *the CERF Secretariat*.

## Punctuation

- **Apostrophes**: `’s` singular possessive · `’s` plural not ending in s (*children’s*) ·
  `s’` plural ending in s (*aid workers’*, *refugees’*). Singular nouns ending in s take
  `’s` when the extra s is pronounced (*Charles’s report*). Abbreviations: *the NGO’s
  decision* (one) vs *the NGOs’ decision* (many); *several NGOs* — no apostrophe for
  plain plurals. Time: *one month’s supply*, *two weeks’ time*.
- **Brackets**: parentheses for side remarks — punctuation inside if the whole sentence
  is inside, outside otherwise. **Square brackets** to clarify inside a quote:
  *“We are hopeful that they [the village leaders] will join…”*
- **Bullets**: full sentences take a full stop; short phrases take no punctuation.
- **Comma**: after an introductory phrase. Never splice two sentences with a comma — use
  a semicolon.
- **Colon**: introduces an elaboration, list or example. **Never a dash after a colon.**
- **Accents**: always keep them in names of people, places and organizations — *Médecins
  Sans Frontières*, *Côte d’Ivoire*, *El Niño*.

## Plain language

- **Active voice by default** (*WFP delivered food to 800 refugees*). Passive only when
  the actor genuinely can't be named (*Thirty civilians were killed in a bomb attack*).
- **Cut the padding**: *a total of*, *a period of*, *also*, *both* are flagged as overused.
  Delete and check whether the meaning changed — if not, leave it out.
- **Say what you mean**: replace *more effective and principled humanitarian action*,
  *showcase*, *partners do not have the capacity to respond* with concrete statements.
- **Avoid ambiguous frequency words** — *biannual*, *bimonthly*, *biweekly* can mean
  either twice-per or every-other. Write *twice a year* / *every two years* instead.
- It is fine to start a sentence with *and* or *but* — just not often.

## Common OCHA-specific traps

- *Humanitarian Coordinator*, **not** *United Nations Humanitarian Coordinator*.
- *Food and Agriculture Organization* — **Agriculture**, not *Agricultural*.
- *HIV* — the V is "virus", so never *the HIV virus*.
- *health care* (noun) vs *health-care* (adjective).
- *capacity-building* is always hyphenated, noun or adjective.
- Spell-check won't catch *chef* for *chief* — search for it explicitly.

## When the answer isn't here

Open `references/OCHA_Editorial_Style_Guide_3rd_ed.pdf`. It's an A–Z: Section 1 grammar
and style, then commonly misused words, unnecessary words, quotation marks/italics,
capitalization, the spelling list, and the acronym list. If it's still ambiguous, ask
Javier — he owns this standard.

## Project Owner

Javier Cueto, Head of Brand and Design Unit

## Maintained by

**OCHA Brand and Design Unit (BDU)**
- Team: ochavisual@un.org
- Focal point: Javier Cueto (cuetoj@un.org)
