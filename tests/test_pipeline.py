import csv
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "data" / "derived" / "notification_groups.csv").open(encoding="utf-8") as f:
            cls.groups = list(csv.DictReader(f))
        with (ROOT / "data" / "derived" / "notifications.csv").open(encoding="utf-8") as f:
            cls.notifications = list(csv.DictReader(f))
        cls.by_id = {r["message_id"]: r for r in cls.notifications}

    def test_message_count(self):
        self.assertEqual(len(self.notifications), 56)

    def test_no_unclassified_messages(self):
        self.assertFalse([r for r in self.notifications if r["message_kind"] == "unclassified"])

    def test_group_count(self):
        self.assertEqual(len(self.groups), 34)

    def test_group_ids_are_future_safe(self):
        ids = [r["group_id"] for r in self.groups]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(re.fullmatch(r"G\d{8}-[ESP]\d{2}", x) for x in ids))
        self.assertTrue(all(re.fullmatch(r"G\d{8}", r["legacy_group_id"]) for r in self.groups))

    def test_emergency_group_count(self):
        self.assertEqual(sum(r["category"] == "emergency" for r in self.groups), 22)

    def test_site_a_same_source_ytd(self):
        def site_in(r, site):
            return site in r["evidence_sites"].split(";")

        emergencies = [r for r in self.groups if r["category"] == "emergency"]
        n25 = sum(site_in(r, "SITE_A") and "2025-01-01" <= r["anchor_date"] <= "2025-08-06" for r in emergencies)
        n26 = sum(site_in(r, "SITE_A") and "2026-01-01" <= r["anchor_date"] <= "2026-08-06" for r in emergencies)
        self.assertEqual((n25, n26), (7, 9))

    def test_august_run_is_same_site(self):
        emergencies = [
            r for r in self.groups
            if r["category"] == "emergency" and "SITE_B" in r["evidence_sites"].split(";")
        ]
        dates = {r["anchor_date"] for r in emergencies}
        self.assertTrue({"2026-08-04", "2026-08-05", "2026-08-06"} <= dates)

    def test_emergency_anchor_semantics(self):
        for r in self.groups:
            if r["category"] == "emergency":
                self.assertEqual(r["anchor_date_kind"], "restoration_eta_date")

    def test_grouped_eta_values_equal_supporting_messages(self):
        for group in self.groups:
            if group["category"] not in {"emergency", "network_switching"}:
                continue
            ids = group["supporting_message_ids"].split(";")
            source = {self.by_id[x]["eta_time"] for x in ids if self.by_id[x]["eta_time"]}
            grouped = set(filter(None, group["eta_values"].split(";")))
            self.assertEqual(source, grouped, group["group_id"])

    def test_shared_emergency_eta_sets_match_between_sites(self):
        shared = [
            r for r in self.groups
            if r["category"] == "emergency"
            and set(r["evidence_sites"].split(";")) == {"SITE_A", "SITE_B"}
        ]
        self.assertEqual(len(shared), 10)
        for g in shared:
            ids = g["supporting_message_ids"].split(";")
            a_times = {self.by_id[x]["eta_time"] for x in ids if self.by_id[x]["site_id"] == "SITE_A"}
            b_times = {self.by_id[x]["eta_time"] for x in ids if self.by_id[x]["site_id"] == "SITE_B"}
            self.assertEqual(a_times, b_times, g["group_id"])

    def test_planned_nov2_explicit_window_not_silently_extended(self):
        r = next(x for x in self.groups if x["legacy_group_id"] == "G20251102")
        self.assertEqual(r["group_id"], "G20251102-P01")
        self.assertEqual(r["scheduled_end"], "14:00")
        self.assertEqual(r["scheduled_window_hours_explicit"], "3")

    def test_nov28_cancellation_is_not_asserted_for_both_sites(self):
        r = next(x for x in self.groups if x["legacy_group_id"] == "G20251128")
        self.assertEqual(r["status"], "cancellation_notice_present")
        self.assertIn("SITE_B", r["notes"])
        self.assertIn("No cancellation SMS for SITE_A", r["notes"])

    def test_planned_announced_window_statistics(self):
        selected = [
            float(r["scheduled_window_hours_explicit"])
            for r in self.groups
            if r["category"] == "planned"
            and r["status"] in {"announced", "announced_with_possible_undated_update"}
        ]
        self.assertEqual(len(selected), 9)
        self.assertEqual(sum(selected), 39.0)
        self.assertAlmostEqual(sum(selected) / len(selected), 13 / 3)

    def test_generated_notifications_use_lf(self):
        self.assertNotIn(b"\r\n", (ROOT / "data" / "derived" / "notifications.csv").read_bytes())


if __name__ == "__main__":
    unittest.main()
