#!/usr/bin/env python3
"""
Pull figures from the OCHA FTS Visualization Tool (PreCheck) Power BI dashboard.

    python3 fts.py headline                  headline figures + data date -> headline.json
    python3 fts.py donors [--top 15]         donor table + ranking        -> donors.csv, ranking.csv
    python3 fts.py page [PAGE]               every visual on a page       -> one CSV each
    python3 fts.py visual PAGE VISUAL_ID     one visual                   -> one CSV
    python3 fts.py pages                     list the report's pages
    python3 fts.py visuals [PAGE]            list a page's visuals and their ids

Output goes to ./fts_data/ under the current directory (override with --out). Run it from
the project folder, so the figures land beside the work that uses them. The report
definition is cached there too (~1.2 MB, reused for six hours).

PAGE defaults to the campaign one-pager "OnePager (87 Days)".

Every figure is read from the dashboard's own visuals — the stored query each visual runs,
replayed verbatim — so it matches the dashboard exactly. Nothing is recalculated.

Standard library only.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys

# No __pycache__ inside the skill folder: the skills are mirrored to Cowork, and a
# compiled cache has no business travelling with them.
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ocha_fts_pbi as pbi  # noqa: E402

# Headline figures on the one-pager. Verified live 2026-10-05.
# Three come from their own cards, by visual id:
KPI_VISUALS = {
    "private_sector_usd": "2bd0f1079166b47156bc",
    "pooled_funds_share": "8eb1d994568b5b556490",
    "direct_to_local_share": "0faa810408b052e06300",
}
# The six GHO figures were separate cards until the FTS team rebuilt the report on 2-3 Oct 2026 (the
# tracker's runs failed on it). They are now one row of ONE custom visual, read by FIELD NAME.
VISUAL_KPIS = "8f70bf0c55723720a799"
KPI_FIELDS = {
    "prioritized_requirements_usd": "FINAL USD Required Prioritized ByGlobalCluster MEAS",
    # RECEIVED funds only. The "Prioritized Funding (USD)" card (c3ecfe62...) now includes pledges and
    # announcements ("USD InPlan Total WithPledges"): $14.40bn against $13.74bn received on 4 Oct.
    "prioritized_funding_usd": "USD InPlan Prioritized",
    "prioritized_coverage": "FINAL Coverage Prioritized ByGlobalCluster MEAS",
    "total_gho_requirements_usd": "FINAL USD Required ByGlobalCluster MEAS",
    "total_gho_funding_usd": "FINAL USD inPLan",
    "total_gho_coverage": "FINAL Coverage ByGlobalCluster MEAS",
}


def read_headline(model, page: str) -> dict:
    """All headline figures. Stops by name if the dashboard has moved a field again, rather than returning a
    zero or a neighbouring number."""
    figures = {k: first_value(pbi.run_visual(model, page, v)) for k, v in KPI_VISUALS.items()}
    rows = pbi.run_visual(model, page, VISUAL_KPIS)
    row = rows[0] if rows else {}
    absent = [f for f in KPI_FIELDS.values() if f not in row]
    if absent:
        raise SystemExit(f"STOP: the dashboard's headline-figures visual no longer has: {'; '.join(absent)}. "
                         f"It now has: {'; '.join(sorted(row)) or 'nothing'}. Update KPI_FIELDS in fts.py "
                         f"(and reference/report_map.md), and tell Javier.")
    figures.update({name: pbi.to_number(row[field]) for name, field in KPI_FIELDS.items()})
    return figures
DATA_DATE_VISUAL = "c299af827dcd82be601b"   # "FTS API checksum date"
DONORS_VISUAL = "756002108d716d0d1335"      # "By Donors / Source Organizations"
STATUS_VISUAL = "375875f4373661800d91"      # funding / pledges / announcements totals


def out_dir(args) -> str:
    path = os.path.abspath(args.out)
    os.makedirs(path, exist_ok=True)
    # Keep the report-definition cache with the outputs, not inside the skill folder:
    # the skill is mirrored to Cowork, and a 1.2 MB cache has no business there.
    pbi.MODEL_CACHE = os.path.join(path, ".model_cache.json")
    return path


def write_csv(path: str, rows: list[dict]) -> None:
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    fields = [f for f in fields if any(r.get(f) is not None for r in rows)]
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k: pbi.to_number(row.get(k)) for k in fields})


def first_value(rows: list[dict]):
    for row in rows:
        for value in row.values():
            if value is not None:
                return pbi.to_number(value)
    return None


def cmd_pages(args):
    out_dir(args)
    for p in pbi.list_pages(pbi.fetch_model(args.refresh)):
        print(f'{p["name"]}  {p["visuals"]:>3}  {p["title"]}')


def cmd_visuals(args):
    out_dir(args)
    for v in pbi.list_visuals(pbi.fetch_model(args.refresh), args.page):
        print(f'{v["id"]}  {v["type"]:<14} {v["title"]}')


def cmd_visual(args):
    d = out_dir(args)
    model = pbi.fetch_model(args.refresh)
    rows = pbi.run_visual(model, args.page, args.visual_id)
    path = os.path.join(d, f"{args.visual_id}.csv")
    write_csv(path, rows)
    print(f"{len(rows)} rows -> {path}")


def cmd_page(args):
    d = out_dir(args)
    model = pbi.fetch_model(args.refresh)
    for v in pbi.list_visuals(model, args.page):
        rows = pbi.run_visual(model, args.page, v["id"])
        path = os.path.join(d, f'{pbi.slugify(v["title"])}__{v["id"][:8]}.csv')
        write_csv(path, rows)
        print(f'{len(rows):>5} rows  {v["type"]:<14} {v["title"]}')


def cmd_headline(args):
    d = out_dir(args)
    model = pbi.fetch_model(args.refresh)
    page = pbi.PAGE_87_DAYS
    figures = read_headline(model, page)
    figures["data_date"] = first_value(pbi.run_visual(model, page, DATA_DATE_VISUAL))
    status = pbi.run_visual(model, page, STATUS_VISUAL)
    for row in status:
        label = (row.get("Status") or "").strip().lower()
        if label in ("pledges", "announcements"):
            figures[f"prioritized_{label}_usd"] = pbi.to_number(row.get("USD"))
    path = os.path.join(d, "headline.json")
    with open(path, "w") as fh:
        json.dump(figures, fh, indent=2)
    req = figures["prioritized_requirements_usd"] or 0
    fund = figures["prioritized_funding_usd"] or 0
    print(f"Data as of {figures['data_date']}")
    print(f"Prioritized: ${fund / 1e9:.2f}bn of ${req / 1e9:.2f}bn "
          f"({(figures['prioritized_coverage'] or 0) * 100:.1f}%)")
    print(f"-> {path}")


def cmd_donors(args):
    d = out_dir(args)
    model = pbi.fetch_model(args.refresh)
    rows = pbi.run_visual(model, pbi.PAGE_87_DAYS, DONORS_VISUAL)
    write_csv(os.path.join(d, "donors.csv"), rows)

    # The ranking counts governments and institutions only. The dashboard lists Private
    # Sector, Multilateral Banks and Other as separate categories; ranking them together
    # with governments is not what a donor ranking means.
    govs = [r for r in rows if (r.get("Donor category") or "").strip() == "Donor"]
    for r in govs:
        r["_amt"] = pbi.to_number(r.get("GHO Funding (Prioritized)")) or 0
    govs.sort(key=lambda r: -r["_amt"])
    ranking = [{
        "rank": i,
        "donor": r.get("Donor"),
        "funding_usd": round(r["_amt"]),
        "share_of_total_pct": round((pbi.to_number(r.get("Share of Total Funding")) or 0) * 100, 2),
        "pledges_usd": round(pbi.to_number(r.get("Pledges")) or 0),
        "announcements_usd": round(pbi.to_number(r.get("Announcements")) or 0),
    } for i, r in enumerate(govs[: args.top], start=1)]
    write_csv(os.path.join(d, "ranking.csv"), ranking)
    print(f"{len(rows)} donor rows, top {len(ranking)} ranked -> {d}")
    for r in ranking[:5]:
        print(f'  {r["rank"]:>2}  {r["donor"][:44]:<44} ${r["funding_usd"] / 1e6:>8,.1f}M')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="fts_data", help="output folder (default ./fts_data)")
    ap.add_argument("--refresh", action="store_true", help="ignore the cached report definition")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("pages")
    v = sub.add_parser("visuals"); v.add_argument("page", nargs="?", default=pbi.PAGE_87_DAYS)
    p = sub.add_parser("page"); p.add_argument("page", nargs="?", default=pbi.PAGE_87_DAYS)
    one = sub.add_parser("visual"); one.add_argument("page"); one.add_argument("visual_id")
    sub.add_parser("headline")
    dn = sub.add_parser("donors"); dn.add_argument("--top", type=int, default=15)
    args = ap.parse_args()
    try:
        {"pages": cmd_pages, "visuals": cmd_visuals, "visual": cmd_visual, "page": cmd_page,
         "headline": cmd_headline, "donors": cmd_donors}[args.cmd](args)
    except pbi.PowerBIError as exc:
        raise SystemExit(f"Could not read the FTS dashboard: {exc}")


if __name__ == "__main__":
    main()
