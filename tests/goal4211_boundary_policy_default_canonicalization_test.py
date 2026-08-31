import inspect
import unittest

import rtdsl as rt
from rtdsl.partner_adapters import PreparedOptixNumbaRadiusGraphGroupedStreamContinuation3D
from rtdsl.partner_adapters import prepare_optix_numba_radius_graph_grouped_stream_continuation_3d


class Goal4211BoundaryPolicyDefaultCanonicalizationTest(unittest.TestCase):
    def test_front_door_plan_default_is_canonical_policy(self) -> None:
        plan = rt.plan_v2_8_fixed_radius_graph_component_continuation(
            point_count=16,
            radius=0.25,
            component_threshold=4,
            backend="optix",
            partner="numba",
            strategy="grouped_stream",
        )
        self.assertEqual(plan["boundary_assignment_policy"], "single_pass_candidate_root_rebased")
        self.assertEqual(plan["boundary_assignment_canonical_policy"], "single_pass_candidate_root_rebased")

    def test_prepare_and_adapter_defaults_are_canonical_policy(self) -> None:
        front_signature = inspect.signature(rt.prepare_v2_8_fixed_radius_graph_component_continuation_3d)
        lower_signature = inspect.signature(prepare_optix_numba_radius_graph_grouped_stream_continuation_3d)
        adapter_signature = inspect.signature(PreparedOptixNumbaRadiusGraphGroupedStreamContinuation3D)

        self.assertEqual(
            front_signature.parameters["boundary_assignment_policy"].default,
            "single_pass_candidate_root_rebased",
        )
        self.assertEqual(
            lower_signature.parameters["boundary_assignment_policy"].default,
            "single_pass_candidate_root_rebased",
        )
        self.assertEqual(
            adapter_signature.parameters["boundary_assignment_policy"].default,
            "single_pass_candidate_root_rebased",
        )

    def test_legacy_alias_is_still_accepted(self) -> None:
        plan = rt.plan_v2_8_fixed_radius_graph_component_continuation(
            point_count=16,
            radius=0.25,
            component_threshold=4,
            backend="optix",
            partner="numba",
            strategy="grouped_stream",
            boundary_assignment_policy="lowest_candidate_then_root",
        )
        self.assertEqual(plan["status"], "accepted_preview")
        self.assertEqual(plan["boundary_assignment_policy"], "lowest_candidate_then_root")
        self.assertEqual(plan["boundary_assignment_canonical_policy"], "single_pass_candidate_root_rebased")


if __name__ == "__main__":
    unittest.main()
