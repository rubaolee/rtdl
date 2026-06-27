#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ROUTE_MAP = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_p0_route_capability_map_2026-06-20.json"
M7_PACKET = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m7_row_classification_packet_2026-06-20.json"
RTNN_RECONCILIATION = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_m112_reconciliation_packet_2026-06-21.json"
)
RTNN_FULL_BATCH_FLOAT32_RUNNER = (
    ROOT / "scripts" / "v3_phoenix_rtnn_full_batch_float32_same_contract_runner.py"
)
RTNN_FULL_BATCH_FLOAT32_EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_full_batch_float32_same_contract_rtx_evidence_2026-06-21.json"
)
RTNN_FULL_BATCH_FLOAT32_REVIEW_GATE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_full_batch_float32_review_gate_2026-06-21.json"
)
RTNN_CUBIN_CACHE_EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_optix_cubin_cache_evidence_2026-06-21.json"
)
RTNN_SELF_QUERY_EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_prepared_self_query_evidence_2026-06-21.json"
)
RTNN_LAZY_EXACT_PREPARE_EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_lazy_exact_prepare_evidence_2026-06-21.json"
)
RTNN_SELF_QUERY_GRAPH_EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_self_query_graph_evidence_2026-06-21.json"
)
RTNN_COLUMN_SOURCE_RESIDENCY_GAP = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_column_source_residency_gap_2026-06-21.json"
)
RTNN_NPZ_CUBIN_CACHE_EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_npz_cubin_cache_evidence_2026-06-21.json"
)
RTNN_PREPARED_REPEAT50_AMORTIZATION_EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_prepared_repeat50_amortization_evidence_2026-06-21.json"
)
RTNN_PREPARED_REPEAT50_REVIEW_REQUEST = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_rtnn_prepared_repeat50_amortization_2026-06-21.md"
)
RTNN_PREPARED_REPEAT50_REVIEW_BLOCKED = (
    ROOT
    / "docs"
    / "reviews"
    / "external_review_blocked_phoenix_v3_rtnn_prepared_repeat50_amortization_2026-06-21.md"
)
RTNN_PREPARED_REPEAT50_REVIEW_GATE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_prepared_repeat50_review_gate_2026-06-21.json"
)
AABB_PREPARE_REUSE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_prepare_reuse_contract_2026-06-21.json"
)
AABB_PREPARE_REUSE_RUNNER = ROOT / "scripts" / "v3_phoenix_aabb_prepare_reuse_pod_runner.py"
AABB_PREPARE_REUSE_SERIOUS_EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_prepare_reuse_serious_rtx_evidence_2026-06-21.json"
)
AABB_PREPARE_REUSE_SCALE_EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_prepare_reuse_scale_evidence_2026-06-21.json"
)
AABB_PREPARE_REUSE_OVERHEAD_GATE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_prepare_reuse_overhead_gate_2026-06-21.json"
)
AABB_PREPARE_REUSE_QUERY_CACHE_EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_prepare_reuse_query_cache_evidence_2026-06-21.json"
)
AABB_NATIVE_QUERY_HANDLE_EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_native_query_handle_evidence_2026-06-21.json"
)
AABB_RAW_ORACLE_EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_raw_oracle_evidence_2026-06-21.json"
)
AABB_NATIVE_QUERY_HANDLE_STABILITY_EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_native_query_handle_stability_evidence_2026-06-21.json"
)
AABB_NATIVE_QUERY_HANDLE_REVIEW_GATE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_native_query_handle_review_gate_2026-06-21.json"
)
AABB_NATIVE_QUERY_HANDLE_ROW_WORDING_GATE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_native_query_handle_row_wording_gate_2026-06-21.json"
)
AABB_NATIVE_QUERY_HANDLE_FINAL_REVIEW_REQUEST = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_aabb_native_query_handle_final_m7_review_2026-06-21.md"
)
AABB_NATIVE_QUERY_HANDLE_FINAL_REVIEW_BLOCKED = (
    ROOT
    / "docs"
    / "reviews"
    / "external_ai_blocked_phoenix_v3_aabb_native_query_handle_final_m7_review_2026-06-21.md"
)
SPATIAL_RAYJOIN_TOPOLOGY_STREAM_CONTRACT = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_rayjoin_topology_stream_contract_2026-06-21.json"
)
SPATIAL_RAYJOIN_M3_GAP_ANALYSIS = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_rayjoin_m3_gap_analysis_2026-06-21.json"
)
SPATIAL_RAYJOIN_M3_EXACT_EXECUTOR_EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_spatial_rayjoin_topology_m3_public_county_exact_executor_repeat50_20260621"
    / "summary.json"
)
SPATIAL_RAYJOIN_EXACT_EXECUTOR_INTAKE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_rayjoin_exact_executor_intake_2026-06-21.json"
)
SPATIAL_RAYJOIN_RELATION_STATUS_NO_GO = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_rayjoin_relation_status_corrected_no_go_2026-06-21.json"
)
SPATIAL_RAYJOIN_RELATION_STATUS_EXACT_F64_INTAKE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_rayjoin_relation_status_exact_f64_intake_2026-06-21.json"
)
SPATIAL_RAYJOIN_RELATION_STATUS_EXACT_F64_REVIEW_GATE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_rayjoin_relation_status_exact_f64_review_gate_2026-06-21.json"
)
SPATIAL_RAYJOIN_RELATION_STATUS_EXACT_F64_ADVERSE_SUBSET = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_rayjoin_relation_status_exact_f64_adverse_subset_2026-06-21.json"
)
SPATIAL_RAYJOIN_ACTIVE_P0_CLOSURE_GATE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_active_p0_closure_gate_2026-06-21.json"
)
SPATIAL_RAYJOIN_PREFILTER_ZERO_EXPERIMENT = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_relation_status_prefilter_zero_experiment_2026-06-21.json"
)
SPATIAL_RAYJOIN_COUNT_ONLY_NO_DIAGNOSTICS_NO_GO = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_relation_status_count_only_no_diagnostics_no_go_2026-06-21.json"
)
SPATIAL_RAYJOIN_SQUARED_BOUNDARY_CANDIDATE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_relation_status_squared_boundary_candidate_2026-06-21.json"
)
SPATIAL_RAYJOIN_SQUARED_BOUNDARY_REVIEW_REQUEST = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_spatial_squared_boundary_candidate_2026-06-21.md"
)
SPATIAL_RAYJOIN_SQUARED_BOUNDARY_EXTERNAL_BLOCKED = (
    ROOT
    / "docs"
    / "reviews"
    / "external_ai_blocked_phoenix_v3_spatial_squared_boundary_candidate_2026-06-21.md"
)
SPATIAL_RAYJOIN_SQUARED_BOUNDARY_CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_spatial_squared_boundary_candidate_review_2026-06-21.md"
)
SPATIAL_RAYJOIN_SQUARED_BOUNDARY_CODEX_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_phoenix_v3_spatial_squared_boundary_candidate_2ai_consensus_2026-06-22.md"
)
SPATIAL_RAYJOIN_DEFAULT_PATH_REVIEW_REQUEST = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_spatial_default_path_promotion_2026-06-22.md"
)
SPATIAL_RAYJOIN_DEFAULT_PATH_CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_spatial_default_path_promotion_review_2026-06-22.md"
)
SPATIAL_RAYJOIN_DEFAULT_PATH_CODEX_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_phoenix_v3_spatial_default_path_promotion_2ai_consensus_2026-06-22.md"
)
SPATIAL_RAYJOIN_DEVICE_FILTERED_REJECTED_LOG = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_spatial_rayjoin_topology_m3_public_county_device_filtered_smoke_20260621"
    / "run.log"
)
SPATIAL_OVERLAY_ACTIVE_COUNT_FULL_SCALE_NO_GO = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_overlay_active_count_full_scale_no_go_2026-06-21.json"
)
SPATIAL_OVERLAY_ACTIVE_COUNT_FULL_SCALE_NO_GO_REVIEW_REQUEST = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_spatial_overlay_active_count_full_scale_no_go_2026-06-21.md"
)
BARNES_HUT_VECTOR_ACCUMULATION_CONTRACT = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_barnes_hut_vector_accumulation_contract_2026-06-21.json"
)
BARNES_HUT_SAME_BASIS_NO_GO = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_barnes_hut_same_basis_wall_time_no_go_2026-06-21.json"
)
BARNES_HUT_FUSED_PARTNER_M7_CANDIDATE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_barnes_hut_fused_partner_m7_candidate_2026-06-21.json"
)
BARNES_HUT_FUSED_PARTNER_REVIEW_REQUEST = (
    ROOT
    / "docs"
    / "reviews"
    / "call_for_review_phoenix_v3_barnes_hut_fused_partner_m7_candidate_2026-06-21.md"
)
BARNES_HUT_FUSED_PARTNER_CLAUDE_BLOCKED = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_blocked_phoenix_v3_barnes_hut_fused_partner_m7_candidate_2026-06-21.md"
)
BARNES_HUT_FUSED_PARTNER_CLAUDE_RETRY_BLOCKED = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_blocked_retry_phoenix_v3_barnes_hut_fused_partner_m7_candidate_2026-06-21.md"
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
BARNES_HUT_M129_WRAPPER_GATE = (
    ROOT
    / "docs"
    / "reports"
    / "goal4525_v3_0_m129_barnes_hut_rt_native_python_wrapper_gate_2026-06-17.json"
)
BARNES_HUT_M131_SEMANTIC_GATE = (
    ROOT
    / "docs"
    / "reports"
    / "goal4527_v3_0_m131_barnes_hut_rt_native_traversal_semantic_gate_2026-06-17.json"
)
BARNES_HUT_M142_CLOSURE_GATE = (
    ROOT
    / "docs"
    / "reports"
    / "goal4541_v3_0_m142_barnes_hut_current_route_closure_gate_2026-06-17.json"
)


CLOSED_GENERIC_ENGINE_WORK: tuple[dict[str, Any], ...] = (
    {
        "id": "grouped_reduction_prepare_amortization",
        "priority": "P0",
        "apps_used_as_evidence": ["raydb_style"],
        "generic_capability": "grouped_reduction",
        "closed_state": (
            "The explicit cupy_device_columns prepared grouped_sum route produced two "
            "supplemental row-scoped M7 rows after POD evidence, subagent review, and "
            "Codex consensus. This closes the prepare-amortization reopen item for the "
            "tested exact rows only."
        ),
        "closed_by_packet": (
            "docs/rebuild/v3/phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2026-06-21.md"
        ),
        "closed_by_consensus": (
            "docs/reviews/codex_phoenix_v3_grouped_reduction_device_column_m7_final_review_packet_2ai_consensus_2026-06-21.md"
        ),
        "m7_rows_added": 2,
        "forbidden_shortcut": (
            "Do not promote whole RayDB, count rows, true zero-copy, pure backend-only ratios, "
            "or broad V3-over-V2 claims from this closure."
        ),
    },
)


QUEUE: tuple[dict[str, Any], ...] = (
    {
        "id": "rtnn_ranked_summary_wall_path",
        "priority": "P0",
        "apps_used_as_evidence": ["rtnn"],
        "generic_capability": "ranked_summary",
        "current_state": (
            "The 65k clustered/shell/uniform raw-summary ladder has OptiX hot wins but "
            "all three wall ratios regress. M104-M112 prove a stronger large aggregate "
            "route exists. A fresh 1,048,576-point RTX same-contract float32 rerun now "
            "shows a 7.790x prepared hot-query OptiX/CuPy-grid win with parity, but "
            "cold-plus-query is 0.393x and runner wall is 0.627x. A generic OptiX CUBIN "
            "content-addressed disk cache now removes most repeated new-process compile "
            "cost for the same serious harness: execution_prepare drops 3.337s to 0.564s "
            "(5.914x), cold-plus-query drops 5.418s to 2.635s (2.056x), and runner wall "
            "drops 6.122s to 3.431s (1.785x). This is real engine progress, but the warm "
            "row still is not M7: cold-plus-query is 0.794x versus CuPy and runner wall "
            "is only 1.098x, below the 2.0x material floor. The next generic self-query "
            "aggregate batch path reuses prepared search device columns as query columns: "
            "it gives 2.482x hot-query speedup and 2.784x input-pack reduction versus the "
            "old prepared-query route, and 19.437x hot-query speedup versus CuPy grid, "
            "with same-contract parity. It still is not M7 because cold-plus-query versus "
            "CuPy is only 1.214x and runner wall is only 1.030x. A later generic lazy "
            "exact-search materialization patch avoids building the unused double-precision "
            "exact search device buffer for float32 aggregate/self-query routes; the same "
            "RTX POD rerun improves self-query prepare by 1.111x and cold-plus-query by "
            "1.080x, but same-day CuPy comparisons are still only 1.292x cold-plus-query "
            "and 1.076x runner-wall. Phoenix then added a generic prepared self-query CUDA "
            "graph replay route and removed the stale 65,536 native graph query cap. A 1,048,576 "
            "point POD run proves same-contract parity and prepared-search-as-query residency, "
            "but graph replay is only about 1.013x on cold-plus-query versus direct self-query "
            "batch, so it is functional engine surface, not a material RTNN performance row. "
            "Phoenix now adds a generic NPZ/NumPy column-source path to the serious RTNN runner "
            "and records the file/column ingestion or residency overhead blocker as a gate: "
            "existing self-query evidence still has only 1.030x runner wall versus CuPy, input "
            "load is 72.8% of runner wall, and non-hot wall is about 491x the hot query. The "
            "column-source path is implemented and locally tested, but it is not M7 until a "
            "fresh same-hardware POD rerun with point_column_source=npz clears parity plus "
            "cold/runner material floors and review. Phoenix then ran that same-hardware "
            "NPZ route and confirmed the input-load blocker was removed, but without the "
            "CUBIN cache OptiX still lost runner wall at 0.312x because execution_prepare "
            "was about 3.007s. Combining NPZ column ingestion with the generic OptiX CUBIN "
            "cache gives a real positive wall result: execution_prepare drops to 0.227s, "
            "cold-plus-query is 1.247x over CuPy grid, and runner wall is 1.328x. This is "
            "still not M7 because both cold-plus-query and runner wall remain below the "
            "2.0x material floor and no external review has accepted RTNN. A follow-up "
            "prepared-session amortization run uses the same 1,048,576 point NPZ+CUBIN "
            "route with repeat=50: hot query is 7.889x over CuPy grid, cold-plus-query "
            "is 1.315x, and runner wall is 3.761x. This is the first current RTNN "
            "runner-wall material candidate, but only for the scoped prepared repeat50 "
            "contract; it adds zero M7 rows until external review and Codex consensus."
        ),
        "generic_engine_action": (
            "Keep the full-batch float32 row behind the review gate. Continue generic "
            "engine work by sending the prepared repeat50 candidate to external review. "
            "If review is blocked, keep the row pending and move to another P0 blocker; "
            "if review accepts it, add only the scoped prepared-session row wording."
        ),
        "evidence_to_reopen_m7": (
            "Unblocked external AI review, Codex consensus response, prepared-hot-query "
            "scope review, NPZ+CUBIN repeat50 POD evidence scoped to prepared-session "
            "amortization, phase/wall timing, source manifest, correctness "
            "summary, and explicit non-universal wording."
        ),
        "reconciliation_packet": (
            "docs/rebuild/v3/phoenix_v3_rtnn_m112_reconciliation_packet_2026-06-21.md"
        ),
        "active_pod_runner": (
            "scripts/v3_phoenix_rtnn_full_batch_float32_same_contract_runner.py"
        ),
        "active_pod_runner_status": (
            "serious_rtx_evidence_collected_hot_query_candidate_pending_2ai_wall_blocked"
        ),
        "latest_evidence_packet": (
            "docs/rebuild/v3/phoenix_v3_rtnn_full_batch_float32_same_contract_rtx_evidence_2026-06-21.md"
        ),
        "latest_review_gate_packet": (
            "docs/rebuild/v3/phoenix_v3_rtnn_full_batch_float32_review_gate_2026-06-21.md"
        ),
        "latest_review_gate_status": "rtnn_full_batch_float32_review_blocked_not_m7",
        "latest_cubin_cache_packet": (
            "docs/rebuild/v3/phoenix_v3_rtnn_optix_cubin_cache_evidence_2026-06-21.md"
        ),
        "latest_cubin_cache_status": (
            "rtnn_optix_cubin_cache_reduces_prepare_not_m7_wall_floor_not_met"
        ),
        "latest_self_query_packet": (
            "docs/rebuild/v3/phoenix_v3_rtnn_prepared_self_query_evidence_2026-06-21.md"
        ),
        "latest_self_query_status": (
            "rtnn_prepared_self_query_hot_path_material_not_m7_wall_floor_not_met"
        ),
        "latest_lazy_exact_prepare_packet": (
            "docs/rebuild/v3/phoenix_v3_rtnn_lazy_exact_prepare_evidence_2026-06-21.md"
        ),
        "latest_lazy_exact_prepare_status": (
            "rtnn_lazy_exact_prepare_reduces_prepare_not_m7_wall_floor_not_met"
        ),
        "latest_self_query_graph_packet": (
            "docs/rebuild/v3/phoenix_v3_rtnn_self_query_graph_evidence_2026-06-21.md"
        ),
        "latest_self_query_graph_status": (
            "rtnn_self_query_graph_large_scale_functional_not_m7_material_floor_not_met"
        ),
        "latest_column_source_packet": (
            "docs/rebuild/v3/phoenix_v3_rtnn_column_source_residency_gap_2026-06-21.md"
        ),
        "latest_column_source_status": "rtnn_npz_column_source_ready_for_pod_rerun_not_m7",
        "latest_npz_cubin_packet": (
            "docs/rebuild/v3/phoenix_v3_rtnn_npz_cubin_cache_evidence_2026-06-21.md"
        ),
        "latest_npz_cubin_status": (
            "rtnn_npz_cubin_cache_wall_improves_not_m7_material_floor_not_met"
        ),
        "latest_repeat50_packet": (
            "docs/rebuild/v3/phoenix_v3_rtnn_prepared_repeat50_amortization_evidence_2026-06-21.md"
        ),
        "latest_repeat50_status": (
            "rtnn_prepared_repeat50_amortization_m7_candidate_pending_external_review_not_release"
        ),
        "latest_repeat50_review_request": (
            "docs/reviews/call_for_review_phoenix_v3_rtnn_prepared_repeat50_amortization_2026-06-21.md"
        ),
        "latest_repeat50_review_blocked_record": (
            "docs/reviews/external_review_blocked_phoenix_v3_rtnn_prepared_repeat50_amortization_2026-06-21.md"
        ),
        "active_candidate_status": (
            "rtnn_prepared_repeat50_candidate_pending_external_review_not_m7"
        ),
        "forbidden_shortcut": (
            "Do not publish hot-query-only RTNN speedups as end-to-end, wall-clock, "
            "paper, V2 comparison, or universal nearest-neighbor claims."
        ),
    },
    {
        "id": "contact_aabb_prepare_reuse",
        "priority": "P0",
        "apps_used_as_evidence": ["contact_manifold", "librts_spatial_index"],
        "generic_capability": "aabb_candidate_stream",
        "current_state": (
            "AABB candidate-stream has one strong M7 count-only row. A serious 32,768 AABB "
            "prepare-reuse RTX run moved the repeated wall result positive at 1.140x OptiX/Embree, "
            "but it remains below the 1.20 material-speedup floor. A 65,536-row repeat50 scale "
            "rerun fell to 1.087x, so scale alone does not reopen M7. The overhead gate now "
            "blocks this route explicitly. A follow-up generic Python query-record cache is real "
            "(one miss and 52 hits per serious backend row) and improves the 32,768 cold-plus-collect "
            "wall ratio to 1.188x, but it still misses the 1.20x floor and the 65,536 row is only "
            "1.135x. The deeper generic native prepared-query handle path now reuses OptiX packed "
            "box-query handles for range_intersection_rows. On the RTX 4000 Ada pod, the same "
            "serious runner cleared the material floor at 32,768 rows with 1.719x cold-plus-collect "
            "wall speedup and at 65,536 rows with 1.637x, with native cache stats showing one miss "
            "and 52 hits. A Huygens review blocked promotion until raw AABB oracle, provenance, "
            "fresh-run stability, external review, and stable-row materialization were closed. "
            "The raw Embree/OptiX oracle now matches an independent closed-boundary CPU AABB oracle, "
            "OptiX fail-closed overflow is observed, and source-manifest provenance is recorded. "
            "Six fresh POD runs across 32,768 and 65,536 AABBs also keep the cold-plus-collect "
            "wall win above the 1.20x material floor, with the weakest fresh run at 1.644x. "
            "Phoenix now defines two stable native-query-handle candidate row ids for 32,768 and "
            "65,536 jittered_grid repeat50 rows and draft non-publishable wording. The route remains "
            "review-blocked/not-M7 because external/2-AI review, external public wording review, and "
            "post-external Codex consensus are still missing. Phoenix now has a concise final external "
            "M7 review request for the exact two stable row IDs, but the latest Claude/Gemini/Chrome "
            "routes produced only tool-blockage evidence, not an external verdict."
        ),
        "generic_engine_action": (
            "Request a new external review over the native-query-handle packet plus the raw oracle, "
            "source-manifest, stability, row-wording, and review-gate packets. If accepted, use only "
            "the two stable candidate row ids for generic AABB candidate streaming; keep full contact "
            "solving, broad AABB, and V3-over-V2 wording out."
        ),
        "evidence_to_reopen_m7": (
            "External AI review, Codex consensus response after external review, and external "
            "row-scoped public wording review. Stable candidate row ids, raw AABB oracle correctness, "
            "source-manifest provenance, fail-closed overflow, and fresh-run stability are now present."
        ),
        "active_candidate_packet": (
            "docs/rebuild/v3/phoenix_v3_aabb_prepare_reuse_contract_2026-06-21.md"
        ),
        "active_candidate_status": "aabb_native_query_handle_review_blocked_not_m7",
        "latest_evidence_packet": (
            "docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_evidence_2026-06-21.md"
        ),
        "latest_evidence_status": "aabb_native_query_handle_m7_candidate_pending_external_review",
        "latest_raw_oracle_packet": (
            "docs/rebuild/v3/phoenix_v3_aabb_raw_oracle_evidence_2026-06-21.md"
        ),
        "latest_raw_oracle_status": "aabb_raw_oracle_pass_not_m7",
        "latest_stability_packet": (
            "docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_stability_evidence_2026-06-21.md"
        ),
        "latest_stability_status": "aabb_native_query_handle_stability_pass_not_m7",
        "latest_review_gate_packet": (
            "docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_review_gate_2026-06-21.md"
        ),
        "latest_review_gate_status": "aabb_native_query_handle_review_blocked_not_m7",
        "latest_final_review_request": (
            "docs/reviews/call_for_review_phoenix_v3_aabb_native_query_handle_final_m7_review_2026-06-21.md"
        ),
        "latest_final_review_blocked_record": (
            "docs/reviews/external_ai_blocked_phoenix_v3_aabb_native_query_handle_final_m7_review_2026-06-21.md"
        ),
        "latest_row_wording_gate_packet": (
            "docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_row_wording_gate_2026-06-21.md"
        ),
        "latest_row_wording_gate_status": (
            "aabb_native_query_handle_row_wording_gate_closed_after_claude_codex_m7_review"
        ),
        "previous_query_cache_packet": (
            "docs/rebuild/v3/phoenix_v3_aabb_prepare_reuse_query_cache_evidence_2026-06-21.md"
        ),
        "previous_query_cache_status": "aabb_prepare_reuse_query_cache_evidence_not_m7_wall_floor_not_met",
        "latest_overhead_gate_packet": (
            "docs/rebuild/v3/phoenix_v3_aabb_prepare_reuse_overhead_gate_2026-06-21.md"
        ),
        "latest_overhead_gate_status": "aabb_prepare_reuse_overhead_gate_blocked_not_m7",
        "previous_scale_evidence_packet": (
            "docs/rebuild/v3/phoenix_v3_aabb_prepare_reuse_scale_evidence_2026-06-21.md"
        ),
        "previous_scale_evidence_status": "aabb_prepare_reuse_scale_evidence_not_m7_scale_does_not_clear_floor",
        "previous_evidence_packet": (
            "docs/rebuild/v3/phoenix_v3_aabb_prepare_reuse_serious_rtx_evidence_2026-06-21.md"
        ),
        "previous_evidence_status": "aabb_prepare_reuse_serious_rtx_evidence_not_m7_low_margin",
        "active_pod_runner": "scripts/v3_phoenix_aabb_prepare_reuse_pod_runner.py",
        "active_pod_runner_status": "native_query_handle_oracle_and_stability_collected_review_blocked_not_m7",
        "forbidden_shortcut": (
            "Do not claim full contact solving, physics throughput, broad AABB-index acceleration, "
            "or broad V3-over-V2 speedup from this candidate. Do not call it M7 until external "
            "review and Codex consensus close."
        ),
    },
    {
        "id": "spatial_rayjoin_topology_stream_author_gap",
        "priority": "P0",
        "apps_used_as_evidence": ["spatial_rayjoin"],
        "generic_capability": "point_location_topology_stream",
        "current_state": (
            "Authored tiled hot routes are strong internal evidence, but RayJoin author RT remains "
            "faster than RTDL OptiX on the PIP comparison and no Spatial RayJoin row is M7-qualified. "
            "The M3 gap analysis shows the real V3 target: old large-PIP evidence moves OptiX hot "
            "wall from 273.922ms to 120.060ms (2.282x) when the query point stream stays resident, "
            "while all public/release/zero-copy flags remain false. The local prepared OptiX payload "
            "now emits a non-authorizing topology_stream_m3_phase_table_v1 and "
            "topology_stream_prepared_handle_v1 metadata. A fresh RTX 4000 Ada public county POD "
            "run collected 5 samples with repeat=50 through exact_prepared_points_executor: row_count "
            "47,262 stayed stable, the full M3 table was present, query-stream residency was "
            "device_resident_prepared_point_probe_columns_with_reusable_exact_executor, and all "
            "claim flags remained false. The rejected device-filtered probe mismatched exact count "
            "47,570 != 47,262, so it remains a correctness blocker, not a fast route."
            " The exact-executor intake now records the key generic bottleneck: topology "
            "continuation/exact refinement is 52.893x the RT traversal/candidate-emission "
            "median and accounts for 99.663% of prepared-query median time. A follow-up "
            "relation_status_corrected_executor_validated POD smoke failed exact validation "
            "at 47,259 != 47,262, so that fused route is recorded as a no-go. A later "
            "native exact-f64 repair changed the reusable scalar-count path to evaluate the "
            "full closed-shape predicate on the device for every AABB candidate; the fresh "
            "repeat50/sample5 RTX packet is exact at 47,262 rows, reduces prepared-query "
            "median from 0.023218s to 0.006309s (3.680x) versus the exact executor, and "
            "is now explicitly review-blocked/not M7 because Claude/Gemini did not produce "
            "an external verdict and author-basis/wording gates remain open. A same-county "
            "RayJoin author timing run now exists for br_county.cdb/br_county.cdb with "
            "repeat=50/warmup=5: author Query is 1.86566ms, about 3.383x faster than "
            "the current RTDL exact-f64 prepared-query median, and query_exec does not "
            "print an author result count. A fresh "
            "br_county_subset adverse-parity POD packet now passes at row_count 6 with "
            "full M3 accounting and no claim flags, closing only the adverse-subset parity "
            "blocker."
        ),
        "generic_engine_action": (
            "Keep the exact-f64 generic device scalar-count intake behind the review gate. Retry "
            "external review when Claude/Gemini is available, add same-dataset author-timing-basis "
            "and public wording review, and do not promote the route from hot-query evidence alone."
        ),
        "evidence_to_reopen_m7": (
            "Unblocked external AI review, Codex consensus response, author-timing-basis comparison, "
            "M3 phase table, same-contract semantics, and non-paper wording. Adverse-subset parity "
            "is now present but is not sufficient for M7."
        ),
        "active_candidate_packet": (
            "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_topology_stream_contract_2026-06-21.md"
        ),
        "active_candidate_status": "spatial_rayjoin_topology_stream_contract_candidate_not_m7",
        "latest_evidence_packet": (
            "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_topology_stream_exact_executor_pod_evidence_2026-06-21.md"
        ),
        "latest_evidence_json": (
            "docs/rebuild/v3/evidence/phoenix_v3_spatial_rayjoin_topology_m3_public_county_exact_executor_repeat50_20260621/summary.json"
        ),
        "latest_evidence_status": "spatial_rayjoin_topology_stream_m3_pod_evidence_pending_review_not_m7",
        "latest_methodology_packet": (
            "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_exact_executor_intake_2026-06-21.md"
        ),
        "latest_methodology_status": "spatial_rayjoin_exact_executor_intake_not_m7",
        "latest_no_go_packet": (
            "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_corrected_no_go_2026-06-21.md"
        ),
        "latest_no_go_status": "spatial_rayjoin_relation_status_corrected_executor_no_go_exact_mismatch",
        "latest_repair_intake_packet": (
            "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_intake_2026-06-21.md"
        ),
        "latest_repair_intake_status": (
            "spatial_rayjoin_relation_status_exact_f64_device_scalar_count_intake_not_m7"
        ),
        "latest_repair_review_gate_packet": (
            "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_review_gate_2026-06-21.md"
        ),
        "latest_repair_review_gate_status": (
            "spatial_rayjoin_relation_status_exact_f64_review_blocked_not_m7"
        ),
        "latest_repair_author_timing_basis_packet": (
            "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_author_basis_same_county_2026-06-21.md"
        ),
        "latest_repair_author_timing_basis_status": (
            "present_but_not_m7_author_query_faster_count_not_printed"
        ),
        "latest_repair_author_timing_basis_scope": (
            "same_county_br_county_query_exec_timing_present_author_count_not_printed"
        ),
        "latest_repair_adverse_subset_packet": (
            "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_adverse_subset_2026-06-21.md"
        ),
        "latest_repair_adverse_subset_status": (
            "spatial_rayjoin_relation_status_exact_f64_adverse_subset_parity_pass_not_m7"
        ),
        "previous_evidence_packet": (
            "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_m3_gap_analysis_2026-06-21.md"
        ),
        "previous_evidence_status": "spatial_rayjoin_m3_gap_analysis_not_m7",
        "rejected_probe_log": (
            "docs/rebuild/v3/evidence/phoenix_v3_spatial_rayjoin_topology_m3_public_county_device_filtered_smoke_20260621/run.log"
        ),
        "rejected_probe_status": "device_filtered_prepared_points_validated_rejected_exact_count_mismatch",
        "active_pod_runner": "scripts/v3_phoenix_spatial_rayjoin_topology_stream_m3_pod_runner.py",
        "active_pod_runner_status": "exact_executor_repeat50_pod_evidence_collected_not_m7",
        "forbidden_shortcut": (
            "Do not compare the tiny all-workload health row to paper-scale RayJoin results, "
            "claim RTDL beats RayJoin, call the device-resident internal delta true zero-copy, "
            "or implement a RayJoin-only native shortcut."
        ),
    },
)


FUTURE_GENERIC_ENGINE_WORK: tuple[dict[str, Any], ...] = (
    {
        "id": "barnes_hut_vector_accumulation_frontier_shape",
        "priority": "future_research_not_current_p0",
        "apps_used_as_evidence": ["barnes_hut"],
        "generic_capability": "vector_accumulation",
        "current_state": (
            "Barnes-Hut is closed for the current V3 route surface as mixed explicit route guidance: "
            "fused CPU/Numba or fused Numba CUDA by scale, with prepared RTDL/OptiX retained only as "
            "OptiX-library CUDA aggregate-frontier device-column evidence. The current prepared RTDL/OptiX "
            "frontier-emission shape loses to fused Numba CUDA on the serious M6 rerun, and M131 blocks a "
            "naive all-node OptiX any-hit implementation because it cannot prove parent-acceptance "
            "subtree-skip semantics. Therefore this is not an active Phoenix P0 build target and adds zero M7 rows."
        ),
        "generic_engine_action": (
            "Keep the generic fused weighted-vector RT-native contract as future research/claim expansion only. "
            "Do not spend current Phoenix V3 release work on an all-node OptiX shortcut; reopen only after a "
            "reviewed hierarchical traversal lowering proves no double counting and beats the fused partner route."
        ),
        "evidence_to_reopen_m7": (
            "A reviewed generic hierarchical traversal design that preserves subtree-skip semantics, an executable "
            "RT-native fused weighted-vector implementation, fresh same-contract RTX evidence beating fused CPU/Numba "
            "and fused Numba CUDA, and external review plus Codex consensus."
        ),
        "active_candidate_packet": (
            "docs/rebuild/v3/phoenix_v3_barnes_hut_vector_accumulation_contract_2026-06-21.md"
        ),
        "active_candidate_status": "barnes_hut_future_research_not_current_p0_not_m7",
        "m129_wrapper_gate": (
            "docs/reports/goal4525_v3_0_m129_barnes_hut_rt_native_python_wrapper_gate_2026-06-17.json"
        ),
        "m131_semantic_gate": (
            "docs/reports/goal4527_v3_0_m131_barnes_hut_rt_native_traversal_semantic_gate_2026-06-17.json"
        ),
        "m142_closure_gate": (
            "docs/reports/goal4541_v3_0_m142_barnes_hut_current_route_closure_gate_2026-06-17.json"
        ),
        "forbidden_shortcut": (
            "Do not publish Barnes-Hut RT-core speedup wording, do not call fused Numba CUDA an RT-core route, "
            "and do not treat Goal4541 current-route closure as RT-native Barnes-Hut completion."
        ),
    },
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    route_map = _load_json(ROUTE_MAP)
    m7_packet = _load_json(M7_PACKET)
    rtnn_reconciliation = _load_json(RTNN_RECONCILIATION)
    rtnn_full_batch_evidence = _load_json(RTNN_FULL_BATCH_FLOAT32_EVIDENCE)
    rtnn_full_batch_review_gate = _load_json(RTNN_FULL_BATCH_FLOAT32_REVIEW_GATE)
    rtnn_cubin_cache_evidence = _load_json(RTNN_CUBIN_CACHE_EVIDENCE)
    rtnn_self_query_evidence = _load_json(RTNN_SELF_QUERY_EVIDENCE)
    rtnn_lazy_exact_prepare_evidence = _load_json(RTNN_LAZY_EXACT_PREPARE_EVIDENCE)
    rtnn_self_query_graph_evidence = _load_json(RTNN_SELF_QUERY_GRAPH_EVIDENCE)
    rtnn_column_source_residency_gap = _load_json(RTNN_COLUMN_SOURCE_RESIDENCY_GAP)
    rtnn_npz_cubin_cache_evidence = _load_json(RTNN_NPZ_CUBIN_CACHE_EVIDENCE)
    rtnn_prepared_repeat50_amortization = _load_json(
        RTNN_PREPARED_REPEAT50_AMORTIZATION_EVIDENCE
    )
    rtnn_prepared_repeat50_review_gate = _load_json(RTNN_PREPARED_REPEAT50_REVIEW_GATE)
    aabb_prepare_reuse = _load_json(AABB_PREPARE_REUSE)
    aabb_prepare_reuse_serious = _load_json(AABB_PREPARE_REUSE_SERIOUS_EVIDENCE)
    aabb_prepare_reuse_scale = _load_json(AABB_PREPARE_REUSE_SCALE_EVIDENCE)
    aabb_prepare_reuse_overhead_gate = _load_json(AABB_PREPARE_REUSE_OVERHEAD_GATE)
    aabb_prepare_reuse_query_cache = _load_json(AABB_PREPARE_REUSE_QUERY_CACHE_EVIDENCE)
    aabb_native_query_handle = _load_json(AABB_NATIVE_QUERY_HANDLE_EVIDENCE)
    aabb_raw_oracle = _load_json(AABB_RAW_ORACLE_EVIDENCE)
    aabb_native_query_handle_stability = _load_json(AABB_NATIVE_QUERY_HANDLE_STABILITY_EVIDENCE)
    aabb_native_query_handle_review_gate = _load_json(AABB_NATIVE_QUERY_HANDLE_REVIEW_GATE)
    aabb_native_query_handle_row_wording_gate = _load_json(AABB_NATIVE_QUERY_HANDLE_ROW_WORDING_GATE)
    spatial_topology_contract = _load_json(SPATIAL_RAYJOIN_TOPOLOGY_STREAM_CONTRACT)
    spatial_m3_gap_analysis = _load_json(SPATIAL_RAYJOIN_M3_GAP_ANALYSIS)
    spatial_m3_exact_executor_evidence = _load_json(SPATIAL_RAYJOIN_M3_EXACT_EXECUTOR_EVIDENCE)
    spatial_exact_executor_intake = _load_json(SPATIAL_RAYJOIN_EXACT_EXECUTOR_INTAKE)
    spatial_relation_status_no_go = _load_json(SPATIAL_RAYJOIN_RELATION_STATUS_NO_GO)
    spatial_relation_status_exact_f64 = _load_json(SPATIAL_RAYJOIN_RELATION_STATUS_EXACT_F64_INTAKE)
    spatial_relation_status_exact_f64_review_gate = _load_json(
        SPATIAL_RAYJOIN_RELATION_STATUS_EXACT_F64_REVIEW_GATE
    )
    spatial_relation_status_exact_f64_adverse_subset = _load_json(
        SPATIAL_RAYJOIN_RELATION_STATUS_EXACT_F64_ADVERSE_SUBSET
    )
    spatial_active_p0_closure_gate = _load_json(SPATIAL_RAYJOIN_ACTIVE_P0_CLOSURE_GATE)
    spatial_prefilter_zero_experiment = _load_json(SPATIAL_RAYJOIN_PREFILTER_ZERO_EXPERIMENT)
    spatial_count_only_no_diag_no_go = _load_json(SPATIAL_RAYJOIN_COUNT_ONLY_NO_DIAGNOSTICS_NO_GO)
    spatial_squared_boundary_candidate = _load_json(SPATIAL_RAYJOIN_SQUARED_BOUNDARY_CANDIDATE)
    spatial_overlay_active_count_full_scale_no_go = _load_json(
        SPATIAL_OVERLAY_ACTIVE_COUNT_FULL_SCALE_NO_GO
    )
    barnes_hut_vector_contract = _load_json(BARNES_HUT_VECTOR_ACCUMULATION_CONTRACT)
    barnes_hut_same_basis_no_go = _load_json(BARNES_HUT_SAME_BASIS_NO_GO)
    barnes_hut_fused_partner_candidate = _load_json(BARNES_HUT_FUSED_PARTNER_M7_CANDIDATE)
    barnes_hut_m129_wrapper_gate = _load_json(BARNES_HUT_M129_WRAPPER_GATE)
    barnes_hut_m131_semantic_gate = _load_json(BARNES_HUT_M131_SEMANTIC_GATE)
    barnes_hut_m142_closure_gate = _load_json(BARNES_HUT_M142_CLOSURE_GATE)
    allowed = set(route_map["allowed_generic_capabilities"])
    queue = [dict(item) for item in QUEUE]
    closed = [dict(item) for item in CLOSED_GENERIC_ENGINE_WORK]
    future_work = [dict(item) for item in FUTURE_GENERIC_ENGINE_WORK]
    spatial_active_p0_closed = (
        spatial_active_p0_closure_gate.get("active_p0_closure_authorized") is True
        and spatial_active_p0_closure_gate.get("external_review_verdict") == "close-active-p0"
        and spatial_active_p0_closure_gate.get("external_review_source") == "claude"
        and spatial_active_p0_closure_gate.get("codex_consensus_status")
        == "codex_consensus_complete_close_active_p0_future_research"
        and spatial_active_p0_closure_gate.get("m7_promotion_authorized") is False
        and spatial_active_p0_closure_gate.get("release_authorized") is False
        and spatial_active_p0_closure_gate.get("rtdl_beats_rayjoin_claim_authorized") is False
        and spatial_active_p0_closure_gate.get("failed_checks") == []
    )
    spatial_overlay_metrics = spatial_overlay_active_count_full_scale_no_go.get("metrics", {})
    spatial_overlay_pair_count = int(spatial_overlay_metrics.get("shape_pair_count", 0))
    spatial_overlay_optix_count = int(spatial_overlay_metrics.get("optix_active_count", 0))
    spatial_overlay_embree_count = int(spatial_overlay_metrics.get("embree_active_count", 0))
    spatial_overlay_count_delta = int(
        spatial_overlay_metrics.get("optix_minus_embree_active_count", 0)
    )
    spatial_overlay_speedup = float(
        spatial_overlay_metrics.get("embree_over_optix_timed_median", 0.0)
    )
    spatial_prefilter_summary = spatial_prefilter_zero_experiment.get("summary", {})
    spatial_prefilter_stable_ms = float(
        spatial_prefilter_summary.get("stable_prefilter_prepared_query_ms", 0.0)
    )
    spatial_prefilter_speedup = float(
        spatial_prefilter_summary.get("stable_prefilter_speedup_vs_old_best", 0.0)
    )
    spatial_prefilter_author_speedup = float(
        spatial_prefilter_summary.get("author_speedup_vs_stable_prefilter", 0.0)
    )
    spatial_prefilter_gap_ms = float(
        spatial_prefilter_summary.get("still_missing_author_bar_by_ms", 0.0)
    )
    spatial_count_only_summary = spatial_count_only_no_diag_no_go.get("summary", {})
    spatial_count_only_delta_ms = float(spatial_count_only_summary.get("prepared_query_delta_ms", 0.0))
    spatial_count_only_ms = float(
        spatial_count_only_summary.get("count_only_prepared_query_ms_median", 0.0)
    )
    spatial_count_only_diagnostic_ms = float(
        spatial_count_only_summary.get("diagnostic_prepared_query_ms_median", 0.0)
    )
    spatial_squared_summary = spatial_squared_boundary_candidate.get("summary", {})
    spatial_squared_ms = float(spatial_squared_summary.get("squared_boundary_median_ms", 0.0))
    spatial_squared_default_ms = float(
        spatial_squared_summary.get("default_path_median_ms", spatial_squared_ms)
    )
    spatial_squared_default_author_speedup = float(
        spatial_squared_summary.get(
            "default_path_speedup_vs_author_query_timer",
            spatial_squared_summary.get("speedup_vs_author_query_timer", 0.0),
        )
    )
    spatial_squared_default_margin_ms = float(
        spatial_squared_summary.get(
            "default_path_author_bar_margin_ms",
            spatial_squared_summary.get("author_bar_margin_ms", 0.0),
        )
    )
    spatial_squared_speedup_vs_prefilter = float(
        spatial_squared_summary.get("speedup_vs_current_prefilter_zero", 0.0)
    )
    spatial_squared_speedup_vs_author = float(
        spatial_squared_summary.get("speedup_vs_author_query_timer", 0.0)
    )
    spatial_squared_margin_ms = float(spatial_squared_summary.get("author_bar_margin_ms", 0.0))
    spatial_squared_boundary_m7_approved = (
        spatial_squared_boundary_candidate.get("status")
        == "spatial_relation_status_squared_boundary_default_path_m7_row_accepted_with_boundary"
        and spatial_squared_boundary_candidate.get("m7_candidate") is True
        and spatial_squared_boundary_candidate.get("external_review_status")
        == "claude_accept_with_boundary_default_path"
        and spatial_squared_boundary_candidate.get("codex_consensus_status")
        == "claude_codex_consensus_accept_default_path_m7_row"
        and spatial_squared_boundary_candidate.get("p1_default_path_resolution_required") is False
        and spatial_squared_boundary_candidate.get("m7_promotion_authorized") is True
        and spatial_squared_boundary_candidate.get("m7_qualified_release_rows_added") == 1
        and spatial_squared_boundary_candidate.get("release_authorized") is False
        and spatial_squared_boundary_candidate.get("public_speedup_claim_authorized") is False
        and spatial_squared_boundary_candidate.get("row_scoped_public_speedup_claim_authorized") is False
        and spatial_squared_boundary_candidate.get("rtdl_beats_rayjoin_claim_authorized") is False
        and spatial_squared_boundary_candidate.get("failed_checks") == []
    )
    spatial_squared_boundary_accepted_with_boundary = (
        spatial_squared_boundary_candidate.get("status")
        == "spatial_relation_status_squared_boundary_accepted_with_boundary_p1_default_path_blocked"
        and spatial_squared_boundary_candidate.get("m7_candidate") is True
        and spatial_squared_boundary_candidate.get("external_review_status") == "claude_accept_with_boundary"
        and spatial_squared_boundary_candidate.get("codex_consensus_status")
        == "claude_codex_consensus_accept_with_boundary_not_release"
        and spatial_squared_boundary_candidate.get("p1_default_path_resolution_required") is True
        and spatial_squared_boundary_candidate.get("m7_promotion_authorized") is False
        and spatial_squared_boundary_candidate.get("m7_qualified_release_rows_added") == 0
        and spatial_squared_boundary_candidate.get("release_authorized") is False
        and spatial_squared_boundary_candidate.get("public_speedup_claim_authorized") is False
        and spatial_squared_boundary_candidate.get("row_scoped_public_speedup_claim_authorized") is False
        and spatial_squared_boundary_candidate.get("rtdl_beats_rayjoin_claim_authorized") is False
        and spatial_squared_boundary_candidate.get("failed_checks") == []
    )
    if spatial_active_p0_closed:
        queue = [item for item in queue if item["id"] != "spatial_rayjoin_topology_stream_author_gap"]
    if spatial_active_p0_closed and not spatial_squared_boundary_m7_approved:
        future_work.append(
            {
                "id": "spatial_rayjoin_topology_stream_author_gap",
                "priority": "future_research_not_current_p0",
                "apps_used_as_evidence": ["spatial_rayjoin"],
                "generic_capability": "point_location_topology_stream",
                "current_state": (
                    "Closed from current Phoenix V3 active P0 after Claude external review plus "
                    "Codex consensus. The exact-f64 device scalar-count repair is real RTDL-vs-RTDL "
                    "progress: prepared-query median improved from 23.217812ms to 6.309319ms "
                    "(3.680x) with exact public-county count 47,262. It is not an M7 row because "
                    "RayJoin author Query remains 1.865660ms, about 3.382x faster than RTDL on "
                    "the same dataset, and the author run did not print a result count. The "
                    "relation-status corrected route remains a no-go at 47,259 != 47,262."
                    f" A later relation-status zero-prefilter experiment is a real generic "
                    f"native optimization: the stable y_then_x public-county prepared-query "
                    f"median improves to {spatial_prefilter_stable_ms:.6f}ms, "
                    f"{spatial_prefilter_speedup:.3f}x faster than the old best legal RTDL "
                    "route, with exact count 47,262. It is still not an M7 row because "
                    f"RayJoin author Query remains {spatial_prefilter_author_speedup:.3f}x "
                    f"faster and the remaining gap is {spatial_prefilter_gap_ms:.6f}ms. "
                    "The boundary-helper fast path was rejected after changing the exact "
                    "count to 47,259."
                    " A count-only/no-diagnostics follow-up was also rejected: it preserved "
                    f"the exact count but was slower ({spatial_count_only_ms:.6f}ms vs "
                    f"{spatial_count_only_diagnostic_ms:.6f}ms, delta "
                    f"+{spatial_count_only_delta_ms:.6f}ms), so the experimental flag was "
                    "not retained in source."
                    " A later guarded squared-boundary exact-f64 candidate is now accepted "
                    "with Claude/Codex boundary rather than promoted: with both default-off relation-status "
                    "zero-prefilter and guarded squared-boundary flags enabled, the public-county "
                    f"repeat50/sample7 prepared-query median is {spatial_squared_ms:.6f}ms, "
                    f"{spatial_squared_speedup_vs_prefilter:.3f}x faster than the current "
                    "prefilter-zero route, exact count remains 47,262, and it clears the "
                    f"1.865660ms author Query timer by {spatial_squared_margin_ms:.6f}ms "
                    f"({spatial_squared_speedup_vs_author:.3f}x). It is still not M7 until "
                    "P1 default-path characterization makes the route real for users and a "
                    "fresh external review accepts user-facing promotion; the predicate-equivalence packet "
                    "records pure squared mismatch risk and guarded zero mismatch."
                    " A later full-scale overlay active-count reopen attempt on 15,700 x "
                    "7,774 shapes (122,051,800 shape-pairs) produced complete OptiX M3 "
                    f"metadata and a {spatial_overlay_speedup:.3f}x timed-median ratio, "
                    f"but is a no-go because OptiX {spatial_overlay_optix_count:,} != "
                    f"Embree {spatial_overlay_embree_count:,} "
                    f"(delta {spatial_overlay_count_delta:,}) and only repeat=1 "
                    "fail-closed exactness was recorded."
                ),
                "generic_engine_action": (
                    "Keep Spatial out of M7 until the guarded squared-boundary candidate resolves "
                    "P1 default-path or explicitly user-facing activation behavior and repeat POD "
                    "evidence is reviewed."
                ),
                "evidence_to_reopen_m7": (
                    "The guarded squared-boundary candidate now supplies the missing same-dataset RTDL "
                    "prepared-query median < 1.865660ms with stable exact count 47,262 and full "
                    "M3 phase table, and it has Claude/Codex accept-with-boundary consensus. It "
                    "still needs P1 default-path or explicitly user-facing activation evidence, "
                    "repeat POD under that user-facing route, public wording review, and fresh "
                    "external review before it can reopen M7."
                ),
                "active_candidate_packet": (
                    "docs/rebuild/v3/phoenix_v3_spatial_active_p0_closure_gate_2026-06-21.md"
                ),
                "active_candidate_status": "spatial_active_p0_closed_current_v3_future_research",
                "closed_by_external_review": (
                    "docs/reviews/claude_phoenix_v3_spatial_active_p0_closure_review_2026-06-21.md"
                ),
                "closed_by_consensus": (
                    "docs/reviews/codex_phoenix_v3_spatial_active_p0_closure_2ai_consensus_2026-06-21.md"
                ),
                "full_scale_overlay_active_count_no_go_packet": (
                    "docs/rebuild/v3/phoenix_v3_spatial_overlay_active_count_full_scale_no_go_2026-06-21.md"
                ),
                "full_scale_overlay_active_count_no_go_status": spatial_overlay_active_count_full_scale_no_go.get(
                    "status"
                ),
                "full_scale_overlay_active_count_no_go_review_request": (
                    "docs/reviews/call_for_review_phoenix_v3_spatial_overlay_active_count_full_scale_no_go_2026-06-21.md"
                ),
                "full_scale_overlay_active_count_shape_pair_count": spatial_overlay_pair_count,
                "full_scale_overlay_active_count_optix_count": spatial_overlay_optix_count,
                "full_scale_overlay_active_count_embree_count": spatial_overlay_embree_count,
                "full_scale_overlay_active_count_delta": spatial_overlay_count_delta,
                "full_scale_overlay_active_count_timed_median_ratio": spatial_overlay_speedup,
                "latest_prefilter_zero_packet": (
                    "docs/rebuild/v3/phoenix_v3_spatial_relation_status_prefilter_zero_experiment_2026-06-21.md"
                ),
                "latest_prefilter_zero_status": spatial_prefilter_zero_experiment.get("status"),
                "latest_prefilter_zero_prepared_query_ms": spatial_prefilter_stable_ms,
                "latest_prefilter_zero_speedup_vs_old_best": spatial_prefilter_speedup,
                "latest_prefilter_zero_author_speedup_vs_rtdl": spatial_prefilter_author_speedup,
                "latest_prefilter_zero_gap_to_author_ms": spatial_prefilter_gap_ms,
                "latest_count_only_no_diagnostics_no_go_packet": (
                    "docs/rebuild/v3/phoenix_v3_spatial_relation_status_count_only_no_diagnostics_no_go_2026-06-21.md"
                ),
                "latest_count_only_no_diagnostics_no_go_status": spatial_count_only_no_diag_no_go.get(
                    "status"
                ),
                "latest_count_only_no_diagnostics_prepared_query_ms": spatial_count_only_ms,
                "latest_count_only_no_diagnostics_delta_ms": spatial_count_only_delta_ms,
                "latest_count_only_no_diagnostics_source_retained": spatial_count_only_summary.get(
                    "count_only_source_retained"
                ),
                "latest_squared_boundary_candidate_packet": (
                    "docs/rebuild/v3/phoenix_v3_spatial_relation_status_squared_boundary_candidate_2026-06-21.md"
                ),
                "latest_squared_boundary_candidate_status": spatial_squared_boundary_candidate.get("status"),
                "latest_squared_boundary_prepared_query_ms": spatial_squared_ms,
                "latest_squared_boundary_speedup_vs_prefilter_zero": spatial_squared_speedup_vs_prefilter,
                "latest_squared_boundary_speedup_vs_author_query": spatial_squared_speedup_vs_author,
                "latest_squared_boundary_author_margin_ms": spatial_squared_margin_ms,
                "latest_squared_boundary_m7_candidate": spatial_squared_boundary_candidate.get("m7_candidate"),
                "latest_squared_boundary_m7_promotion_authorized": spatial_squared_boundary_candidate.get(
                    "m7_promotion_authorized"
                ),
                "latest_squared_boundary_guarded_mismatch_count": spatial_squared_boundary_candidate.get(
                    "predicate_equivalence", {}
                ).get("guarded_mismatch_count"),
                "latest_squared_boundary_pure_mismatch_count": spatial_squared_boundary_candidate.get(
                    "predicate_equivalence", {}
                ).get("pure_squared_mismatch_count"),
                "m7_rows_added": 0,
                "forbidden_shortcut": (
                    "Do not claim RTDL beats RayJoin, true zero-copy, RayJoin-paper reproduction, "
                    "whole Spatial RayJoin speedup, or broad V3-over-V2 speedup from this closure."
                ),
            }
        )
    aabb_native_query_handle_closed = (
        aabb_native_query_handle_review_gate.get("status")
        == "aabb_native_query_handle_two_rows_m7_qualified_row_scoped"
        and aabb_native_query_handle_review_gate.get("m7_promotion_authorized") is True
        and aabb_native_query_handle_review_gate.get("m7_qualified_release_rows_added") == 2
        and aabb_native_query_handle_review_gate.get("failed_checks") == []
    )
    if aabb_native_query_handle_closed:
        queue = [item for item in queue if item["id"] != "contact_aabb_prepare_reuse"]
        closed.append(
            {
                "id": "contact_aabb_prepare_reuse",
                "priority": "P0",
                "apps_used_as_evidence": ["contact_manifold", "librts_spatial_index"],
                "generic_capability": "aabb_candidate_stream",
                "closed_state": (
                    "The AABB native prepared-query-handle route now has Claude external "
                    "review plus Codex consensus. Exactly two jittered_grid repeat50 "
                    "range_intersection_rows rows are M7-qualified: 32,768 at 1.719x "
                    "and 65,536 at 1.637x cold-plus-collect OptiX/Embree wall speedup. "
                    "The closure records raw AABB oracle parity, fail-closed overflow, "
                    "source-manifest provenance, six fresh stability runs, and the required "
                    "slower-OptiX-prepare disclosure."
                ),
                "closed_by_packet": (
                    "docs/rebuild/v3/phoenix_v3_aabb_native_query_handle_review_gate_2026-06-21.md"
                ),
                "closed_by_consensus": (
                    "docs/reviews/codex_phoenix_v3_aabb_native_query_handle_final_m7_review_2ai_consensus_2026-06-21.md"
                ),
                "m7_rows_added": 2,
                "forbidden_shortcut": (
                    "Do not promote Contact Manifold solving, broad AABB-index acceleration, "
                    "OptiX prepare-phase speedup, or broad V3-over-V2 claims from this closure."
                ),
            }
        )
    rtnn_prepared_repeat50_closed = (
        rtnn_prepared_repeat50_review_gate.get("status")
        == "rtnn_prepared_repeat50_m7_qualified_row_scoped"
        and rtnn_prepared_repeat50_review_gate.get("m7_promotion_authorized") is True
        and rtnn_prepared_repeat50_review_gate.get("m7_qualified_release_rows_added") == 1
        and rtnn_prepared_repeat50_review_gate.get("failed_checks") == []
    )
    if rtnn_prepared_repeat50_closed:
        queue = [item for item in queue if item["id"] != "rtnn_ranked_summary_wall_path"]
        closed.append(
            {
                "id": "rtnn_ranked_summary_wall_path",
                "priority": "P0",
                "apps_used_as_evidence": ["rtnn"],
                "generic_capability": "ranked_summary",
                "closed_state": (
                    "The RTNN prepared repeat50 NPZ+CUBIN route now has Claude external "
                    "review plus Codex consensus. Exactly one 1,048,576-point row is "
                    "M7-qualified for prepared-session amortization only: 7.889x hot-query, "
                    "1.315x cold-plus-query, and 3.761x runner-wall speedup over a CuPy "
                    "uniform-grid CUDA-core reference across 50 prepared repeated queries "
                    "on the same search structure. The closure records float32 OptiX versus "
                    "float64-coordinate CuPy grid disclosure, source_manifest.sha256 provenance, "
                    "and no one-shot/cold-start/whole-RTNN wording."
                ),
                "closed_by_packet": (
                    "docs/rebuild/v3/phoenix_v3_rtnn_prepared_repeat50_review_gate_2026-06-21.md"
                ),
                "closed_by_consensus": (
                    "docs/reviews/codex_phoenix_v3_rtnn_prepared_repeat50_amortization_2ai_consensus_2026-06-21.md"
                ),
                "m7_rows_added": 1,
                "forbidden_shortcut": (
                    "Do not promote whole RTNN, one-shot nearest-neighbor, cold-start, paper-equivalent, "
                    "general nearest-neighbor baseline, broad V3-over-V2, or release wording from this closure."
                ),
            }
        )
    pending_external_review_candidates: list[dict[str, Any]] = []
    accepted_with_boundary_candidates: list[dict[str, Any]] = []
    barnes_hut_fused_partner_m7_packet = next(
        (
            packet
            for packet in m7_packet.get("post_classification_final_review_packets", [])
            if packet.get("candidate_row_id")
            == "aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped"
        ),
        {},
    )
    barnes_hut_fused_partner_approved = (
        barnes_hut_fused_partner_m7_packet.get("status")
        == "aggregate_tree_fused_partner_m7_qualified_row_scoped_after_claude_amendments"
        and barnes_hut_fused_partner_m7_packet.get("classification_m7_contribution") == 1
        and barnes_hut_fused_partner_m7_packet.get("m7_qualified_release_rows") == 1
        and barnes_hut_fused_partner_m7_packet.get("current_packet_external_review_status")
        == "claude_approve_with_amendments"
        and barnes_hut_fused_partner_m7_packet.get("current_packet_2ai_consensus_status")
        == "claude_codex_consensus_complete_approve_one_row_scoped_m7_with_amendments"
        and barnes_hut_fused_partner_m7_packet.get("release_authorized") is False
        and barnes_hut_fused_partner_m7_packet.get("public_speedup_claim_authorized") is False
        and barnes_hut_fused_partner_m7_packet.get("rt_core_speedup_claim_authorized") is False
        and BARNES_HUT_FUSED_PARTNER_CLAUDE_REVIEW.exists()
        and BARNES_HUT_FUSED_PARTNER_CODEX_CONSENSUS.exists()
    )
    barnes_hut_fused_partner_pending = (
        barnes_hut_same_basis_no_go.get("status")
        == "barnes_hut_same_basis_no_go_current_frontier_shape_not_m7"
        and barnes_hut_fused_partner_candidate.get("status")
        == "aggregate_tree_fused_partner_m7_candidate_pending_external_review"
        and barnes_hut_fused_partner_candidate.get("local_evidence_sufficient_for_external_public_row_review")
        is True
        and barnes_hut_fused_partner_candidate.get("m7_promotion_authorized") is False
        and barnes_hut_fused_partner_candidate.get("m7_qualified_release_rows_added") == 0
        and barnes_hut_fused_partner_candidate.get("candidate_m7_contribution_if_external_review_approves") == 1
        and not barnes_hut_fused_partner_approved
    )
    if barnes_hut_fused_partner_approved:
        closed.append(
            {
                "id": "barnes_hut_fused_partner_vector_accumulation",
                "priority": "P0",
                "apps_used_as_evidence": ["barnes_hut"],
                "generic_capability": "aggregate_frontier",
                "refined_generic_capability": "vector_accumulation",
                "closed_state": (
                    "The generic aggregate-tree fused weighted-vector Numba CUDA partner route now has "
                    "Claude approve-with-amendments plus Codex consensus. Exactly one 131,072-body "
                    "row is M7-qualified for the amended partner contract: 45.493 ms wall-repeat "
                    "median (r=11, warmup=3), 4.082x faster than CPU/Numba fused baseline on a "
                    "Barnes-Hut tree evidence basis. The 13.591x comparison against the current "
                    "prepared RTDL/OptiX frontier-emission route is supporting metadata only because "
                    "that OptiX route is no-go."
                ),
                "closed_by_packet": (
                    "docs/rebuild/v3/phoenix_v3_barnes_hut_fused_partner_m7_candidate_2026-06-21.md"
                ),
                "closed_by_external_review": (
                    "docs/reviews/claude_phoenix_v3_barnes_hut_fused_partner_m7_candidate_review_2026-06-21.md"
                ),
                "closed_by_consensus": (
                    "docs/reviews/codex_phoenix_v3_barnes_hut_fused_partner_m7_candidate_2ai_consensus_2026-06-21.md"
                ),
                "m7_rows_added": 1,
                "candidate_row_id": barnes_hut_fused_partner_m7_packet["candidate_row_id"],
                "evidence_tree_structure": barnes_hut_fused_partner_m7_packet["evidence_tree_structure"],
                "large_scale_validation_tier": barnes_hut_fused_partner_m7_packet[
                    "large_scale_validation_tier"
                ],
                "forbidden_shortcut": (
                    "Do not call this RT-core acceleration, whole Barnes-Hut, paper reproduction, "
                    "automatic backend selection, broad V3-over-V2 speedup, release authorization, "
                    "or use the 13.591x OptiX no-go comparison as the primary claim."
                ),
            }
        )
    if barnes_hut_fused_partner_pending:
        pending_external_review_candidates.append(
            {
                "id": "barnes_hut_fused_partner_m7_candidate",
                "generic_capability": "aggregate_frontier",
                "refined_generic_capability": "vector_accumulation",
                "candidate_row_id": barnes_hut_fused_partner_candidate["candidate_row_id"],
                "candidate_status": barnes_hut_fused_partner_candidate["status"],
                "candidate_packet": (
                    "docs/rebuild/v3/phoenix_v3_barnes_hut_fused_partner_m7_candidate_2026-06-21.md"
                ),
                "same_basis_no_go_packet": (
                    "docs/rebuild/v3/phoenix_v3_barnes_hut_same_basis_wall_time_no_go_2026-06-21.md"
                ),
                "review_request": (
                    "docs/reviews/call_for_review_phoenix_v3_barnes_hut_fused_partner_m7_candidate_2026-06-21.md"
                ),
                "claude_blocked_record": (
                    "docs/reviews/claude_blocked_phoenix_v3_barnes_hut_fused_partner_m7_candidate_2026-06-21.md"
                ),
                "claude_retry_blocked_record": (
                    "docs/reviews/claude_blocked_retry_phoenix_v3_barnes_hut_fused_partner_m7_candidate_2026-06-21.md"
                ),
                "candidate_m7_contribution_if_external_review_approves": 1,
                "m7_rows_added_now": 0,
                "release_authorized": False,
                "public_speedup_claim_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "next_action": (
                    "Retry Claude after the local session reset and ask whether exactly one "
                    "row-scoped generic fused partner row may close the aggregate_frontier breadth gap."
                ),
                "forbidden_shortcut": (
                    "Do not call this RT-core acceleration, whole Barnes-Hut, paper reproduction, "
                    "automatic backend selection, broad V3-over-V2 speedup, or release authorization."
                ),
            }
        )
    if spatial_squared_boundary_m7_approved:
        closed.append(
            {
                "id": "spatial_squared_boundary_default_path_topology_stream",
                "priority": "P0",
                "apps_used_as_evidence": ["spatial_rayjoin"],
                "generic_capability": "point_location_topology_stream",
                "refined_generic_capability": "exact_f64_guarded_boundary_predicate",
                "closed_state": (
                    "The generic point-location topology stream now has a default-enabled "
                    "relation-status zero prefilter plus guarded squared-boundary exact-f64 "
                    "predicate, validated on POD with no enabling env flags. The public county "
                    "repeat50/sample7 default-path median is 1.080599 ms with exact count 47,262. "
                    "Claude accepted the default-path promotion with boundary and Codex consensus "
                    "counts exactly one bounded M7 release-surface row."
                ),
                "closed_by_packet": (
                    "docs/rebuild/v3/phoenix_v3_spatial_relation_status_squared_boundary_candidate_2026-06-21.md"
                ),
                "closed_by_external_review": (
                    "docs/reviews/claude_phoenix_v3_spatial_default_path_promotion_review_2026-06-22.md"
                ),
                "closed_by_consensus": (
                    "docs/reviews/codex_phoenix_v3_spatial_default_path_promotion_2ai_consensus_2026-06-22.md"
                ),
                "m7_rows_added": 1,
                "candidate_row_id": spatial_squared_boundary_candidate["candidate_row_id"],
                "default_path_median_ms": spatial_squared_summary.get("default_path_median_ms"),
                "exact_row_count": spatial_squared_summary.get("row_count"),
                "forbidden_shortcut": (
                    "Do not claim RTDL beats RayJoin, whole Spatial RayJoin, paper reproduction, "
                    "true zero-copy, V4 embedding, release readiness, public speedup, or broad "
                    "V3-over-V2 speedup. The author Query timer is an internal bar only."
                ),
            }
        )
    if spatial_squared_boundary_accepted_with_boundary:
        accepted_with_boundary_candidates.append(
            {
                "id": "spatial_squared_boundary_m7_candidate",
                "generic_capability": "point_location_topology_stream",
                "refined_generic_capability": "exact_f64_guarded_boundary_predicate",
                "candidate_row_id": spatial_squared_boundary_candidate["candidate_row_id"],
                "candidate_status": spatial_squared_boundary_candidate["status"],
                "candidate_packet": (
                    "docs/rebuild/v3/phoenix_v3_spatial_relation_status_squared_boundary_candidate_2026-06-21.md"
                ),
                "same_basis_no_go_packet": (
                    "docs/rebuild/v3/phoenix_v3_spatial_relation_status_prefilter_zero_experiment_2026-06-21.md"
                ),
                "review_request": (
                    "docs/reviews/call_for_review_phoenix_v3_spatial_squared_boundary_candidate_2026-06-21.md"
                ),
                "external_review": (
                    "docs/reviews/claude_phoenix_v3_spatial_squared_boundary_candidate_review_2026-06-21.md"
                ),
                "codex_consensus": (
                    "docs/reviews/codex_phoenix_v3_spatial_squared_boundary_candidate_2ai_consensus_2026-06-22.md"
                ),
                "historical_blocked_record": (
                    "docs/reviews/external_ai_blocked_phoenix_v3_spatial_squared_boundary_candidate_2026-06-21.md"
                ),
                "candidate_m7_contribution_if_p1_default_path_review_approves": 1,
                "m7_rows_added_now": 0,
                "release_authorized": False,
                "public_speedup_claim_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "next_action": (
                    "Resolve P1 default-path behavior, rerun POD evidence under the default path or "
                    "reviewed user-facing activation contract, then request external review before "
                    "any point_location_topology_stream M7 release-surface promotion."
                ),
                "forbidden_shortcut": (
                    "Do not claim RTDL beats RayJoin, whole Spatial RayJoin, paper reproduction, "
                    "true zero-copy, V4 embedding, release readiness, or broad V3-over-V2 speedup."
                ),
            }
        )

    spatial_supplemental_m7_rows = 1 if spatial_squared_boundary_m7_approved else 0
    current_m7_rows = (
        int(m7_packet.get("phoenix_m7_qualified_release_rows", 0)) + spatial_supplemental_m7_rows
    )

    checks = {
        "route_map_status_not_release": route_map.get("status") == "active_planning_not_release",
        "m7_packet_status_not_release": m7_packet.get("status") == "m7_classification_packet_not_release",
        "m7_packet_base_rows_still_twelve": m7_packet.get("phoenix_m7_qualified_release_rows") == 12,
        "current_m7_rows_is_thirteen_after_spatial_default_path": current_m7_rows == 13,
        "rtnn_reconciliation_exists": RTNN_RECONCILIATION.exists(),
        "rtnn_reconciliation_no_m7_promotion": (
            rtnn_reconciliation.get("status") == "rtnn_m112_reconciled_no_m7_promotion"
            and rtnn_reconciliation.get("m7_qualified_release_rows") == 0
            and rtnn_reconciliation.get("existing_evidence_promotable_now") is False
        ),
        "rtnn_full_batch_float32_runner_exists": RTNN_FULL_BATCH_FLOAT32_RUNNER.exists(),
        "rtnn_full_batch_float32_evidence_exists": RTNN_FULL_BATCH_FLOAT32_EVIDENCE.exists(),
        "rtnn_full_batch_float32_evidence_hot_candidate_not_m7": (
            rtnn_full_batch_evidence.get("status")
            == "rtnn_full_batch_float32_hot_query_candidate_pending_2ai_wall_blocked_not_m7"
            and rtnn_full_batch_evidence.get("m7_qualified_release_rows_added") == 0
            and rtnn_full_batch_evidence.get("m7_promotion_authorized") is False
            and rtnn_full_batch_evidence.get("m7_reopen_candidate_pending_2ai_review") is True
            and rtnn_full_batch_evidence.get("main_row", {}).get(
                "hot_speedup_optix_over_cupy_grid", 0.0
            )
            >= 2.0
            and rtnn_full_batch_evidence.get("main_row", {}).get(
                "runner_wall_speedup_optix_over_cupy_grid", 1.0
            )
            < 1.0
        ),
        "rtnn_full_batch_float32_review_gate_exists": RTNN_FULL_BATCH_FLOAT32_REVIEW_GATE.exists(),
        "rtnn_full_batch_float32_review_gate_blocks_m7": (
            rtnn_full_batch_review_gate.get("status") == "rtnn_full_batch_float32_review_blocked_not_m7"
            and rtnn_full_batch_review_gate.get("failed_checks") == []
            and rtnn_full_batch_review_gate.get("external_review_status") == "blocked_no_external_ai_verdict"
            and rtnn_full_batch_review_gate.get("m7_candidate_reopen_authorized") is False
            and rtnn_full_batch_review_gate.get("m7_promotion_authorized") is False
            and rtnn_full_batch_review_gate.get("release_authorized") is False
            and rtnn_full_batch_review_gate.get("whole_app_speedup_claim_authorized") is False
            and {
                "external_ai_review_missing",
                "cold_plus_query_wall_regresses",
                "runner_wall_regresses",
                "prepared_hot_query_scope_not_reviewed",
                "pack_prepare_amortization_not_solved",
            }.issubset(set(rtnn_full_batch_review_gate.get("required_blockers_before_m7", [])))
        ),
        "rtnn_cubin_cache_evidence_exists": RTNN_CUBIN_CACHE_EVIDENCE.exists(),
        "rtnn_cubin_cache_evidence_not_m7": (
            rtnn_cubin_cache_evidence.get("status")
            == "rtnn_optix_cubin_cache_reduces_prepare_not_m7_wall_floor_not_met"
            and rtnn_cubin_cache_evidence.get("failed_checks") == []
            and rtnn_cubin_cache_evidence.get("m7_qualified_release_rows_added") == 0
            and rtnn_cubin_cache_evidence.get("m7_reopen_candidate_pending_2ai_review") is False
            and rtnn_cubin_cache_evidence.get("m7_promotion_authorized") is False
            and rtnn_cubin_cache_evidence.get("release_authorized") is False
            and rtnn_cubin_cache_evidence.get("public_speedup_claim_authorized") is False
            and rtnn_cubin_cache_evidence.get("broad_v3_faster_than_v2_claim_authorized") is False
            and rtnn_cubin_cache_evidence.get("cache_controls", {}).get("cache_dir_env")
            == "RTDL_OPTIX_CUBIN_CACHE_DIR"
            and rtnn_cubin_cache_evidence.get("cache_controls", {}).get("disable_env")
            == "RTDL_OPTIX_DISABLE_CUBIN_CACHE"
            and rtnn_cubin_cache_evidence.get("improvement_vs_cold_optix", {}).get(
                "execution_prepare_reduction", 0.0
            )
            >= 2.0
            and rtnn_cubin_cache_evidence.get("warm_comparison_vs_cupy_grid", {}).get(
                "rtdl_optix_over_cupy_grid_cold_plus_query_speedup", 99.0
            )
            < 1.0
            and rtnn_cubin_cache_evidence.get("warm_comparison_vs_cupy_grid", {}).get(
                "rtdl_optix_over_cupy_grid_runner_wall_speedup", 99.0
            )
            < 2.0
        ),
        "rtnn_self_query_evidence_exists": RTNN_SELF_QUERY_EVIDENCE.exists(),
        "rtnn_self_query_evidence_not_m7": (
            rtnn_self_query_evidence.get("status")
            == "rtnn_prepared_self_query_hot_path_material_not_m7_wall_floor_not_met"
            and rtnn_self_query_evidence.get("failed_checks") == []
            and rtnn_self_query_evidence.get("m7_qualified_release_rows_added") == 0
            and rtnn_self_query_evidence.get("m7_reopen_candidate_pending_2ai_review") is False
            and rtnn_self_query_evidence.get("m7_promotion_authorized") is False
            and rtnn_self_query_evidence.get("release_authorized") is False
            and rtnn_self_query_evidence.get("public_speedup_claim_authorized") is False
            and rtnn_self_query_evidence.get("broad_v3_faster_than_v2_claim_authorized") is False
            and rtnn_self_query_evidence.get("review_records", {}).get("external_review_status")
            == "blocked_no_external_ai_verdict"
            and rtnn_self_query_evidence.get("review_records", {}).get("two_ai_consensus_exists")
            is False
            and rtnn_self_query_evidence.get("comparisons", {}).get(
                "old_prepared_query_to_new_self_query_hot_speedup", 0.0
            )
            >= 2.0
            and rtnn_self_query_evidence.get("comparisons", {}).get(
                "input_pack_reduction_old_to_new", 0.0
            )
            >= 2.0
            and rtnn_self_query_evidence.get("comparisons", {}).get(
                "new_self_query_over_cupy_hot_speedup", 0.0
            )
            >= 2.0
            and rtnn_self_query_evidence.get("comparisons", {}).get(
                "new_self_query_over_cupy_cold_plus_query_speedup", 99.0
            )
            < 2.0
            and rtnn_self_query_evidence.get("comparisons", {}).get(
                "new_self_query_over_cupy_runner_wall_speedup", 99.0
            )
            < 2.0
        ),
        "rtnn_lazy_exact_prepare_evidence_exists": RTNN_LAZY_EXACT_PREPARE_EVIDENCE.exists(),
        "rtnn_lazy_exact_prepare_evidence_not_m7": (
            rtnn_lazy_exact_prepare_evidence.get("status")
            == "rtnn_lazy_exact_prepare_reduces_prepare_not_m7_wall_floor_not_met"
            and rtnn_lazy_exact_prepare_evidence.get("failed_checks") == []
            and rtnn_lazy_exact_prepare_evidence.get("m7_qualified_release_rows_added") == 0
            and rtnn_lazy_exact_prepare_evidence.get("m7_reopen_candidate_pending_2ai_review") is False
            and rtnn_lazy_exact_prepare_evidence.get("m7_promotion_authorized") is False
            and rtnn_lazy_exact_prepare_evidence.get("release_authorized") is False
            and rtnn_lazy_exact_prepare_evidence.get("public_speedup_claim_authorized") is False
            and rtnn_lazy_exact_prepare_evidence.get("broad_v3_faster_than_v2_claim_authorized") is False
            and rtnn_lazy_exact_prepare_evidence.get("comparisons", {}).get(
                "self_query_prepare_reduction_prepatch_to_lazy", 0.0
            )
            > 1.0
            and rtnn_lazy_exact_prepare_evidence.get("comparisons", {}).get(
                "self_query_cold_plus_query_reduction_prepatch_to_lazy", 0.0
            )
            > 1.0
            and rtnn_lazy_exact_prepare_evidence.get("comparisons", {}).get(
                "lazy_self_query_over_cupy_cold_plus_query_speedup", 99.0
            )
            < 2.0
            and rtnn_lazy_exact_prepare_evidence.get("comparisons", {}).get(
                "lazy_self_query_over_cupy_runner_wall_speedup", 99.0
            )
            < 2.0
        ),
        "rtnn_self_query_graph_evidence_exists": RTNN_SELF_QUERY_GRAPH_EVIDENCE.exists(),
        "rtnn_self_query_graph_evidence_not_m7": (
            rtnn_self_query_graph_evidence.get("status")
            == "rtnn_self_query_graph_large_scale_functional_not_m7_material_floor_not_met"
            and rtnn_self_query_graph_evidence.get("failed_checks") == []
            and rtnn_self_query_graph_evidence.get("m7_qualified_release_rows_added") == 0
            and rtnn_self_query_graph_evidence.get("m7_promotion_authorized") is False
            and rtnn_self_query_graph_evidence.get("release_authorized") is False
            and rtnn_self_query_graph_evidence.get("public_speedup_claim_authorized") is False
            and rtnn_self_query_graph_evidence.get("broad_v3_faster_than_v2_claim_authorized") is False
            and rtnn_self_query_graph_evidence.get("checks", {}).get("point_count_is_serious_1m")
            is True
            and rtnn_self_query_graph_evidence.get("checks", {}).get(
                "same_contract_summary_parity"
            )
            is True
            and rtnn_self_query_graph_evidence.get("checks", {}).get(
                "graph_uses_prepared_search_as_query_points"
            )
            is True
            and rtnn_self_query_graph_evidence.get("checks", {}).get(
                "native_65536_graph_cap_removed"
            )
            is True
            and rtnn_self_query_graph_evidence.get("comparisons", {}).get(
                "graph_over_direct_cold_plus_query_speedup", 99.0
            )
            < 2.0
        ),
        "rtnn_column_source_residency_gap_exists": RTNN_COLUMN_SOURCE_RESIDENCY_GAP.exists(),
        "rtnn_column_source_residency_gap_not_m7": (
            rtnn_column_source_residency_gap.get("status")
            == "rtnn_npz_column_source_ready_for_pod_rerun_not_m7"
            and rtnn_column_source_residency_gap.get("failed_checks") == []
            and rtnn_column_source_residency_gap.get("m7_qualified_release_rows_added") == 0
            and rtnn_column_source_residency_gap.get("m7_promotion_authorized") is False
            and rtnn_column_source_residency_gap.get("release_authorized") is False
            and rtnn_column_source_residency_gap.get("public_speedup_claim_authorized") is False
            and rtnn_column_source_residency_gap.get("broad_v3_faster_than_v2_claim_authorized")
            is False
            and rtnn_column_source_residency_gap.get("implemented_v3_surface", {}).get(
                "default_point_column_source"
            )
            == "npz"
            and rtnn_column_source_residency_gap.get("implemented_v3_surface", {}).get(
                "v4_c_abi_or_embedding"
            )
            is False
            and rtnn_column_source_residency_gap.get("implemented_v3_surface", {}).get(
                "app_specific_native_engine"
            )
            is False
            and rtnn_column_source_residency_gap.get("comparisons", {}).get(
                "new_self_query_over_cupy_runner_wall_speedup", 99.0
            )
            < 2.0
            and rtnn_column_source_residency_gap.get("measurements", {})
            .get("new_prepared_self_query", {})
            .get("input_load_share_of_runner_wall", 0.0)
            > 0.50
        ),
        "rtnn_npz_cubin_cache_evidence_exists": RTNN_NPZ_CUBIN_CACHE_EVIDENCE.exists(),
        "rtnn_npz_cubin_cache_evidence_not_m7": (
            rtnn_npz_cubin_cache_evidence.get("status")
            == "rtnn_npz_cubin_cache_wall_improves_not_m7_material_floor_not_met"
            and rtnn_npz_cubin_cache_evidence.get("failed_checks") == []
            and rtnn_npz_cubin_cache_evidence.get("m7_qualified_release_rows_added") == 0
            and rtnn_npz_cubin_cache_evidence.get("m7_promotion_authorized") is False
            and rtnn_npz_cubin_cache_evidence.get("release_authorized") is False
            and rtnn_npz_cubin_cache_evidence.get("public_speedup_claim_authorized") is False
            and rtnn_npz_cubin_cache_evidence.get("broad_v3_faster_than_v2_claim_authorized")
            is False
            and rtnn_npz_cubin_cache_evidence.get("checks", {}).get(
                "npz_source_recorded_on_both_routes"
            )
            is True
            and rtnn_npz_cubin_cache_evidence.get("checks", {}).get(
                "same_contract_signature_match"
            )
            is True
            and rtnn_npz_cubin_cache_evidence.get("checks", {}).get(
                "cache_reduces_runner_wall_at_least_2x"
            )
            is True
            and rtnn_npz_cubin_cache_evidence.get("warm_comparison_vs_cupy_grid", {}).get(
                "runner_wall_speedup", 0.0
            )
            > 1.0
            and rtnn_npz_cubin_cache_evidence.get("warm_comparison_vs_cupy_grid", {}).get(
                "runner_wall_speedup", 99.0
            )
            < rtnn_npz_cubin_cache_evidence.get("material_speedup_floor", 0.0)
            and rtnn_npz_cubin_cache_evidence.get("warm_comparison_vs_cupy_grid", {}).get(
                "cold_plus_query_speedup", 99.0
            )
            < rtnn_npz_cubin_cache_evidence.get("material_speedup_floor", 0.0)
        ),
        "rtnn_prepared_repeat50_amortization_exists": RTNN_PREPARED_REPEAT50_AMORTIZATION_EVIDENCE.exists(),
        "rtnn_prepared_repeat50_amortization_pending_review_not_m7": (
            rtnn_prepared_repeat50_amortization.get("status")
            == "rtnn_prepared_repeat50_amortization_m7_candidate_pending_external_review_not_release"
            and rtnn_prepared_repeat50_amortization.get("failed_checks") == []
            and rtnn_prepared_repeat50_amortization.get("m7_reopen_candidate_pending_2ai_review")
            is True
            and rtnn_prepared_repeat50_amortization.get("m7_qualified_release_rows_added") == 0
            and rtnn_prepared_repeat50_amortization.get("m7_promotion_authorized") is False
            and rtnn_prepared_repeat50_amortization.get("release_authorized") is False
            and rtnn_prepared_repeat50_amortization.get("public_speedup_claim_authorized") is False
            and rtnn_prepared_repeat50_amortization.get(
                "broad_v3_faster_than_v2_claim_authorized"
            )
            is False
            and rtnn_prepared_repeat50_amortization.get("parameters", {}).get("repeat") == 50
            and rtnn_prepared_repeat50_amortization.get("parameters", {}).get("point_count")
            >= 1_048_576
            and rtnn_prepared_repeat50_amortization.get("checks", {}).get(
                "same_contract_signature_match"
            )
            is True
            and rtnn_prepared_repeat50_amortization.get("comparisons", {}).get(
                "runner_wall_speedup", 0.0
            )
            >= rtnn_prepared_repeat50_amortization.get("material_speedup_floor", 99.0)
            and rtnn_prepared_repeat50_amortization.get("comparisons", {}).get(
                "cold_plus_query_speedup", 99.0
            )
            < rtnn_prepared_repeat50_amortization.get("material_speedup_floor", 0.0)
        ),
        "rtnn_prepared_repeat50_review_request_exists": RTNN_PREPARED_REPEAT50_REVIEW_REQUEST.exists(),
        "rtnn_prepared_repeat50_review_blocked_record_exists": RTNN_PREPARED_REPEAT50_REVIEW_BLOCKED.exists(),
        "rtnn_prepared_repeat50_review_gate_exists": RTNN_PREPARED_REPEAT50_REVIEW_GATE.exists(),
        "rtnn_prepared_repeat50_review_gate_m7_qualified_one_row": (
            rtnn_prepared_repeat50_review_gate.get("status")
            == "rtnn_prepared_repeat50_m7_qualified_row_scoped"
            and rtnn_prepared_repeat50_review_gate.get("failed_checks") == []
            and rtnn_prepared_repeat50_review_gate.get("external_review_status")
            == "claude_approve_with_conditions"
            and rtnn_prepared_repeat50_review_gate.get("current_packet_2ai_consensus_status")
            == "claude_codex_consensus_complete_approve_one_row_scoped_m7"
            and rtnn_prepared_repeat50_review_gate.get("m7_promotion_authorized") is True
            and rtnn_prepared_repeat50_review_gate.get("m7_qualified_release_rows_added") == 1
            and rtnn_prepared_repeat50_review_gate.get("release_authorized") is False
            and rtnn_prepared_repeat50_review_gate.get("public_speedup_claim_authorized") is False
            and rtnn_prepared_repeat50_review_gate.get("broad_v3_faster_than_v2_claim_authorized")
            is False
            and rtnn_prepared_repeat50_review_gate.get("whole_rtnn_claim_authorized") is False
            and rtnn_prepared_repeat50_review_gate.get("one_shot_rtnn_claim_authorized") is False
            and rtnn_prepared_repeat50_review_gate.get("candidate_row", {}).get("runner_wall_speedup", 0.0)
            >= rtnn_prepared_repeat50_review_gate.get("material_speedup_floor", 99.0)
            and rtnn_prepared_repeat50_review_gate.get("candidate_row", {}).get("cold_plus_query_speedup", 99.0)
            < rtnn_prepared_repeat50_review_gate.get("material_speedup_floor", 0.0)
            and "CuPy uniform-grid CUDA-core"
            in rtnn_prepared_repeat50_review_gate.get("candidate_row", {}).get(
                "approved_row_scoped_public_wording", ""
            )
            and "across 50 prepared repeated queries on the same search structure"
            in rtnn_prepared_repeat50_review_gate.get("candidate_row", {}).get(
                "approved_row_scoped_public_wording", ""
            )
        ),
        "aabb_prepare_reuse_contract_exists": AABB_PREPARE_REUSE.exists(),
        "aabb_prepare_reuse_contract_not_m7": (
            aabb_prepare_reuse.get("status") == "aabb_prepare_reuse_contract_candidate_not_m7"
            and aabb_prepare_reuse.get("m7_qualified_release_rows_added") == 0
            and aabb_prepare_reuse.get("m7_promotion_authorized") is False
        ),
        "aabb_prepare_reuse_pod_runner_exists": AABB_PREPARE_REUSE_RUNNER.exists(),
        "aabb_prepare_reuse_serious_evidence_exists": AABB_PREPARE_REUSE_SERIOUS_EVIDENCE.exists(),
        "aabb_prepare_reuse_serious_evidence_not_m7": (
            aabb_prepare_reuse_serious.get("status")
            == "aabb_prepare_reuse_serious_rtx_evidence_not_m7_low_margin"
            and aabb_prepare_reuse_serious.get("m7_qualified_release_rows_added") == 0
            and aabb_prepare_reuse_serious.get("m7_promotion_authorized") is False
            and aabb_prepare_reuse_serious.get("m7_reopen_candidate_pending_2ai_review") is False
            and aabb_prepare_reuse_serious.get("comparisons", {}).get(
                "optix_over_embree_cold_plus_collect_wall_speedup"
            )
            < aabb_prepare_reuse_serious.get("comparisons", {}).get("material_wall_speedup_floor")
        ),
        "aabb_prepare_reuse_scale_evidence_exists": AABB_PREPARE_REUSE_SCALE_EVIDENCE.exists(),
        "aabb_prepare_reuse_scale_evidence_not_m7": (
            aabb_prepare_reuse_scale.get("status")
            == "aabb_prepare_reuse_scale_evidence_not_m7_scale_does_not_clear_floor"
            and aabb_prepare_reuse_scale.get("m7_qualified_release_rows_added") == 0
            and aabb_prepare_reuse_scale.get("m7_promotion_authorized") is False
            and aabb_prepare_reuse_scale.get("m7_reopen_candidate_pending_2ai_review") is False
            and aabb_prepare_reuse_scale.get("checks", {}).get("all_below_material_floor") is True
            and aabb_prepare_reuse_scale.get("checks", {}).get("larger_scale_not_better") is True
        ),
        "aabb_prepare_reuse_overhead_gate_exists": AABB_PREPARE_REUSE_OVERHEAD_GATE.exists(),
        "aabb_prepare_reuse_overhead_gate_blocks_m7": (
            aabb_prepare_reuse_overhead_gate.get("status")
            == "aabb_prepare_reuse_overhead_gate_blocked_not_m7"
            and aabb_prepare_reuse_overhead_gate.get("failed_checks") == []
            and aabb_prepare_reuse_overhead_gate.get("m7_candidate_reopen_authorized") is False
            and aabb_prepare_reuse_overhead_gate.get("m7_promotion_authorized") is False
            and aabb_prepare_reuse_overhead_gate.get("release_authorized") is False
            and aabb_prepare_reuse_overhead_gate.get("public_speedup_claim_authorized") is False
            and aabb_prepare_reuse_overhead_gate.get("blocker_summary", {}).get(
                "best_cold_plus_collect_wall_speedup", 99.0
            )
            < aabb_prepare_reuse_overhead_gate.get("material_wall_speedup_floor", 0.0)
            and {
                "optix_prepare_slower_than_embree",
                "material_wall_floor_not_met",
                "larger_scale_not_better",
                "query_only_claim_forbidden",
                "generic_overhead_reduction_required",
            }.issubset(set(aabb_prepare_reuse_overhead_gate.get("required_blockers_before_m7", [])))
        ),
        "aabb_prepare_reuse_query_cache_evidence_exists": AABB_PREPARE_REUSE_QUERY_CACHE_EVIDENCE.exists(),
        "aabb_prepare_reuse_query_cache_evidence_not_m7": (
            aabb_prepare_reuse_query_cache.get("status")
            == "aabb_prepare_reuse_query_cache_evidence_not_m7_wall_floor_not_met"
            and aabb_prepare_reuse_query_cache.get("failed_checks") == []
            and aabb_prepare_reuse_query_cache.get("m7_qualified_release_rows_added") == 0
            and aabb_prepare_reuse_query_cache.get("m7_candidate_reopen_authorized") is False
            and aabb_prepare_reuse_query_cache.get("m7_promotion_authorized") is False
            and aabb_prepare_reuse_query_cache.get("release_authorized") is False
            and aabb_prepare_reuse_query_cache.get("public_speedup_claim_authorized") is False
            and aabb_prepare_reuse_query_cache.get("checks", {}).get("all_cache_stats_observed") is True
            and aabb_prepare_reuse_query_cache.get("checks", {}).get("all_wall_below_material_floor") is True
            and aabb_prepare_reuse_query_cache.get("checks", {}).get("larger_scale_not_better") is True
            and aabb_prepare_reuse_query_cache.get("blocker_summary", {}).get(
                "best_cold_plus_collect_wall_speedup", 99.0
            )
            < aabb_prepare_reuse_query_cache.get("material_wall_speedup_floor", 0.0)
        ),
        "aabb_native_query_handle_evidence_exists": AABB_NATIVE_QUERY_HANDLE_EVIDENCE.exists(),
        "aabb_native_query_handle_evidence_pending_external_review": (
            aabb_native_query_handle.get("status")
            == "aabb_native_query_handle_m7_candidate_pending_external_review"
            and aabb_native_query_handle.get("failed_checks") == []
            and aabb_native_query_handle.get("m7_qualified_release_rows_added") == 0
            and aabb_native_query_handle.get("m7_candidate_reopen_authorized") is True
            and aabb_native_query_handle.get("m7_promotion_authorized") is False
            and aabb_native_query_handle.get("release_authorized") is False
            and aabb_native_query_handle.get("public_speedup_claim_authorized") is False
            and aabb_native_query_handle.get("broad_v3_faster_than_v2_claim_authorized") is False
            and aabb_native_query_handle.get("candidate_summary", {}).get(
                "best_cold_plus_collect_wall_speedup", 0.0
            )
            >= aabb_native_query_handle.get("material_wall_speedup_floor", 99.0)
            and aabb_native_query_handle.get("candidate_summary", {}).get(
                "largest_cold_plus_collect_wall_speedup", 0.0
            )
            >= aabb_native_query_handle.get("material_wall_speedup_floor", 99.0)
            and aabb_native_query_handle.get("candidate_summary", {}).get(
                "native_query_handle_cache_observed"
            )
            is True
        ),
        "aabb_raw_oracle_evidence_exists": AABB_RAW_ORACLE_EVIDENCE.exists(),
        "aabb_raw_oracle_closes_correctness_not_m7": (
            aabb_raw_oracle.get("status") == "aabb_raw_oracle_pass_not_m7"
            and aabb_raw_oracle.get("failed_checks") == []
            and aabb_raw_oracle.get("raw_aabb_oracle_closes_correctness_blocker") is True
            and len(str(aabb_raw_oracle.get("source_manifest_sha256", ""))) == 64
            and aabb_raw_oracle.get("m7_promotion_authorized") is False
            and aabb_raw_oracle.get("release_authorized") is False
            and aabb_raw_oracle.get("public_speedup_claim_authorized") is False
            and aabb_raw_oracle.get("checks", {}).get("all_rows_match_independent_cpu_oracle") is True
            and aabb_raw_oracle.get("checks", {}).get("optix_capacity_pressure_fail_closed_if_requested") is True
        ),
        "aabb_native_query_handle_stability_exists": AABB_NATIVE_QUERY_HANDLE_STABILITY_EVIDENCE.exists(),
        "aabb_native_query_handle_stability_closes_blocker_not_m7": (
            aabb_native_query_handle_stability.get("status")
            == "aabb_native_query_handle_stability_pass_not_m7"
            and aabb_native_query_handle_stability.get("failed_checks") == []
            and aabb_native_query_handle_stability.get("fresh_run_stability_closes_blocker") is True
            and aabb_native_query_handle_stability.get("m7_promotion_authorized") is False
            and aabb_native_query_handle_stability.get("release_authorized") is False
            and aabb_native_query_handle_stability.get("public_speedup_claim_authorized") is False
            and aabb_native_query_handle_stability.get("stability_summary", {}).get(
                "weakest_cold_plus_collect_wall_speedup", 0.0
            )
            >= aabb_native_query_handle_stability.get("material_wall_speedup_floor", 99.0)
        ),
        "aabb_native_query_handle_row_wording_gate_exists": AABB_NATIVE_QUERY_HANDLE_ROW_WORDING_GATE.exists(),
        "aabb_native_query_handle_row_wording_gate_closed_or_defines_stable_ids": (
            aabb_native_query_handle_row_wording_gate.get("status")
            in {
                "aabb_native_query_handle_stable_row_wording_gate_ready_external_review_blocked_not_m7",
                "aabb_native_query_handle_row_wording_gate_closed_after_claude_codex_m7_review",
            }
            and aabb_native_query_handle_row_wording_gate.get("failed_checks") == []
            and aabb_native_query_handle_row_wording_gate.get("stable_candidate_row_id_gate_closed") is True
            and aabb_native_query_handle_row_wording_gate.get("m7_qualified_release_rows_added") in {0, 2}
            and aabb_native_query_handle_row_wording_gate.get("m7_promotion_authorized") in {False, True}
            and aabb_native_query_handle_row_wording_gate.get("release_authorized") is False
            and aabb_native_query_handle_row_wording_gate.get("public_speedup_claim_authorized") is False
            and aabb_native_query_handle_row_wording_gate.get("candidate_row_ids")
            == [
                "aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50",
                "aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50",
            ]
        ),
        "aabb_native_query_handle_review_gate_exists": AABB_NATIVE_QUERY_HANDLE_REVIEW_GATE.exists(),
        "aabb_native_query_handle_review_gate_m7_qualified_two_rows": (
            aabb_native_query_handle_review_gate.get("status")
            == "aabb_native_query_handle_two_rows_m7_qualified_row_scoped"
            and aabb_native_query_handle_review_gate.get("failed_checks") == []
            and aabb_native_query_handle_review_gate.get("raw_oracle_closes_correctness_blocker") is True
            and aabb_native_query_handle_review_gate.get("source_manifest_provenance_closes_blocker") is True
            and aabb_native_query_handle_review_gate.get("fresh_run_stability_closes_blocker") is True
            and aabb_native_query_handle_review_gate.get("stable_candidate_row_id_gate_closed") is True
            and aabb_native_query_handle_review_gate.get("candidate_wording_gate_present") is True
            and aabb_native_query_handle_review_gate.get("public_wording_review_closed") is True
            and aabb_native_query_handle_review_gate.get("codex_consensus_response_closed") is True
            and aabb_native_query_handle_review_gate.get("claude_p1_conditions_applied") is True
            and aabb_native_query_handle_review_gate.get("m7_promotion_authorized") is True
            and aabb_native_query_handle_review_gate.get("m7_qualified_release_rows_added") == 2
            and aabb_native_query_handle_review_gate.get("required_blockers_before_m7") == []
        ),
        "aabb_native_query_handle_final_review_request_exists": (
            AABB_NATIVE_QUERY_HANDLE_FINAL_REVIEW_REQUEST.exists()
            and "Final M7 Review"
            in AABB_NATIVE_QUERY_HANDLE_FINAL_REVIEW_REQUEST.read_text(encoding="utf-8")
        ),
        "aabb_native_query_handle_final_review_blocked_record_exists": (
            AABB_NATIVE_QUERY_HANDLE_FINAL_REVIEW_BLOCKED.exists()
            and "external_review_blocked_no_2ai_consensus"
            in AABB_NATIVE_QUERY_HANDLE_FINAL_REVIEW_BLOCKED.read_text(encoding="utf-8")
            and "claude.exe" in AABB_NATIVE_QUERY_HANDLE_FINAL_REVIEW_BLOCKED.read_text(encoding="utf-8")
        ),
        "aabb_prepare_reuse_contract_names_runner": (
            aabb_prepare_reuse.get("pod_runner", {}).get("script")
            == "scripts/v3_phoenix_aabb_prepare_reuse_pod_runner.py"
            and aabb_prepare_reuse.get("pod_runner", {}).get("status")
            == "runner_available_not_yet_rt_pod_evidence"
            and aabb_prepare_reuse.get("pod_runner", {}).get("m7_promotion_authorized_by_runner_alone")
            is False
        ),
        "spatial_topology_contract_exists": SPATIAL_RAYJOIN_TOPOLOGY_STREAM_CONTRACT.exists(),
        "spatial_topology_contract_not_m7": (
            spatial_topology_contract.get("status")
            == "spatial_rayjoin_topology_stream_contract_candidate_not_m7"
            and spatial_topology_contract.get("m7_qualified_release_rows_added") == 0
            and spatial_topology_contract.get("m7_promotion_authorized") is False
            and spatial_topology_contract.get("rtdl_beats_rayjoin_claim_authorized") is False
        ),
        "spatial_m3_gap_analysis_exists": SPATIAL_RAYJOIN_M3_GAP_ANALYSIS.exists(),
        "spatial_m3_gap_analysis_not_m7": (
            spatial_m3_gap_analysis.get("status") == "spatial_rayjoin_m3_gap_analysis_not_m7"
            and spatial_m3_gap_analysis.get("m7_qualified_release_rows_added") == 0
            and spatial_m3_gap_analysis.get("m7_promotion_authorized") is False
            and spatial_m3_gap_analysis.get("true_zero_copy_claim_authorized") is False
            and spatial_m3_gap_analysis.get("large_pip_device_resident_delta", {}).get(
                "device_resident_wall_speedup_vs_default", 0.0
            )
            >= 2.0
        ),
        "spatial_m3_exact_executor_evidence_exists": SPATIAL_RAYJOIN_M3_EXACT_EXECUTOR_EVIDENCE.exists(),
        "spatial_m3_exact_executor_evidence_not_m7": (
            spatial_m3_exact_executor_evidence.get("status")
            == "spatial_rayjoin_topology_stream_m3_pod_evidence_pending_review_not_m7"
            and spatial_m3_exact_executor_evidence.get("m7_qualified_release_rows_added") == 0
            and spatial_m3_exact_executor_evidence.get("m7_promotion_authorized") is False
            and spatial_m3_exact_executor_evidence.get("failed_checks") == []
            and spatial_m3_exact_executor_evidence.get("checks", {}).get("all_full_m3_when_required") is True
            and spatial_m3_exact_executor_evidence.get("checks", {}).get("counts_consistent") is True
            and spatial_m3_exact_executor_evidence.get("summary", {}).get("row_count") == 47262
            and spatial_m3_exact_executor_evidence.get("summary", {}).get("query_stream_residency")
            == "device_resident_prepared_point_probe_columns_with_reusable_exact_executor"
            and spatial_m3_exact_executor_evidence.get("summary", {}).get(
                "m3_phase_sec_medians", {}
            ).get("rt_traversal_sec", 0.0)
            > 0.0
        ),
        "spatial_exact_executor_intake_exists": SPATIAL_RAYJOIN_EXACT_EXECUTOR_INTAKE.exists(),
        "spatial_exact_executor_intake_not_m7": (
            spatial_exact_executor_intake.get("status") == "spatial_rayjoin_exact_executor_intake_not_m7"
            and spatial_exact_executor_intake.get("failed_checks") == []
            and spatial_exact_executor_intake.get("m7_qualified_release_rows_added") == 0
            and spatial_exact_executor_intake.get("m7_promotion_authorized") is False
            and spatial_exact_executor_intake.get("prior_author_gap", {}).get(
                "direct_current_packet_comparison_authorized"
            )
            is False
            and spatial_exact_executor_intake.get("m3_bottleneck", {}).get(
                "topology_continuation_over_rt_traversal", 0.0
            )
            > 10.0
        ),
        "spatial_relation_status_no_go_exists": SPATIAL_RAYJOIN_RELATION_STATUS_NO_GO.exists(),
        "spatial_relation_status_no_go_blocks_promotion": (
            spatial_relation_status_no_go.get("status")
            == "spatial_rayjoin_relation_status_corrected_executor_no_go_exact_mismatch"
            and spatial_relation_status_no_go.get("failed_checks") == []
            and spatial_relation_status_no_go.get("m7_qualified_release_rows_added") == 0
            and spatial_relation_status_no_go.get("m7_promotion_authorized") is False
            and spatial_relation_status_no_go.get("exact_authority_count") == 47262
            and spatial_relation_status_no_go.get("candidate_count") == 47259
            and spatial_relation_status_no_go.get("candidate_minus_exact") == -3
        ),
        "spatial_relation_status_exact_f64_intake_exists": (
            SPATIAL_RAYJOIN_RELATION_STATUS_EXACT_F64_INTAKE.exists()
        ),
        "spatial_relation_status_exact_f64_review_gate_exists": (
            SPATIAL_RAYJOIN_RELATION_STATUS_EXACT_F64_REVIEW_GATE.exists()
        ),
        "spatial_relation_status_exact_f64_adverse_subset_exists": (
            SPATIAL_RAYJOIN_RELATION_STATUS_EXACT_F64_ADVERSE_SUBSET.exists()
        ),
        "spatial_active_p0_closure_gate_exists": SPATIAL_RAYJOIN_ACTIVE_P0_CLOSURE_GATE.exists(),
        "spatial_prefilter_zero_experiment_exists": SPATIAL_RAYJOIN_PREFILTER_ZERO_EXPERIMENT.exists(),
        "spatial_prefilter_zero_experiment_near_miss_not_m7": (
            spatial_prefilter_zero_experiment.get("status")
            == "spatial_relation_status_prefilter_zero_near_miss_not_m7"
            and spatial_prefilter_zero_experiment.get("failed_checks") == []
            and spatial_prefilter_zero_experiment.get("m7_qualified_release_rows_added") == 0
            and spatial_prefilter_zero_experiment.get("m7_promotion_authorized") is False
            and spatial_prefilter_zero_experiment.get("release_authorized") is False
            and spatial_prefilter_zero_experiment.get("rtdl_beats_rayjoin_claim_authorized")
            is False
            and spatial_prefilter_zero_experiment.get("summary", {}).get("row_count") == 47262
            and spatial_prefilter_zero_experiment.get("summary", {}).get("row_count_consistent")
            is True
            and spatial_prefilter_speedup > 2.5
            and spatial_prefilter_author_speedup > 1.0
            and spatial_prefilter_gap_ms > 0.0
            and spatial_prefilter_zero_experiment.get("failed_followup_experiment", {}).get(
                "status"
            )
            == "rejected_exact_count_mismatch_not_kept"
        ),
        "spatial_count_only_no_diagnostics_no_go_exists": (
            SPATIAL_RAYJOIN_COUNT_ONLY_NO_DIAGNOSTICS_NO_GO.exists()
        ),
        "spatial_count_only_no_diagnostics_rejected_not_m7": (
            spatial_count_only_no_diag_no_go.get("status")
            == "spatial_relation_status_count_only_no_diagnostics_no_go_not_m7"
            and spatial_count_only_no_diag_no_go.get("failed_checks") == []
            and spatial_count_only_no_diag_no_go.get("m7_qualified_release_rows_added") == 0
            and spatial_count_only_no_diag_no_go.get("m7_promotion_authorized") is False
            and spatial_count_only_no_diag_no_go.get("release_authorized") is False
            and spatial_count_only_no_diag_no_go.get("rtdl_beats_rayjoin_claim_authorized")
            is False
            and spatial_count_only_summary.get("count_only_was_faster") is False
            and spatial_count_only_summary.get("count_only_source_retained") is False
            and spatial_count_only_delta_ms > 0.0
        ),
        "spatial_squared_boundary_candidate_exists": SPATIAL_RAYJOIN_SQUARED_BOUNDARY_CANDIDATE.exists(),
        "spatial_squared_boundary_candidate_default_path_m7_accepted": (
            spatial_squared_boundary_m7_approved
        ),
        "spatial_squared_boundary_historical_review_request_exists": (
            SPATIAL_RAYJOIN_SQUARED_BOUNDARY_REVIEW_REQUEST.exists()
        ),
        "spatial_squared_boundary_historical_claude_review_exists": (
            SPATIAL_RAYJOIN_SQUARED_BOUNDARY_CLAUDE_REVIEW.exists()
        ),
        "spatial_squared_boundary_historical_codex_consensus_exists": (
            SPATIAL_RAYJOIN_SQUARED_BOUNDARY_CODEX_CONSENSUS.exists()
        ),
        "spatial_squared_boundary_historical_external_blocked_record_exists": (
            SPATIAL_RAYJOIN_SQUARED_BOUNDARY_EXTERNAL_BLOCKED.exists()
        ),
        "spatial_default_path_review_request_exists": (
            SPATIAL_RAYJOIN_DEFAULT_PATH_REVIEW_REQUEST.exists()
        ),
        "spatial_default_path_claude_review_exists": (
            SPATIAL_RAYJOIN_DEFAULT_PATH_CLAUDE_REVIEW.exists()
        ),
        "spatial_default_path_codex_consensus_exists": (
            SPATIAL_RAYJOIN_DEFAULT_PATH_CODEX_CONSENSUS.exists()
        ),
        "spatial_overlay_active_count_full_scale_no_go_exists": (
            SPATIAL_OVERLAY_ACTIVE_COUNT_FULL_SCALE_NO_GO.exists()
        ),
        "spatial_overlay_active_count_full_scale_no_go_review_request_exists": (
            SPATIAL_OVERLAY_ACTIVE_COUNT_FULL_SCALE_NO_GO_REVIEW_REQUEST.exists()
        ),
        "spatial_overlay_active_count_full_scale_no_go_blocks_m7": (
            spatial_overlay_active_count_full_scale_no_go.get("status")
            == "spatial_overlay_active_count_full_scale_no_go"
            and spatial_overlay_active_count_full_scale_no_go.get(
                "local_evidence_sufficient_for_external_public_row_review"
            )
            is False
            and spatial_overlay_active_count_full_scale_no_go.get(
                "candidate_m7_contribution_if_external_review_approves"
            )
            == 0
            and spatial_overlay_active_count_full_scale_no_go.get("m7_qualified_release_rows_added_now")
            == 0
            and spatial_overlay_active_count_full_scale_no_go.get("m7_promotion_authorized") is False
            and spatial_overlay_active_count_full_scale_no_go.get("release_authorized") is False
            and spatial_overlay_active_count_full_scale_no_go.get("public_speedup_claim_authorized") is False
            and spatial_overlay_active_count_full_scale_no_go.get("checks", {}).get("active_counts_match")
            is False
            and spatial_overlay_active_count_full_scale_no_go.get("checks", {}).get(
                "optix_m3_table_complete"
            )
            is True
            and spatial_overlay_pair_count == 122051800
            and spatial_overlay_optix_count == 19277
            and spatial_overlay_embree_count == 21228
            and spatial_overlay_count_delta == -1951
            and spatial_overlay_speedup > 1000.0
        ),
        "spatial_relation_status_exact_f64_intake_not_m7": (
            spatial_relation_status_exact_f64.get("status")
            == "spatial_rayjoin_relation_status_exact_f64_device_scalar_count_intake_not_m7"
            and spatial_relation_status_exact_f64.get("failed_checks") == []
            and spatial_relation_status_exact_f64.get("current_exact_count") == 47262
            and spatial_relation_status_exact_f64.get("m7_qualified_release_rows_added") == 0
            and spatial_relation_status_exact_f64.get("m7_promotion_authorized") is False
            and spatial_relation_status_exact_f64.get("release_authorized") is False
            and spatial_relation_status_exact_f64.get("rtdl_beats_rayjoin_claim_authorized") is False
            and spatial_relation_status_exact_f64.get("checks", {}).get(
                "native_source_uses_exact_f64_full_predicate"
            )
            is True
            and spatial_relation_status_exact_f64.get("checks", {}).get(
                "native_source_no_longer_keeps_status_one_without_exact_check"
            )
            is True
            and spatial_relation_status_exact_f64.get("comparison_vs_exact_executor", {}).get(
                "prepared_query_speedup_vs_exact_executor", 0.0
            )
            >= 3.0
            and spatial_relation_status_exact_f64.get("comparison_vs_exact_executor", {}).get(
                "runner_wall_speedup_vs_exact_executor", 0.0
            )
            >= 1.2
        ),
        "spatial_relation_status_exact_f64_review_gate_blocks_m7": (
            spatial_relation_status_exact_f64_review_gate.get("status")
            == "spatial_rayjoin_relation_status_exact_f64_review_blocked_not_m7"
            and spatial_relation_status_exact_f64_review_gate.get("failed_checks") == []
            and spatial_relation_status_exact_f64_review_gate.get("external_review_status")
            == "blocked_no_external_ai_verdict"
            and spatial_relation_status_exact_f64_review_gate.get("m7_candidate_reopen_authorized") is False
            and spatial_relation_status_exact_f64_review_gate.get("m7_promotion_authorized") is False
            and spatial_relation_status_exact_f64_review_gate.get("release_authorized") is False
            and spatial_relation_status_exact_f64_review_gate.get("rtdl_beats_rayjoin_claim_authorized")
            is False
            and spatial_relation_status_exact_f64_review_gate.get("adverse_subset_parity_closed") is True
            and "adverse_subset_parity_missing"
            not in set(spatial_relation_status_exact_f64_review_gate.get("required_blockers_before_m7", []))
            and "same_dataset_rayjoin_author_timing_basis_missing"
            not in set(spatial_relation_status_exact_f64_review_gate.get("required_blockers_before_m7", []))
            and {
                "external_ai_review_missing",
                "rayjoin_author_result_count_not_printed_or_public_scope_review_missing",
                "rayjoin_author_query_faster_than_rtdl_exact_f64_query",
                "public_wording_review_missing",
            }.issubset(set(spatial_relation_status_exact_f64_review_gate.get("required_blockers_before_m7", [])))
        ),
        "spatial_relation_status_exact_f64_author_basis_present_not_m7": (
            spatial_relation_status_exact_f64_review_gate.get("author_timing_basis", {}).get("status")
            == "present_but_not_m7_author_query_faster_count_not_printed"
            and spatial_relation_status_exact_f64_review_gate.get("author_timing_basis", {}).get(
                "same_dataset_author_timing_basis_present"
            )
            is True
            and spatial_relation_status_exact_f64_review_gate.get("author_timing_basis", {})
            .get("current_candidate", {})
            .get("exact_count")
            == 47262
            and spatial_relation_status_exact_f64_review_gate.get("author_timing_basis", {})
            .get("same_dataset_author_evidence", {})
            .get("author_result_count_printed")
            is False
            and spatial_relation_status_exact_f64_review_gate.get("author_timing_basis", {})
            .get("same_dataset_author_evidence", {})
            .get("rayjoin_author_query_speedup_vs_rtdl_exact_f64_prepared_query", 0.0)
            > 1.0
            and spatial_relation_status_exact_f64_review_gate.get("author_timing_basis", {})
            .get("prior_author_evidence", {})
            .get("query_count")
            == 100000
            and spatial_relation_status_exact_f64_review_gate.get("author_timing_basis", {})
            .get("prior_author_evidence", {})
            .get("direct_current_packet_comparison_authorized")
            is False
            and "external public wording review"
            in " ".join(
                spatial_relation_status_exact_f64_review_gate.get("author_timing_basis", {}).get(
                    "required_evidence_before_m7", []
                )
            )
        ),
        "spatial_relation_status_exact_f64_adverse_subset_pass_not_m7": (
            spatial_relation_status_exact_f64_adverse_subset.get("status")
            == "spatial_rayjoin_relation_status_exact_f64_adverse_subset_parity_pass_not_m7"
            and spatial_relation_status_exact_f64_adverse_subset.get("failed_checks") == []
            and spatial_relation_status_exact_f64_adverse_subset.get("adverse_subset_parity_closes_blocker") is True
            and spatial_relation_status_exact_f64_adverse_subset.get("row_count") == 6
            and spatial_relation_status_exact_f64_adverse_subset.get("row_count_consistent") is True
            and spatial_relation_status_exact_f64_adverse_subset.get("m7_qualified_release_rows_added") == 0
            and spatial_relation_status_exact_f64_adverse_subset.get("m7_promotion_authorized") is False
            and spatial_relation_status_exact_f64_adverse_subset.get("release_authorized") is False
            and spatial_relation_status_exact_f64_adverse_subset.get("public_speedup_claim_authorized") is False
        ),
        "spatial_active_p0_closure_gate_authorizes_future_research_closure": spatial_active_p0_closed,
        "spatial_device_filtered_rejected_log_exists": SPATIAL_RAYJOIN_DEVICE_FILTERED_REJECTED_LOG.exists(),
        "spatial_device_filtered_rejected_log_records_mismatch": (
            SPATIAL_RAYJOIN_DEVICE_FILTERED_REJECTED_LOG.exists()
            and "47570 != 47262" in SPATIAL_RAYJOIN_DEVICE_FILTERED_REJECTED_LOG.read_text(encoding="utf-8")
        ),
        "barnes_hut_vector_accumulation_contract_exists": BARNES_HUT_VECTOR_ACCUMULATION_CONTRACT.exists(),
        "barnes_hut_vector_accumulation_contract_not_m7": (
            barnes_hut_vector_contract.get("status")
            == "barnes_hut_vector_accumulation_contract_candidate_not_m7"
            and barnes_hut_vector_contract.get("m7_qualified_release_rows_added") == 0
            and barnes_hut_vector_contract.get("m7_promotion_authorized") is False
            and barnes_hut_vector_contract.get("rt_core_speedup_claim_authorized") is False
        ),
        "barnes_hut_m129_wrapper_ready_native_blocked": (
            barnes_hut_m129_wrapper_gate.get("status")
            == "python_wrapper_ready_native_execution_blocked"
            and barnes_hut_m129_wrapper_gate.get("implementation_gate", {}).get("python_wrapper_ready") is True
            and barnes_hut_m129_wrapper_gate.get("implementation_gate", {}).get("native_execution_ready") is False
            and barnes_hut_m129_wrapper_gate.get("claim_boundary", {}).get("rt_core_speedup_claim_authorized")
            is False
        ),
        "barnes_hut_m131_blocks_naive_all_node_anyhit": (
            barnes_hut_m131_semantic_gate.get("status")
            == "barnes_hut_rt_native_semantic_gate_safe_to_advance_runtime_queue"
            and barnes_hut_m131_semantic_gate.get("semantic_constraints", {}).get(
                "direct_all_node_anyhit_route_accepted"
            )
            is False
            and barnes_hut_m131_semantic_gate.get("semantic_constraints", {}).get(
                "parent_acceptance_suppresses_descendants"
            )
            is True
            and barnes_hut_m131_semantic_gate.get("claim_boundary", {}).get("rt_core_speedup_claim_authorized")
            is False
        ),
        "barnes_hut_m142_current_route_closed_future_research": (
            barnes_hut_m142_closure_gate.get("status")
            == "barnes_hut_current_route_closure_gate_checked"
            and barnes_hut_m142_closure_gate.get("barnes_hut_row", {}).get("work_class")
            == "closed_current_target"
            and barnes_hut_m142_closure_gate.get("barnes_hut_row", {}).get("priority") is None
            and barnes_hut_m142_closure_gate.get("claim_boundary", {}).get(
                "rt_native_hierarchical_traversal_implemented"
            )
            is False
        ),
        "future_work_records_barnes_hut_not_active_p0": any(
            item["id"] == "barnes_hut_vector_accumulation_frontier_shape"
            and item["priority"] == "future_research_not_current_p0"
            and item["active_candidate_status"] == "barnes_hut_future_research_not_current_p0_not_m7"
            for item in future_work
        ),
        "future_work_no_longer_records_spatial_current_gap_after_default_path_m7": all(
            item["id"] != "spatial_rayjoin_topology_stream_author_gap" for item in future_work
        ),
        "barnes_hut_same_basis_no_go_records_current_optix_shape_not_m7": (
            barnes_hut_same_basis_no_go.get("status")
            == "barnes_hut_same_basis_no_go_current_frontier_shape_not_m7"
            and barnes_hut_same_basis_no_go.get("m7_qualified_release_rows_added") == 0
            and barnes_hut_same_basis_no_go.get("current_prepared_optix_frontier_shape_m7_authorized")
            is False
        ),
        "barnes_hut_fused_partner_candidate_no_longer_pending_external_review": (
            barnes_hut_fused_partner_pending is False
        ),
        "barnes_hut_fused_partner_candidate_approved_with_amendments": barnes_hut_fused_partner_approved,
        "barnes_hut_fused_partner_review_request_exists": BARNES_HUT_FUSED_PARTNER_REVIEW_REQUEST.exists(),
        "barnes_hut_fused_partner_claude_blocked_record_exists": BARNES_HUT_FUSED_PARTNER_CLAUDE_BLOCKED.exists(),
        "barnes_hut_fused_partner_claude_retry_blocked_record_exists": (
            BARNES_HUT_FUSED_PARTNER_CLAUDE_RETRY_BLOCKED.exists()
        ),
        "barnes_hut_fused_partner_claude_review_exists": BARNES_HUT_FUSED_PARTNER_CLAUDE_REVIEW.exists(),
        "barnes_hut_fused_partner_codex_consensus_exists": (
            BARNES_HUT_FUSED_PARTNER_CODEX_CONSENSUS.exists()
        ),
        "pending_external_review_candidates_have_no_release_claims": all(
            item["release_authorized"] is False
            and item["public_speedup_claim_authorized"] is False
            and item["rt_core_speedup_claim_authorized"] is False
            and item["m7_rows_added_now"] == 0
            for item in pending_external_review_candidates
        ),
        "accepted_with_boundary_candidates_have_no_release_claims": all(
            item["release_authorized"] is False
            and item["public_speedup_claim_authorized"] is False
            and item["rt_core_speedup_claim_authorized"] is False
            and item["m7_rows_added_now"] == 0
            for item in accepted_with_boundary_candidates
        ),
        "existing_evidence_has_no_next_m7_candidates": m7_packet.get("next_m7_promotion_candidates") == [],
        "existing_optimization_queue_empty": m7_packet.get("optimization_required_reopen_queue") == [],
        "queue_has_no_active_items_after_spatial_closure": [item["id"] for item in queue] == [],
        "closed_work_records_aabb_native_query_handle": any(
            item["id"] == "contact_aabb_prepare_reuse" and item["m7_rows_added"] == 2
            for item in closed
        ),
        "closed_work_records_rtnn_prepared_repeat50": any(
            item["id"] == "rtnn_ranked_summary_wall_path" and item["m7_rows_added"] == 1
            for item in closed
        ),
        "closed_work_records_barnes_hut_fused_partner": any(
            item["id"] == "barnes_hut_fused_partner_vector_accumulation"
            and item["m7_rows_added"] == 1
            and item["generic_capability"] == "aggregate_frontier"
            and item["refined_generic_capability"] == "vector_accumulation"
            for item in closed
        ),
        "closed_work_records_spatial_default_path_topology_stream": any(
            item["id"] == "spatial_squared_boundary_default_path_topology_stream"
            and item["m7_rows_added"] == 1
            and item["generic_capability"] == "point_location_topology_stream"
            and item["refined_generic_capability"] == "exact_f64_guarded_boundary_predicate"
            and item["candidate_row_id"]
            == "point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7"
            for item in closed
        ),
        "queue_capabilities_are_allowed": all(item["generic_capability"] in allowed for item in queue),
        "queue_has_no_app_specific_native_engine_shortcut": all(
            "app-specific" not in item["generic_engine_action"].lower() for item in queue
        ),
        "future_work_has_no_app_specific_native_engine_shortcut": all(
            "app-specific" not in item["generic_engine_action"].lower()
            for item in future_work
        ),
        "queue_preserves_no_release_status": True,
    }
    failed_checks = [name for name, ok in checks.items() if not ok]
    status = "fail" if failed_checks else "generic_engine_work_queue_closed_not_release"

    return {
        "tool": "v3_phoenix_next_engine_work_queue",
        "status": status,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "current_m7_qualified_release_rows": current_m7_rows,
        "base_m7_packet_rows": m7_packet.get("phoenix_m7_qualified_release_rows"),
        "supplemental_m7_rows_from_current_queue": spatial_supplemental_m7_rows,
        "existing_evidence_promotable_now": False,
        "minimum_new_promotion_bar": (
            "A 1.01x-style result cannot qualify as a new Phoenix V3 performance win. "
            "A future row needs material, row-scoped value, phase/wall evidence, correctness, "
            "source provenance, and 2-AI review."
        ),
        "closed_generic_engine_work": closed,
        "queue": queue,
        "pending_external_review_candidates": pending_external_review_candidates,
        "accepted_with_boundary_candidates": accepted_with_boundary_candidates,
        "future_generic_engine_work": future_work,
        "release_blockers_outside_engine_queue": [
            "release_authorization_false",
            "updated_thirteen_row_release_readiness_consensus_required",
        ],
        "checks": checks,
        "failed_checks": failed_checks,
        "decision_audit": {
            "decision": "Keep the Phoenix V3 generic-engine active queue empty while promoting exactly one Spatial default-path topology-stream row into the current M7 release surface, without authorizing release.",
            "was_i_foolish": "No. For the goal-level queue decision, it records the real grouped_sum, AABB native-query-handle, RTNN prepared repeat50, amended Barnes-Hut fused-partner, and Spatial default-path guarded squared-boundary Claude/Codex closures while keeping release, whole-app, one-shot, RTDL-beats-RayJoin, RT-core, true-zero-copy, and broad V3-over-V2 claims forbidden.",
            "foolish_actions": "The foolish action would be to mine the old P0 matrix, the full-scale overlay 1262x timed-median ratio, the Barnes-Hut 13.591x OptiX no-go comparison, the Spatial prefilter near-miss, or the new Spatial default-path row for impressive broad claims while ignoring correctness blockers, wall timing, author-baseline boundaries, validation tier, source provenance, disabled-control limits, or 2-AI review. The concrete tooling mistakes were Bash/PowerShell heredoc quoting and a timed-out minimal Claude check; neither changed release status. The boundary-helper and count-only experiments were rejected.",
            "other_path": "Keep polishing docs or tune individual apps. That can look productive but would not prove a V3 language-level performance breakthrough.",
            "different_path_now": "Use the accepted Spatial default-path packet as one bounded M7 release-surface row, update the breadth/readiness gates to 13 rows and 9 capability families, then seek fresh aggregate 2-AI release-readiness review before any release wording.",
        },
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Phoenix V3 Next Generic Engine Work Queue",
        "",
        (
            "Status: closed generic-engine queue; not release authorization."
            if payload["status"] == "generic_engine_work_queue_closed_not_release"
            else "Status: active generic-engine work queue; not release authorization."
        ),
        "",
        "This packet answers the current Phoenix question: the next work is V3",
        "engine work, not app development. Apps are evidence harnesses only.",
        "",
        "Current hard facts:",
        "",
        f"- `release_authorized: {str(payload['release_authorized']).lower()}`",
        f"- `public_speedup_claim_authorized: {str(payload['public_speedup_claim_authorized']).lower()}`",
        f"- `broad_v3_faster_than_v2_claim_authorized: {str(payload['broad_v3_faster_than_v2_claim_authorized']).lower()}`",
        f"- `current_m7_qualified_release_rows: {payload['current_m7_qualified_release_rows']}`",
        f"- `base_m7_packet_rows: {payload.get('base_m7_packet_rows')}`",
        f"- `supplemental_m7_rows_from_current_queue: {payload.get('supplemental_m7_rows_from_current_queue')}`",
        f"- `existing_evidence_promotable_now: {str(payload['existing_evidence_promotable_now']).lower()}`",
        f"- `pending_external_review_candidate_count: {len(payload.get('pending_external_review_candidates', []))}`",
        f"- `accepted_with_boundary_candidate_count: {len(payload.get('accepted_with_boundary_candidates', []))}`",
        "",
        "Minimum bar:",
        "",
        payload["minimum_new_promotion_bar"],
        "",
        "## Closed Generic Engine Work",
        "",
    ]
    for item in payload["closed_generic_engine_work"]:
        lines.extend(
            [
                f"### {item['id']}",
                "",
                f"- Generic capability: `{item['generic_capability']}`",
                *(
                    [f"- Refined capability: `{item['refined_generic_capability']}`"]
                    if "refined_generic_capability" in item
                    else []
                ),
                f"- Closed state: {item['closed_state']}",
                f"- Closed by packet: `{item['closed_by_packet']}`",
                *(
                    [f"- Closed by external review: `{item['closed_by_external_review']}`"]
                    if "closed_by_external_review" in item
                    else []
                ),
                f"- Closed by consensus: `{item['closed_by_consensus']}`",
                *([f"- Candidate row id: `{item['candidate_row_id']}`"] if "candidate_row_id" in item else []),
                *(
                    [f"- Evidence tree structure: `{item['evidence_tree_structure']}`"]
                    if "evidence_tree_structure" in item
                    else []
                ),
                *(
                    [f"- Large-scale validation tier: `{item['large_scale_validation_tier']}`"]
                    if "large_scale_validation_tier" in item
                    else []
                ),
                f"- M7 rows added: {item['m7_rows_added']}",
                f"- Forbidden shortcut: {item['forbidden_shortcut']}",
                "",
            ]
        )
    lines.extend(
        [
        "## Queue",
        "",
        ]
    )
    for item in payload["queue"]:
        lines.extend(
            [
                f"### {item['id']}",
                "",
                f"- Priority: `{item['priority']}`",
                f"- Generic capability: `{item['generic_capability']}`",
                f"- Apps used as evidence: `{', '.join(item['apps_used_as_evidence'])}`",
                f"- Current state: {item['current_state']}",
                f"- Generic engine action: {item['generic_engine_action']}",
                f"- Evidence to reopen M7: {item['evidence_to_reopen_m7']}",
                *(
                    [f"- Reconciliation packet: `{item['reconciliation_packet']}`"]
                    if "reconciliation_packet" in item
                    else []
                ),
                *(
                    [f"- Latest evidence packet: `{item['latest_evidence_packet']}`"]
                    if "latest_evidence_packet" in item and "active_candidate_packet" not in item
                    else []
                ),
                *(
                    [f"- Latest evidence status: `{item['latest_evidence_status']}`"]
                    if "latest_evidence_status" in item and "active_candidate_packet" not in item
                    else []
                ),
                *(
                    [
                        f"- Latest review gate packet: `{item['latest_review_gate_packet']}`",
                        f"- Latest review gate status: `{item['latest_review_gate_status']}`",
                    ]
                    if "latest_review_gate_packet" in item and "active_candidate_packet" not in item
                    else []
                ),
                *(
                    [
                        f"- Latest CUBIN cache packet: `{item['latest_cubin_cache_packet']}`",
                        f"- Latest CUBIN cache status: `{item['latest_cubin_cache_status']}`",
                    ]
                    if "latest_cubin_cache_packet" in item and "active_candidate_packet" not in item
                    else []
                ),
                *(
                    [
                        f"- Latest self-query packet: `{item['latest_self_query_packet']}`",
                        f"- Latest self-query status: `{item['latest_self_query_status']}`",
                    ]
                    if "latest_self_query_packet" in item and "active_candidate_packet" not in item
                    else []
                ),
                *(
                    [
                        f"- Latest lazy-exact packet: `{item['latest_lazy_exact_prepare_packet']}`",
                        f"- Latest lazy-exact status: `{item['latest_lazy_exact_prepare_status']}`",
                    ]
                    if "latest_lazy_exact_prepare_packet" in item and "active_candidate_packet" not in item
                    else []
                ),
                *(
                    [
                        f"- Latest self-query graph packet: `{item['latest_self_query_graph_packet']}`",
                        f"- Latest self-query graph status: `{item['latest_self_query_graph_status']}`",
                    ]
                    if "latest_self_query_graph_packet" in item and "active_candidate_packet" not in item
                    else []
                ),
                *(
                    [
                        f"- Latest column-source packet: `{item['latest_column_source_packet']}`",
                        f"- Latest column-source status: `{item['latest_column_source_status']}`",
                    ]
                    if "latest_column_source_packet" in item and "active_candidate_packet" not in item
                    else []
                ),
                *(
                    [
                        f"- Latest NPZ+CUBIN packet: `{item['latest_npz_cubin_packet']}`",
                        f"- Latest NPZ+CUBIN status: `{item['latest_npz_cubin_status']}`",
                    ]
                    if "latest_npz_cubin_packet" in item and "active_candidate_packet" not in item
                    else []
                ),
                *(
                    [
                        f"- Latest repeat50 packet: `{item['latest_repeat50_packet']}`",
                        f"- Latest repeat50 status: `{item['latest_repeat50_status']}`",
                        f"- Latest repeat50 review request: `{item['latest_repeat50_review_request']}`",
                        f"- Latest repeat50 review blocked record: `{item['latest_repeat50_review_blocked_record']}`",
                    ]
                    if "latest_repeat50_packet" in item and "active_candidate_packet" not in item
                    else []
                ),
                *(
                    [
                        f"- Active candidate packet: `{item['active_candidate_packet']}`",
                        f"- Active candidate status: `{item['active_candidate_status']}`",
                        *(
                            [
                                f"- Latest evidence packet: `{item['latest_evidence_packet']}`",
                                *(
                                    [f"- Latest evidence JSON: `{item['latest_evidence_json']}`"]
                                    if "latest_evidence_json" in item
                                    else []
                                ),
                                f"- Latest evidence status: `{item['latest_evidence_status']}`",
                                *(
                                    [
                                        f"- Latest raw oracle packet: `{item['latest_raw_oracle_packet']}`",
                                        f"- Latest raw oracle status: `{item['latest_raw_oracle_status']}`",
                                    ]
                                    if "latest_raw_oracle_packet" in item
                                    else []
                                ),
                                *(
                                    [
                                        f"- Latest stability packet: `{item['latest_stability_packet']}`",
                                        f"- Latest stability status: `{item['latest_stability_status']}`",
                                    ]
                                    if "latest_stability_packet" in item
                                    else []
                                ),
                                *(
                                    [
                                        f"- Latest review gate packet: `{item['latest_review_gate_packet']}`",
                                        f"- Latest review gate status: `{item['latest_review_gate_status']}`",
                                    ]
                                    if "latest_review_gate_packet" in item
                                    else []
                                ),
                                *(
                                    [
                                        f"- Latest final review request: `{item['latest_final_review_request']}`",
                                        f"- Latest final review blocked record: `{item['latest_final_review_blocked_record']}`",
                                    ]
                                    if "latest_final_review_request" in item
                                    else []
                                ),
                                *(
                                    [
                                        f"- Latest row-wording gate packet: `{item['latest_row_wording_gate_packet']}`",
                                        f"- Latest row-wording gate status: `{item['latest_row_wording_gate_status']}`",
                                    ]
                                    if "latest_row_wording_gate_packet" in item
                                    else []
                                ),
                                *(
                                    [
                                        f"- Latest methodology packet: `{item['latest_methodology_packet']}`",
                                        f"- Latest methodology status: `{item['latest_methodology_status']}`",
                                    ]
                                    if "latest_methodology_packet" in item
                                    else []
                                ),
                                *(
                                    [
                                        f"- Latest no-go packet: `{item['latest_no_go_packet']}`",
                                        f"- Latest no-go status: `{item['latest_no_go_status']}`",
                                    ]
                                    if "latest_no_go_packet" in item
                                    else []
                                ),
                                *(
                                    [
                                        f"- Latest overhead gate packet: `{item['latest_overhead_gate_packet']}`",
                                        f"- Latest overhead gate status: `{item['latest_overhead_gate_status']}`",
                                    ]
                                    if "latest_overhead_gate_packet" in item
                                    else []
                                ),
                                *(
                                    [
                                        f"- Previous scale evidence packet: `{item['previous_scale_evidence_packet']}`",
                                        f"- Previous scale evidence status: `{item['previous_scale_evidence_status']}`",
                                    ]
                                    if "previous_scale_evidence_packet" in item
                                    else []
                                ),
                                *(
                                    [
                                        f"- Previous query-cache packet: `{item['previous_query_cache_packet']}`",
                                        f"- Previous query-cache status: `{item['previous_query_cache_status']}`",
                                    ]
                                    if "previous_query_cache_packet" in item
                                    else []
                                ),
                                *(
                                    [
                                        f"- Latest repair intake packet: `{item['latest_repair_intake_packet']}`",
                                        f"- Latest repair intake status: `{item['latest_repair_intake_status']}`",
                                    ]
                                    if "latest_repair_intake_packet" in item
                                    else []
                                ),
                                *(
                                    [
                                        f"- Latest repair review gate packet: `{item['latest_repair_review_gate_packet']}`",
                                        f"- Latest repair review gate status: `{item['latest_repair_review_gate_status']}`",
                                    ]
                                    if "latest_repair_review_gate_packet" in item
                                    else []
                                ),
                                *(
                                    [
                                        f"- Latest repair adverse-subset packet: `{item['latest_repair_adverse_subset_packet']}`",
                                        f"- Latest repair adverse-subset status: `{item['latest_repair_adverse_subset_status']}`",
                                    ]
                                    if "latest_repair_adverse_subset_packet" in item
                                    else []
                                ),
                                *(
                                    [
                                        f"- Previous evidence packet: `{item['previous_evidence_packet']}`",
                                        f"- Previous evidence status: `{item['previous_evidence_status']}`",
                                    ]
                                    if "previous_evidence_packet" in item
                                    else []
                                ),
                                *(
                                    [
                                        f"- Rejected probe log: `{item['rejected_probe_log']}`",
                                        f"- Rejected probe status: `{item['rejected_probe_status']}`",
                                    ]
                                    if "rejected_probe_log" in item
                                    else []
                                ),
                            ]
                            if "latest_evidence_packet" in item
                            else []
                        ),
                        *(
                            [f"- Active candidate consensus: `{item['active_candidate_consensus']}`"]
                            if "active_candidate_consensus" in item
                            else []
                        ),
                        *(
                            [
                                f"- Active POD runner: `{item['active_pod_runner']}`",
                                f"- Active POD runner status: `{item['active_pod_runner_status']}`",
                            ]
                            if "active_pod_runner" in item
                            else []
                        ),
                    ]
                    if "active_candidate_packet" in item
                    else []
                ),
                *(
                    [
                        f"- Active candidate status: `{item['active_candidate_status']}`",
                    ]
                    if "active_candidate_status" in item and "active_candidate_packet" not in item
                    else []
                ),
                *(
                    [
                        f"- Active POD runner: `{item['active_pod_runner']}`",
                        f"- Active POD runner status: `{item['active_pod_runner_status']}`",
                    ]
                    if "active_pod_runner" in item and "active_candidate_packet" not in item
                    else []
                ),
                f"- Forbidden shortcut: {item['forbidden_shortcut']}",
                "",
            ]
        )
    lines.extend(["## Pending External Review Candidates", ""])
    pending = payload.get("pending_external_review_candidates", [])
    if pending:
        for item in pending:
            lines.extend(
                [
                    f"### {item['id']}",
                    "",
                    f"- Generic capability: `{item['generic_capability']}`",
                    f"- Refined capability: `{item['refined_generic_capability']}`",
                    f"- Candidate row id: `{item['candidate_row_id']}`",
                    f"- Candidate status: `{item['candidate_status']}`",
                    f"- Candidate packet: `{item['candidate_packet']}`",
                    f"- Same-basis no-go packet: `{item['same_basis_no_go_packet']}`",
                    f"- Review request: `{item['review_request']}`",
                    f"- Claude blocked record: `{item['claude_blocked_record']}`",
                    f"- Claude retry blocked record: `{item['claude_retry_blocked_record']}`",
                    f"- Candidate M7 contribution if external review approves: {item['candidate_m7_contribution_if_external_review_approves']}",
                    f"- M7 rows added now: {item['m7_rows_added_now']}",
                    f"- Next action: {item['next_action']}",
                    f"- Forbidden shortcut: {item['forbidden_shortcut']}",
                    "",
                ]
            )
    else:
        lines.extend(["- none", ""])

    lines.extend(["## Accepted With Boundary Candidates", ""])
    accepted = payload.get("accepted_with_boundary_candidates", [])
    if accepted:
        for item in accepted:
            lines.extend(
                [
                    f"### {item['id']}",
                    "",
                    f"- Generic capability: `{item['generic_capability']}`",
                    f"- Refined capability: `{item['refined_generic_capability']}`",
                    f"- Candidate row id: `{item['candidate_row_id']}`",
                    f"- Candidate status: `{item['candidate_status']}`",
                    f"- Candidate packet: `{item['candidate_packet']}`",
                    f"- Same-basis no-go packet: `{item['same_basis_no_go_packet']}`",
                    f"- Review request: `{item['review_request']}`",
                    f"- External review: `{item['external_review']}`",
                    f"- Codex consensus: `{item['codex_consensus']}`",
                    f"- Historical blocked record: `{item['historical_blocked_record']}`",
                    f"- Candidate M7 contribution if P1 default-path review approves: {item['candidate_m7_contribution_if_p1_default_path_review_approves']}",
                    f"- M7 rows added now: {item['m7_rows_added_now']}",
                    f"- Next action: {item['next_action']}",
                    f"- Forbidden shortcut: {item['forbidden_shortcut']}",
                    "",
                ]
            )
    else:
        lines.extend(["- none", ""])

    lines.extend(
        [
            "## Future Research Records",
            "",
            "These items are tracked so old work is not lost, but they are not active Phoenix V3 P0 build targets.",
            "",
        ]
    )
    for item in payload["future_generic_engine_work"]:
        lines.extend(
            [
                f"### {item['id']}",
                "",
                f"- Priority: `{item['priority']}`",
                f"- Generic capability: `{item['generic_capability']}`",
                f"- Apps used as evidence: `{', '.join(item['apps_used_as_evidence'])}`",
                f"- Current state: {item['current_state']}",
                f"- Generic engine action: {item['generic_engine_action']}",
                f"- Evidence to reopen M7: {item['evidence_to_reopen_m7']}",
                f"- Active candidate packet: `{item['active_candidate_packet']}`",
                f"- Active candidate status: `{item['active_candidate_status']}`",
                *(
                    [f"- M129 wrapper gate: `{item['m129_wrapper_gate']}`"]
                    if "m129_wrapper_gate" in item
                    else []
                ),
                *(
                    [f"- M131 semantic gate: `{item['m131_semantic_gate']}`"]
                    if "m131_semantic_gate" in item
                    else []
                ),
                *(
                    [f"- M142 closure gate: `{item['m142_closure_gate']}`"]
                    if "m142_closure_gate" in item
                    else []
                ),
                *(
                    [f"- Closed by external review: `{item['closed_by_external_review']}`"]
                    if "closed_by_external_review" in item
                    else []
                ),
                *(
                    [f"- Closed by consensus: `{item['closed_by_consensus']}`"]
                    if "closed_by_consensus" in item
                    else []
                ),
                *(
                    [
                        f"- Latest prefilter-zero packet: `{item['latest_prefilter_zero_packet']}`",
                        f"- Latest prefilter-zero status: `{item['latest_prefilter_zero_status']}`",
                        (
                            "- Latest prefilter-zero stable prepared query: "
                            f"{item['latest_prefilter_zero_prepared_query_ms']:.6f} ms"
                        ),
                        (
                            "- Latest prefilter-zero speedup vs old legal RTDL route: "
                            f"{item['latest_prefilter_zero_speedup_vs_old_best']:.3f}x"
                        ),
                        (
                            "- Latest prefilter-zero author speedup vs RTDL: "
                            f"{item['latest_prefilter_zero_author_speedup_vs_rtdl']:.3f}x"
                        ),
                        (
                            "- Latest prefilter-zero remaining author gap: "
                            f"{item['latest_prefilter_zero_gap_to_author_ms']:.6f} ms"
                        ),
                    ]
                    if "latest_prefilter_zero_packet" in item
                    else []
                ),
                *(
                    [
                        (
                            "- Latest count-only/no-diagnostics no-go packet: "
                            f"`{item['latest_count_only_no_diagnostics_no_go_packet']}`"
                        ),
                        (
                            "- Latest count-only/no-diagnostics status: "
                            f"`{item['latest_count_only_no_diagnostics_no_go_status']}`"
                        ),
                        (
                            "- Latest count-only/no-diagnostics prepared query: "
                            f"{item['latest_count_only_no_diagnostics_prepared_query_ms']:.6f} ms"
                        ),
                        (
                            "- Latest count-only/no-diagnostics delta vs diagnostic: "
                            f"+{item['latest_count_only_no_diagnostics_delta_ms']:.6f} ms"
                        ),
                        (
                            "- Latest count-only/no-diagnostics source retained: "
                            f"{str(item['latest_count_only_no_diagnostics_source_retained']).lower()}"
                        ),
                    ]
                    if "latest_count_only_no_diagnostics_no_go_packet" in item
                    else []
                ),
                *(
                    [
                        (
                            "- Latest guarded squared-boundary candidate packet: "
                            f"`{item['latest_squared_boundary_candidate_packet']}`"
                        ),
                        (
                            "- Latest guarded squared-boundary status: "
                            f"`{item['latest_squared_boundary_candidate_status']}`"
                        ),
                        (
                            "- Latest guarded squared-boundary prepared query: "
                            f"{item['latest_squared_boundary_prepared_query_ms']:.6f} ms"
                        ),
                        (
                            "- Latest guarded squared-boundary speedup vs prefilter-zero: "
                            f"{item['latest_squared_boundary_speedup_vs_prefilter_zero']:.3f}x"
                        ),
                        (
                            "- Latest guarded squared-boundary speedup vs author Query: "
                            f"{item['latest_squared_boundary_speedup_vs_author_query']:.3f}x"
                        ),
                        (
                            "- Latest guarded squared-boundary margin under author Query: "
                            f"{item['latest_squared_boundary_author_margin_ms']:.6f} ms"
                        ),
                        (
                            "- Latest guarded squared-boundary M7 candidate: "
                            f"{str(item['latest_squared_boundary_m7_candidate']).lower()}"
                        ),
                        (
                            "- Latest guarded squared-boundary M7 promotion authorized: "
                            f"{str(item['latest_squared_boundary_m7_promotion_authorized']).lower()}"
                        ),
                        (
                            "- Latest guarded squared-boundary predicate mismatches: "
                            f"{item['latest_squared_boundary_guarded_mismatch_count']}"
                        ),
                        (
                            "- Latest pure squared predicate mismatches recorded: "
                            f"{item['latest_squared_boundary_pure_mismatch_count']}"
                        ),
                    ]
                    if "latest_squared_boundary_candidate_packet" in item
                    else []
                ),
                *(
                    [
                        f"- Full-scale overlay active-count no-go packet: `{item['full_scale_overlay_active_count_no_go_packet']}`",
                        f"- Full-scale overlay active-count no-go status: `{item['full_scale_overlay_active_count_no_go_status']}`",
                        f"- Full-scale overlay active-count no-go review request: `{item['full_scale_overlay_active_count_no_go_review_request']}`",
                        (
                            "- Full-scale overlay active-count mismatch: "
                            f"{item['full_scale_overlay_active_count_optix_count']:,} != "
                            f"{item['full_scale_overlay_active_count_embree_count']:,} "
                            f"(delta {item['full_scale_overlay_active_count_delta']:,})"
                        ),
                        (
                            "- Full-scale overlay shape-pairs: "
                            f"{item['full_scale_overlay_active_count_shape_pair_count']:,}"
                        ),
                        (
                            "- Full-scale overlay timed-median ratio rejected: "
                            f"{item['full_scale_overlay_active_count_timed_median_ratio']:.3f}x"
                        ),
                    ]
                    if "full_scale_overlay_active_count_no_go_packet" in item
                    else []
                ),
                *([f"- M7 rows added: {item['m7_rows_added']}"] if "m7_rows_added" in item else []),
                f"- Forbidden shortcut: {item['forbidden_shortcut']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Release Blockers Outside This Queue",
            "",
        ]
    )
    for blocker in payload["release_blockers_outside_engine_queue"]:
        lines.append(f"- `{blocker}`")

    audit = payload["decision_audit"]
    lines.extend(
        [
            "",
            "## Goal-Level Decision Audit",
            "",
            f"Decision: {audit['decision']}",
            "",
            "1. Was I foolish?",
            f"   {audit['was_i_foolish']}",
            "2. If yes, what actions made the decision foolish?",
            f"   {audit['foolish_actions']}",
            "3. Was there another path that would have avoided getting stuck on that idea?",
            f"   {audit['other_path']}",
            "4. Can I now try a different path that actually solves the problem?",
            f"   {audit['different_path_now']}",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Emit the Phoenix V3 next generic-engine work queue.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    text = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        args.md_out.write_text(_render_markdown(payload), encoding="utf-8")
    print(text)
    return 0 if payload["status"] in {
        "active_generic_engine_work_queue_not_release",
        "generic_engine_work_queue_closed_not_release",
    } else 2


if __name__ == "__main__":
    raise SystemExit(main())
