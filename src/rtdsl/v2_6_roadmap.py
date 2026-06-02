from __future__ import annotations

from pathlib import Path
from typing import Any


V2_6_ROADMAP_VERSION = "rtdl.v2_6.roadmap.v1"
V2_6_ROADMAP_STATUS = "v2_6_started_planning_not_release_authorization"
V2_6_CLAUDE_REFERENCE_REPORT = (
    "docs/reports/claude_v2_6_numba_first_class_partner_work_for_main_ai_2026-05-31.md"
)
V2_6_ROADMAP_CLAIM_BOUNDARY = (
    "v2.6 begins from the v2.5 closeout as an internal development lane. It "
    "does not authorize v2.6 release, public speedup wording, whole-app "
    "speedup wording, broad RT-core wording, true-zero-copy wording, automatic "
    "partner selection, automatic Triton selection, Numba speedup wording, or "
    "app-specific native-engine behavior."
)


def v2_6_roadmap() -> dict[str, Any]:
    """Return the initial v2.6 roadmap after the v2.5 closeout cleanup."""

    return {
        "roadmap_version": V2_6_ROADMAP_VERSION,
        "status": V2_6_ROADMAP_STATUS,
        "source_reference": V2_6_CLAUDE_REFERENCE_REPORT,
        "opening_goal": "neutral_buffer_seam_runtime_cleanup_before_first_class_numba",
        "n0_foundation_goal": "Goal2990",
        "n0_foundation_report": "docs/reports/goal2990_v2_6_neutral_partner_handoff_2026-06-01.md",
        "n0_foundation_status": "neutral_descriptor_and_lease_packet_landed_pod_runtime_demonstrator_pending",
        "pod_runner_goal": "Goal2991",
        "pod_runner_report": "docs/reports/goal2991_v2_6_numba_neutral_handoff_pod_runner_2026-06-01.md",
        "pod_runner_status": "executed_on_l4_pod_via_goal2993",
        "pod_evidence_goal": "Goal2993",
        "pod_evidence_report": "docs/reports/goal2993_v2_6_numba_neutral_handoff_l4_pod_2026-06-01.md",
        "pod_evidence_artifact": "docs/reports/goal2993_v2_6_numba_neutral_handoff_l4_pod_2026-06-01.json",
        "pod_evidence_status": "l4_pod_runtime_conformance_passed_not_release_or_speedup_evidence",
        "local_smoke_goal": "Goal2992",
        "local_smoke_report": "docs/reports/goal2992_v2_6_numba_neutral_handoff_local_linux_smoke_2026-06-01.md",
        "local_smoke_artifact": "docs/reports/goal2992_v2_6_numba_neutral_handoff_local_linux_smoke_2026-06-01.json",
        "local_smoke_status": "passed_on_gtx1070_not_release_or_performance_evidence",
        "benchmark_demonstrator_goal": "Goal2994",
        "benchmark_demonstrator_report": "docs/reports/goal2994_raydb_numba_neutral_demo_l4_pod_2026-06-01.md",
        "benchmark_demonstrator_artifact": "docs/reports/goal2994_raydb_numba_neutral_demo_l4_pod_2026-06-01.json",
        "benchmark_demonstrator_status": "raydb_style_avg_sum_count_l4_pod_conformance_passed_not_speedup_evidence",
        "benchmark_minmax_goal": "Goal2995",
        "benchmark_minmax_report": "docs/reports/goal2995_raydb_numba_minmax_l4_pod_2026-06-01.md",
        "benchmark_minmax_artifact": "docs/reports/goal2995_raydb_numba_minmax_l4_pod_2026-06-01.json",
        "benchmark_minmax_status": "raydb_style_all_five_scalar_modes_l4_pod_conformance_passed_not_speedup_evidence",
        "compact_mask_goal": "Goal2997",
        "compact_mask_report": "docs/reports/goal2997_numba_compact_mask_l4_pod_2026-06-01.md",
        "compact_mask_artifact": "docs/reports/goal2997_numba_compact_mask_l4_pod_2026-06-01.json",
        "compact_mask_status": "compact_mask_i64_l4_pod_conformance_passed_stable_order_host_prefix_sum_not_speedup_evidence",
        "triangle_compact_mask_goal": "Goal2999",
        "triangle_compact_mask_report": "docs/reports/goal2999_triangle_counting_numba_compact_mask_wiring_2026-06-01.md",
        "triangle_compact_mask_status": "triangle_counting_witness_row_compact_mask_wiring_prepared_l4_runtime_passed_via_goal3000_not_speedup_evidence",
        "triangle_compact_mask_pod_goal": "Goal3000",
        "triangle_compact_mask_pod_report": "docs/reports/goal3000_triangle_counting_numba_compact_mask_l4_pod_2026-06-01.md",
        "triangle_compact_mask_pod_artifact": "docs/reports/goal3000_triangle_counting_numba_compact_mask_l4_pod_2026-06-01.json",
        "triangle_compact_mask_pod_status": "l4_pod_conformance_passed_clean_source_not_speedup_evidence",
        "rayjoin_compact_mask_goal": "Goal3002",
        "rayjoin_compact_mask_report": "docs/reports/goal3002_rayjoin_numba_compact_mask_wiring_2026-06-01.md",
        "rayjoin_compact_mask_status": "rayjoin_v2_spatial_join_compact_mask_wiring_prepared_l4_runtime_passed_via_goal3003_not_speedup_evidence",
        "rayjoin_compact_mask_pod_goal": "Goal3003",
        "rayjoin_compact_mask_pod_report": "docs/reports/goal3003_rayjoin_numba_compact_mask_l4_pod_2026-06-01.md",
        "rayjoin_compact_mask_pod_artifact": "docs/reports/goal3003_rayjoin_numba_compact_mask_l4_pod_2026-06-01.json",
        "rayjoin_compact_mask_pod_status": "l4_pod_conformance_passed_all_three_workloads_clean_source_not_speedup_evidence",
        "numba_grouped_arg_goal": "Goal3006",
        "numba_grouped_arg_report": "docs/reports/goal3006_numba_grouped_argmin_argmax_preview_2026-06-01.md",
        "numba_grouped_arg_status": "grouped_argmin_f64_and_grouped_argmax_f64_preview_front_door_prepared_not_speedup_evidence",
        "numba_grouped_arg_pod_goal": "Goal3007",
        "numba_grouped_arg_pod_report": "docs/reports/goal3007_numba_grouped_arg_reducer_l4_pod_2026-06-01.md",
        "numba_grouped_arg_pod_artifact": "docs/reports/goal3007_numba_grouped_arg_reducer_l4_pod_2026-06-01.json",
        "numba_grouped_arg_pod_status": "l4_pod_conformance_passed_clean_source_not_speedup_evidence",
        "hausdorff_numba_witness_goal": "Goal3010",
        "hausdorff_numba_witness_report": "docs/reports/goal3010_hausdorff_numba_witness_exact_app_wiring_2026-06-01.md",
        "hausdorff_numba_witness_status": "hausdorff_app_wired_to_generic_numba_grouped_witness_front_door_not_rt_core_path",
        "numba_pairwise_score_rows_goal": "Goal3012",
        "numba_pairwise_score_rows_report": "docs/reports/goal3012_numba_pairwise_score_rows_for_hausdorff_2026-06-01.md",
        "numba_pairwise_score_rows_status": "pairwise_l2_sq_score_rows_2d_generates_generic_score_rows_on_numba_device_for_hausdorff_witness_mode_not_speedup_evidence",
        "numba_pairwise_score_rows_pod_goal": "Goal3013",
        "numba_pairwise_score_rows_pod_report": "docs/reports/goal3013_hausdorff_numba_device_score_rows_l4_pod_2026-06-01.md",
        "numba_pairwise_score_rows_pod_artifact": "docs/reports/goal3013_hausdorff_numba_device_score_rows_l4_pod_2026-06-01.json",
        "numba_pairwise_score_rows_pod_status": "hausdorff_numba_device_score_rows_l4_pod_conformance_passed_clean_source_not_speedup_evidence",
        "numba_block_nearest_rows_goal": "Goal3015",
        "numba_block_nearest_rows_report": "docs/reports/goal3015_numba_block_nearest_rows_for_hausdorff_2026-06-01.md",
        "numba_block_nearest_rows_status": "pairwise_l2_sq_block_nearest_rows_2d_bounded_tile_summary_for_hausdorff_witness_mode_not_speedup_evidence",
        "hausdorff_numba_dense_vs_block_goal": "Goal3016",
        "hausdorff_numba_dense_vs_block_report": "docs/reports/goal3016_hausdorff_numba_dense_vs_block_l4_pod_2026-06-01.md",
        "hausdorff_numba_dense_vs_block_artifact": "docs/reports/goal3016_hausdorff_numba_dense_vs_block_l4_pod_2026-06-01.json",
        "hausdorff_numba_dense_vs_block_status": "l4_internal_phase_timing_dense_device_score_rows_still_faster_block_nearest_is_memory_pressure_path_not_speedup_evidence",
        "numba_grouped_witness_no_host_sync_goal": "Goal3017",
        "numba_grouped_witness_no_host_sync_report": "docs/reports/goal3017_numba_grouped_witness_no_host_sync_fast_path_2026-06-01.md",
        "numba_grouped_witness_no_host_sync_status": "explicit_generated_score_row_fast_path_skips_host_nan_validation_and_present_group_compaction_not_speedup_evidence",
        "hausdorff_numba_no_host_sync_comparison_goal": "Goal3018",
        "hausdorff_numba_no_host_sync_comparison_report": "docs/reports/goal3018_hausdorff_numba_no_host_sync_comparison_l4_pod_2026-06-01.md",
        "hausdorff_numba_no_host_sync_comparison_artifact": "docs/reports/goal3018_hausdorff_numba_no_host_sync_comparison_l4_pod_2026-06-01.json",
        "hausdorff_numba_no_host_sync_comparison_status": "dense_device_score_rows_faster_after_no_host_sync_block_nearest_retained_for_memory_pressure_not_speedup_evidence",
        "l4_optix_readiness_goal": "Goal3020",
        "l4_optix_readiness_report": "docs/reports/goal3020_l4_optix_readiness_and_ptx_toolchain_blocker_2026-06-01.md",
        "l4_optix_readiness_status": "librtdl_optix_build_succeeded_rt_hausdorff_smoke_blocked_by_cuda12_8_ptx_vs_driver565_toolchain_mismatch",
        "l4_optix_cuda126_smoke_goal": "Goal3021",
        "l4_optix_cuda126_smoke_report": "docs/reports/goal3021_l4_optix_cuda126_hausdorff_rt_smoke_2026-06-02.md",
        "l4_optix_cuda126_smoke_artifact": "docs/reports/goal3021_l4_optix_cuda126_hausdorff_rt_smoke_2026-06-02.json",
        "l4_optix_cuda126_smoke_status": "cuda12_6_side_by_side_toolchain_unblocked_rt_hausdorff_smoke_openmp_distance_parity_not_speedup_evidence",
        "hausdorff_optix_cupy_perf_probe_goal": "Goal3022",
        "hausdorff_optix_cupy_perf_probe_report": "docs/reports/goal3022_hausdorff_optix_cupy_perf_probe_2026-06-02.md",
        "hausdorff_optix_cupy_perf_probe_artifact": "docs/reports/goal3022_hausdorff_optix_cupy_perf_probe_2026-06-02.json",
        "hausdorff_optix_cupy_perf_probe_status": "rt_core_correct_but_cupy_grouped_grid_current_fast_reference_for_dense_exact_2d_hausdorff_not_speedup_evidence",
        "hausdorff_optix_group_sweep_goal": "Goal3024",
        "hausdorff_optix_group_sweep_report": "docs/reports/goal3024_hausdorff_optix_group_sweep_2026-06-02.md",
        "hausdorff_optix_group_sweep_artifact": "docs/reports/goal3024_hausdorff_optix_group_sweep_2026-06-02.json",
        "hausdorff_optix_group_sweep_status": "adaptive_group_512_best_current_rt_row_but_cheap_tuning_does_not_close_gap_not_speedup_evidence",
        "hausdorff_adaptive_reduced_probe_goal": "Goal3025",
        "hausdorff_adaptive_reduced_probe_report": "docs/reports/goal3025_hausdorff_adaptive_reduced_pod_probe_2026-06-02.md",
        "hausdorff_adaptive_reduced_probe_artifact": "docs/reports/goal3025_hausdorff_adaptive_reduced_pod_probe_2026-06-02.json",
        "hausdorff_adaptive_reduced_probe_status": "correct_but_slower_than_existing_adaptive_rt_and_cupy_not_promoted_not_speedup_evidence",
        "hausdorff_raw_row_view_probe_goal": "Goal3026",
        "hausdorff_raw_row_view_probe_report": "docs/reports/goal3026_hausdorff_raw_row_view_probe_2026-06-02.md",
        "hausdorff_raw_row_view_probe_artifact": "docs/reports/goal3026_hausdorff_raw_row_view_probe_2026-06-02.json",
        "hausdorff_raw_row_view_probe_status": "raw_row_view_faster_than_old_adaptive_rt_but_still_slower_than_cupy_not_public_speedup_evidence",
        "hausdorff_raw_row_view_larger_scale_goal": "Goal3028",
        "hausdorff_raw_row_view_larger_scale_report": "docs/reports/goal3028_hausdorff_raw_row_view_larger_scale_probe_2026-06-02.md",
        "hausdorff_raw_row_view_larger_scale_artifacts": (
            "docs/reports/goal3028_hausdorff_raw_row_view_larger_scale_probe_2026-06-02.json",
            "docs/reports/goal3028_hausdorff_raw_row_view_32768_probe_2026-06-02.json",
            "docs/reports/goal3028_hausdorff_raw_row_view_65536_probe_2026-06-02.json",
        ),
        "hausdorff_raw_row_view_larger_scale_status": "raw_row_view_rt_stable_improvement_over_old_rt_gap_narrows_but_no_crossover_against_cupy_not_public_speedup_evidence",
        "hausdorff_vectorized_row_view_goal": "Goal3030",
        "hausdorff_vectorized_row_view_status": "generic_optix_row_view_numpy_columns_and_vectorized_hausdorff_raw_row_reducer_landed",
        "hausdorff_vectorized_row_view_pod_goal": "Goal3031",
        "hausdorff_vectorized_row_view_pod_report": "docs/reports/goal3031_hausdorff_vectorized_row_view_l4_pod_2026-06-02.md",
        "hausdorff_vectorized_row_view_pod_artifact": "docs/reports/goal3031_hausdorff_vectorized_row_view_l4_pod_2026-06-02.json",
        "hausdorff_vectorized_row_view_pod_status": "l4_clean_source_vectorized_raw_row_view_faster_than_old_adaptive_rt_still_slower_than_cupy_not_public_speedup_evidence",
        "point_group_nearest_device_columns_goal": "Goal3033",
        "point_group_nearest_device_columns_status": "generic_optix_point_group_nearest_witness_device_columns_producer_landed_no_host_row_materialization",
        "point_group_nearest_device_columns_pod_goal": "Goal3034",
        "point_group_nearest_device_columns_pod_report": "docs/reports/goal3034_point_group_nearest_device_columns_l4_pod_2026-06-02.md",
        "point_group_nearest_device_columns_pod_artifact": "docs/reports/goal3034_point_group_nearest_device_columns_l4_pod_2026-06-02.json",
        "point_group_nearest_device_columns_pod_status": "l4_clean_source_device_columns_match_raw_rows_not_release_not_speedup_evidence_true_zero_copy_still_unauthorized",
        "numba_global_argmax_hardening_goal": "Goal3036",
        "numba_global_argmax_hardening_report": "docs/reports/goal3036_numba_global_argmax_block_reduce_hardening_2026-06-02.md",
        "numba_global_argmax_hardening_status": "global_argmax_u32_f64_block_reduce_no_global_atomics_dirty_overlay_a4000_passed_clean_composition_evidence_pending",
        "point_group_nearest_numba_argmax_pod_goal": "Goal3037",
        "point_group_nearest_numba_argmax_pod_report": "docs/reports/goal3037_point_group_nearest_numba_argmax_a4000_pod_2026-06-02.md",
        "point_group_nearest_numba_argmax_pod_artifact": "docs/reports/goal3037_point_group_nearest_numba_argmax_a4000_pod_2026-06-02.json",
        "point_group_nearest_numba_argmax_pod_status": "clean_a4000_optix_device_columns_to_numba_global_argmax_conformance_passed_not_release_not_speedup_true_zero_copy_still_blocked",
        "hausdorff_device_columns_numba_argmax_strategy_goal": "Goal3039",
        "hausdorff_device_columns_numba_argmax_strategy_report": "docs/reports/goal3039_hausdorff_device_columns_numba_argmax_strategy_2026-06-02.md",
        "hausdorff_device_columns_numba_argmax_strategy_status": "app_level_exact_hausdorff_strategy_wired_pod_perf_evidence_pending_not_speedup_evidence",
        "hausdorff_device_columns_numba_argmax_perf_goal": "Goal3040",
        "hausdorff_device_columns_numba_argmax_perf_report": "docs/reports/goal3040_hausdorff_device_columns_numba_argmax_a4000_perf_2026-06-02.md",
        "hausdorff_device_columns_numba_argmax_perf_artifact": "docs/reports/goal3040_hausdorff_device_columns_numba_argmax_a4000_perf_2026-06-02.json",
        "hausdorff_device_columns_numba_argmax_perf_status": "clean_a4000_correct_negative_perf_result_needs_device_resident_active_set_candidate_frontier_not_speedup_evidence",
        "point_group_active_frontier_goal": "Goal3042",
        "point_group_active_frontier_report": "docs/reports/goal3042_point_group_active_frontier_witness_selection_2026-06-02.md",
        "point_group_active_frontier_artifact": "docs/reports/goal3042_active_frontier_perf_a4000_2026-06-02.json",
        "point_group_active_frontier_status": "generic_optix_active_frontier_witness_selection_a4000_positive_perf_evidence_external_review_pending_not_public_speedup_evidence",
        "hausdorff_witness_index_cleanup_goal": "Goal3044",
        "hausdorff_witness_index_cleanup_report": "docs/reports/goal3044_hausdorff_grouped_witness_index_mapping_cleanup_2026-06-02.md",
        "hausdorff_witness_index_cleanup_artifact": "docs/reports/goal3044_grouped_reduced_witness_index_smoke_a4000_2026-06-02.json",
        "hausdorff_witness_index_cleanup_status": "grouped_one_row_hausdorff_paths_map_native_point_ids_to_original_target_columns_a4000_smoke_passed_not_native_or_speedup_work",
        "hausdorff_active_frontier_multitrial_goal": "Goal3045",
        "hausdorff_active_frontier_multitrial_report": "docs/reports/goal3045_hausdorff_active_frontier_multitrial_harness_2026-06-02.md",
        "hausdorff_active_frontier_multitrial_artifact": "docs/reports/goal3045_hausdorff_active_frontier_multitrial_a4000_2026-06-02.json",
        "hausdorff_active_frontier_multitrial_status": "a4000_same_process_10_trial_median_confirms_active_frontier_crossover_internal_evidence_not_public_speedup_evidence",
        "primary_partner_track": "numba_first_class_user_selectable_partner",
        "partner_choice_rule": "users_choose_supported_partners_explicitly",
        "supported_partner_duty": "provide_high_performance_support_for_supported_partners_without_forcing_a_partner",
        "benchmark_app_role": "reference_or_recommended_implementations_with_project_chosen_partner_paths",
        "generic_engine_boundary": "native_engine_exposes_generic_app_agnostic_primitives_only",
        "triton_status": "paused_ignored_for_recommended_paths_until_new_same_contract_evidence",
        "numba_support_boundary": "support_means_user_selectable_correct_app_path_not_speedup_claim",
        "minimum_demonstration": {
            "one_benchmark_app_enough_for_initial_first_class_claim": True,
            "real_partner_continuation_required": True,
            "cpu_reference_parity_required": True,
            "partner_free_reference_path_required": True,
            "same_contract_perf_gate_required_before_speedup_claim": True,
        },
        "sequenced_work": (
            {
                "step": "N-0",
                "title": "neutral_buffer_seam_cleanup",
                "foundation_status": "Goal2990 neutral descriptor/lease packet landed",
                "exit_gate": (
                    "CuPy and Numba CUDA arrays pass through a neutral descriptor "
                    "without torch conversion on the data path; copy/borrow status "
                    "is runtime-observed and labeled; large L4 pod continuation "
                    "conformance passed for Numba segmented count/sum in Goal2993."
                ),
            },
            {
                "step": "N-1",
                "title": "numba_op_coverage_for_one_demonstrator",
                "exit_gate": "Goal2995 covers count/sum/min/max and avg-as-sum-count for the RayDB-style demonstrator with CPU reference parity",
            },
            {
                "step": "N-2",
                "title": "benchmark_app_numba_user_selected_path",
                "exit_gate": "Goal2994 and Goal2995 route RayDB-style continuations through user-selected Numba; Goal2999/3000 prove triangle witness compaction; Goal3002/3003 prove RayJoin row-stream compaction without changing prepared count/parity fast paths",
            },
            {
                "step": "N-3",
                "title": "conformance_matrix_and_readiness_refresh",
                "exit_gate": "Numba demonstrated ops carry runtime conformance, including Goal2997 compact_mask_i64 and Goal3007 grouped_argmin_f64/grouped_argmax_f64, while release_conformance_complete remains false",
            },
            {
                "step": "N-4",
                "title": "honest_v2_6_closeout_line",
                "exit_gate": "documents support as correctness/choosability, not performance",
            },
        ),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "automatic_partner_selection_allowed": False,
        "automatic_triton_selection_allowed": False,
        "numba_speedup_claim_authorized": False,
        "app_specific_native_engine_logic_authorized": False,
        "claim_boundary": V2_6_ROADMAP_CLAIM_BOUNDARY,
    }


def validate_v2_6_roadmap(
    roadmap: dict[str, Any] | None = None,
    *,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    roadmap = v2_6_roadmap() if roadmap is None else roadmap
    root = Path.cwd() if repo_root is None else Path(repo_root)
    errors: list[str] = []
    if roadmap.get("roadmap_version") != V2_6_ROADMAP_VERSION:
        errors.append("unexpected v2.6 roadmap version")
    if roadmap.get("status") != V2_6_ROADMAP_STATUS:
        errors.append("unexpected v2.6 roadmap status")
    if "neutral_buffer_seam" not in str(roadmap.get("opening_goal", "")):
        errors.append("v2.6 must begin with the neutral buffer seam cleanup")
    if roadmap.get("n0_foundation_goal") != "Goal2990":
        errors.append("v2.6 roadmap must index Goal2990 as the N-0 foundation")
    if "pod_runtime_demonstrator_pending" not in str(roadmap.get("n0_foundation_status", "")):
        errors.append("v2.6 roadmap must keep the pod runtime demonstrator pending")
    if not (root / str(roadmap.get("n0_foundation_report", ""))).exists():
        errors.append("Goal2990 N-0 foundation report is missing")
    if roadmap.get("pod_runner_goal") != "Goal2991":
        errors.append("v2.6 roadmap must index Goal2991 as the Numba neutral-handoff pod runner")
    if roadmap.get("pod_runner_status") != "executed_on_l4_pod_via_goal2993":
        errors.append("Goal2991 runner must point to Goal2993 L4 pod evidence")
    if not (root / str(roadmap.get("pod_runner_report", ""))).exists():
        errors.append("Goal2991 pod-runner report is missing")
    if roadmap.get("pod_evidence_goal") != "Goal2993":
        errors.append("v2.6 roadmap must index Goal2993 as the L4 pod evidence")
    if "not_release_or_speedup_evidence" not in str(roadmap.get("pod_evidence_status", "")):
        errors.append("Goal2993 pod evidence must not be treated as release or speedup evidence")
    if not (root / str(roadmap.get("pod_evidence_report", ""))).exists():
        errors.append("Goal2993 L4 pod evidence report is missing")
    if not (root / str(roadmap.get("pod_evidence_artifact", ""))).exists():
        errors.append("Goal2993 L4 pod evidence artifact is missing")
    if roadmap.get("local_smoke_goal") != "Goal2992":
        errors.append("v2.6 roadmap must index Goal2992 as the local Linux smoke checkpoint")
    if "not_release_or_performance_evidence" not in str(roadmap.get("local_smoke_status", "")):
        errors.append("Goal2992 local smoke must not be treated as release or performance evidence")
    if not (root / str(roadmap.get("local_smoke_report", ""))).exists():
        errors.append("Goal2992 local smoke report is missing")
    if not (root / str(roadmap.get("local_smoke_artifact", ""))).exists():
        errors.append("Goal2992 local smoke artifact is missing")
    if roadmap.get("benchmark_demonstrator_goal") != "Goal2994":
        errors.append("v2.6 roadmap must index Goal2994 as the first benchmark-app demonstrator")
    if "not_speedup_evidence" not in str(roadmap.get("benchmark_demonstrator_status", "")):
        errors.append("Goal2994 benchmark demonstrator must not be treated as speedup evidence")
    if not (root / str(roadmap.get("benchmark_demonstrator_report", ""))).exists():
        errors.append("Goal2994 benchmark demonstrator report is missing")
    if not (root / str(roadmap.get("benchmark_demonstrator_artifact", ""))).exists():
        errors.append("Goal2994 benchmark demonstrator artifact is missing")
    if roadmap.get("benchmark_minmax_goal") != "Goal2995":
        errors.append("v2.6 roadmap must index Goal2995 as the RayDB min/max Numba demonstrator")
    if "all_five_scalar_modes" not in str(roadmap.get("benchmark_minmax_status", "")):
        errors.append("Goal2995 benchmark min/max status must cover all five scalar modes")
    if "not_speedup_evidence" not in str(roadmap.get("benchmark_minmax_status", "")):
        errors.append("Goal2995 benchmark min/max demonstrator must not be treated as speedup evidence")
    if not (root / str(roadmap.get("benchmark_minmax_report", ""))).exists():
        errors.append("Goal2995 benchmark min/max report is missing")
    if not (root / str(roadmap.get("benchmark_minmax_artifact", ""))).exists():
        errors.append("Goal2995 benchmark min/max artifact is missing")
    if roadmap.get("compact_mask_goal") != "Goal2997":
        errors.append("v2.6 roadmap must index Goal2997 as the Numba compact-mask demonstrator")
    if "compact_mask_i64" not in str(roadmap.get("compact_mask_status", "")):
        errors.append("Goal2997 compact-mask status must name compact_mask_i64")
    if "not_speedup_evidence" not in str(roadmap.get("compact_mask_status", "")):
        errors.append("Goal2997 compact-mask demonstrator must not be treated as speedup evidence")
    if not (root / str(roadmap.get("compact_mask_report", ""))).exists():
        errors.append("Goal2997 compact-mask report is missing")
    if not (root / str(roadmap.get("compact_mask_artifact", ""))).exists():
        errors.append("Goal2997 compact-mask artifact is missing")
    if roadmap.get("triangle_compact_mask_goal") != "Goal2999":
        errors.append("v2.6 roadmap must index Goal2999 as triangle-counting compact-mask app wiring")
    if "triangle_counting" not in str(roadmap.get("triangle_compact_mask_status", "")):
        errors.append("Goal2999 triangle compact-mask status must name triangle_counting")
    if "not_speedup_evidence" not in str(roadmap.get("triangle_compact_mask_status", "")):
        errors.append("Goal2999 triangle compact-mask wiring must not be treated as speedup evidence")
    if not (root / str(roadmap.get("triangle_compact_mask_report", ""))).exists():
        errors.append("Goal2999 triangle compact-mask wiring report is missing")
    if roadmap.get("triangle_compact_mask_pod_goal") != "Goal3000":
        errors.append("v2.6 roadmap must index Goal3000 as triangle-counting compact-mask pod evidence")
    if "l4_pod_conformance_passed" not in str(roadmap.get("triangle_compact_mask_pod_status", "")):
        errors.append("Goal3000 triangle compact-mask pod status must record L4 conformance")
    if "not_speedup_evidence" not in str(roadmap.get("triangle_compact_mask_pod_status", "")):
        errors.append("Goal3000 triangle compact-mask pod evidence must not be treated as speedup evidence")
    if not (root / str(roadmap.get("triangle_compact_mask_pod_report", ""))).exists():
        errors.append("Goal3000 triangle compact-mask pod report is missing")
    if not (root / str(roadmap.get("triangle_compact_mask_pod_artifact", ""))).exists():
        errors.append("Goal3000 triangle compact-mask pod artifact is missing")
    if roadmap.get("rayjoin_compact_mask_goal") != "Goal3002":
        errors.append("v2.6 roadmap must index Goal3002 as RayJoin compact-mask app wiring")
    if "rayjoin_v2_spatial_join" not in str(roadmap.get("rayjoin_compact_mask_status", "")):
        errors.append("Goal3002 RayJoin compact-mask status must name rayjoin_v2_spatial_join")
    if "not_speedup_evidence" not in str(roadmap.get("rayjoin_compact_mask_status", "")):
        errors.append("Goal3002 RayJoin compact-mask wiring must not be treated as speedup evidence")
    if not (root / str(roadmap.get("rayjoin_compact_mask_report", ""))).exists():
        errors.append("Goal3002 RayJoin compact-mask wiring report is missing")
    if roadmap.get("rayjoin_compact_mask_pod_goal") != "Goal3003":
        errors.append("v2.6 roadmap must index Goal3003 as RayJoin compact-mask pod evidence")
    if "l4_pod_conformance_passed" not in str(roadmap.get("rayjoin_compact_mask_pod_status", "")):
        errors.append("Goal3003 RayJoin compact-mask pod status must record L4 conformance")
    if "not_speedup_evidence" not in str(roadmap.get("rayjoin_compact_mask_pod_status", "")):
        errors.append("Goal3003 RayJoin compact-mask pod evidence must not be treated as speedup evidence")
    if not (root / str(roadmap.get("rayjoin_compact_mask_pod_report", ""))).exists():
        errors.append("Goal3003 RayJoin compact-mask pod report is missing")
    if not (root / str(roadmap.get("rayjoin_compact_mask_pod_artifact", ""))).exists():
        errors.append("Goal3003 RayJoin compact-mask pod artifact is missing")
    if roadmap.get("numba_grouped_arg_goal") != "Goal3006":
        errors.append("v2.6 roadmap must index Goal3006 as Numba grouped arg reducer preview")
    if "grouped_argmin_f64" not in str(roadmap.get("numba_grouped_arg_status", "")):
        errors.append("Goal3006 grouped arg status must name grouped_argmin_f64")
    if "grouped_argmax_f64" not in str(roadmap.get("numba_grouped_arg_status", "")):
        errors.append("Goal3006 grouped arg status must name grouped_argmax_f64")
    if "not_speedup_evidence" not in str(roadmap.get("numba_grouped_arg_status", "")):
        errors.append("Goal3006 grouped arg preview must not be treated as speedup evidence")
    if not (root / str(roadmap.get("numba_grouped_arg_report", ""))).exists():
        errors.append("Goal3006 grouped arg preview report is missing")
    if roadmap.get("numba_grouped_arg_pod_goal") != "Goal3007":
        errors.append("v2.6 roadmap must index Goal3007 as Numba grouped arg reducer pod evidence")
    if "l4_pod_conformance_passed" not in str(roadmap.get("numba_grouped_arg_pod_status", "")):
        errors.append("Goal3007 grouped arg pod status must record L4 conformance")
    if "not_speedup_evidence" not in str(roadmap.get("numba_grouped_arg_pod_status", "")):
        errors.append("Goal3007 grouped arg pod evidence must not be treated as speedup evidence")
    if not (root / str(roadmap.get("numba_grouped_arg_pod_report", ""))).exists():
        errors.append("Goal3007 grouped arg pod report is missing")
    if not (root / str(roadmap.get("numba_grouped_arg_pod_artifact", ""))).exists():
        errors.append("Goal3007 grouped arg pod artifact is missing")
    if roadmap.get("hausdorff_numba_witness_goal") != "Goal3010":
        errors.append("v2.6 roadmap must index Goal3010 as Hausdorff Numba witness app wiring")
    if "not_rt_core_path" not in str(roadmap.get("hausdorff_numba_witness_status", "")):
        errors.append("Goal3010 Hausdorff Numba witness status must keep the RT-core boundary")
    if not (root / str(roadmap.get("hausdorff_numba_witness_report", ""))).exists():
        errors.append("Goal3010 Hausdorff Numba witness report is missing")
    if roadmap.get("numba_pairwise_score_rows_goal") != "Goal3012":
        errors.append("v2.6 roadmap must index Goal3012 as Numba pairwise score-row generation")
    if "pairwise_l2_sq_score_rows_2d" not in str(roadmap.get("numba_pairwise_score_rows_status", "")):
        errors.append("Goal3012 pairwise score-row status must name pairwise_l2_sq_score_rows_2d")
    if "not_speedup_evidence" not in str(roadmap.get("numba_pairwise_score_rows_status", "")):
        errors.append("Goal3012 pairwise score-row work must not be treated as speedup evidence")
    if not (root / str(roadmap.get("numba_pairwise_score_rows_report", ""))).exists():
        errors.append("Goal3012 pairwise score-row report is missing")
    if roadmap.get("numba_pairwise_score_rows_pod_goal") != "Goal3013":
        errors.append("v2.6 roadmap must index Goal3013 as Hausdorff Numba score-row pod evidence")
    if "l4_pod_conformance_passed" not in str(roadmap.get("numba_pairwise_score_rows_pod_status", "")):
        errors.append("Goal3013 pod status must record L4 conformance")
    if "not_speedup_evidence" not in str(roadmap.get("numba_pairwise_score_rows_pod_status", "")):
        errors.append("Goal3013 pod evidence must not be treated as speedup evidence")
    if not (root / str(roadmap.get("numba_pairwise_score_rows_pod_report", ""))).exists():
        errors.append("Goal3013 pod report is missing")
    if not (root / str(roadmap.get("numba_pairwise_score_rows_pod_artifact", ""))).exists():
        errors.append("Goal3013 pod artifact is missing")
    if roadmap.get("numba_block_nearest_rows_goal") != "Goal3015":
        errors.append("v2.6 roadmap must index Goal3015 as Numba block-nearest row generation")
    if "pairwise_l2_sq_block_nearest_rows_2d" not in str(roadmap.get("numba_block_nearest_rows_status", "")):
        errors.append("Goal3015 block-nearest status must name pairwise_l2_sq_block_nearest_rows_2d")
    if "not_speedup_evidence" not in str(roadmap.get("numba_block_nearest_rows_status", "")):
        errors.append("Goal3015 block-nearest work must not be treated as speedup evidence")
    if not (root / str(roadmap.get("numba_block_nearest_rows_report", ""))).exists():
        errors.append("Goal3015 block-nearest report is missing")
    if roadmap.get("hausdorff_numba_dense_vs_block_goal") != "Goal3016":
        errors.append("v2.6 roadmap must index Goal3016 as Hausdorff dense-vs-block comparison")
    if "not_speedup_evidence" not in str(roadmap.get("hausdorff_numba_dense_vs_block_status", "")):
        errors.append("Goal3016 dense-vs-block comparison must not be treated as speedup evidence")
    if "block_nearest_is_memory_pressure_path" not in str(roadmap.get("hausdorff_numba_dense_vs_block_status", "")):
        errors.append("Goal3016 status must preserve the block-nearest memory-pressure boundary")
    if not (root / str(roadmap.get("hausdorff_numba_dense_vs_block_report", ""))).exists():
        errors.append("Goal3016 dense-vs-block report is missing")
    if not (root / str(roadmap.get("hausdorff_numba_dense_vs_block_artifact", ""))).exists():
        errors.append("Goal3016 dense-vs-block artifact is missing")
    if roadmap.get("numba_grouped_witness_no_host_sync_goal") != "Goal3017":
        errors.append("v2.6 roadmap must index Goal3017 as the Numba no-host-sync grouped witness fast path")
    if "not_speedup_evidence" not in str(roadmap.get("numba_grouped_witness_no_host_sync_status", "")):
        errors.append("Goal3017 fast path must not be treated as speedup evidence")
    if "skips_host_nan_validation" not in str(roadmap.get("numba_grouped_witness_no_host_sync_status", "")):
        errors.append("Goal3017 status must name skipped host NaN validation")
    if not (root / str(roadmap.get("numba_grouped_witness_no_host_sync_report", ""))).exists():
        errors.append("Goal3017 no-host-sync report is missing")
    if roadmap.get("hausdorff_numba_no_host_sync_comparison_goal") != "Goal3018":
        errors.append("v2.6 roadmap must index Goal3018 as the post-fast-path Hausdorff comparison")
    if "dense_device_score_rows_faster" not in str(roadmap.get("hausdorff_numba_no_host_sync_comparison_status", "")):
        errors.append("Goal3018 status must record dense device score rows as the current faster path")
    if "not_speedup_evidence" not in str(roadmap.get("hausdorff_numba_no_host_sync_comparison_status", "")):
        errors.append("Goal3018 comparison must not be treated as speedup evidence")
    if not (root / str(roadmap.get("hausdorff_numba_no_host_sync_comparison_report", ""))).exists():
        errors.append("Goal3018 comparison report is missing")
    if not (root / str(roadmap.get("hausdorff_numba_no_host_sync_comparison_artifact", ""))).exists():
        errors.append("Goal3018 comparison artifact is missing")
    if roadmap.get("l4_optix_readiness_goal") != "Goal3020":
        errors.append("v2.6 roadmap must index Goal3020 as the L4 OptiX readiness probe")
    if "ptx_vs_driver565" not in str(roadmap.get("l4_optix_readiness_status", "")):
        errors.append("Goal3020 status must record the PTX/driver blocker")
    if not (root / str(roadmap.get("l4_optix_readiness_report", ""))).exists():
        errors.append("Goal3020 L4 OptiX readiness report is missing")
    if roadmap.get("l4_optix_cuda126_smoke_goal") != "Goal3021":
        errors.append("v2.6 roadmap must index Goal3021 as the CUDA 12.6 L4 OptiX smoke unblock")
    if "cuda12_6" not in str(roadmap.get("l4_optix_cuda126_smoke_status", "")):
        errors.append("Goal3021 status must record the CUDA 12.6 side-by-side toolkit")
    if "not_speedup_evidence" not in str(roadmap.get("l4_optix_cuda126_smoke_status", "")):
        errors.append("Goal3021 smoke must not be treated as speedup evidence")
    if not (root / str(roadmap.get("l4_optix_cuda126_smoke_report", ""))).exists():
        errors.append("Goal3021 CUDA 12.6 OptiX smoke report is missing")
    if not (root / str(roadmap.get("l4_optix_cuda126_smoke_artifact", ""))).exists():
        errors.append("Goal3021 CUDA 12.6 OptiX smoke artifact is missing")
    if roadmap.get("hausdorff_optix_cupy_perf_probe_goal") != "Goal3022":
        errors.append("v2.6 roadmap must index Goal3022 as the Hausdorff OptiX/CuPy perf probe")
    if "cupy_grouped_grid_current_fast_reference" not in str(
        roadmap.get("hausdorff_optix_cupy_perf_probe_status", "")
    ):
        errors.append("Goal3022 status must keep CuPy grouped-grid as the current fast reference")
    if "not_speedup_evidence" not in str(roadmap.get("hausdorff_optix_cupy_perf_probe_status", "")):
        errors.append("Goal3022 perf probe must not be treated as speedup evidence")
    if not (root / str(roadmap.get("hausdorff_optix_cupy_perf_probe_report", ""))).exists():
        errors.append("Goal3022 Hausdorff OptiX/CuPy perf report is missing")
    if not (root / str(roadmap.get("hausdorff_optix_cupy_perf_probe_artifact", ""))).exists():
        errors.append("Goal3022 Hausdorff OptiX/CuPy perf artifact is missing")
    if roadmap.get("hausdorff_optix_group_sweep_goal") != "Goal3024":
        errors.append("v2.6 roadmap must index Goal3024 as the Hausdorff OptiX group sweep")
    if "cheap_tuning_does_not_close_gap" not in str(roadmap.get("hausdorff_optix_group_sweep_status", "")):
        errors.append("Goal3024 status must record that cheap tuning does not close the gap")
    if "not_speedup_evidence" not in str(roadmap.get("hausdorff_optix_group_sweep_status", "")):
        errors.append("Goal3024 group sweep must not be treated as speedup evidence")
    if not (root / str(roadmap.get("hausdorff_optix_group_sweep_report", ""))).exists():
        errors.append("Goal3024 Hausdorff OptiX group-sweep report is missing")
    if not (root / str(roadmap.get("hausdorff_optix_group_sweep_artifact", ""))).exists():
        errors.append("Goal3024 Hausdorff OptiX group-sweep artifact is missing")
    if roadmap.get("hausdorff_adaptive_reduced_probe_goal") != "Goal3025":
        errors.append("v2.6 roadmap must index Goal3025 as the Hausdorff adaptive-reduced probe")
    if "correct_but_slower" not in str(roadmap.get("hausdorff_adaptive_reduced_probe_status", "")):
        errors.append("Goal3025 status must record the correct-but-slower finding")
    if "not_promoted" not in str(roadmap.get("hausdorff_adaptive_reduced_probe_status", "")):
        errors.append("Goal3025 status must record that the adaptive-reduced probe is not promoted")
    if "not_speedup_evidence" not in str(roadmap.get("hausdorff_adaptive_reduced_probe_status", "")):
        errors.append("Goal3025 adaptive-reduced probe must not be treated as speedup evidence")
    if not (root / str(roadmap.get("hausdorff_adaptive_reduced_probe_report", ""))).exists():
        errors.append("Goal3025 Hausdorff adaptive-reduced report is missing")
    if not (root / str(roadmap.get("hausdorff_adaptive_reduced_probe_artifact", ""))).exists():
        errors.append("Goal3025 Hausdorff adaptive-reduced artifact is missing")
    if roadmap.get("hausdorff_raw_row_view_probe_goal") != "Goal3026":
        errors.append("v2.6 roadmap must index Goal3026 as the Hausdorff raw row-view probe")
    if "raw_row_view_faster_than_old_adaptive_rt" not in str(roadmap.get("hausdorff_raw_row_view_probe_status", "")):
        errors.append("Goal3026 status must record the raw row-view RT improvement")
    if "still_slower_than_cupy" not in str(roadmap.get("hausdorff_raw_row_view_probe_status", "")):
        errors.append("Goal3026 status must keep CuPy as the faster dense exact reference")
    if "not_public_speedup_evidence" not in str(roadmap.get("hausdorff_raw_row_view_probe_status", "")):
        errors.append("Goal3026 raw row-view probe must not be treated as public speedup evidence")
    if not (root / str(roadmap.get("hausdorff_raw_row_view_probe_report", ""))).exists():
        errors.append("Goal3026 Hausdorff raw row-view report is missing")
    if not (root / str(roadmap.get("hausdorff_raw_row_view_probe_artifact", ""))).exists():
        errors.append("Goal3026 Hausdorff raw row-view artifact is missing")
    if roadmap.get("hausdorff_raw_row_view_larger_scale_goal") != "Goal3028":
        errors.append("v2.6 roadmap must index Goal3028 as the larger-scale Hausdorff raw row-view probe")
    if "gap_narrows_but_no_crossover" not in str(roadmap.get("hausdorff_raw_row_view_larger_scale_status", "")):
        errors.append("Goal3028 status must record that the CuPy gap narrows but does not cross over")
    if "not_public_speedup_evidence" not in str(roadmap.get("hausdorff_raw_row_view_larger_scale_status", "")):
        errors.append("Goal3028 larger-scale probe must not be treated as public speedup evidence")
    if not (root / str(roadmap.get("hausdorff_raw_row_view_larger_scale_report", ""))).exists():
        errors.append("Goal3028 larger-scale Hausdorff report is missing")
    for artifact in roadmap.get("hausdorff_raw_row_view_larger_scale_artifacts", ()):
        if not (root / str(artifact)).exists():
            errors.append(f"Goal3028 larger-scale Hausdorff artifact is missing: {artifact}")
    if roadmap.get("numba_global_argmax_hardening_goal") != "Goal3036":
        errors.append("v2.6 roadmap must index Goal3036 as Numba global argmax hardening")
    if "block_reduce_no_global_atomics" not in str(roadmap.get("numba_global_argmax_hardening_status", "")):
        errors.append("Goal3036 status must record block-reduce replacement of global atomics")
    if "clean_composition_evidence_pending" not in str(roadmap.get("numba_global_argmax_hardening_status", "")):
        errors.append("Goal3036 status must keep clean composition evidence pending")
    if not (root / str(roadmap.get("numba_global_argmax_hardening_report", ""))).exists():
        errors.append("Goal3036 Numba global argmax hardening report is missing")
    if roadmap.get("point_group_nearest_numba_argmax_pod_goal") != "Goal3037":
        errors.append("v2.6 roadmap must index Goal3037 as point-group nearest to Numba argmax pod evidence")
    if "clean_a4000" not in str(roadmap.get("point_group_nearest_numba_argmax_pod_status", "")):
        errors.append("Goal3037 status must record clean A4000 evidence")
    if "not_release_not_speedup" not in str(roadmap.get("point_group_nearest_numba_argmax_pod_status", "")):
        errors.append("Goal3037 status must not be treated as release or speedup evidence")
    if "true_zero_copy_still_blocked" not in str(roadmap.get("point_group_nearest_numba_argmax_pod_status", "")):
        errors.append("Goal3037 status must keep true-zero-copy wording blocked")
    if not (root / str(roadmap.get("point_group_nearest_numba_argmax_pod_report", ""))).exists():
        errors.append("Goal3037 point-group nearest Numba argmax pod report is missing")
    if not (root / str(roadmap.get("point_group_nearest_numba_argmax_pod_artifact", ""))).exists():
        errors.append("Goal3037 point-group nearest Numba argmax pod artifact is missing")
    if roadmap.get("hausdorff_device_columns_numba_argmax_strategy_goal") != "Goal3039":
        errors.append("v2.6 roadmap must index Goal3039 as Hausdorff device-column Numba argmax strategy wiring")
    if "app_level_exact_hausdorff_strategy_wired" not in str(
        roadmap.get("hausdorff_device_columns_numba_argmax_strategy_status", "")
    ):
        errors.append("Goal3039 status must record app-level exact Hausdorff strategy wiring")
    if "pod_perf_evidence_pending" not in str(roadmap.get("hausdorff_device_columns_numba_argmax_strategy_status", "")):
        errors.append("Goal3039 status must keep pod performance evidence pending")
    if "not_speedup_evidence" not in str(roadmap.get("hausdorff_device_columns_numba_argmax_strategy_status", "")):
        errors.append("Goal3039 strategy wiring must not be treated as speedup evidence")
    if not (root / str(roadmap.get("hausdorff_device_columns_numba_argmax_strategy_report", ""))).exists():
        errors.append("Goal3039 Hausdorff device-column Numba argmax strategy report is missing")
    if roadmap.get("hausdorff_device_columns_numba_argmax_perf_goal") != "Goal3040":
        errors.append("v2.6 roadmap must index Goal3040 as Hausdorff device-column Numba argmax timing evidence")
    if "negative_perf_result" not in str(roadmap.get("hausdorff_device_columns_numba_argmax_perf_status", "")):
        errors.append("Goal3040 status must record the negative performance result")
    if "not_speedup_evidence" not in str(roadmap.get("hausdorff_device_columns_numba_argmax_perf_status", "")):
        errors.append("Goal3040 timing must not be treated as speedup evidence")
    if "active_set_candidate_frontier" not in str(roadmap.get("hausdorff_device_columns_numba_argmax_perf_status", "")):
        errors.append("Goal3040 status must name active-set/candidate-frontier as the next gap")
    if not (root / str(roadmap.get("hausdorff_device_columns_numba_argmax_perf_report", ""))).exists():
        errors.append("Goal3040 Hausdorff device-column Numba argmax perf report is missing")
    if not (root / str(roadmap.get("hausdorff_device_columns_numba_argmax_perf_artifact", ""))).exists():
        errors.append("Goal3040 Hausdorff device-column Numba argmax perf artifact is missing")
    if roadmap.get("point_group_active_frontier_goal") != "Goal3042":
        errors.append("v2.6 roadmap must index Goal3042 as point-group active-frontier witness selection")
    if "generic_optix_active_frontier" not in str(roadmap.get("point_group_active_frontier_status", "")):
        errors.append("Goal3042 status must record the generic active-frontier primitive")
    if "a4000_positive_perf_evidence" not in str(roadmap.get("point_group_active_frontier_status", "")):
        errors.append("Goal3042 status must record the A4000 positive performance evidence")
    if "external_review_pending" not in str(roadmap.get("point_group_active_frontier_status", "")):
        errors.append("Goal3042 status must keep external review pending")
    if "not_public_speedup_evidence" not in str(roadmap.get("point_group_active_frontier_status", "")):
        errors.append("Goal3042 active-frontier work must not be treated as public speedup evidence")
    if not (root / str(roadmap.get("point_group_active_frontier_report", ""))).exists():
        errors.append("Goal3042 point-group active-frontier report is missing")
    if not (root / str(roadmap.get("point_group_active_frontier_artifact", ""))).exists():
        errors.append("Goal3042 point-group active-frontier artifact is missing")
    if roadmap.get("hausdorff_witness_index_cleanup_goal") != "Goal3044":
        errors.append("v2.6 roadmap must index Goal3044 as the Hausdorff witness-index cleanup")
    if "original_target_columns" not in str(roadmap.get("hausdorff_witness_index_cleanup_status", "")):
        errors.append("Goal3044 status must record original target-column witness mapping")
    if "a4000_smoke_passed" not in str(roadmap.get("hausdorff_witness_index_cleanup_status", "")):
        errors.append("Goal3044 status must record A4000 smoke evidence")
    if "not_native_or_speedup_work" not in str(roadmap.get("hausdorff_witness_index_cleanup_status", "")):
        errors.append("Goal3044 status must not be treated as native or speedup work")
    if not (root / str(roadmap.get("hausdorff_witness_index_cleanup_report", ""))).exists():
        errors.append("Goal3044 Hausdorff witness-index cleanup report is missing")
    if not (root / str(roadmap.get("hausdorff_witness_index_cleanup_artifact", ""))).exists():
        errors.append("Goal3044 Hausdorff witness-index cleanup artifact is missing")
    if roadmap.get("hausdorff_active_frontier_multitrial_goal") != "Goal3045":
        errors.append("v2.6 roadmap must index Goal3045 as active-frontier multitrial evidence")
    if "10_trial_median" not in str(roadmap.get("hausdorff_active_frontier_multitrial_status", "")):
        errors.append("Goal3045 status must record 10-trial median evidence")
    if "not_public_speedup_evidence" not in str(roadmap.get("hausdorff_active_frontier_multitrial_status", "")):
        errors.append("Goal3045 status must not be treated as public speedup evidence")
    if not (root / str(roadmap.get("hausdorff_active_frontier_multitrial_report", ""))).exists():
        errors.append("Goal3045 active-frontier multitrial report is missing")
    if not (root / str(roadmap.get("hausdorff_active_frontier_multitrial_artifact", ""))).exists():
        errors.append("Goal3045 active-frontier multitrial artifact is missing")
    if "numba" not in str(roadmap.get("primary_partner_track", "")):
        errors.append("v2.6 must name Numba as the first-class partner track")
    if "users_choose" not in str(roadmap.get("partner_choice_rule", "")):
        errors.append("v2.6 must keep partner choice user-owned")
    if "high_performance_support" not in str(roadmap.get("supported_partner_duty", "")):
        errors.append("v2.6 must state RTDL's duty for supported partners")
    if "reference_or_recommended" not in str(roadmap.get("benchmark_app_role", "")):
        errors.append("v2.6 must keep benchmark apps as reference/recommended implementations")
    if "app_agnostic" not in str(roadmap.get("generic_engine_boundary", "")):
        errors.append("v2.6 must preserve the app-agnostic native-engine boundary")
    if "ignored" not in str(roadmap.get("triton_status", "")):
        errors.append("Triton must remain ignored for recommended v2.6 kickoff paths")
    demonstration = roadmap.get("minimum_demonstration", {})
    for field in (
        "one_benchmark_app_enough_for_initial_first_class_claim",
        "real_partner_continuation_required",
        "cpu_reference_parity_required",
        "partner_free_reference_path_required",
        "same_contract_perf_gate_required_before_speedup_claim",
    ):
        if demonstration.get(field) is not True:
            errors.append(f"{field} must remain true")
    steps = tuple(row.get("step") for row in roadmap.get("sequenced_work", ()))
    if steps != ("N-0", "N-1", "N-2", "N-3", "N-4"):
        errors.append("v2.6 roadmap step order must remain N-0 through N-4")
    if not (root / V2_6_CLAUDE_REFERENCE_REPORT).exists():
        errors.append("Claude v2.6 reference report is missing")
    for field in (
        "release_authorized",
        "public_speedup_claim_authorized",
        "rt_core_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
        "automatic_partner_selection_allowed",
        "automatic_triton_selection_allowed",
        "numba_speedup_claim_authorized",
        "app_specific_native_engine_logic_authorized",
    ):
        if roadmap.get(field) is not False:
            errors.append(f"{field} must remain false")
    return {
        "status": "accept" if not errors else "reject",
        "roadmap_version": roadmap.get("roadmap_version"),
        "errors": tuple(errors),
    }
