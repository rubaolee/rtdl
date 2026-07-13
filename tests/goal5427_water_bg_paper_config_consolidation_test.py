import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5427_water_bg_paper_config_consolidation.json"
)
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5427_water_bg_paper_config_consolidation.py"
)


class Goal5427WaterBgPaperConfigConsolidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_consolidates_existing_evidence_without_rerun(self) -> None:
        payload = self.summary
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5427.water_bg_paper_config_consolidation.v1",
        )
        self.assertTrue(payload["matched"])
        self.assertEqual(payload["status"], "existing_goal5314_evidence_sufficient__no_rerun")
        self.assertFalse(payload["execution"]["new_author_execution"])
        self.assertFalse(payload["execution"]["new_rtdl_execution"])
        self.assertFalse(payload["decision"]["rerun_required_now"])

    def test_uses_goal5314_paper_config_denominator(self) -> None:
        author = self.summary["author_denominator"]
        self.assertEqual(author["selected"], "goal5314_paper_config_n_points_cell_8")
        self.assertEqual(author["num_points_cell"], 8)
        self.assertAlmostEqual(author["hd_result"], 0.8964367508888245, places=12)
        self.assertTrue(author["matches_paper_log"])

    def test_keeps_goal5311_default_denominator_as_mismatch_only(self) -> None:
        default = self.summary["default_author_denominator_kept_as_config_sensitivity"]
        self.assertEqual(default["num_points_cell"], 15)
        self.assertAlmostEqual(default["goal5311_default_author_hd_result"], 0.8970130085945129, places=12)
        self.assertFalse(default["goal5311_paper_value_matched"])
        self.assertIn("must not be used as the paper denominator", default["reason"])

    def test_rtdl_exact_witness_matches_declared_tolerance(self) -> None:
        rtdl = self.summary["rtdl_evidence"]
        self.assertEqual(rtdl["route"], "existing_goal5314_exact_witness")
        self.assertTrue(rtdl["per_source_witness_exact"])
        self.assertAlmostEqual(rtdl["hd_result_float64"], 0.8964380566690101, places=12)
        self.assertAlmostEqual(rtdl["abs_diff_vs_author_paper_config"], 1.305780185645311e-06, places=15)
        self.assertLessEqual(rtdl["abs_diff_vs_author_paper_config"], rtdl["declared_tolerance"])
        self.assertTrue(rtdl["matched_with_declared_tolerance"])
        self.assertTrue(rtdl["distance_float32_matches_paper_log"])

    def test_input_artifact_reuse_comes_from_goal5426_hash_gate(self) -> None:
        reuse = self.summary["input_artifact_reuse"]
        self.assertTrue(reuse["goal5426_reuse_gate_passed"])
        self.assertFalse(reuse["goal5426_generation_safety_gate_passed"])
        self.assertTrue(reuse["waterbodies_goal5426_path"].endswith("USADetailedWaterBodies_full_public.wkt"))
        self.assertTrue(reuse["blockgroups_goal5426_path"].endswith("USACensusBlockGroupBoundaries_full_public.wkt"))
        self.assertEqual(
            reuse["waterbodies_sha256"],
            "0c4ad7d7c1953364478d4940a8eb1696cca24d0dfd6422aafc532b1983f3dd39",
        )
        self.assertEqual(
            reuse["blockgroups_sha256"],
            "8a1d3cd848083e5182de81521f07d8850c597910320250066d850928b017e66e",
        )

    def test_claim_boundary_blocks_overclaim(self) -> None:
        boundary = self.summary["claim_boundary"]
        self.assertTrue(boundary["full_public_level_b_scalar_match_claimed"])
        self.assertTrue(boundary["existing_evidence_consolidation_only"])
        self.assertFalse(boundary["new_execution_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["geo_figure5_reproduction_claimed"])
        self.assertFalse(boundary["full_xhd_paper_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["author_rt_core_equivalence_claimed"])
        self.assertFalse(boundary["route_micro_optimization_goal_authorized"])
        self.assertFalse(boundary["explicit_lb_reopened"])

    def test_script_is_consolidation_only(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("current_pod_ssh", source)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("hd_exec", source)
        self.assertNotIn("directed_max_of_nearest_distance", source)


if __name__ == "__main__":
    unittest.main()
