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

from run_xhd_active_query_frontier_bridge_probe import (  # noqa: E402
    _columns_3d,
    _full_cover_radius,
    _load_preprocessed_points,
    _parse_grid_shape,
)


RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
DEFAULT_AUTHOR_TRACE_V2 = RESULTS / "xhd_goal5387_author_trace_v2_execution.json"


def _read_author_trace_v2(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    trace = payload.get("author_lb_trace_v2")
    if not isinstance(trace, dict):
        raise ValueError("author trace artifact must contain author_lb_trace_v2")
    batch = trace.get("batch_0")
    if not isinstance(batch, dict):
        raise ValueError("author trace v2 artifact must contain batch_0")
    raw_rows = int(trace["raw_offload_rows_before_sort_reduce"])
    return {
        "schema": trace.get("schema"),
        "active_in_queue_size": int(trace["active_in_queue_size"]),
        "raw_offload_rows_before_sort_reduce": raw_rows,
        "status_count_offloading_append": int(trace["status_count_offloading_append"]),
        "status_count_init": int(trace.get("status_count_init", trace["active_in_queue_size"])),
        "status_count_aborted": int(trace.get("status_count_aborted", 0)),
        "status_count_miss": int(trace.get("status_count_miss", 0)),
        "status_count_completed": int(trace.get("status_count_completed", 0)),
        "feedback_update_count": int(trace.get("load_balance_feedback_update_count", 0)),
        "batch_0": {
            "raw_offload_row_hash": int(batch["raw_offload_row_hash"]),
            "raw_offload_row_sample_point_ids": [int(value) for value in batch.get("raw_offload_row_sample_point_ids", [])],
            "raw_offload_row_sample_cell_ids": [int(value) for value in batch.get("raw_offload_row_sample_cell_ids", [])],
            "cmin2_initial_hash": int(batch["cmin2_initial_hash"]),
            "cmin2_after_ray_hash": int(batch["cmin2_after_ray_hash"]),
            "cmin2_after_load_balance_hash": int(batch["cmin2_after_load_balance_hash"]),
            "load_balance_feedback_update_count": int(batch.get("load_balance_feedback_update_count", 0)),
            "status_count_offloading": int(batch.get("status_count_offloading", raw_rows)),
        },
    }


def _cell_mbr_min_max(cell_columns: dict[str, object]) -> tuple[np.ndarray, np.ndarray]:
    mins = np.column_stack(
        [
            np.asarray(cell_columns["min_x"], dtype=np.float64),
            np.asarray(cell_columns["min_y"], dtype=np.float64),
            np.asarray(cell_columns["min_z"], dtype=np.float64),
        ]
    )
    maxs = np.column_stack(
        [
            np.asarray(cell_columns["max_x"], dtype=np.float64),
            np.asarray(cell_columns["max_y"], dtype=np.float64),
            np.asarray(cell_columns["max_z"], dtype=np.float64),
        ]
    )
    return np.ascontiguousarray(mins), np.ascontiguousarray(maxs)


def _status_code_counts(status_codes: np.ndarray) -> dict[str, int]:
    if status_codes.size == 0:
        return {}
    values, counts = np.unique(status_codes.astype(np.int64), return_counts=True)
    return {str(int(value)): int(count) for value, count in zip(values, counts)}


def summarize_v7_status_stream(
    *,
    native_status: dict[str, object],
    active_query_count: int,
    author_trace_v2: dict[str, object],
) -> dict[str, object]:
    columns = native_status["columns"]
    status_codes = np.asarray(columns["status_codes"], dtype=np.int64)
    offload_mask = status_codes == 2
    offload_rows = {
        "source_ids": np.asarray(columns["source_ids"], dtype=np.int64)[offload_mask],
        "cell_ids": np.asarray(columns["cell_ids"], dtype=np.int64)[offload_mask],
        "active_queue_indices": np.asarray(columns["active_queue_indices"], dtype=np.int64)[offload_mask],
        "query_row_ids": np.asarray(columns["query_row_ids"], dtype=np.int64)[offload_mask],
    }
    trace_summary = rt.active_query_status_trace_summary_numpy_columns(
        offload_rows,
        active_queue_indices=np.arange(int(active_query_count), dtype=np.int64),
        hash_columns=("source_ids", "cell_ids"),
        sample_columns=("source_ids", "cell_ids", "active_queue_indices", "query_row_ids"),
        return_metadata=True,
    )
    author_batch = author_trace_v2["batch_0"]
    author_rows = int(author_trace_v2["raw_offload_rows_before_sort_reduce"])
    author_hash = int(author_batch["raw_offload_row_hash"])
    row_count = int(trace_summary["row_count"])
    status_count_offloading = int(trace_summary["status_count_offloading"])
    best_before = np.asarray(columns["current_best_before_sq"], dtype=np.float64)
    best_after = np.asarray(columns["current_best_after_sq"], dtype=np.float64)
    comparison = {
        "author_active_in_queue_size": int(author_trace_v2["active_in_queue_size"]),
        "rtdl_active_query_count": int(active_query_count),
        "active_query_count_parity": bool(int(active_query_count) == int(author_trace_v2["active_in_queue_size"])),
        "author_raw_offload_rows_before_sort_reduce": author_rows,
        "rtdl_v7_offload_rows": row_count,
        "row_delta_author_minus_rtdl_v7": int(author_rows - row_count),
        "row_ratio_rtdl_v7_div_author": (row_count / author_rows) if author_rows else None,
        "row_count_parity": bool(row_count == author_rows),
        "author_status_count_offloading": int(author_trace_v2["status_count_offloading_append"]),
        "rtdl_status_count_offloading": status_count_offloading,
        "status_count_offloading_parity": bool(status_count_offloading == int(author_trace_v2["status_count_offloading_append"])),
        "author_raw_offload_row_hash": author_hash,
        "rtdl_raw_offload_row_hash": int(trace_summary["raw_offload_row_hash"]),
        "hash_parity": bool(int(trace_summary["raw_offload_row_hash"]) == author_hash),
        "author_raw_offload_row_sample_point_ids": list(author_batch.get("raw_offload_row_sample_point_ids", [])),
        "author_raw_offload_row_sample_cell_ids": list(author_batch.get("raw_offload_row_sample_cell_ids", [])),
        "rtdl_sample_source_ids": trace_summary["samples"].get("source_ids", []),
        "rtdl_sample_cell_ids": trace_summary["samples"].get("cell_ids", []),
        "feedback_update_count_author": int(author_trace_v2["feedback_update_count"]),
        "feedback_update_count_rtdl_v7": None,
        "feedback_update_count_parity": None,
    }
    return {
        "native_result_metadata": {
            key: value
            for key, value in native_status.items()
            if key != "columns"
        },
        "status_code_counts": _status_code_counts(status_codes),
        "transition_phase_code_counts": _status_code_counts(
            np.asarray(columns["transition_phase_codes"], dtype=np.int64)
        ),
        "current_best_before_finite_count": int(np.count_nonzero(np.isfinite(best_before))),
        "current_best_after_finite_count": int(np.count_nonzero(np.isfinite(best_after))),
        "trace_summary": trace_summary,
        "comparison_to_author": comparison,
        "claim_boundary": {
            "explicit_lb_support_claimed": False,
            "row_count_parity_claimed": False,
            "hash_sample_parity_claimed": False,
            "same_denominator_memory_claimed": False,
            "performance_claimed": False,
            "author_rt_core_algorithm_parity_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
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
    author_trace_v2 = _read_author_trace_v2(Path(args.author_trace_v2))

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
        current_best_distances = seed["columns"]["nearest_distances"]
        current_best_item_ids = seed["columns"]["nearest_item_ids"]
        seed_sec = time.perf_counter() - seed_start
    elif args.initial_state == "none":
        current_best_distances = np.full(points_a.shape[0], np.inf, dtype=np.float64)
        current_best_item_ids = np.full(points_a.shape[0], -1, dtype=np.int64)
    else:
        raise ValueError("--initial-state must be none or local-grid-cell")

    cell_columns = grid["cell_columns"]
    cell_mbr_min, cell_mbr_max = _cell_mbr_min_max(cell_columns)
    target_coords = None
    target_ids = None
    point_row_indices = None
    if bool(args.inline_nearest):
        target_coords = np.ascontiguousarray(target_columns["coordinate_matrix"], dtype=np.float64)
        target_ids = np.ascontiguousarray(target_columns["ids"], dtype=np.int64)
        point_row_indices = np.asarray(cell_columns["point_row_indices"], dtype=np.uint64)

    v7_start = time.perf_counter()
    native_status = rt.collect_active_query_status_stream_3d_optix(
        query_coords=np.ascontiguousarray(source_columns["coordinate_matrix"], dtype=np.float64),
        query_point_ids=np.ascontiguousarray(source_columns["ids"], dtype=np.int64),
        cell_ids=np.asarray(cell_columns["cell_ids"], dtype=np.int64),
        point_begin_offsets=np.asarray(cell_columns["point_begin_offsets"], dtype=np.uint64),
        point_counts=np.asarray(cell_columns["point_counts"], dtype=np.uint64),
        cell_mbr_min=cell_mbr_min,
        cell_mbr_max=cell_mbr_max,
        radius=radius,
        current_best_distances=current_best_distances,
        current_best_item_ids=current_best_item_ids,
        max_inline_points=int(args.max_inline_points),
        row_capacity=int(args.row_capacity),
        emit_pruned_rows=bool(args.emit_pruned_rows),
        inline_nearest=bool(args.inline_nearest),
        frontier_status_probe_mode=args.frontier_status_probe_mode,
        target_coords=target_coords,
        target_point_ids=target_ids,
        point_row_indices=point_row_indices,
    )
    v7_sec = time.perf_counter() - v7_start
    status_summary = summarize_v7_status_stream(
        native_status=native_status,
        active_query_count=int(points_a.shape[0]),
        author_trace_v2=author_trace_v2,
    )
    comparison = status_summary["comparison_to_author"]
    matched = bool(
        comparison["active_query_count_parity"]
        and comparison["row_count_parity"]
        and comparison["status_count_offloading_parity"]
        and comparison["hash_parity"]
    )
    if matched:
        status = "native_v7_status_stream_author_trace_parity_passed"
    else:
        status = "native_v7_status_stream_denominator_or_hash_mismatch__lb_remains_fail_closed"

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5398.native_v7_status_stream_parity_gate.v1",
        "goal": "Goal5398",
        "status": status,
        "matched": matched,
        "purpose": "Compare generic native v7 active-query status-stream rows against the Goal5387 author trace v2 oracle.",
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
        "grid_shape": list(grid_shape),
        "grid_cell_builder": args.grid_cell_builder,
        "grid_cell_point_order": args.grid_cell_point_order,
        "initial_state": args.initial_state,
        "local_grid_seed_executor": args.local_grid_seed_executor,
        "seed_metadata": None if seed is None else seed.get("metadata"),
        "radius": radius,
        "max_inline_points": int(args.max_inline_points),
        "row_capacity": int(args.row_capacity),
        "emit_pruned_rows": bool(args.emit_pruned_rows),
        "inline_nearest": bool(args.inline_nearest),
        "frontier_status_probe_mode": args.frontier_status_probe_mode,
        "author_trace_v2": author_trace_v2,
        "native_v7_status_stream": status_summary,
        "timings_sec": {
            "load_inputs": load_sec,
            "grid_cell_mbrs": grid_sec,
            "initial_seed": seed_sec,
            "native_v7_status_stream": v7_sec,
            "total": time.perf_counter() - total_start,
        },
        "decision": {
            "explicit_lb_support_remains_unsupported": not matched,
            "row_count_parity": bool(comparison["row_count_parity"]),
            "hash_parity": bool(comparison["hash_parity"]),
            "next_gate": (
                "continue_explicit_lb_status_stream"
                if matched
                else "native_v7_semantic_gap_or_status_machine_redesign"
            ),
        },
        "claim_boundary": {
            "full_trace_summary_gate_claimed": True,
            "explicit_lb_support_claimed": False,
            "row_count_parity_claimed": False,
            "hash_sample_parity_claimed": False,
            "same_denominator_memory_claimed": False,
            "performance_claimed": False,
            "author_rt_core_algorithm_parity_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
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
    parser.add_argument("--source-limit", type=int, default=None)
    parser.add_argument("--grid-shape", default="96,60,72")
    parser.add_argument("--grid-cell-builder", default="native_cuda", choices=("native_cuda", "numpy"))
    parser.add_argument("--grid-cell-point-order", default="input-stable", choices=("point-id", "input-stable"))
    parser.add_argument("--initial-state", default="local-grid-cell", choices=("none", "local-grid-cell"))
    parser.add_argument("--local-grid-seed-executor", default="native_cuda", choices=("auto", "numpy", "numba", "native_cuda"))
    parser.add_argument("--radius", type=float, default=None)
    parser.add_argument("--max-inline-points", type=int, default=256)
    parser.add_argument("--row-capacity", type=int, required=True)
    parser.add_argument("--emit-pruned-rows", action="store_true")
    parser.add_argument("--inline-nearest", action="store_true")
    parser.add_argument(
        "--frontier-status-probe-mode",
        default="active-initial-best-prune",
        choices=("default", "heavy-before-inline-prune", "active-initial-best-prune"),
    )
    parser.add_argument("--author-trace-v2", type=Path, default=DEFAULT_AUTHOR_TRACE_V2)
    parser.add_argument("--summary", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = build_summary(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["status"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
