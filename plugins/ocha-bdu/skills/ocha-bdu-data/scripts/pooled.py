"""
Readers for OCHA's three pooled-fund data hubs. Standard library only, Python 3.9+.

    cerf.data.unocha.org   CERF only     -> cerfgms-webapi.unocha.org   (project level)
    cbpf.data.unocha.org   CBPF only     -> cbpfapi.unocha.org/vo2/odata (project level)
    pfdata.unocha.org      CERF + CBPF   -> the pfbi web job's CSVs + cbpfgms.github.io lookups
                                            (country-month level; the hub's own summary files)

All three are public: no keys. Every figure keeps the fund it came from, because a country can
have more than one fund (Kenya: the closed Kenya CBPF and "Kenya (ESAHF)", a window of the
regional East and Southern Africa Humanitarian Fund). See reference/sources.md for the traps.

Maintained by the OCHA Brand and Design Unit (BDU), ochavisual@un.org.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from typing import Dict, Iterable, List, Optional

# --------------------------------------------------------------------------------------
# Endpoints. Found by reading the hubs' own chart scripts (Nov 2026). If one moves, open the
# hub in a browser, watch the network tab, and update it here and in reference/sources.md.
# --------------------------------------------------------------------------------------
CERF_API = "https://cerfgms-webapi.unocha.org/v1"
CBPF_API = "https://cbpfapi.unocha.org/vo2/odata"
PF_DOWNLOAD = "https://pfbi-webjob-contribution-prod-g7b3h4b9ftfahnbk.eastus2-01.azurewebsites.net/download"
PF_MST = "https://cbpfgms.github.io/pfbi-data/mst"

CACHE_DIR = os.path.join(os.getcwd(), "ocha_data", ".cache")   # set by the CLI from --out
CACHE_TTL = 6 * 3600   # the hubs refresh overnight; six hours keeps a working session consistent
REFRESH = False

_UA = "Mozilla/5.0 (Macintosh) OCHA-BDU-ocha-data/1.0"


class DataError(RuntimeError):
    pass


# --------------------------------------------------------------------------------------
# Fetching, with a small file cache
# --------------------------------------------------------------------------------------
def fetch(url: str, params: Optional[dict] = None, timeout: int = 300) -> bytes:
    if params:
        url = url + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    key = hashlib.sha1(url.encode()).hexdigest()[:20]
    path = os.path.join(CACHE_DIR, key)
    if not REFRESH and os.path.exists(path) and time.time() - os.path.getmtime(path) < CACHE_TTL:
        with open(path, "rb") as fh:
            return fh.read()
    req = urllib.request.Request(url, headers={"User-Agent": _UA, "Accept-Encoding": "gzip",
                                               "Accept": "application/json, text/csv, */*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            if resp.headers.get("Content-Encoding") == "gzip":
                body = gzip.decompress(body)
    except urllib.error.HTTPError as exc:
        raise DataError(f"{exc.code} from {url}") from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise DataError(f"could not reach {url}: {exc}") from None
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(body)
    return body


def fetch_json(url: str, params: Optional[dict] = None):
    body = fetch(url, params)
    try:
        return json.loads(body.decode("utf-8-sig"))
    except ValueError:
        raise DataError(f"not JSON: {url} (starts {body[:80]!r})") from None


def fetch_csv(url: str) -> List[dict]:
    return list(csv.DictReader(io.StringIO(fetch(url).decode("utf-8-sig"))))


def odata(entity: str, filt: Optional[str] = None) -> List[dict]:
    """All rows of a CBPF OData entity, following paging links if the server pages."""
    params = {"$format": "json"}
    if filt:
        params["$filter"] = filt
    data = fetch_json(f"{CBPF_API}/{entity}", params)
    rows = list(data.get("value", []))
    nxt = data.get("odata.nextLink")
    while nxt:
        page = fetch_json(nxt if nxt.startswith("http") else f"{CBPF_API}/{nxt}")
        rows += page.get("value", [])
        nxt = page.get("odata.nextLink")
    return rows


def num(v) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def as_int(v) -> Optional[int]:
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


# --------------------------------------------------------------------------------------
# Lookups and country resolution
# --------------------------------------------------------------------------------------
def mst(name: str) -> list:
    return fetch_json(f"{PF_MST}/{name}.json")


# Short names people actually type. Keys are lower-case; values are ISO3.
ALIASES = {"drc": "COD", "dr congo": "COD", "congo drc": "COD", "car": "CAF", "opt": "PSE",
           "palestine": "PSE", "sudan": "SDN", "syria": "SYR", "south sudan": "SSD",
           "venezuela": "VEN", "turkey": "TUR", "turkiye": "TUR", "türkiye": "TUR"}


def countries() -> List[dict]:
    """pfdata's MstCountry: one row per pooled-fund 'country', regional fund windows included."""
    return mst("MstCountry")


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def resolve_country(text: str) -> dict:
    """'DRC', 'Kenya', 'COD', 'CD' -> {'iso3','iso2','name','pf_ids':[MstCountry ids]}."""
    q = _norm(text)
    rows = countries()
    iso3 = ALIASES.get(q)
    if not iso3:
        for c in rows:
            keys = {_norm(c["PooledFundName"]), _norm(c.get("PooledFundNameAbbrv")),
                    _norm(c.get("CountryCode")), _norm(c.get("ISO2Code"))}
            if q in keys:
                iso3 = c["CountryCode"]
                break
    if not iso3:
        hits = {c["CountryCode"] for c in rows if q and q in _norm(c["PooledFundName"])}
        if len(hits) == 1:
            iso3 = hits.pop()
        elif hits:
            raise DataError(f"'{text}' matches several countries: {', '.join(sorted(hits))}. Use the ISO3 code.")
    if not iso3:
        raise DataError(f"no pooled-fund country matches '{text}'")
    same = [c for c in rows if c.get("CountryCode") == iso3]
    main = next((c for c in same if "(" not in c["PooledFundName"]), same[0])
    return {"iso3": iso3, "iso2": main.get("ISO2Code"), "name": main["PooledFundName"],
            "pf_ids": [c["id"] for c in same]}


# --------------------------------------------------------------------------------------
# CERF — project level, from the CERF data hub's API
# --------------------------------------------------------------------------------------
def cerf_projects(year: Optional[int] = None, iso3: Optional[str] = None,
                  emergency: Optional[str] = None, keyword: Optional[str] = None) -> List[dict]:
    """One row per CERF project. `emergency` matches the emergency type ("Ebola");
    `keyword` matches emergency type, project title or summary."""
    out = []
    for p in fetch_json(f"{CERF_API}/project/All.json"):
        if year and p.get("year") != year:
            continue
        if iso3 and p.get("countryCode") != iso3:
            continue
        if emergency and emergency.lower() not in (p.get("emergencyTypeName") or "").lower():
            continue
        if keyword:
            text = " ".join(str(p.get(k) or "") for k in ("emergencyTypeName", "projectTitle", "projectSummary"))
            if not re.search(keyword, text, re.I):
                continue
        out.append(p)
    return out


def cerf_rows(projects: Iterable[dict], by_sector: bool = False) -> List[dict]:
    """Flatten CERF projects to plain rows (one per project, or one per project-sector)."""
    rows = []
    for p in projects:
        base = {
            "fund": "CERF",
            "window": p.get("windowFullName"),
            "year": p.get("year"),
            "country": p.get("countryName"),
            "iso3": p.get("countryCode"),
            "application": p.get("applicationCode"),
            "project": p.get("projectCode"),
            "agency": p.get("agencyShortName"),
            "emergency": p.get("emergencyTypeName"),
            "status": p.get("allocationStatus"),
            "approved_date": (p.get("dateUSGSignature") or "")[:10],
            "title": p.get("projectTitle"),
        }
        if by_sector:
            for s in (p.get("projectsectors") or {}).get("projectsectors", []):
                rows.append({**base, "sector": s.get("sectorName"), "amount_usd": num(s.get("sectorAmount"))})
        else:
            rows.append({**base, "amount_usd": num(p.get("totalAmountApproved"))})
    return rows


# --------------------------------------------------------------------------------------
# CBPF — project level, from the CBPF data hub's OData API
# --------------------------------------------------------------------------------------
def cbpf_funds() -> List[dict]:
    """Every CBPF fund, regional windows included: Id, PoolfundName, CountryCode (ISO2), parent."""
    return odata("Poolfund")


def cbpf_funds_for(country: dict) -> List[dict]:
    return [f for f in cbpf_funds() if f.get("CountryCode") == country["iso2"]]


def cbpf_allocations(year: int, fund_ids: Optional[List[int]] = None) -> List[dict]:
    """Allocation rounds (title, source, approved totals). FundTypeId here: 1 = CBPF, 2 = CERF."""
    rows = odata("AllocationTypes", f"AllocationYear eq {int(year)}")
    rows = [r for r in rows if r.get("FundTypeId") == 1]
    if fund_ids:
        rows = [r for r in rows if r.get("PooledFundId") in fund_ids]
    return rows


def cbpf_raw(year: int, fund_ids: Optional[List[int]] = None) -> List[dict]:
    """ProjectSummary rows: one per project x cluster x location. Slow (~40 s for four funds);
    always pass fund ids when you can."""
    filt = f"AllocationYear eq {int(year)}"
    if fund_ids:
        filt += " and (" + " or ".join(f"PooledFundId eq {int(i)}" for i in fund_ids) + ")"
    return odata("ProjectSummary", filt)


def cbpf_rows(raw: List[dict], by: str = "project", keyword: Optional[str] = None) -> List[dict]:
    """Collapse ProjectSummary rows. by='project' (one per project) or 'cluster' (one per
    project-cluster). `keyword` matches project or allocation title."""
    if keyword:
        raw = [r for r in raw if re.search(keyword, f"{r.get('ProjectTitle') or ''} {r.get('AllocationType') or ''}", re.I)]
    out: Dict[tuple, dict] = {}
    totals: Dict[str, float] = defaultdict(float)
    for r in raw:
        code = r["ChfProjectCode"]
        key = (code, r.get("Cluster")) if by == "cluster" else (code,)
        row = out.get(key)
        if row is None:
            row = out[key] = {
                "fund": r.get("PooledFundName"),
                "fund_id": r.get("PooledFundId"),
                "year": r.get("AllocationYear"),
                "allocation": r.get("AllocationType"),
                "allocation_id": r.get("AllocationTypeId"),
                "allocation_source": r.get("AllocationSourceName"),
                "project": code,
                "partner": r.get("OrganizationName"),
                "partner_type": r.get("OrganizationType"),
                "status": r.get("ProjectStatus"),
                "approved_date": (r.get("ApprovedDate") or "")[:10],
                "title": r.get("ProjectTitle"),
            }
            if by == "cluster":
                row["cluster"] = r.get("Cluster")
            row["amount_usd"] = 0.0 if by == "cluster" else num(r.get("Budget"))
        if by == "cluster":
            # Do NOT take BudgetByCluster from one row: a cluster can hold several sub-clusters
            # (Protection, GBV, Child Protection all read "Protection"), each with its own
            # BudgetByCluster, and rows repeat per location. The rows are unique per sub-cluster
            # x admin-1 location, so summing BudgetByClusterByAdminLocation1 gives the cluster
            # amount, and summed over a project it equals Budget (checked on 170 projects, Nov 2026).
            v = num(r.get("BudgetByClusterByAdminLocation1"))
            row["amount_usd"] += v
            totals[code] += v
    if by == "cluster":
        budgets = {r["ChfProjectCode"]: num(r.get("Budget")) for r in raw}
        off = [c for c, b in budgets.items() if abs(totals[c] - b) > 1]
        if off:
            raise DataError(f"cluster split no longer adds up to the project budget for {len(off)} project(s), "
                            f"e.g. {off[0]}: the CBPF API's row layout changed. Fix cbpf_rows in pooled.py.")
    return list(out.values())


# --------------------------------------------------------------------------------------
# pfdata — the combined CERF + CBPF hub's summary files
# --------------------------------------------------------------------------------------
PF_FUNDTYPE = {"1": "CERF", "2": "CBPF"}    # pfdata's MstFund. NOT the same as cbpfapi's FundTypeId.


def pf_allocations(year: Optional[int] = None) -> List[dict]:
    """Approved allocations per country per month, CERF and CBPF. The country is pfdata's
    MstCountry, and a regional fund's money is filed under the plain country (Kenya, not
    'Kenya (ESAHF)'): this file cannot tell you WHICH fund, only CERF vs CBPF."""
    names = {c["id"]: c for c in countries()}
    out = []
    for r in fetch_csv(f"{PF_DOWNLOAD}/loadAllocations/allocationSummarybyapproveddate.csv"):
        month, _, yr = (r.get("ApprovedDate") or "").partition("-")
        if year and yr != str(year):
            continue
        c = names.get(as_int(r.get("PooledFundName")), {})
        out.append({"fund_type": PF_FUNDTYPE.get(r.get("FundType"), r.get("FundType")),
                    "country": c.get("PooledFundName"), "iso3": c.get("CountryCode"),
                    "pf_country_id": as_int(r.get("PooledFundName")),
                    "month": f"{yr}-{month}", "year": as_int(yr), "amount_usd": num(r.get("Budget"))})
    return out


def pf_contributions(year: Optional[int] = None) -> List[dict]:
    """Contributions per donor to each fund (CERF = pooled fund 109), pledged and paid."""
    names = {c["id"]: c["PooledFundName"] for c in countries()}
    donors = {d["id"]: d for d in mst("MstDonor")}
    out = []
    for r in fetch_csv(f"{PF_DOWNLOAD}/loadContributionByCERFCBPFAll/contributionbycerfcbpfAll.csv"):
        if year and r.get("FiscalYear") != str(year):
            continue
        d = donors.get(as_int(r.get("DonorId")), {})
        pid = as_int(r.get("PooledFundId"))
        out.append({"year": as_int(r.get("FiscalYear")), "pledge_paid_month": r.get("PledgePaidDate"),
                    # A donor can be missing from pfdata's lookup (Isle of Man, Nov 2026): keep its
                    # money visible under its id instead of a blank name. The CBPF hub has the name.
                    "donor": d.get("donorName") or f"donor id {r.get('DonorId')} (not in pfdata's donor list)",
                    "donor_type": d.get("donorType"),
                    "fund": "CERF" if names.get(pid) == "CERF" else f"CBPF {names.get(pid)}",
                    "pledged_usd": num(r.get("PledgeAmt")), "paid_usd": num(r.get("PaidAmt"))})
    return out


def data_dates() -> dict:
    """The hubs' own 'last updated' stamp (the CBPF API's, which pfdata shows too)."""
    try:
        v = fetch_json(f"{CBPF_API}/LastModified")["value"][0]["last_updated_date"]
    except (DataError, KeyError, IndexError):
        v = None
    return {"cbpf_and_pfdata_last_updated": v}


# --------------------------------------------------------------------------------------
# Helpers for tables
# --------------------------------------------------------------------------------------
def group(rows: List[dict], keys: List[str], value: str = "amount_usd", count: str = "project") -> List[dict]:
    tot: Dict[tuple, float] = defaultdict(float)
    n: Dict[tuple, set] = defaultdict(set)
    for r in rows:
        k = tuple(r.get(x) for x in keys)
        tot[k] += num(r.get(value))
        if count:
            n[k].add(r.get(count))
    out = []
    for k, v in sorted(tot.items(), key=lambda kv: -kv[1]):
        row = dict(zip(keys, k))
        row[value] = round(v, 2)
        if count:
            row["projects"] = len(n[k])
        out.append(row)
    return out
