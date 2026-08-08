# Telasi public outage API findings — 2026-08-08

## Endpoints tested

### Publication list / search

`POST https://app.telasi.ge/api/view/telasi/getPoweroutages`

Public-frontend-style payload:

```json
{
  "searchText": "",
  "pageNumber": 1,
  "perPage": 12,
  "selectedlan": "ka",
  "taxonomy": {
    "content_poweroutage": [2769, 2770]
  }
}
```

The response contains two parallel top-level objects, `api` and `content`.
For this endpoint/payload, the actual outage-publication records are in
`content.list`; `api.list` is empty.

Each `content.list` record already contains the publication's full HTML body in
`editor`. A second API call is therefore not required to retrieve the text of
the outage publication.

### `getMtData`

`POST https://www.telasi.ge/api/getMtData`

Tested payload:

```json
{
  "url": "/company-news/power-outage?content=5584",
  "lang": "ka"
}
```

This endpoint returned Nuxt/SEO metadata for the page (`seoData`, language and
related metadata), not the outage publication body. It should not be treated as
the detail-data endpoint for outage records.

## Available corpus

A single request with `perPage=2000` returned **889 public Telasi outage
publications**.

Publication timestamp range in the fetched corpus:

- earliest: **2025-10-13 17:02:30**
- latest at fetch time: **2026-08-08 12:25:45**

This is an archive of public website publications, not an authoritative internal
outage-event ledger. The archive currently exposed through this query does not
cover the earlier 2024–mid-2025 portion of the resident SMS record.

The number 889 is a count of **publications**, not physical outage incidents.
Multiple publications can refer to related events, duplicates can exist, and a
single subscriber-level interruption may have no corresponding public
publication at all.

## Search for Orkhevi

Searching for the Georgian substring `ორხევ` returned **17 publications**:

- **13** with observed taxonomy ID `2770` (`unplanned` in this analysis);
- **4** with observed taxonomy ID `2769` (`planned_or_scheduled`).

The search is text-based. A hit can refer to Orkhevi Settlement, Orkhevi
industrial zone, an Orkhevi road/exit, or another textual occurrence. Therefore
17 search hits must not be translated into “17 outages of the user's service
point” or even “17 settlement-wide outages.”

Examples include:

- ID 5584, published 2026-07-11, unplanned switching, ETA 04:31;
- ID 4761, published 2026-02-02, unplanned fault, ETA 21:42;
- IDs 4539 and 4541, both published 2025-12-06, fire-related, ETA 09:25;
- ID 4426, published 2025-11-05, unplanned fault, ETA 04:17;
- planned publication ID 4970 for 12 March 2026, whose body contains an
  11:00–18:00 restriction window in a section mentioning Orkhevi industrial
  zone.

## Comparison with resident SMS ETAs

All public API publications were compared with the restoration ETA values in
the supplied emergency SMS record using exact `YYYY-MM-DD HH:MM` matching.

For SMS dates that fall inside the public API archive period, **no exact ETA
match was found in the 889-publication corpus**.

Examples:

| Resident SMS ETA | Public Orkhevi publication on same date / nearby context |
|---|---|
| 2025-11-05 14:22 | Orkhevi search hit ID 4426 has ETA 04:17 |
| 2025-12-06 17:11 | Orkhevi hits IDs 4539/4541 have ETA 09:25; other city publications have other ETAs |
| 2026-01-22 12:00 / 20:00 | Public corpus has other 22 January publications, but no exact 12:00 or 20:00 ETA |
| 2026-04-07 19:33 / 22:29 | No exact ETA match |
| 2026-07-14 15:19 | No exact ETA match |
| 2026-08-04 14:32 | No exact ETA match |
| 2026-08-05 12:54 | No exact ETA match |
| 2026-08-06 17:40 | No exact ETA match |

This is an important negative result: the public Telasi website-publication
layer is **not a complete subscriber-level interruption history**. Absence of a
matching public card does not contradict an SMS notification sent to a
subscriber.

The result also shows why same-calendar-day matching is insufficient. Telasi
can publish several distinct outage notices on one date, each with different
areas and ETAs.

## Data-quality cautions in Telasi's own public corpus

The public API contains records that require source-preserving quality flags,
including:

- duplicate or near-duplicate publications;
- apparent copied year errors (some 2026 publications contain restoration ETA
  years of 2025);
- publication timestamps later than the ETA stated in the body;
- records whose publication timestamp/month does not agree with the date named
  in the title/body;
- obvious reused or mistyped dates in some records.

For example, publication ID 4644 was published in January 2026 but its body
contains a restoration ETA year of 2025. Such values are retained as-source and
must be flagged rather than silently corrected.

These anomalies mean that the public API is an official publication source, but
not a clean ground-truth event ledger.

## Methodological consequence

The repository now has three different evidence layers:

1. **subscriber SMS notifications** — strongest evidence that a particular
   subscriber was notified about an interruption;
2. **Telasi public outage publications/API** — official public statements about
   selected affected areas and expected restoration times;
3. **GNERC/system-level reliability information** — aggregate regulatory
   context.

The public Telasi API should be used to corroborate and contextualize the SMS
record, not replace it.

For a formal request to Telasi, the mismatch itself is useful: Telasi can be
asked to supply its internal interruption/event IDs and actual start/restoration
timestamps corresponding to the subscriber SMS, because those subscriber-level
records are demonstrably not recoverable from the public publication API.

## Reproducibility

The comparison is implemented in `scripts/compare_telasi_api_sms.py`.
The GitHub Actions integration fetches the live public corpus, the Orkhevi search
subset and then checks the comparison invariants. On 2026-08-08 the validation
workflow completed successfully with the 889-publication corpus, 17 Orkhevi
search results and zero exact SMS-ETA matches.
