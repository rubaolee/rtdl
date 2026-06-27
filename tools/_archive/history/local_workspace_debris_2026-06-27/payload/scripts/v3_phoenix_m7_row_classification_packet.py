#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROUTE_MAP = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_p0_route_capability_map_2026-06-20.json"
DEFAULT_JSON_OUT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m7_row_classification_packet_2026-06-20.json"
DEFAULT_MD_OUT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m7_row_classification_packet_2026-06-20.md"

M4_INDEX = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_m4_grouped_continuation_20260620"
    / "phoenix_v3_m4_evidence_index_2026-06-20.json"
)
M5_INTAKE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_m5_topology_20260620"
    / "m5_topology_intake_summary.json"
)
M6_INTAKE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_m6_barnes_hut_20260620"
    / "m6_barnes_hut_intake_summary.json"
)
RAYDB_M28 = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_raydb_m28_grouped_reduction_20260620"
    / "m28_raydb_grouped_reduction_524288.json"
)
TRIANGLE_INTAKE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_triangle_prepared_graph_20260620"
    / "triangle_prepared_graph_intake_summary.json"
)
RTNN_INTAKE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_rtnn_ranked_summary_20260620"
    / "rtnn_ranked_summary_intake_summary.json"
)
GROUPED_SUM_262144_FINAL = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_grouped_reduction_sum_262144_m7_final_review_packet_2026-06-21.json"
)
GROUPED_DEVICE_COLUMN_FINAL = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.json"
)
AABB_32768_FINAL = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_candidate_stream_32768_m7_final_review_packet_2026-06-21.json"
)
AABB_NATIVE_QUERY_HANDLE_FINAL = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_native_query_handle_review_gate_2026-06-21.json"
)
RTNN_PREPARED_REPEAT50_FINAL = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_prepared_repeat50_review_gate_2026-06-21.json"
)
TRIANGLE_80000_FINAL = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_2026-06-21.json"
)
RTDBSCAN_COMPONENT_SIGNATURE_FINAL = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtdbscan_component_signature_optimized_rtx_evidence_2026-06-21.json"
)
HAUSDORFF_THRESHOLD_SUMMARY_FINAL = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_hausdorff_threshold_summary_repeat5_rtx_evidence_2026-06-21.json"
)
ROBOT_COLLISION_FLAG_STREAM_FINAL = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_robot_collision_flag_stream_no_probe_paired_rtx_evidence_2026-06-21.json"
)
BARNES_HUT_FUSED_PARTNER_CANDIDATE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_barnes_hut_fused_partner_m7_candidate_2026-06-21.json"
)
BARNES_HUT_FUSED_PARTNER_CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_barnes_hut_fused_partner_m7_candidate_review_2026-06-21.md"
)
BARNES_HUT_FUSED_PARTNER_CODEX_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_phoenix_v3_barnes_hut_fused_partner_m7_candidate_2ai_consensus_2026-06-21.md"
)
CONTACT_MANIFOLD_BOUNDARY = (
    "docs/rebuild/v3/phoenix_v3_contact_manifold_broadphase_boundary_2026-06-21.md"
)
CONTACT_MANIFOLD_EXTERNAL_REVIEW = (
    "docs/reviews/claude_phoenix_v3_contact_manifold_broadphase_boundary_review_2026-06-21.md"
)
CONTACT_MANIFOLD_CODEX_CONSENSUS = (
    "docs/reviews/codex_phoenix_v3_contact_manifold_broadphase_boundary_2ai_consensus_2026-06-21.md"
)


CAPABILITY_REVIEW_STATUS: dict[str, dict[str, Any]] = {
    "component_union": {
        "review_status": "claude_codex_m7_qualified_row_scoped",
        "goal4392_gate": "M4",
        "evidence_basis": "docs/rebuild/v3/phoenix_v3_rtdbscan_component_signature_optimized_rtx_evidence_2026-06-21.md",
        "external_review": "docs/reviews/claude_phoenix_v3_rtdbscan_component_signature_optimized_rtx_evidence_repeat5_final_review_2026-06-21.md",
        "codex_consensus": "docs/reviews/codex_phoenix_v3_rtdbscan_component_signature_optimized_rtx_evidence_2ai_consensus_2026-06-21.md",
        "accepted_internal_facts": (
            "The optimized same-contract component-signature route is 1.102x to 1.236x OptiX over Embree on 65,536 to 524,288 zero-noise clustered3d rows.",
            "The 262,144 and 524,288 rows were rerun at repeat=5/warmup=1 with four measured iterations.",
            "Large-row correctness is OptiX/Embree intra-run canonical component-signature agreement, not independent CPU reference validation.",
            "The Numba continuation still dominates at 262,144 and 524,288 points and must remain in public wording.",
        ),
        "m7_blockers": (
            "do_not_generalize_to_full_dbscan_rt_dbscan_paper_v2_or_noisy_datasets",
        ),
    },
    "grouped_reduction": {
        "review_status": "accepted_internal_grouped_reduction_not_m7",
        "goal4392_gate": "M4",
        "evidence_basis": "docs/rebuild/v3/phoenix_v3_raydb_m28_grouped_reduction_pod_evidence_2026-06-20.md",
        "external_review": "docs/reviews/claude_phoenix_v3_raydb_m28_grouped_reduction_evidence_review_2026-06-20.md",
        "codex_consensus": "docs/reviews/codex_phoenix_v3_raydb_m28_grouped_reduction_2ai_consensus_2026-06-20.md",
        "accepted_internal_facts": (
            "RayDB-style 524,288-row / 2,048-group count and sum rows match CPU reference.",
            "OptiX hot-query count and sum rows are faster than Embree under the same internal contract.",
        ),
        "m7_blockers": (
            "hot_query_only_not_end_to_end_application_timing",
            "sum_workload_build_and_cold_prepare_costs_exceed_213_seconds",
            "no_author_code_or_paper_dataset_comparison",
            "no_public_row_level_release_review",
        ),
    },
    "point_location_topology_stream": {
        "review_status": "accepted_internal_m5_author_complete_not_m7",
        "goal4392_gate": "M5",
        "evidence_basis": "docs/rebuild/v3/phoenix_v3_m5_topology_pod_evidence_2026-06-20.md",
        "external_review": "docs/reviews/claude_phoenix_v3_m5_author_recovery_review_2026-06-20.md",
        "codex_consensus": "docs/reviews/codex_phoenix_v3_m5_author_recovery_2ai_consensus_2026-06-20.md",
        "accepted_internal_facts": (
            "RTDL OptiX and Embree match on the backend-parity-filtered PIP point-location row.",
            "RayJoin author query_exec was recovered and measured.",
        ),
        "m7_blockers": (
            "rayjoin_author_rt_faster_than_rtdl_optix",
            "not_full_rayjoin_paper_reproduction",
            "mixed_timing_basis_requires_public_methodology_review",
            "no_public_row_level_release_review",
        ),
    },
    "prepared_graph_chunk": {
        "review_status": "accepted_internal_triangle_candidate_not_m7",
        "goal4392_gate": "M7",
        "evidence_basis": "docs/rebuild/v3/phoenix_v3_triangle_prepared_graph_intake_2026-06-20.md",
        "external_review": "docs/reviews/claude_phoenix_v3_triangle_prepared_graph_intake_review_2026-06-20.md",
        "codex_consensus": "docs/reviews/codex_phoenix_v3_triangle_prepared_graph_intake_2ai_consensus_2026-06-20.md",
        "accepted_internal_facts": (
            "20,000- and 80,000-clique synthetic RT-Graph 2A1 rows pass oracle and same-contract checks.",
            "OptiX hot-query rows are strongly faster than Embree; wall speedup is positive but smaller.",
        ),
        "m7_blockers": (
            "synthetic_k4_clique_ladder_not_paper_dataset",
            "not_graph_database_or_full_triangle_counting_app",
            "no_author_code_or_paper_dataset_comparison",
            "prepared_graph_chunk_executor_linkage_not_closed",
            "hot_query_vs_wall_timing_ratio_not_characterized_for_release",
            "public_row_level_external_review_not_done",
        ),
    },
    "ranked_summary": {
        "review_status": "accepted_internal_rtnn_candidate_not_m7",
        "goal4392_gate": "M7",
        "evidence_basis": "docs/rebuild/v3/phoenix_v3_rtnn_ranked_summary_intake_2026-06-20.md",
        "external_review": "docs/reviews/claude_phoenix_v3_rtnn_ranked_summary_intake_review_2026-06-20.md",
        "codex_consensus": "docs/reviews/codex_phoenix_v3_rtnn_ranked_summary_intake_2ai_consensus_2026-06-20.md",
        "accepted_internal_facts": (
            "65,536-point clustered, shell, and uniform ranked-summary rows match aggregate summaries.",
            "OptiX hot elapsed is faster than Embree for all three distributions.",
        ),
        "m7_blockers": (
            "wall_timing_optix_slower_than_embree_for_all_three_distributions",
            "distribution_specific_not_universal_rtnn_acceleration",
            "paper_equivalent_rtnn_row_false",
            "summary_rows_materialized",
            "no_author_code_or_external_ann_baseline_comparison",
            "no_multi_run_variance_evidence",
            "prepared_cuda_graph_replay_false",
            "public_row_level_external_review_not_done",
        ),
    },
    "aggregate_frontier": {
        "review_status": "accepted_internal_m6_route_parity_not_m7",
        "goal4392_gate": "M6",
        "evidence_basis": "docs/rebuild/v3/phoenix_v3_m6_barnes_hut_pod_evidence_2026-06-20.md",
        "external_review": "docs/reviews/claude_phoenix_v3_m6_barnes_hut_evidence_review_2026-06-20.md",
        "codex_consensus": "docs/reviews/codex_phoenix_v3_m6_barnes_hut_evidence_2ai_consensus_2026-06-20.md",
        "accepted_internal_facts": (
            "32,768 / 65,536 / 131,072-body route parity passes across four routes.",
            "Fused Numba CUDA is fastest on the current rerun; prepared OptiX is slower.",
        ),
        "m7_blockers": (
            "prepared_optix_not_fastest_route",
            "route_ratios_use_mixed_timing_basis",
            "not_full_exact_force_or_paper_reproduction",
            "fused_rt_native_weighted_vector_primitive_not_closed",
        ),
    },
    "vector_accumulation": {
        "review_status": "accepted_internal_m6_route_parity_not_m7",
        "goal4392_gate": "M6",
        "evidence_basis": "docs/rebuild/v3/phoenix_v3_m6_barnes_hut_pod_evidence_2026-06-20.md",
        "external_review": "docs/reviews/claude_phoenix_v3_m6_barnes_hut_evidence_review_2026-06-20.md",
        "codex_consensus": "docs/reviews/codex_phoenix_v3_m6_barnes_hut_evidence_2ai_consensus_2026-06-20.md",
        "accepted_internal_facts": (
            "Vector accumulation is exercised through the same M6 route-parity packet.",
        ),
        "m7_blockers": (
            "prepared_optix_not_fastest_route",
            "fused_vector_primitive_not_closed_as_app_agnostic_release_surface",
        ),
    },
    "threshold_summary": {
        "review_status": "claude_codex_large_row_m7_smaller_rows_blocked",
        "goal4392_gate": "M7",
        "evidence_basis": "docs/rebuild/v3/phoenix_v3_hausdorff_threshold_summary_repeat5_rtx_evidence_2026-06-21.md",
        "external_review": (
            "docs/reviews/claude_phoenix_v3_hausdorff_threshold_summary_repeat5_m7_review_2026-06-21.md",
            "docs/reviews/claude_phoenix_v3_hausdorff_threshold_summary_p0_repair_final_review_2026-06-21.md",
        ),
        "codex_consensus": "docs/reviews/codex_phoenix_v3_hausdorff_threshold_summary_p0_repair_2ai_consensus_2026-06-21.md",
        "accepted_internal_facts": (
            "The 262,144-copy / 1,048,576-points-per-side Hausdorff threshold-summary row matches the deterministic threshold oracle.",
            "The approved large row has five independent paired process samples with phase-total mean 1.240x and weakest phase-total 1.224x OptiX over Embree.",
            "The 16,384-copy and 65,536-copy rows remain blocked because they are not phase-total wins.",
        ),
        "m7_blockers": (
            "smaller_threshold_summary_rows_not_phase_total_wins",
            "do_not_generalize_to_full_hausdorff_xhd_v2_or_other_thresholds",
        ),
    },
    "collision_flag_stream": {
        "review_status": "claude_codex_m7_qualified_row_scoped",
        "goal4392_gate": "M7",
        "evidence_basis": "docs/rebuild/v3/phoenix_v3_robot_collision_flag_stream_no_probe_paired_rtx_evidence_2026-06-21.md",
        "external_review": "docs/reviews/claude_phoenix_v3_robot_collision_flag_stream_no_probe_paired_m7_review_2026-06-21.md",
        "codex_consensus": "docs/reviews/codex_phoenix_v3_robot_collision_flag_stream_no_probe_paired_2ai_consensus_2026-06-21.md",
        "accepted_internal_facts": (
            "The old validation-inclusive wall path was blocked because the CPU probe-reference oracle dominated timing.",
            "The repaired packet separates CPU probe-reference validation from no-probe performance timing.",
            "Five no-probe paired process samples all have wrapper speedup above 1x, with mean wrapper speedup 1.171x OptiX over Embree.",
            "The 5.086x tail and 5.075x total-run-window speedups are only prepared query execution phase metrics.",
        ),
        "m7_blockers": (
            "do_not_generalize_to_full_robot_planning_exact_or_continuous_collision_v2_or_zero_copy",
        ),
    },
}

UNFOCUSED_CAPABILITY_STATUS = {
    "aabb_candidate_stream": "candidate_from_all_app_route_map_needs_m7_packet",
    "collision_flag_stream": "candidate_from_all_app_route_map_needs_m7_packet",
    "compact_positive_stream": "candidate_from_all_app_route_map_needs_m7_packet",
    "device_ray_hit_stream": "internal_supporting_evidence_needs_public_contract",
    "threshold_summary": "candidate_from_all_app_route_map_needs_m7_packet",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Phoenix V3 M7 row classification packet.")
    parser.add_argument("--route-map", type=Path, default=DEFAULT_ROUTE_MAP)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    args = parser.parse_args()

    payload = build_payload(args.route_map)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(f"wrote {args.json_out}")
    print(f"wrote {args.md_out}")
    return 0


def build_payload(route_map_path: Path) -> dict[str, Any]:
    route_map = _read_json(route_map_path)
    focused = _focused_evidence()
    aabb_final = _read_json(AABB_32768_FINAL)
    triangle_final = _read_json(TRIANGLE_80000_FINAL)
    rtdbscan_final = _read_json(RTDBSCAN_COMPONENT_SIGNATURE_FINAL)
    hausdorff_final = _read_json(HAUSDORFF_THRESHOLD_SUMMARY_FINAL)
    collision_final = _read_json(ROBOT_COLLISION_FLAG_STREAM_FINAL)
    rows = [
        _classify_row(row, aabb_final, triangle_final, rtdbscan_final, hausdorff_final, collision_final)
        for row in route_map["rows"]
    ]
    capabilities = _capability_summaries(rows, focused)
    supplemental_packets = _post_classification_final_review_packets()
    m7_rows = [row for row in rows if row["m7_classification"] == "m7_qualified_release_row"]
    supplemental_m7_rows = sum(packet["classification_m7_contribution"] for packet in supplemental_packets)
    blocked_rows = [row for row in rows if row["m7_classification"] != "m7_qualified_release_row"]
    return {
        "version": "phoenix_v3_m7_row_classification_packet_2026_06_20",
        "status": "m7_classification_packet_not_release",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "phoenix_m7_qualified_release_rows": len(m7_rows) + supplemental_m7_rows,
        "source_route_map": _rel(route_map_path),
        "broad_v2_v3_denominator_rule": route_map["broad_v2_v3_denominator_rule"],
        "focused_evidence": focused,
        "capability_summaries": capabilities,
        "post_classification_final_review_packets": supplemental_packets,
        "capability_scope_notes": (
            {
                "capability": "vector_accumulation",
                "status": "covered_by_amended_fused_partner_m7_row_rt_native_future_research",
                "release_authorized": False,
                "public_speedup_claim_authorized": False,
                "note": (
                    "Claude and Codex now allow exactly one amended M7 milestone row for the generic "
                    "aggregate-tree fused weighted-vector Numba CUDA partner route. This covers the "
                    "aggregate_frontier/vector_accumulation breadth gap for the narrow row-scoped "
                    "partner contract only. It does not complete RT-native Barnes-Hut, RT-core acceleration, "
                    "whole-app Barnes-Hut, paper reproduction, broad V3-over-V2, or release readiness. "
                    "RT-native hierarchical traversal remains future research and still requires a reviewed "
                    "subtree-skip-preserving design before any RT-core wording."
                ),
            },
        ),
        "next_engine_work_queue": {
            "status": "generic_engine_work_queue_closed_not_release",
            "source": "docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md",
            "active_p0_ids": (),
            "future_research_ids": (
                "barnes_hut_vector_accumulation_frontier_shape",
                "spatial_rayjoin_topology_stream_author_gap",
            ),
            "closed_by_new_barnes_hut_partner_row": (
                "aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped"
            ),
        },
        "row_classifications": rows,
        "summary": {
            "row_count": len(rows),
            "apps_covered": len({row["app_id"] for row in rows}),
            "capability_count": len({row["generic_capability"] for row in rows}),
            "m7_qualified_release_rows": len(m7_rows) + supplemental_m7_rows,
            "route_map_m7_qualified_release_rows": len(m7_rows),
            "supplemental_m7_qualified_release_rows": supplemental_m7_rows,
            "blocked_or_internal_rows": len(blocked_rows),
            "p0_or_blocked_rows": len([row for row in rows if row["priority"].startswith("P0")]),
            "public_claim_rows": 0,
            "row_scoped_public_claim_rows": len(m7_rows) + supplemental_m7_rows,
            "release_authorized": False,
            "final_review_blocked_packets": len(
                [
                    packet
                    for packet in supplemental_packets
                    if packet["current_packet_external_review_status"] == "blocked_current_packet"
                ]
            ),
            "next_work": (
                "Do not promote more rows from old evidence. The aggregate_frontier/vector_accumulation "
                "breadth gap is now closed only for the amended Numba CUDA partner M7 milestone row. "
                "Spatial topology-stream remains future research, not current release scope. "
                "AABB native query-handle is now closed as two supplemental M7 rows, and RTNN "
                "prepared repeat50 is closed as one supplemental M7 row. "
                "RT-native Barnes-Hut/vector accumulation remains future research, not an active Phoenix P0."
            ),
        },
        "next_m7_promotion_candidates": (),
        "optimization_required_reopen_queue": (),
        "goal_level_decision_audit": {
            "decision": "count the two reviewed grouped-reduction device-column rows, the two reviewed AABB native-query-handle rows, the one reviewed RTNN prepared-repeat50 row, and the one reviewed Barnes-Hut fused-partner row as supplemental M7 rows while keeping the packet non-release",
            "was_i_foolish": "No. This updates the global row count only after external/2-AI review, P1 wording/provenance conditions, exact-row boundaries, and Claude's Barnes-Hut amendments.",
            "foolish_actions": (
                "It would be foolish to treat the new rows as a V3 release, call the Embree/device-column ratios pure backend-only, "
                "turn the 218.248x cold-prepare phase ratio into headline wording, present RTNN repeat50 as a one-shot nearest-neighbor win, "
                "or headline the Barnes-Hut 13.591x OptiX no-go comparison."
            ),
            "other_path": "Leave the rows pending after Claude approval. That would avoid changing the global count but would freeze reviewed generic-engine improvements.",
            "different_path_now": (
                "Regenerate classification/docs/tests, keep release authorization false, and leave Spatial topology-stream as the remaining breadth blocker."
            ),
        },
    }


def _post_classification_final_review_packets() -> tuple[dict[str, Any], ...]:
    grouped_sum = _read_json(GROUPED_SUM_262144_FINAL)
    grouped_device = _read_json(GROUPED_DEVICE_COLUMN_FINAL)
    aabb = _read_json(AABB_32768_FINAL)
    aabb_native = _read_json(AABB_NATIVE_QUERY_HANDLE_FINAL)
    rtnn_repeat50 = _read_json(RTNN_PREPARED_REPEAT50_FINAL)
    triangle = _read_json(TRIANGLE_80000_FINAL)
    hausdorff = _read_json(HAUSDORFF_THRESHOLD_SUMMARY_FINAL)
    collision = _read_json(ROBOT_COLLISION_FLAG_STREAM_FINAL)
    barnes_hut_fused = _read_json(BARNES_HUT_FUSED_PARTNER_CANDIDATE)
    grouped_row = grouped_sum["candidate_row"]
    aabb_row = aabb["candidate_row"]
    hausdorff_row = next(row for row in hausdorff["pairs"] if row.get("m7_candidate"))
    barnes_hut_fused_131072 = barnes_hut_fused["large_same_basis_summary"]["candidate_131072"]
    return (
        {
            "packet": _rel(GROUPED_SUM_262144_FINAL),
            "classification_counting_basis": "supplemental_new_row",
            "classification_m7_contribution": grouped_sum["m7_qualified_release_rows"],
            "status": grouped_sum["status"],
            "generic_capability": grouped_sum["generic_capability"],
            "candidate_row_id": grouped_sum["candidate_row_id"],
            "local_evidence_sufficient_for_external_public_row_review": grouped_sum[
                "local_evidence_sufficient_for_external_public_row_review"
            ],
            "row_scoped_public_speedup_claim_authorized": grouped_sum[
                "row_scoped_public_speedup_claim_authorized"
            ],
            "local_gate_reading": grouped_row["local_gate_reading"],
            "current_packet_external_review_status": grouped_sum["current_packet_external_review_status"],
            "current_packet_2ai_consensus_status": grouped_sum["current_packet_2ai_consensus_status"],
            "external_review": grouped_sum["external_review"],
            "codex_consensus": grouped_sum["codex_consensus"],
            "previous_external_review_blockage": grouped_sum["previous_external_review_blockage"],
            "m7_qualified_release_rows": grouped_sum["m7_qualified_release_rows"],
            "actual_repeat100_loop_speedup": grouped_row["actual_repeat100_loop_speedup"],
            "actual_repeat100_cold_plus_loop_speedup": grouped_row["actual_repeat100_cold_plus_loop_speedup"],
            "excluded_row_count": len(grouped_sum["excluded_rows"]),
            "source_provenance_basis": grouped_sum["source_provenance"]["traceability_basis"],
        },
        {
            "packet": _rel(GROUPED_DEVICE_COLUMN_FINAL),
            "classification_counting_basis": grouped_device["classification_counting_basis"],
            "classification_m7_contribution": grouped_device["m7_qualified_release_rows"],
            "status": grouped_device["status"],
            "generic_capability": grouped_device["generic_capability"],
            "candidate_row_id": "; ".join(row["row_id"] for row in grouped_device["candidate_rows"]),
            "candidate_row_ids": [row["row_id"] for row in grouped_device["candidate_rows"]],
            "local_evidence_sufficient_for_external_public_row_review": grouped_device[
                "local_evidence_sufficient_for_external_public_row_review"
            ],
            "row_scoped_public_speedup_claim_authorized": grouped_device[
                "row_scoped_public_speedup_claim_authorized"
            ],
            "local_gate_reading": grouped_device["candidate_rows"][0]["local_gate_reading"],
            "current_packet_external_review_status": grouped_device["current_packet_external_review_status"],
            "current_packet_2ai_consensus_status": grouped_device["current_packet_2ai_consensus_status"],
            "external_review": grouped_device["external_review"],
            "codex_consensus": grouped_device["codex_consensus"],
            "external_ai_blocked_note": grouped_device["external_ai_blocked_note"],
            "m7_qualified_release_rows": grouped_device["m7_qualified_release_rows"],
            "min_host_packed_over_device_columns_cold_plus_loop_speedup": grouped_device["summary"][
                "min_host_packed_over_device_columns_cold_plus_loop_speedup"
            ],
            "max_host_packed_over_device_columns_cold_plus_loop_speedup": grouped_device["summary"][
                "max_host_packed_over_device_columns_cold_plus_loop_speedup"
            ],
            "min_embree_over_optix_device_columns_cold_plus_loop_speedup": grouped_device["summary"][
                "min_embree_over_optix_device_columns_cold_plus_loop_speedup"
            ],
            "all_cpu_reference_match": grouped_device["summary"]["all_cpu_reference_match"],
            "all_device_routes_remove_host_packed_rays": grouped_device["summary"][
                "all_device_routes_remove_host_packed_rays"
            ],
            "p1_review_fixes_applied": grouped_device["p1_review_fixes_applied"],
            "source_manifest_path": grouped_device["source_provenance"]["source_manifest_path"],
        },
        {
            "packet": _rel(AABB_32768_FINAL),
            "classification_counting_basis": "route_map_row_promoted",
            "classification_m7_contribution": 0,
            "status": aabb["status"],
            "generic_capability": aabb["generic_capability"],
            "candidate_row_id": aabb["candidate_row_id"],
            "local_evidence_sufficient_for_external_public_row_review": aabb[
                "local_evidence_sufficient_for_external_public_row_review"
            ],
            "row_scoped_public_speedup_claim_authorized": aabb[
                "row_scoped_public_speedup_claim_authorized"
            ],
            "local_gate_reading": aabb_row["local_gate_reading"],
            "current_packet_external_review_status": aabb["current_packet_external_review_status"],
            "current_packet_2ai_consensus_status": aabb["current_packet_2ai_consensus_status"],
            "external_review": aabb["external_review"],
            "codex_consensus": aabb["codex_consensus"],
            "m7_qualified_release_rows": aabb["m7_qualified_release_rows"],
            "numeric_contract": aabb_row["numeric_contract"],
            "query_optix_over_embree": aabb_row["query_optix_over_embree"],
            "wall_optix_over_embree": aabb_row["wall_optix_over_embree"],
            "elapsed_optix_over_embree": aabb_row["elapsed_optix_over_embree"],
            "matches_float32_cpu_reference": aabb_row["matches_float32_cpu_reference"],
            "matches_float64_cpu_reference": aabb_row["matches_float64_cpu_reference"],
        },
        {
            "packet": _rel(AABB_NATIVE_QUERY_HANDLE_FINAL),
            "classification_counting_basis": "supplemental_new_rows_after_claude_codex_consensus",
            "classification_m7_contribution": aabb_native["m7_qualified_release_rows_added"],
            "status": aabb_native["status"],
            "generic_capability": aabb_native["generic_capability"],
            "candidate_row_id": "; ".join(aabb_native["stable_candidate_row_ids"]),
            "candidate_row_ids": aabb_native["stable_candidate_row_ids"],
            "local_evidence_sufficient_for_external_public_row_review": True,
            "row_scoped_public_speedup_claim_authorized": aabb_native[
                "row_scoped_public_speedup_claim_authorized"
            ],
            "local_gate_reading": "m7_qualified_row_scoped_after_claude_codex_consensus",
            "current_packet_external_review_status": aabb_native["external_review_status"],
            "current_packet_2ai_consensus_status": "claude_codex_consensus_complete_approve_two_row_scoped_m7_rows",
            "external_review": aabb_native["review_records"]["claude_final_review"],
            "codex_consensus": aabb_native["review_records"]["codex_final_consensus"],
            "m7_qualified_release_rows": aabb_native["m7_qualified_release_rows_added"],
            "best_cold_plus_collect_wall_speedup": aabb_native["material_signal_preserved"][
                "best_cold_plus_collect_wall_speedup"
            ],
            "weakest_cold_plus_collect_wall_speedup": aabb_native["material_signal_preserved"][
                "weakest_cold_plus_collect_wall_speedup"
            ],
            "source_manifest_provenance_sha256": aabb_native["source_manifest_provenance_sha256"],
            "p1_promotion_record_requirements": aabb_native["p1_promotion_record_requirements"],
            "approved_row_scoped_public_wording": aabb_native["approved_row_scoped_public_wording"],
            "forbidden_public_wording": aabb_native["forbidden_public_wording"],
            "release_authorized": aabb_native["release_authorized"],
            "broad_v3_faster_than_v2_claim_authorized": aabb_native[
                "broad_v3_faster_than_v2_claim_authorized"
            ],
        },
        {
            "packet": _rel(RTNN_PREPARED_REPEAT50_FINAL),
            "classification_counting_basis": "supplemental_new_row_after_claude_codex_consensus",
            "classification_m7_contribution": rtnn_repeat50["m7_qualified_release_rows_added"],
            "status": rtnn_repeat50["status"],
            "generic_capability": rtnn_repeat50["generic_capability"],
            "candidate_row_id": rtnn_repeat50["candidate_row"]["row_id"],
            "candidate_row_ids": rtnn_repeat50["candidate_row_ids"],
            "local_evidence_sufficient_for_external_public_row_review": True,
            "row_scoped_public_speedup_claim_authorized": rtnn_repeat50[
                "row_scoped_public_speedup_claim_authorized"
            ],
            "local_gate_reading": "m7_qualified_row_scoped_after_claude_codex_consensus",
            "current_packet_external_review_status": rtnn_repeat50["external_review_status"],
            "current_packet_2ai_consensus_status": rtnn_repeat50[
                "current_packet_2ai_consensus_status"
            ],
            "external_review": rtnn_repeat50["review_records"]["claude_external_review"],
            "codex_consensus": rtnn_repeat50["review_records"]["codex_consensus"],
            "m7_qualified_release_rows": rtnn_repeat50["m7_qualified_release_rows_added"],
            "hot_query_speedup": rtnn_repeat50["candidate_row"]["hot_query_speedup"],
            "cold_plus_query_speedup": rtnn_repeat50["candidate_row"]["cold_plus_query_speedup"],
            "runner_wall_speedup": rtnn_repeat50["candidate_row"]["runner_wall_speedup"],
            "precision_disclosure": rtnn_repeat50["candidate_row"]["precision_disclosure"],
            "source_manifest_path": rtnn_repeat50["candidate_row"]["source_manifest_path"],
            "approved_row_scoped_public_wording": rtnn_repeat50["candidate_row"][
                "approved_row_scoped_public_wording"
            ],
            "forbidden_public_wording": rtnn_repeat50["forbidden_public_wording"],
            "release_authorized": rtnn_repeat50["release_authorized"],
            "whole_rtnn_claim_authorized": rtnn_repeat50["whole_rtnn_claim_authorized"],
            "one_shot_rtnn_claim_authorized": rtnn_repeat50["one_shot_rtnn_claim_authorized"],
            "broad_v3_faster_than_v2_claim_authorized": rtnn_repeat50[
                "broad_v3_faster_than_v2_claim_authorized"
            ],
        },
        {
            "packet": _rel(BARNES_HUT_FUSED_PARTNER_CANDIDATE),
            "classification_counting_basis": "supplemental_new_row_after_claude_approve_with_amendments",
            "classification_m7_contribution": 1,
            "status": "aggregate_tree_fused_partner_m7_qualified_row_scoped_after_claude_amendments",
            "generic_capability": "aggregate_frontier",
            "refined_generic_capability": "vector_accumulation",
            "candidate_row_id": barnes_hut_fused["candidate_row_id"],
            "candidate_row_ids": [barnes_hut_fused["candidate_row_id"]],
            "contract": barnes_hut_fused["contract"],
            "local_evidence_sufficient_for_external_public_row_review": True,
            "row_scoped_public_speedup_claim_authorized": True,
            "public_speedup_claim_authorized": False,
            "release_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "local_gate_reading": "m7_qualified_row_scoped_after_claude_amendments_and_codex_consensus",
            "current_packet_external_review_status": "claude_approve_with_amendments",
            "current_packet_2ai_consensus_status": (
                "claude_codex_consensus_complete_approve_one_row_scoped_m7_with_amendments"
            ),
            "external_review": _rel(BARNES_HUT_FUSED_PARTNER_CLAUDE_REVIEW),
            "codex_consensus": _rel(BARNES_HUT_FUSED_PARTNER_CODEX_CONSENSUS),
            "m7_qualified_release_rows": 1,
            "evidence_tree_structure": "barnes_hut_theta_0.5_2d_bucketized",
            "large_scale_validation_tier": "route_parity_plus_checksum_no_independent_oracle",
            "evidence_source_artifact": barnes_hut_fused["source_packets"]["large_rerank"],
            "body_count": barnes_hut_fused_131072["body_count"],
            "candidate_wall_repeat_ms": barnes_hut_fused_131072["candidate_wall_repeat_ms"],
            "repeat": 11,
            "warmup": 3,
            "cpu_numba_fused_over_candidate": barnes_hut_fused_131072[
                "cpu_numba_fused_over_candidate"
            ],
            "prepared_optix_numba_over_candidate_supplemental_not_primary": barnes_hut_fused_131072[
                "prepared_optix_numba_over_candidate"
            ],
            "independent_exact_force_cpu_oracle_at_scale_claimed": False,
            "approved_row_scoped_public_wording": (
                "Generic aggregate-tree fused weighted-vector sum, Numba CUDA partner "
                "(`generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1`): "
                "at 131,072 bodies on a Barnes-Hut tree (theta=0.5, 2D), 45.493 ms "
                "wall-repeat median (r=11, warmup=3), 4.082x faster than CPU/Numba "
                "fused baseline. Not an RT-core claim. Large-scale validation: route "
                "parity plus checksum across three scales; independent exact-force CPU "
                "oracle not claimed at this scale."
            ),
            "supporting_metadata_only": {
                "prepared_optix_frontier_emission_route_status": "no_go",
                "prepared_optix_numba_over_candidate": barnes_hut_fused_131072[
                    "prepared_optix_numba_over_candidate"
                ],
            },
            "amendments_applied": [
                "evidence_tree_structure",
                "large_scale_validation_tier",
                "primary_wording_uses_cpu_numba_fused_comparison",
                "prepared_optix_ratio_supporting_metadata_only",
                "evidence_source_artifact_pinned",
            ],
            "forbidden_public_wording": [
                "RT-core acceleration",
                "whole Barnes-Hut application speedup",
                "broad V3-over-V2 speedup",
                "paper reproduction",
                "13.591x over OptiX as the primary claim",
            ],
        },
        {
            "packet": _rel(TRIANGLE_80000_FINAL),
            "classification_counting_basis": "route_map_row_promoted",
            "classification_m7_contribution": 0,
            "status": triangle["status"],
            "generic_capability": triangle["generic_capability"],
            "candidate_row_id": triangle["candidate_row_id"],
            "local_evidence_sufficient_for_external_public_row_review": triangle[
                "local_evidence_sufficient_for_external_public_row_review"
            ],
            "row_scoped_public_speedup_claim_authorized": triangle[
                "row_scoped_public_speedup_claim_authorized"
            ],
            "local_gate_reading": "m7_qualified_row_scoped_after_claude_refresh_and_codex_consensus",
            "current_packet_external_review_status": triangle["current_packet_external_review_status"],
            "current_packet_2ai_consensus_status": triangle["current_packet_2ai_consensus_status"],
            "external_review": triangle.get("claude_review", triangle["external_review"]),
            "superseded_fallback_review": triangle["external_review"],
            "codex_consensus": triangle["codex_consensus"],
            "m7_qualified_release_rows": triangle["m7_qualified_release_rows"],
            "hot_optix_over_embree": triangle["row"]["hot_optix_over_embree"],
            "wall_optix_over_embree": triangle["row"]["wall_optix_over_embree"],
            "m113_graph_capture_claim_authorized": triangle["m113_graph_capture_claim_authorized"],
            "supporting_row_promoted": False,
        },
        {
            "packet": _rel(HAUSDORFF_THRESHOLD_SUMMARY_FINAL),
            "classification_counting_basis": "route_map_row_promoted",
            "classification_m7_contribution": 0,
            "status": hausdorff["status"],
            "generic_capability": hausdorff["generic_capability"],
            "candidate_row_id": hausdorff["candidate_row_id"],
            "local_evidence_sufficient_for_external_public_row_review": hausdorff[
                "local_evidence_sufficient_for_external_public_row_review"
            ],
            "row_scoped_public_speedup_claim_authorized": hausdorff[
                "row_scoped_public_speedup_claim_authorized"
            ],
            "local_gate_reading": "m7_qualified_row_scoped_after_p0_repair_and_claude_codex_consensus",
            "current_packet_external_review_status": hausdorff["current_packet_external_review_status"],
            "current_packet_2ai_consensus_status": hausdorff["current_packet_2ai_consensus_status"],
            "external_review": hausdorff["external_review"],
            "codex_consensus": hausdorff["codex_consensus"],
            "m7_qualified_release_rows": hausdorff["m7_qualified_release_rows"],
            "query_ratio_mean": hausdorff_row["stability_repair"]["query_ratio_mean"],
            "phase_total_ratio_mean": hausdorff_row["stability_repair"]["phase_total_ratio_mean"],
            "weakest_phase_total_optix_speedup_vs_embree": hausdorff_row["stability_repair"][
                "weakest_phase_total_optix_speedup_vs_embree"
            ],
            "phase_total_includes_scene_preparation": True,
            "threshold": hausdorff_row["threshold"],
            "point_count_per_side": hausdorff_row["point_count_a"],
        },
        {
            "packet": _rel(ROBOT_COLLISION_FLAG_STREAM_FINAL),
            "classification_counting_basis": "route_map_row_promoted",
            "classification_m7_contribution": 0,
            "status": collision["status"],
            "generic_capability": collision["generic_capability"],
            "candidate_row_id": collision["candidate_row_id"],
            "local_evidence_sufficient_for_external_public_row_review": collision["gate_reading"][
                "local_evidence_sufficient_for_external_public_row_review"
            ],
            "row_scoped_public_speedup_claim_authorized": collision[
                "row_scoped_public_speedup_claim_authorized"
            ],
            "local_gate_reading": "m7_qualified_row_scoped_after_claude_p1_amendments_and_codex_consensus",
            "current_packet_external_review_status": collision["gate_reading"][
                "current_packet_external_review_status"
            ],
            "current_packet_2ai_consensus_status": collision["gate_reading"][
                "current_packet_2ai_consensus_status"
            ],
            "external_review": "docs/reviews/claude_phoenix_v3_robot_collision_flag_stream_no_probe_paired_m7_review_2026-06-21.md",
            "codex_consensus": "docs/reviews/codex_phoenix_v3_robot_collision_flag_stream_no_probe_paired_2ai_consensus_2026-06-21.md",
            "m7_qualified_release_rows": 1,
            "tail_total_run_optix_speedup_vs_embree_mean": collision["aggregate_ratios"][
                "tail_total_run_optix_speedup_vs_embree_mean"
            ],
            "total_run_window_optix_speedup_vs_embree_mean": collision["aggregate_ratios"][
                "total_run_window_optix_speedup_vs_embree_mean"
            ],
            "wrapper_no_probe_optix_speedup_vs_embree_mean": collision["aggregate_ratios"][
                "wrapper_no_probe_optix_speedup_vs_embree_mean"
            ],
            "weakest_wrapper_no_probe_optix_speedup_vs_embree": collision["aggregate_ratios"][
                "wrapper_no_probe_optix_speedup_vs_embree_min"
            ],
        },
    )


def _classify_row(
    row: dict[str, Any],
    aabb_final: dict[str, Any],
    triangle_final: dict[str, Any],
    rtdbscan_final: dict[str, Any],
    hausdorff_final: dict[str, Any],
    collision_final: dict[str, Any],
) -> dict[str, Any]:
    capability = row["generic_capability"]
    if _is_rtdbscan_component_union_m7_row(row, rtdbscan_final):
        summary = rtdbscan_final["summary"]
        return {
            "app_id": row["app_id"],
            "comparison_group": row["comparison_group"],
            "priority": row["priority"],
            "goal4392_gate": row["goal4392_gate"],
            "generic_capability": capability,
            "review_status": "claude_codex_m7_qualified_row_scoped",
            "route_map_release_evidence_status": "m7_qualified_after_repeat5_final_review",
            "m7_classification": "m7_qualified_release_row",
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "row_scoped_public_speedup_claim_authorized": True,
            "m7_promotion_authorized": True,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "optix_speedup_vs_embree": summary["weakest_serious_optix_speedup_vs_embree"],
            "speedup_floor": summary["weakest_serious_optix_speedup_vs_embree"],
            "speedup_ceiling": summary["strongest_serious_optix_speedup_vs_embree"],
            "v2_14_vs_v3_app_geomean": row["v2_14_vs_v3_app_geomean"],
            "evidence_basis": "docs/rebuild/v3/phoenix_v3_rtdbscan_component_signature_optimized_rtx_evidence_2026-06-21.md",
            "external_review": rtdbscan_final["external_review"],
            "codex_consensus": rtdbscan_final["codex_consensus"],
            "accepted_internal_facts": [
                "Claude approved the Option B repeat=5 repair for the 262,144 and 524,288 point rows.",
                "The approved row is 1.102x to 1.236x faster end-to-end than same-contract Embree on zero-noise four-cluster synthetic clustered3d rows.",
                "Large-scale correctness is OptiX/Embree intra-run canonical component-signature agreement, not independent CPU reference validation.",
                "The Numba continuation dominates at 262,144 and 524,288 points and must remain in the wording.",
            ],
            "m7_blockers": [],
            "allowed_internal_reading": rtdbscan_final["candidate_row_scoped_wording"],
            "forbidden_public_reading": (
                "Do not generalize this exact row to V3 release evidence, broad V3-over-V2 evidence, "
                "whole-application speedup evidence, RTDBSCAN paper evidence, full DBSCAN acceleration, "
                "noisy or irregular-cluster datasets, other hardware, or routes beyond component-signature continuation."
            ),
            "candidate_row_id": "component_union_clustered3d_65536_524288_repeat5_row_scoped",
            "large_scale_correctness_basis": summary["large_scale_correctness_basis"],
        }
    if _is_aabb_m7_row(row, aabb_final):
        aabb_row = aabb_final["candidate_row"]
        return {
            "app_id": row["app_id"],
            "comparison_group": row["comparison_group"],
            "priority": row["priority"],
            "goal4392_gate": row["goal4392_gate"],
            "generic_capability": capability,
            "review_status": "claude_codex_m7_qualified_row_scoped",
            "route_map_release_evidence_status": "m7_qualified_after_final_review",
            "m7_classification": "m7_qualified_release_row",
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "row_scoped_public_speedup_claim_authorized": True,
            "m7_promotion_authorized": True,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "optix_speedup_vs_embree": row["optix_speedup_vs_embree"],
            "v2_14_vs_v3_app_geomean": row["v2_14_vs_v3_app_geomean"],
            "evidence_basis": _rel(AABB_32768_FINAL),
            "external_review": aabb_final["external_review"],
            "codex_consensus": aabb_final["codex_consensus"],
            "accepted_internal_facts": [
                "RTDL Embree, RTDL OptiX, and an independent chunked NumPy float32 CPU oracle match counts.",
                "Claude accepted the native float32-inclusive numeric contract after the P0 wording fix.",
            ],
            "m7_blockers": [],
            "allowed_internal_reading": aabb_final["approved_row_scoped_public_wording"],
            "forbidden_public_reading": (
                "Do not generalize this exact row to V3 release evidence, broad V3-over-V2 evidence, "
                "whole-application speedup evidence, LibRTS paper/authors-code evidence, full spatial-index "
                "acceleration, or float64 exact-geometry evidence."
            ),
            "candidate_row_id": aabb_final["candidate_row_id"],
            "numeric_contract": aabb_row["numeric_contract"],
            "query_optix_over_embree": aabb_row["query_optix_over_embree"],
            "wall_optix_over_embree": aabb_row["wall_optix_over_embree"],
            "elapsed_optix_over_embree": aabb_row["elapsed_optix_over_embree"],
        }
    if _is_triangle_m7_row(row, triangle_final):
        triangle_row = triangle_final["row"]
        return {
            "app_id": row["app_id"],
            "comparison_group": row["comparison_group"],
            "priority": row["priority"],
            "goal4392_gate": row["goal4392_gate"],
            "generic_capability": capability,
            "review_status": "claude_codex_m7_qualified_row_scoped",
            "route_map_release_evidence_status": "m7_qualified_after_final_review",
            "m7_classification": "m7_qualified_release_row",
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "row_scoped_public_speedup_claim_authorized": True,
            "m7_promotion_authorized": True,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "optix_speedup_vs_embree": row["optix_speedup_vs_embree"],
            "v2_14_vs_v3_app_geomean": row["v2_14_vs_v3_app_geomean"],
            "evidence_basis": _rel(TRIANGLE_80000_FINAL),
            "external_review": triangle_final.get("claude_review", triangle_final["external_review"]),
            "codex_consensus": triangle_final["codex_consensus"],
            "superseded_fallback_review": triangle_final["external_review"],
            "accepted_internal_facts": [
                "Both routes match the 320,000-triangle oracle under the same RT-Graph 2A1 weighted-any-hit contract.",
                "Claude external refresh review found no evidence P0 and required P1 review-status fixes that are applied.",
            ],
            "m7_blockers": [],
            "allowed_internal_reading": triangle_final["draft_row_scoped_public_wording"],
            "forbidden_public_reading": (
                "Do not generalize this exact row to V3 release evidence, broad V3-over-V2 evidence, "
                "whole-application speedup evidence, RT-Graph paper evidence, graph database acceleration, "
                "M113 graph-capture readiness, automatic partner selection, or other Triangle rows."
            ),
            "candidate_row_id": triangle_final["candidate_row_id"],
            "hot_optix_over_embree": triangle_row["hot_optix_over_embree"],
            "wall_optix_over_embree": triangle_row["wall_optix_over_embree"],
            "oracle_triangle_count": triangle_row["oracle_triangle_count"],
            "m113_graph_capture_claim_authorized": triangle_final["m113_graph_capture_claim_authorized"],
        }
    if _is_hausdorff_threshold_summary_m7_row(row, hausdorff_final):
        hausdorff_row = next(item for item in hausdorff_final["pairs"] if item.get("m7_candidate"))
        stability = hausdorff_row["stability_repair"]
        return {
            "app_id": row["app_id"],
            "comparison_group": row["comparison_group"],
            "priority": row["priority"],
            "goal4392_gate": row["goal4392_gate"],
            "generic_capability": capability,
            "review_status": "claude_codex_m7_qualified_row_scoped",
            "route_map_release_evidence_status": "m7_qualified_after_p0_repair_final_review",
            "m7_classification": "m7_qualified_release_row",
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "row_scoped_public_speedup_claim_authorized": True,
            "m7_promotion_authorized": True,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "optix_speedup_vs_embree": stability["phase_total_ratio_mean"],
            "query_ratio_mean": stability["query_ratio_mean"],
            "phase_total_ratio_mean": stability["phase_total_ratio_mean"],
            "weakest_phase_total_optix_speedup_vs_embree": stability[
                "weakest_phase_total_optix_speedup_vs_embree"
            ],
            "phase_total_includes_scene_preparation": True,
            "v2_14_vs_v3_app_geomean": row["v2_14_vs_v3_app_geomean"],
            "evidence_basis": "docs/rebuild/v3/phoenix_v3_hausdorff_threshold_summary_repeat5_rtx_evidence_2026-06-21.md",
            "external_review": hausdorff_final["external_review"],
            "codex_consensus": hausdorff_final["codex_consensus"],
            "accepted_internal_facts": [
                "Claude closed both P0s after a five-sample independent paired process stability rerun and an explicit oracle definition.",
                "All five large-row phase-total paired samples are above 1x, with weakest phase-total 1.224x OptiX over Embree.",
                "The approved wording discloses that phase-total includes scene preparation.",
                "Smaller threshold-summary rows remain blocked because they are query wins but not phase-total wins.",
            ],
            "m7_blockers": [],
            "allowed_internal_reading": hausdorff_final["approved_row_scoped_public_wording"],
            "forbidden_public_reading": (
                "Do not generalize this exact row to V3 release evidence, broad V3-over-V2 evidence, "
                "whole-application speedup evidence, X-HD paper evidence, full Hausdorff distance or witness "
                "materialization, other thresholds, other sizes, other GPUs, or routes beyond threshold-summary."
            ),
            "candidate_row_id": hausdorff_final["candidate_row_id"],
            "threshold": hausdorff_row["threshold"],
            "point_count_per_side": hausdorff_row["point_count_a"],
            "oracle_definition": hausdorff_final["oracle_definition"],
        }
    if _is_robot_collision_flag_stream_m7_row(row, collision_final):
        ratios = collision_final["aggregate_ratios"]
        return {
            "app_id": row["app_id"],
            "comparison_group": row["comparison_group"],
            "priority": row["priority"],
            "goal4392_gate": row["goal4392_gate"],
            "generic_capability": capability,
            "review_status": "claude_codex_m7_qualified_row_scoped",
            "route_map_release_evidence_status": "m7_qualified_after_no_probe_paired_review",
            "m7_classification": "m7_qualified_release_row",
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "row_scoped_public_speedup_claim_authorized": True,
            "m7_promotion_authorized": True,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "optix_speedup_vs_embree": ratios["wrapper_no_probe_optix_speedup_vs_embree_mean"],
            "tail_total_run_optix_speedup_vs_embree_mean": ratios[
                "tail_total_run_optix_speedup_vs_embree_mean"
            ],
            "total_run_window_optix_speedup_vs_embree_mean": ratios[
                "total_run_window_optix_speedup_vs_embree_mean"
            ],
            "wrapper_no_probe_optix_speedup_vs_embree_mean": ratios[
                "wrapper_no_probe_optix_speedup_vs_embree_mean"
            ],
            "weakest_wrapper_no_probe_optix_speedup_vs_embree": ratios[
                "wrapper_no_probe_optix_speedup_vs_embree_min"
            ],
            "v2_14_vs_v3_app_geomean": row["v2_14_vs_v3_app_geomean"],
            "evidence_basis": _rel(ROBOT_COLLISION_FLAG_STREAM_FINAL),
            "external_review": "docs/reviews/claude_phoenix_v3_robot_collision_flag_stream_no_probe_paired_m7_review_2026-06-21.md",
            "codex_consensus": "docs/reviews/codex_phoenix_v3_robot_collision_flag_stream_no_probe_paired_2ai_consensus_2026-06-21.md",
            "accepted_internal_facts": [
                "Claude accepted separating CPU probe-reference validation from no-probe performance timing for row-scoped M7.",
                "All five no-probe paired process samples have wrapper speedup above 1x, with mean 1.171x OptiX over Embree.",
                "The 5.086x tail and 5.075x total-run-window metrics are prepared query execution phase metrics only.",
                "The wrapper metric is the conservative process-level bound excluding only the CPU probe-reference oracle.",
            ],
            "m7_blockers": [],
            "allowed_internal_reading": collision_final["allowed_wording"],
            "forbidden_public_reading": (
                "Do not generalize this exact row to V3 release evidence, broad V3-over-V2 evidence, "
                "whole-application speedup evidence, full robot planning, exact solid collision, continuous "
                "collision, zero-copy, or 5x end-to-end prepared setup speedup."
            ),
            "candidate_row_id": collision_final["candidate_row_id"],
            "shape": collision_final["shape"],
            "validation_protocol": collision_final["validation_protocol"],
            "timing_protocol": collision_final["timing_protocol"],
        }
    status = CAPABILITY_REVIEW_STATUS.get(capability)
    if status is None:
        if _is_contact_manifold_boundary_row(row):
            status = {
                "review_status": "focused_boundary_wall_regression_not_m7",
                "goal4392_gate": row["goal4392_gate"],
                "evidence_basis": CONTACT_MANIFOLD_BOUNDARY,
                "external_review": CONTACT_MANIFOLD_EXTERNAL_REVIEW,
                "codex_consensus": CONTACT_MANIFOLD_CODEX_CONSENSUS,
                "accepted_internal_facts": (
                    "The contact broadphase row matches CPU reference and accepts the v2.4 phase contract.",
                    "The query metric is 1.235x and collect-k is 2.759x OptiX over Embree.",
                    "The wall OptiX-over-Embree ratio is 0.803x, so OptiX is slower on the current wall path.",
                ),
                "m7_blockers": (
                    "wall_timing_optix_slower_than_embree",
                    "full_contact_solver_not_claimed",
                    "optix_prepare_aabb_index_cost_offsets_hot_query_gain",
                    "future_public_row_review_required_before_m7",
                ),
            }
        else:
            status = {
                "review_status": UNFOCUSED_CAPABILITY_STATUS.get(capability, "candidate_needs_m7_packet"),
                "goal4392_gate": row["goal4392_gate"],
                "evidence_basis": "docs/rebuild/v3/phoenix_v3_p0_route_capability_map_2026-06-20.json",
                "accepted_internal_facts": (
                    "Present in the all-app calibrated route map as row-scoped candidate evidence.",
                ),
                "m7_blockers": (
                    "no_focused_m7_packet",
                    "no_public_row_level_external_review",
                    "not_whole_app_or_paper_reproduction",
                ),
            }
    blockers = list(status["m7_blockers"])
    if row["release_evidence_status"] == "blocked_by_paired_regression":
        blockers.append("paired_v2_14_vs_v3_regression_or_route_loss")
    return {
        "app_id": row["app_id"],
        "comparison_group": row["comparison_group"],
        "priority": row["priority"],
        "goal4392_gate": row["goal4392_gate"],
        "generic_capability": capability,
        "review_status": status["review_status"],
        "route_map_release_evidence_status": row["release_evidence_status"],
        "m7_classification": "not_m7_qualified",
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "row_scoped_public_speedup_claim_authorized": False,
        "m7_promotion_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "optix_speedup_vs_embree": row["optix_speedup_vs_embree"],
        "v2_14_vs_v3_app_geomean": row["v2_14_vs_v3_app_geomean"],
        "evidence_basis": status["evidence_basis"],
        "accepted_internal_facts": list(status["accepted_internal_facts"]),
        "m7_blockers": blockers,
        "allowed_internal_reading": row["claim_boundary"],
        "forbidden_public_reading": (
            "Do not use this row as V3 release evidence, broad V3-over-V2 evidence, "
            "whole-application speedup evidence, or paper-reproduction evidence."
        ),
    }


def _capability_summaries(rows: list[dict[str, Any]], focused: dict[str, Any]) -> list[dict[str, Any]]:
    summaries = []
    for capability in sorted({row["generic_capability"] for row in rows}):
        status = CAPABILITY_REVIEW_STATUS.get(capability)
        row_count = len([row for row in rows if row["generic_capability"] == capability])
        m7_count = len(
            [
                row
                for row in rows
                if row["generic_capability"] == capability
                and row["m7_classification"] == "m7_qualified_release_row"
            ]
        )
        if status is None:
            if capability == "aabb_candidate_stream" and m7_count:
                summaries.append(
                    {
                        "generic_capability": capability,
                        "review_status": "one_route_map_row_m7_qualified_row_scoped",
                        "row_count": row_count,
                        "m7_qualified_release_rows": m7_count,
                        "release_authorized": False,
                        "public_speedup_claim_authorized": False,
                        "row_scoped_public_speedup_claim_authorized": True,
                        "evidence_basis": _rel(AABB_32768_FINAL),
                        "external_review": "docs/reviews/claude_phoenix_v3_aabb_candidate_stream_32768_m7_final_review_packet_review_2026-06-21.md",
                        "codex_consensus": "docs/reviews/codex_phoenix_v3_aabb_candidate_stream_32768_m7_final_review_packet_2ai_consensus_2026-06-21.md",
                        "m7_blockers": (
                            "remaining_aabb_rows_not_m7",
                            "do_not_generalize_to_full_spatial_index_or_v3_over_v2",
                        ),
                    }
                )
                continue
            summaries.append(
                {
                    "generic_capability": capability,
                    "review_status": UNFOCUSED_CAPABILITY_STATUS.get(capability, "candidate_needs_m7_packet"),
                    "row_count": row_count,
                    "m7_qualified_release_rows": 0,
                    "release_authorized": False,
                    "public_speedup_claim_authorized": False,
                    "row_scoped_public_speedup_claim_authorized": False,
                    "m7_blockers": (
                        "no_focused_m7_packet",
                        "no_public_row_level_external_review",
                    ),
                }
            )
            continue
        if capability == "component_union" and m7_count:
            final = _read_json(RTDBSCAN_COMPONENT_SIGNATURE_FINAL)
            summaries.append(
                {
                    "generic_capability": capability,
                    "review_status": "claude_codex_m7_qualified_row_scoped",
                    "goal4392_gate": status["goal4392_gate"],
                    "row_count": row_count,
                    "m7_qualified_release_rows": m7_count,
                    "release_authorized": False,
                    "public_speedup_claim_authorized": False,
                    "row_scoped_public_speedup_claim_authorized": True,
                    "evidence_basis": "docs/rebuild/v3/phoenix_v3_rtdbscan_component_signature_optimized_rtx_evidence_2026-06-21.md",
                    "external_review": final["external_review"],
                    "codex_consensus": final["codex_consensus"],
                    "m7_blockers": (
                        "do_not_generalize_to_full_dbscan_rt_dbscan_paper_v2_or_noisy_datasets",
                    ),
                    "focused_evidence_key": _focused_key_for_capability(capability, focused),
                }
            )
            continue
        if capability == "prepared_graph_chunk" and m7_count:
            summaries.append(
                {
                    "generic_capability": capability,
                    "review_status": "one_triangle_route_map_row_m7_qualified_after_claude_refresh",
                    "goal4392_gate": status["goal4392_gate"],
                    "row_count": row_count,
                    "m7_qualified_release_rows": m7_count,
                    "release_authorized": False,
                    "public_speedup_claim_authorized": False,
                    "row_scoped_public_speedup_claim_authorized": True,
                    "evidence_basis": _rel(TRIANGLE_80000_FINAL),
                    "external_review": "docs/reviews/claude_phoenix_v3_triangle_prepared_graph_80000_m7_refresh_review_2026-06-21.md",
                    "superseded_fallback_review": "docs/reviews/codex_subagent_phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_review_2026-06-21.md",
                    "codex_consensus": "docs/reviews/codex_phoenix_v3_triangle_prepared_graph_80000_m7_final_review_packet_2ai_consensus_2026-06-21.md",
                    "m7_blockers": (
                        "remaining_triangle_rows_not_m7",
                        "do_not_generalize_to_graph_database_paper_m113_full_app_or_v3_over_v2",
                    ),
                    "focused_evidence_key": _focused_key_for_capability(capability, focused),
                }
            )
            continue
        if capability == "threshold_summary" and m7_count:
            final = _read_json(HAUSDORFF_THRESHOLD_SUMMARY_FINAL)
            summaries.append(
                {
                    "generic_capability": capability,
                    "review_status": "one_large_row_m7_qualified_row_scoped",
                    "goal4392_gate": status["goal4392_gate"],
                    "row_count": row_count,
                    "m7_qualified_release_rows": m7_count,
                    "release_authorized": False,
                    "public_speedup_claim_authorized": False,
                    "row_scoped_public_speedup_claim_authorized": True,
                    "evidence_basis": _rel(HAUSDORFF_THRESHOLD_SUMMARY_FINAL),
                    "external_review": final["external_review"],
                    "codex_consensus": final["codex_consensus"],
                    "m7_blockers": (
                        "remaining_threshold_summary_rows_not_phase_total_wins",
                        "do_not_generalize_to_full_hausdorff_xhd_v2_other_thresholds_or_other_gpus",
                    ),
                    "focused_evidence_key": _focused_key_for_capability(capability, focused),
                }
            )
            continue
        if capability == "collision_flag_stream" and m7_count:
            final = _read_json(ROBOT_COLLISION_FLAG_STREAM_FINAL)
            summaries.append(
                {
                    "generic_capability": capability,
                    "review_status": "claude_codex_m7_qualified_row_scoped",
                    "goal4392_gate": status["goal4392_gate"],
                    "row_count": row_count,
                    "m7_qualified_release_rows": m7_count,
                    "release_authorized": False,
                    "public_speedup_claim_authorized": False,
                    "row_scoped_public_speedup_claim_authorized": True,
                    "evidence_basis": _rel(ROBOT_COLLISION_FLAG_STREAM_FINAL),
                    "external_review": "docs/reviews/claude_phoenix_v3_robot_collision_flag_stream_no_probe_paired_m7_review_2026-06-21.md",
                    "codex_consensus": "docs/reviews/codex_phoenix_v3_robot_collision_flag_stream_no_probe_paired_2ai_consensus_2026-06-21.md",
                    "m7_blockers": (
                        "do_not_generalize_to_full_robot_planning_exact_or_continuous_collision_v2_or_zero_copy",
                    ),
                    "focused_evidence_key": _focused_key_for_capability(capability, focused),
                    "wrapper_no_probe_optix_speedup_vs_embree_mean": final["aggregate_ratios"][
                        "wrapper_no_probe_optix_speedup_vs_embree_mean"
                    ],
                }
            )
            continue
        summaries.append(
            {
                "generic_capability": capability,
                "review_status": status["review_status"],
                "goal4392_gate": status["goal4392_gate"],
                "row_count": row_count,
                "m7_qualified_release_rows": 0,
                "release_authorized": False,
                "public_speedup_claim_authorized": False,
                "row_scoped_public_speedup_claim_authorized": False,
                "evidence_basis": status["evidence_basis"],
                "external_review": status.get("external_review"),
                "codex_consensus": status.get("codex_consensus"),
                "m7_blockers": status["m7_blockers"],
                "focused_evidence_key": _focused_key_for_capability(capability, focused),
            }
        )
    return summaries


def _is_aabb_m7_row(row: dict[str, Any], aabb_final: dict[str, Any]) -> bool:
    candidate = aabb_final["candidate_row"]
    return (
        row["app_id"] == candidate["app_id"]
        and row["comparison_group"] == candidate["comparison_group"]
        and row["generic_capability"] == aabb_final["generic_capability"]
        and aabb_final["m7_promotion_authorized"]
        and aabb_final["row_scoped_public_speedup_claim_authorized"]
    )


def _is_triangle_m7_row(row: dict[str, Any], triangle_final: dict[str, Any]) -> bool:
    return (
        row["app_id"] == triangle_final["source_app_id"]
        and row["comparison_group"] == triangle_final["source_comparison_group"]
        and row["generic_capability"] == triangle_final["generic_capability"]
        and triangle_final["m7_promotion_authorized"]
        and triangle_final["row_scoped_public_speedup_claim_authorized"]
    )


def _is_rtdbscan_component_union_m7_row(row: dict[str, Any], rtdbscan_final: dict[str, Any]) -> bool:
    return (
        row["app_id"] == "rt_dbscan"
        and row["comparison_group"] == "dbscan_cluster_signature"
        and row["generic_capability"] == "component_union"
        and rtdbscan_final["m7_promotion_authorized"]
        and rtdbscan_final["row_scoped_public_speedup_claim_authorized"]
    )


def _is_hausdorff_threshold_summary_m7_row(row: dict[str, Any], hausdorff_final: dict[str, Any]) -> bool:
    return (
        row["app_id"] == "hausdorff_xhd"
        and row["comparison_group"] == "hausdorff_threshold_copies_262144"
        and row["generic_capability"] == hausdorff_final["generic_capability"]
        and hausdorff_final["m7_promotion_authorized"]
        and hausdorff_final["row_scoped_public_speedup_claim_authorized"]
    )


def _is_robot_collision_flag_stream_m7_row(row: dict[str, Any], collision_final: dict[str, Any]) -> bool:
    return (
        row["app_id"] == collision_final["app_id"]
        and row["comparison_group"] == collision_final["comparison_group"]
        and row["generic_capability"] == collision_final["generic_capability"]
        and collision_final["m7_promotion_authorized"]
        and collision_final["row_scoped_public_speedup_claim_authorized"]
    )


def _is_contact_manifold_boundary_row(row: dict[str, Any]) -> bool:
    return (
        row["app_id"] == "contact_manifold"
        and row["comparison_group"] == "generic_aabb_broadphase_collect_k"
        and row["generic_capability"] == "aabb_candidate_stream"
    )


def _focused_key_for_capability(capability: str, focused: dict[str, Any]) -> str | None:
    mapping = {
        "component_union": "m4_grouped_continuation",
        "grouped_reduction": "raydb_m28_grouped_reduction",
        "point_location_topology_stream": "m5_topology",
        "prepared_graph_chunk": "triangle_prepared_graph",
        "ranked_summary": "rtnn_ranked_summary",
        "aggregate_frontier": "m6_barnes_hut",
        "vector_accumulation": "m6_barnes_hut",
        "threshold_summary": "hausdorff_threshold_summary",
    }
    key = mapping.get(capability)
    return key if key in focused else None


def _focused_evidence() -> dict[str, Any]:
    m4 = _read_json(M4_INDEX)
    m5 = _read_json(M5_INTAKE)
    m6 = _read_json(M6_INTAKE)
    raydb = _read_json(RAYDB_M28)
    triangle = _read_json(TRIANGLE_INTAKE)
    rtnn = _read_json(RTNN_INTAKE)
    raydb_pairs = {pair["mode"]: pair for pair in raydb["comparison"]["same_contract_backend_pairs"]}
    return {
        "m4_grouped_continuation": {
            "source": _rel(M4_INDEX),
            "status": m4["status"],
            "row_count": len(m4["rows"]),
            "phoenix_m7_qualified_release_rows": m4["phoenix_m7_qualified_release_rows"],
            "all_rows_not_m7": all(not row["phoenix_m7_qualified"] for row in m4["rows"]),
            "system_python_packaging_gap_status": m4["binding_environment"]["open_packaging_gap"]["status"],
            "m10_clean_pass": next(row for row in m4["rows"] if row["gate"] == "M10")["clean_pass"],
        },
        "m5_topology": {
            "source": _rel(M5_INTAKE),
            "status": m5["status"],
            "status_label": m5["status_label"],
            "m5_author_code_comparison_status": m5["m5_author_code_comparison_status"],
            "phoenix_m7_qualified_release_rows": m5["phoenix_m7_qualified_release_rows"],
            "rayjoin_author_rt_speedup_vs_rtdl_optix_native_traversal": m5["metrics"][
                "pip_rayjoin_rt_speedup_vs_rtdl_optix_native_traversal"
            ],
            "rayjoin_author_rt_is_faster_than_rtdl_optix": True,
        },
        "m6_barnes_hut": {
            "source": _rel(M6_INTAKE),
            "status": m6["status"],
            "overall_status": m6["overall_status"],
            "phoenix_m7_qualified_release_rows": m6["phoenix_m7_qualified_release_rows"],
            "fastest_by_scale": m6["fastest_by_scale"],
            "timing_basis_mixed": m6["timing_basis_mixed"],
            "prepared_optix_over_fastest": {
                str(item["body_count"]): item["optix_numba_over_fastest"] for item in m6["body_summaries"]
            },
        },
        "raydb_m28_grouped_reduction": {
            "source": _rel(RAYDB_M28),
            "status": raydb["status"],
            "generated_rows": raydb["parameters"]["generated_rows"],
            "generated_groups": raydb["parameters"]["generated_groups"],
            "count_embree_over_optix": raydb_pairs["count"]["embree_over_optix_median"],
            "sum_embree_over_optix": raydb_pairs["sum"]["embree_over_optix_median"],
            "sum_min_workload_build_sec": min(
                row["workload_build_sec"] for row in raydb["rows"] if row["mode"] == "sum"
            ),
            "comparison_scope": raydb_pairs["sum"]["comparison_scope"],
        },
        "triangle_prepared_graph": {
            "source": _rel(TRIANGLE_INTAKE),
            "status": triangle["status"],
            "generic_capability_status": triangle["generic_capability_status"],
            "m7_qualified": triangle["comparison"]["m7_qualified"],
            "max_hot_optix_speedup_vs_embree": max(pair["optix_speedup_vs_embree"] for pair in triangle["pairs"]),
            "min_wall_optix_speedup_vs_embree": min(pair["optix_wall_speedup_vs_embree"] for pair in triangle["pairs"]),
            "m7_blockers": triangle["m7_blockers"],
        },
        "rtnn_ranked_summary": {
            "source": _rel(RTNN_INTAKE),
            "status": rtnn["status"],
            "generic_capability_status": rtnn["generic_capability_status"],
            "m7_qualified": rtnn["comparison"]["m7_qualified"],
            "all_hot_optix_faster_than_embree": rtnn["comparison"]["all_hot_optix_faster_than_embree"],
            "all_wall_optix_slower_than_embree": rtnn["comparison"]["all_wall_optix_slower_than_embree"],
            "m7_blockers": rtnn["m7_blockers"],
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    count_words = {
        1: "One",
        2: "Two",
        3: "Three",
        4: "Four",
        5: "Five",
    }
    lines: list[str] = [
        "# Phoenix V3 M7 Row Classification Packet",
        "",
        "Status: M7 classification packet, not release authorization.",
        "",
        "## Verdict",
        "",
        "This packet classifies the current Phoenix V3 candidate evidence after the focused M4/M5/M6, RayDB, Triangle, RTNN, grouped_sum, AABB, RTDBSCAN, Hausdorff, and Robot Collision final-review closures.",
        "",
        "```text",
        "release_authorized: false",
        "public_speedup_claim_authorized: false",
        "broad_v3_faster_than_v2_claim_authorized: false",
        f"Phoenix M7-qualified release rows: {payload['phoenix_m7_qualified_release_rows']}",
        "```",
        "",
        (
            "The result is deliberately strict: "
            f"{payload['summary']['route_map_m7_qualified_release_rows']} original route-map rows "
            "(AABB, RTDBSCAN component_union, Triangle, Hausdorff threshold_summary, and Robot Collision collision_flag_stream) "
            f"and {payload['summary']['supplemental_m7_qualified_release_rows']} supplemental rows "
            "(grouped_sum plus AABB native query-handle plus RTNN prepared repeat50 plus Barnes-Hut fused partner rows) are now M7-qualified and row-scoped; "
            "all other rows remain internal, blocked, or candidate evidence. V3 release remains unauthorized."
        ),
        "",
        "## Why This Exists",
        "",
        "Phoenix V3 must not repeat the earlier failure mode where internal technical progress was mistaken for user-facing release proof.",
        "The packet turns each current performance row into one of two states: M7-qualified release row, or not M7-qualified with explicit blockers.",
        "",
        "## Focused Evidence Snapshot",
        "",
        "| Evidence | Status | M7 rows | Release reading |",
        "| --- | --- | ---: | --- |",
    ]
    focused = payload["focused_evidence"]
    lines.extend(
        [
            f"| M4 grouped continuation | `{focused['m4_grouped_continuation']['status']}` | {focused['m4_grouped_continuation']['phoenix_m7_qualified_release_rows']} | internal component/continuation evidence only |",
            f"| M5 topology | `{focused['m5_topology']['status_label']}` | {focused['m5_topology']['phoenix_m7_qualified_release_rows']} | RayJoin author RT is faster than RTDL OptiX, so no RTDL-beats-RayJoin claim |",
            f"| M6 Barnes-Hut | `{focused['m6_barnes_hut']['overall_status']}` | {focused['m6_barnes_hut']['phoenix_m7_qualified_release_rows']} | fused Numba CUDA is fastest; prepared OptiX is route-parity evidence |",
            f"| RayDB grouped reduction | `{focused['raydb_m28_grouped_reduction']['status']}` | 0 | hot-query evidence only; not end-to-end DB timing |",
            f"| Triangle prepared graph | `{focused['triangle_prepared_graph']['status']}` | 1 | exact 80,000-clique non-graph stream row only; not graph DB or paper reproduction |",
            f"| RTNN ranked summary | `{focused['rtnn_ranked_summary']['status']}` | 0 | hot rows win, wall timing regresses |",
            "",
            "## Supplemental Final Review Packets",
            "",
            "These packets were created after the route-map classification. They can add row-scoped M7-qualified rows without authorizing a V3 release.",
            "",
            "| Packet | Candidate | Local reading | External review | Consensus | M7 rows |",
            "| --- | --- | --- | --- | --- | ---: |",
        ]
    )
    for packet in payload["post_classification_final_review_packets"]:
        lines.append(
            f"| `{packet['packet']}` | `{packet['candidate_row_id']}` | "
            f"`{packet['local_gate_reading']}` | `{packet['current_packet_external_review_status']}` | "
            f"`{packet['current_packet_2ai_consensus_status']}` | {packet['m7_qualified_release_rows']} |"
        )
    lines.extend(
        [
            "",
            "## Capability Classification",
            "",
            "| Capability | Review status | Rows | M7 rows | Main blocker |",
            "| --- | --- | ---:| ---:| --- |",
        ]
    )
    for item in payload["capability_summaries"]:
        blockers = item.get("m7_blockers", ())
        main_blocker = blockers[0] if blockers else "none"
        lines.append(
            f"| `{item['generic_capability']}` | `{item['review_status']}` | {item['row_count']} | "
            f"{item['m7_qualified_release_rows']} | `{main_blocker}` |"
        )
    capability_m7_ids: dict[str, set[str]] = {}
    for row in payload["row_classifications"]:
        if row["m7_classification"] != "m7_qualified_release_row":
            continue
        capability_m7_ids.setdefault(row["generic_capability"], set()).add(row["candidate_row_id"])
    for packet in payload["post_classification_final_review_packets"]:
        capability = packet.get("generic_capability")
        if not capability:
            continue
        candidate_ids = [item.strip() for item in packet["candidate_row_id"].split(";") if item.strip()]
        for candidate_id in candidate_ids:
            capability_m7_ids.setdefault(capability, set()).add(candidate_id)
    lines.extend(
        [
            "",
            "## Capability M7 Count Summary",
            "",
        ]
    )
    for capability in sorted(capability_m7_ids):
        count = len(capability_m7_ids[capability])
        word = count_words.get(count, str(count))
        noun = "row is" if count == 1 else "rows are"
        lines.append(f"- {word} exact `{capability}` {noun} M7-qualified.")
    lines.extend(
        [
            "",
            "## Capability Scope Notes",
            "",
        ]
    )
    for note in payload["capability_scope_notes"]:
        lines.append(f"- `{note['capability']}`: `{note['status']}`. {note['note']}")
    lines.extend(
        [
            "",
            "## Row Classification",
            "",
            "| App | Row | Capability | Class | Leading blocker |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in payload["row_classifications"]:
        leading_blocker = row["m7_blockers"][0] if row["m7_blockers"] else "none"
        lines.append(
            f"| `{row['app_id']}` | `{row['comparison_group']}` | `{row['generic_capability']}` | "
            f"`{row['m7_classification']}` | `{leading_blocker}` |"
        )
    m7_rows = [row for row in payload["row_classifications"] if row["m7_classification"] == "m7_qualified_release_row"]
    lines.extend(
        [
            "",
            "## M7 Row IDs",
            "",
        ]
    )
    for row in m7_rows:
        lines.append(
            f"- `{row['candidate_row_id']}`: `{row['generic_capability']}` / `{row['app_id']}`."
        )
    lines.extend(
        [
            "",
            "## Next M7 Promotion Candidates",
            "",
        ]
    )
    if payload["next_m7_promotion_candidates"]:
        for candidate in payload["next_m7_promotion_candidates"]:
            fixes = ", ".join(candidate["must_fix_before_m7"])
            lines.append(f"- `{candidate['candidate']}`: {candidate['why']}. Must fix: {fixes}.")
    else:
        lines.append("- None from current evidence. Reopen only after a generic-engine change.")
    queue = payload["next_engine_work_queue"]
    lines.extend(
        [
            "",
            "## Next Engine Work Queue",
            "",
            f"Status: `{queue['status']}`.",
            "",
            f"Source: `{queue['source']}`.",
            "",
            "Active Phoenix P0 items:",
            "",
        ]
    )
    for item in queue["active_p0_ids"]:
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            "Future research, not active Phoenix P0:",
            "",
        ]
    )
    for item in queue["future_research_ids"]:
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            payload["summary"]["next_work"],
        ]
    )
    lines.extend(
        [
            "",
            "## Optimization-Required Reopen Queue",
            "",
        ]
    )
    for item in payload["optimization_required_reopen_queue"]:
        lines.append(
            f"- `{item['candidate']}`: `{item['current_boundary']}`. "
            f"{item['required_change_before_reopen']}"
        )
    if not payload["optimization_required_reopen_queue"]:
        lines.append("- None in this classification packet. Continue through `phoenix_v3_next_generic_engine_work_queue_2026-06-21`.")
    audit = payload["goal_level_decision_audit"]
    lines.extend(
        [
            "",
            "## Goal-Level Decision Audit",
            "",
            f"Decision: {audit['decision']}",
            "",
            "1. Was I foolish?",
            "",
            f"   {audit['was_i_foolish']}",
            "",
            "2. If yes, what actions made the decision foolish?",
            "",
            f"   {audit['foolish_actions']}",
            "",
            "3. Was there another path?",
            "",
            f"   {audit['other_path']}",
            "",
            "4. Can I now try a different path that actually solves the problem?",
            "",
            f"   {audit['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
