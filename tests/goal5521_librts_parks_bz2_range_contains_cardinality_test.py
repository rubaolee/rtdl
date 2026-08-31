from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "Paper-reproduction-apps" / "librts-paper" / "results"
RESULT = RESULTS / "goal5521_parks_bz2_range_contains_cardinality_gate.json"
PRECHECK = RESULTS / "goal5521_parks_bz2_author_capacity_precheck.json"


class Goal5521ParksBz2RangeContainsCardinalityTest(unittest.TestCase):
    def test_five_exact_cardinalities_match_author_rtdl_and_paper_log(self):
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        expected = {50000: 52849, 100000: 105826, 200000: 211714, 400000: 423396, 800000: 846860}
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

    def test_capacity_precheck_and_distinct_batch_accounting(self):
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        precheck = json.loads(PRECHECK.read_text(encoding="utf-8"))
        self.assertEqual(precheck["status"], "parks_bz2_author_50000_completed")
        self.assertTrue(precheck["decision"]["authorize_rtdl_cache_and_matrix"])
        self.assertFalse(precheck["capacity_failure"])
        self.assertEqual(payload["prepared_base"]["runtime_distinct_query_batches"], 5)
        self.assertFalse(payload["prepared_base"]["same_input_replay_used"])
        self.assertTrue(payload["evidence_accounting"]["all_query_files_distinct"])
        self.assertTrue(payload["evidence_accounting"]["cache_is_app_owned"])

    def test_range_contains_inventory_is_complete_at_count_level(self):
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        coverage = payload["coverage"]
        self.assertEqual(coverage["exact_archive_range_contains_pair_count"], 14)
        self.assertEqual(coverage["matched_before_goal5521"], 9)
        self.assertEqual(coverage["new_goal5521_matches"], 5)
        self.assertEqual(coverage["matched_after_goal5521"], 14)
        self.assertEqual(coverage["remaining_not_checkpointed"], 0)
        self.assertTrue(coverage["complete_range_contains_matrix_claimed"])

    def test_claims_remain_count_level_and_bounded(self):
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        boundary = payload["claim_boundary"]
        self.assertTrue(boundary["complete_range_contains_count_matrix_only"])
        self.assertFalse(boundary["pointwise_containment_equivalence_claimed"])
        self.assertFalse(boundary["performance_ratio_authorized"])
        self.assertFalse(boundary["figure_reproduction_claimed"])
        self.assertFalse(boundary["complete_paper_reproduction_claimed"])
        self.assertFalse(boundary["author_specific_rtdl_core_behavior_authorized"])
        self.assertFalse(boundary["embree_in_scope"])


if __name__ == "__main__":
    unittest.main()
