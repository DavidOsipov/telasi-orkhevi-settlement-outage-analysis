#!/usr/bin/env python3
from pathlib import Path
import csv, re, hashlib
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "source_transcripts"
OUT = ROOT / "data" / "derived" / "notifications.csv"

SOURCES = [
    ("SITE_A", SOURCE_DIR / "site_a_sms_redacted.txt"),
    ("SITE_B", SOURCE_DIR / "site_b_sms_redacted.txt"),
]

MONTHS = {m.lower(): i for i, m in enumerate(
    ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], 1
)}

def split_blocks(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    starts = [i for i, line in enumerate(lines)
              if re.match(r'^(gatsnobebt|gacnobeb[tT]|s/s)', line, re.I)]
    blocks = []
    for idx, start in enumerate(starts):
        end = starts[idx + 1] - 1 if idx + 1 < len(starts) else len(lines) - 1
        text = "\n".join(lines[start:end+1]).strip()
        blocks.append((start + 1, end + 1, text))
    return blocks

def iso_date_from_token(token):
    token = token.strip().lstrip("?")
    # DD/MM/YYYY
    m = re.fullmatch(r'(\d{1,2})/(\d{1,2})/(\d{4})', token)
    if m:
        d, mo, y = map(int, m.groups())
        return f"{y:04d}-{mo:02d}-{d:02d}"
    # DD.MM.YYYY
    m = re.fullmatch(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', token)
    if m:
        d, mo, y = map(int, m.groups())
        return f"{y:04d}-{mo:02d}-{d:02d}"
    # DD-Mon-YYYY
    m = re.fullmatch(r'(\d{1,2})-([A-Za-z]{3})-(\d{4})', token)
    if m:
        d, mon, y = m.groups()
        return f"{int(y):04d}-{MONTHS[mon.lower()]:02d}-{int(d):02d}"
    # DD-MM-YY
    m = re.fullmatch(r'(\d{1,2})-(\d{1,2})-(\d{2})', token)
    if m:
        d, mo, y = map(int, m.groups())
        return f"{2000+y:04d}-{mo:02d}-{d:02d}"
    raise ValueError(f"Unsupported date token: {token!r}")

def classify(text):
    low = text.lower()
    if "avariuli gamortvis" in low or "magali zabvis kabelis dazianebis" in low:
        return "emergency"
    if "qselshi gadartvis" in low:
        return "network_switching"
    if "gauqmebulia" in low or ("samushaoebis" in low and "gadadebis" in low and "ar segiwydebat" in low):
        return "planned_cancellation"
    if "gadaudebeli" in low:
        return "planned_notice"
    if "dasrulebis dro gadaido" in low:
        return "planned_update"
    return "unclassified"

def extract_fields(kind, text):
    anchor_date = ""
    anchor_kind = ""
    eta_time = ""
    sched_start = ""
    sched_end = ""

    if kind in {"emergency", "network_switching"}:
        m = re.search(r'\??(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2})', text)
        if m:
            anchor_date = iso_date_from_token(m.group(1))
            anchor_kind = "restoration_eta_date"
            eta_time = m.group(2)
    elif kind == "planned_notice":
        m = re.search(
            r'(\d{1,2}-(?:[A-Za-z]{3}|\d{1,2})-\d{2,4})\s+'
            r'(\d{1,2}(?::\d{2})?(?::\d{2})?\s*(?:AM|PM)?)'
            r'-dan\s+'
            r'(\d{1,2}(?::\d{2})?(?::\d{2})?\s*(?:AM|PM)?)'
            r'-mde',
            text, re.I)
        if m:
            anchor_date = iso_date_from_token(m.group(1))
            anchor_kind = "scheduled_interruption_date"
            sched_start = m.group(2).strip()
            sched_end = m.group(3).strip()
    elif kind == "planned_cancellation":
        # A cancellation can use DD.MM.YYYY or DD-MM-YY.
        m = re.search(r'(\d{1,2}\.\d{1,2}\.\d{4}|\d{1,2}-\d{1,2}-\d{2})', text)
        if m:
            anchor_date = iso_date_from_token(m.group(1))
            anchor_kind = "scheduled_interruption_date"
        tm = re.search(
            r'(\d{1,2}(?::\d{2})?(?::\d{2})?\s*(?:AM|PM)?)'
            r'-dan\s+'
            r'(\d{1,2}(?::\d{2})?(?::\d{2})?\s*(?:AM|PM)?)'
            r'-mde',
            text, re.I)
        if tm:
            sched_start = tm.group(1).strip()
            sched_end = tm.group(2).strip()

    return anchor_date, anchor_kind, eta_time, sched_start, sched_end

rows = []
for site_id, path in SOURCES:
    for seq, (line_start, line_end, text) in enumerate(split_blocks(path), 1):
        message_id = f"{site_id}-{seq:03d}"
        kind = classify(text)
        anchor_date, anchor_kind, eta_time, sched_start, sched_end = extract_fields(kind, text)
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        rows.append({
            "message_id": message_id,
            "site_id": site_id,
            "source_file": path.name,
            "source_line_start": line_start,
            "source_line_end": line_end,
            "message_kind": kind,
            "anchor_date": anchor_date,
            "anchor_date_kind": anchor_kind,
            "eta_time": eta_time,
            "scheduled_start_text": sched_start,
            "scheduled_end_text": sched_end,
            "text_sha256": sha,
        })

OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

print(f"Wrote {len(rows)} notifications to {OUT}")
