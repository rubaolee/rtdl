from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MATRIX = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5300_thai_asian_level_b_rtdl_comparison_matrix_2026-07-09.json"
)


class Goal5300ThaiAsianRtdlComparisonTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        cls.routes = {route["route_id"]: route for route in cls.matrix["rtdl_routes"]}

    def test_matrix_is_level_b_and_no_ratio_claim(self) -> None:
        self.assertEqual(
            self.matrix["schema"],
            "rtdl.paper_reproduction.xhd.goal5300.thai_asian_level_b_rtdl_comparison.v1",
        )
        self.assertEqual(self.matrix["case_id"], "thai_asian_scaled")
        self.assertEqual(self.matrix["level"], "level_b_same_source_graphics_candidate")
        boundary = self.matrix["claim_boundary"]
        self.assertTrue(boundary["level_b_same_source_rtdl_comparison_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["figure_reproduction_claimed"])
        self.assertFalse(boundary["full_paper_reproduction_claimed"])
        self.assertFalse(boundary["author_performance_parity_claimed"])
        self.assertFalse(boundary["author_vs_rtdl_ratio_claimed"])
        self.assertFalse(boundary["author_rt_core_algorithm_equivalence_claimed"])
        self.assertFalse(self.matrix["ratio_policy"]["ratio_authorized"])

    def test_author_case_is_goal5298_value_matched(self) -> None:
        author = self.matrix["author"]
        self.assertEqual(author["source_goal"], "Goal5298")
        self.assertTrue(author["matched_paper_log_value"])
        self.assertEqual(author["input_point_counts"], [4999996, 3609600])
        self.assertAlmostEqual(author["hd_result"], 0.28763842582702637)
        self.assertLessEqual(author["paper_log_abs_diff"], 1e-6)

    def test_exact_witness_route_matches_author_and_keeps_exact_witness(self) -> None:
        route = self.routes["exact_witness"]
        self.assertEqual(route["route_label"], "cell-mbr-exact-witness")
        self.assertTrue(route["matched_author_rerun"])
        self.assertTrue(route["matched_paper_log"])
        self.assertTrue(route["per_source_witness_exact"])
        self.assertFalse(route["global_bound_early_break"])
        self.assertEqual(route["frontier_row_count"], 0)
        self.assertLessEqual(route["abs_diff_vs_author_rerun"], 1e-6)
        self.assertAlmostEqual(route["hd_result"], 0.2876384148709406)

    def test_fast_scalar_route_matches_scalar_but_not_exact_witness(self) -> None:
        route = self.routes["fast_scalar"]
        self.assertEqual(route["route_label"], "cell-mbr-fast-scalar")
        self.assertTrue(route["matched_author_rerun"])
        self.assertTrue(route["matched_paper_log"])
        self.assertFalse(route["per_source_witness_exact"])
        self.assertTrue(route["global_bound_early_break"])
        self.assertGreater(route["global_bound_early_break_count"], 0)
        self.assertGreater(route["frontier_row_count"], 0)
        self.assertLessEqual(route["abs_diff_vs_author_rerun"], 1e-6)
        self.assertAlmostEqual(route["hd_result"], 0.2876384148709406)

    def test_exact_witness_is_faster_than_fast_scalar_on_this_pair(self) -> None:
        exact = self.routes["exact_witness"]
        fast = self.routes["fast_scalar"]
        self.assertLess(exact["rtdl_route_wall_sec"], fast["rtdl_route_wall_sec"])
        self.assertIn("exact-witness is faster", " ".join(self.matrix["observations"]))

    def test_route_artifacts_exist(self) -> None:
        for route in self.matrix["rtdl_routes"]:
            with self.subTest(route=route["route_id"]):
                artifact = ROOT / route["artifact"]
                process_artifact = ROOT / route["process_artifact"]
                self.assertTrue(artifact.exists(), artifact)
                self.assertTrue(process_artifact.exists(), process_artifact)
                payload = json.loads(artifact.read_text(encoding="utf-8"))
                process = json.loads(process_artifact.read_text(encoding="utf-8"))
                self.assertIn("HDResult", payload)
                self.assertIn("RTDL", payload)
                self.assertEqual(process["returncode"], 0)


if __name__ == "__main__":
    unittest.main()
