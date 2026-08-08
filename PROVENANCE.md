# Provenance

## Resident-supplied source material

The public SMS source files are **redacted text transcripts**, not forensic exports of a phone/SMS database.

Limitations:

- original SMS receipt timestamps are not preserved;
- device/SIM metadata are not preserved;
- subscriber numbers are replaced with stable pseudonyms;
- exact addresses are not published;
- transcript order is not treated as a verified timestamp sequence.

They are therefore stored under `data/source_transcripts/`, not described as raw phone evidence.

## Resident-derived data

`scripts/build_notifications.py` converts source transcript blocks into `data/derived/notifications.csv` using deterministic IDs, source line ranges and SHA-256 hashes of each redacted message block.

`data/derived/notification_groups.csv` is manually reviewed. Every group points to one or more source-message IDs. New group IDs include date/category/sequence (`GYYYYMMDD-XNN`); the previous date-only ID remains in `legacy_group_id`.

`validate.py` rebuilds `notifications.csv` and checks that group evidence sites, dates, ETA sets and planned-window arithmetic agree with supporting message rows.

## Telasi public API source layer

`data/telasi_api/` is a separate official-source publication layer obtained from Telasi's public website APIs.

### Canonical Orkhevi search snapshot

The 2026-08-08 Orkhevi search response was captured in Postman after manually re-entering the Georgian UTF-8 query because a copied cURL/import path had mangled `searchText`.

The original JSON is 295,834 bytes with SHA-256:

`99e9f1a1331b97300bc1984304c2d71db8acd46fbf543a8ff0e45d3eecf0cb89`

Because the repository write channel used for that snapshot was text-only, the source bytes are stored reversibly as deterministic gzip → Base64 split into eight verified text chunks. `MANIFEST.json` records original/gzip/Base64/chunk hashes, and both `validate.py` and `scripts/reconstruct_telasi_api_snapshot.py` reconstruct the original source bytes.

### Focused exploratory API probes

GitHub Actions run `31253449527` / artifact `9020698787` tested four `getPoweroutages` request shapes plus `getMtData`. The raw exploratory responses were inspected from GitHub Actions artifact `9020698787`; they are not duplicated in-repo. Their byte lengths, SHA-256 values and parsed counts are retained in `raw/2026-08-08/MANIFEST.json`.

The exploratory workflow's console summary mistakenly inspected `api.listCount` / `api.list`, so it printed zeros. The inspected artifact responses show that the actual records were under `content.listCount` / `content.list`:

- user exact page payload: reported total 889, page 1 contains 12 records;
- taxonomy search for `ორხევ`: 17/17 records;
- contentType + taxonomy search: 17/17 records;
- general contentType list: reported total 889, page 1 contains 100 records.

The incorrect exploratory summary is not treated as evidence; the corrected observations were derived from the artifact raw responses and retained with response hashes in the manifest.

The `getMtData` response is also preserved and contains page/Nuxt metadata rather than the outage publication body.

### What is intentionally not committed

A browser network trace/netlog was used during reverse-engineering but is not published because such traces can contain unrelated request metadata and are not needed to reproduce the relevant API calls. Endpoint, payload and header semantics needed for reproduction are documented in `data/telasi_api/README.md`.

## API-derived outputs

`scripts/fetch_telasi_api.py` can:

- normalize a captured response;
- perform a live text search;
- fetch a single list page; or
- reconstruct all currently API-reported list pages with raw-page preservation and completeness checks.

Runtime live data are written under ignored `artifacts/` and are not automatically promoted to curated repository evidence.

`scripts/compare_telasi_api_sms.py` performs exact restoration-ETA corroboration. It distinguishes complete and partial API corpora and refuses a corpus-wide negative conclusion when completeness is not established.

## External context

`data/external_context.csv` contains separately sourced system-level context. These rows are not local notification groups and are not automatically assigned as causes of local events.

## Stronger future evidence

For a formal reliability dispute, stronger resident evidence would include:

- SMS receipt timestamp;
- sender identity/short code;
- full original message body;
- device timezone;
- immutable original export hash.

Independent power-loss/restoration logging or authoritative Telasi incident records would allow physical incidents and durations to be reconstructed.
