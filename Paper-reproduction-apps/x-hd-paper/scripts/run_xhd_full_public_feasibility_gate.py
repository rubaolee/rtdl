#!/usr/bin/env python3
"""Run a bounded feasibility gate for a full public X-HD priority candidate.

Goal5180 uses the full public Stanford Dragon/HappyBuddha Level-B candidate as
input, but deliberately limits the source side for the first safety gate. The
gate proves that the scalable seeded/frontier/inline-nearest route can consume
the full target point set and match a subset exact oracle without materializing
the full pairwise matrix.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Iterable

import numpy as np


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_xhd_cell_mbr_frontier_route_gate as seeded_route
from xhd_input_loader import load_points, translate_points_to_min_bound


def _parse_grid_shape(value: str) -> tuple[int, int, int]:
    parts = tuple(int(part.strip()) for part in value.replace("x", ",").split(",") if part.strip())
    if len(parts) != 3 or any(part <= 0 for part in parts):
        raise ValueError(f"grid shape must be three positive integers, got: {value!r}")
    return parts


def _select_source_indices(count: int, *, limit: int, policy: str) -> list[int]:
    if count <= 0:
        raise ValueError("cannot select from an empty source set")
    if limit <= 0:
        raise ValueError("--source-limit must be positive")
    if limit > count:
        raise ValueError(f"--source-limit {limit} exceeds source count {count}")
    if policy == "first":
        return list(range(limit))
    if policy == "evenly-spaced":
        if limit == 1:
            return [0]
        indices = [int(round(i * (count - 1) / (limit - 1))) for i in range(limit)]
        # Guard against pathological duplicate rounding if future limits get
        # close to the source count.
        seen: set[int] = set()
        unique: list[int] = []
        for index in indices:
            if index not in seen:
                seen.add(index)
                unique.append(index)
        probe = 0
        while len(unique) < limit:
            if probe not in seen:
                unique.append(probe)
                seen.add(probe)
            probe += 1
        return sorted(unique)
    raise ValueError("--source-selection-policy must be first or evenly-spaced")


def _points_to_array(points: list[tuple[float, ...]]) -> np.ndarray:
    arr = np.asarray(points, dtype=np.float64)
    if arr.ndim != 2 or arr.shape[1] != 3:
        raise ValueError(f"expected 3-D points, got shape {arr.shape}")
    return arr


def _exact_directed_subset(
    source_points: list[tuple[float, ...]],
    target_points: list[tuple[float, ...]],
) -> dict[str, object]:
    """Exact directed HD over a bounded source subset and full target set.

    This oracle avoids an NxM matrix. It vectorizes one source row at a time
    against the full target set and keeps only nearest-witness state.
    """

    source = _points_to_array(source_points)
    target = _points_to_array(target_points)
    if len(source) == 0 or len(target) == 0:
        raise ValueError("source and target must be non-empty")
    nearest_distances: list[float] = []
    nearest_item_ids: list[int] = []
    exact_start = time.perf_counter()
    for row in source:
        deltas = target - row
        squared = np.einsum("ij,ij->i", deltas, deltas)
        item_id = int(np.argmin(squared))
        nearest_item_ids.append(item_id)
        nearest_distances.append(float(math.sqrt(float(squared[item_id]))))
    max_source_id = int(np.argmax(np.asarray(nearest_distances, dtype=np.float64)))
    exact_sec = time.perf_counter() - exact_start
    return {
        "distance": float(nearest_distances[max_source_id]),
        "source_id": max_source_id,
        "target_id": int(nearest_item_ids[max_source_id]),
        "source_count": int(len(source)),
        "target_count": int(len(target)),
        "pair_evaluations": int(len(source) * len(target)),
        "oracle_strategy": "vectorized_per_source_exact_nearest_full_target_no_pair_matrix",
        "elapsed_sec": exact_sec,
    }


def _resolve_bridge_paths(bridge: dict[str, object]) -> tuple[Path, Path]:
    candidates = bridge["public_same_source_candidates"]  # type: ignore[index]
    source_basename = str(bridge.get("source_basename") or "dragon.ply")
    target_basename = str(bridge.get("target_basename") or "happy_buddha.ply")
    if source_basename not in candidates or target_basename not in candidates:  # type: ignore[operator]
        order = bridge.get("author_basename_order")
        if isinstance(order, list) and len(order) >= 2:
            source_basename = str(order[0])
            target_basename = str(order[1])
    source = Path(str(candidates[source_basename]["path"]).replace("\\", "/"))  # type: ignore[index]
    target = Path(str(candidates[target_basename]["path"]).replace("\\", "/"))  # type: ignore[index]
    return source, target


def build_summary(args: argparse.Namespace) -> dict[str, object]:
    total_start = time.perf_counter()
    bridge = json.loads(Path(args.bridge).read_text(encoding="utf-8"))
    profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    input1, input2 = _resolve_bridge_paths(bridge)
    if not input1.exists() or not input2.exists():
        raise FileNotFoundError(f"missing full public candidate files: {input1} / {input2}")

    load_start = time.perf_counter()
    points_a_full = load_points(input1, n_dims=3, input_type="ply")
    points_b_full = load_points(input2, n_dims=3, input_type="ply")
    preprocessing: list[str] = []
    if args.translate_each_input_to_min_bound:
        points_a_full = translate_points_to_min_bound(points_a_full)
        points_b_full = translate_points_to_min_bound(points_b_full)
        preprocessing.append("translate_each_input_to_min_bound")
    load_sec = time.perf_counter() - load_start

    selection_start = time.perf_counter()
    source_indices = _select_source_indices(
        len(points_a_full),
        limit=args.source_limit,
        policy=args.source_selection_policy,
    )
    points_a_subset = [points_a_full[index] for index in source_indices]
    selection_sec = time.perf_counter() - selection_start

    exact = _exact_directed_subset(points_a_subset, points_b_full)
    grid_shape = _parse_grid_shape(args.grid_shape)

    route_start = time.perf_counter()
    route = seeded_route._directed_cell_mbr_route(  # app-owned route helper
        points_a_subset,
        points_b_full,
        label="a_to_b_subset",
        backend=args.backend,
        grid_shape=grid_shape,
        radius=None,
        fallback_radius=seeded_route._full_cover_radius(points_a_subset, points_b_full),
        max_inline_points=args.max_inline_points,
        initial_state="nearest-cell-mbr",
        seed_cell_budget=4,
        local_grid_seed_executor="auto",
        frontier_nearest_executor=args.frontier_nearest_executor,
        frontier_row_order=args.frontier_row_order,
        frontier_inline_nearest=bool(args.frontier_inline_nearest),
        frontier_row_capacity=getattr(args, "frontier_row_capacity", None),
    )
    route_sec = time.perf_counter() - route_start
    route_abs_diff = abs(float(route["distance"]) - float(exact["distance"]))
    matched = bool(route_abs_diff <= float(args.tolerance))
    total_sec = time.perf_counter() - total_start

    return {
        "schema": "rtdl.paper_reproduction.xhd.full_public_feasibility_gate.v1",
        "goal": "Goal5180",
        "status": "full_public_candidate_bounded_subset_route_feasibility_checked",
        "target": bridge["target"],
        "level": "level_b_same_source_candidate_only",
        "input1": str(input1),
        "input2": str(input2),
        "full_point_counts": {
            "source": len(points_a_full),
            "target": len(points_b_full),
        },
        "source_subset": {
            "selection_policy": args.source_selection_policy,
            "source_limit": int(args.source_limit),
            "selected_indices": source_indices,
        },
        "preprocessing": preprocessing,
        "grid_shape": list(grid_shape),
        "backend": args.backend,
        "route_options": {
            "initial_state": "nearest-cell-mbr",
            "frontier_nearest_executor": args.frontier_nearest_executor,
            "frontier_row_order": args.frontier_row_order,
            "frontier_inline_nearest": bool(args.frontier_inline_nearest),
            "frontier_row_capacity": None
            if getattr(args, "frontier_row_capacity", None) is None
            else int(args.frontier_row_capacity),
            "max_inline_points": int(args.max_inline_points),
        },
        "goal5179_pairwise_estimate": profile["pairwise_estimate"],
        "route_feasibility": {
            "pairwise_exact_route_allowed": False,
            "scalable_route_exercised_on_full_target_with_bounded_source_subset": True,
            "full_target_loaded": True,
            "full_source_loaded_for_deterministic_subset_selection": True,
            "full_all_source_route_run": False,
            "full_pairwise_rows_materialized": False,
            "capacity_policy": {
                "this_gate": (
                    "explicit_fail_closed_row_capacity"
                    if getattr(args, "frontier_row_capacity", None) is not None
                    else "local_numpy_or_backend_default_capacity"
                ),
                "actual_frontier_row_count_recorded": True,
                "next_pod_optix_gate_must_use_fail_closed_row_capacity": True,
            },
            "next_gate_should_be": (
                "increase source subset and/or run POD OptiX feasibility; do not "
                "claim full-route performance until the all-source route runs"
            ),
        },
        "exact_subset_reference": exact,
        "rtdl_route": route,
        "route_abs_diff": route_abs_diff,
        "matched": matched,
        "phase_timings_sec": {
            "load_full_inputs": load_sec,
            "select_source_subset": selection_sec,
            "exact_subset_reference": float(exact["elapsed_sec"]),
            "rtdl_route_wall": route_sec,
            "total": total_sec,
        },
        "claim_boundary": {
            "level_b_same_source_candidate_claimed": True,
            "bounded_subset_route_run_claimed": True,
            "full_all_source_route_run_claimed": False,
            "performance_ratio_claimed": False,
            "figure_reproduction_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
        },
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge", required=True, type=Path)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--backend", default="numpy", choices=("numpy", "optix"))
    parser.add_argument("--grid-shape", default="32,32,32")
    parser.add_argument("--source-limit", type=int, default=16)
    parser.add_argument(
        "--source-selection-policy",
        default="evenly-spaced",
        choices=("first", "evenly-spaced"),
    )
    parser.add_argument("--translate-each-input-to-min-bound", action="store_true")
    parser.add_argument("--max-inline-points", type=int, default=64)
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
    parser.add_argument("--frontier-inline-nearest", action="store_true")
    parser.add_argument("--frontier-row-capacity", type=int)
    parser.add_argument("--tolerance", type=float, default=1e-9)
    args = parser.parse_args(list(argv) if argv is not None else None)

    summary = build_summary(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "wrote",
        args.output,
        "matched=",
        summary["matched"],
        "source_limit=",
        summary["source_subset"]["source_limit"],
        "target_count=",
        summary["full_point_counts"]["target"],
    )
    return 0 if summary["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
