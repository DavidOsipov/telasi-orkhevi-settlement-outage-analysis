# Telasi Orkhevi Settlement outage analysis

A reproducible, privacy-conscious evidence package about Telasi electricity-interruption notifications centered on **Orkhevi Settlement (ორხევის დასახლება), Samgori District, Tbilisi, Georgia**.

## Critical interpretation rule

This repository contains two distinct primary evidence layers:

1. **resident-supplied SMS notifications**; and
2. **Telasi public outage publications/API responses**.

Neither layer is a complete utility incident ledger.

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

At `SITE_B`, emergency SMS carry restoration ETAs on **4, 5, and 6 August 2026**. This is three emergency notification groups at one service point on three consecutive ETA dates; without SMS receipt/restoration timestamps it is not proof of three distinct physical outage incidents.

For the equal period **1 January–6 August**, the same SITE_A series contains:

- 2025: **7** emergency ETA-date groups;
- 2026: **9** groups;
- descriptive change: **+28.6%**.

This is a same-source change in the supplied notification record. Because SITE_A's exact public property mapping is unresolved, it must **not** be restated as an Orkhevi-wide outage-rate increase. No p-value or confidence interval is reported.

During the overlapping emergency period from **2025-12-06 through 2026-08-06**:

- SITE_A: **10 unique emergency ETA dates**;
- SITE_B: **11 unique emergency ETA dates**;
- shared ETA dates: **10**;
- Jaccard similarity of the unique ETA-date sets: **10/11 = 0.909**.

All ten shared curated groups have matching ETA-time sets between the two sites. This strongly supports repeated shared affected scope, but does not prove a specific feeder, transformer, substation, or topology.

For planned notices without a cancellation signal in the same curated group, **9 explicit announced windows total 39.0 hours**, mean **4.33 h** and median **4.00 h**. These are announced windows, not measured downtime.

The analysis also prints per-site gaps between emergency **ETA-date notification groups**. Those values must not be described as “an outage every N days,” because SMS completeness and physical-incident identity are unknown.

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
- `data/site_metadata.csv` — source roles and geographic cautions.
- `data/external_context.csv` — separately sourced system-level context.
- `scripts/build_notifications.py` — resident transcript parser.
- `scripts/analyze.py` — conservative descriptive analysis.
- `scripts/validate.py` — SMS/group/API provenance, schema, privacy, arithmetic and hash validation.
- `scripts/fetch_telasi_api.py` — UTF-8-safe Telasi API fetcher/normalizer with real pagination.
- `scripts/compare_telasi_api_sms.py` — exact ETA corroboration helper; corpus-wide negative conclusions require internally consistent records plus two agreeing count-complete pagination passes.
- `scripts/reconstruct_telasi_api_snapshot.py` — cross-platform reconstruction and verification of the canonical raw API snapshot.
- `tests/` — offline regression tests for SMS analysis, window logic and API fixtures/pagination.
- `.github/workflows/quality.yml` — offline reproducibility checks.
- `.github/workflows/telasi-api-live-probe.yml` — live API semantics/pagination probe.

## Reproduce offline

No third-party Python packages are required.

```bash
python scripts/build_notifications.py
python scripts/validate.py
python -m unittest discover -s tests -v
python scripts/analyze.py --output reports/analysis-output.txt
python scripts/reconstruct_telasi_api_snapshot.py
```

`quality.yml` additionally fails if rebuilding changes committed `notifications.csv` or `reports/analysis-output.txt`.

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

The repository's MIT License covers original scripts/software and analytical material authored by the repository owner. Third-party SMS text and raw Telasi API/publication material are excluded from that repository-owner MIT grant. See [`LICENSE-SCOPE.md`](LICENSE-SCOPE.md).
