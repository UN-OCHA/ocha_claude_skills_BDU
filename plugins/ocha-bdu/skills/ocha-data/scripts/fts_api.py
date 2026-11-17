"""
FTS public API (api.hpc.tools) — funding tagged with an FTS keyword, such as EBOLA2026.

USE THIS ONLY FOR WHAT THE DASHBOARD CANNOT SHOW. The published figures (GHO funding, donors,
plans) come from the PreCheck dashboard (fts.py), because the API does not reproduce them. An
emergency response tracked by keyword has no dashboard page and, often, no FTS emergency page
either (the 2026 Ebola response: emergency 1031 had 0 flows; its flows carry the keyword
EBOLA2026). Always say a keyword figure came from the FTS API.

The API cannot filter by keyword on the server (filterBy=keyword, keywords, flowKeyword and
?keyword= all error, Nov 2026), so this pages through every flow of the year and filters here.

Counting rule (verified 17 Nov 2026 against OCHA Comms' published Ebola figure, $487M, and two
recipient lines in their 10 Nov sheet that matched to the dollar):
  status paid or commitment · boundary incoming AND internal · no de-duplication.
Incoming only gave $324.7M; leaf flows only $484.8M. Pledges are excluded.

Standard library only, Python 3.9+. Maintained by the OCHA Brand and Design Unit (BDU).
"""

from __future__ import annotations

import gzip
import json
import os
import time
import urllib.error
import urllib.request
from collections import defaultdict
from typing import Dict, List, Optional

API = "https://api.hpc.tools/v1/public/fts/flow"
CACHE_TTL = 6 * 3600
STATUSES = {"paid", "commitment"}
BOUNDARIES = {"incoming", "internal"}

# --by option -> (side of the flow, object type)
GROUPS = {
    "recipient": ("destinationObjects", "Organization"),
    "donor": ("sourceObjects", "Organization"),
    "country": ("destinationObjects", "Location"),
    "sector": ("destinationObjects", "GlobalCluster"),
    "plan": ("destinationObjects", "Plan"),
}


class ApiError(RuntimeError):
    pass


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "OCHA-BDU-ocha-data/1.0",
                                               "Accept": "application/json", "Accept-Encoding": "gzip"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                body = resp.read()
                if resp.headers.get("Content-Encoding") == "gzip":
                    body = gzip.decompress(body)
                return json.loads(body.decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            if attempt == 2:
                raise ApiError(f"FTS API did not answer {url}: {exc}") from None
            time.sleep(5 * (attempt + 1))
    raise ApiError("unreachable")


def year_flows(year: int, cache_dir: str, refresh: bool = False, progress=None) -> dict:
    """Every flow for the year, all pages. Cached (gzip) for six hours: ~25,000 flows, 26 pages."""
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, f"fts_api_flows_{year}.json.gz")
    if not refresh and os.path.exists(path) and time.time() - os.path.getmtime(path) < CACHE_TTL:
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            return json.load(fh)
    url: Optional[str] = f"{API}?year={int(year)}&limit=1000"
    flows: List[dict] = []
    expected, page = None, 0
    while url:
        data = _get(url)
        page += 1
        meta = data.get("meta") or {}
        expected = expected or meta.get("count")
        flows += (data.get("data") or {}).get("flows") or []
        if progress:
            progress(page, len(flows), expected)
        url = meta.get("nextLink")
    # A short read would silently undercount every total: stop rather than serve it.
    if expected and len(flows) != expected:
        raise ApiError(f"read {len(flows)} flows but the API reported {expected}. Run again with --refresh.")
    result = {"year": year, "fetched_utc": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "flows": flows}
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        json.dump(result, fh)
    return result


def counts(flow: dict) -> bool:
    return flow.get("status") in STATUSES and flow.get("boundary") in BOUNDARIES


def keyword_flows(flows: List[dict], keyword: str) -> List[dict]:
    k = keyword.strip().lower()
    return [f for f in flows if counts(f) and any((x or "").lower() == k for x in (f.get("keywords") or []))]


def names(flow: dict, side: str, kind: str) -> str:
    """The flow's objects of one type. Several (a shared flow) are joined, never split or
    counted twice, so the groups still add up to the total."""
    found = [o.get("name") for o in (flow.get(side) or []) if o.get("type") == kind and o.get("name")]
    return "; ".join(sorted(set(found))) or "Not specified"


def by_group(flows: List[dict], by: str) -> List[dict]:
    side, kind = GROUPS[by]
    tot: Dict[str, float] = defaultdict(float)
    n: Dict[str, int] = defaultdict(int)
    for f in flows:
        g = names(f, side, kind)
        tot[g] += float(f.get("amountUSD") or 0)
        n[g] += 1
    return [{by: g, "amount_usd": round(v, 2), "flows": n[g]} for g, v in sorted(tot.items(), key=lambda kv: -kv[1])]


def flow_rows(flows: List[dict]) -> List[dict]:
    return [{
        "flow_id": int(f["id"]) if str(f.get("id") or "").isdigit() else f.get("id"),  # else the CSV writer makes it 394650.0
        "date": (f.get("date") or "")[:10],
        "status": f.get("status"),
        "boundary": f.get("boundary"),
        "amount_usd": f.get("amountUSD"),
        "donor": names(f, "sourceObjects", "Organization"),
        "recipient": names(f, "destinationObjects", "Organization"),
        "country": names(f, "destinationObjects", "Location"),
        "sector": names(f, "destinationObjects", "GlobalCluster"),
        "plan": names(f, "destinationObjects", "Plan"),
        "description": f.get("description"),
    } for f in sorted(flows, key=lambda f: -float(f.get("amountUSD") or 0))]
