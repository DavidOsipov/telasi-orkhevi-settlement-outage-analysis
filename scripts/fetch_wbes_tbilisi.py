#!/usr/bin/env python3
"""Fetch and normalize the official WBES 2023 Tbilisi infrastructure subgroup.

The raw response is preserved byte-for-byte. Published decimal strings are also
preserved verbatim; any fraction emitted by this tool is only the exact rational
representation of the displayed API string, not an unrounded survey estimate.

WBES "typical month" is preserved as a survey concept and is not silently
reinterpreted as an arithmetic mean Gregorian calendar month.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from urllib.request import Request, urlopen

DEFAULT_URL = (
    "https://extdataportal.worldbank.org/api/esapi/"
    "GetEconomyCutsData/economyid/74/year/2023/topicid/8/cutsid/3/?lang=en"
)
SOURCE_TOPIC_PAGE = "https://www.enterprisesurveys.org/en/data/exploretopics/infrastructure-and-climate"
SOURCE_MICRODATA_C7 = "https://microdata.worldbank.org/catalog/6443/variable/F1/V57?name=c7"
DEFAULT_OUTPUT_DIR = Path("artifacts/wbes/tbilisi-2023")

WANTED_FIELDS = {
    "in16": "Percent of firms experiencing electrical outages",
    "bready_in2": "[B-READY] Average number of electrical outages in a typical month",
    "bready_in3_median": "[B-READY] Duration, in hours, of a typical electrical outage [median]",
    "in12": "Percent of firms identifying electricity as a major or very severe constraint",
    "bready_in9": "[B-READY] Percent of firms owning or sharing a generator",
}

TYPICAL_MONTH_NOTE = (
    "WBES 'typical month' is a survey concept for the most common type of month regarding outages, "
    "not an arithmetic mean Gregorian calendar month. The published typical-month value cannot be "
    "exactly converted to 'one outage every N days' and is not definition-identical to the SITE_B "
    "inter-arrival metric."
)


def exact_fraction_from_display(text: str) -> dict:
    value = Fraction(text)
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "exact_fraction_from_display": (
            str(value.numerator)
            if value.denominator == 1
            else f"{value.numerator}/{value.denominator}"
        ),
    }


def fetch(url: str, timeout: int) -> tuple[bytes, dict]:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "telasi-orkhevi-settlement-outage-analysis/1.0 (+reproducible research)",
        },
        method="GET",
    )
    with urlopen(request, timeout=timeout) as response:
        body = response.read()
        metadata = {
            "http_status": response.status,
            "content_type": response.headers.get("Content-Type"),
            "date_header": response.headers.get("Date"),
        }
    return body, metadata


def normalize(raw: bytes, source_url: str, fetched_at: str) -> dict:
    data = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(data, list):
        raise ValueError("WBES endpoint response is not a JSON list")

    tbilisi_rows = [row for row in data if isinstance(row, dict) and row.get("subCut") == "Tbilisi"]
    if not tbilisi_rows:
        raise ValueError("No Tbilisi subgroup rows found")

    by_field: dict[str, dict] = {}
    for row in tbilisi_rows:
        field = row.get("queryFieldName")
        if isinstance(field, str):
            if field in by_field:
                raise ValueError(f"Duplicate Tbilisi queryFieldName: {field}")
            by_field[field] = row

    missing = sorted(set(WANTED_FIELDS) - set(by_field))
    if missing:
        raise ValueError(f"Missing expected Tbilisi indicators: {', '.join(missing)}")

    indicators: dict[str, dict] = {}
    for field, expected_label in WANTED_FIELDS.items():
        row = by_field[field]
        actual_label = row.get("indicator")
        if actual_label != expected_label:
            raise ValueError(
                f"Tbilisi indicator label changed for {field}: expected {expected_label!r}, got {actual_label!r}"
            )
        published = row.get("country")
        if not isinstance(published, str):
            raise ValueError(
                f"Tbilisi indicator {field} country value is not a JSON string; refusing to claim lexical precision"
            )
        indicators[field] = {
            "indicator_id": row.get("indicatorId"),
            "query_field_name": field,
            "indicator": actual_label,
            "published_value": published,
            **exact_fraction_from_display(published),
        }

    return {
        "schema_version": 1,
        "source": "World Bank Enterprise Surveys",
        "economy": "Georgia",
        "survey_year": 2023,
        "topic_id": 8,
        "cut_id": 3,
        "cut": "Location",
        "subcut": "Tbilisi",
        "source_endpoint": source_url,
        "source_topic_page": SOURCE_TOPIC_PAGE,
        "source_microdata_variable_c7": SOURCE_MICRODATA_C7,
        "fetched_at_utc": fetched_at,
        "raw_response_bytes": len(raw),
        "raw_response_sha256": hashlib.sha256(raw).hexdigest(),
        "tbilisi_row_count": len(tbilisi_rows),
        "precision_note": (
            "WBES API values are published/display values with finite decimal precision. "
            "The rational forms in this file exactly represent those returned decimal strings; "
            "they do not recover hidden unrounded weighted survey estimates."
        ),
        "typical_month_semantics_note": TYPICAL_MONTH_NOTE,
        "indicators": indicators,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()

    fetched_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    raw, http_metadata = fetch(args.url, args.timeout)
    normalized = normalize(raw, args.url, fetched_at)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = args.output_dir / "wbes-tbilisi-topic8-location-cuts.raw.json"
    normalized_path = args.output_dir / "wbes-tbilisi-benchmark.json"
    metadata_path = args.output_dir / "wbes-tbilisi-fetch-metadata.json"

    raw_path.write_bytes(raw)
    normalized_path.write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    metadata = {
        "source_endpoint": args.url,
        "source_topic_page": SOURCE_TOPIC_PAGE,
        "source_microdata_variable_c7": SOURCE_MICRODATA_C7,
        "fetched_at_utc": fetched_at,
        **http_metadata,
        "raw_response_bytes": len(raw),
        "raw_response_sha256": normalized["raw_response_sha256"],
        "typical_month_semantics_note": TYPICAL_MONTH_NOTE,
        "raw_file": raw_path.name,
        "normalized_file": normalized_path.name,
    }
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(f"Fetched {args.url}")
    print(f"Raw bytes: {len(raw)}")
    print(f"Raw SHA-256: {normalized['raw_response_sha256']}")
    for field in WANTED_FIELDS:
        item = normalized["indicators"][field]
        print(
            f"{field}: {item['published_value']} "
            f"(exact fraction from displayed value: {item['exact_fraction_from_display']})"
        )
    print("WBES typical-month values are not converted to a fixed day interval.")
    print(f"Wrote {raw_path}")
    print(f"Wrote {normalized_path}")
    print(f"Wrote {metadata_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
