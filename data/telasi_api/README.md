# Telasi public power-outage API

Official endpoint used by the Telasi web application:

`POST https://app.telasi.ge/api/view/telasi/getPoweroutages`

A public-frontend-style payload is:

```json
{
  "searchText": "ორხევ",
  "pageNumber": 1,
  "perPage": 100,
  "selectedlan": "ka",
  "taxonomy": {
    "content_poweroutage": [2769, 2770]
  }
}
```

Run:

```bash
python scripts/fetch_telasi_api.py --search-text "ორხევ" --per-page 100
```

To fetch the complete currently exposed publication corpus in one request:

```bash
python scripts/fetch_telasi_api.py --search-text "" --per-page 2000
```

At the 2026-08-08 test, this returned 889 publications spanning 2025-10-13 through 2026-08-08.

## Actual response structure

The response contains parallel top-level objects named `api` and `content`.
For the power-outage query tested here, the actual records are in:

- `content.listCount`
- `content.list`

The parallel `api.listCount` is zero and `api.list` is empty.

Each `content.list` item already includes the full publication HTML in the
`editor` field, together with fields such as `id`, `date`, `created_at`,
`updated_at`, `status`, `content_type`, `taxonomy`, `slug`, `title` and `teaser`.

The earlier hypothesis that a second request is required to fetch the
publication body was tested and rejected.

## `getMtData` is not the outage-detail API

The endpoint:

`POST https://www.telasi.ge/api/getMtData`

with a payload such as:

```json
{"url":"/company-news/power-outage?content=5584","lang":"ka"}
```

returns Nuxt/page metadata including SEO information. It does **not** provide
the outage publication body; that body is already present in
`getPoweroutages` → `content.list[].editor`.

## Observed taxonomy IDs

In the fetched corpus, records carrying only taxonomy ID `2769` are treated by
this repository as `planned_or_scheduled`, while records carrying only `2770`
are treated as `unplanned`.

These labels are based on the observed titles/body content and should be kept
as an empirical mapping unless an official Telasi taxonomy definition is
located.

## Orkhevi search result

Searching the Georgian substring `ორხევ` returned 17 public publications in
the 2026-08-08 fetch:

- 13 `unplanned` publications;
- 4 `planned_or_scheduled` publications.

This is a text search, not an electrical-topology query. A hit can refer to an
Orkhevi industrial-zone address, road/exit, or another textual occurrence and
must not automatically be attributed to the user's service point or the whole
settlement.

## Evidence semantics

This API is a separate official-source layer and must not be silently merged
with resident SMS records.

For unplanned publications, the script parses the Georgian phrase for the
estimated restoration time from `editor`. The parsed value is stored as
`restoration_eta` and remains exactly that: an **estimated restoration time**,
not an actual restoration timestamp or outage duration.

The public API contains duplicates and apparent source-data errors/typos. Raw
responses are therefore preserved together with a SHA-256 digest before any
normalization.

## Matching to SMS

Use:

```bash
python scripts/compare_telasi_api_sms.py --fetch
```

The 2026-08-08 complete-corpus comparison found **no exact restoration-ETA
match** between the supplied emergency SMS values and any of the 889 public
Telasi publications.

That is a useful negative result. It indicates that the website/API publication
layer is **not a complete subscriber-level outage history**. It does not
invalidate the SMS records.

Do not infer a match solely because a public publication and a subscriber SMS
occur on the same calendar date; Telasi can publish many different notices on
the same day with different areas and ETAs.

See `reports/telasi-api-findings-2026-08-08.md` for the detailed findings and
caveats.

The pull-request workflow fetches the live corpus and asserts the currently
observed structural invariants. This is intentional: if Telasi changes the API
schema, taxonomy behavior, archive depth, or Orkhevi search result count, CI
will fail instead of silently producing incompatible data.
