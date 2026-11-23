#!/bin/bash
# Encode a PNG frame sequence (00000.png, 00001.png, …) into an MP4 that plays everywhere.
#
#   bash encode.sh <frames_dir> <output.mp4> [fps]
#
# H.264, CRF 16 (visually lossless for flat graphics), yuv420p for compatibility, BT.709
# colour tags so players don't shift the brand colours, and fast-start so it streams.
# If the frames are 3840x2160 and a 1920x1080 file is also needed, add a second pass with
#   -vf "scale=1920:1080:flags=lanczos"
#
# Maintained by: OCHA Brand and Design Unit (BDU) — ochavisual@un.org
set -euo pipefail

FRAMES="${1:?frames directory}"
OUT="${2:?output .mp4}"
FPS="${3:-30}"
FFMPEG="${FFMPEG:-ffmpeg}"

command -v "$FFMPEG" >/dev/null || { echo "ffmpeg not found — install it or set FFMPEG=/path/to/ffmpeg" >&2; exit 1; }

# The BT.709 tags also go to x264 directly (-x264-params). On ffmpeg 8.1 (checked September 2026) the three
# -color_* options alone did not reach libx264 for PNG input: only the matrix was written, the primaries and
# the transfer stayed "unknown" — which QuickTime can show washed out. Keep both; the check below says if
# a future ffmpeg drops them again.
"$FFMPEG" -y -loglevel error -framerate "$FPS" -i "$FRAMES/%05d.png" \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -movflags +faststart \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -x264-params colorprim=bt709:transfer=bt709:colormatrix=bt709 "$OUT"

FFPROBE="${FFPROBE:-ffprobe}"
if command -v "$FFPROBE" >/dev/null; then
  TAGS=$("$FFPROBE" -v error -select_streams v:0 -show_entries stream=color_space,color_transfer,color_primaries -of csv=p=0 "$OUT")
  [ "$TAGS" = "bt709,bt709,bt709" ] || echo "WARNING: colour tags are '$TAGS', not bt709 throughout — players may shift the brand colours" >&2
fi

echo "Encoded $OUT"
