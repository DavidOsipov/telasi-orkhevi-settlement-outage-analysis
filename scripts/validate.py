#!/usr/bin/env python3
from pathlib import Path
import csv, re, hashlib, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_transcripts"
NOTIFICATIONS = ROOT / "data" / "derived" / "notifications.csv"
GROUPS = ROOT / "data" / "derived" / "notification_groups.csv"
EXTERNAL = ROOT / "data" / "external_context.csv"

# Rebuild notifications from source transcripts so derived message rows cannot silently drift.
subprocess.run([sys.executable, str(ROOT/"scripts"/"build_notifications.py")], check=True)

notifications = list(csv.DictReader(NOTIFICATIONS.open(encoding="utf-8")))
groups = list(csv.DictReader(GROUPS.open(encoding="utf-8")))
notification_by_id = {r["message_id"]: r for r in notifications}

assert len(notification_by_id) == len(notifications), "message_id values must be unique"
assert notifications, "notifications.csv is empty"
assert groups, "notification_groups.csv is empty"

allowed_kinds = {"emergency","network_switching","planned_notice","planned_cancellation","planned_update","unclassified"}
assert all(r["message_kind"] in allowed_kinds for r in notifications)

# Every group must point to real source-message rows and evidence sites must match them.
for g in groups:
    ids = [x for x in g["supporting_message_ids"].split(";") if x]
    assert ids, f"{g['group_id']} has no supporting messages"
    missing = [x for x in ids if x not in notification_by_id]
    assert not missing, f"{g['group_id']} references missing messages: {missing}"
    source_sites = {notification_by_id[x]["site_id"] for x in ids}
    stated_sites = set(g["evidence_sites"].split(";"))
    assert source_sites == stated_sites, f"{g['group_id']} evidence_sites mismatch: {source_sites} vs {stated_sites}"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", g["anchor_date"]), f"Bad anchor date in {g['group_id']}"
    if g["category"] in {"emergency","network_switching"}:
        assert g["anchor_date_kind"] == "restoration_eta_date"
    if g["category"] == "planned":
        assert g["anchor_date_kind"] == "scheduled_interruption_date"
    directly_dated = {
        notification_by_id[x]["anchor_date"]
        for x in ids
        if notification_by_id[x]["anchor_date"]
    }
    assert not directly_dated or directly_dated == {g["anchor_date"]}, (
        f"{g['group_id']} anchor date disagrees with supporting messages: {directly_dated}"
    )

# No subscriber/account numbers in public source transcripts.
for path in SOURCE_DIR.glob("*.txt"):
    text = path.read_text(encoding="utf-8")
    assert not re.search(r"abonentis nomeri:\s*\d+", text, re.I), f"Subscriber number leaked in {path.name}"
    assert not re.search(r"ab\.#\s*\d+", text, re.I), f"Subscriber number leaked in {path.name}"

# Confirm the known exact duplicate is preserved at message level, rather than silently discarded.
dupe_hashes = {}
for r in notifications:
    dupe_hashes.setdefault(r["text_sha256"], []).append(r["message_id"])
exact_dupes = [ids for ids in dupe_hashes.values() if len(ids) > 1]
assert any(set(ids) == {"SITE_A-005","SITE_A-006"} for ids in exact_dupes), "Expected 2026-04-07 exact duplicate not detected"

# External context rows must be sourced.
external = list(csv.DictReader(EXTERNAL.open(encoding="utf-8")))
assert external and all(r["source_url"].startswith("https://") for r in external)

# Guard against recurrence of the old date-level/event-level conflation.
assert "events.csv" not in {p.name for p in (ROOT/"data"/"derived").glob("*.csv")}, "Do not reintroduce ambiguous events.csv"

print(f"Validation OK: {len(notifications)} source-message rows, {len(groups)} curated notification groups")
