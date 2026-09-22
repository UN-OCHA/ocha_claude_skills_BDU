# The review tool — comments on exact frames

For every OCHA video and animation. `ocha-video` keeps it (`scripts/review/`), `ocha-animation`
points here. Built for the SG Awards 2026 film, where it carried about 75 comments over seven rounds
in three days.

A local page that plays the renders of a job. The reviewer pauses anywhere, clicks the picture (or
drags an area) and types. Every comment is saved with **the render, the exact frame and the spot**,
so Claude can open that very frame without asking where or when, and answers in the same place.
Local only: it runs on this Mac and the video never leaves it.

## Start it

```bash
python3 <this skill>/scripts/review/review_server.py \
  --videos "<job>/assets/build/previews" \
  --comments "<job>/info/review/<job_name>_review.json" \
  --title "<Film name>" --author "<reviewer’s first name>" \
  [--timeline "<job>/assets/build/timeline.json"]   # an animation: shows the scene and the words spoken
# → http://localhost:8765
```

In the Claude desktop app, give it an entry in the project’s `.claude/launch.json` and start it
with `preview_start`, so it opens in the app’s browser pane:

```json
{ "name": "<job>-review", "runtimeExecutable": "python3",
  "runtimeArgs": ["<skill path>/scripts/review/review_server.py", "--videos", "…", "--comments", "…", "--title", "…"],
  "port": 8765 }
```

The app stops preview servers from time to time: when the person says the page is down, start it
again (the comments are safe in the file).

## The loop

1. **Render** into `previews/`, numbered: `<job_name>_film_v07.mp4`. Variants add words after the
   version, which the list shows: `…_v07_no_voice.mp4` → “v07 · no voice”;
   `…_v06_music_02_reveal.mp4` → “v06 · music: Reveal”. Add a no-voice copy whenever sound is being
   reviewed (`mix.py --no-voice`).
2. **The reviewer comments.** Status **open**.
3. **Claude fixes, renders, and answers every comment it fixed**, through the server while it runs:
   ```
   PATCH /api/comments/<id>   {"status": "fixed", "reply": "v08: <what changed, in plain words>", "fixedIn": "<job_name>_film_v08.mp4"}
   ```
   One reply per comment, starting with the version. When the same point was made in several
   comments, answer each. If something needs the reviewer’s choice first (options to hear or see),
   say so in the reply and leave it **open**.
4. **The reviewer checks** and marks it **“Looks good”** (status `ok`), or reopens it with a new
   comment on top.

Never edit the comments file by hand while the server runs: it would overwrite what the page
writes. Read it any time (`GET /api/comments` or the file itself) to see what is open.

## Reading a comment

`{"video", "frame", "t", "x", "y", "w", "h", "text", "status", "reply", "fixedIn"}` — `t` is the time
in seconds (frame / 30); `x, y` the spot as a share of the picture’s width and height (`w, h` > 0 for
an area). For an animation, open the page at that moment (`world.html?t=25.733`) or pull that frame
from the render (`ffmpeg -ss 25.733 -i <render> -frames:v 1 …`).

## Closing the job

When the final is out, the renders in `previews/` go (the person decides: delete or archive —
`ocha-files-and-folders`). The comments file stays in `info/review/` as the record of every decision.

The look is the OCHA App Kit: `vendor/ocha-app-kit.css` is kept current by the design system’s
`app-kit/sync.py` (this tool is registered in its `apps.json`). Never edit it here.
