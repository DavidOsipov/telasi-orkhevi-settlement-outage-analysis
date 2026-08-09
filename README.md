# Telasi Orkhevi Settlement outage-notification analysis

A reproducible, privacy-conscious evidence package about Telasi electricity-interruption notifications for **one residential building in Orkhevi Settlement (ორხევის დასახლება), Samgori District, Tbilisi, Georgia**.

## Critical interpretation rule

The repository separates three kinds of material:

1. **resident-supplied SMS notifications** from two residents of the same building;
2. **Telasi public outage publications/API responses**; and
3. **independent external benchmark/context data**, currently including World Bank Enterprise Surveys (WBES).

Neither the resident SMS layer nor the Telasi publication layer is a complete utility incident ledger.

For emergency SMS and many Telasi public notices, the stated date/time is an **estimated restoration time**. It is not automatically an outage-start timestamp or an actual restoration timestamp. The repository therefore does not equate notification/publication dates with distinct physical outage incidents and does not calculate physical outage duration from ETAs.

## Resident sources and geographic scope

- Primary locality: **Orkhevi Settlement (ორხევის დასახლება), Tbilisi**
- [Wikidata: Q130437988](https://www.wikidata.org/entity/Q130437988)
- `SITE_A`: **neighbor resident SMS archive for the same building**; earliest supplied anchor date: **2024-11-10**.
- `SITE_B`: **repository-owner resident SMS archive for the same building**; earliest supplied anchor date: **2025-11-12**. Its emergency series begins on **2025-12-06**.

`SITE_A` / `SITE_B` are stable legacy source IDs. They must **not** be interpreted as two geographic sites or two different buildings.

The exact address, apartment numbers and subscriber/account numbers are intentionally not public. The source mapping used in this repository treats the included `SITE_A` transcript as belonging to the same Orkhevi building as `SITE_B`; unrelated messages the neighbor may receive for other properties are outside this supplied dataset.

See [`SCOPE.md`](SCOPE.md) and [`PROVENANCE.md`](PROVENANCE.md).

## Resident-SMS evidence

The combined source-record anchor span is **2024-11-10 through 2026-08-06**. That is **635 calendar dates when counted inclusively**; the elapsed difference between the first and last anchor dates is **634 days**. This is a retrospective transcript span, not a proven complete observation window.

Current curated data contain:

- **56** redacted source-message records;
- **22 unique building-level emergency restoration-ETA notification groups** after cross-resident grouping/deduplication;
- **1** network-switching restoration-ETA group;
- **11** planned-work-related groups, including cancellation/update signals.

These counts are not claimed to equal the number of physical outages.

Group IDs use a future-safe form such as `G20260805-E01` (`E` emergency, `S` switching, `P` planned) so multiple groups can exist on the same date. The former date-only IDs are retained in `legacy_group_id` for traceability.

## Current descriptive findings

### Longest constant-source resident series: SITE_A

`SITE_A` contains **21** emergency ETA-date groups from **2024-11-10 through 2026-08-06**. The 21 groups create **20 consecutive inter-arrival intervals** spanning exactly **634 elapsed days**.

- exact mean notification-group gap: **317/10 = 31.7 days**;
- median gap: **23 days**;
- minimum gap: **1 day**;
- maximum gap: **100 days**.

This is the preferred resident source for descriptive longitudinal comparisons because the evidence source stays constant across the supplied span. It is still **not** a complete physical-outage incidence series.

### SITE_B and recent clustering

`SITE_B` contains **11** emergency ETA-date groups from **2025-12-06 through 2026-08-06**: 10 consecutive intervals over exactly 243 elapsed days.

- exact mean notification-group gap: **243/10 = 24.3 days**;
- exact median gap: **45/2 = 22.5 days**.

At `SITE_B`, emergency SMS carry restoration ETAs on **4, 5 and 6 August 2026**. This is three notification groups on three consecutive ETA dates; without receipt/restoration timestamps it is not proof of three distinct physical outage incidents.

The SITE_A and SITE_B counts overlap and must not be added together as separate building incidents.

### Building-level union

The deduplicated building-level union contains **22** emergency groups. Across its first-to-last anchors there are 21 intervals over 634 days, so the exact mean gap is **634/21 days**.

This union is useful as a catalogue of known building-level notifications, but it is **not** the preferred longitudinal series because ascertainment changes when the second resident archive begins.

### Equal-period SITE_A comparison

For **1 January–6 August** in the same SITE_A series:

- 2025: **7** emergency ETA-date groups;
- 2026: **9** groups;
- exact count ratio: **9/7**;
- exact relative change: **2/7**;
- exact percentage change: **200/7%** (decimal rounded to six places: **28.571429%**).

This is geographically relevant to the Orkhevi building, but remains a resident notification series rather than a complete building-wide physical-outage rate. No p-value or confidence interval is reported.

### Cross-resident corroboration

During the overlapping emergency period from **2025-12-06 through 2026-08-06**:

- SITE_A: **10 unique emergency ETA dates**;
- SITE_B: **11 unique emergency ETA dates**;
- shared ETA dates: **10**;
- exact Jaccard similarity of the unique ETA-date sets: **10/11**.

All ten shared curated groups have matching ETA-time sets between the two resident archives. This is strong **cross-resident corroboration for one building**; it is not evidence about two service points or network topology.

### Planned notices

For planned notices without a cancellation signal in the same curated group:

- **9** explicit announced windows;
- exact total announced time: **39 hours**;
- exact mean window: **13/3 hours = 4 h 20 min**;
- exact median window: **4 hours**.

These are announced windows, not measured downtime.

## Independent Tbilisi context: WBES 2023

The repository preserves selected published/display values from the **World Bank Enterprise Surveys (WBES), Georgia 2023, Tbilisi location subgroup** under [`data/benchmarks/`](data/benchmarks/):

- firms experiencing electrical outages: **31.8%**;
- average electrical outages in a **typical month**: **0.8**;
- firms identifying electricity as a major or very severe constraint: **38.6%**;
- firms owning or sharing a generator: **29.8%**.

The displayed `0.8` can be represented exactly as **4/5**, but only as the rational representation of the published decimal string. It does not recover a hidden unrounded survey estimate.

More importantly, WBES **“typical month” is a survey concept, not the arithmetic mean Gregorian calendar month**. Therefore this repository does **not**:

- convert `0.8` into “one outage every N days”;
- treat SITE_A, SITE_B or building-union calendar inter-arrival normalizations as definition-identical to WBES;
- claim an `X×` or `Y%` Orkhevi-vs-Tbilisi physical-outage reliability difference from these non-identical metrics.

Conditional arithmetic quotients are retained in machine-readable exact-analysis output only as diagnostic/reproducibility fields and are explicitly marked **not a rate ratio**.

See [`data/benchmarks/README.md`](data/benchmarks/README.md) and [`reports/exact-rate-analysis.txt`](reports/exact-rate-analysis.txt).

## Telasi public API evidence

[`data/telasi_api/`](data/telasi_api/) documents Telasi's public power-outage API and preserves dated source snapshots.

The canonical Orkhevi text-search response captured on **2026-08-08** contains **17 public Telasi publications** in `content.list`: 13 with observed taxonomy ID `2770` and 4 with observed taxonomy ID `2769`.

A text hit for `ორხევი` can refer to the settlement, industrial zone, named roads/exits, or other Orkhevi-associated wording. Therefore 17 search hits are **not 17 outages of this building and not 17 settlement-wide outages**.

Exploratory general-list responses reported `content.listCount = 889`, but the reviewed probe artifact contains only page 1 (12 or 100 records depending on payload). The current client therefore uses two full pagination passes and only accepts a corpus as complete when both passes are count-complete and agree on total, publication identities and publication contents.

See [`data/telasi_api/README.md`](data/telasi_api/README.md) and [`reports/telasi-api-findings-2026-08-08.md`](reports/telasi-api-findings-2026-08-08.md).

## Repository structure

- `data/source_transcripts/` — redacted resident-supplied SMS transcripts.
- `data/derived/notifications.csv` — reproducibly parsed one-row-per-message table.
- `data/derived/notification_groups.csv` — manually reviewed grouped SMS evidence.
- `data/telasi_api/` — Telasi public API documentation and preserved/provenanced source material.
- `data/benchmarks/` — independently sourced external aggregate benchmarks.
- `data/site_metadata.csv` — resident-source roles and cautions.
- `data/external_context.csv` — separately sourced system-level context.
- `scripts/build_notifications.py` — resident transcript parser.
- `scripts/analyze.py` — conservative descriptive analysis using rational arithmetic for core metrics.
- `scripts/analyze_exact_rates.py` — exact-fraction statistics plus explicitly separated benchmark diagnostics.
- `scripts/fetch_wbes_tbilisi.py` — reproducible WBES Tbilisi subgroup fetch/normalization.
- `scripts/validate.py` — source/group/API provenance, schema, privacy and arithmetic validation.
- `scripts/fetch_telasi_api.py` — UTF-8-safe Telasi API fetcher/normalizer with two-pass pagination.
- `scripts/compare_telasi_api_sms.py` — exact ETA corroboration helper with completeness gating.
- `reports/analysis-output.txt` — deterministic conservative descriptive output.
- `reports/exact-rate-analysis.txt` — deterministic exact-fraction human-readable output.

## Reproduce offline

No third-party Python packages are required for the offline analytical reports.

```bash
python scripts/build_notifications.py
python scripts/validate.py
python scripts/analyze.py --output reports/analysis-output.txt
python scripts/analyze_exact_rates.py --output-text reports/exact-rate-analysis.txt --output-json artifacts/exact-rate-analysis.json
python scripts/reconstruct_telasi_api_snapshot.py
```

The repository also contains regression tests, but they are not required merely to inspect or regenerate these reports.

## Refresh the independent WBES benchmark

```bash
python scripts/fetch_wbes_tbilisi.py \
  --output-dir artifacts/wbes/tbilisi-2023
```

Live output remains under ignored `artifacts/` until deliberately reviewed and promoted as evidence.

## Further documentation

- [`METHODOLOGY.md`](METHODOLOGY.md) — evidence model, grouping, arithmetic and interpretation rules.
- [`PROVENANCE.md`](PROVENANCE.md) — resident/API/benchmark source provenance.
- [`SCOPE.md`](SCOPE.md) — geographic and temporal scope.
- [`AUDIT.md`](AUDIT.md) — material corrections and re-audit history.
- [`PRIVACY.md`](PRIVACY.md) — publication/privacy constraints.
- [`LICENSE-SCOPE.md`](LICENSE-SCOPE.md) — licensing boundaries for original and third-party material.

## Unsupported reliability claims

The current evidence is insufficient for defensible calculation of physical outage count, mean physical outage duration, SAIDI, SAIFI, CAIDI, or MTTR. Those require authoritative interruption start/restoration timestamps and a defined affected-customer population, or equivalent independent monitoring.

## License

The repository's MIT License covers original scripts/software and analytical material authored by the repository owner. Third-party source data are excluded from that repository-owner MIT grant where applicable; see [`LICENSE-SCOPE.md`](LICENSE-SCOPE.md).
