from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"


class Goal5512RangeIntersectsCapacityResolutionTest(unittest.TestCase):
    def test_large_case_gate_distinguishes_match_and_capacity_failure(self) -> None:
        result = json.loads(
            (APP / "results" / "goal5512_range_intersects_capacity_resolution_gate.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(result["query_family"], "range-intersects_select_0.0001_queries_10000")
        self.assertEqual(result["matched_case_count"], 1)
        self.assertEqual(result["author_capacity_failure_case_count"], 1)
        self.assertEqual(result["unresolved_case_count"], 0)
        self.assertTrue(result["claim_boundary"]["count_match_only_for_lakes"])
        self.assertTrue(result["claim_boundary"]["parks_author_capacity_failure_only"])
        self.assertFalse(result["claim_boundary"]["complete_range_intersects_matrix_claimed"])
        self.assertFalse(result["claim_boundary"]["pointwise_intersection_equivalence_claimed"])
        self.assertFalse(result["claim_boundary"]["performance_ratio_authorized"])

    def test_parks_failure_is_not_a_semantic_mismatch(self) -> None:
        parks = json.loads(
            (APP / "results" / "goal5512_parks_bz2_select0001_10000.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(parks["status"], "author_capacity_failure")
        self.assertIn("cudaErrorMemoryAllocation", parks["author"]["stderr"])
        self.assertFalse(parks["claim_boundary"]["semantic_mismatch_claimed"])


if __name__ == "__main__":
    unittest.main()
