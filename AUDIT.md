# Methodology audit — through 2026-08-09

This file records material corrections made during adversarial review and later reproducibility/documentation re-audits. Earlier corrections are historical; later entries supersede earlier assumptions where explicitly stated.

## Initial evidence-model corrections

1. **Event/date conflation removed.** Old `events.csv` forced one row per calendar date and described it as event-level. It was replaced with message-level `notifications.csv` and curated `notification_groups.csv`.
2. **Emergency date semantics corrected.** Emergency SMS dates are restoration-ETA dates, not outage-start dates.
3. **“Lower bound on outages” claim removed.** Missing SMS can undercount while updates/duplicates can overcount.
4. **Year-over-year comparison fixed.** The invalid mixed-source comparison was replaced with same-source SITE_A 7-vs-9; the exact relative change is `2/7`, or `200/7%`.
5. **Unsupported p-value/confidence interval removed.** The data-generating model is not established.
6. **Sliding-window boundary bug fixed.** Windows are evaluated only when fully contained in the supplied anchor span.
7. **Planned-work extension uncertainty preserved.** The undated “moved to 16:00” SMS is not silently attached to 2025-11-02.
8. **28 Nov cancellation scope corrected.** Cancellation is explicit in the SITE_B archive only.
9. **Redacted transcripts are not called raw phone evidence.**
10. **Licensing scope clarified.** Third-party source text/data are excluded from the repository-owner MIT grant where applicable.

## Telasi API/reproducibility hardening

11. **Public API records located correctly.** `getPoweroutages` records are under `content.list`; `api.list` is empty for captured request shapes.
12. **`getMtData` role corrected.** It provides page/Nuxt metadata, not the outage publication body.
13. **Unicode/cURL failure documented.** Georgian `searchText` was observed being mangled during Copy-as-cURL → Postman import; the client sends UTF-8 JSON directly.
14. **False complete-corpus assumption removed.** An exploratory response reported `content.listCount=889` but returned only page-1 records. No preserved 889-publication snapshot is claimed.
15. **Real pagination implemented and hardened.** `--all-pages` performs two independently count-complete passes and requires stable total, identities and contents.
16. **Corpus-wide negative ETA claims gated on completeness.** Positive exact matches can corroborate partial data; global negative claims require the completeness/stability gate.
17. **Canonical API snapshot cryptographically validated.** The in-repo Orkhevi response is reconstructible with byte counts and hashes.
18. **Exploratory probe-summary bug documented.** The old console summary inspected `api.*`; raw `content.*` responses are authoritative for that capture.
19. **Conflicting duplicate publication IDs fail completeness.**
20. **Transient live API outputs are ignored by Git until deliberately reviewed.**

## Grouping/reproducibility hardening

21. **Date-only group-ID limitation removed.** IDs include category and sequence (`GYYYYMMDD-XNN`); old date-only IDs remain traceability metadata and need not be unique.
22. **Window counting made group-safe.** Multiple same-day groups are not silently collapsed.
23. **Planned-window arithmetic validated against supporting messages.**
24. **Derived CSV/report outputs use deterministic line endings and regeneration paths.**
25. **Comparison completeness is recomputed rather than trusting a metadata boolean alone.**

## Source-identity correction: one building, two resident archives

26. **SITE_A/SITE_B geographic interpretation superseded.** The IDs do not represent two sites or two buildings.
27. **Current identity:** SITE_A is the neighbor resident SMS archive and SITE_B is the repository-owner archive for the **same Orkhevi residential building**.
28. **`evidence_sites` is a legacy column name.** In this resident dataset it contains evidence-source IDs, not geographic-site assertions.
29. **Cross-resident overlap reinterpreted.** The `10/11` Jaccard is corroboration between two resident archives for the same building, not two-site correlation or network-topology evidence.
30. **Source ascertainment made explicit.** SITE_A begins earlier; the building-level union changes ascertainment when SITE_B begins. SITE_A is the preferred long single-source series for longitudinal normalization; the union is secondary/contextual.
31. **Same-building geography restores relevance of SITE_A 7→9.** It is an Orkhevi-building resident series, but still not a complete physical-outage rate.

## Exact-arithmetic hardening

32. **Core descriptive arithmetic moved to rational fractions.** Binary floating point is not the canonical representation for mean gaps, count ratios, Jaccard or planned-window means.
33. **SITE_A:** 21 emergency groups → 20 consecutive intervals over 634 days → exact mean gap `317/10` days.
34. **SITE_B:** 11 emergency groups → 10 intervals over 243 days → exact mean gap `243/10` days; median `45/2` days.
35. **Building union:** 22 emergency groups → 21 intervals over 634 days → exact mean gap `634/21` days, with changing-ascertainment warning.
36. **SITE_A equal-period comparison:** ratio `9/7`, relative change `2/7`, percentage change `200/7%`.
37. **Cross-resident overlap:** exact Jaccard `10/11`.
38. **Planned windows:** 9 selected groups, total 39 hours, mean `13/3` hours, median 4 hours.
39. **Relative-change label corrected.** The dimensionless change `2/7` is now separate from percentage change `200/7%`; the old label conflated the two forms.

## Independent WBES benchmark hardening

40. **WBES Tbilisi 2023 capture provenance preserved.** Source endpoint, capture date, raw response size/SHA-256 and Actions artifact provenance are recorded.
41. **Published decimals are finite-precision source values.** `0.8 → 4/5` is exact only as a representation of the displayed decimal string, not as recovery of an unrounded survey estimate.
42. **“Typical month” semantics corrected.** WBES `0.8 outages in a typical month` is not a fixed arithmetic mean-calendar-month rate.
43. **Invalid direct reliability ratios removed from human conclusions.** Earlier arithmetic comparisons such as SITE_A/WBES `48699/40576`, union/WBES `1022679/811520`, and SITE_B/WBES `5411/3456` are no longer reported as `X×` or `Y%` reliability differences.
44. **Diagnostic quotients retained only in machine-readable output.** They are explicitly tagged as diagnostic arithmetic / not a rate ratio for reproducibility and backward compatibility.
45. **Defensible WBES conclusions narrowed to published context.** Current human-readable benchmark values are `31.8%` firms experiencing outages, `0.8` average outages in a typical month, `38.6%` electricity major/very severe constraint, and `29.8%` owning/sharing a generator, with non-comparability cautions.

## Documentation re-audit — 2026-08-09

46. **README, METHODOLOGY, PROVENANCE, SCOPE and Russian statistical summary synchronized with the same-building source model and exact arithmetic.**
47. **Human exact-rate report synchronized with WBES semantics.** No direct resident-series/WBES reliability ratio remains in the human-readable output.
48. **Benchmark documentation added.** `data/benchmarks/README.md` defines provenance, precision and “typical month” rules.
49. **Privacy and licensing documentation expanded to cover external benchmark material and to avoid publication of respondent-level WBES microdata without separate review.**
50. **Telasi API documentation re-read and retained.** Its 17-hit focused fixture, 13/4 observed taxonomy split, 889-vs-page-1 warning, ETA semantics and two-pass pagination cautions remain compatible with the current statistical model and required no statistical revision in this pass.
