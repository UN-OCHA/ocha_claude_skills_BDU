[OCHA BDU skills - what's new since this computer last checked]

Source: the OCHA BDU plugin (github.com/UN-OCHA/ocha_claude_skills_BDU), maintained by the OCHA Brand and Design Unit (ochavisual@un.org). Its skills were updated. This note appears once per update.

What to do, once in this session:
- At the end of your first reply, add a short section headed "What's new in the OCHA BDU skills" and say, in plain words and in the user's language, what changed: one short line per change, 4 lines at most. Write for designers, not developers: what they can now do or what now works differently. No file names, no version numbers.
- Then record that this note was shown, so it doesn't come back: in the Claude settings file (~/.claude/settings.json on a Mac, %USERPROFILE%\.claude\settings.json on Windows; create it if missing), keep everything already there and set, under "env": "OCHA_BDU_NEWS_SEEN": "2026.11.18.2". Check the file is still valid JSON. Change nothing else. You don't need to ask first: this setting only records that the note was shown.

The updates, newest first:
## 2026.11.18.2

- **Funding data (ocha-data):** reading the FTS funding dashboard works again after the FTS team changed it, and Claude can now also read the dashboard's hidden emergency pages, such as Ebola 2026.
- **Social media (ocha-social-media):** figure slides can have a smaller intro line under the big number, and Claude keeps people in photos out of the dark text gradient.
- **Video review (ocha-video):** the review page now plays at 1.5x and 2x speed.
- **New:** after each update, Claude tells you in a few lines what changed, like this.
