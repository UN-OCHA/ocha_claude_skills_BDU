[OCHA BDU skills - update from Javi, since this computer last checked]

Source: the OCHA BDU plugin (github.com/UN-OCHA/ocha_claude_skills_BDU), maintained by Javi (Javier Cueto) and the OCHA Brand and Design Unit (ochavisual@un.org). Javi updated its skills. This note appears once per update.

What to do, once in this session:
- At the end of your first reply, add a short section headed "Update from Javi (OCHA BDU skills)" and say, in plain words and in the user's language, what changed: one short line per change, 4 lines at most. Write for designers, not developers: what they can now do or what now works differently. No file names, no version numbers.
- Lines marked "Javi recommends:" are steps Javi wants each colleague to take. Say them as his recommendation, plainly ("Javi recommends: ..."), then offer to do the step now, explain in one sentence what it changes, and do it only after the user says yes. If it isn't needed on this computer (for example the old folders aren't there), say so in one line instead of asking. Never delete or change anything without that yes.
- Then record that this note was shown, so it doesn't come back: in the Claude settings file (~/.claude/settings.json on a Mac, %USERPROFILE%\.claude\settings.json on Windows; create it if missing), keep everything already there and set, under "env": "OCHA_BDU_NEWS_SEEN": "2026.11.26". Check the file is still valid JSON. Change nothing else. You don't need to ask first: this setting only records that the note was shown.

The updates, newest first:
## 2026.11.26

- The Frontify skill now explains BDU's own blocks on the brand site (Font preview, AI prompt, Useful links): what each is for and how to add one, for example a new font.
- Logos and templates on the brand site are Dropbox links, not uploads, so updating the file in Dropbox updates the page. Claude makes the link and offers to connect your Dropbox first if it isn't yet.

## 2026.11.25.3

- **Three views of funding (data):** Claude now keeps all humanitarian funding, the Global Humanitarian Overview (GHO) plans and the prioritized GHO apart, and says which one each figure comes from.
- **More funding tables:** you can ask for prioritized figures by sector, plan, donor or recipient organization, and Claude can search the whole FTS dashboard for a table before saying it isn't there.
- **JPEG finals at full quality:** final JPEGs, including mockups, are now always exported at quality 100.

## 2026.11.25.2

- **Editable Illustrator files now look like the final:** textures, torn edges and shadows come in as images, one per piece, so they can still be moved.
- **Layers by meaning:** the .ai is organised into one layer per part of the design (background, heading, each section), each with its own text, shapes and images.
- **Layout tips in the graphic styles:** organise content in blocks with their own space, keep related things together, and let arrows leave a group from its middle.
