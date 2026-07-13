#!/usr/bin/env python3
"""Run a bounded subset-scaling gate for a full public X-HD candidate."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from pathlib import Path
from typing import Iterable

import numpy as np


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_xhd_cell_mbr_frontier_route_gate as seeded_route
import run_xhd_full_public_feasibility_gate as feasibility_gate
from xhd_input_loader import load_points_matrix
from xhd_input_loader import point_matrix_to_rows
from xhd_input_loader import translate_point_matrix_to_min_bound


def _parse_source_limits(value: str) -> list[int]:
    limits = [int(item.strip()) for item in value.replace(";", ",").split(",") if item.strip()]
    if not limits or any(limit <= 0 for limit in limits):
        raise ValueError("--source-limits must contain positive integers")
    if len(set(limits)) != len(limits):
        raise ValueError("--source-limits must not contain duplicates")
    return limits


def _parse_source_limits_for_count(value: str, *, source_count: int) -> list[int]:
    tokens = [item.strip() for item in value.replace(";", ",").split(",") if item.strip()]
    if not tokens:
        raise ValueError("--source-limits must contain positive integers or 'all'")
    limits: list[int] = []
    for token in tokens:
        if token.lower() == "all":
            limits.append(int(source_count))
        else:
            limits.append(int(token))
    if any(limit <= 0 for limit in limits):
        raise ValueError("--source-limits must contain positive integers or 'all'")
    if len(set(limits)) != len(limits):
        raise ValueError("--source-limits must not contain duplicates after resolving 'all'")
    return limits


def _parse_single_source_limit_for_count(value: str | None, *, source_count: int) -> int | None:
    if value is None:
        return None
    token = str(value).strip()
    if not token:
        raise ValueError("--route-warmup-source-limit must be a positive integer or 'all'")
    limit = int(source_count) if token.lower() == "all" else int(token)
    if limit <= 0:
        raise ValueError("--route-warmup-source-limit must be a positive integer or 'all'")
    if limit > int(source_count):
        raise ValueError(f"--route-warmup-source-limit {limit} exceeds source count {source_count}")
    return limit


def _resolve_author_hd_result(args: argparse.Namespace) -> float | None:
    if getattr(args, "author_hd_result", None) is not None:
        return float(args.author_hd_result)
    author_summary = getattr(args, "author_summary", None)
    if author_summary is None:
        return None
    payload = json.loads(Path(author_summary).read_text(encoding="utf-8"))
    if "author_hd_result" in payload:
        return float(payload["author_hd_result"])
    if "HDResult" in payload:
        return float(payload["HDResult"])
    raise KeyError(f"{author_summary} does not contain author_hd_result or HDResult")


def _suggest_capacity(row_counts: list[int], source_limits: list[int]) -> dict[str, object]:
    if not row_counts:
        return {
            "suggested_next_explicit_row_capacity": None,
            "basis": "no row counts",
        }
    max_rows = max(row_counts)
    max_rows_index = row_counts.index(max_rows)
    source_limit_for_max_rows = source_limits[max_rows_index]
    return {
        "max_observed_frontier_rows": max_rows,
        "source_limit_for_max_rows": source_limit_for_max_rows,
        "max_observed_rows_per_source": max_rows / max(1, source_limit_for_max_rows),
        "suggested_next_explicit_row_capacity": int(math.ceil(max_rows * 1.5)),
        "basis": "ceil(max_observed_frontier_rows * 1.5) for the next bounded POD/OptiX gate",
    }


def build_summary(args: argparse.Namespace) -> dict[str, object]:
    total_start = time.perf_counter()
    bridge = json.loads(Path(args.bridge).read_text(encoding="utf-8"))
    profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    input1, input2 = feasibility_gate._resolve_bridge_paths(bridge)
    if not input1.exists() or not input2.exists():
        raise FileNotFoundError(f"missing full public candidate files: {input1} / {input2}")
    load_start = time.perf_counter()
    points_a_full = load_points_matrix(input1, n_dims=3, input_type="ply")
    points_b_full = load_points_matrix(input2, n_dims=3, input_type="ply")
    preprocessing: list[str] = []
    if args.translate_each_input_to_min_bound:
        points_a_full = translate_point_matrix_to_min_bound(points_a_full, copy=False)
        points_b_full = translate_point_matrix_to_min_bound(points_b_full, copy=False)
        preprocessing.append("translate_each_input_to_min_bound")
    load_sec = time.perf_counter() - load_start
    source_limits = _parse_source_limits_for_count(args.source_limits, source_count=len(points_a_full))
    max_limit = max(source_limits)
    if max_limit > len(points_a_full):
        raise ValueError(f"largest source limit {max_limit} exceeds source count {len(points_a_full)}")
    route_warmup_limit = _parse_single_source_limit_for_count(
        getattr(args, "route_warmup_source_limit", None),
        source_count=len(points_a_full),
    )

    grid_shape = feasibility_gate._parse_grid_shape(args.grid_shape)
    skip_exact_oracle = bool(getattr(args, "skip_exact_oracle", False))
    author_hd_result = _resolve_author_hd_result(args)
    if skip_exact_oracle and author_hd_result is None:
        raise ValueError("--skip-exact-oracle requires --author-hd-result or --author-summary")

    def run_case(limit: int, *, role: str) -> dict[str, object]:
        case_start = time.perf_counter()
        selection_start = time.perf_counter()
        source_count = int(len(points_a_full))
        if int(limit) == source_count:
            points_a_subset = points_a_full
            source_indices_head = list(range(min(8, source_count)))
            tail_count = min(8, source_count)
            source_indices_tail = list(range(source_count - tail_count, source_count))
            source_subset_materialized = False
        else:
            source_indices = feasibility_gate._select_source_indices(
                source_count,
                limit=limit,
                policy=args.source_selection_policy,
            )
            points_a_subset = points_a_full[np.asarray(source_indices, dtype=np.int64), :]
            source_indices_head = source_indices[: min(8, len(source_indices))]
            source_indices_tail = source_indices[-min(8, len(source_indices)) :]
            source_subset_materialized = True
        selection_sec = time.perf_counter() - selection_start
        exact_pair_evaluations = limit * len(points_b_full)
        if not skip_exact_oracle and exact_pair_evaluations > args.max_exact_pair_evaluations:
            raise ValueError(
                f"source limit {limit} would require {exact_pair_evaluations} exact pair evaluations, "
                f"above --max-exact-pair-evaluations {args.max_exact_pair_evaluations}"
            )
        exact = (
            None
            if skip_exact_oracle
            else feasibility_gate._exact_directed_subset(
                point_matrix_to_rows(points_a_subset),
                point_matrix_to_rows(points_b_full),
            )
        )
        route_start = time.perf_counter()
        route = seeded_route._directed_cell_mbr_route(
            points_a_subset,
            points_b_full,
            label=f"a_to_b_subset_{limit}",
            backend=args.backend,
            grid_shape=grid_shape,
            radius=None,
            fallback_radius=seeded_route._full_cover_radius(points_a_subset, points_b_full),
            max_inline_points=args.max_inline_points,
            initial_state=getattr(args, "initial_state", "nearest-cell-mbr"),
            seed_cell_budget=int(getattr(args, "seed_cell_budget", 4)),
            local_grid_seed_executor=getattr(args, "local_grid_seed_executor", "auto"),
            frontier_nearest_executor=args.frontier_nearest_executor,
            frontier_row_order=args.frontier_row_order,
            cell_order=getattr(args, "cell_order", "native"),
            frontier_inline_nearest=bool(args.frontier_inline_nearest),
            global_bound_early_break=bool(getattr(args, "global_bound_early_break", False)),
            collect_inline_stats=bool(getattr(args, "collect_inline_stats", False)),
            collect_frontier_native_phase_timings=bool(
                getattr(args, "collect_frontier_native_phase_timings", False)
            ),
            frontier_row_capacity=getattr(args, "frontier_row_capacity", None),
        )
        route_sec = time.perf_counter() - route_start
        route_abs_diff = None if exact is None else abs(float(route["distance"]) - float(exact["distance"]))
        author_abs_diff = None if author_hd_result is None else abs(float(route["distance"]) - author_hd_result)
        if exact is not None:
            matched = bool(route_abs_diff <= float(args.tolerance))
            match_basis = "exact_subset_reference"
        elif author_abs_diff is not None:
            matched = bool(author_abs_diff <= float(getattr(args, "author_tolerance", 1e-6)))
            match_basis = "author_hd_result"
        else:
            matched = None
            match_basis = "no_comparator"
        case_sec = time.perf_counter() - case_start
        row_count = int(route["frontier_row_count"])
        return {
            "source_limit": limit,
            "case_role": role,
            "excluded_from_summary_statistics": role == "warmup",
            "selected_indices_head": source_indices_head,
            "selected_indices_tail": source_indices_tail,
            "selection_policy": args.source_selection_policy,
            "source_subset_materialized": source_subset_materialized,
            "source_subset_selection_contract": (
                "all_source_no_copy_view"
                if not source_subset_materialized
                else "deterministic_indexed_subset_copy"
            ),
            "matched": matched,
            "match_basis": match_basis,
            "route_abs_diff": route_abs_diff,
            "author_abs_diff": author_abs_diff,
            "author_hd_result": author_hd_result,
            "exact_subset_reference": exact,
            "exact_oracle_used": exact is not None,
            "rtdl_route": {
                "distance": float(route["distance"]),
                "source_id": int(route["source_id"]),
                "target_id": int(route["target_id"]),
                "frontier_row_count": row_count,
                "max_inline_points": int(route.get("max_inline_points", args.max_inline_points)),
                "complete_frontier_state_passthrough": bool(route.get("complete_frontier_state_passthrough", False)),
                "grid_cell_count": int(route["grid_cell_count"]),
                "initial_cell_mbr_tests": int(route["initial_cell_mbr_tests"]),
                "initial_grid_cell_probes": int(route.get("initial_grid_cell_probes", 0)),
                "initial_cell_lookup_strategy": route.get("initial_cell_lookup_strategy"),
                "initial_seed_executor": route.get("initial_seed_executor"),
                "initial_seed_executor_requested": route.get("initial_seed_executor_requested"),
                "initial_query_coordinate_matrix_reused": bool(route.get("initial_query_coordinate_matrix_reused", False)),
                "initial_target_coordinate_matrix_reused": bool(route.get("initial_target_coordinate_matrix_reused", False)),
                "initial_dense_lookup_cell_capacity": int(route.get("initial_dense_lookup_cell_capacity", 0)),
                "initial_dense_lookup_max_cells": int(route.get("initial_dense_lookup_max_cells", 0)),
                "initial_scanned_cell_count": int(route.get("initial_scanned_cell_count", 0)),
                "initial_cell_selection": route.get("initial_cell_selection"),
                "initial_seed_quality": route.get("initial_seed_quality"),
                "initial_scanned_cell_budget_per_query": int(route.get("initial_scanned_cell_budget_per_query", 0)),
                "initial_candidate_distance_evaluations": int(route["initial_candidate_distance_evaluations"]),
                "continuation_candidate_distance_evaluations": int(route["candidate_distance_evaluations"]),
                "total_candidate_distance_evaluations": int(route["total_candidate_distance_evaluations"]),
                "nearest_executor": route["nearest_executor"],
                "max_reduction_strategy": route.get("max_reduction_strategy"),
                "max_tie_candidate_count": route.get("max_tie_candidate_count"),
                "frontier_contract": route["frontier_contract"],
                "cell_order": route.get("cell_order"),
                "cell_order_changed": bool(route.get("cell_order_changed", False)),
                "cell_order_contract": route.get("cell_order_contract"),
                "frontier_native_symbol": route["frontier_native_symbol"],
                "frontier_row_order": route["frontier_row_order"],
                "frontier_row_order_requested": route["frontier_row_order_requested"],
                "frontier_inline_nearest": route["frontier_inline_nearest"],
                "frontier_inline_nearest_requested": route["frontier_inline_nearest_requested"],
                "global_bound_early_break": route.get("global_bound_early_break"),
                "global_bound_early_break_requested": route.get("global_bound_early_break_requested"),
                "global_bound_early_break_count": route.get("global_bound_early_break_count"),
                "global_bound_distance": route.get("global_bound_distance"),
                "global_bound_contract": route.get("global_bound_contract"),
                "per_source_witness_exact": route.get("per_source_witness_exact"),
                "inline_stats_collected": bool(route.get("inline_stats_collected", False)),
                "inline_cell_hit_count": route.get("inline_cell_hit_count"),
                "inline_point_evaluation_count": route.get("inline_point_evaluation_count"),
                "inline_nearest_pruning": route.get("inline_nearest_pruning"),
                "intersection_pruning": route.get("intersection_pruning"),
                "intersection_attribute_min_distance_sq": route.get("intersection_attribute_min_distance_sq"),
                "anyhit_row_distance_computation": route.get("anyhit_row_distance_computation"),
                "frontier_query_coordinate_matrix_reused": bool(route.get("frontier_query_coordinate_matrix_reused", False)),
                "frontier_target_coordinate_matrix_reused": bool(route.get("frontier_target_coordinate_matrix_reused", False)),
                "frontier_native_phase_timings_collected": bool(route.get("frontier_native_phase_timings_collected", False)),
                "frontier_native_phase_timings": route.get("frontier_native_phase_timings"),
                "frontier_row_capacity_requested": route["frontier_row_capacity_requested"],
                "frontier_row_capacity": route["frontier_row_capacity"],
                "frontier_full_row_capacity": route["frontier_full_row_capacity"],
                "frontier_row_capacity_policy": route["frontier_row_capacity_policy"],
                "frontier_row_capacity_attempts": route["frontier_row_capacity_attempts"],
                "frontier_attempted_count": route["frontier_attempted_count"],
                "phase_timings_sec": route["phase_timings_sec"],
            },
            "phase_timings_sec": {
                "select_source_subset": selection_sec,
                "exact_subset_reference": None if exact is None else float(exact["elapsed_sec"]),
                "rtdl_route_wall": route_sec,
                "case_total": case_sec,
            },
        }

    route_warmup = None if route_warmup_limit is None else run_case(route_warmup_limit, role="warmup")
    cases: list[dict[str, object]] = [run_case(limit, role="measured") for limit in source_limits]

    row_counts = [int(case["rtdl_route"]["frontier_row_count"]) for case in cases]  # type: ignore[index]
    route_times = [float(case["phase_timings_sec"]["rtdl_route_wall"]) for case in cases]  # type: ignore[index]
    exact_times = [
        float(case["phase_timings_sec"]["exact_subset_reference"])  # type: ignore[index]
        for case in cases
        if case["phase_timings_sec"]["exact_subset_reference"] is not None  # type: ignore[index]
    ]
    all_matched = all(case["matched"] is True for case in cases)
    full_all_source_run = any(int(limit) == len(points_a_full) for limit in source_limits)
    total_sec = time.perf_counter() - total_start
    return {
        "schema": "rtdl.paper_reproduction.xhd.full_public_subset_scaling_gate.v1",
        "goal": getattr(args, "run_goal", "Goal5181"),
        "status": (
            "full_public_candidate_all_source_route_only_checked"
            if full_all_source_run and skip_exact_oracle
            else "full_public_candidate_bounded_subset_scaling_checked"
        ),
        "target": bridge["target"],
        "level": "level_b_same_source_candidate_only",
        "input1": str(input1),
        "input2": str(input2),
        "full_point_counts": {
            "source": len(points_a_full),
            "target": len(points_b_full),
        },
        "preprocessing": preprocessing,
        "grid_shape": list(grid_shape),
        "backend": args.backend,
        "local_grid_seed_executor": getattr(args, "local_grid_seed_executor", "auto"),
        "cell_order": getattr(args, "cell_order", "native"),
        "global_bound_early_break": bool(getattr(args, "global_bound_early_break", False)),
        "collect_frontier_native_phase_timings": bool(
            getattr(args, "collect_frontier_native_phase_timings", False)
        ),
        "source_limits": source_limits,
        "route_warmup_source_limit": route_warmup_limit,
        "route_warmup": route_warmup,
        "skip_exact_oracle": skip_exact_oracle,
        "author_hd_result": author_hd_result,
        "author_tolerance": float(getattr(args, "author_tolerance", 1e-6)),
        "cases": cases,
        "summary_statistics": {
            "all_matched": all_matched,
            "max_frontier_row_count": max(row_counts) if row_counts else 0,
            "median_route_wall_sec": float(statistics.median(route_times)) if route_times else None,
            "max_route_wall_sec": max(route_times) if route_times else None,
            "median_exact_subset_reference_sec": float(statistics.median(exact_times)) if exact_times else None,
            "max_exact_subset_reference_sec": max(exact_times) if exact_times else None,
            "full_all_source_route_run": full_all_source_run,
            "route_warmup_used": route_warmup is not None,
        },
        "capacity_planning": _suggest_capacity(row_counts, source_limits),
        "goal5179_pairwise_estimate": profile["pairwise_estimate"],
        "route_feasibility": {
            "pairwise_exact_route_allowed": False,
            "scalable_route_exercised_on_full_target_with_bounded_source_subsets": not full_all_source_run,
            "scalable_route_exercised_on_full_source_and_target": full_all_source_run,
            "full_target_loaded": True,
            "full_source_loaded_for_deterministic_subset_selection": True,
            "full_all_source_route_run": full_all_source_run,
            "route_warmup_used": route_warmup is not None,
            "route_warmup_excluded_from_summary_statistics": route_warmup is not None,
            "exact_oracle_used": not skip_exact_oracle,
            "full_pairwise_rows_materialized": False,
            "next_gate_should_be": (
                "review route-only all-source evidence before any performance "
                "or exact-paper claim"
                if full_all_source_run
                else "run POD/OptiX bounded subset with explicit fail-closed row capacity "
                "or increase source subset before any all-source route claim"
            ),
            "frontier_row_capacity_requested": None
            if getattr(args, "frontier_row_capacity", None) is None
            else int(args.frontier_row_capacity),
        },
        "phase_timings_sec": {
            "load_full_inputs": load_sec,
            "route_warmup": None
            if route_warmup is None
            else float(route_warmup["phase_timings_sec"]["case_total"]),
            "total": total_sec,
        },
        "claim_boundary": {
            "level_b_same_source_candidate_claimed": True,
            "bounded_subset_scaling_claimed": not full_all_source_run,
            "route_only_author_comparison_claimed": bool(full_all_source_run and skip_exact_oracle),
            "full_all_source_route_run_claimed": full_all_source_run,
            "performance_ratio_claimed": False,
            "figure_reproduction_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
            "exact_oracle_claimed": not skip_exact_oracle,
        },
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge", required=True, type=Path)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--backend", default="numpy", choices=("numpy", "optix"))
    parser.add_argument("--grid-shape", default="32,32,32")
    parser.add_argument("--source-limits", default="16,64,128")
    parser.add_argument(
        "--route-warmup-source-limit",
        help=(
            "Optional same-process route warmup case. Accepts a positive integer "
            "or 'all'. The warmup result is recorded separately and excluded "
            "from measured case summary statistics."
        ),
    )
    parser.add_argument("--run-goal", default="Goal5181")
    parser.add_argument(
        "--source-selection-policy",
        default="evenly-spaced",
        choices=("first", "evenly-spaced"),
    )
    parser.add_argument("--translate-each-input-to-min-bound", action="store_true")
    parser.add_argument("--max-inline-points", type=int, default=64)
    parser.add_argument(
        "--initial-state",
        default="nearest-cell-mbr",
        choices=("nearest-cell-mbr", "local-grid-cell", "grid-cell-budget", "grid-branch-bound"),
    )
    parser.add_argument("--seed-cell-budget", type=int, default=4)
    parser.add_argument(
        "--local-grid-seed-executor",
        default="auto",
        choices=("auto", "numba", "numba_parallel", "native_cuda"),
        help=(
            "Executor for --initial-state=local-grid-cell. native_cuda is an "
            "explicit experimental generic CUDA seed path; default keeps the "
            "existing Numba route."
        ),
    )
    parser.add_argument(
        "--frontier-nearest-executor",
        default="auto",
        choices=("auto", "numpy", "numba", "numba_parallel"),
    )
    parser.add_argument(
        "--frontier-row-order",
        default="native",
        choices=("sorted", "native"),
    )
    parser.add_argument(
        "--cell-order",
        default="native",
        choices=("native", "point-count-asc", "point-count-desc"),
        help=(
            "Experimental generic cell primitive ordering before cell-MBR "
            "frontier traversal. This preserves cell IDs and point offsets."
        ),
    )
    parser.add_argument("--frontier-inline-nearest", action="store_true")
    parser.add_argument(
        "--global-bound-early-break",
        action="store_true",
        help=(
            "Enable the optional generic max-nearest global-bound early-break "
            "contract in native inline-nearest traversal. Experimental; "
            "reported with explicit early-break metadata."
        ),
    )
    parser.add_argument("--collect-inline-stats", action="store_true")
    parser.add_argument("--collect-frontier-native-phase-timings", action="store_true")
    parser.add_argument("--frontier-row-capacity", type=int)
    parser.add_argument("--max-exact-pair-evaluations", type=int, default=100_000_000)
    parser.add_argument("--skip-exact-oracle", action="store_true")
    parser.add_argument("--author-summary", type=Path)
    parser.add_argument("--author-hd-result", type=float)
    parser.add_argument("--author-tolerance", type=float, default=1e-6)
    parser.add_argument("--tolerance", type=float, default=1e-9)
    args = parser.parse_args(list(argv) if argv is not None else None)

    summary = build_summary(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "wrote",
        args.output,
        "all_matched=",
        summary["summary_statistics"]["all_matched"],
        "source_limits=",
        ",".join(str(item) for item in summary["source_limits"]),
        "max_frontier_rows=",
        summary["summary_statistics"]["max_frontier_row_count"],
    )
    return 0 if summary["summary_statistics"]["all_matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
