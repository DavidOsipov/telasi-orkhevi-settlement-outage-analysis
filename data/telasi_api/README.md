# Telasi public power-outage API

Official endpoint used by the Telasi web application:

`POST https://app.telasi.ge/api/view/telasi/getPoweroutages`

Current Orkhevi-oriented query payload:

```json
{"contentType":"poweroutage","searchText":"ორხევ"}
```

Run:

```bash
python scripts/fetch_telasi_api.py --search-text "ორხევ"
```

By default, the script writes an exact `response.json`, fetch metadata including a SHA-256 hash, and a normalized `records.csv` under `artifacts/telasi_api/`.

## Evidence semantics

This API is a separate official-source layer and must not be silently merged with resident SMS records.

The response exposes fields including `id`, `code`, `users_count`, `outage_time`, `poweron_time`, `delayed`, address/title fields, taxonomy, and record creation/update timestamps.

The meaning of `poweron_time` should be treated conservatively. Unless Telasi documentation establishes otherwise, this repository does **not** assume that it is an actual restoration timestamp. The derived `api_window_minutes` field is therefore only the mathematical difference between `outage_time` and `poweron_time`, not a claimed physical outage duration.

## Matching to SMS

Potential API/SMS matches should be stored explicitly with a match method and confidence. Useful evidence includes:

- date/time consistency;
- address or Orkhevi name match;
- outage type (`planned`, emergency/`არაგეგმური`, switching/`გადართვა`, etc.);
- matching restoration ETA where applicable;
- Telasi `code` / API `id`.

Do not infer a match solely because two records occur on the same date.
