import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    REPO_ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_ranked_summary_wall_time_boundary_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")
TUTORIAL = REPO_ROOT / "tutorials" / "current" / "11_rtnn_ranked_summary_boundary.md"


class V3PhoenixRTNNRankedSummaryWallTimeBoundaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")
        cls.tutorial = TUTORIAL.read_text(encoding="utf-8")

    def test_packet_is_wall_time_boundary_not_m7(self):
        self.assertEqual(
            self.payload["status"],
            "rtnn_ranked_summary_wall_time_boundary_not_m7",
        )
        self.assertEqual(self.payload["generic_capability"], "ranked_summary")
        self.assertEqual(
            self.payload["generic_capability_status"],
            "distribution_specific_candidate_wall_regression",
        )
        self.assertFalse(self.payload["release_authorized"])
        self.assertFalse(self.payload["public_speedup_claim_authorized"])
        self.assertFalse(self.payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(self.payload["universal_rtnn_acceleration_claim_authorized"])
        self.assertFalse(self.payload["paper_reproduction_claim_authorized"])
        self.assertFalse(self.payload["m7_promotion_authorized"])
        self.assertEqual(self.payload["m7_qualified_release_rows"], 0)
        self.assertEqual(
            self.payload["current_packet_external_review_status"],
            "claude_approved_after_p1_tutorial_fix",
        )
        self.assertEqual(
            self.payload["current_packet_2ai_consensus_status"],
            "claude_codex_consensus_complete_no_m7_promotion",
        )

    def test_rows_make_hot_signal_and_wall_loss_visible(self):
        rows = {row["distribution"]: row for row in self.payload["rows"]}
        self.assertAlmostEqual(rows["clustered"]["hot_optix_over_embree"], 3.3328837799050297)
        self.assertAlmostEqual(rows["clustered"]["wall_optix_over_embree"], 0.6250743900537069)
        self.assertAlmostEqual(rows["shell"]["hot_optix_over_embree"], 1.1816254369605883)
        self.assertAlmostEqual(rows["shell"]["wall_optix_over_embree"], 0.3157743032193997)
        self.assertAlmostEqual(rows["uniform"]["hot_optix_over_embree"], 1.0835478947384676)
        self.assertAlmostEqual(rows["uniform"]["wall_optix_over_embree"], 0.30313162572346836)
        for row in rows.values():
            self.assertEqual(row["query_count"], 65536)
            self.assertEqual(row["k_max"], 50)
            self.assertGreater(row["hot_optix_over_embree"], 1.0)
            self.assertLess(row["wall_optix_over_embree"], 1.0)

    def test_blockers_and_forbidden_wording_are_explicit(self):
        blockers = set(self.payload["m7_blockers"])
        self.assertIn("wall_timing_optix_slower_than_embree_for_all_three_distributions", blockers)
        self.assertIn("distribution_specific_not_universal_rtnn_acceleration", blockers)
        self.assertIn("no_multi_run_variance_evidence", blockers)
        forbidden = "\n".join(self.payload["forbidden_public_wording"])
        self.assertIn("RTNN V3 is 3.333x faster", forbidden)
        self.assertIn("V3 proves universal RTNN acceleration", forbidden)
        self.assertIn("RTDL beats Embree for RTNN end to end", forbidden)
        self.assertIn("RTNN is M7-qualified", forbidden)

    def test_markdown_and_tutorial_preserve_claim_boundary(self):
        for text in (self.text, self.tutorial):
            self.assertIn("3.333x", text)
            self.assertIn("0.625x", text)
            self.assertIn("Wall ratios below 1.0 mean OptiX is slower", text)
            self.assertIn("3.16x as long as Embree", text)
            self.assertIn("not a release", text)
            self.assertIn("Do not claim RTNN V3 is 3.333x faster", text)
            self.assertIn("Do not claim V3 proves universal RTNN acceleration", text)
        self.assertIn("materialized summary-row overhead", self.tutorial)
        self.assertIn("paper-equivalent", self.tutorial)
        self.assertIn("Was I foolish?", self.text)
        self.assertIn("No. The prior 2-AI intake already accepts the hot signal", self.text)


if __name__ == "__main__":
    unittest.main()
