"""Pure parsing/request helpers for Telasi public power-outage publications."""

from __future__ import annotations

import hashlib
import html
import json
import re
from datetime import datetime
from html.parser import HTMLParser
from urllib.request import Request, urlopen

ENDPOINT = "https://app.telasi.ge/api/view/telasi/getPoweroutages"
DEFAULT_SEARCH_TEXT = "ორხევი"
DEFAULT_TAXONOMY = (2769, 2770)
DEFAULT_PER_PAGE = 100

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
    """Return YYYY-MM-DD HH:MM for an explicitly stated restoration ETA.

    Telasi source HTML sometimes inserts spaces between individual digits, so
    the parser intentionally accepts forms such as ``1 1 .07.2026 04 : 31``.
    Source-side year/date mistakes are not corrected here.
    """
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
    """Classify empirically observed taxonomy IDs.

    These labels are observations from the captured corpus, not a documented
    Telasi taxonomy specification.
    """
    ids = set(taxonomy_ids(item))
    if ids == {2769}:
        return "planned_or_scheduled"
    if ids == {2770}:
        return "unplanned"
    return "unknown"


def orkhevi_match_kind(text: str) -> str:
    """Describe why a text-search hit appears related to Orkhevi."""
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
    # Payload observed from the site's search interaction.
    return {"contentType": "poweroutage", "searchText": search_text}


def make_list_payload(page_number: int, per_page: int, selected_lang: str) -> dict:
    # Separate payload observed from the site's paginated listing.
    return {
        "searchText": "",
        "pageNumber": page_number,
        "perPage": per_page,
        # Spelling preserved verbatim from Telasi's frontend payload.
        "selectedlan": selected_lang,
        "taxonomy": {"content_poweroutage": list(DEFAULT_TAXONOMY)},
    }


def fetch_raw(payload: dict, selected_lang: str, timeout: float) -> tuple[bytes, int, str]:
    # ensure_ascii=False is critical: Georgian must remain UTF-8 JSON. A
    # browser Copy-as-cURL -> Postman import path was observed mangling it.
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    request = Request(
        ENDPOINT,
        data=body,
        method="POST",
        headers={
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json; charset=utf-8",
            "lang": selected_lang,
            "Origin": "https://www.telasi.ge",
            "Referer": "https://www.telasi.ge/",
            "User-Agent": "telasi-orkhevi-settlement-outage-analysis/1.0",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read(), response.status, response.headers.get("Content-Type", "")


def parse_document(raw: bytes) -> dict:
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Telasi response is not valid UTF-8 JSON") from exc
    if not isinstance(document, dict):
        raise ValueError("Telasi response JSON is not an object")
    return document


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
