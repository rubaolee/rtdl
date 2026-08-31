from __future__ import annotations

import pathlib
import unittest

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
FRONT_DOOR = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4005_partition_convergence_candidate_front_door_contract_2026-06-08.md"


class Goal4005PartitionConvergenceCandidateFrontDoorContractTest(unittest.TestCase):
    def test_candidate_strategy_is_visible_but_not_supported_as_runtime(self) -> None:
        description = rt.describe_v2_8_fixed_radius_graph_component_front_door()
        self.assertEqual(description["supported_strategies"], ("grouped_stream",))
        self.assertIn("partition_convergence_hybrid", description["candidate_strategies"])
        self.assertIn("direct_side_effect_default", description["rejected_default_strategies"])
        self.assertIn("microcell_graph", description["rejected_default_strategies"])

    def test_candidate_plan_fails_closed_without_native_implementation(self) -> None:
        plan = rt.plan_v2_8_fixed_radius_graph_component_continuation(
            point_count=65536,
            radius=0.055,
            component_threshold=12,
            backend="optix",
            partner="cupy",
            strategy="partition_convergence_hybrid",
        )
        self.assertEqual(plan["status"], "candidate_requires_native_implementation")
        self.assertFalse(plan["runtime_executable"])
        self.assertFalse(plan["native_abi_added"])
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
        self.assertIn("Goal3999", plan["candidate_strategy_evidence_goals"])
        self.assertIn("actual_benchmark_radius_pod_evidence", plan["candidate_strategy_requirements"])

    def test_prepare_rejects_candidate_strategy_until_runtime_exists(self) -> None:
        with self.assertRaisesRegex(ValueError, "candidate_requires_native_implementation"):
            rt.prepare_v2_8_fixed_radius_graph_component_continuation_3d(
                (rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),),
                radius=0.055,
                component_threshold=12,
                strategy="partition_convergence_hybrid",
            )

    def test_report_and_source_record_no_default_promotion(self) -> None:
        source = FRONT_DOOR.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "partition_convergence_hybrid",
            "candidate_requires_native_implementation",
            "direct_side_effect_default",
            "microcell_graph",
        ]:
            self.assertIn(fragment, source)
            self.assertIn(fragment, report)
        self.assertIn("does not add a native ABI", report)
        self.assertIn("authorize hidden dispatch", report)


if __name__ == "__main__":
    unittest.main()
