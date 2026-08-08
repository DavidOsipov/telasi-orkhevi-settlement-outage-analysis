# Scope

## Geographic scope

The repository is centered on **Orkhevi Settlement (ორხევის დასახლება), Samgori District, Tbilisi, Georgia**.

Canonical place identifier:

- Wikidata: `Q130437988`

`SITE_B` is the primary service point associated with the Orkhevi analysis.

`SITE_A` is a neighbor-supplied corroborating longitudinal series. The resident explicitly warned that she receives Telasi SMS for more than one property in different places. The supplied transcript contains one pseudonymized subscriber number, and its exact property/location mapping is not published.

Therefore SITE_A's pre-overlap history and its 7→9 equal-period comparison must not be presented as Orkhevi-specific unless the private subscriber-to-property mapping is confirmed.

## What the resident evidence supports

The supplied records show repeated electricity-interruption notifications affecting the primary Orkhevi service point and a strongly correlated second service point during the overlap period.

The overlap is consistent with both points repeatedly being included in the same affected network scope. The public evidence does not prove exact feeder/transformer/substation topology.

A defensible formulation is:

> The dataset documents repeated Telasi electricity-interruption notifications at an Orkhevi service point, corroborated across much of the overlapping period by a second strongly correlated service point.

For SITE_B, the supplied emergency ETA-date series contains 11 groups from 2025-12-06 through 2026-08-06. Ten consecutive inter-arrival intervals span exactly 243 elapsed days, giving an exact mean notification-group gap of `243/10 = 24.3` days. This is a descriptive property of the supplied notification anchors, not a proven physical-outage recurrence rate.

## Telasi API geographic scope

Searching Telasi's public API for the Georgian substring `ორხევი` is a **text query**, not a network-topology query.

Returned publications can mention:

- Orkhevi Settlement;
- Orkhevi industrial zone;
- Orkhevi-named exits/roads;
- streets or locations described in broader Orkhevi context.

Therefore the canonical 17-hit API snapshot is contextual/publication evidence and cannot be translated directly into 17 SITE_B outages or 17 settlement-wide outages.

## Independent benchmark scope

The WBES benchmark is **Tbilisi-wide business-establishment survey context for 2023**, not household/service-point monitoring and not an Orkhevi sample.

The captured WBES values include `31.8%` of firms experiencing electrical outages and `0.8` average outages in a **typical month**. Those values are useful independent context, but they are not definition-identical to the SITE_B restoration-ETA notification series.

In particular, WBES “typical month” is not treated as an arithmetic mean calendar month. The repository therefore does not convert `0.8` into “one outage every N days” and does not claim a direct `X×` or `Y%` Orkhevi-vs-Tbilisi reliability difference.

## Time scope

The combined resident source-record anchor span is **2024-11-10 through 2026-08-06**.

This is a span of supplied scheduled dates/restoration-ETA dates, not a proven complete continuous observation window.

The primary SITE_B supplied record begins later than SITE_A. That coverage difference must be respected in time comparisons.

The Telasi API snapshots and retained WBES benchmark capture are point-in-time captures made on **2026-08-08**. Their underlying source periods differ: the resident SMS record is 2024–2026, the canonical Telasi API material is a 2026 capture of public publications, and the WBES benchmark refers to the **Georgia 2023** survey.

## External grid context

Nationwide transmission-system events are stored separately in `data/external_context.csv`. They are contextual events, not local Telasi notification groups, and are not automatically treated as causes of local Orkhevi notifications.
