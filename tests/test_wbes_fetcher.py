import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fetch_wbes_tbilisi.py"
SPEC = importlib.util.spec_from_file_location("fetch_wbes_tbilisi", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class WbesFetcherTests(unittest.TestCase):
    def make_rows(self):
        return [
            {
                "indicatorId": 183,
                "indicator": "Percent of firms experiencing electrical outages",
                "subCut": "Tbilisi",
                "country": "31.8",
                "queryFieldName": "in16",
            },
            {
                "indicatorId": 231,
                "indicator": "[B-READY] Average number of electrical outages in a typical month",
                "subCut": "Tbilisi",
                "country": "0.8",
                "queryFieldName": "bready_in2",
            },
            {
                "indicatorId": 232,
                "indicator": "[B-READY] Duration, in hours, of a typical electrical outage [median]",
                "subCut": "Tbilisi",
                "country": "0",
                "queryFieldName": "bready_in3_median",
            },
            {
                "indicatorId": 101,
                "indicator": "Percent of firms identifying electricity as a major or very severe constraint",
                "subCut": "Tbilisi",
                "country": "38.6",
                "queryFieldName": "in12",
            },
            {
                "indicatorId": 246,
                "indicator": "[B-READY] Percent of firms owning or sharing a generator",
                "subCut": "Tbilisi",
                "country": "29.8",
                "queryFieldName": "bready_in9",
            },
        ]

    def test_normalization_preserves_display_strings_and_exact_fractions(self):
        raw = json.dumps(self.make_rows(), separators=(",", ":")).encode("utf-8")
        result = MODULE.normalize(raw, "https://example.invalid/wbes", "2026-08-08T00:00:00Z")
        monthly = result["indicators"]["bready_in2"]
        self.assertEqual(monthly["published_value"], "0.8")
        self.assertEqual(monthly["numerator"], 4)
        self.assertEqual(monthly["denominator"], 5)
        self.assertEqual(monthly["exact_fraction_from_display"], "4/5")

    def test_numeric_json_value_is_rejected_for_lexical_precision(self):
        rows = self.make_rows()
        rows[1]["country"] = 0.8
        raw = json.dumps(rows, separators=(",", ":")).encode("utf-8")
        with self.assertRaisesRegex(ValueError, "not a JSON string"):
            MODULE.normalize(raw, "https://example.invalid/wbes", "2026-08-08T00:00:00Z")

    def test_indicator_label_drift_is_rejected(self):
        rows = self.make_rows()
        rows[1]["indicator"] = "Changed label"
        raw = json.dumps(rows, separators=(",", ":")).encode("utf-8")
        with self.assertRaisesRegex(ValueError, "indicator label changed"):
            MODULE.normalize(raw, "https://example.invalid/wbes", "2026-08-08T00:00:00Z")


if __name__ == "__main__":
    unittest.main()
