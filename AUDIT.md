# Methodology audit — through 2026-08-09

This file records material corrections made during adversarial review, API/reproducibility hardening, exact-arithmetic hardening, and the later documentation/statistical-conclusion re-audit.

## Initial critical corrections

1. **Event/date conflation removed.** Old `events.csv` forced one row per calendar date and described it as event-level. It was replaced with message-level `notifications.csv` and curated `notification_groups.csv`.
2. **Emergency date semantics corrected.** Emergency SMS dates are restoration-ETA dates, not outage-start dates.
3. **“Lower bound on outages” claim removed.** Missing SMS can undercount while updates/duplicates can overcount.
4. **Year-over-year comparison fixed.** The invalid mixed-source 7-vs-10 comparison was replaced with same-source SITE_A 7-vs-9. The exact relative count change is `2/7 = 200/7%`; decimal forms are presentation only.
5. **Unsupported p-value/confidence interval removed.** The data-generating model is not established.
6. **Sliding-window boundary bug fixed.** Windows are evaluated only when fully contained in the supplied anchor span.
7. **Planned-work extension uncertainty preserved.** The undated “moved to 16:00” SMS is not silently attached to 2025-11-02.
8. **28 Nov cancellation scope corrected.** Cancellation is explicit at SITE_B only.
9. **Source provenance renamed.** Redacted transcripts are not described as raw phone evidence.
10. **Geographic scope weakened appropriately.** SITE_A's exact property mapping is not publicly asserted.
11. **MIT licensing scope clarified.** Third-party source text/data are excluded from the repository-owner MIT grant where applicable.

## API/reproducibility hardening corrections

12. **Public API records located correctly.** `getPoweroutages` records are under `content.list`; `api.list` is empty for captured request shapes.
13. **`getMtData` role corrected.** It provides page/Nuxt metadata, not the outage publication body.
14. **Unicode/cURL failure documented.** Georgian `searchText` was observed being mangled during Copy-as-cURL → Postman import; the client sends UTF-8 JSON directly.
15. **False complete-corpus assumption removed.** An exploratory response reported `content.listCount=889` but returned only 100 page-1 records. No preserved 889-publication snapshot is claimed.
16. **Real pagination implemented.** `--all-pages` follows pages, detects effective server page size and preserves raw pages; the later second hardening pass strengthened this further to two-pass stability verification (see item 33).
17. **Corpus-wide negative ETA claims gated on completeness.** Exact positive matches are valid on partial data; “no match in the corpus” requires complete-fetch metadata.
18. **Canonical API snapshot cryptographically validated.** The in-repo Orkhevi response has byte counts/SHA-256/Git-blob hashes and is reconstructed offline; exploratory probe observations retain artifact provenance plus response size/SHA-256 without duplicating bulky payloads.
19. **Exploratory probe-summary bug documented.** The old probe printed zeros because it inspected `api.*`; raw `content.*` responses are authoritative for that capture.
20. **Date-only group-ID limitation removed.** IDs now include category and sequence (`GYYYYMMDD-XNN`) while old IDs remain as `legacy_group_id`.
21. **Window counting made group-safe.** Cluster analysis counts group rows, not `set(date)`, so multiple same-day groups will not collapse.
22. **Combined “30.19 days” recurrence headline removed.** Gaps are reported per site as notification ETA-date gaps and explicitly cannot be restated as outage recurrence.
23. **SITE_A geography caveat attached to the 7→9 comparison.** The longitudinal change is not described as an Orkhevi-wide rate change.
24. **Planned-window arithmetic validated.** Stored group windows are checked against supporting messages and recomputed durations.
25. **Byte-stable CSV generation added.** Derived CSV writers use explicit LF line endings.
26. **Generated-report drift fixed.** Publish/CI paths regenerate deterministic analytical outputs and detect committed drift.
27. **API regression coverage added.** Offline fixture coverage includes taxonomy/geographic classification, spaced-digit ETA parsing, source-side year errors, focused-snapshot matching and pagination edge cases.
28. **Transient live API outputs ignored.** `artifacts/` is Git-ignored to avoid accidentally committing unreviewed live responses.
29. **Exploratory API provenance retained without repository bloat.** Page-1/list/search probes are referenced by Actions run/artifact ID and response SHA-256/count metadata; browser netlogs and bulky duplicate probe payloads remain intentionally unpublished.

## Second hardening re-audit

30. **Legacy ID uniqueness contradiction removed.** `legacy_group_id` is now validated as the date-derived old identifier but is intentionally allowed to repeat when multiple groups share a date.
31. **Cross-site overlap labeling corrected.** Jaccard is explicitly a comparison of unique ETA-date sets; the exact value is `10/11`.
32. **Comparison completeness is recomputed.** `compare_telasi_api_sms.py` no longer trusts a metadata boolean alone; it verifies reported/fetched/CSV counts and unique publication IDs.
33. **Live pagination strengthened against page movement.** `--all-pages` requires two independently count-complete passes to agree on total, publication identities, and full record contents before global negative conclusions are allowed.
34. **Narrative-summary regression coverage added.** Current headline statistics are pinned to computed analysis values.
35. **Conflicting duplicate publication IDs rejected.** A pagination pass is not allowed to silently deduplicate the same publication ID when its contents differ across pages; such a pass fails completeness.

## Exact-arithmetic hardening

36. **Core descriptive arithmetic moved to rational fractions.** Binary floating point is no longer the canonical representation for mean gaps, count ratios, Jaccard or planned-window means.
37. **SITE_B inter-arrival arithmetic made explicit.** Eleven emergency ETA groups yield ten consecutive intervals spanning exactly 243 days, so the exact mean gap is `243/10` days and the median is `45/2` days.
38. **SITE_A equal-period change made exact.** `7→9` is ratio `9/7`, relative change `2/7`, or `200/7%`; `28.571429%` is explicitly rounded display text.
39. **Cross-site overlap made exact.** Jaccard is `10/11`; decimal `0.909090909091` is explicitly rounded display text.
40. **Planned-window mean made exact.** Nine selected windows total exactly 39 hours, mean `13/3` hours and median 4 hours.
41. **WBES values are preserved as source decimal strings.** For example, displayed `0.8` is represented as `4/5` only as the exact rational representation of the returned string, not as recovery of an unrounded survey estimate.
42. **Independent WBES provenance added.** The Tbilisi 2023 subgroup capture records source endpoint, capture date, response length/SHA-256 and Actions artifact provenance.

## Documentation/statistical-conclusion re-audit — 2026-08-09

43. **README/METHODOLOGY/PROVENANCE/SCOPE/PRIVACY/LICENSE documentation synchronized with the exact-analysis layer.** Old headline forms such as `+28.6%`, `0.909`, and `4.33 h` are no longer presented as canonical values where exact fractions are available.
44. **WBES “typical month” semantics corrected.** The survey concept is not an arithmetic mean Gregorian calendar month. Therefore published `0.8 outages in a typical month` is not converted into “one outage every N days.”
45. **Direct `1.56568× / +56.57%` Orkhevi-vs-Tbilisi reliability claim removed.** The quotient between SITE_B's mean-Gregorian-month inter-arrival normalization and WBES's typical-month indicator is retained, if at all, only as diagnostic arithmetic in machine-readable output and explicitly must not be reported as a reliability ratio.
46. **Independent benchmark conclusions narrowed.** Defensible WBES statements are the published Tbilisi values themselves (for example `31.8%` firms experiencing outages and `0.8` average outages in a typical month), plus the statement that the benchmark and resident SMS series are not definition-identical.
47. **SITE_B headline wording tightened.** `243/10 = 24.3 days` is the exact mean gap between the ten consecutive emergency ETA-date notification-group intervals in the supplied series, not “a physical outage every 24.3 days.”
48. **Reproducibility documentation updated.** Both `reports/analysis-output.txt` and `reports/exact-rate-analysis.txt`, plus the WBES refresh script and benchmark data directory, are now documented as first-class repository components.
