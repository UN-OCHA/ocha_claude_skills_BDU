"""Make a .jsx safe for ExtendScript: ExtendScript reads script files in the system encoding, so
any non-ASCII character inside a string literal arrives garbled in InDesign ("·" -> "¬∑").
This rewrites every non-ASCII character inside double-quoted strings as \\uXXXX, in place.
Usage: python3 escape_jsx.py file.jsx [...]  -- run it after every edit of a script that sets text."""
import re, sys
for p in sys.argv[1:]:
    s = open(p, encoding="utf-8").read()
    out = re.sub(r'"(?:[^"\\\n]|\\.)*"', lambda m: "".join(c if ord(c) < 128 else "\\u%04X" % ord(c) for c in m.group(0)), s)
    left = re.findall(r'"[^"\n]*[^\x00-\x7f][^"\n]*"', out)
    open(p, "w", encoding="utf-8").write(out)
    print(p.rsplit("/", 1)[-1], "non-ASCII left in strings:", len(left))
