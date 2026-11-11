---
name: ocha-data
description: OCHA humanitarian funding data from its official public sources — the CERF data hub (cerf.data.unocha.org), the CBPF data hub (cbpf.data.unocha.org), the Pooled Funds Data Hub (pfdata.unocha.org) and the FTS dashboard. Use to check a figure someone supplied (“Kenya, humanitarian fund, $2,287,000”: which fund, which allocation, which date, does it match?), to find and contrast figures across the three fund hubs, and to pull tables as CSV for charts and infographics — allocations by country, fund, allocation round, sector or cluster, agency and partner; contributions by donor; GHO funding, coverage, requirements and donor rankings from FTS. Trigger on CERF, CBPF, pooled fund(s), country-based pooled fund, humanitarian fund, regional fund, ESAHF, RhPF, allocation, “check this figure”, “verify these numbers”, “where does this number come from”, funding infographic, FTS, “pull the FTS data”, funding figures, top donors, donor ranking, coverage, prioritized requirements. Do NOT use the public FTS API (api.hpc.tools) for published FTS figures — it does not match the dashboard.
---

# OCHA funding data

Four public sources, no keys, standard-library Python. Two scripts in this skill’s `scripts/`
folder:

| Script | Reads |
|---|---|
| `ocha_data.py` | the three **pooled-fund** hubs: CERF, CBPF, and the combined Pooled Funds hub |
| `fts.py` | the **FTS** dashboard (GHO funding, requirements, coverage, donors) |

Run them from the project folder, so the CSVs land beside the work (`./ocha_data/`, `./fts_data/`;
`--out` to change). Downloads are cached in the output folder for six hours; `--refresh` ignores
the cache. In the shared plugin, the scripts sit in this skill’s `scripts/` folder; on Javi’s Mac
that is `~/.claude/skills/ocha-data/scripts/`.

## The two pooled-fund sites — why two similar names

They are closely related, and share their data:

- **CBPF data hub** (cbpf.data.unocha.org) — the older site, **CBPFs only**. OCHA’s donor
  visibility team goes here first for **donor data on the CBPFs** (who gave what to which fund).
  It runs on the CBPF API, which also holds the project-level detail this skill reads.
- **Pooled Funds Data Hub** (pfdata.unocha.org) — the newer **umbrella portal for CBPFs and CERF
  together**, linked from the CBPF hub. Use it to see both funds side by side, and for the
  operational level: by country, month, sector, partner type and location.
- **CERF data hub** (cerf.data.unocha.org) is CERF’s own site, built on the same files and lookups.

Both CBPF and pfdata show the same “last updated” stamp, from the same back end, so their figures
agree. They differ in grain: the pfdata download files are summaries, filed by country, so they
can’t say which fund window (Kenya vs Kenya (ESAHF)) or which emergency a figure belongs to. For
that, use the CBPF hub (projects and allocation rounds) or the CERF hub (projects).

Donor contributions to the CBPFs agree between the two sites (checked 2025 and 2026, Nov 2026: totals
within a few hundred dollars, from rounding). Only labels differ: “United States” on the CBPF hub is
“United States of America” on pfdata, the two sites swap the labels “PRIVATE SECTOR” and “Private
Contributions”, and a donor missing from pfdata’s donor list shows as “donor id N”. For donor
figures on the CBPFs, quote the CBPF hub’s names.

## Which source for what

| Need | Source | Command |
|---|---|---|
| Is this pooled-fund figure right? | all three hubs at once | `ocha_data.py check` |
| CERF by country, agency, sector, emergency, allocation | CERF data hub (project level) | `ocha_data.py cerf` |
| A CBPF by allocation round, partner, partner type, cluster | CBPF data hub (project level) | `ocha_data.py cbpf` |
| CERF and CBPF side by side, per country or month | Pooled Funds hub (summary files) | `ocha_data.py allocations` |
| Who gave to CERF or a CBPF | Pooled Funds hub | `ocha_data.py contributions` |
| GHO funding, coverage, requirements, top donors | FTS dashboard | `fts.py` |

## Check a figure

```bash
python3 …/ocha_data.py check --country Kenya --amount 2,287,000 --year 2026
python3 …/ocha_data.py check --country DRC --amount 59,050,000 --year 2026 --fund cerf --keyword ebola
```

It looks at every level a figure could come from — project, allocation (CERF application or CBPF
allocation round), all of a country’s projects matching the keyword, the year total, and the
Pooled Funds hub’s country-month rows — and answers **MATCH: yes**, with the fund, level, date and
reference of each hit, or **MATCH: no** with the closest figures. A figure written as 2,287,000 is
treated as rounded to the thousand (±500); a round 6,000,000 allows ±500,000, and the answer says
“rounded” with the exact source amount. Override with `--tolerance`.

`--keyword` is a regular expression on CERF’s emergency type and on project and allocation titles
(`'ebola|evd|mve'` catches the French CBPF titles too). Always pass it when the figure is about one
emergency: without it, an allocation of the same size for a different crisis can match.

Report a check like this: *“Kenya Humanitarian Fund $2,287,000 = Kenya (ESAHF), the CBPF window of
the East and Southern Africa Humanitarian Fund, allocation ‘Ebola EVD Preparedness’, $2,287,327.51,
approved October 2026 (CBPF data hub, data as of 11 Nov 2026). Match: yes, rounded.”*

**Never change the figures in someone’s sheet.** A mismatch is a finding: say what the source
says, and let Javi decide.

## Pull tables

```bash
python3 …/ocha_data.py cerf --year 2026 --emergency Ebola --by agency     # or country, sector, application, window, project
python3 …/ocha_data.py cbpf --year 2026 --country Uganda --by allocation  # or partner, partner_type, cluster, fund, project
python3 …/ocha_data.py cbpf --year 2026 --country DRC --keyword 'ebola|evd|mve' --by partner
python3 …/ocha_data.py allocations --year 2026 --by country               # CERF + CBPF per country (or month, fund_type)
python3 …/ocha_data.py contributions --year 2026 --fund cerf --by donor   # paid and pledged
python3 …/ocha_data.py funds Kenya                                        # which funds exist for a country
python3 …/ocha_data.py status                                             # the hubs’ data date
```

Every CSV row names its fund. `cbpf` without `--country` or `--fund-id` reads every fund for the
year and takes minutes; give a country.

## What the figures mean — get these right

- **Which fund.** A country can have several. Kenya’s own CBPF is closed; Kenya’s money now comes
  through **“Kenya (ESAHF)”**, a window of the regional East and Southern Africa Humanitarian Fund.
  The same goes for Uganda (ESAHF) and the RhPF windows (Chad, Haiti, Colombia…). Always say which
  fund a figure came from, by the name the source uses. “Humanitarian Fund” in a sheet usually
  means the CBPF window for that country.
- **The Pooled Funds hub cannot tell you which fund.** Its summary files file a regional window’s
  money under the plain country (Kenya, not Kenya (ESAHF)), and carry no emergency type or title.
  Use it to contrast CERF and CBPF per country and month; use the CERF and CBPF hubs for anything
  about one fund, allocation or emergency.
- **Dates.** CERF: the USG’s approval date per project; an application’s date is its last project.
  CBPF: each project’s approval date; an allocation round runs over weeks, so its CBPF hub date is
  the latest project, and the Pooled Funds hub files it in that month. The HC’s planned date in
  the allocation list can be months earlier.
- **Approved, not disbursed.** All hub amounts are approved budgets. CBPF projects still under
  approval are not in them.
- **CERF sectors are CERF’s own** (Health, WASH, Common Services, Food Assistance…). A sheet that
  says “enabling services” or “Logistics (Health)” used another breakdown; compare totals, not labels.
- **CERF agency names** are short names (WHO, UNICEF, UNDSS). CBPF partners are full names.

## FTS — the global funding dashboard

```bash
python3 …/fts.py headline              # requirements, funding, coverage, pledges, data date -> headline.json
python3 …/fts.py donors --top 15       # donor table -> donors.csv, ranking -> ranking.csv
python3 …/fts.py page                  # every visual on the one-pager, one CSV each
python3 …/fts.py visual PAGE ID        # one visual
python3 …/fts.py pages | visuals [PAGE]
python3 …/fts.py tables                # the named tables below
python3 …/fts.py table plans           # one table -> fts_plans.csv; `table all` for every one
```

| Table | What it holds |
|---|---|
| `plans` | every GHO plan: funding, requirements, coverage, plan type |
| `plan-groups` | GHO totals by plan group (HRPs, flash appeals, RRPs, other) |
| `years` | inside, outside and total humanitarian funding, requirements, coverage, 2024–2026 |
| `gho-sectors`, `gho-countries` | GHO funding, requirements and coverage by global sector / country |
| `gho-donors`, `gho-recipients` | GHO funding by donor / recipient organization |
| `sectors`, `countries` | all humanitarian funding (inside and outside GHO) by sector / country |
| `donors`, `recipients` | all humanitarian funding by donor / recipient organization |
| `donor-types`, `recipient-types` | by type: governments, pooled funds… / UN, NGOs… |
| `earmarking` | earmarked vs unearmarked share |

**What “the whole dashboard” covers.** Only 7 of the report’s 49 pages are published; the
rest are hidden drafts (a country one-pager for Ebola, Venezuela, Nepal…) that cannot be read.
Every table shows the dashboard’s **default view: 2026, global, pledges and outgoing flows
excluded**. Other years or one country need the dashboard’s filters, which these commands don’t
set. The tables use different measures, so their totals differ (GHO funding is $15.7bn in
`plan-groups` and $14.1bn in `gho-donors`, Nov 2026): quote a total from the same table as its
rows, and state the data date.

The **OCHA FTS Visualization Tool (PreCheck)** is a public Power BI report and the source of truth
for OCHA’s published funding figures:
https://app.powerbi.com/view?r=eyJrIjoiNGE3NGU5OWItNWIwYy00NGJlLWI5ZTUtNGJhYzBiYWVhNjlmIiwidCI6IjBmOWUzNWRiLTU0NGYtNGY2MC1iZGNjLTVlYTQxNmU2ZGM3MCIsImMiOjh9
`fts.py` replays each visual’s own stored query, so every figure matches the dashboard exactly.
**Always state the data date** with any figure; `headline` returns it.

**Why not the FTS API.** The public API (`api.hpc.tools`) **does not reproduce the dashboard’s
numbers**. The dashboard attributes pooled-fund money back to the original donor and strips
regional-plan double counting. A plain API pull put Sweden ~$190M light and reordered the top ten;
in September 2026 the old API tracker said $23.42bn / $12.27bn / 52.4% where the dashboard said
$24.94bn / $13.36bn / 53.5%. If a figure must match what OCHA publishes, it comes from `fts.py`.

FTS figures and pooled-fund hub figures are different things: FTS tracks all humanitarian funding
by plan and donor; the hubs track what CERF and the CBPFs allocated. Don’t add one to the other.

- **Prioritized vs total.** The 87 Million Lives campaign uses the **prioritized** figures (the
  hyper-prioritized GHO). “Total GHO” is the full appeal. Never mix them in one frame.
- **$23 billion vs $24.94 billion.** $23bn is the GHO 2026 prioritized requirement **at launch**
  (Dec 2025), the figure the USG uses publicly. The dashboard shows it **as revised since**. Both
  are official; coverage and shortfall depend on which is the denominator, so never pair $23bn with
  the dashboard’s coverage %. Ask which is wanted.
- **Funding excludes pledges and announcements.** Neither is money received; the dashboard ranks
  on funding only. Show them, if at all, as a separate label.
- **Donor categories.** A donor *ranking* means the Donor category (governments and institutions)
  only, not Private Sector, Multilateral Banks or Other.
- **Names.** For anything public use UN short names; the European Commission keeps its own name.
- **“People prioritized”** is the GHO’s own term for the 87 million. Avoid “assistance”.

## When it breaks

- **Pooled-fund hubs:** `reference/sources.md` lists every endpoint, field and trap, and how to
  find a moved endpoint (open the hub, watch the network tab). A `404` or `not JSON` names the URL.
- **FTS:** `reference/fts_report_map.md` (which visual holds what) and `reference/fts_decoding.md`
  (the Power BI format). Cluster host moved → 404; visual ids changed → “visual not found”, list
  them with `fts.py visuals`; a figure empty → check the data date first, and if the dashboard
  stopped refreshing, that is the finding.

## Where else the FTS client lives

Two projects carry their own copy of the FTS client and must stay self-contained. This skill’s copy
is canonical; if you fix the client, update all three.

- `~/OCHA DMU Dropbox/<your-name>/Projects/2026/UNGA81/UNGA81_87M_Event/tooling/data_pipeline/`
  — the 87 Million Lives figures workbook.
- `UN-OCHA/gho-prioritized-tracker-BDU` (GitHub) — the daily GitHub Action that publishes the
  prioritized figures as CSVs for Datawrapper.

<!-- bdu-suggest-change:start -->
**Suggesting a change to this skill.** If the person corrects you or states a rule that would apply to other jobs too, or you find this skill is wrong or missing something, say so once, at the end of your reply. Don’t do this for changes that only concern the current job, and don’t edit the skill yourself, because the next update would overwrite it. Leave out anything confidential from the job. Say:

> This could be worth adding to the OCHA BDU skills. If you agree, copy this message and send it to Javi:
> **Skill:** ocha-data
> **Proposed rule:** [the rule, in one or two sentences]
> **Why:** [what happened, with one example]
<!-- bdu-suggest-change:end -->
