import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    REPO_ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_robot_collision_flag_stream_boundary_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")
TUTORIAL = REPO_ROOT / "tutorials" / "current" / "14_robot_collision_flag_stream.md"


class V3PhoenixRobotCollisionFlagStreamBoundaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")
        cls.tutorial = TUTORIAL.read_text(encoding="utf-8")

    def test_packet_is_boundary_not_m7(self):
        self.assertEqual(
            self.payload["status"],
            "robot_collision_flag_stream_boundary_not_m7",
        )
        self.assertEqual(self.payload["generic_capability"], "collision_flag_stream")
        self.assertFalse(self.payload["release_authorized"])
        self.assertFalse(self.payload["public_speedup_claim_authorized"])
        self.assertFalse(self.payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(self.payload["robot_planning_speedup_claim_authorized"])
        self.assertFalse(self.payload["exact_solid_collision_claim_authorized"])
        self.assertFalse(self.payload["continuous_collision_claim_authorized"])
        self.assertFalse(self.payload["m7_promotion_authorized"])
        self.assertEqual(self.payload["m7_qualified_release_rows"], 0)

    def test_row_keeps_hot_signal_beside_wall_boundary(self):
        row = self.payload["candidate_row"]
        self.assertEqual(row["app_id"], "robot_collision")
        self.assertEqual(row["comparison_group"], "prepared_collision_flags")
        self.assertEqual(row["generic_capability"], "collision_flag_stream")
        self.assertEqual(row["shape"]["pose_count"], 8192)
        self.assertEqual(row["shape"]["segment_count"], 147456)
        self.assertEqual(row["warmup_count"], 1)
        self.assertEqual(row["repeat_count"], 5)
        self.assertEqual(row["tail_measurement_count"], 4)
        self.assertTrue(row["run_level_probe_reference_matches"])
        self.assertAlmostEqual(row["hot_optix_over_embree"], 5.166099499578449)
        self.assertAlmostEqual(row["traversal_optix_over_embree"], 69.90408595731981)
        self.assertAlmostEqual(row["wall_optix_over_embree"], 0.9966762231083877)
        self.assertTrue(row["discrete_sampled_probe_contract_only"])
        self.assertFalse(row["continuous_collision_supported"])
        self.assertFalse(row["exact_solid_collision_claim_authorized"])
        self.assertIsNone(row["matches_cpu_reference"])
        self.assertIsNone(row["summary_matches_cpu_reference_field"])
        self.assertIn("matches_probe_reference=true", row["reference_evidence_note"])

    def test_paired_v2_context_blocks_broad_claim(self):
        context = self.payload["paired_v2_v3_context"]
        self.assertAlmostEqual(context["app_geomean_speedup_vs_v2_14"], 1.015679032862817)
        self.assertTrue(context["paired_rows_are_standard_goal2626_rows"])
        self.assertTrue(context["large_or_new_m7_row_same_v2_14_baseline_absent"])
        self.assertAlmostEqual(context["embree_v3_speedup_vs_v2_14"], 1.0030988288747607)
        self.assertAlmostEqual(context["optix_v3_speedup_vs_v2_14"], 1.0284170094728975)

    def test_blockers_and_forbidden_wording_are_explicit(self):
        blockers = set(self.payload["m7_blockers"])
        self.assertIn("wall_timing_is_parity_not_speedup", blockers)
        self.assertIn("probe_reference_dominates_wall_time", blockers)
        self.assertIn("discrete_sampled_probe_contract_only_not_full_robot_planning", blockers)
        self.assertIn("summary_matches_cpu_reference_field_null_in_all_app_row", blockers)
        forbidden = "\n".join(self.payload["forbidden_public_wording"])
        self.assertIn("Robot Collision V3 is 5.166x faster end to end", forbidden)
        self.assertIn("RTDL accelerates full robot planning", forbidden)
        self.assertIn("collision_flag_stream is M7-qualified", forbidden)

    def test_markdown_and_tutorial_preserve_claim_boundary(self):
        for text in (self.text,):
            self.assertIn("5.166x", text)
            self.assertIn("69.904x", text)
            self.assertIn("0.997x", text)
            self.assertIn("probe-reference", text)
            self.assertIn("Do not claim Robot Collision V3 is 5.166x faster end to end", text)
            self.assertIn("Do not claim RTDL accelerates full robot planning", text)
            self.assertIn("not a release", text)
        self.assertIn("5.086x", self.tutorial)
        self.assertIn("1.171x", self.tutorial)
        self.assertIn(
            "collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped",
            self.tutorial,
        )
        self.assertIn("probe-reference", self.tutorial)
        self.assertIn("Do not claim RTDL accelerates full robot planning", self.tutorial)
        self.assertIn("not a release", self.tutorial)
        self.assertIn("Was I foolish?", self.text)


if __name__ == "__main__":
    unittest.main()
