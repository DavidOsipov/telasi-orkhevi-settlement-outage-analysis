# Methodology audit — 2026-08-08

This file records material corrections made after adversarial review.

## Critical corrections

1. **Event/date conflation removed.**
   The old `events.csv` forced one row per calendar date and described the table as event-level. It has been replaced with message-level `notifications.csv` and curated `notification_groups.csv`.

2. **Emergency date semantics corrected.**
   Emergency SMS dates are restoration-ETA dates, not outage-start dates.

3. **“Lower bound on outages” claim removed.**
   Missing SMS can undercount; repeated/updated SMS can overcount. Bias direction is not known.

4. **Year-over-year comparison fixed.**
   The old 7-vs-10 comparison mixed one-site 2025 coverage with a two-site 2026 union. The corrected descriptive same-source comparison is SITE_A: 7 vs 9.

5. **Inferential p-value and confidence interval removed.**
   The old Poisson/binomial-style inference assumed a sampling/event model not justified by this retrospective SMS record.

6. **Sliding-window boundary bug fixed.**
   The old `max_window()` could report windows extending beyond the last data date. New analysis evaluates only fully contained calendar windows.

7. **Planned-work extension uncertainty preserved.**
   An undated “completion moved to 16:00” SMS is no longer silently attached to 2025-11-02 for numeric totals.

8. **28 Nov cancellation scope corrected.**
   The dataset records an explicit cancellation at SITE_B. It no longer claims that a cancellation SMS was received at SITE_A.

9. **Source provenance renamed.**
   `data/raw/` became `data/source_transcripts/` because the public files are redacted text transcripts without original SMS metadata.

10. **Geographic scope weakened appropriately.**
    SITE_B is the primary Orkhevi point. SITE_A's exact property/location mapping is not publicly asserted until privately confirmed.

11. **MIT licensing scope clarified.**
    Third-party SMS transcript text is excluded from the repository-owner MIT grant.
