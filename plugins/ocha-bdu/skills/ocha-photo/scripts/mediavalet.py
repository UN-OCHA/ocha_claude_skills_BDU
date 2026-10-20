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
  python3 mediavalet.py search "<plain description>" --out <folder> [--country SDN] [--year 2026]
        # MediaValet's AI search; <folder>/results.json + contact_sheet.jpg to choose from

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


def api_get(path, token, retry_500=False):
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
            # 500 is retried only where asked: the download-job status check throws a server-side
            # NullReferenceException when polled a moment after the job is created.
            if (e.code in (429, 502, 503, 504) or (retry_500 and e.code == 500)) and attempt < 4:
                time.sleep(3 * (attempt + 1))
                continue
            sys.exit(f"MediaValet API error {e.code} on {path}: {e.read().decode(errors='replace')[:300]}")


def credit_from(description, organisation="", photographer=""):
    """OCHA captions end with 'Credit: UNOCHA/Name'. Partner photos often use '© Name/ WFP' instead:
    that is returned as 'WFP/Name', the OCHA order. '' when there is neither."""
    m = re.search(r"Credit:\s*(.+?)\s*$", description or "", re.S)
    if m:
        return m.group(1).strip()
    m = re.search(r"©\s*([^/\n]+?)\s*/\s*([^\n]+?)\s*$", description or "")
    if m:
        return f"{m.group(2).strip()}/{m.group(1).strip()}"
    # Many photos keep the credit only in MediaValet's Copyright + Photographer fields.
    if organisation and photographer:
        return f"{organisation.strip()}/{photographer.strip()}"
    return ""


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
    names = attribute_names(token)
    ids = [asset_id(a) for a in assets]
    meta = {}
    for aid, link in zip(ids, assets):
        a = api_get("/assets/" + aid, token)["payload"]
        f = a.get("file") or {}
        desc = a.get("description") or f.get("description") or ""
        fields = {names.get(k, "").lower(): str(v or "") for k, v in (a.get("attributes") or {}).items()}
        meta[aid] = {"asset_id": aid, "title": a.get("title"), "file": f.get("fileName"),
                     "expected_bytes": f.get("sizeInBytes"), "width": f.get("imageWidth"),
                     "height": f.get("imageHeight"),
                     "credit": credit_from(desc, fields.get("copyright", ""), fields.get("photographer", "")),
                     "caption": desc, "link": link, "web_link": asset_link(aid)}
    job = api_post("/downloads", token, {"downloadSettingsPostDetail": {
        "allowsAssetDownload": True,
        "images": {"shareOriginals": True, "renditionType": "Original"},
        "ids": ids, "zipFileName": "bdu_originals"}})
    bid = job["payload"]["batchId"]
    time.sleep(3)                            # give MediaValet a moment to register the job
    deadline = time.time() + 600
    while True:
        st = api_get("/downloads/" + bid, token, retry_500=True)["payload"]
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


def attribute_names(token):
    """Library attribute id -> name (Country, Date Created, Photographer, Copyright…). The ids are
    specific to OCHA's library, so look them up by name rather than hardcoding them."""
    p = api_get("/attributes", token).get("payload", [])
    return {a["id"]: a.get("name", "") for a in (p if isinstance(p, list) else p.get("attributes", []))}


def caption_year(desc):
    """Year of the date an OCHA caption opens with ("Kebe Town, Oromia, ETHIOPIA. 10 February 2025.",
    "27 May 2025, China camp…", "Gaza, October 2025."). Only the opening is read: later years in the
    caption are context ("Since February 2025…", "In August 2025, clashes…"), not when it was taken."""
    m = re.search(r"\b(20\d\d)\b", (desc or "")[:120])
    return m.group(1) if m else ""


def search(query, out, country=None, year=None, count=40, pool=400):
    """Find photos with MediaValet's AI search (the same as the sparkle "Smart Search" in the web app).

    useSemanticSearch=true matches on meaning and on what is in the picture, so a plain description
    ("aid workers distributing food in Sudan") works. A keyword search for the same sentence returns
    nothing. Semantic search ranks by meaning only: it happily returns South Sudan for "Sudan" and
    2024 for "2026", so --country and --year filter on the photo's own metadata afterwards.

    Writes <out>/results.json and <out>/contact_sheet.jpg (numbered thumbnails) for choosing.
    """
    from io import BytesIO
    token = access_token()
    names = attribute_names(token)
    # The ranking only knows what is in the sentence: a country left out of the query is ranked out
    # before the filter ever sees it (Sudan 2026 aid workers: 10 of 200 without "Sudan", 24 with it).
    if country and len(country) > 3 and country.lower() not in query.lower():
        query = f"{query} {country}"
    if year and str(year) not in query:
        query = f"{query} {year}"
    found, offset = [], 0
    while offset < pool:
        page = api_post("/assets/search", token, {
            "search": query, "count": min(100, pool - offset), "offset": offset,
            "useSemanticSearch": True, "includeTotalCount": True, "includeSoftDeleted": False})
        p = page.get("payload", page)
        assets = p.get("assets", []) if isinstance(p, dict) else []
        if not assets:
            break
        found += assets
        offset += len(assets)

    def attr(a, name):
        for k, v in (a.get("attributes") or {}).items():
            if names.get(k, "").lower() == name.lower():
                return str(v or "")
        return ""

    results = []
    for a in found:
        if (a.get("media") or {}).get("type") not in (None, "Image"):
            continue
        title = a.get("title") or ""
        desc = a.get("description") or (a.get("file") or {}).get("description") or ""
        ctry = attr(a, "Country")
        taken = attr(a, "Date Created")[:10]
        code = title[:3].upper() if re.match(r"[A-Za-z]{3}_", title) else ""
        m = re.match(r"[A-Za-z]{3}_(\d{2})(\d{4})_", title)          # ISO3_MMYYYY_ in OCHA file names
        # When was the photo TAKEN? Never the upload date (photos are often uploaded months later).
        # Evidence, strongest first: the date the caption opens with ("Place, Country. 6 May 2025."),
        # then the ISO3_MMYYYY_ file name, then the camera date (sometimes unset, or stamped 2014/2016).
        # A year mentioned elsewhere in the caption does NOT count: "In August 2025, clashes forced
        # them to flee…" sat on a photo taken in May 2026 and slipped into a 2025 search.
        cap_year = caption_year(desc)
        file_year = m.group(2) if m else ""
        yr = cap_year or file_year or taken[:4]
        known = {y for y in (cap_year, file_year, taken[:4]) if y}
        # cap/file disagreeing is a real conflict; a lone odd camera year is usually a mis-set clock
        date_note = ""
        conflict = bool(cap_year and file_year and cap_year != file_year)
        if conflict:
            date_note = f"dates disagree: caption {cap_year}, file name {file_year}, camera {taken[:4] or '?'}"
        elif len(known) > 1:
            date_note = f"camera date {taken[:4]} differs from caption/file name {yr}"
        if country:
            c = country.strip().lower()
            ok = (c == code.lower()) or (c == ctry.lower())
            # caption fallback, without letting "Sudan" match "South Sudan"
            if not ok and not code and not ctry:
                ok = bool(re.search(r"(?<!south )\b" + re.escape(c) + r"\b", desc.lower()))
            if not ok:
                continue
        # Keep a photo whose sources disagree if any of them matches, flagged: a caption typo
        # ("12 January 2024" in a shoot of 12 January 2025) must not hide it. The person decides.
        if year and str(year) != yr and not (conflict and str(year) in known):
            continue
        results.append({"n": len(results) + 1, "asset_id": a["id"], "title": title, "country": ctry or code,
                        "date_taken": taken or (f"{m.group(2)}-{m.group(1)}" if m else ""),
                        "year_taken": yr, "date_check": date_note,
                        "photographer": attr(a, "Photographer"), "organisation": attr(a, "Copyright"),
                        "credit": credit_from(desc, attr(a, "Copyright"), attr(a, "Photographer")),
                        "caption": desc.strip(), "web_link": asset_link(a["id"]),
                        "thumb": (a.get("media") or {}).get("medium") or (a.get("media") or {}).get("small")})
        if len(results) >= count:
            break

    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "results.json"), "w") as f:
        json.dump([{k: v for k, v in r.items() if k != "thumb"} for r in results], f, indent=2, ensure_ascii=False)
    print(f"{len(found)} photos matched the meaning; {len(results)} kept after filters.")
    for r in results:
        print(f"{r['n']:>3}. {r['title']}  [{r['country']} {r['year_taken']}]  {r['credit'] or r['organisation']}")
        if r["date_check"]:
            print(f"     ⚠ {r['date_check']}")
        print(f"     {r['caption'][:160]}")
    if not results:
        return
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("(Pillow not installed: no contact sheet. Thumbnails are not needed to choose by caption.)")
        return
    W, H, cols = 320, 240, 5
    rows = (len(results) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * W, rows * (H + 28)), "white")
    draw = ImageDraw.Draw(sheet)
    for i, r in enumerate(results):
        x, y = (i % cols) * W, (i // cols) * (H + 28)
        try:
            with urllib.request.urlopen(urllib.request.Request(r["thumb"], headers=UA), timeout=30) as resp:
                im = Image.open(BytesIO(resp.read())).convert("RGB")
            im.thumbnail((W - 8, H - 8))
            sheet.paste(im, (x + (W - im.width) // 2, y + (H - im.height) // 2))
        except Exception:
            draw.text((x + 8, y + H // 2), "(no preview)", fill="grey")
        draw.text((x + 8, y + H + 6), f"{r['n']}. {r['title'][:40]}", fill="black")
    sheet.save(os.path.join(out, "contact_sheet.jpg"), quality=85)
    print("Contact sheet:", os.path.join(out, "contact_sheet.jpg"))


# ---------------------------------------------------------------- changes to MediaValet
# Everything below WRITES to OCHA's shared library, through the shared BDU team account, so
# MediaValet itself cannot show who asked. Every write therefore needs --by "<person>" and is
# logged to the job folder. The confirmation rules (SKILL.md §6) are enforced here too: a write
# without the right confirmation flags prints what it WOULD do and changes nothing.

def api_send(method, path, token, body=None, content_type="application/json"):
    d = creds()
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(API + path, method=method, data=data, headers={
        **UA, "Authorization": "Bearer " + token, "Ocp-Apim-Subscription-Key": d["mediavalet_subscription_key"],
        "x-mv-api-version": "1.2", "Accept": "application/json", "Content-Type": content_type})
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        sys.exit(f"MediaValet API error {e.code} on {method} {path}: {e.read().decode(errors='replace')[:300]}")


def log_change(log, by, action, detail):
    import datetime
    os.makedirs(os.path.dirname(os.path.abspath(log)), exist_ok=True)
    new = not os.path.exists(log)
    with open(log, "a", encoding="utf-8") as f:
        if new:
            f.write("# Changes made in MediaValet\n\nDone through the BDU team account, so MediaValet "
                    "itself does not show who asked. One line per change.\n\n")
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write(f"- {stamp} · {by} · {action} · {detail}\n")


# New MediaValet calls lightboxes "collections": same object, same id, same API. The web app sends
# /browse/lightboxes/<id> to /v5/collections/<id> (found in MediaValet's own route table, Oct 2026).
WEB = "https://unocha.mediavalet.com"


def asset_link(aid):
    """The asset's page in the MediaValet web app (works when signed in). Route taken from the web
    app's own build manifest (/browse/assets/[assetId]); /v5/assets/<id> does NOT exist."""
    return f"{WEB}/v5/browse/assets/{aid}"


def collection_link(lid):
    return f"{WEB}/v5/collections/{lid}"


def lightbox_list(token):
    p = api_get("/lightboxes?includePermissions=true", token).get("payload", [])
    return p if isinstance(p, list) else p.get("lightboxes", [])


def lightbox_id(ref, token):
    """A lightbox id, or its exact name (case-insensitive). Ambiguous or unknown names stop."""
    if UUID.fullmatch(ref.strip().lower()):
        return ref.strip().lower(), ref
    hits = [l for l in lightbox_list(token) if (l.get("name") or "").strip().lower() == ref.strip().lower()]
    if len(hits) != 1:
        sys.exit(f"{'No' if not hits else str(len(hits))} lightbox(es) named “{ref}”. Use `lightboxes` to list them.")
    return hits[0]["id"], hits[0].get("name")


def cmd_lightboxes(token, filt):
    for l in lightbox_list(token):
        if filt and filt.lower() not in (l.get("name") or "").lower():
            continue
        print(f"{l.get('name')}  ·  {l.get('assetCount')} photos  ·  {collection_link(l['id'])}")


def cmd_lightbox_create(token, name, description, by, log):
    import uuid
    lid = str(uuid.uuid4())
    api_send("POST", "/lightboxes", token, {"id": lid, "name": name, "description": description or ""})
    log_change(log, by, "created lightbox", f"“{name}” ({lid})")
    print(f"Created collection “{name}”: {collection_link(lid)}")


def cmd_lightbox_add(token, ref, assets, by, log):
    lid, name = lightbox_id(ref, token)
    ids = [asset_id(a) for a in assets]
    api_send("POST", f"/lightboxes/{lid}/assets", token, ids)
    log_change(log, by, "added to lightbox", f"“{name}”: {len(ids)} photo{"s" if len(ids) != 1 else ""} ({', '.join(ids)})")
    print(f"Added {len(ids)} photo{"s" if len(ids) != 1 else ""} to “{name}”.")


def cmd_lightbox_remove(token, ref, assets, confirm, by, log):
    lid, name = lightbox_id(ref, token)
    ids = [asset_id(a) for a in assets]
    if not confirm:
        print(f"Would take {len(ids)} photo{"s" if len(ids) != 1 else ""} out of “{name}” (the photos stay in the library). "
              "Nothing changed: re-run with --confirm once the person has said yes.")
        return
    for i in ids:
        api_send("DELETE", f"/lightboxes/{lid}/assets/{i}", token)
    log_change(log, by, "removed from lightbox", f"“{name}”: {len(ids)} photo{"s" if len(ids) != 1 else ""} ({', '.join(ids)})")
    print(f"Took {len(ids)} photo{"s" if len(ids) != 1 else ""} out of “{name}”.")


def cmd_lightbox_delete(token, ref, confirm, by, log):
    lid, name = lightbox_id(ref, token)
    if not confirm:
        print(f"Would delete the lightbox “{name}” (its photos stay in the library). "
              "Nothing changed: re-run with --confirm once the person has said yes.")
        return
    api_send("DELETE", f"/lightboxes/{lid}", token)
    log_change(log, by, "deleted lightbox", f"“{name}” ({lid})")
    print(f"Deleted the lightbox “{name}”.")


def cmd_share(token, ref, recipient, expires, originals, confirm, by, log):
    """A public web gallery of a collection: anyone with the link sees it, no sign-in.

    shareTo MUST be "ExternalUser" and the collection id must be in "ids" too. With "Unknown" MediaValet
    answers 202 and a shareId, but no gallery exists: the /galleries/ page says "nothing here".
    With ExternalUser the reply carries payload.link (tested 14 Oct 2026, opened signed out)."""
    lid, name = lightbox_id(ref, token)
    size = "original files" if originals else "web-size images"
    if not confirm:
        print(f"Would make a public gallery of “{name}” for {recipient}, expiring {expires}, {size}. "
              "Anyone with the link can see and download these photos, no sign-in needed. Nothing changed: "
              "re-run with --confirm once the person has said yes.")
        return
    res = api_send("POST", "/shareLightboxes", token, {
        "shareTo": "ExternalUser", "shareVia": "Link", "allowAssetDownload": True,
        "images": {"shareOriginals": bool(originals), "spectrum": "SRgb",
                   "renditionType": "Original" if originals else "HighDefinition",
                   "resolution": "Print" if originals else "Web"},
        "videos": {"shareOriginals": bool(originals)}, "audio": {"shareOriginals": bool(originals)},
        "documents": {"shareOriginals": bool(originals)},
        "ids": [lid], "lightboxId": lid, "DynamicWebGallery": True,
        "gallerySettings": {"expiryDate": expires}, "message": {"recipients": [], "text": ""}})
    link = (res.get("payload") or {}).get("link")
    if not link:
        sys.exit("MediaValet accepted the share but returned no gallery link: " + json.dumps(res)[:300])
    log_change(log, by, "public gallery", f"“{name}” for {recipient}, {size}, expires {expires}: {link}")
    print(f"Public gallery (no sign-in), expires {expires}, {size}:\n{link}")


def new_caption(old, caption=None, credit=None):
    if caption is not None:
        text = caption.strip()
        m = re.search(r"Credit:\s*.+?\s*$", old or "", re.S)       # a new caption keeps the old credit
        if credit is None and m and "Credit:" not in text:
            text += "\n" + m.group(0).strip()
    else:
        text = old or ""
    if credit is not None:
        if re.search(r"Credit:\s*.+?\s*$", text, re.S):
            text = re.sub(r"Credit:\s*.+?\s*$", "Credit: " + credit.strip(), text, flags=re.S)
        else:
            text = text.rstrip() + "\nCredit: " + credit.strip()
    return text


def cmd_edit(token, assets, caption, credit, apply, confirm_count, by, log):
    if caption is None and credit is None:
        sys.exit("Give --caption and/or --credit.")
    plan = []
    for a in assets:
        aid = asset_id(a)
        asset = api_get("/assets/" + aid, token)["payload"]
        old = asset.get("description") or ""
        plan.append((aid, asset.get("title"), old, new_caption(old, caption, credit)))
    for aid, title, old, new in plan:
        print(f"── {title}\n   BEFORE: {old.strip()[-300:]}\n   AFTER:  {new.strip()[-300:]}")
    if not apply:
        print(f"\nNothing changed. Confirmation 1: show this to the person. Confirmation 2: once they've "
              f"said yes twice, re-run with --apply --confirm-count {len(plan)}.")
        return
    if confirm_count != len(plan):
        sys.exit(f"--confirm-count must be {len(plan)} (the number of photos changing). Nothing changed.")
    for aid, title, old, new in plan:
        api_send("PATCH", "/assets/" + aid, token, [{"op": "replace", "path": "/description", "value": new}])
        log_change(log, by, "edited caption/credit", f"{title} ({aid}). Before: “{old.strip()[-160:]}”")
    print(f"Changed {len(plan)} photo{"s" if len(plan) != 1 else ""} in MediaValet.")


def cmd_delete(token, assets, apply, confirm_count, confirm_names, by, log):
    plan = []
    for a in assets:
        aid = asset_id(a)
        asset = api_get("/assets/" + aid, token)["payload"]
        plan.append((aid, (asset.get("file") or {}).get("fileName") or asset.get("title")))
    print("Would move these photos to MediaValet’s deleted items (an admin can restore them):")
    for aid, fn in plan:
        print(f"   {fn}  ({aid})")
    if not apply:
        print(f"\nNothing changed. This needs three confirmations from the person (SKILL.md §6); then "
              f"re-run with --apply --confirm-count {len(plan)} --confirm-names \"<the file names they typed>\".")
        return
    typed = {n.strip().lower() for n in (confirm_names or "").split(",") if n.strip()}
    expected = {fn.strip().lower() for _, fn in plan}
    if confirm_count != len(plan) or typed != expected:
        sys.exit("The count or the typed file names don’t match the photos listed. Nothing deleted.")
    for aid, fn in plan:
        api_send("DELETE", f"/assets/{aid}?isHardDelete=false", token)   # soft delete only, never hard
        log_change(log, by, "deleted photo (soft, restorable)", f"{fn} ({aid})")
    print(f"Moved {len(plan)} photo{"s" if len(plan) != 1 else ""} to deleted items.")


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
    s = sub.add_parser("search")
    s.add_argument("query", help='a plain description, e.g. "aid workers distributing food"')
    s.add_argument("--out", required=True)
    s.add_argument("--country", help="ISO3 code or country name, e.g. SDN or Sudan")
    s.add_argument("--year", help="year the photo was taken, e.g. 2026")
    s.add_argument("--count", type=int, default=40, help="how many to keep after filters")

    def writer(p):                           # every command that changes MediaValet
        p.add_argument("--by", required=True, help="the person who asked (logged)")
        p.add_argument("--log", default="info/mediavalet_changes.md", help="change log in the job folder")
        return p
    lb = sub.add_parser("lightboxes"); lb.add_argument("filter", nargs="?")
    c = writer(sub.add_parser("lightbox-create")); c.add_argument("name"); c.add_argument("--description")
    c = writer(sub.add_parser("lightbox-add")); c.add_argument("lightbox"); c.add_argument("assets", nargs="+")
    c = writer(sub.add_parser("lightbox-remove")); c.add_argument("lightbox"); c.add_argument("assets", nargs="+")
    c.add_argument("--confirm", action="store_true")
    c = writer(sub.add_parser("lightbox-delete")); c.add_argument("lightbox"); c.add_argument("--confirm", action="store_true")
    c = writer(sub.add_parser("share")); c.add_argument("lightbox")
    c.add_argument("--for", dest="recipient", required=True, help="who the link is for")
    c.add_argument("--expires", required=True, help="YYYY-MM-DD")
    c.add_argument("--originals", action="store_true"); c.add_argument("--confirm", action="store_true")
    c = writer(sub.add_parser("edit")); c.add_argument("assets", nargs="+")
    c.add_argument("--caption"); c.add_argument("--credit")
    c.add_argument("--apply", action="store_true"); c.add_argument("--confirm-count", type=int)
    c = writer(sub.add_parser("delete")); c.add_argument("assets", nargs="+")
    c.add_argument("--apply", action="store_true"); c.add_argument("--confirm-count", type=int)
    c.add_argument("--confirm-names")
    args = ap.parse_args()
    # Several ids or links can arrive as ONE argument (zsh doesn't split "$IDS"); asset_id() would
    # then keep only the last one, silently. Split on whitespace so every photo counts.
    if getattr(args, "assets", None):
        args.assets = [part for a in args.assets for part in a.split()]
    if args.cmd == "setup":
        setup()
    elif args.cmd == "login":
        login()
    elif args.cmd == "info":
        print(json.dumps(api_get("/assets/" + asset_id(args.asset), access_token()), indent=2)[:6000])
    elif args.cmd == "download":
        download(args.assets, args.out)
    elif args.cmd == "search":
        search(args.query, args.out, args.country, args.year, args.count)
    elif args.cmd == "lightboxes":
        cmd_lightboxes(access_token(), args.filter)
    elif args.cmd == "lightbox-create":
        cmd_lightbox_create(access_token(), args.name, args.description, args.by, args.log)
    elif args.cmd == "lightbox-add":
        cmd_lightbox_add(access_token(), args.lightbox, args.assets, args.by, args.log)
    elif args.cmd == "lightbox-remove":
        cmd_lightbox_remove(access_token(), args.lightbox, args.assets, args.confirm, args.by, args.log)
    elif args.cmd == "lightbox-delete":
        cmd_lightbox_delete(access_token(), args.lightbox, args.confirm, args.by, args.log)
    elif args.cmd == "share":
        cmd_share(access_token(), args.lightbox, args.recipient, args.expires, args.originals, args.confirm, args.by, args.log)
    elif args.cmd == "edit":
        cmd_edit(access_token(), args.assets, args.caption, args.credit, args.apply, args.confirm_count, args.by, args.log)
    elif args.cmd == "delete":
        cmd_delete(access_token(), args.assets, args.apply, args.confirm_count, args.confirm_names, args.by, args.log)


if __name__ == "__main__":
    main()
