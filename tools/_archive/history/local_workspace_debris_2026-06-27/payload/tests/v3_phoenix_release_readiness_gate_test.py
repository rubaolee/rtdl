import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_release_readiness_gate.py"
AGGREGATE_ALIAS_JSON = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_aggregate_release_readiness_gate_2026-06-21.json"


class V3PhoenixReleaseReadinessGateTest(unittest.TestCase):
    def test_gate_blocks_v3_major_release_until_runtime_performance_mandate_passes(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["tool"], "v3_phoenix_release_readiness_gate")
        self.assertEqual(payload["gate"], "v3_performance_release_candidate")
        self.assertEqual(payload["status"], "redo_required")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows"], 13)
        self.assertEqual(payload["failed_checks"], [])
        self.assertEqual(
            payload["blocking_reasons"],
            [
                "broad_v2x_performance_not_proven",
                "serious_all_app_paired_evidence_failed_release_bar",
                "current_scoped_13_row_surface_not_v3_major_release",
                "current_core_gap_external_review_blocks_release",
            ],
        )
        self.assertNotIn("twelve_row_surface_still_too_narrow_for_major_release", payload["blocking_reasons"])
        self.assertNotIn("missing_point_location_topology_stream_m7_capability_family", payload["blocking_reasons"])
        self.assertNotIn("twelve_row_release_readiness_consensus_blocks_release", payload["blocking_reasons"])
        self.assertNotIn("current_eleven_row_release_readiness_consensus_blocks_release", payload["blocking_reasons"])
        self.assertNotIn("broad_v3_faster_than_v2_claim_not_authorized", payload["blocking_reasons"])
        self.assertNotIn("secondary_rt_performance_confirmation_not_closed", payload["blocking_reasons"])
        self.assertNotIn("general_release_installer_not_ready", payload["blocking_reasons"])
        self.assertNotIn("external_release_readiness_consensus_blocks_major_release_wording", payload["blocking_reasons"])
        self.assertNotIn("generic_engine_work_queue_open", payload["blocking_reasons"])
        self.assertTrue(all(payload["checks"].values()))
        self.assertTrue(payload["checks"]["eleven_row_claude_review_blocks_release"])
        self.assertTrue(payload["checks"]["eleven_row_codex_consensus_blocks_release"])
        self.assertTrue(payload["checks"]["twelve_row_post_p1_claude_review_approves_blocked_not_release"])
        self.assertTrue(payload["checks"]["twelve_row_post_p1_codex_consensus_blocks_release"])
        self.assertTrue(payload["checks"]["wording_gate_final_public_surface"])
        self.assertTrue(payload["checks"]["wording_gate_level_is_final_public_surface"])
        self.assertTrue(payload["checks"]["wording_gate_has_all_expected_m7_row_ids"])
        self.assertTrue(payload["checks"]["final_wording_gate_claude_review_approves_with_p1_fixed"])
        self.assertTrue(payload["checks"]["final_wording_gate_codex_consensus_complete_not_release"])
        self.assertTrue(payload["checks"]["release_surface_breadth_gate_blocks_not_release"])
        self.assertTrue(payload["checks"]["release_surface_breadth_gate_thirteen_rows"])
        self.assertTrue(payload["checks"]["release_surface_breadth_gate_records_9_of_9_capability_coverage"])
        self.assertTrue(payload["checks"]["release_surface_breadth_gate_records_no_missing_capabilities"])
        self.assertTrue(payload["checks"]["release_surface_breadth_gate_expected_current_rows_match"])
        self.assertTrue(payload["checks"]["release_surface_breadth_gate_existing_evidence_not_promotable"])
        self.assertTrue(payload["checks"]["release_surface_breadth_gate_blocks_major_release"])
        self.assertTrue(payload["checks"]["objective_conformance_gate_passed_not_release"])
        self.assertTrue(payload["checks"]["objective_conformance_current_payload_passed_not_release"])
        self.assertTrue(payload["checks"]["objective_conformance_release_false"])
        self.assertTrue(payload["checks"]["objective_conformance_public_speed_false"])
        self.assertTrue(payload["checks"]["objective_conformance_broad_speed_false"])
        self.assertTrue(payload["checks"]["objective_conformance_covers_goal_routes"])
        self.assertTrue(payload["checks"]["objective_conformance_excludes_v4_embedding_broad_claims"])
        self.assertTrue(payload["checks"]["release_surface_breadth_claude_review_approves_with_p1_fixes_required"])
        self.assertTrue(payload["checks"]["release_surface_breadth_codex_consensus_complete_not_release"])
        self.assertTrue(payload["checks"]["aggregate_13_row_review_request_targets_current_surface"])
        self.assertTrue(payload["checks"]["external_verdict_response_template_ingestible_contract_present"])
        self.assertTrue(payload["checks"]["aggregate_13_row_external_ai_blocked_recorded"])
        self.assertTrue(payload["checks"]["aggregate_13_row_codex_subagent_review_blocks_release"])
        self.assertTrue(payload["checks"]["aggregate_13_row_fallback_consensus_blocks_release"])
        self.assertTrue(payload["checks"]["external_verdict_intake_external_verdict_obtained"])
        self.assertTrue(payload["checks"]["external_verdict_intake_current_payload_external_verdict_obtained"])
        self.assertTrue(payload["checks"]["external_verdict_intake_valid_external_verdict_true"])
        self.assertTrue(payload["checks"]["external_verdict_intake_release_false"])
        self.assertTrue(payload["checks"]["external_verdict_intake_scoped_packet_true"])
        self.assertTrue(payload["checks"]["external_verdict_intake_accepts_claude_release_ready"])
        self.assertTrue(payload["checks"]["external_verdict_intake_rejects_blocked_record"])
        self.assertTrue(payload["checks"]["external_verdict_intake_rejects_codex_subagent"])
        self.assertTrue(payload["checks"]["external_verdict_intake_rejects_codex_fallback"])
        self.assertTrue(payload["checks"]["bounded_external_review_protocol_active"])
        self.assertTrue(payload["checks"]["bounded_external_review_protocol_records_scoped_verdict_and_current_redo"])
        self.assertTrue(payload["checks"]["bounded_external_review_protocol_blocks_infinite_retry"])
        self.assertTrue(payload["checks"]["current_handoff_records_current_blocked_state"])
        self.assertTrue(payload["checks"]["refresh_local_records_bounded_external_review_rule"])
        self.assertTrue(payload["checks"]["aggregate_13_row_review_packet_reference_files_exist"])
        self.assertTrue(payload["checks"]["aggregate_13_row_review_records_scope_extension_reviewed"])
        self.assertTrue(payload["checks"]["aggregate_13_row_fallback_records_scope_extension_reviewed"])
        self.assertTrue(payload["checks"]["thirteen_row_scope_extension_candidate_reviewed_not_release"])
        self.assertTrue(payload["checks"]["thirteen_row_scope_extension_review_request_prepared"])
        self.assertTrue(payload["checks"]["thirteen_row_scope_extension_claude_accepts_with_amendments_not_release"])
        self.assertTrue(payload["checks"]["thirteen_row_scope_extension_codex_consensus_reviewed_not_release"])
        self.assertEqual(set(payload["expected_base_m7_packet_rows"]), set(payload["evidence"]["m7_rows_from_packet"]))
        self.assertEqual(
            set(payload["expected_m7_rows"]),
            set(payload["evidence"]["current_surface_m7_rows_from_release_surface"]),
        )
        self.assertEqual(
            set(payload["expected_app_boundary_m7_rows"]),
            set(payload["evidence"]["m7_rows_from_app_boundary"]),
        )
        self.assertEqual(
            payload["evidence"]["secondary_platform_status"],
            "compatibility_confirmed_hardware_scope_waiver_reviewed_not_release",
        )
        self.assertTrue(payload["evidence"]["secondary_rt_hardware_scope_waiver_reviewed"])
        self.assertTrue(payload["evidence"]["secondary_platform_closes_release_blocker"])
        self.assertEqual(
            payload["evidence"]["secondary_platform_closes_release_blocker_method"],
            "reviewed_hardware_scoped_waiver",
        )
        self.assertEqual(
            payload["evidence"]["secondary_platform_closes_release_blocker_scope"],
            "single_rtx_4000_ada_driver_550_127_05_pod",
        )
        self.assertEqual(
            payload["evidence"]["hardware_performance_scope"],
            "single_rtx_4000_ada_driver_550_127_05_pod",
        )
        self.assertFalse(payload["evidence"]["secondary_rt_performance_confirmation_authorized"])
        self.assertFalse(payload["evidence"]["multi_gpu_performance_portability_claim_authorized"])
        self.assertEqual(
            payload["evidence"]["install_reproducibility_status"],
            "staged_pod_gate_present_general_release_installer_not_ready",
        )
        self.assertTrue(payload["evidence"]["staged_gpu_pod_gate_available"])
        self.assertEqual(payload["evidence"]["release_scope"], "source_tree_pod_gated_thirteen_row")
        self.assertTrue(payload["evidence"]["source_tree_pod_gated_candidate_present"])
        self.assertTrue(payload["evidence"]["source_tree_pod_gated_candidate_reviewed"])
        self.assertTrue(payload["evidence"]["source_tree_pod_gated_scoped_release_wording_reviewed"])
        self.assertFalse(payload["evidence"]["general_release_installer_ready"])
        self.assertTrue(payload["evidence"]["installer_closes_release_blocker"])
        self.assertEqual(
            payload["evidence"]["installer_closes_release_blocker_scope"],
            "source_tree_pod_gated_thirteen_row",
        )
        self.assertFalse(payload["evidence"]["package_install_claim_authorized"])
        self.assertEqual(
            payload["evidence"]["wording_gate_level"],
            "final_public_surface_claim_boundary_gate",
        )
        self.assertTrue(payload["evidence"]["wording_gate_final_public_surface_gate"])
        self.assertEqual(payload["evidence"]["wording_gate_missing_expected_m7_row_ids"], [])
        self.assertIn("blocks release wording", payload["evidence"]["wording_gate_release_authorization_note"])
        self.assertEqual(
            payload["evidence"]["release_surface_breadth_status"],
            "surface_breadth_passed_not_release",
        )
        self.assertEqual(payload["evidence"]["release_surface_breadth_total_m7_row_count"], 13)
        self.assertEqual(payload["evidence"]["release_surface_breadth_m7_capability_family_count"], 9)
        self.assertEqual(payload["evidence"]["release_surface_breadth_minimum_m7_capability_families"], 9)
        self.assertEqual(
            payload["evidence"]["release_surface_breadth_missing_m7_capability_families"],
            [],
        )
        self.assertIn(
            "updated_thirteen_row_release_readiness_consensus_required",
            payload["evidence"]["release_surface_breadth_blocking_reasons"],
        )
        self.assertFalse(payload["evidence"]["release_surface_breadth_existing_evidence_promotable_now"])
        self.assertEqual(
            payload["evidence"]["objective_conformance_status"],
            "objective_conformance_passed_not_release",
        )
        self.assertEqual(
            payload["evidence"]["objective_conformance_path"],
            "docs\\rebuild\\v3\\phoenix_v3_objective_conformance_gate_2026-06-22.json",
        )
        self.assertEqual(payload["evidence"]["objective_conformance_required_capability_coverage_count"], 5)
        self.assertEqual(payload["evidence"]["objective_conformance_required_capability_count"], 5)
        self.assertEqual(
            set(payload["evidence"]["objective_conformance_required_capabilities_covered"]),
            {
                "raydb_grouped_reduction",
                "rtdbscan_component_union",
                "spatial_rayjoin_topology_stream",
                "triangle_prepared_graph",
                "rtnn_ranked_summary",
            },
        )
        self.assertIn("v4_c_abi_embedding", payload["evidence"]["objective_conformance_exclusions"])
        self.assertIn("broad_v3_over_v2_speedup_claim", payload["evidence"]["objective_conformance_exclusions"])
        self.assertEqual(payload["evidence"]["next_engine_queue_status"], "generic_engine_work_queue_closed_not_release")
        self.assertFalse(payload["evidence"]["existing_evidence_promotable_now"])
        self.assertEqual(payload["evidence"]["next_engine_queue_ids"], [])
        self.assertEqual(
            set(payload["evidence"]["future_engine_work_ids"]),
            {"barnes_hut_vector_accumulation_frontier_shape"},
        )
        self.assertEqual(payload["evidence"]["eleven_row_claude_review_verdict"], "not-release-ready-fix-p0")
        self.assertEqual(
            payload["evidence"]["eleven_row_consensus_status"],
            "claude_codex_consensus_current_eleven_row_not_release_ready_fix_p0",
        )
        self.assertEqual(payload["evidence"]["aggregate_release_claude_review_verdict"], "not-release-ready-fix-p0")
        self.assertEqual(
            payload["evidence"]["aggregate_release_consensus_status"],
            "claude_codex_consensus_phoenix_v3_aggregate_release_not_ready_fix_p0",
        )
        self.assertEqual(payload["evidence"]["twelve_row_post_p1_claude_review_verdict"], "approve-blocked-not-release")
        self.assertEqual(
            payload["evidence"]["twelve_row_consensus_status"],
            "twelve_row_release_readiness_consensus_blocks_release",
        )
        self.assertEqual(payload["evidence"]["final_wording_gate_claude_review_verdict"], "approve-with-amendments")
        self.assertEqual(
            payload["evidence"]["final_wording_gate_consensus_status"],
            "claude_codex_consensus_final_public_surface_wording_gate_upgrade_complete_not_release",
        )
        self.assertEqual(
            payload["evidence"]["release_surface_breadth_claude_review_verdict"],
            "approve-with-amendments",
        )
        self.assertEqual(
            payload["evidence"]["release_surface_breadth_consensus_status"],
            "claude_codex_consensus_release_surface_breadth_gate_complete_not_release",
        )
        self.assertEqual(
            payload["evidence"]["aggregate_13_row_review_request_target"],
            "thirteen_row_nine_capability_surface",
        )
        self.assertEqual(
            payload["evidence"]["aggregate_13_row_scoped_dossier_external_review_status"],
            "external_verdict_obtained_claude_scoped_dossier_release_ready_not_v3_release",
        )
        self.assertEqual(payload["evidence"]["aggregate_13_row_codex_subagent_verdict"], "approve_blocked_not_release")
        self.assertEqual(
            payload["evidence"]["aggregate_13_row_fallback_consensus_status"],
            "codex_subagent_fallback_consensus_approve_blocked_not_release",
        )
        self.assertEqual(payload["evidence"]["external_verdict_intake_status"], "external_verdict_obtained")
        self.assertTrue(payload["evidence"]["external_verdict_intake_valid_external_verdict_obtained"])
        self.assertFalse(payload["evidence"]["external_verdict_intake_release_authorized"])
        self.assertTrue(payload["evidence"]["external_verdict_intake_scoped_packet_authorized"])
        self.assertEqual(payload["evidence"]["external_verdict_intake_accepted_verdict"], "release_ready")
        self.assertEqual(
            payload["evidence"]["external_verdict_intake_accepted_candidate_ids"],
            ["claude_after_dossier_release_ready"],
        )
        self.assertEqual(
            payload["evidence"]["external_verdict_intake_path"],
            "docs\\rebuild\\v3\\phoenix_v3_external_verdict_intake_2026-06-22.json",
        )
        self.assertEqual(
            payload["evidence"]["external_verdict_response_template_path"],
            "docs\\reviews\\phoenix_v3_external_verdict_response_template_2026-06-22.md",
        )
        self.assertIn("machine-readable Verdict", payload["evidence"]["external_verdict_response_template_contract"])
        self.assertEqual(payload["evidence"]["core_gaps_external_verdict_status"], "external_verdict_obtained")
        self.assertEqual(payload["evidence"]["core_gaps_external_verdict"], "approve_blocked_not_release")
        self.assertEqual(
            payload["evidence"]["core_gaps_external_status_line"],
            "external_verdict_obtained_claude_approve_blocked_not_release",
        )
        self.assertFalse(payload["evidence"]["core_gaps_external_release_authorized"])
        self.assertFalse(payload["evidence"]["core_gaps_external_public_speedup_claim_authorized"])
        self.assertFalse(payload["evidence"]["core_gaps_external_broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["evidence"]["core_gaps_external_major_version_mandate_overridden"])
        self.assertEqual(
            payload["evidence"]["core_gaps_external_review_path"],
            "docs\\reviews\\claude_phoenix_v3_external_review_2026-06-22.md",
        )
        self.assertEqual(
            payload["evidence"]["core_gaps_external_verdict_intake_path"],
            "docs\\rebuild\\v3\\phoenix_v3_core_gaps_external_verdict_intake_2026-06-22.json",
        )
        self.assertEqual(
            payload["evidence"]["core_gaps_external_status_path"],
            "docs\\rebuild\\v3\\phoenix_v3_core_gaps_external_verdict_status_2026-06-22.md",
        )
        self.assertIn("non-release redirect", payload["evidence"]["core_gaps_external_verdict_effect"])
        self.assertEqual(
            payload["evidence"]["set_a_set_b_release_bar_proposal_status"],
            "proposal_only_not_authorization",
        )
        self.assertEqual(
            payload["evidence"]["set_a_set_b_release_bar_proposal_path"],
            "docs\\reviews\\phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md",
        )
        self.assertIn("runtime_executed True", payload["evidence"]["set_a_set_b_release_bar_proposal_precondition"])
        self.assertEqual(payload["evidence"]["bounded_external_review_protocol_status"], "active_process_guard")
        self.assertEqual(
            payload["evidence"]["bounded_external_review_protocol_path"],
            "docs\\rebuild\\v3\\phoenix_v3_bounded_external_review_protocol_2026-06-22.md",
        )
        self.assertIn("scoped packet evidence", payload["evidence"]["bounded_external_review_protocol_effect"])
        self.assertEqual(
            payload["evidence"]["current_handoff_status"],
            "current_handoff_records_redo_required_state",
        )
        self.assertEqual(
            payload["evidence"]["current_handoff_path"],
            "docs\\handoff\\PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md",
        )
        self.assertEqual(
            payload["evidence"]["refresh_local_path"],
            "docs\\handoff\\REFRESH_LOCAL_2026-04-13.md",
        )
        self.assertEqual(
            payload["evidence"]["refresh_local_bounded_external_review_status"],
            "records_current_bounded_review_and_handoff_rule",
        )
        self.assertEqual(payload["evidence"]["aggregate_13_row_review_packet_reference_file_count"], 24)
        self.assertIn(
            "docs\\rebuild\\v3\\phoenix_v3_release_completion_audit_2026-06-22.md",
            payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertIn(
            "docs\\rebuild\\v3\\phoenix_v3_user_facing_performance_dossier_2026-06-22.md",
            payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertIn(
            "docs\\rebuild\\v3\\phoenix_v3_objective_conformance_gate_2026-06-22.json",
            payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertIn(
            "docs\\rebuild\\v3\\evidence\\phoenix_v3_latest_v3_rebuild_matrix_after_aabb_runner_m2_20260622.json",
            payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertIn(
            "docs\\reports\\phoenix_v3_aabb_native_query_handle_runner_route_m2_2026-06-22.md",
            payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertIn(
            "docs\\rebuild\\v3\\phoenix_v3_spatial_topology_stream_redo_alignment_2026-06-22.md",
            payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertIn(
            "docs\\rebuild\\v3\\phoenix_v3_external_verdict_intake_2026-06-22.json",
            payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertIn(
            "docs\\reviews\\phoenix_v3_external_verdict_response_template_2026-06-22.md",
            payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertIn(
            "docs\\reviews\\claude_phoenix_v3_external_review_2026-06-22.md",
            payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertIn(
            "docs\\rebuild\\v3\\phoenix_v3_core_gaps_external_verdict_intake_2026-06-22.json",
            payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertIn(
            "docs\\rebuild\\v3\\phoenix_v3_core_gaps_external_verdict_status_2026-06-22.md",
            payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertIn(
            "docs\\reviews\\phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md",
            payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertIn(
            "docs\\reviews\\claude_phoenix_v3_spatial_default_path_promotion_review_2026-06-22.md",
            payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertIn(
            "docs\\reports\\phoenix_v3_surface_integrity_gate_update_2026-06-22.md",
            payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertIn(
            "docs\\reports\\phoenix_v3_short_user_path_guard_update_2026-06-22.md",
            payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertIn(
            "docs\\reviews\\codex_phoenix_v3_source_tree_pod_gated_thirteen_row_scope_extension_2ai_consensus_2026-06-22.md",
            payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertTrue(payload["evidence"]["aggregate_13_row_scoped_dossier_external_authorization_obtained"])
        self.assertEqual(
            set(payload["evidence"]["external_verdict_intake_rejection_ids"]),
            {
                "latest_external_blocked_record",
                "codex_subagent_review",
                "codex_fallback_consensus",
            },
        )
        self.assertIn(
            "external_review_not_obtained_marker",
            payload["evidence"]["external_verdict_intake_rejection_reasons"]["latest_external_blocked_record"],
        )
        self.assertIn(
            "codex_subagent_or_internal_reviewer",
            payload["evidence"]["external_verdict_intake_rejection_reasons"]["codex_subagent_review"],
        )
        self.assertIn(
            "fallback_consensus_not_external_verdict",
            payload["evidence"]["external_verdict_intake_rejection_reasons"]["codex_fallback_consensus"],
        )
        self.assertFalse(payload["evidence"]["aggregate_13_row_installer_scope_review_required"])
        self.assertEqual(payload["evidence"]["current_installer_closure_scope"], "source_tree_pod_gated_thirteen_row")
        self.assertEqual(
            payload["evidence"]["thirteen_row_scope_extension_candidate_status"],
            "source_tree_pod_gated_thirteen_row_scope_extension_reviewed_not_release",
        )
        self.assertTrue(payload["evidence"]["thirteen_row_scope_extension_reviewed"])
        self.assertEqual(
            payload["evidence"]["thirteen_row_scope_extension_claude_review_verdict"],
            "accept-with-amendments-not-release",
        )
        self.assertEqual(
            payload["evidence"]["thirteen_row_scope_extension_consensus_status"],
            "claude_codex_consensus_source_tree_pod_gated_thirteen_row_scope_extension_reviewed_not_release",
        )
        self.assertEqual(payload["evidence"]["proposed_installer_closure_scope"], "source_tree_pod_gated_thirteen_row")

    def test_strict_release_mode_exits_nonzero_on_current_redo_required_state(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--strict-release"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 1, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "redo_required")
        self.assertTrue(payload["strict_release_exit_requested"])
        self.assertFalse(payload["release_authorized"])

    def test_legacy_aggregate_alias_is_current_redo_required_state(self):
        payload = json.loads(AGGREGATE_ALIAS_JSON.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "redo_required")
        self.assertEqual(payload["m7_qualified_release_rows"], 13)
        self.assertIn("broad_v2x_performance_not_proven", payload["blocking_reasons"])
        self.assertIn("serious_all_app_paired_evidence_failed_release_bar", payload["blocking_reasons"])
        self.assertEqual(payload["evidence"]["release_surface_breadth_total_m7_row_count"], 13)
        self.assertEqual(payload["evidence"]["release_surface_breadth_m7_capability_family_count"], 9)
        self.assertEqual(payload["evidence"]["release_surface_breadth_missing_m7_capability_families"], [])

    def test_gate_records_user_required_decision_audit(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        audit = json.loads(completed.stdout)["decision_audit"]
        self.assertEqual(
            set(audit),
            {"decision", "was_i_foolish", "foolish_actions", "other_path", "different_path_now"},
        )
        self.assertIn("Yes.", audit["was_i_foolish"])
        self.assertIn("13-row capability surface", audit["foolish_actions"])
        self.assertIn("serious all-app", audit["different_path_now"])


if __name__ == "__main__":
    unittest.main()


