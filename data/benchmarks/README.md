# Independent benchmark data

This directory contains deliberately reviewed external benchmark values kept separate from the resident SMS and Telasi public-publication evidence layers.

## WBES Tbilisi 2023

`wbes_tbilisi_2023.json` records selected published/display indicators from the **World Bank Enterprise Surveys (WBES), Georgia 2023, Tbilisi location subgroup**.

Captured values currently include:

- `31.8` — percent of firms experiencing electrical outages;
- `0.8` — average number of electrical outages in a **typical month**;
- `38.6` — percent of firms identifying electricity as a major or very severe constraint;
- `29.8` — percent of firms owning or sharing a generator.

The capture was made on 2026-08-08 from the World Bank Enterprise Surveys data portal backend. The JSON records the source endpoint, response byte count/SHA-256 and GitHub Actions run/job/artifact provenance.

## Precision rule

Published WBES values are retained as decimal strings. For example, `"0.8"` can be represented exactly as the rational number `4/5` **only as a representation of the returned decimal string**. That does not recover a hidden unrounded weighted survey estimate.

`scripts/fetch_wbes_tbilisi.py` refuses to claim lexical decimal precision if an expected source value is no longer returned as a JSON string.

## “Typical month” semantics

Do not interpret WBES `0.8 outages in a typical month` as `0.8 outages per arithmetic mean Gregorian calendar month`.

The Enterprise Survey question is explicitly about outages in a **typical month** during the last fiscal year. World Bank questionnaire guidance treats a typical month as the most common type of month regarding the characteristic being asked, rather than a fixed 30/30.436875-day rate unit.

Consequences for this repository:

- do not convert WBES `0.8` into a day interval;
- do not report the conditional resident-series/WBES arithmetic quotients as outage-rate ratios;
- do not state that the Orkhevi building has `X×` or `Y%` more physical outages than Tbilisi on the basis of these non-identical measures;
- use WBES as independent Tbilisi context alongside the resident series, with source, population, period and definition differences explicit.

The exact-analysis JSON may retain old quotient fields for reproducibility/backward compatibility, but they are marked diagnostic arithmetic only and are omitted from the human-readable statistical conclusions.

## Refreshing the benchmark

A live refresh can be written to ignored runtime artifacts:

```bash
python scripts/fetch_wbes_tbilisi.py \
  --output-dir artifacts/wbes/tbilisi-2023
```

Review the response and provenance before deliberately promoting a refreshed value under `data/benchmarks/`.
