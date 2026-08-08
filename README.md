# Telasi Orkhevi Settlement outage analysis

A reproducible, privacy-preserving record of electricity interruption SMS notices for two correlated Telasi service points in Orkhevi Settlement, Samgori District, Tbilisi, Georgia.

## Geographic scope

This repository concerns electricity interruptions affecting two correlated Telasi service points in **Orkhevi Settlement (ორხევის დასახლება), Samgori District, Tbilisi, Georgia**.

Canonical place identifier: **[Wikidata Q130437988](https://www.wikidata.org/entity/Q130437988)**.

The repository does not claim that every interruption affected the whole settlement. The SMS evidence supports a shared upstream distribution fault domain for the two observed service points, while the exact feeder / transformer topology is not public in this dataset.

## Current dataset

Observation window: **2024-11-10 to 2026-08-06 (635 days)**.

Conservative event-level count:

- **22 emergency interruption dates**;
- **1 network-switching interruption date**;
- **9 non-cancelled planned/urgent-work dates**;
- **2 cancelled planned-work dates**.

The 4-6 August 2026 run is the densest three-day emergency cluster in the supplied SMS record.

This repository deliberately treats the SMS dataset as a **lower-bound observational record**, not an official reliability dataset.

## Repository structure

- `data/raw/` — redacted source SMS text.
- `data/processed/events.csv` — manually reviewed conservative event-level dataset.
- `data/processed/national_context.csv` — separate contextual national-grid events; not counted in local SMS statistics.
- `scripts/analyze.py` — reproducible descriptive statistics and year-over-year comparison.
- `scripts/validate.py` — basic consistency and privacy checks.
- `reports/statistical-summary-ru.md` — detailed statistical interpretation in Russian.
- `METHODOLOGY.md` — classification, deduplication, limitations.
- `SCOPE.md` — geographic and evidentiary scope, including settlement-wide limitations.
- `PRIVACY.md` — public-release safeguards.

## Reproduce

```bash
python scripts/validate.py
python scripts/analyze.py
```

No third-party Python dependencies are required.

## Key limitation

The SMS messages usually provide an estimated restoration time, not a verified outage start time or actual restoration timestamp. Some outages may generate no SMS. Therefore the repository does not claim official SAIDI, SAIFI, CAIDI, MTTR, or complete interruption counts.

## Public-use principle

Subscriber numbers and addresses are intentionally absent from the public data. A complainant can provide the relevant subscriber number privately to Telasi while citing this repository as longitudinal supporting evidence.

## Publish to GitHub

On Windows PowerShell, after extracting the archive and opening the repository directory:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\publish.ps1
```

This validates the public dataset, initializes Git, creates `DavidOsipov/telasi-orkhevi-settlement-outage-analysis` as a public GitHub repository with GitHub CLI, and pushes `main`.

If the repository is created manually on GitHub first, the files can instead be pushed normally or updated through the connected GitHub integration.

## License

The repository is released under the **MIT License**. See [`LICENSE`](LICENSE).

The license applies to the repository contents published by the repository owner. Source SMS text remains factual/evidentiary material supplied for analysis; personal identifiers are removed before publication.

