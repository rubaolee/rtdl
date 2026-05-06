import unittest

import rtdsl as rt


class V15InternalReadinessGateTest(unittest.TestCase):
    def test_gate_validates_expected_contract_counts(self):
        gate = rt.validate_v1_5_internal_readiness_gate()

        self.assertEqual(gate["status"], "internal_v1_5_contract_gate_passing_non_public")
        self.assertEqual(
            gate["contract_surface_counts"],
            {
                "inventory_rows": 14,
                "grouped_contracts": 5,
                "db_contracts": 3,
                "float_sum_contracts": 2,
                "bounded_collection_contracts": 1,
            },
        )
        for count_field, count in gate["contract_surface_counts"].items():
            with self.subTest(count_field=count_field):
                self.assertEqual(gate[count_field], count)
        self.assertEqual(gate["total_contract_surfaces"], 25)
        self.assertEqual(gate["total_contract_surfaces"], sum(gate["contract_surface_counts"].values()))

    def test_gate_keeps_public_release_and_speedup_blocked(self):
        gate = rt.validate_v1_5_internal_readiness_gate()

        self.assertFalse(gate["public_release_authorized"])
        self.assertFalse(gate["public_speedup_wording_authorized"])
        self.assertFalse(gate["release_tag_action_authorized"])
        self.assertEqual(gate["requires_external_consensus_for_public_claims"], "3-AI")

        boundary = gate["claim_boundary"]
        self.assertIn("not public v1.5 release wording", boundary)
        self.assertIn("not public speedup wording", boundary)
        self.assertIn("v1.0 tag remains unchanged", boundary)

    def test_gate_represents_all_hardened_validators(self):
        gate = rt.validate_v1_5_internal_readiness_gate()

        self.assertEqual(
            set(gate["validators"]),
            {
                "validate_v1_5_generic_migration_inventory",
                "validate_v1_5_grouped_reduction_contracts",
                "validate_v1_5_db_compact_summary_contracts",
                "validate_v1_5_float_sum_reduction_contracts",
                "validate_v1_5_collect_k_bounded_contracts",
            },
        )
        self.assertIn("COLLECT_K_BOUNDED", gate["experimental_primitives"])

    def test_gate_preserves_stable_summary_primitive_target(self):
        gate = rt.validate_v1_5_internal_readiness_gate()

        self.assertEqual(
            gate["stable_summary_primitives"],
            (
                "COUNT_HITS",
                "REDUCE_FLOAT(MIN)",
                "REDUCE_FLOAT(MAX)",
                "REDUCE_FLOAT(SUM)",
                "REDUCE_INT(COUNT)",
                "REDUCE_INT(SUM)",
            ),
        )
        self.assertEqual(gate["stable_summary_primitives"], rt.V1_5_GENERIC_SCALAR_REDUCTION_PRIMITIVES)
        self.assertNotIn("COLLECT_K_BOUNDED", gate["stable_summary_primitives"])

    def test_gate_preserves_backend_scope_boundary(self):
        gate = rt.validate_v1_5_internal_readiness_gate()

        self.assertEqual(gate["active_backend_scope"], ("embree", "optix"))
        self.assertEqual(gate["frozen_before_v2_1_backends"], ("vulkan", "hiprt", "apple_rt"))
        self.assertFalse(set(gate["active_backend_scope"]) & set(gate["frozen_before_v2_1_backends"]))

    def test_gate_requires_inventory_rows_to_be_pod_verified(self):
        gate = rt.validate_v1_5_internal_readiness_gate()

        self.assertEqual(gate["allowed_inventory_statuses"], ("pod_verified_generic",))
        self.assertEqual(gate["inventory_status_counts"], {"pod_verified_generic": 14})
        self.assertEqual(sum(gate["inventory_status_counts"].values()), gate["inventory_rows"])

    def test_gate_keeps_bounded_collection_experimental(self):
        gate = rt.validate_v1_5_internal_readiness_gate()

        self.assertEqual(
            gate["allowed_experimental_contract_statuses"],
            ("experimental_diagnostic_only",),
        )
        self.assertEqual(
            gate["experimental_contract_status_counts"],
            {"experimental_diagnostic_only": 1},
        )
        self.assertEqual(
            sum(gate["experimental_contract_status_counts"].values()),
            gate["bounded_collection_contracts"],
        )

    def test_gate_exposes_remaining_blockers_and_consensus_requirement(self):
        gate = rt.validate_v1_5_internal_readiness_gate()

        self.assertGreater(len(gate["blockers"]), 0)
        self.assertEqual(
            gate["required_blocker_phrases"],
            (
                "app-level continuations remain outside v1.5 generic subpath scope",
                "whole-app speedup wording remains blocked",
                "public NVIDIA wording remains blocked",
                "3-AI consensus",
            ),
        )
        for phrase in gate["required_blocker_phrases"]:
            with self.subTest(phrase=phrase):
                self.assertTrue(any(phrase in blocker for blocker in gate["blockers"]))

    def test_decision_allows_only_internal_next_actions(self):
        decision = rt.validate_v1_5_internal_readiness_decision()

        self.assertEqual(decision["decision"], "continue_internal_non_public_v1_5_hardening")
        self.assertEqual(decision["total_contract_surfaces"], 25)
        self.assertEqual(
            decision["allowed_next_actions"],
            (
                "continue_internal_contract_hardening",
                "collect_pod_validation_from_git",
                "request_external_review_before_public_claims",
            ),
        )
        self.assertEqual(decision["allowed_next_actions"], rt.V1_5_INTERNAL_READINESS_ALLOWED_NEXT_ACTIONS)
        for blocked_action in (
            "public_v1_5_release_wording",
            "public_speedup_wording",
            "release_tag_action",
            "stable_collect_k_bounded_promotion",
            "new_pre_v2_1_backend_implementation",
        ):
            with self.subTest(blocked_action=blocked_action):
                self.assertIn(blocked_action, decision["blocked_next_actions"])
        self.assertEqual(decision["blocked_next_actions"], rt.V1_5_INTERNAL_READINESS_BLOCKED_NEXT_ACTIONS)
        self.assertEqual(
            decision["public_claim_preconditions"],
            (
                "exact_subpath_evidence",
                "fresh_git_pod_validation",
                "external_3_ai_consensus",
                "public_wording_review",
            ),
        )
        self.assertEqual(
            decision["public_claim_preconditions"],
            rt.V1_5_INTERNAL_READINESS_PUBLIC_CLAIM_PRECONDITIONS,
        )
        self.assertFalse(decision["public_claims_ready"])
        self.assertEqual(decision["required_external_review_partners"], ("claude", "gemini"))
        self.assertEqual(
            decision["required_external_review_partners"],
            rt.V1_5_INTERNAL_READINESS_REQUIRED_EXTERNAL_REVIEW_PARTNERS,
        )
        self.assertEqual(decision["accepted_external_review_partners"], ("claude",))
        self.assertEqual(
            decision["accepted_external_review_partners"],
            rt.V1_5_INTERNAL_READINESS_ACCEPTED_EXTERNAL_REVIEW_PARTNERS,
        )
        self.assertEqual(decision["missing_external_review_partners"], ("gemini",))
        self.assertFalse(decision["external_3_ai_consensus_ready"])
        self.assertEqual(decision["source_usage_mode"], "source_tree_pythonpath")
        self.assertEqual(decision["source_usage_mode"], rt.V1_5_INTERNAL_READINESS_SOURCE_USAGE_MODE)
        self.assertEqual(decision["source_usage_command"], "PYTHONPATH=src:. python ...")
        self.assertEqual(
            decision["source_usage_command"],
            rt.V1_5_INTERNAL_READINESS_SOURCE_USAGE_COMMAND,
        )
        self.assertFalse(decision["editable_install_claim_authorized"])
        self.assertFalse(decision["package_release_artifact_authorized"])
        self.assertEqual(decision["active_backend_scope"], ("embree", "optix"))
        self.assertEqual(decision["frozen_before_v2_1_backends"], ("vulkan", "hiprt", "apple_rt"))
        self.assertFalse(set(decision["active_backend_scope"]) & set(decision["frozen_before_v2_1_backends"]))
        self.assertFalse(decision["new_backend_implementation_authorized"])
        self.assertFalse(decision["pre_v2_1_frozen_backend_work_authorized"])
        self.assertFalse(decision["public_release_authorized"])
        self.assertFalse(decision["public_speedup_wording_authorized"])
        self.assertFalse(decision["release_tag_action_authorized"])


if __name__ == "__main__":
    unittest.main()
