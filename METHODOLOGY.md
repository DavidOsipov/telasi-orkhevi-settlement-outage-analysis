# Methodology

## 1. Evidence model

This repository separates three layers that must not be conflated:

1. **Source transcript message** — one redacted SMS text block supplied by a resident.
2. **Notification group** — a manually reviewed grouping of one or more SMS messages that appear to refer to the same scheduled date or the same emergency restoration-ETA date.
3. **Outage incident** — a real interruption of electricity supply.

The repository directly contains evidence for layers 1 and 2. It does **not** have enough metadata to identify layer 3 reliably in every case.

Accordingly, `notification_groups.csv` is **not an outage-event log**.

## 2. Meaning of dates

For emergency SMS, the date/time in the Telasi text is described as the **estimated time of restoration** (`energomomaragebis agdgenis savaraudo droa`).

Therefore:

- an emergency `anchor_date` is a `restoration_eta_date`;
- it is **not** treated as a verified outage-start date;
- the repository does not claim that the interruption necessarily began on that same calendar date.

For planned-work messages, the anchor date is the explicitly scheduled interruption date.

## 3. Classification

Message-level classification is based on the wording in the supplied transliteration:

- `emergency`: contains `avariuli gamortvis` or an explicit emergency cause such as high-voltage cable damage;
- `network_switching`: interruption attributed to `qselshi gadartvis`;
- `planned_notice`: advance notice of work with a scheduled interruption window;
- `planned_cancellation`: explicit cancellation/postponement wording;
- `planned_update`: update about planned-work completion without a complete standalone date/window.

`network_switching` remains separate from `emergency`.

## 4. Grouping and duplicates

Exact duplicate SMS messages are preserved in `notifications.csv` and may be grouped together in `notification_groups.csv`.

Same-day ETA messages may represent:

- an updated ETA for one incident;
- more than one incident on the same day;
- duplicated notification delivery.

When the supplied evidence cannot distinguish these, the group is marked ambiguous.

Examples:

- 2025-06-28: ETA 01:18 and 17:43, `incident_count_min=1`, `incident_count_max=2`.
- 2026-01-22: ETA 12:00 and 20:00 at both sites. The later clock time may be a revised ETA, but receipt timestamps are absent.
- 2026-04-07: ETA 19:33 and 22:29 at both sites; SITE_A also contains an exact duplicate 22:29 SMS.

Different emergency anchor dates are kept as different **notification groups**, but they are not automatically asserted to be different physical outage incidents. A prolonged multi-day incident with repeated ETA updates cannot be excluded from transcript text alone.

## 5. Completeness and bias

The supplied material is a retrospective SMS transcript, not a prospectively monitored outage sensor.

Known incompleteness:

- some real outages may generate no SMS;
- messages may be missing from the supplied archive;
- SMS receipt timestamps are absent;
- actual restoration timestamps are absent.

Potential bias is therefore **not guaranteed to be one-directional**. Missing notifications can undercount outage incidents, while unrecognized updates or duplicates can overcount them.

The repository must not describe the notification-group count as a proven lower bound on the number of real outage incidents.

## 6. Cross-site corroboration

The two supplied series overlap strongly from late 2025 onward. Ten emergency restoration-ETA dates are shared by SITE_A and SITE_B, often with identical ETA times to the minute.

This is strong evidence that the two service points repeatedly received notifications associated with the same affected scope. It is consistent with a shared upstream distribution-domain explanation.

It does **not** prove a specific feeder, transformer, substation, or network topology. It also does not, by itself, prove the public location of SITE_A.

## 7. Comparisons over time

Comparisons must use the same evidence source on both sides.

The old comparison of 7 emergency groups in 2025 with 10 in 2026 mixed:

- SITE_A-only coverage in most of 2025; and
- the union of SITE_A and SITE_B in 2026.

That comparison was invalid because ascertainment changed.

The corrected descriptive comparison uses SITE_A only:

- 2025-01-01 through 2025-08-06: 7 emergency restoration-ETA groups;
- 2026-01-01 through 2026-08-06: 9 groups.

This is a descriptive +28.6% change in recorded groups. It is **not** presented as a statistically established change in true outage rate because notification completeness, independence, and stationarity are not established.

No p-value or confidence interval is reported for the current dataset.

## 8. Cluster analysis

Sliding-window cluster counts use only **complete calendar windows** contained in the supplied record span. Windows are never allowed to extend beyond the last supplied anchor date.

The notable 4-6 August 2026 pattern is evaluated at SITE_B itself: SITE_B has emergency notifications whose restoration ETAs fall on 4, 5, and 6 August.

This supports the descriptive statement:

> Three emergency SMS notification groups at the same service point carried restoration-ETA dates on three consecutive calendar days.

Without receipt timestamps and confirmed restorations between messages, the repository does not elevate that statement to “three distinct outage incidents on three consecutive days.”

## 9. Planned-work hours

Scheduled-window hours describe what the notice announced. They are not measured downtime.

The undated SITE_A planned-work update saying completion moved to 16:00 is not silently attached to 2025-11-02 for numeric totals. The explicit 2025-11-02 notice remains 11:00-14:00 (3 h); the possible association is documented separately.

## 10. Reliability metrics that cannot be calculated

This evidence is insufficient for official or defensible calculation of:

- SAIDI;
- SAIFI;
- CAIDI;
- MTTR;
- mean physical outage duration;
- complete physical outage count.

Those require authoritative interruption start/restoration timestamps and a defined customer population, or equivalent high-quality monitoring data.
