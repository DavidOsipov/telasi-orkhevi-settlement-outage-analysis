# Telasi Orkhevi Settlement outage analysis

A reproducible, privacy-conscious evidence package about Telasi electricity-interruption notifications centered on **Orkhevi Settlement (ორხევის დასახლება), Samgori District, Tbilisi, Georgia**.

## Critical interpretation rule

This repository contains three analytically distinct evidence/context layers:

1. **resident-supplied SMS notifications**;
2. **Telasi public outage publications/API responses**; and
3. **independent external benchmarks/context**, including World Bank Enterprise Surveys (WBES).

Neither the resident SMS layer nor the Telasi publication layer is a complete utility incident ledger.

For emergency SMS and many Telasi public notices, the stated date/time is an **estimated restoration time**. It is not automatically an outage-start timestamp or an actual restoration timestamp. The repository therefore does not equate notification/publication dates with distinct physical outage incidents and does not calculate physical outage duration from ETAs.

## Geographic scope

- Primary locality: **Orkhevi Settlement (ორხევის დასახლება), Tbilisi**
- [Wikidata: Q130437988](https://www.wikidata.org/entity/Q130437988)
- `SITE_B`: primary Orkhevi service point
- `SITE_A`: neighbor-supplied corroborating longitudinal series; its exact public property/location mapping is intentionally unresolved because the resident receives Telasi messages for more than one property.

See [`SCOPE.md`](SCOPE.md).

## Resident-SMS evidence

Combined source-record anchor span: **2024-11-10 through 2026-08-06**. This is a retrospective transcript span, not a proven complete observation window.

Current curated data contain:

- **56** redacted source-message records;
- **22** emergency restoration-ETA notification groups;
- **1** network-switching restoration-ETA group;
- **11** planned-work-related groups, including cancellation/update signals.

These counts are not claimed to equal the number of physical outages.

Group IDs use a future-safe form such as `G20260805-E01` (`E` emergency, `S` switching, `P` planned) so multiple groups can exist on the same date. The former date-only IDs are retained in `legacy_group_id` for traceability.

## Current descriptive findings

### SITE_B inter-arrival record

SITE_B has **11 emergency restoration-ETA notification groups** from **2025-12-06 through 2026-08-06**. Between the first and last anchor there are exactly **243 elapsed days** and **10 consecutive inter-arrival intervals**.

Therefore:

- exact mean gap: **243/10 = 24.3 days**;
- exact median gap: **45/2 = 22.5 days**;
- exact standardized inter-arrival count per 30 days: **100/81**.

These are notification-group inter-arrival metrics. They are **not** a physical-outage incidence rate and must not be restated as “a real outage every 24.3 days.” The supplied transcript is not a proven complete observation window and multiple notifications can belong to one physical incident.

At SITE_B, emergency SMS carry restoration ETAs on **4, 5, and 6 August 2026**. This is three emergency notification groups at one service point on three consecutive ETA dates; without SMS receipt/restoration timestamps it is not proof of three distinct physical outage incidents.

### Same-source SITE_A comparison

For the equal period **1 January–6 August** in the same SITE_A series:

- 2025: **7** emergency ETA-date groups;
- 2026: **9** groups;
- exact count ratio: **9/7**;
- exact relative change: **2/7**, or **200/7%** (decimal rounded to six places: **28.571429%**).

This is a same-source change in the supplied notification record. Because SITE_A's exact public property mapping is unresolved, it must **not** be restated as an Orkhevi-wide outage-rate increase. No p-value or confidence interval is reported.

### Cross-site overlap

During the overlapping emergency period from **2025-12-06 through 2026-08-06**:

- SITE_A: **10 unique emergency ETA dates**;
- SITE_B: **11 unique emergency ETA dates**;
- shared ETA dates: **10**;
- exact Jaccard similarity of the unique ETA-date sets: **10/11** (decimal rounded to 12 places: **0.909090909091**).

All ten shared curated groups have matching ETA-time sets between the two sites. This strongly supports repeated shared affected scope, but does not prove a specific feeder, transformer, substation, or topology.

### Planned notices

For planned notices without a cancellation signal in the same curated group:

- **9** explicit announced windows;
- exact total announced time: **39 hours**;
- exact mean window: **13/3 hours = 4 h 20 min**;
- exact median window: **4 hours**.

These are announced windows, not measured downtime.

## Independent Tbilisi benchmark: WBES 2023

The repository preserves a captured **World Bank Enterprise Surveys (WBES), Georgia 2023, Tbilisi location subgroup** benchmark under [`data/benchmarks/`](data/benchmarks/).

Relevant published/display values are:

- firms experiencing electrical outages: **31.8%**;
- average electrical outages in a **typical month**: **0.8**;
- firms identifying electricity as a major or very severe constraint: **38.6%**;
- firms owning or sharing a generator: **29.8%**.

Two cautions are essential:

1. these are finite-precision published/display values, not hidden unrounded survey estimates; and
2. WBES **“typical month” is a survey concept, not the arithmetic mean Gregorian calendar month**.

Accordingly, this repository does **not** convert WBES `0.8` into “one outage every N days” and does **not** claim a direct `X×` or `Y%` Orkhevi-vs-Tbilisi outage-rate difference. The populations, years, evidence sources, completeness, event identity and month definitions differ.

See [`data/benchmarks/README.md`](data/benchmarks/README.md) and [`reports/exact-rate-analysis.txt`](reports/exact-rate-analysis.txt).

## Telasi public API evidence

[`data/telasi_api/`](data/telasi_api/) documents Telasi's public power-outage API and preserves dated source snapshots.

The canonical Orkhevi text-search response captured on **2026-08-08** contains **17 public Telasi publications** in `content.list`:

- 13 with observed taxonomy ID `2770`;
- 4 with observed taxonomy ID `2769`.

A text hit for `ორხევი` can refer to the settlement, industrial zone, named roads/exits, or other Orkhevi-associated wording. Therefore 17 search hits are **not 17 outages of SITE_B and not 17 settlement-wide outages**.

Exploratory general-list responses on the same date reported `content.listCount = 889`, but the reviewed exploratory probe artifact contains only **page 1** (12 or 100 records depending on payload). The repository therefore **does not claim that a complete 889-publication historical snapshot was preserved**. The current client has an explicit `--all-pages` mode that performs **two full pagination passes** and succeeds only when both passes are count-complete and agree on the reported total, publication identities, and publication contents. This reduces live-list movement risk but is still not an atomic internal Telasi database snapshot.

The API contains source-side anomalies, including publication timestamps later than stated ETAs and at least one January 2026 publication whose body contains an ETA year of 2025. Parsers preserve those values literally rather than silently correcting Telasi's source data.

See [`data/telasi_api/README.md`](data/telasi_api/README.md) and [`reports/telasi-api-findings-2026-08-08.md`](reports/telasi-api-findings-2026-08-08.md).

## Repository structure

- `data/source_transcripts/` — redacted resident-supplied SMS transcripts.
- `data/derived/notifications.csv` — reproducibly parsed one-row-per-message table.
- `data/derived/notification_groups.csv` — manually reviewed grouped SMS evidence.
- `data/telasi_api/` — Telasi public API documentation and a cryptographically verified canonical raw snapshot plus provenance metadata for exploratory probes.
- `data/benchmarks/` — independently sourced external benchmark captures/normalized values, currently WBES Tbilisi 2023.
- `data/site_metadata.csv` — source roles and geographic cautions.
- `data/external_context.csv` — separately sourced system-level context.
- `scripts/build_notifications.py` — resident transcript parser.
- `scripts/analyze.py` — conservative descriptive analysis using exact rational arithmetic for core metrics.
- `scripts/analyze_exact_rates.py` — exact-fraction inter-arrival/statistical calculations and benchmark semantics.
- `scripts/fetch_wbes_tbilisi.py` — reproducible WBES Tbilisi subgroup fetch/normalization.
- `scripts/validate.py` — SMS/group/API provenance, schema, privacy, arithmetic and hash validation.
- `scripts/fetch_telasi_api.py` — UTF-8-safe Telasi API fetcher/normalizer with real pagination.
- `scripts/compare_telasi_api_sms.py` — exact ETA corroboration helper; corpus-wide negative conclusions require internally consistent records plus two agreeing count-complete pagination passes.
- `scripts/reconstruct_telasi_api_snapshot.py` — cross-platform reconstruction and verification of the canonical raw API snapshot.
- `reports/analysis-output.txt` — deterministic conservative descriptive output.
- `reports/exact-rate-analysis.txt` — deterministic exact-fraction output and external-benchmark interpretation.
- `tests/` — offline regression tests.
- `.github/workflows/quality.yml` — offline reproducibility checks.
- `.github/workflows/telasi-api-live-probe.yml` — live API semantics/pagination probe.

## Reproduce offline

No third-party Python packages are required.

```bash
python scripts/build_notifications.py
python scripts/validate.py
python scripts/analyze.py --output reports/analysis-output.txt
python scripts/analyze_exact_rates.py --output-text reports/exact-rate-analysis.txt --output-json artifacts/exact-rate-analysis.json
python scripts/reconstruct_telasi_api_snapshot.py
```

The repository also contains regression tests, but they are not required merely to inspect or regenerate the analytical reports.

`quality.yml` checks that rebuilding does not change committed `notifications.csv`, `reports/analysis-output.txt`, or `reports/exact-rate-analysis.txt`.

## Refresh the independent WBES benchmark

```bash
python scripts/fetch_wbes_tbilisi.py \
  --output-dir artifacts/wbes/tbilisi-2023
```

Live output remains under ignored `artifacts/` until it is deliberately reviewed and promoted as evidence.

## Fetch live Telasi data

Search Orkhevi:

```bash
python scripts/fetch_telasi_api.py \
  --search-text "ორხევი" \
  --output-dir artifacts/telasi_api/orkhevi
```

Fetch and verify two complete/stable list passes:

```bash
python scripts/fetch_telasi_api.py \
  --all-pages \
  --per-page 100 \
  --output-dir artifacts/telasi_api/all
```

Compare a **complete** live corpus with resident SMS ETAs:

```bash
python scripts/compare_telasi_api_sms.py \
  --api-dir artifacts/telasi_api/all \
  --orkhevi-dir artifacts/telasi_api/orkhevi \
  --require-complete \
  --output artifacts/telasi_api/comparison.json
```

`artifacts/` is ignored by Git to prevent transient live responses from being accidentally published as curated source snapshots.

## Unsupported reliability claims

The current evidence is insufficient for defensible calculation of physical outage count, mean physical outage duration, SAIDI, SAIFI, CAIDI, or MTTR. Those require authoritative interruption start/restoration timestamps and a defined affected-customer population, or equivalent independent monitoring.

## License

The repository's MIT License covers original scripts/software and analytical material authored by the repository owner. Third-party source data are excluded from that repository-owner MIT grant; see [`LICENSE-SCOPE.md`](LICENSE-SCOPE.md).
