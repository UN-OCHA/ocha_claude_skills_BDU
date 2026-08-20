#!/usr/bin/env python3
"""
Scaffold caption cues from a finished clip with faster-whisper (word + segment timings).

    python3 transcribe.py VIDEO.mp4 [lang]        # lang defaults to auto; pass e.g. en, es

Prints each segment as `[start-end] text` AND a ready-to-paste `cues` block using the
segment START as each cue start (the render script derives ends = next start). You then
TRANSLATE + tidy the text in place (keep the timings). Segments are already close to social
caption size; split any that run long, and apply the punctuation rule (capital after a period).

Needs the project venv that has faster-whisper, e.g.:
    /path/to/ocha_quick_vid/.venv/bin/python transcribe.py VIDEO.mp4 en
"""
import sys, json, subprocess, os

def main():
    if len(sys.argv) < 2:
        print("usage: transcribe.py VIDEO [lang]"); sys.exit(1)
    src = sys.argv[1]; lang = sys.argv[2] if len(sys.argv) > 2 else None
    wav = os.path.splitext(src)[0] + ".16k.wav"
    subprocess.run([os.environ.get("FFMPEG", "/opt/homebrew/bin/ffmpeg"), "-y", "-loglevel", "error",
                    "-i", src, "-ac", "1", "-ar", "16000", wav], check=True)
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    segs, info = m.transcribe(wav, language=lang, beam_size=5, word_timestamps=True)
    rows = []
    for s in segs:
        rows.append((round(s.start, 2), round(s.end, 2), s.text.strip()))
    print(f"# language={info.language}  segments={len(rows)}  (translate the text, keep the timings)\n")
    for s, e, t in rows:
        print(f"[{s:6.2f}-{e:6.2f}] {t}")
    print('\n"cues": [')
    for s, e, t in rows:
        print(f'    [{s:.2f}, {json.dumps(t, ensure_ascii=False)}],')
    print("],")

if __name__ == "__main__":
    main()
