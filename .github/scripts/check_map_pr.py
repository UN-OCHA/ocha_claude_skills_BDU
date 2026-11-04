#!/usr/bin/env python3
"""The check on every pull request to main: is it safe to merge without anyone reviewing it?

    python3 check_map_pr.py <base_sha> <head_sha>

Fails when the pull request:
  - changes anything outside the shared skill folders listed in ALLOWED (git cannot give someone
    write access to one folder only, so this check is what enforces it);
  - adds a link, which could point outside the folder;
  - contains a credential or a personal path. The repo is public, and this is the only safety
    check these changes get: the sweep in the publish script runs on one Mac, at publish time.

It only reads the pull request's files as data and never runs them. See map-skill-check.yml.
"""
import re
import subprocess
import sys

ALLOWED = ("plugins/ocha-bdu/skills/ocha-mapping/",)
MAX_SCAN_BYTES = 8 * 1024 * 1024

# Square brackets in a few of these keep the publish script's own sweep from matching this file.
SHAPES = [
    ("Dropbox token", r"\bsl\.(?:u\.)?[A-Za-z0-9_-]{40,}"),
    ("analytics token", r"ocha-dv-analytics[-]|qv-analytics[-]"),
    ("Trello token", r"\bATTA[A-Za-z0-9]{60,}"),
    ("GitHub token", r"\bgh[pousr]_[A-Za-z0-9]{30,}|\bgithub_pat_[A-Za-z0-9_]{50,}"),
    ("Slack token", r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),
    ("Anthropic or OpenAI key", r"\bsk-(?:ant-)?[A-Za-z0-9_-]{20,}"),
    ("ElevenLabs key", r"\bsk_[A-Za-z0-9]{30,}"),
    ("AWS key", r"\bAKIA[0-9A-Z]{16}\b"),
    ("Google API key", r"\bAIza[0-9A-Za-z_-]{35}\b"),
    ("private key", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ("credential in a setting", r"(?:TOKEN|API_?KEY|SECRET|PASSWORD)\s*[=:]\s*[\"']?[A-Za-z0-9_.\-]{16,}"),
    ("personal Mac path", r"/Users/(?!<)[A-Za-z0-9._-]+/"),
    ("personal Windows path", r"[A-Za-z]:\\+Users\\+(?!<)[A-Za-z0-9._-]+"),
    ("personal Dropbox path", r"OCHA DMU Dropbox[/\\]+(?!<your-name>)[A-Za-z]"),
]
SHAPES = [(label, re.compile(rx)) for label, rx in SHAPES]


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout


def changed_files(base, head):
    """Every path touched, as (new mode, path). --no-renames: a move out of the folder shows both ends."""
    fields = git("diff", "--raw", "-z", "--no-renames", f"{base}...{head}").decode("utf-8", "replace").split("\0")
    return [(fields[i].split()[1], fields[i + 1]) for i in range(0, len(fields) - 1, 2)]


def main():
    base, head = sys.argv[1], sys.argv[2]
    problems = []
    files = changed_files(base, head)
    for mode, path in files:
        if not path.startswith(ALLOWED):
            problems.append(f"{path}: outside the folders this check allows")
        if mode == "120000":
            problems.append(f"{path}: links are not allowed")
        if mode == "000000" or not path.startswith(ALLOWED):
            continue  # deleted, or already refused above
        data = git("show", f"{head}:{path}")
        if len(data) > MAX_SCAN_BYTES:
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue  # binary (pdf, png, font): nothing to read
        for label, rx in SHAPES:
            m = rx.search(text)
            if m:
                problems.append(f"{path}:{text.count(chr(10), 0, m.start()) + 1}: looks like a {label}")
    if problems:
        print("NOT safe to merge. Fix these, then push again:")
        for p in problems:
            print("  - " + p)  # the location only, never the matched value: this log is public
        sys.exit(1)
    print(f"OK: {len(files)} file(s) changed, all inside the allowed folders, no credentials or personal paths.")


if __name__ == "__main__":
    main()
