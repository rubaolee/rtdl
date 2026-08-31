from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
SUMMARY = RESULTS / "xhd_goal5313_water_bg_n_points_cell_alignment_summary.json"
AUTHOR_NPC8 = RESULTS / "xhd_goal5313_author_water_bg_full_public_n_points_cell_8.json"
WITNESS_PROBE = RESULTS / "xhd_goal5313_water_bg_witness_distance_probe.json"


class Goal5313XhdWaterBgNPointsCellAlignmentTest(unittest.TestCase):
    def test_author_paper_config_reproduces_paper_log_value(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5313.water_bg_n_points_cell_alignment.v1",
        )
        self.assertTrue(payload["decision"]["goal5311_author_default_mismatch_explained"])
        self.assertTrue(payload["decision"]["water_bg_public_candidate_matches_author_paper_config"])
        self.assertFalse(payload["decision"]["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(payload["decision"]["figure5_reproduction_claimed"])
        self.assertFalse(payload["decision"]["performance_ratio_claimed"])

        default = payload["author_rerun_default_goal5311"]
        self.assertEqual(default["num_points_per_cell"], 15)
        self.assertAlmostEqual(default["hd_result"], 0.8970130085945129)
        self.assertFalse(default["matches_paper_log"])

        paper_config = payload["author_rerun_paper_config_goal5313"]
        self.assertEqual(paper_config["num_points_per_cell"], 8)
        self.assertAlmostEqual(paper_config["hd_result"], 0.8964367508888245)
        self.assertEqual(paper_config["abs_diff_vs_paper_log"], 0.0)
        self.assertTrue(paper_config["matches_paper_log"])

    def test_witness_probe_separates_float64_rtdl_from_float32_author_value(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        witness = payload["witness_pair_probe"]

        self.assertEqual(witness["source_id"], 13579843)
        self.assertEqual(witness["target_id"], 22441127)
        self.assertAlmostEqual(witness["distance_float64"], 0.8964380566690101)
        self.assertAlmostEqual(witness["distance_float32_numpy"], 0.8964367508888245)
        self.assertTrue(witness["distance_float64_matches_rtdl"])
        self.assertTrue(witness["distance_float32_matches_paper_log"])

        rtdl = payload["rtdl_exact_witness_goal5312"]
        self.assertTrue(rtdl["per_source_witness_exact"])
        self.assertAlmostEqual(rtdl["abs_diff_vs_author_paper_config"], 1.305780185645311e-06)
        self.assertFalse(payload["decision"]["rtdl_float64_matches_author_float32_at_1e_6"])
        self.assertTrue(payload["decision"]["rtdl_float64_matches_author_float32_at_2e_6"])

    def test_underlying_artifacts_remain_json_and_claim_bounded(self) -> None:
        author = json.loads(AUTHOR_NPC8.read_text(encoding="utf-8"))
        self.assertEqual(author["Running"]["NumPointsPerCell"], 8)
        self.assertEqual(author["Input"]["Type"], "Float")
        self.assertFalse(author["Input"]["Normalize"])

        witness = json.loads(WITNESS_PROBE.read_text(encoding="utf-8"))
        self.assertTrue(witness["interpretation"]["rtdl_witness_pair_is_self_consistent"])
        self.assertTrue(witness["interpretation"]["rtdl_witness_pair_float32_matches_paper_log"])
        self.assertFalse(witness["interpretation"]["full_public_author_scalar_match_closed"])


if __name__ == "__main__":
    unittest.main()
