# Methodology

## 1. Evidence model

The repository separates evidence layers that must not be silently conflated:

1. **Resident source message** — one redacted SMS text block supplied by a resident.
2. **Resident notification group** — a manually reviewed grouping of one or more resident SMS messages that appear to concern the same scheduled date or emergency restoration-ETA date.
3. **Telasi public publication** — one website/API publication exposed by Telasi's public system.
4. **Physical outage incident** — an actual interruption of electricity supply.
5. **External/system context** — regulator or transmission-system information stored separately.

The repository preserves evidence for layers 1–3 and contextual sources for layer 5. It does not have enough metadata to identify layer 4 reliably in every case.

## 2. Resident-source identity

`SITE_A` and `SITE_B` are stable legacy identifiers, but they **do not represent two geographic sites**.

- `SITE_A` = neighbor resident SMS archive for the same Orkhevi building; supplied history begins in 2024.
- `SITE_B` = repository-owner resident SMS archive for that same building; supplied history begins in 2025.

The exact address, apartment numbers and subscriber/account numbers are not public.

The neighbor may receive Telasi SMS for other properties generally, but the user clarified on 2026-08-08 that the pseudonymized `SITE_A` transcript in this repository concerns the **same building** as `SITE_B`.

The legacy CSV column name `evidence_sites` is therefore semantically an **evidence-source identifier set** for this dataset. It is retained to avoid unnecessary identifier/schema churn.

## 3. Meaning of resident SMS dates

For emergency SMS, the Telasi wording describes the date/time as the **estimated restoration time** (`energomomaragebis agdgenis savaraudo droa`). Therefore emergency `anchor_date` is `restoration_eta_date`; it is not a verified outage-start date and an ETA is not an actual restoration timestamp.

For planned-work messages, the anchor date is the explicitly scheduled interruption date.

## 4. Grouping, identifiers and duplicates

Exact duplicate SMS messages remain present in `notifications.csv` and can be grouped together in `notification_groups.csv`.

Same-day ETA messages may represent one incident with a revised ETA, multiple incidents on the same day, or duplicated delivery. Ambiguity is preserved when the evidence cannot distinguish these.

Examples:

- 2025-06-28: ETA 01:18 and 17:43, `incident_count_min=1`, `incident_count_max=2`;
- 2026-01-22: ETA 12:00 and 20:00 in both resident archives;
- 2026-04-07: ETA 19:33 and 22:29 in both archives, plus an exact duplicate 22:29 SMS in SITE_A.

Group IDs use `GYYYYMMDD-XNN`, where `X` is `E`, `S` or `P`. Different groups are not automatically distinct physical incidents.

## 5. Completeness and ascertainment

The resident material is a retrospective SMS archive, not a prospectively monitored outage sensor.

Known limitations include missing SMS, absent receipt timestamps, absent actual restoration timestamps, and multiple notifications for one physical incident.

There is an additional source-coverage issue: `SITE_A` begins in 2024 while `SITE_B` begins in 2025. A building-level union of both archives is useful for preserving all known notification groups, but its **ascertainment changes over time** because the later period has two resident sources instead of one.

Therefore:

- the **longest single-source SITE_A series** is preferred for longitudinal rate normalization;
- the building union is secondary/contextual;
- the shorter SITE_B series is useful for recent clustering but is not the preferred long-run benchmark.

## 6. Cross-resident corroboration

In the overlapping emergency period from 2025-12-06 through 2026-08-06, SITE_A and SITE_B share ten emergency restoration-ETA dates out of eleven unique dates in their union. All ten shared curated groups have matching ETA-time sets to the minute.

This is strong **cross-resident corroboration for the same building**. It is not evidence of correlation between two service points and does not establish feeder, transformer, substation or network topology.

## 7. Comparisons over time

Comparisons should use the same evidence source on both sides.

The equal-period comparison uses SITE_A only:

- 2025-01-01 through 2025-08-06: 7 emergency ETA-date groups;
- 2026-01-01 through 2026-08-06: 9 groups;
- exact count ratio: `9/7`;
- exact relative change: `2/7`, or `200/7%`.

Because SITE_A is now confirmed as this Orkhevi building, the series is geographically relevant to the building. It still must not be described as a complete building-wide physical-outage rate because notification completeness and event identity remain uncertain.

No p-value or confidence interval is reported.

## 8. Gap, union and cluster analysis

For the longest single resident archive, SITE_A contains 21 emergency groups from 2024-11-10 through 2026-08-06: 20 inter-arrival intervals over exactly 634 elapsed days, giving an exact mean notification gap of `634/20 = 317/10 = 31.7` days.

SITE_B contains 11 emergency groups from 2025-12-06 through 2026-08-06: 10 intervals over 243 elapsed days, exact mean `243/10 = 24.3` days.

The deduplicated building-level union contains 22 curated emergency groups over the same 634-day first-to-last span: 21 inter-arrival intervals, exact mean `634/21` days. This union is **not** the preferred rate series because source ascertainment changes after SITE_B begins.

The 4–6 August 2026 feature in SITE_B supports only:

> Three emergency SMS notification groups in the repository-owner archive for the same building carried restoration-ETA dates on three consecutive calendar dates.

Without receipt timestamps and confirmed restorations between messages, this is not elevated to “three distinct outages on three consecutive days.”

## 9. Planned-work windows

Scheduled-window hours describe what notices announced, not measured downtime.

For the current nine planned groups without a cancellation signal in the same curated group, explicit announced windows total exactly 39 h, mean `13/3` h and median 4 h.

## 10. Independent Tbilisi benchmark

The World Bank Enterprise Surveys 2023 Tbilisi subgroup publishes `0.8` electrical outages in a typical month. The exact rational representation of that **displayed decimal string** is `4/5`; it is not the hidden unrounded weighted survey estimate.

The preferred comparison uses the longest single-source SITE_A series. With the exact mean Gregorian month `48699/1600` days, SITE_A's event-bounded inter-arrival normalization is:

- `48699/50720` notification groups per mean Gregorian month;
- ratio to displayed WBES `4/5`: `48699/40576`;
- exact relative excess: `203075/10144%`.

This is a mathematically exact transformation of the declared notification series and displayed WBES value, but **not** a statistically rigorous Orkhevi-building-vs-Tbilisi physical-outage reliability ratio. The source metrics, populations, years, completeness and event definitions differ.

The building-union and SITE_B comparisons are retained only as secondary diagnostics.

## 11. Telasi public API semantics

The public endpoint observed is `POST https://app.telasi.ge/api/view/telasi/getPoweroutages`. Records are in `content.list` for the captured request shapes.

A public API row is a publication, not a physical outage incident. Text search for `ორხევი` is not a building-level or electrical-topology query.

`content.listCount` is a reported total, not proof that one response contains that many records. The `--all-pages` implementation performs two independent full pagination passes and requires both to be count-complete and mutually stable before corpus-wide negative claims are allowed.

## 12. Reliability metrics not supported by current evidence

Current evidence is insufficient for defensible calculation of physical outage count, mean physical outage duration, SAIDI, SAIFI, CAIDI or MTTR. Those require authoritative interruption start/restoration timestamps and a defined affected-customer population, or equivalent independent monitoring.

## 13. Reproducibility controls

- Core arithmetic uses exact rational fractions rather than binary floating-point values.
- `validate.py` checks resident source/group consistency, ETA sets, planned-window arithmetic, privacy rules and API snapshot hashes.
- Unit tests pin the same-building source semantics and exact benchmark fractions.
- `scripts/analyze.py` and `scripts/analyze_exact_rates.py` regenerate committed reports.
- GitHub Actions fails if regenerated derived/report files differ from committed versions.
