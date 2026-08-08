#!/usr/bin/env python3
from pathlib import Path
import csv, math, statistics
from datetime import date, datetime, timedelta
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ROOT / "data" / "processed" / "events.csv"

def load():
    rows = []
    with EVENTS.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            r["date"] = date.fromisoformat(r["date"])
            rows.append(r)
    return rows

def binom_two_sided(k, n, p=0.5):
    # Exact two-sided binomial test using the "probability <= observed" definition.
    def pmf(x):
        return math.comb(n, x) * (p ** x) * ((1-p) ** (n-x))
    obs = pmf(k)
    return min(1.0, sum(pmf(x) for x in range(n+1) if pmf(x) <= obs + 1e-15))

def max_window(dates, days):
    best = None
    for start in dates:
        end = start + timedelta(days=days-1)
        selected = [d for d in dates if start <= d <= end]
        cand = (len(selected), start, end, selected)
        if best is None or cand[0] > best[0]:
            best = cand
    return best

rows = load()
start = min(r["date"] for r in rows)
end = max(r["date"] for r in rows)
obs_days = (end - start).days + 1

emergency = sorted(r["date"] for r in rows if r["category"] == "emergency")
switching = sorted(r["date"] for r in rows if r["category"] == "network_switching")
planned = [r for r in rows if r["category"] == "planned" and r["status"] != "cancelled"]
cancelled = [r for r in rows if r["category"] == "planned" and r["status"] == "cancelled"]

gaps = [(b-a).days for a,b in zip(emergency, emergency[1:])]
emergency_rate_year = len(emergency) / obs_days * 365
unplanned_days = len(set(emergency + switching))
actual_or_announced = unplanned_days + len(planned)

print(f"Observation: {start} to {end} inclusive = {obs_days} days")
print(f"Emergency interruption dates (conservative): {len(emergency)}")
print(f"Network-switching interruption dates: {len(switching)}")
print(f"Non-cancelled planned interruption dates: {len(planned)}")
print(f"Cancelled planned-work dates: {len(cancelled)}")
print(f"All non-cancelled recorded/announced interruption dates: {actual_or_announced}")
print(f"Emergency-date annualized rate: {emergency_rate_year:.2f} per 365 days")
print(f"Emergency gaps: mean={statistics.mean(gaps):.2f} d, median={statistics.median(gaps):.1f} d, min={min(gaps)} d, max={max(gaps)} d")
print()

planned_hours = sum(float(r["announced_window_hours"]) for r in planned)
print(f"Non-cancelled announced planned windows: {planned_hours:.1f} h total; mean={planned_hours/len(planned):.2f} h/event")
print(f"Cancelled announced windows: {sum(float(r['announced_window_hours']) for r in cancelled):.1f} h")
print()

# Same-period year-over-year: Jan 1 through Aug 6
def ytd_count(year):
    s = date(year,1,1)
    e = date(year,8,6)
    return sum(s <= d <= e for d in emergency), (e-s).days+1

n25, e25 = ytd_count(2025)
n26, e26 = ytd_count(2026)
rr = (n26/e26)/(n25/e25)
se = math.sqrt(1/n26 + 1/n25)
lo, hi = math.exp(math.log(rr)-1.96*se), math.exp(math.log(rr)+1.96*se)
pval = binom_two_sided(n26, n25+n26, 0.5)  # equal exposure
print(f"2025-01-01..08-06: {n25} emergency dates / {e25} days")
print(f"2026-01-01..08-06: {n26} emergency dates / {e26} days")
print(f"Rate ratio 2026/2025: {rr:.3f}; approximate 95% CI {lo:.3f}–{hi:.3f}; exact two-sided p={pval:.3f}")
print()

for w in (3, 7, 14, 24, 30, 60):
    c, s, e, sel = max_window(emergency, w)
    print(f"Max {w}-day window: {c} emergency dates, {s}..{e}: " + ", ".join(str(x) for x in sel))
