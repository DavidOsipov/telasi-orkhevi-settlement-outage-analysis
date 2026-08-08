# Provenance

## Resident-supplied source material

The public SMS source files are **redacted text transcripts**, not forensic exports of a phone/SMS database.

`SITE_A` and `SITE_B` are stable legacy source IDs, not geographic site IDs:

- `SITE_A` = neighbor resident SMS archive for the same Orkhevi building; supplied history begins in 2024.
- `SITE_B` = repository-owner resident SMS archive for that same building; supplied history begins in 2025.

The same-building relationship was clarified on 2026-08-08. The neighbor may receive Telasi messages for other properties generally, but the pseudonymized SITE_A transcript used in this repository concerns the same Orkhevi building as SITE_B.

Limitations:

- original SMS receipt timestamps are not preserved;
- device/SIM metadata are not preserved;
- subscriber numbers are replaced with stable pseudonyms;
- exact building/apartment addresses are not published;
- transcript order is not treated as a verified timestamp sequence.

They are therefore stored under `data/source_transcripts/`, not described as raw phone evidence.

## Resident-derived data

`scripts/build_notifications.py` converts source transcript blocks into `data/derived/notifications.csv` using deterministic IDs, source line ranges and SHA-256 hashes of each redacted message block.

`data/derived/notification_groups.csv` is manually reviewed. Every group points to one or more source-message IDs. The legacy column name `evidence_sites` stores resident source IDs; it should not be interpreted as evidence for different geographic sites.

New group IDs include date/category/sequence (`GYYYYMMDD-XNN`); the previous date-only ID remains in `legacy_group_id`.

## Exact analytical outputs

Core descriptive arithmetic is represented as reduced rational fractions. Decimal values in analytical reports are presentation values only and are explicitly labeled when rounded.

Current source-derived identities include:

- SITE_A: 20 consecutive emergency-group intervals across 634 elapsed days → exact mean gap `317/10` days;
- SITE_B: 10 intervals across 243 elapsed days → exact mean gap `243/10` days;
- building union: 21 intervals across 634 elapsed days → exact mean gap `634/21` days;
- SITE_A equal-period relative count change: `2/7`, or `200/7%`;
- cross-resident Jaccard: `10/11`;
- planned-window mean: `13/3` hours.

These are mathematical properties of the curated notification anchors/windows, not physical-outage reliability metrics.

## Source-coverage consequence

SITE_A begins in 2024 and SITE_B begins in 2025. Therefore the building-level union changes ascertainment over time: the earlier period has one resident archive and the later period has two. The longest single-source SITE_A series is preferred for longitudinal normalization; the union is secondary/contextual.

## Telasi public API source layer

`data/telasi_api/` is a separate official-source publication layer obtained from Telasi's public website APIs.

The canonical 2026-08-08 Orkhevi search response reconstructs to **295,834 bytes** with SHA-256:

`99e9f1a1331b97300bc1984304c2d71db8acd46fbf543a8ff0e45d3eecf0cb89`

Exploratory API probes are referenced by GitHub Actions provenance and response hashes in `data/telasi_api/raw/2026-08-08/MANIFEST.json`; bulky duplicate probe payloads and browser netlogs are intentionally not committed.

## Independent benchmark source: WBES Tbilisi 2023

`data/benchmarks/wbes_tbilisi_2023.json` preserves selected World Bank Enterprise Surveys Tbilisi 2023 subgroup published/display values and capture provenance.

The retained capture metadata include:

- source endpoint;
- capture date: `2026-08-08`;
- raw response size: `19052` bytes;
- raw response SHA-256: `e1fdd8d139a786b05808a0a9861727e5bf48121f87f2cabafe157bdf6c74accd`;
- GitHub Actions run/job/artifact IDs and artifact SHA-256.

Published decimals are retained as source strings. For example, `"0.8"` can be represented exactly as `4/5` **as a representation of that displayed decimal only**; it does not recover a hidden unrounded weighted estimate.

The WBES “typical month” indicator is preserved as a survey concept rather than silently reinterpreted as an arithmetic mean Gregorian month. Consequently, the repository does not derive an exact “one outage every N days” value or a direct resident-series/Tbilisi reliability ratio from it.

`scripts/fetch_wbes_tbilisi.py` is the reproducible live refresh path. Live refreshes go to ignored `artifacts/` first and are not automatically promoted to `data/benchmarks/`.

## External grid context

`data/external_context.csv` contains separately sourced system-level context. These rows are not local notification groups and are not automatically assigned as causes of local events.

## Stronger future evidence

For a formal reliability dispute, stronger evidence would include SMS receipt timestamps, sender identity, immutable original exports, and ideally independent power-loss/restoration logging or authoritative Telasi incident records.
