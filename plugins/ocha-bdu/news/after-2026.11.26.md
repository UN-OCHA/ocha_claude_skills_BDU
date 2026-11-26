[OCHA BDU skills - update from Javi, since this computer last checked]

Source: the OCHA BDU plugin (github.com/UN-OCHA/ocha_claude_skills_BDU), maintained by Javi (Javier Cueto) and the OCHA Brand and Design Unit (ochavisual@un.org). Javi updated its skills. This note appears once per update.

What to do, once in this session:
- At the end of your first reply, add a short section headed "Update from Javi (OCHA BDU skills)" and say, in plain words and in the user's language, what changed: one short line per change, 4 lines at most. Write for designers, not developers: what they can now do or what now works differently. No file names, no version numbers.
- Lines marked "Javi recommends:" are steps Javi wants each colleague to take. Say them as his recommendation, plainly ("Javi recommends: ..."), then offer to do the step now, explain in one sentence what it changes, and do it only after the user says yes. If it isn't needed on this computer (for example the old folders aren't there), say so in one line instead of asking. Never delete or change anything without that yes.
- Then record that this note was shown, so it doesn't come back: in the Claude settings file (~/.claude/settings.json on a Mac, %USERPROFILE%\.claude\settings.json on Windows; create it if missing), keep everything already there and set, under "env": "OCHA_BDU_NEWS_SEEN": "2026.11.26.3". Check the file is still valid JSON. Change nothing else. You don't need to ask first: this setting only records that the note was shown.

The updates, newest first:
## 2026.11.26.3

- Connecting Claude to the brand site: Claude now finds the frontify-mcp folder wherever your Dropbox keeps it. If it still can't, it asks you to make that folder available offline and drag it into the chat.

## 2026.11.26.2

- Logo and template links on the brand site now use Dropbox's download version, so one click downloads the file instead of opening a Dropbox preview.
