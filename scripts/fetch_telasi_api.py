#!/usr/bin/env python3
"""Fetch or normalize Telasi public power-outage publications.

This CLI preserves source responses and delegates parsing/pagination to small,
testable standard-library modules. ETAs remain estimates, not actual outage
duration or restoration timestamps.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError

from telasi_api_core import (
    DEFAULT_PER_PAGE, DEFAULT_SEARCH_TEXT, ENDPOINT, content_object, fetch_raw,
    make_list_payload, make_search_payload, parse_document,
)
from telasi_api_pagination import fetch_all_list_pages, write_normalized_outputs

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--search-text", default=DEFAULT_SEARCH_TEXT)
    parser.add_argument("--list-mode", action="store_true", help="Use one paginated-list request instead of search mode")
    parser.add_argument("--all-pages", action="store_true", help="Fetch every currently exposed paginated-list page")
    parser.add_argument("--page-number", type=int, default=1)
    parser.add_argument("--per-page", type=int, default=DEFAULT_PER_PAGE)
    parser.add_argument("--selected-lang", default="ka")
    parser.add_argument("--input-json", help="Normalize a captured response instead of making a network request")
    parser.add_argument("--output-dir", default="artifacts/telasi_api")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--max-pages", type=int, default=None, help="Safety bound for --all-pages")
    args = parser.parse_args()

    if args.page_number < 1 or args.per_page < 1:
        raise SystemExit("--page-number and --per-page must be positive")
    if args.max_pages is not None and args.max_pages < 1:
        raise SystemExit("--max-pages must be positive")
    if args.input_json and args.all_pages:
        raise SystemExit("--input-json cannot be combined with --all-pages")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    processed_at = datetime.now().astimezone().isoformat(timespec="seconds")

    metadata: dict = {"processed_at": processed_at}

    if args.all_pages:
        try:
            document, pagination_meta = fetch_all_list_pages(
                output_dir=output_dir,
                per_page=args.per_page,
                selected_lang=args.selected_lang,
                timeout=args.timeout,
                max_pages=args.max_pages,
            )
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            raise SystemExit(f"Telasi API all-pages fetch failed: {exc}") from exc
        metadata.update(pagination_meta)
        write_normalized_outputs(document, output_dir, metadata)
        if not pagination_meta["complete_against_reported_total"]:
            raise SystemExit(
                "Telasi API pagination ended before the reported total was reconstructed; "
                f"see {output_dir/'fetch_metadata.json'}"
            )
        print(json.dumps(metadata, ensure_ascii=False, indent=2))
        return 0

    if args.input_json:
        source_path = Path(args.input_json)
        raw = source_path.read_bytes()
        payload = None
        status = None
        response_content_type = "application/json (local capture)"
        source = str(source_path)
    else:
        payload = (
            make_list_payload(args.page_number, args.per_page, args.selected_lang)
            if args.list_mode
            else make_search_payload(args.search_text)
        )
        source = ENDPOINT
        try:
            raw, status, response_content_type = fetch_raw(payload, args.selected_lang, args.timeout)
        except (HTTPError, URLError, TimeoutError) as exc:
            raise SystemExit(f"Telasi API request failed: {exc}") from exc

    raw_path = output_dir / "response.json"
    raw_path.write_bytes(raw)
    try:
        document = parse_document(raw)
        content = content_object(document)
    except ValueError as exc:
        raise SystemExit(f"Invalid Telasi API response; preserved at {raw_path}: {exc}") from exc

    metadata.update(
        {
            "mode": "input_json" if args.input_json else ("list_page" if args.list_mode else "search"),
            "source": source,
            "endpoint": ENDPOINT,
            "method": None if args.input_json else "POST",
            "payload": payload,
            "http_status": status,
            "response_content_type": response_content_type,
            "response_bytes": len(raw),
            "response_sha256": hashlib.sha256(raw).hexdigest(),
            "content_page": content.get("page"),
        }
    )
    write_normalized_outputs(document, output_dir, metadata)
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
