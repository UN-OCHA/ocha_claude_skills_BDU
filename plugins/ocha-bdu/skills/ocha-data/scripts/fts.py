#!/usr/bin/env python3
"""
Pull figures from the OCHA FTS Visualization Tool (PreCheck) Power BI dashboard.

    python3 fts.py headline                  headline figures + data date -> headline.json
    python3 fts.py donors [--top 15]         donor table + ranking        -> donors.csv, ranking.csv
    python3 fts.py page [PAGE]               every visual on a page       -> one CSV each
    python3 fts.py visual PAGE VISUAL_ID     one visual                   -> one CSV
    python3 fts.py pages                     list the report's pages
    python3 fts.py visuals [PAGE]            list a page's visuals and their ids
    python3 fts.py tables                    list the named tables (plans, sectors, countries, donors…)
    python3 fts.py table NAME|all            one named table, or all of them   -> fts_<name>.csv

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


# --------------------------------------------------------------------------------------------
# Named tables. Only 7 of the report's 49 pages are published (the rest are hidden drafts with
# no stored query, so they cannot be read, e.g. the Ebola one-pager). These are the useful tables
# on the published pages, mapped and checked on 11 Nov 2026. All show the dashboard's default
# view: 2026, global, pledges and outgoing flows excluded. Ids change if the FTS team rebuilds a
# page: `fts.py visuals PAGE` lists the current ones; update here and in reference/fts_report_map.md.
# --------------------------------------------------------------------------------------------
PAGE_PLANS = "9fc1ea690b6b64c05d51"      # "OnePager (Plans) V2" — GHO view
PAGE_WEEKLY = "ReportSection353c4b8293ee828c3e33"   # "Weekly"

TABLES = {
    # name: (page, visual id, first-column label, what it is)
    "plans": (PAGE_PLANS, "6bed06e2ab84e322e4ab", None,
              "every GHO plan: funding, requirements, coverage, plan type"),
    "plan-groups": (PAGE_WEEKLY, "b0a4c298653e5af791f7", None,
                    "GHO totals by plan group (HRPs, flash appeals, RRPs, other) and plan"),
    "years": (PAGE_WEEKLY, "a1521b8314273109b300", "Year",
              "inside GHO, outside GHO and total funding, requirements, coverage: 2024–2026"),
    "gho-sectors": (PAGE_PLANS, "a34334a12674240b4562", "Global sector",
                    "GHO funding, requirements and coverage by global sector"),
    "gho-countries": (PAGE_PLANS, "738054d9e4be236263d6", "Country",
                      "GHO funding, requirements and coverage by country"),
    "gho-donors": (PAGE_PLANS, "d6056b9a407734ebd7a0", None,
                   "GHO funding by donor, with donor category and share"),
    "gho-recipients": (PAGE_PLANS, "4addea0cb2d50c9b44e9", None,
                       "GHO funding by recipient organization"),
    "sectors": (pbi.PAGE_DONORS, "2424b9b1fb04e1d50ec1", None,
                "all humanitarian funding by global sector: total, inside and outside GHO"),
    "countries": (pbi.PAGE_DONORS, "08e5cbc1c6d2484c0f9c", None,
                  "all humanitarian funding by country: total, inside and outside GHO"),
    "donors": (pbi.PAGE_DONORS, "df0c7d1c3857fe6d533a", None,
               "all humanitarian funding by donor: total, share, inside and outside GHO"),
    "recipients": (pbi.PAGE_RECIPIENTS, "0c0b656c878e836bbe45", "Recipient",
                   "all humanitarian funding by recipient organization, with share"),
    "donor-types": (pbi.PAGE_RECIPIENTS, "53027e57bba09c3a177f", None,
                    "all humanitarian funding by donor type (governments, pooled funds…)"),
    "recipient-types": (pbi.PAGE_DONORS, "0cf191c67290a24d6d26", "Recipient type",
                        "all humanitarian funding by recipient type (UN, NGOs…)"),
    "earmarking": (pbi.PAGE_DONORS, "10b8addaa6002310360d", None,
                   "earmarked vs unearmarked share (Grand Bargain definition)"),
}

# Power BI's internal column names, as the decoder passes them through, -> plain names.
COLUMN_NAMES = {
    "%GT _calc_FINAL_USD_TotalFunding_MEAS": "Share",
    "FINAL USD TotalFunding MEAS1": "Total Funding",
    "%1": "Share",
    "%": "Share",
    "Org Destination Parent Display V2": "Recipient",
    "Org Destination Display V3 OrgType": "Recipient type",
    "_Dim_Plan_Group_Year": "Year",
    "Plan GroupType LONG": "Plan group",
    "Plan Year STR": "Plan year",
    "Meta IsEarmarked": "Earmarking",
}
# Classifier columns that only repeat one value on every row.
DROP_COLUMNS = {"GlobalCluster Classif NotSpec", "Country Classif SeparateNotSpec", "Plan IsEstimate"}


def tidy(rows: list, first_label) -> list:
    """Plain column names; the pivot's grand-total row (blank first cell) labelled 'Total'."""
    out = []
    for row in rows:
        new = {}
        for i, (k, v) in enumerate(row.items()):
            if k in DROP_COLUMNS:
                continue
            name = COLUMN_NAMES.get(k, k)
            if i == 0 and (first_label or k in ("..", "")):
                name = first_label or "Name"
            v = pbi.to_number(v)
            if "year" in name.lower() and isinstance(v, float) and v.is_integer():
                v = int(v)   # years arrive as numbers, 2026.0; write them as 2026
            new[name] = v
        first = next(iter(new))
        if new[first] in (None, ""):
            new[first] = "Total"
        out.append(new)
    return out


def cmd_tables(args):
    for name, (_, _, _, what) in TABLES.items():
        print(f"  {name:<16} {what}")
    print("\nAll: the dashboard's default view — 2026, global, pledges excluded.")


def cmd_table(args):
    d = out_dir(args)
    model = pbi.fetch_model(args.refresh)
    date = first_value(pbi.run_visual(model, pbi.PAGE_87_DAYS, DATA_DATE_VISUAL))
    names = list(TABLES) if args.name == "all" else [args.name]
    for name in names:
        if name not in TABLES:
            raise SystemExit(f"No table '{name}'. `fts.py tables` lists them.")
        page, vid, label, what = TABLES[name]
        try:
            rows = tidy(pbi.run_visual(model, page, vid), label)
        except pbi.PowerBIError as exc:
            raise SystemExit(f"STOP: table '{name}' ({what}) could not be read: {exc}. The FTS team may have "
                             f"rebuilt the page; `fts.py visuals {page}` lists the current visual ids. Update TABLES "
                             f"in fts.py and reference/fts_report_map.md, and tell Javier.")
        path = os.path.join(d, f"fts_{name.replace('-', '_')}.csv")
        write_csv(path, rows)
        print(f"{len(rows):>5} rows  {name:<16} -> {path}")
    print(f"Data as of {date}")


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
    sub.add_parser("tables")
    tb = sub.add_parser("table"); tb.add_argument("name", help="a name from `fts.py tables`, or 'all'")
    args = ap.parse_args()
    try:
        {"pages": cmd_pages, "visuals": cmd_visuals, "visual": cmd_visual, "page": cmd_page,
         "headline": cmd_headline, "donors": cmd_donors,
         "tables": cmd_tables, "table": cmd_table}[args.cmd](args)
    except pbi.PowerBIError as exc:
        raise SystemExit(f"Could not read the FTS dashboard: {exc}")


if __name__ == "__main__":
    main()
