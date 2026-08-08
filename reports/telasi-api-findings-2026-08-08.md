# Telasi public outage API findings — 2026-08-08

## Endpoints and response layout

### `getPoweroutages`

`POST https://app.telasi.ge/api/view/telasi/getPoweroutages`

Two request families were observed on Telasi's public frontend:

**Search mode**

```json
{"contentType":"poweroutage","searchText":"ორხევი"}
```

**Paginated list mode**

```json
{
  "searchText":"",
  "pageNumber":1,
  "perPage":12,
  "selectedlan":"ka",
  "taxonomy":{"content_poweroutage":[2769,2770]}
}
```

The relevant records are returned under `content.list`; the parallel `api.list` is empty in the captured responses.

Every search/list record already contains the publication's HTML body in `editor`.

### `getMtData`

`POST https://www.telasi.ge/api/getMtData`

Tested payload:

```json
{"url":"/company-news/power-outage?content=5584","lang":"ka"}
```

The captured response contains Nuxt/page/SEO metadata. It is not the outage-publication body endpoint.

## Georgian Unicode failure discovered during reproduction

A Brave Copy-as-cURL → Postman import path mangled Georgian `searchText`. Manually re-entering `ორხევი` produced the expected response.

The repository client serializes JSON with `ensure_ascii=False`, encodes it as UTF-8 and sends `Content-Type: application/json; charset=utf-8` plus `lang: ka`.

## Canonical Orkhevi snapshot

The preserved Postman response for `ორხევი` has:

- `content.listCount = 17`;
- 17 `content.list` objects;
- 13 records with observed taxonomy `[2770]`;
- 4 records with `[2769]`;
- reconstructed original SHA-256 `99e9f1a1331b97300bc1984304c2d71db8acd46fbf543a8ff0e45d3eecf0cb89`.

The geographic classifier finds:

- 9 explicit settlement-name matches;
- 1 industrial-zone match;
- 2 Orkhevi-named exit/road matches;
- 5 broader Orkhevi-name matches.

This is a **text-search publication set**, not a set of 17 SITE_B incidents.

## Exploratory list probes and the 889 misunderstanding

Focused GitHub Actions run `31253449527` produced four `getPoweroutages` responses in artifact `9020698787`. The raw artifact was inspected during this audit; the repository retains the request/response observations and SHA-256 values rather than duplicating the entire artifact.

Correctly reading `content.*` gives:

| Probe | Reported `content.listCount` | Records actually present in response |
|---|---:|---:|
| exact frontend list payload, `perPage=12` | 889 | 12 |
| taxonomy search for `ორხევ` | 17 | 17 |
| contentType + taxonomy search for `ორხევ`, `perPage=100` | 17 | 17 |
| general contentType list, `perPage=100` | 889 | 100 |

The exploratory workflow originally printed zeros because it inspected `api.listCount/api.list`. That console summary was wrong; the artifact responses were inspected and the corrected observations plus response hashes are recorded in `MANIFEST.json`.

More importantly, **889 was a reported total, not the number of records returned in one response**. The reviewed general-list artifact response is only page 1. The repository therefore makes no claim that a complete 889-publication snapshot was saved on 2026-08-08.

The current fetcher has `--all-pages` mode and only marks a corpus complete when unique fetched publication count equals the API-reported total.

## ETA extraction and source-data anomalies

For the 13 unplanned rows in the canonical Orkhevi snapshot, the parser extracts an explicit restoration ETA from each publication, including spaced-digit formatting such as `1 1 .07.2026 04 : 31`.

Source values are not silently repaired. Examples:

- content ID `5584`: publication timestamp 2026-07-11 07:43:46, stated ETA 2026-07-11 04:31;
- content ID `4640`: publication timestamp 2026-01-03 09:46:06, stated ETA 2026-01-03 09:31;
- content ID `4644`: publication timestamp in January 2026, body ETA parsed literally as **2025-01-04 08:05**.

These anomalies demonstrate that the public publication API is an official source of what Telasi published, not a clean internal event ledger.

## Comparison with resident SMS

Within the **focused 17-hit Orkhevi snapshot**, there is no exact `YYYY-MM-DD HH:MM` restoration-ETA match with the supplied emergency SMS values.

Examples:

- resident SMS 2025-11-05 14:22 vs public Orkhevi hit ID 4426 ETA 04:17;
- resident SMS 2025-12-06 17:11 vs IDs 4539/4541 ETA 09:25.

This negative result applies only to the focused 17-publication fixture. It does **not** justify “no exact match exists anywhere in the public archive,” because a complete historical list snapshot was not preserved in the evidence package.

`scripts/compare_telasi_api_sms.py` now requires complete-pagination metadata before a corpus-wide negative conclusion can be treated as such.

## Planned-work cross-check example

Publication ID `4970` contains an 11:00–18:00 planned restriction window in a section mentioning the Orkhevi industrial zone. The resident SMS dataset also contains a 12 March 2026 planned 11:00–18:00 window at both SITE_A and SITE_B.

This is useful public-source corroboration of the announced window, but the API wording does not establish that the publication and both subscriber messages refer to the exact same feeder/service point.

## Reproducibility

Offline:

```bash
python scripts/validate.py
python -m unittest discover -s tests -v
python scripts/reconstruct_telasi_api_snapshot.py
```

Live complete-list fetch:

```bash
python scripts/fetch_telasi_api.py \
  --all-pages \
  --per-page 100 \
  --output-dir artifacts/telasi_api/all
```

Live comparison requires completeness:

```bash
python scripts/compare_telasi_api_sms.py \
  --api-dir artifacts/telasi_api/all \
  --orkhevi-dir artifacts/telasi_api/orkhevi \
  --require-complete
```

The live workflow asserts semantic/completeness properties rather than hard-coding historical counts such as 17 or 889, because those public values can legitimately change over time.
