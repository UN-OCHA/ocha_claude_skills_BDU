"""MediaValet API helper for BDU social media jobs.

Credentials live ONLY in ~/.claude/tokens.json (never in a skill, a job folder or the chat):
  mediavalet_client_id, mediavalet_client_secret, mediavalet_subscription_key
  mediavalet_refresh_token   (written by `login`, renewed on every use)

Commands:
  python3 mediavalet.py setup                 # one-time: Client ID + Secret + Primary Key via private dialogs (ask Javier Cueto)
  python3 mediavalet.py login                 # one-time browser sign-in (BDU team account)
  python3 mediavalet.py info <asset-url-or-id> # print the asset's metadata (JSON)
  python3 mediavalet.py download <asset-url-or-id>... --out <folder>
        # original files + <folder>/credits.json (title, file name, credit, caption, link)

Sign-in uses MediaValet's authorization-code flow with refresh tokens. The redirect URL
http://localhost:8765/callback must be whitelisted by MediaValet support for the client.
"""
import argparse
import http.server
import json
import os
import re
import secrets
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser

TOKENS = os.path.expanduser("~/.claude/tokens.json")
AUTH = "https://login.mediavalet.com"
API = "https://api.mediavalet.com"
REDIRECT = "http://localhost:8765/callback"
SCOPE = "openid api offline_access"
# MediaValet sits behind Cloudflare, which blocks Python's default "Python-urllib" user agent
# (error 1010, "browser signature"). Every request must send a normal user agent.
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) OCHA-BDU-MediaValet/1.0"}
UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


def load():
    if not os.path.exists(TOKENS):
        return {}
    with open(TOKENS) as f:
        return json.load(f)


def save(d):
    tmp = TOKENS + ".tmp"
    with open(tmp, "w") as f:
        json.dump(d, f, indent=2)
    os.chmod(tmp, 0o600)
    os.replace(tmp, TOKENS)


def creds():
    d = load()
    missing = [k for k in ("mediavalet_client_id", "mediavalet_client_secret",
                           "mediavalet_subscription_key") if not d.get(k)]
    if missing:
        sys.exit("MediaValet credentials missing in ~/.claude/tokens.json: " + ", ".join(missing))
    return d


def ask_private(prompt):
    """macOS dialog with hidden input: the value never touches the chat or the terminal output."""
    import subprocess
    script = (f'display dialog "{prompt}" default answer "" with hidden answer '
              f'with title "MediaValet — stored on this Mac only" buttons {{"Cancel","Save"}} default button "Save"')
    r = subprocess.run(["osascript", "-e", script, "-e", "text returned of result"], capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        sys.exit("Setup cancelled — nothing saved.")
    return r.stdout.strip()


def setup():
    print("Ask Javier Cueto (cuetoj@un.org) for the MediaValet Client ID, Secret and Primary Key, then paste them in the dialogs.")
    client_id = ask_private("Paste the MediaValet CLIENT ID (from Javier):")
    secret = ask_private("Paste the MediaValet SECRET (from Javier):")
    key = ask_private("Paste the MediaValet PRIMARY KEY (from Javier):")
    d = load()
    d.update(mediavalet_client_id=client_id, mediavalet_client_secret=secret, mediavalet_subscription_key=key)
    os.makedirs(os.path.dirname(TOKENS), exist_ok=True)
    save(d)
    print("Saved to ~/.claude/tokens.json. Next: python3 mediavalet.py login")


def token_request(form):
    d = creds()
    form = dict(form, client_id=d["mediavalet_client_id"], client_secret=d["mediavalet_client_secret"])
    req = urllib.request.Request(AUTH + "/connect/token", data=urllib.parse.urlencode(form).encode(),
                                 headers={"Content-Type": "application/x-www-form-urlencoded", **UA})
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        # Never print the request (it carries the secret); the server's error text is safe.
        sys.exit(f"MediaValet sign-in failed ({e.code}): {e.read().decode(errors='replace')[:300]}")


def access_token():
    d = load()
    rt = d.get("mediavalet_refresh_token")
    if not rt:
        sys.exit("Not signed in to MediaValet yet. Run: python3 mediavalet.py login")
    t = token_request({"grant_type": "refresh_token", "refresh_token": rt})
    if t.get("refresh_token"):            # refresh tokens rotate: keep the newest one
        d = load()
        d["mediavalet_refresh_token"] = t["refresh_token"]
        save(d)
    return t["access_token"]


def login():
    d = creds()
    state = secrets.token_urlsafe(16)
    got = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = {k: v[0] for k, v in urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).items()}
            # Ignore anything that isn't THIS sign-in (stale tabs, browser retries, favicon):
            # only a callback carrying our state value counts.
            if q.get("state") == state:
                got.update(q)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            if not got:
                msg = "Old or unrelated sign-in link ignored. Use the newest MediaValet sign-in tab."
            elif "code" in got:
                msg = "Signed in to MediaValet. You can close this tab."
            else:
                msg = "MediaValet sign-in did not complete: " + got.get("error", "unknown error")
            self.wfile.write(f"<p style='font-family:sans-serif'>{msg}</p>".encode())

        def log_message(self, *a):
            pass

    # Dual-stack listener: browsers may resolve "localhost" to ::1 (IPv6) or 127.0.0.1 (IPv4).
    # An IPv4-only listener silently loses the callback when the browser picks ::1.
    import socket

    class DualStack(http.server.HTTPServer):
        address_family = socket.AF_INET6

        def server_bind(self):
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            super().server_bind()

    srv = DualStack(("::", 8765), H)
    url = AUTH + "/connect/authorize?" + urllib.parse.urlencode({
        "client_id": d["mediavalet_client_id"], "response_type": "code", "scope": SCOPE,
        "redirect_uri": REDIRECT, "state": state})
    if os.environ.get("MV_NO_BROWSER"):      # for driving the sign-in from a specific browser tab
        print("SIGN-IN URL:", url, flush=True)
    else:
        print("Opening the MediaValet sign-in in your browser…", flush=True)
        webbrowser.open(url)
    import time
    deadline = time.time() + 900           # 15 min: time to find the tab and sign in
    srv.timeout = 5
    while not got and time.time() < deadline:
        srv.handle_request()
    if not got:
        sys.exit("Timed out waiting for the MediaValet sign-in (15 min). Run login again.")
    if "code" not in got:
        sys.exit("Sign-in failed: " + got.get("error_description", got.get("error", "no code returned")))
    t = token_request({"grant_type": "authorization_code", "code": got["code"], "redirect_uri": REDIRECT})
    if not t.get("refresh_token"):
        sys.exit("Signed in, but MediaValet returned no refresh token (offline_access not enabled?).")
    d = load()
    d["mediavalet_refresh_token"] = t["refresh_token"]
    save(d)
    print("Signed in. Refresh token stored in ~/.claude/tokens.json.")


def api_get(path, token):
    d = creds()
    req = urllib.request.Request(API + path, headers={
        **UA,
        "Authorization": "Bearer " + token,
        "Ocp-Apim-Subscription-Key": d["mediavalet_subscription_key"],
        "x-mv-api-version": "1.2", "Accept": "application/json"})
    import time
    for attempt in range(5):                 # MediaValet returns brief 502/503/504s, notably on job status
        try:
            with urllib.request.urlopen(req) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and attempt < 4:
                time.sleep(3 * (attempt + 1))
                continue
            sys.exit(f"MediaValet API error {e.code} on {path}: {e.read().decode(errors='replace')[:300]}")


def credit_from(description):
    """OCHA captions end with 'Credit: UNOCHA/Name' — return 'UNOCHA/Name' or ''."""
    m = re.search(r"Credit:\s*(.+?)\s*$", description or "", re.S)
    return m.group(1).strip() if m else ""


def api_post(path, token, body):
    d = creds()
    req = urllib.request.Request(API + path, method="POST", data=json.dumps(body).encode(), headers={
        **UA, "Authorization": "Bearer " + token, "Ocp-Apim-Subscription-Key": d["mediavalet_subscription_key"],
        "x-mv-api-version": "1.2", "Accept": "application/json", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"MediaValet API error {e.code} on {path}: {e.read().decode(errors='replace')[:300]}")


def download(assets, out):
    """Download ORIGINAL files through MediaValet's Downloads service.

    Do NOT use media.original / media.download from the asset: despite the names they point to the
    1504 px "Large" preview (same trap as Quick Download in the web app). The real original only
    comes from a download job with shareOriginals=true, delivered as a zip.
    """
    import time
    import zipfile
    os.makedirs(out, exist_ok=True)
    token = access_token()
    ids = [asset_id(a) for a in assets]
    meta = {}
    for aid, link in zip(ids, assets):
        a = api_get("/assets/" + aid, token)["payload"]
        f = a.get("file") or {}
        desc = a.get("description") or f.get("description") or ""
        meta[aid] = {"asset_id": aid, "title": a.get("title"), "file": f.get("fileName"),
                     "expected_bytes": f.get("sizeInBytes"), "width": f.get("imageWidth"),
                     "height": f.get("imageHeight"), "credit": credit_from(desc), "caption": desc, "link": link}
    job = api_post("/downloads", token, {"downloadSettingsPostDetail": {
        "allowsAssetDownload": True,
        "images": {"shareOriginals": True, "renditionType": "Original"},
        "ids": ids, "zipFileName": "bdu_originals"}})
    bid = job["payload"]["batchId"]
    deadline = time.time() + 600
    while True:
        st = api_get("/downloads/" + bid, token)["payload"]
        if str(st.get("status")).lower() == "completed" and st.get("processedCount") == st.get("itemCount"):
            break
        if str(st.get("status")).lower() in ("failed", "error", "cancelled"):
            sys.exit(f"MediaValet download job {bid} ended with status {st.get('status')}.")
        if time.time() > deadline:
            sys.exit(f"MediaValet download job {bid} not ready after 10 min (status {st.get('status')}).")
        time.sleep(5)
    zpath = os.path.join(out, ".bdu_originals.zip")
    with urllib.request.urlopen(urllib.request.Request(st["filePath"], headers=UA)) as r, open(zpath, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    with zipfile.ZipFile(zpath) as z:
        names = [n for n in z.namelist() if not n.endswith("/")]
        for n in names:                     # flatten: files go straight into `out`
            target = os.path.join(out, os.path.basename(n))
            with z.open(n) as src, open(target, "wb") as dst:
                dst.write(src.read())
    os.remove(zpath)
    records, problems = [], []
    by_stem = {os.path.splitext(os.path.basename(n))[0].lower(): os.path.basename(n) for n in names}
    for aid in ids:
        m = meta[aid]
        stem = os.path.splitext(m["file"] or m["title"] or aid)[0].lower()
        got = by_stem.get(stem)
        if not got:
            problems.append(f"{m['title']}: not found in the download zip")
            continue
        size = os.path.getsize(os.path.join(out, got))
        if m["expected_bytes"] and int(m["expected_bytes"]) != size:
            problems.append(f"{got}: {size} bytes, MediaValet says the original is {m['expected_bytes']}")
        m.update(file=got, bytes=size)
        records.append(m)
        print(f"{got}  {m['width']}x{m['height']}  {size/1e6:.1f} MB  credit: {m['credit'] or '(none found)'}")
    with open(os.path.join(out, "credits.json"), "w") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    if problems:
        sys.exit("Downloaded, but check these:\n  " + "\n  ".join(problems))


def asset_id(s):
    ids = UUID.findall(s)
    if not ids:
        sys.exit(f"No asset id found in: {s}")
    return ids[-1]                        # in a browse URL the asset id comes after the category id


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup")
    sub.add_parser("login")
    i = sub.add_parser("info")
    i.add_argument("asset")
    dl = sub.add_parser("download")
    dl.add_argument("assets", nargs="+")
    dl.add_argument("--out", required=True)
    args = ap.parse_args()
    if args.cmd == "setup":
        setup()
    elif args.cmd == "login":
        login()
    elif args.cmd == "info":
        print(json.dumps(api_get("/assets/" + asset_id(args.asset), access_token()), indent=2)[:6000])
    elif args.cmd == "download":
        download(args.assets, args.out)


if __name__ == "__main__":
    main()
