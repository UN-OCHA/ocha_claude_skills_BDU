#!/bin/zsh
# Render the graphic: tools/un_drf_platform.html -> export/un_drf_platform_2025x1525.png
# (300 dpi at 17.1 cm wide: artwork 16.1 cm plus a 5 mm margin). Run from the job folder: zsh tools/render.sh
# Needs Google Chrome and Roboto installed. The styles not chosen are in archive/<style>/ with their templates;
# render one with: zsh tools/render.sh archive/<style>/<file>.html <out.png>
set -e
cd "$(dirname "$0")/.."
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SRC="${1:-tools/un_drf_platform.html}"
OUT="${2:-export/un_drf_platform_2025x1525.png}"
# Page is 486 x 366 pt = 648 x 488 CSS px. Scale 3.125 gives 2025 x 1525 px = 300 dpi.
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --allow-file-access-from-files --force-device-scale-factor=3.125 \
  --window-size=648,488 --screenshot="$PWD/$OUT" "file://$PWD/$SRC" 2>/dev/null
ls -la "$OUT"
