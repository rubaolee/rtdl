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


RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
DEFAULT_ORACLE = RESULTS / "xhd_goal5374_author_lb_status_trace_oracle.json"


def _coordinate_matrix_3d(points: object) -> np.ndarray:
    coords = np.asarray(points, dtype=np.float64)
    if coords.ndim != 2 or coords.shape[1] != 3:
        raise ValueError("active-query frontier bridge probe expects an Nx3 point matrix")
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
    if args.source_limit is not None:
        limit = int(args.source_limit)
        if limit <= 0:
            raise ValueError("--source-limit must be positive when provided")
        points_a = points_a[:limit]
        preprocessing.append(f"source_limit_{limit}")
    return _coordinate_matrix_3d(points_a), _coordinate_matrix_3d(points_b), preprocessing


def _read_author_oracle(path: Path) -> dict[str, int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    trace = payload.get("author_lb_trace") or payload.get("author_lb_trace_v2")
    if not isinstance(trace, dict):
        raise ValueError("author oracle must contain author_lb_trace or author_lb_trace_v2")
    batch = trace.get("batch_0") if isinstance(trace.get("batch_0"), dict) else {}
    raw_rows = int(trace["raw_offload_rows_before_sort_reduce"])
    return {
        "active_in_queue_size": int(trace["active_in_queue_size"]),
        "raw_offload_rows_before_sort_reduce": raw_rows,
        "raw_offload_rows_author_width_bytes": int(
            trace.get("raw_offload_rows_author_width_bytes", raw_rows * 2 * 4)
        ),
        "raw_offload_row_hash": (
            None if "raw_offload_row_hash" not in batch else int(batch["raw_offload_row_hash"])
        ),
        "raw_offload_row_sample_point_ids": list(batch.get("raw_offload_row_sample_point_ids", [])),
        "raw_offload_row_sample_cell_ids": list(batch.get("raw_offload_row_sample_cell_ids", [])),
    }


def bridge_status_summary_from_native_frontier(
    *,
    source_columns: dict[str, object],
    native_frontier: dict[str, object],
    max_inline_points: int,
    author_oracle: dict[str, int],
) -> dict[str, object]:
    """Apply the generic active-query bridge to a native frontier result."""

    query_ids = np.asarray(source_columns["ids"], dtype=np.int64)
    nearest_state = native_frontier.get("nearest_state", {})
    best_distances = np.asarray(
        nearest_state.get("current_best_distances", np.full(query_ids.size, np.inf)),
        dtype=np.float64,
    )
    best_items = np.asarray(
        nearest_state.get("current_best_item_ids", np.full(query_ids.size, -1)),
        dtype=np.int64,
    )
    if best_distances.shape != query_ids.shape:
        raise ValueError("nearest_state current_best_distances must match source ids")
    if best_items.shape != query_ids.shape:
        raise ValueError("nearest_state current_best_item_ids must match source ids")

    status = rt.active_query_status_from_frontier_row_table_numpy_columns(
        query_row_ids=np.arange(query_ids.size, dtype=np.int64),
        active_queue_indices=np.arange(query_ids.size, dtype=np.int64),
        source_ids=query_ids,
        current_best_sq=best_distances * best_distances,
        current_best_item_ids=best_items,
        frontier_row_table=native_frontier["row_table"],
        heavy_threshold=int(max_inline_points),
        return_metadata=True,
    )
    telemetry = status["telemetry"]
    trace_summary = rt.active_query_status_trace_summary_numpy_columns(
        status["offload_rows"],
        active_queue_indices=np.arange(query_ids.size, dtype=np.int64),
        hash_columns=("source_ids", "cell_ids"),
        sample_columns=("source_ids", "cell_ids", "work_counts"),
        return_metadata=True,
    )
    offload_rows = int(telemetry["offload_row_count"])
    author_rows = int(author_oracle["raw_offload_rows_before_sort_reduce"])
    author_width_bytes = int(author_oracle["raw_offload_rows_author_width_bytes"])
    author_active = int(author_oracle["active_in_queue_size"])
    rtdl_width_bytes = int(offload_rows * 2 * 4)
    author_hash = author_oracle.get("raw_offload_row_hash")
    hash_comparable = author_hash is not None
    sample_comparable = bool(
        author_oracle.get("raw_offload_row_sample_point_ids")
        and author_oracle.get("raw_offload_row_sample_cell_ids")
    )
    return {
        "bridge_contract": status["metadata"]["contract"],
        "reference_contract": status["metadata"]["reference_contract"],
        "active_query_count": int(telemetry["active_query_count"]),
        "candidate_row_count": int(telemetry["candidate_row_count"]),
        "offload_row_count": offload_rows,
        "completed_row_count": int(telemetry["completed_row_count"]),
        "miss_row_count": int(telemetry["miss_row_count"]),
        "aborted_row_count": int(telemetry["aborted_row_count"]),
        "attempted_output_row_count": int(telemetry["attempted_output_row_count"]),
        "emitted_output_row_count": int(telemetry["emitted_output_row_count"]),
        "overflowed": bool(telemetry["overflowed"]),
        "trace_summary": trace_summary,
        "comparison_to_author": {
            "author_active_in_queue_size": author_active,
            "rtdl_active_query_count": int(telemetry["active_query_count"]),
            "active_query_count_parity": bool(int(telemetry["active_query_count"]) == author_active),
            "author_raw_offload_rows_before_sort_reduce": author_rows,
            "rtdl_bridge_offload_rows": offload_rows,
            "row_delta_author_minus_rtdl_bridge": int(author_rows - offload_rows),
            "row_ratio_rtdl_bridge_div_author": (offload_rows / author_rows) if author_rows else None,
            "row_count_parity": bool(offload_rows == author_rows),
            "author_raw_offload_rows_author_width_bytes": author_width_bytes,
            "rtdl_bridge_author_width_bytes": rtdl_width_bytes,
            "author_width_byte_delta_author_minus_rtdl": int(author_width_bytes - rtdl_width_bytes),
            "author_width_byte_parity": bool(rtdl_width_bytes == author_width_bytes),
            "author_raw_offload_row_hash": author_hash,
            "rtdl_raw_offload_row_hash": trace_summary["raw_offload_row_hash"],
            "hash_comparable_to_author": bool(hash_comparable),
            "hash_parity": None
            if not hash_comparable
            else bool(int(author_hash) == int(trace_summary["raw_offload_row_hash"])),
            "author_raw_offload_row_sample_point_ids": author_oracle.get(
                "raw_offload_row_sample_point_ids", []
            ),
            "author_raw_offload_row_sample_cell_ids": author_oracle.get(
                "raw_offload_row_sample_cell_ids", []
            ),
            "rtdl_sample_source_ids": trace_summary["samples"].get("source_ids", []),
            "rtdl_sample_cell_ids": trace_summary["samples"].get("cell_ids", []),
            "sample_comparable_to_author": bool(sample_comparable),
        },
        "claim_boundary": {
            "explicit_lb_support_claimed": False,
            "row_count_parity_claimed": False,
            "hash_sample_parity_claimed": False,
            "same_denominator_memory_claimed": False,
            "performance_claimed": False,
            "author_rt_core_algorithm_parity_claimed": False,
        },
    }


def build_summary(args: argparse.Namespace) -> dict[str, object]:
    total_start = time.perf_counter()
    load_start = time.perf_counter()
    points_a, points_b, preprocessing = _load_preprocessed_points(args)
    load_sec = time.perf_counter() - load_start
    source_columns = _columns_3d(points_a)
    target_columns = _columns_3d(points_b)
    grid_shape = _parse_grid_shape(args.grid_shape)
    radius = _full_cover_radius(points_a, points_b) if args.radius is None else float(args.radius)
    author_oracle = _read_author_oracle(Path(args.author_oracle))

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
    seed = None
    current_best_distances = None
    current_best_item_ids = None
    seed_sec = 0.0
    if args.initial_state == "local-grid-cell":
        seed_start = time.perf_counter()
        seed = rt.seed_nearest_witness_from_local_grid_cell_numpy_columns(
            source_columns,
            target_columns,
            grid["cell_columns"],
            coordinate_fields=("x", "y", "z"),
            executor=args.local_grid_seed_executor,
            return_metadata=True,
        )
        seed_sec = time.perf_counter() - seed_start
        current_best_distances = seed["columns"]["nearest_distances"]
        current_best_item_ids = seed["columns"]["nearest_item_ids"]
    elif args.initial_state != "none":
        raise ValueError("--initial-state must be none or local-grid-cell")

    frontier_start = time.perf_counter()
    frontier = rt.cell_mbr_nearest_frontier_native_3d_optix_columns(
        source_columns,
        grid["cell_columns"],
        target_point_columns=target_columns if bool(args.inline_nearest) else None,
        radius=radius,
        current_best_distances=current_best_distances,
        current_best_item_ids=current_best_item_ids,
        max_inline_points=int(args.max_inline_points),
        row_capacity=int(args.frontier_row_capacity),
        emit_pruned_rows=bool(args.emit_pruned_rows),
        sort_rows=False,
        inline_nearest=bool(args.inline_nearest),
        collect_inline_stats=bool(args.collect_inline_stats),
        global_bound_early_break=bool(args.global_bound_early_break),
        frontier_status_probe_mode=args.frontier_status_probe_mode,
        collect_native_phase_timings=bool(args.collect_frontier_native_phase_timings),
        allow_overflow_telemetry=False,
        return_split_frontiers=False,
        return_metadata=True,
    )
    frontier_sec = time.perf_counter() - frontier_start
    bridge_start = time.perf_counter()
    bridge = bridge_status_summary_from_native_frontier(
        source_columns=source_columns,
        native_frontier=frontier,
        max_inline_points=int(args.max_inline_points),
        author_oracle=author_oracle,
    )
    bridge_sec = time.perf_counter() - bridge_start
    metadata = frontier["metadata"]

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5381.active_query_frontier_bridge_probe.v1",
        "paper_app": "x-hd-paper",
        "purpose": (
            "App-owned probe that feeds generic native cell-MBR frontier rows "
            "through the generic active-query status-machine frontier bridge, "
            "then compares bridge offload rows against the Goal5374 author oracle."
        ),
        "input1": str(args.input1),
        "input2": str(args.input2),
        "input_type": args.input_type,
        "input_n_dims": int(args.n_dims),
        "execution_n_dims": 3,
        "point_count_a": int(points_a.shape[0]),
        "point_count_b": int(points_b.shape[0]),
        "source_limit": None if args.source_limit is None else int(args.source_limit),
        "source_limit_applied": bool(args.source_limit is not None),
        "preprocessing": preprocessing,
        "grid_shape": grid_shape,
        "grid_cell_builder": args.grid_cell_builder,
        "grid_cell_point_order": args.grid_cell_point_order,
        "initial_state": args.initial_state,
        "local_grid_seed_executor": args.local_grid_seed_executor,
        "seed_metadata": None if seed is None else seed.get("metadata"),
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
            "native_symbol": metadata.get("native_generic_symbol"),
            "frontier_status_probe_contract": metadata.get("frontier_status_probe_contract"),
            "frontier_status_probe_mode_code": metadata.get("frontier_status_probe_mode_code"),
        },
        "active_query_bridge": bridge,
        "timings_sec": {
            "load_inputs": load_sec,
            "grid_cell_mbrs": grid_sec,
            "initial_seed": seed_sec,
            "frontier_rows": frontier_sec,
            "active_query_bridge": bridge_sec,
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
            "source_limited_smoke_claimed_as_author_oracle_parity": False,
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
    parser.add_argument(
        "--source-limit",
        type=int,
        default=None,
        help=(
            "Optional source-side row limit for bounded smoke runs. "
            "A source-limited run cannot establish full author-oracle row parity."
        ),
    )
    parser.add_argument("--grid-shape", default="96,60,72")
    parser.add_argument("--grid-cell-builder", default="native_cuda", choices=("native_cuda", "numpy"))
    parser.add_argument("--grid-cell-point-order", default="point-id", choices=("point-id", "input-stable"))
    parser.add_argument("--initial-state", default="none", choices=("none", "local-grid-cell"))
    parser.add_argument("--local-grid-seed-executor", default="auto", choices=("auto", "numpy", "numba", "native_cuda"))
    parser.add_argument("--radius", type=float, default=None)
    parser.add_argument("--max-inline-points", type=int, required=True)
    parser.add_argument("--frontier-row-capacity", type=int, required=True)
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
    parser.add_argument("--author-oracle", type=Path, default=DEFAULT_ORACLE)
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
