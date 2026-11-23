#!/bin/bash
# Run an Illustrator 2026 ExtendScript with named arguments, passed as $.global.ARGS (see make_*_ai.jsx).
# Addressed by path: several Illustrator versions share one bundle id, and the 2026 one must run it.
# Usage: run_ai.sh <script.jsx> key=value [key=value ...]
set -euo pipefail
SCRIPT="$1"; shift
TMP="$(mktemp -t ai_args).jsx"
trap 'rm -f "$TMP"' EXIT
python3 - "$TMP" "$SCRIPT" "$@" <<'PY'
import json, sys
tmp, script, *pairs = sys.argv[1:]
args = dict(kv.split("=", 1) for kv in pairs)
open(tmp, "w", encoding="utf-8").write("$.global.ARGS = %s;\n$.evalFile(File(%s));" % (json.dumps(args), json.dumps(script)))
PY
APP="${ILLUSTRATOR_APP:-/Applications/Adobe Illustrator 2026/Adobe Illustrator.app}"
osascript -e "with timeout of 1800 seconds" \
  -e "tell application \"$APP\" to do javascript \"\$.evalFile(File('$TMP'))\"" \
  -e "end timeout"
