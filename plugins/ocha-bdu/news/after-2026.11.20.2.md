[OCHA BDU skills - what's new since this computer last checked]

Source: the OCHA BDU plugin (github.com/UN-OCHA/ocha_claude_skills_BDU), maintained by the OCHA Brand and Design Unit (ochavisual@un.org). Its skills were updated. This note appears once per update.

What to do, once in this session:
- At the end of your first reply, add a short section headed "What's new in the OCHA BDU skills" and say, in plain words and in the user's language, what changed: one short line per change, 4 lines at most. Write for designers, not developers: what they can now do or what now works differently. No file names, no version numbers.
- Then record that this note was shown, so it doesn't come back: in the Claude settings file (~/.claude/settings.json on a Mac, %USERPROFILE%\.claude\settings.json on Windows; create it if missing), keep everything already there and set, under "env": "OCHA_BDU_NEWS_SEEN": "2026.11.23.2". Check the file is still valid JSON. Change nothing else. You don't need to ask first: this setting only records that the note was shown.

The updates, newest first:
## 2026.11.23.2

- **Logos (ocha-logo-production):** clearer advice for sharing logo files from Dropbox: make the link by hand in Dropbox (Share -> "Anyone with the link") and test it in a private window, because the link Claude's Dropbox connector makes only opens for OCHA team members.
- **Charts, maps, brand and design (ocha-dataviz, ocha-mapping, ocha-visual-identity, ocha-design):** removed pointers to internal BDU tools you don't have installed.

## 2026.11.23

- **Photos (ocha-photo):** a new point on sensitive photos: a recognisable woman at the door of her own home can be identified and found, however beautiful the photo. Weigh it case by case, and when in doubt pick people seen from behind or at a distance, or let the shelters and objects tell the story.
- **Social media (ocha-social-media):** Claude now uses the latest cleared copy from the Trello comments, can bold just a few words in a text box, and accepts a manual line break when no box width avoids a short last line.

## 2026.11.21

- **Social media (ocha-social-media):** Claude now does the Canva steps that need Chrome (fonts, guides, transitions) straight away, without stopping to ask each time.
- **Social media (ocha-social-media):** new layout tips: crop a wide group photo to one clear subject on 3:4 slides, choose photos that show what the figure says, and use a soft shade behind small labels on busy photos.
- **Photos (ocha-photo):** searching MediaValet by country works best with the country's name, not its three-letter code.
