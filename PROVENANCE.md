# Provenance

## Source material

The public source files are **redacted text transcripts**, not forensic exports of the SMS database.

They were assembled from messages supplied in the conversation and have these limitations:

- original SMS receipt timestamps are not preserved;
- device/SIM metadata are not preserved;
- subscriber numbers are replaced with stable pseudonyms;
- exact addresses are not published;
- message ordering reflects the supplied transcript order and must not be treated as a verified timestamp sequence.

The files are therefore stored under `data/source_transcripts/`, not described as raw phone evidence.

## Derived data

`scripts/build_notifications.py` converts source transcript blocks into `data/derived/notifications.csv`.

`data/derived/notification_groups.csv` is manually reviewed. Every group contains `supporting_message_ids` that point back to one or more rows in `notifications.csv`, which in turn contain source file and line ranges plus SHA-256 hashes of the redacted message text.

## Stronger future evidence

For a formal reliability dispute, stronger evidence would include an export preserving:

- SMS receipt timestamp;
- sender identity/short code;
- full message body;
- device timezone;
- immutable original file hash.

Independent logging of actual power-loss and restoration timestamps would further allow physical outage incidents and durations to be reconstructed.
