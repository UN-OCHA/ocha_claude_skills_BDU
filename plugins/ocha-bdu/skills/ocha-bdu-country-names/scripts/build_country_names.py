#!/usr/bin/env python3
"""Rebuild data/country_names.csv from the two UN sources of truth (agreed with Paolo, Oct 2026).

    uv run --with openpyxl python3 build_country_names.py      (openpyxl reads the UNTERM Excel)

1. UNTERM (UN Secretariat terminology): official short and formal names of the 193 Member States,
   the 2 Observer States and 2 members of specialized agencies, in the six UN languages.
   Downloaded from the same API the UNTERM country page uses for its "Excel" button.
2. UN M49 (UN Statistics Division): ISO2/ISO3/M49 codes, UN regions, LDC/LLDC/SIDS, and the
   countries and areas that are NOT in UNTERM's list (territories such as Western Sahara or Puerto Rico).

Writes data/country_names.csv (one row per country or area) and data/sources.json (dates, counts).
Stops, writing nothing, if any UNTERM name can't be matched to an M49 code: a silent gap here
would put a wrong or missing code into every chart and map that uses the file.
"""
import csv, datetime, html, io, json, os, re, sys, urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNTERM_XLSX = "https://conferences.unite.un.org/untermapi/api/term/downloadCountries"
M49_PAGE = "https://unstats.un.org/unsd/methodology/m49/overview/"
UA = {"User-Agent": "Mozilla/5.0 (OCHA BDU country names)"}


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        return r.read()


def key(name):
    """Match key: UNTERM writes 'Sudan (the)' and "Côte d'Ivoire", M49 'Sudan' and 'Côte d’Ivoire'."""
    name = re.sub(r"\s*\*+$", "", name.strip())
    name = re.sub(r"\s*\((the|The)\)$", "", name)
    return name.replace("’", "'").strip().lower()


def main():
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(fetch(UNTERM_XLSX)), read_only=True)
    rows = list(wb.worksheets[0].iter_rows(values_only=True))
    head = [h.strip() for h in rows[0]]
    unterm = [dict(zip(head, r)) for r in rows[1:] if r[0] and r[1]]

    page = fetch(M49_PAGE).decode("utf-8")
    i = page.find('id="ENG_Overview"')
    seg = page[i:page.find("</table>", i)]
    m49 = []
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", seg, re.S):
        c = [html.unescape(re.sub("<[^>]+>", "", x)).strip() for x in re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)]
        if len(c) >= 16 and c[9].isdigit():
            m49.append(c)
    by_key = {key(c[8]): c for c in m49}

    out, missing, used = [], [], set()
    for u in unterm:
        raw = u["English short"].strip()
        stars = len(re.search(r"\*+$", raw).group(0)) if re.search(r"\*+$", raw) else 0
        status = {0: "Member State", 1: "Observer State", 2: "Member of specialized agencies"}[stars]
        m = by_key.get(key(raw))
        if not m:
            missing.append(raw)
            continue
        used.add(key(raw))
        out.append(row(m, status, u))
    if missing:
        sys.exit("Not written: these UNTERM names have no M49 match, fix the matching first:\n  " + "\n  ".join(missing))
    for k, m in by_key.items():
        if k not in used:
            out.append(row(m, "Other area (M49 only, not in UNTERM)", None))
    out.sort(key=lambda r: r["name_en_short"].lower())

    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    cols = list(out[0].keys())
    with open(os.path.join(HERE, "data", "country_names.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(out)
    counts = {}
    for r in out:
        counts[r["un_status"]] = counts.get(r["un_status"], 0) + 1
    with open(os.path.join(HERE, "data", "sources.json"), "w", encoding="utf-8") as f:
        json.dump({"built": datetime.date.today().isoformat(), "unterm": UNTERM_XLSX, "m49": M49_PAGE,
                   "rows": len(out), "by_status": counts}, f, indent=2, ensure_ascii=False)
    print(f"{len(out)} rows written:", counts)


def row(m, status, u):
    clean = lambda s: re.sub(r"\s*\*+$", "", (s or "").strip())
    r = {"iso3": m[11], "iso2": m[10], "m49": m[9], "un_status": status,
         "name_en_short": clean(u["English short"]) if u else m[8],
         "name_en_formal": clean(u["English formal"]) if u else "",
         "name_fr_short": clean(u["French short"]) if u else "",
         "name_es_short": clean(u["Spanish short"]) if u else "",
         "name_ar_short": clean(u["Arabic short"]) if u else "",
         "name_zh_short": clean(u["Chinese short"]) if u else "",
         "name_ru_short": clean(u["Russian short"]) if u else "",
         "name_fr_formal": clean(u["French formal"]) if u else "",
         "name_es_formal": clean(u["Spanish formal"]) if u else "",
         "name_ar_formal": clean(u["Arabic formal"]) if u else "",
         "name_zh_formal": clean(u["Chinese formal"]) if u else "",
         "name_ru_formal": clean(u["Russian formal"]) if u else "",
         "name_m49": m[8], "region": m[3], "subregion": m[5], "intermediate_region": m[7],
         "ldc": "yes" if m[12] else "", "lldc": "yes" if m[13] else "", "sids": "yes" if m[14] else ""}
    return r


if __name__ == "__main__":
    main()
