from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.v2_10_amd_hiprt_benchmark_parity import (
    summarize_v2_10_amd_hiprt_benchmark_parity,
    validate_v2_10_amd_hiprt_benchmark_parity,
    v2_10_amd_hiprt_benchmark_parity,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3756_robot_collision_amd_parity_contract_correction_2026-06-07.md"


class Goal3756RobotCollisionAmdParityContractCorrectionTest(unittest.TestCase):
    def test_robot_collision_amd_row_matches_actual_2d_hiprt_app_route(self) -> None:
        row = next(row for row in v2_10_amd_hiprt_benchmark_parity() if row["app"] == "robot_collision")
        self.assertEqual(row["required_engine_features"], ("ray_triangle_any_hit_2d", "visibility_rows"))
        self.assertNotIn("ray_triangle_any_hit_3d", row["required_engine_features"])
        self.assertEqual(row["missing_generic_contracts"], ())
        self.assertEqual(row["parity_stage"], "ready_for_amd_functional_pod")
        self.assertIn("row any-hit functional parity", row["first_amd_goal"])
        self.assertIn("Ray2D/Triangle2D row route", row["rationale"])
        self.assertIn("Prepared pose-flag summaries remain an OptiX-only contract", row["rationale"])

    def test_robot_collision_app_surface_exposes_hiprt_but_prepared_summary_stays_optix_only(self) -> None:
        support = rt.app_engine_support("robot_collision_screening", "hiprt")
        self.assertEqual(support.status, "direct_cli_native")
        self.assertIn("ready for AMD functional validation", support.note)

        from examples.v2_0.apps.robotics import rtdl_robot_collision_screening_app as app

        with self.assertRaisesRegex(ValueError, "prepared OptiX summary modes require backend='optix'"):
            app.run_app("hiprt", optix_summary_mode="prepared_pose_flags")

    def test_summary_counts_and_claim_boundary_stay_unchanged(self) -> None:
        validation = validate_v2_10_amd_hiprt_benchmark_parity()
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())
        summary = summarize_v2_10_amd_hiprt_benchmark_parity()
        self.assertEqual(summary["stage_counts"]["ready_for_amd_functional_pod"], 1)
        self.assertEqual(summary["ready_for_amd_functional_pod_apps"], ("robot_collision",))
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["amd_perf_claim_authorized"])

    def test_report_documents_the_correction(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("ray_triangle_any_hit_2d", text)
        self.assertIn("not the prepared OptiX pose-flag summary", text)
        self.assertIn("no AMD performance evidence", text)


if __name__ == "__main__":
    unittest.main()
