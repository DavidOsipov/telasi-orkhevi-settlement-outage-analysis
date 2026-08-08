#!/usr/bin/env python3
from pathlib import Path
import csv, statistics
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parents[1]
GROUPS = ROOT / "data" / "derived" / "notification_groups.csv"

def load_groups():
    rows = []
    with GROUPS.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            r["anchor_date"] = date.fromisoformat(r["anchor_date"])
            rows.append(r)
    return rows

def site_in(row, site_id):
    return site_id in row["evidence_sites"].split(";")

def complete_window_max(dates, days, span_start, span_end):
    """Maximum number of anchor dates in any fully observed calendar window.

    Iterates over every possible calendar-day start. Windows extending beyond
    the supplied record span are never evaluated.
    """
    if not dates or (span_end - span_start).days + 1 < days:
        return None
    date_set = set(dates)
    best = None
    start = span_start
    last_start = span_end - timedelta(days=days - 1)
    while start <= last_start:
        end = start + timedelta(days=days - 1)
        selected = sorted(d for d in date_set if start <= d <= end)
        candidate = (len(selected), start, end, selected)
        if best is None or candidate[0] > best[0]:
            best = candidate
        start += timedelta(days=1)
    return best

rows = load_groups()
all_dates = sorted(r["anchor_date"] for r in rows)
record_start, record_end = min(all_dates), max(all_dates)
record_span_days = (record_end - record_start).days + 1

emergency = [r for r in rows if r["category"] == "emergency"]
switching = [r for r in rows if r["category"] == "network_switching"]
planned = [r for r in rows if r["category"] == "planned"]

print(f"Source-record anchor span: {record_start} to {record_end} inclusive = {record_span_days} calendar days")
print("IMPORTANT: this is a retrospective transcript span, not a proven complete observation window.")
print(f"Emergency notification groups keyed by restoration-ETA date: {len(emergency)}")
print(f"Network-switching notification groups keyed by restoration-ETA date: {len(switching)}")
print(f"Planned-work notification groups keyed by scheduled date: {len(planned)}")
print()

# Emergency ETA-date gap summaries are descriptive only.
em_dates = sorted(r["anchor_date"] for r in emergency)
gaps = [(b-a).days for a,b in zip(em_dates, em_dates[1:])]
print("Emergency ETA-date gaps (descriptive; not verified outage inter-arrival times):")
print(f"  mean={statistics.mean(gaps):.2f} d; median={statistics.median(gaps):.1f} d; min={min(gaps)} d; max={max(gaps)} d")
print()

# Comparable same-source year-over-year descriptive comparison: SITE_A only.
def site_a_ytd(year):
    s, e = date(year,1,1), date(year,8,6)
    selected = [r for r in emergency if site_in(r, "SITE_A") and s <= r["anchor_date"] <= e]
    return len(selected)

n25 = site_a_ytd(2025)
n26 = site_a_ytd(2026)
print("Same-source descriptive comparison (SITE_A only; Jan 1-Aug 6):")
print(f"  2025: {n25} emergency ETA-date groups")
print(f"  2026: {n26} emergency ETA-date groups")
if n25:
    print(f"  descriptive ratio: {n26/n25:.3f} ({(n26/n25-1)*100:+.1f}%)")
print("  No p-value/CI is reported because notification completeness and event independence are not established.")
print()

# Cross-site corroboration in the emergency overlap.
a = {r["anchor_date"]: r for r in emergency if site_in(r, "SITE_A")}
b = {r["anchor_date"]: r for r in emergency if site_in(r, "SITE_B")}
overlap_start = date(2025,12,6)
overlap_end = record_end
a_overlap = {d for d in a if overlap_start <= d <= overlap_end}
b_overlap = {d for d in b if overlap_start <= d <= overlap_end}
shared = a_overlap & b_overlap
union = a_overlap | b_overlap
print(f"Cross-site emergency ETA-date overlap ({overlap_start}..{overlap_end}):")
print(f"  SITE_A groups: {len(a_overlap)}")
print(f"  SITE_B groups: {len(b_overlap)}")
print(f"  shared dates: {len(shared)}")
print(f"  Jaccard(date sets): {len(shared)/len(union):.3f}" if union else "  Jaccard: n/a")
print()

# Planned windows: explicit non-cancelled notices only; do not infer actual downtime.
explicit_planned = [r for r in planned if r["status"] in {"announced","announced_with_possible_undated_update"}]
hours = sum(float(r["scheduled_window_hours_explicit"]) for r in explicit_planned if r["scheduled_window_hours_explicit"])
print(f"Explicit scheduled windows in planned notices without a cancellation signal in the same group: {len(explicit_planned)} groups, {hours:.1f} announced hours")
print("  These are notice-window hours, not verified outage-duration hours.")
print("  The undated 2025-11 planned-work extension is not included beyond the explicit 11:00-14:00 window.")
print()

# Cluster windows: use SITE_B because the 4/5/6 Aug run occurs at one service point,
# and require fully contained windows.
site_b_em = sorted(r["anchor_date"] for r in emergency if site_in(r, "SITE_B"))
site_b_start, site_b_end = min(site_b_em), max(site_b_em)
print("SITE_B complete-window maxima for emergency restoration-ETA dates:")
for w in (3,7,14,24,30):
    result = complete_window_max(site_b_em, w, site_b_start, site_b_end)
    if result:
        count, s, e, selected = result
        print(f"  {w:2d}-day window: max {count} groups, {s}..{e}: " + ", ".join(map(str, selected)))
print()
print("Interpretation: the 4-6 Aug run is three emergency notifications whose restoration ETAs fall on three consecutive dates at SITE_B. Without SMS receipt/restoration timestamps, this is not by itself proof of three distinct outage incidents.")
