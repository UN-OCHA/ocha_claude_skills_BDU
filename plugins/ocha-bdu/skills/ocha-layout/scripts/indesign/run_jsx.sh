#!/bin/bash
# Run an InDesign 2026 ExtendScript with named arguments.
# Usage: run_jsx.sh <script.jsx> key=value [key=value ...]
# Arguments go through a small generated .jsx file, so values can hold spaces, quotes and
# backslashes (GREP patterns) without fighting AppleScript's string escaping.
set -euo pipefail
SCRIPT="$1"; shift
TMP="$(mktemp -t indd_args).jsx"
trap 'rm -f "$TMP"' EXIT
python3 - "$TMP" "$SCRIPT" "$@" <<'EOF'
import json, sys
tmp, script, *pairs = sys.argv[1:]
lines = []
for kv in pairs:
    k, v = kv.split("=", 1)
    lines.append(f"app.scriptArgs.setValue({json.dumps(k)}, {json.dumps(v)});")
lines.append(f"$.evalFile(File({json.dumps(script)}));")
open(tmp, "w", encoding="utf-8").write("\n".join(lines))
EOF
APP="${INDESIGN_APP:-Adobe InDesign 2026}"
osascript -e "with timeout of 1800 seconds" \
  -e "tell application \"$APP\" to do script (POSIX file \"$TMP\") language javascript" \
  -e "end timeout"
