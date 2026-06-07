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
        self.assertEqual(
            row["required_engine_features"],
            ("ray_triangle_any_hit_2d", "visibility_rows", "prepared_grouped_visibility_flags_2d"),
        )
        self.assertNotIn("ray_triangle_any_hit_3d", row["required_engine_features"])
        self.assertEqual(row["missing_generic_contracts"], ())
        self.assertEqual(row["parity_stage"], "ready_for_amd_functional_pod")
        self.assertIn("prepared grouped visibility flags", row["first_amd_goal"])
        self.assertIn("Ray2D/Triangle2D row route", row["rationale"])
        self.assertIn("Goal3763", row["rationale"])
        self.assertIn("Goal3765", row["rationale"])
        self.assertIn("not AMD hardware evidence", row["rationale"])
        self.assertIn("generic HIPRT prepared grouped visibility-flag summary", row["rationale"])

    def test_robot_collision_app_surface_exposes_hiprt_prepared_grouped_summary(self) -> None:
        support = rt.app_engine_support("robot_collision_screening", "hiprt")
        self.assertEqual(support.status, "direct_cli_native")
        self.assertIn("ready for AMD functional validation", support.note)

        feature = rt.engine_feature_support("prepared_grouped_visibility_flags_2d", "hiprt")
        self.assertEqual(feature.status, "native")
        self.assertIn("Goal3765", feature.note)

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
        self.assertIn("prepared grouped visibility flags", text)
        self.assertIn("no AMD performance evidence", text)


if __name__ == "__main__":
    unittest.main()
