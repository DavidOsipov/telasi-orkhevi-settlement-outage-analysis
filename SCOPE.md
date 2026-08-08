# Scope

## Geographic scope

This repository concerns electricity interruption evidence collected from two correlated Telasi service points in **Orkhevi Settlement (ორხევის დასახლება), Samgori District, Tbilisi, Georgia**.

Canonical place identifier:

- Wikidata: `Q130437988`
- Place: Orkhevi Settlement, Tbilisi, Georgia

## Evidentiary scope

The repository contains resident-supplied Telasi SMS notifications and a conservative normalization of those messages into event-level records.

The evidence supports the conclusion that the two observed service points frequently experienced the same upstream distribution events: in the overlapping record, shared emergency events have matching estimated restoration times to the minute.

This does **not** establish the exact physical topology of the distribution network. In particular, the public evidence does not prove that the two service points are connected to:

- the same low-voltage feeder;
- the same transformer;
- the same medium-voltage feeder; or
- any specifically identified Telasi substation.

Those questions require Telasi network records.

## Settlement-wide claims

The dataset must not be interpreted as proof that every recorded interruption affected all of Orkhevi Settlement.

The defensible claim is narrower:

> The supplied SMS records document repeated electricity interruptions affecting at least two correlated Telasi service points in Orkhevi Settlement, with a longitudinal record extending from November 2024 through August 2026.

Where external sources document wider Tbilisi-wide or nationwide grid events, those events are stored separately as contextual evidence and are not automatically counted as local Orkhevi interruption events.

## Time scope

Current observation window:

**2024-11-10 through 2026-08-06**, inclusive.

The observation window may be extended when additional historical SMS records or independently verifiable outage evidence become available.

## Known limitations

The source SMS messages generally provide an estimated restoration time, not:

- a verified interruption start timestamp;
- an actual restoration timestamp;
- affected-customer counts;
- feeder or transformer identifiers;
- an authoritative cause code;
- complete coverage of all interruptions.

Some outages occurred without an SMS. Event counts derived from this repository should therefore be treated as a **lower-bound observational record**.

Official reliability indicators such as SAIDI, SAIFI, CAIDI, or MTTR cannot be calculated reliably from this dataset alone.
