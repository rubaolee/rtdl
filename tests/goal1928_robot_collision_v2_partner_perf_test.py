from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1928_robot_collision_v2_partner_perf.py"
REPORT = ROOT / "docs" / "reports" / "goal1928_robot_collision_v2_partner_perf_2026-05-13.md"


class Goal1928RobotCollisionV2PartnerPerfTest(unittest.TestCase):
    def test_runner_compares_v1_8_robot_pose_flags_to_v2_partner_adapter(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("robot_profiler.run_suite", text)
        self.assertIn('result_mode="pose_flags"', text)
        self.assertIn("robot_collision_pose_flags_optix_prepared_partner_device_columns", text)
        self.assertIn("allocate_robot_collision_pose_partner_device_output_columns", text)
        self.assertIn("prepare_optix_ray_triangle_any_hit_2d_device_triangle_zero_copy_scene", text)
        self.assertIn("colliding_pose_count_match", text)
        self.assertIn("pose_collision_flags_match", text)
        self.assertIn("_v1_pose_flags", text)
        self.assertIn("v2_vs_v1_8_prepared_ratio", text)

    def test_runner_has_pod_progress_and_claim_boundaries(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("[goal1928] start robot_collision_screening", text)
        self.assertIn("[goal1928] timing", text)
        self.assertIn("--pose-count", text)
        self.assertIn("--obstacle-count", text)
        self.assertIn("--partners", text)
        self.assertIn('"v2_0_release_authorized": False', text)
        self.assertIn('"whole_app_speedup_claim_authorized": False', text)
        self.assertIn('"broad_rt_core_speedup_claim_authorized": False', text)

    def test_report_keeps_scope_narrow(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Status: harness-ready-pod-needed", text)
        self.assertIn("robot_collision_screening", text)
        self.assertIn("v1.8 prepared OptiX pose flags", text)
        self.assertIn("v2 prepared OptiX partner columns", text)
        self.assertIn("Exact flag-vector parity", text)
        self.assertIn("does not authorize v2.0 release", text)
        self.assertIn("does not claim broad RT-core speedup", text)


if __name__ == "__main__":
    unittest.main()
