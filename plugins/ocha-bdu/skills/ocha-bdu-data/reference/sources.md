# Pooled-fund sources — endpoints, fields and traps

Verified live on **11 November 2026**, by reading each hub’s own chart scripts. All public, no keys.
When an endpoint moves: open the hub in a browser, open the network tab, reload, and look for the
`.csv` / `.json` requests. Update `scripts/pooled.py` and this page.

## CERF data hub — cerf.data.unocha.org

| What | URL |
|---|---|
| **Every CERF project, all years** (~18 MB JSON, ~8,700 rows) | `https://cerfgms-webapi.unocha.org/v1/project/All.json` |
| Agencies | `https://cerfgms-webapi.unocha.org/v1/agency/All.json` |
| Countries | `https://cerfgms-webapi.unocha.org/v1/country/All.json` |
| Applications (one row per allocation, with emergency type) | `…/download/loadCERFApplication_v2/cerf_application_v2.csv` |
| Allocation summary by organization (stale for 2026 in Nov 2026) | `…/download/loadAllocations/cerf_allocationSummary_byorg.csv` |
| Contributions overview | `https://cbpfgms.github.io/pfbi-data/cerf_sample_data/CERF_ContributionTotal.csv` |
| Year summary card | `…/download/cerf/CERFSummary-<year>.json` |

`project/All.json` fields used: `year`, `countryName`, `countryCode` (ISO3), `applicationCode`
(the allocation, e.g. `CERF-COD-26-RR-1565`), `projectCode`, `agencyShortName`,
`emergencyTypeName` (“Ebola”, “Cholera”, “Drought”…), `windowFullName` (Rapid Response /
Underfunded Emergencies), `totalAmountApproved`, `projectsectors.projectsectors[]`
(`sectorName`, `sectorAmount`), `allocationStatus`, `dateUSGSignature` (approval date; **missing on
some rows**). Projects “Under Review” appear with agency “To be determined”.

`cerf_application_v2.csv`: `CountryID` is the **MstCountry id** (pfdata’s), not CERF’s own
`countryID` in `project/All.json`, which is MstCountry’s `CERFId`. Two id systems; resolve by ISO3.

## CBPF data hub — cbpf.data.unocha.org

OData v3 at `https://cbpfapi.unocha.org/vo2/odata` (`/vo3/odata` serves the same entity sets).
Add `$format=json`. `$filter` works and is essential: unfiltered `ProjectSummary` takes minutes.

| Entity | Use |
|---|---|
| `Poolfund` | every fund: `Id`, `PoolfundName` (“DRC”, “Kenya (ESAHF)”), `CountryCode` (**ISO2**), `ParentPooledFundId` |
| `AllocationTypes` | allocation rounds: `AllocationTitle`, `AllocationSource`, `TotalApprovedBudget`, `TotalUnderApprovalBudget`, `AllocationHCLastProjectApprovalDate`, `AllocationTypeId`, `PooledFundId`, **`FundTypeId` 1 = CBPF, 2 = CERF** |
| `ProjectSummary` | project level: one row **per project × cluster × location**. `Budget` is the project total (dedupe by `ChfProjectCode`); `BudgetByCluster` per (project, cluster). `AllocationTypeId`, `AllocationType` (round title), `OrganizationName`, `OrganizationType`, `ApprovedDate` |
| `LastModified` | the data date shown by both CBPF and pfdata hubs |
| `ContributionTotal`, `DonorMaster`, `CBPFSummary`, `ProjectSummaryV2`, `AllocationFlowByOrgType`… | not used yet |

Example: `ProjectSummary?$format=json&$filter=AllocationYear eq 2026 and (PooledFundId eq 24 or PooledFundId eq 511)`
(~40 s, ~10 MB for four funds).

Titles are in the fund’s working language: DRC is mostly French (“MVE” = maladie à virus Ebola).

## Pooled Funds Data Hub — pfdata.unocha.org (CERF + CBPF)

Downloads at `https://pfbi-webjob-contribution-prod-g7b3h4b9ftfahnbk.eastus2-01.azurewebsites.net/download/`:

| File | Columns |
|---|---|
| `loadAllocations/allocationSummarybyapproveddate.csv` | `ApprovedDate` (MM-YYYY), `PooledFundName` (= **MstCountry id**), `FundType` (**1 = CERF, 2 = CBPF**), `Budget` |
| `loadAllocations/sectorSummarybyOrg.csv` | year, fund, partner code, org type, cluster, allocation source, budget |
| `loadContributionByCERFCBPFAll/contributionbycerfcbpfAll.csv` | `FiscalYear`, `PledgePaidDate`, `DonorId`, `PooledFundId` (MstCountry id; **109 = CERF**), `PledgeAmt`, `PaidAmt` — the “All” file includes closed funds |
| `loadAllocations/allocationSummarySankey.csv`, `loadContribution/contributionSummarySankey.csv` | the Sankey charts |
| `loadLocations/fund_adm1.csv` | budgets by admin-1 location |

Lookups at `https://cbpfgms.github.io/pfbi-data/mst/`: `MstCountry`, `MstFund`, `MstFundv2`,
`MstDonor`, `MstCluster`, `MstClusterCBPFCERF`, `MstOrganization`, `MstPartner`, `MstAllocation`,
`MstEmergencyType`, `MstEmergencyGroup`, `MstRegion` (`.json`).

## The traps

1. **FundType is flipped between sources.** pfdata: 1 = CERF, 2 = CBPF. cbpfapi `AllocationTypes`:
   1 = CBPF, 2 = CERF.
2. **Three country id systems.** MstCountry `id` (pfdata files, CERF applications), MstCountry
   `CERFId` (CERF API `countryID`), MstCountry `CBPFId` = cbpfapi `PooledFundId`. Resolve by ISO3
   (CERF API) and ISO2 (cbpfapi `Poolfund.CountryCode`).
3. **Regional windows.** MstCountry lists “Kenya” (CBPFId 57, closed) and “Kenya (ESAHF)”
   (CBPFId 511) separately, but `allocationSummarybyapproveddate.csv` files Kenya (ESAHF)’s
   October 2026 allocation under plain “Kenya” (id 52). Only the CBPF hub names the window.
4. **pfdata month = latest project approval** in the round, not the HC’s planned date.
5. **Some CERF projects have no `dateUSGSignature`** — code must use `.get`.

## Worked example (11 Nov 2026)

`check --country Kenya --amount 2,287,000 --year 2026` → Kenya (ESAHF), allocation “[US AWARD TRANCH 2]
Ebola EVD Preparedness”, 3 projects, $2,287,327.51, latest project approved 15 October 2026; the
Pooled Funds hub files the same amount as CBPF, “Kenya”, October 2026. Match: yes, rounded.
