# Provenance

## Resident-supplied source material

The public SMS source files are **redacted text transcripts**, not forensic exports of the SMS database.

They were assembled from messages supplied in the conversation and have these limitations:

- original SMS receipt timestamps are not preserved;
- device/SIM metadata are not preserved;
- subscriber numbers are replaced with stable pseudonyms;
- exact addresses are not published;
- message ordering reflects the supplied transcript order and must not be treated as a verified timestamp sequence.

The files are therefore stored under `data/source_transcripts/`, not described as raw phone evidence.

## Telasi public API source layer

`data/telasi_api/` is a separate official-source publication layer obtained from Telasi's public website APIs.

The dated snapshot under `data/telasi_api/raw/2026-08-08/` preserves:

- the successful `getPoweroutages` Orkhevi-search response originally captured through Postman;
- the `getMtData` response captured by the repository's GitHub Actions probe;
- endpoint/payload provenance and cryptographic hashes in `MANIFEST.json`.

The large `getPoweroutages` response is stored reversibly as deterministic gzip → Base64 split into verified text chunks. Its reconstructed original JSON SHA-256 is recorded in the manifest.

These API records prove what Telasi's public publication system exposed at capture time. They are **not automatically authoritative measurements of physical outage start/end times**. Publication timestamps, stated restoration ETAs, taxonomy labels and source-side typos are preserved rather than silently corrected.

## Derived data

`scripts/build_notifications.py` converts source transcript blocks into `data/derived/notifications.csv`.

`data/derived/notification_groups.csv` is manually reviewed. Every group contains `supporting_message_ids` that point back to one or more rows in `notifications.csv`, which in turn contain source file and line ranges plus SHA-256 hashes of the redacted message text.

`scripts/fetch_telasi_api.py` can fetch/normalize the public Telasi publication API or normalize an already captured response. API-derived normalization must remain distinguishable from the resident SMS-derived tables.

## Stronger future evidence

For a formal reliability dispute, stronger resident evidence would include an export preserving:

- SMS receipt timestamp;
- sender identity/short code;
- full message body;
- device timezone;
- immutable original file hash.

Independent logging of actual power-loss and restoration timestamps would further allow physical outage incidents and durations to be reconstructed.
