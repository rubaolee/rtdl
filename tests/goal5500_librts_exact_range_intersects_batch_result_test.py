from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
RESULTS = APP / "results"


class Goal5500ExactRangeIntersectsBatchResultTest(unittest.TestCase):
    def test_extraction_and_gate_cover_six_exact_pairs(self) -> None:
        extraction = json.loads(
            (RESULTS / "librts_goal5500_range_intersects_batch_extraction.json").read_text(
                encoding="utf-8"
            )
        )
        gate = json.loads(
            (RESULTS / "librts_goal5500_range_intersects_batch_gate.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(extraction["status"], "exact_archive_operation_batch_safely_extracted")
        self.assertEqual(extraction["extraction"]["selected_pair_count"], 6)
        self.assertEqual(extraction["extraction"]["selected_member_count"], 12)
        self.assertTrue(extraction["claim_boundary"]["archive_verified"])

        self.assertEqual(gate["schema"], "rtdl.paper_reproduction.librts.exact_range_intersects_batch.v1")
        self.assertEqual(gate["case_count"], 6)
        self.assertEqual(gate["matched_case_count"], 3)
        self.assertFalse(gate["matched"])
        self.assertEqual(gate["status"], "exact_input_range_intersects_batch_mismatch")
        self.assertFalse(gate["claim_boundary"]["complete_range_intersects_matrix_claimed"])
        self.assertFalse(gate["claim_boundary"]["pointwise_intersection_equivalence_claimed"])
        self.assertFalse(gate["claim_boundary"]["performance_ratio_authorized"])

    def test_case_outcomes_are_explicit_and_fail_closed(self) -> None:
        gate = json.loads(
            (RESULTS / "librts_goal5500_range_intersects_batch_gate.json").read_text(
                encoding="utf-8"
            )
        )
        by_geometry = {
            Path(case["input_identity"]["geometry_path"]).name: case
            for case in gate["cases"]
            if "input_identity" in case
        }

        expected_matches = {
            "dtl_cnty.wkt": 1_570_285,
            "USACensusBlockGroupBoundaries.wkt": 33_404_355,
            "USADetailedWaterBodies.wkt": 55_205_607,
        }
        for geometry, expected_count in expected_matches.items():
            case = by_geometry[geometry]
            self.assertTrue(case["matched"], geometry)
            self.assertEqual(case["author"]["result_count"], expected_count)
            self.assertEqual(case["rtdl"]["result_count"], expected_count)
            self.assertTrue(case["input_identity"]["same_files_passed_to_author_and_rtdl"])

        self.assertEqual(
            by_geometry["parks_Europe.wkt"]["status"],
            "exact_input_range_intersects_count_mismatch",
        )
        self.assertEqual(
            by_geometry["parks_Europe.wkt"]["rtdl"]["result_count"]
            - by_geometry["parks_Europe.wkt"]["author"]["result_count"],
            3_791,
        )
        self.assertEqual(
            by_geometry["lakes.bz2.wkt"]["rtdl"]["result_count"]
            - by_geometry["lakes.bz2.wkt"]["author"]["result_count"],
            54_695,
        )

        failed = next(
            case for case in gate["cases"] if case.get("status") == "case_execution_failed"
        )
        self.assertIn("out of memory", failed["error"].lower())
        self.assertFalse(failed["matched"])
        self.assertFalse(gate["claim_boundary"]["complete_paper_reproduction_claimed"])


if __name__ == "__main__":
    unittest.main()
