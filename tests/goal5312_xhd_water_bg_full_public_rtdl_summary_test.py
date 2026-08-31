from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5312_water_bg_full_public_rtdl_summary.json"
)
FAST_JSON = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5312_water_bg_full_public_rtdl_cell_mbr.json"
)
EXACT_JSON = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5312_water_bg_full_public_rtdl_exact_witness.json"
)


class Goal5312XhdWaterBgFullPublicRtdlSummaryTest(unittest.TestCase):
    def test_summary_records_full_public_execution_but_not_author_match(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5312.water_bg_full_public_rtdl_route_summary.v1",
        )
        self.assertTrue(payload["decision"]["full_public_rtdl_execution_passed"])
        self.assertFalse(payload["decision"]["author_same_public_scalar_match_passed"])
        self.assertTrue(payload["decision"]["fast_scalar_is_not_correctness_gate"])
        self.assertFalse(payload["decision"]["performance_ratio_claimed"])

        author = payload["author_same_public"]
        self.assertAlmostEqual(author["hd_result"], 0.8970130085945129)
        self.assertAlmostEqual(author["paper_log_hd_result"], 0.8964367508888245)
        self.assertEqual(author["point_counts"], [22824823, 52271467])

        for key in ("rtdl_fast_scalar", "rtdl_exact_witness"):
            route = payload[key]
            self.assertAlmostEqual(route["hd_result"], 0.8964380566690101)
            self.assertFalse(route["matched_author_at_1e-6"])
            self.assertEqual(route["point_count_a"], 22824823)
            self.assertEqual(route["point_count_b"], 52271467)
            self.assertEqual(route["input_n_dims"], 2)
            self.assertEqual(route["execution_n_dims"], 3)
            self.assertTrue(route["lift_2d_to_3d_zero_z"])
            self.assertGreater(route["load_input_sec"], route["rtdl_route_sec"])

        self.assertFalse(payload["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(payload["claim_boundary"]["figure5_reproduction_claimed"])
        self.assertFalse(payload["claim_boundary"]["performance_ratio_claimed"])
        self.assertFalse(payload["claim_boundary"]["author_rt_core_algorithm_equivalence_claimed"])

    def test_underlying_route_artifacts_are_valid_json(self) -> None:
        for path in (FAST_JSON, EXACT_JSON):
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["RTDL"]["route"]["cell_mbr_summary"]["input_n_dims"], 2)
            self.assertEqual(payload["RTDL"]["route"]["cell_mbr_summary"]["execution_n_dims"], 3)
            self.assertTrue(payload["RTDL"]["route"]["cell_mbr_summary"]["lift_2d_to_3d_zero_z"])


if __name__ == "__main__":
    unittest.main()
