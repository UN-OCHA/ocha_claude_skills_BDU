#!/usr/bin/env python3
"""
OCHA pooled-fund data: CERF, CBPF and the combined Pooled Funds hub, from their public sources.

  check      --country C --amount A [--year Y] [--keyword K] [--fund cerf|cbpf|any]
             Is this figure in the data? Lists the source rows it matches (fund, allocation,
             project, date), or the closest ones when nothing matches.
  cerf       --year Y [--country C] [--emergency E] [--keyword K] --by country|agency|sector|
             application|emergency|window|project                        -> CSV
  cbpf       --year Y --country C (or --fund-id N) [--keyword K] --by fund|allocation|partner|
             partner_type|cluster|project                                 -> CSV
  allocations --year Y [--country C] --by country|month|fund_type        -> CSV (pfdata, CERF + CBPF)
  contributions --year Y [--fund cerf|cbpf|all] --by donor|fund|donor_type -> CSV
  funds      COUNTRY      which funds exist for a country (CERF, CBPF, regional windows)
  status     the hubs' data date

Output goes to ./ocha_data/ (override with --out); downloads are cached there for six hours
(--refresh to ignore the cache). Run it from the project folder. Standard library only.
FTS (the global funding dashboard) has its own script: fts.py, in the same folder.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import os
import re
import sys

sys.dont_write_bytecode = True   # no __pycache__ inside the skill folder
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pooled as pf  # noqa: E402


# ----------------------------------------------------------------------------------------
def out_dir(args) -> str:
    path = os.path.abspath(args.out)
    os.makedirs(path, exist_ok=True)
    pf.CACHE_DIR = os.path.join(path, ".cache")
    pf.REFRESH = args.refresh
    return path


def write_csv(path: str, rows: list) -> None:
    fields = []
    for r in rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def slug(*parts) -> str:
    return "_".join(re.sub(r"[^a-z0-9]+", "-", str(p).lower()).strip("-") for p in parts if p)


def money(v: float) -> str:
    return f"${v:,.2f}"


def show(rows: list, cols: list, limit: int = 25) -> None:
    for r in rows[:limit]:
        label = " · ".join(str(r.get(c) or "—") for c in cols)
        print(f"  {money(r['amount_usd']):>18}  {label}" + (f"  ({r['projects']} projects)" if "projects" in r else ""))
    if len(rows) > limit:
        print(f"  … {len(rows) - limit} more rows in the CSV")


def this_year() -> int:
    return datetime.date.today().year


# ----------------------------------------------------------------------------------------
CERF_BY = {"country": ["country"], "agency": ["agency"], "sector": ["sector"],
           "application": ["application", "country", "emergency", "approved_date"],
           "emergency": ["emergency"], "window": ["window"], "project": None}


def cmd_cerf(args):
    d = out_dir(args)
    iso3 = pf.resolve_country(args.country)["iso3"] if args.country else None
    projects = pf.cerf_projects(args.year, iso3, args.emergency, args.keyword)
    rows = pf.cerf_rows(projects, by_sector=(args.by == "sector"))
    if args.by == "application":   # an application's date is its last project's approval
        last = {}
        for r in rows:
            last[r["application"]] = max(last.get(r["application"], ""), r["approved_date"] or "")
        for r in rows:
            r["approved_date"] = last[r["application"]]
    table = sorted(rows, key=lambda r: -r["amount_usd"]) if args.by == "project" else pf.group(rows, CERF_BY[args.by])
    path = os.path.join(d, slug("cerf", args.year, args.country, args.emergency, args.keyword, "by", args.by) + ".csv")
    write_csv(path, table)
    total = sum(r["amount_usd"] for r in rows)
    print(f"CERF {args.year}{' · ' + args.country if args.country else ''}"
          f"{' · ' + args.emergency if args.emergency else ''}: {money(total)} in {len(projects)} projects")
    show(table, CERF_BY[args.by] or ["country", "agency", "project"])
    print(f"-> {path}")


CBPF_BY = {"fund": ["fund"], "allocation": ["fund", "allocation", "allocation_source"],
           "partner": ["partner", "partner_type"], "partner_type": ["partner_type"],
           "cluster": ["cluster"], "project": None}


def cbpf_fund_ids(args) -> list:
    if args.fund_id:
        return args.fund_id
    if args.country:
        funds = pf.cbpf_funds_for(pf.resolve_country(args.country))
        if not funds:
            raise pf.DataError(f"no open CBPF fund for {args.country}. `funds {args.country}` lists what exists.")
        return [f["Id"] for f in funds]
    return []


def cmd_cbpf(args):
    d = out_dir(args)
    ids = cbpf_fund_ids(args)
    if not ids:
        print("No country or fund given: reading every fund for the year, which takes minutes.", file=sys.stderr)
    raw = pf.cbpf_raw(args.year, ids)
    rows = pf.cbpf_rows(raw, by="cluster" if args.by == "cluster" else "project", keyword=args.keyword)
    table = sorted(rows, key=lambda r: -r["amount_usd"]) if args.by == "project" else pf.group(rows, CBPF_BY[args.by])
    path = os.path.join(d, slug("cbpf", args.year, args.country, *(args.fund_id or []), args.keyword, "by", args.by) + ".csv")
    write_csv(path, table)
    funds = sorted({r["fund"] for r in rows})
    print(f"CBPF {args.year} · {', '.join(funds) or 'no projects'}"
          f"{' · keyword ' + args.keyword if args.keyword else ''}: {money(sum(r['amount_usd'] for r in rows))}")
    show(table, CBPF_BY[args.by] or ["fund", "partner", "project"])
    print(f"-> {path}")


def cmd_allocations(args):
    d = out_dir(args)
    rows = pf.pf_allocations(args.year)
    if args.country:
        rows = [r for r in rows if r["iso3"] == pf.resolve_country(args.country)["iso3"]]
    keys = {"country": ["country", "fund_type"], "month": ["month", "fund_type"], "fund_type": ["fund_type"]}[args.by]
    table = pf.group(rows, keys, count=None)
    path = os.path.join(d, slug("pfdata_allocations", args.year, args.country, "by", args.by) + ".csv")
    write_csv(path, table)
    print(f"Pooled Funds hub, approved allocations {args.year or 'all years'}: {money(sum(r['amount_usd'] for r in rows))}")
    show(table, keys)
    print(f"-> {path}")


def cmd_contributions(args):
    d = out_dir(args)
    rows = pf.pf_contributions(args.year)
    if args.fund == "cerf":
        rows = [r for r in rows if r["fund"] == "CERF"]
    elif args.fund == "cbpf":
        rows = [r for r in rows if r["fund"] != "CERF"]
    keys = {"donor": ["donor", "donor_type"], "fund": ["fund"], "donor_type": ["donor_type"]}[args.by]
    paid = pf.group(rows, keys, value="paid_usd", count=None)
    pledged = {tuple(r[k] for k in keys): r["pledged_usd"] for r in pf.group(rows, keys, value="pledged_usd", count=None)}
    for r in paid:
        r["pledged_usd"] = pledged.get(tuple(r[k] for k in keys), 0.0)
    path = os.path.join(d, slug("contributions", args.fund, args.year, "by", args.by) + ".csv")
    write_csv(path, paid)
    print(f"Contributions {args.year} to {args.fund.upper()}: paid {money(sum(r['paid_usd'] for r in rows))}, "
          f"pledged {money(sum(r['pledged_usd'] for r in rows))}")
    for r in paid[:15]:
        print(f"  {money(r['paid_usd']):>18} paid  {money(r['pledged_usd']):>18} pledged  {' · '.join(str(r[k]) for k in keys)}")
    print(f"-> {path}")


def cmd_funds(args):
    out_dir(args)
    c = pf.resolve_country(args.country)
    print(f"{c['name']} ({c['iso3']})")
    print("  CERF: allocates by country; CERF projects carry the country, not a fund window")
    for f in pf.cbpf_funds_for(c):
        parent = f" — window of fund {f['ParentPooledFundId']}" if f.get("ParentPooledFundId") else ""
        print(f"  CBPF: {f['PoolfundName']}  (fund id {f['Id']}){parent}")
    names = [x["PooledFundName"] for x in pf.countries() if x["id"] in c["pf_ids"]]
    print(f"  Pooled Funds hub files list it as: {'; '.join(names)}")


def cmd_status(args):
    out_dir(args)
    for k, v in pf.data_dates().items():
        print(f"{k}: {v}")


# ----------------------------------------------------------------------------------------
# check — find a figure in the sources
# ----------------------------------------------------------------------------------------
def rounding_tolerance(amount: float) -> float:
    """A figure written as 2,287,000 was rounded to thousands: allow half a thousand either way.
    Up to millions; a figure like 6,000,000 still matches 5,986,821, and the report says 'rounded'."""
    a, k = int(round(amount)), 0
    while a and a % 10 == 0 and k < 6:
        a //= 10
        k += 1
    return 0.5 * 10 ** k if k else 0.5


def candidates(args, country: dict) -> list:
    out = []
    years = [args.year] if args.year else [this_year(), this_year() - 1]
    kw = args.keyword
    if args.fund in ("cerf", "any"):
        for y in years:
            prj = pf.cerf_projects(y, country["iso3"])
            rows = pf.cerf_rows(prj)
            if kw:
                rows_kw = pf.cerf_rows([p for p in prj if re.search(kw, " ".join(
                    str(p.get(k) or "") for k in ("emergencyTypeName", "projectTitle", "projectSummary")), re.I)])
            else:
                rows_kw = rows
            for r in rows_kw:
                out.append(dict(source="CERF data hub", level="project", fund="CERF", amount=r["amount_usd"],
                                date=r["approved_date"], ref=f"{r['project']} {r['agency']} ({r['emergency']})"))
            apps = {}
            for r in rows_kw:
                a = apps.setdefault(r["application"], {"amount": 0.0, "date": "", "em": r["emergency"], "n": 0})
                a["amount"] += r["amount_usd"]
                a["date"] = max(a["date"], r["approved_date"] or "")
                a["n"] += 1
            for code, a in apps.items():
                out.append(dict(source="CERF data hub", level="allocation", fund="CERF", amount=a["amount"],
                                date=a["date"], ref=f"{code} ({a['em']}, {a['n']} projects)"))
            if kw and rows_kw:
                out.append(dict(source="CERF data hub", level=f"all '{kw}' in {y}", fund="CERF",
                                amount=sum(r["amount_usd"] for r in rows_kw), date=str(y),
                                ref=f"{len(apps)} allocations, {len(rows_kw)} projects"))
            out.append(dict(source="CERF data hub", level=f"year total {y}", fund="CERF",
                            amount=sum(r["amount_usd"] for r in rows), date=str(y), ref=f"{len(rows)} projects"))
    if args.fund in ("cbpf", "any"):
        funds = pf.cbpf_funds_for(country)
        ids = [f["Id"] for f in funds]
        for y in years if ids else []:
            raw = pf.cbpf_raw(y, ids)
            allp = pf.cbpf_rows(raw)
            rows = pf.cbpf_rows(raw, keyword=kw) if kw else allp
            for r in rows:
                out.append(dict(source="CBPF data hub", level="project", fund=r["fund"], amount=r["amount_usd"],
                                date=r["approved_date"], ref=f"{r['project']} {r['partner']}"))
            groups = {}
            for scope, rs in (("allocation", allp), (f"'{kw}' projects in allocation", rows if kw else [])):
                for r in rs:
                    g = groups.setdefault((scope, r["fund"], r["allocation_id"]),
                                          {"amount": 0.0, "date": "", "title": r["allocation"], "n": 0})
                    g["amount"] += r["amount_usd"]
                    g["date"] = max(g["date"], r["approved_date"] or "")
                    g["n"] += 1
            for (scope, fund, _), g in groups.items():
                out.append(dict(source="CBPF data hub", level=scope, fund=fund, amount=g["amount"], date=g["date"],
                                ref=f"{(g['title'] or '')[:90]} ({g['n']} projects)"))
            byfund = {}
            for r in rows:
                byfund[r["fund"]] = byfund.get(r["fund"], 0.0) + r["amount_usd"]
            for fund, amt in byfund.items():
                out.append(dict(source="CBPF data hub", level=f"all {'%r ' % kw if kw else ''}projects in {y}",
                                fund=fund, amount=amt, date=str(y), ref=""))
    for y in years:
        for r in pf.pf_allocations(y):
            if r["iso3"] != country["iso3"]:
                continue
            if args.fund != "any" and r["fund_type"].lower() != args.fund:
                continue
            # This file has no emergency type, title or fund window: say so on the row, so a
            # same-sized allocation for a different emergency is never read as the match.
            fund = "CERF" if r["fund_type"] == "CERF" else "CBPF (which fund: not in this file)"
            level = "country-month, all emergencies" if kw else "country-month"
            out.append(dict(source="Pooled Funds hub", level=level, fund=fund,
                            amount=r["amount_usd"], date=r["month"], ref=f"filed under '{r['country']}'"))
    return out


def cmd_check(args):
    out_dir(args)
    country = pf.resolve_country(args.country)
    tol = args.tolerance if args.tolerance is not None else rounding_tolerance(args.amount)
    rows = candidates(args, country)
    for r in rows:
        r["diff"] = r["amount"] - args.amount
    hits = sorted([r for r in rows if abs(r["diff"]) <= tol], key=lambda r: abs(r["diff"]))
    print(f"Looking for {money(args.amount)} for {country['name']}"
          f"{' · ' + args.keyword if args.keyword else ''} (allowing ±{tol:,.0f} for rounding)")
    print(f"Data as of: {pf.data_dates().get('cbpf_and_pfdata_last_updated') or 'unknown'}")
    if hits:
        print("MATCH: yes")
        for r in hits:
            exact = "exact" if abs(r["diff"]) < 1 else f"rounded (source {money(r['amount'])})"
            print(f"  {exact:<34} {r['fund']} — {r['level']} — {r['date']} — {r['ref']}  [{r['source']}]")
    else:
        print("MATCH: no. Closest figures in the sources:")
        for r in sorted(rows, key=lambda r: abs(r["diff"]))[:args.closest]:
            print(f"  {money(r['amount']):>18} ({r['diff']:+,.0f})  {r['fund']} — {r['level']} — {r['date']} — {r['ref']}  [{r['source']}]")


# ----------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="ocha_data", help="output folder (default ./ocha_data)")
    ap.add_argument("--refresh", action="store_true", help="ignore cached downloads")
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check")
    c.add_argument("--country", required=True)
    c.add_argument("--amount", required=True, type=lambda s: float(s.replace(",", "").replace("$", "")))
    c.add_argument("--year", type=int)
    c.add_argument("--keyword", help="regular expression on emergency type / titles, e.g. 'ebola|evd|mve'")
    c.add_argument("--fund", choices=["cerf", "cbpf", "any"], default="any")
    c.add_argument("--tolerance", type=float, help="USD either way (default: from the figure's rounding)")
    c.add_argument("--closest", type=int, default=8)

    ce = sub.add_parser("cerf")
    ce.add_argument("--year", type=int, default=this_year())
    ce.add_argument("--country"); ce.add_argument("--emergency"); ce.add_argument("--keyword")
    ce.add_argument("--by", choices=list(CERF_BY), default="country")

    cb = sub.add_parser("cbpf")
    cb.add_argument("--year", type=int, default=this_year())
    cb.add_argument("--country"); cb.add_argument("--fund-id", type=int, nargs="+"); cb.add_argument("--keyword")
    cb.add_argument("--by", choices=list(CBPF_BY), default="allocation")

    al = sub.add_parser("allocations")
    al.add_argument("--year", type=int, default=this_year()); al.add_argument("--country")
    al.add_argument("--by", choices=["country", "month", "fund_type"], default="country")

    co = sub.add_parser("contributions")
    co.add_argument("--year", type=int, default=this_year())
    co.add_argument("--fund", choices=["cerf", "cbpf", "all"], default="all")
    co.add_argument("--by", choices=["donor", "fund", "donor_type"], default="donor")

    fu = sub.add_parser("funds"); fu.add_argument("country")
    sub.add_parser("status")

    args = ap.parse_args()
    try:
        {"check": cmd_check, "cerf": cmd_cerf, "cbpf": cmd_cbpf, "allocations": cmd_allocations,
         "contributions": cmd_contributions, "funds": cmd_funds, "status": cmd_status}[args.cmd](args)
    except pf.DataError as exc:
        raise SystemExit(f"ocha-data: {exc}")


if __name__ == "__main__":
    main()
