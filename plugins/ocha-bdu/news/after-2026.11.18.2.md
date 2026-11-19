[OCHA BDU skills - what's new since this computer last checked]

Source: the OCHA BDU plugin (github.com/UN-OCHA/ocha_claude_skills_BDU), maintained by the OCHA Brand and Design Unit (ochavisual@un.org). Its skills were updated. This note appears once per update.

What to do, once in this session:
- At the end of your first reply, add a short section headed "What's new in the OCHA BDU skills" and say, in plain words and in the user's language, what changed: one short line per change, 4 lines at most. Write for designers, not developers: what they can now do or what now works differently. No file names, no version numbers.
- Then record that this note was shown, so it doesn't come back: in the Claude settings file (~/.claude/settings.json on a Mac, %USERPROFILE%\.claude\settings.json on Windows; create it if missing), keep everything already there and set, under "env": "OCHA_BDU_NEWS_SEEN": "2026.11.19.4". Check the file is still valid JSON. Change nothing else. You don't need to ask first: this setting only records that the note was shown.

The updates, newest first:
## 2026.11.19.4

- **Social media:** new layout tips from Javier: put text in the photo's empty spaces, keep it well clear of faces in portraits, let the gradient follow the text, and place the photo credit in a bottom corner on the margin.
- **Social media:** to make a country name stand out, set it one weight heavier than the rest of its line.

## 2026.11.19.3

- **Photos:** searching MediaValet by country ("find photos of Burkina Faso...") works again. It had stopped returning results.

## 2026.11.19.2

- **Brand site (ocha-frontify):** links Claude adds to brand.unocha.org now always use the page's permanent link, so they keep working when a page is renamed or moved.

## 2026.11.19

- **Funding data (ocha-data):** ask Claude for the link to the FTS funding dashboard, opened straight on any page, such as the Ebola 2026 one-pager.
- **Compress a PDF (ocha-utilities):** it now also shrinks PDFs with see-through images (common in Canva exports) and keeps long A4 reports sharp.

## 2026.11.18.3

- **Compress a PDF (ocha-utilities):** compressing a heavy Canva PDF is now much faster, with the same sharp photos and the same colours as before.
