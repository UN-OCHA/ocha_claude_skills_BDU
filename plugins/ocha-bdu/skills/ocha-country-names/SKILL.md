---
name: ocha-country-names
description: >
  The UN source of truth for country names and codes in OCHA work: official short and formal names in
  the six UN languages (UNTERM), ISO3/ISO2/M49 codes and UN regions (UN M49), and OCHA’s own usage on
  top. Use whenever a country is named or coded in anything OCHA makes — text, captions, chart labels,
  map labels, file names, data joins — or the user asks “what’s the official name of…”, “Turkey or
  Türkiye?”, “ISO code for…”, “which region is…”, “is X a Member State?”, “country name in French /
  Arabic”, “country list”, “list of countries”, “M49”, “UNTERM”, “ISO3”. Disputed areas and how to show
  them on maps stay with `ocha-mapping`.
---

# OCHA country names and codes

One table, `data/country_names.csv`, built from the UN’s own sources. **Look names and codes up here;
never write them from memory.** A wrong or outdated name (“Turkey”, “Ivory Coast”, “Swaziland”) is a
visible error in a UN product.

## 1. Sources of truth (agreed with Paolo, October 2026)

| What | Source | Covers |
|---|---|---|
| **Names** | **UNTERM**, the UN Secretariat’s terminology database (unterm.un.org → Countries) | Official short and formal names of the 193 Member States, the 2 Observer States (Holy See, State of Palestine) and 2 members of specialized agencies (Cook Islands, Niue), in Arabic, Chinese, English, French, Russian and Spanish |
| **Codes and regions** | **UN M49**, UN Statistics Division (unstats.un.org/unsd/methodology/m49) | ISO3, ISO2 and M49 codes, UN regions and subregions, LDC / LLDC / SIDS, and 51 other areas that aren’t in UNTERM’s list (territories such as Western Sahara, Puerto Rico, Greenland) |
| **OCHA usage** | OCHA’s own decisions (§3) | Where OCHA comms deliberately differ from the official name |

If they disagree: UNTERM for the name, M49 for the code and region, §3 when OCHA has decided otherwise.

## 2. Using the table

`data/country_names.csv`, one row per country or area. Columns: `iso3`, `iso2`, `m49`, `un_status`,
`name_en_short`, `name_en_formal`, short and formal names in `fr`, `es`, `ar`, `zh`, `ru`, `name_m49`,
`region`, `subregion`, `intermediate_region`, `ldc`, `lldc`, `sids`. `data/sources.json` says when it
was built.

- **Short name** in almost everything: text, labels, charts, maps, social. **Formal name** only where a
  formal title is needed (letters, official documents): “the Republic of the Sudan”.
- **“(the)” in UNTERM** means the short name takes “the” in running text. Drop the brackets: in a label or
  title write `Sudan`, `Philippines`; in a sentence write “in the Sudan”, “the Philippines has…”.
- **Other brackets are part of the name:** `Bolivia (Plurinational State of)`, `Venezuela (Bolivarian
  Republic of)`, `Netherlands (Kingdom of the)`. Write them as they are.
- **Keep every accent and character:** Türkiye, Côte d’Ivoire, Curaçao, Réunion.
- **Non-English names** come from the matching column, never from translating the English one.
- **Codes:** match datasets on `iso3`, never on names (names vary by source). In file names use the ISO3
  code in lower case (`ocha-files-and-folders`).
- **Status matters in wording:** only rows with `un_status` “Member State” are Member States. Don’t call
  an Observer State or another area a “country” or “Member State” in a way that implies a status it
  doesn’t have; “countries and territories” or “countries and areas” covers a mixed list.
- **Listing several countries in running text:** alphabetical order (OCHA style guide).
- **Not in the table** (for example Kosovo, which M49 doesn’t list): don’t invent a name or code. Disputed
  areas follow the territories guidance in `ocha-mapping`; ask if unsure.

## 3. OCHA usage on top of the official name

Only what OCHA has actually decided. Anything not listed here: use the UNTERM short name, and ask before
using a shorter form in a formal product.

| Official (UNTERM) | OCHA usage | Source |
|---|---|---|
| State of Palestine | **Occupied Palestinian Territory**, acronym **OPT**, for OCHA’s humanitarian work there (ISO3 `PSE`) | `ocha-editorial-style`, updates since the 3rd edition |
| Democratic Republic of the Congo | Acronym **DRC** after first mention | OCHA Editorial Style Guide, 3rd ed. |
| Syrian Arab Republic | **Syria** in running text (for example “the Syria response”) | OCHA Editorial Style Guide, 3rd ed. |

## 4. Never write

These are outdated or unofficial; the table has the right name.

| Not | Write |
|---|---|
| Turkey | Türkiye |
| Ivory Coast | Côte d’Ivoire |
| Swaziland | Eswatini |
| Burma | Myanmar |
| Czech Republic | Czechia |
| Macedonia, FYROM | North Macedonia |
| Cape Verde | Cabo Verde |
| East Timor | Timor-Leste |
| Vietnam | Viet Nam |
| Holland | Netherlands (Kingdom of the) |
| Russia (in formal products) | Russian Federation |
| North Korea / South Korea | Democratic People’s Republic of Korea / Republic of Korea |

## 5. Keeping it current

Rebuild the table when a name changes (UNTERM updates names after official notifications, as with
Türkiye in 2022), or every few months:

```bash
cd <this skill>/scripts && uv run --with openpyxl python3 build_country_names.py
```

It downloads UNTERM’s official Excel export and the M49 table, joins them on the English name, and stops
without writing if any UNTERM name can’t be matched to a code. Then check the changes before using them.

---

## Project Owner

Javier Cueto, Head of Brand and Design Unit

## Maintained by

**OCHA Brand and Design Unit (BDU)**
- Team: ochavisual@un.org
- Focal point: Javier Cueto (cuetoj@un.org)
