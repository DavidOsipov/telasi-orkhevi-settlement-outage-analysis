# Telasi public power-outage API

This directory documents a separate **official-source publication layer** obtained from Telasi's public website APIs.

It must not be silently merged with resident SMS evidence. The API returns public Telasi **publications/search hits**, not a complete subscriber-level interruption log and not an authoritative physical-incident database.

## 1. Search endpoint

`POST https://app.telasi.ge/api/view/telasi/getPoweroutages`

Observed search payload:

```json
{"contentType":"poweroutage","searchText":"ორხევი"}
```

Important request headers:

```text
Content-Type: application/json; charset=utf-8
lang: ka
```

The client also sends public-site-compatible `Origin` and `Referer` headers.

### UTF-8 warning

During the 2026-08-08 investigation, a Brave **Copy as cURL → Postman** import path mangled Georgian `searchText`. Manually re-entering `ორხევი` fixed the request.

Always inspect the actual request body before interpreting an empty result. `scripts/fetch_telasi_api.py` avoids shell/cURL re-encoding by serializing Unicode JSON directly and encoding it as UTF-8.

## 2. Response structure

Successful captured responses contain parallel top-level objects:

```text
api
content
```

For the request shapes documented here, publication records are in:

- `content.listCount`
- `content.page`
- `content.list`

The parallel `api.listCount` is `0` and `api.list` is empty.

Each `content.list[]` publication can include:

- `id`
- `date`, `created_at`, `updated_at`
- `status`
- `content_type`
- `taxonomy`
- `slug`
- `title`
- `teaser`
- `editor` — full publication HTML

A second detail API is therefore not required to obtain the publication body for these records.

## 3. Paginated list mode

The public page was also observed sending:

```json
{
  "searchText":"",
  "pageNumber":1,
  "perPage":12,
  "selectedlan":"ka",
  "taxonomy":{"content_poweroutage":[2769,2770]}
}
```

Search mode and list mode are separate frontend request shapes even though they use the same endpoint.

### `listCount` is not response length

An exploratory 2026-08-08 general-list response reported:

```text
content.listCount = 889
len(content.list) = 100
```

Another exact frontend payload returned 12 records while reporting the same total 889.

Therefore `content.listCount=889` does **not** prove that 889 records were fetched in one request. Earlier experimental code made that assumption; it has been removed.

Use real pagination:

```bash
python scripts/fetch_telasi_api.py \
  --all-pages \
  --per-page 100 \
  --output-dir artifacts/telasi_api/all
```

`--all-pages`:

- preserves every raw page under `raw_pages/`;
- detects the effective first-page size rather than trusting requested `perPage`;
- follows page numbers;
- deduplicates by publication ID for pagination stability;
- records raw-page SHA-256 values;
- records a stop reason;
- fails unless unique fetched count equals the API-reported total.

A transient live corpus is written under ignored `artifacts/` and is not automatically promoted to curated source evidence.

## 4. `getMtData`

`POST https://www.telasi.ge/api/getMtData`

Captured example:

```json
{"url":"/company-news/power-outage?content=5584","lang":"ka"}
```

The 2026-08-08 response contains page/Nuxt/SEO metadata (`placeFillers`, `htmlTag`, `urlParts`, `headerObjects`). It does **not** contain the outage publication body. That body is already present in `getPoweroutages` → `content.list[].editor`.

## 5. Observed taxonomy semantics

In the canonical 17-hit snapshot:

- taxonomy ID `2769` occurs on planned/scheduled-work publications;
- taxonomy ID `2770` occurs on unplanned interruption publications.

The repository labels these empirically as `planned_or_scheduled` and `unplanned`.

This is an **observed mapping**, not an official Telasi taxonomy specification unless/until Telasi documentation is found.

## 6. Orkhevi text-search snapshot

The canonical Postman response captured on 2026-08-08 for `ორხევი` contains:

- 17 publications;
- 13 `unplanned` rows;
- 4 `planned_or_scheduled` rows.

Normalized geographic match classes are:

- 9 `explicit_settlement`;
- 1 `industrial_zone`;
- 2 `orkhevi_named_exit`;
- 5 `broader_orkhevi_name_match`.

Searching `ორხევი` is a text search, not an electrical-topology query. **17 hits must not be restated as 17 outages of SITE_B or of the whole settlement.**

## 7. Time semantics and source-data quality

For unplanned publications, the parser extracts Telasi's phrase for estimated restoration time and stores it as `restoration_eta`.

This remains an **ETA**, not actual restoration and not outage duration.

The captured public data contain source-side anomalies. Examples include:

- publication timestamps later than stated ETAs;
- a January 2026 publication whose body contains ETA year 2025;
- duplicate/near-duplicate publications.

The repository preserves these values literally and flags them analytically rather than silently correcting source material.

## 8. Preserved raw evidence

See `raw/2026-08-08/MANIFEST.json`.

### Canonical Orkhevi response

The original source response has:

```text
bytes   295834
sha256  99e9f1a1331b97300bc1984304c2d71db8acd46fbf543a8ff0e45d3eecf0cb89
```

It is stored reversibly as deterministic gzip → Base64 split into eight text chunks because the repository write channel available at capture time was text-only.

Cross-platform verification/reconstruction:

```bash
python scripts/reconstruct_telasi_api_snapshot.py \
  --output artifacts/telasi_api/orkhevi-response.json
```

`validate.py` performs the same byte/hash checks automatically.

### Focused exploratory probes

Raw page/search responses from GitHub Actions run `31253449527`, artifact `9020698787`, were inspected during the audit but are not duplicated in the repository. The manifest retains their byte lengths, SHA-256 hashes, request payloads and parsed response counts.

They include:

| Request | Reported total | Records present |
|---|---:|---:|
| exact frontend list payload, page 1, `perPage=12` | 889 | 12 |
| taxonomy search `ორხევ`, `perPage=100` | 17 | 17 |
| contentType + taxonomy search `ორხევ`, `perPage=100` | 17 | 17 |
| contentType general list, page 1, `perPage=100` | 889 | 100 |

The exploratory workflow's printed summary was wrong because it inspected `api.*`; `MANIFEST.json` records corrected `content.*` observations derived from the artifact raw responses.

Browser netlogs are intentionally not committed because they can contain unrelated/private request metadata. Relevant request shapes are documented here and in the manifest.

## 9. Normalize a preserved response

```bash
python scripts/reconstruct_telasi_api_snapshot.py \
  --output artifacts/telasi_api/orkhevi-response.json

python scripts/fetch_telasi_api.py \
  --input-json artifacts/telasi_api/orkhevi-response.json \
  --output-dir artifacts/telasi_api/normalized-orkhevi
```

The fetcher writes:

- preserved `response.json` for a single-response mode;
- `fetch_metadata.json` with SHA-256 and semantic warnings;
- LF-stable `records.csv`.

## 10. Matching public publications to resident SMS

Exact restoration-ETA matching is implemented by `scripts/compare_telasi_api_sms.py`.

For the focused 17-hit Orkhevi fixture, there is no exact ETA match with resident emergency SMS. This conclusion applies only to those 17 publications.

For a corpus-wide comparison, first fetch all pages and require completeness:

```bash
python scripts/compare_telasi_api_sms.py \
  --api-dir artifacts/telasi_api/all \
  --orkhevi-dir artifacts/telasi_api/orkhevi \
  --require-complete \
  --output artifacts/telasi_api/comparison.json
```

A positive exact match is useful corroboration even in partial data. A zero-match corpus-wide statement is not allowed unless `complete_against_reported_total` is true.

## 11. Offline regression coverage

`tests/test_telasi_api.py` covers:

- canonical snapshot reconstruction/hash;
- 17-row fixture count;
- 13/4 taxonomy classification;
- 9/1/2/5 geographic classification;
- spaced-digit ETA parsing;
- preservation of the 2025-year source anomaly in a 2026 publication;
- no exact ETA match within the focused 17-hit fixture;
- explicit proof that the 889-count exploratory response is partial;
- mocked pagination when the server caps requested `perPage`.

The live workflow tests current API semantics without hard-coding historical values such as 17 or 889.
