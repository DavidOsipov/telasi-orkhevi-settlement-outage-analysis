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

    def test_source_identity_is_same_building(self):
        identity = self.analysis["source_identity"]
        self.assertIn("same Orkhevi building", identity["relationship"])
        self.assertIn("not be interpreted as two geographic sites", identity["legacy_identifier_warning"])

    def test_calendar_constant_is_exact_gregorian_mean(self):
        month = self.analysis["calendar_constants"]["mean_gregorian_month_days"]
        self.assertEqual(as_fraction(month), Fraction(48699, 1600))
        self.assertEqual(month["exact_decimal"], "30.436875")

    def test_long_single_source_a_is_exact(self):
        a = self.analysis["source_a_emergency_interarrival"]
        self.assertEqual(a["group_count"], 21)
        self.assertEqual(a["interarrival_interval_count"], 20)
        self.assertEqual(a["elapsed_days_between_first_and_last_anchor"], 634)
        self.assertEqual(as_fraction(a["mean_gap_days"]), Fraction(317, 10))
        self.assertEqual(
            as_fraction(a["standardized_interarrival_groups_per_mean_gregorian_month"]),
            Fraction(48699, 50720),
        )

    def test_building_union_is_exact_but_secondary(self):
        u = self.analysis["building_union_emergency_interarrival"]
        self.assertEqual(u["group_count"], 22)
        self.assertEqual(u["interarrival_interval_count"], 21)
        self.assertEqual(u["elapsed_days_between_first_and_last_anchor"], 634)
        self.assertEqual(as_fraction(u["mean_gap_days"]), Fraction(634, 21))
        self.assertEqual(
            as_fraction(u["standardized_interarrival_groups_per_mean_gregorian_month"]),
            Fraction(1022679, 1014400),
        )
        self.assertIn("ascertainment changes", self.analysis["comparison_policy"])

    def test_recent_source_b_is_still_exact(self):
        b = self.analysis["source_b_emergency_interarrival"]
        self.assertEqual(b["group_count"], 11)
        self.assertEqual(as_fraction(b["mean_gap_days"]), Fraction(243, 10))
        self.assertEqual(
            as_fraction(b["standardized_interarrival_groups_per_mean_gregorian_month"]),
            Fraction(5411, 4320),
        )

    def test_wbes_display_value_precision(self):
        wbes = self.analysis["wbes_tbilisi_2023"]
        self.assertEqual(wbes["published_average_outages_typical_month_text"], "0.8")
        self.assertEqual(as_fraction(wbes["published_average_outages_typical_month_fraction_from_display"]), Fraction(4, 5))
        self.assertIn("not the hidden unrounded weighted survey estimate", wbes["precision_warning"])

    def test_primary_benchmark_uses_long_source_a(self):
        c = self.analysis["benchmark_comparisons"]["primary_long_single_source_a"]
        self.assertEqual(as_fraction(c["ratio_over_wbes_display"]), Fraction(48699, 40576))
        self.assertEqual(as_fraction(c["relative_excess_percent_over_wbes_display"]), Fraction(203075, 10144))

    def test_secondary_benchmark_values_are_explicit(self):
        u = self.analysis["benchmark_comparisons"]["secondary_building_union"]
        b = self.analysis["benchmark_comparisons"]["secondary_recent_source_b"]
        self.assertEqual(as_fraction(u["ratio_over_wbes_display"]), Fraction(1022679, 811520))
        self.assertEqual(as_fraction(b["ratio_over_wbes_display"]), Fraction(5411, 3456))

    def test_existing_descriptive_ratios_are_exact(self):
        ytd = self.analysis["source_a_equal_period_comparison"]
        self.assertEqual(as_fraction(ytd["count_ratio_2026_over_2025"]), Fraction(9, 7))
        self.assertEqual(as_fraction(ytd["relative_change_percent"]), Fraction(200, 7))
        overlap = self.analysis["cross_resident_overlap"]
        self.assertEqual(as_fraction(overlap["jaccard"]), Fraction(10, 11))

    def test_human_report_does_not_use_approximation_symbol(self):
        text = MODULE.render_text(self.analysis)
        self.assertNotIn("≈", text)
        self.assertIn("PRIMARY — long single-source SITE_A", text)
        self.assertIn("same building", text)
        self.assertIn("Do not rewrite", text)

if __name__ == "__main__":
    unittest.main()
