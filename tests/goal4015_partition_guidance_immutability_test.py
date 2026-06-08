from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4015_partition_guidance_immutability_2026-06-08.md"


class Goal4015PartitionGuidanceImmutabilityTest(unittest.TestCase):
    def test_exported_guidance_mapping_is_read_only(self) -> None:
        with self.assertRaises(TypeError):
            rt.V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_PARTITION_GUIDANCE[
                "dense_cell_pair_matrix_allowed"
            ] = True

    def test_describe_returns_copy_not_source_guidance(self) -> None:
        description = rt.describe_v2_8_fixed_radius_graph_component_front_door()
        guidance = description["candidate_strategy_partition_guidance"]["partition_convergence_hybrid"]
        guidance["dense_cell_pair_matrix_allowed"] = True

        fresh = rt.describe_v2_8_fixed_radius_graph_component_front_door()
        fresh_guidance = fresh["candidate_strategy_partition_guidance"]["partition_convergence_hybrid"]
        self.assertFalse(fresh_guidance["dense_cell_pair_matrix_allowed"])
        self.assertFalse(rt.V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_PARTITION_GUIDANCE["dense_cell_pair_matrix_allowed"])

    def test_plan_returns_copy_not_source_guidance(self) -> None:
        plan = rt.plan_v2_8_fixed_radius_graph_component_continuation(
            point_count=65536,
            radius=0.055,
            component_threshold=12,
            partner="cupy",
            strategy="partition_convergence_hybrid",
        )
        guidance = plan["candidate_strategy_partition_guidance"]
        guidance["dense_cell_pair_matrix_allowed"] = True

        fresh = rt.plan_v2_8_fixed_radius_graph_component_continuation(
            point_count=65536,
            radius=0.055,
            component_threshold=12,
            partner="cupy",
            strategy="partition_convergence_hybrid",
        )
        self.assertFalse(fresh["candidate_strategy_partition_guidance"]["dense_cell_pair_matrix_allowed"])

    def test_source_and_report_record_mutability_boundary(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "MappingProxyType",
            "_hybrid_partition_guidance_metadata",
            "read-only mapping",
            "fresh plain dict copies",
            "does not change the runtime route",
        ):
            self.assertIn(fragment, source + "\n" + report)


if __name__ == "__main__":
    unittest.main()
