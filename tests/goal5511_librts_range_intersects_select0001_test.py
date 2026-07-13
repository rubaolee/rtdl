from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"


class Goal5511RangeIntersectsSelect0001Test(unittest.TestCase):
    def test_manifest_has_four_exact_archive_cases(self) -> None:
        cases = json.loads(
            (APP / "data" / "goal5511_range_intersects_select0001_exact_batch.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(len(cases), 4)
        self.assertEqual(
            {case["query_member"] for case in cases},
            {
                "PPoPPAE/datasets/queries/range-intersects_select_0.001_queries_10000/"
                + suffix
                for suffix in (
                    "parks_Europe.wkt",
                    "dtl_cnty.wkt",
                    "USACensusBlockGroupBoundaries.wkt",
                    "USADetailedWaterBodies.wkt",
                )
            },
        )

    def test_gate_has_four_count_matches_and_strict_boundaries(self) -> None:
        result = json.loads(
            (APP / "results" / "goal5511_exact_range_intersects_select0001_gate.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(result["query_family"], "range-intersects_select_0.001_queries_10000")
        self.assertEqual(result["case_count"], 4)
        self.assertEqual(result["matched_case_count"], 4)
        self.assertTrue(result["evidence_integrity"]["same_files_passed_to_author_and_rtdl"])
        self.assertFalse(result["claim_boundary"]["complete_range_intersects_matrix_claimed"])
        self.assertFalse(result["claim_boundary"]["pointwise_intersection_equivalence_claimed"])
        self.assertFalse(result["claim_boundary"]["performance_ratio_authorized"])
        self.assertFalse(result["claim_boundary"]["complete_paper_reproduction_claimed"])
        self.assertFalse(result["claim_boundary"]["embree_in_scope"])

    def test_each_case_is_author_rtdl_count_level_only(self) -> None:
        result = json.loads(
            (APP / "results" / "goal5511_exact_range_intersects_select0001_gate.json").read_text(
                encoding="utf-8"
            )
        )
        for case in result["cases"]:
            self.assertTrue(case["matched"])
            self.assertTrue(case["input_identity"]["same_files_passed_to_author_and_rtdl"])
            self.assertEqual(case["author"]["result_count"], case["rtdl"]["result_count"])
            self.assertFalse(case["claim_boundary"]["pointwise_intersection_equivalence_claimed"])


if __name__ == "__main__":
    unittest.main()
