# Methodology

## Unit of analysis

The primary unit is an **SMS-recorded interruption date/event**, not an official SAIFI/SAIDI event.

The source material does not contain reliable SMS receipt timestamps or confirmed restoration timestamps.
Therefore this repository does **not** claim to measure:

- actual outage duration;
- SAIDI;
- SAIFI;
- CAIDI;
- MTTR;
- complete outage frequency.

The event counts are a **lower bound**, because outages may occur without an SMS.

## Classification

- `emergency`: SMS contains `avariuli gamortvis` or a direct emergency cause such as high-voltage cable damage.
- `network_switching`: supply interruption attributed to `qselshi gadartvis` (network switching). It is kept separate from emergency outages.
- `planned`: advance notice of urgent/planned work.
- `cancelled`: a planned interruption explicitly cancelled/postponed.

## Deduplication

Repeated SMS on the same event date are merged when they look like revised ETAs or exact duplicates.

Examples:
- 2026-01-22: 12:00 -> 20:00, later message names high-voltage cable damage: one incident.
- 2026-04-07: 19:33 -> 22:29, plus an exact duplicate 22:29 at SITE_A: one incident.
- 2025-06-28: 01:18 and 17:43. This is ambiguous. The conservative dataset counts one emergency date and stores `possible_episodes=1-2`.

## Privacy

Subscriber/account numbers are not published. Two stable pseudonyms are used:

- `SITE_A`
- `SITE_B`

The private mapping should be kept outside the public repository.

## Cross-site corroboration

From the overlapping record in late 2025 through 2026, SITE_A's emergency dates are a subset of SITE_B's supplied emergency dates, and shared events have matching ETAs to the minute. This supports treating them as evidence of a common upstream distribution fault domain, while **not** proving that both services are on the same feeder or transformer.

## Statistical caution

A same-period comparison (1 Jan-6 Aug) gives 7 emergency dates in 2025 and 10 in 2026. The rate ratio is about 1.43, but the sample is too small to establish a statistically significant year-over-year increase.

The unusually dense 4-6 August 2026 run is a real descriptive feature of this record, but any p-value selected after seeing the cluster would suffer from post-selection bias. It should be presented as a cluster in the observed record, not as proof of a specific cause.
