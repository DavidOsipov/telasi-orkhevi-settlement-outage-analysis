#!/usr/bin/env python3
"""Exact arithmetic for descriptive SMS-notification metrics and benchmarks.

Canonical values are kept as fractions. Decimal strings are emitted only as
explicitly rounded representations for readability.

This script does NOT estimate SAIDI/SAIFI or physical-outage rates. Its rate
normalizations are based on gaps between curated emergency restoration-ETA
notification groups and are therefore descriptive notification metrics only.

The WBES "typical month" indicator is not definition-identical to a mean
calendar month. Any arithmetic division between a SITE_B calendar-normalized
inter-arrival metric and the WBES displayed value is retained only as a
reproducibility diagnostic and must not be reported as a reliability ratio.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from decimal import Decimal, localcontext, ROUND_HALF_UP
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GROUPS = ROOT / "data" / "derived" / "notification_groups.csv"
DEFAULT_WBES = ROOT / "data" / "benchmarks" / "wbes_tbilisi_2023.json"

# Exact average Gregorian year: 365 + 97/400 days.
DAYS_PER_GREGORIAN_YEAR = Fraction(146097, 400)
DAYS_PER_GREGORIAN_MONTH = DAYS_PER_GREGORIAN_YEAR / 12
DAYS_PER_30_DAY_PERIOD = Fraction(30, 1)


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def terminating_decimal(value: Fraction) -> str | None:
    """Return an exact finite decimal if the reduced denominator has only 2/5 factors."""
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
    scale = 10**places
    scaled = value * scale
    assert scaled.denominator == 1
    if places == 0:
        return str(scaled.numerator)
    sign = "-" if scaled.numerator < 0 else ""
    digits = str(abs(scaled.numerator)).rjust(places + 1, "0")
    return f"{sign}{digits[:-places]}.{digits[-places:]}"


def rounded_decimal(value: Fraction, places: int = 12) -> str:
    """Human-readable decimal, explicitly rounded; the fraction remains canonical."""
    quantum = Decimal(1).scaleb(-places)
    with localcontext() as ctx:
        ctx.prec = max(50, places + 30)
        dec = Decimal(value.numerator) / Decimal(value.denominator)
        return format(dec.quantize(quantum, rounding=ROUND_HALF_UP), "f")


def fraction_payload(value: Fraction) -> dict:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "exact_fraction": fraction_text(value),
        "exact_decimal": terminating_decimal(value),
        "decimal_12dp_rounded": rounded_decimal(value, 12),
    }


def parse_decimal_fraction(text: str) -> Fraction:
    """Parse a source decimal string exactly, never through binary float."""
    return Fraction(text.strip())


def load_groups(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            row["anchor_date"] = date.fromisoformat(row["anchor_date"])
            rows.append(row)
    if not rows:
        raise ValueError(f"no notification groups found in {path}")
    return rows


def site_in(row: dict, site_id: str) -> bool:
    return site_id in row["evidence_sites"].split(";")


def exact_median_int(values: list[int]) -> Fraction:
    if not values:
        raise ValueError("median of empty sequence")
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return Fraction(ordered[middle], 1)
    return Fraction(ordered[middle - 1] + ordered[middle], 2)


def gap_metrics(rows: list[dict]) -> dict:
    ordered = sorted(rows, key=lambda r: (r["anchor_date"], r["group_id"]))
    if len(ordered) < 2:
        raise ValueError("at least two rows are required for inter-arrival analysis")
    gaps = [
        (current["anchor_date"] - previous["anchor_date"]).days
        for previous, current in zip(ordered, ordered[1:])
    ]
    elapsed_days = (ordered[-1]["anchor_date"] - ordered[0]["anchor_date"]).days
    interval_count = len(gaps)
    assert sum(gaps) == elapsed_days
    mean_gap = Fraction(elapsed_days, interval_count)
    rate_30 = Fraction(interval_count, elapsed_days) * DAYS_PER_30_DAY_PERIOD
    rate_gregorian_month = Fraction(interval_count, elapsed_days) * DAYS_PER_GREGORIAN_MONTH
    return {
        "group_count": len(ordered),
        "first_anchor_date": ordered[0]["anchor_date"].isoformat(),
        "last_anchor_date": ordered[-1]["anchor_date"].isoformat(),
        "elapsed_days_between_first_and_last_anchor": elapsed_days,
        "interarrival_interval_count": interval_count,
        "gaps_days": gaps,
        "mean_gap_days": fraction_payload(mean_gap),
        "median_gap_days": fraction_payload(exact_median_int(gaps)),
        "min_gap_days": min(gaps),
        "max_gap_days": max(gaps),
        "standardized_interarrival_groups_per_30_days": fraction_payload(rate_30),
        "standardized_interarrival_groups_per_mean_gregorian_month": fraction_payload(rate_gregorian_month),
        "normalization_note": (
            "These are event-bounded inter-arrival normalizations: interval_count / elapsed_days, "
            "not observation-window incidence rates. The mean Gregorian month is exactly "
            "146097/(400*12) = 48699/1600 days by convention."
        ),
    }


def load_wbes(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    indicators = data.get("indicators")
    if not isinstance(indicators, dict):
        raise ValueError(f"{path}: expected an 'indicators' object")
    monthly = indicators.get("bready_in2")
    if not isinstance(monthly, dict) or "published_value" not in monthly:
        raise ValueError(f"{path}: missing bready_in2 published_value")
    return data


def site_a_equal_period(emergency: list[dict]) -> dict:
    def count(year: int) -> int:
        start = date(year, 1, 1)
        end = date(year, 8, 6)
        return sum(
            site_in(r, "SITE_A") and start <= r["anchor_date"] <= end
            for r in emergency
        )

    n_2025 = count(2025)
    n_2026 = count(2026)
    if n_2025 == 0:
        raise ValueError("SITE_A 2025 comparison denominator is zero")
    ratio = Fraction(n_2026, n_2025)
    change = ratio - 1
    return {
        "period": "Jan 1 through Aug 6 inclusive",
        "2025_group_count": n_2025,
        "2026_group_count": n_2026,
        "count_ratio_2026_over_2025": fraction_payload(ratio),
        "relative_change": fraction_payload(change),
        "relative_change_percent": fraction_payload(change * 100),
    }


def cross_site_overlap(emergency: list[dict]) -> dict:
    start = date(2025, 12, 6)
    end = max(r["anchor_date"] for r in emergency)
    a_dates = {
        r["anchor_date"] for r in emergency
        if site_in(r, "SITE_A") and start <= r["anchor_date"] <= end
    }
    b_dates = {
        r["anchor_date"] for r in emergency
        if site_in(r, "SITE_B") and start <= r["anchor_date"] <= end
    }
    shared = a_dates & b_dates
    union = a_dates | b_dates
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "site_a_unique_eta_dates": len(a_dates),
        "site_b_unique_eta_dates": len(b_dates),
        "shared_eta_dates": len(shared),
        "union_eta_dates": len(union),
        "jaccard": fraction_payload(Fraction(len(shared), len(union))) if union else None,
    }


def planned_window_metrics(rows: list[dict]) -> dict:
    selected = [
        r for r in rows
        if r["category"] == "planned"
        and r["status"] in {"announced", "announced_with_possible_undated_update"}
        and r["scheduled_window_hours_explicit"]
    ]
    hours = [parse_decimal_fraction(r["scheduled_window_hours_explicit"]) for r in selected]
    if not hours:
        raise ValueError("no explicit planned windows found")
    total = sum(hours, Fraction(0, 1))
    ordered = sorted(hours)
    middle = len(ordered) // 2
    median = ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2
    return {
        "group_count": len(hours),
        "total_announced_hours": fraction_payload(total),
        "mean_announced_hours": fraction_payload(total / len(hours)),
        "median_announced_hours": fraction_payload(median),
    }


def build_analysis(groups_path: Path, wbes_path: Path) -> dict:
    rows = load_groups(groups_path)
    emergency = [r for r in rows if r["category"] == "emergency"]
    site_a = [r for r in emergency if site_in(r, "SITE_A")]
    site_b = [r for r in emergency if site_in(r, "SITE_B")]

    a_gaps = gap_metrics(site_a)
    b_gaps = gap_metrics(site_b)

    wbes = load_wbes(wbes_path)
    wbes_text = str(wbes["indicators"]["bready_in2"]["published_value"])
    wbes_display_rate = parse_decimal_fraction(wbes_text)
    site_b_gregorian_month = Fraction(
        b_gaps["standardized_interarrival_groups_per_mean_gregorian_month"]["numerator"],
        b_gaps["standardized_interarrival_groups_per_mean_gregorian_month"]["denominator"],
    )
    ratio_to_wbes_display = site_b_gregorian_month / wbes_display_rate
    excess_over_wbes_display = ratio_to_wbes_display - 1

    return {
        "schema_version": 1,
        "arithmetic_policy": {
            "canonical_representation": "reduced rational fractions",
            "binary_float_used_for_core_metrics": False,
            "decimal_policy": "decimal_12dp_rounded is presentation-only; exact_fraction is canonical",
        },
        "metric_scope_warning": (
            "Emergency rows are curated restoration-ETA notification groups, not proven distinct physical outages. "
            "The supplied transcript span is not a proven complete observation window."
        ),
        "calendar_constants": {
            "mean_gregorian_year_days": fraction_payload(DAYS_PER_GREGORIAN_YEAR),
            "mean_gregorian_month_days": fraction_payload(DAYS_PER_GREGORIAN_MONTH),
            "standard_30_day_period_days": fraction_payload(DAYS_PER_30_DAY_PERIOD),
        },
        "site_a_emergency_interarrival": a_gaps,
        "site_b_emergency_interarrival": b_gaps,
        "site_a_equal_period_comparison": site_a_equal_period(emergency),
        "cross_site_overlap": cross_site_overlap(emergency),
        "planned_windows": planned_window_metrics(rows),
        "wbes_tbilisi_2023": {
            "source": wbes.get("source"),
            "source_endpoint": wbes.get("source_endpoint"),
            "percent_firms_experiencing_outages_display": wbes["indicators"].get("in16", {}).get("published_value"),
            "published_average_outages_typical_month_text": wbes_text,
            "published_average_outages_typical_month_fraction_from_display": fraction_payload(wbes_display_rate),
            "precision_warning": (
                "The fraction above is the exact rational representation of the decimal string published by the "
                "World Bank API. It is not the hidden unrounded survey estimate."
            ),
            "typical_month_semantics_warning": (
                "WBES 'typical month' is a survey concept for the most common type of month regarding outages, "
                "not the arithmetic mean Gregorian calendar month. The published 0.8 therefore has no exact "
                "conversion to 'one outage every N days'."
            ),
        },
        "site_b_vs_wbes_descriptive_normalization": {
            "status": "diagnostic_arithmetic_only_not_a_rate_ratio",
            "site_b_mean_gregorian_month_interarrival_rate": fraction_payload(site_b_gregorian_month),
            "wbes_published_typical_month_rate_from_display": fraction_payload(wbes_display_rate),
            "ratio_site_b_over_wbes_display": fraction_payload(ratio_to_wbes_display),
            "relative_excess_over_wbes_display": fraction_payload(excess_over_wbes_display),
            "relative_excess_percent_over_wbes_display": fraction_payload(excess_over_wbes_display * 100),
            "comparison_warning": (
                "This arithmetic contrast is retained for reproducibility only. The SITE_B numerator is normalized "
                "to an arithmetic mean Gregorian calendar month, whereas the WBES denominator is a weighted survey "
                "indicator for a 'typical month'. Do not report this quotient as 'Orkhevi has X times/more outages "
                "than Tbilisi'. The source metrics, populations, years, completeness, event identity, and month "
                "definitions differ."
            ),
        },
    }


def render_text(data: dict) -> str:
    b = data["site_b_emergency_interarrival"]
    a = data["site_a_emergency_interarrival"]
    ytd = data["site_a_equal_period_comparison"]
    overlap = data["cross_site_overlap"]
    planned = data["planned_windows"]
    comparison = data["site_b_vs_wbes_descriptive_normalization"]
    wbes = data["wbes_tbilisi_2023"]

    lines = [
        "Exact descriptive rate analysis",
        "===============================",
        "",
        data["metric_scope_warning"],
        "",
        "Canonical arithmetic rule: reduced fractions are exact; decimal_12dp values are rounded presentation only.",
        "",
        "SITE_B emergency restoration-ETA notification-group inter-arrivals:",
        f"  groups: {b['group_count']}",
        f"  first..last anchor: {b['first_anchor_date']} .. {b['last_anchor_date']}",
        f"  elapsed days: {b['elapsed_days_between_first_and_last_anchor']}",
        f"  inter-arrival intervals: {b['interarrival_interval_count']}",
        f"  exact mean gap: {b['mean_gap_days']['exact_fraction']} days"
        + (f" = {b['mean_gap_days']['exact_decimal']} days" if b['mean_gap_days']['exact_decimal'] else ""),
        f"  exact median gap: {b['median_gap_days']['exact_fraction']} days"
        + (f" = {b['median_gap_days']['exact_decimal']} days" if b['median_gap_days']['exact_decimal'] else ""),
        f"  exact standardized inter-arrival count / 30 days: {b['standardized_interarrival_groups_per_30_days']['exact_fraction']}",
        "  standardized inter-arrival count / mean Gregorian calendar month: "
        f"{b['standardized_interarrival_groups_per_mean_gregorian_month']['exact_fraction']} "
        f"(decimal rounded to 12 dp: {b['standardized_interarrival_groups_per_mean_gregorian_month']['decimal_12dp_rounded']})",
        "  These standardizations are derived from the 10 observed inter-arrival intervals, not from a proven complete observation window.",
        "",
        "SITE_A emergency restoration-ETA notification-group inter-arrivals:",
        f"  groups: {a['group_count']}",
        f"  exact mean gap: {a['mean_gap_days']['exact_fraction']} days",
        f"  exact median gap: {a['median_gap_days']['exact_fraction']} days",
        "",
        "SITE_A equal-period count comparison (Jan 1-Aug 6):",
        f"  2025: {ytd['2025_group_count']}",
        f"  2026: {ytd['2026_group_count']}",
        f"  exact ratio: {ytd['count_ratio_2026_over_2025']['exact_fraction']}",
        f"  exact relative change: {ytd['relative_change']['exact_fraction']}",
        f"  exact relative change percent: {ytd['relative_change_percent']['exact_fraction']}% "
        f"(decimal rounded to 12 dp: {ytd['relative_change_percent']['decimal_12dp_rounded']}%)",
        "",
        "Cross-site overlap:",
        f"  exact Jaccard: {overlap['jaccard']['exact_fraction']} "
        f"(decimal rounded to 12 dp: {overlap['jaccard']['decimal_12dp_rounded']})",
        "",
        "Planned announced windows:",
        f"  groups: {planned['group_count']}",
        f"  exact total hours: {planned['total_announced_hours']['exact_fraction']}",
        f"  exact mean hours: {planned['mean_announced_hours']['exact_fraction']}",
        f"  exact median hours: {planned['median_announced_hours']['exact_fraction']}",
        "",
        "WBES Tbilisi 2023 independent benchmark:",
        f"  percent of firms experiencing electrical outages (published display value): {wbes['percent_firms_experiencing_outages_display']}%",
        f"  average outages in a typical month (published display value): {wbes['published_average_outages_typical_month_text']}",
        "  exact rational representation of the displayed 0.8: "
        f"{wbes['published_average_outages_typical_month_fraction_from_display']['exact_fraction']}",
        "  No direct SITE_B/WBES outage-rate ratio is reported.",
        "  WBES 'typical month' is not the arithmetic mean Gregorian month, so 0.8 cannot be exactly converted to 'one outage every N days'.",
        "",
        wbes["precision_warning"],
        wbes["typical_month_semantics_warning"],
        comparison["comparison_warning"],
        "",
        "Do not rewrite the SITE_B gap/rate metrics as a physical-outage rate or SAIFI.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--groups", type=Path, default=DEFAULT_GROUPS)
    parser.add_argument("--wbes", type=Path, default=DEFAULT_WBES)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-text", type=Path)
    args = parser.parse_args()

    data = build_analysis(args.groups, args.wbes)
    text = render_text(data)
    print(text, end="")

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    if args.output_text:
        args.output_text.parent.mkdir(parents=True, exist_ok=True)
        args.output_text.write_text(text, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
