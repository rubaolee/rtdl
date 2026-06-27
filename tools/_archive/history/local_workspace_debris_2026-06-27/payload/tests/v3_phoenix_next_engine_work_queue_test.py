import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_next_engine_work_queue.py"
QUEUE_JSON = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_next_generic_engine_work_queue_2026-06-21.json"
QUEUE_MD = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_next_generic_engine_work_queue_2026-06-21.md"


class V3PhoenixNextEngineWorkQueueTest(unittest.TestCase):
    def load(self):
        return json.loads(QUEUE_JSON.read_text(encoding="utf-8"))

    def test_queue_is_engine_work_not_release_authorization(self):
        payload = self.load()
        self.assertEqual(payload["status"], "generic_engine_work_queue_closed_not_release")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["existing_evidence_promotable_now"])
        self.assertEqual(payload["current_m7_qualified_release_rows"], 13)
        self.assertEqual(payload["base_m7_packet_rows"], 12)
        self.assertEqual(payload["supplemental_m7_rows_from_current_queue"], 1)
        self.assertEqual(len(payload["pending_external_review_candidates"]), 0)
        self.assertEqual(len(payload["accepted_with_boundary_candidates"]), 0)
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))
        self.assertTrue(payload["checks"]["spatial_relation_status_exact_f64_author_basis_present_not_m7"])
        self.assertTrue(payload["checks"]["spatial_active_p0_closure_gate_authorizes_future_research_closure"])
        self.assertTrue(payload["checks"]["spatial_overlay_active_count_full_scale_no_go_blocks_m7"])
        self.assertTrue(payload["checks"]["spatial_overlay_active_count_full_scale_no_go_review_request_exists"])
        self.assertTrue(payload["checks"]["spatial_prefilter_zero_experiment_exists"])
        self.assertTrue(payload["checks"]["spatial_prefilter_zero_experiment_near_miss_not_m7"])
        self.assertTrue(payload["checks"]["spatial_squared_boundary_candidate_default_path_m7_accepted"])
        self.assertTrue(payload["checks"]["spatial_squared_boundary_historical_review_request_exists"])
        self.assertTrue(payload["checks"]["spatial_squared_boundary_historical_claude_review_exists"])
        self.assertTrue(payload["checks"]["spatial_squared_boundary_historical_codex_consensus_exists"])
        self.assertTrue(payload["checks"]["spatial_squared_boundary_historical_external_blocked_record_exists"])
        self.assertTrue(payload["checks"]["spatial_default_path_review_request_exists"])
        self.assertTrue(payload["checks"]["spatial_default_path_claude_review_exists"])
        self.assertTrue(payload["checks"]["spatial_default_path_codex_consensus_exists"])
        self.assertTrue(payload["checks"]["queue_has_no_active_items_after_spatial_closure"])
        self.assertTrue(payload["checks"]["barnes_hut_fused_partner_candidate_no_longer_pending_external_review"])
        self.assertTrue(payload["checks"]["barnes_hut_fused_partner_candidate_approved_with_amendments"])
        self.assertTrue(payload["checks"]["closed_work_records_barnes_hut_fused_partner"])
        self.assertTrue(payload["checks"]["closed_work_records_spatial_default_path_topology_stream"])
        self.assertTrue(payload["checks"]["barnes_hut_fused_partner_claude_review_exists"])
        self.assertTrue(payload["checks"]["barnes_hut_fused_partner_codex_consensus_exists"])
        self.assertTrue(payload["checks"]["barnes_hut_fused_partner_claude_retry_blocked_record_exists"])
        self.assertTrue(payload["checks"]["pending_external_review_candidates_have_no_release_claims"])
        self.assertTrue(payload["checks"]["accepted_with_boundary_candidates_have_no_release_claims"])
        self.assertIn("1.01x-style result cannot qualify", payload["minimum_new_promotion_bar"])

    def test_queue_contains_only_generic_engine_capabilities(self):
        payload = self.load()
        queue = {item["id"]: item for item in payload["queue"]}
        self.assertEqual(set(queue), set())
        future = {item["id"]: item for item in payload["future_generic_engine_work"]}
        self.assertEqual(
            set(future),
            {
                "barnes_hut_vector_accumulation_frontier_shape",
            },
        )
        closed = {item["id"]: item for item in payload["closed_generic_engine_work"]}
        self.assertEqual(
            set(closed),
            {
                "grouped_reduction_prepare_amortization",
                "contact_aabb_prepare_reuse",
                "rtnn_ranked_summary_wall_path",
                "barnes_hut_fused_partner_vector_accumulation",
                "spatial_squared_boundary_default_path_topology_stream",
            },
        )
        self.assertEqual(closed["grouped_reduction_prepare_amortization"]["generic_capability"], "grouped_reduction")
        self.assertEqual(closed["grouped_reduction_prepare_amortization"]["m7_rows_added"], 2)
        self.assertEqual(closed["contact_aabb_prepare_reuse"]["generic_capability"], "aabb_candidate_stream")
        self.assertEqual(closed["contact_aabb_prepare_reuse"]["m7_rows_added"], 2)
        self.assertEqual(closed["rtnn_ranked_summary_wall_path"]["generic_capability"], "ranked_summary")
        self.assertEqual(closed["rtnn_ranked_summary_wall_path"]["m7_rows_added"], 1)
        self.assertEqual(closed["barnes_hut_fused_partner_vector_accumulation"]["generic_capability"], "aggregate_frontier")
        self.assertEqual(
            closed["barnes_hut_fused_partner_vector_accumulation"]["refined_generic_capability"],
            "vector_accumulation",
        )
        self.assertEqual(closed["barnes_hut_fused_partner_vector_accumulation"]["m7_rows_added"], 1)
        self.assertIn("4.082x faster than CPU/Numba", closed["barnes_hut_fused_partner_vector_accumulation"]["closed_state"])
        self.assertIn("13.591x OptiX no-go comparison", closed["barnes_hut_fused_partner_vector_accumulation"]["forbidden_shortcut"])
        self.assertEqual(
            closed["spatial_squared_boundary_default_path_topology_stream"]["generic_capability"],
            "point_location_topology_stream",
        )
        self.assertEqual(
            closed["spatial_squared_boundary_default_path_topology_stream"]["refined_generic_capability"],
            "exact_f64_guarded_boundary_predicate",
        )
        self.assertEqual(closed["spatial_squared_boundary_default_path_topology_stream"]["m7_rows_added"], 1)
        self.assertEqual(
            closed["spatial_squared_boundary_default_path_topology_stream"]["candidate_row_id"],
            "point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7",
        )
        self.assertEqual(future["barnes_hut_vector_accumulation_frontier_shape"]["generic_capability"], "vector_accumulation")
        self.assertEqual(
            future["barnes_hut_vector_accumulation_frontier_shape"]["priority"],
            "future_research_not_current_p0",
        )
        self.assertEqual(
            future["barnes_hut_vector_accumulation_frontier_shape"]["active_candidate_status"],
            "barnes_hut_future_research_not_current_p0_not_m7",
        )
        for item in queue.values():
            self.assertEqual(item["priority"], "P0")
            self.assertIn("generic", item["generic_engine_action"].lower())
            self.assertIn("Do not", item["forbidden_shortcut"])
            self.assertNotIn("release", item["priority"].lower())
        pending = {item["id"]: item for item in payload["pending_external_review_candidates"]}
        self.assertEqual(set(pending), set())
        accepted = {item["id"]: item for item in payload["accepted_with_boundary_candidates"]}
        self.assertEqual(set(accepted), set())

    def test_queue_preserves_current_blockers_instead_of_repromoting_old_evidence(self):
        payload = self.load()
        queue = {item["id"]: item for item in payload["queue"]}
        future = {item["id"]: item for item in payload["future_generic_engine_work"]}
        closed = {item["id"]: item for item in payload["closed_generic_engine_work"]}
        self.assertIn("cupy_device_columns", closed["grouped_reduction_prepare_amortization"]["closed_state"])
        rtnn_closed = closed["rtnn_ranked_summary_wall_path"]
        self.assertIn("Claude external review plus Codex consensus", rtnn_closed["closed_state"])
        self.assertIn("1,048,576-point", rtnn_closed["closed_state"])
        self.assertIn("7.889x hot-query", rtnn_closed["closed_state"])
        self.assertIn("1.315x cold-plus-query", rtnn_closed["closed_state"])
        self.assertIn("3.761x runner-wall", rtnn_closed["closed_state"])
        self.assertIn("CuPy uniform-grid CUDA-core", rtnn_closed["closed_state"])
        self.assertIn("across 50 prepared repeated queries", rtnn_closed["closed_state"])
        self.assertIn("float32 OptiX versus float64-coordinate CuPy grid", rtnn_closed["closed_state"])
        self.assertIn("source_manifest.sha256", rtnn_closed["closed_state"])
        self.assertEqual(
            rtnn_closed["closed_by_packet"],
            "docs/rebuild/v3/phoenix_v3_rtnn_prepared_repeat50_review_gate_2026-06-21.md",
        )
        self.assertEqual(
            rtnn_closed["closed_by_consensus"],
            "docs/reviews/codex_phoenix_v3_rtnn_prepared_repeat50_amortization_2ai_consensus_2026-06-21.md",
        )
        self.assertIn("whole RTNN", rtnn_closed["forbidden_shortcut"])
        self.assertIn("one-shot", rtnn_closed["forbidden_shortcut"])
        self.assertIn("broad V3-over-V2", rtnn_closed["forbidden_shortcut"])
        aabb_closed = closed["contact_aabb_prepare_reuse"]
        self.assertIn("Claude external review plus Codex consensus", aabb_closed["closed_state"])
        self.assertIn("1.719x", aabb_closed["closed_state"])
        self.assertIn("1.637x", aabb_closed["closed_state"])
        self.assertIn("raw AABB oracle parity", aabb_closed["closed_state"])
        self.assertIn("slower-OptiX-prepare disclosure", aabb_closed["closed_state"])
        self.assertEqual(
            aabb_closed["closed_by_packet"],
            "docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_review_gate_2026-06-21.md",
        )
        self.assertEqual(
            aabb_closed["closed_by_consensus"],
            "docs/reviews/codex_phoenix_v3_aabb_native_query_handle_final_m7_review_2ai_consensus_2026-06-21.md",
        )
        self.assertIn("broad AABB-index acceleration", aabb_closed["forbidden_shortcut"])
        spatial_closed = closed["spatial_squared_boundary_default_path_topology_stream"]
        self.assertIn("default-enabled relation-status zero prefilter", spatial_closed["closed_state"])
        self.assertIn("guarded squared-boundary exact-f64 predicate", spatial_closed["closed_state"])
        self.assertIn("no enabling env flags", spatial_closed["closed_state"])
        self.assertIn("1.080599 ms", spatial_closed["closed_state"])
        self.assertIn("exact count 47,262", spatial_closed["closed_state"])
        self.assertEqual(
            spatial_closed["closed_by_packet"],
            "docs/rebuild/v3/phoenix_v3_spatial_relation_status_squared_boundary_candidate_2026-06-21.md",
        )
        self.assertEqual(
            spatial_closed["closed_by_external_review"],
            "docs/reviews/claude_phoenix_v3_spatial_default_path_promotion_review_2026-06-22.md",
        )
        self.assertEqual(
            spatial_closed["closed_by_consensus"],
            "docs/reviews/codex_phoenix_v3_spatial_default_path_promotion_2ai_consensus_2026-06-22.md",
        )
        self.assertAlmostEqual(spatial_closed["default_path_median_ms"], 1.0805986821651459)
        self.assertEqual(spatial_closed["exact_row_count"], 47262)
        self.assertEqual(spatial_closed["m7_rows_added"], 1)
        self.assertIn("RTDL beats RayJoin", spatial_closed["forbidden_shortcut"])
        self.assertIn("true zero-copy", spatial_closed["forbidden_shortcut"])
        self.assertIn("public speedup", spatial_closed["forbidden_shortcut"])
        self.assertIn("M131 blocks a naive all-node OptiX any-hit", future["barnes_hut_vector_accumulation_frontier_shape"]["current_state"])
        self.assertIn("not an active Phoenix P0 build target", future["barnes_hut_vector_accumulation_frontier_shape"]["current_state"])
        self.assertEqual(
            future["barnes_hut_vector_accumulation_frontier_shape"]["active_candidate_packet"],
            "docs/rebuild/v3/phoenix_v3_barnes_hut_vector_accumulation_contract_2026-06-21.md",
        )
        self.assertEqual(
            future["barnes_hut_vector_accumulation_frontier_shape"]["active_candidate_status"],
            "barnes_hut_future_research_not_current_p0_not_m7",
        )
        self.assertIn("goal4525_v3_0_m129", future["barnes_hut_vector_accumulation_frontier_shape"]["m129_wrapper_gate"])
        self.assertIn("goal4527_v3_0_m131", future["barnes_hut_vector_accumulation_frontier_shape"]["m131_semantic_gate"])
        self.assertIn("goal4541_v3_0_m142", future["barnes_hut_vector_accumulation_frontier_shape"]["m142_closure_gate"])
        self.assertNotIn("general_release_installer_not_ready", payload["release_blockers_outside_engine_queue"])
        self.assertNotIn("secondary_rt_performance_confirmation_not_closed", payload["release_blockers_outside_engine_queue"])
        self.assertIn(
            "updated_thirteen_row_release_readiness_consensus_required",
            payload["release_blockers_outside_engine_queue"],
        )

    def test_markdown_keeps_user_decision_audit_and_non_app_boundary(self):
        text = QUEUE_MD.read_text(encoding="utf-8")
        for phrase in (
            "not release authorization",
            "Apps are evidence harnesses only",
            "existing_evidence_promotable_now: false",
            "pending_external_review_candidate_count: 0",
            "accepted_with_boundary_candidate_count: 0",
            "current_m7_qualified_release_rows: 13",
            "base_m7_packet_rows: 12",
            "supplemental_m7_rows_from_current_queue: 1",
            "A 1.01x-style result cannot qualify",
            "Closed Generic Engine Work",
            "grouped_reduction_prepare_amortization",
            "rtnn_ranked_summary_wall_path",
            "RTNN prepared repeat50 NPZ+CUBIN route now has Claude external review plus Codex consensus",
            "phoenix_v3_rtnn_prepared_repeat50_review_gate_2026-06-21.md",
            "codex_phoenix_v3_rtnn_prepared_repeat50_amortization_2ai_consensus_2026-06-21.md",
            "7.889x hot-query",
            "1.315x cold-plus-query",
            "3.761x runner-wall",
            "CuPy uniform-grid CUDA-core",
            "source_manifest.sha256",
            "barnes_hut_fused_partner_vector_accumulation",
            "aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped",
            "claude_phoenix_v3_barnes_hut_fused_partner_m7_candidate_review_2026-06-21.md",
            "codex_phoenix_v3_barnes_hut_fused_partner_m7_candidate_2ai_consensus_2026-06-21.md",
            "barnes_hut_theta_0.5_2d_bucketized",
            "route_parity_plus_checksum_no_independent_oracle",
            "M7 rows added: 1",
            "contact_aabb_prepare_reuse",
            "AABB native prepared-query-handle route now has Claude external review plus Codex consensus",
            "phoenix_v3_aabb_native_query_handle_review_gate_2026-06-21.md",
            "codex_phoenix_v3_aabb_native_query_handle_final_m7_review_2ai_consensus_2026-06-21.md",
            "32,768 at 1.719x",
            "65,536 at 1.637x",
            "slower-OptiX-prepare disclosure",
            "spatial_squared_boundary_default_path_topology_stream",
            "point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7",
            "claude_phoenix_v3_spatial_default_path_promotion_review_2026-06-22.md",
            "codex_phoenix_v3_spatial_default_path_promotion_2ai_consensus_2026-06-22.md",
            "default-path median is 1.080599 ms",
            "exact count 47,262",
            "The author Query timer is an internal bar only",
            "Future Research Records",
            "barnes_hut_vector_accumulation_frontier_shape",
            "phoenix_v3_barnes_hut_vector_accumulation_contract_2026-06-21.md",
            "barnes_hut_future_research_not_current_p0_not_m7",
            "future_research_not_current_p0",
            "goal4525_v3_0_m129_barnes_hut_rt_native_python_wrapper_gate_2026-06-17.json",
            "goal4527_v3_0_m131_barnes_hut_rt_native_traversal_semantic_gate_2026-06-17.json",
            "goal4541_v3_0_m142_barnes_hut_current_route_closure_gate_2026-06-17.json",
            "Pending External Review Candidates",
            "- none",
            "Accepted With Boundary Candidates",
            "- none",
            "Goal-Level Decision Audit",
        ):
            self.assertIn(phrase, text)

    def test_script_rebuilds_queue_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "queue.json"
            md_out = Path(tmp) / "queue.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertEqual(json.loads(json_out.read_text(encoding="utf-8")), self.load())
            self.assertIn("Phoenix V3 Next Generic Engine Work Queue", md_out.read_text(encoding="utf-8"))

    def test_gate_records_user_required_decision_audit(self):
        audit = self.load()["decision_audit"]
        self.assertEqual(
            set(audit),
            {"decision", "was_i_foolish", "foolish_actions", "other_path", "different_path_now"},
        )
        self.assertIn("No.", audit["was_i_foolish"])
        self.assertIn("old P0 matrix", audit["foolish_actions"])
        self.assertIn("1262x timed-median ratio", audit["foolish_actions"])
        self.assertIn("Bash/PowerShell heredoc", audit["foolish_actions"])
        self.assertIn("13 rows and 9 capability families", audit["different_path_now"])
        self.assertIn("Barnes-Hut 13.591x OptiX no-go comparison", audit["foolish_actions"])
        self.assertIn("RTNN prepared repeat50", audit["was_i_foolish"])
        self.assertIn("grouped_sum", audit["was_i_foolish"])
        self.assertIn("AABB native-query-handle", audit["was_i_foolish"])
        self.assertIn("amended Barnes-Hut fused-partner", audit["was_i_foolish"])
        self.assertIn("one-shot", audit["was_i_foolish"])
        self.assertIn("Spatial default-path", audit["was_i_foolish"])
        self.assertIn("guarded squared-boundary", audit["was_i_foolish"])


if __name__ == "__main__":
    unittest.main()
