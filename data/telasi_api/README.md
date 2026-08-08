# Telasi public power-outage API

This directory documents and preserves a separate **official-source publication layer** obtained from Telasi's public website API.

It must not be silently merged with the resident SMS evidence. The API returns public Telasi **publications/search hits**, not a complete subscriber-level interruption log and not an authoritative incident database.

## 1. Search endpoint

Endpoint used by the public Telasi frontend:

`POST https://app.telasi.ge/api/view/telasi/getPoweroutages`

Observed browser search request for Orkhevi:

```json
{"contentType":"poweroutage","searchText":"ორხევი"}
```

Important request headers observed/used successfully:

```text
Content-Type: application/json
lang: ka
```

The repository client also sends browser-compatible `Origin` and `Referer` headers.

### UTF-8 warning

The Georgian query must remain valid UTF-8. During the 2026-08-08 investigation, a Brave `Copy as cURL` → Postman import path mangled the Georgian `searchText` into non-Georgian characters. Manually re-entering `ორხევი` in Postman fixed the request.

Do not assume a copied cURL body is correct: inspect the actual request body before interpreting an empty result.

## 2. Response structure

For the successful Orkhevi search captured on 2026-08-08, the response had two parallel top-level objects:

```text
api
content
```

The search results were in:

- `content.listCount`
- `content.list`

The parallel `api.listCount` was `0` and `api.list` was empty.

The captured Orkhevi response contains `content.listCount = 17` and 17 publication objects.

Each `content.list[]` object can contain fields including:

- `id`
- `date`, `created_at`, `updated_at`
- `status`
- `content_type`
- `taxonomy`
- `slug`
- `title`
- `teaser`
- `editor` — the full publication HTML

Because the full publication body is already in `editor`, a second detail API is not required to obtain the outage-publication text for these search results.

## 3. Separate paginated-list payload

The public page was also observed sending a different payload for the general list:

```json
{
  "searchText":"",
  "pageNumber":1,
  "perPage":12,
  "selectedlan":"ka",
  "taxonomy":{"content_poweroutage":[2769,2770]}
}
```

Search mode and list/pagination mode should be treated as separate frontend request shapes even though they use the same endpoint.

## 4. `getMtData`

The page also calls:

`POST https://www.telasi.ge/api/getMtData`

Example observed payload:

```json
{"url":"/company-news/power-outage?content=5584","lang":"ka"}
```

Our 2026-08-08 probe returned page/Nuxt metadata (`placeFillers`, `htmlTag`, `urlParts`, `headerObjects`) including SEO/canonical information. It did **not** return the outage publication body. The body for content ID 5584 was already present in `getPoweroutages` → `content.list[].editor`.

A raw response from this probe is preserved in this directory's dated snapshot.

## 5. Observed taxonomy semantics

In the 2026-08-08 Orkhevi search result:

- taxonomy ID `2769` occurs on publications that appear to be planned/scheduled-work notices;
- taxonomy ID `2770` occurs on publications that appear to be unplanned interruption notices.

The repository labels these empirically as `planned_or_scheduled` and `unplanned`.

This is an observed mapping, **not an official Telasi taxonomy specification**, unless/until such documentation is found.

## 6. Geographic caution

Searching `ორხევი` is a text search, not an electrical-topology query.

Hits may mention:

- `ორხევის დასახლება` — Orkhevi Settlement;
- the Orkhevi industrial zone;
- an Orkhevi-named exit/road;
- streets or other locations described as associated with Orkhevi.

Therefore `17 search hits` must not be restated as `17 outages of the user's service point` or even automatically as `17 outages of the settlement`.

## 7. Time semantics

For unplanned publications, Telasi text may state `ელექტრომომარაგების აღდგენის სავარაუდო დრო` — an **estimated restoration time**.

It is an ETA, not a verified actual restoration timestamp. Do not calculate actual outage duration from it without an authoritative outage-start and actual-restoration record.

The Telasi publication corpus also contains apparent source-data anomalies/typos. Raw responses are therefore preserved before normalization rather than silently corrected.

## 8. Reproduce / normalize

Search live Telasi data:

```bash
python scripts/fetch_telasi_api.py --search-text "ორხევი" --output-dir artifacts/telasi_api
```

Normalize an already captured JSON file without network access:

```bash
python scripts/fetch_telasi_api.py \
  --input-json response.json \
  --output-dir artifacts/telasi_api
```

Use paginated-list request shape:

```bash
python scripts/fetch_telasi_api.py \
  --list-mode \
  --page-number 1 \
  --per-page 12 \
  --output-dir artifacts/telasi_api
```

The script writes the raw response unchanged as `response.json`, a SHA-256-bearing metadata file, and a normalized CSV.

## 9. Preserved snapshot — 2026-08-08

See `raw/2026-08-08/`.

The large Orkhevi search response is stored as a deterministic gzip stream encoded as Base64 so it can be committed through text-only tooling while retaining byte-for-byte recoverability of the original JSON.

Decode it with:

```bash
base64 -d data/telasi_api/raw/2026-08-08/getPoweroutages-search-orkhevi.response.json.gz.b64 \
  | gzip -d \
  > response.json
```

Then verify the SHA-256 listed in `MANIFEST.json`.
