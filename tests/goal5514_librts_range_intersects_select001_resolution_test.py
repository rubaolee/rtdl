from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"


class Goal5514RangeIntersectsSelect001ResolutionTest(unittest.TestCase):
    def test_six_geometry_states_are_resolved(self) -> None:
        result = json.loads((APP / "results" / "goal5514_exact_range_intersects_select001_resolution_gate.json").read_text(encoding="utf-8"))
        self.assertEqual(result["case_count"], 6)
        self.assertEqual(result["matched_case_count"], 5)
        self.assertEqual(result["author_capacity_failure_case_count"], 1)
        self.assertEqual(result["unresolved_case_count"], 0)
        self.assertTrue(result["claim_boundary"]["author_capacity_failure_not_semantic_mismatch"])
        self.assertFalse(result["claim_boundary"]["complete_range_intersects_matrix_claimed"])
        self.assertFalse(result["claim_boundary"]["pointwise_intersection_equivalence_claimed"])
        self.assertFalse(result["claim_boundary"]["performance_ratio_authorized"])

    def test_parks_failure_is_explicit(self) -> None:
        parks = json.loads((APP / "results" / "goal5514_parks_bz2_select001_10000.json").read_text(encoding="utf-8"))
        self.assertEqual(parks["status"], "author_capacity_failure")
        self.assertIn("cudaErrorMemoryAllocation", parks["author"]["stderr"])
        self.assertFalse(parks["claim_boundary"]["semantic_mismatch_claimed"])


if __name__ == "__main__":
    unittest.main()
