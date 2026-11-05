# Translated versions

For wording and number formats, use `ocha-editorial-style` (French: its `references/french.md`). This
guide covers how to build a translation.

## Method

- **Rebuild with a script, don’t hand-edit.** Keep all wording in one file keyed by the exact English text,
  and a script that applies it to a copy of the English file. When English changes, rebuild.
- **Fail on a missing string.** A build that silently leaves English behind is worse than one that stops.
- **Style names stay in English,** so the two files stay comparable and tips can name them. Menu paths in
  tips give the language’s name with the English in brackets.
- **Set the language on styles only,** never on the text as well: that leaves local overrides everywhere.
- **Maps stay in English** in translated templates. Only titles set as text are translated. Other charts
  are rebuilt from translated strings.
- **A copied file still links to the English package** until relinked.

## Making room

Text gets longer: French runs 15–25% over English.

1. Let tables and frames grow where the page allows, then move free frames with small, recorded moves
   in a script, so a rebuild repeats them.
2. Prefer one line less in a heading over cutting text. Don’t cut placeholder lines: pages keep their length.
3. Shorten a heading only when it breaks the layout, and record it for the reviewer.

## Checks

- Compare pages side by side with English, plus a script check: same page count, no overset text, and maps
  identical to English.
- Run the override checks on both languages (`references/indesign.md`).
- Give the reviewer one page: wording you had to choose, layout changes and what was left as is.
