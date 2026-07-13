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

import rtdsl as rt

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from run_xhd_author_json_gate import exact_hausdorff, load_author_hd_result
from xhd_input_loader import load_points_matrix
from xhd_input_loader import lift_point_matrix_2d_to_3d_zero_z
from xhd_input_loader import normalize_point_matrix_to_author_float32_unit_box
from xhd_input_loader import normalize_point_matrix_to_author_unit_box
from xhd_input_loader import point_matrix_to_rows
from xhd_input_loader import translate_point_matrix_to_min_bound


def _coordinate_matrix_3d(points: object) -> np.ndarray:
    coords = np.asarray(points, dtype=np.float64)
    if coords.ndim != 2 or coords.shape[1] != 3:
        raise ValueError("3-D route expects an Nx3 point matrix")
    return np.ascontiguousarray(coords)


def _columns_3d(points: object) -> dict[str, object]:
    coords = _coordinate_matrix_3d(points)
    return {
        "ids": np.arange(coords.shape[0], dtype=np.int64),
        "x": coords[:, 0],
        "y": coords[:, 1],
        "z": coords[:, 2],
        "coordinate_matrix": coords,
        "coordinate_matrix_fields": ("x", "y", "z"),
    }


def _full_cover_radius(points_a: object, points_b: object) -> float:
    coords_a = _coordinate_matrix_3d(points_a)
    coords_b = _coordinate_matrix_3d(points_b)
    mins = np.minimum(coords_a.min(axis=0), coords_b.min(axis=0))
    maxs = np.maximum(coords_a.max(axis=0), coords_b.max(axis=0))
    diag = math.sqrt(float(np.sum((maxs - mins) * (maxs - mins))))
    return float(diag + 1.0e-9)


def _parse_grid_shape(value: str) -> tuple[int, int, int]:
    parts = tuple(int(item) for item in value.lower().replace("x", ",").split(",") if item.strip())
    if len(parts) != 3:
        raise ValueError("--grid-shape must contain three dimensions, e.g. 4,4,4")
    if any(part <= 0 for part in parts):
        raise ValueError("--grid-shape dimensions must be positive")
    return parts


def _nearest_from_complete_frontier_state(
    source_columns: dict[str, object],
    frontier_state: dict[str, object],
    *,
    executor_requested: str,
) -> dict[str, object]:
    """Return nearest columns when native inline traversal already finished all queries."""

    source_ids = np.asarray(source_columns["ids"], dtype=np.int64)
    state_source_ids = np.asarray(frontier_state["query_point_ids"], dtype=np.int64)
    nearest_distances = np.asarray(frontier_state["current_best_distances"], dtype=np.float64)
    nearest_item_ids = np.asarray(frontier_state["current_best_item_ids"], dtype=np.int64)
    if (
        source_ids.shape != state_source_ids.shape
        or source_ids.shape != nearest_distances.shape
        or source_ids.shape != nearest_item_ids.shape
    ):
        raise RuntimeError("complete frontier state arrays must match source ids")
    if not np.array_equal(source_ids, state_source_ids):
        raise RuntimeError("complete frontier state source ids do not match route source ids")
    incomplete = np.where((nearest_item_ids < 0) | ~np.isfinite(nearest_distances))[0]
    if incomplete.size:
        raise RuntimeError(
            "complete frontier state is missing nearest witnesses for source rows "
            f"{incomplete.tolist()}"
        )
    return {
        "columns": {
            "source_ids": source_ids.astype(np.int64, copy=False),
            "nearest_item_ids": nearest_item_ids.astype(np.int64, copy=False),
            "nearest_distances": nearest_distances.astype(np.float64, copy=False),
        },
        "metadata": {
            "adapter": "nearest_from_complete_frontier_state",
            "partner": "route_orchestration",
            "contract": "generic_nearest_witness_from_complete_frontier_state",
            "coordinate_fields": ("x", "y", "z"),
            "query_count": int(source_ids.size),
            "frontier_row_count": 0,
            "used_frontier_row_count": 0,
            "candidate_distance_evaluations": 0,
            "executor": "complete_frontier_state_passthrough",
            "executor_requested": str(executor_requested),
            "reduction_strategy": "native_inline_nearest_state_already_complete",
            "app_semantics": "none",
            "native_engine_row_contract": "consumes_generic_complete_nearest_state",
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        },
    }


def _nearest_state_columns_without_completeness_check(
    source_columns: dict[str, object],
    frontier_state: dict[str, object],
    *,
    executor_requested: str,
) -> dict[str, object]:
    source_ids = np.asarray(source_columns["ids"], dtype=np.int64)
    state_source_ids = np.asarray(frontier_state["query_point_ids"], dtype=np.int64)
    nearest_distances = np.asarray(frontier_state["current_best_distances"], dtype=np.float64)
    nearest_item_ids = np.asarray(frontier_state["current_best_item_ids"], dtype=np.int64)
    if (
        source_ids.shape != state_source_ids.shape
        or source_ids.shape != nearest_distances.shape
        or source_ids.shape != nearest_item_ids.shape
    ):
        raise RuntimeError("frontier state arrays must match source ids")
    if not np.array_equal(source_ids, state_source_ids):
        raise RuntimeError("frontier state source ids do not match route source ids")
    return {
        "columns": {
            "source_ids": source_ids.astype(np.int64, copy=False),
            "nearest_item_ids": nearest_item_ids.astype(np.int64, copy=False),
            "nearest_distances": nearest_distances.astype(np.float64, copy=False),
        },
        "metadata": {
            "adapter": "nearest_from_frontier_state_with_possible_missing_values",
            "partner": "route_orchestration",
            "contract": "generic_nearest_witness_from_frontier_state_with_fallback",
            "coordinate_fields": ("x", "y", "z"),
            "query_count": int(source_ids.size),
            "frontier_row_count": 0,
            "used_frontier_row_count": 0,
            "candidate_distance_evaluations": 0,
            "executor": "frontier_state_passthrough_before_missing_fallback",
            "executor_requested": str(executor_requested),
            "reduction_strategy": "frontier_state_passthrough_before_missing_fallback",
            "app_semantics": "none",
            "native_engine_row_contract": "consumes_generic_nearest_state",
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        },
    }


def _fill_missing_nearest_with_pairwise_fallback(
    source_columns: dict[str, object],
    target_columns: dict[str, object],
    nearest: dict[str, object],
    *,
    coordinate_fields=("x", "y", "z"),
) -> dict[str, object]:
    columns = nearest["columns"]
    source_ids = np.asarray(columns["source_ids"], dtype=np.int64)
    nearest_item_ids = np.asarray(columns["nearest_item_ids"], dtype=np.int64)
    nearest_distances = np.asarray(columns["nearest_distances"], dtype=np.float64)
    missing = np.where((nearest_item_ids < 0) | ~np.isfinite(nearest_distances))[0]
    metadata = dict(nearest.get("metadata", {}))
    if missing.size == 0:
        metadata.setdefault("missing_nearest_fallback_count", 0)
        metadata.setdefault("missing_nearest_fallback_candidate_rows", 0)
        result = dict(nearest)
        result["metadata"] = metadata
        return result

    subset_source = {"ids": np.asarray(source_columns["ids"], dtype=np.int64)[missing]}
    for field in coordinate_fields:
        subset_source[field] = np.asarray(source_columns[field], dtype=np.float64)[missing]

    candidates = rt.pairwise_l2_distance_candidate_rows_numpy_columns(
        subset_source,
        target_columns,
        coordinate_fields=coordinate_fields,
        return_metadata=True,
    )
    fallback = rt.nearest_witness_numpy_columns(
        candidates["candidate_rows"],
        candidates["source_ids"],
        return_metadata=True,
    )
    filled_item_ids = nearest_item_ids.copy()
    filled_distances = nearest_distances.copy()
    filled_item_ids[missing] = np.asarray(fallback["columns"]["nearest_item_ids"], dtype=np.int64)
    filled_distances[missing] = np.asarray(fallback["columns"]["nearest_distances"], dtype=np.float64)
    metadata.update(
        {
            "missing_nearest_fallback_count": int(missing.size),
            "missing_nearest_fallback_candidate_rows": int(candidates["metadata"]["row_count"]),
            "missing_nearest_fallback_contract": (
                "generic_pairwise_l2_distance_candidate_rows -> generic_nearest_witness_columns"
            ),
            "missing_nearest_fallback_app_semantics": "none",
            "reduction_strategy": (
                str(metadata.get("reduction_strategy", "frontier_state"))
                + "_with_missing_pairwise_l2_fallback"
            ),
        }
    )
    return {
        "columns": {
            "source_ids": source_ids,
            "nearest_item_ids": filled_item_ids,
            "nearest_distances": filled_distances,
        },
        "metadata": metadata,
    }


def _order_cell_columns(
    cell_columns: dict[str, object],
    *,
    cell_order: str,
) -> tuple[dict[str, object], dict[str, object]]:
    if cell_order == "native":
        return cell_columns, {
            "cell_order": "native",
            "cell_order_changed": False,
            "cell_order_contract": "input_order_preserved",
        }
    if cell_order not in {"point-count-asc", "point-count-desc"}:
        raise ValueError("--cell-order must be native, point-count-asc, or point-count-desc")

    point_counts = np.asarray(cell_columns["point_counts"], dtype=np.uint64)
    cell_ids = np.asarray(cell_columns["cell_ids"], dtype=np.int64)
    if point_counts.shape != cell_ids.shape:
        raise ValueError("cell point_counts and cell_ids must have matching shape")

    if cell_order == "point-count-asc":
        order = np.lexsort((cell_ids, point_counts))
    else:
        order = np.lexsort((cell_ids, -point_counts.astype(np.int64)))

    ordered: dict[str, object] = {}
    for key, value in cell_columns.items():
        arr = np.asarray(value)
        if arr.shape[:1] == point_counts.shape[:1]:
            ordered[key] = np.ascontiguousarray(arr[order])
        else:
            ordered[key] = value
    return ordered, {
        "cell_order": cell_order,
        "cell_order_changed": True,
        "cell_order_contract": "app_owned_generic_cell_primitive_ordering",
    }


def _directed_cell_mbr_route(
    source_points: object,
    target_points: object,
    *,
    label: str,
    backend: str,
    grid_shape: tuple[int, int, int],
    radius: float | None,
    fallback_radius: float,
    max_inline_points: int,
    initial_state: str,
    seed_cell_budget: int,
    local_grid_seed_executor: str,
    grid_branch_bound_seed_executor: str,
    frontier_nearest_executor: str,
    frontier_row_order: str,
    frontier_inline_nearest: bool,
    cell_order: str = "native",
    grid_cell_point_order: str = "point-id",
    grid_cell_builder: str = "numpy",
    skip_frontier_if_exact_seed: bool = False,
    global_bound_early_break: bool = False,
    collect_inline_stats: bool = False,
    collect_frontier_native_phase_timings: bool = False,
    frontier_row_capacity: int | None = None,
    emit_nearest_columns: bool = False,
) -> dict[str, object]:
    direction_start = time.perf_counter()
    source_columns_start = time.perf_counter()
    source_columns = _columns_3d(source_points)
    source_columns_sec = time.perf_counter() - source_columns_start
    target_columns_start = time.perf_counter()
    target_columns = _columns_3d(target_points)
    target_columns_sec = time.perf_counter() - target_columns_start
    grid_start = time.perf_counter()
    if grid_cell_builder == "numpy":
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target_columns,
            coordinate_fields=("x", "y", "z"),
            grid_shape=grid_shape,
            cell_point_order=grid_cell_point_order,
            return_metadata=True,
        )
    elif grid_cell_builder == "native_cuda":
        grid = rt.point_grid_cell_mbrs_native_3d_cuda_columns(
            target_columns,
            coordinate_fields=("x", "y", "z"),
            grid_shape=grid_shape,
            cell_point_order=grid_cell_point_order,
            return_metadata=True,
        )
    else:
        raise ValueError("grid_cell_builder must be 'numpy' or 'native_cuda'")
    grid_sec = time.perf_counter() - grid_start
    seed = None
    current_best_distances = None
    current_best_item_ids = None
    seed_sec = 0.0
    if initial_state == "nearest-cell-mbr":
        seed_start = time.perf_counter()
        seed = rt.seed_nearest_witness_from_nearest_cell_mbr_numpy_columns(
            source_columns,
            target_columns,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            return_metadata=True,
        )
        seed_sec = time.perf_counter() - seed_start
        current_best_distances = seed["columns"]["nearest_distances"]
        current_best_item_ids = seed["columns"]["nearest_item_ids"]
    elif initial_state == "local-grid-cell":
        seed_start = time.perf_counter()
        seed = rt.seed_nearest_witness_from_local_grid_cell_numpy_columns(
            source_columns,
            target_columns,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            executor=local_grid_seed_executor,
            return_metadata=True,
        )
        seed_sec = time.perf_counter() - seed_start
        current_best_distances = seed["columns"]["nearest_distances"]
        current_best_item_ids = seed["columns"]["nearest_item_ids"]
    elif initial_state == "grid-cell-budget":
        seed_start = time.perf_counter()
        seed = rt.seed_nearest_witness_from_grid_cell_budget_numpy_columns(
            source_columns,
            target_columns,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            max_scanned_cells_per_query=seed_cell_budget,
            return_metadata=True,
        )
        seed_sec = time.perf_counter() - seed_start
        current_best_distances = seed["columns"]["nearest_distances"]
        current_best_item_ids = seed["columns"]["nearest_item_ids"]
    elif initial_state == "grid-branch-bound":
        seed_start = time.perf_counter()
        seed = rt.seed_nearest_witness_from_grid_branch_bound_numpy_columns(
            source_columns,
            target_columns,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            executor=grid_branch_bound_seed_executor,
            return_metadata=True,
        )
        seed_sec = time.perf_counter() - seed_start
        current_best_distances = seed["columns"]["nearest_distances"]
        current_best_item_ids = seed["columns"]["nearest_item_ids"]
    elif initial_state != "none":
        raise ValueError(
            "--initial-state must be 'none', 'nearest-cell-mbr', 'local-grid-cell', "
            "'grid-cell-budget', or 'grid-branch-bound'"
        )
    frontier_cell_columns, cell_order_metadata = _order_cell_columns(
        grid["cell_columns"],
        cell_order=cell_order,
    )
    radius_start = time.perf_counter()
    finite_seed_distances = (
        np.asarray(current_best_distances, dtype=np.float64)
        if current_best_distances is not None
        else None
    )
    finite_seed_distances = (
        finite_seed_distances[np.isfinite(finite_seed_distances)]
        if finite_seed_distances is not None
        else None
    )
    direction_radius = (
        float(radius)
        if radius is not None
        else (
            float(np.max(finite_seed_distances)) + 1.0e-12
            if finite_seed_distances is not None and finite_seed_distances.size == len(current_best_distances)
            else float(fallback_radius)
        )
    )
    radius_sec = time.perf_counter() - radius_start
    frontier_start = time.perf_counter()
    exact_seed_frontier_skipped = bool(
        skip_frontier_if_exact_seed
        and seed is not None
        and seed["metadata"].get("seed_quality") == "exact_nearest_witness_under_grid_cell_branch_bound"
    )
    if exact_seed_frontier_skipped:
        frontier_state = {
            "query_point_ids": np.asarray(seed["columns"]["source_ids"], dtype=np.int64),
            "current_best_distances": np.asarray(seed["columns"]["nearest_distances"], dtype=np.float64),
            "current_best_item_ids": np.asarray(seed["columns"]["nearest_item_ids"], dtype=np.int64),
        }
        frontier = {
            "nearest_state": frontier_state,
            "row_table": {
                "columns": {
                    "frontier_kind_codes": np.asarray([], dtype=np.int64),
                    "query_row_ids": np.asarray([], dtype=np.int64),
                    "query_point_ids": np.asarray([], dtype=np.int64),
                    "cell_ids": np.asarray([], dtype=np.int64),
                    "point_begin_offsets": np.asarray([], dtype=np.int64),
                    "point_counts": np.asarray([], dtype=np.int64),
                    "min_distances": np.asarray([], dtype=np.float64),
                    "max_distances": np.asarray([], dtype=np.float64),
                }
            },
            "metadata": {
                "adapter": "exact_seed_frontier_skip",
                "contract": "generic_exact_seed_frontier_skip",
                "row_count": 0,
                "frontier_row_order": "not_applicable_exact_seed",
                "sort_rows": False,
                "inline_nearest": False,
                "global_bound_early_break": False,
                "per_source_witness_exact": True,
                "query_coordinate_matrix_reused": False,
                "target_coordinate_matrix_reused": False,
                "native_generic_symbol": None,
                "exact_seed_frontier_skipped": True,
                "app_semantics": "none",
                "rt_core_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
            },
        }
    elif backend == "optix":
        sort_frontier_rows = frontier_row_order == "sorted"
        frontier = rt.cell_mbr_nearest_frontier_native_3d_optix_columns(
            source_columns,
            frontier_cell_columns,
            target_point_columns=target_columns,
            radius=direction_radius,
            current_best_distances=current_best_distances,
            current_best_item_ids=current_best_item_ids,
            max_inline_points=max_inline_points,
            emit_pruned_rows=False,
            sort_rows=sort_frontier_rows,
            inline_nearest=bool(frontier_inline_nearest),
            collect_inline_stats=bool(collect_inline_stats),
            global_bound_early_break=bool(global_bound_early_break),
            collect_native_phase_timings=bool(collect_frontier_native_phase_timings),
            row_capacity=frontier_row_capacity,
            return_split_frontiers=False,
            return_metadata=True,
        )
    elif backend == "numpy":
        frontier = rt.cell_mbr_nearest_frontier_numpy_columns(
            source_columns,
            frontier_cell_columns,
            coordinate_fields=("x", "y", "z"),
            radius=direction_radius,
            current_best_distances=current_best_distances,
            current_best_item_ids=current_best_item_ids,
            max_inline_points=max_inline_points,
            row_capacity=frontier_row_capacity,
            return_metadata=True,
        )
    else:
        raise ValueError("backend must be 'numpy' or 'optix'")
    frontier_sec = time.perf_counter() - frontier_start
    frontier_state = frontier["nearest_state"]
    nearest_start = time.perf_counter()
    if int(frontier["metadata"]["row_count"]) == 0:
        nearest = _nearest_state_columns_without_completeness_check(
            source_columns,
            frontier_state,
            executor_requested=frontier_nearest_executor,
        )
    else:
        nearest = rt.nearest_witness_from_cell_mbr_frontier_numpy_columns(
            source_columns,
            target_columns,
            frontier_cell_columns,
            frontier["row_table"],
            coordinate_fields=("x", "y", "z"),
            current_best_distances=frontier_state["current_best_distances"],
            current_best_item_ids=frontier_state["current_best_item_ids"],
            executor=frontier_nearest_executor,
            allow_missing=True,
            return_metadata=True,
        )
    nearest = _fill_missing_nearest_with_pairwise_fallback(
        source_columns,
        target_columns,
        nearest,
        coordinate_fields=("x", "y", "z"),
    )
    nearest_sec = time.perf_counter() - nearest_start
    max_start = time.perf_counter()
    max_witness = rt.max_nearest_distance_witness_numpy_columns(
        nearest["columns"],
        return_metadata=True,
    )
    max_sec = time.perf_counter() - max_start
    direction_total_sec = time.perf_counter() - direction_start
    result = {
        "label": label,
        "distance": float(max_witness["value"]),
        "source_id": int(max_witness["source_id"]),
        "target_id": int(max_witness["item_id"]),
        "grid_cell_count": int(grid["metadata"]["cell_count"]),
        "radius": direction_radius,
        "initial_state": initial_state,
        "seed_cell_budget": int(seed_cell_budget),
        "initial_state_contract": None if seed is None else seed["metadata"]["contract"],
        "initial_cell_mbr_selection": None
        if seed is None
        else seed["metadata"].get("cell_mbr_selection"),
        "initial_cell_selection": None
        if seed is None
        else seed["metadata"].get("cell_mbr_selection", seed["metadata"].get("cell_selection")),
        "initial_candidate_distance_evaluations": 0
        if seed is None
        else int(seed["metadata"]["candidate_distance_evaluations"]),
        "initial_cell_mbr_tests": 0 if seed is None else int(seed["metadata"].get("cell_mbr_tests", 0)),
        "initial_grid_cell_probes": 0 if seed is None else int(seed["metadata"].get("grid_cell_probes", 0)),
        "initial_cell_lookup_strategy": None
        if seed is None
        else seed["metadata"].get("cell_lookup_strategy"),
        "initial_seed_executor": None if seed is None else seed["metadata"].get("executor"),
        "initial_seed_executor_requested": None if seed is None else seed["metadata"].get("executor_requested"),
        "initial_query_coordinate_matrix_reused": False
        if seed is None
        else bool(seed["metadata"].get("query_coordinate_matrix_reused", False)),
        "initial_target_coordinate_matrix_reused": False
        if seed is None
        else bool(seed["metadata"].get("target_coordinate_matrix_reused", False)),
        "initial_dense_lookup_cell_capacity": 0
        if seed is None
        else int(seed["metadata"].get("dense_lookup_cell_capacity", 0)),
        "initial_dense_lookup_max_cells": 0
        if seed is None
        else int(seed["metadata"].get("dense_lookup_max_cells", 0)),
        "initial_scanned_cell_count": 0 if seed is None else int(seed["metadata"].get("scanned_cell_count", 0)),
        "initial_scanned_cell_budget_per_query": 0
        if seed is None
        else int(seed["metadata"].get("scanned_cell_budget_per_query", 0)),
        "initial_seed_quality": None if seed is None else seed["metadata"].get("seed_quality", "nearest_cell_mbr"),
        "initial_native_phase_timings_collected": False
        if seed is None
        else bool(seed["metadata"].get("native_phase_timings_collected", False)),
        "initial_native_phase_timings": None if seed is None else seed["metadata"].get("native_phase_timings"),
        "frontier_row_count": int(frontier["metadata"]["row_count"]),
        "exact_seed_frontier_skipped": bool(frontier["metadata"].get("exact_seed_frontier_skipped", False)),
        "exact_seed_frontier_skip_requested": bool(skip_frontier_if_exact_seed),
        "max_inline_points": int(max_inline_points),
        "complete_frontier_state_passthrough": nearest["metadata"]["executor"]
        == "complete_frontier_state_passthrough",
        "candidate_distance_evaluations": int(nearest["metadata"]["candidate_distance_evaluations"]),
        "total_candidate_distance_evaluations": int(nearest["metadata"]["candidate_distance_evaluations"])
        + (0 if seed is None else int(seed["metadata"]["candidate_distance_evaluations"])),
        "frontier_contract": frontier["metadata"]["contract"],
        "cell_order": cell_order_metadata["cell_order"],
        "cell_order_changed": bool(cell_order_metadata["cell_order_changed"]),
        "cell_order_contract": cell_order_metadata["cell_order_contract"],
        "grid_cell_point_order": grid["metadata"].get("cell_point_order"),
        "grid_cell_point_order_contract": grid["metadata"].get("cell_point_order_contract"),
        "grid_cell_builder": grid["metadata"].get("partner"),
        "grid_cell_builder_adapter": grid["metadata"].get("adapter"),
        "grid_cell_builder_native_symbol": grid["metadata"].get("native_generic_symbol"),
        "frontier_native_symbol": frontier["metadata"].get("native_generic_symbol"),
        "frontier_row_order": frontier["metadata"].get("frontier_row_order"),
        "frontier_row_order_requested": frontier_row_order,
        "frontier_sort_rows": bool(frontier["metadata"].get("sort_rows", True)),
        "frontier_inline_nearest": bool(frontier["metadata"].get("inline_nearest", False)),
        "frontier_inline_nearest_requested": bool(frontier_inline_nearest),
        "global_bound_early_break": bool(frontier["metadata"].get("global_bound_early_break", False)),
        "global_bound_early_break_requested": bool(global_bound_early_break),
        "global_bound_early_break_count": frontier["metadata"].get("global_bound_early_break_count"),
        "global_bound_distance": frontier["metadata"].get("global_bound_distance"),
        "global_bound_contract": frontier["metadata"].get("global_bound_contract"),
        "per_source_witness_exact": frontier["metadata"].get("per_source_witness_exact"),
        "inline_stats_collected": bool(frontier["metadata"].get("inline_stats_collected", False)),
        "inline_cell_hit_count": frontier["metadata"].get("inline_cell_hit_count"),
        "inline_point_evaluation_count": frontier["metadata"].get("inline_point_evaluation_count"),
        "inline_nearest_pruning": frontier["metadata"].get("inline_nearest_pruning"),
        "intersection_pruning": frontier["metadata"].get("intersection_pruning"),
        "intersection_attribute_min_distance_sq": frontier["metadata"].get(
            "intersection_attribute_min_distance_sq"
        ),
        "anyhit_row_distance_computation": frontier["metadata"].get("anyhit_row_distance_computation"),
        "frontier_query_coordinate_matrix_reused": bool(
            frontier["metadata"].get("query_coordinate_matrix_reused", False)
        ),
        "frontier_target_coordinate_matrix_reused": bool(
            frontier["metadata"].get("target_coordinate_matrix_reused", False)
        ),
        "frontier_native_phase_timings_collected": bool(
            frontier["metadata"].get("native_phase_timings_collected", False)
        ),
        "frontier_native_phase_timings": frontier["metadata"].get("native_phase_timings"),
        "frontier_native_memory_telemetry_collected": bool(
            frontier["metadata"].get("native_memory_telemetry_collected", False)
        ),
        "frontier_native_memory_telemetry": frontier["metadata"].get("native_memory_telemetry"),
        "frontier_row_capacity_requested": None
        if frontier_row_capacity is None
        else int(frontier_row_capacity),
        "frontier_row_capacity": frontier["metadata"].get("row_capacity"),
        "frontier_full_row_capacity": frontier["metadata"].get("full_row_capacity"),
        "frontier_row_capacity_policy": frontier["metadata"].get("row_capacity_policy"),
        "frontier_row_capacity_attempts": list(frontier["metadata"].get("row_capacity_attempts", ())),
        "frontier_attempted_count": frontier["metadata"].get("attempted_count"),
        "nearest_contract": nearest["metadata"]["contract"],
        "nearest_executor": nearest["metadata"]["executor"],
        "nearest_executor_requested": nearest["metadata"]["executor_requested"],
        "nearest_reduction_strategy": nearest["metadata"]["reduction_strategy"],
        "missing_nearest_fallback_count": nearest["metadata"].get("missing_nearest_fallback_count", 0),
        "missing_nearest_fallback_candidate_rows": nearest["metadata"].get(
            "missing_nearest_fallback_candidate_rows",
            0,
        ),
        "missing_nearest_fallback_contract": nearest["metadata"].get(
            "missing_nearest_fallback_contract"
        ),
        "max_contract": max_witness["metadata"]["contract"],
        "max_reduction_strategy": max_witness["metadata"].get("reduction_strategy"),
        "max_tie_candidate_count": max_witness["metadata"].get("tie_candidate_count"),
        "phase_timings_sec": {
            "source_columns": source_columns_sec,
            "target_columns": target_columns_sec,
            "grid_cell_mbrs": grid_sec,
            "initial_state_seed": seed_sec,
            "radius_selection": radius_sec,
            "frontier_rows": frontier_sec,
            "nearest_continuation": nearest_sec,
            "max_nearest_reduction": max_sec,
            "direction_total": direction_total_sec,
        },
    }
    if emit_nearest_columns:
        nearest_columns = nearest["columns"]
        result["nearest_columns"] = {
            "source_ids": np.asarray(nearest_columns["source_ids"], dtype=np.int64).tolist(),
            "nearest_item_ids": np.asarray(nearest_columns["nearest_item_ids"], dtype=np.int64).tolist(),
            "nearest_distances": np.asarray(nearest_columns["nearest_distances"], dtype=np.float64).tolist(),
            "contract": nearest["metadata"]["contract"],
            "app_semantics": nearest["metadata"].get("app_semantics", "none"),
            "metadata": {
                "missing_nearest_fallback_count": int(
                    nearest["metadata"].get("missing_nearest_fallback_count", 0)
                ),
                "missing_nearest_fallback_candidate_rows": int(
                    nearest["metadata"].get("missing_nearest_fallback_candidate_rows", 0)
                ),
                "coverage_complete_before_fallback": bool(
                    nearest["metadata"].get("coverage_complete", True)
                ),
                "allow_missing": bool(nearest["metadata"].get("allow_missing", False)),
                "reduction_strategy": nearest["metadata"].get("reduction_strategy"),
            },
        }
    return result


def _single_pass_radius_trace_metadata(
    *,
    directed_a_to_b: dict[str, object],
    directed_b_to_a: dict[str, object] | None,
    point_count_a: int,
    point_count_b: int,
    grid_shape: tuple[int, int, int],
    radius: float | None,
    fallback_radius: float,
    direction_mode: str,
) -> dict[str, object]:
    """Build app-owned radius trace metadata for the current single-pass route.

    The current RTDL cell-MBR route is not the author's iterative radius queue.
    This diagnostic therefore records the selected route radius and frontier
    output proxy while explicitly marking author queue semantics as unaligned.
    """

    def direction_row(label: str, directed: dict[str, object], source_count: int, target_count: int) -> dict[str, object]:
        return {
            "label": label,
            "iteration": 1,
            "radius": float(directed["radius"]),
            "radius_source": "explicit_cli_radius" if radius is not None else "route_auto_selected_radius",
            "num_input_points": int(source_count),
            "num_output_points": int(directed["frontier_row_count"]),
            "target_point_count": int(target_count),
            "input_count_semantics": "source_point_count_before_single_pass_not_author_in_queue",
            "output_count_semantics": "frontier_row_count_after_single_pass_not_author_out_queue",
            "grid_shape": [int(value) for value in grid_shape],
            "initial_state": directed.get("initial_state"),
            "frontier_row_count": int(directed["frontier_row_count"]),
            "global_bound_early_break": bool(directed.get("global_bound_early_break", False)),
            "global_bound_early_break_count": directed.get("global_bound_early_break_count"),
            "per_source_witness_exact": directed.get("per_source_witness_exact"),
        }

    directions = [direction_row("a_to_b", directed_a_to_b, point_count_a, point_count_b)]
    if directed_b_to_a is not None:
        directions.append(direction_row("b_to_a", directed_b_to_a, point_count_b, point_count_a))

    return {
        "schema": "rtdl.paper_reproduction.xhd.route_radius_trace_metadata.v1",
        "status": "single_pass_cell_mbr_radius_trace_metadata_available__author_queue_semantics_not_aligned",
        "source": "app_owned_internal_diagnostic",
        "direction_mode": direction_mode,
        "route_iteration_model": "single_pass_cell_mbr_route_not_author_radius_loop",
        "route_uses_radius_growth_helper": False,
        "author_tune_radius_supported": False,
        "author_queue_semantics_aligned": False,
        "author_trace_comparison_ready": False,
        "fallback_full_cover_radius": float(fallback_radius),
        "directions": directions,
        "claim_boundary": {
            "author_tune_radius_route_mapping_claimed": False,
            "author_rt_core_algorithm_equivalence_claimed": False,
            "figure8_reproduction_claimed": False,
            "performance_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
        "next_required_gate": (
            "compare this RTDL route trace against author hd_exec iteration traces "
            "only after a route variant emits author-like radius/input/output "
            "iterations; this single-pass diagnostic is not itself trace parity."
        ),
    }


def build_summary(args: argparse.Namespace) -> dict[str, object]:
    input_n_dims = int(args.n_dims)
    lift_2d_to_3d_zero_z = bool(getattr(args, "lift_2d_to_3d_zero_z", False))
    if input_n_dims not in {2, 3}:
        raise ValueError("cell-MBR frontier route gate supports only 2-D or 3-D inputs")
    if input_n_dims == 2 and not lift_2d_to_3d_zero_z:
        raise ValueError(
            "2-D cell-MBR inputs require explicit --lift-2d-to-3d-zero-z; "
            "the default 2-D route remains public-columnar"
        )
    validation_mode = getattr(args, "validation_mode", "exact-and-author")
    if validation_mode not in {"exact-and-author", "author-only", "none"}:
        raise ValueError("--validation-mode must be exact-and-author, author-only, or none")
    frontier_nearest_executor = getattr(args, "frontier_nearest_executor", "auto")
    local_grid_seed_executor = getattr(args, "local_grid_seed_executor", "auto")
    grid_branch_bound_seed_executor = getattr(args, "grid_branch_bound_seed_executor", "auto")
    frontier_row_order = getattr(args, "frontier_row_order", "sorted")
    cell_order = getattr(args, "cell_order", "native")
    grid_cell_point_order = getattr(args, "grid_cell_point_order", "point-id")
    grid_cell_builder = getattr(args, "grid_cell_builder", "numpy")
    skip_frontier_if_exact_seed = bool(getattr(args, "skip_frontier_if_exact_seed", False))
    frontier_inline_nearest = bool(getattr(args, "frontier_inline_nearest", False))
    global_bound_early_break = bool(getattr(args, "global_bound_early_break", False))
    collect_inline_stats = bool(getattr(args, "collect_inline_stats", False))
    collect_frontier_native_phase_timings = bool(
        getattr(args, "collect_frontier_native_phase_timings", False)
    )
    emit_radius_trace_metadata = bool(getattr(args, "emit_radius_trace_metadata", False))
    seed_cell_budget = int(getattr(args, "seed_cell_budget", 4))
    frontier_row_capacity = getattr(args, "frontier_row_capacity", None)
    if frontier_row_capacity is not None and int(frontier_row_capacity) < 0:
        raise ValueError("--frontier-row-capacity must be non-negative")
    direction_mode = getattr(args, "direction_mode", "symmetric-diagnostic")
    if frontier_row_order not in {"sorted", "native"}:
        raise ValueError("--frontier-row-order must be sorted or native")
    if cell_order not in {"native", "point-count-asc", "point-count-desc"}:
        raise ValueError("--cell-order must be native, point-count-asc, or point-count-desc")
    if grid_cell_point_order not in {"point-id", "input-stable"}:
        raise ValueError("--grid-cell-point-order must be point-id or input-stable")
    if grid_cell_builder not in {"numpy", "native_cuda"}:
        raise ValueError("--grid-cell-builder must be numpy or native_cuda")
    if direction_mode not in {"symmetric-diagnostic", "directed-a-to-b"}:
        raise ValueError("--direction-mode must be symmetric-diagnostic or directed-a-to-b")
    total_start = time.perf_counter()
    input1 = Path(args.input1)
    input2 = Path(args.input2)
    load_start = time.perf_counter()
    points_a = load_points_matrix(input1, n_dims=input_n_dims, input_type=args.input_type)
    points_b = load_points_matrix(input2, n_dims=input_n_dims, input_type=args.input_type)
    point_input_representation = "numpy_coordinate_matrix"
    preprocessing: list[str] = []
    if input_n_dims == 2:
        points_a = lift_point_matrix_2d_to_3d_zero_z(points_a, copy=False)
        points_b = lift_point_matrix_2d_to_3d_zero_z(points_b, copy=False)
        preprocessing.append("lift_2d_to_3d_zero_z_for_cell_mbr")
    if bool(getattr(args, "normalize_each_input_to_author_unit_box", False)):
        if bool(getattr(args, "author_float32_normalization", False)):
            points_a = normalize_point_matrix_to_author_float32_unit_box(points_a, copy=False)
            points_b = normalize_point_matrix_to_author_float32_unit_box(points_b, copy=False)
            preprocessing.append("normalize_each_input_to_author_float32_unit_box")
        else:
            points_a = normalize_point_matrix_to_author_unit_box(points_a, copy=False)
            points_b = normalize_point_matrix_to_author_unit_box(points_b, copy=False)
            preprocessing.append("normalize_each_input_to_author_unit_box")
    if args.translate_each_input_to_min_bound:
        points_a = translate_point_matrix_to_min_bound(points_a, copy=False)
        points_b = translate_point_matrix_to_min_bound(points_b, copy=False)
        preprocessing.append("translate_each_input_to_min_bound")
    load_sec = time.perf_counter() - load_start
    exact = None
    exact_sec: float | None = None
    if validation_mode == "exact-and-author":
        exact_start = time.perf_counter()
        exact = exact_hausdorff(point_matrix_to_rows(points_a), point_matrix_to_rows(points_b))
        exact_sec = time.perf_counter() - exact_start
    grid_shape = _parse_grid_shape(args.grid_shape)
    fallback_radius = _full_cover_radius(points_a, points_b)
    radius = None if args.radius is None else float(args.radius)

    route_start = time.perf_counter()
    directed_ab = _directed_cell_mbr_route(
        points_a,
        points_b,
        label="a_to_b",
        backend=args.backend,
        grid_shape=grid_shape,
        radius=radius,
        fallback_radius=fallback_radius,
        max_inline_points=args.max_inline_points,
        initial_state=args.initial_state,
        seed_cell_budget=seed_cell_budget,
        local_grid_seed_executor=local_grid_seed_executor,
        grid_branch_bound_seed_executor=grid_branch_bound_seed_executor,
        frontier_nearest_executor=frontier_nearest_executor,
        frontier_row_order=frontier_row_order,
        frontier_inline_nearest=frontier_inline_nearest,
        cell_order=cell_order,
        grid_cell_point_order=grid_cell_point_order,
        grid_cell_builder=grid_cell_builder,
        skip_frontier_if_exact_seed=skip_frontier_if_exact_seed,
        global_bound_early_break=global_bound_early_break,
        collect_inline_stats=collect_inline_stats,
        collect_frontier_native_phase_timings=collect_frontier_native_phase_timings,
        frontier_row_capacity=frontier_row_capacity,
    )
    directed_ba = None
    if direction_mode == "symmetric-diagnostic":
        directed_ba = _directed_cell_mbr_route(
            points_b,
            points_a,
            label="b_to_a",
            backend=args.backend,
            grid_shape=grid_shape,
            radius=radius,
            fallback_radius=fallback_radius,
            max_inline_points=args.max_inline_points,
            initial_state=args.initial_state,
            seed_cell_budget=seed_cell_budget,
            local_grid_seed_executor=local_grid_seed_executor,
            grid_branch_bound_seed_executor=grid_branch_bound_seed_executor,
            frontier_nearest_executor=frontier_nearest_executor,
            frontier_row_order=frontier_row_order,
            frontier_inline_nearest=frontier_inline_nearest,
            cell_order=cell_order,
            grid_cell_point_order=grid_cell_point_order,
            grid_cell_builder=grid_cell_builder,
            skip_frontier_if_exact_seed=skip_frontier_if_exact_seed,
            global_bound_early_break=global_bound_early_break,
            collect_inline_stats=collect_inline_stats,
            collect_frontier_native_phase_timings=collect_frontier_native_phase_timings,
            frontier_row_capacity=frontier_row_capacity,
        )
    route_sec = time.perf_counter() - route_start
    route_hausdorff = (
        None
        if directed_ba is None
        else max(float(directed_ab["distance"]), float(directed_ba["distance"]))
    )
    exact_reference_key = "directed_a_to_b" if direction_mode == "directed-a-to-b" else "hausdorff"
    route_exact_value = float(directed_ab["distance"]) if direction_mode == "directed-a-to-b" else float(route_hausdorff)
    exact_diff = None if exact is None else abs(route_exact_value - float(exact[exact_reference_key]))

    author_json = Path(args.author_json) if args.author_json else None
    author_hd = (
        load_author_hd_result(author_json)
        if validation_mode != "none" and author_json is not None and author_json.exists()
        else None
    )
    author_reference_key = "directed_a_to_b"
    author_comparison_distance = float(directed_ab["distance"])
    author_abs_diff = None if author_hd is None else abs(float(author_hd) - author_comparison_distance)
    author_matched = None if author_abs_diff is None else bool(author_abs_diff <= args.tolerance)
    validation_checks = []
    if author_matched is not None:
        validation_checks.append(author_matched)
    if exact_diff is not None:
        validation_checks.append(bool(exact_diff <= args.tolerance))
    matched = None if not validation_checks else bool(all(validation_checks))
    total_sec = time.perf_counter() - total_start
    radius_trace_metadata = (
        _single_pass_radius_trace_metadata(
            directed_a_to_b=directed_ab,
            directed_b_to_a=directed_ba,
            point_count_a=len(points_a),
            point_count_b=len(points_b),
            grid_shape=grid_shape,
            radius=radius,
            fallback_radius=fallback_radius,
            direction_mode=direction_mode,
        )
        if emit_radius_trace_metadata
        else None
    )

    summary = {
        "schema": "rtdl.paper_reproduction.xhd.cell_mbr_frontier_route_gate.v1",
        "paper_app": "x-hd-paper",
        "input1": str(input1),
        "input2": str(input2),
        "n_dims": 3,
        "input_n_dims": input_n_dims,
        "execution_n_dims": 3,
        "lift_2d_to_3d_zero_z": lift_2d_to_3d_zero_z,
        "input_type": args.input_type,
        "point_input_representation": point_input_representation,
        "point_count_a": len(points_a),
        "point_count_b": len(points_b),
        "reference_preprocessing": preprocessing,
        "backend": args.backend,
        "grid_shape": grid_shape,
        "radius": "auto" if radius is None else radius,
        "fallback_full_cover_radius": fallback_radius,
        "max_inline_points": int(args.max_inline_points),
        "initial_state": args.initial_state,
        "seed_cell_budget": seed_cell_budget,
        "local_grid_seed_executor": local_grid_seed_executor,
        "grid_branch_bound_seed_executor": grid_branch_bound_seed_executor,
        "frontier_nearest_executor": frontier_nearest_executor,
        "frontier_row_order": frontier_row_order,
        "cell_order": cell_order,
        "grid_cell_point_order": grid_cell_point_order,
        "grid_cell_builder": grid_cell_builder,
        "skip_frontier_if_exact_seed": skip_frontier_if_exact_seed,
        "frontier_inline_nearest": frontier_inline_nearest,
        "global_bound_early_break": global_bound_early_break,
        "collect_inline_stats": collect_inline_stats,
        "collect_frontier_native_phase_timings": collect_frontier_native_phase_timings,
        "emit_radius_trace_metadata": emit_radius_trace_metadata,
        "frontier_row_capacity": None if frontier_row_capacity is None else int(frontier_row_capacity),
        "direction_mode": direction_mode,
        "validation_mode": validation_mode,
        "rtdl_route": {
            "route": f"rtdl_cell_mbr_frontier_{args.backend}_3d",
            "directed_a_to_b": directed_ab,
            "directed_b_to_a": directed_ba,
            "hausdorff": route_hausdorff,
            "exact_reference_key": exact_reference_key,
            "route_contract": (
                "RTDL 3-D cell-MBR frontier route using generic grid-cell MBRs, "
                "generic cell-MBR frontier rows, generic nearest-witness continuation, "
                "and generic max-nearest reduction. It is not the author X-HD "
                "RT-core implementation and not a performance claim. When explicitly "
                "requested, 2-D inputs are embedded into z=0 before this generic 3-D route."
            ),
        },
        "exact_reference": exact,
        "rtdl_exact_abs_diff": exact_diff,
        "rtdl_matches_exact_reference": None if exact_diff is None else bool(exact_diff <= args.tolerance),
        "author_comparison_reference": author_reference_key,
        "author_comparison_distance": author_comparison_distance,
        "author_json": None if author_json is None else str(author_json),
        "author_hd_result": author_hd,
        "author_abs_diff": author_abs_diff,
        "tolerance": args.tolerance,
        "matched": matched,
        "run_phases": {
            "load_input_sec": load_sec,
            "exact_reference_sec": exact_sec,
            "rtdl_route_sec": route_sec,
            "validation_mode": validation_mode,
            "total_sec": total_sec,
        },
        "boundary": (
            "Representative same-input RTDL cell-MBR frontier route gate. This "
            "uses generic RTDL system APIs and compares against the exact value "
            "and optional author HDResult for the same bounded fixture. It is not "
            "full X-HD paper reproduction, not the author's fused RT algorithm, "
            "and not a performance claim."
        ),
        "paper_reproduction_claim_authorized": False,
        "performance_claim_authorized": False,
        "author_performance_parity_claimed": False,
    }
    if radius_trace_metadata is not None:
        summary["radius_trace_metadata"] = radius_trace_metadata
    return summary


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the X-HD cell-MBR frontier route gate.")
    parser.add_argument("--input1", required=True)
    parser.add_argument("--input2", required=True)
    parser.add_argument("--n-dims", type=int, default=3)
    parser.add_argument("--input-type", default="ply", choices=("wkt", "ply", "off"))
    parser.add_argument(
        "--lift-2d-to-3d-zero-z",
        action="store_true",
        help=(
            "Explicitly embed 2-D inputs into z=0 so they can use the generic "
            "3-D cell-MBR route. This is disabled by default."
        ),
    )
    parser.add_argument(
        "--normalize-each-input-to-author-unit-box",
        action="store_true",
        help=(
            "Apply the author X-HD NormalizePoints transform to each input "
            "before route execution: subtract per-axis lower bounds and divide "
            "by the largest axis extent of that input."
        ),
    )
    parser.add_argument(
        "--author-float32-normalization",
        action="store_true",
        help=(
            "When author-unit-box normalization is enabled, perform the "
            "normalization arithmetic with float32 coordinate semantics to "
            "match the author paper branch's default float implementation."
        ),
    )
    parser.add_argument("--translate-each-input-to-min-bound", action="store_true")
    parser.add_argument("--backend", default="numpy", choices=("numpy", "optix"))
    parser.add_argument("--grid-shape", default="4,4,4")
    parser.add_argument("--radius", type=float)
    parser.add_argument("--max-inline-points", type=int, default=64)
    parser.add_argument(
        "--initial-state",
        default="none",
        choices=("none", "nearest-cell-mbr", "local-grid-cell", "grid-cell-budget", "grid-branch-bound"),
    )
    parser.add_argument(
        "--seed-cell-budget",
        type=int,
        default=4,
        help=(
            "For --initial-state=grid-cell-budget, scan at most this many "
            "nearby occupied grid cells per query while building the generic "
            "nearest-state upper-bound seed."
        ),
    )
    parser.add_argument(
        "--frontier-nearest-executor",
        default="auto",
        choices=("auto", "numpy", "numba", "numba_parallel"),
    )
    parser.add_argument(
        "--local-grid-seed-executor",
        default="auto",
        choices=("auto", "numba", "numba_parallel", "native_cuda"),
        help=(
            "Executor for --initial-state=local-grid-cell. native_cuda is an "
            "explicit experimental generic CUDA seed path; the default keeps "
            "the existing Numba route."
        ),
    )
    parser.add_argument(
        "--grid-branch-bound-seed-executor",
        default="auto",
        choices=("auto", "numba", "numba_parallel", "native_cuda"),
        help=(
            "Executor for --initial-state=grid-branch-bound. native_cuda is an "
            "explicit experimental generic CUDA exact grid branch-bound seed path; "
            "the default keeps the existing Numba route."
        ),
    )
    parser.add_argument(
        "--frontier-row-order",
        default="sorted",
        choices=("sorted", "native"),
        help=(
            "Native OptiX frontier row ordering policy. sorted preserves the "
            "legacy sorted+unique row table; native leaves rows in backend "
            "emission order for streaming consumers that do their own grouping."
        ),
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
    parser.add_argument(
        "--grid-cell-point-order",
        default="point-id",
        choices=("point-id", "input-stable"),
        help=(
            "Point ordering inside each generic grid cell. point-id preserves "
            "the historical cell_id/point_id order; input-stable preserves "
            "input order within each cell and is valid for nearest routes whose "
            "tie-break is computed explicitly by item id."
        ),
    )
    parser.add_argument(
        "--grid-cell-builder",
        default="numpy",
        choices=("numpy", "native_cuda"),
        help=(
            "Generic point-grid cell MBR builder backend. numpy preserves the "
            "existing reference path; native_cuda uses the experimental "
            "CUDA/Thrust 3-D builder with the same cell-column contract."
        ),
    )
    parser.add_argument(
        "--frontier-inline-nearest",
        action="store_true",
        help=(
            "Ask the native 3-D cell-MBR frontier producer to compute nearest "
            "witnesses for inline frontier rows and leave only offload rows for "
            "the downstream continuation."
        ),
    )
    parser.add_argument(
        "--skip-frontier-if-exact-seed",
        action="store_true",
        help=(
            "Experimental generic route shortcut: if the selected initial-state "
            "seed declares per-source exact nearest witnesses, bypass the "
            "frontier producer and reduce the exact seed directly."
        ),
    )
    parser.add_argument(
        "--global-bound-early-break",
        action="store_true",
        help=(
            "Enable the optional generic max-nearest global-bound early-break "
            "contract in native inline-nearest traversal. Early-aborted "
            "per-source witnesses may be approximate; the flag is experimental."
        ),
    )
    parser.add_argument(
        "--collect-inline-stats",
        action="store_true",
        help=(
            "Use the optional native telemetry ABI to count inline cell hits "
            "and inline point-distance evaluations. This is diagnostic and may "
            "add counter overhead."
        ),
    )
    parser.add_argument(
        "--collect-frontier-native-phase-timings",
        action="store_true",
        help=(
            "Collect diagnostic native phase timings for the generic OptiX "
            "cell-MBR frontier collector. This does not change route semantics "
            "and is not a performance claim by itself."
        ),
    )
    parser.add_argument(
        "--emit-radius-trace-metadata",
        action="store_true",
        help=(
            "Emit app-owned internal radius trace metadata for the current "
            "single-pass cell-MBR route. This is diagnostic only and does not "
            "enable author tune_radius semantics."
        ),
    )
    parser.add_argument(
        "--frontier-row-capacity",
        type=int,
        help=(
            "Explicit fail-closed capacity for generic cell-MBR frontier rows. "
            "If omitted, the backend may use its default or inferred policy."
        ),
    )
    parser.add_argument(
        "--direction-mode",
        default="symmetric-diagnostic",
        choices=("symmetric-diagnostic", "directed-a-to-b"),
        help=(
            "symmetric-diagnostic preserves the historical route by also running "
            "B->A and reporting a symmetric diagnostic. directed-a-to-b matches "
            "the author HDResult contract proven by Goal5126 and avoids the "
            "extra diagnostic direction."
        ),
    )
    parser.add_argument(
        "--validation-mode",
        default="exact-and-author",
        choices=("exact-and-author", "author-only", "none"),
        help=(
            "Validation included in total_sec. exact-and-author runs the exact "
            "reference and optional author comparison; author-only skips exact "
            "reference; none skips both."
        ),
    )
    parser.add_argument("--author-json")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--tolerance", type=float, default=1e-6)
    args = parser.parse_args(list(argv) if argv is not None else None)

    summary = build_summary(args)
    out = Path(args.summary)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["matched"] is not False else 1


if __name__ == "__main__":
    raise SystemExit(main())
