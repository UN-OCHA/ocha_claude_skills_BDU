#!/usr/bin/env python3
"""Stamp the OCHA skills plugin with a date version when its content has changed.

    python3 ~/.claude/scripts/stamp_plugin_version.py <repo> [YYYY-MM-DD]

Versions look like 2026.11.4, then 2026.11.4.2 for a second publish on the same day.

LOAD-BEARING: once plugin.json has a version, Claude only updates colleagues when that version
changes. A publish that changes the plugin without changing the version reaches nobody, with no
error anywhere. So this compares the plugin against the commit that last stamped it, which also
catches changes committed by hand between publishes. The optional date is for tests only.
"""
import datetime
import json
import os
import subprocess
import sys

PLUGIN = "plugins/ocha-bdu"
MANIFEST = f"{PLUGIN}/.claude-plugin/plugin.json"


def git(repo, *args, check=True):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=check)
    return r.stdout


def committed_manifest(repo, ref="HEAD"):
    r = subprocess.run(["git", "-C", repo, "show", f"{ref}:{MANIFEST}"], capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 else {}


def plugin_changed(repo, current):
    """True if plugin files differ from the last stamped commit, or nothing was ever stamped."""
    if not current:
        return True
    uncommitted = git(repo, "status", "--porcelain", "--", PLUGIN).splitlines()
    if any(not line.endswith(MANIFEST) for line in uncommitted):
        return True
    stamped = git(repo, "log", "-1", "--format=%H", "--", MANIFEST).strip()
    committed = git(repo, "diff", "--name-only", stamped, "HEAD", "--", PLUGIN).splitlines()
    return any(path != MANIFEST for path in committed)


def next_version(current, today):
    base = f"{today.year}.{today.month}.{today.day}"
    if current == base:
        return f"{base}.2"
    if current.startswith(base + "."):
        return f"{base}.{int(current.rsplit('.', 1)[1]) + 1}"
    return base


def main():
    repo = sys.argv[1]
    today = datetime.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else datetime.date.today()
    path = os.path.join(repo, MANIFEST)
    with open(path) as f:
        manifest = json.load(f)
    current = manifest.get("version", "")

    # Already stamped by a run that stopped before committing: don't stamp twice.
    if current and current != committed_manifest(repo).get("version", ""):
        print(f"   version {current} (already stamped, not yet committed)")
        return
    if not plugin_changed(repo, current):
        print(f"   version {current} (plugin unchanged)")
        return

    version = next_version(current, today)
    stamped = {"name": manifest["name"], "version": version}
    stamped.update((k, v) for k, v in manifest.items() if k not in stamped)
    with open(path, "w") as f:
        json.dump(stamped, f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open(path) as f:
        if json.load(f).get("version") != version:
            sys.exit("ABORT: the plugin version did not save")
    print(f"   version {current or '(none)'} → {version}")


if __name__ == "__main__":
    main()
