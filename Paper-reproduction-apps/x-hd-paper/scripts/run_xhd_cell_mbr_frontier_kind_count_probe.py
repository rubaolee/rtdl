from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from xhd_input_loader import load_points_matrix
from xhd_input_loader import lift_point_matrix_2d_to_3d_zero_z
from xhd_input_loader import normalize_point_matrix_to_author_float32_unit_box
from xhd_input_loader import normalize_point_matrix_to_author_unit_box
from xhd_input_loader import translate_point_matrix_to_min_bound


def _coordinate_matrix_3d(points: object) -> np.ndarray:
    coords = np.asarray(points, dtype=np.float64)
    if coords.ndim != 2 or coords.shape[1] != 3:
        raise ValueError("3-D frontier kind-count probe expects an Nx3 point matrix")
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
    return float(math.sqrt(float(np.sum((maxs - mins) * (maxs - mins)))) + 1.0e-9)


def _parse_grid_shape(value: str) -> tuple[int, int, int]:
    parts = tuple(int(item) for item in value.lower().replace("x", ",").split(",") if item.strip())
    if len(parts) != 3:
        raise ValueError("--grid-shape must contain three dimensions, e.g. 96,60,72")
    if any(part <= 0 for part in parts):
        raise ValueError("--grid-shape dimensions must be positive")
    return parts


def _load_preprocessed_points(args: argparse.Namespace) -> tuple[np.ndarray, np.ndarray, list[str]]:
    points_a = load_points_matrix(Path(args.input1), n_dims=int(args.n_dims), input_type=args.input_type)
    points_b = load_points_matrix(Path(args.input2), n_dims=int(args.n_dims), input_type=args.input_type)
    preprocessing: list[str] = []
    if int(args.n_dims) == 2:
        if not bool(args.lift_2d_to_3d_zero_z):
            raise ValueError("2-D probes require --lift-2d-to-3d-zero-z")
        points_a = lift_point_matrix_2d_to_3d_zero_z(points_a, copy=False)
        points_b = lift_point_matrix_2d_to_3d_zero_z(points_b, copy=False)
        preprocessing.append("lift_2d_to_3d_zero_z_for_cell_mbr")
    if bool(args.normalize_each_input_to_author_unit_box):
        if bool(args.author_float32_normalization):
            points_a = normalize_point_matrix_to_author_float32_unit_box(points_a, copy=False)
            points_b = normalize_point_matrix_to_author_float32_unit_box(points_b, copy=False)
            preprocessing.append("normalize_each_input_to_author_float32_unit_box")
        else:
            points_a = normalize_point_matrix_to_author_unit_box(points_a, copy=False)
            points_b = normalize_point_matrix_to_author_unit_box(points_b, copy=False)
            preprocessing.append("normalize_each_input_to_author_unit_box")
    if bool(args.translate_each_input_to_min_bound):
        points_a = translate_point_matrix_to_min_bound(points_a, copy=False)
        points_b = translate_point_matrix_to_min_bound(points_b, copy=False)
        preprocessing.append("translate_each_input_to_min_bound")
    return _coordinate_matrix_3d(points_a), _coordinate_matrix_3d(points_b), preprocessing


def build_summary(args: argparse.Namespace) -> dict[str, object]:
    total_start = time.perf_counter()
    load_start = time.perf_counter()
    points_a, points_b, preprocessing = _load_preprocessed_points(args)
    load_sec = time.perf_counter() - load_start
    source_columns = _columns_3d(points_a)
    target_columns = _columns_3d(points_b)
    grid_shape = _parse_grid_shape(args.grid_shape)
    radius = _full_cover_radius(points_a, points_b) if args.radius is None else float(args.radius)

    grid_start = time.perf_counter()
    if args.grid_cell_builder == "native_cuda":
        grid = rt.point_grid_cell_mbrs_native_3d_cuda_columns(
            target_columns,
            coordinate_fields=("x", "y", "z"),
            grid_shape=grid_shape,
            cell_point_order=args.grid_cell_point_order,
            return_metadata=True,
        )
    elif args.grid_cell_builder == "numpy":
        grid = rt.point_grid_cell_mbrs_numpy_columns(
            target_columns,
            coordinate_fields=("x", "y", "z"),
            grid_shape=grid_shape,
            cell_point_order=args.grid_cell_point_order,
            return_metadata=True,
        )
    else:
        raise ValueError("--grid-cell-builder must be native_cuda or numpy")
    grid_sec = time.perf_counter() - grid_start

    frontier_start = time.perf_counter()
    frontier = rt.cell_mbr_nearest_frontier_native_3d_optix_columns(
        source_columns,
        grid["cell_columns"],
        target_point_columns=target_columns if bool(args.inline_nearest) else None,
        radius=radius,
        current_best_distances=None,
        current_best_item_ids=None,
        max_inline_points=int(args.max_inline_points),
        row_capacity=int(args.frontier_row_capacity),
        emit_pruned_rows=bool(args.emit_pruned_rows),
        sort_rows=False,
        inline_nearest=bool(args.inline_nearest),
        collect_inline_stats=bool(args.collect_inline_stats),
        global_bound_early_break=bool(args.global_bound_early_break),
        frontier_status_probe_mode=args.frontier_status_probe_mode,
        collect_native_phase_timings=bool(args.collect_frontier_native_phase_timings),
        allow_overflow_telemetry=True,
        return_split_frontiers=False,
        return_metadata=True,
    )
    frontier_sec = time.perf_counter() - frontier_start
    metadata = frontier["metadata"]
    native_memory = metadata.get("native_memory_telemetry") or {}
    raw_kind_counts = native_memory.get("raw_frontier_kind_counts") or {}
    raw_kind2 = int(native_memory.get("raw_frontier_kind2_rows", raw_kind_counts.get("2", 0) or 0))
    author_rows = None if args.author_offloading_size is None else int(args.author_offloading_size)
    comparison = None
    if author_rows is not None:
        comparison = {
            "author_offloading_size_rows": author_rows,
            "rtdl_raw_frontier_kind2_rows": raw_kind2,
            "row_delta_author_minus_rtdl_kind2": int(author_rows - raw_kind2),
            "row_ratio_rtdl_kind2_div_author": (raw_kind2 / author_rows) if author_rows else None,
            "row_count_parity": bool(raw_kind2 == author_rows),
        }

    return {
        "schema": "rtdl.paper_reproduction.xhd.cell_mbr_frontier_kind_count_probe.v1",
        "paper_app": "x-hd-paper",
        "purpose": (
            "Generic cell-MBR frontier count-only diagnostic. Counts raw frontier "
            "rows by generic kind before host row download/materialization."
        ),
        "input1": str(args.input1),
        "input2": str(args.input2),
        "input_type": args.input_type,
        "input_n_dims": int(args.n_dims),
        "execution_n_dims": 3,
        "point_count_a": int(points_a.shape[0]),
        "point_count_b": int(points_b.shape[0]),
        "preprocessing": preprocessing,
        "grid_shape": grid_shape,
        "grid_cell_builder": args.grid_cell_builder,
        "grid_cell_point_order": args.grid_cell_point_order,
        "radius": radius,
        "max_inline_points": int(args.max_inline_points),
        "frontier_row_capacity": int(args.frontier_row_capacity),
        "emit_pruned_rows": bool(args.emit_pruned_rows),
        "inline_nearest": bool(args.inline_nearest),
        "collect_inline_stats": bool(args.collect_inline_stats),
        "global_bound_early_break": bool(args.global_bound_early_break),
        "frontier_status_probe_mode": args.frontier_status_probe_mode,
        "frontier": {
            "row_count": int(metadata.get("row_count", 0)),
            "attempted_count": int(metadata.get("attempted_count", 0)),
            "row_capacity": int(metadata.get("row_capacity", 0)),
            "overflowed": bool(metadata.get("overflowed", False)),
            "overflow_telemetry_only": bool(metadata.get("overflow_telemetry_only", False)),
            "overflow_failure_mode": metadata.get("overflow_failure_mode"),
            "native_symbol": metadata.get("native_generic_symbol"),
            "native_memory_telemetry_collected": bool(metadata.get("native_memory_telemetry_collected", False)),
            "native_memory_telemetry": native_memory,
            "raw_frontier_kind_counts": raw_kind_counts,
            "raw_frontier_kind1_rows": int(native_memory.get("raw_frontier_kind1_rows", 0) or 0),
            "raw_frontier_kind2_rows": raw_kind2,
            "raw_frontier_kind3_rows": int(native_memory.get("raw_frontier_kind3_rows", 0) or 0),
            "frontier_row_order": metadata.get("frontier_row_order"),
            "global_bound_early_break_count": metadata.get("global_bound_early_break_count"),
            "global_bound_distance": metadata.get("global_bound_distance"),
            "frontier_status_probe_contract": metadata.get("frontier_status_probe_contract"),
            "frontier_status_probe_mode_code": metadata.get("frontier_status_probe_mode_code"),
            "inline_cell_hit_count": metadata.get("inline_cell_hit_count"),
            "inline_point_eval_count": metadata.get("inline_point_eval_count"),
        },
        "comparison_to_author": comparison,
        "timings_sec": {
            "load_inputs": load_sec,
            "grid_cell_mbrs": grid_sec,
            "frontier_probe": frontier_sec,
            "total": time.perf_counter() - total_start,
        },
        "claim_boundary": {
            "full_xhd_paper_reproduction_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "explicit_lb_support_claimed": False,
            "row_count_parity_claimed": False,
            "same_denominator_memory_claimed": False,
            "performance_claimed": False,
            "author_rt_core_algorithm_parity_claimed": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input1", required=True)
    parser.add_argument("--input2", required=True)
    parser.add_argument("--input-type", default="ply", choices=("csv", "ply", "off"))
    parser.add_argument("--n-dims", type=int, default=3)
    parser.add_argument("--lift-2d-to-3d-zero-z", action="store_true")
    parser.add_argument("--normalize-each-input-to-author-unit-box", action="store_true")
    parser.add_argument("--author-float32-normalization", action="store_true")
    parser.add_argument("--translate-each-input-to-min-bound", action="store_true")
    parser.add_argument("--grid-shape", default="96,60,72")
    parser.add_argument("--grid-cell-builder", default="native_cuda", choices=("native_cuda", "numpy"))
    parser.add_argument("--grid-cell-point-order", default="point-id", choices=("point-id", "input-stable"))
    parser.add_argument("--radius", type=float, default=None)
    parser.add_argument("--max-inline-points", type=int, required=True)
    parser.add_argument("--frontier-row-capacity", type=int, default=0)
    parser.add_argument("--emit-pruned-rows", action="store_true")
    parser.add_argument("--inline-nearest", action="store_true")
    parser.add_argument("--collect-inline-stats", action="store_true")
    parser.add_argument("--global-bound-early-break", action="store_true")
    parser.add_argument(
        "--frontier-status-probe-mode",
        default="default",
        choices=("default", "heavy-before-inline-prune", "active-initial-best-prune"),
    )
    parser.add_argument("--collect-frontier-native-phase-timings", action="store_true")
    parser.add_argument("--author-offloading-size", type=int, default=None)
    parser.add_argument("--summary", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = build_summary(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
