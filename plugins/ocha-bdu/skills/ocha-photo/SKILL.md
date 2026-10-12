---
name: ocha-photo
description: >
  Get and prepare OCHA photos for any BDU job — social media, video, reports, web, presentations. Covers
  MediaValet (OCHA's photo library at unocha.mediavalet.com): one-time setup and sign-in, downloading the
  TRUE original files from asset links, and reading each photo's credit and caption; the BDU default photo
  enhancement (tone and colour only, offered every time); and photo credits. Use whenever someone shares a
  MediaValet link, asks to "get the photos", "download from MediaValet", "find the credit", "photo credit",
  "enhance / improve / colour-correct the photos", "make the photos look better", or any job needs OCHA
  photos. Other OCHA skills (ocha-social-media, ocha-video, ocha-design) use this one for photos.
---

# OCHA photos (MediaValet, enhancement, credits)

OCHA photos are documentary evidence. Get the **original** file, credit it in the **OCHA credit format**
(§4), choose it with **dignity** in mind (§5), and only ever adjust **tone and colour** — never content.

Save files per `ocha-files-and-folders`: originals in `source/photos_mediavalet/`, enhanced versions in
`source/photos_enhanced/`, credits in `info/photos_and_credits.md`.

---

## 1. MediaValet — check the setup first

Photos come from the MediaValet API with `scripts/mediavalet.py`. Each Mac needs a **one-time setup**;
check it before the job (`python3 …/mediavalet.py info <any asset link>` works only when set up and signed in).

If it isn’t set up, tell the person:

*“To download photos from MediaValet I need a one-time setup on your Mac. Please **ask Javier Cueto
(cuetoj@un.org) for the MediaValet Client ID, Secret and Primary Key**. When you have them, I’ll open three
private boxes for you to paste them in — please don’t paste them into this chat. Then you sign in to
MediaValet once with the BDU team account.”*

```bash
python3 ~/.claude/skills/ocha-photo/scripts/mediavalet.py setup     # Client ID + Secret + Primary Key, private dialogs
python3 ~/.claude/skills/ocha-photo/scripts/mediavalet.py login     # browser sign-in, BDU team account (the person types the password)
```

- `setup` stores the three values only in `~/.claude/tokens.json` on that Mac. Never ask for them in chat,
  never write them into a job folder or a skill.
- `login` opens the MediaValet sign-in in the browser and waits up to 15 minutes. **The person signs in
  themselves** — never type a password. The tab then says “Signed in to MediaValet”.
- After that it stays signed in. If a command says the sign-in expired (long unused, or the account
  password changed), run `login` again.

## 2. Download originals and credits

```bash
python3 ~/.claude/skills/ocha-photo/scripts/mediavalet.py download <asset links or ids…> --out source/photos_mediavalet
```

- Accepts MediaValet asset links as people paste them (`…/assets/<id>/…`) or bare asset ids.
- Fetches the **true original** of each photo and checks its size against MediaValet’s record.
- Writes `credits.json` next to the photos: title, file, size, credit, caption, link per photo. Put the
  credits, in the OCHA format (§4), into `info/photos_and_credits.md`.
- `info <link>` prints an asset’s full metadata (keywords, categories, upload date…) when more is needed.
- **Read-only.** Never change anything in MediaValet (captions, credits, keywords, uploads) unless Javier
  explicitly asks — even to fix a credit’s capitalisation.

**Traps (already handled by the script — don’t “simplify” them away):** the asset’s `original`/`download`
links are the 1504 px preview despite their names, so originals come only through a MediaValet download
job; MediaValet’s firewall rejects Python’s default user agent; the job status check sometimes returns a
brief 503.

**Fallback — web app in Chrome** (setup not done yet, or the API is down): open each asset link → Show
details → note the credit (end of the description, “Credit: …”) → **Download → Advanced Download →
Custom → JPG, Original Size, sRGB, no watermark**; the zip arrives once “Ready for download” shows.
**Never Quick Download** — it gives the 1504 px preview.

## 3. Enhancement — the default, but always ask

The BDU default edit improves every photo a little: levels without a colour cast, gentle contrast, a slight
shadow lift (faces under headscarves open up), vibrance that spares skin and bright fabrics, light
sharpening. Tone and colour only, never content. It does most on hazy or flat photos and very little on
photos that are already good.

**Always ask before running it**, every job:

*“I usually apply BDU’s standard photo enhancement (tone and colour only — the originals are kept). Do you
want me to do it? I can show you a before/after first.”*

- If yes:
  ```bash
  python3 ~/.claude/skills/ocha-photo/scripts/enhance_photo.py source/photos_mediavalet/*.[jJ][pP]*[gG] --out source/photos_enhanced
  ```
  Use the enhanced files in the design; keep the originals untouched.
- If they want to see it first, make side-by-side before/after images in `info/` and show them.
- If no, use the originals as they are.
- Never retouch content (removing people, objects, logos), never use generative fill on documentary photos.

## 4. Credits, captions and names — OCHA brand rules

Source: OCHA brand portal → Social media & Campaigns → **Photography** (“Photo’s names, captions and
Photo Library”, “Photo guidance”, “Diversity and inclusivity guide”).

**Without a caption and a credit, a photo cannot be used.** If MediaValet has neither, stop and tell the person.

**Credit format** — credits must appear on every photo (and video) from OCHA and its partners; placement
can be discreet:

| Source | Credit |
|---|---|
| OCHA photo | `UNOCHA/First name Last name` |
| Partner photo | `Partner/First name Last name` |

- Take the photographer’s name from MediaValet (end of the description, “Credit: …”) and write it in this
  format, in normal capitalisation — e.g. MediaValet’s “UNOCHA/Irène NDILNODJI” becomes
  `UNOCHA/Irène Ndilnodji`. Tell the person whenever the MediaValet record differs from the standard,
  so the library record can be corrected too.
- In social media designs the credit line reads `Photo: UNOCHA/First Last`.
- One credit per photo, on the slide/page where that photo appears.
- If the credit is missing, or names a different organisation than the brief, **ask** — never invent or
  guess a credit.

**Captions** — required in OCHA’s photo library and in reports; **not required** on social media assets,
posters and outside reports. A full caption gives: location (village/city), full country name, date, the
“who”, the “what” (ideally a direct quote) and the “why” (context). Use the caption to check the copy:
flag any mismatch (place, fund, partner, date) to the requester rather than changing the copy.

**File names in the library** follow `[ISO3]_[MMYYYY]_UNOCHA_[camera number]`, e.g.
`AFG_032021_UNOCHA_DSC00349` or `TCD_062026_UNOCHA-5839`. Keep the original file names when saving.

## 5. Choosing photos — dignity and inclusion

When choosing or suggesting photos (not only when given links):

- **Dignity and respect.** Show people as whole human beings — needs and vulnerability, but also
  personality, strength and agency. Avoid images that reduce people to helplessness or suffering; don’t
  sanitise real situations either (the situation can be undignified, the person is not).
- **Avoid the single story.** Don’t repeat stereotypes of a place or group; vary angles and moments.
- **Informed consent.** Prefer photos where the caption shows the person agreed and understood the use;
  be careful with children and identifiable people in sensitive situations — ask if unsure.
- **Diversity and inclusion.** Follow OCHA’s *Diversity and Inclusivity in Imagery Guide* (PDF on the brand
  portal, OCHA staff only) — balanced representation of gender, age, disability and roles (people as
  actors, not only recipients).
- The image and its text work together: a dignified photo can be undone by its caption or copy, and vice versa.

---

## Project Owner

Javier Cueto, Head of Brand and Design Unit

## Maintained by

**OCHA Brand and Design Unit (BDU)**
- Team: ochavisual@un.org
- Focal point: Javier Cueto (cuetoj@un.org)
