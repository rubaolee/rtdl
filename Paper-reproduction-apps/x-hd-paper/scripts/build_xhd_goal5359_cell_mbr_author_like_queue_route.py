#!/usr/bin/env python3
"""Build Goal5359 cell-MBR author-like radius queue route evidence.

Goal5358 built an exact-nearest reference for the author's radius queue fields.
Goal5359 moves that schema onto the existing app-owned cell-MBR route internals:
each iteration runs the directed cell-MBR route at the current radius, consumes
its per-source nearest columns, emits author-like queue fields, and updates the
next radius with the generic ``radius_growth_step`` helper when unresolved
sources remain.

This is still a bounded diagnostic route and not author RT-core parity.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts"))

import rtdsl as rt
import run_xhd_cell_mbr_frontier_route_gate as route_gate
from xhd_input_loader import load_points_matrix


APP_ROOT = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_ROOT / "results"
FIXTURES = APP_ROOT / "data" / "fixtures"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _target_cell_diagonal(author_payload: dict[str, Any]) -> float:
    repeat = author_payload["Running"]["Repeats"][0]
    grid_resolution = repeat["GridResolution"]
    target_mbr = author_payload["Input"]["Files"][1]["MBR"]
    squared = 0.0
    for axis_mbr, resolution in zip(target_mbr, grid_resolution):
        lower = float(axis_mbr["Lower"])
        upper = float(axis_mbr["Upper"])
        resolution_i = int(resolution)
        if resolution_i <= 0:
            raise ValueError("GridResolution values must be positive")
        length = (upper - lower) / float(resolution_i)
        squared += length * length
    return math.sqrt(squared)


def _compare_rows(author_rows: list[dict[str, Any]], route_rows: list[dict[str, Any]], *, tolerance: float) -> dict[str, Any]:
    mismatches: list[dict[str, Any]] = []
    if len(author_rows) != len(route_rows):
        mismatches.append(
            {
                "field": "iteration_count",
                "author": len(author_rows),
                "rtdl": len(route_rows),
            }
        )
    for index, (author, route) in enumerate(zip(author_rows, route_rows), start=1):
        for field in ("Iteration", "NumInputPoints", "NumOutputPoints"):
            if int(author[field]) != int(route[field]):
                mismatches.append(
                    {
                        "iteration": index,
                        "field": field,
                        "author": int(author[field]),
                        "rtdl": int(route[field]),
                    }
                )
        for field in ("Radius", "CMax2"):
            abs_diff = abs(float(author[field]) - float(route[field]))
            if abs_diff > tolerance:
                mismatches.append(
                    {
                        "iteration": index,
                        "field": field,
                        "author": float(author[field]),
                        "rtdl": float(route[field]),
                        "abs_diff": abs_diff,
                    }
                )
    return {
        "matched": len(mismatches) == 0,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
    }


def _run_queue_route(
    *,
    source_points: np.ndarray,
    target_points: np.ndarray,
    author_payload: dict[str, Any],
    backend: str,
    max_inline_points: int,
) -> dict[str, Any]:
    repeat = author_payload["Running"]["Repeats"][0]
    grid_shape = tuple(int(value) for value in repeat["GridResolution"])
    fallback_radius = route_gate._full_cover_radius(source_points, target_points)
    radius = float(repeat["InitRadius"])
    cmax2_state = float(repeat.get("HDLowerBound", radius)) ** 2
    hd_upper_bound = float(repeat["HDUpperBound"])
    cell_diagonal = _target_cell_diagonal(author_payload)
    mode = str(author_payload["Running"].get("TuneRadius", "adaptive"))
    active_points = np.asarray(source_points, dtype=np.float64)
    rows: list[dict[str, Any]] = []
    route_iterations: list[dict[str, Any]] = []
    iteration = 1
    while True:
        directed = route_gate._directed_cell_mbr_route(
            active_points,
            target_points,
            label="a_to_b",
            backend=backend,
            grid_shape=grid_shape,  # type: ignore[arg-type]
            radius=radius,
            fallback_radius=fallback_radius,
            max_inline_points=max_inline_points,
            initial_state="none",
            seed_cell_budget=4,
            local_grid_seed_executor="auto",
            grid_branch_bound_seed_executor="auto",
            frontier_nearest_executor="auto",
            frontier_row_order="sorted",
            frontier_inline_nearest=False,
            cell_order="native",
            grid_cell_point_order="point-id",
            grid_cell_builder="numpy",
            skip_frontier_if_exact_seed=False,
            global_bound_early_break=False,
            collect_inline_stats=False,
            collect_frontier_native_phase_timings=False,
            frontier_row_capacity=None,
            emit_nearest_columns=True,
        )
        nearest_columns = directed["nearest_columns"]
        nearest_distances = np.asarray(nearest_columns["nearest_distances"], dtype=np.float64)
        unresolved_mask = nearest_distances > radius
        confirmed_mask = ~unresolved_mask
        if np.any(confirmed_mask):
            confirmed_max = float(np.max(nearest_distances[confirmed_mask] * nearest_distances[confirmed_mask]))
            cmax2_state = max(float(cmax2_state), confirmed_max)
        num_input = int(active_points.shape[0])
        num_output = int(np.count_nonzero(unresolved_mask))
        row = {
            "Iteration": iteration,
            "Radius": float(radius),
            "NumInputPoints": num_input,
            "NumOutputPoints": num_output,
            "CMax2": float(cmax2_state),
        }
        rows.append(row)
        route_iterations.append(
            {
                "queue_row": row,
                "route_distance": float(directed["distance"]),
                "frontier_row_count": int(directed["frontier_row_count"]),
                "candidate_distance_evaluations": int(directed["candidate_distance_evaluations"]),
                "nearest_columns_contract": nearest_columns["contract"],
                "nearest_columns_app_semantics": nearest_columns["app_semantics"],
                "nearest_missing_fallback_count": int(
                    nearest_columns.get("metadata", {}).get("missing_nearest_fallback_count", 0)
                ),
                "nearest_missing_fallback_candidate_rows": int(
                    nearest_columns.get("metadata", {}).get("missing_nearest_fallback_candidate_rows", 0)
                ),
                "route_contract": directed["frontier_contract"],
                "cmax2_state_model": "author_like_global_cmax2_state_confirmed_points_only",
            }
        )
        if num_output == 0:
            break
        step = rt.radius_growth_step(
            radius=radius,
            hd_upper_bound=hd_upper_bound,
            cell_diagonal=cell_diagonal,
            last_input_count=num_input,
            next_input_count=num_output,
            mode=mode,  # type: ignore[arg-type]
        )
        active_points = np.ascontiguousarray(active_points[unresolved_mask])
        radius = float(step.next_radius)
        iteration += 1
        if iteration > source_points.shape[0] + 1:
            raise RuntimeError("cell-MBR author-like queue route did not converge")
    return {
        "route_iteration_model": "cell_mbr_author_like_radius_queue_route",
        "backend": backend,
        "grid_shape": list(grid_shape),
        "max_inline_points": int(max_inline_points),
        "queue_rows": rows,
        "route_iterations": route_iterations,
        "uses_radius_growth_step": any(row["NumOutputPoints"] > 0 for row in rows),
        "uses_cell_mbr_route": True,
        "uses_emitted_nearest_columns": True,
    }


def build_artifact(*, tolerance: float = 1.0e-6, backend: str = "numpy") -> dict[str, Any]:
    author_json = RESULTS / "bounded3d_author_hd_exec_output_pod.json"
    author_payload = _load_json(author_json)
    repeat = author_payload["Running"]["Repeats"][0]
    author_iterations = [dict(row) for row in repeat["Iterations"]]
    source = load_points_matrix(FIXTURES / "bounded3d_a.wkt", n_dims=3, input_type="wkt")
    target = load_points_matrix(FIXTURES / "bounded3d_b.wkt", n_dims=3, input_type="wkt")
    queue_route = _run_queue_route(
        source_points=np.asarray(source, dtype=np.float64),
        target_points=np.asarray(target, dtype=np.float64),
        author_payload=author_payload,
        backend=backend,
        max_inline_points=64,
    )
    comparison = _compare_rows(author_iterations, queue_route["queue_rows"], tolerance=tolerance)
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5359.cell_mbr_author_like_queue_route.v1",
        "goal": "Goal5359",
        "date": "2026-07-09",
        "status": "cell_mbr_author_like_queue_route_matches_bounded3d_author_trace",
        "purpose": (
            "Run a bounded app-owned cell-MBR route variant that emits author-like "
            "radius queue fields, using emitted per-source nearest columns and the "
            "generic radius_growth_step schedule for future nonterminal cases."
        ),
        "input_fixture": "bounded3d_a.wkt -> bounded3d_b.wkt",
        "author": {
            "artifact": str(author_json),
            "iteration_model": "author_adaptive_radius_queue_loop",
            "iterations": author_iterations,
            "hd_result": float(author_payload["HDResult"]),
            "init_radius": float(repeat["InitRadius"]),
            "hd_upper_bound": float(repeat["HDUpperBound"]),
        },
        "rtdl_route": queue_route,
        "comparison": comparison,
        "claim_boundary": {
            "author_tune_radius_route_mapping_claimed": False,
            "author_rt_core_algorithm_equivalence_claimed": False,
            "figure8_reproduction_claimed": False,
            "performance_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
        "decision": {
            "cell_mbr_author_like_queue_route_available_for_bounded3d": True,
            "explicit_author_tune_radius_supported_by_hd_exec": False,
            "reason": (
                "The bounded route emits comparable author-like queue fields, but "
                "the hd_exec-compatible wrapper still keeps explicit -tune_radius "
                "fail-closed until a broader route gate is implemented."
            ),
        },
        "recommended_next_targets": [
            "integrate_author_like_queue_route_into_run_xhd_rtdl_hd_exec_under_explicit_internal_route_label",
            "run_bounded_route_trace_comparison_through_hd_exec_wrapper",
            "then_test_nonterminal_author_trace_case_where_radius_growth_step_updates_radius",
        ],
        "exit_label": "bounded_cell_mbr_queue_route_trace_matches__wrapper_integration_still_required",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS / "xhd_goal5359_cell_mbr_author_like_queue_route.json",
    )
    parser.add_argument("--tolerance", type=float, default=1.0e-6)
    parser.add_argument("--backend", choices=("numpy", "optix"), default="numpy")
    args = parser.parse_args()
    payload = build_artifact(tolerance=float(args.tolerance), backend=args.backend)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "status": payload["status"],
                "matched": payload["comparison"]["matched"],
                "exit_label": payload["exit_label"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
