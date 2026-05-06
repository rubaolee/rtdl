import unittest

import rtdsl as rt


class V15StandaloneReleaseGateTest(unittest.TestCase):
    def test_gate_blocks_release_from_primitive_only_readiness(self):
        gate = rt.validate_v1_5_standalone_release_gate()

        self.assertEqual(gate["status"], "blocked_pending_standalone_language_completion")
        self.assertEqual(gate["scope_kind"], "standalone_embree_optix_language_runtime")
        self.assertFalse(gate["primitive_packet_sufficient_for_release"])
        self.assertTrue(gate["primitive_packet_is_prerequisite_only"])
        self.assertFalse(gate["public_release_authorized"])
        self.assertFalse(gate["release_tag_action_authorized"])
        self.assertFalse(gate["new_public_release_tag_authorized"])
        self.assertFalse(gate["current_public_release_tag_move_authorized"])

        boundary = gate["claim_boundary"]
        self.assertIn("standalone v1.5 release is blocked", boundary)
        self.assertIn("do not tag v1.5 from primitive-only readiness", boundary)

    def test_gate_requires_expanded_standalone_completion_work(self):
        gate = rt.validate_v1_5_standalone_release_gate()

        self.assertEqual(gate["required_gates"], rt.V1_5_STANDALONE_RELEASE_REQUIRED_GATES)
        self.assertEqual(
            gate["passed_gates"],
            (
                "primitive_packet_prerequisite",
                "roadmap_consensus",
                "collect_k_bounded_resolution",
                "app_migration_classification",
                "same_contract_per_app_correctness",
                "same_contract_per_app_benchmarks",
                "test_backed_support_maturity_matrix",
            ),
        )
        self.assertEqual(
            gate["failed_gates"],
            (
                "release_docs_and_public_wording",
            ),
        )
        for failed_gate in gate["failed_gates"]:
            with self.subTest(failed_gate=failed_gate):
                self.assertFalse(gate["gate_results"][failed_gate])
        self.assertTrue(gate["gate_results"]["same_contract_per_app_correctness"])
        self.assertTrue(gate["gate_results"]["same_contract_per_app_benchmarks"])
        self.assertTrue(gate["gate_results"]["collect_k_bounded_resolution"])
        self.assertTrue(gate["gate_results"]["test_backed_support_maturity_matrix"])

    def test_gate_resolves_collect_k_bounded_by_excluding_row_returning_apps(self):
        gate = rt.validate_v1_5_standalone_release_gate()

        self.assertEqual(gate["collect_k_bounded_statuses"], ("experimental_diagnostic_only",))
        self.assertEqual(
            gate["collect_k_bounded_resolution"],
            "resolved_by_explicit_row_returning_app_exclusion",
        )
        self.assertTrue(gate["collect_k_bounded_resolution_complete"])
        self.assertEqual(
            gate["collect_k_bounded_excluded_row_returning_apps"],
            ("polygon_set_jaccard", "segment_polygon_anyhit_rows"),
        )
        self.assertNotIn("collect_k_bounded_resolution", gate["failed_gates"])

    def test_gate_preserves_backend_usage_and_partner_track_boundaries(self):
        gate = rt.validate_v1_5_standalone_release_gate()

        self.assertEqual(gate["active_backend_scope"], ("embree", "optix"))
        self.assertEqual(gate["frozen_before_v2_1_backends"], ("vulkan", "hiprt", "apple_rt"))
        self.assertEqual(gate["source_usage_command"], "PYTHONPATH=src:. python ...")
        self.assertEqual(
            gate["collect_k_bounded_followup_track"],
            (
                ("v1.5.1", "collect_k_bounded_fail_closed_semantics"),
                ("v1.5.1", "native_embree_optix_collection_parity"),
                ("v1.5.1", "same_contract_collection_benchmarks"),
                ("v1.5.1", "external_review_before_collect_k_promotion"),
            ),
        )
        self.assertEqual(gate["collect_k_bounded_followup_track"], rt.V1_5_1_COLLECT_K_BOUNDED_TRACK)
        self.assertEqual(
            gate["partner_track"],
            (
                ("v1.6", "partner_api_design"),
                ("v1.7", "first_partner_prototype"),
                ("v1.8", "partner_conformance_suite"),
                ("v1.9", "partner_ecosystem_hardening"),
                ("v2.0", "public_partner_ready_rtdl"),
            ),
        )
        self.assertEqual(gate["partner_track"], rt.V1_5_STANDALONE_PARTNER_TRACK)

    def test_gate_next_actions_are_standalone_completion_tasks(self):
        gate = rt.validate_v1_5_standalone_release_gate()

        self.assertEqual(
            gate["allowed_next_actions"],
            (
                "refresh_release_docs_and_public_wording",
            ),
        )
        self.assertEqual(
            gate["allowed_next_actions"],
            rt.V1_5_STANDALONE_RELEASE_ALLOWED_NEXT_ACTIONS,
        )

    def test_gate_embeds_app_classification_summary(self):
        gate = rt.validate_v1_5_standalone_release_gate()

        self.assertTrue(gate["gate_results"]["app_migration_classification"])
        self.assertEqual(gate["standalone_included_app_count"], 14)
        self.assertEqual(gate["standalone_excluded_app_count"], 4)
        for classification in rt.V1_5_STANDALONE_APP_CLASSIFICATIONS:
            with self.subTest(classification=classification):
                self.assertIn(classification, gate["app_classification_counts"])

    def test_gate_embeds_completed_same_contract_correctness_summary(self):
        gate = rt.validate_v1_5_standalone_release_gate()

        self.assertTrue(gate["gate_results"]["same_contract_per_app_correctness"])
        self.assertEqual(gate["same_contract_correctness_covered_app_count"], 14)
        self.assertEqual(gate["same_contract_correctness_pending_app_count"], 0)
        self.assertEqual(gate["same_contract_correctness_excluded_app_count"], 4)
        self.assertEqual(gate["same_contract_correctness_pending_apps"], ())

    def test_gate_embeds_completed_support_maturity_summary(self):
        gate = rt.validate_v1_5_standalone_release_gate()

        self.assertTrue(gate["gate_results"]["test_backed_support_maturity_matrix"])
        self.assertEqual(gate["support_maturity_included_app_count"], 14)
        self.assertEqual(gate["support_maturity_excluded_app_count"], 4)
        self.assertEqual(gate["support_maturity_failed_apps"], ())
        self.assertTrue(gate["support_maturity_test_backed"])

    def test_gate_embeds_completed_benchmark_evidence_summary(self):
        gate = rt.validate_v1_5_standalone_release_gate()

        self.assertTrue(gate["gate_results"]["same_contract_per_app_benchmarks"])
        self.assertEqual(gate["benchmark_evidence_included_app_count"], 14)
        self.assertEqual(gate["benchmark_evidence_excluded_app_count"], 4)
        self.assertEqual(gate["benchmark_evidence_failed_apps"], ())
        self.assertFalse(gate["benchmark_evidence_public_wording_authorized"])


if __name__ == "__main__":
    unittest.main()
