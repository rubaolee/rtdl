from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Mapping

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


APP_ROOT = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_ROOT / "results"
DEFAULT_INPUT1 = APP_ROOT / "data" / "external" / "stanford" / "dragon_recon" / "dragon_vrip.ply"
DEFAULT_INPUT2 = APP_ROOT / "data" / "external" / "stanford" / "asian_dragon.ply"
DEFAULT_AUTHOR_TRACE_V2 = RESULTS / "xhd_goal5387_author_trace_v2_execution.json"
DEFAULT_GOAL5365_GATE = RESULTS / "xhd_goal5365_rtdl_lb_counterpart_gate.json"
DEFAULT_OUTPUT = RESULTS / "xhd_goal5406_real_full_cover_surface_stream_gate_pod.json"
OFFLOAD_FRONTIER_KIND_CODE = 2


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_author_trace_v2(path: Path) -> dict[str, Any]:
    payload = _read_json(path)
    trace = payload.get("author_lb_trace_v2")
    if not isinstance(trace, dict):
        raise ValueError("author trace artifact must contain author_lb_trace_v2")
    batch = trace.get("batch_0")
    if not isinstance(batch, dict):
        raise ValueError("author trace artifact must contain author_lb_trace_v2.batch_0")
    return {
        "active_in_queue_size": int(trace["active_in_queue_size"]),
        "raw_offload_rows_before_sort_reduce": int(trace["raw_offload_rows_before_sort_reduce"]),
        "status_count_offloading_append": int(trace["status_count_offloading_append"]),
        "feedback_update_count": int(trace.get("load_balance_feedback_update_count", 0)),
        "batch_0": {
            "raw_offload_row_hash": int(batch["raw_offload_row_hash"]),
            "raw_offload_row_sample_point_ids": [int(value) for value in batch.get("raw_offload_row_sample_point_ids", [])],
            "raw_offload_row_sample_cell_ids": [int(value) for value in batch.get("raw_offload_row_sample_cell_ids", [])],
        },
    }


def _goal5365_full_cover_rows(path: Path) -> int:
    payload = _read_json(path)
    rows = payload["rtdl_counterparts"]["lb256_heavy_offload"]["heavy_offload_peak_rows"]
    return int(rows)


def offload_rows_from_frontier_row_table(row_table: Mapping[str, object]) -> dict[str, np.ndarray]:
    columns = row_table.get("columns", row_table)
    if not isinstance(columns, Mapping):
        raise ValueError("frontier row table columns must be a mapping")
    kind_codes = np.asarray(columns["frontier_kind_codes"], dtype=np.int64)
    mask = kind_codes == OFFLOAD_FRONTIER_KIND_CODE
    return {
        "source_ids": np.asarray(columns["query_point_ids"], dtype=np.int64)[mask],
        "cell_ids": np.asarray(columns["cell_ids"], dtype=np.int64)[mask],
        "query_row_ids": np.asarray(columns["query_row_ids"], dtype=np.int64)[mask],
    }


def summarize_full_cover_frontier(
    *,
    frontier: Mapping[str, object],
    active_count: int,
) -> dict[str, Any]:
    offload_rows = offload_rows_from_frontier_row_table(frontier["row_table"])
    return rt.active_query_status_trace_summary_numpy_columns(
        offload_rows,
        active_queue_indices=np.arange(int(active_count), dtype=np.int64),
        hash_columns=("source_ids", "cell_ids"),
        sample_columns=("source_ids", "cell_ids", "query_row_ids"),
        return_metadata=True,
    )


def build_summary(args: argparse.Namespace) -> dict[str, Any]:
    total_start = time.perf_counter()
    load_start = time.perf_counter()
    points_a, points_b, preprocessing = _load_preprocessed_points(args)
    load_sec = time.perf_counter() - load_start

    source_columns = _columns_3d(points_a)
    target_columns = _columns_3d(points_b)
    grid_shape = _parse_grid_shape(args.grid_shape)
    radius = _full_cover_radius(points_a, points_b) if args.radius is None else float(args.radius)
    author_trace = _read_author_trace_v2(Path(args.author_trace_v2))
    goal5365_rows = _goal5365_full_cover_rows(Path(args.goal5365_gate))

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
        target_point_columns=target_columns,
        radius=radius,
        current_best_distances=None,
        current_best_item_ids=None,
        max_inline_points=int(args.max_inline_points),
        row_capacity=None if args.frontier_row_capacity is None else int(args.frontier_row_capacity),
        emit_pruned_rows=False,
        sort_rows=bool(args.sort_rows),
        inline_nearest=True,
        collect_inline_stats=False,
        global_bound_early_break=False,
        frontier_status_probe_mode="default",
        collect_native_phase_timings=bool(args.collect_frontier_native_phase_timings),
        allow_overflow_telemetry=False,
        return_split_frontiers=False,
        return_metadata=True,
    )
    frontier_sec = time.perf_counter() - frontier_start

    summary_start = time.perf_counter()
    trace_summary = summarize_full_cover_frontier(
        frontier=frontier,
        active_count=int(points_a.shape[0]),
    )
    summary_sec = time.perf_counter() - summary_start
    total_sec = time.perf_counter() - total_start

    row_count = int(trace_summary["row_count"])
    author_rows = int(author_trace["raw_offload_rows_before_sort_reduce"])
    author_hash = int(author_trace["batch_0"]["raw_offload_row_hash"])
    full_cover_count_matched = row_count == goal5365_rows
    row_count_parity = row_count == author_rows
    hash_parity = int(trace_summary["raw_offload_row_hash"]) == author_hash
    active_parity = int(points_a.shape[0]) == int(author_trace["active_in_queue_size"])
    feedback_parity = None
    matched = bool(full_cover_count_matched and active_parity)
    status = (
        "real_full_cover_surface_generated__author_delta_remaining"
        if matched and not row_count_parity
        else (
            "real_full_cover_surface_matches_author_target"
            if matched and row_count_parity and hash_parity
            else "real_full_cover_surface_gate_failed"
        )
    )

    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5406.real_full_cover_surface_stream_gate.v1",
        "goal": "Goal5406",
        "paper_app": "x-hd-paper",
        "purpose": (
            "Generate the real full-public RTDL full-cover cell-MBR offload row "
            "surface and summarize row count/hash/sample before any claim about "
            "explicit -lb parity."
        ),
        "status": status,
        "matched": matched,
        "input1": str(args.input1),
        "input2": str(args.input2),
        "input_type": args.input_type,
        "n_dims": int(args.n_dims),
        "point_count_a": int(points_a.shape[0]),
        "point_count_b": int(points_b.shape[0]),
        "preprocessing": preprocessing,
        "grid_shape": list(grid_shape),
        "grid_cell_builder": args.grid_cell_builder,
        "grid_cell_point_order": args.grid_cell_point_order,
        "radius": radius,
        "max_inline_points": int(args.max_inline_points),
        "sort_rows": bool(args.sort_rows),
        "frontier_row_capacity_requested": None if args.frontier_row_capacity is None else int(args.frontier_row_capacity),
        "frontier_metadata": frontier.get("metadata", {}),
        "trace_summary": trace_summary,
        "author_trace_v2": author_trace,
        "comparison": {
            "active_query_count_author": int(author_trace["active_in_queue_size"]),
            "active_query_count_rtdl": int(points_a.shape[0]),
            "active_query_count_parity": active_parity,
            "goal5365_full_cover_rows": goal5365_rows,
            "rtdl_full_cover_rows": row_count,
            "full_cover_count_matched_goal5365": full_cover_count_matched,
            "author_raw_offload_rows": author_rows,
            "row_delta_author_minus_rtdl_full_cover": int(author_rows - row_count),
            "row_ratio_rtdl_full_cover_div_author": row_count / author_rows if author_rows else None,
            "row_count_parity_with_author": row_count_parity,
            "author_raw_offload_row_hash": author_hash,
            "rtdl_full_cover_row_hash": int(trace_summary["raw_offload_row_hash"]),
            "hash_parity_with_author": hash_parity,
            "author_sample_point_ids": list(author_trace["batch_0"]["raw_offload_row_sample_point_ids"]),
            "author_sample_cell_ids": list(author_trace["batch_0"]["raw_offload_row_sample_cell_ids"]),
            "rtdl_sample_source_ids": list(trace_summary["samples"].get("source_ids", [])),
            "rtdl_sample_cell_ids": list(trace_summary["samples"].get("cell_ids", [])),
            "status_count_offloading_author": int(author_trace["status_count_offloading_append"]),
            "status_count_offloading_rtdl": int(trace_summary["status_count_offloading"]),
            "status_count_offloading_parity": int(trace_summary["status_count_offloading"]) == int(author_trace["status_count_offloading_append"]),
            "feedback_update_count_author": int(author_trace["feedback_update_count"]),
            "feedback_update_count_rtdl": None,
            "feedback_update_count_parity": feedback_parity,
        },
        "timings_sec": {
            "load_inputs": load_sec,
            "grid_cell_mbrs": grid_sec,
            "frontier_rows": frontier_sec,
            "trace_summary": summary_sec,
            "total": total_sec,
        },
        "decision": {
            "real_full_cover_surface_generated": matched,
            "direct_full_goal5387_stream_parity_passed": bool(matched and row_count_parity and hash_parity),
            "explicit_lb_support_authorized": bool(matched and row_count_parity and hash_parity and feedback_parity is True),
            "remaining_delta_rows_if_full_cover_only": int(author_rows - row_count) if matched and not row_count_parity else 0,
            "next_goal_if_delta_remaining": "Goal5407_isolate_real_full_cover_to_author_delta_or_fail_close_explicit_lb",
        },
        "claim_boundary": {
            "real_full_cover_surface_count_claimed": matched,
            "explicit_lb_support_claimed": False,
            "row_count_parity_with_author_claimed": bool(row_count_parity),
            "hash_sample_parity_with_author_claimed": bool(hash_parity),
            "feedback_parity_claimed": False,
            "figure7_reproduction_claimed": False,
            "figure11_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input1", default=str(DEFAULT_INPUT1))
    parser.add_argument("--input2", default=str(DEFAULT_INPUT2))
    parser.add_argument("--input-type", default="ply")
    parser.add_argument("--n-dims", type=int, default=3)
    parser.add_argument("--grid-shape", default="96,60,72")
    parser.add_argument("--grid-cell-builder", choices=("native_cuda", "numpy"), default="native_cuda")
    parser.add_argument("--grid-cell-point-order", default="point-id")
    parser.add_argument("--max-inline-points", type=int, default=256)
    parser.add_argument("--frontier-row-capacity", type=int, default=None)
    parser.add_argument("--radius", type=float, default=None)
    parser.add_argument("--sort-rows", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--collect-frontier-native-phase-timings", action="store_true")
    parser.add_argument("--source-limit", type=int, default=None)
    parser.add_argument("--normalize-each-input-to-author-unit-box", action="store_true")
    parser.add_argument("--author-float32-normalization", action="store_true")
    parser.add_argument("--translate-each-input-to-min-bound", action="store_true", default=True)
    parser.add_argument("--lift-2d-to-3d-zero-z", action="store_true")
    parser.add_argument("--author-trace-v2", default=str(DEFAULT_AUTHOR_TRACE_V2))
    parser.add_argument("--goal5365-gate", default=str(DEFAULT_GOAL5365_GATE))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_summary(args)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"output": str(output), "status": payload["status"], "matched": payload["matched"]}, indent=2))
    return 0 if payload["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
