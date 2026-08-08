# Methodology

## 1. Evidence model

The repository separates evidence layers that must not be silently conflated:

1. **Resident source message** — one redacted SMS text block supplied by a resident.
2. **Resident notification group** — a manually reviewed grouping of one or more resident SMS messages that appear to concern the same scheduled date or emergency restoration-ETA date.
3. **Telasi public publication** — one website/API publication exposed by Telasi's public system.
4. **Physical outage incident** — an actual interruption of electricity supply.
5. **Independent external benchmark/context** — regulator, transmission-system or independent survey information kept separate from the local evidence layers.

The repository preserves evidence for layers 1–3 and contextual/benchmark sources for layer 5. It does **not** have enough metadata to identify layer 4 reliably in every case.

Neither `notification_groups.csv` nor Telasi `content.list` is treated as an authoritative outage-event ledger.

## 2. Resident-source identity

`SITE_A` and `SITE_B` are stable legacy identifiers, but they **do not represent two geographic sites**.

- `SITE_A` = neighbor resident SMS archive for the same Orkhevi building; supplied history begins in 2024.
- `SITE_B` = repository-owner resident SMS archive for that same building; supplied history begins in 2025.

The exact address, apartment numbers and subscriber/account numbers are not public.

The neighbor may receive Telasi SMS for other properties generally, but the pseudonymized `SITE_A` transcript used in this repository concerns the **same building** as `SITE_B`.

The legacy CSV column name `evidence_sites` is therefore semantically an **evidence-source identifier set** for this dataset. It is retained to avoid unnecessary schema churn.

## 3. Meaning of resident SMS dates

For emergency SMS, the Telasi wording describes the date/time as the **estimated restoration time** (`energomomaragebis agdgenis savaraudo droa`). Therefore:

- emergency `anchor_date` is `restoration_eta_date`;
- it is not a verified outage-start date;
- the interruption may have begun on a different calendar date;
- an ETA is not an actual restoration timestamp.

For planned-work messages, the anchor date is the explicitly scheduled interruption date.

## 4. Grouping, identifiers and duplicates

Exact duplicate SMS messages remain present in `notifications.csv` and can be grouped together in `notification_groups.csv`.

Same-day ETA messages may represent one incident with a revised ETA, multiple incidents on the same day, or duplicated delivery. Ambiguity is preserved when the evidence cannot distinguish these.

Examples:

- 2025-06-28: ETA 01:18 and 17:43, `incident_count_min=1`, `incident_count_max=2`;
- 2026-01-22: ETA 12:00 and 20:00 in both resident archives;
- 2026-04-07: ETA 19:33 and 22:29 in both archives, plus an exact duplicate 22:29 SMS in SITE_A.

Group IDs use `GYYYYMMDD-XNN`, where `X` is `E`, `S` or `P`. Different groups are not automatically distinct physical incidents. The date-only legacy ID remains traceability metadata and need not be unique if multiple groups occur on one date.

## 5. Completeness and ascertainment

The resident material is a retrospective SMS archive, not a prospectively monitored outage sensor.

Known limitations include:

- real interruptions can occur without an SMS;
- messages can be absent from the supplied archives;
- SMS receipt timestamps are absent;
- actual restoration timestamps are absent;
- one incident can generate multiple messages or ETA updates.

There is an additional source-coverage issue: SITE_A begins in 2024 while SITE_B begins in 2025. A building-level union of both archives is useful for preserving all known notification groups, but its **ascertainment changes over time** because the later period has two resident sources instead of one.

Therefore:

- the **longest single-source SITE_A series** is preferred for longitudinal normalization;
- the building union is secondary/contextual;
- the shorter SITE_B series is useful for recent clustering but is not the preferred long-run source series.

## 6. Exact arithmetic policy

Core descriptive arithmetic is represented as reduced rational fractions rather than binary floating point.

Current exact values include:

- SITE_A mean emergency ETA-date group gap: **317/10 days = 31.7 days**;
- SITE_B mean gap: **243/10 days = 24.3 days**;
- SITE_B median gap: **45/2 days = 22.5 days**;
- building-union mean gap: **634/21 days**;
- SITE_A 2026/2025 equal-period count ratio: **9/7**;
- SITE_A relative count change: **2/7**, or **200/7%**;
- cross-resident ETA-date Jaccard: **10/11**;
- planned-window mean: **13/3 hours**.

When a rational value has no terminating decimal expansion, decimal output is explicitly labeled as rounded presentation only. The fraction is canonical.

The exact-analysis script also computes event-bounded normalizations such as `interval_count / elapsed_days × 30` or the same quantity multiplied by the arithmetic mean Gregorian month. Those are mathematical normalizations of the observed inter-arrival sequence, **not complete-observation incidence rates**.

## 7. Cross-resident corroboration

In the overlapping emergency period from 2025-12-06 through 2026-08-06, SITE_A and SITE_B share ten emergency restoration-ETA dates out of eleven unique dates in their union. All ten shared curated groups have matching ETA-time sets to the minute.

The exact Jaccard similarity of the unique ETA-date sets is **10/11**.

This is strong **cross-resident corroboration for the same building**. It is not evidence of correlation between two service points and does not establish feeder, transformer, substation or network topology.

## 8. Comparisons over time

Comparisons should use the same evidence source on both sides.

The equal-period comparison uses SITE_A only:

- 2025-01-01 through 2025-08-06: **7** emergency ETA-date groups;
- 2026-01-01 through 2026-08-06: **9** groups;
- exact count ratio: **9/7**;
- exact relative change: **2/7**;
- exact percentage change: **200/7%** (28.571429% rounded to six decimal places).

Because SITE_A is confirmed as the same Orkhevi building, the series is geographically relevant to the building. It still must not be described as a complete building-wide physical-outage rate because notification completeness and event identity remain uncertain.

No p-value or confidence interval is reported.

## 9. Gap, union and cluster analysis

For SITE_A, 21 emergency groups from 2024-11-10 through 2026-08-06 produce 20 consecutive inter-arrival intervals over exactly 634 elapsed days, giving an exact mean notification gap of **317/10 days**.

SITE_B contains 11 emergency groups from 2025-12-06 through 2026-08-06: 10 intervals over 243 elapsed days, exact mean **243/10 days**.

The deduplicated building-level union contains 22 curated emergency groups over the 634-day first-to-last span: 21 intervals, exact mean **634/21 days**. This union is **not** the preferred rate series because source ascertainment changes after SITE_B begins.

The 4–6 August 2026 feature in SITE_B supports only:

> Three emergency SMS notification groups in the repository-owner archive for the same building carried restoration-ETA dates on three consecutive calendar dates.

Without receipt timestamps and confirmed restorations between messages, this is not elevated to “three distinct outages on three consecutive days.”

## 10. Planned-work windows

Scheduled-window hours describe what notices announced, not measured downtime.

For the current nine planned groups without a cancellation signal in the same curated group:

- exact total announced window time: **39 hours**;
- exact mean: **13/3 hours = 4 h 20 min**;
- exact median: **4 hours**.

The undated SITE_A update saying planned-work completion moved to 16:00 is not silently attached to the 2025-11-02 explicit 11:00–14:00 notice for numeric totals.

## 11. Independent WBES Tbilisi benchmark

The repository preserves selected published/display values from the **World Bank Enterprise Surveys, Georgia 2023, Tbilisi location subgroup**:

- firms experiencing electrical outages: **31.8%**;
- average number of electrical outages in a **typical month**: **0.8**;
- firms identifying electricity as a major or very severe constraint: **38.6%**;
- firms owning or sharing a generator: **29.8%**.

The published `0.8` can be represented exactly as **4/5**, but only as the rational representation of that finite-precision display string. It does not recover a hidden unrounded weighted survey estimate.

Critically, WBES **“typical month” is a survey concept, not an arithmetic mean Gregorian calendar month**. Therefore:

- `0.8` is not converted to “one outage every N days”;
- resident mean-calendar-month inter-arrival normalizations are not treated as definition-identical to WBES;
- no headline `X×` or `Y%` Orkhevi-building-vs-Tbilisi physical-outage reliability ratio is reported.

For reproducibility/backward compatibility, machine-readable exact-analysis output retains the former arithmetic quotients between resident Gregorian-month normalizations and the WBES displayed value. They are explicitly marked **diagnostic arithmetic only / not a rate ratio** and are omitted from the human-readable conclusions.

## 12. Telasi public API semantics

The public endpoint observed is `POST https://app.telasi.ge/api/view/telasi/getPoweroutages`. Records are in `content.list` for the captured request shapes.

A public API row is a publication, not a physical outage incident. Text search for `ორხევი` is not a building-level or electrical-topology query.

`content.listCount` is a reported total, not proof that one response contains that many records. The `--all-pages` implementation performs two independent full pagination passes and requires both to be count-complete and mutually stable before corpus-wide negative claims are allowed.

The canonical focused Orkhevi fixture contains 17 publications, but that is a text-search publication set rather than a count of building outages.

## 13. Provenance

The canonical 2026-08-08 Orkhevi Telasi API response is preserved with byte counts and hashes under `data/telasi_api/raw/2026-08-08/`.

The WBES benchmark capture is documented under `data/benchmarks/` with its source endpoint, capture date, response size/SHA-256 and Actions artifact provenance. Live refreshes are written to ignored `artifacts/` first and are not automatically promoted to evidence.

## 14. Reliability metrics not supported by current evidence

Current evidence is insufficient for defensible calculation of:

- physical outage count;
- mean physical outage duration;
- SAIDI;
- SAIFI;
- CAIDI;
- MTTR.

Those require authoritative interruption start/restoration timestamps and a defined affected-customer population, or equivalent independent monitoring.

## 15. Reproducibility controls

- Core arithmetic uses exact rational fractions rather than binary floating-point values.
- `validate.py` checks resident source/group consistency, ETA sets, planned-window arithmetic, privacy rules and API snapshot hashes.
- `scripts/analyze.py` regenerates `reports/analysis-output.txt`.
- `scripts/analyze_exact_rates.py` regenerates `reports/exact-rate-analysis.txt` and can emit machine-readable JSON.
- `scripts/fetch_wbes_tbilisi.py` can refresh the independent Tbilisi benchmark into ignored runtime artifacts for review.
- GitHub Actions is configured to detect drift in committed generated resident/report outputs.
