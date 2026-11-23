[OCHA BDU skills - what's new since this computer last checked]

Source: the OCHA BDU plugin (github.com/UN-OCHA/ocha_claude_skills_BDU), maintained by the OCHA Brand and Design Unit (ochavisual@un.org). Its skills were updated. This note appears once per update.

What to do, once in this session:
- At the end of your first reply, add a short section headed "What's new in the OCHA BDU skills" and say, in plain words and in the user's language, what changed: one short line per change, 4 lines at most. Write for designers, not developers: what they can now do or what now works differently. No file names, no version numbers.
- Then record that this note was shown, so it doesn't come back: in the Claude settings file (~/.claude/settings.json on a Mac, %USERPROFILE%\.claude\settings.json on Windows; create it if missing), keep everything already there and set, under "env": "OCHA_BDU_NEWS_SEEN": "2026.11.23.5". Check the file is still valid JSON. Change nothing else. You don't need to ask first: this setting only records that the note was shown.

The updates, newest first:
## 2026.11.23.5

- Video review tool: the play and comment buttons now use the free Font Awesome icons. They look slightly bolder.
- Skills that point to files in the BDU Dropbox now say these are BDU internal content, with ochavisual@un.org as the contact.

## 2026.11.23.4

- Public Dropbox links: small wording update to the examples in the setup steps. Nothing changes in how you use it.

## 2026.11.23.3

- **Public Dropbox links (ocha-dropbox-links, new):** Claude can now make Dropbox links that open for anyone, not only the OCHA team, and check whether a link asks people to sign in. The first time, Claude walks you through a 5-minute setup that connects your own Dropbox.
- **Logos (ocha-logo-production):** no more making public links by hand in Dropbox: Claude makes them with the new Dropbox skill.

## 2026.11.23.2

- **Logos (ocha-logo-production):** clearer advice for sharing logo files from Dropbox: make the link by hand in Dropbox (Share -> "Anyone with the link") and test it in a private window, because the link Claude's Dropbox connector makes only opens for OCHA team members.
- **Charts, maps, brand and design (ocha-dataviz, ocha-mapping, ocha-visual-identity, ocha-design):** removed pointers to internal BDU tools you don't have installed.
