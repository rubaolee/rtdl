import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    REPO_ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_hausdorff_threshold_summary_boundary_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")
TUTORIAL = REPO_ROOT / "tutorials" / "current" / "13_hausdorff_threshold_summary.md"


class V3PhoenixHausdorffThresholdSummaryBoundaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")
        cls.tutorial = TUTORIAL.read_text(encoding="utf-8")

    def test_packet_is_boundary_not_m7(self):
        self.assertEqual(
            self.payload["status"],
            "hausdorff_threshold_summary_boundary_not_m7",
        )
        self.assertEqual(self.payload["generic_capability"], "threshold_summary")
        self.assertFalse(self.payload["release_authorized"])
        self.assertFalse(self.payload["public_speedup_claim_authorized"])
        self.assertFalse(self.payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(self.payload["full_hausdorff_witness_claim_authorized"])
        self.assertFalse(self.payload["m7_promotion_authorized"])
        self.assertEqual(self.payload["m7_qualified_release_rows"], 0)

    def test_rows_show_query_wins_and_mixed_wall_timing(self):
        rows = {row["copies"]: row for row in self.payload["rows"]}
        self.assertAlmostEqual(rows[16384]["query_optix_over_embree"], 2.0004351689051236)
        self.assertAlmostEqual(rows[16384]["wall_optix_over_embree"], 0.656528063761309)
        self.assertAlmostEqual(rows[65536]["query_optix_over_embree"], 1.5953013783748708)
        self.assertAlmostEqual(rows[65536]["wall_optix_over_embree"], 0.9652152672040554)
        self.assertAlmostEqual(rows[262144]["query_optix_over_embree"], 1.8644032673876425)
        self.assertAlmostEqual(rows[262144]["wall_optix_over_embree"], 1.2576431649500308)

    def test_best_current_row_has_oracle_match_but_repeat_one_blocks_m7(self):
        row = self.payload["best_current_row"]
        self.assertEqual(row["candidate_row_id"], "hausdorff_threshold_summary_copies_262144")
        self.assertEqual(row["comparison_group"], "hausdorff_threshold_copies_262144")
        self.assertEqual(row["point_count_a"], 1048576)
        self.assertEqual(row["point_count_b"], 1048576)
        self.assertAlmostEqual(row["threshold"], 0.4)
        self.assertAlmostEqual(row["query_optix_over_embree"], 1.8644032673876425)
        self.assertAlmostEqual(row["wall_optix_over_embree"], 1.2576431649500308)
        self.assertEqual(row["warmup"], 0)
        self.assertEqual(row["repeat"], 1)
        self.assertTrue(row["matches_oracle"])
        self.assertTrue(row["oracle_decision_matches"])
        self.assertTrue(row["oracle_identity_matches"])
        self.assertTrue(row["oracle_within_threshold"])
        self.assertFalse(row["m7_promotion_authorized"])
        self.assertFalse(row["row_scoped_public_speedup_claim_authorized"])
        self.assertEqual(row["m7_blocker"], "repeat1_no_multi_run_variance_evidence")

    def test_blockers_and_forbidden_wording_are_explicit(self):
        blockers = set(self.payload["m7_blockers"])
        self.assertIn("threshold_decision_only_not_full_exact_hausdorff_witness", blockers)
        self.assertIn("wall_timing_mixed_across_scales", blockers)
        self.assertIn("repeat1_no_multi_run_variance_evidence", blockers)
        self.assertIn("no_current_rtx_pod_rerun", blockers)
        forbidden = "\n".join(self.payload["forbidden_public_wording"])
        self.assertIn("Hausdorff V3 is 2x faster end to end", forbidden)
        self.assertIn("full exact Hausdorff witness materialization", forbidden)
        self.assertIn("threshold_summary is M7-qualified", forbidden)

    def test_markdown_and_tutorial_preserve_claim_boundary(self):
        self.assertIn("2.000x", self.text)
        self.assertIn("0.657x", self.text)
        self.assertIn("Do not claim Hausdorff V3 is 2x faster end to end", self.text)
        self.assertIn("Do not claim RTDL accelerates full exact Hausdorff witness materialization", self.text)
        self.assertIn("not a release", self.text)
        self.assertIn("repeat", self.text)
        self.assertIn("hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped", self.tutorial)
        self.assertIn("query speedup mean: 1.639x", self.tutorial)
        self.assertIn("phase-total speedup mean: 1.240x", self.tutorial)
        self.assertIn("weakest phase-total speedup: 1.224x", self.tutorial)
        self.assertIn("phase-total includes scene preparation", self.tutorial)
        self.assertIn("Do not claim Hausdorff V3 is faster end to end", self.tutorial)
        self.assertIn("not a release", self.tutorial)
        self.assertIn("Was I foolish?", self.text)


if __name__ == "__main__":
    unittest.main()
