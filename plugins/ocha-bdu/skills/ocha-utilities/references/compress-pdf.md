# Compress a PDF

For PDFs that are too heavy to send or upload, above all **Canva exports**. Canva saves every page as one
uncompressed 300 ppi image, so a 7-page carousel can reach 136 MB. This tool brings it down 6–8 times
(136 MB → 22 MB) with no visible loss.

## Run it

```bash
python3 ~/.claude/skills/ocha-utilities/scripts/compress_pdf.py "input.pdf"
```

- It writes `input_compressed.pdf` next to the original and never changes the original.
- It prints the new size and a similarity score per page. Above 45 dB the difference can’t be seen.
- Needs PyMuPDF, Pillow and numpy (`pip install pymupdf pillow numpy` if missing).

## Settings

| Need | Option | Typical result (7-page Canva carousel) |
|---|---|---|
| Default: looks identical, full resolution | `--quality 95` (default) | 136 MB → 22 MB |
| Smaller, still no visible loss | `--quality 90` | about 16 MB |
| Screen only (email, Teams), never print | `--max-ppi 150` | about 5 MB |

Use the default unless the person asks for smaller. Never go below quality 85 for photos.

## What it does

- Re-encodes every image as JPEG at the same resolution, with full colour detail (4:4:4 chroma), so text
  on top of photos stays sharp.
- Skips images it can’t improve: transparency, unusual colour spaces, or images already smaller than the
  JPEG would be.

## The colour trap — why the script writes the images itself

Canva leaves its images **without a colour profile**. On a Mac with a wide-gamut screen, the colours then
go to the display unconverted and look extra saturated. Most PDF tools (including PyMuPDF’s
`replace_image`) **add an sRGB profile** when they re-encode. That is technically correct, but the photos
then look visibly flatter than the original, and people notice. The script keeps each image’s original
colour space, so the compressed PDF looks exactly like the original.

If someone says the compressed file looks “less punchy”, check the image colour spaces with
`pdfimages -list` (column `color`: `rgb` = no profile, as Canva; `icc` = a profile was added).

## Check before delivering

Open the compressed PDF next to the original at 100 % and compare a photo with skin tones and a block of
small text. The person decides if it’s good enough.
