from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4044_partition_candidate_runtime_status_metadata_2026-06-08.md"


class Goal4044PartitionCandidateRuntimeStatusMetadataTest(unittest.TestCase):
    def test_description_exposes_preview_status_without_default_promotion(self) -> None:
        description = rt.describe_v2_8_fixed_radius_graph_component_front_door()
        status = description["candidate_strategy_runtime_status"]["partition_convergence_hybrid"]

        self.assertEqual(status["planner_status"], "candidate_requires_native_implementation")
        self.assertTrue(status["executable_preview_available"])
        self.assertTrue(status["prepared_front_door_runtime_executable"])
        self.assertEqual(status["prepared_front_door_runtime_status"], "explicit_cupy_preview_not_promoted")
        self.assertFalse(status["default_route_promoted"])
        self.assertFalse(status["partition_convergence_hybrid_promoted"])
        self.assertEqual(status["latest_preview_evidence_goals"], ("Goal4040", "Goal4041", "Goal4062"))
        self.assertIn("Goal4041_mixed_timing_not_universal_speed_win", status["promotion_blockers"])
        self.assertIn("host_compact_label_materialization_breaks_resident_output", status["promotion_blockers"])
        self.assertIn("promoted native partition handle", status["next_engineering_target"])

    def test_candidate_plan_carries_same_runtime_status(self) -> None:
        plan = rt.plan_v2_8_fixed_radius_graph_component_continuation(
            point_count=8192,
            radius=0.055,
            component_threshold=12,
            backend="optix",
            partner="cupy",
            strategy="partition_convergence_hybrid",
        )
        status = plan["candidate_strategy_runtime_status"]

        self.assertEqual(plan["status"], "candidate_requires_native_implementation")
        self.assertFalse(plan["runtime_executable"])
        self.assertTrue(status["executable_preview_available"])
        self.assertFalse(status["default_route_promoted"])
        self.assertIn("Goal4041", plan["candidate_strategy_evidence_goals"])
        self.assertEqual(status["promotion_blockers"], rt.V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_PROMOTION_BLOCKERS)
        self.assertFalse(plan["automatic_partner_selection_allowed"])
        self.assertFalse(plan["public_speedup_claim_authorized"])
        self.assertFalse(plan["true_zero_copy_claim_authorized"])

    def test_report_records_runtime_status_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "executable_preview_available: true",
            "prepared_front_door_runtime_executable: true",
            "prepared_front_door_runtime_status: explicit_cupy_preview_not_promoted",
            "default_route_promoted: false",
            "Goal4041_mixed_timing_not_universal_speed_win",
            "host_compact_label_materialization_breaks_resident_output",
            "promoted native partition handle",
            "does not promote",
            "automatic partner selection",
            "true-zero-copy",
        ):
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
