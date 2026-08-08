#!/usr/bin/env python3
"""Compare Telasi public outage publications with curated SMS notification groups.

This script deliberately compares *published restoration ETAs* with SMS
restoration ETAs. A match is corroborative evidence, while a non-match does not
mean that the subscriber interruption did not occur: the public website is a
publication layer and need not contain every subscriber-level interruption.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROUPS = ROOT / "data" / "derived" / "notification_groups.csv"
FETCHER = ROOT / "scripts" / "fetch_telasi_api.py"


def load_sms_etas() -> list[dict]:
    rows: list[dict] = []
    with GROUPS.open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["category"] != "emergency":
                continue
            for eta in [x for x in row["eta_values"].split(";") if x]:
                rows.append(
                    {
                        "group_id": row["group_id"],
                        "anchor_date": row["anchor_date"],
                        "evidence_sites": row["evidence_sites"],
                        "eta": f"{row['anchor_date']} {eta}",
                    }
                )
    return rows


def load_api_records(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-dir", default="artifacts/telasi_api/all")
    parser.add_argument("--orkhevi-dir", default="artifacts/telasi_api/orkhevi")
    parser.add_argument("--fetch", action="store_true", help="Fetch fresh Telasi API corpus first")
    parser.add_argument("--output", default="artifacts/telasi_api/comparison.json")
    args = parser.parse_args()

    api_dir = Path(args.api_dir)
    orkhevi_dir = Path(args.orkhevi_dir)

    if args.fetch:
        subprocess.run(
            [sys.executable, str(FETCHER), "--search-text", "", "--per-page", "2000", "--output-dir", str(api_dir)],
            check=True,
        )
        subprocess.run(
            [sys.executable, str(FETCHER), "--search-text", "ორხევ", "--per-page", "100", "--output-dir", str(orkhevi_dir)],
            check=True,
        )

    api_records = load_api_records(api_dir / "records.csv")
    orkhevi_records = load_api_records(orkhevi_dir / "records.csv")
    sms = load_sms_etas()

    by_eta: dict[str, list[dict]] = defaultdict(list)
    for row in api_records:
        if row["restoration_eta"]:
            by_eta[row["restoration_eta"]].append(row)

    matches = []
    nonmatches = []
    for item in sms:
        api_matches = by_eta.get(item["eta"], [])
        result = {
            **item,
            "api_match_count": len(api_matches),
            "api_publication_ids": [r["id"] for r in api_matches],
        }
        (matches if api_matches else nonmatches).append(result)

    dated_api = [r for r in api_records if r["publication_date"]]
    content_fingerprints = Counter(
        (r["title"], r["editor_text"], r["restoration_eta"])
        for r in api_records
    )
    likely_duplicate_rows = sum(count - 1 for count in content_fingerprints.values() if count > 1)

    result = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "api_publication_count": len(api_records),
        "api_publication_date_min": min((r["publication_date"] for r in dated_api), default=""),
        "api_publication_date_max": max((r["publication_date"] for r in dated_api), default=""),
        "orkhevi_search_publication_count": len(orkhevi_records),
        "orkhevi_search_class_counts": dict(Counter(r["publication_class"] for r in orkhevi_records)),
        "sms_eta_value_count": len(sms),
        "sms_eta_values_with_exact_public_api_match": len(matches),
        "sms_eta_values_without_exact_public_api_match": len(nonmatches),
        "likely_duplicate_publication_rows_by_normalized_content": likely_duplicate_rows,
        "matches": matches,
        "nonmatches": nonmatches,
        "interpretation": (
            "Exact ETA matching is a corroboration test only. Zero matches do not falsify the SMS record; "
            "they indicate that the public Telasi publication corpus is not a complete subscriber-level outage log."
        ),
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
