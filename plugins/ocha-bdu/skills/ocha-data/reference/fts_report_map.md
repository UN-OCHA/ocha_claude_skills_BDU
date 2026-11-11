# FTS dashboard — report map

Verified live on **5 October 2026** (tables and cards as first mapped on 11 September). Visual ids
change if the FTS team deletes and re-adds a visual, so re-verify with `fts.py visuals` before
trusting an id from here. **They did change on 2–3 October 2026:** the six GHO headline cards below
were removed in a report rebuild, which stopped the GHO tracker's daily run for three days. Their
figures are now fields of one custom visual (see the headline section).

## Report identity

| | |
|---|---|
| Resource key | `4a74e99b-5b0c-44be-b9e5-4bac0baea69f` (from the share link's base64 `k`) |
| Tenant | `0f9e35db-544f-4f60-bdcc-5ea416e6dc70` |
| Cluster | `https://wabi-north-europe-j-primary-api.analysis.windows.net` |
| Report | "OCHA FTS - Visualization Tool - Pilot - PROD.pbix", 49 pages |

## The campaign one-pager — `590cff7c154827063455` "OnePager (87 Days)"

The page the 87 Million Lives figures come from. Filters already applied: year 2026, GHO
plans only, prioritized, outgoing flows excluded.

### Headline figures (cards and gauges)

**The six GHO figures are one row of one custom (Deneb) visual, `8f70bf0c55723720a799`, read by field
name** (since 2–3 Oct 2026; before that each was its own card):

| Field | Figure (4 Oct 2026) |
|---|---|
| `FINAL USD Required Prioritized ByGlobalCluster MEAS` | Prioritized requirements, $24.98bn |
| `USD InPlan Prioritized` | Prioritized funding **received**, $13.74bn |
| `FINAL Coverage Prioritized ByGlobalCluster MEAS` | Prioritized coverage (0–1), 0.550 |
| `FINAL USD Required ByGlobalCluster MEAS` | Total GHO requirements, $35.11bn |
| `FINAL USD inPLan` | Total GHO funding, $14.68bn |
| `FINAL Coverage ByGlobalCluster MEAS` | Total GHO coverage (0–1), 0.418 |

The same visual also holds two gap measures (`…Required GAP BetweenPrioAndNonPrio`, `…Required
Prioritized ByGlobalCluster GAP`); they are not used. **Trap:** the card `c3ecfe6256e41bba66e6`,
titled “Prioritized Funding (USD)”, now reads *received + pledges + announcements* ($14.40bn) — never
use it as “funding received”; the 87M rule is that pledges are never added to funding.

Cards that still exist, by visual id:

| Visual id | Figure |
|---|---|
| `2bd0f1079166b47156bc` | Private sector contributions (USD) |
| `8eb1d994568b5b556490` | Pooled funds (share, 0–1) |
| `0faa810408b052e06300` | Direct contributions to national and local organizations (share, 0–1) |
| `c299af827dcd82be601b` | **Data date** ("FTS API checksum date") |
| `c3ecfe6256e41bba66e6` | Prioritized funding (second card, same figure) |

### Tables

| Visual id | Content | Columns |
|---|---|---|
| `756002108d716d0d1335` | By donor / source organization | Donor category, Donor, Donor (as reported), GHO Funding (Prioritized), Share of Total Funding, Pledges, Announcements |
| `4580dbf51a453ccb2288` | By recipient organization | Recipient category, Recipient, funding, share |
| `c056db16e838338ec71e` | By GHO plan | Plan type, Plan name, prioritized required, funding, coverage |
| `62a920851c11809a4084` | By global sector | Sector category, Global sector, required, funding, coverage |
| `375875f4373661800d91` | Funding status | Funding / Pledges / Announcements totals |
| `9ffa7a920004b1206137` | Multi-donor mechanisms | Pooled funds, UN agencies (already counted in the total) |
| `80069514600c63e36171` | Prioritized total potential (donut) | funding + pledges + announcements |
| `a749f841059885de33cb` | By contribution type (donut) | |

## Other pages worth knowing

`fts.py pages` lists all 49. The ones with obvious reuse:

| Page | Name |
|---|---|
| `5bedb7e690789f789ba8` | Org_Donors_V2 — donor detail |
| `56d95b34860b7ad5cf15` | Org_Recipients_V2 — recipient detail |
| `6ca75c869b08e812c5bb` | OnePager (Plans-Prioritized) V2 |
| `b5b23620ad140ab13253` | 87 Days_Ratios |
| `ed10ddb93d24bdbbadf7` | OnePager_WithTotals (87 Days) |

Several pages are dev copies or crisis-specific one-pagers (Ebola, Venezuela, Iran). Check
a page's title before relying on it.

## Plan names

The plans table returns plan names in full and in the plan's own language — "République
Démocratique du Congo Besoins Humanitaires et Plan de Réponse 2026". Shorten for display;
never translate or rename a plan without checking.

## Named tables (`fts.py tables`) — mapped 11 November 2026

Only 7 of the 49 pages are published and carry stored queries: OnePager (87 Days), OnePager
(Horiz) V2, OnePager (Plans) V2 `9fc1ea690b6b64c05d51`, Org_Donors_V2 `5bedb7e690789f789ba8`,
Org_Recipients_V2 `56d95b34860b7ad5cf15`, Weekly `ReportSection353c4b8293ee828c3e33`, Home. The
other 42 (country one-pagers such as Ebola, DataTables, ByGlobClus…) have no query and cannot be
read. All tables below are the default view: `Item = 2026`, global analysis, pledges, outgoing
and multi-year flows excluded.

| Name | Page | Visual |
|---|---|---|
| plans | Plans V2 | `6bed06e2ab84e322e4ab` By GHO Plans |
| plan-groups | Weekly | `b0a4c298653e5af791f7` 2026 GHO Funding Progress |
| years | Weekly | `a1521b8314273109b300` Funding Overview |
| gho-sectors | Plans V2 | `a34334a12674240b4562` By Global Sectors |
| gho-countries | Plans V2 | `738054d9e4be236263d6` By Locations |
| gho-donors | Plans V2 | `d6056b9a407734ebd7a0` By Donors / Source Organizations |
| gho-recipients | Plans V2 | `4addea0cb2d50c9b44e9` By Recipient Organizations |
| sectors | Org_Donors_V2 | `2424b9b1fb04e1d50ec1` By Global Clusters |
| countries | Org_Donors_V2 | `08e5cbc1c6d2484c0f9c` By Locations |
| donors | Org_Donors_V2 | `df0c7d1c3857fe6d533a` By Source Organizations |
| recipients | Org_Recipients_V2 | `0c0b656c878e836bbe45` By Recipient Organizations |
| donor-types | Org_Recipients_V2 | `53027e57bba09c3a177f` By Donor/Source Type |
| recipient-types | Org_Donors_V2 | `0cf191c67290a24d6d26` By Recipient Type |
| earmarking | Org_Donors_V2 | `10b8addaa6002310360d` Earmarking |

Weekly also has 2025 and 2024 GHO Funding Progress tables (`4108253c3e6e9624b3b4`,
`90e9959a469805b0430e`); several other Weekly tables return no rows in the default view.

