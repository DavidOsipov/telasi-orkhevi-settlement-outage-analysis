# Telasi Orkhevi Settlement outage analysis

A reproducible, privacy-conscious evidence package about Telasi electricity-interruption notifications for **one residential building in Orkhevi Settlement (ორხევის დასახლება), Samgori District, Tbilisi, Georgia**.

## Critical interpretation rule

This repository contains two distinct primary evidence layers:

1. **resident-supplied SMS notifications**; and
2. **Telasi public outage publications/API responses**.

Neither layer is a complete utility incident ledger.

For emergency SMS and many Telasi public notices, the stated date/time is an **estimated restoration time**. It is not automatically an outage-start timestamp or an actual restoration timestamp. The repository therefore does not equate notification/publication dates with distinct physical outage incidents and does not calculate physical outage duration from ETAs.

## Resident sources and geographic scope

- Primary locality: **Orkhevi Settlement (ორხევის დასახლება), Tbilisi**
- [Wikidata: Q130437988](https://www.wikidata.org/entity/Q130437988)
- `SITE_A`: **neighbor resident SMS archive for the same building**, with supplied history beginning in 2024.
- `SITE_B`: **repository-owner resident SMS archive for the same building**, with supplied history beginning in 2025.

`SITE_A` / `SITE_B` are retained as stable legacy source IDs. They must **not** be interpreted as two geographic sites or two different buildings.

The exact address, apartment numbers and subscriber/account numbers are intentionally not public. The neighbor may receive Telasi messages for other properties generally, but the user clarified on 2026-08-08 that the pseudonymized `SITE_A` transcript used here is for the same Orkhevi building as `SITE_B`.

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

The longest single-resident archive is `SITE_A` (neighbor). It contains **21** emergency ETA-date groups from 2024-11-10 through 2026-08-06, giving 20 inter-arrival gaps over exactly 634 elapsed days:

- exact mean notification gap: **317/10 = 31.7 days**.

`SITE_B` is a shorter, later archive. Its emergency series contains 11 groups from 2025-12-06 through 2026-08-06:

- exact mean notification gap: **243/10 = 24.3 days**.

The building-level union contains **22** curated emergency groups. Because the second resident archive begins later, that union changes ascertainment over time and is not the preferred constant-source rate series.

For the equal period **1 January–6 August**, the same `SITE_A` series contains:

- 2025: **7** emergency ETA-date groups;
- 2026: **9** groups;
- exact descriptive relative change: **200/7%** (28.571429% rounded to 6 dp).

This is now known to be an Orkhevi-building resident series, but it is still not a complete physical-outage rate.

During the overlapping emergency period from **2025-12-06 through 2026-08-06**:

- SITE_A: **10 unique emergency ETA dates**;
- SITE_B: **11 unique emergency ETA dates**;
- shared ETA dates: **10**;
- Jaccard similarity of the unique ETA-date sets: **10/11**.

This is **cross-resident corroboration for one building**, not correlation between two sites or evidence of shared upstream topology.

At the repository-owner archive (`SITE_B`), emergency SMS carry restoration ETAs on **4, 5 and 6 August 2026**. This is three notification groups on three consecutive ETA dates; without receipt/restoration timestamps it is not proof of three distinct physical outage incidents.

For planned notices without a cancellation signal in the same curated group, **9 explicit announced windows total 39 hours**, exact mean **13/3 h** and median **4 h**. These are announced windows, not measured downtime.

## Independent Tbilisi benchmark

The repository preserves the World Bank Enterprise Surveys 2023 Tbilisi subgroup benchmark. WBES publishes **0.8 electrical outages in a typical month** for Tbilisi businesses. The exact rational representation of that displayed decimal is **4/5**; it does not recover the hidden unrounded survey estimate.

For comparison, the preferred long single-source `SITE_A` inter-arrival series normalizes to an exact mean-Gregorian-month notification rate of **48699/50720**, and its exact ratio to the displayed WBES `4/5` value is **48699/40576** (1.200192231861 rounded to 12 dp), an exact relative excess of **203075/10144%** for that declared normalization.

This comparison is a proxy/sanity check, not a statistically rigorous building-vs-Tbilisi physical-outage reliability ratio: source metrics, populations, years, completeness and event identity differ.

The shorter recent `SITE_B` series produces a larger ratio, but it is not used as the primary benchmark because it covers a shorter and more recent interval.

## Telasi public API evidence

[`data/telasi_api/`](data/telasi_api/) documents Telasi's public power-outage API and preserves dated source snapshots.

The canonical Orkhevi text-search response captured on **2026-08-08** contains **17 public Telasi publications** in `content.list`: 13 observed taxonomy `2770` and 4 observed taxonomy `2769`.

A text hit for `ორხევი` can refer to the settlement, industrial zone, named roads/exits, or other Orkhevi-associated wording. Therefore 17 search hits are **not 17 outages of this building and not 17 settlement-wide outages**.

Exploratory general-list responses reported `content.listCount = 889`, but the reviewed probe artifact contains only page 1 (12 or 100 records depending on payload). The current client therefore uses two full pagination passes and only accepts a corpus as complete when both passes are count-complete and agree on total, publication identities and publication contents.

## Reproduce offline

No third-party Python packages are required.

```bash
python scripts/build_notifications.py
python scripts/validate.py
python -m unittest discover -s tests -v
python scripts/analyze.py --output reports/analysis-output.txt
python scripts/analyze_exact_rates.py --output-text reports/exact-rate-analysis.txt
python scripts/reconstruct_telasi_api_snapshot.py
```

## Unsupported reliability claims

The current evidence is insufficient for defensible calculation of physical outage count, mean physical outage duration, SAIDI, SAIFI, CAIDI, or MTTR. Those require authoritative interruption start/restoration timestamps and a defined affected-customer population, or equivalent independent monitoring.

## License

The repository's MIT License covers original scripts/software and analytical material authored by the repository owner. Third-party SMS text and raw Telasi API/publication material are excluded from that repository-owner MIT grant. See [`LICENSE-SCOPE.md`](LICENSE-SCOPE.md).
