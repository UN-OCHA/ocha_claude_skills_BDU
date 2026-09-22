#!/usr/bin/env python3
"""Review tool for OCHA videos and animations: watch a render, click the frame, leave a comment.

    python3 review_server.py --videos <folder of renders> --comments <job>/info/review/<name>_review.json \\
        [--timeline <job>/assets/build/timeline.json] [--title "Film name"] [--author "Name"] [--port 8765]
    # then open http://localhost:8765

Every comment keeps the render it was made on, the exact frame, and the point (or box) clicked on
the picture, so Claude can open that very frame without asking where or when. Claude answers in the
same file through this server's API while it runs (reply, status, fixedIn — see
references/review-tool.md); the page picks that up on its own within a few seconds.
The timeline is optional: an animation's timeline.json adds the scene and the words being spoken
under the player.

Local only: the server listens on this Mac alone and the video never leaves it. Standard library only.
The look is the OCHA App Kit (vendor/ocha-app-kit.css — synced by the design system's
app-kit/sync.py, never edited here) with the official OCHA logo (ocha-logo.svg, the 2024
horizontal blue file, untouched). Built for the SG Awards 2026 film (BDU).
"""
import argparse, json, os, re, secrets, threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

HERE = Path(__file__).resolve().parent
KIT = HERE / "vendor/ocha-app-kit.css"
FAVICON = HERE / "vendor/favicon.svg"
LOGO = HERE / "ocha-logo.svg"
STATUSES = {"open", "fixed", "ok"}   # open → fixed (Claude, with the version) → ok ("Looks good", the reviewer)
LOCK = threading.Lock()
STATIC = {"/": ("review.html", "text/html; charset=utf-8"), "/review.js": ("review.js", "text/javascript; charset=utf-8"),
          "/review.css": ("review.css", "text/css; charset=utf-8")}
CFG = {}   # set from the command line in main()


def videos():
    """Every render in the folder, newest first."""
    out = [{"name": p.name, "size": p.stat().st_size, "mtime": p.stat().st_mtime} for p in CFG["videos"].glob("*.mp4")]
    return sorted(out, key=lambda v: -v["mtime"])


def load():
    store = CFG["comments"]
    if not store.exists():
        return {"film": CFG["title"], "fps": CFG["fps"], "comments": []}
    return json.loads(store.read_text(encoding="utf-8"))


def save(data):
    store = CFG["comments"]
    store.parent.mkdir(parents=True, exist_ok=True)
    tmp = store.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, store)   # atomic: a crash never leaves half a file


def num(v, lo, hi):
    v = float(v)
    return min(max(v, lo), hi)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):   # quiet, except for failures
        if args and str(args[1])[:1] in "45":
            super().log_message(fmt, *args)

    def send_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path, ctype):
        """With byte ranges: the browser needs them to seek in a video."""
        size = path.stat().st_size
        start, end, rng = 0, size - 1, self.headers.get("Range")
        m = re.match(r"bytes=(\d*)-(\d*)$", rng or "")
        if m and (m.group(1) or m.group(2)):
            if m.group(1):
                start = int(m.group(1)); end = int(m.group(2)) if m.group(2) else size - 1
            else:
                start = max(0, size - int(m.group(2)))
            end = min(end, size - 1)
            if start > end:
                self.send_response(416); self.send_header("Content-Range", f"bytes */{size}"); self.end_headers(); return
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-cache")   # a re-render under the same name must show up
        self.send_header("Last-Modified", self.date_time_string(int(path.stat().st_mtime)))
        self.end_headers()
        try:
            with open(path, "rb") as f:
                f.seek(start)
                left = end - start + 1
                while left > 0:
                    chunk = f.read(min(1 << 16, left))
                    if not chunk:
                        break
                    self.wfile.write(chunk); left -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass   # the browser drops ranges it no longer needs while seeking

    def read_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        p = urlparse(self.path).path
        if p in STATIC:
            name, ctype = STATIC[p]
            return self.send_file(HERE / name, ctype)
        if p == "/kit.css":
            if not KIT.exists():   # fail loudly: the page must not quietly lose the OCHA look
                return self.send_error(500, f"OCHA App Kit not found at {KIT}")
            return self.send_file(KIT, "text/css; charset=utf-8")
        if p == "/logo.svg":
            return self.send_file(LOGO, "image/svg+xml")
        if p in ("/favicon.ico", "/favicon.svg") and FAVICON.exists():
            return self.send_file(FAVICON, "image/svg+xml")
        if p == "/api/config":
            return self.send_json({"title": CFG["title"], "fps": CFG["fps"], "videos": str(CFG["videos"])})
        if p == "/api/videos":
            return self.send_json(videos())
        if p.startswith("/video/"):
            name = unquote(p[len("/video/"):])
            if name not in {v["name"] for v in videos()}:
                return self.send_error(404)
            return self.send_file(CFG["videos"] / name, "video/mp4")
        if p == "/api/timeline":
            if CFG["timeline"]:
                return self.send_file(CFG["timeline"], "application/json; charset=utf-8")
            return self.send_json({"scenes": [], "lines": []})   # a video with no timeline: no scene names under the player
        if p == "/api/comments":
            with LOCK:
                return self.send_json(load())
        self.send_error(404)

    def do_HEAD(self):   # health checks ask for headers only
        if urlparse(self.path).path in STATIC:
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):   # a new comment
        if urlparse(self.path).path != "/api/comments":
            return self.send_error(404)
        try:
            b = self.read_json()
            if b.get("video") not in {v["name"] for v in videos()}:
                raise ValueError("unknown video")
            frame = int(num(b.get("frame", 0), 0, 10 ** 6))
            text = str(b.get("text", "")).strip()[:4000]
            if not text:
                raise ValueError("empty comment")
            c = {"id": "c" + secrets.token_hex(3), "video": b["video"], "frame": frame, "t": round(frame / CFG["fps"], 3),
                 "x": round(num(b.get("x", 0.5), 0, 1), 4), "y": round(num(b.get("y", 0.5), 0, 1), 4),
                 "w": round(num(b.get("w", 0), 0, 1), 4), "h": round(num(b.get("h", 0), 0, 1), 4),
                 "text": text, "author": CFG["author"], "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 "status": "open", "reply": "", "fixedIn": ""}
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            return self.send_json({"error": str(e)}, 400)
        with LOCK:   # read, change, write: never overwrites what Claude wrote meanwhile
            data = load(); data["comments"].append(c); save(data)
        self.send_json(c, 201)

    def do_PATCH(self):   # the page: edit the text, set the status. Claude: reply, fixedIn (through here while the server runs, so nothing races)
        m = re.match(r"^/api/comments/(c[0-9a-f]+)$", urlparse(self.path).path)
        if not m:
            return self.send_error(404)
        try:
            b = self.read_json()
        except json.JSONDecodeError as e:
            return self.send_json({"error": str(e)}, 400)
        with LOCK:
            data = load()
            c = next((c for c in data["comments"] if c["id"] == m.group(1)), None)
            if c is None:
                return self.send_json({"error": "no such comment"}, 404)
            if "text" in b and str(b["text"]).strip():
                c["text"] = str(b["text"]).strip()[:4000]
            if b.get("status") in STATUSES:
                c["status"] = b["status"]
            if "reply" in b:
                c["reply"] = str(b["reply"]).strip()[:4000]
            if "fixedIn" in b:
                c["fixedIn"] = str(b["fixedIn"])[:200]
            save(data)
        self.send_json(c)

    def do_DELETE(self):
        m = re.match(r"^/api/comments/(c[0-9a-f]+)$", urlparse(self.path).path)
        if not m:
            return self.send_error(404)
        with LOCK:
            data = load()
            before = len(data["comments"])
            data["comments"] = [c for c in data["comments"] if c["id"] != m.group(1)]
            if len(data["comments"]) == before:
                return self.send_json({"error": "no such comment"}, 404)
            save(data)
        self.send_json({"deleted": m.group(1)})


def main():
    ap = argparse.ArgumentParser(description="OCHA review tool: comments on exact frames of a video's renders.")
    ap.add_argument("--videos", required=True, help="folder of renders (.mp4) to review")
    ap.add_argument("--comments", required=True, help="the comments file, e.g. <job>/info/review/<name>_review.json")
    ap.add_argument("--timeline", help="optional: an animation's timeline.json (scenes and spoken lines)")
    ap.add_argument("--title", help="shown in the header (default: the comments file's name)")
    ap.add_argument("--author", default=os.environ.get("REVIEW_AUTHOR", "Reviewer"), help="name stored with new comments")
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8765")))
    ap.add_argument("--fps", type=int, default=30)
    a = ap.parse_args()
    CFG.update(videos=Path(a.videos).expanduser().resolve(), comments=Path(a.comments).expanduser().resolve(),
               timeline=Path(a.timeline).expanduser().resolve() if a.timeline else None, author=a.author, fps=a.fps)
    CFG["title"] = a.title or CFG["comments"].stem.replace("_review", "").replace("_", " ")
    for need in [CFG["videos"], KIT, LOGO] + ([CFG["timeline"]] if CFG["timeline"] else []):
        if not need.exists():
            raise SystemExit(f"Missing: {need}")
    print(f"Review: http://localhost:{a.port}  ·  renders from {CFG['videos']}  ·  comments → {CFG['comments']}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", a.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
