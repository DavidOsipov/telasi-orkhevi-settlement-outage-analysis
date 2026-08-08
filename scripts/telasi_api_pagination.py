"""Pagination and normalized-output helpers for Telasi public API data."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

from telasi_api_core import ENDPOINT, content_object, fetch_raw, make_list_payload, normalize_rows, parse_document

def _item_key(item: dict) -> str:
    if item.get("id") is not None:
        return f"id:{item['id']}"
    canonical = json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def fetch_all_list_pages(
    *,
    output_dir: Path,
    per_page: int,
    selected_lang: str,
    timeout: float,
    max_pages: int | None,
) -> tuple[dict, dict]:
    """Fetch the currently exposed paginated list and preserve every raw page.

    Telasi may cap ``perPage`` below the requested value. Pagination therefore
    uses the number of records actually returned by the first page to estimate
    how many pages are required, and collection stops only when the reported
    total has been reached or progress becomes impossible.
    """
    raw_dir = output_dir / "raw_pages"
    raw_dir.mkdir(parents=True, exist_ok=True)

    unique: dict[str, dict] = {}
    page_meta: list[dict] = []
    reported_total: int | None = None
    reported_totals_seen: list[int] = []
    effective_page_size: int | None = None
    page_number = 1
    stop_reason = ""

    while True:
        payload = make_list_payload(page_number, per_page, selected_lang)
        raw, status, content_type = fetch_raw(payload, selected_lang, timeout)
        page_path = raw_dir / f"page-{page_number:03d}.json"
        page_path.write_bytes(raw)
        document = parse_document(raw)
        content = content_object(document)
        items = [item for item in content["list"] if isinstance(item, dict)]

        value = content.get("listCount")
        if isinstance(value, int) and value >= 0:
            reported_totals_seen.append(value)
        if reported_total is None:
            reported_total = value if isinstance(value, int) and value >= 0 else None
            effective_page_size = len(items) or None

        response_page = content.get("page")
        if isinstance(response_page, int) and response_page != page_number:
            stop_reason = "response_page_mismatch"
            page_meta.append({
                "page_number": page_number,
                "payload": payload,
                "http_status": status,
                "response_content_type": content_type,
                "response_bytes": len(raw),
                "response_sha256": hashlib.sha256(raw).hexdigest(),
                "returned_items": len(items),
                "new_unique_items": 0,
                "content_listCount": content.get("listCount"),
                "content_page": response_page,
            })
            break

        before = len(unique)
        for item in items:
            unique.setdefault(_item_key(item), item)
        added = len(unique) - before

        page_meta.append(
            {
                "page_number": page_number,
                "payload": payload,
                "http_status": status,
                "response_content_type": content_type,
                "response_bytes": len(raw),
                "response_sha256": hashlib.sha256(raw).hexdigest(),
                "returned_items": len(items),
                "new_unique_items": added,
                "content_listCount": content.get("listCount"),
                "content_page": content.get("page"),
            }
        )

        if reported_total is not None and len(unique) >= reported_total:
            stop_reason = "reported_total_reached"
            break
        if not items:
            stop_reason = "empty_page_before_reported_total"
            break
        if added == 0:
            stop_reason = "no_new_unique_items"
            break

        page_number += 1
        if max_pages is not None and page_number > max_pages:
            stop_reason = "max_pages_reached"
            break
        if max_pages is None and reported_total is not None and effective_page_size:
            estimated = math.ceil(reported_total / effective_page_size)
            # A small cushion handles page movement while the live site changes.
            if page_number > estimated + 3:
                stop_reason = "estimated_page_bound_exceeded"
                break

    list_count_stable = len(set(reported_totals_seen)) <= 1
    complete = reported_total is not None and len(unique) == reported_total and list_count_stable
    aggregate = {
        "api": {"listCount": 0, "page": 1, "list": []},
        "content": {
            "listCount": reported_total,
            "page": 1,
            "list": list(unique.values()),
        },
        "_derived_aggregate": {
            "source": ENDPOINT,
            "raw_pages": len(page_meta),
            "complete_against_reported_total": complete,
            "stop_reason": stop_reason,
        },
    }
    aggregate_path = output_dir / "aggregate.json"
    aggregate_path.write_text(json.dumps(aggregate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    fetch_meta = {
        "mode": "all_pages",
        "endpoint": ENDPOINT,
        "reported_total": reported_total,
        "fetched_unique_count": len(unique),
        "requested_per_page": per_page,
        "effective_first_page_size": effective_page_size,
        "raw_page_count": len(page_meta),
        "reported_totals_seen": reported_totals_seen,
        "list_count_stable_across_pages": list_count_stable,
        "complete_against_reported_total": complete,
        "stop_reason": stop_reason,
        "pages": page_meta,
    }
    return aggregate, fetch_meta


def write_normalized_outputs(document: dict, output_dir: Path, metadata: dict) -> None:
    rows = normalize_rows(document)
    class_counts: dict[str, int] = {}
    match_counts: dict[str, int] = {}
    for row in rows:
        class_counts[row["publication_class"]] = class_counts.get(row["publication_class"], 0) + 1
        match_counts[row["orkhevi_match_kind"]] = match_counts.get(row["orkhevi_match_kind"], 0) + 1

    content = content_object(document)
    metadata.update(
        {
            "content_listCount": content.get("listCount"),
            "normalized_row_count": len(rows),
            "publication_class_counts": class_counts,
            "orkhevi_match_kind_counts": match_counts,
            "parallel_api_listCount": document.get("api", {}).get("listCount") if isinstance(document.get("api"), dict) else None,
            "semantic_warning": (
                "Records are Telasi public outage publications/search hits, not a complete incident log. "
                "A search hit for Orkhevi may refer to the settlement, industrial zone, named exits/streets, "
                "or broader Orkhevi-associated addresses. restoration_eta is a stated estimate, not actual duration."
            ),
        }
    )
    (output_dir / "fetch_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )

    fieldnames = [
        "id", "publication_date", "created_at", "updated_at", "status", "content_type",
        "taxonomy_ids", "publication_class", "orkhevi_match_kind", "slug", "title",
        "teaser_text", "editor_text", "restoration_eta", "announced_windows", "editor_html",
    ]
    with (output_dir / "records.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
