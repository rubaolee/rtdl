#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

try:
    import v3_release_wording_gate
except ModuleNotFoundError:  # pragma: no cover - exercised by unittest import path.
    from scripts import v3_release_wording_gate

try:
    import v3_phoenix_secondary_platform_gate
except ModuleNotFoundError:  # pragma: no cover - exercised by unittest import path.
    from scripts import v3_phoenix_secondary_platform_gate

try:
    import v3_phoenix_install_reproducibility_gate
except ModuleNotFoundError:  # pragma: no cover - exercised by unittest import path.
    from scripts import v3_phoenix_install_reproducibility_gate

try:
    import v3_phoenix_next_engine_work_queue
except ModuleNotFoundError:  # pragma: no cover - exercised by unittest import path.
    from scripts import v3_phoenix_next_engine_work_queue

try:
    import v3_phoenix_release_surface_breadth_gate
except ModuleNotFoundError:  # pragma: no cover - exercised by unittest import path.
    from scripts import v3_phoenix_release_surface_breadth_gate

try:
    import v3_phoenix_objective_conformance_gate
except ModuleNotFoundError:  # pragma: no cover - exercised by unittest import path.
    from scripts import v3_phoenix_objective_conformance_gate

try:
    import v3_phoenix_external_verdict_intake
except ModuleNotFoundError:  # pragma: no cover - exercised by unittest import path.
    from scripts import v3_phoenix_external_verdict_intake

try:
    import v3_phoenix_major_performance_mandate_gate
except ModuleNotFoundError:  # pragma: no cover - exercised by unittest import path.
    from scripts import v3_phoenix_major_performance_mandate_gate


ROOT = Path(__file__).resolve().parents[1]

M7_PACKET = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m7_row_classification_packet_2026-06-20.json"
APP_CLASSIFICATION = ROOT / "docs" / "rebuild" / "v3" / "v3_benchmark_app_classification_2026-06-20.json"
RUNBOOK = ROOT / "docs" / "rebuild" / "v3" / "v3_setup_and_rerun_runbook_2026-06-20.md"
BLOCKERS = ROOT / "docs" / "rebuild" / "v3" / "v3_release_authorization_blockers_2026-06-20.md"
SIX_ROW_CONSENSUS = ROOT / "docs" / "reviews" / "codex_phoenix_v3_six_row_release_readiness_2ai_consensus_2026-06-21.md"
ELEVEN_ROW_CLAUDE_REVIEW = (
    ROOT / "docs" / "reviews" / "claude_phoenix_v3_eleven_row_release_readiness_review_2026-06-21.md"
)
ELEVEN_ROW_CONSENSUS = (
    ROOT / "docs" / "reviews" / "codex_phoenix_v3_eleven_row_release_readiness_2ai_consensus_2026-06-21.md"
)
DEVICE_COLUMN_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2ai_consensus_2026-06-21.md"
)
GOAL4392_AUDIT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_goal4392_alignment_audit_2026-06-20.md"
DESIGN_MANDATE = ROOT / "docs" / "reports" / "v3_0_design_intent_reconstruction_and_performance_mandate_2026-06-20.md"
SECONDARY_PLATFORM_STRATEGY = ROOT / "docs" / "rebuild" / "v3" / "v3_secondary_platform_strategy_2026-06-21.md"
INSTALL_REPRODUCIBILITY_STRATEGY = ROOT / "docs" / "rebuild" / "v3" / "v3_install_reproducibility_strategy_2026-06-21.md"
NEXT_ENGINE_WORK_QUEUE = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_next_generic_engine_work_queue_2026-06-21.md"
SECONDARY_HARDWARE_WAIVER_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_secondary_rt_hardware_scope_waiver_review_2026-06-21.md"
)
SECONDARY_HARDWARE_WAIVER_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_phoenix_v3_secondary_rt_hardware_scope_waiver_2ai_consensus_2026-06-21.md"
)
AGGREGATE_RELEASE_CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_aggregate_release_readiness_review_2026-06-21.md"
)
AGGREGATE_RELEASE_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_phoenix_v3_aggregate_release_readiness_2ai_consensus_2026-06-21.md"
)
TWELVE_ROW_POST_P1_CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_twelve_row_release_readiness_after_p1_fixes_compact_review_2026-06-21.md"
)
TWELVE_ROW_POST_P1_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_phoenix_v3_twelve_row_release_readiness_after_p1_fixes_2ai_consensus_2026-06-21.md"
)
FINAL_WORDING_GATE_CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_final_public_surface_wording_gate_upgrade_review_2026-06-21.md"
)
FINAL_WORDING_GATE_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_phoenix_v3_final_public_surface_wording_gate_upgrade_2ai_consensus_2026-06-21.md"
)
RELEASE_SURFACE_BREADTH_GATE_JSON = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_release_surface_breadth_gate_2026-06-21.json"
)
RELEASE_SURFACE_BREADTH_GATE_MD = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_release_surface_breadth_gate_2026-06-21.md"
)
RELEASE_SURFACE_BREADTH_CLAUDE_REVIEW = (
    ROOT / "docs" / "reviews" / "claude_phoenix_v3_release_surface_breadth_gate_review_2026-06-21.md"
)
RELEASE_SURFACE_BREADTH_CONSENSUS = (
    ROOT / "docs" / "reviews" / "codex_phoenix_v3_release_surface_breadth_gate_2ai_consensus_2026-06-21.md"
)
OBJECTIVE_CONFORMANCE_GATE_JSON = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_objective_conformance_gate_2026-06-22.json"
)
AGGREGATE_13_ROW_REVIEW_REQUEST = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_aggregate_release_readiness_13_row_2026-06-22.md"
)
EXTERNAL_VERDICT_RESPONSE_TEMPLATE = (
    ROOT / "docs" / "reviews" / "phoenix_v3_external_verdict_response_template_2026-06-22.md"
)
AGGREGATE_13_ROW_EXTERNAL_BLOCKED = (
    ROOT
    / "docs"
    / "reviews"
    / "external_ai_blocked_phoenix_v3_aggregate_release_readiness_13_row_after_dossier_2026-06-22.md"
)
AGGREGATE_13_ROW_CODEX_SUBAGENT_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_subagent_phoenix_v3_aggregate_release_readiness_13_row_review_2026-06-22.md"
)
AGGREGATE_13_ROW_FALLBACK_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_phoenix_v3_aggregate_release_readiness_13_row_2ai_fallback_consensus_2026-06-22.md"
)
EXTERNAL_VERDICT_INTAKE = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_external_verdict_intake_2026-06-22.json"
)
CORE_GAPS_EXTERNAL_REVIEW = (
    ROOT / "docs" / "reviews" / "claude_phoenix_v3_external_review_2026-06-22.md"
)
CORE_GAPS_EXTERNAL_INTAKE = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_core_gaps_external_verdict_intake_2026-06-22.json"
)
CORE_GAPS_EXTERNAL_STATUS = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_core_gaps_external_verdict_status_2026-06-22.md"
)
SET_A_SET_B_RELEASE_BAR_PROPOSAL = (
    ROOT / "docs" / "reviews" / "phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md"
)
BOUNDED_EXTERNAL_REVIEW_PROTOCOL = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_bounded_external_review_protocol_2026-06-22.md"
)
CURRENT_HANDOFF = ROOT / "docs" / "handoff" / "PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md"
REFRESH_LOCAL = ROOT / "docs" / "handoff" / "REFRESH_LOCAL_2026-04-13.md"
SURFACE_INTEGRITY_GATE_UPDATE_REPORT = (
    ROOT / "docs" / "reports" / "phoenix_v3_surface_integrity_gate_update_2026-06-22.md"
)
SHORT_USER_PATH_GUARD_UPDATE_REPORT = (
    ROOT / "docs" / "reports" / "phoenix_v3_short_user_path_guard_update_2026-06-22.md"
)
CURRENT_STATUS = ROOT / "docs" / "rebuild" / "v3" / "v3_current_status_2026-06-20.md"
READINESS_DISTANCE_PACKET = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_readiness_distance_packet_2026-06-22.md"
)
COMPLETION_AUDIT = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_release_completion_audit_2026-06-22.md"
)
PERFORMANCE_DOSSIER = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_user_facing_performance_dossier_2026-06-22.md"
)
MAJOR_PERFORMANCE_MANDATE = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_redo_mandate_major_version_performance_2026-06-22.md"
)
LATEST_FULL_MATRIX = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_latest_v3_rebuild_matrix_after_aabb_runner_m2_20260622.json"
)
AABB_RUNNER_M2_REPORT = (
    ROOT / "docs" / "reports" / "phoenix_v3_aabb_native_query_handle_runner_route_m2_2026-06-22.md"
)
SPATIAL_DEFAULT_PATH_CLAUDE_REVIEW = (
    ROOT / "docs" / "reviews" / "claude_phoenix_v3_spatial_default_path_promotion_review_2026-06-22.md"
)
SPATIAL_DEFAULT_PATH_CODEX_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_phoenix_v3_spatial_default_path_promotion_2ai_consensus_2026-06-22.md"
)
SPATIAL_SQUARED_BOUNDARY_CANDIDATE = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_spatial_relation_status_squared_boundary_candidate_2026-06-21.md"
)
SPATIAL_SQUARED_BOUNDARY_CANDIDATE_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_relation_status_squared_boundary_candidate_2026-06-21.json"
)
SPATIAL_TOPOLOGY_STREAM_REDO_ALIGNMENT = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_topology_stream_redo_alignment_2026-06-22.md"
)
THIRTEEN_ROW_SCOPE_EXTENSION_CANDIDATE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "v3_source_tree_pod_gated_thirteen_row_scope_extension_candidate_2026-06-22.md"
)
THIRTEEN_ROW_SCOPE_EXTENSION_REVIEW_REQUEST = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_source_tree_pod_gated_thirteen_row_scope_extension_2026-06-22.md"
)
THIRTEEN_ROW_SCOPE_EXTENSION_CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_source_tree_pod_gated_thirteen_row_scope_extension_review_2026-06-22.md"
)
THIRTEEN_ROW_SCOPE_EXTENSION_CODEX_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_phoenix_v3_source_tree_pod_gated_thirteen_row_scope_extension_2ai_consensus_2026-06-22.md"
)
SECONDARY_HARDWARE_SCOPE = "single_rtx_4000_ada_driver_550_127_05_pod"

EXPECTED_M7_ROWS = (
    "grouped_reduction_sum_scalar_broadcast_repeat100_262144",
    "grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups",
    "grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups",
    "aabb_candidate_stream_all_count_only_float32_32768",
    "aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50",
    "aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50",
    "rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02",
    "aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped",
    "component_union_clustered3d_65536_524288_repeat5_row_scoped",
    "prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream",
    "hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped",
    "collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped",
)
SPATIAL_SUPPLEMENTAL_M7_ROW = (
    "point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7"
)
EXPECTED_CURRENT_M7_ROWS = EXPECTED_M7_ROWS + (SPATIAL_SUPPLEMENTAL_M7_ROW,)

EXPECTED_APP_BOUNDARY_M7_ROWS = (
    "grouped_reduction_sum_scalar_broadcast_repeat100_262144",
    "grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups",
    "grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups",
    "aabb_candidate_stream_all_count_only_float32_32768",
    "component_union_clustered3d_65536_524288_repeat5_row_scoped",
    "prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream",
    "hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped",
    "collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped",
)

REQUIRED_BLOCKER_PHRASES = (
    "V3 major release requires broad V2.x performance superiority",
    "status: redo_required",
    "release_authorized: false",
    "broad_v2x_performance_not_proven",
    "serious_all_app_paired_evidence_failed_release_bar",
    "current_scoped_13_row_surface_not_v3_major_release",
    "Final public-surface wording gate is complete but still does not authorize speed claims",
    "final_public_surface_gate: true",
    "final_public_surface_claim_boundary_gate",
    "General release installer is not packaged, but scoped installer blocker is closed",
    "staged_pod_gate_present_general_release_installer_not_ready",
    "release_scope: source_tree_pod_gated_thirteen_row",
    "installer_closes_release_blocker_scope: source_tree_pod_gated_thirteen_row",
    "--accept-experimental-pod-gate",
    "not a general release installer",
    "does not authorize package-install wording",
    "Current 13-row installer scope extension is reviewed",
    "source_tree_pod_gated_thirteen_row_scope_extension_reviewed: true",
    "aggregate_13_row_installer_scope_review_required: false",
    "source_tree_pod_gated_thirteen_row",
    "Secondary RT hardware scope waiver is reviewed",
    "secondary_rt_hardware_scope_waiver_reviewed: true",
    "secondary_platform_closes_release_blocker_scope: single_rtx_4000_ada_driver_550_127_05_pod",
    "Broad V3-over-V2 speedup remains forbidden claim wording",
    "broad_v3_faster_than_v2_claim_authorized: false",
    "Generic engine work queue is closed for this scoped release",
    "generic_engine_work_queue_closed_not_release",
    "Phoenix M7 scoped surface has thirteen rows but is not V3 major release authorization",
    "thirteen exact M7-qualified/supplemental row-scoped claims",
    "Rows outside this list remain internal, blocked, no-go, historical, or future",
    "System Python packaging gap",
    "compatibility_confirmed_hardware_scope_waiver_reviewed_not_release",
    "single_rtx_4000_ada_driver_550_127_05_pod",
)

REQUIRED_RUNBOOK_PHRASES = (
    "Current Phoenix Rerun Contract",
    "scripts/v3_phoenix_major_performance_mandate_gate.py --pretty",
    "scripts/v3_release_wording_gate.py --pretty",
    "final_public_surface_gate: true",
    "final_public_surface_claim_boundary_gate",
    "scripts/v3_phoenix_release_readiness_gate.py --pretty",
    "scripts/v3_phoenix_release_readiness_gate.py --strict-release",
    "scripts/v3_phoenix_next_engine_work_queue.py --pretty",
    "generic_engine_work_queue_closed_not_release",
    "existing_evidence_promotable_now: false",
    "status: redo_required",
    "release_authorized: false",
    "public_speedup_claim_authorized: false",
    "broad_v3_faster_than_v2_claim_authorized: false",
    "Phoenix M7-qualified release rows: 13",
    "v3_source_tree_pod_gated_thirteen_row_scope_extension_candidate_2026-06-22.md",
    "aggregate_13_row_installer_scope_review_required: false",
    "current_installer_closure_scope: source_tree_pod_gated_thirteen_row",
    "proposed_installer_closure_scope: source_tree_pod_gated_thirteen_row",
    "thirteen_row_scope_extension_reviewed: true",
)

REQUIRED_CONSENSUS_PHRASES = (
    "release_authorized: false",
    "public_speedup_claim_authorized: false",
    "broad_v3_faster_than_v2_claim_authorized: false",
    "V3 is not ready to be called a responsible major release",
)

REQUIRED_ELEVEN_ROW_CLAUDE_REVIEW_PHRASES = (
    "Verdict: `not-release-ready-fix-p0`",
    "The eleven-row surface is real, honest, and meaningfully stronger",
    "The active generic-engine queue is correctly closed.",
    "Three P0 blockers remain genuinely open",
    "General release installer is not ready.",
    "Secondary RT-core performance confirmation is not closed.",
    "External release-readiness consensus has not been updated",
    "There is no remaining generic-engine work on the critical path to release.",
    "This review does not authorize release.",
)

REQUIRED_ELEVEN_ROW_CONSENSUS_PHRASES = (
    "claude_codex_consensus_current_eleven_row_not_release_ready_fix_p0",
    "Verdict:",
    "`not-release-ready-fix-p0`",
    "This does not authorize release.",
    "The superseding current-state consensus is itself a blocking consensus",
    "general_release_installer_not_ready",
    "secondary_rt_performance_confirmation_not_closed",
    "current_eleven_row_release_readiness_consensus_blocks_release",
    "broad_v3_faster_than_v2_claim_not_authorized",
)

REQUIRED_DEVICE_COLUMN_CONSENSUS_PHRASES = (
    "row decision: promote_both_rows",
    "m7_qualified_release_rows_from_this_packet: 2",
    "release_authorized: false",
    "true_zero_copy_authorized: false",
    "pure backend-only Embree/OptiX ratios",
)

REQUIRED_GOAL4392_PHRASES = (
    "Rebuild V3 as the Goal4392 execution-graph / prepared-continuation language",
    "Rows that do not instantiate a named generic V3 capability must be removed",
    "1.012x V3 speedup versus V2.14",
)

REQUIRED_DESIGN_MANDATE_PHRASES = (
    "V3 is RTDL's independent-language performance release",
    "No current V3 release-grade same-contract OptiX-vs-Embree matrix",
    "Create a V3-only performance gate",
)

REQUIRED_SECONDARY_PLATFORM_PHRASES = (
    "compatibility_confirmed_hardware_scope_waiver_reviewed_not_release",
    "secondary_rt_performance_confirmation_authorized: false",
    "secondary_rt_hardware_scope_waiver_reviewed: true",
    "secondary_platform_closes_release_blocker: true",
    "secondary_platform_closes_release_blocker_method: reviewed_hardware_scoped_waiver",
    "secondary_platform_closes_release_blocker_scope: single_rtx_4000_ada_driver_550_127_05_pod",
    "multi_gpu_performance_portability_claim_authorized: false",
    "release_authorized: false",
    "GTX 1070-class hardware has no RT cores",
    "single_rtx_4000_ada_driver_550_127_05_pod",
)

REQUIRED_SECONDARY_WAIVER_REVIEW_PHRASES = (
    "Verdict: `accept-with-amendments-not-release`",
    "secondary_rt_hardware_scope_waiver_reviewed",
    "secondary_platform_closes_release_blocker: true",
    "secondary_rt_performance_confirmation_authorized: false",
    "release_authorized: false",
    "single_rtx_4000_ada_driver_550_127_05_pod",
    "This review does not authorize V3 release.",
)

REQUIRED_SECONDARY_WAIVER_CONSENSUS_PHRASES = (
    "claude_codex_consensus_secondary_rt_hardware_scope_waiver_not_release",
    "Verdict: `accept-with-amendments-not-release`",
    "secondary_rt_hardware_scope_waiver_reviewed: true",
    "secondary_platform_closes_release_blocker: true",
    "secondary_platform_closes_release_blocker_method: reviewed_hardware_scoped_waiver",
    "secondary_platform_closes_release_blocker_scope: single_rtx_4000_ada_driver_550_127_05_pod",
    "secondary_rt_performance_confirmation_authorized: false",
    "multi_gpu_performance_portability_claim_authorized: false",
    "broad_v3_faster_than_v2_claim_authorized: false",
    "package_install_claim_authorized: false",
    "release_authorized: false",
    "This consensus does not authorize release.",
)

REQUIRED_AGGREGATE_RELEASE_CLAUDE_REVIEW_PHRASES = (
    "`not-release-ready-fix-p0`",
    "Scoped installer closes installer blocker",
    "Scoped hardware waiver closes secondary-RT blocker",
    "P0-1",
    "`release_authorized: false`",
    "P0-2",
    "`eleven_row_surface_still_too_narrow_for_major_release`",
    "P0-3",
    "`current_eleven_row_release_readiness_consensus_blocks_release`",
    "A scoped release under this framing remains blocked",
)

REQUIRED_AGGREGATE_RELEASE_CONSENSUS_PHRASES = (
    "claude_codex_consensus_phoenix_v3_aggregate_release_not_ready_fix_p0",
    "Verdict: `not-release-ready-fix-p0`",
    "installer_closes_release_blocker: true",
    "installer_closes_release_blocker_scope: source_tree_pod_gated_eleven_row",
    "secondary_platform_closes_release_blocker: true",
    "secondary_platform_closes_release_blocker_scope: single_rtx_4000_ada_driver_550_127_05_pod",
    "release_authorization_false",
    "eleven_row_surface_still_too_narrow_for_major_release",
    "aggregate_release_readiness_consensus_blocks_release",
    "broad_v3_faster_than_v2_claim_authorized: false",
    "release_authorized: false",
)

REQUIRED_TWELVE_ROW_POST_P1_CLAUDE_REVIEW_PHRASES = (
    "Verdict: `approve-blocked-not-release`",
    "No new P0 findings.",
    "P1-4 is fully closed.",
    "P1-1 is mechanically closed",
    "twelve_row_release_readiness_consensus_blocks_release",
    "This review does not authorize release. It authorizes Codex to write the twelve-row aggregate consensus.",
)

REQUIRED_TWELVE_ROW_POST_P1_CONSENSUS_PHRASES = (
    "twelve_row_release_readiness_consensus_blocks_release",
    "source_tree_pod_gated_twelve_row is accepted as the correct successor",
    "installer_closes_release_blocker_scope: source_tree_pod_gated_twelve_row",
    "general_release_installer_ready: false",
    "package_install_claim_authorized: false",
    "release_authorized: false",
    "public_speedup_claim_authorized: false",
    "broad_v3_faster_than_v2_claim_authorized: false",
    "missing_point_location_topology_stream_m7_capability_family",
    "aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped",
    "opens no RT-core claim",
)

REQUIRED_FINAL_WORDING_GATE_CLAUDE_REVIEW_PHRASES = (
    "Verdict: `approve-with-amendments`",
    "P0 Findings",
    "None.",
    "P1-1",
    "P1-2",
    "The upgrade closes the old first-pass wording-scanner ambiguity",
    "The release-readiness gate correctly consumes the stronger wording gate",
    "No P0 fixes are required.",
)

REQUIRED_FINAL_WORDING_GATE_CONSENSUS_PHRASES = (
    "claude_codex_consensus_final_public_surface_wording_gate_upgrade_complete_not_release",
    "`approve-with-amendments-complete`",
    "gate_level: final_public_surface_claim_boundary_gate",
    "final_public_surface_gate: true",
    "missing_expected_m7_row_ids: []",
    "release_authorized: false",
    "P1-1 was fixed",
    "P1-2 was fixed",
    "91 modules / 438 tests OK",
    "Do not say this authorizes release.",
)

REQUIRED_RELEASE_SURFACE_BREADTH_CLAUDE_REVIEW_PHRASES = (
    "Verdict: `approve-with-amendments`",
    "P0 Findings",
    "- None.",
    "P1-1",
    "P1-2",
    "P1-3",
    "Required Fixes",
)

REQUIRED_RELEASE_SURFACE_BREADTH_CONSENSUS_PHRASES = (
    "claude_codex_consensus_release_surface_breadth_gate_complete_not_release",
    "`approve-with-amendments-complete`",
    "P1-1 fixed",
    "P1-2 fixed",
    "P1-3 fixed",
    "Release authorization: false",
)

REQUIRED_AGGREGATE_13_ROW_REVIEW_REQUEST_PHRASES = (
    "Phoenix V3 Aggregate Release-Readiness Review Request: 13-Row Surface",
    "13-row / 9-capability surface",
    "missing capability families: none",
    "Installer Scope Closure",
    "release_scope: source_tree_pod_gated_thirteen_row",
    "installer_closes_release_blocker_scope: source_tree_pod_gated_thirteen_row",
    "source_tree_pod_gated_thirteen_row_scope_extension_reviewed: true",
    "aggregate_13_row_installer_scope_review_required: false",
    "general_release_installer_ready: false",
    "package_install_claim_authorized: false",
    "current_core_gap_external_review_blocks_release",
    "point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7",
    "phoenix_v3_latest_v3_rebuild_matrix_after_aabb_runner_m2_20260622.json",
    "phoenix_v3_release_completion_audit_2026-06-22.md",
    "phoenix_v3_user_facing_performance_dossier_2026-06-22.md",
    "surface row integrity rows: 13",
    "surface row paths all exist: true",
    "surface row unsupported-claim flags blocked: true",
    "surface rows are generic capability rows: true",
    "phoenix_v3_surface_integrity_gate_update_2026-06-22.md",
    "phoenix_v3_short_user_path_guard_update_2026-06-22.md",
    "phoenix_v3_bounded_external_review_protocol_2026-06-22.md",
    "one bounded automated attempt",
    "no release promotion without a real external verdict",
    "111 modules / 557 tests OK",
    "scripts/v3_phoenix_external_verdict_intake.py",
    "Reviewer: Claude",
    "Reviewer: Gemini",
    "Reviewer: Human external reviewer",
    "Verdict: `approve_blocked_not_release`",
    "`release_ready`",
    "`approve_blocked_not_release`",
    "`block_p0`",
    "`block_p1`",
    "phoenix_v3_external_verdict_response_template_2026-06-22.md",
    "Expected Output Format",
)

REQUIRED_EXTERNAL_VERDICT_RESPONSE_TEMPLATE_PHRASES = (
    "Phoenix V3 External Verdict Response Template",
    "scripts/v3_phoenix_external_verdict_intake.py",
    "Reviewer: Claude",
    "Verdict: `approve_blocked_not_release`",
    "Scope: Phoenix V3 aggregate 13-row / 9-capability release-readiness packet.",
    "`release_ready`",
    "`approve_blocked_not_release`",
    "`block_p0`",
    "`block_p1`",
    "Do not use this template for a Codex self-review",
    "fallback consensus",
    "timeout record",
)

REQUIRED_AGGREGATE_13_ROW_EXTERNAL_BLOCKED_PHRASES = (
    "External AI Blocked: Phoenix V3 Aggregate Release Readiness After Dossier",
    "C:\\Users\\Lestat\\.local\\bin\\claude.exe",
    "stdin",
    "external_review_not_obtained_claude_no_output_timeout_after_dossier",
    "stdout bytes: 0",
    "stderr bytes: 0",
    "substantive verdict returned: false",
    "process stopped by bounded timeout: true",
    "Phoenix V3 remains `blocked_not_release`",
)

REQUIRED_AGGREGATE_13_ROW_CODEX_SUBAGENT_PHRASES = (
    "Codex Subagent Review: Phoenix V3 Aggregate 13-Row Release Readiness",
    "`approve_blocked_not_release`",
    "cannot substitute for a Claude/Gemini external release authorization",
    "The 13-row / 9-capability surface removes the old missing-Spatial / surface-width blocker.",
    "Phoenix V3 release is not authorized.",
    "100 modules / 486 tests OK",
)

REQUIRED_AGGREGATE_13_ROW_FALLBACK_CONSENSUS_PHRASES = (
    "codex_subagent_fallback_consensus_approve_blocked_not_release",
    "required external Claude/Gemini release authorization",
    "The old missing-Spatial / surface-width blocker is removed.",
    "Phoenix V3 release remains blocked.",
    "phoenix_v3_latest_v3_rebuild_matrix_after_aabb_runner_m2_20260622.json",
    "phoenix_v3_release_completion_audit_2026-06-22.md",
    "phoenix_v3_user_facing_performance_dossier_2026-06-22.md",
    "phoenix_v3_short_user_path_guard_update_2026-06-22.md",
    "phoenix_v3_bounded_external_review_protocol_2026-06-22.md",
    "one bounded automated attempt",
    "no release promotion without a real external verdict",
    "111 modules / 557 tests OK",
    "The scoped installer/reproducibility blocker is closed",
    "source_tree_pod_gated_thirteen_row",
    "source_tree_pod_gated_thirteen_row_scope_extension_reviewed: true",
    "aggregate_13_row_installer_scope_review_required: false",
    "installer_closes_release_blocker_scope: source_tree_pod_gated_thirteen_row",
    "release_authorized: false",
    "Phoenix V3 is not release-authorized yet.",
)

REQUIRED_BOUNDED_EXTERNAL_REVIEW_PROTOCOL_PHRASES = (
    "External AI review is a bounded gate, not an infinite loop.",
    "Make at most one automated external-AI attempt for that packet in the active",
    "Use a hard wall-clock timeout",
    "Save a blocked review record with the exact status",
    "`external_review_not_obtained_<tool>_<reason>`",
    "Do not promote release wording from a missing external verdict.",
    "Continue non-release V3 work that does not depend on the missing verdict.",
    "A later accepted verdict can supersede a missing-verdict blocker.",
    "A scoped external verdict cannot override the major-version performance mandate.",
    "aggregate_13_row_scoped_dossier_external_review_status:",
    "external_verdict_obtained_claude_scoped_dossier_release_ready_not_v3_release",
    "aggregate_13_row_scoped_dossier_external_authorization_obtained: true",
    "release_authorized: false",
    "status: redo_required",
    "Only a written review record with one of these labels can change aggregate",
    "`release_ready`",
    "`approve_blocked_not_release`",
    "`block_p0`",
    "`block_p1`",
    "Fallback review cannot:",
    "authorize a Phoenix V3 release",
    "replace a missing external aggregate verdict",
)

REQUIRED_CURRENT_HANDOFF_PHRASES = (
    "# Phoenix V3 Current Handoff",
    "Status: `redo_required`",
    "Do not resume V4.",
    "Phoenix M7-qualified release rows: 13",
    "planned capability families: 9 / 9",
    "missing capability families: none",
    "phoenix_v3_latest_v3_rebuild_matrix_after_aabb_runner_m2_20260622.json",
    "phoenix_v3_release_completion_audit_2026-06-22.md",
    "phoenix_v3_user_facing_performance_dossier_2026-06-22.md",
    "111 modules / 557 tests OK",
    "source_tree_pod_gated_thirteen_row",
    "single_rtx_4000_ada_driver_550_127_05_pod",
    "generic_engine_work_queue_closed_not_release",
    "external_verdict_obtained_claude_scoped_dossier_release_ready_not_v3_release",
    "V3 major release requires broad V2.x performance superiority",
    "current_scoped_13_row_surface_not_v3_major_release",
    "serious_all_app_paired_evidence_failed_release_bar",
    "phoenix_v3_serious_v2x_paired_benchmark_2026-06-22.md",
    "claude_phoenix_v3_aggregate_release_readiness_13_row_after_dossier_review_2026-06-22.md",
    "one bounded automated attempt",
    "redo_required",
    "C:\\Users\\Lestat\\.local\\bin\\claude.exe",
    "The fallback consensus does not replace external release authorization.",
    "Goal-Level Decision Audit",
)

REQUIRED_REFRESH_LOCAL_PHRASES = (
    "2026-06-22 Phoenix bounded-review rule",
    "`docs/rebuild/v3/phoenix_v3_bounded_external_review_protocol_2026-06-22.md`",
    "one complete review packet",
    "one bounded automated Claude attempt",
    "do not use Gemini again",
    "Google policy/tooling issue is solved",
    "`external_review_not_obtained_<tool>_<reason>`",
    "Do not loop on Claude availability, quota, PATH, auth",
    "current handoff entry point",
    "`docs/handoff/PHOENIX_V3_CURRENT_HANDOFF_2026-06-22.md`",
    "older V3/V4",
    "failure cannot become an infinite retry loop",
)

REQUIRED_THIRTEEN_ROW_SCOPE_EXTENSION_CANDIDATE_PHRASES = (
    "source_tree_pod_gated_thirteen_row_scope_extension_reviewed_not_release",
    "source_tree_pod_gated_thirteen_row",
    "source_tree_pod_gated_twelve_row",
    "point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7",
    "Install-Script Coverage Confirmation",
    "`v3_install_gpu_pod_env.sh` covers the Spatial",
    "No new package pins, build steps, or environment variables are required",
    "Required Gate Script Delta If Accepted",
    "aggregate_13_row_installer_scope_review_required` to false",
    "release_authorized: false",
    "package_install_claim_authorized: false",
    "Do not say:",
)

REQUIRED_THIRTEEN_ROW_SCOPE_EXTENSION_REVIEW_REQUEST_PHRASES = (
    "Review Request: Phoenix V3 Source-Tree / Pod-Gated Thirteen-Row Scope Extension",
    "source_tree_pod_gated_twelve_row",
    "source_tree_pod_gated_thirteen_row",
    "This is not a release-readiness review and must not authorize release.",
    "aggregate_13_row_installer_scope_review_required: true",
    "Do not authorize release.",
)

REQUIRED_THIRTEEN_ROW_SCOPE_EXTENSION_CLAUDE_REVIEW_PHRASES = (
    "accept-with-amendments-not-release",
    "One P0 amendment is required",
    "Install-script coverage confirmation",
    "`release_scope` | `source_tree_pod_gated_twelve_row` | `source_tree_pod_gated_thirteen_row`",
    "`installer_closes_release_blocker_scope` | `source_tree_pod_gated_twelve_row` | `source_tree_pod_gated_thirteen_row`",
    "`source_tree_pod_gated_thirteen_row_scope_extension_reviewed` | `false` | `true`",
    "`aggregate_13_row_installer_scope_review_required` | `true` | `false`",
    "This review does not authorize release.",
)

REQUIRED_THIRTEEN_ROW_SCOPE_EXTENSION_CODEX_CONSENSUS_PHRASES = (
    "claude_codex_consensus_source_tree_pod_gated_thirteen_row_scope_extension_reviewed_not_release",
    "Claude verdict: `accept-with-amendments-not-release`",
    "v3_install_gpu_pod_env.sh covers the Spatial",
    "release_scope: source_tree_pod_gated_thirteen_row",
    "installer_closes_release_blocker_scope: source_tree_pod_gated_thirteen_row",
    "source_tree_pod_gated_thirteen_row_scope_extension_reviewed: true",
    "aggregate_13_row_installer_scope_review_required: false",
    "release_authorized: false",
    "package_install_claim_authorized: false",
)

REQUIRED_INSTALL_REPRODUCIBILITY_PHRASES = (
    "staged_pod_gate_present_general_release_installer_not_ready",
    "staged_gpu_pod_gate_available: true",
    "source_tree_pod_gated_candidate_reviewed: true",
    "release_scope: source_tree_pod_gated_thirteen_row",
    "source_tree_pod_gated_scoped_release_wording_reviewed: true",
    "source_tree_pod_gated_thirteen_row_scope_extension_reviewed: true",
    "aggregate_13_row_installer_scope_review_required: false",
    "general_release_installer_ready: false",
    "package_install_claim_authorized: false",
    "installer_closes_release_blocker: true",
    "installer_closes_release_blocker_scope: source_tree_pod_gated_thirteen_row",
    "--accept-experimental-pod-gate",
)

REQUIRED_NEXT_ENGINE_QUEUE_PHRASES = (
    "closed generic-engine queue",
    "existing_evidence_promotable_now: false",
    "A 1.01x-style result cannot qualify",
    "current_m7_qualified_release_rows: 13",
    "base_m7_packet_rows: 12",
    "supplemental_m7_rows_from_current_queue: 1",
    "Closed Generic Engine Work",
    "grouped_reduction_prepare_amortization",
    "M7 rows added: 2",
    "codex_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2ai_consensus_2026-06-21.md",
    "rtnn_ranked_summary_wall_path",
    "phoenix_v3_rtnn_prepared_repeat50_review_gate_2026-06-21.md",
    "codex_phoenix_v3_rtnn_prepared_repeat50_amortization_2ai_consensus_2026-06-21.md",
    "7.889x hot-query",
    "3.761x runner-wall",
    "contact_aabb_prepare_reuse",
    "barnes_hut_fused_partner_vector_accumulation",
    "aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped",
    "4.082x faster than CPU/Numba fused baseline",
    "13.591x comparison against the current prepared RTDL/OptiX frontier-emission route is supporting metadata only",
    "spatial_squared_boundary_default_path_topology_stream",
    "point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7",
    "claude_phoenix_v3_spatial_default_path_promotion_review_2026-06-22.md",
    "codex_phoenix_v3_spatial_default_path_promotion_2ai_consensus_2026-06-22.md",
    "default-path median is 1.080599 ms",
    "Future Research Records",
    "barnes_hut_vector_accumulation_frontier_shape",
    "future_research_not_current_p0",
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _check_file(path: Path) -> bool:
    return path.exists() and path.is_file()


def _all_false(items: list[Any]) -> bool:
    return all(item is False for item in items)


def _m7_row_ids_from_packet(packet: dict[str, Any]) -> list[str]:
    rows: list[str] = []
    for item in packet.get("row_classifications", []):
        if item.get("m7_classification") == "m7_qualified_release_row":
            rows.append(item.get("candidate_row_id", ""))
    for item in packet.get("post_classification_final_review_packets", []):
        if item.get("classification_m7_contribution", 0) > 0 and item.get("row_scoped_public_speedup_claim_authorized") is True:
            if item.get("candidate_row_ids"):
                rows.extend(item["candidate_row_ids"])
            else:
                rows.append(item.get("candidate_row_id", ""))
    return rows


def _rejection_has_reason(payload: dict[str, Any], candidate_id: str, reason: str) -> bool:
    return any(
        item.get("candidate_id") == candidate_id
        and item.get("accepted") is False
        and reason in item.get("reasons", [])
        for item in payload.get("current_rejections", [])
    )


def _build_checks() -> tuple[dict[str, bool], dict[str, Any]]:
    evidence: dict[str, Any] = {}
    checks: dict[str, bool] = {}

    for name, path in {
        "m7_packet": M7_PACKET,
        "app_classification": APP_CLASSIFICATION,
        "runbook": RUNBOOK,
        "blockers": BLOCKERS,
        "six_row_consensus": SIX_ROW_CONSENSUS,
        "eleven_row_claude_review": ELEVEN_ROW_CLAUDE_REVIEW,
        "eleven_row_consensus": ELEVEN_ROW_CONSENSUS,
        "device_column_consensus": DEVICE_COLUMN_CONSENSUS,
        "goal4392_audit": GOAL4392_AUDIT,
        "design_mandate": DESIGN_MANDATE,
        "secondary_platform_strategy": SECONDARY_PLATFORM_STRATEGY,
        "install_reproducibility_strategy": INSTALL_REPRODUCIBILITY_STRATEGY,
        "next_engine_work_queue": NEXT_ENGINE_WORK_QUEUE,
        "secondary_hardware_waiver_review": SECONDARY_HARDWARE_WAIVER_REVIEW,
        "secondary_hardware_waiver_consensus": SECONDARY_HARDWARE_WAIVER_CONSENSUS,
        "aggregate_release_claude_review": AGGREGATE_RELEASE_CLAUDE_REVIEW,
        "aggregate_release_consensus": AGGREGATE_RELEASE_CONSENSUS,
        "twelve_row_post_p1_claude_review": TWELVE_ROW_POST_P1_CLAUDE_REVIEW,
        "twelve_row_post_p1_consensus": TWELVE_ROW_POST_P1_CONSENSUS,
        "final_wording_gate_claude_review": FINAL_WORDING_GATE_CLAUDE_REVIEW,
        "final_wording_gate_consensus": FINAL_WORDING_GATE_CONSENSUS,
        "release_surface_breadth_gate_json": RELEASE_SURFACE_BREADTH_GATE_JSON,
        "release_surface_breadth_gate_md": RELEASE_SURFACE_BREADTH_GATE_MD,
        "release_surface_breadth_claude_review": RELEASE_SURFACE_BREADTH_CLAUDE_REVIEW,
        "release_surface_breadth_consensus": RELEASE_SURFACE_BREADTH_CONSENSUS,
        "objective_conformance_gate_json": OBJECTIVE_CONFORMANCE_GATE_JSON,
        "aggregate_13_row_review_request": AGGREGATE_13_ROW_REVIEW_REQUEST,
        "external_verdict_response_template": EXTERNAL_VERDICT_RESPONSE_TEMPLATE,
        "aggregate_13_row_external_blocked": AGGREGATE_13_ROW_EXTERNAL_BLOCKED,
        "aggregate_13_row_codex_subagent_review": AGGREGATE_13_ROW_CODEX_SUBAGENT_REVIEW,
        "aggregate_13_row_fallback_consensus": AGGREGATE_13_ROW_FALLBACK_CONSENSUS,
        "external_verdict_intake": EXTERNAL_VERDICT_INTAKE,
        "core_gaps_external_review": CORE_GAPS_EXTERNAL_REVIEW,
        "core_gaps_external_intake": CORE_GAPS_EXTERNAL_INTAKE,
        "core_gaps_external_status": CORE_GAPS_EXTERNAL_STATUS,
        "set_a_set_b_release_bar_proposal": SET_A_SET_B_RELEASE_BAR_PROPOSAL,
        "bounded_external_review_protocol": BOUNDED_EXTERNAL_REVIEW_PROTOCOL,
        "current_handoff": CURRENT_HANDOFF,
        "refresh_local": REFRESH_LOCAL,
        "current_status": CURRENT_STATUS,
        "readiness_distance_packet": READINESS_DISTANCE_PACKET,
        "latest_full_matrix": LATEST_FULL_MATRIX,
        "aabb_runner_m2_report": AABB_RUNNER_M2_REPORT,
        "spatial_default_path_claude_review": SPATIAL_DEFAULT_PATH_CLAUDE_REVIEW,
        "spatial_default_path_codex_consensus": SPATIAL_DEFAULT_PATH_CODEX_CONSENSUS,
        "spatial_squared_boundary_candidate": SPATIAL_SQUARED_BOUNDARY_CANDIDATE,
        "spatial_squared_boundary_candidate_json": SPATIAL_SQUARED_BOUNDARY_CANDIDATE_JSON,
        "spatial_topology_stream_redo_alignment": SPATIAL_TOPOLOGY_STREAM_REDO_ALIGNMENT,
        "thirteen_row_scope_extension_candidate": THIRTEEN_ROW_SCOPE_EXTENSION_CANDIDATE,
        "thirteen_row_scope_extension_review_request": THIRTEEN_ROW_SCOPE_EXTENSION_REVIEW_REQUEST,
        "thirteen_row_scope_extension_claude_review": THIRTEEN_ROW_SCOPE_EXTENSION_CLAUDE_REVIEW,
        "thirteen_row_scope_extension_codex_consensus": THIRTEEN_ROW_SCOPE_EXTENSION_CODEX_CONSENSUS,
    }.items():
        checks[f"{name}_exists"] = _check_file(path)

    if not all(checks.values()):
        return checks, evidence

    m7_packet = _load_json(M7_PACKET)
    app_classification = _load_json(APP_CLASSIFICATION)
    runbook = _read_text(RUNBOOK)
    blockers = _read_text(BLOCKERS)
    six_row_consensus = _read_text(SIX_ROW_CONSENSUS)
    eleven_row_claude_review = _read_text(ELEVEN_ROW_CLAUDE_REVIEW)
    eleven_row_consensus = _read_text(ELEVEN_ROW_CONSENSUS)
    device_column_consensus = _read_text(DEVICE_COLUMN_CONSENSUS)
    goal4392_audit = _read_text(GOAL4392_AUDIT)
    design_mandate = _read_text(DESIGN_MANDATE)
    secondary_platform_strategy = _read_text(SECONDARY_PLATFORM_STRATEGY)
    install_reproducibility_strategy = _read_text(INSTALL_REPRODUCIBILITY_STRATEGY)
    next_engine_work_queue = _read_text(NEXT_ENGINE_WORK_QUEUE)
    secondary_hardware_waiver_review = _read_text(SECONDARY_HARDWARE_WAIVER_REVIEW)
    secondary_hardware_waiver_consensus = _read_text(SECONDARY_HARDWARE_WAIVER_CONSENSUS)
    aggregate_release_claude_review = _read_text(AGGREGATE_RELEASE_CLAUDE_REVIEW)
    aggregate_release_consensus = _read_text(AGGREGATE_RELEASE_CONSENSUS)
    twelve_row_post_p1_claude_review = _read_text(TWELVE_ROW_POST_P1_CLAUDE_REVIEW)
    twelve_row_post_p1_consensus = _read_text(TWELVE_ROW_POST_P1_CONSENSUS)
    final_wording_gate_claude_review = _read_text(FINAL_WORDING_GATE_CLAUDE_REVIEW)
    final_wording_gate_consensus = _read_text(FINAL_WORDING_GATE_CONSENSUS)
    release_surface_breadth_claude_review = _read_text(RELEASE_SURFACE_BREADTH_CLAUDE_REVIEW)
    release_surface_breadth_consensus = _read_text(RELEASE_SURFACE_BREADTH_CONSENSUS)
    aggregate_13_row_review_request = _read_text(AGGREGATE_13_ROW_REVIEW_REQUEST)
    external_verdict_response_template = _read_text(EXTERNAL_VERDICT_RESPONSE_TEMPLATE)
    aggregate_13_row_external_blocked = _read_text(AGGREGATE_13_ROW_EXTERNAL_BLOCKED)
    aggregate_13_row_codex_subagent_review = _read_text(AGGREGATE_13_ROW_CODEX_SUBAGENT_REVIEW)
    aggregate_13_row_fallback_consensus = _read_text(AGGREGATE_13_ROW_FALLBACK_CONSENSUS)
    external_verdict_intake_payload = _load_json(EXTERNAL_VERDICT_INTAKE)
    external_verdict_intake_current_payload = v3_phoenix_external_verdict_intake.build_payload()
    core_gaps_external_review = _read_text(CORE_GAPS_EXTERNAL_REVIEW)
    core_gaps_external_intake_payload = _load_json(CORE_GAPS_EXTERNAL_INTAKE)
    core_gaps_external_status = _read_text(CORE_GAPS_EXTERNAL_STATUS)
    set_a_set_b_release_bar_proposal = _read_text(SET_A_SET_B_RELEASE_BAR_PROPOSAL)
    major_performance_payload = v3_phoenix_major_performance_mandate_gate.build_payload()
    bounded_external_review_protocol = _read_text(BOUNDED_EXTERNAL_REVIEW_PROTOCOL)
    current_handoff = _read_text(CURRENT_HANDOFF)
    refresh_local = _read_text(REFRESH_LOCAL)
    thirteen_row_scope_extension_candidate = _read_text(THIRTEEN_ROW_SCOPE_EXTENSION_CANDIDATE)
    thirteen_row_scope_extension_review_request = _read_text(THIRTEEN_ROW_SCOPE_EXTENSION_REVIEW_REQUEST)
    thirteen_row_scope_extension_claude_review = _read_text(THIRTEEN_ROW_SCOPE_EXTENSION_CLAUDE_REVIEW)
    thirteen_row_scope_extension_codex_consensus = _read_text(THIRTEEN_ROW_SCOPE_EXTENSION_CODEX_CONSENSUS)
    secondary_platform_payload = v3_phoenix_secondary_platform_gate.build_payload()
    install_reproducibility_payload = v3_phoenix_install_reproducibility_gate.build_payload()
    next_engine_queue_payload = v3_phoenix_next_engine_work_queue.build_payload()
    release_surface_breadth_payload = v3_phoenix_release_surface_breadth_gate.build_payload()
    objective_conformance_payload = _load_json(OBJECTIVE_CONFORMANCE_GATE_JSON)
    objective_conformance_current_payload = v3_phoenix_objective_conformance_gate.build_payload()
    wording_payload = v3_release_wording_gate.build_payload(
        (
            "docs/rebuild/v3/phoenix_v3_m7_row_classification_packet_2026-06-20.json",
            "docs/rebuild/v3/v3_benchmark_app_classification_2026-06-20.json",
            "docs/rebuild/v3/v3_release_authorization_blockers_2026-06-20.md",
            "docs/rebuild/v3/v3_setup_and_rerun_runbook_2026-06-20.md",
            "docs/rebuild/v3/phoenix_v3_release_surface_breadth_gate_2026-06-21.md",
            "docs/rebuild/v3/phoenix_v3_release_surface_breadth_gate_2026-06-21.json",
            "docs/rebuild/v3/v3_secondary_platform_strategy_2026-06-21.md",
            "docs/rebuild/v3/v3_install_reproducibility_strategy_2026-06-21.md",
            "docs/rebuild/v3/v3_source_tree_pod_gated_reproducibility_candidate_2026-06-21.md",
            "docs/rebuild/v3/phoenix_v3_next_generic_engine_work_queue_2026-06-21.md",
            "docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_ray_batch_candidate_2026-06-21.md",
            "docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_ray_batch_candidate_2026-06-21.json",
            "docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_ray_batch_pod_evidence_2026-06-21.md",
            "docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_ray_batch_pod_evidence_2026-06-21.json",
        )
    )

    base_m7_packet_summary = m7_packet.get("summary", {})
    m7_rows_from_packet = _m7_row_ids_from_packet(m7_packet)
    app_m7_rows = app_classification.get("m7_row_ids", [])

    checks.update(
        {
            "m7_packet_status_not_release": m7_packet.get("status") == "m7_classification_packet_not_release",
            "m7_packet_release_false": m7_packet.get("release_authorized") is False,
            "m7_packet_public_speed_false": m7_packet.get("public_speedup_claim_authorized") is False,
            "m7_packet_broad_speed_false": m7_packet.get("broad_v3_faster_than_v2_claim_authorized") is False,
            "base_m7_packet_has_12_rows_before_spatial_default_extension": (
                m7_packet.get("phoenix_m7_qualified_release_rows") == 12
            ),
            "base_m7_packet_summary_has_12_rows": base_m7_packet_summary.get("m7_qualified_release_rows") == 12,
            "base_m7_packet_summary_zero_public_claim_rows": (
                base_m7_packet_summary.get("public_claim_rows") == 0
            ),
            "base_m7_packet_summary_has_12_row_scoped_claim_rows": (
                base_m7_packet_summary.get("row_scoped_public_claim_rows") == 12
            ),
            "m7_expected_rows_match_packet": set(m7_rows_from_packet) == set(EXPECTED_M7_ROWS),
            "app_boundary_status_not_release": app_classification.get("status") == "phoenix_boundary_classification_not_release",
            "app_boundary_release_false": app_classification.get("v3_release_authorized") is False,
            "app_boundary_public_speed_false": app_classification.get("public_speedup_claim_authorized") is False,
            "app_boundary_broad_speed_false": app_classification.get("broad_v3_faster_than_v2_claim_authorized") is False,
            "app_boundary_snapshot_eight_rows": app_classification.get("phoenix_m7_qualified_release_rows") == 8,
            "app_boundary_expected_snapshot_rows_match": set(app_m7_rows) == set(EXPECTED_APP_BOUNDARY_M7_ROWS),
            "all_apps_public_claims_false": _all_false(
                [app.get("public_claim_allowed_now") for app in app_classification.get("apps", {}).values()]
            ),
            "wording_gate_pass": wording_payload.get("status") == "pass",
            "wording_gate_final_public_surface": wording_payload.get("final_public_surface_gate") is True,
            "wording_gate_level_is_final_public_surface": (
                wording_payload.get("gate_level") == "final_public_surface_claim_boundary_gate"
            ),
            "wording_gate_has_all_expected_m7_row_ids": (
                wording_payload.get("missing_expected_m7_row_ids") == []
                and set(wording_payload.get("expected_m7_row_ids", [])) == set(EXPECTED_CURRENT_M7_ROWS)
            ),
            "wording_gate_release_false": wording_payload.get("release_authorized") is False,
            "wording_gate_public_speed_false": wording_payload.get("public_speedup_claim_authorized") is False,
            "major_performance_gate_redo_required": (
                major_performance_payload.get("status") == "redo_required"
            ),
            "major_performance_gate_release_false": (
                major_performance_payload.get("release_authorized") is False
            ),
            "major_performance_gate_broad_speed_false": (
                major_performance_payload.get("broad_v3_faster_than_v2_claim_authorized") is False
            ),
            "release_surface_breadth_gate_blocks_not_release": (
                release_surface_breadth_payload.get("status") == "surface_breadth_passed_not_release"
            ),
            "release_surface_breadth_gate_release_false": (
                release_surface_breadth_payload.get("release_authorized") is False
            ),
            "release_surface_breadth_gate_public_speed_false": (
                release_surface_breadth_payload.get("public_speedup_claim_authorized") is False
            ),
            "release_surface_breadth_gate_thirteen_rows": (
                release_surface_breadth_payload.get("evidence", {}).get("total_m7_row_count") == 13
            ),
            "release_surface_breadth_gate_records_9_of_9_capability_coverage": (
                release_surface_breadth_payload.get("evidence", {}).get("m7_capability_family_count") == 9
                and release_surface_breadth_payload.get("evidence", {}).get(
                    "minimum_m7_capability_families_for_major_release"
                )
                == 9
            ),
            "release_surface_breadth_gate_records_no_missing_capabilities": (
                release_surface_breadth_payload.get("evidence", {}).get("missing_m7_capability_families")
                == []
            ),
            "release_surface_breadth_gate_expected_current_rows_match": (
                set(
                    row_id
                    for rows in release_surface_breadth_payload.get("evidence", {})
                    .get("m7_rows_by_capability", {})
                    .values()
                    for row_id in rows
                )
                == set(EXPECTED_CURRENT_M7_ROWS)
            ),
            "release_surface_breadth_gate_existing_evidence_not_promotable": (
                release_surface_breadth_payload.get("evidence", {}).get("existing_evidence_promotable_now") is False
            ),
            "release_surface_breadth_gate_blocks_major_release": (
                "updated_thirteen_row_release_readiness_consensus_required"
                in release_surface_breadth_payload.get("blocking_reasons", [])
                and "release_authorization_false" in release_surface_breadth_payload.get("blocking_reasons", [])
            ),
            "objective_conformance_gate_passed_not_release": (
                objective_conformance_payload.get("status") == "objective_conformance_passed_not_release"
            ),
            "objective_conformance_current_payload_passed_not_release": (
                objective_conformance_current_payload.get("status") == "objective_conformance_passed_not_release"
            ),
            "objective_conformance_release_false": (
                objective_conformance_payload.get("release_authorized") is False
            ),
            "objective_conformance_public_speed_false": (
                objective_conformance_payload.get("public_speedup_claim_authorized") is False
            ),
            "objective_conformance_broad_speed_false": (
                objective_conformance_payload.get("broad_v3_faster_than_v2_claim_authorized") is False
            ),
            "objective_conformance_covers_goal_routes": (
                objective_conformance_payload.get("evidence", {}).get("objective_required_capability_coverage_count")
                == objective_conformance_payload.get("evidence", {}).get("objective_required_capability_count")
                == 5
            ),
            "objective_conformance_excludes_v4_embedding_broad_claims": (
                objective_conformance_payload.get("checks", {}).get("v4_cabi_embedding_out_of_v3_public_surface")
                is True
                and objective_conformance_payload.get("checks", {}).get("broad_v2_speedup_claim_out") is True
                and objective_conformance_payload.get("checks", {}).get("surface_rows_all_generic") is True
            ),
            "blockers_cover_release_reasons": all(phrase in blockers for phrase in REQUIRED_BLOCKER_PHRASES),
            "runbook_contract_present": all(phrase in runbook for phrase in REQUIRED_RUNBOOK_PHRASES),
            "prior_release_readiness_consensus_blocks_release": all(
                phrase in six_row_consensus for phrase in REQUIRED_CONSENSUS_PHRASES
            ),
            "eleven_row_claude_review_blocks_release": all(
                phrase in eleven_row_claude_review for phrase in REQUIRED_ELEVEN_ROW_CLAUDE_REVIEW_PHRASES
            ),
            "eleven_row_codex_consensus_blocks_release": all(
                phrase in eleven_row_consensus for phrase in REQUIRED_ELEVEN_ROW_CONSENSUS_PHRASES
            ),
            "device_column_consensus_promotes_two_rows_not_release": all(
                phrase in device_column_consensus for phrase in REQUIRED_DEVICE_COLUMN_CONSENSUS_PHRASES
            ),
            "goal4392_generic_boundary_present": all(phrase in goal4392_audit for phrase in REQUIRED_GOAL4392_PHRASES),
            "design_mandate_phase_a_present": all(phrase in design_mandate for phrase in REQUIRED_DESIGN_MANDATE_PHRASES),
            "secondary_platform_strategy_present": all(
                phrase in secondary_platform_strategy for phrase in REQUIRED_SECONDARY_PLATFORM_PHRASES
            ),
            "secondary_hardware_waiver_review_accepts_not_release": all(
                phrase in secondary_hardware_waiver_review for phrase in REQUIRED_SECONDARY_WAIVER_REVIEW_PHRASES
            ),
            "secondary_hardware_waiver_consensus_accepts_not_release": all(
                phrase in secondary_hardware_waiver_consensus
                for phrase in REQUIRED_SECONDARY_WAIVER_CONSENSUS_PHRASES
            ),
            "aggregate_release_claude_review_blocks_release": all(
                phrase in aggregate_release_claude_review
                for phrase in REQUIRED_AGGREGATE_RELEASE_CLAUDE_REVIEW_PHRASES
            ),
            "aggregate_release_codex_consensus_blocks_release": all(
                phrase in aggregate_release_consensus for phrase in REQUIRED_AGGREGATE_RELEASE_CONSENSUS_PHRASES
            ),
            "twelve_row_post_p1_claude_review_approves_blocked_not_release": all(
                phrase in twelve_row_post_p1_claude_review
                for phrase in REQUIRED_TWELVE_ROW_POST_P1_CLAUDE_REVIEW_PHRASES
            ),
            "twelve_row_post_p1_codex_consensus_blocks_release": all(
                phrase in twelve_row_post_p1_consensus for phrase in REQUIRED_TWELVE_ROW_POST_P1_CONSENSUS_PHRASES
            ),
            "final_wording_gate_claude_review_approves_with_p1_fixed": all(
                phrase in final_wording_gate_claude_review
                for phrase in REQUIRED_FINAL_WORDING_GATE_CLAUDE_REVIEW_PHRASES
            ),
            "final_wording_gate_codex_consensus_complete_not_release": all(
                phrase in final_wording_gate_consensus for phrase in REQUIRED_FINAL_WORDING_GATE_CONSENSUS_PHRASES
            ),
            "release_surface_breadth_claude_review_approves_with_p1_fixes_required": all(
                phrase in release_surface_breadth_claude_review
                for phrase in REQUIRED_RELEASE_SURFACE_BREADTH_CLAUDE_REVIEW_PHRASES
            ),
            "release_surface_breadth_codex_consensus_complete_not_release": all(
                phrase in release_surface_breadth_consensus
                for phrase in REQUIRED_RELEASE_SURFACE_BREADTH_CONSENSUS_PHRASES
            ),
            "aggregate_13_row_review_request_targets_current_surface": all(
                phrase in aggregate_13_row_review_request
                for phrase in REQUIRED_AGGREGATE_13_ROW_REVIEW_REQUEST_PHRASES
            ),
            "external_verdict_response_template_ingestible_contract_present": all(
                phrase in external_verdict_response_template
                for phrase in REQUIRED_EXTERNAL_VERDICT_RESPONSE_TEMPLATE_PHRASES
            ),
            "aggregate_13_row_external_ai_blocked_recorded": all(
                phrase in aggregate_13_row_external_blocked
                for phrase in REQUIRED_AGGREGATE_13_ROW_EXTERNAL_BLOCKED_PHRASES
            ),
            "aggregate_13_row_codex_subagent_review_blocks_release": all(
                phrase in aggregate_13_row_codex_subagent_review
                for phrase in REQUIRED_AGGREGATE_13_ROW_CODEX_SUBAGENT_PHRASES
            ),
            "aggregate_13_row_fallback_consensus_blocks_release": all(
                phrase in aggregate_13_row_fallback_consensus
                for phrase in REQUIRED_AGGREGATE_13_ROW_FALLBACK_CONSENSUS_PHRASES
            ),
            "external_verdict_intake_external_verdict_obtained": (
                external_verdict_intake_payload.get("status") == "external_verdict_obtained"
            ),
            "external_verdict_intake_current_payload_external_verdict_obtained": (
                external_verdict_intake_current_payload.get("status") == "external_verdict_obtained"
            ),
            "external_verdict_intake_valid_external_verdict_true": (
                external_verdict_intake_payload.get("valid_external_verdict_obtained") is True
            ),
            "external_verdict_intake_release_false": (
                external_verdict_intake_payload.get("release_authorized") is False
            ),
            "external_verdict_intake_scoped_packet_true": (
                external_verdict_intake_payload.get("scoped_packet_authorized") is True
            ),
            "external_verdict_intake_accepts_claude_release_ready": (
                external_verdict_intake_payload.get("accepted_verdict") == "release_ready"
                and any(
                    item.get("candidate_id") == "claude_after_dossier_release_ready"
                    and item.get("scoped_packet_authorized") is True
                    and item.get("release_authorized") is False
                    for item in external_verdict_intake_payload.get("accepted_candidates", [])
                )
            ),
            "external_verdict_intake_rejects_blocked_record": (
                _rejection_has_reason(
                    external_verdict_intake_payload,
                    "latest_external_blocked_record",
                    "external_review_not_obtained_marker",
                )
                and _rejection_has_reason(
                    external_verdict_intake_payload,
                    "latest_external_blocked_record",
                    "bounded_timeout_record",
                )
            ),
            "external_verdict_intake_rejects_codex_subagent": _rejection_has_reason(
                external_verdict_intake_payload,
                "codex_subagent_review",
                "codex_subagent_or_internal_reviewer",
            ),
            "external_verdict_intake_rejects_codex_fallback": _rejection_has_reason(
                external_verdict_intake_payload,
                "codex_fallback_consensus",
                "fallback_consensus_not_external_verdict",
            ),
            "core_gaps_external_verdict_obtained": (
                core_gaps_external_intake_payload.get("status") == "external_verdict_obtained"
            ),
            "core_gaps_external_verdict_approve_blocked": (
                core_gaps_external_intake_payload.get("accepted_verdict") == "approve_blocked_not_release"
            ),
            "core_gaps_external_release_false": (
                core_gaps_external_intake_payload.get("release_authorized") is False
            ),
            "core_gaps_external_public_claims_false": (
                "public_speedup_claim_authorized: false" in core_gaps_external_review
                and "broad_v3_faster_than_v2_claim_authorized: false" in core_gaps_external_review
                and "major_version_mandate_overridden: false" in core_gaps_external_review
            ),
            "core_gaps_external_status_records_non_authorization": (
                "proposal_only_not_authorization" in core_gaps_external_status
                and "does not authorize publishing" in core_gaps_external_status
            ),
            "set_a_set_b_proposal_only_not_authorization": (
                "proposal only, not an authorization" in set_a_set_b_release_bar_proposal
            ),
            "set_a_set_b_precondition_blocks_all_app_rerun": (
                "runtime_executed: True" in set_a_set_b_release_bar_proposal
                and ">= 2 set_A probes" in set_a_set_b_release_bar_proposal
            ),
            "bounded_external_review_protocol_active": all(
                phrase in bounded_external_review_protocol
                for phrase in REQUIRED_BOUNDED_EXTERNAL_REVIEW_PROTOCOL_PHRASES
            ),
            "bounded_external_review_protocol_records_scoped_verdict_and_current_redo": (
                "external_review_not_obtained_claude_no_output_timeout"
                in bounded_external_review_protocol
                and "external_verdict_obtained_claude_scoped_dossier_release_ready_not_v3_release"
                in bounded_external_review_protocol
                and "aggregate_13_row_scoped_dossier_external_authorization_obtained: true"
                in bounded_external_review_protocol
                and "status: redo_required" in bounded_external_review_protocol
                and "release_authorized: false" in bounded_external_review_protocol
                and "A scoped external verdict cannot override the major-version performance mandate."
                in bounded_external_review_protocol
            ),
            "bounded_external_review_protocol_blocks_infinite_retry": (
                "Make at most one automated external-AI attempt" in bounded_external_review_protocol
                and "Continue non-release V3 work that does not depend on the missing verdict."
                in bounded_external_review_protocol
            ),
            "current_handoff_records_current_blocked_state": all(
                phrase in current_handoff for phrase in REQUIRED_CURRENT_HANDOFF_PHRASES
            ),
            "refresh_local_records_bounded_external_review_rule": all(
                phrase in refresh_local for phrase in REQUIRED_REFRESH_LOCAL_PHRASES
            ),
            "aggregate_13_row_review_records_scope_extension_reviewed": (
                "Installer Scope Closure" in aggregate_13_row_review_request
                and "source_tree_pod_gated_thirteen_row" in aggregate_13_row_review_request
                and "source_tree_pod_gated_thirteen_row_scope_extension_reviewed: true"
                in aggregate_13_row_review_request
                and "aggregate_13_row_installer_scope_review_required: false"
                in aggregate_13_row_review_request
            ),
            "aggregate_13_row_fallback_records_scope_extension_reviewed": (
                "The scoped installer/reproducibility blocker is closed"
                in aggregate_13_row_fallback_consensus
                and "source_tree_pod_gated_thirteen_row" in aggregate_13_row_fallback_consensus
                and "source_tree_pod_gated_thirteen_row_scope_extension_reviewed: true"
                in aggregate_13_row_fallback_consensus
                and "aggregate_13_row_installer_scope_review_required: false"
                in aggregate_13_row_fallback_consensus
            ),
            "thirteen_row_scope_extension_candidate_reviewed_not_release": all(
                phrase in thirteen_row_scope_extension_candidate
                for phrase in REQUIRED_THIRTEEN_ROW_SCOPE_EXTENSION_CANDIDATE_PHRASES
            ),
            "thirteen_row_scope_extension_review_request_prepared": all(
                phrase in thirteen_row_scope_extension_review_request
                for phrase in REQUIRED_THIRTEEN_ROW_SCOPE_EXTENSION_REVIEW_REQUEST_PHRASES
            ),
            "thirteen_row_scope_extension_claude_accepts_with_amendments_not_release": all(
                phrase in thirteen_row_scope_extension_claude_review
                for phrase in REQUIRED_THIRTEEN_ROW_SCOPE_EXTENSION_CLAUDE_REVIEW_PHRASES
            ),
            "thirteen_row_scope_extension_codex_consensus_reviewed_not_release": all(
                phrase in thirteen_row_scope_extension_codex_consensus
                for phrase in REQUIRED_THIRTEEN_ROW_SCOPE_EXTENSION_CODEX_CONSENSUS_PHRASES
            ),
            "secondary_platform_gate_waiver_reviewed_not_release": (
                secondary_platform_payload.get("status")
                == "compatibility_confirmed_hardware_scope_waiver_reviewed_not_release"
            ),
            "secondary_platform_closes_release_blocker_under_waiver": (
                secondary_platform_payload.get("secondary_platform_closes_release_blocker") is True
                and secondary_platform_payload.get("secondary_platform_closes_release_blocker_method")
                == "reviewed_hardware_scoped_waiver"
            ),
            "secondary_platform_records_hardware_scope": (
                secondary_platform_payload.get("secondary_platform_closes_release_blocker_scope")
                == SECONDARY_HARDWARE_SCOPE
                and secondary_platform_payload.get("hardware_performance_scope") == SECONDARY_HARDWARE_SCOPE
                and secondary_platform_payload.get("secondary_rt_hardware_scope_waiver_reviewed") is True
            ),
            "secondary_rt_performance_confirmation_false": (
                secondary_platform_payload.get("secondary_rt_performance_confirmation_authorized") is False
            ),
            "secondary_multi_gpu_portability_false": (
                secondary_platform_payload.get("multi_gpu_performance_portability_claim_authorized") is False
            ),
            "install_reproducibility_strategy_present": all(
                phrase in install_reproducibility_strategy for phrase in REQUIRED_INSTALL_REPRODUCIBILITY_PHRASES
            ),
            "install_gate_staged_pod_available": (
                install_reproducibility_payload.get("status")
                == "staged_pod_gate_present_general_release_installer_not_ready"
            ),
            "install_gate_general_release_installer_false": (
                install_reproducibility_payload.get("general_release_installer_ready") is False
            ),
            "install_gate_closes_release_blocker_under_scope": (
                install_reproducibility_payload.get("installer_closes_release_blocker") is True
            ),
            "install_gate_records_scoped_release": (
                install_reproducibility_payload.get("release_scope") == "source_tree_pod_gated_thirteen_row"
                and install_reproducibility_payload.get("installer_closes_release_blocker_scope")
                == "source_tree_pod_gated_thirteen_row"
                and install_reproducibility_payload.get("source_tree_pod_gated_scoped_release_wording_reviewed")
                is True
                and install_reproducibility_payload.get(
                    "source_tree_pod_gated_thirteen_row_scope_extension_reviewed"
                )
                is True
                and install_reproducibility_payload.get("aggregate_13_row_installer_scope_review_required")
                is False
            ),
            "install_gate_package_claim_false": (
                install_reproducibility_payload.get("package_install_claim_authorized") is False
            ),
            "next_engine_work_queue_present": all(
                phrase in next_engine_work_queue for phrase in REQUIRED_NEXT_ENGINE_QUEUE_PHRASES
            ),
            "next_engine_queue_status_closed_not_release": (
                next_engine_queue_payload.get("status") == "generic_engine_work_queue_closed_not_release"
            ),
            "next_engine_queue_existing_evidence_not_promotable": (
                next_engine_queue_payload.get("existing_evidence_promotable_now") is False
            ),
            "next_engine_queue_has_no_active_items_after_spatial_closure": len(next_engine_queue_payload.get("queue", [])) == 0,
            "next_engine_queue_has_barnes_hut_future_record": (
                any(
                    item.get("id") == "barnes_hut_vector_accumulation_frontier_shape"
                    and item.get("priority") == "future_research_not_current_p0"
                    for item in next_engine_queue_payload.get("future_generic_engine_work", [])
                )
            ),
            "next_engine_queue_has_barnes_hut_fused_partner_closed_work": (
                any(
                    item.get("id") == "barnes_hut_fused_partner_vector_accumulation"
                    and item.get("m7_rows_added") == 1
                    and item.get("candidate_row_id")
                    == "aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped"
                    for item in next_engine_queue_payload.get("closed_generic_engine_work", [])
                )
            ),
            "next_engine_queue_has_spatial_default_path_closed_work": (
                any(
                    item.get("id") == "spatial_squared_boundary_default_path_topology_stream"
                    and item.get("m7_rows_added") == 1
                    and item.get("candidate_row_id") == SPATIAL_SUPPLEMENTAL_M7_ROW
                    for item in next_engine_queue_payload.get("closed_generic_engine_work", [])
                )
            ),
            "next_engine_queue_has_no_spatial_future_research_record": (
                all(
                    item.get("id") != "spatial_rayjoin_topology_stream_author_gap"
                    for item in next_engine_queue_payload.get("future_generic_engine_work", [])
                )
            ),
        }
    )

    row_false_flags: list[bool] = []
    for row in m7_packet.get("row_classifications", []):
        row_false_flags.append(row.get("release_authorized") is False)
        row_false_flags.append(row.get("public_speedup_claim_authorized") is False)
        row_false_flags.append(row.get("broad_v3_faster_than_v2_claim_authorized") is False)
    checks["all_route_rows_keep_false_authorization"] = all(row_false_flags)
    current_review_packet_reference_files = [
        CURRENT_STATUS,
        READINESS_DISTANCE_PACKET,
        COMPLETION_AUDIT,
        PERFORMANCE_DOSSIER,
        OBJECTIVE_CONFORMANCE_GATE_JSON,
        LATEST_FULL_MATRIX,
        AABB_RUNNER_M2_REPORT,
        SURFACE_INTEGRITY_GATE_UPDATE_REPORT,
        SHORT_USER_PATH_GUARD_UPDATE_REPORT,
        BOUNDED_EXTERNAL_REVIEW_PROTOCOL,
        EXTERNAL_VERDICT_INTAKE,
        EXTERNAL_VERDICT_RESPONSE_TEMPLATE,
        CORE_GAPS_EXTERNAL_REVIEW,
        CORE_GAPS_EXTERNAL_INTAKE,
        CORE_GAPS_EXTERNAL_STATUS,
        SET_A_SET_B_RELEASE_BAR_PROPOSAL,
        SPATIAL_DEFAULT_PATH_CLAUDE_REVIEW,
        SPATIAL_DEFAULT_PATH_CODEX_CONSENSUS,
        SPATIAL_SQUARED_BOUNDARY_CANDIDATE,
        SPATIAL_SQUARED_BOUNDARY_CANDIDATE_JSON,
        SPATIAL_TOPOLOGY_STREAM_REDO_ALIGNMENT,
        THIRTEEN_ROW_SCOPE_EXTENSION_CANDIDATE,
        THIRTEEN_ROW_SCOPE_EXTENSION_CLAUDE_REVIEW,
        THIRTEEN_ROW_SCOPE_EXTENSION_CODEX_CONSENSUS,
    ]
    checks["aggregate_13_row_review_packet_reference_files_exist"] = all(
        path.exists() for path in current_review_packet_reference_files
    )

    evidence.update(
        {
            "m7_rows_from_packet": m7_rows_from_packet,
            "m7_rows_from_app_boundary": app_m7_rows,
            "base_m7_packet_summary": {
                "meaning": "The older base M7 packet before the later Spatial default-path extension; current surface row count is recorded separately as 13.",
                "m7_qualified_release_rows": base_m7_packet_summary.get("m7_qualified_release_rows"),
                "route_map_m7_qualified_release_rows": base_m7_packet_summary.get(
                    "route_map_m7_qualified_release_rows"
                ),
                "supplemental_m7_qualified_release_rows": base_m7_packet_summary.get(
                    "supplemental_m7_qualified_release_rows"
                ),
                "public_claim_rows": base_m7_packet_summary.get("public_claim_rows"),
                "row_scoped_public_claim_rows": base_m7_packet_summary.get("row_scoped_public_claim_rows"),
            },
            "wording_gate_status": wording_payload.get("status"),
            "wording_gate_level": wording_payload.get("gate_level"),
            "wording_gate_final_public_surface_gate": wording_payload.get("final_public_surface_gate"),
            "wording_gate_violation_count": len(wording_payload.get("violations", [])),
            "wording_gate_missing_required_strings": wording_payload.get("missing_required_strings", []),
            "wording_gate_missing_required_scanned_files": wording_payload.get("missing_required_scanned_files", []),
            "wording_gate_missing_expected_m7_row_ids": wording_payload.get("missing_expected_m7_row_ids", []),
            "wording_gate_release_authorization_note": wording_payload.get("release_authorization_note"),
            "major_performance_mandate_status": major_performance_payload.get("status"),
            "major_performance_mandate_blocking_reasons": major_performance_payload.get(
                "blocking_reasons", []
            ),
            "major_performance_mandate_path": str(MAJOR_PERFORMANCE_MANDATE.relative_to(ROOT)),
            "release_surface_breadth_status": release_surface_breadth_payload.get("status"),
            "release_surface_breadth_blocking_reasons": release_surface_breadth_payload.get("blocking_reasons", []),
            "release_surface_breadth_total_m7_row_count": release_surface_breadth_payload.get("evidence", {}).get(
                "total_m7_row_count"
            ),
            "release_surface_breadth_m7_capability_family_count": release_surface_breadth_payload.get(
                "evidence", {}
            ).get("m7_capability_family_count"),
            "release_surface_breadth_minimum_m7_capability_families": release_surface_breadth_payload.get(
                "evidence", {}
            ).get("minimum_m7_capability_families_for_major_release"),
            "release_surface_breadth_missing_m7_capability_families": release_surface_breadth_payload.get(
                "evidence", {}
            ).get("missing_m7_capability_families", []),
            "release_surface_breadth_existing_evidence_promotable_now": release_surface_breadth_payload.get(
                "evidence", {}
            ).get("existing_evidence_promotable_now"),
            "objective_conformance_status": objective_conformance_payload.get("status"),
            "objective_conformance_path": str(OBJECTIVE_CONFORMANCE_GATE_JSON.relative_to(ROOT)),
            "objective_conformance_required_capability_coverage_count": objective_conformance_payload.get(
                "evidence", {}
            ).get("objective_required_capability_coverage_count"),
            "objective_conformance_required_capability_count": objective_conformance_payload.get(
                "evidence", {}
            ).get("objective_required_capability_count"),
            "objective_conformance_required_capabilities_covered": objective_conformance_payload.get(
                "evidence", {}
            ).get("objective_required_capabilities_covered", []),
            "objective_conformance_exclusions": objective_conformance_payload.get("evidence", {}).get(
                "exclusions", {}
            ),
            "secondary_platform_status": secondary_platform_payload.get("status"),
            "secondary_rt_hardware_scope_waiver_reviewed": secondary_platform_payload.get(
                "secondary_rt_hardware_scope_waiver_reviewed"
            ),
            "secondary_platform_closes_release_blocker": secondary_platform_payload.get(
                "secondary_platform_closes_release_blocker"
            ),
            "secondary_platform_closes_release_blocker_method": secondary_platform_payload.get(
                "secondary_platform_closes_release_blocker_method"
            ),
            "secondary_platform_closes_release_blocker_scope": secondary_platform_payload.get(
                "secondary_platform_closes_release_blocker_scope"
            ),
            "hardware_performance_scope": secondary_platform_payload.get("hardware_performance_scope"),
            "secondary_rt_performance_confirmation_authorized": secondary_platform_payload.get(
                "secondary_rt_performance_confirmation_authorized"
            ),
            "multi_gpu_performance_portability_claim_authorized": secondary_platform_payload.get(
                "multi_gpu_performance_portability_claim_authorized"
            ),
            "secondary_platform_required_next_action": secondary_platform_payload.get("required_next_action"),
            "install_reproducibility_status": install_reproducibility_payload.get("status"),
            "staged_gpu_pod_gate_available": install_reproducibility_payload.get("staged_gpu_pod_gate_available"),
            "release_scope": install_reproducibility_payload.get("release_scope"),
            "source_tree_pod_gated_candidate_present": install_reproducibility_payload.get(
                "source_tree_pod_gated_candidate_present"
            ),
            "source_tree_pod_gated_candidate_reviewed": install_reproducibility_payload.get(
                "source_tree_pod_gated_candidate_reviewed"
            ),
            "source_tree_pod_gated_scoped_release_wording_reviewed": install_reproducibility_payload.get(
                "source_tree_pod_gated_scoped_release_wording_reviewed"
            ),
            "general_release_installer_ready": install_reproducibility_payload.get("general_release_installer_ready"),
            "installer_closes_release_blocker": install_reproducibility_payload.get("installer_closes_release_blocker"),
            "installer_closes_release_blocker_scope": install_reproducibility_payload.get(
                "installer_closes_release_blocker_scope"
            ),
            "package_install_claim_authorized": install_reproducibility_payload.get(
                "package_install_claim_authorized"
            ),
            "install_reproducibility_required_next_action": install_reproducibility_payload.get(
                "required_next_action"
            ),
            "next_engine_queue_status": next_engine_queue_payload.get("status"),
            "existing_evidence_promotable_now": next_engine_queue_payload.get("existing_evidence_promotable_now"),
            "next_engine_queue_ids": [item.get("id") for item in next_engine_queue_payload.get("queue", [])],
            "future_engine_work_ids": [
                item.get("id") for item in next_engine_queue_payload.get("future_generic_engine_work", [])
            ],
            "eleven_row_claude_review_verdict": "not-release-ready-fix-p0",
            "eleven_row_consensus_status": "claude_codex_consensus_current_eleven_row_not_release_ready_fix_p0",
            "aggregate_release_claude_review_verdict": "not-release-ready-fix-p0",
            "aggregate_release_consensus_status": (
                "claude_codex_consensus_phoenix_v3_aggregate_release_not_ready_fix_p0"
            ),
            "twelve_row_post_p1_claude_review_verdict": "approve-blocked-not-release",
            "twelve_row_consensus_status": "twelve_row_release_readiness_consensus_blocks_release",
            "final_wording_gate_claude_review_verdict": "approve-with-amendments",
            "final_wording_gate_consensus_status": (
                "claude_codex_consensus_final_public_surface_wording_gate_upgrade_complete_not_release"
            ),
            "release_surface_breadth_claude_review_verdict": "approve-with-amendments",
            "release_surface_breadth_consensus_status": (
                "claude_codex_consensus_release_surface_breadth_gate_complete_not_release"
            ),
            "aggregate_13_row_review_request_target": "thirteen_row_nine_capability_surface",
            "aggregate_13_row_scoped_dossier_external_review_status": (
                "external_verdict_obtained_claude_scoped_dossier_release_ready_not_v3_release"
            ),
            "aggregate_13_row_codex_subagent_verdict": "approve_blocked_not_release",
            "aggregate_13_row_fallback_consensus_status": (
                "codex_subagent_fallback_consensus_approve_blocked_not_release"
            ),
            "aggregate_13_row_scoped_dossier_external_authorization_obtained": True,
            "external_verdict_intake_status": external_verdict_intake_payload.get("status"),
            "external_verdict_intake_valid_external_verdict_obtained": external_verdict_intake_payload.get(
                "valid_external_verdict_obtained"
            ),
            "external_verdict_intake_release_authorized": external_verdict_intake_payload.get(
                "release_authorized"
            ),
            "external_verdict_intake_scoped_packet_authorized": external_verdict_intake_payload.get(
                "scoped_packet_authorized"
            ),
            "external_verdict_intake_accepted_verdict": external_verdict_intake_payload.get("accepted_verdict"),
            "external_verdict_intake_accepted_candidate_ids": [
                item.get("candidate_id") for item in external_verdict_intake_payload.get("accepted_candidates", [])
            ],
            "external_verdict_intake_path": str(EXTERNAL_VERDICT_INTAKE.relative_to(ROOT)),
            "external_verdict_intake_rejection_ids": [
                item.get("candidate_id") for item in external_verdict_intake_payload.get("current_rejections", [])
            ],
            "external_verdict_intake_rejection_reasons": {
                item.get("candidate_id"): item.get("reasons", [])
                for item in external_verdict_intake_payload.get("current_rejections", [])
            },
            "external_verdict_response_template_path": str(EXTERNAL_VERDICT_RESPONSE_TEMPLATE.relative_to(ROOT)),
            "external_verdict_response_template_contract": (
                "requires Reviewer plus one machine-readable Verdict label for intake"
            ),
            "core_gaps_external_verdict_status": core_gaps_external_intake_payload.get("status"),
            "core_gaps_external_verdict": core_gaps_external_intake_payload.get("accepted_verdict"),
            "core_gaps_external_status_line": core_gaps_external_intake_payload.get("status_line"),
            "core_gaps_external_release_authorized": core_gaps_external_intake_payload.get(
                "release_authorized"
            ),
            "core_gaps_external_scoped_packet_authorized": core_gaps_external_intake_payload.get(
                "scoped_packet_authorized"
            ),
            "core_gaps_external_public_speedup_claim_authorized": False,
            "core_gaps_external_broad_v3_faster_than_v2_claim_authorized": False,
            "core_gaps_external_major_version_mandate_overridden": False,
            "core_gaps_external_review_path": str(CORE_GAPS_EXTERNAL_REVIEW.relative_to(ROOT)),
            "core_gaps_external_verdict_intake_path": str(CORE_GAPS_EXTERNAL_INTAKE.relative_to(ROOT)),
            "core_gaps_external_status_path": str(CORE_GAPS_EXTERNAL_STATUS.relative_to(ROOT)),
            "core_gaps_external_verdict_effect": (
                "current non-release redirect to Gap 1; older aggregate release_ready remains "
                "scoped packet evidence only"
            ),
            "set_a_set_b_release_bar_proposal_status": "proposal_only_not_authorization",
            "set_a_set_b_release_bar_proposal_path": str(SET_A_SET_B_RELEASE_BAR_PROPOSAL.relative_to(ROOT)),
            "set_a_set_b_release_bar_proposal_precondition": (
                "freeze Set A / Set B classification and require runtime_executed True on >=2 Set-A probes "
                "before another full all-app pod run"
            ),
            "bounded_external_review_protocol_status": "active_process_guard",
            "bounded_external_review_protocol_path": str(BOUNDED_EXTERNAL_REVIEW_PROTOCOL.relative_to(ROOT)),
            "bounded_external_review_protocol_effect": (
                "the prior missing external review is recorded; the later accepted Claude release_ready "
                "verdict is scoped packet evidence and cannot override the major performance mandate"
            ),
            "current_handoff_path": str(CURRENT_HANDOFF.relative_to(ROOT)),
            "current_handoff_status": "current_handoff_records_redo_required_state",
            "refresh_local_path": str(REFRESH_LOCAL.relative_to(ROOT)),
            "refresh_local_bounded_external_review_status": "records_current_bounded_review_and_handoff_rule",
            "aggregate_13_row_review_packet_reference_file_count": len(current_review_packet_reference_files),
            "aggregate_13_row_review_packet_reference_files": [
                str(path.relative_to(ROOT)) for path in current_review_packet_reference_files
            ],
            "aggregate_13_row_installer_scope_review_required": False,
            "current_installer_closure_scope": install_reproducibility_payload.get(
                "installer_closes_release_blocker_scope"
            ),
            "thirteen_row_scope_extension_candidate_status": (
                "source_tree_pod_gated_thirteen_row_scope_extension_reviewed_not_release"
            ),
            "thirteen_row_scope_extension_reviewed": True,
            "thirteen_row_scope_extension_claude_review_verdict": "accept-with-amendments-not-release",
            "thirteen_row_scope_extension_consensus_status": (
                "claude_codex_consensus_source_tree_pod_gated_thirteen_row_scope_extension_reviewed_not_release"
            ),
            "proposed_installer_closure_scope": "source_tree_pod_gated_thirteen_row",
            "current_surface_m7_rows_from_release_surface": sorted(
                row_id
                for rows in release_surface_breadth_payload.get("evidence", {})
                .get("m7_rows_by_capability", {})
                .values()
                for row_id in rows
            ),
        }
    )
    return checks, evidence


def build_payload(strict_release: bool = False) -> dict[str, Any]:
    checks, evidence = _build_checks()
    failed_checks = [name for name, passed in checks.items() if not passed]
    structural_pass = not failed_checks

    major_performance_ready = evidence.get("major_performance_mandate_status") == "major_performance_passed"
    release_authorized = bool(
        structural_pass
        and major_performance_ready
        and evidence.get("external_verdict_intake_valid_external_verdict_obtained") is True
        and evidence.get("external_verdict_intake_accepted_verdict") == "release_ready"
        and evidence.get("external_verdict_intake_scoped_packet_authorized") is True
        and evidence.get("core_gaps_external_verdict") == "release_ready"
    )
    public_speedup_claim_authorized = False
    broad_v3_faster_than_v2_claim_authorized = False
    m7_qualified_release_rows = len(EXPECTED_CURRENT_M7_ROWS) if structural_pass else None

    if not structural_pass:
        status = "fail"
    elif release_authorized:
        status = "release_ready"
    elif evidence.get("major_performance_mandate_status") == "redo_required":
        status = "redo_required"
    else:
        status = "blocked_not_release"

    blocking_reasons = []
    if structural_pass and status == "redo_required":
        blocking_reasons = list(evidence.get("major_performance_mandate_blocking_reasons", []))
        if evidence.get("core_gaps_external_verdict") == "approve_blocked_not_release":
            blocking_reasons.append("current_core_gap_external_review_blocks_release")
    elif structural_pass and status == "blocked_not_release":
        blocking_reasons = [
            "release_authorization_false",
            "updated_thirteen_row_release_readiness_consensus_required",
        ]

    return {
        "tool": "v3_phoenix_release_readiness_gate",
        "gate": "v3_performance_release_candidate",
        "status": status,
        "strict_release_exit_requested": strict_release,
        "release_authorized": release_authorized,
        "public_speedup_claim_authorized": public_speedup_claim_authorized,
        "broad_v3_faster_than_v2_claim_authorized": broad_v3_faster_than_v2_claim_authorized,
        "m7_qualified_release_rows": m7_qualified_release_rows,
        "expected_m7_rows": list(EXPECTED_CURRENT_M7_ROWS),
        "expected_base_m7_packet_rows": list(EXPECTED_M7_ROWS),
        "expected_app_boundary_m7_rows": list(EXPECTED_APP_BOUNDARY_M7_ROWS),
        "blocking_reasons": blocking_reasons,
        "failed_checks": failed_checks,
        "checks": checks,
        "evidence": evidence,
        "decision_audit": {
            "decision": "Downgrade Phoenix V3 to redo_required until it proves broad V2.x performance superiority across serious all-app benchmarks.",
            "was_i_foolish": "Yes. I treated scoped row evidence and a scoped external verdict as enough for a V3 major release.",
            "foolish_actions": "I let a 13-row capability surface and accepted review obscure the user's harder requirement: V3 must solve V2.x's performance problem, not merely document selected wins.",
            "other_path": "Keep scoped release_ready and disclaim broad speed. That would be internally honest but product-wrong for a major V3.",
            "different_path_now": "Block release, preserve scoped evidence as internal material, and rebuild the generic runtime contracts that failed the completed serious all-app V3-vs-V2.x benchmark bar.",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate Phoenix V3 release-readiness gate.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument(
        "--strict-release",
        action="store_true",
        help="Exit nonzero when the current evidence is structurally valid but not release-authorized.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(strict_release=args.strict_release)
    text = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)

    if payload["status"] == "fail":
        return 2
    if args.strict_release and payload["status"] in {"blocked_not_release", "redo_required"}:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

