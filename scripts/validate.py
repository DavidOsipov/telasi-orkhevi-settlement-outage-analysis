#!/usr/bin/env python3
from pathlib import Path
import csv
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "data" / "processed" / "events.csv"
rows = list(csv.DictReader(path.open(encoding="utf-8")))

assert rows, "events.csv is empty"
dates = [date.fromisoformat(r["date"]) for r in rows]
assert dates == sorted(dates), "events.csv must be sorted by date"
assert len(dates) == len(set(dates)), "event-level dates must be unique in conservative dataset"

assert sum(r["category"] == "emergency" for r in rows) == 22
assert sum(r["category"] == "network_switching" for r in rows) == 1
assert sum(r["category"] == "planned" and r["status"] != "cancelled" for r in rows) == 9
assert sum(r["category"] == "planned" and r["status"] == "cancelled" for r in rows) == 2

import re
for raw in (ROOT/"data/raw").glob("*.txt"):
    text = raw.read_text(encoding="utf-8")
    # A public raw file must not contain a numeric subscriber/account value.
    assert not re.search(r"abonentis nomeri:\s*\d+", text, flags=re.I)
    assert not re.search(r"ab\.#\s*\d+", text, flags=re.I)

print("Validation OK")
