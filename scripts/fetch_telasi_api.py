#!/usr/bin/env python3
"""Fetch or normalize Telasi's public power-outage publication API.

The endpoint returns public *publications*, not an authoritative utility incident
log. For the public search payload, matching records are returned in the
``content`` object; the parallel ``api`` object may remain empty.

For unplanned publications, an estimated restoration timestamp is extracted
from Georgian ``editor`` text when present. It remains an ETA, not an actual
restoration timestamp or outage duration.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ENDPOINT = "https://app.telasi.ge/api/view/telasi/getPoweroutages"
DEFAULT_SEARCH_TEXT = "ორხევი"
DEFAULT_TAXONOMY = (2769, 2770)


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def html_to_text(value: object) -> str:
    if not isinstance(value, str) or not value:
        return ""
    parser = _TextExtractor()
    parser.feed(value)
    parser.close()
    text = html.unescape(" ".join(parser.parts)).replace("\xa0", " ")
    return " ".join(text.split())


def _digits(value: str) -> int:
    return int(re.sub(r"\s+", "", value))


def extract_restoration_eta(text: str) -> str:
    """Return YYYY-MM-DD HH:MM for an explicitly stated restoration ETA."""
    marker = "აღდგენის სავარაუდო დრო"
    pos = text.find(marker)
    if pos < 0:
        return ""
    tail = text[pos : pos + 300]
    match = re.search(
        r"(\d(?:\s*\d)?)\s*\.\s*"
        r"(\d(?:\s*\d)?)\s*\.\s*"
        r"(\d\s*\d\s*\d\s*\d)\s+"
        r"(\d(?:\s*\d)?)\s*:\s*"
        r"(\d\s*\d)",
        tail,
    )
    if not match:
        return ""
    day, month, year, hour, minute = (_digits(value) for value in match.groups())
    try:
        parsed = datetime(year, month, day, hour, minute)
    except ValueError:
        return ""
    return parsed.strftime("%Y-%m-%d %H:%M")


def extract_announced_windows(text: str) -> str:
    """Return explicit HH:MM-HH:MM windows found anywhere in a publication."""
    matches = re.findall(
        r"(\d{1,2}:\d{2})\s*საათიდან\s*(\d{1,2}:\d{2})\s*საათამდე",
        text,
    )
    return ";".join(f"{start}-{end}" for start, end in matches)


def taxonomy_ids(item: dict) -> list[int]:
    taxonomy = item.get("taxonomy")
    if not isinstance(taxonomy, dict):
        return []
    values = taxonomy.get("content_poweroutage")
    if not isinstance(values, list):
        return []
    return [value for value in values if isinstance(value, int)]


def publication_class(item: dict) -> str:
    """Classify IDs observed in the current Telasi public search result.

    2769 is associated with scheduled/planned-work notices in the supplied
    response; 2770 is associated with unplanned interruption publications.
    These labels are empirical API semantics, not a documented Telasi schema.
    """
    ids = set(taxonomy_ids(item))
    if ids == {2769}:
        return "planned_or_scheduled"
    if ids == {2770}:
        return "unplanned"
    return "unknown"


def orkhevi_match_kind(text: str) -> str:
    """Describe why a search hit appears related to Orkhevi."""
    compact = text.replace("\xa0", " ")
    settlement_patterns = (
        r"ორხევი\s*ს\s*დასახლ",
        r"ორხევის\s*დასახლ",
        r"ორხევის\s*დას\.",
    )
    if any(re.search(pattern, compact) for pattern in settlement_patterns):
        return "explicit_settlement"
    if re.search(r"ორხევი\s*ს\s*საწარმოო\s*ზონ|ორხევის\s*საწარმოო\s*ზონ", compact):
        return "industrial_zone"
    if re.search(r"ორხევი\s*ს\s*გასასვლ|ორხევის\s*გასასვლ", compact):
        return "orkhevi_named_exit"
    if "ორხევ" in compact:
        return "broader_orkhevi_name_match"
    return "no_orkhevi_text_match"


def make_search_payload(search_text: str) -> dict:
    return {"contentType": "poweroutage", "searchText": search_text}


def make_list_payload(page_number: int, per_page: int, selected_lang: str) -> dict:
    return {
        "searchText": "",
        "pageNumber": page_number,
        "perPage": per_page,
        "selectedlan": selected_lang,
        "taxonomy": {"content_poweroutage": list(DEFAULT_TAXONOMY)},
    }


def fetch(payload: dict, selected_lang: str, timeout: float) -> tuple[bytes, int, str]:
    # ensure_ascii=False is intentional: Georgian must be sent as UTF-8 JSON.
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    request = Request(
        ENDPOINT,
        data=body,
        method="POST",
        headers={
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "lang": selected_lang,
            "Origin": "https://www.telasi.ge",
            "Referer": "https://www.telasi.ge/",
            "User-Agent": "telasi-orkhevi-settlement-outage-analysis/1.0",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read(), response.status, response.headers.get("Content-Type", "")


def content_object(document: dict) -> dict:
    content = document.get("content")
    if not isinstance(content, dict):
        raise ValueError("Response does not contain a top-level 'content' object")
    if not isinstance(content.get("list"), list):
        raise ValueError("Response content.list is not a list")
    return content


def normalize_rows(document: dict) -> list[dict]:
    content = content_object(document)
    rows: list[dict] = []
    for item in content["list"]:
        if not isinstance(item, dict):
            continue
        editor_html = item.get("editor") if isinstance(item.get("editor"), str) else ""
        editor_text = html_to_text(editor_html)
        searchable_text = " ".join(
            filter(None, [html_to_text(item.get("title")), html_to_text(item.get("teaser")), editor_text])
        )
        rows.append(
            {
                "id": item.get("id"),
                "publication_date": item.get("date"),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "status": item.get("status"),
                "content_type": item.get("content_type"),
                "taxonomy_ids": ";".join(map(str, taxonomy_ids(item))),
                "publication_class": publication_class(item),
                "orkhevi_match_kind": orkhevi_match_kind(searchable_text),
                "slug": item.get("slug"),
                "title": html_to_text(item.get("title")),
                "teaser_text": html_to_text(item.get("teaser")),
                "editor_text": editor_text,
                "restoration_eta": extract_restoration_eta(editor_text),
                "announced_windows": extract_announced_windows(editor_text),
                "editor_html": editor_html,
            }
        )
    return rows


def load_document(raw: bytes, raw_path: Path) -> dict:
    raw_path.write_bytes(raw)
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Telasi response is not valid UTF-8 JSON; saved to {raw_path}") from exc
    if not isinstance(document, dict):
        raise SystemExit("Telasi response JSON is not an object")
    return document


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--search-text", default=DEFAULT_SEARCH_TEXT)
    parser.add_argument("--list-mode", action="store_true")
    parser.add_argument("--page-number", type=int, default=1)
    parser.add_argument("--per-page", type=int, default=100)
    parser.add_argument("--selected-lang", default="ka")
    parser.add_argument("--input-json", help="Normalize a captured response instead of making a network request")
    parser.add_argument("--output-dir", default="artifacts/telasi_api")
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    if args.page_number < 1 or args.per_page < 1:
        raise SystemExit("--page-number and --per-page must be positive")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "response.json"
    processed_at = datetime.now().astimezone().isoformat(timespec="seconds")

    if args.input_json:
        source_path = Path(args.input_json)
        raw = source_path.read_bytes()
        status = None
        response_content_type = "application/json (local capture)"
        payload = None
        source = str(source_path)
    else:
        payload = (
            make_list_payload(args.page_number, args.per_page, args.selected_lang)
            if args.list_mode
            else make_search_payload(args.search_text)
        )
        source = ENDPOINT
        try:
            raw, status, response_content_type = fetch(payload, args.selected_lang, args.timeout)
        except (HTTPError, URLError, TimeoutError) as exc:
            raise SystemExit(f"Telasi API request failed: {exc}") from exc

    document = load_document(raw, raw_path)
    content = content_object(document)
    rows = normalize_rows(document)
    sha256 = hashlib.sha256(raw).hexdigest()

    class_counts: dict[str, int] = {}
    match_counts: dict[str, int] = {}
    for row in rows:
        class_counts[row["publication_class"]] = class_counts.get(row["publication_class"], 0) + 1
        match_counts[row["orkhevi_match_kind"]] = match_counts.get(row["orkhevi_match_kind"], 0) + 1

    metadata = {
        "source": source,
        "endpoint": ENDPOINT,
        "method": None if args.input_json else "POST",
        "payload": payload,
        "processed_at": processed_at,
        "http_status": status,
        "response_content_type": response_content_type,
        "response_sha256": sha256,
        "content_listCount": content.get("listCount"),
        "content_page": content.get("page"),
        "normalized_row_count": len(rows),
        "publication_class_counts": class_counts,
        "orkhevi_match_kind_counts": match_counts,
        "parallel_api_listCount": document.get("api", {}).get("listCount") if isinstance(document.get("api"), dict) else None,
        "semantic_warning": (
            "Records are Telasi public outage publications/search hits, not a complete incident log. "
            "A search hit for ორხევი can refer to the settlement, industrial zone, named exits/streets, "
            "or broader Orkhevi-associated addresses. restoration_eta is a stated estimate, not actual duration."
        ),
    }
    (output_dir / "fetch_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    fieldnames = [
        "id", "publication_date", "created_at", "updated_at", "status", "content_type",
        "taxonomy_ids", "publication_class", "orkhevi_match_kind", "slug", "title",
        "teaser_text", "editor_text", "restoration_eta", "announced_windows", "editor_html",
    ]
    with (output_dir / "records.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    for row in rows:
        print(
            f"{row['id']}\t{row['publication_class']}\t{row['orkhevi_match_kind']}\t"
            f"{row['publication_date']}\tETA={row['restoration_eta'] or '-'}\t{row['title']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
