import unittest

import rtdsl as rt


class Goal4209BoundaryPolicyCanonicalAliasCleanupTest(unittest.TestCase):
    def test_front_door_exposes_canonical_policy_and_alias(self) -> None:
        description = rt.describe_v2_8_fixed_radius_graph_component_front_door()
        self.assertIn(
            "single_pass_candidate_root_rebased",
            description["supported_boundary_assignment_policies"],
        )
        self.assertEqual(
            description["boundary_assignment_policy_aliases"]["lowest_candidate_then_root"],
            "single_pass_candidate_root_rebased",
        )
        self.assertEqual(
            description["recommended_boundary_assignment_policy"],
            "single_pass_candidate_root_rebased",
        )

    def test_plan_metadata_reports_canonical_policy_for_legacy_alias(self) -> None:
        plan = rt.plan_v2_8_fixed_radius_graph_component_continuation(
            point_count=16,
            radius=0.25,
            component_threshold=4,
            backend="optix",
            partner="numba",
            strategy="grouped_stream",
            boundary_assignment_policy="lowest_candidate_then_root",
        )
        self.assertEqual(plan["boundary_assignment_policy"], "lowest_candidate_then_root")
        self.assertEqual(plan["boundary_assignment_canonical_policy"], "single_pass_candidate_root_rebased")

    def test_plan_accepts_canonical_policy_name(self) -> None:
        plan = rt.plan_v2_8_fixed_radius_graph_component_continuation(
            point_count=16,
            radius=0.25,
            component_threshold=4,
            backend="optix",
            partner="numba",
            strategy="grouped_stream",
            boundary_assignment_policy="single_pass_candidate_root_rebased",
        )
        self.assertEqual(plan["status"], "accepted_preview")
        self.assertEqual(plan["boundary_assignment_policy"], "single_pass_candidate_root_rebased")
        self.assertEqual(plan["boundary_assignment_canonical_policy"], "single_pass_candidate_root_rebased")


if __name__ == "__main__":
    unittest.main()
