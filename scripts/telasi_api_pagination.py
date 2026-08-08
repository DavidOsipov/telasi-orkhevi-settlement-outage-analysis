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


def _item_digest(item: dict) -> str:
    canonical = json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _fetch_list_pass(
    *,
    output_dir: Path,
    per_page: int,
    selected_lang: str,
    timeout: float,
    max_pages: int | None,
) -> tuple[dict[str, dict], dict]:
    """Fetch one paginated pass and preserve every raw page.

    This proves count-completeness only for this pass. Snapshot stability is
    established separately by comparing two complete passes.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    unique: dict[str, dict] = {}
    conflicting_duplicate_keys: set[str] = set()
    page_meta: list[dict] = []
    reported_total: int | None = None
    reported_totals_seen: list[int] = []
    effective_page_size: int | None = None
    page_number = 1
    stop_reason = ""

    while True:
        payload = make_list_payload(page_number, per_page, selected_lang)
        raw, status, content_type = fetch_raw(payload, selected_lang, timeout)
        page_path = output_dir / f"page-{page_number:03d}.json"
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
            page_meta.append(
                {
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
                }
            )
            break

        before = len(unique)
        for item in items:
            key = _item_key(item)
            if key in unique:
                if _item_digest(unique[key]) != _item_digest(item):
                    conflicting_duplicate_keys.add(key)
                continue
            unique[key] = item
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
            # Cushion handles modest live movement without allowing an infinite loop.
            if page_number > estimated + 3:
                stop_reason = "estimated_page_bound_exceeded"
                break

    list_count_stable = bool(reported_totals_seen) and len(set(reported_totals_seen)) == 1
    count_complete = (
        reported_total is not None
        and len(unique) == reported_total
        and list_count_stable
        and not conflicting_duplicate_keys
        and stop_reason == "reported_total_reached"
    )
    metadata = {
        "reported_total": reported_total,
        "fetched_unique_count": len(unique),
        "requested_per_page": per_page,
        "effective_first_page_size": effective_page_size,
        "raw_page_count": len(page_meta),
        "reported_totals_seen": reported_totals_seen,
        "list_count_stable_across_pages": list_count_stable,
        "count_complete_against_reported_total": count_complete,
        "conflicting_duplicate_keys": sorted(conflicting_duplicate_keys),
        "stop_reason": stop_reason,
        "pages": page_meta,
    }
    return unique, metadata


def _snapshot_fingerprints(items: dict[str, dict]) -> dict[str, str]:
    return {key: _item_digest(value) for key, value in items.items()}


def fetch_all_list_pages(
    *,
    output_dir: Path,
    per_page: int,
    selected_lang: str,
    timeout: float,
    max_pages: int | None,
) -> tuple[dict, dict]:
    """Fetch two complete passes and require a stable reconstructed corpus.

    A single page-number/offset-style walk can mix states if the live API changes
    while pages are being fetched. Therefore a corpus is marked complete only
    when two independently fetched count-complete passes agree on reported
    total, record identities, and normalized source-record contents.

    This still does not make the public API an atomic database snapshot; it is a
    conservative two-pass stability check suitable for gating corpus-wide
    negative statements in this repository.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    pass1_items, pass1 = _fetch_list_pass(
        output_dir=output_dir / "raw_pages_pass_1",
        per_page=per_page,
        selected_lang=selected_lang,
        timeout=timeout,
        max_pages=max_pages,
    )
    pass2_items, pass2 = _fetch_list_pass(
        output_dir=output_dir / "raw_pages_pass_2",
        per_page=per_page,
        selected_lang=selected_lang,
        timeout=timeout,
        max_pages=max_pages,
    )

    stable_total = pass1["reported_total"] == pass2["reported_total"]
    stable_identity_set = set(pass1_items) == set(pass2_items)
    stable_contents = _snapshot_fingerprints(pass1_items) == _snapshot_fingerprints(pass2_items)
    stable_across_two_passes = stable_total and stable_identity_set and stable_contents
    count_complete_both = (
        pass1["count_complete_against_reported_total"]
        and pass2["count_complete_against_reported_total"]
    )
    complete = bool(count_complete_both and stable_across_two_passes)

    # Use pass 2 as the final aggregate only when both passes agree; otherwise
    # preserve it for diagnostics but mark the result incomplete.
    final_items = pass2_items
    reported_total = pass2["reported_total"]
    aggregate = {
        "api": {"listCount": 0, "page": 1, "list": []},
        "content": {
            "listCount": reported_total,
            "page": 1,
            "list": list(final_items.values()),
        },
        "_derived_aggregate": {
            "source": ENDPOINT,
            "raw_passes": 2,
            "count_complete_against_reported_total": bool(count_complete_both),
            "stable_across_two_full_passes": stable_across_two_passes,
            "complete_against_reported_total": complete,
        },
    }
    (output_dir / "aggregate.json").write_text(
        json.dumps(aggregate, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    fetch_meta = {
        "mode": "all_pages_two_pass_stability_check",
        "endpoint": ENDPOINT,
        "reported_total": reported_total,
        "fetched_unique_count": len(final_items),
        "requested_per_page": per_page,
        "count_complete_against_reported_total": bool(count_complete_both),
        "stable_reported_total_across_passes": stable_total,
        "stable_identity_set_across_passes": stable_identity_set,
        "stable_contents_across_passes": stable_contents,
        "stable_across_two_full_passes": stable_across_two_passes,
        "complete_against_reported_total": complete,
        "passes": [pass1, pass2],
        "semantic_warning": (
            "Two agreeing complete pagination passes reduce live-list movement risk but do not create an atomic "
            "database snapshot. Corpus-wide negative statements apply only to the stable public publication state "
            "reconstructed by these passes, not to Telasi's internal incident ledger."
        ),
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
            "semantic_warning": metadata.get("semantic_warning") or (
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
