import inspect
import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4197_predicate_boundary_lowest_root_two_pass_policy_2026-06-09.md"
OPTIX_CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
PARTNER_ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"


class Goal4197PredicateBoundaryLowestRootTwoPassPolicyTest(unittest.TestCase):
    def test_front_door_exposes_explicit_numba_two_pass_boundary_policy(self) -> None:
        plan = rt.plan_v2_8_fixed_radius_graph_component_continuation(
            point_count=16,
            radius=0.25,
            component_threshold=4,
            backend="optix",
            partner="numba",
            strategy="grouped_stream",
            boundary_assignment_policy="lowest_component_root_two_pass",
        )

        self.assertEqual(plan["status"], "accepted_preview")
        self.assertEqual(plan["user_selected_partner"], "numba")
        self.assertEqual(plan["boundary_assignment_policy"], "lowest_component_root_two_pass")
        self.assertFalse(plan["automatic_partner_selection_allowed"])
        self.assertFalse(plan["app_specific_engine_logic_allowed"])
        self.assertFalse(plan["public_speedup_claim_authorized"])
        self.assertFalse(plan["true_zero_copy_claim_authorized"])

    def test_two_pass_policy_is_not_silently_available_for_cupy(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires partner='numba'"):
            rt.plan_v2_8_fixed_radius_graph_component_continuation(
                point_count=16,
                radius=0.25,
                component_threshold=4,
                backend="optix",
                partner="cupy",
                strategy="grouped_stream",
                boundary_assignment_policy="lowest_component_root_two_pass",
            )

    def test_describe_and_signatures_record_policy_surface(self) -> None:
        description = rt.describe_v2_8_fixed_radius_graph_component_front_door()
        self.assertIn(
            "lowest_component_root_two_pass",
            description["supported_boundary_assignment_policies"],
        )
        self.assertIn(
            "boundary_assignment_policy",
            inspect.signature(rt.prepare_v2_8_fixed_radius_graph_component_continuation_3d).parameters,
        )
        self.assertIn(
            "boundary_assignment_policy",
            inspect.signature(rt.prepare_optix_numba_radius_graph_grouped_stream_continuation_3d).parameters,
        )

    def test_native_fallback_records_component_roots_not_raw_candidate_ids(self) -> None:
        optix_core = OPTIX_CORE.read_text(encoding="utf-8")
        adapters = PARTNER_ADAPTERS.read_text(encoding="utf-8")

        self.assertIn("target_root = find_grouped_union_root_readonly", optix_core)
        self.assertIn("atomicMin(params.fallback_candidate_out + source, target_root)", optix_core)
        self.assertIn("lowest_component_root_after_two_prepared_rt_passes", adapters)
        self.assertIn("boundary_assignment_pass_count", adapters)

    def test_report_records_preview_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal4197", report)
        self.assertIn("lowest_component_root_two_pass", report)
        self.assertIn("explicit user-selected policy", report)
        self.assertIn("not the default", report)
        self.assertIn("does not authorize release", report)


if __name__ == "__main__":
    unittest.main()
