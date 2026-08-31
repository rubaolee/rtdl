from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"


class Goal5513RangeIntersectsSelect001Test(unittest.TestCase):
    def test_manifest_has_four_cases(self) -> None:
        cases = json.loads(
            (APP / "data" / "goal5513_range_intersects_select001_exact_batch.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(len(cases), 4)
        self.assertEqual(
            {case["query_member"] for case in cases},
            {
                "PPoPPAE/datasets/queries/range-intersects_select_0.01_queries_10000/"
                + suffix
                for suffix in (
                    "parks_Europe.wkt",
                    "dtl_cnty.wkt",
                    "USACensusBlockGroupBoundaries.wkt",
                    "USADetailedWaterBodies.wkt",
                )
            },
        )

    def test_gate_has_four_count_matches_and_no_overclaim(self) -> None:
        result = json.loads(
            (APP / "results" / "goal5513_exact_range_intersects_select001_gate.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(result["query_family"], "range-intersects_select_0.01_queries_10000")
        self.assertEqual(result["case_count"], 4)
        self.assertEqual(result["matched_case_count"], 4)
        self.assertFalse(result["claim_boundary"]["complete_range_intersects_matrix_claimed"])
        self.assertFalse(result["claim_boundary"]["pointwise_intersection_equivalence_claimed"])
        self.assertFalse(result["claim_boundary"]["performance_ratio_authorized"])
        self.assertFalse(result["claim_boundary"]["complete_paper_reproduction_claimed"])
        self.assertFalse(result["claim_boundary"]["embree_in_scope"])

    def test_case_counts_are_equal(self) -> None:
        result = json.loads(
            (APP / "results" / "goal5513_exact_range_intersects_select001_gate.json").read_text(
                encoding="utf-8"
            )
        )
        for case in result["cases"]:
            self.assertTrue(case["matched"])
            self.assertEqual(case["author"]["result_count"], case["rtdl"]["result_count"])
            self.assertTrue(case["input_identity"]["same_files_passed_to_author_and_rtdl"])


if __name__ == "__main__":
    unittest.main()
