#!/usr/bin/env python3
"""Build the "What's new" notes that tell colleagues, in plain words, what an update changed.

    python3 build_whats_new.py <repo> [--require]

How it works (details in plugins/ocha-bdu/hooks/README.md):
- Before a publish, write the plain-words note in plugins/ocha-bdu/news/next.md: 2 to 4 short
  bullet lines, one per change a colleague would notice, written for designers, not developers.
  When an update leaves something for colleagues to DO (a rename, a setup, a setting, old files
  to remove), write that line as "Javi recommends: <the step>" so their Claude offers to do it.
- This script moves it into news/CHANGES.md under the plugin's new version, then writes one
  small file per version, news/after-<version>.md, holding what came after that version.
- At session start the plugin's hook prints after-<the version this computer last saw>.md, so
  Claude tells each colleague only what is new to them, once. The latest version's file is
  empty: nothing to say.

--require (used by the publish script with --push): stop if the plugin got a new version but
no note says what changed. An update nobody explains is what this exists to prevent.

LOAD-BEARING: the after-*.md files must be plain ASCII. Windows PowerShell 5.1 garbles UTF-8
without a BOM, and the hook may run there. CHANGES.md itself can use any characters.
"""
import json
import os
import re
import subprocess
import sys
import unicodedata

PLUGIN = "plugins/ocha-bdu"
MANIFEST = f"{PLUGIN}/.claude-plugin/plugin.json"
NEWS = f"{PLUGIN}/news"
MAX_ENTRIES = 5  # a colleague who skipped many updates gets the latest five, not a wall of text

HEADER = re.compile(r"^## (\d{4}\.\d{1,2}\.\d{1,2}(?:\.\d+)?)\b.*$", re.M)

ASCII_MAP = {"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-",
             "—": "-", "…": "...", "×": "x", " ": " ", " ": " ",
             "→": "->", "·": "-", "•": "-"}

INSTRUCTIONS = """[OCHA BDU skills - update from Javi, since this computer last checked]

Source: the OCHA BDU plugin (github.com/UN-OCHA/ocha_claude_skills_BDU), maintained by Javi (Javier Cueto) and the OCHA Brand and Design Unit (ochavisual@un.org). Javi updated its skills. This note appears once per update.

What to do, once in this session:
- At the end of your first reply, add a short section headed "Update from Javi (OCHA BDU skills)" and say, in plain words and in the user's language, what changed: one short line per change, 4 lines at most. Write for designers, not developers: what they can now do or what now works differently. No file names, no version numbers.
- Lines marked "Javi recommends:" are steps Javi wants each colleague to take. Say them as his recommendation, plainly ("Javi recommends: ..."), then offer to do the step now, explain in one sentence what it changes, and do it only after the user says yes. If it isn't needed on this computer (for example the old folders aren't there), say so in one line instead of asking. Never delete or change anything without that yes.
- Then record that this note was shown, so it doesn't come back: in the Claude settings file (~/.claude/settings.json on a Mac, %USERPROFILE%\\.claude\\settings.json on Windows; create it if missing), keep everything already there and set, under "env": "OCHA_BDU_NEWS_SEEN": "{latest}". Check the file is still valid JSON. Change nothing else. You don't need to ask first: this setting only records that the note was shown.

The updates, newest first:
"""


def ascii_only(text: str, where: str) -> str:
    for k, v in ASCII_MAP.items():
        text = text.replace(k, v)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    bad = sorted({c for c in text if ord(c) > 127})
    if bad:
        sys.exit(f"ABORT: {where} has characters the Windows hook can't show: {' '.join(bad)}. "
                 "Rephrase them or add them to ASCII_MAP.")
    return text


def read(path: str) -> str:
    return open(path, encoding="utf-8").read() if os.path.exists(path) else ""


def entries(changes: str) -> list:
    """[(version, block text)], newest first, as written in CHANGES.md."""
    marks = list(HEADER.finditer(changes))
    out = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(changes)
        out.append((m.group(1), changes[m.start():end].strip()))
    return out


def upstream_version(repo: str) -> str:
    r = subprocess.run(["git", "-C", repo, "show", f"@{{u}}:{MANIFEST}"], capture_output=True, text=True)
    return json.loads(r.stdout).get("version", "") if r.returncode == 0 else ""


def main():
    repo = sys.argv[1]
    require = "--require" in sys.argv[2:]
    news = os.path.join(repo, NEWS)
    os.makedirs(news, exist_ok=True)
    version = json.load(open(os.path.join(repo, MANIFEST)))["version"]
    changes_path = os.path.join(news, "CHANGES.md")
    changes = read(changes_path)
    found = entries(changes)

    note = read(os.path.join(news, "next.md")).strip()
    if note:
        if found and found[0][0] == version:  # a second publish before this one went out
            changes = changes.replace(found[0][1], found[0][1] + "\n" + note, 1)
        else:
            head = "# What's new in the OCHA BDU skills\n\nNewest first. Written for colleagues, in plain words.\n"
            body = changes.split("\n## ", 1)
            rest = ("\n## " + body[1]) if len(body) == 2 else ""
            changes = f"{head}\n## {version}\n\n{note}\n{rest}"
        open(changes_path, "w", encoding="utf-8").write(changes.rstrip() + "\n")
        os.remove(os.path.join(news, "next.md"))
        found = entries(changes)
        print(f"   note added under {version}")
    elif require and version != upstream_version(repo) and not any(v == version for v, _ in found):
        sys.exit(f"ABORT: version {version} has no 'What's new' note. Write 2-4 plain-words lines, one per "
                 f"change a colleague would notice, in {NEWS}/next.md, then publish again.")

    if not found:
        print("   no notes yet")
        return
    latest = found[0][0]
    wanted = {"after-.md"}
    for i, (v, _) in enumerate(found):
        newer = found[:i][:MAX_ENTRIES]
        wanted.add(f"after-{v}.md")
        text = ""
        if newer:
            text = INSTRUCTIONS.replace("{latest}", latest) + "\n\n".join(b for _, b in newer) + "\n"
        open(os.path.join(news, f"after-{v}.md"), "w", encoding="ascii").write(ascii_only(text, f"the note for {v}"))
    # Never seen anything (new install, or before this existed): the latest update only.
    first = INSTRUCTIONS.replace("{latest}", latest) + found[0][1] + "\n"
    open(os.path.join(news, "after-.md"), "w", encoding="ascii").write(ascii_only(first, "the latest note"))
    for name in os.listdir(news):
        if name.startswith("after-") and name not in wanted:
            os.remove(os.path.join(news, name))
    print(f"   notes ready, latest {latest}")


if __name__ == "__main__":
    main()
