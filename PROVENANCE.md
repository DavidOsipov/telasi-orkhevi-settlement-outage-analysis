# Provenance

## Resident-supplied source material

The public SMS source files are **redacted text transcripts**, not forensic exports of a phone/SMS database.

`SITE_A` and `SITE_B` are stable legacy source IDs, not geographic site IDs:

- `SITE_A` = neighbor resident SMS archive for the same Orkhevi building; supplied history begins in 2024.
- `SITE_B` = repository-owner resident SMS archive for that same building; supplied history begins in 2025.

The user clarified this same-building relationship on 2026-08-08. The neighbor may receive Telasi messages for other properties generally, but the pseudonymized SITE_A transcript used in this repository is treated as the same Orkhevi building as SITE_B.

Limitations:

- original SMS receipt timestamps are not preserved;
- device/SIM metadata are not preserved;
- subscriber numbers are replaced with stable pseudonyms;
- exact building/apartment addresses are not published;
- transcript order is not treated as a verified timestamp sequence.

They are therefore stored under `data/source_transcripts/`, not described as raw phone evidence.

## Resident-derived data

`scripts/build_notifications.py` converts source transcript blocks into `data/derived/notifications.csv` using deterministic IDs, source line ranges and SHA-256 hashes of each redacted message block.

`data/derived/notification_groups.csv` is manually reviewed. Every group points to one or more source-message IDs. The legacy column name `evidence_sites` stores these resident source IDs; it should not be interpreted as evidence for different geographic sites.

New group IDs include date/category/sequence (`GYYYYMMDD-XNN`); the previous date-only ID remains in `legacy_group_id`.

`validate.py` rebuilds `notifications.csv` and checks source/group dates, ETA sets and planned-window arithmetic.

## Source-coverage consequence

SITE_A begins in 2024 and SITE_B begins in 2025. Therefore the building-level union changes ascertainment over time: the earlier period has one resident archive and the later period has two. The longest single-source SITE_A series is preferred for longitudinal rate normalization; the union is secondary/contextual.

## Telasi public API source layer

`data/telasi_api/` is a separate official-source publication layer obtained from Telasi's public website APIs.

The canonical 2026-08-08 Orkhevi search response is preserved and reconstructs to 295,834 bytes with SHA-256:

`99e9f1a1331b97300bc1984304c2d71db8acd46fbf543a8ff0e45d3eecf0cb89`

Exploratory API probes are referenced by GitHub Actions provenance and response hashes in `data/telasi_api/raw/2026-08-08/MANIFEST.json`; bulky duplicate probe payloads and browser netlogs are intentionally not committed.

## Independent benchmark source

`data/benchmarks/wbes_tbilisi_2023.json` preserves the World Bank Enterprise Surveys Tbilisi 2023 subgroup values and capture provenance. Published decimals are treated as finite-precision source display values. Exact rational forms in the analysis represent those displayed strings exactly; they do not recover hidden unrounded weighted estimates.

## Stronger future evidence

For a formal reliability dispute, stronger evidence would include SMS receipt timestamps, sender identity, immutable original exports, and ideally independent power-loss/restoration logging or authoritative Telasi incident records.
