import unittest

import rtdsl as rt


class Goal1399CollectKBoundedResolutionTest(unittest.TestCase):
    def test_resolution_is_defined_but_not_promoted(self):
        resolution = rt.validate_v1_5_collect_k_bounded_resolution()

        self.assertEqual(resolution["primitive"], "COLLECT_K_BOUNDED")
        self.assertEqual(resolution["status"], "defined_pending_evidence")
        self.assertEqual(resolution["status"], rt.V1_5_COLLECT_K_BOUNDED_RESOLUTION_STATUS)
        self.assertIn("promote_to_standalone", resolution["resolution_strategy"])
        self.assertIn("exclude_row_returning_apps", resolution["fallback_strategy"])
        self.assertFalse(resolution["stable_promotion_authorized"])
        self.assertFalse(resolution["public_wording_allowed"])
        self.assertFalse(resolution["release_tag_action_authorized"])

    def test_resolution_preserves_fail_closed_semantics(self):
        resolution = rt.validate_v1_5_collect_k_bounded_resolution()

        self.assertEqual(resolution["capacity_parameter"], "k")
        self.assertEqual(resolution["capacity_unit"], "candidate_pair_rows")
        self.assertEqual(
            resolution["ordering_policy"],
            "stable_by_left_id_then_right_id_after_candidate_discovery",
        )
        self.assertEqual(resolution["overflow_policy"], "no_silent_truncation")
        self.assertEqual(resolution["failure_mode"], "fail_closed_overflow")
        self.assertFalse(resolution["truncation_allowed"])
        self.assertTrue(resolution["complete_candidate_coverage_required"])
        self.assertFalse(resolution["score_reduction_allowed_on_overflow"])

    def test_resolution_gates_are_explicit(self):
        resolution = rt.validate_v1_5_collect_k_bounded_resolution()

        self.assertEqual(resolution["promotion_gates"], rt.V1_5_COLLECT_K_BOUNDED_PROMOTION_GATES)
        self.assertEqual(
            resolution["passed_gates"],
            (
                "published_capacity_ordering_overflow_contract",
                "python_fail_closed_reference_tests",
                "score_reduction_guarded_by_complete_collection",
            ),
        )
        self.assertIn("embree_native_fail_closed_collection", resolution["failed_gates"])
        self.assertIn("optix_native_fail_closed_collection", resolution["failed_gates"])
        self.assertIn("same_contract_app_benchmark_suite", resolution["failed_gates"])
        self.assertIn("external_review_before_public_promotion", resolution["failed_gates"])

    def test_standalone_gate_embeds_resolution_plan_without_passing_release_gate(self):
        gate = rt.validate_v1_5_standalone_release_gate()

        self.assertEqual(gate["collect_k_bounded_resolution_plan_status"], "defined_pending_evidence")
        self.assertIn("promote_to_standalone", gate["collect_k_bounded_resolution_strategy"])
        self.assertIn("exclude_row_returning_apps", gate["collect_k_bounded_resolution_fallback"])
        self.assertIn("collect_k_bounded_resolution", gate["failed_gates"])
        self.assertIn("app_migration_classification", gate["passed_gates"])
        self.assertFalse(gate["gate_results"]["collect_k_bounded_resolution"])
        self.assertFalse(gate["release_tag_action_authorized"])


if __name__ == "__main__":
    unittest.main()
