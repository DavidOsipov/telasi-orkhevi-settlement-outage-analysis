# Methodology

## 1. Evidence model

The repository separates evidence layers that must not be silently conflated:

1. **Resident source message** — one redacted SMS text block supplied by a resident.
2. **Resident notification group** — a manually reviewed grouping of one or more resident SMS messages that appear to concern the same scheduled date or emergency restoration-ETA date.
3. **Telasi public publication** — one website/API publication exposed by Telasi's public system. It can describe an affected area and an ETA/window but is not automatically subscriber-specific.
4. **Physical outage incident** — an actual interruption of electricity supply.
5. **Independent external benchmark/context** — regulator, transmission-system or independent survey information kept separate from the local evidence layers.

The repository directly preserves evidence for layers 1–3 and contextual/benchmark sources for layer 5. It does **not** have enough metadata to identify layer 4 reliably in every case.

Accordingly, neither `notification_groups.csv` nor Telasi `content.list` is treated as an authoritative outage-event ledger.

## 2. Meaning of resident SMS dates

For emergency SMS, the Telasi wording describes the date/time as the **estimated restoration time** (`energomomaragebis agdgenis savaraudo droa`).

Therefore:

- emergency `anchor_date` is `restoration_eta_date`;
- it is not a verified outage-start date;
- the interruption may have begun on a different calendar date;
- an ETA is not an actual restoration timestamp.

For planned-work messages, the anchor date is the explicitly scheduled interruption date.

## 3. Resident message classification

Message-level classification is based on wording in the supplied transliteration:

- `emergency`: contains `avariuli gamortvis` or a direct emergency cause such as high-voltage cable damage;
- `network_switching`: interruption attributed to `qselshi gadartvis`;
- `planned_notice`: advance notice with a scheduled interruption window;
- `planned_cancellation`: explicit cancellation/postponement;
- `planned_update`: update about planned-work completion without a complete standalone date/window.

`network_switching` remains separate from `emergency`.

## 4. Grouping, identifiers and duplicates

Exact duplicate SMS messages remain present in `notifications.csv` and can be grouped together in `notification_groups.csv`.

Same-day ETA messages may represent:

- one incident with a revised ETA;
- multiple incidents on the same day;
- duplicated notification delivery.

When the evidence cannot distinguish these, ambiguity is preserved.

Examples:

- 2025-06-28: ETA 01:18 and 17:43, `incident_count_min=1`, `incident_count_max=2`;
- 2026-01-22: ETA 12:00 and 20:00 at both sites; update ordering is plausible but receipt timestamps are absent;
- 2026-04-07: ETA 19:33 and 22:29 at both sites, plus an exact duplicate 22:29 SMS at SITE_A.

Group IDs use `GYYYYMMDD-XNN`, where `X` is `E` (emergency), `S` (network switching) or `P` (planned). This prevents the data model from reintroducing the false assumption “one calendar date = one group.” The old date-only value is preserved as `legacy_group_id` for traceability; because it is date-only, it is **not required to be unique** if multiple groups share a date.

Different groups are not automatically distinct physical incidents.

## 5. Completeness and bias

The resident material is a retrospective SMS transcript, not a prospectively monitored outage sensor.

Known limitations include:

- real outages can occur without an SMS;
- messages can be missing from the supplied archive;
- SMS receipt timestamps are absent;
- actual restoration timestamps are absent;
- one incident can generate multiple messages/ETA updates.

Bias is therefore not guaranteed to be one-directional. Missing notifications can undercount incidents, while unrecognized updates/duplicates can overcount them. Notification-group count is not described as a proven lower or upper bound on physical outage count.

## 6. Exact arithmetic policy

Core descriptive arithmetic is represented with reduced rational fractions rather than binary floating point.

Examples from the current data:

- SITE_B mean emergency ETA-date group gap: **243/10 days = 24.3 days**;
- SITE_B median gap: **45/2 days = 22.5 days**;
- SITE_A mean gap: **317/10 days = 31.7 days**;
- SITE_A 2026/2025 equal-period count ratio: **9/7**;
- SITE_A relative count change: **2/7 = 200/7%**;
- cross-site ETA-date Jaccard: **10/11**;
- planned-window mean: **13/3 hours**.

When a rational value has no terminating decimal expansion, decimal output is explicitly labeled as rounded presentation only. The fraction is canonical.

`scripts/analyze_exact_rates.py` also reports standardized inter-arrival counts over a 30-day period or an arithmetic mean Gregorian calendar month. These are derived from the bounded inter-arrival sequence (`interval_count / elapsed_days`) and are **not observation-window incidence rates**.

## 7. Cross-site corroboration

In the overlapping emergency period from 2025-12-06 through 2026-08-06, SITE_A and SITE_B share ten emergency restoration-ETA dates, and all ten shared groups have matching ETA-time sets to the minute.

The exact Jaccard similarity of the unique ETA-date sets is **10/11**.

This is strong evidence that both service points repeatedly received notifications associated with the same affected scope. It is consistent with a shared upstream distribution-domain explanation.

It does **not** establish a specific feeder, transformer, substation, or exact topology. It also does not establish SITE_A's public location.

## 8. Comparisons over time

Comparisons must use the same evidence source on both sides.

The corrected equal-period comparison uses SITE_A only:

- 2025-01-01 through 2025-08-06: **7** emergency ETA-date groups;
- 2026-01-01 through 2026-08-06: **9** groups;
- exact count ratio: **9/7**;
- exact relative change: **2/7**, or **200/7%** (decimal rounded to six places: **28.571429%**).

This is not presented as a statistically established change in true outage rate because notification completeness, independence and stationarity are unknown.

Additionally, SITE_A's exact public property/location mapping remains unresolved. The 7→9 comparison is therefore a same-source longitudinal observation and must not be restated as an Orkhevi-wide rate change without privately confirming the mapping.

No p-value or confidence interval is reported.

## 9. Gap and cluster analysis

Gap summaries are calculated **separately per site** from emergency ETA-date notification groups. The combined stitched A/B series is not used as a headline “average recurrence” metric.

For SITE_B, 11 emergency groups span 243 elapsed days from the first to the last anchor, producing 10 consecutive gaps. The exact mean gap is therefore **243/10 days**. This is mathematically exact for the supplied anchors, but it is still a notification inter-arrival metric rather than a verified physical-outage recurrence interval.

Sliding-window cluster counts use only calendar windows fully contained within the supplied anchor span for the relevant site. The implementation counts **group rows**, not a set of dates, so multiple future groups on one date will not be silently collapsed.

The 4–6 August 2026 feature at SITE_B supports only the statement:

> Three emergency SMS notification groups at the same service point carried restoration-ETA dates on three consecutive calendar dates.

Without receipt timestamps and confirmed restorations between messages, this is not elevated to “three distinct outages on three consecutive days.”

## 10. Planned-work windows

Scheduled-window hours describe what notices announced, not measured downtime.

The undated SITE_A planned-work update saying completion moved to 16:00 is not silently attached to 2025-11-02 for numeric totals. The explicit 2025-11-02 notice remains 11:00–14:00 (3 h).

For the current nine planned groups without a cancellation signal in the same curated group:

- exact total announced window time: **39 hours**;
- exact mean: **13/3 hours = 4 h 20 min**;
- exact median: **4 hours**.

The validator recomputes every stored planned-window duration and checks it against the supporting message windows.

## 11. Independent WBES Tbilisi benchmark

The repository preserves published/display values from the **World Bank Enterprise Surveys, Georgia 2023, Tbilisi location subgroup**.

Current captured values include:

- firms experiencing electrical outages: **31.8%**;
- average number of electrical outages in a **typical month**: **0.8**;
- firms identifying electricity as a major or very severe constraint: **38.6%**;
- firms owning or sharing a generator: **29.8%**.

The published `0.8` can be represented exactly as the rational number **4/5**, but that is exact only for the displayed decimal string. It does not recover any hidden unrounded weighted survey estimate.

More importantly, WBES **“typical month” is a survey concept for the most common type of month regarding outages, not an arithmetic mean Gregorian calendar month**. Therefore:

- `0.8` is not converted to “one outage every N days”;
- the SITE_B mean gap is not directly inverted and compared as a definition-identical outage rate;
- no headline `X×` or `Y%` Orkhevi-vs-Tbilisi reliability ratio is reported.

The JSON output may retain a conditional arithmetic quotient between a SITE_B mean-Gregorian-month normalization and the displayed WBES value for reproducibility. That quotient is explicitly marked **diagnostic arithmetic only**, not a statistical reliability result.

## 12. Telasi public API semantics

The public endpoint observed is:

`POST https://app.telasi.ge/api/view/telasi/getPoweroutages`

For the captured request shapes, records are in `content.list`; the parallel `api.list` is empty.

Search mode and list/pagination mode are separate frontend request shapes. Georgian `searchText` must remain UTF-8; a Copy-as-cURL → Postman import was observed mangling it.

A public API row is a **publication**, not a physical outage incident. Text search for `ორხევი` is not an electrical-topology query.

For unplanned publications, `scripts/fetch_telasi_api.py` extracts the explicitly stated restoration ETA from `editor`. Parsed source values are preserved even when they appear internally inconsistent. Examples in the 2026-08-08 snapshot include publication timestamps later than the body ETA and a January 2026 publication whose body contains an ETA year of 2025.

### Pagination completeness

`content.listCount` is a reported total, not proof that one response contains that many records. An exploratory request on 2026-08-08 reported 889 but returned only 100 page-1 records.

The current `--all-pages` implementation therefore:

- performs **two independent full pagination passes**;
- preserves every raw page separately for each pass;
- follows page numbers until each pass reaches the API-reported total or fails closed;
- detects server-side `perPage` caps from actual returned page size;
- deduplicates by publication ID within each pass;
- records stop reasons and raw-page hashes;
- requires stable `listCount` within each pass;
- requires both passes to be count-complete;
- requires the two passes to agree on reported total, publication identity set, and full publication-record contents.

This is a conservative **two-pass stability check**, not proof of an atomic Telasi database snapshot. A corpus-wide negative statement such as “no exact API ETA match exists” is allowed only when those stability/completeness checks pass **and** the comparison script independently verifies that `records.csv`, its IDs, and fetch metadata are mutually consistent. Positive exact matches remain useful even with partial data.

## 13. Raw/source provenance

The canonical 17-hit Orkhevi response is preserved byte-for-byte under `data/telasi_api/raw/2026-08-08/` with byte counts, SHA-256 digests and Git blob SHA-1 values. Exploratory probe responses remain in the cited GitHub Actions artifact; their request shapes, byte lengths, SHA-256 hashes and parsed counts are retained in `MANIFEST.json`.

The WBES benchmark capture is documented under `data/benchmarks/` with the source endpoint, capture date, response byte count/SHA-256 and Actions artifact provenance.

`validate.py` reconstructs and verifies the canonical in-repo Telasi snapshot offline. `scripts/reconstruct_telasi_api_snapshot.py` provides a standalone cross-platform reconstruction path for that response. `scripts/fetch_wbes_tbilisi.py` provides the reproducible live WBES fetch/normalization path.

Browser netlogs are intentionally excluded because they can contain unrelated/private request metadata; relevant endpoint, payload and header semantics are documented separately.

## 14. Reliability metrics not supported by current evidence

Current evidence is insufficient for defensible calculation of:

- physical outage count;
- mean physical outage duration;
- SAIDI;
- SAIFI;
- CAIDI;
- MTTR.

Those require authoritative interruption start/restoration timestamps and a defined customer population, or equivalent independent monitoring.

## 15. Reproducibility controls

- CSV generation uses explicit LF line endings for byte-stable cross-platform output.
- `validate.py` rebuilds resident derived data and verifies group/source consistency, ETA sets, planned-window arithmetic, privacy rules and API snapshot hashes.
- `scripts/analyze.py --output reports/analysis-output.txt` regenerates the conservative descriptive report.
- `scripts/analyze_exact_rates.py --output-text reports/exact-rate-analysis.txt` regenerates the exact-fraction report.
- `scripts/fetch_wbes_tbilisi.py` can refresh the independent Tbilisi benchmark into ignored runtime artifacts for review.
- GitHub Actions is configured to detect drift in committed generated resident/report outputs.
