from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "Paper-reproduction-apps" / "librts-paper" / "results" / "goal5523_parks_europe_point_contains_cardinality_gate.json"


class Goal5523ParksEuropePointContainsCardinalityTest(unittest.TestCase):
    def test_five_exact_cardinalities_match(self):
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        expected = {50000: 54568, 100000: 109279, 200000: 218598, 400000: 437276, 800000: 874543}
        observed = {
            int(case["query_cardinality"]): (int(case["author"]["result_count"]), int(case["rtdl"]["result_count"]), bool(case["matched"]))
            for case in payload["cases"]
        }
        self.assertEqual(observed, {key: (value, value, True) for key, value in expected.items()})

    def test_distinct_batches_and_prior_checkpoint(self):
        payload = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(payload["prepared_base"]["runtime_distinct_query_batches"], 5)
        self.assertFalse(payload["prepared_base"]["same_input_replay_used"])
        self.assertTrue(payload["evidence_accounting"]["all_query_files_distinct"])
        self.assertTrue(payload["evidence_accounting"]["prior_100000_checkpoint_identity_and_count_match"])
        self.assertTrue(payload["evidence_accounting"]["cache_is_app_owned"])

    def test_point_contains_inventory_is_complete_at_count_level(self):
        coverage = json.loads(RESULT.read_text(encoding="utf-8"))["coverage"]
        self.assertEqual(coverage["exact_archive_point_contains_pair_count"], 14)
        self.assertEqual(coverage["matched_after_goal5523"], 14)
        self.assertEqual(coverage["remaining_not_checkpointed"], 0)
        self.assertTrue(coverage["complete_point_contains_matrix_claimed"])

    def test_claim_boundary(self):
        boundary = json.loads(RESULT.read_text(encoding="utf-8"))["claim_boundary"]
        self.assertTrue(boundary["complete_point_contains_count_matrix_only"])
        self.assertFalse(boundary["pointwise_containment_equivalence_claimed"])
        self.assertFalse(boundary["performance_ratio_authorized"])
        self.assertFalse(boundary["figure_reproduction_claimed"])
        self.assertFalse(boundary["complete_paper_reproduction_claimed"])
        self.assertFalse(boundary["author_specific_rtdl_core_behavior_authorized"])
        self.assertFalse(boundary["embree_in_scope"])


if __name__ == "__main__":
    unittest.main()
