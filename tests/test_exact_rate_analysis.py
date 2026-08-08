import importlib.util
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_exact_rates.py"
SPEC = importlib.util.spec_from_file_location("analyze_exact_rates", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def as_fraction(payload: dict) -> Fraction:
    return Fraction(payload["numerator"], payload["denominator"])


class ExactRateAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analysis = MODULE.build_analysis(
            ROOT / "data" / "derived" / "notification_groups.csv",
            ROOT / "data" / "benchmarks" / "wbes_tbilisi_2023.json",
        )

    def test_calendar_constant_is_exact_gregorian_mean(self):
        month = self.analysis["calendar_constants"]["mean_gregorian_month_days"]
        self.assertEqual(as_fraction(month), Fraction(48699, 1600))
        self.assertEqual(month["exact_decimal"], "30.436875")

    def test_site_b_interarrival_arithmetic_is_exact(self):
        site_b = self.analysis["site_b_emergency_interarrival"]
        self.assertEqual(site_b["group_count"], 11)
        self.assertEqual(site_b["interarrival_interval_count"], 10)
        self.assertEqual(site_b["elapsed_days_between_first_and_last_anchor"], 243)
        self.assertEqual(as_fraction(site_b["mean_gap_days"]), Fraction(243, 10))
        self.assertEqual(as_fraction(site_b["median_gap_days"]), Fraction(45, 2))
        self.assertEqual(
            as_fraction(site_b["standardized_interarrival_groups_per_30_days"]),
            Fraction(100, 81),
        )
        self.assertEqual(
            as_fraction(site_b["standardized_interarrival_groups_per_mean_gregorian_month"]),
            Fraction(5411, 4320),
        )

    def test_wbes_display_value_is_not_silently_treated_as_unrounded_truth(self):
        wbes = self.analysis["wbes_tbilisi_2023"]
        self.assertEqual(wbes["published_average_outages_typical_month_text"], "0.8")
        self.assertEqual(
            as_fraction(wbes["published_average_outages_typical_month_fraction_from_display"]),
            Fraction(4, 5),
        )
        self.assertIn("not the hidden unrounded survey estimate", wbes["precision_warning"])

    def test_site_b_vs_wbes_ratio_matches_declared_normalization(self):
        comparison = self.analysis["site_b_vs_wbes_descriptive_normalization"]
        self.assertEqual(
            as_fraction(comparison["ratio_site_b_over_wbes_display"]),
            Fraction(5411, 3456),
        )
        self.assertEqual(
            as_fraction(comparison["relative_excess_percent_over_wbes_display"]),
            Fraction(48875, 864),
        )

    def test_existing_descriptive_ratios_are_exact(self):
        ytd = self.analysis["site_a_equal_period_comparison"]
        self.assertEqual(as_fraction(ytd["count_ratio_2026_over_2025"]), Fraction(9, 7))
        self.assertEqual(as_fraction(ytd["relative_change"]), Fraction(2, 7))
        self.assertEqual(as_fraction(ytd["relative_change_percent"]), Fraction(200, 7))

        overlap = self.analysis["cross_site_overlap"]
        self.assertEqual(as_fraction(overlap["jaccard"]), Fraction(10, 11))

        planned = self.analysis["planned_windows"]
        self.assertEqual(as_fraction(planned["total_announced_hours"]), Fraction(39, 1))
        self.assertEqual(as_fraction(planned["mean_announced_hours"]), Fraction(13, 3))
        self.assertEqual(as_fraction(planned["median_announced_hours"]), Fraction(4, 1))

    def test_human_report_does_not_use_approximation_symbol(self):
        text = MODULE.render_text(self.analysis)
        self.assertNotIn("≈", text)
        self.assertIn("decimal rounded to 12 dp", text)
        self.assertIn("Do not rewrite", text)


if __name__ == "__main__":
    unittest.main()
