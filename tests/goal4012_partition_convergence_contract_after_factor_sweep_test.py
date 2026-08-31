from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
FRONT_DOOR = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4012_partition_convergence_contract_after_factor_sweep_2026-06-08.md"


class Goal4012PartitionConvergenceContractAfterFactorSweepTest(unittest.TestCase):
    def test_candidate_contract_includes_goal4011_evidence(self) -> None:
        description = rt.describe_v2_8_fixed_radius_graph_component_front_door()
        goals = description["candidate_strategy_evidence_goals"]["partition_convergence_hybrid"]
        for goal in ("Goal4007", "Goal4009", "Goal4011"):
            self.assertIn(goal, goals)

    def test_candidate_requirements_reject_dense_matrix_and_hidden_root_mutation(self) -> None:
        requirements = rt.V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_REQUIREMENTS
        for requirement in (
            "compressed_occupied_partition_key_structure",
            "bounded_near_partition_enumeration",
            "no_dense_cell_pair_matrix",
            "readonly_root_find_default_preserved",
            "explicit_root_convergence_changes_only",
            "root_read_telemetry_reduction_required",
            "radius_x_0_125_partition_factor_evidence",
        ):
            self.assertIn(requirement, requirements)

    def test_partition_guidance_is_fail_closed_and_device_resident(self) -> None:
        guidance = rt.V2_8_FIXED_RADIUS_GRAPH_COMPONENT_HYBRID_PARTITION_GUIDANCE
        self.assertEqual(guidance["recommended_tested_cell_factor"], "radius_x_0.125")
        self.assertFalse(guidance["dense_cell_pair_matrix_allowed"])
        self.assertEqual(
            guidance["required_partition_pair_enumeration"],
            "compressed_occupied_partition_keys_with_bounded_near_offsets",
        )
        for column in (
            "point_partition_ids",
            "occupied_partition_keys",
            "partition_offsets",
            "partition_counts",
            "partition_aabbs",
        ):
            self.assertIn(column, guidance["required_device_resident_columns"])
        for shortcut in (
            "dense_all_cell_pair_matrix",
            "hidden_root_path_halving_inside_readonly_find",
            "app_specific_dbscan_or_clustering_native_abi",
        ):
            self.assertIn(shortcut, guidance["rejected_shortcuts"])

    def test_candidate_plan_remains_non_executable_and_non_authorizing(self) -> None:
        plan = rt.plan_v2_8_fixed_radius_graph_component_continuation(
            point_count=65536,
            radius=0.055,
            component_threshold=12,
            backend="optix",
            partner="numba",
            strategy="partition_convergence_hybrid",
        )
        self.assertEqual(plan["status"], "candidate_requires_native_implementation")
        self.assertFalse(plan["runtime_executable"])
        self.assertFalse(plan["native_abi_added"])
        self.assertIn("Goal4011", plan["candidate_strategy_evidence_goals"])
        self.assertFalse(plan["candidate_strategy_partition_guidance"]["dense_cell_pair_matrix_allowed"])
        for flag in (
            "fallback_selected",
            "hidden_dispatch_allowed",
            "automatic_partner_selection_allowed",
            "app_specific_engine_logic_allowed",
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
        ):
            self.assertFalse(plan[flag])

    def test_report_and_source_record_goal4012_boundary(self) -> None:
        source = FRONT_DOOR.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "Goal4011",
            "radius_x_0.125",
            "compressed_occupied_partition_key_structure",
            "no_dense_cell_pair_matrix",
            "hidden_root_path_halving_inside_readonly_find",
            "does not add a native ABI",
            "does not authorize public speedup wording",
        ):
            self.assertIn(fragment, source + "\n" + report)


if __name__ == "__main__":
    unittest.main()
