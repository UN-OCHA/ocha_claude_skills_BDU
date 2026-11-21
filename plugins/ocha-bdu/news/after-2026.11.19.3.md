[OCHA BDU skills - what's new since this computer last checked]

Source: the OCHA BDU plugin (github.com/UN-OCHA/ocha_claude_skills_BDU), maintained by the OCHA Brand and Design Unit (ochavisual@un.org). Its skills were updated. This note appears once per update.

What to do, once in this session:
- At the end of your first reply, add a short section headed "What's new in the OCHA BDU skills" and say, in plain words and in the user's language, what changed: one short line per change, 4 lines at most. Write for designers, not developers: what they can now do or what now works differently. No file names, no version numbers.
- Then record that this note was shown, so it doesn't come back: in the Claude settings file (~/.claude/settings.json on a Mac, %USERPROFILE%\.claude\settings.json on Windows; create it if missing), keep everything already there and set, under "env": "OCHA_BDU_NEWS_SEEN": "2026.11.21". Check the file is still valid JSON. Change nothing else. You don't need to ask first: this setting only records that the note was shown.

The updates, newest first:
## 2026.11.21

- **Social media (ocha-social-media):** Claude now does the Canva steps that need Chrome (fonts, guides, transitions) straight away, without stopping to ask each time.
- **Social media (ocha-social-media):** new layout tips: crop a wide group photo to one clear subject on 3:4 slides, choose photos that show what the figure says, and use a soft shade behind small labels on busy photos.
- **Photos (ocha-photo):** searching MediaValet by country works best with the country's name, not its three-letter code.

## 2026.11.20.2

- **Photos (ocha-photo):** downloading from MediaValet now works on Windows too, and photographer names in any alphabet are kept correctly in the credits.

## 2026.11.20

- **Brand site (ocha-frontify):** Claude now stops before putting one uploaded image on two blocks, so deleting a test section can no longer blank an image on a live page.

## 2026.11.19.4

- **Social media:** new layout tips from Javier: put text in the photo's empty spaces, keep it well clear of faces in portraits, let the gradient follow the text, and place the photo credit in a bottom corner on the margin.
- **Social media:** to make a country name stand out, set it one weight heavier than the rest of its line.
