import base64
import gzip
import hashlib
import sys
import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "data" / "telasi_api" / "raw" / "2026-08-08"
MANIFEST = json.loads((SNAPSHOT / "MANIFEST.json").read_text(encoding="utf-8"))

SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
import telasi_api_core as core
import telasi_api_pagination as pagination
import compare_telasi_api_sms as compare


def canonical_document():
    canonical = MANIFEST["canonical_orkhevi_search"]
    joined = b"".join((SNAPSHOT / item["path"]).read_bytes() for item in canonical["chunks"])
    return json.loads(gzip.decompress(base64.b64decode(joined)).decode("utf-8"))


class TelasiApiFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = canonical_document()
        cls.rows = core.normalize_rows(cls.document)
        cls.by_id = {str(row["id"]): row for row in cls.rows}

    def test_canonical_snapshot_hash_and_count(self):
        canonical = MANIFEST["canonical_orkhevi_search"]
        joined = b"".join((SNAPSHOT / item["path"]).read_bytes() for item in canonical["chunks"])
        raw = gzip.decompress(base64.b64decode(joined))
        self.assertEqual(hashlib.sha256(raw).hexdigest(), canonical["original_json_sha256"])
        self.assertEqual(len(raw), canonical["original_json_bytes"])
        self.assertEqual(self.document["content"]["listCount"], 17)
        self.assertEqual(len(self.document["content"]["list"]), 17)

    def test_taxonomy_and_geographic_classification(self):
        self.assertEqual(Counter(r["publication_class"] for r in self.rows), Counter({"unplanned": 13, "planned_or_scheduled": 4}))
        self.assertEqual(
            Counter(r["orkhevi_match_kind"] for r in self.rows),
            Counter({"explicit_settlement": 9, "broader_orkhevi_name_match": 5, "orkhevi_named_exit": 2, "industrial_zone": 1}),
        )

    def test_all_unplanned_fixture_rows_have_parsed_eta(self):
        unplanned = [r for r in self.rows if r["publication_class"] == "unplanned"]
        self.assertEqual(len(unplanned), 13)
        self.assertTrue(all(r["restoration_eta"] for r in unplanned))

    def test_spaced_georgian_eta_is_parsed(self):
        self.assertEqual(self.by_id["5584"]["restoration_eta"], "2026-07-11 04:31")

    def test_source_side_year_error_is_preserved_not_corrected(self):
        row = self.by_id["4644"]
        self.assertTrue(str(row["created_at"]).startswith("2026-01-04"))
        self.assertEqual(row["restoration_eta"], "2025-01-04 08:05")

    def test_no_exact_sms_eta_match_in_focused_17_hit_fixture(self):
        api_etas = {r["restoration_eta"] for r in self.rows if r["restoration_eta"]}
        import csv
        sms = set()
        with (ROOT / "data" / "derived" / "notification_groups.csv").open(encoding="utf-8") as handle:
            for group in csv.DictReader(handle):
                if group["category"] == "emergency":
                    for value in filter(None, group["eta_values"].split(";")):
                        sms.add(f"{group['anchor_date']} {value}")
        self.assertFalse(api_etas & sms)

    def test_focused_general_list_probe_is_explicitly_partial(self):
        probe = next(
            x for x in MANIFEST["exploratory_probe_observations"]["responses"]
            if x["logical_path"].endswith("contenttype-all.response.json.gz.b64")
        )
        self.assertEqual(probe["observed_response"]["content_listCount"], 889)
        self.assertEqual(probe["observed_response"]["content_list_length"], 100)
        self.assertLess(probe["observed_response"]["content_list_length"], probe["observed_response"]["content_listCount"])

    def test_all_pages_logic_handles_server_side_page_cap(self):
        def page_doc(total, page, items):
            return {"api": {"listCount": 0, "list": []}, "content": {"listCount": total, "page": page, "list": items}}

        docs = [
            page_doc(3, 1, [{"id": 1}, {"id": 2}]),
            page_doc(3, 2, [{"id": 3}]),
        ]
        # Two identical complete passes are required for a stable corpus.
        responses = [
            (json.dumps(doc).encode("utf-8"), 200, "application/json")
            for doc in docs + docs
        ]

        with tempfile.TemporaryDirectory() as tmp, patch.object(pagination, "fetch_raw", side_effect=responses):
            aggregate, meta = pagination.fetch_all_list_pages(
                output_dir=Path(tmp), per_page=1000, selected_lang="ka", timeout=1, max_pages=None
            )
            self.assertTrue(meta["count_complete_against_reported_total"])
            self.assertTrue(meta["stable_across_two_full_passes"])
            self.assertTrue(meta["complete_against_reported_total"])
            self.assertEqual(meta["reported_total"], 3)
            self.assertEqual(len(meta["passes"]), 2)
            self.assertTrue(all(p["effective_first_page_size"] == 2 for p in meta["passes"]))
            self.assertTrue(all(p["raw_page_count"] == 2 for p in meta["passes"]))
            self.assertEqual([item["id"] for item in aggregate["content"]["list"]], [1, 2, 3])

    def test_all_pages_marks_changing_list_count_incomplete(self):
        def page_doc(total, page, items):
            return {"api": {"listCount": 0, "list": []}, "content": {"listCount": total, "page": page, "list": items}}

        pass_docs = [
            page_doc(3, 1, [{"id": 1}, {"id": 2}]),
            page_doc(4, 2, [{"id": 3}]),
        ]
        responses = [
            (json.dumps(doc).encode("utf-8"), 200, "application/json")
            for doc in pass_docs + pass_docs
        ]
        with tempfile.TemporaryDirectory() as tmp, patch.object(pagination, "fetch_raw", side_effect=responses):
            _, meta = pagination.fetch_all_list_pages(
                output_dir=Path(tmp), per_page=2, selected_lang="ka", timeout=1, max_pages=2
            )
            self.assertFalse(meta["count_complete_against_reported_total"])
            self.assertFalse(meta["complete_against_reported_total"])
            self.assertTrue(all(not p["list_count_stable_across_pages"] for p in meta["passes"]))
            self.assertEqual(meta["passes"][0]["reported_totals_seen"], [3, 4])

    def test_one_pass_rejects_conflicting_duplicate_id_contents(self):
        def page_doc(total, page, items):
            return {"api": {"listCount": 0, "list": []}, "content": {"listCount": total, "page": page, "list": items}}

        docs = [
            page_doc(2, 1, [{"id": 1, "title": "A"}]),
            page_doc(2, 2, [{"id": 1, "title": "B"}, {"id": 2, "title": "C"}]),
        ]
        responses = [(json.dumps(doc).encode("utf-8"), 200, "application/json") for doc in docs]
        with tempfile.TemporaryDirectory() as tmp, patch.object(pagination, "fetch_raw", side_effect=responses):
            _, meta = pagination._fetch_list_pass(
                output_dir=Path(tmp), per_page=1, selected_lang="ka", timeout=1, max_pages=2
            )
            self.assertFalse(meta["count_complete_against_reported_total"])
            self.assertEqual(meta["conflicting_duplicate_keys"], ["id:1"])

    def test_two_pass_check_detects_same_count_but_moving_corpus(self):
        def page_doc(total, page, items):
            return {"api": {"listCount": 0, "list": []}, "content": {"listCount": total, "page": page, "list": items}}

        docs = [
            page_doc(3, 1, [{"id": 1}, {"id": 2}]),
            page_doc(3, 2, [{"id": 3}]),
            page_doc(3, 1, [{"id": 1}, {"id": 2}]),
            page_doc(3, 2, [{"id": 4}]),
        ]
        responses = [(json.dumps(doc).encode("utf-8"), 200, "application/json") for doc in docs]
        with tempfile.TemporaryDirectory() as tmp, patch.object(pagination, "fetch_raw", side_effect=responses):
            _, meta = pagination.fetch_all_list_pages(
                output_dir=Path(tmp), per_page=2, selected_lang="ka", timeout=1, max_pages=None
            )
            self.assertTrue(meta["count_complete_against_reported_total"])
            self.assertFalse(meta["stable_identity_set_across_passes"])
            self.assertFalse(meta["stable_across_two_full_passes"])
            self.assertFalse(meta["complete_against_reported_total"])

    def test_compare_recomputes_completeness_from_csv_and_metadata(self):
        records = [{"id": "1"}]
        dishonest = {
            "complete_against_reported_total": True,
            "stable_across_two_full_passes": True,
            "reported_total": 999,
            "fetched_unique_count": 999,
        }
        complete, failures = compare.assess_corpus_completeness(records, dishonest)
        self.assertFalse(complete)
        self.assertIn("records_csv_count_mismatch", failures)

        honest_records = [{"id": "1"}, {"id": "2"}]
        honest = {
            "complete_against_reported_total": True,
            "stable_across_two_full_passes": True,
            "reported_total": 2,
            "fetched_unique_count": 2,
        }
        complete, failures = compare.assess_corpus_completeness(honest_records, honest)
        self.assertTrue(complete)
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
