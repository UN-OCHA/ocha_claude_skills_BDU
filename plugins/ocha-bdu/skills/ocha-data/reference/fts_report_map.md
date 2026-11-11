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
