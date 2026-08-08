import importlib.util
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("analysis_module", ROOT / "scripts" / "analyze.py")
analysis = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(analysis)

class AnalysisTests(unittest.TestCase):
    def test_fully_contained_window_counts_multiple_groups_on_same_date(self):
        rows = [
            {"anchor_date": date(2026, 8, 5), "group_id": "G20260805-E01"},
            {"anchor_date": date(2026, 8, 5), "group_id": "G20260805-E02"},
            {"anchor_date": date(2026, 8, 6), "group_id": "G20260806-E01"},
        ]
        result = analysis.fully_contained_window_max(rows, 1, date(2026, 8, 5), date(2026, 8, 6))
        self.assertIsNotNone(result)
        count, start, end, selected = result
        self.assertEqual(count, 2)
        self.assertEqual((start, end), (date(2026, 8, 5), date(2026, 8, 5)))
        self.assertEqual([r["group_id"] for r in selected], ["G20260805-E01", "G20260805-E02"])

    def test_report_uses_same_building_source_semantics(self):
        text = analysis.render()
        self.assertIn("two residents of the same Orkhevi building", text)
        self.assertIn("SITE_A (neighbor archive, starts 2024): mean=317/10 = 31.7 d", text)
        self.assertIn("SITE_B (repository-owner archive, starts 2025): mean=243/10 = 24.3 d", text)
        self.assertNotIn("Per-site emergency", text)
        self.assertNotIn("Cross-site", text)

    def test_building_union_is_explicitly_ascertainment_limited(self):
        text = analysis.render()
        self.assertIn("mean gap=634/21", text)
        self.assertIn("not a constant-ascertainment incidence series", text)

    def test_current_window_maxima(self):
        text = analysis.render()
        self.assertIn("3-day window: max 3 groups, 2026-08-04..2026-08-06", text)
        self.assertIn("24-day window: max 4 groups, 2026-07-14..2026-08-06", text)

    def test_cross_resident_overlap_is_date_set_based(self):
        text = analysis.render()
        self.assertIn("Cross-resident emergency ETA-date overlap at the same building", text)
        self.assertIn("SITE_A unique ETA dates: 10", text)
        self.assertIn("SITE_B unique ETA dates: 11", text)
        self.assertIn("shared ETA dates: 10", text)
        self.assertIn("Jaccard(unique ETA-date sets): 10/11", text)
        self.assertIn("not two-site/network-topology evidence", text)

if __name__ == "__main__":
    unittest.main()
