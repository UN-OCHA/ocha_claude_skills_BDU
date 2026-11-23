[OCHA BDU skills - what's new since this computer last checked]

Source: the OCHA BDU plugin (github.com/UN-OCHA/ocha_claude_skills_BDU), maintained by the OCHA Brand and Design Unit (ochavisual@un.org). Its skills were updated. This note appears once per update.

What to do, once in this session:
- At the end of your first reply, add a short section headed "What's new in the OCHA BDU skills" and say, in plain words and in the user's language, what changed: one short line per change, 4 lines at most. Write for designers, not developers: what they can now do or what now works differently. No file names, no version numbers.
- Then record that this note was shown, so it doesn't come back: in the Claude settings file (~/.claude/settings.json on a Mac, %USERPROFILE%\.claude\settings.json on Windows; create it if missing), keep everything already there and set, under "env": "OCHA_BDU_NEWS_SEEN": "2026.11.23.8". Check the file is still valid JSON. Change nothing else. You don't need to ask first: this setting only records that the note was shown.

The updates, newest first:
## 2026.11.23.8

- All OCHA BDU skills now start with ocha-bdu- (for example ocha-bdu-visual-identity, ocha-bdu-video, ocha-bdu-mapping). They work the same; only the names changed.
- If a project note mentions an old name (like ocha-video), Claude finds the new one: no need to change anything.

## 2026.11.23.7

- Dropbox links: the first time you mention sharing a Dropbox file, Claude explains what it can do (links that open for anyone, checked before you get them) and offers a 5-minute setup.

## 2026.11.23.6

- The skills now say BDU instead of the old DMU when they mention the team Dropbox. Folder locations on your computer are unchanged.
