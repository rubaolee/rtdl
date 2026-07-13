#!/usr/bin/env python3
"""Build Goal5358 author-like radius queue reference evidence.

The current cell-MBR route is a single-pass route and cannot be relabeled as
the author's adaptive radius queue.  This goal builds the smallest honest
author-like queue reference in the X-HD app layer:

1. use generic RTDL nearest/witness primitives to compute exact directed
   nearest distances;
2. simulate the author's radius queue fields from those distances;
3. compare the resulting Iteration/Radius/NumInputPoints/NumOutputPoints rows
   to a bounded author ``hd_exec`` JSON trace.

This is a semantics reference for future route work, not a performance path and
not author RT-core parity.
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
from xhd_input_loader import load_points_matrix


APP_ROOT = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_ROOT / "results"
FIXTURES = APP_ROOT / "data" / "fixtures"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _columns_3d(points: np.ndarray) -> dict[str, object]:
    coords = np.asarray(points, dtype=np.float64)
    if coords.ndim != 2 or coords.shape[1] != 3:
        raise ValueError("expected an Nx3 point matrix")
    coords = np.ascontiguousarray(coords)
    return {
        "ids": np.arange(coords.shape[0], dtype=np.int64),
        "x": coords[:, 0],
        "y": coords[:, 1],
        "z": coords[:, 2],
    }


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


def _nearest_distances_with_generic_pipeline(source: np.ndarray, target: np.ndarray) -> dict[str, Any]:
    source_columns = _columns_3d(source)
    target_columns = _columns_3d(target)
    candidates = rt.pairwise_l2_distance_candidate_rows_numpy_columns(
        source_columns,
        target_columns,
        coordinate_fields=("x", "y", "z"),
        return_metadata=True,
    )
    nearest = rt.nearest_witness_numpy_columns(
        candidates["candidate_rows"],
        candidates["source_ids"],
        return_metadata=True,
    )
    nearest_columns = nearest["columns"]
    max_witness = rt.max_nearest_distance_witness_numpy_columns(
        nearest_columns,
        return_metadata=True,
    )
    return {
        "nearest": nearest,
        "max_witness": max_witness,
        "nearest_distances": np.asarray(nearest_columns["nearest_distances"], dtype=np.float64),
        "metadata": {
            "contract": (
                "generic_pairwise_l2_distance_candidate_rows -> "
                "generic_nearest_witness_columns -> generic_max_nearest_distance_with_witness"
            ),
            "app_semantics": "none",
            "candidate_row_count": int(candidates["metadata"]["row_count"]),
            "nearest_source_count": int(nearest["metadata"]["source_count"]),
            "max_contract": max_witness["metadata"]["contract"],
        },
    }


def _simulate_author_like_queue(
    *,
    nearest_distances: np.ndarray,
    initial_radius: float,
    hd_upper_bound: float,
    cell_diagonal: float,
    mode: rt.RadiusGrowthMode,
) -> list[dict[str, Any]]:
    active = np.ones(nearest_distances.shape[0], dtype=bool)
    radius = float(initial_radius)
    cmax2_state = float(initial_radius) * float(initial_radius)
    rows: list[dict[str, Any]] = []
    iteration = 1
    while True:
        active_distances = nearest_distances[active]
        if active_distances.size == 0:
            break
        unresolved_active = active_distances > radius
        confirmed_active = ~unresolved_active
        if np.any(confirmed_active):
            confirmed_max = float(np.max(active_distances[confirmed_active] * active_distances[confirmed_active]))
            cmax2_state = max(float(cmax2_state), confirmed_max)
        num_input = int(active_distances.size)
        num_output = int(np.count_nonzero(unresolved_active))
        rows.append(
            {
                "Iteration": iteration,
                "Radius": float(radius),
                "NumInputPoints": num_input,
                "NumOutputPoints": num_output,
                "CMax2": float(cmax2_state),
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
            mode=mode,
        )
        active_indices = np.flatnonzero(active)
        next_active = np.zeros_like(active)
        next_active[active_indices[unresolved_active]] = True
        active = next_active
        radius = float(step.next_radius)
        iteration += 1
        if iteration > nearest_distances.size + 1:
            raise RuntimeError("radius queue simulation did not converge")
    return rows


def _compare_rows(author_rows: list[dict[str, Any]], rtdl_rows: list[dict[str, Any]], *, tolerance: float) -> dict[str, Any]:
    mismatches: list[dict[str, Any]] = []
    if len(author_rows) != len(rtdl_rows):
        mismatches.append(
            {
                "field": "iteration_count",
                "author": len(author_rows),
                "rtdl": len(rtdl_rows),
            }
        )
    for index, (author, rtdl) in enumerate(zip(author_rows, rtdl_rows), start=1):
        for field in ("Iteration", "NumInputPoints", "NumOutputPoints"):
            if int(author[field]) != int(rtdl[field]):
                mismatches.append(
                    {
                        "iteration": index,
                        "field": field,
                        "author": int(author[field]),
                        "rtdl": int(rtdl[field]),
                    }
                )
        for field in ("Radius", "CMax2"):
            abs_diff = abs(float(author[field]) - float(rtdl[field]))
            if abs_diff > tolerance:
                mismatches.append(
                    {
                        "iteration": index,
                        "field": field,
                        "author": float(author[field]),
                        "rtdl": float(rtdl[field]),
                        "abs_diff": abs_diff,
                    }
                )
    return {
        "matched": len(mismatches) == 0,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
    }


def build_artifact(*, tolerance: float = 1.0e-6) -> dict[str, Any]:
    author_json = RESULTS / "bounded3d_author_hd_exec_output_pod.json"
    author_payload = _load_json(author_json)
    repeat = author_payload["Running"]["Repeats"][0]
    author_iterations = [dict(row) for row in repeat["Iterations"]]
    source = load_points_matrix(FIXTURES / "bounded3d_a.wkt", n_dims=3, input_type="wkt")
    target = load_points_matrix(FIXTURES / "bounded3d_b.wkt", n_dims=3, input_type="wkt")
    nearest_payload = _nearest_distances_with_generic_pipeline(source, target)
    rtdl_iterations = _simulate_author_like_queue(
        nearest_distances=nearest_payload["nearest_distances"],
        initial_radius=float(repeat["InitRadius"]),
        hd_upper_bound=float(repeat["HDUpperBound"]),
        cell_diagonal=_target_cell_diagonal(author_payload),
        mode=str(author_payload["Running"].get("TuneRadius", "adaptive")),  # type: ignore[arg-type]
    )
    comparison = _compare_rows(author_iterations, rtdl_iterations, tolerance=tolerance)
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5358.author_like_radius_queue_reference.v1",
        "goal": "Goal5358",
        "date": "2026-07-09",
        "status": "author_like_radius_queue_reference_matches_bounded3d_author_trace",
        "purpose": (
            "Build an app-owned author-like radius queue reference from generic "
            "nearest/witness primitives, so future route work has a comparable "
            "Iteration/Radius/NumInputPoints/NumOutputPoints target."
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
        "rtdl_reference": {
            "iteration_model": "generic_exact_nearest_author_like_radius_queue_reference",
            "iterations": rtdl_iterations,
            "hd_result": float(nearest_payload["max_witness"]["value"]),
            "pipeline_metadata": nearest_payload["metadata"],
            "uses_radius_growth_step": any(row["NumOutputPoints"] > 0 for row in rtdl_iterations),
            "uses_generic_nearest_pipeline": True,
        },
        "comparison": comparison,
        "claim_boundary": {
            "author_tune_radius_route_mapping_claimed": False,
            "author_rt_core_algorithm_equivalence_claimed": False,
            "figure8_reproduction_claimed": False,
            "performance_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
        "decision": {
            "author_like_iteration_schema_available": True,
            "current_cell_mbr_route_replaced": False,
            "explicit_author_tune_radius_supported": False,
            "reason": (
                "This is a generic exact-nearest semantics reference. It does not "
                "make the current cell-MBR route author-queue-compatible yet."
            ),
        },
        "recommended_next_targets": [
            "implement_cell_mbr_author_like_queue_route_using_this_iteration_schema",
            "compare_route_queue_trace_against_author_trace",
            "only_then_consider_accepting_explicit_author_tune_radius",
        ],
        "exit_label": "author_like_queue_reference_ready__route_implementation_still_required",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS / "xhd_goal5358_author_like_radius_queue_reference.json",
    )
    parser.add_argument("--tolerance", type=float, default=1.0e-6)
    args = parser.parse_args()
    payload = build_artifact(tolerance=float(args.tolerance))
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
