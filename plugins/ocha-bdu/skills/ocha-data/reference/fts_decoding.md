# Power BI DSR — how the response is encoded, and the traps

`querydata` returns results in **DSR**, Power BI's compressed row format. `decode_dsr` in
`ocha_fts_pbi.py` handles all of this; these notes are for when it needs changing.

## Shape

```
result.data.dsr.DS[0]
  ValueDicts   { "D0": ["United States of America, Government of (grouped)", ...] }
  PH           [ { "DM0": [ row, row, ... ] }, ... ]      one dict per data window
result.data.descriptor.Select   one entry per selected column: Kind, Value (slot), Name
```

Each **row** can carry:

| Key | Meaning |
|---|---|
| `S` | schema for this level — list of `{N: slot, T: type, DN: dict name}` |
| `C` | the values actually present on this row, in schema order |
| `R` | bitmask — bit i set means column i **repeats** the previous row's value (omitted from C) |
| `Ø` | bitmask — bit i set means column i is **null** (omitted from C) |
| `<slot>` | a value given directly by slot name rather than packed into C |
| `M` | nested child levels: `[{ "DM1": [rows] }]` |

For each column i in the schema: direct key if present → else repeat if `R` bit set → else
null if `Ø` bit set → else take the next value from `C`. If `C` runs out, the remaining
columns are null (trailing nulls are omitted, not flagged). If the column has a `DN` and
the value is an integer, it is an index into `ValueDicts[DN]`.

## The traps — each of these cost real time

1. **The schema is declared once per level, not per branch.** A level's `S` appears on the
   first row that has it; later rows at that level — including rows under a *different*
   parent — reuse it. Keep one schema registry for the whole shape, keyed by level name
   (`DM0`, `DM1`…). Resetting it per branch silently drops every value from the second
   branch onward.

2. **`A<n>` slots are not all junk.** The descriptor lists `Subtotal` slots (a measure's
   value on a grouping row) and `Max`/`Aggregates` slots (feeding in-cell data bars). Map
   subtotal slots to the measure's label; discard only `Max`/`Min`/`Aggregates`. Dropping
   every `A` slot deleted the real values from the pooled-funds table.

3. **Big numbers come back as strings** (`"4390416075.708869"`) to protect precision; small
   ones as ints. Convert with `to_number`, never `int()`.

4. **Headers labelled `.`** — the report hides some column headers, so the query's
   `NativeReferenceName` is `.` or `.1`. Fall back to an alias table, then to the model
   column name.

5. **Grouping rows carry no leaf values.** A matrix emits a header row per group and a
   grand-total row; keep only rows that have both a dimension and a measure.

6. **The row window.** Each visual's `Binding.DataReduction` caps rows (often 500). Widen it
   before replaying, or large tables truncate at their on-screen size.

7. **Gzip.** Both endpoints return gzip whether asked or not. `modelsAndExploration` is a
   **GET** — a POST returns 405.

## Finding the query for a visual

`modelsAndExploration → exploration.sections[] → visualContainers[]`. Each container's
`config` (a JSON string) holds the title and type; its `query` field (also a JSON string)
holds the resolved `Commands` to replay. A container with no `query` is a text box, image
or button.
