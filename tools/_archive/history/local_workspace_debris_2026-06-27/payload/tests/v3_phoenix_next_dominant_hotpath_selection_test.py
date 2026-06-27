import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SELECTION_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_next_dominant_engine_hotpath_selection_2026-06-22.json"
)
SELECTION_MD = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_next_dominant_engine_hotpath_selection_2026-06-22.md"
)


class V3PhoenixNextDominantHotpathSelectionTest(unittest.TestCase):
    def load(self) -> dict:
        return json.loads(SELECTION_JSON.read_text(encoding="utf-8"))

    def test_selection_reopens_redo_engine_work_without_release_claims(self):
        payload = self.load()

        self.assertEqual(
            payload["status"],
            "active_p0_prepared_execution_session_runner_not_release",
        )
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["full_all_app_rerun_authorized_now"])
        self.assertEqual(payload["current_release_blocker"]["status"], "redo_required")
        self.assertEqual(payload["current_release_blocker"]["same_metric_comparison_count"], 52)
        self.assertAlmostEqual(
            payload["current_release_blocker"]["overall_geomean_v3_speedup_vs_v2_14"],
            1.0117790403434224,
        )
        self.assertEqual(payload["current_release_blocker"]["apps_with_geomean_gt_1_05"], 1)
        self.assertEqual(payload["current_release_blocker"]["apps_with_geomean_lt_0_95"], 2)
        self.assertFalse(payload["current_release_blocker"]["release_consideration_eligible"])

    def test_selected_p0_is_generic_prepared_execution_session_runner(self):
        payload = self.load()
        selected = payload["selected_p0"]

        self.assertEqual(selected["id"], "prepared_execution_session_runner")
        self.assertEqual(selected["priority"], "P0")
        self.assertEqual(selected["generic_capability"], "productized_prepared_execution_session")
        self.assertIn("explicit backend", selected["decision"])
        self.assertIn("explicit partner", selected["decision"])
        self.assertIn("one reusable runtime path", selected["decision"])
        self.assertGreaterEqual(len(selected["first_primitives_to_route"]), 4)
        primitive_ids = {row["primitive_family"] for row in selected["first_primitives_to_route"]}
        self.assertEqual(
            primitive_ids,
            {
                "fixed_radius_count_threshold_self_query",
                "aabb_index_query_2d_native_query_handle",
                "grouped_reduction_and_component_union_continuation",
                "point_location_topology_stream",
            },
        )
        grouped = next(
            row
            for row in selected["first_primitives_to_route"]
            if row["primitive_family"] == "grouped_reduction_and_component_union_continuation"
        )
        self.assertIn("RayDB grouped_reduction and RTDBSCAN component_union are now redo-closed", grouped["reason"])
        self.assertIn(
            "docs/rebuild/v3/phoenix_v3_raydb_grouped_reduction_redo_alignment_2026-06-22.md",
            grouped["latest_evidence"],
        )
        self.assertIn(
            "docs/rebuild/v3/phoenix_v3_rtdbscan_component_union_redo_alignment_2026-06-22.md",
            grouped["latest_evidence"],
        )
        topology = next(
            row
            for row in selected["first_primitives_to_route"]
            if row["primitive_family"] == "point_location_topology_stream"
        )
        self.assertIn("Spatial topology_stream is now redo-closed", topology["reason"])
        self.assertIn("public RayJoin author comparisons require separate result-count", topology["reason"])
        self.assertIn(
            "docs/rebuild/v3/phoenix_v3_spatial_topology_stream_redo_alignment_2026-06-22.md",
            topology["latest_evidence"],
        )
        self.assertIn(
            "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_hotpath_probe_no_go_2026-06-21.json",
            topology["latest_evidence"],
        )
        code_paths = {row["path"] for row in selected["current_code_evidence"]}
        self.assertIn("src/rtdsl/v3_0_execution_graph.py", code_paths)
        self.assertIn("src/rtdsl/v3_0_prepared_graph_chunk_executor.py", code_paths)
        self.assertIn("src/rtdsl/prepared_execution.py", code_paths)
        self.assertIn("src/rtdsl/prepared_session_residency.py", code_paths)
        self.assertIn("m1_1_current_status", selected)
        m1_1 = selected["m1_1_current_status"]
        self.assertEqual(
            m1_1["report"],
            "docs/reports/phoenix_v3_fixed_radius_self_query_runner_binding_m1_1_2026-06-22.md",
        )
        self.assertEqual(
            m1_1["primitive_family"],
            "fixed_radius_count_threshold_self_query",
        )
        self.assertTrue(m1_1["runtime_executed_in_local_contract_test"])
        self.assertFalse(m1_1["wired_into_real_benchmark_route"])
        self.assertFalse(m1_1["pod_performance_evidence"])
        self.assertFalse(m1_1["release_authorized"])
        self.assertFalse(m1_1["public_speedup_claim_authorized"])
        self.assertFalse(m1_1["full_all_app_rerun_authorized_by_this_packet"])
        self.assertIn("m1_2_current_status", selected)
        m1_2 = selected["m1_2_current_status"]
        self.assertEqual(
            m1_2["report"],
            "docs/reports/phoenix_v3_grouped_stream_runner_route_m1_2_2026-06-22.md",
        )
        self.assertEqual(
            m1_2["probe_route"],
            "PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D.run",
        )
        self.assertTrue(m1_2["productized_execution_path_visible_in_route"])
        self.assertIn("prepared_execution_session_runner_used", m1_2["runner_metadata_expected"])
        self.assertTrue(m1_2["pod_performance_evidence"])
        self.assertEqual(
            m1_2["pod_ab_report"],
            "docs/reports/phoenix_v3_grouped_stream_runner_route_pod_ab_2026-06-22.md",
        )
        self.assertEqual(m1_2["pod_ab_status"], "m1_2_runner_route_pod_ab_neutral_not_release")
        self.assertAlmostEqual(m1_2["geomean_before_over_after_speedup"], 0.9978812011247638)
        self.assertFalse(m1_2["material_speedup_observed"])
        self.assertFalse(m1_2["release_authorized"])
        self.assertFalse(m1_2["public_speedup_claim_authorized"])
        self.assertFalse(m1_2["full_all_app_rerun_authorized_by_this_packet"])
        self.assertIn("m2_current_status", selected)
        m2 = selected["m2_current_status"]
        self.assertEqual(
            m2["report"],
            "docs/reports/phoenix_v3_aabb_native_query_handle_runner_route_m2_2026-06-22.md",
        )
        self.assertEqual(
            m2["status"],
            "m2_aabb_native_query_handle_runner_contract_validated_not_release",
        )
        self.assertEqual(m2["primitive_family"], "aabb_index_query_2d_native_query_handle")
        self.assertEqual(
            m2["helper"],
            "run_aabb_index_query_2d_range_intersection_prepared_session",
        )
        self.assertIn("src/rtdsl/prepared_execution.py", m2["code"])
        self.assertIn("src/rtdsl/__init__.py", m2["code"])
        self.assertEqual(m2["test"], "tests/v3_phoenix_prepared_execution_session_runner_test.py")
        self.assertEqual(
            m2["route"],
            "examples/current/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py::aabb_broadphase_witness_rows",
        )
        self.assertEqual(
            m2["route_test"],
            "tests/v3_phoenix_aabb_prepare_reuse_pod_runner_test.py::test_contact_aabb_route_uses_productized_prepared_session_runner",
        )
        self.assertTrue(m2["runtime_executed_in_local_contract_test"])
        self.assertTrue(m2["set_a_probe_candidate"])
        self.assertTrue(m2["productized_execution_path_visible_in_helper"])
        self.assertEqual(
            m2["m2_1_route_status"],
            "m2_1_aabb_runner_backed_contact_route_validated_not_release",
        )
        self.assertTrue(m2["wired_into_real_benchmark_route"])
        self.assertTrue(m2["productized_execution_path_visible_in_route"])
        self.assertEqual(m2["route_runtime_executed_count_in_test"], 3)
        self.assertEqual(m2["route_cache_hit_count_in_test"], 2)
        self.assertEqual(
            m2["m2_1_pod_ab_status"],
            "m2_1_aabb_runner_route_pod_ab_pending_2ai_not_m7",
        )
        self.assertTrue(m2["pod_performance_evidence"])
        self.assertEqual(
            m2["pod_ab_report"],
            "docs/reports/phoenix_v3_aabb_runner_route_m2_1_pod_ab_2026-06-22.md",
        )
        self.assertEqual(
            m2["pod_ab_call_for_review"],
            "docs/reviews/call_for_review_phoenix_v3_aabb_runner_route_m2_1_pod_ab_2026-06-22.md",
        )
        self.assertEqual(
            m2["pod_ab_summary"],
            "docs/rebuild/v3/evidence/phoenix_v3_aabb_runner_m2_1_pod_ab_20260622_180241/summary.json",
        )
        self.assertTrue(m2["pod_ab_productized_runner_visible_for_prepared_backends"])
        self.assertAlmostEqual(
            m2["pod_ab_optix_over_embree_cold_plus_collect_wall_speedup"],
            1.34595769645315,
        )
        self.assertAlmostEqual(
            m2["pod_ab_optix_over_embree_query_total_speedup"],
            1.73787303873785,
        )
        self.assertEqual(m2["pod_ab_embree_runtime_executed_count"], 50)
        self.assertEqual(m2["pod_ab_optix_runtime_executed_count"], 50)
        self.assertEqual(m2["pod_ab_embree_cache_hit_count"], 49)
        self.assertEqual(m2["pod_ab_optix_cache_hit_count"], 49)
        self.assertTrue(m2["pod_ab_m7_reopen_candidate_pending_2ai_review"])
        self.assertIn("pending external review", m2["pod_performance_evidence_note"])
        self.assertTrue(m2["material_speedup_observed"])
        self.assertIn("clearing the 1.20x material", m2["interpretation"])
        self.assertFalse(m2["release_authorized"])
        self.assertFalse(m2["public_speedup_claim_authorized"])
        self.assertFalse(m2["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(m2["full_all_app_rerun_authorized_by_this_packet"])
        self.assertIn("rtdbscan_component_signature_runner_contract_status", selected)
        component_signature = selected["rtdbscan_component_signature_runner_contract_status"]
        self.assertEqual(
            component_signature["report"],
            "docs/reports/phoenix_v3_rtdbscan_component_signature_runner_route_m3_2026-06-22.md",
        )
        self.assertEqual(
            component_signature["route_report"],
            "docs/reports/phoenix_v3_rtdbscan_component_signature_runner_route_m3_1_2026-06-22.md",
        )
        self.assertEqual(
            component_signature["status"],
            "rtdbscan_component_signature_runner_route_wired_local_validated_not_release",
        )
        self.assertEqual(
            component_signature["helper"],
            "run_radius_graph_component_signature_3d_prepared_session",
        )
        self.assertEqual(
            component_signature["primitive_family"],
            "fixed_radius_graph_component_signature",
        )
        self.assertEqual(
            component_signature["continuation_contract"],
            "grouped_stream_component_size_signature_3d",
        )
        self.assertEqual(
            component_signature["productized_execution_path"],
            "prepared_execution_session_runner",
        )
        self.assertTrue(component_signature["runtime_executed_in_local_contract_test"])
        self.assertEqual(component_signature["explicit_partner"], "numba")
        self.assertTrue(component_signature["set_a_probe_candidate"])
        self.assertTrue(component_signature["wired_into_real_benchmark_route"])
        self.assertIn("rt_dbscan", component_signature["route"])
        self.assertEqual(
            component_signature["route_test"],
            "tests.v3_phoenix_rtdbscan_component_signature_optimization_test",
        )
        self.assertTrue(component_signature["route_local_contract_validated"])
        self.assertEqual(component_signature["route_runtime_executed_count_in_fake_runner_test"], 3)
        self.assertEqual(component_signature["route_cache_hit_count_in_fake_runner_test"], 2)
        self.assertFalse(component_signature["pod_performance_evidence"])
        self.assertFalse(component_signature["material_speedup_observed"])
        self.assertIn("RTDBSCAN component-signature", component_signature["next_route_target"])
        self.assertIn("focused same-hardware pod A/B", component_signature["next_action"])
        self.assertFalse(component_signature["release_authorized"])
        self.assertFalse(component_signature["public_speedup_claim_authorized"])
        self.assertFalse(component_signature["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(component_signature["true_zero_copy_claim_authorized"])
        self.assertFalse(component_signature["full_all_app_rerun_authorized_by_this_packet"])

    def test_external_review_alignment_records_approve_blocked_not_release(self):
        payload = self.load()
        review = payload["external_review_alignment"]

        self.assertEqual(review["verdict"], "approve_blocked_not_release")
        self.assertEqual(
            review["status_line"],
            "external_verdict_obtained_claude_approve_blocked_not_release",
        )
        self.assertEqual(review["direction_decision"], "continue_with_redirect")
        self.assertFalse(review["release_authorized"])
        self.assertFalse(review["public_speedup_claim_authorized"])
        self.assertFalse(review["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(review["major_version_mandate_overridden"])
        self.assertEqual(
            review["intake_path"],
            "docs/rebuild/v3/phoenix_v3_core_gaps_external_verdict_intake_2026-06-22.json",
        )
        self.assertIn("Gap 1 is the critical path", review["accepted_interpretation"])

    def test_set_a_set_b_proposal_is_measurement_design_not_gate_change(self):
        payload = self.load()
        proposal = payload["set_a_set_b_bar_proposal"]

        self.assertEqual(proposal["status"], "proposal_only_not_authorization")
        self.assertFalse(proposal["release_gate_changed_by_this_file"])
        self.assertIn("Set A", proposal["working_next_measurement_design"])
        self.assertIn("Set B", proposal["working_next_measurement_design"])
        self.assertIn("productized execution path", proposal["working_next_measurement_design"])
        self.assertIn("at least two Set-A probes", proposal["precondition_before_all_app_pod_time"])

    def test_deferred_paths_block_old_failure_modes(self):
        payload = self.load()
        decisions = {row["id"]: row["decision"] for row in payload["deferred_or_rejected_paths"]}

        self.assertEqual(decisions["more_symbol_cache_polishing"], "defer")
        self.assertEqual(decisions["self_query_count_refresh_speed_claim"], "reject_as_speed_path")
        self.assertEqual(decisions["app_specific_native_engine_shortcuts"], "reject")
        self.assertEqual(
            decisions["raydb_specific_grouped_sum_variants"],
            "reject_unless_shared_runtime_primitive",
        )
        self.assertEqual(
            decisions["spatial_public_rayjoin_speedup_wording"],
            "reject_until_author_result_count_and_paper_scope_are_proven",
        )
        self.assertEqual(decisions["repeat_full_all_app_now"], "reject_for_now")
        self.assertIn("0.998x", payload["deferred_or_rejected_paths"][1]["reason"])
        self.assertIn("1.062x", payload["deferred_or_rejected_paths"][0]["reason"])
        self.assertIn("1.001x", payload["deferred_or_rejected_paths"][0]["reason"])
        raydb_reason = next(
            row["reason"]
            for row in payload["deferred_or_rejected_paths"]
            if row["id"] == "raydb_specific_grouped_sum_variants"
        )
        self.assertIn("redo-closed", raydb_reason)
        self.assertIn("shared grouped_reduction", raydb_reason)
        spatial_reason = next(
            row["reason"]
            for row in payload["deferred_or_rejected_paths"]
            if row["id"] == "spatial_public_rayjoin_speedup_wording"
        )
        self.assertIn("one internal point_location_topology_stream row", spatial_reason)
        self.assertIn("47570-count route remains rejected", spatial_reason)

    def test_pod_trigger_requires_material_focused_evidence_before_full_rerun(self):
        payload = self.load()
        trigger = payload["pod_trigger_for_next_full_run"]

        required = " ".join(trigger["required_before_full_rerun"])
        self.assertIn("generic runtime code", required)
        self.assertIn("at least two Set-A probes", required)
        self.assertIn("focused pod A/B", required)
        self.assertIn("Set A / Set B classification is frozen", required)
        self.assertIn("correctness signatures", required)
        self.assertEqual(
            trigger["minimum_full_release_bar"]["overall_geomean_v3_speedup_vs_v2_14"],
            ">= 1.20x for release consideration",
        )
        self.assertEqual(
            trigger["minimum_full_release_bar"]["app_geomean_wins_gt_1_05"],
            ">= 8 of 10",
        )

    def test_markdown_is_reader_facing_and_keeps_boundaries(self):
        text = SELECTION_MD.read_text(encoding="utf-8")
        for phrase in (
            "active_p0_prepared_execution_session_runner_not_release",
            "Phoenix V3 remains `redo_required`",
            "prepared_execution_session_runner",
            "productized_prepared_execution_session",
            "verdict: approve_blocked_not_release",
            "proposal_only_not_authorization",
            "m2_no_execution_skeleton",
            "runtime_executed: false",
            "Current M1.1 status",
            "m1_1_fixed_radius_self_query_runner_binding_validated_not_release",
            "runtime_executed: true in local contract test",
            "not wired into a real benchmark route yet; no pod performance evidence",
            "Current M1.2 status",
            "m1_2_runner_backed_fixed_radius_probe_route_validated_not_release",
            "PreparedOptixCupyRadiusGraphGroupedStreamContinuation3D.run",
            "productized_execution_path_visible_in_route: true",
            "pod A/B exists but is neutral; no release/public/all-app authorization",
            "Current M1.2 pod A/B status",
            "m1_2_runner_route_pod_ab_neutral_not_release",
            "geomean_before_over_after_speedup: 0.9978812011247638",
            "material_speedup_observed: false",
            "Current M2 contract status",
            "m2_aabb_native_query_handle_runner_contract_validated_not_release",
            "run_aabb_index_query_2d_range_intersection_prepared_session",
            "productized_execution_path_visible_in_helper: true",
            "Current M2.1 route status",
            "m2_1_aabb_runner_backed_contact_route_validated_not_release",
            "aabb_broadphase_witness_rows",
            "productized_execution_path_visible_in_route: true",
            "runtime_executed_count_in_route_test: 3",
            "cache_hit_count_in_route_test: 2",
            "must not be reinterpreted as runner-backed evidence",
            "Current M2.1 pod A/B status",
            "m2_1_aabb_runner_route_pod_ab_pending_2ai_not_m7",
            "phoenix_v3_aabb_runner_route_m2_1_pod_ab_2026-06-22.md",
            "call_for_review_phoenix_v3_aabb_runner_route_m2_1_pod_ab_2026-06-22.md",
            "productized_runner_visible_for_prepared_backends: true",
            "optix_over_embree_cold_plus_collect_wall_speedup: 1.34595769645315",
            "optix_over_embree_query_total_speedup: 1.73787303873785",
            "runtime_executed_count: embree=50 optix=50",
            "cache_hit_count: embree=49 optix=49",
            "positive focused Set-A evidence pending external review",
            "Current RTDBSCAN/component-union runner-contract status",
            "rtdbscan_component_signature_runner_route_wired_local_validated_not_release",
            "run_radius_graph_component_signature_3d_prepared_session",
            "fixed_radius_graph_component_signature",
            "grouped_stream_component_size_signature_3d",
            "wired_into_real_benchmark_route: true",
            "route_test: tests.v3_phoenix_rtdbscan_component_signature_optimization_test",
            "pod_performance_evidence: false",
            "route_target: RTDBSCAN component-signature / component-union continuation",
            "without adding RTDBSCAN-specific native engine logic",
            "`runtime_executed: True` must be shown on at least two Set-A probes",
            "fixed_radius_count_threshold_self_query",
            "aabb_index_query_2d_native_query_handle",
            "grouped_reduction_and_component_union_continuation",
            "point_location_topology_stream",
            "Spatial public RayJoin speedup wording",
            "Self-query count-refresh speed claim",
            "Repeat full all-app now",
            "overall_geomean_v3_speedup_vs_v2_14 >= 1.20x",
            "Goal-Level Decision Audit",
            "V4, C ABI, embedding, SDK, or multi-language host scope belongs in Phoenix",
        ):
            self.assertIn(phrase, text)

    def test_gate_records_user_required_decision_audit(self):
        audit = self.load()["decision_audit"]
        self.assertEqual(
            set(audit),
            {"decision", "was_i_foolish", "foolish_actions", "other_path", "different_path_now"},
        )
        self.assertIn("prepared_execution_session_runner", audit["decision"])
        self.assertIn("No for this decision", audit["was_i_foolish"])
        self.assertIn("old closed 13-row queue", audit["foolish_actions"])
        self.assertIn("app-specific tuning", audit["other_path"])
        self.assertIn("M0-M149", audit["different_path_now"])


if __name__ == "__main__":
    unittest.main()
