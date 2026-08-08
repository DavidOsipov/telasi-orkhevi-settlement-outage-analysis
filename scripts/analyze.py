#!/usr/bin/env python3
"""Produce conservative descriptive statistics from curated SMS notification groups.

Core arithmetic uses fractions rather than binary floating-point values. When a
repeating decimal is printed, the report labels it explicitly as rounded.
"""

from __future__ import annotations

from pathlib import Path
import argparse
import csv
from datetime import date, timedelta
from decimal import Decimal, localcontext, ROUND_HALF_UP
from fractions import Fraction

ROOT = Path(__file__).resolve().parents[1]
GROUPS = ROOT / "data" / "derived" / "notification_groups.csv"


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def exact_decimal(value: Fraction) -> str | None:
    denominator = value.denominator
    twos = fives = 0
    while denominator % 2 == 0:
        denominator //= 2
        twos += 1
    while denominator % 5 == 0:
        denominator //= 5
        fives += 1
    if denominator != 1:
        return None
    places = max(twos, fives)
    scaled = value * (10**places)
    assert scaled.denominator == 1
    if places == 0:
        return str(scaled.numerator)
    sign = "-" if scaled.numerator < 0 else ""
    digits = str(abs(scaled.numerator)).rjust(places + 1, "0")
    return f"{sign}{digits[:-places]}.{digits[-places:]}"


def rounded_decimal(value: Fraction, places: int) -> str:
    quantum = Decimal(1).scaleb(-places)
    with localcontext() as ctx:
        ctx.prec = max(50, places + 30)
        dec = Decimal(value.numerator) / Decimal(value.denominator)
        return format(dec.quantize(quantum, rounding=ROUND_HALF_UP), "f")


def display_fraction(value: Fraction, *, places: int = 3) -> str:
    finite = exact_decimal(value)
    if finite is not None:
        if value.denominator == 1:
            return fraction_text(value)
        return f"{fraction_text(value)} = {finite}"
    return f"{fraction_text(value)} (decimal rounded to {places} dp: {rounded_decimal(value, places)})"


def load_groups() -> list[dict]:
    rows = []
    with GROUPS.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["anchor_date"] = date.fromisoformat(row["anchor_date"])
            rows.append(row)
    return rows


def site_in(row: dict, site_id: str) -> bool:
    return site_id in row["evidence_sites"].split(";")


def fully_contained_window_max(rows: list[dict], days: int, span_start: date, span_end: date):
    """Maximum number of groups in any calendar window fully inside the supplied anchor span.

    Rows, rather than a set of dates, are counted. This remains correct if a
    future dataset contains multiple curated groups on the same calendar date.
    """
    if not rows or (span_end - span_start).days + 1 < days:
        return None
    best = None
    start = span_start
    last_start = span_end - timedelta(days=days - 1)
    while start <= last_start:
        end = start + timedelta(days=days - 1)
        selected = sorted(
            (r for r in rows if start <= r["anchor_date"] <= end),
            key=lambda r: (r["anchor_date"], r["group_id"]),
        )
        candidate = (len(selected), start, end, selected)
        if best is None or candidate[0] > best[0]:
            best = candidate
        start += timedelta(days=1)
    return best


def exact_median_int(values: list[int]) -> Fraction:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("median of empty sequence")
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return Fraction(ordered[middle], 1)
    return Fraction(ordered[middle - 1] + ordered[middle], 2)


def exact_median_fraction(values: list[Fraction]) -> Fraction:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("median of empty sequence")
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def gap_stats(rows: list[dict]):
    dates = sorted(r["anchor_date"] for r in rows)
    gaps = [(b - a).days for a, b in zip(dates, dates[1:])]
    if not gaps:
        return None
    mean = Fraction(sum(gaps), len(gaps))
    median = exact_median_int(gaps)
    return mean, median, min(gaps), max(gaps)


def render() -> str:
    rows = load_groups()
    all_dates = sorted(r["anchor_date"] for r in rows)
    record_start, record_end = min(all_dates), max(all_dates)
    record_span_days = (record_end - record_start).days + 1

    emergency = [r for r in rows if r["category"] == "emergency"]
    switching = [r for r in rows if r["category"] == "network_switching"]
    planned = [r for r in rows if r["category"] == "planned"]

    out: list[str] = []
    emit = out.append
    emit(f"Source-record anchor span: {record_start} to {record_end} inclusive = {record_span_days} calendar days")
    emit("IMPORTANT: this is a retrospective transcript span, not a proven complete observation window.")
    emit(f"Emergency notification groups keyed by restoration-ETA date: {len(emergency)}")
    emit(f"Network-switching notification groups keyed by restoration-ETA date: {len(switching)}")
    emit(f"Planned-work notification groups keyed by scheduled date: {len(planned)}")
    emit("")

    emit("Per-site emergency ETA-date gaps (descriptive notification gaps; not physical-outage inter-arrival times):")
    for site_id in ("SITE_A", "SITE_B"):
        site_rows = [r for r in emergency if site_in(r, site_id)]
        stats = gap_stats(site_rows)
        if stats:
            mean, median, minimum, maximum = stats
            emit(
                f"  {site_id}: mean={display_fraction(mean)} d; median={display_fraction(median)} d; "
                f"min={minimum} d; max={maximum} d"
            )
    emit("  Do not restate these values as 'an outage every N days': SMS completeness and incident identity are not established.")
    emit("")

    def site_a_ytd(year: int) -> int:
        start, end = date(year, 1, 1), date(year, 8, 6)
        return sum(site_in(r, "SITE_A") and start <= r["anchor_date"] <= end for r in emergency)

    n25 = site_a_ytd(2025)
    n26 = site_a_ytd(2026)
    emit("Same-source descriptive comparison (SITE_A only; Jan 1-Aug 6):")
    emit(f"  2025: {n25} emergency ETA-date groups")
    emit(f"  2026: {n26} emergency ETA-date groups")
    if n25:
        ratio = Fraction(n26, n25)
        relative_change = ratio - 1
        emit(f"  exact descriptive ratio: {display_fraction(ratio)}")
        emit(f"  exact relative change: {display_fraction(relative_change, places=6)}")
        emit(f"  exact relative change percent: {display_fraction(relative_change * 100, places=6)}%")
    emit("  SITE_A's exact public property/location mapping is intentionally unresolved; do not restate this as an Orkhevi-wide rate change.")
    emit("  No p-value/CI is reported because notification completeness and event independence are not established.")
    emit("")

    overlap_start = date(2025, 12, 6)
    overlap_end = record_end
    a_overlap_dates = {
        r["anchor_date"] for r in emergency
        if site_in(r, "SITE_A") and overlap_start <= r["anchor_date"] <= overlap_end
    }
    b_overlap_dates = {
        r["anchor_date"] for r in emergency
        if site_in(r, "SITE_B") and overlap_start <= r["anchor_date"] <= overlap_end
    }
    shared = a_overlap_dates & b_overlap_dates
    union = a_overlap_dates | b_overlap_dates
    emit(f"Cross-site emergency ETA-date overlap ({overlap_start}..{overlap_end}):")
    emit(f"  SITE_A unique ETA dates: {len(a_overlap_dates)}")
    emit(f"  SITE_B unique ETA dates: {len(b_overlap_dates)}")
    emit(f"  shared ETA dates: {len(shared)}")
    emit(
        f"  Jaccard(unique ETA-date sets): {display_fraction(Fraction(len(shared), len(union)))}"
        if union else "  Jaccard: n/a"
    )
    emit("")

    explicit_planned = [r for r in planned if r["status"] in {"announced", "announced_with_possible_undated_update"}]
    explicit_hours = [
        Fraction(r["scheduled_window_hours_explicit"])
        for r in explicit_planned
        if r["scheduled_window_hours_explicit"]
    ]
    total_hours = sum(explicit_hours, Fraction(0, 1))
    emit(
        f"Explicit scheduled windows in planned notices without a cancellation signal in the same group: "
        f"{len(explicit_planned)} groups, {display_fraction(total_hours)} announced hours"
    )
    if explicit_hours:
        mean_hours = total_hours / len(explicit_hours)
        median_hours = exact_median_fraction(explicit_hours)
        emit(
            f"  announced-window exact mean={display_fraction(mean_hours)} h; "
            f"median={display_fraction(median_hours)} h"
        )
    emit("  These are notice-window hours, not verified outage-duration hours.")
    emit("  The undated 2025-11 planned-work extension is not included beyond the explicit 11:00-14:00 window.")
    emit("")

    site_b_em = [r for r in emergency if site_in(r, "SITE_B")]
    site_b_start = min(r["anchor_date"] for r in site_b_em)
    site_b_end = max(r["anchor_date"] for r in site_b_em)
    emit("SITE_B fully-contained calendar-window maxima for emergency restoration-ETA groups:")
    for width in (3, 7, 14, 24, 30):
        result = fully_contained_window_max(site_b_em, width, site_b_start, site_b_end)
        if result:
            count, start, end, selected = result
            details = ", ".join(f"{r['anchor_date']}({r['group_id']})" for r in selected)
            emit(f"  {width:2d}-day window: max {count} groups, {start}..{end}: {details}")
    emit("")
    emit(
        "Interpretation: the 4-6 Aug run is three emergency notification groups whose restoration ETAs fall on three "
        "consecutive dates at SITE_B. Without SMS receipt/restoration timestamps, this is not by itself proof of three "
        "distinct physical outage incidents."
    )
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="Write the report to this path in addition to stdout")
    args = parser.parse_args()
    text = render()
    print(text, end="")
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
