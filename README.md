# Telasi Orkhevi Settlement outage analysis

A reproducible, privacy-conscious analysis of Telasi electricity-interruption SMS notifications centered on Orkhevi Settlement, Samgori District, Tbilisi, Georgia.

## Critical interpretation rule

This repository analyzes **SMS notifications**, not a complete utility outage log.

For emergency SMS, the date/time in the message is an **estimated restoration time**. It is not a verified outage-start timestamp. Consequently, the repository uses the term **emergency restoration-ETA notification group** rather than treating each date as a proven physical outage incident.

## Geographic scope

- Primary locality: **Orkhevi Settlement (ორხევის დასახლება), Tbilisi**
- Wikidata: `Q130437988`
- `SITE_B`: primary Orkhevi service point
- `SITE_A`: strongly correlated neighbor-supplied longitudinal series; its exact public location is deliberately not asserted until the subscriber-to-property mapping is privately confirmed.

See [`SCOPE.md`](SCOPE.md).

## Current evidence

Combined source-record anchor span: **2024-11-10 through 2026-08-06**.

Current curated data contain:

- **22 emergency restoration-ETA notification groups**;
- **1 network-switching restoration-ETA notification group**;
- **11 planned-work-related notification groups**, including cancellation signals;
- **56 individual redacted source-message records** after parsing the supplied transcripts.

These counts are not claimed to equal the number of physical outage incidents.

## August 2026 pattern

At `SITE_B`, emergency notifications carry restoration-ETA dates on:

- 2026-07-14
- 2026-08-04
- 2026-08-05
- 2026-08-06

Thus the supplied record contains **three emergency notification groups at the same service point with restoration ETAs on three consecutive dates, 4-6 August 2026**.

Without receipt timestamps and confirmed restoration between the messages, this must not be restated as proven evidence of three distinct physical outages.

## Repository structure

- `data/source_transcripts/` — redacted resident-supplied SMS transcripts.
- `data/derived/notifications.csv` — reproducibly parsed one-row-per-message data.
- `data/derived/notification_groups.csv` — manually reviewed grouped notification evidence.
- `data/site_metadata.csv` — source roles and coverage cautions.
- `data/external_context.csv` — separately sourced nationwide-grid context.
- `scripts/build_notifications.py` — transcript parser.
- `scripts/analyze.py` — descriptive analysis using consistent-source comparisons and complete windows.
- `scripts/validate.py` — provenance/privacy/schema consistency checks.
- `tests/test_pipeline.py` — regression tests.
- `METHODOLOGY.md` — detailed analytical rules and limitations.
- `PROVENANCE.md` — source and transformation provenance.
- `SCOPE.md` — geographic/evidentiary scope.
- `PRIVACY.md` — privacy constraints.
- `LICENSE-SCOPE.md` — scope of the MIT grant.

## Reproduce

```bash
python scripts/build_notifications.py
python scripts/validate.py
python -m unittest discover -s tests -v
python scripts/analyze.py
```

No third-party Python packages are required.

## Statistical posture

The repository currently reports descriptive statistics only.

A same-source comparison for SITE_A gives:

- Jan 1-Aug 6, 2025: 7 emergency restoration-ETA groups
- Jan 1-Aug 6, 2026: 9 groups

That is a descriptive increase of 28.6% in the supplied notification record. No p-value or confidence interval is presented because completeness of notification capture and independence of events are not established.

## License

The repository includes the MIT License for original software/scripts and analytical material authored by the repository owner.

Third-party SMS transcript text under `data/source_transcripts/` is excluded from that repository-owner MIT grant. See [`LICENSE-SCOPE.md`](LICENSE-SCOPE.md).
