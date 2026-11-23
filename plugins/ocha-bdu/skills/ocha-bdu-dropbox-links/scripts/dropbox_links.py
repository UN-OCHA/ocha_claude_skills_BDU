#!/usr/bin/env python3
"""Public ("anyone with the link") Dropbox links, through the Dropbox API.

Why this exists: the Dropbox connector's create_shared_link makes links that only OCHA team members
can open, and it takes the file's one main link. This script makes links that open for anyone.

Each person connects THEIR OWN Dropbox once, with their own small Dropbox app. The two values it
needs live only on that computer, in ~/.claude/tokens.json:
  dropbox_app_key        the App key of the person's own Dropbox app (not a secret on its own)
  dropbox_refresh_token  written by `setup`; does not expire unless the access is removed

Commands (Windows: `python` or `py` instead of `python3`):
  python3 dropbox_links.py status                  # connected? as whom?
  python3 dropbox_links.py open-console            # opens the Dropbox page where the app is made
  python3 dropbox_links.py setup                   # App key + Allow + code, in private pop-ups
  python3 dropbox_links.py share <file-or-folder>... [--download | --direct]
        # a local path inside the Dropbox folder, a Dropbox path (/Team folder/...) or an id (id:...)
  python3 dropbox_links.py check <url>...          # does the link open for someone not signed in?

Sign-in uses Dropbox's PKCE flow: no app secret exists anywhere. Nothing secret is ever printed.
"""
import argparse
import base64
import hashlib
import json
import os
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

TOKENS = os.path.expanduser("~/.claude/tokens.json")
API = "https://api.dropboxapi.com/2"
AUTH_URL = "https://www.dropbox.com/oauth2/authorize"
TOKEN_URL = "https://api.dropboxapi.com/oauth2/token"
CONSOLE_URL = "https://www.dropbox.com/developers/apps/create"
KEY_APP, KEY_REFRESH = "dropbox_app_key", "dropbox_refresh_token"
# The app must have these ticked on its Permissions tab BEFORE `setup`: a connection only carries
# the permissions the app had when the person clicked Allow.
SCOPES = ["files.metadata.read", "sharing.read", "sharing.write"]

# Windows: the console and files default to a Western code page, so a file name in Arabic,
# Cyrillic or with many accents crashed print(). Load-bearing: every text file here is opened with
# encoding="utf-8", and output is UTF-8 on every system.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# --- tokens.json ------------------------------------------------------------------------------

def load():
    if not os.path.exists(TOKENS):
        return {}
    with open(TOKENS, encoding="utf-8") as f:
        return json.load(f)


def save(d):
    os.makedirs(os.path.dirname(TOKENS), exist_ok=True)
    tmp = TOKENS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)
    os.chmod(tmp, 0o600)
    os.replace(tmp, TOKENS)


# --- private pop-ups (same pattern as ocha-bdu-photo/scripts/mediavalet.py) ------------------------

TITLE = "Dropbox - stored on this computer only"


def ask_private(prompt):
    """A pop-up with hidden input, so the value never touches the chat or the terminal output.
    Mac: the system dialog. Windows (and others): a small Python window; on Windows without
    Python's window kit, Windows PowerShell's own sign-in box. Claude runs commands without a
    keyboard prompt, so a terminal prompt (input/getpass) would not work here."""
    value = None
    if sys.platform == "darwin":
        import subprocess
        safe = prompt.replace("\\", "\\\\").replace('"', '\\"')
        script = (f'display dialog "{safe}" default answer "" with hidden answer '
                  f'with title "{TITLE}" buttons {{"Cancel","Save"}} default button "Save"')
        r = subprocess.run(["osascript", "-e", script, "-e", "text returned of result"],
                           capture_output=True, text=True)
        value = r.stdout if r.returncode == 0 else None
    else:
        try:
            value = _ask_private_tk(prompt)
        except ImportError:
            if sys.platform != "win32":
                sys.exit("No private pop-up available on this computer (Python's tkinter is missing).")
            value = _ask_private_powershell(prompt)
    if not value or not value.strip():
        sys.exit("Setup cancelled - nothing saved.")
    return value.strip()


def _ask_private_tk(prompt):
    import tkinter as tk
    root = tk.Tk()
    root.title(TITLE)
    root.attributes("-topmost", True)        # the window must not open behind the Claude app
    root.resizable(False, False)
    result = {}
    tk.Label(root, text=prompt, padx=16, pady=12, justify="left").pack(anchor="w")
    entry = tk.Entry(root, show="*", width=48)
    entry.pack(padx=16, fill="x")

    def done(_=None):
        result["v"] = entry.get()
        root.destroy()
        return "break"

    row = tk.Frame(root, pady=12)
    row.pack()
    tk.Button(row, text="Cancel", width=10, command=root.destroy).pack(side="left", padx=4)
    tk.Button(row, text="Save", width=10, command=done, default="active").pack(side="left", padx=4)
    entry.bind("<Return>", done)
    root.bind("<Escape>", lambda _: root.destroy())
    root.after(200, entry.focus_force)
    root.mainloop()
    return result.get("v")


def _ask_private_powershell(prompt):
    """Windows PowerShell 5.1 (built into Windows 10/11) shows Get-Credential as a window with a
    hidden password box. The value comes back on the script's output, never on screen."""
    import subprocess
    ps = ("$c = Get-Credential -UserName 'Dropbox' -Message $env:DBX_PROMPT; "
          "if ($c) { [Console]::Out.Write($c.GetNetworkCredential().Password) }")
    r = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps], capture_output=True, text=True,
                       env=dict(os.environ, DBX_PROMPT=prompt + "  (paste it in the Password box)"))
    return r.stdout if r.returncode == 0 else None


# --- connection --------------------------------------------------------------------------------

NOT_SET_UP = ("Dropbox is not connected on this computer yet. "
              "Follow the one-time setup in the ocha-bdu-dropbox-links skill (section 1).")


def _form_post(url, form):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(form).encode(), method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


_TOKEN = None


def access_token():
    """A fresh short-lived access token, minted from the stored refresh token once per run."""
    global _TOKEN
    if _TOKEN:
        return _TOKEN
    d = load()
    if not (d.get(KEY_APP) and d.get(KEY_REFRESH)):
        sys.exit(NOT_SET_UP)
    try:
        _TOKEN = _form_post(TOKEN_URL, {"grant_type": "refresh_token", "client_id": d[KEY_APP],
                                        "refresh_token": d[KEY_REFRESH]})["access_token"]
    except urllib.error.HTTPError as e:
        # A dead connection is a stop, not something to route around (never fall back to the
        # Dropbox connector: its links are team-only).
        sys.exit(f"The Dropbox connection stopped working ({e.code}): "
                 f"{e.read().decode('utf-8', 'replace')[:300]}\n"
                 "If this says invalid_grant, the access was removed: run `setup` again.")
    return _TOKEN


_ROOT = None


def api(endpoint, body, root=True):
    """POST to the Dropbox API. Returns (status, json). root=True sends the team's root namespace,
    so team-space paths (/Team folder/...) work, not only the person's own folder."""
    global _ROOT
    headers = {"Authorization": "Bearer " + access_token(), "Content-Type": "application/json"}
    if root:
        if _ROOT is None:
            _ROOT = account()["root_info"]["root_namespace_id"]
        headers["Dropbox-API-Path-Root"] = json.dumps({".tag": "root", "root": _ROOT})
    req = urllib.request.Request(API + endpoint, method="POST", headers=headers,
                                 data=b"null" if body is None else json.dumps(body).encode("utf-8"))
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode("utf-8")
            return 200, (json.loads(raw) if raw.strip() not in ("", "null") else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(raw)
        except ValueError:
            return e.code, {"error_summary": raw[:300]}


_ACCOUNT = None


def account():
    global _ACCOUNT
    if _ACCOUNT is None:
        code, a = api("/users/get_current_account", None, root=False)
        if code != 200:
            sys.exit(f"Could not read the Dropbox account ({code}): {a.get('error_summary', a)}")
        _ACCOUNT = a
    return _ACCOUNT


def cmd_status():
    d = load()
    if not (d.get(KEY_APP) and d.get(KEY_REFRESH)):
        print("NOT SET UP - " + NOT_SET_UP)
        return 1
    a = account()
    print(f"READY - connected to the Dropbox of {a['name']['display_name']} <{a['email']}>")
    return 0


def cmd_open_console():
    webbrowser.open(CONSOLE_URL)
    print("Opened " + CONSOLE_URL)


def cmd_setup():
    """App key (pop-up) -> Allow in the browser -> code (pop-up) -> refresh token saved."""
    app_key = ask_private("Paste the APP KEY of your Dropbox app.\n\n"
                          "It is on the app's Settings tab, labelled 'App key'.\n"
                          "(Not the App secret.)")
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode().rstrip("=")
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    url = AUTH_URL + "?" + urllib.parse.urlencode({
        "client_id": app_key, "response_type": "code", "code_challenge": challenge,
        "code_challenge_method": "S256",
        "token_access_type": "offline",      # load-bearing: this is what yields a refresh token
    })
    print("Opening the Dropbox Allow page in your browser…", flush=True)
    webbrowser.open(url)
    code = ask_private("In the browser: click Continue, then Allow.\n\n"
                       "Dropbox then shows a code. Copy it and paste it here.")
    try:
        t = _form_post(TOKEN_URL, {"code": code, "grant_type": "authorization_code",
                                   "client_id": app_key, "code_verifier": verifier})
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:300]
        hint = ("The App key was not recognised: copy it again from the app's Settings tab."
                if "client_id" in detail or "invalid_client" in detail else
                "The code works once and only for a few minutes: run setup again and paste a fresh one.")
        sys.exit(f"Dropbox refused the connection ({e.code}): {detail}\n{hint}")
    if not t.get("refresh_token"):
        sys.exit("Dropbox gave no lasting access (no refresh token). Run setup again.")
    granted = set(t.get("scope", "").split())
    missing = [s for s in SCOPES if s not in granted]
    if missing:
        sys.exit("The app is missing these permissions: " + ", ".join(missing) + ".\n"
                 "On the app's Permissions tab, tick them, click Submit at the bottom, "
                 "then run setup again. Nothing was saved.")
    d = load()
    d[KEY_APP], d[KEY_REFRESH] = app_key, t["refresh_token"]
    d.pop("dropbox_api_personal_access_token", None)   # an old short-lived token would only mislead
    save(d)
    global _TOKEN
    _TOKEN = None
    a = account()
    print(f"Connected to the Dropbox of {a['name']['display_name']} <{a['email']}>. "
          "Saved on this computer only (~/.claude/tokens.json). This does not need to be done again.")


# --- paths ---------------------------------------------------------------------------------------

def dropbox_folders():
    """Local Dropbox folders from the desktop app's info.json: [(local_root, is_team_root)].
    A team-space account has root_path (the folder holding the team folders and the member folder);
    its paths then map one-to-one onto the team's root namespace."""
    places = [os.path.expanduser("~/.dropbox/info.json")]
    for var in ("APPDATA", "LOCALAPPDATA"):
        if os.environ.get(var):
            places.append(os.path.join(os.environ[var], "Dropbox", "info.json"))
    roots = []
    for p in places:
        if not os.path.isfile(p):
            continue
        try:
            with open(p, encoding="utf-8") as f:
                info = json.load(f)
        except (OSError, ValueError):
            continue
        for kind in ("business", "personal"):
            acc = info.get(kind) or {}
            base = acc.get("root_path") or acc.get("path")
            if base:
                roots.append(base)
    return roots


def to_dropbox_ref(arg):
    """Local path inside the Dropbox folder -> Dropbox path. Ids and Dropbox paths pass through."""
    if arg.startswith(("id:", "ns:")):
        return arg
    local = os.path.expanduser(arg)
    if os.path.exists(local):
        full = os.path.realpath(os.path.abspath(local))
        for base in dropbox_folders():
            b = os.path.realpath(base)
            # Dropbox paths are case-insensitive, and so are the default Mac and Windows disks.
            if full.lower() == b.lower() or full.lower().startswith(b.lower().rstrip(os.sep) + os.sep):
                rel = full[len(b):].replace(os.sep, "/")
                return rel if rel.startswith("/") else "/" + rel
        sys.exit(f"{arg} is on this computer but not inside a Dropbox folder, so it can't get a Dropbox link.")
    if arg.startswith("/"):
        return arg
    sys.exit(f"Not found: {arg}. Give a file in the Dropbox folder on this computer, "
             "a Dropbox path starting with /, or an id: from the Dropbox connector.")


# --- links ---------------------------------------------------------------------------------------

def is_public(link):
    perms = link.get("link_permissions", {})
    for key in ("effective_audience", "resolved_visibility"):
        if (perms.get(key) or {}).get(".tag") == "public":
            return True
    return False


SETTINGS = {"requested_visibility": "public", "access": "viewer", "allow_download": True}


def fail(what, code, r):
    summary = r.get("error_summary", r)
    hint = ""
    if "missing_scope" in str(summary):
        hint = ("\nThe Dropbox app is missing a permission. Tick files.metadata.read, sharing.read and "
                "sharing.write on its Permissions tab, click Submit, then run setup again.")
    elif "not_found" in str(summary):
        hint = "\nDropbox can't see this file from the connected account. Is it in YOUR Dropbox?"
    elif "settings_error" in str(summary) or "not_authorized" in str(summary):
        hint = "\nThe team's sharing settings refused a public link for this file."
    raise RuntimeError(f"{what} failed ({code}): {summary}{hint}")


def public_link(ref):
    """Return a public link for ref, keeping an existing link whenever possible, because that link
    may already be on a live page (brand portal, README). Order:
      1. an existing public link -> reuse it as it is
      2. an existing restricted link (e.g. made by the Dropbox connector) -> switch it to public
      3. none, or one that can't be switched -> revoke it and make a new public link."""
    code, r = api("/sharing/list_shared_links", {"path": ref, "direct_only": True})
    if code != 200:
        fail("Reading the file's links", code, r)
    links = r.get("links", [])
    for link in links:
        if is_public(link):
            return link["url"], "existing public link kept"
    for link in links:
        code, m = api("/sharing/modify_shared_link_settings",
                      {"url": link["url"], "settings": SETTINGS, "remove_expiration": True})
        if code == 200 and is_public(m):
            return m["url"], "existing team-only link switched to public (same address)"
    revoked = 0
    for link in links:
        code, rr = api("/sharing/revoke_shared_link", {"url": link["url"]})
        if code != 200:
            fail("Removing the old team-only link", code, rr)
        revoked += 1
    code, c = api("/sharing/create_shared_link_with_settings", {"path": ref, "settings": SETTINGS})
    if code != 200:
        fail("Making the public link", code, c)
    if not is_public(c):
        raise RuntimeError("Dropbox made the link but not as public (team sharing settings?).")
    return c["url"], ("old team-only link replaced by a new public one" if revoked else "new public link")


def with_dl(url, value):
    p = urllib.parse.urlparse(url)
    q = [(k, v) for k, v in urllib.parse.parse_qsl(p.query) if k != "dl"]
    if value is not None:
        q.append(("dl", value))
    return urllib.parse.urlunparse(p._replace(query=urllib.parse.urlencode(q)))


def direct(url):
    """dl.dropboxusercontent.com form: returns the bytes with no redirect (Canva and other fetchers
    that don't follow redirects need it)."""
    p = urllib.parse.urlparse(with_dl(url, None))
    return urllib.parse.urlunparse(p._replace(netloc="dl.dropboxusercontent.com"))


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def opens_logged_out(url):
    """True when the link downloads for someone who is not signed in: a public link sends the
    download (302 to *.dropboxusercontent.com); a team-only link answers with a sign-in page."""
    if "dropboxusercontent.com" in urllib.parse.urlparse(url).netloc:
        test, want_redirect = url, False
    else:
        test, want_redirect = with_dl(url, "1"), True
    opener = urllib.request.build_opener(_NoRedirect)
    req = urllib.request.Request(test, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
    try:
        with opener.open(req, timeout=30) as r:
            code, loc = r.status, ""
    except urllib.error.HTTPError as e:
        code, loc = e.code, e.headers.get("Location", "")
    if want_redirect:
        return code in (301, 302, 303, 307) and "dropboxusercontent.com" in loc
    return code == 200


def cmd_share(items, mode):
    bad = 0
    for arg in items:
        try:
            url, how = public_link(to_dropbox_ref(arg))
            out = with_dl(url, "1") if mode == "download" else direct(url) if mode == "direct" else url
            ok = opens_logged_out(out)
            print(f"{'OK' if ok else 'NOT PUBLIC'}\t{arg}\t{out}\t({how})")
            bad += 0 if ok else 1
        except (RuntimeError, SystemExit) as e:
            print(f"FAIL\t{arg}\t{e}", file=sys.stderr)
            bad += 1
    return 1 if bad else 0


def cmd_check(urls):
    bad = 0
    for u in urls:
        ok = opens_logged_out(u)
        print(f"{'PUBLIC' if ok else 'NOT PUBLIC'}\t{u}")
        bad += 0 if ok else 1
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description="Public Dropbox links (anyone with the link).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("open-console")
    sub.add_parser("setup")
    s = sub.add_parser("share")
    s.add_argument("items", nargs="+", help="local path in the Dropbox folder, /Dropbox/path or id:…")
    g = s.add_mutually_exclusive_group()
    g.add_argument("--download", action="store_true", help="link downloads straight away (dl=1)")
    g.add_argument("--direct", action="store_true", help="dl.dropboxusercontent.com form, no redirect")
    c = sub.add_parser("check")
    c.add_argument("urls", nargs="+")
    a = ap.parse_args()
    if a.cmd == "status":
        return cmd_status()
    if a.cmd == "open-console":
        return cmd_open_console()
    if a.cmd == "setup":
        return cmd_setup()
    if a.cmd == "share":
        return cmd_share(a.items, "download" if a.download else "direct" if a.direct else "preview")
    if a.cmd == "check":
        return cmd_check(a.urls)


if __name__ == "__main__":
    sys.exit(main() or 0)
