#!/usr/bin/env python3
"""Compare Telasi public publication ETAs with curated resident SMS ETAs.

Exact ETA matching is a corroboration test. A non-match is not evidence that the
subscriber interruption did not occur. A global negative conclusion is only
allowed when two full pagination passes agree and the loaded CSV is internally
consistent with the API-reported total and fetch metadata.
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


def load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assess_corpus_completeness(api_records: list[dict], api_meta: dict) -> tuple[bool, list[str]]:
    """Recompute whether a loaded corpus is safe for global negative claims.

    Metadata is necessary but not sufficient: records.csv can be stale, truncated,
    or paired with the wrong fetch_metadata.json. Fail closed on any mismatch.
    """
    reasons: list[str] = []
    if api_meta.get("complete_against_reported_total") is not True:
        reasons.append("metadata_not_complete")
    if api_meta.get("stable_across_two_full_passes") is not True:
        reasons.append("two_pass_stability_not_proven")

    reported_total = api_meta.get("reported_total")
    fetched_unique_count = api_meta.get("fetched_unique_count")
    if not isinstance(reported_total, int) or reported_total < 0:
        reasons.append("invalid_reported_total")
    if not isinstance(fetched_unique_count, int) or fetched_unique_count < 0:
        reasons.append("invalid_fetched_unique_count")
    if isinstance(reported_total, int) and isinstance(fetched_unique_count, int) and fetched_unique_count != reported_total:
        reasons.append("metadata_count_mismatch")
    if isinstance(reported_total, int) and len(api_records) != reported_total:
        reasons.append("records_csv_count_mismatch")

    ids = [row.get("id", "") for row in api_records]
    if api_records and (any(not value for value in ids) or len(set(ids)) != len(ids)):
        reasons.append("records_csv_ids_missing_or_nonunique")

    return not reasons, reasons


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-dir", default="artifacts/telasi_api/all")
    parser.add_argument("--orkhevi-dir", default="artifacts/telasi_api/orkhevi")
    parser.add_argument("--fetch", action="store_true", help="Fetch a two-pass stable paginated corpus plus Orkhevi search")
    parser.add_argument("--require-complete", action="store_true", help="Fail unless two-pass stability and CSV/metadata consistency are proven")
    parser.add_argument("--output", default="artifacts/telasi_api/comparison.json")
    args = parser.parse_args()

    api_dir = Path(args.api_dir)
    orkhevi_dir = Path(args.orkhevi_dir)

    if args.fetch:
        subprocess.run(
            [sys.executable, str(FETCHER), "--all-pages", "--per-page", "100", "--output-dir", str(api_dir)],
            check=True,
        )
        subprocess.run(
            [sys.executable, str(FETCHER), "--search-text", "ორხევი", "--output-dir", str(orkhevi_dir)],
            check=True,
        )

    api_records = load_csv(api_dir / "records.csv")
    api_meta = load_json(api_dir / "fetch_metadata.json")
    orkhevi_records = load_csv(orkhevi_dir / "records.csv")
    sms = load_sms_etas()

    complete, completeness_failures = assess_corpus_completeness(api_records, api_meta)
    reported_total = api_meta.get("reported_total", api_meta.get("content_listCount"))
    if args.require_complete and not complete:
        raise SystemExit(
            "API corpus is not internally consistent and stable enough for corpus-wide negative claims: "
            + ", ".join(completeness_failures)
        )

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

    content_fingerprints = Counter(
        (r["title"], r["editor_text"], r["restoration_eta"])
        for r in api_records
    )
    likely_duplicate_rows = sum(count - 1 for count in content_fingerprints.values() if count > 1)

    if complete:
        interpretation = (
            "Exact ETA matching was run against two agreeing count-complete pagination passes. "
            "A zero exact-match result means no matching public publication ETA was present in that stable reconstructed public corpus; "
            "it does not falsify resident SMS or prove the public site is a complete subscriber-level outage log."
        )
    else:
        interpretation = (
            "The supplied API corpus is partial. Exact matches are valid positive corroboration, but zero matches "
            "cannot support a corpus-wide negative conclusion."
        )

    result = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "api_corpus_complete_against_reported_total": complete,
        "api_corpus_stable_across_two_full_passes": api_meta.get("stable_across_two_full_passes") is True,
        "api_completeness_failures": completeness_failures,
        "api_reported_total": reported_total,
        "api_publication_count_loaded": len(api_records),
        "orkhevi_search_publication_count": len(orkhevi_records),
        "orkhevi_search_class_counts": dict(Counter(r["publication_class"] for r in orkhevi_records)),
        "sms_eta_value_count": len(sms),
        "sms_eta_values_with_exact_public_api_match": len(matches),
        "sms_eta_values_without_exact_public_api_match": len(nonmatches),
        "likely_duplicate_publication_rows_by_normalized_content": likely_duplicate_rows,
        "matches": matches,
        "nonmatches": nonmatches,
        "interpretation": interpretation,
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
