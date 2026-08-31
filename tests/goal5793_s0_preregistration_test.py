from __future__ import annotations

import copy
import json
import unittest

from scripts import goal5793_audit_s0_preregistration as audit
from scripts import goal5793_build_s0_preregistration as builder


def decode_json(data: bytes) -> dict:
    return json.loads(data.decode("utf-8"))


def reseal(document: dict, field: str) -> dict:
    document = copy.deepcopy(document)
    document.pop(field, None)
    document[field] = audit.sha256_bytes(audit.canonical_bytes(document))
    return document


class Goal5793S0PreregistrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        outputs_a = builder.build_documents()
        outputs_b = builder.build_documents()
        if outputs_a != outputs_b:
            raise AssertionError("S0 builder is not deterministic")
        cls.outputs = outputs_a
        cls.source = decode_json(outputs_a[builder.SOURCE_OUT])
        cls.candidates = decode_json(outputs_a[builder.CANDIDATE_OUT])
        cls.protocol = decode_json(outputs_a[builder.PROTOCOL_OUT])
        cls.result = decode_json(outputs_a[builder.RESULT_OUT])
        cls.report = outputs_a[builder.REPORT_OUT].decode("utf-8")
        cls.self_review = outputs_a[builder.SELF_REVIEW_OUT].decode("utf-8")
        audit_outputs_a = audit.build_outputs(outputs_a)
        audit_outputs_b = audit.build_outputs(outputs_a)
        if audit_outputs_a != audit_outputs_b:
            raise AssertionError("S0 independent audit/CFR builder is not deterministic")
        cls.audit_outputs = audit_outputs_a

    def expect_failure(self, expected: str, fn, *args, **kwargs) -> None:
        with self.assertRaises(audit.AuditFailure) as raised:
            fn(*args, **kwargs)
        self.assertEqual(raised.exception.fail_id, expected)

    def test_00_deterministic_baseline_and_full_virtual_chain(self) -> None:
        audit.validate_documents(
            self.source,
            self.candidates,
            self.protocol,
            self.result,
            self.report,
            self.self_review,
            virtual_files=self.outputs,
        )
        self.assertEqual(
            self.source["declared_product_native_source_zero_drift_authority"]["summary"],
            audit.COMPLETE_SUMMARY,
        )
        self.assertEqual(self.candidates["counts"], audit.EXPECTED_COUNTS)
        self.assertEqual(self.candidates["ordered_triplets"], [])
        self.assertEqual(self.protocol["current_literals"]["entropy_draw_count"], 0)
        self.assertEqual(len(self.protocol["deferred_entropy"]["selection_encoding"]["field_order"]), 21)
        self.assertIn(
            "preentropy_science_projection_rows_sha256",
            self.protocol["deferred_entropy"]["selection_encoding"]["field_order"],
        )
        self.assertIn(b"SEND ONLY THIS FILE TO THE REVIEWER", self.audit_outputs[audit.CFR_PATH])

    def test_01_h01_zero_drift_authority_mismatch(self) -> None:
        mutated = copy.deepcopy(self.source)
        mutated["declared_product_native_source_zero_drift_authority"]["rows"] = mutated[
            "declared_product_native_source_zero_drift_authority"
        ]["rows"][:-1]
        mutated = reseal(mutated, "source_authority_sha256")
        self.expect_failure("ZERO_DRIFT_AUTHORITY_MISMATCH", audit.validate_source, mutated, compare_live=False)

    def test_02_h02_explanatory_submanifest_overclaim(self) -> None:
        mutated = copy.deepcopy(self.source)
        mutated["critical_explanatory_submanifest"]["complete_authority"] = True
        mutated = reseal(mutated, "source_authority_sha256")
        self.expect_failure("EXPLANATORY_SUBMANIFEST_OVERCLAIM", audit.validate_source, mutated, compare_live=False)

    def test_03_h03_universe_row_set_mismatch(self) -> None:
        mutated = copy.deepcopy(self.candidates)
        mutated["rows"] = mutated["rows"][:-1]
        mutated = reseal(mutated, "candidate_authority_sha256")
        self.expect_failure("UNIVERSE_ROW_SET_MISMATCH", audit.validate_candidates, mutated)

    def test_04_h04_source_gap_hygiene_failure(self) -> None:
        mutated = copy.deepcopy(self.candidates)
        row = next(row for row in mutated["rows"] if row["candidate_id"] in audit.SOURCE_GAP_IDS)
        row["primary_source_requalification"]["source_gaps"] = []
        mutated = reseal(mutated, "candidate_authority_sha256")
        self.expect_failure("SOURCE_GAP_HYGIENE_FAILURE", audit.validate_candidates, mutated)

    def test_05_h04_source_reachability_overclaim(self) -> None:
        mutated = copy.deepcopy(self.candidates)
        mutated["source_evidence_reachability"]["observed_hashes_are_reviewer_reachable_without_refetch"] = True
        mutated = reseal(mutated, "candidate_authority_sha256")
        self.expect_failure("SOURCE_GAP_HYGIENE_FAILURE", audit.validate_candidates, mutated)

    def test_06_h05_exposure_authority_mismatch(self) -> None:
        mutated = copy.deepcopy(self.candidates)
        mutated["rows"][0]["paper_identity_visible_via_goal5753_catalog"] = False
        mutated = reseal(mutated, "candidate_authority_sha256")
        self.expect_failure("EXPOSURE_AUTHORITY_MISMATCH", audit.validate_candidates, mutated)

    def test_07_h06_forbidden_selection_feature_dependence(self) -> None:
        mutated = copy.deepcopy(self.candidates)
        mutated["rows"][0]["performance_or_ease_used_for_eligibility"] = True
        mutated = reseal(mutated, "candidate_authority_sha256")
        self.expect_failure("FORBIDDEN_SELECTION_FEATURE_DEPENDENCE", audit.validate_candidates, mutated)

    def test_08_h07_role_requalification_mismatch(self) -> None:
        mutated = copy.deepcopy(self.candidates)
        row = next(row for row in mutated["rows"] if row["candidate_id"] in audit.SOURCE_GAP_IDS)
        row["role_a_unconventional_correct_expected_admission"] = "QUALIFIED"
        mutated = reseal(mutated, "candidate_authority_sha256")
        self.expect_failure("ROLE_REQUALIFICATION_MISMATCH", audit.validate_candidates, mutated)

    def test_09_h07_old_catalog_reentry(self) -> None:
        mutated = copy.deepcopy(self.candidates)
        mutated["uniform_policy"]["all_35_rows_permanently_selection_ineligible"] = False
        mutated = reseal(mutated, "candidate_authority_sha256")
        self.expect_failure("ROLE_REQUALIFICATION_MISMATCH", audit.validate_candidates, mutated)

    def test_10_h08_triplet_set_mismatch(self) -> None:
        mutated = copy.deepcopy(self.candidates)
        mutated["ordered_triplets"] = [["a", "b", "c"]]
        mutated["ordered_triplet_rows_sha256"] = audit.sha256_bytes(audit.canonical_bytes(mutated["ordered_triplets"]))
        mutated = reseal(mutated, "candidate_authority_sha256")
        self.expect_failure("TRIPLET_SET_MISMATCH", audit.validate_candidates, mutated)

    def test_11_h09_premature_entropy_or_selection(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["current_literals"]["anchor"] = {"outputValue": "00" * 64}
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("PREMATURE_ENTROPY_OR_SELECTION", audit.validate_protocol, mutated)

    def test_12_h10_stage_predecessor_unsatisfied(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["authorization"]["authorizes_systematic_search"] = True
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("STAGE_PREDECESSOR_UNSATISFIED", audit.validate_protocol, mutated)

    def test_13_h10_authorization_key_deletion(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        del mutated["authorization"]["authorizes_systematic_search"]
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("STAGE_PREDECESSOR_UNSATISFIED", audit.validate_protocol, mutated)

    def test_14_h11_search_before_examiner_freeze(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        states = mutated["state_machine"]
        x1 = states.index("X1_GENERIC_EXAMINER_REGISTRY_ENV_SHARED_NATIVE_IMPLEMENTED_REVIEWED")
        x2 = states.index("X2_HARVESTER_ENTROPY_CLIENT_AND_EXPANSION_PROTOCOL_IMPLEMENTED_OFFLINE_REVIEWED")
        states[x1], states[x2] = states[x2], states[x1]
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("SEARCH_BEFORE_EXAMINER_FREEZE", audit.validate_protocol, mutated)

    def test_15_h11_current_state_forged_to_result(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["current_state"] = "RESULT"
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("SEARCH_BEFORE_EXAMINER_FREEZE", audit.validate_protocol, mutated)

    def test_16_h12_length_preserving_query_mutation(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["x2_systematic_expansion"]["logical_search_terms"] = ["CUDA" for _ in range(11)]
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("EXPANSION_PROTOCOL_DRIFT", audit.validate_protocol, mutated)

    def test_17_h12_date_window_mutation(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["x2_systematic_expansion"]["publication_date_window"]["from"] = "2026-08-22"
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("EXPANSION_PROTOCOL_DRIFT", audit.validate_protocol, mutated)

    def test_18_h12_manual_source_search_enabled(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["x2_systematic_expansion"]["uniform_full_text_resolution"][
            "general_web_search_author_homepage_search_or_manual_extra_attempt_allowed"
        ] = True
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("SOURCE_GAP_HYGIENE_FAILURE", audit.validate_protocol, mutated)

    def test_19_h13_examiner_metadata_dependence(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["x1_generic_examiner_contract"]["decision_code_forbidden_inputs"].remove("role_assignment")
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("EXAMINER_METADATA_DEPENDENCE", audit.validate_protocol, mutated)

    def test_20_h14_registry_derivation_or_core_drift(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["x1_generic_examiner_contract"]["registry_derivation"]["forbidden_postfreeze_changes"] = ["x"] * 7
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("REGISTRY_DERIVATION_OR_CORE_DRIFT", audit.validate_protocol, mutated)

    def test_21_h14_postsearch_taxonomy_amendment(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["x3_preentropy_science_projection"]["normalized_problem_family_rule"][
            "new_split_merge_or_label_after_first_live_call_allowed"
        ] = True
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("ROLE_REQUALIFICATION_MISMATCH", audit.validate_protocol, mutated)

    def test_22_h15_entropy_next_closest_enabled(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["deferred_entropy"]["alternate_or_next_available_target_allowed"] = True
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", audit.validate_protocol, mutated)

    def test_23_h15_exact_timestamp_check_removed(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["deferred_entropy"]["target_rule"]["required_exact_response"][0] = "accept HTTP 200"
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", audit.validate_protocol, mutated)

    def test_24_h15_mapping_changed(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["deferred_entropy"]["selection_encoding"]["hash"] = "SHA-512"
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", audit.validate_protocol, mutated)

    def test_24a_h15_field_order_changed(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        order = mutated["deferred_entropy"]["selection_encoding"]["field_order"]
        order[0], order[1] = order[1], order[0]
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", audit.validate_protocol, mutated)

    def test_24b_h15_rejection_boundary_changed(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["deferred_entropy"]["rejection_boundary_test"]["threshold_hex"] = "f" * 64
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", audit.validate_protocol, mutated)

    def test_25_h15_beacon_verifier_deferred_until_after_search(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["x2_systematic_expansion"][
            "entropy_client_and_verifier_must_be_frozen_reviewed_and_owner_closed_before_first_live_search"
        ] = False
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", audit.validate_protocol, mutated)

    def test_26_h16_post_outcome_rescue(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["postselection_input_and_implementation_freeze"]["replacement_row_or_candidate_allowed"] = True
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("POST_OUTCOME_RESCUE", audit.validate_protocol, mutated)

    def test_27_h17_outcome_dependent_validity(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["postselection_input_and_implementation_freeze"]["result_dependent_validity_allowed"] = True
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("OUTCOME_DEPENDENT_VALIDITY", audit.validate_protocol, mutated)

    def test_28_h18_friction_ledger_mismatch(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["structural_friction_ledger"]["required_for_all_three_rows_including_failures"].remove(
            "private API call count and exact call sites"
        )
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("FRICTION_LEDGER_MISMATCH", audit.validate_protocol, mutated)

    def test_29_h19_usability_overclaim(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["structural_friction_ledger"]["supports_easy_or_better_than_cuda_claim"] = True
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("USABILITY_OVERCLAIM", audit.validate_protocol, mutated)

    def test_30_h20_exposure_claim_overreach(self) -> None:
        mutated = copy.deepcopy(self.candidates)
        mutated["rows"][0]["unseen_claimed"] = True
        mutated = reseal(mutated, "candidate_authority_sha256")
        self.expect_failure("EXPOSURE_CLAIM_OVERREACH", audit.validate_candidates, mutated)

    def test_31_bare_held_out_claim_rejected(self) -> None:
        self.expect_failure(
            "EXPOSURE_CLAIM_OVERREACH",
            audit.validate_claim_text,
            self.report + "\nThis is held-out evidence.",
            self.self_review,
        )

    def test_31a_coordinated_free_form_report_overclaim_rejected(self) -> None:
        mutated_outputs = dict(self.outputs)
        mutated_report = self.report + "\nThe framework works across arbitrary applications.\n"
        mutated_outputs[builder.REPORT_OUT] = mutated_report.encode("utf-8")
        mutated_result = copy.deepcopy(self.result)
        report_row = next(
            row for row in mutated_result["supporting_artifacts"] if row["path"] == builder.REPORT_OUT.relative_to(builder.ROOT).as_posix()
        )
        report_row["bytes"] = len(mutated_outputs[builder.REPORT_OUT])
        report_row["file_sha256"] = audit.sha256_bytes(mutated_outputs[builder.REPORT_OUT])
        mutated_result = reseal(mutated_result, "result_sha256")
        mutated_outputs[builder.RESULT_OUT] = builder.json_bytes(mutated_result)
        self.expect_failure(
            "EXPOSURE_CLAIM_OVERREACH",
            audit.validate_documents,
            self.source,
            self.candidates,
            self.protocol,
            mutated_result,
            mutated_report,
            self.self_review,
            virtual_files=mutated_outputs,
        )

    def test_32_root_result_overclaim_and_key_deletion_rejected(self) -> None:
        mutated = copy.deepcopy(self.result)
        mutated["claim_boundary"]["generalization_claimed"] = True
        mutated = reseal(mutated, "result_sha256")
        self.expect_failure(
            "USABILITY_OVERCLAIM",
            audit.validate_result,
            mutated,
            self.source,
            self.candidates,
            self.protocol,
            virtual_files=self.outputs,
        )
        mutated = copy.deepcopy(self.result)
        del mutated["authorization"]["authorizes_entropy"]
        mutated = reseal(mutated, "result_sha256")
        self.expect_failure(
            "STAGE_PREDECESSOR_UNSATISFIED",
            audit.validate_result,
            mutated,
            self.source,
            self.candidates,
            self.protocol,
            virtual_files=self.outputs,
        )

    def test_33_permanent_no_pod_timing_or_core_change(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["permanent_goal5793_invariants"]["goal5793_pod_or_ssh_allowed_ever"] = True
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("REGISTRY_DERIVATION_OR_CORE_DRIFT", audit.validate_protocol, mutated)

    def test_34_no_goal5793_examiner_entropy_or_scientific_output_exists(self) -> None:
        forbidden = [
            builder.ROOT / "scripts/goal5793_generic_examiner.py",
            builder.ROOT / "history/internal_docs/goal5793_selected_triplet.json",
            builder.ROOT / "history/internal_docs/goal5793_exam_result.json",
        ]
        self.assertTrue(all(not path.exists() for path in forbidden))
        self.assertFalse(any(self.protocol["authorization"].values()))
        self.assertFalse(any(self.result["authorization"].values()))

    def test_34a_historical_filename_requires_adjacent_disclaimer(self) -> None:
        mutated = copy.deepcopy(self.candidates)
        mutated["source_universe_historical_filename_disclaimer"] = "historical"
        mutated = reseal(mutated, "candidate_authority_sha256")
        self.expect_failure("EXPOSURE_CLAIM_OVERREACH", audit.validate_candidates, mutated)

    def test_34b_stage_transition_guard_cannot_be_bypassed_by_label(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["stage_transition_guards"]["state_label_alone_never_authorizes_transition"] = False
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("STAGE_PREDECESSOR_UNSATISFIED", audit.validate_protocol, mutated)

    def test_34c_declared_exposure_registry_scans_archive_contents(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["x1_generic_examiner_contract"]["pre_x1_declared_project_exposure_registry"][
            "archive_member_path_or_index_only_is_sufficient"
        ] = True
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("EXPOSURE_AUTHORITY_MISMATCH", audit.validate_protocol, mutated)

    def test_34d_dedup_fallback_cross_component_ambiguity_is_fail_closed(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["x2_systematic_expansion"]["deduplication_algorithm"]["fallback_cross_component_rule"] = "merge by title"
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("EXPANSION_PROTOCOL_DRIFT", audit.validate_protocol, mutated)

    def test_34e_query_order_cannot_be_parallelized(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["x2_systematic_expansion"]["global_query_execution_order"][
            "concurrent_or_interleaved_requests_allowed"
        ] = True
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("EXPANSION_PROTOCOL_DRIFT", audit.validate_protocol, mutated)

    def test_34f_primary_document_identity_has_no_manual_substitution(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["x2_systematic_expansion"]["uniform_full_text_resolution"][
            "authoritative_work_identity_crosscheck"
        ]["manual_paper_or_version_choice_allowed"] = True
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("SOURCE_GAP_HYGIENE_FAILURE", audit.validate_protocol, mutated)

    def test_34g_role_b_quantifier_cannot_change(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["x3_preentropy_science_projection"]["role_predicate_quantifiers"]["B"] = "any difference"
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("ROLE_REQUALIFICATION_MISMATCH", audit.validate_protocol, mutated)

    def test_34h_preselection_examiner_invocation_is_forbidden(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["x3_preentropy_science_projection"]["preselection_decision_isolation"][
            "future_candidate_examiner_invocation_count_before_selection"
        ] = 1
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("EXAMINER_METADATA_DEPENDENCE", audit.validate_protocol, mutated)

    def test_34i_triplet_sort_cannot_use_unframed_concatenation(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["x3_triplet_enumeration"]["enumerator"] = "sort by concatenated UTF-8 tuple order"
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("TRIPLET_SET_MISMATCH", audit.validate_protocol, mutated)

    def test_34j_anchor_previous_output_binding_is_required(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["deferred_entropy"]["anchor_rule"]["previous_link_rule"] = "fetch something earlier"
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", audit.validate_protocol, mutated)

    def test_34k_output_recomputation_and_trust_bundle_are_required(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["deferred_entropy"]["authentication_and_chain_verification"][
            "output_recomputation_rule"
        ] = "trust returned outputValue"
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", audit.validate_protocol, mutated)

    def test_34l_target_poll_schedule_is_fixed_and_bounded(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["deferred_entropy"]["target_rule"]["poll_schedule_seconds_after_target_ms"].append(7200)
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", audit.validate_protocol, mutated)

    def test_34m_n_zero_and_n_one_kats_are_exact(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["deferred_entropy"]["cardinality_known_answer_tests"]["n_zero"]["hash_evaluation_count"] = 1
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", audit.validate_protocol, mutated)
        mutated = copy.deepcopy(self.protocol)
        mutated["deferred_entropy"]["cardinality_known_answer_tests"]["n_one"]["selected_index"] = None
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", audit.validate_protocol, mutated)

    def test_34n_friction_missingness_cannot_turn_not_reached_into_zero(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["structural_friction_ledger"]["missingness_rules"]["not_reached_metric"] = "record zero"
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("FRICTION_LEDGER_MISMATCH", audit.validate_protocol, mutated)

    def test_34o_fallback_only_collision_cannot_become_equivalence_edge(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["x2_systematic_expansion"]["deduplication_algorithm"]["edge_rules_in_order"].append(
            "same fallback identity when both records lack strong identifiers"
        )
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("EXPANSION_PROTOCOL_DRIFT", audit.validate_protocol, mutated)

    def test_34p_author_code_direct_link_policy_cannot_choose_a_convenient_repo(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["x2_systematic_expansion"]["author_code_policy"]["direct_link_extraction_and_resolution"][
            "multiple_distinct_repository_or_ref_candidates"
        ] = "choose the easiest implementation"
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("FORBIDDEN_SELECTION_FEATURE_DEPENDENCE", audit.validate_protocol, mutated)

    def test_34q_friction_metrics_cannot_hide_different_availability_sets(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["structural_friction_ledger"]["cross_metric_aggregation_over_different_availability_sets_allowed"] = True
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("FRICTION_LEDGER_MISMATCH", audit.validate_protocol, mutated)

    def test_34r_review_dag_requires_one_cfr_and_x1_only_closure(self) -> None:
        mutated = copy.deepcopy(self.protocol)
        mutated["external_review_and_absorption_dag"]["reviewer_receives_exactly_one_file"] = False
        mutated = reseal(mutated, "protocol_authority_sha256")
        self.expect_failure("STAGE_PREDECESSOR_UNSATISFIED", audit.validate_protocol, mutated)

    def test_35_postwrite_full_chain_if_present(self) -> None:
        required = [
            builder.SOURCE_OUT,
            builder.CANDIDATE_OUT,
            builder.PROTOCOL_OUT,
            builder.REPORT_OUT,
            builder.SELF_REVIEW_OUT,
            builder.RESULT_OUT,
        ]
        if not all(path.exists() for path in required):
            self.skipTest("formal S0 outputs not yet written")
        source, candidates, protocol, result, report, self_review = audit.load_documents()
        audit.validate_documents(source, candidates, protocol, result, report, self_review)


if __name__ == "__main__":
    unittest.main()
