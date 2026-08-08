#!/usr/bin/env python3
"""Fetch Telasi public power-outage API records without third-party dependencies.

The script preserves the server JSON response and also writes a normalized CSV.
It deliberately calls the interval between ``outage_time`` and ``poweron_time``
``api_window_minutes`` rather than outage duration: the public API does not, by
itself, establish that ``poweron_time`` is an actual restoration timestamp.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ENDPOINT = "https://app.telasi.ge/api/view/telasi/getPoweroutages"
DEFAULT_SEARCH_TEXT = "ორხევ"


def parse_dt(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def api_window_minutes(item: dict) -> int | None:
    start = parse_dt(item.get("outage_time"))
    end = parse_dt(item.get("poweron_time"))
    if start is None or end is None or end < start:
        return None
    return int((end - start).total_seconds() // 60)


def fetch(search_text: str, timeout: float) -> tuple[bytes, int, str]:
    payload = {
        "contentType": "poweroutage",
        "searchText": search_text,
    }
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    request = Request(
        ENDPOINT,
        data=body,
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "telasi-orkhevi-settlement-outage-analysis/1.0",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read(), response.status, response.headers.get("Content-Type", "")


def normalize_rows(document: dict) -> list[dict]:
    api = document.get("api")
    if not isinstance(api, dict):
        raise ValueError("Response does not contain an 'api' object")
    items = api.get("list")
    if not isinstance(items, list):
        raise ValueError("Response api.list is not a list")

    rows: list[dict] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "id": item.get("id"),
                "code": item.get("code"),
                "full_title": item.get("full_title"),
                "title": item.get("title"),
                "teaser": item.get("teaser"),
                "editor": item.get("editor"),
                "outage_time": item.get("outage_time"),
                "poweron_time": item.get("poweron_time"),
                "api_window_minutes": api_window_minutes(item),
                "users_count": item.get("users_count"),
                "delayed": item.get("delayed"),
                "status": item.get("status"),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "slug": item.get("slug"),
                "taxonomy_json": json.dumps(item.get("taxonomy"), ensure_ascii=False, sort_keys=True),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--search-text", default=DEFAULT_SEARCH_TEXT)
    parser.add_argument("--output-dir", default="artifacts/telasi_api")
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = {"contentType": "poweroutage", "searchText": args.search_text}
    fetched_at = datetime.now().astimezone().isoformat(timespec="seconds")

    try:
        raw, status, content_type = fetch(args.search_text, args.timeout)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise SystemExit(f"Telasi API request failed: {exc}") from exc

    sha256 = hashlib.sha256(raw).hexdigest()
    raw_path = output_dir / "response.json"
    raw_path.write_bytes(raw)

    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Telasi API returned non-JSON content; raw response saved to {raw_path}") from exc

    rows = normalize_rows(document)

    metadata = {
        "endpoint": ENDPOINT,
        "method": "POST",
        "payload": payload,
        "fetched_at": fetched_at,
        "http_status": status,
        "content_type": content_type,
        "response_sha256": sha256,
        "api_listCount": document.get("api", {}).get("listCount"),
        "normalized_row_count": len(rows),
        "semantic_warning": (
            "api_window_minutes is the difference between the API fields outage_time and "
            "poweron_time; it is not asserted to be actual physical outage duration."
        ),
    }
    (output_dir / "fetch_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    csv_path = output_dir / "records.csv"
    fieldnames = [
        "id", "code", "full_title", "title", "teaser", "editor",
        "outage_time", "poweron_time", "api_window_minutes", "users_count",
        "delayed", "status", "created_at", "updated_at", "slug", "taxonomy_json",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    for row in rows:
        print(
            f"{row['id']}\t{row['code']}\t{row['full_title']}\t"
            f"{row['outage_time']} -> {row['poweron_time']}\t"
            f"{row['api_window_minutes']} min\tusers={row['users_count']}\t"
            f"{row['editor'] or row['teaser']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
