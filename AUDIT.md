# Methodology audit — 2026-08-08

This file records material corrections made during adversarial review and the later API/reproducibility hardening pass.

## Initial critical corrections

1. **Event/date conflation removed.** Old `events.csv` forced one row per calendar date and described it as event-level. It was replaced with message-level `notifications.csv` and curated `notification_groups.csv`.
2. **Emergency date semantics corrected.** Emergency SMS dates are restoration-ETA dates, not outage-start dates.
3. **“Lower bound on outages” claim removed.** Missing SMS can undercount while updates/duplicates can overcount.
4. **Year-over-year comparison fixed.** The invalid mixed-source 7-vs-10 comparison was replaced with same-source SITE_A 7-vs-9 (+28.6% descriptive only).
5. **Unsupported p-value/confidence interval removed.** The data-generating model is not established.
6. **Sliding-window boundary bug fixed.** Windows are evaluated only when fully contained in the supplied anchor span.
7. **Planned-work extension uncertainty preserved.** The undated “moved to 16:00” SMS is not silently attached to 2025-11-02.
8. **28 Nov cancellation scope corrected.** Cancellation is explicit at SITE_B only.
9. **Source provenance renamed.** Redacted transcripts are not described as raw phone evidence.
10. **Geographic scope weakened appropriately.** SITE_A's exact property mapping is not publicly asserted.
11. **MIT licensing scope clarified.** Third-party source text is excluded from the repository-owner MIT grant.

## API/reproducibility hardening corrections

12. **Public API records located correctly.** `getPoweroutages` records are under `content.list`; `api.list` is empty for captured request shapes.
13. **`getMtData` role corrected.** It provides page/Nuxt metadata, not the outage publication body.
14. **Unicode/cURL failure documented.** Georgian `searchText` was observed being mangled during Copy-as-cURL → Postman import; the client sends UTF-8 JSON directly.
15. **False complete-corpus assumption removed.** An exploratory response reported `content.listCount=889` but returned only 100 page-1 records. No preserved 889-publication snapshot is claimed.
16. **Real pagination implemented.** `--all-pages` follows pages, detects effective server page size, preserves raw pages and fails if unique fetched count does not equal the API-reported total.
17. **Corpus-wide negative ETA claims gated on completeness.** Exact positive matches are valid on partial data; “no match in the corpus” requires complete-fetch metadata.
18. **Canonical API snapshot cryptographically validated.** The in-repo Orkhevi response has byte counts/SHA-256/Git-blob hashes and is reconstructed offline; exploratory probe observations retain artifact provenance plus response size/SHA-256 without duplicating bulky payloads.
19. **Exploratory probe-summary bug documented.** The old probe printed zeros because it inspected `api.*`; raw `content.*` responses are authoritative for that capture.
20. **Date-only group-ID limitation removed.** IDs now include category and sequence (`GYYYYMMDD-XNN`) while old IDs remain as `legacy_group_id`.
21. **Window counting made group-safe.** Cluster analysis counts group rows, not `set(date)`, so multiple same-day groups will not collapse.
22. **Combined “30.19 days” recurrence headline removed.** Gaps are reported per site as notification ETA-date gaps and explicitly cannot be restated as outage recurrence.
23. **SITE_A geography caveat attached to +28.6%.** The longitudinal change is not described as an Orkhevi-wide rate change.
24. **Planned-window arithmetic validated.** Stored group windows are checked against supporting messages and recomputed durations.
25. **Byte-stable CSV generation added.** Derived CSV writers use explicit LF line endings.
26. **Generated-report drift fixed.** Publish scripts regenerate `reports/analysis-output.txt`; CI fails if generated derived/report files differ from committed versions.
27. **API regression coverage added.** Offline fixture tests cover taxonomy/geographic classification, spaced-digit ETA parsing, source-side year errors, focused-snapshot matching and mocked pagination under a server-side page cap.
28. **Transient live API outputs ignored.** `artifacts/` is Git-ignored to avoid accidentally committing unreviewed live responses.
29. **Exploratory API provenance retained without repository bloat.** Page-1/list/search probes are referenced by Actions run/artifact ID and response SHA-256/count metadata; browser netlogs and bulky duplicate probe payloads remain intentionally unpublished.
