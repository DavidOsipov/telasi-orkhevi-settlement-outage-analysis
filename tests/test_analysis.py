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

    def test_current_report_uses_site_specific_notification_gaps(self):
        text = analysis.render()
        self.assertIn("SITE_A: mean=31.70 d; median=23.0 d", text)
        self.assertIn("SITE_B: mean=24.30 d; median=22.5 d", text)
        self.assertNotIn("mean=30.19 d", text)
        self.assertIn("Do not restate these values as 'an outage every N days'", text)

    def test_current_window_maxima(self):
        text = analysis.render()
        self.assertIn("3-day window: max 3 groups, 2026-08-04..2026-08-06", text)
        self.assertIn("24-day window: max 4 groups, 2026-07-14..2026-08-06", text)


if __name__ == "__main__":
    unittest.main()
