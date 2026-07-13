from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
RESULTS = APP / "results"


class Goal5498LibrtsExactRangeIntersectsLineCloseoutTest(unittest.TestCase):
    def test_closeout_is_bounded_to_two_matched_cases(self):
        first = json.loads(
            (RESULTS / "librts_goal5496_range_intersects_dtl_cnty_gate.json").read_text(
                encoding="utf-8"
            )
        )
        second = json.loads(
            (RESULTS / "librts_goal5497_range_intersects_dtl_cnty_select0001_gate.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(first["matched"])
        self.assertTrue(second["matched"])
        self.assertEqual(first["author"]["result_count"], 1570285)
        self.assertEqual(second["author"]["result_count"], 242920)
        self.assertEqual(first["input_identity"]["geometry_sha256"], second["input_identity"]["geometry_sha256"])
        self.assertNotEqual(first["input_identity"]["query_sha256"], second["input_identity"]["query_sha256"])
        self.assertEqual(first["author"]["load_factor"], "1")
        self.assertEqual(second["author"]["load_factor"], "1")
        self.assertFalse(first["claim_boundary"]["performance_ratio_authorized"])
        self.assertFalse(second["claim_boundary"]["performance_ratio_authorized"])

    def test_manifest_does_not_claim_full_range_intersects_coverage(self):
        manifest = json.loads(
            (APP / "data" / "manifest.json").read_text(encoding="utf-8")
        )
        boundaries = manifest["boundaries"]
        self.assertTrue(boundaries["goal5497_exact_range_intersects_batch_matched"])
        self.assertNotIn("goal5498_full_range_intersects_matrix_matched", boundaries)
        self.assertFalse(boundaries["full_paper_reproduction_claimed"])
        self.assertFalse(boundaries["author_performance_parity_claimed"])


if __name__ == "__main__":
    unittest.main()
