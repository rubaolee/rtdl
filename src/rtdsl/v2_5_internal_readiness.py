from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .partner_continuation_protocol import validate_v2_5_partner_continuation_contract
from .partner_continuation_protocol import validate_v2_5_partner_preview_gate
from .v2_5_determinism_policy import validate_v2_5_continuation_determinism_policies
from .v2_5_execution_path_policy import validate_v2_5_execution_path_policy
from .v2_5_partner_selection_guidance import validate_v2_5_partner_selection_guidance
from .v2_5_partner_conformance_matrix import validate_v2_5_partner_conformance_matrix
from .v2_5_partner_conformance_matrix import v2_5_partner_conformance_matrix
from .v2_5_partner_support_matrix import validate_v2_5_partner_support_matrix
from .v2_5_triton_app_migration import validate_v2_5_tiered_benchmark_manifest
from .v2_5_triton_app_migration import v2_5_tiered_benchmark_manifest
from .v2_5_triton_app_migration import v2_5_triton_front_door_coverage


V2_5_INTERNAL_READINESS_PACKET_VERSION = "rtdl.v2_5.internal_readiness_packet.v1"
V2_5_INTERNAL_READINESS_STATUS = "internal_evidence_packet_coherent_not_release_ready"
V2_5_INTERNAL_READINESS_CLAIM_BOUNDARY = (
    "v2.5 internal readiness means the current source-tree evidence packet is "
    "coherent for engineering review. It does not authorize release, public "
    "speedup wording, broad RT-core wording, whole-app speedup wording, true "
    "zero-copy wording, package-install wording, Triton preview auto-selection, "
    "or app-specific native engine logic."
)

V2_5_INTERNAL_READINESS_REQUIRED_REPORTS = (
    "docs/reports/goal2773_v2_5_status_next_goals_review_packet_2026-05-31.md",
    "docs/reports/goal2774_v2_5_grouped_hit_stream_support_matrix_2026-05-31.md",
    "docs/reports/goal2775_hit_stream_neutral_seam_reconciliation_2026-05-31.md",
    "docs/reports/goal2776_v2_5_grouped_argmax_witness_reduction_2026-05-31.md",
    "docs/reports/goal2777_v2_5_grouped_topk_ranked_summary_2026-05-31.md",
    "docs/reports/goal2778_v2_5_grouped_vector_sum_2026-05-31.md",
    "docs/reports/goal2779_v2_5_edge_list_components_2026-05-31.md",
    "docs/reports/goal2780_topk_adapter_triton_grouped_topk_2026-05-31.md",
    "docs/reports/goal2781_grouped_vector_sum_adapter_2026-05-31.md",
    "docs/reports/goal2782_v2_5_partner_selection_guidance_2026-05-31.md",
    "docs/reports/goal2783_v2_5_app_migration_selection_guidance_2026-05-31.md",
    "docs/reports/goal2784_dense_point_topk_triton_adapter_kernel_2026-05-31.md",
    "docs/reports/goal2785_presegmented_vector_sum_triton_offsets_2026-05-31.md",
    "docs/reports/goal2786_batched_vector_sum_offsets_tuning_2026-05-31.md",
    "docs/reports/goal2787_hausdorff_generic_argmin_argmax_triton_adapter_2026-05-31.md",
    "docs/reports/goal2788_dense_point_nearest_hausdorff_strategy_2026-05-31.md",
    "docs/reports/goal2789_neutral_buffer_torch_carrier_reconciliation_2026-05-31.md",
    "docs/reports/goal2790_tiled_dense_point_nearest_hausdorff_strategy_2026-05-31.md",
    "docs/reports/goal2792_partner_selection_explain_plan_2026-05-31.md",
    "docs/reports/goal2793_v2_5_partner_role_reconciliation_2026-05-31.md",
    "docs/reports/goal2794_v2_5_continuation_determinism_policy_2026-05-31.md",
    "docs/reports/goal2795_v2_5_tier_label_reconciliation_2026-05-31.md",
    "docs/reports/goal2796_raydb_scalar_reduction_selection_guidance_2026-05-31.md",
    "docs/reports/goal2797_triangle_counting_v2_5_canonical_harness_2026-05-31.md",
    "docs/reports/goal2798_librts_v2_5_warm_median_harness_2026-05-31.md",
    "docs/reports/goal2799_spatial_rayjoin_v2_5_prepared_count_harness_2026-05-31.md",
    "docs/reports/goal2800_rtnn_v2_5_live_ranked_summary_harness_2026-05-31.md",
    "docs/reports/goal2801_hausdorff_xhd_v2_5_canonical_entrypoint_2026-05-31.md",
    "docs/reports/goal2802_rt_dbscan_v2_5_live_grouped_stream_harness_2026-05-31.md",
    "docs/reports/goal2803_barnes_hut_v2_5_consolidated_harness_2026-05-31.md",
    "docs/reports/goal2804_v2_5_clean_artifact_metadata_refresh_2026-05-31.md",
    "docs/reports/goal2805_v2_5_broad_clean_pod_regression_gate_2026-05-31.md",
    "docs/reports/goal2835_primitive_payload_entrypoint_metadata_2026-05-31.md",
    "docs/reports/goal2836_goal2835_primitive_payload_entrypoint_metadata_consensus_2026-05-31.md",
    "docs/reports/goal2837_fixed_radius_graph_entrypoint_metadata_2026-05-31.md",
    "docs/reports/goal2838_goal2837_fixed_radius_graph_entrypoint_metadata_consensus_2026-05-31.md",
    "docs/reports/goal2839_rtnn_same_stream_runner_mode_2026-05-31.md",
    "docs/reports/goal2840_goal2839_rtnn_same_stream_runner_mode_consensus_2026-05-31.md",
    "docs/reports/goal2841_rtnn_same_stream_scale_probe_2026-05-31.md",
    "docs/reports/goal2842_goal2841_rtnn_same_stream_scale_probe_consensus_2026-05-31.md",
    "docs/reports/goal2843_v2_5_execution_path_policy_2026-05-31.md",
    "docs/reports/goal2844_goal2843_execution_path_policy_consensus_2026-05-31.md",
    "docs/reports/goal2847_current_head_canonical_harness_refresh_2026-05-31.md",
    "docs/reports/goal2848_goal2847_current_head_canonical_harness_consensus_2026-05-31.md",
    "docs/reports/goal2851_barnes_hut_harness_progress_logging_2026-05-31.md",
    "docs/reports/goal2852_goal2851_barnes_hut_progress_logging_consensus_2026-05-31.md",
    "docs/reports/goal2855_v2_5_current_canonical_harness_packet_runner_2026-05-31.md",
    "docs/reports/goal2856_goal2855_v2_5_canonical_packet_runner_consensus_2026-05-31.md",
    "docs/reports/goal2861_v2_5_generic_partner_front_door_completion_2026-05-31.md",
    "docs/reports/goal2862_goal2861_generic_front_door_completion_consensus_2026-05-31.md",
    "docs/reports/goal2865_current_head_packet_after_front_doors_2026-05-31.md",
    "docs/reports/goal2866_goal2865_current_head_packet_consensus_2026-05-31.md",
    "docs/reports/goal2867_v2_5_app_facing_front_door_bypass_audit_2026-05-31.md",
    "docs/reports/goal2869_v2_5_readiness_indexes_front_door_bypass_audit_2026-05-31.md",
    "docs/reports/goal2870_v2_5_last_day_review_intake_and_runner_fail_closed_hardening_2026-05-31.md",
    "docs/reports/goal2870_goal2868_last_day_review_intake_consensus_2026-05-31.md",
    "docs/reports/goal2871_hit_stream_torch_carrier_seam_authority_guard_2026-05-31.md",
    "docs/reports/goal2872_triton_tie_break_conformance_smoke_2026-05-31.md",
    "docs/reports/goal2873_v2_5_partner_conformance_matrix_2026-05-31.md",
    "docs/reports/goal2874_triton_preview_current_pod_conformance_backfill_2026-05-31.md",
    "docs/reports/goal2875_numba_runtime_conformance_smoke_2026-05-31.md",
    "docs/reports/goal2876_current_packet_after_partner_conformance_closure_2026-05-31.md",
    "docs/reports/goal2878_goal2868_residual_closure_map_after_conformance_2026-05-31.md",
    "docs/reports/goal2879_torch_carrier_seam_authority_provenance_2026-05-31.md",
    "docs/reports/goal2880_current_packet_after_torch_carrier_provenance_2026-05-31.md",
    "docs/reports/goal2883_torch_carrier_runtime_seam_trace_2026-05-31.md",
    "docs/reports/goal2885_v2_5_partner_conformance_readiness_snapshot_2026-05-31.md",
    "docs/reports/goal2887_goal2886_review_intake_and_carrier_authority_field_rename_2026-05-31.md",
    "docs/reports/goal2889_torch_carrier_copy_decision_seam_lease_wrap_2026-05-31.md",
    "docs/reports/goal2891_runtime_provenance_index_in_conformance_snapshot_2026-05-31.md",
    "docs/reports/goal2893_current_packet_after_runtime_provenance_index_2026-05-31.md",
    "docs/reports/goal2896_raydb_same_contract_performance_decision_gate_2026-05-31.md",
    "docs/reports/goal2898_raydb_perf_gate_readiness_integration_2026-05-31.md",
    "docs/reports/goal2901_goal2897_raydb_perf_gate_review_intake_2026-05-31.md",
    "docs/reports/goal2902_current_packet_perf_triage_2026-05-31.md",
    "docs/reports/goal2903_hausdorff_reduced_bbox_default_2026-05-31.md",
    "docs/reports/goal2904_current_packet_after_hausdorff_fix_2026-05-31.md",
    "docs/reports/goal2905_barnes_hut_measured_partner_selection_2026-05-31.md",
    "docs/reports/goal2906_current_packet_after_partner_selection_2026-05-31.md",
    "docs/reports/goal2907_hausdorff_repeat_stability_and_rtnn_near_parity_2026-05-31.md",
    "docs/reports/goal2908_current_packet_after_repeat9_2026-05-31.md",
    "docs/reports/goal2909_rtnn_repeat_stability_2026-05-31.md",
    "docs/reports/goal2911_scale_stable_canonical_perf_rows_2026-05-31.md",
    "docs/reports/goal2912_current_packet_scaled_defaults_2026-05-31.md",
    "docs/reports/goal2915_goal2912_scaled_v2_5_packet_external_review_consensus_2026-06-01.md",
    "docs/reports/goal2916_packet_toolchain_provenance_metadata_2026-06-01.md",
    "docs/reports/goal2917_current_packet_with_toolchain_provenance_2026-06-01.md",
    "docs/reports/goal2920_rtnn_hausdorff_large_scale_stability_and_hd_default_2026-06-01.md",
    "docs/reports/goal2921_current_packet_after_hausdorff_target4096_2026-06-01.md",
    "docs/reports/goal2923_goal2920_2921_stability_review_consensus_2026-06-01.md",
    "docs/reports/goal2924_hausdorff_prepared_radius_guard_second_arch_smoke_2026-06-01.md",
    "docs/reports/goal2925_current_packet_after_radius_guard_2026-06-01.md",
    "docs/reports/goal2928_goal2924_2925_radius_guard_packet_consensus_2026-06-01.md",
    "docs/reports/goal2929_tier_c_no_regression_and_10_benchmark_foundation_2026-06-01.md",
    "docs/reports/goal2931_goal2929_tier_c_10_benchmark_consensus_2026-06-01.md",
    "docs/reports/goal2932_cupy_presegmented_vector_sum_partner_2026-06-01.md",
    "docs/reports/goal2933_barnes_hut_cupy_vector_selection_2026-06-01.md",
    "docs/reports/goal2934_current_packet_after_cupy_vector_2026-06-01.md",
    "docs/reports/goal2936_measured_vector_partner_selection_helper_2026-06-01.md",
    "docs/reports/goal2937_measured_vector_partner_selection_pod_smoke_2026-06-01.md",
    "docs/reports/goal2938_optix_row_view_typed_partner_columns_2026-06-01.md",
    "docs/reports/goal2939_rayjoin_row_view_partner_columns_pod_smoke_2026-06-01.md",
    "docs/reports/goal2941_rayjoin_row_view_partner_columns_scale_probe_2026-06-01.md",
    "docs/reports/goal2942_current_packet_after_row_columns_2026-06-01.md",
    "docs/reports/goal2943_generic_event_ordered_hit_stream_front_door_2026-06-01.md",
    "docs/reports/goal2945_current_packet_after_hit_stream_front_door_2026-06-01.md",
    "docs/reports/goal2947_generic_event_ordered_payload_grouped_sum_front_door_2026-06-01.md",
    "docs/reports/goal2948_payload_grouped_sum_scale_probe_2026-06-01.md",
    "docs/reports/goal2950_raydb_payload_grouped_sum_front_door_probe_2026-06-01.md",
    "docs/reports/goal2952_hausdorff_target8192_default_tuning_2026-06-01.md",
    "docs/reports/goal2954_rtnn_graph_replay_route_tuning_2026-06-01.md",
    "docs/reports/goal2955_current_packet_after_rtnn_graph_replay_2026-06-01.md",
    "docs/reports/goal2958_rtnn_graph_replay_scale_chunking_2026-06-01.md",
    "docs/reports/goal2959_current_packet_after_rtnn_chunking_2026-06-01.md",
    "docs/reports/goal2962_large_scale_v2_5_stress_probe_2026-06-01.md",
)

V2_5_INTERNAL_READINESS_TIER_B_CLEAN_ARTIFACTS = {
    "rtnn": (
        "docs/reports/goal2800_pod_artifacts/"
        "rtnn_v25_live_ranked_summary_65536_clean_from_git.json"
    ),
    "hausdorff_xhd": (
        "docs/reports/goal2801_pod_artifacts/"
        "hausdorff_xhd_v25_canonical_entrypoint_4096_clean_from_git.json"
    ),
    "rt_dbscan": (
        "docs/reports/goal2802_pod_artifacts/"
        "rt_dbscan_v25_live_grouped_stream_32768_65536_131072_clean_from_git.json"
    ),
    "barnes_hut": (
        "docs/reports/goal2803_pod_artifacts/"
        "barnes_hut_v25_consolidated_harness_clean_from_git.json"
    ),
}

V2_5_INTERNAL_READINESS_CURRENT_CANONICAL_HARNESS_SUMMARY = (
    "docs/reports/goal2847_current_head_canonical_harness_pod/goal2847_summary.json"
)
V2_5_INTERNAL_READINESS_CURRENT_CANONICAL_HARNESS_ARTIFACTS = (
    "docs/reports/goal2847_current_head_canonical_harness_pod/goal2797_triangle_counting.json",
    "docs/reports/goal2847_current_head_canonical_harness_pod/goal2798_librts.json",
    "docs/reports/goal2847_current_head_canonical_harness_pod/goal2799_spatial_rayjoin.json",
    "docs/reports/goal2847_current_head_canonical_harness_pod/goal2800_rtnn.json",
    "docs/reports/goal2847_current_head_canonical_harness_pod/goal2801_hausdorff_xhd.json",
    "docs/reports/goal2847_current_head_canonical_harness_pod/goal2802_rt_dbscan.json",
    "docs/reports/goal2847_current_head_canonical_harness_pod/goal2803_barnes_hut.json",
)
V2_5_INTERNAL_READINESS_CURRENT_CANONICAL_RUNNER_SUMMARY = (
    "docs/reports/goal2959_current_packet_after_rtnn_chunk_pod/goal2855_summary.json"
)
V2_5_INTERNAL_READINESS_CURRENT_PACKET_PERF_TRIAGE = (
    "docs/reports/goal2959_current_packet_after_rtnn_chunk_pod/goal2959_triage.json"
)

V2_5_INTERNAL_READINESS_REQUIRED_EXTERNAL_REVIEW_PATHS = (
    "docs/reviews/goal2773_claude_review_v2_5_status_next_goals_2026-05-31.md",
    "docs/reviews/goal2800_claude_review_rtnn_live_ranked_summary_harness_2026-05-31.md",
    "docs/reviews/goal2801_claude_review_hausdorff_xhd_canonical_entrypoint_2026-05-31.md",
    "docs/reviews/goal2802_claude_review_rt_dbscan_live_grouped_stream_harness_2026-05-31.md",
    "docs/reviews/goal2802_gemini_review_rt_dbscan_live_grouped_stream_harness_2026-05-31.md",
    "docs/reviews/goal2803_claude_review_barnes_hut_consolidated_harness_2026-05-31.md",
    "docs/reviews/goal2803_gemini_review_barnes_hut_consolidated_harness_2026-05-31.md",
    "docs/reviews/goal2804_gemini_review_v2_5_clean_artifact_metadata_refresh_2026-05-31.md",
    "docs/reviews/goal2806_claude_review_v2_5_internal_readiness_packet_2026-05-31.md",
    "docs/reviews/goal2806_gemini_review_v2_5_internal_readiness_packet_2026-05-31.md",
    "docs/reviews/goal2836_gemini_review_goal2835_primitive_payload_entrypoint_metadata_2026-05-31.md",
    "docs/reviews/goal2838_gemini_review_goal2837_fixed_radius_graph_entrypoint_metadata_2026-05-31.md",
    "docs/reviews/goal2840_gemini_review_goal2839_rtnn_same_stream_runner_mode_2026-05-31.md",
    "docs/reviews/goal2842_gemini_review_goal2841_rtnn_same_stream_scale_probe_2026-05-31.md",
    "docs/reviews/goal2844_gemini_review_goal2843_execution_path_policy_2026-05-31.md",
    "docs/reviews/goal2848_gemini_review_goal2847_current_head_canonical_harness_2026-05-31.md",
    "docs/reviews/goal2852_gemini_review_goal2851_barnes_hut_progress_logging_2026-05-31.md",
    "docs/reviews/goal2856_gemini_review_goal2855_v2_5_canonical_packet_runner_2026-05-31.md",
    "docs/reviews/goal2862_gemini_review_goal2861_generic_front_door_completion_2026-05-31.md",
    "docs/reviews/goal2866_gemini_review_goal2865_current_head_packet_2026-05-31.md",
    "docs/reviews/goal2868_claude_review_v2_5_last_day_work_since_claude_reviews_2026-05-31.md",
    "docs/reviews/goal2868_gemini_review_v2_5_last_day_work_since_claude_reviews_2026-05-31.md",
    "docs/reviews/goal2881_claude_review_v2_5_residual_closure_and_current_packet_2026-05-31.md",
    "docs/reviews/goal2886_claude_review_runtime_trace_and_conformance_snapshot_2026-05-31.md",
    "docs/reviews/goal2897_external_review_goal2896_raydb_same_contract_perf_gate_2026-05-31.md",
    "docs/reviews/goal2913_gemini_review_goal2907_2912_scaled_v2_5_perf_packet_2026-05-31.md",
    "docs/reviews/goal2914_claude_review_goal2907_2912_scaled_v2_5_perf_packet_2026-05-31.md",
    "docs/reviews/goal2922_gemini_review_goal2920_2921_rtnn_hausdorff_stability_2026-06-01.md",
    "docs/reviews/goal2926_gemini_review_goal2924_2925_radius_guard_packet_2026-06-01.md",
    "docs/reviews/goal2930_gemini_review_goal2929_tier_c_10_benchmark_foundation_2026-06-01.md",
    "docs/reviews/goal2956_gemini_review_goal2955_zero_target_packet_2026-06-01.md",
    "docs/reviews/goal2957_claude_review_goal2955_zero_target_packet_2026-06-01.md",
    "docs/reviews/goal2960_gemini_review_goal2958_2959_rtnn_chunk_packet_2026-06-01.md",
    "docs/reviews/goal2961_claude_review_goal2958_2959_rtnn_chunk_packet_2026-06-01.md",
)

V2_5_INTERNAL_READINESS_BLOCKED_ACTIONS = (
    "v2_5_release",
    "release_tag_action",
    "public_speedup_wording",
    "broad_rt_core_speedup_wording",
    "whole_app_speedup_wording",
    "true_zero_copy_wording",
    "package_install_wording",
    "triton_preview_auto_selection",
    "native_app_specific_engine_logic",
)

V2_5_INTERNAL_READINESS_ALLOWED_NEXT_ACTIONS = (
    "keep_goal2855_current_canonical_packet_runner_green",
    "keep_goal2867_front_door_bypass_audit_green",
    "triage_goal2868_last_day_external_review_before_any_release_packet",
    "use_goal2878_to_distinguish_goal2868_historical_residuals_from_post_goal2873_closure",
    "request_goal2877_external_review_for_goal2873_to_goal2876_conformance_closure",
    "keep_goal2879_torch_carrier_seam_authority_provenance_green",
    "triage_goal2881_claude_review_before_any_release_packet",
    "keep_goal2883_runtime_seam_trace_green",
    "keep_goal2885_partner_conformance_snapshot_green",
    "triage_goal2886_claude_review_before_any_release_packet",
    "keep_goal2887_carrier_authority_field_rename_green",
    "keep_goal2889_copy_decision_seam_lease_wrap_green",
    "keep_goal2891_runtime_provenance_snapshot_green",
    "keep_goal2896_raydb_same_contract_perf_gate_green",
    "triage_goal2897_external_review_for_goal2896_raydb_perf_gate",
    "track_goal2897_compiler_flag_alignment_before_release_packet",
    "track_goal2897_multivendor_or_second_arch_perf_check_before_release_packet",
    "use_goal2902_current_packet_perf_triage_for_next_perf_targets",
    "keep_goal2903_hausdorff_reduced_bbox_default_green",
    "keep_goal2905_measured_partner_selection_green",
    "use_goal2907_repeat_stability_for_short_row_perf_triage",
    "use_goal2908_current_packet_after_repeat9_for_rtnn_stability_followup",
    "use_goal2909_rtnn_repeat_stability_for_distribution_dependent_perf_triage",
    "use_goal2911_scaled_canonical_rows_for_short_row_perf_stability",
    "keep_goal2912_scaled_current_packet_green",
    "keep_goal2915_scaled_packet_external_review_consensus_green",
    "keep_goal2916_toolchain_provenance_metadata_green",
    "keep_goal2917_toolchain_packet_green",
    "keep_goal2920_hausdorff_target4096_large_probe_green",
    "keep_goal2921_current_packet_after_hausdorff_target4096_green",
    "keep_goal2923_stability_review_consensus_green",
    "keep_goal2924_hausdorff_prepared_radius_guard_green",
    "keep_goal2925_current_packet_after_radius_guard_green",
    "keep_goal2928_radius_guard_packet_consensus_green",
    "keep_goal2929_tier_c_no_regression_foundation_green",
    "keep_goal2931_tier_c_10_benchmark_consensus_green",
    "keep_goal2932_cupy_vector_sum_preview_green",
    "keep_goal2933_barnes_hut_cupy_vector_selection_green",
    "keep_goal2934_current_packet_after_cupy_vector_green",
    "keep_goal2936_measured_vector_partner_selection_helper_green",
    "keep_goal2937_measured_vector_partner_selection_pod_smoke_green",
    "keep_goal2938_optix_row_view_typed_partner_columns_green",
    "keep_goal2939_rayjoin_row_view_partner_columns_pod_smoke_green",
    "keep_goal2941_rayjoin_row_view_partner_columns_scale_probe_green",
    "keep_goal2942_current_packet_after_row_columns_green",
    "keep_goal2943_generic_event_ordered_hit_stream_front_door_green",
    "keep_goal2945_current_packet_after_hit_stream_front_door_green",
    "keep_goal2947_payload_grouped_sum_front_door_green",
    "keep_goal2948_payload_grouped_sum_scale_probe_green",
    "keep_goal2950_raydb_payload_grouped_sum_planner_guard_green",
    "keep_goal2952_hausdorff_target8192_default_green",
    "keep_goal2954_rtnn_graph_replay_route_green",
    "keep_goal2955_current_packet_zero_perf_targets_green",
    "keep_goal2958_rtnn_graph_replay_scale_chunking_green",
    "keep_goal2959_current_packet_after_rtnn_chunking_green",
    "triage_goal2956_2957_zero_target_packet_reviews_before_release_packet",
    "triage_goal2960_2961_rtnn_chunk_packet_reviews_before_release_packet",
    "keep_goal2962_large_scale_stress_probe_green",
    "continue_internal_v2_5_hardening_or_prepare_user_requested_release_packet",
    "request_fresh_3ai_release_review_only_if_user_requests_release",
)


def v2_5_internal_readiness_packet(
    *, repo_root: str | Path | None = None
) -> dict[str, Any]:
    """Return the current v2.5 internal evidence index.

    This is a source-tree engineering gate. Passing it means the current
    v2.5 evidence packet is indexed, internally coherent, and bounded. It is
    intentionally not a release authorization.
    """

    root = Path.cwd() if repo_root is None else Path(repo_root)
    manifest = v2_5_tiered_benchmark_manifest()
    front_door_coverage = v2_5_triton_front_door_coverage()
    tier_b_artifacts = _tier_b_artifact_metadata(root)
    current_canonical_harness = _current_canonical_harness_metadata(root)
    current_canonical_runner = _current_canonical_runner_metadata(root)
    current_packet_perf_triage = _current_packet_perf_triage_metadata(root)
    partner_conformance_snapshot = _partner_conformance_snapshot()
    required_report_presence = _path_presence(root, V2_5_INTERNAL_READINESS_REQUIRED_REPORTS)
    review_presence = _path_presence(root, V2_5_INTERNAL_READINESS_REQUIRED_EXTERNAL_REVIEW_PATHS)

    return {
        "packet_version": V2_5_INTERNAL_READINESS_PACKET_VERSION,
        "status": V2_5_INTERNAL_READINESS_STATUS,
        "milestone": "v2.5",
        "scope": "internal_source_tree_engineering_readiness_index",
        "manifest": manifest,
        "front_door_coverage": front_door_coverage,
        "manifest_validation": validate_v2_5_tiered_benchmark_manifest(),
        "core_validations": {
            "partner_continuation_contract": validate_v2_5_partner_continuation_contract(),
            "partner_preview_gate": validate_v2_5_partner_preview_gate(),
            "partner_support_matrix": validate_v2_5_partner_support_matrix(),
            "partner_selection_guidance": validate_v2_5_partner_selection_guidance(
                repo_root=root
            ),
            "execution_path_policy": validate_v2_5_execution_path_policy(),
            "determinism_policy": validate_v2_5_continuation_determinism_policies(),
            "partner_conformance_matrix": validate_v2_5_partner_conformance_matrix(),
        },
        "benchmark_app_count": manifest["benchmark_app_count"],
        "tier_counts": manifest["tier_counts"],
        "tier_b_clean_artifacts": tier_b_artifacts,
        "tier_b_clean_artifact_count": len(tier_b_artifacts),
        "current_canonical_harness": current_canonical_harness,
        "current_canonical_runner": current_canonical_runner,
        "current_packet_perf_triage": current_packet_perf_triage,
        "partner_conformance_snapshot": partner_conformance_snapshot,
        "required_reports": V2_5_INTERNAL_READINESS_REQUIRED_REPORTS,
        "required_report_presence": required_report_presence,
        "missing_required_reports": tuple(
            path for path, present in required_report_presence.items() if not present
        ),
        "external_review_paths": V2_5_INTERNAL_READINESS_REQUIRED_EXTERNAL_REVIEW_PATHS,
        "external_review_presence": review_presence,
        "missing_external_reviews": tuple(
            path for path, present in review_presence.items() if not present
        ),
        "broad_clean_pod_gate": {
            "goal": "Goal2805",
            "commit": "6faf7de8",
            "test_modules": 50,
            "test_count": 239,
            "result": "OK",
            "report": (
                "docs/reports/"
                "goal2805_v2_5_broad_clean_pod_regression_gate_2026-05-31.md"
            ),
        },
        "claim_authorization": {
            "v2_5_release_authorized": False,
            "release_tag_action_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "package_install_claim_authorized": False,
            "triton_preview_auto_selection_authorized": False,
            "native_app_specific_engine_logic_authorized": False,
        },
        "blocked_actions": V2_5_INTERNAL_READINESS_BLOCKED_ACTIONS,
        "allowed_next_actions": V2_5_INTERNAL_READINESS_ALLOWED_NEXT_ACTIONS,
        "claim_boundary": V2_5_INTERNAL_READINESS_CLAIM_BOUNDARY,
    }


def validate_v2_5_internal_readiness_packet(
    *, repo_root: str | Path | None = None
) -> dict[str, Any]:
    packet = v2_5_internal_readiness_packet(repo_root=repo_root)
    errors: list[str] = []
    if packet["packet_version"] != V2_5_INTERNAL_READINESS_PACKET_VERSION:
        errors.append("unexpected v2.5 internal readiness packet version")
    if packet["status"] != V2_5_INTERNAL_READINESS_STATUS:
        errors.append("unexpected v2.5 internal readiness status")
    if packet["manifest_validation"]["status"] != "accept":
        errors.append("v2.5 tiered benchmark manifest does not validate")
    if packet["benchmark_app_count"] != 10:
        errors.append("v2.5 internal packet must cover exactly 10 benchmark apps")
    if packet["tier_counts"] != {"A": 3, "B": 4, "C": 3}:
        errors.append("v2.5 internal packet tier counts changed")
    front_door_coverage = packet["front_door_coverage"]
    if front_door_coverage["benchmark_app_count"] != 10:
        errors.append("v2.5 front-door coverage must cover exactly 10 benchmark apps")
    if front_door_coverage["fully_front_door_ready_count"] != 10:
        errors.append("all promoted v2.5 benchmark apps must have generic front-door coverage")
    for row in front_door_coverage["apps"]:
        if row["front_door_status"] != "adapter_front_door_ready":
            errors.append(f"{row['app_id']} is not adapter-front-door-ready")
        if tuple(row["dispatcher_only_operations"]) != ():
            errors.append(f"{row['app_id']} still has dispatcher-only front-door gaps")
        if tuple(row["missing_operations"]) != ():
            errors.append(f"{row['app_id']} still has missing front-door operations")
    for name, validation in packet["core_validations"].items():
        if validation["status"] != "accept":
            errors.append(f"core validation failed: {name}")
    if tuple(packet["missing_required_reports"]) != ():
        errors.append("required v2.5 reports are missing")
    if tuple(packet["missing_external_reviews"]) != ():
        errors.append("required v2.5 external review paths are missing")
    if packet["tier_b_clean_artifact_count"] != 4:
        errors.append("expected four Tier B clean artifacts")
    current_harness = packet["current_canonical_harness"]
    if current_harness.get("summary_status") != "pass":
        errors.append("current canonical harness summary did not pass")
    if current_harness.get("artifact_count") != 7:
        errors.append("expected seven current canonical harness artifacts")
    if not _looks_like_sha(str(current_harness.get("source_commit", ""))):
        errors.append("current canonical harness lacks source commit")
    for name, artifact in current_harness.get("artifacts", {}).items():
        if artifact.get("status") != "pass":
            errors.append(f"{name} current canonical artifact did not pass")
        if artifact.get("source_dirty") != []:
            errors.append(f"{name} current canonical artifact is not source clean")
        if artifact.get("source_commit") != current_harness.get("source_commit"):
            errors.append(f"{name} source commit differs from current canonical summary")
        if "NVIDIA" not in str(artifact.get("gpu", "")):
            errors.append(f"{name} current canonical artifact lacks NVIDIA pod identity")
    current_runner = packet["current_canonical_runner"]
    if current_runner.get("status") != "pass":
        errors.append("current canonical packet runner summary did not pass")
    if current_runner.get("returncode_ok") is not True:
        errors.append("current canonical packet runner child return codes were not all OK")
    if current_runner.get("artifact_status_ok") is not True:
        errors.append("current canonical packet runner artifact statuses were not all OK")
    if current_runner.get("source_commit_consistent") is not True:
        errors.append("current canonical packet runner source commits are inconsistent")
    if current_runner.get("artifact_count") != 7:
        errors.append("current canonical packet runner must cover seven artifacts")
    if current_runner.get("expected_artifact_count") != 7:
        errors.append("current canonical packet runner expected count changed")
    if current_runner.get("dirty_artifacts") != {}:
        errors.append("current canonical packet runner recorded dirty artifacts")
    if current_runner.get("claim_boundary_violations") != {}:
        errors.append("current canonical packet runner recorded claim-boundary violations")
    if not _looks_like_sha(str(current_runner.get("source_commit", ""))):
        errors.append("current canonical packet runner lacks source commit")
    toolchain = (current_runner.get("runner_metadata") or {}).get("toolchain") or {}
    if toolchain.get("metadata_version") != "rtdl.goal2916.toolchain_provenance.v1":
        errors.append("current canonical packet runner lacks Goal2916 toolchain metadata")
    if toolchain.get("rtdl_optix_ptx_compiler") != "nvcc":
        errors.append("current canonical packet runner must record nvcc PTX compiler")
    if toolchain.get("rtdl_optix_library_exists") is not True:
        errors.append("current canonical packet runner must record reachable RTDL OptiX library")
    if toolchain.get("optix_header_exists") is not True:
        errors.append("current canonical packet runner must record reachable OptiX header")
    if (toolchain.get("claim_boundary") or {}).get("compiler_fairness_claim_authorized") is not False:
        errors.append("toolchain metadata must not authorize compiler fairness claims")
    if (toolchain.get("claim_boundary") or {}).get("multivendor_claim_authorized") is not False:
        errors.append("toolchain metadata must not authorize multivendor claims")
    perf_triage = packet["current_packet_perf_triage"]
    if perf_triage.get("status") != "pass":
        errors.append("current packet performance triage did not pass")
    if perf_triage.get("performance_target_count") != 0:
        errors.append("current packet performance triage still has performance targets")
    if perf_triage.get("top_priority") is not None:
        errors.append("current packet performance triage top priority should be empty")
    conformance_snapshot = packet["partner_conformance_snapshot"]
    if conformance_snapshot["runtime_conformance_gap_count"] != 0:
        errors.append("partner conformance snapshot recorded runtime gaps")
    if conformance_snapshot["release_conformance_complete"] is not False:
        errors.append("partner conformance snapshot must keep release conformance false")
    if conformance_snapshot["preview_runtime_conformance_complete"] is not True:
        errors.append("partner conformance snapshot must keep preview runtime conformance complete")
    if conformance_snapshot["cell_count"] != 52:
        errors.append("partner conformance snapshot cell count changed")
    if conformance_snapshot["runtime_provenance_record_count"] != 1:
        errors.append("partner conformance snapshot must index the current runtime provenance record")
    for record in conformance_snapshot.get("runtime_provenance_records", ()):
        if record.get("status") != "pod_runtime_copy_decision_seam_wrapped":
            errors.append("runtime provenance record status changed")
        if record.get("goal2889_copy_decision_seam_wrap_indexed") is not True:
            errors.append("runtime provenance record lost copy-decision seam wrap")
        if record.get("goal2889_executed_conversion_seam_lease_indexed") is not True:
            errors.append("runtime provenance record lost executed conversion seam lease")
        if record.get("goal2883_same_pointer_evidence_indexed") is not True:
            errors.append("runtime provenance record lost observed pointer-equality evidence")
        if record.get("true_zero_copy_claim_authorized") is not False:
            errors.append("runtime provenance record must not authorize true zero-copy")
        if record.get("release_authorized") is not False:
            errors.append("runtime provenance record must not authorize release")
    for app_id, artifact in packet["tier_b_clean_artifacts"].items():
        if artifact.get("status") != "pass":
            errors.append(f"{app_id} clean artifact did not pass")
        if not _looks_like_sha(str(artifact.get("source_commit", ""))):
            errors.append(f"{app_id} clean artifact lacks source commit")
        if artifact.get("source_dirty") != []:
            errors.append(f"{app_id} clean artifact is not source clean")
        if "NVIDIA" not in str(artifact.get("gpu", "")):
            errors.append(f"{app_id} clean artifact lacks NVIDIA pod identity")
        boundary = artifact.get("claim_boundary", {})
        if isinstance(boundary, dict):
            for flag in (
                "public_speedup_claim_authorized",
                "whole_app_speedup_claim_authorized",
                "native_engine_customization",
            ):
                if boundary.get(flag) is not False:
                    errors.append(f"{app_id} clean artifact boundary changed: {flag}")
    for flag, value in packet["claim_authorization"].items():
        if value is not False:
            errors.append(f"v2.5 internal packet must not authorize {flag}")
    boundary = str(packet["claim_boundary"])
    for phrase in (
        "internal readiness",
        "does not authorize release",
        "public speedup wording",
        "broad RT-core wording",
        "whole-app speedup wording",
        "true zero-copy wording",
        "package-install wording",
        "Triton preview auto-selection",
        "app-specific native engine logic",
    ):
        if phrase not in boundary:
            errors.append("v2.5 internal readiness claim boundary is incomplete")
    return {
        "status": "accept" if not errors else "reject",
        "packet_version": packet["packet_version"],
        "benchmark_app_count": packet["benchmark_app_count"],
        "tier_counts": packet["tier_counts"],
        "tier_b_clean_artifact_count": packet["tier_b_clean_artifact_count"],
        "current_canonical_harness_artifact_count": packet["current_canonical_harness"]["artifact_count"],
        "current_canonical_runner_artifact_count": packet["current_canonical_runner"]["artifact_count"],
        "current_packet_perf_target_count": packet["current_packet_perf_triage"]["performance_target_count"],
        "broad_clean_pod_gate_result": packet["broad_clean_pod_gate"]["result"],
        "blocked_actions": packet["blocked_actions"],
        "errors": tuple(errors),
    }


def _path_presence(root: Path, paths: tuple[str, ...]) -> dict[str, bool]:
    return {path: (root / path).exists() for path in paths}


def _tier_b_artifact_metadata(root: Path) -> dict[str, dict[str, Any]]:
    artifacts: dict[str, dict[str, Any]] = {}
    for app_id, relative_path in V2_5_INTERNAL_READINESS_TIER_B_CLEAN_ARTIFACTS.items():
        path = root / relative_path
        if not path.exists():
            artifacts[app_id] = {"path": relative_path, "status": "missing"}
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        artifacts[app_id] = {
            "path": relative_path,
            "status": payload.get("status"),
            "source_commit": payload.get("source_commit"),
            "source_dirty": payload.get("source_dirty"),
            "gpu": payload.get("gpu"),
            "claim_boundary": payload.get("claim_boundary", {}),
        }
    return artifacts


def _current_canonical_harness_metadata(root: Path) -> dict[str, Any]:
    summary_path = root / V2_5_INTERNAL_READINESS_CURRENT_CANONICAL_HARNESS_SUMMARY
    if not summary_path.exists():
        return {
            "summary_path": V2_5_INTERNAL_READINESS_CURRENT_CANONICAL_HARNESS_SUMMARY,
            "summary_status": "missing",
            "source_commit": None,
            "artifact_count": 0,
            "artifacts": {},
        }
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    artifacts: dict[str, dict[str, Any]] = {}
    for relative_path in V2_5_INTERNAL_READINESS_CURRENT_CANONICAL_HARNESS_ARTIFACTS:
        path = root / relative_path
        name = path.name
        if not path.exists():
            artifacts[name] = {"path": relative_path, "status": "missing"}
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        artifacts[name] = {
            "path": relative_path,
            "goal": payload.get("goal"),
            "status": payload.get("status"),
            "source_commit": payload.get("source_commit"),
            "source_dirty": payload.get("source_dirty"),
            "gpu": payload.get("gpu"),
        }
    return {
        "summary_path": V2_5_INTERNAL_READINESS_CURRENT_CANONICAL_HARNESS_SUMMARY,
        "summary_status": "pass" if summary.get("all_pass") is True else "reject",
        "goal": summary.get("goal"),
        "source_commit": summary.get("source_commit"),
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "claim_boundary": (
            "The current canonical harness packet is engineering health evidence. "
            "It does not authorize v2.5 release or broad public speedup claims."
        ),
    }


def _current_canonical_runner_metadata(root: Path) -> dict[str, Any]:
    summary_path = root / V2_5_INTERNAL_READINESS_CURRENT_CANONICAL_RUNNER_SUMMARY
    if not summary_path.exists():
        return {
            "summary_path": V2_5_INTERNAL_READINESS_CURRENT_CANONICAL_RUNNER_SUMMARY,
            "status": "missing",
            "artifact_count": 0,
            "expected_artifact_count": 7,
            "source_commit": None,
        }
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    return {
        "summary_path": V2_5_INTERNAL_READINESS_CURRENT_CANONICAL_RUNNER_SUMMARY,
        "status": summary.get("status"),
        "all_pass": summary.get("all_pass"),
        "artifact_count": summary.get("artifact_count"),
        "expected_artifact_count": summary.get("expected_artifact_count"),
        "returncode_ok": summary.get("returncode_ok"),
        "artifact_status_ok": summary.get("artifact_status_ok"),
        "source_commit_consistent": summary.get("source_commit_consistent"),
        "source_commit": summary.get("source_commit"),
        "dirty_artifacts": summary.get("dirty_artifacts"),
        "claim_boundary_violations": summary.get("claim_boundary_violations"),
        "runner_metadata": summary.get("runner_metadata"),
        "claim_boundary": (
            "Goal2855 runner evidence is an operational readiness guard. "
            "It does not authorize v2.5 release or public performance claims."
        ),
    }


def _current_packet_perf_triage_metadata(root: Path) -> dict[str, Any]:
    triage_path = root / V2_5_INTERNAL_READINESS_CURRENT_PACKET_PERF_TRIAGE
    if not triage_path.exists():
        return {
            "path": V2_5_INTERNAL_READINESS_CURRENT_PACKET_PERF_TRIAGE,
            "status": "missing",
            "app_count": 0,
            "performance_target_count": None,
            "top_priority": None,
            "performance_targets": (),
        }
    triage = json.loads(triage_path.read_text(encoding="utf-8"))
    targets = tuple(triage.get("performance_targets", ()))
    apps = tuple(triage.get("apps", ()))
    return {
        "path": V2_5_INTERNAL_READINESS_CURRENT_PACKET_PERF_TRIAGE,
        "status": triage.get("status"),
        "app_count": len(apps),
        "performance_target_count": len(targets),
        "top_priority": triage.get("top_priority"),
        "performance_targets": targets,
        "claim_boundary": (
            "The current packet performance triage is an internal optimization index. "
            "Zero current targets does not authorize release or public speedup claims."
        ),
    }


def _partner_conformance_snapshot() -> dict[str, Any]:
    matrix = validate_v2_5_partner_conformance_matrix()
    full_matrix = v2_5_partner_conformance_matrix()
    cells = tuple(full_matrix["cells"])
    pod_runtime_cells = tuple(
        {
            "operation": cell["operation"],
            "partner": cell["partner"],
            "evidence_goal": cell["evidence_goal"],
        }
        for cell in cells
        if cell["conformance_status"] == "pod_cuda_runtime_smoke_recorded"
    )
    descriptor_only_cells = tuple(
        {
            "operation": cell["operation"],
            "partner": cell["partner"],
            "evidence_goal": cell["evidence_goal"],
        }
        for cell in cells
        if cell["conformance_status"] == "descriptor_only_no_generic_kernel"
    )
    runtime_provenance_records = _runtime_provenance_records()
    return {
        "matrix_version": full_matrix["matrix_version"],
        "status": matrix["status"],
        "allowed_partners": full_matrix["allowed_partners"],
        "operation_count": len(full_matrix["operations"]),
        "cell_count": full_matrix["cell_count"],
        "preview_runtime_conformance_complete": full_matrix["preview_runtime_conformance_complete"],
        "runtime_conformance_gap_count": full_matrix["runtime_conformance_gap_count"],
        "release_conformance_complete": full_matrix["release_conformance_complete"],
        "release_blocker_count": full_matrix["release_blocker_count"],
        "pod_runtime_cell_count": len(pod_runtime_cells),
        "descriptor_only_cell_count": len(descriptor_only_cells),
        "pod_runtime_cells": pod_runtime_cells,
        "descriptor_only_cells": descriptor_only_cells,
        "runtime_provenance_record_count": len(runtime_provenance_records),
        "runtime_provenance_records": runtime_provenance_records,
        "claim_boundary": (
            "This snapshot indexes partner conformance evidence for readiness review. "
            "It does not authorize release, public speedup claims, true-zero-copy "
            "claims, or Triton preview auto-selection."
        ),
    }


def _runtime_provenance_records() -> tuple[dict[str, Any], ...]:
    return (
        {
            "path": "bounded_triton_torch_carrier_typed_payload_gather",
            "partner": "triton",
            "carrier": "torch",
            "operation": "hit_stream_typed_payload_gather",
            "status": "pod_runtime_copy_decision_seam_wrapped",
            "evidence_goal": "Goal2889",
            "report_path": (
                "docs/reports/"
                "goal2889_torch_carrier_copy_decision_seam_lease_wrap_2026-05-31.md"
            ),
            "test_module": "tests.goal2889_torch_carrier_copy_decision_seam_lease_wrap_test",
            "same_pointer_evidence_goal": "Goal2883",
            "goal2883_same_pointer_evidence_indexed": True,
            "goal2889_copy_decision_seam_wrap_indexed": True,
            "goal2889_executed_conversion_seam_lease_indexed": True,
            "scope": (
                "runtime provenance for the bounded Triton torch-carrier gather path; "
                "not a release-grade proof for every future partner path"
            ),
            "public_speedup_claim_authorized": False,
            "broad_rt_core_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "triton_preview_auto_selection_authorized": False,
            "release_authorized": False,
        },
    )


def _looks_like_sha(value: str) -> bool:
    return len(value) == 40 and all(char in "0123456789abcdef" for char in value)
