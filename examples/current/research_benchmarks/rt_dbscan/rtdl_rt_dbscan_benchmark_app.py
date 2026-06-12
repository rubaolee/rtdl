from __future__ import annotations

from contextlib import nullcontext
import argparse
import json
import math
import random
import statistics
import sys
import time
from pathlib import Path
from typing import Iterable

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


NOISE_CLUSTER_ID = -1
DEFAULT_DATASET_CONFIG = {
    "tiny": {"point_count": 9, "radius": 0.20, "min_neighbors": 3},
    "clustered3d": {"point_count": 512, "radius": 0.055, "min_neighbors": 12},
    "road3d": {"point_count": 512, "radius": 0.030, "min_neighbors": 8},
    "ngsim_dense": {"point_count": 512, "radius": 0.012, "min_neighbors": 20},
}
DEFAULT_DIRECTED_ADJACENCY_EDGE_BUDGET = 160_000_000
DEFAULT_BLOCKED_GROUPED_SEGMENT_TARGET_HITS = 8_000_000
DEFAULT_GROUPED_UNION_QUERY_BLOCK_SIZE = 8192
RT_DBSCAN_GROUPED_STREAM_TIMING_BREAKDOWN_SCHEMA = "rt_dbscan_grouped_stream_host_overhead_breakdown_v1"
DIRECTED_ADJACENCY_INDEX_BYTES = 4
DIRECTED_ADJACENCY_OFFSET_BYTES = 8
RT_DBSCAN_TESTED_DIRECT_STATUS_PARTITION_CELL_FACTOR_OPTIONS = {
    "clustered3d": (
        {"point_count": 65536, "factor": 0.25, "replay_speedup": 2.961, "one_shot_total_speedup": 2.506, "evidence_refs": ("Goal4117", "Goal4130")},
        {"point_count": 131072, "factor": 0.25, "replay_speedup": 3.211, "one_shot_total_speedup": 3.110, "evidence_refs": ("Goal4122", "Goal4130")},
        {"point_count": 262144, "factor": 0.25, "replay_speedup": 3.118, "one_shot_total_speedup": 3.192, "evidence_refs": ("Goal4126", "Goal4130")},
        {"point_count": 524288, "factor": 0.25, "replay_speedup": 3.291, "one_shot_total_speedup": 3.250, "evidence_refs": ("Goal4134",)},
        {"point_count": 1048576, "factor": 0.25, "replay_speedup": 3.430, "one_shot_total_speedup": 3.383, "evidence_refs": ("Goal4138",)},
    ),
    "road3d": (
        {"point_count": 65536, "factor": 0.25, "replay_speedup": 1.866, "one_shot_total_speedup": 2.609, "evidence_refs": ("Goal4117", "Goal4130")},
        {"point_count": 131072, "factor": 0.25, "replay_speedup": 1.545, "one_shot_total_speedup": 2.606, "evidence_refs": ("Goal4122", "Goal4130")},
        {"point_count": 262144, "factor": 0.25, "replay_speedup": 1.428, "one_shot_total_speedup": 2.272, "evidence_refs": ("Goal4126", "Goal4130")},
        {"point_count": 524288, "factor": 0.25, "replay_speedup": 1.367, "one_shot_total_speedup": 1.910, "evidence_refs": ("Goal4134",)},
        {"point_count": 1048576, "factor": 0.25, "replay_speedup": 1.396, "one_shot_total_speedup": 1.705, "evidence_refs": ("Goal4138",)},
    ),
    "ngsim_dense": (
        {"point_count": 65536, "factor": 0.25, "replay_speedup": 0.969, "one_shot_total_speedup": 3.679, "evidence_refs": ("Goal4130",)},
        {"point_count": 65536, "factor": 0.5, "replay_speedup": 1.312, "one_shot_total_speedup": 1.819, "evidence_refs": ("Goal4117", "Goal4130")},
        {"point_count": 131072, "factor": 0.25, "replay_speedup": 1.399, "one_shot_total_speedup": 3.410, "evidence_refs": ("Goal4122", "Goal4130")},
        {"point_count": 262144, "factor": 0.25, "replay_speedup": 1.642, "one_shot_total_speedup": 2.939, "evidence_refs": ("Goal4126", "Goal4130")},
        {"point_count": 524288, "factor": 0.25, "replay_speedup": 1.769, "one_shot_total_speedup": 2.489, "evidence_refs": ("Goal4134",)},
        {"point_count": 1048576, "factor": 0.25, "replay_speedup": 1.790, "one_shot_total_speedup": 2.432, "evidence_refs": ("Goal4138",)},
    ),
}
RT_DBSCAN_TESTED_DIRECT_STATUS_SINGLE_PASS_CONVERGENCE_OPTIONS = {
    ("clustered3d", 65536, 0.25): {"replay_speedup_vs_until_stable": 1.945, "total_speedup_vs_until_stable": 8.851, "evidence_refs": ("Goal4150",)},
    ("road3d", 65536, 0.25): {"replay_speedup_vs_until_stable": 2.017, "total_speedup_vs_until_stable": 1.654, "evidence_refs": ("Goal4150",)},
    ("ngsim_dense", 65536, 0.25): {"replay_speedup_vs_until_stable": 1.944, "total_speedup_vs_until_stable": 1.111, "evidence_refs": ("Goal4150",)},
    ("clustered3d", 131072, 0.25): {"replay_speedup_vs_until_stable": 2.121, "total_speedup_vs_until_stable": 1.308, "evidence_refs": ("Goal4150",)},
    ("road3d", 131072, 0.25): {"replay_speedup_vs_until_stable": 2.069, "total_speedup_vs_until_stable": 1.255, "evidence_refs": ("Goal4150",)},
    ("ngsim_dense", 131072, 0.25): {"replay_speedup_vs_until_stable": 1.849, "total_speedup_vs_until_stable": 1.117, "evidence_refs": ("Goal4150",)},
    ("clustered3d", 262144, 0.25): {"replay_speedup_vs_until_stable": 2.046, "total_speedup_vs_until_stable": 1.506, "evidence_refs": ("Goal4150",)},
    ("road3d", 262144, 0.25): {"replay_speedup_vs_until_stable": 2.102, "total_speedup_vs_until_stable": 1.502, "evidence_refs": ("Goal4150",)},
    ("ngsim_dense", 262144, 0.25): {"replay_speedup_vs_until_stable": 1.996, "total_speedup_vs_until_stable": 1.176, "evidence_refs": ("Goal4150",)},
    ("clustered3d", 524288, 0.25): {"replay_speedup_vs_until_stable": 2.076, "total_speedup_vs_until_stable": 1.659, "evidence_refs": ("Goal4150",)},
    ("road3d", 524288, 0.25): {"replay_speedup_vs_until_stable": 2.086, "total_speedup_vs_until_stable": 1.681, "evidence_refs": ("Goal4150",)},
    ("ngsim_dense", 524288, 0.25): {"replay_speedup_vs_until_stable": 2.010, "total_speedup_vs_until_stable": 1.218, "evidence_refs": ("Goal4150",)},
    ("clustered3d", 1048576, 0.25): {"replay_speedup_vs_until_stable": 1.987, "total_speedup_vs_until_stable": 1.857, "evidence_refs": ("Goal4149",)},
    ("road3d", 1048576, 0.25): {"replay_speedup_vs_until_stable": 2.080, "total_speedup_vs_until_stable": 1.817, "evidence_refs": ("Goal4149",)},
    ("ngsim_dense", 1048576, 0.25): {"replay_speedup_vs_until_stable": 2.010, "total_speedup_vs_until_stable": 1.381, "evidence_refs": ("Goal4149",)},
}
RT_DBSCAN_DIRECT_STATUS_APP_MODE = "partner_cupy_prepared_direct_status_union_component_signature_3d"
RT_DBSCAN_GROUPED_STREAM_NUMBA_APP_MODE = "optix_rt_core_grouped_stream_numba_column_signature_3d"
RT_DBSCAN_PREDICATE_DIRECT_STATUS_APP_MODE = (
    "optix_rt_core_flags_cupy_predicate_direct_status_column_signature_3d"
)
RT_DBSCAN_PREDICATE_DIRECT_STATUS_ALL_TRUE_APP_MODE = (
    "optix_rt_core_flags_cupy_predicate_direct_status_all_true_column_signature_3d"
)
RT_DBSCAN_DECLARED_ALL_TRUE_DIRECT_STATUS_APP_MODE = (
    "partner_cupy_declared_all_true_predicate_direct_status_column_signature_3d"
)


def estimate_rt_dbscan_directed_adjacency_edges(dataset: str, point_count: int) -> int:
    """Return an evidence-bounded estimate for directed fixed-radius adjacency size."""
    point_count = int(point_count)
    if point_count < 1:
        raise ValueError("point_count must be positive")
    if dataset == "tiny":
        return 33
    if dataset == "clustered3d":
        return max(point_count, int(round(0.126 * point_count * point_count)))
    if dataset == "road3d":
        return max(point_count, int(round(0.018 * point_count * point_count)))
    if dataset == "ngsim_dense":
        return max(point_count, int(round(0.055 * point_count * point_count)))
    raise ValueError("dataset must be tiny, clustered3d, road3d, or ngsim_dense")


def _estimated_directed_adjacency_bytes(point_count: int, directed_edges: int) -> int:
    return (
        int(directed_edges) * DIRECTED_ADJACENCY_INDEX_BYTES
        + (int(point_count) + 1) * DIRECTED_ADJACENCY_OFFSET_BYTES
    )


def plan_rt_dbscan_execution(dataset: str, point_count: int) -> dict[str, object]:
    """Return an explicit benchmark-app plan from the current reviewed evidence."""
    point_count = int(point_count)
    current_route_advisor = None
    if dataset == "tiny":
        selected_mode = "cpu_reference"
        reason = "tiny correctness fixture; no GPU performance claim"
    elif dataset == "ngsim_dense":
        selected_mode = "partner_cupy_prepared_grid_components_3d"
        reason = "Goal2425 showed compact ngsim_dense rows favor the prepared pure-CuPy continuation through 262k"
        current_route_advisor = explain_rt_dbscan_explicit_route_choice(
            dataset,
            repeated_component_signature=False,
            point_count=point_count,
        )
    elif dataset == "road3d" and point_count < 524288:
        selected_mode = "partner_cupy_prepared_grid_components_3d"
        reason = "Goal2425 showed road3d favors the prepared pure-CuPy continuation below the 524k crossover"
        current_route_advisor = explain_rt_dbscan_explicit_route_choice(
            dataset,
            repeated_component_signature=False,
            point_count=point_count,
        )
    elif dataset == "clustered3d" and point_count < 65536:
        selected_mode = "partner_cupy_prepared_grid_components_3d"
        reason = "Goal2425 showed clustered3d needs at least the 65k scale before prepared RT wins over prepared pure CuPy"
        current_route_advisor = explain_rt_dbscan_explicit_route_choice(
            dataset,
            repeated_component_signature=False,
            point_count=point_count,
        )
    else:
        selected_mode = "optix_rt_core_flags_cupy_prepared_grid_components_3d"
        reason = "Goal2425 showed prepared RT-count plus prepared CuPy grid wins for this measured scale/shape"
        current_route_advisor = explain_rt_dbscan_explicit_route_choice(
            dataset,
            repeated_component_signature=False,
            point_count=point_count,
        )
    current_route_first_option = None
    if current_route_advisor is not None and current_route_advisor["options"]:
        current_route_first_option = current_route_advisor["options"][0]
    return {
        "adapter": "plan_rt_dbscan_execution",
        "selected_mode": selected_mode,
        "reason": reason,
        "policy": "explicit_benchmark_plan_from_goal2425_prepared_fairness_evidence",
        "legacy_plan_compatibility_mode": True,
        "current_route_guidance_source": "explain_rt_dbscan_explicit_route_choice_goal4151",
        "current_route_advisor": current_route_advisor,
        "current_route_first_option": current_route_first_option,
        "selected_mode_boundary": (
            "planned_rt_dbscan remains a legacy compatibility execution mode from Goal2425. "
            "Use current_route_advisor for current explicit user-selected route and factor guidance; "
            "the legacy plan does not auto-select partition-cell factors from the advisor."
        ),
        "not_hidden_dispatcher": True,
        "hidden_dispatch_allowed": False,
        "automatic_partner_selection_authorized": False,
        "automatic_partition_cell_factor_selection_authorized": False,
        "release_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
    }


def explain_rt_dbscan_explicit_route_choice(
    dataset: str,
    *,
    repeated_component_signature: bool,
    point_count: int | None = None,
) -> dict[str, object]:
    """Explain current explicit RT-DBSCAN route choices without dispatching."""

    if dataset not in DEFAULT_DATASET_CONFIG:
        raise ValueError("dataset must be tiny, clustered3d, road3d, or ngsim_dense")
    repeated = bool(repeated_component_signature)
    resolved_point_count = None if point_count is None else int(point_count)
    if resolved_point_count is not None and resolved_point_count < 1:
        raise ValueError("point_count must be positive when provided")
    default_option = {
        "mode": RT_DBSCAN_GROUPED_STREAM_NUMBA_APP_MODE,
        "partner": "numba",
        "partition_cell_factor": None,
        "when": "conservative one-shot/default component-signature route",
        "predicate_mix_boundary": (
            "recommended for custom radius/min-neighbor settings that produce mixed predicate flags "
            "unless the caller explicitly accepts a different policy-aware semantic contract"
        ),
        "border_assignment_policy": "one_predicate_true_neighbor_candidate_per_predicate_false_item_captured_during_rt_pass",
        "canonical_component_size_signature_comparison": True,
        "policy_aware_semantic_signature_comparison": True,
        "evidence_refs": (
            "Goal3859",
            "Goal3936",
            "Goal4100",
            "Goal4115",
            "Goal4118",
            "Goal4159",
            "Goal4160",
            "Goal4165",
            "Goal4166",
        ),
    }
    options: list[dict[str, object]] = [default_option]
    if dataset in RT_DBSCAN_TESTED_DIRECT_STATUS_PARTITION_CELL_FACTOR_OPTIONS:
        tested_options = list(RT_DBSCAN_TESTED_DIRECT_STATUS_PARTITION_CELL_FACTOR_OPTIONS[dataset])
        metric_key = "replay_speedup" if repeated else "one_shot_total_speedup"
        if resolved_point_count is not None:
            tested_options.sort(
                key=lambda row: (
                    abs(int(row["point_count"]) - resolved_point_count),
                    -float(row[metric_key]),
                    float(row["factor"]),
                )
            )
        else:
            tested_options.sort(key=lambda row: (int(row["point_count"]), -float(row[metric_key]), float(row["factor"])))
        direct_options = []
        all_true_options = []
        declared_all_true_options = []
        for tested in tested_options:
            all_true_option = {
                "mode": RT_DBSCAN_PREDICATE_DIRECT_STATUS_ALL_TRUE_APP_MODE,
                "partner": "cupy",
                "partition_cell_factor": float(tested["factor"]),
                "tested_point_count": int(tested["point_count"]),
                "when": (
                    "explicit all-predicate fast path for rows whose threshold predicate is known "
                    "or measured to be all true"
                ),
                "all_predicate_fast_path_required": True,
                "mixed_predicate_fail_closed": True,
                "mixed_predicate_fallback_route": RT_DBSCAN_GROUPED_STREAM_NUMBA_APP_MODE,
                "border_assignment_policy": "not_needed_all_predicate_true",
                "border_assignment_policy_status": (
                    "mixed predicates are rejected instead of using the current lowest-id border policy"
                ),
                "evidence_refs": (
                    "Goal4158",
                    "Goal4159",
                    "Goal4160",
                    "Goal4162",
                ),
            }
            declared_all_true_option = {
                "mode": RT_DBSCAN_DECLARED_ALL_TRUE_DIRECT_STATUS_APP_MODE,
                "partner": "cupy",
                "partition_cell_factor": float(tested["factor"]),
                "tested_point_count": int(tested["point_count"]),
                "when": (
                    "explicit caller-declared all-predicate route for rows whose predicate flags "
                    "are externally proven all true"
                ),
                "predicate_flags_source": "caller_declared_all_true",
                "caller_declared_predicate_columns_require_external_proof": True,
                "rt_count_threshold_executed": False,
                "rt_core_acceleration_claim_authorized": False,
                "mixed_predicate_fail_closed": True,
                "mixed_predicate_fallback_route": RT_DBSCAN_GROUPED_STREAM_NUMBA_APP_MODE,
                "border_assignment_policy": "not_needed_all_predicate_true",
                "automatic_route_selection_authorized": False,
                "route_promotion_authorized": False,
                "evidence_refs": (
                    "Goal4172",
                    "Goal4173",
                ),
            }
            direct_option = {
                "mode": RT_DBSCAN_DIRECT_STATUS_APP_MODE,
                "predicate_direct_status_candidate_mode": RT_DBSCAN_PREDICATE_DIRECT_STATUS_APP_MODE,
                "partner": "cupy",
                "partition_cell_factor": float(tested["factor"]),
                "tested_point_count": int(tested["point_count"]),
                "replay_speedup_vs_current": float(tested["replay_speedup"]),
                "one_shot_total_speedup_vs_current": float(tested["one_shot_total_speedup"]),
                "direct_status_convergence_mode": "until_stable",
                "direct_status_convergence_mode_status": "stable_convergence_proven_default",
                "predicate_scope": (
                    "proven for the default benchmark predicate shape; custom mixed-predicate overrides "
                    "remain blocked unless the caller chooses a policy-aware semantic contract; "
                    "they are not broadly faster in Goal4165"
                ),
                "all_predicate_fast_path_evidence": "Goal4158",
                "border_assignment_policy": "lowest_predicate_true_point_id_within_radius",
                "border_assignment_policy_status": (
                    "explicit metadata only; reference_grouped_stream_compatible policy not implemented"
                ),
                "canonical_component_size_signature_comparison": True,
                "policy_aware_semantic_signature_comparison": True,
                "mixed_predicate_performance_status": (
                    "Goal4165 shows the candidate is not broadly faster on sparse mixed rows"
                ),
                "when": (
                    "explicit repeated component-signature route over reused point/partition columns"
                    if repeated
                    else "explicit warmed one-shot component-signature route with prepare paid once"
                ),
                "evidence_refs": (
                    "Goal4116",
                    "Goal4118",
                    "Goal4158",
                    "Goal4159",
                    "Goal4160",
                    "Goal4161",
                    "Goal4162",
                    "Goal4165",
                    "Goal4166",
                    *tuple(tested["evidence_refs"]),
                ),
            }
            single_pass = RT_DBSCAN_TESTED_DIRECT_STATUS_SINGLE_PASS_CONVERGENCE_OPTIONS.get(
                (dataset, int(tested["point_count"]), float(tested["factor"]))
            )
            if single_pass is not None:
                direct_option.update(
                    {
                        "direct_status_convergence_mode": "single_pass_candidate",
                        "direct_status_convergence_mode_status": (
                            "explicit_user_selected_same_signature_candidate_not_default"
                        ),
                        "single_pass_same_signature_vs_until_stable": True,
                        "single_pass_replay_speedup_vs_until_stable": float(
                            single_pass["replay_speedup_vs_until_stable"]
                        ),
                        "single_pass_total_speedup_vs_until_stable": float(
                            single_pass["total_speedup_vs_until_stable"]
                        ),
                        "single_pass_promoted_default": False,
                        "single_pass_evidence_refs": tuple(single_pass["evidence_refs"]),
                    }
                )
            direct_options.append(direct_option)
            all_true_options.append(all_true_option)
            declared_all_true_options.append(declared_all_true_option)
        options = direct_options + all_true_options + options
        options.extend(declared_all_true_options)
    elif repeated:
        options.append(
            {
                "mode": RT_DBSCAN_DIRECT_STATUS_APP_MODE,
                "partner": "cupy",
                "partition_cell_factor": None,
                "when": "requires new same-contract factor evidence for this dataset",
                "evidence_refs": ("Goal4118",),
            }
        )
    return {
        "adapter": "explain_rt_dbscan_explicit_route_choice",
        "dataset": dataset,
        "repeated_component_signature": repeated,
        "point_count": resolved_point_count,
        "status": "advisory_only_no_dispatch",
        "user_must_select_route": True,
        "automatic_dispatch_authorized": False,
        "automatic_partner_selection_authorized": False,
        "automatic_partition_cell_factor_selection_authorized": False,
        "automatic_convergence_mode_selection_authorized": False,
        "hidden_dispatch_allowed": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "native_dbscan_abi_added": False,
        "app_specific_engine_logic_allowed": False,
        "canonical_component_size_signature_helper": "canonical_component_size_signature",
        "policy_aware_semantic_signature_helper": "policy_aware_rt_dbscan_semantic_signature",
        "mixed_predicate_comparison_contracts": (
            "policy_bound_component_sizes",
            "core_noise_assigned_counts_only",
        ),
        "mixed_predicate_policy_probe": "Goal4165",
        "mixed_predicate_policy_aware_contract": "Goal4166",
        "mixed_predicate_performance_status": (
            "policy-aware counts-only semantics can pass even when component-size policy differs, "
            "but predicate direct-status is not promoted for mixed rows because Goal4165 does not "
            "show broad performance advantage"
        ),
        "mixed_predicate_route_promotion_blocked_by": ("Goal4159", "Goal4160"),
        "current_predicate_border_assignment_policy": "lowest_predicate_true_point_id_within_radius",
        "target_predicate_border_assignment_policy": "reference_grouped_stream_compatible",
        "claim_boundary": (
            "Advisory RT-DBSCAN route explanation only. It does not execute a route, "
            "choose a partner automatically, choose a partition cell factor automatically, "
            "choose a convergence mode automatically, authorize release, authorize public "
            "speedup wording, authorize broad RT-core wording, or add app-specific engine logic."
        ),
        "options": tuple(options),
    }


def plan_rt_dbscan_continuation_execution(
    dataset: str,
    point_count: int,
    *,
    directed_edge_budget: int | None = None,
) -> dict[str, object]:
    """Plan the explicit adjacency-continuation contract for RT-DBSCAN experiments."""
    point_count = int(point_count)
    edge_budget = int(
        DEFAULT_DIRECTED_ADJACENCY_EDGE_BUDGET
        if directed_edge_budget is None
        else directed_edge_budget
    )
    if edge_budget < 1:
        raise ValueError("directed_edge_budget must be positive")
    estimated_edges = estimate_rt_dbscan_directed_adjacency_edges(dataset, point_count)
    estimated_bytes = _estimated_directed_adjacency_bytes(point_count, estimated_edges)
    full_stream_fits_budget = estimated_edges <= edge_budget

    if dataset == "tiny":
        selected_mode = "cpu_reference"
        reason = "tiny correctness fixture; no GPU continuation plan is needed"
    elif full_stream_fits_budget:
        selected_mode = "optix_rt_core_adjacency_cupy_components_3d"
        reason = (
            "estimated directed adjacency stream fits the explicit budget; "
            "Goal2431/2435/2452/2457 evidence says the full stream is faster than chunked or grouped when it fits"
        )
    else:
        selected_mode = "optix_rt_core_grouped_stream_cupy_components_3d"
        reason = (
            "estimated directed adjacency stream exceeds the explicit budget; "
            "Goal2457/2461/2463/2465/2475/2476 evidence says the grouped stream avoids the giant "
            "neighbor-index table, reuses prepared device search points, reduces avoidable anyhit work, "
            "and beats chunked continuation for the measured dense branch"
        )
    return {
        "adapter": "plan_rt_dbscan_continuation_execution",
        "selected_mode": selected_mode,
        "reason": reason,
        "policy": (
            "explicit_continuation_plan_from_goal2431_2433_2435_2452_2457_2461_2463_2465_2475_2476_evidence"
        ),
        "evidence_goals": [
            "Goal2431",
            "Goal2433",
            "Goal2435",
            "Goal2452",
            "Goal2457",
            "Goal2461",
            "Goal2463",
            "Goal2465",
            "Goal2475",
            "Goal2476",
        ],
        "estimated_directed_edge_count": estimated_edges,
        "directed_edge_budget": edge_budget,
        "estimated_full_adjacency_bytes": estimated_bytes,
        "full_stream_fits_budget": full_stream_fits_budget,
        "planner_surface": "benchmark_app_plan_explain_not_engine_dispatch",
        "not_hidden_dispatcher": True,
        "release_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
    }


def plan_rt_dbscan_blocked_grouped_continuation_design(
    dataset: str,
    point_count: int,
    *,
    segment_target_hits: int = DEFAULT_BLOCKED_GROUPED_SEGMENT_TARGET_HITS,
) -> dict[str, object]:
    """Return the Goal2467 non-executable design plan for blocked grouped union.

    This is deliberately not a runtime dispatcher. It records the next generic
    primitive shape and a sizing estimate so native work can be reviewed before
    implementation and pod timing.
    """
    point_count = int(point_count)
    segment_target_hits = int(segment_target_hits)
    if segment_target_hits < 1:
        raise ValueError("segment_target_hits must be positive")
    estimated_edges = estimate_rt_dbscan_directed_adjacency_edges(dataset, point_count)
    estimated_segments = max(1, math.ceil(estimated_edges / segment_target_hits))
    return {
        "adapter": "plan_rt_dbscan_blocked_grouped_continuation_design",
        "design_status": "needs-more-evidence",
        "runtime_executable": False,
        "selected_mode": "design_only_generic_blocked_grouped_stream_candidate",
        "target_primitive": "generic_fixed_radius_blocked_grouped_component_continuation_3d",
        "candidate_native_contract": "fixed_radius_hit_stream_to_segmented_grouped_union_workspaces",
        "reason": (
            "Goal2461/2463/2465 removed transfer and all-items avoidable anyhit overhead; "
            "the remaining target is generic grouped-union global atomic pressure"
        ),
        "policy": "goal2467_design_only_no_hidden_dispatch_no_native_abi_until_review",
        "evidence_goals": [
            "Goal2457",
            "Goal2459",
            "Goal2461",
            "Goal2463",
            "Goal2465",
        ],
        "estimated_directed_edge_count": estimated_edges,
        "segment_target_hits": segment_target_hits,
        "estimated_segment_count": estimated_segments,
        "app_independent_engine_required": True,
        "forbidden_native_vocabulary": ["dbscan", "cluster", "min_neighbors"],
        "planner_surface": "benchmark_app_design_explain_not_engine_dispatch",
        "not_hidden_dispatcher": True,
        "release_claim_authorized": False,
        "performance_claim_authorized": False,
        "pod_validation_required": True,
    }


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def make_rt_dbscan_points(dataset: str, *, point_count: int, seed: int) -> tuple[rt.Point3D, ...]:
    """Generate deterministic 3-D point fixtures for the RT-DBSCAN study.

    These are paper-inspired stressors, not paper-dataset replacements.
    """
    if point_count < 1:
        raise ValueError("point_count must be positive")
    rng = random.Random(seed)

    if dataset == "tiny":
        base = (
            (0.00, 0.00, 0.00),
            (0.08, 0.04, 0.01),
            (-0.07, 0.05, 0.02),
            (0.04, -0.08, -0.01),
            (0.62, 0.62, 0.04),
            (0.70, 0.66, 0.02),
            (0.58, 0.55, 0.00),
            (0.72, 0.55, 0.03),
            (0.98, 0.04, 0.97),
        )
        return tuple(rt.Point3D(id=index + 1, x=x, y=y, z=z) for index, (x, y, z) in enumerate(base[:point_count]))

    points: list[rt.Point3D] = []
    if dataset == "clustered3d":
        centers = [(0.22, 0.25, 0.30), (0.74, 0.30, 0.25), (0.54, 0.74, 0.72), (0.22, 0.77, 0.42)]
        for index in range(point_count):
            cx, cy, cz = centers[index % len(centers)]
            points.append(
                rt.Point3D(
                    id=index + 1,
                    x=_clamp01(rng.gauss(cx, 0.025)),
                    y=_clamp01(rng.gauss(cy, 0.025)),
                    z=_clamp01(rng.gauss(cz, 0.025)),
                )
            )
    elif dataset == "road3d":
        for index in range(point_count):
            t = (index + 0.5) / point_count
            lane = -0.012 if index % 2 == 0 else 0.012
            points.append(
                rt.Point3D(
                    id=index + 1,
                    x=t,
                    y=_clamp01(0.50 + lane + 0.030 * math.sin(8.0 * math.pi * t) + rng.gauss(0.0, 0.004)),
                    z=_clamp01(0.20 + 0.10 * t + rng.gauss(0.0, 0.006)),
                )
            )
    elif dataset == "ngsim_dense":
        side = max(1, round(point_count ** (1.0 / 3.0)))
        for index in range(point_count):
            ix = index % side
            iy = (index // side) % side
            iz = (index // (side * side)) % side
            points.append(
                rt.Point3D(
                    id=index + 1,
                    x=_clamp01(0.45 + 0.10 * (ix / max(1, side - 1)) + rng.gauss(0.0, 0.0015)),
                    y=_clamp01(0.45 + 0.10 * (iy / max(1, side - 1)) + rng.gauss(0.0, 0.0015)),
                    z=_clamp01(0.45 + 0.10 * (iz / max(1, side - 1)) + rng.gauss(0.0, 0.0015)),
                )
            )
    else:
        raise ValueError("dataset must be tiny, clustered3d, road3d, or ngsim_dense")
    return tuple(points)


def make_fixed_radius_neighbors_3d_embree_kernel(*, radius: float, k_max: int):
    """Build a generic Embree fixed-radius row kernel for the app's chosen radius."""

    @rt.kernel(backend="rtdl", precision="float_approx")
    def _rt_dbscan_fixed_radius_neighbors_3d_embree():
        query_points = rt.input("query_points", rt.Points3D, role="probe")
        search_points = rt.input("search_points", rt.Points3D, role="build")
        candidates = rt.traverse(query_points, search_points, accel="bvh")
        hits = rt.refine(
            candidates,
            predicate=rt.fixed_radius_neighbors(radius=radius, k_max=k_max),
        )
        return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])

    return _rt_dbscan_fixed_radius_neighbors_3d_embree


def fixed_radius_pairs_and_neighbor_counts_3d(
    points: tuple[rt.Point3D, ...],
    *,
    radius: float,
) -> tuple[tuple[tuple[int, int], ...], tuple[int, ...]]:
    """Return undirected fixed-radius pairs and inclusive neighbor counts."""
    radius = float(radius)
    if radius < 0.0:
        raise ValueError("radius must be non-negative")
    radius_sq = radius * radius
    neighbor_counts = [1 for _ in points]
    pairs: list[tuple[int, int]] = []
    for left, left_point in enumerate(points):
        for right in range(left + 1, len(points)):
            right_point = points[right]
            dx = left_point.x - right_point.x
            dy = left_point.y - right_point.y
            dz = left_point.z - right_point.z
            if dx * dx + dy * dy + dz * dz <= radius_sq:
                neighbor_counts[left] += 1
                neighbor_counts[right] += 1
                pairs.append((left, right))
    return tuple(pairs), tuple(neighbor_counts)


def _component_rows_from_pairs_and_flags(
    points: tuple[rt.Point3D, ...],
    within_pairs: Iterable[tuple[int, int]],
    neighbor_counts: Iterable[int],
    *,
    predicate_flags: Iterable[bool],
) -> tuple[dict[str, object], ...]:
    counts = [int(count) for count in neighbor_counts]
    is_core = [bool(flag) for flag in predicate_flags]
    if len(counts) != len(points) or len(is_core) != len(points):
        raise ValueError("neighbor_counts and predicate_flags must match points")
    parent = list(range(len(points)))

    def find(item: int) -> int:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root == right_root:
            return
        if left_root < right_root:
            parent[right_root] = left_root
        else:
            parent[left_root] = right_root

    pairs = tuple(within_pairs)
    for left, right in pairs:
        if is_core[left] and is_core[right]:
            union(left, right)

    roots = [-1 for _ in points]
    for index, core in enumerate(is_core):
        if core:
            roots[index] = find(index)
    for left, right in pairs:
        if roots[left] == -1 and is_core[right]:
            roots[left] = find(right)
        if roots[right] == -1 and is_core[left]:
            roots[right] = find(left)

    dense_by_root: dict[int, int] = {}
    next_label = 1
    rows: list[dict[str, object]] = []
    for index, point in enumerate(points):
        root = roots[index]
        if root < 0:
            cluster_id = NOISE_CLUSTER_ID
        else:
            if root not in dense_by_root:
                dense_by_root[root] = next_label
                next_label += 1
            cluster_id = dense_by_root[root]
        rows.append(
            {
                "point_id": point.id,
                "cluster_id": cluster_id,
                "is_core": bool(is_core[index]),
                "neighbor_count": int(counts[index]),
            }
        )
    return tuple(rows)


def _component_rows_from_pairs(
    points: tuple[rt.Point3D, ...],
    within_pairs: Iterable[tuple[int, int]],
    neighbor_counts: list[int],
    *,
    min_neighbors: int,
) -> tuple[dict[str, object], ...]:
    return _component_rows_from_pairs_and_flags(
        points,
        within_pairs,
        neighbor_counts,
        predicate_flags=(count >= min_neighbors for count in neighbor_counts),
    )


def _component_rows_from_parent_and_pairs(
    points: tuple[rt.Point3D, ...],
    within_pairs: Iterable[tuple[int, int]],
    neighbor_counts: Iterable[int],
    *,
    predicate_flags: Iterable[bool],
    parent: Iterable[int],
) -> tuple[dict[str, object], ...]:
    counts = [int(count) for count in neighbor_counts]
    is_core = [bool(flag) for flag in predicate_flags]
    parent_copy = [int(item) for item in parent]
    if len(counts) != len(points) or len(is_core) != len(points) or len(parent_copy) != len(points):
        raise ValueError("neighbor_counts, predicate_flags, and parent must match points")

    def find(item: int) -> int:
        while parent_copy[item] != item:
            parent_copy[item] = parent_copy[parent_copy[item]]
            item = parent_copy[item]
        return item

    roots = [-1 for _ in points]
    for index, core in enumerate(is_core):
        if core:
            roots[index] = find(index)
    for left, right in within_pairs:
        if roots[left] == -1 and is_core[right]:
            roots[left] = find(right)
        if roots[right] == -1 and is_core[left]:
            roots[right] = find(left)

    dense_by_root: dict[int, int] = {}
    next_label = 1
    rows: list[dict[str, object]] = []
    for index, point in enumerate(points):
        root = roots[index]
        if root < 0:
            cluster_id = NOISE_CLUSTER_ID
        else:
            if root not in dense_by_root:
                dense_by_root[root] = next_label
                next_label += 1
            cluster_id = dense_by_root[root]
        rows.append(
            {
                "point_id": point.id,
                "cluster_id": cluster_id,
                "is_core": bool(is_core[index]),
                "neighbor_count": int(counts[index]),
            }
        )
    return tuple(rows)


def _deduplicate_segment_union_proposals(
    segment_pairs: Iterable[tuple[int, int]],
) -> tuple[tuple[int, int], ...]:
    local_parent: dict[int, int] = {}

    def ensure(item: int) -> None:
        if item not in local_parent:
            local_parent[item] = item

    def find(item: int) -> int:
        ensure(item)
        while local_parent[item] != item:
            local_parent[item] = local_parent[local_parent[item]]
            item = local_parent[item]
        return item

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root == right_root:
            return
        if left_root < right_root:
            local_parent[right_root] = left_root
        else:
            local_parent[left_root] = right_root

    for left, right in segment_pairs:
        union(left, right)

    components: dict[int, list[int]] = {}
    for item in local_parent:
        components.setdefault(find(item), []).append(item)

    proposals: list[tuple[int, int]] = []
    for members in components.values():
        if len(members) < 2:
            continue
        ordered = sorted(members)
        anchor = ordered[0]
        proposals.extend((anchor, item) for item in ordered[1:])
    return tuple(proposals)


def simulate_fixed_radius_blocked_grouped_component_continuation_3d(
    points: tuple[rt.Point3D, ...],
    *,
    radius: float,
    predicate_flags: Iterable[bool],
    neighbor_counts: Iterable[int] | None = None,
    segment_target_hits: int = DEFAULT_BLOCKED_GROUPED_SEGMENT_TARGET_HITS,
    segment_capacity_hits: int | None = None,
) -> tuple[tuple[dict[str, object], ...], dict[str, object]]:
    """Local oracle for the Goal2467 blocked grouped-continuation contract."""
    segment_target_hits = int(segment_target_hits)
    if segment_target_hits < 1:
        raise ValueError("segment_target_hits must be positive")
    segment_capacity = segment_target_hits if segment_capacity_hits is None else int(segment_capacity_hits)
    if segment_capacity < 1:
        raise ValueError("segment_capacity_hits must be positive")

    flags = tuple(bool(flag) for flag in predicate_flags)
    if len(flags) != len(points):
        raise ValueError("predicate_flags must match points")

    pairs, computed_counts = fixed_radius_pairs_and_neighbor_counts_3d(points, radius=radius)
    counts = computed_counts if neighbor_counts is None else tuple(int(count) for count in neighbor_counts)
    if len(counts) != len(points):
        raise ValueError("neighbor_counts must match points")

    segments = tuple(pairs[index : index + segment_target_hits] for index in range(0, len(pairs), segment_target_hits))
    max_segment_hits = max((len(segment) for segment in segments), default=0)
    overflow_segment_count = sum(1 for segment in segments if len(segment) > segment_capacity)
    fallback_to_unblocked = overflow_segment_count > 0

    local_or_segment_union_proposals = 0
    deduplicated_union_proposals = 0
    global_parent_atomic_successes = 0
    parent = list(range(len(points)))

    def find(item: int) -> int:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(left: int, right: int) -> bool:
        left_root = find(left)
        right_root = find(right)
        if left_root == right_root:
            return False
        if left_root < right_root:
            parent[right_root] = left_root
        else:
            parent[left_root] = right_root
        return True

    if not fallback_to_unblocked:
        for segment in segments:
            core_pairs = tuple((left, right) for left, right in segment if flags[left] and flags[right])
            local_or_segment_union_proposals += len(core_pairs)
            deduplicated = _deduplicate_segment_union_proposals(core_pairs)
            deduplicated_union_proposals += len(deduplicated)
            for left, right in deduplicated:
                if union(left, right):
                    global_parent_atomic_successes += 1
    else:
        local_or_segment_union_proposals = sum(1 for left, right in pairs if flags[left] and flags[right])

    global_parent_atomic_attempts = 0 if fallback_to_unblocked else deduplicated_union_proposals
    proposal_rejection_rate = 0.0
    if local_or_segment_union_proposals > 0 and not fallback_to_unblocked:
        proposal_rejection_rate = 1.0 - (
            deduplicated_union_proposals / max(1, local_or_segment_union_proposals)
        )

    if fallback_to_unblocked:
        rows = _component_rows_from_pairs_and_flags(
            points,
            pairs,
            counts,
            predicate_flags=flags,
        )
    else:
        rows = _component_rows_from_parent_and_pairs(
            points,
            pairs,
            counts,
            predicate_flags=flags,
            parent=parent,
        )
    metadata = {
        "adapter": "simulate_fixed_radius_blocked_grouped_component_continuation_3d",
        "reference_only": True,
        "target_primitive": "generic_fixed_radius_blocked_grouped_component_continuation_3d",
        "candidate_native_contract": "fixed_radius_hit_stream_to_segmented_grouped_union_workspaces",
        "input_contract": "host_point_rows_fixed_radius_3d_with_predicate_flags",
        "hit_stream_pair_count": len(pairs),
        "predicate_true_count": sum(1 for flag in flags if flag),
        "segment_count": len(segments),
        "segment_target_hits": segment_target_hits,
        "segment_capacity_hits": segment_capacity,
        "max_segment_hits": max_segment_hits,
        "overflow_segment_count": overflow_segment_count,
        "fallback_to_unblocked_grouped_union": fallback_to_unblocked,
        "baseline_global_parent_atomic_attempts": local_or_segment_union_proposals,
        "global_parent_atomic_attempts": global_parent_atomic_attempts,
        "global_parent_atomic_successes": global_parent_atomic_successes,
        "local_or_segment_union_proposals": local_or_segment_union_proposals,
        "deduplicated_union_proposals": deduplicated_union_proposals,
        "proposal_rejection_rate": proposal_rejection_rate,
        "component_label_policy": "positive_root_index_labels_noise_minus_one",
        "app_independent_engine_required": True,
        "native_abi_added": False,
        "runtime_route_authorized": False,
        "rt_core_accelerated": False,
        "performance_claim_authorized": False,
        "release_claim_authorized": False,
    }
    return rows, metadata


def cpu_spatial_bucket_dbscan(
    points: tuple[rt.Point3D, ...],
    *,
    radius: float,
    min_neighbors: int,
) -> tuple[tuple[dict[str, object], ...], dict[str, object]]:
    cells: dict[tuple[int, int, int], list[int]] = {}
    cell_size = radius if radius > 0.0 else 1.0
    radius_sq = radius * radius
    for index, point in enumerate(points):
        key = (math.floor(point.x / cell_size), math.floor(point.y / cell_size), math.floor(point.z / cell_size))
        cells.setdefault(key, []).append(index)

    neighbor_counts = [1 for _ in points]
    pairs: list[tuple[int, int]] = []
    offsets = tuple((dx, dy, dz) for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1))
    for cell_key, left_indices in cells.items():
        cx, cy, cz = cell_key
        for ox, oy, oz in offsets:
            other_key = (cx + ox, cy + oy, cz + oz)
            if other_key not in cells or other_key < cell_key:
                continue
            right_indices = cells[other_key]
            for left_offset, left in enumerate(left_indices):
                start = left_offset + 1 if other_key == cell_key else 0
                for right in right_indices[start:]:
                    left_point = points[left]
                    right_point = points[right]
                    dx = left_point.x - right_point.x
                    dy = left_point.y - right_point.y
                    dz = left_point.z - right_point.z
                    if dx * dx + dy * dy + dz * dz <= radius_sq:
                        neighbor_counts[left] += 1
                        neighbor_counts[right] += 1
                        pairs.append((left, right))
    rows = _component_rows_from_pairs(points, pairs, neighbor_counts, min_neighbors=min_neighbors)
    return rows, {"cell_count": len(cells), "candidate_edge_count": len(pairs), "path": "cpu_spatial_bucket_reference"}


def _rows_from_partner_columns(columns: dict[str, object], *, partner: str) -> tuple[dict[str, object], ...]:
    if partner == "torch":
        point_ids = columns["point_ids"].detach().cpu().tolist()
        labels = columns["component_labels"].detach().cpu().tolist()
        core_flags = columns["is_core"].detach().cpu().tolist()
        counts = columns["neighbor_counts"].detach().cpu().tolist()
    elif partner == "cupy":
        import cupy

        point_ids = cupy.asnumpy(columns["point_ids"]).tolist()
        labels = cupy.asnumpy(columns["component_labels"]).tolist()
        core_flags = cupy.asnumpy(columns["is_core"]).tolist()
        counts = cupy.asnumpy(columns["neighbor_counts"]).tolist()
    elif partner == "numba":
        point_ids = columns["point_ids"].copy_to_host().tolist()
        labels = columns["component_labels"].copy_to_host().tolist()
        core_flags = columns["is_core"].copy_to_host().tolist()
        counts = columns["neighbor_counts"].copy_to_host().tolist()
    else:
        raise ValueError("partner must be torch, cupy, or numba")
    return tuple(
        {
            "point_id": int(point_id),
            "cluster_id": int(label),
            "is_core": bool(core),
            "neighbor_count": int(count),
        }
        for point_id, label, core, count in zip(point_ids, labels, core_flags, counts)
    )


def _cluster_signature_from_host_columns(
    point_ids: Iterable[int],
    component_labels: Iterable[int],
    core_flags: Iterable[object],
) -> dict[str, object]:
    dense_by_original: dict[int, int] = {}
    cluster_sizes: dict[int, int] = {}
    next_label = 1
    core_count = 0
    noise_count = 0
    for _point_id, label_value, core_value in sorted(
        zip(point_ids, component_labels, core_flags),
        key=lambda item: int(item[0]),
    ):
        if bool(core_value):
            core_count += 1
        label = int(label_value)
        if label == NOISE_CLUSTER_ID:
            noise_count += 1
            continue
        if label not in dense_by_original:
            dense_by_original[label] = next_label
            next_label += 1
        dense_label = dense_by_original[label]
        cluster_sizes[dense_label] = cluster_sizes.get(dense_label, 0) + 1
    return {
        "cluster_sizes": dict(sorted(cluster_sizes.items())),
        "core_count": core_count,
        "noise_count": noise_count,
    }


def _cluster_signature_from_partner_columns(columns: dict[str, object], *, partner: str) -> dict[str, object]:
    if partner == "torch":
        point_ids = columns["point_ids"].detach().cpu().tolist()
        labels = columns["component_labels"].detach().cpu().tolist()
        core_flags = columns["is_core"].detach().cpu().tolist()
    elif partner == "cupy":
        import cupy

        point_ids = cupy.asnumpy(columns["point_ids"]).tolist()
        labels = cupy.asnumpy(columns["component_labels"]).tolist()
        core_flags = cupy.asnumpy(columns["is_core"]).tolist()
    elif partner == "numba":
        point_ids = columns["point_ids"].copy_to_host().tolist()
        labels = columns["component_labels"].copy_to_host().tolist()
        core_flags = columns["is_core"].copy_to_host().tolist()
    else:
        raise ValueError("partner must be torch, cupy, or numba")
    return _cluster_signature_from_host_columns(point_ids, labels, core_flags)


def _cluster_signature_from_nonnegative_label_counts(
    label_counts: Iterable[int],
    *,
    core_count: int,
    noise_count: int = 0,
) -> dict[str, object]:
    cluster_sizes: dict[int, int] = {}
    dense_label = 1
    for count_value in label_counts:
        count = int(count_value)
        if count <= 0:
            continue
        cluster_sizes[dense_label] = count
        dense_label += 1
    return {
        "cluster_sizes": dict(sorted(cluster_sizes.items())),
        "core_count": int(core_count),
        "noise_count": int(noise_count),
    }


def _component_size_signature_payload(component_sizes: Iterable[int]) -> dict[str, object]:
    sizes = tuple(sorted(int(size) for size in component_sizes if int(size) > 0))
    return {
        "component_sizes": sizes,
        "component_count": len(sizes),
        "point_count": sum(sizes),
        "contract": "fixed_radius_graph_component_size_signature_3d",
    }


def _cluster_signature_from_numba_label_columns(
    columns: dict[str, object],
    *,
    point_count: int,
) -> dict[str, object]:
    """Build a DBSCAN signature from generic Numba label and flag columns.

    This stays in the app layer and uses a generic Numba label-count/flag-count
    partner primitive. It does not add a native DBSCAN continuation.
    """

    result = rt.run_numba_label_count_and_flag_count_i64(
        columns["component_labels"],
        columns["is_core"],
        label_count=int(point_count) + 1,
        validate_labels=False,
    )
    label_counts = result["outputs"]["label_counts"].copy_to_host().tolist()
    core_count = int(result["outputs"]["flag_true_count"].copy_to_host()[0])
    noise_count = int(result["outputs"]["negative_label_count"].copy_to_host()[0])
    return _cluster_signature_from_nonnegative_label_counts(
        label_counts,
        core_count=core_count,
        noise_count=noise_count,
    )


def _cluster_signature_from_numba_signature_count_columns(
    columns: dict[str, object],
) -> dict[str, object]:
    label_counts = columns["label_counts"].copy_to_host().tolist()
    core_count = int(columns["flag_true_count"].copy_to_host()[0])
    noise_count = int(columns["negative_label_count"].copy_to_host()[0])
    return _cluster_signature_from_nonnegative_label_counts(
        label_counts,
        core_count=core_count,
        noise_count=noise_count,
    )


def _cluster_signature_from_cupy_signature_count_columns(
    columns: dict[str, object],
) -> dict[str, object]:
    import cupy

    label_counts = cupy.asnumpy(columns["label_counts"]).tolist()
    core_count = int(cupy.asnumpy(columns["flag_true_count"])[0])
    noise_count = int(cupy.asnumpy(columns["negative_label_count"])[0])
    return _cluster_signature_from_nonnegative_label_counts(
        label_counts,
        core_count=core_count,
        noise_count=noise_count,
    )


def _optix_ranked_summaries_to_cupy_core_columns(
    points: tuple[rt.Point3D, ...],
    summaries: Iterable[dict[str, object]],
    *,
    min_neighbors: int,
):
    import cupy

    by_query_id = {int(row["query_id"]): row for row in summaries}
    counts: list[int] = []
    flags: list[int] = []
    for point in points:
        row = by_query_id.get(point.id)
        count = 0 if row is None else int(row["neighbor_count"])
        counts.append(count)
        flags.append(1 if count >= min_neighbors else 0)
    return {
        "neighbor_counts": cupy.asarray(counts, dtype=cupy.uint32),
        "core_flags": cupy.asarray(flags, dtype=cupy.uint32),
        "summary_rows": len(by_query_id),
    }


def _component_rows_from_neighbor_rows(
    points: tuple[rt.Point3D, ...],
    neighbor_rows: Iterable[dict[str, object]],
    *,
    min_neighbors: int,
) -> tuple[dict[str, object], ...]:
    index_by_id = {point.id: index for index, point in enumerate(points)}
    neighbor_counts = [0 for _ in points]
    pairs: set[tuple[int, int]] = set()
    for row in neighbor_rows:
        query_id = int(row["query_id"])
        neighbor_id = int(row["neighbor_id"])
        if query_id not in index_by_id or neighbor_id not in index_by_id:
            continue
        left = index_by_id[query_id]
        right = index_by_id[neighbor_id]
        neighbor_counts[left] += 1
        if left != right:
            pairs.add((min(left, right), max(left, right)))
    return _component_rows_from_pairs(points, sorted(pairs), neighbor_counts, min_neighbors=min_neighbors)


def cluster_signature(rows: Iterable[dict[str, object]]) -> dict[str, object]:
    cluster_sizes: dict[int, int] = {}
    core_count = 0
    noise_count = 0
    for row in rows:
        if bool(row["is_core"]):
            core_count += 1
        cluster_id = int(row["cluster_id"])
        if cluster_id == NOISE_CLUSTER_ID:
            noise_count += 1
        else:
            cluster_sizes[cluster_id] = cluster_sizes.get(cluster_id, 0) + 1
    return {
        "cluster_sizes": dict(sorted(cluster_sizes.items())),
        "core_count": core_count,
        "noise_count": noise_count,
    }


def canonical_component_size_signature(signature: dict[str, object]) -> dict[str, object]:
    """Normalize a cluster signature when component label ids are arbitrary."""

    cluster_sizes = signature.get("cluster_sizes", {})
    if not isinstance(cluster_sizes, dict):
        raise TypeError("signature['cluster_sizes'] must be a dict")
    return {
        "cluster_sizes": tuple(sorted(int(value) for value in cluster_sizes.values() if int(value) > 0)),
        "core_count": int(signature["core_count"]),
        "noise_count": int(signature["noise_count"]),
    }


def same_canonical_component_size_signature(left: dict[str, object], right: dict[str, object]) -> bool:
    return canonical_component_size_signature(left) == canonical_component_size_signature(right)


def policy_aware_rt_dbscan_semantic_signature(
    signature: dict[str, object],
    *,
    border_assignment_policy: str,
    component_size_contract: str = "policy_bound_component_sizes",
) -> dict[str, object]:
    """Return a policy-aware app-layer semantic signature for DBSCAN-like outputs.

    Border items can legally touch multiple predicate-true components. When a
    caller treats a concrete border assignment policy as part of the contract,
    component-size distribution belongs in the signature. When the caller only
    contracts core/noise/assigned counts, border tie-break differences should not
    masquerade as semantic failures.
    """

    component_size_contract = str(component_size_contract)
    if component_size_contract not in {
        "policy_bound_component_sizes",
        "core_noise_assigned_counts_only",
    }:
        raise ValueError(
            "component_size_contract must be 'policy_bound_component_sizes' "
            "or 'core_noise_assigned_counts_only'"
        )
    canonical = canonical_component_size_signature(signature)
    cluster_sizes = tuple(int(value) for value in canonical["cluster_sizes"])
    assigned_count = int(sum(cluster_sizes))
    core_count = int(canonical["core_count"])
    noise_count = int(canonical["noise_count"])
    payload: dict[str, object] = {
        "contract": "rt_dbscan_policy_aware_semantic_signature_v1",
        "component_size_contract": component_size_contract,
        "border_assignment_policy": str(border_assignment_policy),
        "core_count": core_count,
        "noise_count": noise_count,
        "assigned_count": assigned_count,
        "border_count": max(0, assigned_count - core_count),
        "point_count": assigned_count + noise_count,
    }
    if component_size_contract == "policy_bound_component_sizes":
        payload["cluster_sizes"] = cluster_sizes
        payload["component_count"] = len(cluster_sizes)
    return payload


def same_policy_aware_rt_dbscan_semantic_signature(
    left: dict[str, object],
    right: dict[str, object],
    *,
    border_assignment_policy: str,
    component_size_contract: str = "policy_bound_component_sizes",
) -> bool:
    return policy_aware_rt_dbscan_semantic_signature(
        left,
        border_assignment_policy=border_assignment_policy,
        component_size_contract=component_size_contract,
    ) == policy_aware_rt_dbscan_semantic_signature(
        right,
        border_assignment_policy=border_assignment_policy,
        component_size_contract=component_size_contract,
    )


def _densify_cluster_labels(rows: Iterable[dict[str, object]]) -> tuple[dict[str, object], ...]:
    dense_by_original: dict[int, int] = {}
    next_label = 1
    normalized: list[dict[str, object]] = []
    for row in sorted(rows, key=lambda item: int(item["point_id"])):
        item = dict(row)
        cluster_id = int(item["cluster_id"])
        if cluster_id != NOISE_CLUSTER_ID:
            if cluster_id not in dense_by_original:
                dense_by_original[cluster_id] = next_label
                next_label += 1
            item["cluster_id"] = dense_by_original[cluster_id]
        normalized.append(item)
    return tuple(normalized)


def _optional_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _build_grouped_stream_timing_breakdown(
    timing_sec: dict[str, float],
    metadata: dict[str, object],
    *,
    elapsed_sec: float,
) -> dict[str, object]:
    """Build a host-observed grouped-stream timing packet without changing runtime semantics."""
    sec = {key: float(value) for key, value in timing_sec.items()}
    native_metadata = metadata.get("native_grouped_stream_metadata", {})
    if not isinstance(native_metadata, dict):
        native_metadata = {}
    count_metadata = metadata.get("count_metadata", {})
    if not isinstance(count_metadata, dict):
        count_metadata = {}
    count_native_metadata = count_metadata.get("native_metadata", {})
    if not isinstance(count_native_metadata, dict):
        count_native_metadata = {}

    grouped_native_sec = _optional_float(native_metadata.get("native_elapsed_sec")) or 0.0
    count_native_sec = _optional_float(count_native_metadata.get("native_elapsed_sec")) or 0.0
    count_native_current_run_sec = 0.0 if metadata.get("core_flag_cache_reused") else count_native_sec
    adapter_run_sec = sec.get("adapter_run_sec", 0.0)
    known_host_phase_sec = sum(sec.values())

    derived_sec = {
        "elapsed_sec": float(elapsed_sec),
        "known_host_phase_sec": known_host_phase_sec,
        "unattributed_elapsed_sec": max(0.0, float(elapsed_sec) - known_host_phase_sec),
        "grouped_native_sec": grouped_native_sec,
        "count_native_current_run_sec": count_native_current_run_sec,
        "known_native_current_run_sec": grouped_native_sec + count_native_current_run_sec,
        "adapter_non_native_estimated_sec": max(
            0.0,
            adapter_run_sec - grouped_native_sec - count_native_current_run_sec,
        ),
    }
    return {
        "schema": RT_DBSCAN_GROUPED_STREAM_TIMING_BREAKDOWN_SCHEMA,
        "host_observed_sec": sec,
        "derived_sec": derived_sec,
        "notes": [
            "Host-observed timings are diagnostic and may include async GPU synchronization effects.",
            "Native elapsed fields come from RTDL native metadata where available.",
            "This timing packet does not authorize a paper, broad RT-core, or whole-app speedup claim.",
        ],
        "performance_claim_authorized": False,
    }


def run_rt_dbscan_benchmark(
    *,
    mode: str,
    dataset: str,
    point_count: int | None,
    radius: float | None,
    min_neighbors: int | None,
    seed: int,
    partner: str,
    include_rows: bool,
    validate: bool,
    adjacency_edge_budget: int | None = None,
    chunk_adjacency_edge_budget: int | None = None,
    reuse_chunk_neighbor_index_workspace: bool = False,
    chunk_neighbor_index_workspace_pool_size: int = 0,
    grouped_union_query_block_size: int | None = None,
    grouped_union_same_root_culling: bool = True,
    grouped_union_direct_side_effect: bool = False,
    partition_pair_enumeration: str = "mode_default",
    partition_cell_factor: float = 0.125,
    direct_status_convergence_mode: str = "until_stable",
    repeat: int = 1,
    warmup: int = 0,
) -> dict[str, object]:
    config = DEFAULT_DATASET_CONFIG[dataset]
    resolved_point_count = int(point_count if point_count is not None else config["point_count"])
    resolved_radius = float(radius if radius is not None else config["radius"])
    resolved_min_neighbors = int(min_neighbors if min_neighbors is not None else config["min_neighbors"])
    if include_rows and mode in {
        "optix_rt_core_grouped_stream_cupy_column_signature_3d",
        "optix_rt_core_grouped_stream_numba_column_signature_3d",
        "optix_rt_core_grouped_stream_blocked_cupy_column_signature_3d",
        "optix_rt_core_grouped_stream_blocked_numba_column_signature_3d",
        "optix_rt_core_flags_numba_prepared_grid_column_signature_3d",
        "embree_core_flags_numba_prepared_grid_column_signature_3d",
        "partner_cupy_partition_convergence_component_signature_3d",
        "partner_cupy_prepared_partition_convergence_component_signature_3d",
        "partner_cupy_prepared_direct_status_union_component_signature_3d",
        "optix_rt_core_flags_cupy_predicate_direct_status_column_signature_3d",
        "optix_rt_core_flags_cupy_predicate_direct_status_all_true_column_signature_3d",
        "partner_cupy_declared_all_true_predicate_direct_status_column_signature_3d",
    }:
        raise ValueError("signature mode does not materialize Python rows; column-signature mode does not materialize Python rows")
    if repeat < 1:
        raise ValueError("repeat must be positive")
    if warmup < 0 or warmup >= repeat:
        raise ValueError("warmup must be non-negative and smaller than repeat")
    resolved_partition_cell_factor = float(partition_cell_factor)
    if resolved_partition_cell_factor <= 0.0:
        raise ValueError("partition_cell_factor must be positive")
    direct_status_convergence_mode = str(direct_status_convergence_mode)
    if direct_status_convergence_mode not in {"until_stable", "single_pass_candidate"}:
        raise ValueError(
            "direct_status_convergence_mode must be 'until_stable' or 'single_pass_candidate'"
        )
    if partition_pair_enumeration not in {
        "mode_default",
        "host",
        "device_bounded_offsets",
        "device_count_then_emit",
        "device_count_then_emit_non_skip",
        "device_count_then_emit_non_skip_unordered",
    }:
        raise ValueError(
            "partition_pair_enumeration must be 'mode_default', 'host', "
            "'device_bounded_offsets', 'device_count_then_emit', "
            "'device_count_then_emit_non_skip', or "
            "'device_count_then_emit_non_skip_unordered'"
        )
    partition_pair_enumeration_kwargs = (
        {}
        if partition_pair_enumeration == "mode_default"
        else {"pair_enumeration": partition_pair_enumeration}
    )
    if mode == "planned_rt_dbscan":
        plan = plan_rt_dbscan_execution(dataset, resolved_point_count)
        selected_mode = str(plan["selected_mode"])
        payload = run_rt_dbscan_benchmark(
            mode=selected_mode,
            dataset=dataset,
            point_count=resolved_point_count,
            radius=resolved_radius,
            min_neighbors=resolved_min_neighbors,
            seed=seed,
            partner=partner,
            include_rows=include_rows,
            validate=validate,
            adjacency_edge_budget=adjacency_edge_budget,
            chunk_adjacency_edge_budget=chunk_adjacency_edge_budget,
            reuse_chunk_neighbor_index_workspace=reuse_chunk_neighbor_index_workspace,
            chunk_neighbor_index_workspace_pool_size=chunk_neighbor_index_workspace_pool_size,
            grouped_union_query_block_size=grouped_union_query_block_size,
            grouped_union_same_root_culling=grouped_union_same_root_culling,
            grouped_union_direct_side_effect=grouped_union_direct_side_effect,
            partition_pair_enumeration=partition_pair_enumeration,
            repeat=repeat,
            warmup=warmup,
        )
        payload["mode"] = mode
        payload["selected_mode"] = selected_mode
        metadata = dict(payload.get("metadata", {}))
        metadata["execution_plan"] = plan
        payload["metadata"] = metadata
        claim_boundary = dict(payload.get("claim_boundary", {}))
        claim_boundary["planned_execution"] = True
        claim_boundary["automatic_hidden_dispatcher"] = False
        claim_boundary["release_claim_authorized"] = False
        payload["claim_boundary"] = claim_boundary
        return payload
    if mode == "planned_rt_dbscan_continuation":
        plan = plan_rt_dbscan_continuation_execution(
            dataset,
            resolved_point_count,
            directed_edge_budget=adjacency_edge_budget,
        )
        selected_mode = str(plan["selected_mode"])
        payload = run_rt_dbscan_benchmark(
            mode=selected_mode,
            dataset=dataset,
            point_count=resolved_point_count,
            radius=resolved_radius,
            min_neighbors=resolved_min_neighbors,
            seed=seed,
            partner=partner,
            include_rows=include_rows,
            validate=validate,
            adjacency_edge_budget=adjacency_edge_budget,
            chunk_adjacency_edge_budget=chunk_adjacency_edge_budget,
            reuse_chunk_neighbor_index_workspace=reuse_chunk_neighbor_index_workspace,
            chunk_neighbor_index_workspace_pool_size=chunk_neighbor_index_workspace_pool_size,
            grouped_union_query_block_size=grouped_union_query_block_size,
            grouped_union_same_root_culling=grouped_union_same_root_culling,
            grouped_union_direct_side_effect=grouped_union_direct_side_effect,
            partition_pair_enumeration=partition_pair_enumeration,
            repeat=repeat,
            warmup=warmup,
        )
        payload["mode"] = mode
        payload["selected_mode"] = selected_mode
        metadata = dict(payload.get("metadata", {}))
        metadata["execution_plan"] = plan
        payload["metadata"] = metadata
        claim_boundary = dict(payload.get("claim_boundary", {}))
        claim_boundary["planned_continuation_execution"] = True
        claim_boundary["automatic_hidden_dispatcher"] = False
        claim_boundary["release_claim_authorized"] = False
        claim_boundary["paper_reproduction_claim_authorized"] = False
        payload["claim_boundary"] = claim_boundary
        return payload
    points = make_rt_dbscan_points(dataset, point_count=resolved_point_count, seed=seed)

    start = time.perf_counter()
    timing_breakdown_sec: dict[str, float] | None = None
    signature_override: dict[str, object] | None = None
    reference_signature_override: dict[str, object] | None = None
    elapsed_override: float | None = None
    metadata: dict[str, object]
    if mode == "cpu_reference":
        rows, metadata = cpu_spatial_bucket_dbscan(points, radius=resolved_radius, min_neighbors=resolved_min_neighbors)
    elif mode == "rtdl_cpu_rows":
        neighbor_rows = rt.fixed_radius_neighbors_cpu(
            points,
            points,
            radius=resolved_radius,
            k_max=len(points),
        )
        rows = _component_rows_from_neighbor_rows(points, neighbor_rows, min_neighbors=resolved_min_neighbors)
        metadata = {
            "path": "rtdl_cpu_fixed_radius_neighbor_rows",
            "neighbor_row_count": len(neighbor_rows),
            "native_engine_row_contract": "generic_fixed_radius_neighbors_3d_rows",
        }
    elif mode == "embree_prepared_rows":
        kernel = make_fixed_radius_neighbors_3d_embree_kernel(
            radius=resolved_radius,
            k_max=len(points),
        )
        neighbor_rows = rt.run_embree(
            kernel,
            query_points=points,
            search_points=points,
        )
        rows = _component_rows_from_neighbor_rows(points, neighbor_rows, min_neighbors=resolved_min_neighbors)
        metadata = {
            "path": "embree_fixed_radius_neighbor_rows_3d",
            "neighbor_row_count": len(neighbor_rows),
            "native_engine_row_contract": "generic_fixed_radius_neighbors_3d_rows",
            "native_execution_path": "embree_point_query_fixed_radius_3d",
            "embree_backend_used": True,
            "rt_core_accelerated": False,
            "materializes_neighbor_rows": True,
        }
    elif mode == "embree_core_flags_numba_prepared_grid_column_signature_3d":
        import numpy as np
        from numba import cuda

        prepare_start = time.perf_counter()
        point_columns = rt.point_rows_to_partner_columns(points, partner="numba")
        prepared_grid = rt.prepare_radius_graph_components_3d_numba_grid_partner_columns(
            point_columns,
            radius=resolved_radius,
            partner="numba",
        )
        embree_kernel = make_fixed_radius_neighbors_3d_embree_kernel(
            radius=resolved_radius,
            k_max=resolved_min_neighbors,
        )
        prepare_sec = time.perf_counter() - prepare_start
        point_index_by_id = {int(point.id): index for index, point in enumerate(points)}
        prepared_query_runs: list[dict[str, object]] = []
        for iteration in range(repeat):
            run_timing: dict[str, float] = {}
            run_start = time.perf_counter()
            embree_start = time.perf_counter()
            threshold_rows = rt.run_embree(
                embree_kernel,
                query_points=points,
                search_points=points,
            )
            embree_elapsed = time.perf_counter() - embree_start
            counts_host = np.zeros((len(points),), dtype=np.uint32)
            for row in threshold_rows:
                query_index = point_index_by_id[int(row["query_id"])]
                if counts_host[query_index] < resolved_min_neighbors:
                    counts_host[query_index] += 1
            flags_host = (counts_host >= resolved_min_neighbors).astype(np.uint32, copy=False)
            upload_start = time.perf_counter()
            neighbor_counts_device = cuda.to_device(counts_host)
            core_flags_device = cuda.to_device(flags_host)
            cuda.synchronize()
            upload_elapsed = time.perf_counter() - upload_start
            continuation_start = time.perf_counter()
            result = rt.radius_graph_components_3d_numba_prepared_grid_partner_columns(
                prepared_grid,
                min_neighbors=resolved_min_neighbors,
                core_flags=core_flags_device,
                neighbor_counts=neighbor_counts_device,
                core_flag_source="embree_fixed_radius_threshold_capped_rows_3d",
                return_metadata=True,
            )
            continuation_elapsed = time.perf_counter() - continuation_start
            signature_start = time.perf_counter()
            run_signature = _cluster_signature_from_partner_columns(result["columns"], partner="numba")
            run_timing["embree_threshold_capped_rows_sec"] = embree_elapsed
            run_timing["embree_threshold_columns_upload_sec"] = upload_elapsed
            run_timing["numba_component_continuation_sec"] = continuation_elapsed
            run_timing["column_signature_sec"] = time.perf_counter() - signature_start
            prepared_query_runs.append(
                {
                    "iteration": iteration,
                    "is_warmup": iteration < warmup,
                    "elapsed_sec": time.perf_counter() - run_start,
                    "timing_sec": run_timing,
                    "signature": run_signature,
                    "rows": (),
                    "metadata": dict(result["metadata"]),
                    "embree_threshold_row_count": len(threshold_rows),
                    "core_flag_count": int(flags_host.sum()),
                }
            )
        measured_runs = [row for row in prepared_query_runs if not bool(row["is_warmup"])]
        if not measured_runs:
            raise RuntimeError("RT-DBSCAN Embree+Numba repeat produced no measured rows")
        phase_names = sorted({name for row in measured_runs for name in row["timing_sec"]})
        timing_breakdown_sec = {
            name: float(statistics.median(float(row["timing_sec"][name]) for row in measured_runs if name in row["timing_sec"]))
            for name in phase_names
        }
        timing_total_sec = {
            name: float(sum(float(row["timing_sec"][name]) for row in measured_runs if name in row["timing_sec"]))
            for name in phase_names
        }
        elapsed_override = float(statistics.median(float(row["elapsed_sec"]) for row in measured_runs))
        elapsed_total_sec = float(sum(float(row["elapsed_sec"]) for row in measured_runs))
        signature_override = dict(measured_runs[-1]["signature"])
        rows = ()
        metadata = dict(measured_runs[-1]["metadata"])
        metadata.update(
            {
                "path": "embree_threshold_capped_rows_numba_prepared_grid_radius_graph_column_signature_3d",
                "embree_threshold_capped_rows_sec": timing_breakdown_sec["embree_threshold_capped_rows_sec"],
                "embree_threshold_columns_upload_sec": timing_breakdown_sec["embree_threshold_columns_upload_sec"],
                "numba_component_continuation_sec": timing_breakdown_sec["numba_component_continuation_sec"],
                "column_signature_sec": timing_breakdown_sec["column_signature_sec"],
                "native_engine_summary_contract": "generic_fixed_radius_count_threshold_3d_host_columns_via_threshold_capped_rows",
                "native_execution_path": "embree_point_query_fixed_radius_3d_threshold_capped_rows",
                "embree_backend_used": True,
                "rt_core_accelerated": False,
                "materializes_neighbor_summaries": False,
                "materializes_neighbor_rows": True,
                "materializes_python_rows": False,
                "signature_source": "partner_column_arrays_no_python_row_dicts",
                "neighbor_count_policy": "threshold_capped_at_min_neighbors_not_exact_full_degree",
                "embree_prepared_3d_scene_handle_used": False,
                "current_embree_3d_scene_setup_paid_in_threshold_phase": True,
                "embree_threshold_row_count": int(measured_runs[-1]["embree_threshold_row_count"]),
                "core_flag_count": int(measured_runs[-1]["core_flag_count"]),
                "prepared_query_repeat_protocol": {
                    "repeat": repeat,
                    "warmup": warmup,
                    "measured_iterations": len(measured_runs),
                    "prepare_sec": prepare_sec,
                    "median_elapsed_sec": elapsed_override,
                    "elapsed_sec_total": elapsed_total_sec,
                },
                "timing_total_sec": timing_total_sec,
            }
        )
    elif mode == "partner_spatial_bucket_3d":
        point_columns = rt.point_rows_to_partner_columns(points, partner=partner)
        result = rt.radius_graph_components_3d_spatial_bucket_partner_columns(
            point_columns,
            radius=resolved_radius,
            min_neighbors=resolved_min_neighbors,
            partner=partner,
            return_metadata=True,
        )
        rows = _rows_from_partner_columns(result["columns"], partner=partner)
        metadata = dict(result["metadata"])
    elif mode == "partner_cupy_grid_components_3d":
        point_columns = rt.point_rows_to_partner_columns(points, partner="cupy")
        result = rt.radius_graph_components_3d_cupy_grid_partner_columns(
            point_columns,
            radius=resolved_radius,
            min_neighbors=resolved_min_neighbors,
            partner="cupy",
            return_metadata=True,
        )
        rows = _rows_from_partner_columns(result["columns"], partner="cupy")
        metadata = dict(result["metadata"])
    elif mode == "partner_numba_grid_components_3d":
        point_columns = rt.point_rows_to_partner_columns(points, partner="numba")
        result = rt.radius_graph_components_3d_numba_grid_partner_columns(
            point_columns,
            radius=resolved_radius,
            min_neighbors=resolved_min_neighbors,
            partner="numba",
            return_metadata=True,
        )
        rows = _rows_from_partner_columns(result["columns"], partner="numba")
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "path": "partner_numba_grid_radius_graph_components_3d",
                "rt_core_accelerated": False,
                "materializes_neighbor_rows": False,
                "raw_cuda_kernel_required": False,
            }
        )
    elif mode == "partner_cupy_prepared_grid_components_3d":
        point_columns = rt.point_rows_to_partner_columns(points, partner="cupy")
        prepared_grid = rt.prepare_radius_graph_components_3d_cupy_grid_partner_columns(
            point_columns,
            radius=resolved_radius,
            partner="cupy",
        )
        result = rt.radius_graph_components_3d_cupy_prepared_grid_partner_columns(
            prepared_grid,
            min_neighbors=resolved_min_neighbors,
            return_metadata=True,
        )
        rows = _rows_from_partner_columns(result["columns"], partner="cupy")
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "path": "partner_cupy_prepared_grid_radius_graph_components_3d",
                "rt_core_accelerated": False,
                "materializes_neighbor_rows": False,
            }
        )
    elif mode == "partner_numba_prepared_grid_components_3d":
        point_columns = rt.point_rows_to_partner_columns(points, partner="numba")
        prepared_grid = rt.prepare_radius_graph_components_3d_numba_grid_partner_columns(
            point_columns,
            radius=resolved_radius,
            partner="numba",
        )
        result = rt.radius_graph_components_3d_numba_prepared_grid_partner_columns(
            prepared_grid,
            min_neighbors=resolved_min_neighbors,
            return_metadata=True,
        )
        rows = _rows_from_partner_columns(result["columns"], partner="numba")
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "path": "partner_numba_prepared_grid_radius_graph_components_3d",
                "rt_core_accelerated": False,
                "materializes_neighbor_rows": False,
                "raw_cuda_kernel_required": False,
            }
        )
    elif mode == "partner_cupy_prepared_adjacency_components_3d":
        point_columns = rt.point_rows_to_partner_columns(points, partner="cupy")
        prepared_adjacency = rt.prepare_radius_graph_adjacency_3d_cupy_partner_columns(
            point_columns,
            radius=resolved_radius,
            partner="cupy",
        )
        result = rt.radius_graph_components_3d_cupy_prepared_adjacency_partner_columns(
            prepared_adjacency,
            min_neighbors=resolved_min_neighbors,
            return_metadata=True,
        )
        rows = _rows_from_partner_columns(result["columns"], partner="cupy")
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "path": "partner_cupy_prepared_directed_adjacency_radius_graph_components_3d",
                "rt_core_accelerated": False,
                "materializes_neighbor_rows": False,
                "materializes_directed_adjacency_stream": True,
            }
        )
    elif mode == "partner_cupy_partition_convergence_component_signature_3d":
        signature_start = time.perf_counter()
        result = rt.build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d(
            points,
            radius=resolved_radius,
            cell_factor=resolved_partition_cell_factor,
            validate_summary_same_contract=validate,
            validate_against_component_labels=validate,
            **partition_pair_enumeration_kwargs,
        )
        component_signature_sec = time.perf_counter() - signature_start
        rows = ()
        component_sizes = result["columns"]["component_size_signature"]
        signature_override = _component_size_signature_payload(component_sizes)
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "path": "partner_cupy_partition_convergence_component_signature_3d",
                "front_door": "v2_8_fixed_radius_graph_component_continuation_3d",
                "front_door_operation": "fixed_radius_graph_component_size_signature_3d",
                "v2_8_front_door_route": True,
                "partition_convergence_hybrid_candidate": True,
                "partition_convergence_hybrid_promoted": False,
                "explicit_candidate_preview": True,
                "current_default_route": False,
                "native_engine_summary_contract": "generic_fixed_radius_partition_convergence_summary_3d",
                "native_execution_path": "partner_cupy_fixed_radius_partition_convergence_preview_3d",
                "partner": "cupy",
                "partition_cell_factor_user_selection": resolved_partition_cell_factor,
                "partition_pair_enumeration_user_selection": partition_pair_enumeration,
                "partition_pair_enumeration_effective": metadata.get("partition_summary_pair_enumeration"),
                "partition_pair_enumeration_explicit_override": partition_pair_enumeration != "mode_default",
                "partition_pair_enumeration_default_route_changed": False,
                "optix_backend_used": False,
                "rt_core_accelerated": False,
                "materializes_neighbor_summaries": False,
                "materializes_neighbor_rows": False,
                "materializes_python_rows": False,
                "materializes_full_component_labels": False,
                "signature_source": "component_size_signature_column_no_python_row_dicts",
                "validation_reference_kind": "fixed_radius_graph_component_labels_reference_3d",
                "component_signature_sec": component_signature_sec,
                "full_dbscan_semantics": False,
                "dbscan_core_border_noise_semantics": False,
                "graph_component_contract_only": True,
                "public_speedup_claim_authorized": False,
                "release_authorized": False,
            }
        )
        if validate:
            reference = rt.build_v2_8_fixed_radius_partition_convergence_component_labels_reference_3d(
                points,
                radius=resolved_radius,
                cell_factor=float(metadata.get("cell_factor", 0.125)),
                partition_summary=None,
            )
            label_values = tuple(int(value) for value in reference["columns"]["component_labels"])
            reference_sizes = sorted(label_values.count(label) for label in set(label_values))
            reference_signature_override = _component_size_signature_payload(reference_sizes)
    elif mode == "partner_cupy_prepared_partition_convergence_component_signature_3d":
        prepare_start = time.perf_counter()
        prepared_partition_summary = (
            rt.prepare_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(
                points,
                radius=resolved_radius,
                cell_factor=resolved_partition_cell_factor,
                validate_summary_same_contract=validate,
                **partition_pair_enumeration_kwargs,
            )
        )
        prepared_partition_summary_sec = time.perf_counter() - prepare_start
        signature_start = time.perf_counter()
        result = rt.run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_preview_3d(
            prepared_partition_summary,
            validate_summary_same_contract=False,
            validate_against_component_labels=validate,
        )
        component_signature_sec = time.perf_counter() - signature_start
        rows = ()
        component_sizes = result["columns"]["component_size_signature"]
        signature_override = _component_size_signature_payload(component_sizes)
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "path": "partner_cupy_prepared_partition_convergence_component_signature_3d",
                "front_door": "v2_8_fixed_radius_graph_component_continuation_3d",
                "front_door_operation": "fixed_radius_graph_component_size_signature_3d",
                "v2_8_front_door_route": True,
                "partition_convergence_hybrid_candidate": True,
                "partition_convergence_hybrid_promoted": False,
                "explicit_candidate_preview": True,
                "current_default_route": False,
                "prepared_partition_summary_app_mode": True,
                "prepared_partition_summary_reused": True,
                "native_engine_summary_contract": "generic_fixed_radius_partition_convergence_summary_3d",
                "native_execution_path": "partner_cupy_prepared_fixed_radius_partition_convergence_preview_3d",
                "partner": "cupy",
                "partition_cell_factor_user_selection": resolved_partition_cell_factor,
                "partition_pair_enumeration_user_selection": partition_pair_enumeration,
                "partition_pair_enumeration_effective": metadata.get("partition_summary_pair_enumeration"),
                "partition_pair_enumeration_explicit_override": partition_pair_enumeration != "mode_default",
                "partition_pair_enumeration_default_route_changed": False,
                "optix_backend_used": False,
                "rt_core_accelerated": False,
                "materializes_neighbor_summaries": False,
                "materializes_neighbor_rows": False,
                "materializes_python_rows": False,
                "materializes_full_component_labels": False,
                "signature_source": "prepared_component_size_signature_column_no_python_row_dicts",
                "validation_reference_kind": "fixed_radius_graph_component_labels_reference_3d",
                "prepared_partition_summary_sec": prepared_partition_summary_sec,
                "component_signature_sec": component_signature_sec,
                "prepared_partition_total_sec": prepared_partition_summary_sec + component_signature_sec,
                "full_dbscan_semantics": False,
                "dbscan_core_border_noise_semantics": False,
                "graph_component_contract_only": True,
                "public_speedup_claim_authorized": False,
                "release_authorized": False,
            }
        )
        if validate:
            reference = rt.build_v2_8_fixed_radius_partition_convergence_component_labels_reference_3d(
                points,
                radius=resolved_radius,
                cell_factor=float(metadata.get("cell_factor", 0.125)),
                partition_summary=None,
            )
            label_values = tuple(int(value) for value in reference["columns"]["component_labels"])
            reference_sizes = sorted(label_values.count(label) for label in set(label_values))
            reference_signature_override = _component_size_signature_payload(reference_sizes)
    elif mode == "partner_cupy_prepared_direct_status_union_component_signature_3d":
        prepare_start = time.perf_counter()
        prepared_direct_status = (
            rt.prepare_v2_8_fixed_radius_partition_convergence_direct_status_union_cupy_preview_3d(
                points,
                radius=resolved_radius,
                cell_factor=resolved_partition_cell_factor,
            )
        )
        prepared_direct_status_sec = time.perf_counter() - prepare_start
        prepared_direct_status_runs: list[dict[str, object]] = []
        for iteration in range(repeat):
            run_start = time.perf_counter()
            signature_start = time.perf_counter()
            result = rt.run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_direct_status_union_preview_3d(
                prepared_direct_status,
                convergence_mode=direct_status_convergence_mode,
                validate_against_materialized_signature=validate,
            )
            component_signature_sec = time.perf_counter() - signature_start
            component_sizes = result["columns"]["component_size_signature"]
            prepared_direct_status_runs.append(
                {
                    "iteration": iteration,
                    "is_warmup": iteration < warmup,
                    "elapsed_sec": time.perf_counter() - run_start,
                    "timing_sec": {
                        "component_signature_sec": component_signature_sec,
                    },
                    "signature": _component_size_signature_payload(component_sizes),
                    "metadata": dict(result["metadata"]),
                }
            )
        measured_runs = [row for row in prepared_direct_status_runs if not bool(row["is_warmup"])]
        if not measured_runs:
            raise RuntimeError("prepared direct-status repeat produced no measured rows")
        component_signature_sec = float(
            statistics.median(float(row["timing_sec"]["component_signature_sec"]) for row in measured_runs)
        )
        elapsed_override = float(statistics.median(float(row["elapsed_sec"]) for row in measured_runs))
        rows = ()
        signature_override = dict(measured_runs[-1]["signature"])
        metadata = dict(measured_runs[-1]["metadata"])
        metadata.update(
            {
                "path": "partner_cupy_prepared_direct_status_union_component_signature_3d",
                "front_door": "v2_8_fixed_radius_graph_component_continuation_3d",
                "front_door_operation": "fixed_radius_graph_component_size_signature_3d",
                "v2_8_front_door_route": True,
                "partition_convergence_hybrid_candidate": True,
                "partition_convergence_hybrid_promoted": False,
                "explicit_candidate_preview": True,
                "current_default_route": False,
                "prepared_direct_status_union_app_mode": True,
                "prepared_direct_status_union_reused": True,
                "prepared_direct_status_union_handle_metadata": prepared_direct_status.to_metadata(),
                "native_engine_summary_contract": "generic_fixed_radius_partition_convergence_direct_status_union_3d",
                "native_execution_path": "partner_cupy_prepared_fixed_radius_direct_status_union_preview_3d",
                "partner": "cupy",
                "partition_cell_factor_user_selection": resolved_partition_cell_factor,
                "partition_pair_enumeration_user_selection": partition_pair_enumeration,
                "partition_pair_enumeration_effective": "device_direct_status_union",
                "partition_pair_enumeration_explicit_override": partition_pair_enumeration != "mode_default",
                "partition_pair_enumeration_ignored_by_direct_status_union": partition_pair_enumeration != "mode_default",
                "partition_pair_enumeration_default_route_changed": False,
                "direct_status_convergence_mode_user_selection": direct_status_convergence_mode,
                "direct_status_convergence_mode_default_route_changed": False,
                "direct_status_single_pass_candidate": direct_status_convergence_mode == "single_pass_candidate",
                "direct_status_single_pass_promoted": False,
                "optix_backend_used": False,
                "rt_core_accelerated": False,
                "materializes_neighbor_summaries": False,
                "materializes_neighbor_rows": False,
                "materializes_python_rows": False,
                "materializes_full_component_labels": False,
                "materializes_partition_pair_rows": False,
                "materializes_near_pair_columns": False,
                "pair_materialization_avoided": True,
                "signature_source": "prepared_direct_status_component_size_signature_column_no_python_row_dicts",
                "validation_reference_kind": "fixed_radius_graph_component_labels_reference_3d",
                "prepared_direct_status_sec": prepared_direct_status_sec,
                "component_signature_sec": component_signature_sec,
                "prepared_direct_status_total_sec": prepared_direct_status_sec + component_signature_sec,
                "prepared_direct_status_repeat_protocol": {
                    "repeat": repeat,
                    "warmup": warmup,
                    "measured_run_count": len(measured_runs),
                    "prepare_sec": prepared_direct_status_sec,
                    "elapsed_sec_median": elapsed_override,
                    "elapsed_sec_total": float(sum(float(row["elapsed_sec"]) for row in measured_runs)),
                    "signatures_stable": len(
                        {json.dumps(row["signature"], sort_keys=True) for row in measured_runs}
                    )
                    == 1,
                },
                "full_dbscan_semantics": False,
                "dbscan_core_border_noise_semantics": False,
                "graph_component_contract_only": True,
                "public_speedup_claim_authorized": False,
                "release_authorized": False,
            }
        )
        if validate:
            reference = rt.build_v2_8_fixed_radius_partition_convergence_component_labels_reference_3d(
                points,
                radius=resolved_radius,
                cell_factor=float(metadata.get("cell_factor", 0.125)),
                partition_summary=None,
            )
            label_values = tuple(int(value) for value in reference["columns"]["component_labels"])
            reference_sizes = sorted(label_values.count(label) for label in set(label_values))
            reference_signature_override = _component_size_signature_payload(reference_sizes)
    elif mode in {
        RT_DBSCAN_PREDICATE_DIRECT_STATUS_APP_MODE,
        RT_DBSCAN_PREDICATE_DIRECT_STATUS_ALL_TRUE_APP_MODE,
        RT_DBSCAN_DECLARED_ALL_TRUE_DIRECT_STATUS_APP_MODE,
    }:
        use_declared_all_predicate = mode == RT_DBSCAN_DECLARED_ALL_TRUE_DIRECT_STATUS_APP_MODE
        require_all_predicate_fast_path = mode in {
            RT_DBSCAN_PREDICATE_DIRECT_STATUS_ALL_TRUE_APP_MODE,
            RT_DBSCAN_DECLARED_ALL_TRUE_DIRECT_STATUS_APP_MODE,
        }
        prepare_start = time.perf_counter()
        output_columns = None
        if not use_declared_all_predicate:
            output_columns = rt.allocate_fixed_radius_count_threshold_3d_partner_device_output_columns(
                len(points),
                partner="cupy",
            )
        prepared_predicate_direct_status = (
            rt.prepare_v2_8_fixed_radius_partition_convergence_direct_status_union_cupy_preview_3d(
                points,
                radius=resolved_radius,
                cell_factor=resolved_partition_cell_factor,
            )
            if use_declared_all_predicate
            else rt.prepare_v2_8_fixed_radius_partition_convergence_predicate_direct_status_union_cupy_preview_3d(
                points,
                radius=resolved_radius,
                cell_factor=resolved_partition_cell_factor,
            )
        )
        prepared_predicate_direct_status_sec = time.perf_counter() - prepare_start
        prepared_runs: list[dict[str, object]] = []
        count_context = (
            nullcontext(None)
            if use_declared_all_predicate
            else rt.prepare_optix_fixed_radius_count_threshold_3d(
                points,
                max_radius=resolved_radius,
            )
        )
        with prepared_predicate_direct_status, count_context as prepared_count:
            if use_declared_all_predicate:
                threshold_result = {
                    "columns": {},
                    "metadata": {
                        "path": "caller_declared_all_true_predicate_no_columns_3d",
                        "predicate_flags_source": "caller_declared_all_true",
                        "predicate_flags_exactness": "caller_asserted_not_rt_count_threshold_verified",
                        "neighbor_count_policy": "not_materialized_all_items_declared_predicate_true",
                        "rt_count_threshold_executed": False,
                        "optix_backend_used_for_threshold": False,
                        "all_predicate_declared": True,
                        "all_predicate_fast_path_expected": True,
                        "predicate_columns_materialized": False,
                        "uses_generic_all_items_direct_status_signature": True,
                        "release_authorized": False,
                        "public_speedup_claim_authorized": False,
                        "route_promotion_authorized": False,
                    },
                }
            else:
                threshold_result = None
            threshold_elapsed = 0.0
            for iteration in range(repeat):
                run_timing: dict[str, float] = {}
                run_start = time.perf_counter()
                if threshold_result is None:
                    threshold_start = time.perf_counter()
                    threshold_result = rt.fixed_radius_count_threshold_3d_optix_prepared_partner_device_columns(
                        prepared_count,
                        points,
                        radius=resolved_radius,
                        threshold=resolved_min_neighbors,
                        partner="cupy",
                        output_columns=output_columns,
                        return_metadata=True,
                    )
                    threshold_elapsed = time.perf_counter() - threshold_start
                run_timing["optix_rt_count_threshold_sec"] = threshold_elapsed if iteration == 0 else 0.0
                signature_start = time.perf_counter()
                if use_declared_all_predicate:
                    result = (
                        rt.run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_direct_status_union_preview_3d(
                            prepared_predicate_direct_status,
                            convergence_mode=direct_status_convergence_mode,
                        )
                    )
                    result_metadata = dict(result["metadata"])
                    result_metadata["all_predicate_fast_path"] = True
                    run_signature = _cluster_signature_from_nonnegative_label_counts(
                        result["columns"]["component_size_signature"],
                        core_count=len(points),
                        noise_count=0,
                    )
                else:
                    result = (
                        rt.run_v2_8_fixed_radius_partition_convergence_predicate_signature_cupy_prepared_direct_status_union_preview_3d(
                            prepared_predicate_direct_status,
                            predicate_flags=threshold_result["columns"]["threshold_flags"],
                            neighbor_counts=threshold_result["columns"]["neighbor_counts"],
                            convergence_mode=direct_status_convergence_mode,
                        )
                    )
                    result_metadata = dict(result["metadata"])
                    run_signature = _cluster_signature_from_cupy_signature_count_columns(result["columns"])
                if require_all_predicate_fast_path and not bool(result_metadata.get("all_predicate_fast_path", False)):
                    raise ValueError(
                        f"{mode} "
                        "requires all_predicate_fast_path; use "
                        "optix_rt_core_grouped_stream_numba_column_signature_3d for mixed predicate rows"
                    )
                run_timing["predicate_direct_status_signature_sec"] = time.perf_counter() - signature_start
                prepared_runs.append(
                    {
                        "iteration": iteration,
                        "is_warmup": iteration < warmup,
                        "elapsed_sec": time.perf_counter() - run_start,
                        "timing_sec": run_timing,
                        "signature": run_signature,
                        "rows": (),
                        "metadata": result_metadata,
                        "threshold_metadata": dict(threshold_result["metadata"]),
                    }
                )
        measured_runs = [row for row in prepared_runs if not bool(row["is_warmup"])]
        if not measured_runs:
            raise RuntimeError("RT-DBSCAN predicate direct-status repeat produced no measured rows")
        phase_names = sorted({name for row in measured_runs for name in row["timing_sec"]})
        timing_breakdown_sec = {
            name: float(statistics.median(float(row["timing_sec"][name]) for row in measured_runs if name in row["timing_sec"]))
            for name in phase_names
        }
        timing_breakdown_sec["prepare_predicate_direct_status_sec"] = prepared_predicate_direct_status_sec
        elapsed_override = float(statistics.median(float(row["elapsed_sec"]) for row in measured_runs))
        signature_override = dict(measured_runs[-1]["signature"])
        rows = measured_runs[-1]["rows"]
        metadata = dict(measured_runs[-1]["metadata"])
        threshold_metadata = dict(measured_runs[-1]["threshold_metadata"])
        metadata.update(
            {
                "path": (
                    "partner_cupy_declared_all_true_predicate_direct_status_column_signature_3d"
                    if use_declared_all_predicate
                    else (
                        "optix_rt_count_threshold_cupy_predicate_direct_status_all_true_column_signature_3d"
                        if require_all_predicate_fast_path
                        else "optix_rt_count_threshold_cupy_predicate_direct_status_column_signature_3d"
                    )
                ),
                "front_door_operation": "fixed_radius_graph_predicate_component_size_signature_3d",
                "native_engine_summary_contract": (
                    "generic_all_items_direct_status_component_signature_wrapped_as_all_predicate_signature"
                    if use_declared_all_predicate
                    else "generic_prepared_fixed_radius_count_threshold_3d_device_columns_plus_predicate_direct_status_union"
                ),
                "native_execution_path": (
                    "prepared_direct_status_union_component_signature_wrapped_as_all_predicate_signature"
                    if use_declared_all_predicate
                    else "prepared_rt_core_count_threshold_3d_then_partner_predicate_direct_status_union_preview"
                ),
                "optix_backend_used": not use_declared_all_predicate,
                "partner": "cupy",
                "rt_core_accelerated": not use_declared_all_predicate,
                "predicate_flags_source": (
                    "caller_declared_all_true" if use_declared_all_predicate else "optix_rt_count_threshold"
                ),
                "rt_count_threshold_executed": not use_declared_all_predicate,
                "caller_declared_predicate_columns": False,
                "predicate_columns_materialized": not use_declared_all_predicate,
                "uses_generic_all_items_direct_status_signature": use_declared_all_predicate,
                "caller_declared_predicate_columns_require_external_proof": use_declared_all_predicate,
                "materializes_neighbor_summaries": False,
                "materializes_neighbor_rows": False,
                "materializes_python_rows": False,
                "signature_source": "partner_column_signature_counts_no_python_row_dicts",
                "predicate_direct_status_candidate": True,
                "predicate_direct_status_promoted": False,
                "all_predicate_only_mode": require_all_predicate_fast_path,
                "all_predicate_fast_path_required": require_all_predicate_fast_path,
                "all_predicate_fast_path_observed": bool(metadata.get("all_predicate_fast_path", False)),
                "mixed_predicate_fail_closed": require_all_predicate_fast_path,
                "mixed_predicate_fallback_route": RT_DBSCAN_GROUPED_STREAM_NUMBA_APP_MODE,
                "hidden_dispatch_allowed": False,
                "route_promotion_authorized": False,
                "direct_status_convergence_mode_user_selection": direct_status_convergence_mode,
                "direct_status_convergence_mode_default_route_changed": False,
                "automatic_convergence_mode_selection_authorized": False,
                "neighbor_count_policy": (
                    "not_materialized_all_items_declared_predicate_true"
                    if use_declared_all_predicate
                    else "threshold_capped_at_min_neighbors_not_exact_full_degree"
                ),
                "threshold_metadata": threshold_metadata,
                "prepared_predicate_direct_status_sec": prepared_predicate_direct_status_sec,
                "predicate_direct_status_signature_sec": timing_breakdown_sec["predicate_direct_status_signature_sec"],
                "prepared_predicate_direct_status_total_sec": (
                    prepared_predicate_direct_status_sec
                    + timing_breakdown_sec["predicate_direct_status_signature_sec"]
                ),
                "prepared_query_repeat_protocol": {
                    "repeat": repeat,
                    "warmup": warmup,
                    "measured_iterations": len(measured_runs),
                    "prepare_sec": prepared_predicate_direct_status_sec,
                    "median_elapsed_sec": elapsed_override,
                    "signatures_stable": len(
                        {json.dumps(row["signature"], sort_keys=True) for row in measured_runs}
                    )
                    == 1,
                },
                "timing_breakdown_sec": timing_breakdown_sec,
                "dbscan_core_border_noise_semantics": True,
                "native_dbscan_abi_added": False,
                "release_authorized": False,
                "public_speedup_claim_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
            }
        )
    elif mode == "optix_core_flags_cupy_grid_components_3d":
        if resolved_min_neighbors > 64:
            raise ValueError("optix_core_flags_cupy_grid_components_3d currently requires min_neighbors <= 64")
        optix_start = time.perf_counter()
        with rt.prepare_optix_fixed_radius_neighbors_3d(points, max_radius=resolved_radius) as prepared:
            summaries = prepared.run_ranked_summary(
                points,
                radius=resolved_radius,
                k_max=max(1, resolved_min_neighbors),
            )
        optix_elapsed = time.perf_counter() - optix_start
        core_columns = _optix_ranked_summaries_to_cupy_core_columns(
            points,
            summaries,
            min_neighbors=resolved_min_neighbors,
        )
        point_columns = rt.point_rows_to_partner_columns(points, partner="cupy")
        continuation_start = time.perf_counter()
        result = rt.radius_graph_components_3d_cupy_grid_partner_columns(
            point_columns,
            radius=resolved_radius,
            min_neighbors=resolved_min_neighbors,
            partner="cupy",
            core_flags=core_columns["core_flags"],
            neighbor_counts=core_columns["neighbor_counts"],
            core_flag_source="optix_ranked_fixed_radius_summary_threshold",
            return_metadata=True,
        )
        continuation_elapsed = time.perf_counter() - continuation_start
        rows = _rows_from_partner_columns(result["columns"], partner="cupy")
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "path": "optix_core_flags_cupy_grid_radius_graph_components_3d",
                "optix_core_flag_summary_rows": core_columns["summary_rows"],
                "optix_core_flag_sec": optix_elapsed,
                "cupy_component_continuation_sec": continuation_elapsed,
                "native_engine_summary_contract": "generic_prepared_ranked_fixed_radius_neighbor_summaries_3d",
                "native_execution_path": "prepared_uniform_cell_cuda_grid_3d",
                "optix_backend_used": True,
                "rt_core_accelerated": False,
                "materializes_neighbor_summaries": True,
                "materializes_neighbor_rows": False,
                "neighbor_count_policy": "threshold_capped_at_min_neighbors_not_exact_full_degree",
            }
        )
    elif mode == "optix_rt_core_flags_cupy_grid_components_3d":
        point_columns = rt.point_rows_to_partner_columns(points, partner="cupy")
        output_columns = rt.allocate_fixed_radius_count_threshold_3d_partner_device_output_columns(
            len(points),
            partner="cupy",
        )
        optix_start = time.perf_counter()
        with rt.prepare_optix_fixed_radius_count_threshold_3d(points, max_radius=resolved_radius) as prepared:
            threshold_result = rt.fixed_radius_count_threshold_3d_optix_prepared_partner_device_columns(
                prepared,
                points,
                radius=resolved_radius,
                threshold=resolved_min_neighbors,
                partner="cupy",
                output_columns=output_columns,
                return_metadata=True,
            )
        optix_elapsed = time.perf_counter() - optix_start
        continuation_start = time.perf_counter()
        result = rt.radius_graph_components_3d_cupy_grid_partner_columns(
            point_columns,
            radius=resolved_radius,
            min_neighbors=resolved_min_neighbors,
            partner="cupy",
            core_flags=threshold_result["columns"]["threshold_flags"],
            neighbor_counts=threshold_result["columns"]["neighbor_counts"],
            core_flag_source="optix_rt_fixed_radius_count_threshold_3d_device_outputs",
            return_metadata=True,
        )
        continuation_elapsed = time.perf_counter() - continuation_start
        rows = _rows_from_partner_columns(result["columns"], partner="cupy")
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "path": "optix_rt_count_threshold_cupy_grid_radius_graph_components_3d",
                "optix_rt_count_threshold_sec": optix_elapsed,
                "cupy_component_continuation_sec": continuation_elapsed,
                "native_engine_summary_contract": "generic_prepared_fixed_radius_count_threshold_3d_device_columns",
                "native_execution_path": "prepared_rt_core_count_threshold_3d",
                "optix_backend_used": True,
                "rt_core_accelerated": True,
                "materializes_neighbor_summaries": False,
                "materializes_neighbor_rows": False,
                "neighbor_count_policy": "threshold_capped_at_min_neighbors_not_exact_full_degree",
                "threshold_metadata": threshold_result["metadata"],
            }
        )
    elif mode == "optix_rt_core_flags_cupy_prepared_grid_components_3d":
        with rt.prepare_optix_cupy_radius_graph_components_3d(
            points,
            radius=resolved_radius,
            partner="cupy",
        ) as prepared:
            result = rt.radius_graph_components_3d_optix_cupy_prepared_partner_columns(
                prepared,
                min_neighbors=resolved_min_neighbors,
                return_metadata=True,
            )
        rows = _rows_from_partner_columns(result["columns"], partner="cupy")
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "path": "optix_rt_count_threshold_cupy_prepared_grid_radius_graph_components_3d",
                "native_engine_summary_contract": "generic_prepared_fixed_radius_count_threshold_3d_device_columns",
                "native_execution_path": "prepared_rt_core_count_threshold_3d",
                "optix_backend_used": True,
                "rt_core_accelerated": True,
                "materializes_neighbor_summaries": False,
                "materializes_neighbor_rows": False,
                "neighbor_count_policy": "threshold_capped_at_min_neighbors_not_exact_full_degree",
            }
        )
    elif mode in {
        "optix_rt_core_flags_numba_prepared_grid_components_3d",
        "optix_rt_core_flags_numba_prepared_grid_column_signature_3d",
    }:
        column_signature_mode = mode == "optix_rt_core_flags_numba_prepared_grid_column_signature_3d"
        prepare_start = time.perf_counter()
        point_columns = rt.point_rows_to_partner_columns(points, partner="numba")
        prepared_grid = rt.prepare_radius_graph_components_3d_numba_grid_partner_columns(
            point_columns,
            radius=resolved_radius,
            partner="numba",
        )
        output_columns = rt.allocate_fixed_radius_count_threshold_3d_partner_device_output_columns(
            len(points),
            partner="numba",
        )
        prepared_query_runs: list[dict[str, object]] = []
        with rt.prepare_optix_fixed_radius_count_threshold_3d(points, max_radius=resolved_radius) as prepared:
            prepare_sec = time.perf_counter() - prepare_start
            for iteration in range(repeat):
                run_timing: dict[str, float] = {}
                run_start = time.perf_counter()
                optix_start = time.perf_counter()
                threshold_result = rt.fixed_radius_count_threshold_3d_optix_prepared_partner_device_columns(
                    prepared,
                    points,
                    radius=resolved_radius,
                    threshold=resolved_min_neighbors,
                    partner="numba",
                    output_columns=output_columns,
                    return_metadata=True,
                )
                optix_elapsed = time.perf_counter() - optix_start
                continuation_start = time.perf_counter()
                result = rt.radius_graph_components_3d_numba_prepared_grid_partner_columns(
                    prepared_grid,
                    min_neighbors=resolved_min_neighbors,
                    core_flags=threshold_result["columns"]["threshold_flags"],
                    neighbor_counts=threshold_result["columns"]["neighbor_counts"],
                    core_flag_source="optix_rt_fixed_radius_count_threshold_3d_numba_device_outputs",
                    return_metadata=True,
                )
                continuation_elapsed = time.perf_counter() - continuation_start
                run_timing["optix_rt_count_threshold_sec"] = optix_elapsed
                run_timing["numba_component_continuation_sec"] = continuation_elapsed
                if column_signature_mode:
                    signature_start = time.perf_counter()
                    run_signature = _cluster_signature_from_partner_columns(result["columns"], partner="numba")
                    run_timing["column_signature_sec"] = time.perf_counter() - signature_start
                    run_rows = ()
                else:
                    rows_start = time.perf_counter()
                    run_rows = _rows_from_partner_columns(result["columns"], partner="numba")
                    run_timing["rows_materialization_sec"] = time.perf_counter() - rows_start
                    densify_start = time.perf_counter()
                    run_rows = _densify_cluster_labels(run_rows)
                    run_timing["densify_cluster_labels_sec"] = time.perf_counter() - densify_start
                    run_signature = cluster_signature(run_rows)
                prepared_query_runs.append(
                    {
                        "iteration": iteration,
                        "is_warmup": iteration < warmup,
                        "elapsed_sec": time.perf_counter() - run_start,
                        "timing_sec": run_timing,
                        "signature": run_signature,
                        "rows": run_rows,
                        "metadata": dict(result["metadata"]),
                        "threshold_metadata": dict(threshold_result["metadata"]),
                    }
                )
        measured_runs = [row for row in prepared_query_runs if not bool(row["is_warmup"])]
        if not measured_runs:
            raise RuntimeError("RT-DBSCAN OptiX+Numba repeat produced no measured rows")
        phase_names = sorted({name for row in measured_runs for name in row["timing_sec"]})
        timing_breakdown_sec = {
            name: float(statistics.median(float(row["timing_sec"][name]) for row in measured_runs if name in row["timing_sec"]))
            for name in phase_names
        }
        timing_total_sec = {
            name: float(sum(float(row["timing_sec"][name]) for row in measured_runs if name in row["timing_sec"]))
            for name in phase_names
        }
        elapsed_override = float(statistics.median(float(row["elapsed_sec"]) for row in measured_runs))
        elapsed_total_sec = float(sum(float(row["elapsed_sec"]) for row in measured_runs))
        signature_override = dict(measured_runs[-1]["signature"])
        rows = measured_runs[-1]["rows"]
        metadata = dict(measured_runs[-1]["metadata"])
        threshold_metadata = dict(measured_runs[-1]["threshold_metadata"])
        metadata.update(
            {
                "path": (
                    "optix_rt_count_threshold_numba_prepared_grid_radius_graph_column_signature_3d"
                    if column_signature_mode
                    else "optix_rt_count_threshold_numba_prepared_grid_radius_graph_components_3d"
                ),
                "optix_rt_count_threshold_sec": timing_breakdown_sec["optix_rt_count_threshold_sec"],
                "numba_component_continuation_sec": timing_breakdown_sec["numba_component_continuation_sec"],
                "native_engine_summary_contract": "generic_prepared_fixed_radius_count_threshold_3d_device_columns",
                "native_execution_path": "prepared_rt_core_count_threshold_3d",
                "optix_backend_used": True,
                "rt_core_accelerated": True,
                "materializes_neighbor_summaries": False,
                "materializes_neighbor_rows": False,
                "materializes_python_rows": not column_signature_mode,
                "signature_source": (
                    "partner_column_arrays_no_python_row_dicts"
                    if column_signature_mode
                    else "python_row_dicts_after_label_densification"
                ),
                "neighbor_count_policy": "threshold_capped_at_min_neighbors_not_exact_full_degree",
                "threshold_metadata": threshold_metadata,
                "prepared_query_repeat_protocol": {
                    "repeat": repeat,
                    "warmup": warmup,
                    "measured_iterations": len(measured_runs),
                    "prepare_sec": prepare_sec,
                    "median_elapsed_sec": elapsed_override,
                    "elapsed_sec_total": elapsed_total_sec,
                },
                "timing_total_sec": timing_total_sec,
            }
        )
    elif mode == "optix_rt_core_adjacency_cupy_components_3d":
        with rt.prepare_optix_cupy_radius_graph_adjacency_3d(
            points,
            radius=resolved_radius,
            partner="cupy",
        ) as prepared:
            result = rt.radius_graph_components_3d_optix_cupy_prepared_adjacency_partner_columns(
                prepared,
                min_neighbors=resolved_min_neighbors,
                return_metadata=True,
            )
        rows = _rows_from_partner_columns(result["columns"], partner="cupy")
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "path": "optix_rt_adjacency_cupy_radius_graph_components_3d",
                "native_engine_summary_contract": "generic_prepared_fixed_radius_adjacency_3d_device_columns",
                "native_execution_path": "prepared_rt_core_adjacency_3d",
                "optix_backend_used": True,
                "rt_core_accelerated": True,
                "materializes_neighbor_summaries": False,
                "materializes_neighbor_rows": False,
                "materializes_directed_adjacency_stream": True,
                "neighbor_count_policy": "exact_full_degree_from_prepared_rt_adjacency_stream",
            }
        )
    elif mode == "optix_rt_core_chunked_adjacency_cupy_components_3d":
        with rt.prepare_optix_cupy_radius_graph_chunked_adjacency_3d(
            points,
            radius=resolved_radius,
            partner="cupy",
            max_directed_edges_per_chunk=chunk_adjacency_edge_budget,
            reuse_neighbor_index_workspace=reuse_chunk_neighbor_index_workspace,
            neighbor_index_workspace_pool_size=chunk_neighbor_index_workspace_pool_size,
        ) as prepared:
            result = rt.radius_graph_components_3d_optix_cupy_prepared_chunked_adjacency_partner_columns(
                prepared,
                min_neighbors=resolved_min_neighbors,
                return_metadata=True,
            )
        rows = _rows_from_partner_columns(result["columns"], partner="cupy")
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "path": "optix_rt_chunked_adjacency_cupy_radius_graph_components_3d",
                "native_engine_summary_contract": "generic_prepared_fixed_radius_adjacency_3d_device_columns",
                "native_execution_path": "prepared_rt_core_chunked_adjacency_3d",
                "optix_backend_used": True,
                "rt_core_accelerated": True,
                "materializes_neighbor_summaries": False,
                "materializes_neighbor_rows": False,
                "materializes_directed_adjacency_stream": False,
                "materializes_bounded_directed_adjacency_chunks": True,
                "neighbor_count_policy": "exact_full_degree_from_prepared_rt_chunked_adjacency_stream",
            }
        )
    elif mode == "optix_rt_core_grouped_stream_cupy_components_3d" or mode in {
        "optix_rt_core_grouped_stream_cupy_column_signature_3d",
        "optix_rt_core_grouped_stream_numba_components_3d",
        "optix_rt_core_grouped_stream_numba_column_signature_3d",
        "optix_rt_core_grouped_stream_blocked_cupy_components_3d",
        "optix_rt_core_grouped_stream_blocked_cupy_column_signature_3d",
        "optix_rt_core_grouped_stream_blocked_numba_components_3d",
        "optix_rt_core_grouped_stream_blocked_numba_column_signature_3d",
    }:
        blocked_grouped_stream = mode.startswith("optix_rt_core_grouped_stream_blocked")
        grouped_stream_partner = "numba" if "_numba_" in mode else "cupy"
        resolved_query_block_size = (
            int(grouped_union_query_block_size)
            if grouped_union_query_block_size is not None
            else DEFAULT_GROUPED_UNION_QUERY_BLOCK_SIZE
        )
        column_signature_mode = mode in {
            "optix_rt_core_grouped_stream_cupy_column_signature_3d",
            "optix_rt_core_grouped_stream_numba_column_signature_3d",
            "optix_rt_core_grouped_stream_blocked_cupy_column_signature_3d",
            "optix_rt_core_grouped_stream_blocked_numba_column_signature_3d",
        }
        prepare_start = time.perf_counter()
        prepared_query_runs: list[dict[str, object]] = []
        prepare_sec = 0.0
        with rt.prepare_v2_8_fixed_radius_graph_component_continuation_3d(
            points,
            radius=resolved_radius,
            component_threshold=resolved_min_neighbors,
            backend="optix",
            partner=grouped_stream_partner,
            strategy="grouped_stream",
            grouped_union_query_block_size=resolved_query_block_size if blocked_grouped_stream else None,
            grouped_union_same_root_culling=grouped_union_same_root_culling,
            grouped_union_direct_side_effect=grouped_union_direct_side_effect,
        ) as prepared:
            prepare_sec = time.perf_counter() - prepare_start
            for iteration in range(repeat):
                run_timing: dict[str, float] = {}
                run_start = time.perf_counter()
                adapter_start = time.perf_counter()
                if column_signature_mode and grouped_stream_partner == "numba":
                    result = rt.fixed_radius_graph_component_size_signature_3d_v2_8(
                        prepared,
                        component_threshold=resolved_min_neighbors,
                        return_metadata=True,
                    )
                else:
                    result = rt.fixed_radius_graph_component_labels_3d_v2_8(
                        prepared,
                        component_threshold=resolved_min_neighbors,
                        return_metadata=True,
                    )
                run_timing["adapter_run_sec"] = time.perf_counter() - adapter_start
                signature_strategy = None
                if column_signature_mode:
                    signature_start = time.perf_counter()
                    if grouped_stream_partner == "numba" and "label_counts" in result["columns"]:
                        run_signature = _cluster_signature_from_numba_signature_count_columns(
                            result["columns"],
                        )
                        signature_strategy = "numba_direct_component_signature_counts"
                    elif grouped_stream_partner == "numba":
                        run_signature = _cluster_signature_from_numba_label_columns(
                            result["columns"],
                            point_count=len(points),
                        )
                        signature_strategy = "numba_label_count_and_flag_count_label_columns"
                    else:
                        run_signature = _cluster_signature_from_partner_columns(
                            result["columns"],
                            partner=grouped_stream_partner,
                        )
                        signature_strategy = "host_column_materialized_signature"
                    run_timing["column_signature_sec"] = time.perf_counter() - signature_start
                    run_rows = ()
                else:
                    rows_start = time.perf_counter()
                    run_rows = _rows_from_partner_columns(result["columns"], partner=grouped_stream_partner)
                    run_timing["rows_materialization_sec"] = time.perf_counter() - rows_start
                    densify_start = time.perf_counter()
                    run_rows = _densify_cluster_labels(run_rows)
                    run_timing["densify_cluster_labels_sec"] = time.perf_counter() - densify_start
                    run_signature = cluster_signature(run_rows)
                prepared_query_runs.append(
                    {
                        "iteration": iteration,
                        "is_warmup": iteration < warmup,
                        "elapsed_sec": time.perf_counter() - run_start,
                        "timing_sec": run_timing,
                        "signature": run_signature,
                        "signature_strategy": signature_strategy,
                        "rows": run_rows,
                        "metadata": dict(result["metadata"]),
                    }
                )
        measured_runs = [row for row in prepared_query_runs if not bool(row["is_warmup"])]
        if not measured_runs:
            raise RuntimeError("RT-DBSCAN grouped-stream repeat produced no measured rows")
        phase_names = sorted({name for row in measured_runs for name in row["timing_sec"]})
        timing_breakdown_sec = {
            name: float(statistics.median(float(row["timing_sec"][name]) for row in measured_runs if name in row["timing_sec"]))
            for name in phase_names
        }
        timing_breakdown_sec["prepare_sec"] = prepare_sec
        elapsed_override = float(statistics.median(float(row["elapsed_sec"]) for row in measured_runs))
        signature_override = dict(measured_runs[-1]["signature"])
        rows = measured_runs[-1]["rows"]
        result = {"metadata": dict(measured_runs[-1]["metadata"])}
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "path": (
                    "optix_rt_grouped_stream_blocked_cupy_radius_graph_column_signature_3d"
                    if mode == "optix_rt_core_grouped_stream_blocked_cupy_column_signature_3d"
                    else "optix_rt_grouped_stream_blocked_numba_radius_graph_column_signature_3d"
                    if mode == "optix_rt_core_grouped_stream_blocked_numba_column_signature_3d"
                    else "optix_rt_grouped_stream_blocked_cupy_radius_graph_components_3d"
                    if mode == "optix_rt_core_grouped_stream_blocked_cupy_components_3d"
                    else "optix_rt_grouped_stream_blocked_numba_radius_graph_components_3d"
                    if mode == "optix_rt_core_grouped_stream_blocked_numba_components_3d"
                    else "optix_rt_grouped_stream_numba_radius_graph_column_signature_3d"
                    if mode == "optix_rt_core_grouped_stream_numba_column_signature_3d"
                    else "optix_rt_grouped_stream_numba_radius_graph_components_3d"
                    if mode == "optix_rt_core_grouped_stream_numba_components_3d"
                    else "optix_rt_grouped_stream_cupy_radius_graph_column_signature_3d"
                    if mode == "optix_rt_core_grouped_stream_cupy_column_signature_3d"
                    else "optix_rt_grouped_stream_cupy_radius_graph_components_3d"
                ),
                "front_door": "v2_8_fixed_radius_graph_component_continuation_3d",
                "front_door_operation": "fixed_radius_graph_component_labels_3d",
                "v2_8_front_door_route": True,
                "native_engine_summary_contract": (
                    "generic_prepared_fixed_radius_grouped_union_3d_self_range_device_workspaces"
                    if blocked_grouped_stream
                    else "generic_prepared_fixed_radius_grouped_union_3d_self_device_workspaces"
                ),
                "native_execution_path": (
                    "prepared_rt_core_grouped_union_3d_self_query_blocked_ranges"
                    if blocked_grouped_stream
                    else "prepared_rt_core_grouped_union_3d_self_query"
                ),
                "query_source": (
                    "prepared_search_points_self_query_device_range"
                    if blocked_grouped_stream
                    else "prepared_search_points_self_query_device"
                ),
                "grouped_union_query_blocked_candidate": blocked_grouped_stream,
                "grouped_union_query_block_size": resolved_query_block_size if blocked_grouped_stream else None,
                "grouped_union_same_root_culling_enabled": grouped_union_same_root_culling,
                "grouped_union_direct_side_effect_enabled": grouped_union_direct_side_effect,
                "optix_backend_used": True,
                "partner": grouped_stream_partner,
                "rt_core_accelerated": True,
                "materializes_neighbor_summaries": False,
                "materializes_neighbor_rows": False,
                "materializes_directed_adjacency_stream": False,
                "materializes_bounded_directed_adjacency_chunks": False,
                "materializes_python_rows": mode in {
                    "optix_rt_core_grouped_stream_cupy_components_3d",
                    "optix_rt_core_grouped_stream_numba_components_3d",
                    "optix_rt_core_grouped_stream_blocked_cupy_components_3d",
                    "optix_rt_core_grouped_stream_blocked_numba_components_3d",
                },
                "signature_source": (
                    "partner_column_arrays_no_python_row_dicts"
                    if column_signature_mode
                    else "python_row_dicts_after_label_densification"
                ),
                "column_signature_strategy": (
                    measured_runs[-1].get("signature_strategy") if column_signature_mode else None
                ),
                "column_signature_uses_numba_segmented_count": (
                    measured_runs[-1].get("signature_strategy") == "numba_segmented_count_all_core_labels"
                    if column_signature_mode
                    else False
                ),
                "column_signature_uses_numba_label_count_and_flag_count": (
                    measured_runs[-1].get("signature_strategy")
                    == "numba_label_count_and_flag_count_label_columns"
                    if column_signature_mode
                    else False
                ),
                "column_signature_uses_numba_direct_component_signature": (
                    measured_runs[-1].get("signature_strategy")
                    == "numba_direct_component_signature_counts"
                    if column_signature_mode
                    else False
                ),
                "column_signature_materializes_point_ids": (
                    measured_runs[-1].get("signature_strategy")
                    not in {
                        "numba_segmented_count_all_core_labels",
                        "numba_label_count_and_flag_count_label_columns",
                        "numba_direct_component_signature_counts",
                    }
                    if column_signature_mode
                    else None
                ),
                "column_signature_materializes_core_flags": (
                    measured_runs[-1].get("signature_strategy")
                    not in {
                        "numba_segmented_count_all_core_labels",
                        "numba_label_count_and_flag_count_label_columns",
                        "numba_direct_component_signature_counts",
                    }
                    if column_signature_mode
                    else None
                ),
                "neighbor_count_policy": "threshold_capped_at_min_neighbors_not_exact_full_degree",
                "prepared_query_repeat_protocol": {
                    "repeat": repeat,
                    "warmup": warmup,
                    "measured_run_count": len(measured_runs),
                    "elapsed_sec_median": elapsed_override,
                    "elapsed_sec_total": float(sum(float(row["elapsed_sec"]) for row in measured_runs)),
                    "signatures_stable": len(
                        {json.dumps(row["signature"], sort_keys=True) for row in measured_runs}
                    )
                    == 1,
                },
            }
        )
    elif mode == "optix_rt_core_flags_cupy_microcell_graph_components_3d":
        point_columns = rt.point_rows_to_partner_columns(points, partner="cupy")
        output_columns = rt.allocate_fixed_radius_count_threshold_3d_partner_device_output_columns(
            len(points),
            partner="cupy",
        )
        optix_start = time.perf_counter()
        with rt.prepare_optix_fixed_radius_count_threshold_3d(points, max_radius=resolved_radius) as prepared:
            threshold_result = rt.fixed_radius_count_threshold_3d_optix_prepared_partner_device_columns(
                prepared,
                points,
                radius=resolved_radius,
                threshold=resolved_min_neighbors,
                partner="cupy",
                output_columns=output_columns,
                return_metadata=True,
            )
        optix_elapsed = time.perf_counter() - optix_start
        continuation_start = time.perf_counter()
        result = rt.radius_graph_components_3d_cupy_microcell_graph_partner_columns(
            point_columns,
            radius=resolved_radius,
            min_neighbors=resolved_min_neighbors,
            partner="cupy",
            core_flags=threshold_result["columns"]["threshold_flags"],
            neighbor_counts=threshold_result["columns"]["neighbor_counts"],
            core_flag_source="optix_rt_fixed_radius_count_threshold_3d_device_outputs",
            return_metadata=True,
        )
        continuation_elapsed = time.perf_counter() - continuation_start
        rows = _rows_from_partner_columns(result["columns"], partner="cupy")
        metadata = dict(result["metadata"])
        metadata.update(
            {
                "path": "optix_rt_count_threshold_cupy_microcell_radius_graph_components_3d",
                "optix_rt_count_threshold_sec": optix_elapsed,
                "cupy_component_continuation_sec": continuation_elapsed,
                "native_engine_summary_contract": "generic_prepared_fixed_radius_count_threshold_3d_device_columns",
                "native_execution_path": "prepared_rt_core_count_threshold_3d",
                "optix_backend_used": True,
                "rt_core_accelerated": True,
                "materializes_neighbor_summaries": False,
                "materializes_neighbor_rows": False,
                "neighbor_count_policy": "threshold_capped_at_min_neighbors_not_exact_full_degree",
                "threshold_metadata": threshold_result["metadata"],
            }
        )
    elif mode == "partner_core_flags_3d":
        point_columns = rt.point_rows_to_partner_columns(points, partner=partner)
        result = rt.fixed_radius_count_threshold_3d_partner_columns(
            point_columns,
            point_columns,
            radius=resolved_radius,
            threshold=resolved_min_neighbors,
            partner=partner,
            return_metadata=True,
        )
        columns = result["columns"]
        if partner == "torch":
            point_ids = columns["query_ids"].detach().cpu().tolist()
            counts = columns["neighbor_counts"].detach().cpu().tolist()
            flags = columns["threshold_flags"].detach().cpu().tolist()
        else:
            import cupy

            point_ids = cupy.asnumpy(columns["query_ids"]).tolist()
            counts = cupy.asnumpy(columns["neighbor_counts"]).tolist()
            flags = cupy.asnumpy(columns["threshold_flags"]).tolist()
        rows = tuple(
            {
                "point_id": int(point_id),
                "cluster_id": 1 if int(flag) else NOISE_CLUSTER_ID,
                "is_core": bool(flag),
                "neighbor_count": int(count),
            }
            for point_id, count, flag in zip(point_ids, counts, flags)
        )
        metadata = dict(result["metadata"])
        metadata["path"] = "generic_3d_core_flag_only_not_full_dbscan"
    elif mode == "optix_prepared_rows":
        with rt.prepare_optix_fixed_radius_neighbors_3d(points, max_radius=resolved_radius) as prepared:
            neighbor_rows = prepared.run_exact(points, radius=resolved_radius, k_max=len(points))
        rows = _component_rows_from_neighbor_rows(points, neighbor_rows, min_neighbors=resolved_min_neighbors)
        metadata = {
            "path": "optix_prepared_fixed_radius_neighbor_rows_3d",
            "neighbor_row_count": len(neighbor_rows),
            "native_engine_row_contract": "generic_prepared_fixed_radius_neighbors_3d_rows",
            "native_execution_path": "prepared_uniform_cell_cuda_grid_3d",
            "optix_backend_used": True,
            "rt_core_accelerated": False,
            "materializes_neighbor_rows": True,
        }
    else:
        raise ValueError("unsupported mode")
    if signature_override is None:
        densify_start = time.perf_counter()
        rows = _densify_cluster_labels(rows)
        if timing_breakdown_sec is not None:
            timing_breakdown_sec["densify_cluster_labels_sec"] = time.perf_counter() - densify_start
    elapsed = elapsed_override if elapsed_override is not None else time.perf_counter() - start
    if timing_breakdown_sec is not None:
        metadata["benchmark_timing_breakdown"] = _build_grouped_stream_timing_breakdown(
            timing_breakdown_sec,
            metadata,
            elapsed_sec=elapsed,
        )

    signature = signature_override if signature_override is not None else cluster_signature(rows)
    reference_signature = None
    matches_reference = None
    if validate and reference_signature_override is not None:
        reference_signature = reference_signature_override
        matches_reference = signature == reference_signature
    elif validate and mode != "cpu_reference":
        reference_rows, _ = cpu_spatial_bucket_dbscan(points, radius=resolved_radius, min_neighbors=resolved_min_neighbors)
        reference_signature = cluster_signature(reference_rows)
        matches_reference = signature == reference_signature
    elif mode == "cpu_reference":
        reference_signature = signature
        matches_reference = True

    payload = {
        "app": "rt_dbscan_benchmark",
        "paper": {
            "title": "RT-DBSCAN: Accelerating DBSCAN using Ray Tracing Hardware",
            "venue": "IPDPS 2023",
            "authors": ["Vani Nagarajan", "Milind Kulkarni"],
            "doi": "10.1109/IPDPS54959.2023.00100",
        },
        "mode": mode,
        "dataset": dataset,
        "point_count": len(points),
        "radius": resolved_radius,
        "min_neighbors": resolved_min_neighbors,
        "seed": seed,
        "elapsed_sec": elapsed,
        "signature": signature,
        "reference_signature": reference_signature,
        "matches_reference": matches_reference,
        "metadata": metadata,
        "claim_boundary": {
            "paper_dataset_reproduction": False,
            "paper_speedup_claim_authorized": False,
            "native_dbscan_abi_added": False,
            "rt_core_accelerated": bool(metadata.get("rt_core_accelerated", False)),
            "full_dbscan": bool(metadata.get("full_dbscan_semantics", mode != "partner_core_flags_3d")),
            "host_bucket_index_used": bool(metadata.get("host_bucket_index_used", False)),
        },
    }
    if include_rows:
        payload["rows"] = rows
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="RT-DBSCAN-inspired current RTDL benchmark app.")
    parser.add_argument(
        "--mode",
        choices=(
            "cpu_reference",
            "planned_rt_dbscan",
            "planned_rt_dbscan_continuation",
            "rtdl_cpu_rows",
            "embree_prepared_rows",
            "partner_spatial_bucket_3d",
            "partner_cupy_grid_components_3d",
            "partner_numba_grid_components_3d",
            "partner_cupy_prepared_grid_components_3d",
            "partner_numba_prepared_grid_components_3d",
            "partner_cupy_prepared_adjacency_components_3d",
            "partner_cupy_partition_convergence_component_signature_3d",
            "partner_cupy_prepared_partition_convergence_component_signature_3d",
            "partner_cupy_prepared_direct_status_union_component_signature_3d",
            "optix_rt_core_flags_cupy_predicate_direct_status_column_signature_3d",
            "optix_rt_core_flags_cupy_predicate_direct_status_all_true_column_signature_3d",
            "partner_cupy_declared_all_true_predicate_direct_status_column_signature_3d",
            "embree_core_flags_numba_prepared_grid_column_signature_3d",
            "optix_core_flags_cupy_grid_components_3d",
            "optix_rt_core_flags_cupy_grid_components_3d",
            "optix_rt_core_flags_cupy_prepared_grid_components_3d",
            "optix_rt_core_flags_numba_prepared_grid_components_3d",
            "optix_rt_core_flags_numba_prepared_grid_column_signature_3d",
            "optix_rt_core_adjacency_cupy_components_3d",
            "optix_rt_core_chunked_adjacency_cupy_components_3d",
            "optix_rt_core_grouped_stream_cupy_components_3d",
            "optix_rt_core_grouped_stream_cupy_column_signature_3d",
            "optix_rt_core_grouped_stream_numba_components_3d",
            "optix_rt_core_grouped_stream_numba_column_signature_3d",
            "optix_rt_core_grouped_stream_blocked_cupy_components_3d",
            "optix_rt_core_grouped_stream_blocked_cupy_column_signature_3d",
            "optix_rt_core_grouped_stream_blocked_numba_components_3d",
            "optix_rt_core_grouped_stream_blocked_numba_column_signature_3d",
            "optix_rt_core_flags_cupy_microcell_graph_components_3d",
            "partner_core_flags_3d",
            "optix_prepared_rows",
        ),
        default="cpu_reference",
    )
    parser.add_argument("--dataset", choices=tuple(DEFAULT_DATASET_CONFIG), default="tiny")
    parser.add_argument("--point-count", type=int, default=None)
    parser.add_argument("--radius", type=float, default=None)
    parser.add_argument("--min-neighbors", type=int, default=None)
    parser.add_argument("--seed", type=int, default=20260519)
    parser.add_argument("--partner", choices=("torch", "cupy", "numba"), default="cupy")
    parser.add_argument(
        "--explain-route-choice",
        action="store_true",
        help="Print explicit RT-DBSCAN route options for the selected dataset and exit without dispatching.",
    )
    parser.add_argument(
        "--repeated-component-signature",
        action="store_true",
        help="For --explain-route-choice, describe the repeated component-signature contract.",
    )
    parser.add_argument("--include-rows", action="store_true")
    parser.add_argument("--no-validation", action="store_true")
    parser.add_argument("--adjacency-edge-budget", type=int, default=None)
    parser.add_argument("--chunk-adjacency-edge-budget", type=int, default=None)
    parser.add_argument("--reuse-chunk-neighbor-index-workspace", action="store_true")
    parser.add_argument("--chunk-neighbor-index-workspace-pool-size", type=int, default=0)
    parser.add_argument("--grouped-union-query-block-size", type=int, default=None)
    parser.add_argument("--disable-grouped-union-same-root-culling", action="store_true")
    parser.add_argument("--enable-grouped-union-direct-side-effect", action="store_true")
    parser.add_argument(
        "--partition-pair-enumeration",
        choices=(
            "mode_default",
            "host",
            "device_bounded_offsets",
            "device_count_then_emit",
            "device_count_then_emit_non_skip",
            "device_count_then_emit_non_skip_unordered",
        ),
        default="mode_default",
        help=(
            "Only for partition-convergence preview modes: keep the mode default or explicitly "
            "select host, device bounded-offsets, device count-then-emit, or non-skip "
            "device count-then-emit pair enumeration."
        ),
    )
    parser.add_argument(
        "--partition-cell-factor",
        type=float,
        default=0.125,
        help=(
            "Explicit user-selected partition cell factor for partition-convergence preview modes. "
            "This is advisory/user-controlled and does not authorize hidden auto-tuning."
        ),
    )
    parser.add_argument(
        "--direct-status-convergence-mode",
        choices=("until_stable", "single_pass_candidate"),
        default="until_stable",
        help=(
            "Only for prepared direct-status mode: keep the convergence-proven stable loop "
            "or explicitly test the single-pass candidate. The candidate is not promoted."
        ),
    )
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--warmup", type=int, default=0)
    args = parser.parse_args(argv)
    if args.explain_route_choice:
        print(
            json.dumps(
                explain_rt_dbscan_explicit_route_choice(
                    args.dataset,
                    repeated_component_signature=args.repeated_component_signature,
                    point_count=args.point_count,
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    print(
        json.dumps(
            run_rt_dbscan_benchmark(
                mode=args.mode,
                dataset=args.dataset,
                point_count=args.point_count,
                radius=args.radius,
                min_neighbors=args.min_neighbors,
                seed=args.seed,
                partner=args.partner,
                include_rows=args.include_rows,
                validate=not args.no_validation,
                adjacency_edge_budget=args.adjacency_edge_budget,
                chunk_adjacency_edge_budget=args.chunk_adjacency_edge_budget,
                reuse_chunk_neighbor_index_workspace=args.reuse_chunk_neighbor_index_workspace,
                chunk_neighbor_index_workspace_pool_size=args.chunk_neighbor_index_workspace_pool_size,
                grouped_union_query_block_size=args.grouped_union_query_block_size,
                grouped_union_same_root_culling=not args.disable_grouped_union_same_root_culling,
                grouped_union_direct_side_effect=args.enable_grouped_union_direct_side_effect,
                partition_pair_enumeration=args.partition_pair_enumeration,
                partition_cell_factor=args.partition_cell_factor,
                direct_status_convergence_mode=args.direct_status_convergence_mode,
                repeat=args.repeat,
                warmup=args.warmup,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
