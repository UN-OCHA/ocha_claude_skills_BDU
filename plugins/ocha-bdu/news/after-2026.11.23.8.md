[OCHA BDU skills - update from Javi, since this computer last checked]

Source: the OCHA BDU plugin (github.com/UN-OCHA/ocha_claude_skills_BDU), maintained by Javi (Javier Cueto) and the OCHA Brand and Design Unit (ochavisual@un.org). Javi updated its skills. This note appears once per update.

What to do, once in this session:
- At the end of your first reply, add a short section headed "Update from Javi (OCHA BDU skills)" and say, in plain words and in the user's language, what changed: one short line per change, 4 lines at most. Write for designers, not developers: what they can now do or what now works differently. No file names, no version numbers.
- Lines marked "Javi recommends:" are steps Javi wants each colleague to take. Say them as his recommendation, plainly ("Javi recommends: ..."), then offer to do the step now, explain in one sentence what it changes, and do it only after the user says yes. If it isn't needed on this computer (for example the old folders aren't there), say so in one line instead of asking. Never delete or change anything without that yes.
- Then record that this note was shown, so it doesn't come back: in the Claude settings file (~/.claude/settings.json on a Mac, %USERPROFILE%\.claude\settings.json on Windows; create it if missing), keep everything already there and set, under "env": "OCHA_BDU_NEWS_SEEN": "2026.11.24.2". Check the file is still valid JSON. Change nothing else. You don't need to ask first: this setting only records that the note was shown.

The updates, newest first:
## 2026.11.24.2

- **New: graphic styles.** BDU's named looks now have their own skill, for static graphics as well as films. Ask for "the newsprint style" or "the cut-out style" and Claude follows the recipe.
- **Newsprint**, the first new style: cream printed paper, OCHA icons in ink, black caption strips and an orange marker on the key idea. A sober, newsy look for explainers and diagrams, with a starter graphic to copy.
- **Old pictures for free:** the style points to the Public Domain Image Archive for photos, old charts and engravings that need no credit.

## 2026.11.24

- **Updates from Javi:** update notes now say plainly when Javi recommends a step, and Claude offers to do it for you.
- **Staying up to date:** if your OCHA skills get stuck on an old version, Claude now notices and tells you exactly what to do.
- **Javi recommends:** if you still have old OCHA skill folders whose names don't start with "ocha-bdu-" (from before Monday's rename), let Claude delete them. They are out of date and make Claude load every skill twice.
