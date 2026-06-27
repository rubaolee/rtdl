import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_m7_row_classification_packet.py"
PACKET = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m7_row_classification_packet_2026-06-20.json"
REPORT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m7_row_classification_packet_2026-06-20.md"


class V3PhoenixM7RowClassificationPacketTest(unittest.TestCase):
    def load(self):
        return json.loads(PACKET.read_text(encoding="utf-8"))

    def test_packet_is_not_release_authorization(self):
        payload = self.load()
        self.assertEqual(payload["status"], "m7_classification_packet_not_release")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertEqual(payload["phoenix_m7_qualified_release_rows"], 12)
        self.assertEqual(payload["summary"]["m7_qualified_release_rows"], 12)
        self.assertEqual(payload["summary"]["route_map_m7_qualified_release_rows"], 5)
        self.assertEqual(payload["summary"]["supplemental_m7_qualified_release_rows"], 7)
        self.assertEqual(payload["summary"]["row_count"], 19)
        self.assertEqual(payload["summary"]["apps_covered"], 10)
        self.assertEqual(payload["summary"]["public_claim_rows"], 0)
        self.assertEqual(payload["summary"]["row_scoped_public_claim_rows"], 12)
        self.assertEqual(payload["summary"]["final_review_blocked_packets"], 0)

    def test_every_row_is_blocked_or_internal_with_explicit_blockers(self):
        payload = self.load()
        rows = payload["row_classifications"]
        self.assertEqual(len(rows), 19)
        for row in rows:
            self.assertFalse(row["release_authorized"])
            self.assertFalse(row["public_speedup_claim_authorized"])
            self.assertFalse(row["broad_v3_faster_than_v2_claim_authorized"])
            if row["m7_classification"] == "m7_qualified_release_row":
                self.assertTrue(row["row_scoped_public_speedup_claim_authorized"])
                if row["comparison_group"] == "aabb_index_all_count_only_large_32768":
                    self.assertEqual(row["numeric_contract"], "native_float32_inclusive_boundary")
                    self.assertIn("float64 exact-geometry", row["forbidden_public_reading"])
                elif row["comparison_group"] == "triangle_count_rt_graph_2a1_cliques_80000":
                    self.assertEqual(
                        row["candidate_row_id"],
                        "prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream",
                    )
                    self.assertFalse(row["m113_graph_capture_claim_authorized"])
                    self.assertIn("automatic partner selection", row["forbidden_public_reading"])
                elif row["comparison_group"] == "dbscan_cluster_signature":
                    self.assertEqual(
                        row["candidate_row_id"],
                        "component_union_clustered3d_65536_524288_repeat5_row_scoped",
                    )
                    self.assertAlmostEqual(row["speedup_floor"], 1.1019949345652873)
                    self.assertAlmostEqual(row["speedup_ceiling"], 1.2356860771339773)
                    self.assertIn("zero-noise four-cluster synthetic", row["allowed_internal_reading"])
                    self.assertIn("Numba continuation still dominates", row["allowed_internal_reading"])
                    self.assertIn("not independent CPU reference validation", row["large_scale_correctness_basis"])
                    self.assertIn("full DBSCAN acceleration", row["forbidden_public_reading"])
                elif row["comparison_group"] == "hausdorff_threshold_copies_262144":
                    self.assertEqual(
                        row["candidate_row_id"],
                        "hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped",
                    )
                    self.assertAlmostEqual(row["phase_total_ratio_mean"], 1.240042444838897)
                    self.assertAlmostEqual(row["weakest_phase_total_optix_speedup_vs_embree"], 1.2243669013234328)
                    self.assertTrue(row["phase_total_includes_scene_preparation"])
                    self.assertEqual(row["threshold"], 0.4)
                    self.assertEqual(row["point_count_per_side"], 1048576)
                    self.assertIn("phase-total includes scene preparation", row["allowed_internal_reading"])
                    self.assertIn("full Hausdorff distance", row["forbidden_public_reading"])
                    self.assertIn("expected_tiled_hausdorff", row["oracle_definition"])
                elif row["comparison_group"] == "prepared_collision_flags":
                    self.assertEqual(
                        row["candidate_row_id"],
                        "collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped",
                    )
                    self.assertAlmostEqual(row["tail_total_run_optix_speedup_vs_embree_mean"], 5.086007905721244)
                    self.assertAlmostEqual(row["total_run_window_optix_speedup_vs_embree_mean"], 5.074757302896491)
                    self.assertAlmostEqual(row["wrapper_no_probe_optix_speedup_vs_embree_mean"], 1.1707471638911713)
                    self.assertAlmostEqual(row["weakest_wrapper_no_probe_optix_speedup_vs_embree"], 1.0827873042297134)
                    self.assertEqual(row["shape"]["static_obstacle_triangle_count"], 4096)
                    self.assertTrue(row["validation_protocol"]["all_validation_rows_match_probe_reference"])
                    self.assertTrue(row["timing_protocol"]["timed_rows_use_no_probe_reference"])
                    self.assertIn("prepared query execution phase", row["allowed_internal_reading"])
                    self.assertIn("full robot planning", row["forbidden_public_reading"])
                else:
                    self.fail(f"unexpected M7 row {row['comparison_group']}")
            else:
                self.assertFalse(row["row_scoped_public_speedup_claim_authorized"])
                self.assertGreater(len(row["m7_blockers"]), 0)
                self.assertIn("Do not use this row as V3 release evidence", row["forbidden_public_reading"])
            self.assertNotEqual(row["evidence_basis"], "")

    def test_focused_evidence_preserves_hard_negative_facts(self):
        focused = self.load()["focused_evidence"]
        self.assertEqual(focused["m4_grouped_continuation"]["phoenix_m7_qualified_release_rows"], 0)
        self.assertTrue(focused["m4_grouped_continuation"]["all_rows_not_m7"])
        self.assertEqual(focused["m4_grouped_continuation"]["system_python_packaging_gap_status"], "open")
        self.assertFalse(focused["m4_grouped_continuation"]["m10_clean_pass"])

        self.assertEqual(focused["m5_topology"]["m5_author_code_comparison_status"], "complete")
        self.assertTrue(focused["m5_topology"]["rayjoin_author_rt_is_faster_than_rtdl_optix"])
        self.assertGreater(
            focused["m5_topology"]["rayjoin_author_rt_speedup_vs_rtdl_optix_native_traversal"],
            3.0,
        )

        self.assertTrue(focused["m6_barnes_hut"]["timing_basis_mixed"])
        self.assertTrue(
            all(route == "numba_cuda_fused" for route in focused["m6_barnes_hut"]["fastest_by_scale"].values())
        )
        self.assertGreater(focused["m6_barnes_hut"]["prepared_optix_over_fastest"]["131072"], 10.0)

        self.assertGreater(focused["raydb_m28_grouped_reduction"]["sum_embree_over_optix"], 100.0)
        self.assertGreater(focused["raydb_m28_grouped_reduction"]["sum_min_workload_build_sec"], 200.0)
        self.assertEqual(
            focused["raydb_m28_grouped_reduction"]["comparison_scope"],
            "internal_same_contract_prepared_query_refresh_not_public_speedup",
        )

        self.assertEqual(focused["triangle_prepared_graph"]["status"], "internal_triangle_prepared_graph_candidate_not_m7")
        self.assertFalse(focused["triangle_prepared_graph"]["m7_qualified"])
        self.assertIn(
            "prepared_graph_chunk_executor_linkage_not_closed",
            focused["triangle_prepared_graph"]["m7_blockers"],
        )

        self.assertEqual(focused["rtnn_ranked_summary"]["status"], "internal_rtnn_ranked_summary_candidate_not_m7")
        self.assertFalse(focused["rtnn_ranked_summary"]["m7_qualified"])
        self.assertTrue(focused["rtnn_ranked_summary"]["all_hot_optix_faster_than_embree"])
        self.assertTrue(focused["rtnn_ranked_summary"]["all_wall_optix_slower_than_embree"])

    def test_contact_manifold_row_points_to_focused_boundary_not_unfocused_packet(self):
        row = next(
            row
            for row in self.load()["row_classifications"]
            if row["app_id"] == "contact_manifold"
        )
        self.assertEqual(row["review_status"], "focused_boundary_wall_regression_not_m7")
        self.assertEqual(
            row["evidence_basis"],
            "docs/rebuild/v3/phoenix_v3_contact_manifold_broadphase_boundary_2026-06-21.md",
        )
        self.assertIn("wall_timing_optix_slower_than_embree", row["m7_blockers"])
        self.assertNotIn("no_focused_m7_packet", row["m7_blockers"])

    def test_capability_summaries_keep_reviewed_and_unfocused_routes_separate(self):
        summaries = {item["generic_capability"]: item for item in self.load()["capability_summaries"]}
        self.assertEqual(
            summaries["grouped_reduction"]["review_status"],
            "accepted_internal_grouped_reduction_not_m7",
        )
        self.assertEqual(
            summaries["point_location_topology_stream"]["review_status"],
            "accepted_internal_m5_author_complete_not_m7",
        )
        self.assertEqual(
            summaries["aggregate_frontier"]["review_status"],
            "accepted_internal_m6_route_parity_not_m7",
        )
        self.assertEqual(
            summaries["aabb_candidate_stream"]["review_status"],
            "one_route_map_row_m7_qualified_row_scoped",
        )
        self.assertEqual(summaries["aabb_candidate_stream"]["m7_qualified_release_rows"], 1)
        self.assertTrue(summaries["aabb_candidate_stream"]["row_scoped_public_speedup_claim_authorized"])
        self.assertEqual(
            summaries["prepared_graph_chunk"]["review_status"],
            "one_triangle_route_map_row_m7_qualified_after_claude_refresh",
        )
        self.assertEqual(summaries["prepared_graph_chunk"]["m7_qualified_release_rows"], 1)
        self.assertTrue(summaries["prepared_graph_chunk"]["row_scoped_public_speedup_claim_authorized"])
        self.assertEqual(
            summaries["component_union"]["review_status"],
            "claude_codex_m7_qualified_row_scoped",
        )
        self.assertEqual(summaries["component_union"]["m7_qualified_release_rows"], 1)
        self.assertTrue(summaries["component_union"]["row_scoped_public_speedup_claim_authorized"])
        self.assertIn(
            "do_not_generalize_to_full_dbscan_rt_dbscan_paper_v2_or_noisy_datasets",
            summaries["component_union"]["m7_blockers"],
        )
        self.assertEqual(
            summaries["threshold_summary"]["review_status"],
            "one_large_row_m7_qualified_row_scoped",
        )
        self.assertEqual(summaries["threshold_summary"]["m7_qualified_release_rows"], 1)
        self.assertTrue(summaries["threshold_summary"]["row_scoped_public_speedup_claim_authorized"])
        self.assertIn(
            "remaining_threshold_summary_rows_not_phase_total_wins",
            summaries["threshold_summary"]["m7_blockers"],
        )
        self.assertEqual(
            summaries["collision_flag_stream"]["review_status"],
            "claude_codex_m7_qualified_row_scoped",
        )
        self.assertEqual(summaries["collision_flag_stream"]["m7_qualified_release_rows"], 1)
        self.assertTrue(summaries["collision_flag_stream"]["row_scoped_public_speedup_claim_authorized"])
        self.assertAlmostEqual(
            summaries["collision_flag_stream"]["wrapper_no_probe_optix_speedup_vs_embree_mean"],
            1.1707471638911713,
        )
        self.assertIn(
            "do_not_generalize_to_full_robot_planning_exact_or_continuous_collision_v2_or_zero_copy",
            summaries["collision_flag_stream"]["m7_blockers"],
        )
        for key, item in summaries.items():
            if key in {
                "aabb_candidate_stream",
                "collision_flag_stream",
                "component_union",
                "prepared_graph_chunk",
                "threshold_summary",
            }:
                continue
            self.assertEqual(item["m7_qualified_release_rows"], 0)
            self.assertFalse(item["release_authorized"])
            self.assertFalse(item["public_speedup_claim_authorized"])
        self.assertIn("remaining_triangle_rows_not_m7", summaries["prepared_graph_chunk"]["m7_blockers"])
        self.assertIn(
            "paper_equivalent_rtnn_row_false",
            summaries["ranked_summary"]["m7_blockers"],
        )
        self.assertIn(
            "prepared_cuda_graph_replay_false",
            summaries["ranked_summary"]["m7_blockers"],
        )

    def test_next_m7_candidates_are_empty_until_engine_optimization_reopens_rows(self):
        payload = self.load()
        self.assertEqual(payload["next_m7_promotion_candidates"], [])
        queue = {item["candidate"]: item for item in payload["optimization_required_reopen_queue"]}
        self.assertEqual(queue, {})
        self.assertEqual(
            payload["next_engine_work_queue"]["active_p0_ids"],
            [],
        )
        self.assertEqual(
            payload["next_engine_work_queue"]["future_research_ids"],
            [
                "barnes_hut_vector_accumulation_frontier_shape",
                "spatial_rayjoin_topology_stream_author_gap",
            ],
        )
        self.assertIn(
            "RT-native Barnes-Hut/vector accumulation remains future research",
            payload["summary"]["next_work"],
        )
        self.assertIn(
            "AABB native query-handle is now closed as two supplemental M7 rows",
            payload["summary"]["next_work"],
        )

    def test_post_classification_final_review_packet_is_blocked_not_promoted(self):
        packets = self.load()["post_classification_final_review_packets"]
        self.assertEqual(len(packets), 9)
        packet = next(item for item in packets if item["generic_capability"] == "grouped_reduction")
        self.assertEqual(
            packet["candidate_row_id"],
            "grouped_reduction_sum_scalar_broadcast_repeat100_262144",
        )
        self.assertEqual(packet["classification_counting_basis"], "supplemental_new_row")
        self.assertEqual(packet["classification_m7_contribution"], 1)
        self.assertTrue(packet["local_evidence_sufficient_for_external_public_row_review"])
        self.assertTrue(packet["row_scoped_public_speedup_claim_authorized"])
        self.assertEqual(packet["local_gate_reading"], "m7_qualified_row_scoped_after_claude_codex_consensus")
        self.assertEqual(packet["current_packet_external_review_status"], "claude_approved")
        self.assertEqual(packet["current_packet_2ai_consensus_status"], "claude_codex_consensus_complete")
        self.assertEqual(packet["m7_qualified_release_rows"], 1)
        self.assertAlmostEqual(packet["actual_repeat100_loop_speedup"], 200.352573808868)
        self.assertAlmostEqual(packet["actual_repeat100_cold_plus_loop_speedup"], 27.9170612400067)
        self.assertIn(
            "claude_phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_review_2026-06-21.md",
            packet["external_review"],
        )
        self.assertEqual(packet["source_provenance_basis"], "source_manifest.sha256")
        device = next(
            item
            for item in packets
            if item["packet"].endswith(
                "phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.json"
            )
        )
        self.assertEqual(
            device["classification_counting_basis"],
            "supplemental_new_rows_after_claude_external_review_and_codex_supersession_consensus",
        )
        self.assertEqual(device["classification_m7_contribution"], 2)
        self.assertEqual(device["m7_qualified_release_rows"], 2)
        self.assertEqual(device["status"], "grouped_reduction_device_column_scoped_row_evidence_not_release")
        self.assertEqual(
            device["current_packet_external_review_status"],
            "claude_external_approve_with_required_fixes_p1_applied_2026-06-22",
        )
        self.assertEqual(
            device["current_packet_2ai_consensus_status"],
            "claude_codex_consensus_complete_after_subagent_gap_supersession_2026-06-22",
        )
        self.assertTrue(device["all_cpu_reference_match"])
        self.assertTrue(device["all_device_routes_remove_host_packed_rays"])
        self.assertGreater(device["min_host_packed_over_device_columns_cold_plus_loop_speedup"], 3.0)
        self.assertGreater(device["max_host_packed_over_device_columns_cold_plus_loop_speedup"], 70.0)
        self.assertGreater(device["min_embree_over_optix_device_columns_cold_plus_loop_speedup"], 100.0)
        self.assertIn(
            "grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups",
            device["candidate_row_ids"],
        )
        self.assertIn(
            "grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups",
            device["candidate_row_ids"],
        )
        self.assertIn("source_manifest.sha256", device["source_manifest_path"])
        self.assertIn("same-contract context", "\n".join(device["p1_review_fixes_applied"]))
        aabb = next(
            item
            for item in packets
            if item["packet"].endswith(
                "phoenix_v3_aabb_candidate_stream_32768_m7_final_review_packet_2026-06-21.json"
            )
        )
        self.assertEqual(aabb["candidate_row_id"], "aabb_candidate_stream_all_count_only_float32_32768")
        self.assertEqual(aabb["classification_counting_basis"], "route_map_row_promoted")
        self.assertEqual(aabb["classification_m7_contribution"], 0)
        self.assertEqual(aabb["current_packet_external_review_status"], "claude_approved_after_p0_wording_fix")
        self.assertEqual(aabb["current_packet_2ai_consensus_status"], "claude_codex_consensus_complete")
        self.assertTrue(aabb["matches_float32_cpu_reference"])
        self.assertFalse(aabb["matches_float64_cpu_reference"])
        self.assertAlmostEqual(aabb["query_optix_over_embree"], 814.3388221324167)
        aabb_native = next(
            item
            for item in packets
            if item["packet"].endswith("phoenix_v3_aabb_native_query_handle_review_gate_2026-06-21.json")
        )
        self.assertEqual(
            aabb_native["classification_counting_basis"],
            "supplemental_new_rows_after_claude_codex_consensus",
        )
        self.assertEqual(aabb_native["classification_m7_contribution"], 2)
        self.assertEqual(aabb_native["m7_qualified_release_rows"], 2)
        self.assertEqual(aabb_native["status"], "aabb_native_query_handle_two_rows_m7_qualified_row_scoped")
        self.assertEqual(aabb_native["current_packet_external_review_status"], "claude_approve_with_conditions")
        self.assertEqual(
            aabb_native["current_packet_2ai_consensus_status"],
            "claude_codex_consensus_complete_approve_two_row_scoped_m7_rows",
        )
        self.assertIn(
            "aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50",
            aabb_native["candidate_row_ids"],
        )
        self.assertIn(
            "aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50",
            aabb_native["candidate_row_ids"],
        )
        self.assertGreater(aabb_native["best_cold_plus_collect_wall_speedup"], 1.7)
        self.assertGreater(aabb_native["weakest_cold_plus_collect_wall_speedup"], 1.6)
        self.assertEqual(
            aabb_native["source_manifest_provenance_sha256"],
            "f7d8a0ae6e39c691bf7c949b23741181abcc24fc3e3ef405f73c7a113d1e4422",
        )
        self.assertIn("OptiX prepare alone remains slower than Embree", "\n".join(aabb_native["approved_row_scoped_public_wording"]))
        self.assertIn("POD source directory had no git_head", "\n".join(aabb_native["p1_promotion_record_requirements"]))
        self.assertIn("OptiX prepare alone remains slower than Embree", "\n".join(aabb_native["p1_promotion_record_requirements"]))
        rtnn_repeat50 = next(item for item in packets if item["generic_capability"] == "ranked_summary")
        self.assertEqual(
            rtnn_repeat50["candidate_row_id"],
            "rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02",
        )
        self.assertEqual(
            rtnn_repeat50["classification_counting_basis"],
            "supplemental_new_row_after_claude_codex_consensus",
        )
        self.assertEqual(rtnn_repeat50["classification_m7_contribution"], 1)
        self.assertEqual(rtnn_repeat50["m7_qualified_release_rows"], 1)
        self.assertEqual(rtnn_repeat50["status"], "rtnn_prepared_repeat50_m7_qualified_row_scoped")
        self.assertEqual(rtnn_repeat50["current_packet_external_review_status"], "claude_approve_with_conditions")
        self.assertEqual(
            rtnn_repeat50["current_packet_2ai_consensus_status"],
            "claude_codex_consensus_complete_approve_one_row_scoped_m7",
        )
        self.assertAlmostEqual(rtnn_repeat50["hot_query_speedup"], 7.88855708189875)
        self.assertAlmostEqual(rtnn_repeat50["cold_plus_query_speedup"], 1.3150391330840123)
        self.assertAlmostEqual(rtnn_repeat50["runner_wall_speedup"], 3.760722286400028)
        self.assertIn("float32 internal precision", rtnn_repeat50["precision_disclosure"])
        self.assertIn("source_manifest.sha256", rtnn_repeat50["source_manifest_path"])
        self.assertFalse(rtnn_repeat50["release_authorized"])
        self.assertFalse(rtnn_repeat50["whole_rtnn_claim_authorized"])
        self.assertFalse(rtnn_repeat50["one_shot_rtnn_claim_authorized"])
        self.assertIn("CuPy uniform-grid CUDA-core", rtnn_repeat50["approved_row_scoped_public_wording"])
        self.assertIn("RTNN is solved", "\n".join(rtnn_repeat50["forbidden_public_wording"]))
        barnes = next(item for item in packets if item["generic_capability"] == "aggregate_frontier")
        self.assertEqual(
            barnes["candidate_row_id"],
            "aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped",
        )
        self.assertEqual(
            barnes["classification_counting_basis"],
            "supplemental_new_row_after_claude_approve_with_amendments",
        )
        self.assertEqual(barnes["classification_m7_contribution"], 1)
        self.assertEqual(barnes["m7_qualified_release_rows"], 1)
        self.assertEqual(barnes["status"], "aggregate_tree_fused_partner_m7_qualified_row_scoped_after_claude_amendments")
        self.assertEqual(barnes["current_packet_external_review_status"], "claude_approve_with_amendments")
        self.assertEqual(
            barnes["current_packet_2ai_consensus_status"],
            "claude_codex_consensus_complete_approve_one_row_scoped_m7_with_amendments",
        )
        self.assertEqual(barnes["evidence_tree_structure"], "barnes_hut_theta_0.5_2d_bucketized")
        self.assertEqual(
            barnes["large_scale_validation_tier"],
            "route_parity_plus_checksum_no_independent_oracle",
        )
        self.assertIn("m6_barnes_hut_rerank_32768_65536_131072_partitioned_r11.json", barnes["evidence_source_artifact"])
        self.assertAlmostEqual(barnes["candidate_wall_repeat_ms"], 45.492701)
        self.assertAlmostEqual(barnes["cpu_numba_fused_over_candidate"], 4.081631994617688)
        self.assertAlmostEqual(
            barnes["prepared_optix_numba_over_candidate_supplemental_not_primary"],
            13.591229310768684,
        )
        self.assertIn("4.082x faster than CPU/Numba fused baseline", barnes["approved_row_scoped_public_wording"])
        self.assertIn("Large-scale validation: route parity plus checksum", barnes["approved_row_scoped_public_wording"])
        self.assertIn("prepared_optix_ratio_supporting_metadata_only", barnes["amendments_applied"])
        self.assertIn("13.591x over OptiX as the primary claim", barnes["forbidden_public_wording"])
        self.assertFalse(barnes["release_authorized"])
        self.assertFalse(barnes["public_speedup_claim_authorized"])
        self.assertFalse(barnes["rt_core_speedup_claim_authorized"])
        triangle = next(item for item in packets if item["generic_capability"] == "prepared_graph_chunk")
        self.assertEqual(
            triangle["candidate_row_id"],
            "prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream",
        )
        self.assertEqual(triangle["classification_counting_basis"], "route_map_row_promoted")
        self.assertEqual(triangle["classification_m7_contribution"], 0)
        self.assertEqual(
            triangle["current_packet_external_review_status"],
            "claude_reviewed_approved_with_amendments_2026-06-21",
        )
        self.assertEqual(
            triangle["current_packet_2ai_consensus_status"],
            "claude_codex_consensus_complete",
        )
        self.assertIn(
            "claude_phoenix_v3_triangle_prepared_graph_80000_m7_refresh_review_2026-06-21.md",
            triangle["external_review"],
        )
        self.assertFalse(triangle["m113_graph_capture_claim_authorized"])
        self.assertAlmostEqual(triangle["hot_optix_over_embree"], 347.23219125688223)
        self.assertAlmostEqual(triangle["wall_optix_over_embree"], 6.342008514587283)
        hausdorff = next(item for item in packets if item["generic_capability"] == "threshold_summary")
        self.assertEqual(
            hausdorff["candidate_row_id"],
            "hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped",
        )
        self.assertEqual(hausdorff["classification_counting_basis"], "route_map_row_promoted")
        self.assertEqual(hausdorff["classification_m7_contribution"], 0)
        self.assertEqual(
            hausdorff["current_packet_external_review_status"],
            "claude_approved_after_p0_repair_and_scene_prepare_wording",
        )
        self.assertEqual(
            hausdorff["current_packet_2ai_consensus_status"],
            "claude_codex_consensus_complete",
        )
        self.assertTrue(hausdorff["phase_total_includes_scene_preparation"])
        self.assertAlmostEqual(hausdorff["query_ratio_mean"], 1.6386841066991966)
        self.assertAlmostEqual(hausdorff["phase_total_ratio_mean"], 1.240042444838897)
        self.assertAlmostEqual(hausdorff["weakest_phase_total_optix_speedup_vs_embree"], 1.2243669013234328)
        collision = next(item for item in packets if item["generic_capability"] == "collision_flag_stream")
        self.assertEqual(
            collision["candidate_row_id"],
            "collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped",
        )
        self.assertEqual(collision["classification_counting_basis"], "route_map_row_promoted")
        self.assertEqual(collision["classification_m7_contribution"], 0)
        self.assertEqual(
            collision["current_packet_external_review_status"],
            "claude_approved_with_p1_amendments_resolved",
        )
        self.assertEqual(collision["current_packet_2ai_consensus_status"], "claude_codex_consensus_complete")
        self.assertAlmostEqual(collision["tail_total_run_optix_speedup_vs_embree_mean"], 5.086007905721244)
        self.assertAlmostEqual(collision["total_run_window_optix_speedup_vs_embree_mean"], 5.074757302896491)
        self.assertAlmostEqual(collision["wrapper_no_probe_optix_speedup_vs_embree_mean"], 1.1707471638911713)
        self.assertAlmostEqual(collision["weakest_wrapper_no_probe_optix_speedup_vs_embree"], 1.0827873042297134)

    def test_vector_accumulation_scope_note_prevents_silent_subsumption(self):
        notes = {item["capability"]: item for item in self.load()["capability_scope_notes"]}
        self.assertEqual(
            notes["vector_accumulation"]["status"],
            "covered_by_amended_fused_partner_m7_row_rt_native_future_research",
        )
        self.assertFalse(notes["vector_accumulation"]["release_authorized"])
        self.assertFalse(notes["vector_accumulation"]["public_speedup_claim_authorized"])
        self.assertIn("exactly one amended M7 milestone row", notes["vector_accumulation"]["note"])
        self.assertIn("aggregate_frontier/vector_accumulation breadth gap", notes["vector_accumulation"]["note"])
        self.assertIn("RT-native hierarchical traversal remains future research", notes["vector_accumulation"]["note"])

    def test_script_rebuilds_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "packet.json"
            md_out = Path(tmp) / "packet.md"
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
            rebuilt = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertEqual(rebuilt["summary"], self.load()["summary"])
            self.assertEqual(rebuilt["focused_evidence"], self.load()["focused_evidence"])
            self.assertEqual(rebuilt["capability_summaries"], self.load()["capability_summaries"])
            self.assertEqual(rebuilt["next_engine_work_queue"], self.load()["next_engine_work_queue"])
            self.assertEqual(
                rebuilt["post_classification_final_review_packets"],
                self.load()["post_classification_final_review_packets"],
            )
            self.assertEqual(rebuilt["capability_scope_notes"], self.load()["capability_scope_notes"])
            self.assertEqual(rebuilt["row_classifications"], self.load()["row_classifications"])
            self.assertIn("Phoenix M7-qualified release rows: 12", md_out.read_text(encoding="utf-8"))

    def test_report_keeps_release_boundary_visible(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in [
            "not release authorization",
            "release_authorized: false",
            "public_speedup_claim_authorized: false",
            "broad_v3_faster_than_v2_claim_authorized: false",
            "Phoenix M7-qualified release rows: 12",
            "RayJoin author RT is faster than RTDL OptiX",
            "hot rows win, wall timing regresses",
            "5 original route-map rows (AABB, RTDBSCAN component_union, Triangle, Hausdorff threshold_summary, and Robot Collision collision_flag_stream) and 7 supplemental rows (grouped_sum plus AABB native query-handle plus RTNN prepared repeat50 plus Barnes-Hut fused partner rows)",
            "Supplemental Final Review Packets",
            "aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped",
            "claude_codex_consensus_complete_approve_one_row_scoped_m7_with_amendments",
            "None from current evidence. Reopen only after a generic-engine change.",
            "Optimization-Required Reopen Queue",
            "RT-native Barnes-Hut/vector accumulation remains future research",
            "component_union_clustered3d_65536_524288_repeat5_row_scoped",
            "claude_codex_m7_qualified_row_scoped",
            "collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped",
            "claude_approved_with_p1_amendments_resolved",
            "grouped_reduction_sum_scalar_broadcast_repeat100_262144",
            "grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups",
            "grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups",
            "claude_external_approve_with_required_fixes_p1_applied_2026-06-22",
            "claude_codex_consensus_complete_after_subagent_gap_supersession_2026-06-22",
            "aabb_candidate_stream_all_count_only_float32_32768",
            "aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50",
            "aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50",
            "claude_approve_with_conditions",
            "claude_codex_consensus_complete_approve_two_row_scoped_m7_rows",
            "rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02",
            "claude_codex_consensus_complete_approve_one_row_scoped_m7",
            "prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream",
            "hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped",
            "claude_reviewed_approved_with_amendments_2026-06-21",
            "claude_approved_after_p0_wording_fix",
            "claude_approved_after_p0_repair_and_scene_prepare_wording",
            "claude_codex_consensus_complete",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
