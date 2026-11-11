#!/usr/bin/env python3
"""
OCHA FTS Power BI reader — pull data straight out of a "publish to web" Power BI report.

Used for the 87 Million Lives campaign league table / donor-ranking animation. The
report is the FTS Visualization Tool (PreCheck), whose figures are the ones printed on
the tables at the UNGA81 side event, so it is the source of truth for anything shown on
the screens in that room.

Why this exists
---------------
The published FTS API (api.hpc.tools) cannot reproduce the dashboard's numbers. The
dashboard un-nests pooled-fund contributions back to the original donor and drops
regional-plan double counting, so a plain API pull puts Sweden ~190M light and reorders
the top ten. Reading the report itself is the only way to match what the room sees.

How it works
------------
A publish-to-web report exposes two anonymous endpoints, authenticated only by the
resource key in the share URL:

  GET  /public/reports/<resourceKey>/modelsAndExploration   -> full report definition
  POST /public/reports/querydata?synchronous=true           -> run a visual's query

Every visual in the report definition carries a `query` field holding the *resolved*
DAX-equivalent semantic query, with all report-, page- and visual-level filters already
merged in. We replay that query verbatim, so a visual read here returns exactly what the
same visual renders on screen. Nothing is reimplemented, so nothing can drift.

Responses come back as DSR (a compressed row format). `decode_dsr` unpacks it.

No third-party dependencies — Python 3.10+ standard library only, so this can run in a
GitHub Action without a requirements file.

Maintained by: OCHA Brand and Design Unit (BDU) — ochavisual@un.org
Focal point:   Javier Cueto (cuetoj@un.org)
"""

from __future__ import annotations

import gzip
import json
import os
import re
import time
import urllib.error
import urllib.request

# --------------------------------------------------------------------------------------
# Report identity
# --------------------------------------------------------------------------------------
# From the share URL: app.powerbi.com/view?r=<base64 of {"k":<key>,"t":<tenant>,"c":<n>}>
RESOURCE_KEY = "4a74e99b-5b0c-44be-b9e5-4bac0baea69f"

# The cluster host is NOT derivable from the share URL — it is whichever wabi-* region
# hosts the workspace. Read it off `performance.getEntriesByType('resource')` in the
# browser if the report is ever moved to another capacity; a wrong host returns 404.
CLUSTER = "https://wabi-north-europe-j-primary-api.analysis.windows.net"

# Page (section) names inside the report. There are 49; these are the ones we use.
PAGE_87_DAYS = "590cff7c154827063455"  # "OnePager (87 Days)" — the campaign one-pager
PAGE_DONORS = "5bedb7e690789f789ba8"  # "Org_Donors_V2"
PAGE_RECIPIENTS = "56d95b34860b7ad5cf15"  # " Org_Recipients_V2"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_CACHE = os.path.join(SCRIPT_DIR, ".model_cache.json")
MODEL_CACHE_TTL = 6 * 3600  # seconds; the report definition changes rarely

_HEADERS = {
    "X-PowerBI-ResourceKey": RESOURCE_KEY,
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip",
    "Origin": "https://app.powerbi.com",
    "Referer": "https://app.powerbi.com/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) OCHA-BDU/1.0",
}


class PowerBIError(RuntimeError):
    pass


# --------------------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------------------
def _request(url: str, payload: dict | None = None, timeout: int = 120) -> dict:
    """GET (payload=None) or POST JSON, transparently gunzipping the response."""
    data = json.dumps(payload).encode() if payload is not None else None
    headers = dict(_HEADERS)
    if data is not None:
        headers["Content-Type"] = "application/json;charset=UTF-8"
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            if resp.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
    except urllib.error.HTTPError as exc:  # surface the body, it explains the failure
        body = exc.read()
        try:
            body = gzip.decompress(body)
        except Exception:
            pass
        raise PowerBIError(f"HTTP {exc.code} from {url}: {body[:500]!r}") from exc
    return json.loads(raw.decode("utf-8"))


def fetch_model(force: bool = False) -> dict:
    """Report definition (~1.2 MB). Cached on disk, since it is large and near-static."""
    if not force and os.path.exists(MODEL_CACHE):
        if time.time() - os.path.getmtime(MODEL_CACHE) < MODEL_CACHE_TTL:
            with open(MODEL_CACHE) as fh:
                return json.load(fh)
    url = f"{CLUSTER}/public/reports/{RESOURCE_KEY}/modelsAndExploration?preferReadOnlySession=true"
    model = _request(url)
    slim = _slim_model(model)
    with open(MODEL_CACHE, "w") as fh:
        json.dump(slim, fh)
    return slim


def _slim_model(model: dict) -> dict:
    """Strip the response to what we actually query with.

    The full payload is ~13 MB — Power BI feature flags, theme data, and every visual's
    formatting for all 49 pages. We only ever read a visual's `config` and `query`, and
    only 9 pages carry a resolved `query` at all. Keeping the rest would sync 13 MB
    through Dropbox on every refresh for no benefit.
    """
    sections = []
    for section in model["exploration"]["sections"]:
        containers = section.get("visualContainers") or []
        kept = [
            {"config": c["config"], "query": c["query"]}
            for c in containers
            if c.get("query") and c.get("config")
        ]
        sections.append(
            {
                "name": section["name"],
                "displayName": section.get("displayName"),
                "visualCount": len(containers),  # the page's real size, before trimming
                "visualContainers": kept,
            }
        )
    return {
        "models": model["models"],
        "exploration": {
            "id": model["exploration"].get("id"),
            "reportId": model["exploration"]["reportId"],
            "sections": sections,
        },
    }


# --------------------------------------------------------------------------------------
# Report navigation
# --------------------------------------------------------------------------------------
def list_pages(model: dict) -> list[dict]:
    return [
        {
            "name": s["name"],
            "title": s.get("displayName"),
            "visuals": s.get("visualCount", len(s.get("visualContainers") or [])),
            "readable": len(s.get("visualContainers") or []),
        }
        for s in model["exploration"]["sections"]
    ]


def _visual_title(single_visual: dict) -> str:
    """Best-effort human title: the visual's title text, else its visual type."""
    try:
        expr = single_visual["vcObjects"]["title"][0]["properties"]["text"]["expr"]
        literal = expr["Literal"]["Value"]
        return literal.strip("'")
    except Exception:
        return single_visual.get("visualType", "visual")


def list_visuals(model: dict, page_name: str) -> list[dict]:
    """Every visual on a page that carries a runnable query."""
    section = next(s for s in model["exploration"]["sections"] if s["name"] == page_name)
    out = []
    for container in section["visualContainers"]:
        try:
            config = json.loads(container["config"])
        except Exception:
            continue
        single = config.get("singleVisual") or {}
        query = container.get("query")
        if not query:
            continue  # text boxes, images, shapes, navigation buttons
        out.append(
            {
                "id": config.get("name"),
                "title": _visual_title(single),
                "type": single.get("visualType"),
                "query": query,
            }
        )
    return out


def find_visual(model: dict, page_name: str, visual_id: str) -> dict:
    for visual in list_visuals(model, page_name):
        if visual["id"] == visual_id:
            return visual
    raise PowerBIError(f"visual {visual_id} not found on page {page_name}")


# --------------------------------------------------------------------------------------
# Querying
# --------------------------------------------------------------------------------------
def _widen_window(commands: dict, count: int) -> dict:
    """Raise the row cap the visual asks for, so tables aren't truncated at render size."""
    for command in commands.get("Commands", []):
        binding = (command.get("SemanticQueryDataShapeCommand") or {}).get("Binding") or {}
        reduction = binding.get("DataReduction") or {}
        for key in ("Primary", "Secondary"):
            window = (reduction.get(key) or {}).get("Window")
            if window is not None:
                window["Count"] = max(window.get("Count", 0), count)
    return commands


def run_visual(model: dict, page_name: str, visual_id: str, window: int = 5000) -> list[dict]:
    """Run one visual's own query and return its rows as dicts."""
    visual = find_visual(model, page_name, visual_id)
    commands = _widen_window(json.loads(visual["query"]), window)
    dataset = model["models"][0]

    payload = {
        "version": "1.0.0",
        "queries": [
            {
                "Query": commands,
                "CacheKey": json.dumps(commands),
                "QueryId": "",
                "ApplicationContext": {
                    "DatasetId": dataset["dbName"],
                    "Sources": [
                        {"ReportId": str(model["exploration"]["reportId"]), "VisualId": visual_id}
                    ],
                },
            }
        ],
        "cancelQueries": [],
        "modelId": dataset["id"],
    }

    response = _request(f"{CLUSTER}/public/reports/querydata?synchronous=true", payload)
    result = response["results"][0]
    if "result" not in result:
        raise PowerBIError(f"query failed for {visual_id}: {json.dumps(result)[:400]}")
    return decode_dsr(result["result"]["data"], commands)


# --------------------------------------------------------------------------------------
# DSR decoding
# --------------------------------------------------------------------------------------
# Power BI returns rows in a compressed shape:
#   C  — the values actually present on this row
#   R  — bitmask: bit i set means "column i repeats the previous row's value" (omitted from C)
#   Ø  — bitmask: bit i set means "column i is null" (omitted from C)
#   DN — the column's value dictionary; the value in C is then an index into it
# Groupings nest: an outer row carries child rows under M[..][DM<n>].
_NULL_KEY = "Ø"
_AGGREGATE_SLOT = re.compile(r"A\d+")


# Several dimension columns are labelled "." in the report (the header is hidden and the
# visual's own title carries the meaning). Give those a real name so the CSVs read.
_COLUMN_ALIASES = {
    "_calc_Org_Source_Parent_Display_VIZ": "Donor",
    "_calc_Org_Source_Display": "Donor (as reported)",
    "_calc_Org_Source_Parent_Display_Classif_Custom_DonorOrOther": "Donor category",
    "_calc_Org_Destination_Display_V3_VIZ": "Recipient",
    "_calc_Org_Dest_Display_Classif_Custom_DonorOrOther": "Recipient category",
    "_calc_Plan_Name": "Plan",
    "_calc_Plan_GroupType": "Plan type",
    "_calc_Plan_GroupType_2026": "Plan type",
    "_calc_GlobalCluster_VIZ_2026": "Global sector",
    "_calc_Location_Name_VIZ": "Location",
    "_calc_Meta_Status_HighLevel": "Status",
    "_calc_Country_STAR": "Country",
    "_calc_GlobalCluster_Classif_NotSpec_2026": "Sector category",
    "_calc_Plan_IsEstimate": "Plan is estimate",
    "_calc_Org_Source_OrgType_Display_VIZ": "Donor type",
}


def _humanise(internal: str) -> str:
    """Derive a readable header from a model column name, e.g. `v._calc_Foo_Bar` -> Foo Bar."""
    tail = internal.rsplit(".", 1)[-1].rstrip(")")  # Min(Table._calc_Foo) -> _calc_Foo
    tail = re.sub(r"^_+(calc|origdata)_", "", tail)
    tail = re.sub(r"_(VIZ|MEAS|V\d+)$", "", tail)
    return tail.replace("_", " ").strip() or internal


def _label_for(internal: str, labels: dict[str, str]) -> str:
    """Resolve a descriptor entry to a header: report label, then alias, then derived."""
    if internal in labels:
        return labels[internal]
    prop = internal.rsplit(".", 1)[-1].rstrip(")")
    return _COLUMN_ALIASES.get(prop) or _humanise(internal)


def _friendly_names(commands: dict) -> dict[str, str]:
    """Map the query's internal Select names to the labels shown in the report."""
    names = {}
    for command in commands.get("Commands", []):
        query = (command.get("SemanticQueryDataShapeCommand") or {}).get("Query") or {}
        for select in query.get("Select", []):
            internal = select.get("Name")
            if not internal:
                continue
            label = select.get("NativeReferenceName") or ""
            if re.fullmatch(r"\.\d*", label) or not label or label.startswith("_calc_"):
                # Placeholder header — fall back to an alias, then to the column name.
                prop = internal.rsplit(".", 1)[-1]
                label = _COLUMN_ALIASES.get(prop) or _humanise(internal)
            names[internal] = label
    return names


def _decode_level(
    dm_name: str,
    rows: list,
    value_dicts: dict,
    inherited: dict,
    schemas: dict[str, list],
) -> list[dict]:
    """Decode one grouping level of the matrix, recursing into nested levels.

    A level declares its schema once, on the first row that carries one, and every later
    row at that level reuses it — including rows under a *different* parent. So the
    schema registry is shared across the whole shape, keyed by level name (DM0, DM1...).
    Resetting it per branch silently drops values from the second branch onwards.
    """
    decoded: list[dict] = []
    previous: list = []

    for row in rows:
        if "S" in row:  # (re)declares the schema for this level from here on
            schemas[dm_name] = row["S"]
            previous = []
        schema = schemas.get(dm_name) or []

        if len(previous) != len(schema):
            previous = [None] * len(schema)
        values = list(previous)

        repeat_mask = row.get("R", 0)
        null_mask = row.get(_NULL_KEY, 0)
        packed = row.get("C", [])
        cursor = 0

        for index, column in enumerate(schema):
            key = column.get("N")
            if key in row:  # value given directly rather than packed into C
                value = row[key]
            elif repeat_mask & (1 << index):
                value = values[index]
            elif null_mask & (1 << index):
                value = None
            elif cursor < len(packed):
                value = packed[cursor]
                cursor += 1
            else:
                value = None  # trailing nulls are simply omitted

            # Resolve dictionary-encoded values (ints index into ValueDicts[DN])
            dict_name = column.get("DN")
            if dict_name and isinstance(value, int):
                table = value_dicts.get(dict_name) or []
                if 0 <= value < len(table):
                    value = table[value]
            values[index] = value

        previous = values
        record = dict(inherited)
        record.update({column["N"]: values[i] for i, column in enumerate(schema)})

        children: list[dict] = []
        for nested in row.get("M", []) or []:
            for child_name, child_rows in nested.items():
                children.extend(
                    _decode_level(child_name, child_rows, value_dicts, record, schemas)
                )

        # A grouping row exists to label its children; emit it only if it has none.
        decoded.extend(children if children else [record])

    return decoded


def _slot_labels(data: dict, commands: dict) -> tuple[dict[str, str], set[str], set[str]]:
    """Map DSR slots to headers.

    Returns (slot -> label, dimension slots, slots to discard).

    Measures appear under their own slot at leaf level and under a *subtotal* slot on
    grouping rows, so both map to the same header. `Max` aggregate slots only feed the
    in-cell data bars and carry no information, so they are discarded.
    """
    labels = _friendly_names(commands)
    slot_to_label: dict[str, str] = {}
    dimensions: set[str] = set()
    discard: set[str] = set()

    for entry in data.get("descriptor", {}).get("Select", []) or []:
        if not entry:
            continue
        slot = entry.get("Value")
        if not slot:
            continue
        label = _label_for(entry.get("Name") or slot, labels)
        slot_to_label[slot] = label
        if entry.get("Kind") == 1:
            dimensions.add(slot)
        for subtotal_slot in entry.get("Subtotal") or []:
            slot_to_label[subtotal_slot] = label
        for aggregate in entry.get("Aggregates") or []:
            discard.update(aggregate.get("Ids") or [])
        discard.update(entry.get("Max") or [])
        discard.update(entry.get("Min") or [])

    discard -= set(dimensions)
    return slot_to_label, dimensions, discard


def decode_dsr(data: dict, commands: dict) -> list[dict]:
    """Turn a querydata response into a list of dicts keyed by the report's own labels."""
    shapes = data.get("dsr", {}).get("DS") or []
    if not shapes:
        return []
    shape = shapes[0]
    value_dicts = shape.get("ValueDicts") or {}

    schemas: dict[str, list] = {}
    raw_rows: list[dict] = []
    for window in shape.get("PH", []):
        for level_name, level_rows in window.items():
            raw_rows.extend(_decode_level(level_name, level_rows, value_dicts, {}, schemas))

    slot_to_label, dimension_slots, discard = _slot_labels(data, commands)
    slot_order = {slot: i for i, slot in enumerate(slot_to_label)}

    decoded: list[dict] = []
    for row in raw_rows:
        record: dict[str, object] = {}
        used: dict[str, str] = {}
        has_dimension = has_measure = False

        ordered = sorted(
            row.items(),
            key=lambda kv: (kv[0] not in dimension_slots, slot_order.get(kv[0], 99)),
        )
        for slot, value in ordered:
            if slot in discard:
                continue
            label = slot_to_label.get(slot, slot)
            key = label.lower()
            if key in used and used[key] in record and record[used[key]] is not None:
                # A real collision between two different selects sharing a header.
                label = f"{label} ({slot})"
            else:
                label = used.get(key, label)
            used.setdefault(key, label)

            if value is not None:
                if slot in dimension_slots:
                    has_dimension = True
                else:
                    has_measure = True
            if record.get(label) is None:
                record[label] = value

        # Drop the shape's grand-total row (no dimensions) and empty grouping headers.
        # Cards and gauges have no dimensions at all, so there is nothing to drop.
        if has_measure and (has_dimension or not dimension_slots):
            decoded.append(record)

    # Grouping rows omit the columns of the levels below them, so rows arrive ragged and
    # in varying key order. Give every row the same columns, dimensions first.
    columns: list[str] = []
    for slot in sorted(
        slot_to_label,
        key=lambda s: (s not in dimension_slots, slot_order.get(s, 99)),
    ):
        label = slot_to_label[slot]
        if slot in discard or label in columns:
            continue
        if any(label in row for row in decoded):
            columns.append(label)
    for row in decoded:  # keep any label the descriptor did not account for
        for label in row:
            if label not in columns:
                columns.append(label)

    return [{label: row.get(label) for label in columns} for row in decoded]


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", (text or "").strip().lower())
    return re.sub(r"[\s_-]+", "_", text)[:60] or "visual"


def to_number(value):
    """Power BI sends large numbers as strings to protect precision."""
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return value
    return value


if __name__ == "__main__":
    import sys

    model = fetch_model()
    if len(sys.argv) > 1 and sys.argv[1] == "pages":
        for page in list_pages(model):
            print(f'{page["name"]}  {page["visuals"]:>3} visuals  {page["title"]}')
    else:
        page = sys.argv[1] if len(sys.argv) > 1 else PAGE_87_DAYS
        for visual in list_visuals(model, page):
            print(f'{visual["id"]}  {visual["type"]:<18} {visual["title"]}')
