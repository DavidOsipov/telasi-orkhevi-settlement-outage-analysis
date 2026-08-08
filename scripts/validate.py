#!/usr/bin/env python3
"""Validate resident-SMS data, curated grouping, and preserved Telasi API evidence.

This script deliberately avoids Python ``assert`` statements so validation
cannot be disabled by running Python with ``-O``.
"""

from __future__ import annotations

from pathlib import Path
import csv
import re
import subprocess
import sys
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_transcripts"
NOTIFICATIONS = ROOT / "data" / "derived" / "notifications.csv"
GROUPS = ROOT / "data" / "derived" / "notification_groups.csv"
EXTERNAL = ROOT / "data" / "external_context.csv"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"Validation failed: {message}")


def parse_clock(value: str) -> datetime:
    value = value.strip()
    for fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p", "%I:%M:%S %p"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    raise SystemExit(f"Validation failed: unsupported clock value {value!r}")


def canonical_clock(value: str) -> str:
    return parse_clock(value).strftime("%H:%M")


def window_hours(start: str, end: str) -> float:
    s = parse_clock(start)
    e = parse_clock(end)
    delta = (e - s).total_seconds() / 3600
    if delta < 0:
        delta += 24
    return delta


# Rebuild notifications so committed derived rows cannot silently drift.
subprocess.run([sys.executable, str(ROOT / "scripts" / "build_notifications.py")], check=True)
raw_notifications = NOTIFICATIONS.read_bytes()
require(b"\r\n" not in raw_notifications, "notifications.csv must use LF line endings for byte-stable regeneration")

notifications = list(csv.DictReader(NOTIFICATIONS.open(encoding="utf-8")))
groups = list(csv.DictReader(GROUPS.open(encoding="utf-8")))
notification_by_id = {r["message_id"]: r for r in notifications}

require(len(notification_by_id) == len(notifications), "message_id values must be unique")
require(bool(notifications), "notifications.csv is empty")
require(bool(groups), "notification_groups.csv is empty")
require(len(notifications) == 56, f"unexpected source-message count: {len(notifications)}")
require(len(groups) == 34, f"unexpected curated group count: {len(groups)}")

allowed_kinds = {"emergency", "network_switching", "planned_notice", "planned_cancellation", "planned_update", "unclassified"}
require(all(r["message_kind"] in allowed_kinds for r in notifications), "unknown message_kind value")
require(not [r for r in notifications if r["message_kind"] == "unclassified"], "unclassified source messages remain")

# Group IDs are date + category + sequence, so multiple same-day groups remain representable.
group_ids = [g["group_id"] for g in groups]
require(len(group_ids) == len(set(group_ids)), "group_id values must be unique")
require(all(re.fullmatch(r"G\d{8}-[ESP]\d{2}", gid) for gid in group_ids), "unexpected group_id format")

allowed_confidence = {"high", "medium", "low"}
for g in groups:
    ids = [x for x in g["supporting_message_ids"].split(";") if x]
    require(bool(ids), f"{g['group_id']} has no supporting messages")
    missing = [x for x in ids if x not in notification_by_id]
    require(not missing, f"{g['group_id']} references missing messages: {missing}")

    source_sites = {notification_by_id[x]["site_id"] for x in ids}
    stated_sites = set(g["evidence_sites"].split(";"))
    require(source_sites == stated_sites, f"{g['group_id']} evidence_sites mismatch: {source_sites} vs {stated_sites}")
    require(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", g["anchor_date"])), f"bad anchor date in {g['group_id']}")
    expected_legacy = "G" + g["anchor_date"].replace("-", "")
    require(g["legacy_group_id"] == expected_legacy, f"bad legacy_group_id in {g['group_id']}: {g['legacy_group_id']}")
    try:
        datetime.strptime(g["anchor_date"], "%Y-%m-%d")
    except ValueError as exc:
        raise SystemExit(f"Validation failed: invalid anchor date in {g['group_id']}: {g['anchor_date']}") from exc
    require(g["grouping_confidence"] in allowed_confidence, f"bad grouping_confidence in {g['group_id']}")

    category_code = {"emergency": "E", "network_switching": "S", "planned": "P"}.get(g["category"])
    require(category_code is not None, f"unknown group category: {g['category']}")
    require(
        g["group_id"].startswith("G" + g["anchor_date"].replace("-", "") + "-" + category_code),
        f"{g['group_id']} does not encode its date/category",
    )

    if g["category"] in {"emergency", "network_switching"}:
        require(g["anchor_date_kind"] == "restoration_eta_date", f"bad anchor semantics in {g['group_id']}")
        source_etas = {notification_by_id[x]["eta_time"] for x in ids if notification_by_id[x]["eta_time"]}
        grouped_etas = {x for x in g["eta_values"].split(";") if x}
        require(source_etas == grouped_etas, f"{g['group_id']} eta_values mismatch: {source_etas} vs {grouped_etas}")
    elif g["category"] == "planned":
        require(g["anchor_date_kind"] == "scheduled_interruption_date", f"bad planned anchor semantics in {g['group_id']}")
        require(not g["eta_values"], f"planned group {g['group_id']} unexpectedly has eta_values")

    directly_dated = {notification_by_id[x]["anchor_date"] for x in ids if notification_by_id[x]["anchor_date"]}
    require(
        not directly_dated or directly_dated == {g["anchor_date"]},
        f"{g['group_id']} anchor date disagrees with supporting messages: {directly_dated}",
    )

    try:
        min_count = int(g["incident_count_min"])
        max_count = int(g["incident_count_max"])
    except ValueError as exc:
        raise SystemExit(f"Validation failed: non-integer incident count in {g['group_id']}") from exc
    require(0 <= min_count <= max_count, f"bad incident count range in {g['group_id']}")

    if g["category"] == "planned" and g["scheduled_start"] and g["scheduled_end"]:
        calculated = window_hours(g["scheduled_start"], g["scheduled_end"])
        try:
            stored = float(g["scheduled_window_hours_explicit"])
        except ValueError as exc:
            raise SystemExit(f"Validation failed: bad stored planned hours in {g['group_id']}") from exc
        require(abs(calculated - stored) < 1e-9, f"bad planned window hours in {g['group_id']}: {stored} != {calculated}")

        supporting_windows = set()
        for x in ids:
            r = notification_by_id[x]
            if r["scheduled_start_text"] and r["scheduled_end_text"]:
                supporting_windows.add((canonical_clock(r["scheduled_start_text"]), canonical_clock(r["scheduled_end_text"])))
        if supporting_windows:
            expected = {(canonical_clock(g["scheduled_start"]), canonical_clock(g["scheduled_end"]))}
            require(
                supporting_windows == expected,
                f"{g['group_id']} scheduled window disagrees with supporting messages: {supporting_windows}",
            )

# No subscriber/account numbers in public source transcripts.
for path in SOURCE_DIR.glob("*.txt"):
    text = path.read_text(encoding="utf-8")
    require(not re.search(r"abonentis nomeri:\s*\d+", text, re.I), f"subscriber number leaked in {path.name}")
    require(not re.search(r"ab\.#\s*\d+", text, re.I), f"subscriber number leaked in {path.name}")

# Confirm the known exact duplicate is preserved at message level.
dupe_hashes: dict[str, list[str]] = {}
for r in notifications:
    dupe_hashes.setdefault(r["text_sha256"], []).append(r["message_id"])
exact_dupes = [ids for ids in dupe_hashes.values() if len(ids) > 1]
require(any(set(ids) == {"SITE_A-005", "SITE_A-006"} for ids in exact_dupes), "expected 2026-04-07 exact duplicate not detected")

# External context rows must be sourced.
external = list(csv.DictReader(EXTERNAL.open(encoding="utf-8")))
require(bool(external), "external_context.csv is empty")
require(all(r["source_url"].startswith("https://") for r in external), "external context row lacks HTTPS source URL")

# Guard against recurrence of the old date-level/event-level conflation.
require("events.csv" not in {p.name for p in (ROOT / "data" / "derived").glob("*.csv")}, "do not reintroduce ambiguous events.csv")


from validate_telasi_snapshots import validate_telasi_snapshots
validate_telasi_snapshots(ROOT)

print(
    f"Validation OK: {len(notifications)} source-message rows, {len(groups)} curated notification groups; "
    "Telasi API snapshots/hashes OK"
)
