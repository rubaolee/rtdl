from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "Paper-reproduction-apps" / "librts-paper" / "results" / "goal5522_parks_bz2_point_contains_cardinality_gate.json"


class Goal5522ParksBz2PointContainsCardinalityTest(unittest.TestCase):
    def test_five_exact_cardinalities_match(self):
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        expected = {50000: 56428, 100000: 112729, 200000: 225699, 400000: 451007, 800000: 901103}
        observed = {
            int(case["query_cardinality"]): (
                int(case["author"]["result_count"]),
                int(case["rtdl"]["result_count"]),
                bool(case["matched"]),
            )
            for case in payload["cases"]
        }
        self.assertEqual(observed, {key: (value, value, True) for key, value in expected.items()})
        self.assertTrue(payload["evidence_accounting"]["all_author_counts_match_pinned_paper_logs"])

    def test_distinct_queries_and_app_owned_reuse(self):
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(payload["prepared_base"]["runtime_distinct_query_batches"], 5)
        self.assertFalse(payload["prepared_base"]["same_input_replay_used"])
        self.assertTrue(payload["evidence_accounting"]["all_query_files_distinct"])
        self.assertTrue(payload["evidence_accounting"]["cache_reused_from_goal5521"])
        self.assertTrue(payload["evidence_accounting"]["cache_is_app_owned"])

    def test_point_contains_coverage_moves_to_ten_of_fourteen(self):
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        coverage = payload["coverage"]
        self.assertEqual(coverage["matched_before_goal5522"], 6)
        self.assertEqual(coverage["new_unique_goal5522_matches"], 4)
        self.assertEqual(coverage["matched_after_goal5522"], 10)
        self.assertEqual(coverage["remaining_not_checkpointed"], 4)
        self.assertFalse(coverage["complete_point_contains_matrix_claimed"])

    def test_claims_remain_count_level(self):
        boundary = json.loads(RESULT.read_text(encoding="utf-8"))["claim_boundary"]
        self.assertFalse(boundary["pointwise_containment_equivalence_claimed"])
        self.assertFalse(boundary["performance_ratio_authorized"])
        self.assertFalse(boundary["figure_reproduction_claimed"])
        self.assertFalse(boundary["complete_paper_reproduction_claimed"])
        self.assertFalse(boundary["author_specific_rtdl_core_behavior_authorized"])
        self.assertFalse(boundary["embree_in_scope"])


if __name__ == "__main__":
    unittest.main()
