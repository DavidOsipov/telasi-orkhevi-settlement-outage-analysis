# Scope

## Geographic scope

The repository is centered on **one residential building in Orkhevi Settlement (ორხევის დასახლება), Samgori District, Tbilisi, Georgia**.

Canonical place identifier:

- Wikidata: `Q130437988`

`SITE_A` and `SITE_B` are retained as stable legacy identifiers, but they are **not two geographic sites**.

- `SITE_A` = the neighbor's resident SMS archive for this building; supplied history begins in 2024.
- `SITE_B` = the repository owner's resident SMS archive for the same building; supplied history begins in 2025.

The exact building address, apartment numbers and subscriber/account numbers are intentionally not public.

The neighbor receives Telasi messages for more than one property generally, but the pseudonymized `SITE_A` transcript used in this repository concerns the **same Orkhevi building** as `SITE_B`.

## What the resident evidence supports

The supplied records document repeated Telasi electricity-interruption notifications associated with one Orkhevi building, corroborated by two resident SMS archives during their overlapping period.

A defensible formulation is:

> The dataset documents repeated Telasi electricity-interruption notifications for one residential building in Orkhevi, with two resident archives independently preserving many of the same restoration-ETA notifications during the overlap period.

The overlap is **cross-resident corroboration of one location**, not evidence of correlation between two different service points and not evidence of a particular feeder, transformer, substation or topology.

The longest constant resident series, SITE_A, has 21 emergency ETA-date groups forming 20 consecutive inter-arrival intervals over exactly 634 elapsed days; the exact mean notification-group gap is `317/10 = 31.7` days. This is a descriptive property of the supplied anchors, not a proven physical-outage recurrence rate.

## Time and ascertainment scope

The combined resident source-record anchor span is **2024-11-10 through 2026-08-06**.

SITE_A is the longer single-resident series. SITE_B begins later. This means a simple union of the two archives changes ascertainment over time: before SITE_B begins there is one resident source, while later there are two. The union is useful for preserving all known building-level notification groups, but it should not be treated as a constant-observation-rate series.

The span consists of supplied scheduled dates/restoration-ETA dates, not a proven complete continuous observation window.

## Independent benchmark scope

The WBES benchmark is **Tbilisi-wide business-establishment survey context for 2023**, not household/service-point monitoring and not an Orkhevi-building sample.

The captured published/display values include `31.8%` of firms experiencing electrical outages and `0.8` average outages in a **typical month**. Those values provide independent Tbilisi context but are not definition-identical to resident restoration-ETA notification inter-arrival metrics.

WBES “typical month” is not treated as an arithmetic mean calendar month. The repository therefore does not convert `0.8` into “one outage every N days” and does not claim a direct `X×` or `Y%` Orkhevi-building-vs-Tbilisi physical-outage reliability difference.

Any arithmetic quotient retained in machine-readable exact-analysis output is diagnostic/reproducibility metadata only.

## Telasi API geographic scope

Searching Telasi's public API for the Georgian substring `ორხევი` is a **text query**, not a building-level or electrical-topology query.

Returned publications can mention Orkhevi Settlement, the industrial zone, named roads/exits, or broader Orkhevi-associated locations. The canonical 17-hit API snapshot therefore cannot be translated directly into 17 outages of this building or 17 settlement-wide outages.

The Telasi API snapshots are point-in-time captures on **2026-08-08**. A reported API `listCount` does not, by itself, establish that every listed publication was preserved locally.

## External grid context

Nationwide transmission-system events are stored separately in `data/external_context.csv`. They are contextual events, not local Telasi notification groups, and are not automatically treated as causes of local Orkhevi notifications.
