from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "Paper-reproduction-apps" / "librts-paper" / "results" / "goal5520_parks_europe_range_contains_cardinality_gate.json"


class Goal5520ParksEuropeRangeContainsCardinalityTest(unittest.TestCase):
    def test_five_exact_cardinalities_match(self):
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "parks_europe_exact_range_contains_five_cardinality_matrix_matched")
        expected = {50000: 52245, 100000: 104426, 200000: 208918, 400000: 417968, 800000: 835864}
        observed = {
            int(case["query_cardinality"]): (
                int(case["author"]["result_count"]),
                int(case["rtdl"]["result_count"]),
            )
            for case in payload["cases"]
        }
        self.assertEqual(observed, {key: (value, value) for key, value in expected.items()})
        self.assertEqual(payload["matched_case_count"], 5)

    def test_prepared_session_and_prior_checkpoint_are_not_conflated(self):
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        prepared = payload["prepared_base"]
        self.assertEqual(prepared["runtime_distinct_query_batches"], 4)
        self.assertEqual(prepared["matrix_distinct_query_batches"], 5)
        self.assertEqual(prepared["prior_checkpoint_case_count"], 1)
        self.assertFalse(prepared["same_input_replay_used"])
        self.assertTrue(payload["evidence_accounting"]["all_query_files_distinct"])
        self.assertTrue(payload["evidence_accounting"]["cache_is_app_owned"])

    def test_claims_remain_bounded(self):
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        boundary = payload["claim_boundary"]
        self.assertFalse(boundary["same_input_replay_claimed"])
        self.assertFalse(boundary["pointwise_containment_equivalence_claimed"])
        self.assertFalse(boundary["complete_range_contains_matrix_claimed"])
        self.assertFalse(boundary["performance_ratio_authorized"])
        self.assertFalse(boundary["complete_paper_reproduction_claimed"])
        self.assertFalse(boundary["author_specific_rtdl_core_behavior_authorized"])
        self.assertFalse(boundary["embree_in_scope"])
        self.assertEqual(payload["coverage"]["matched_after_goal5520"], 9)
        self.assertEqual(payload["coverage"]["remaining_not_checkpointed"], 5)


if __name__ == "__main__":
    unittest.main()
