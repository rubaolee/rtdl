from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

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
from run_xhd_goal5406_real_full_cover_surface_stream_gate import (  # noqa: E402
    DEFAULT_AUTHOR_TRACE_V2,
    DEFAULT_INPUT1,
    DEFAULT_INPUT2,
)


APP_ROOT = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_ROOT / "results"
DEFAULT_OUTPUT = RESULTS / "xhd_goal5411_bounded_statused_deferral_sample_row_gate_pod.json"


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return _json_safe(value.tolist())
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if np.isposinf(value):
            return "inf"
        if np.isneginf(value):
            return "-inf"
        if np.isnan(value):
            return "nan"
        return value
    return value


def _read_author_samples(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    trace = payload.get("author_lb_trace_v2")
    if not isinstance(trace, dict):
        raise ValueError("author trace v2 artifact must contain author_lb_trace_v2")
    batch = trace.get("batch_0")
    if not isinstance(batch, dict):
        raise ValueError("author trace v2 artifact must contain author_lb_trace_v2.batch_0")
    return {
        "active_in_queue_size": int(trace["active_in_queue_size"]),
        "raw_offload_rows_before_sort_reduce": int(trace["raw_offload_rows_before_sort_reduce"]),
        "raw_offload_row_hash": int(batch["raw_offload_row_hash"]),
        "raw_offload_row_sample_point_ids": [int(value) for value in batch["raw_offload_row_sample_point_ids"]],
        "raw_offload_row_sample_cell_ids": [int(value) for value in batch["raw_offload_row_sample_cell_ids"]],
        "feedback_update_count": int(trace.get("load_balance_feedback_update_count", 0)),
        "cmin2_after_ray_hash": int(batch.get("cmin2_after_ray_hash", 0)),
        "cmin2_after_load_balance_hash": int(batch.get("cmin2_after_load_balance_hash", 0)),
    }


def sample_pair_membership(
    *,
    source_ids: np.ndarray,
    cell_ids: np.ndarray,
    sample_source_ids: list[int],
    sample_cell_ids: list[int],
    max_cells_to_record: int = 64,
) -> list[dict[str, Any]]:
    source_ids = np.asarray(source_ids, dtype=np.int64)
    cell_ids = np.asarray(cell_ids, dtype=np.int64)
    if source_ids.shape != cell_ids.shape:
        raise ValueError("source_ids and cell_ids must have matching shape")
    rows: list[dict[str, Any]] = []
    for source_id, cell_id in zip(sample_source_ids, sample_cell_ids):
        sid = int(source_id)
        cid = int(cell_id)
        source_cells = np.sort(cell_ids[source_ids == sid])
        rows.append(
            {
                "source_id": sid,
                "author_cell_id": cid,
                "statused_deferral_row_count_for_source": int(source_cells.size),
                "author_cell_present_in_statused_deferral_stream": bool(np.any(source_cells == cid)),
                "statused_deferral_cells_sample": [
                    int(value) for value in source_cells[: int(max_cells_to_record)].tolist()
                ],
            }
        )
    return rows


def _columns_for_source_subset(points_a: np.ndarray, sample_source_ids: list[int]) -> dict[str, object]:
    subset = np.ascontiguousarray(points_a[np.asarray(sample_source_ids, dtype=np.int64)])
    columns = _columns_3d(subset)
    columns["ids"] = np.asarray(sample_source_ids, dtype=np.int64)
    return columns


def build_summary(args: argparse.Namespace) -> dict[str, Any]:
    total_start = time.perf_counter()
    author = _read_author_samples(Path(args.author_trace_v2))
    sample_source_ids = list(author["raw_offload_row_sample_point_ids"])
    sample_cell_ids = list(author["raw_offload_row_sample_cell_ids"])
    load_args = argparse.Namespace(
        input1=str(args.input1),
        input2=str(args.input2),
        input_type=str(args.input_type),
        n_dims=int(args.n_dims),
        lift_2d_to_3d_zero_z=False,
        normalize_each_input_to_author_unit_box=False,
        author_float32_normalization=False,
        translate_each_input_to_min_bound=bool(args.translate_each_input_to_min_bound),
        source_limit=None,
    )
    load_start = time.perf_counter()
    points_a, points_b, preprocessing = _load_preprocessed_points(load_args)
    load_sec = time.perf_counter() - load_start
    source_columns = _columns_for_source_subset(points_a, sample_source_ids)
    target_columns = _columns_3d(points_b)
    grid_shape = _parse_grid_shape(str(args.grid_shape))
    radius = _full_cover_radius(points_a, points_b) if args.radius is None else float(args.radius)

    grid_start = time.perf_counter()
    grid = rt.point_grid_cell_mbrs_native_3d_cuda_columns(
        target_columns,
        coordinate_fields=("x", "y", "z"),
        grid_shape=grid_shape,
        cell_point_order=str(args.grid_cell_point_order),
        return_metadata=True,
    )
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

    bridge_start = time.perf_counter()
    query_count = len(sample_source_ids)
    nearest_state = frontier.get("nearest_state", {})
    best_distances = np.asarray(
        nearest_state.get("current_best_distances", np.full(query_count, np.inf)),
        dtype=np.float64,
    )
    best_items = np.asarray(
        nearest_state.get("current_best_item_ids", np.full(query_count, -1)),
        dtype=np.int64,
    )
    status = rt.active_query_status_from_frontier_row_table_numpy_columns(
        query_row_ids=np.arange(query_count, dtype=np.int64),
        active_queue_indices=np.arange(query_count, dtype=np.int64),
        source_ids=np.asarray(sample_source_ids, dtype=np.int64),
        current_best_sq=best_distances * best_distances,
        current_best_item_ids=best_items,
        frontier_row_table=frontier["row_table"],
        heavy_threshold=int(args.max_inline_points),
        radius_sq=radius * radius,
        global_bound_sq=None,
        return_metadata=True,
    )
    summary = rt.active_query_status_trace_summary_numpy_columns(
        status["offload_rows"],
        active_queue_indices=np.arange(query_count, dtype=np.int64),
        hash_columns=("source_ids", "cell_ids"),
        sample_columns=("source_ids", "cell_ids", "work_counts"),
        return_metadata=True,
    )
    offload_source_ids = np.asarray(status["offload_rows"]["source_ids"], dtype=np.int64)
    offload_cell_ids = np.asarray(status["offload_rows"]["cell_ids"], dtype=np.int64)
    memberships = sample_pair_membership(
        source_ids=offload_source_ids,
        cell_ids=offload_cell_ids,
        sample_source_ids=sample_source_ids,
        sample_cell_ids=sample_cell_ids,
    )
    bridge_sec = time.perf_counter() - bridge_start

    all_samples_present = all(
        bool(row["author_cell_present_in_statused_deferral_stream"]) for row in memberships
    )
    gate_status = (
        "bounded_xhd_statused_deferral_sample_row_gate_passed"
        if all_samples_present
        else "bounded_xhd_statused_deferral_sample_row_gate_failed__sample_rows_not_recovered"
    )
    return _json_safe(
        {
            "schema": "rtdl.paper_reproduction.xhd.goal5411.bounded_statused_deferral_sample_row_gate.v1",
            "goal": "Goal5411",
            "status": gate_status,
            "matched": True,
            "purpose": (
                "Use the generic statused large-cell deferral stream over the "
                "Goal5387 author sample source ids and test whether author "
                "sample source/cell rows are recovered without hard-coded rows."
            ),
            "input1": str(args.input1),
            "input2": str(args.input2),
            "preprocessing": preprocessing,
            "sample_source_ids": sample_source_ids,
            "sample_cell_ids": sample_cell_ids,
            "generic_semantic": {
                "name": "statused_large_cell_deferral_stream",
                "app_semantics": "none",
                "frontier_bridge_contract": status["metadata"]["contract"],
                "reference_contract": status["metadata"]["reference_contract"],
                "trace_summary_contract": summary["contract"],
            },
            "observed_telemetry": status["telemetry"],
            "trace_summary": summary,
            "author_sample_membership": memberships,
            "classification": {
                "all_author_sample_pairs_present": bool(all_samples_present),
                "label": (
                    "author_sample_rows_recovered_by_statused_deferral_stream"
                    if all_samples_present
                    else "author_sample_rows_not_recovered_by_statused_deferral_stream"
                ),
            },
            "decision": {
                "bounded_xhd_author_sample_row_gate_passed": bool(all_samples_present),
                "full_goal5387_row_identity_gate_authorized": bool(all_samples_present),
                "explicit_lb_support_authorized": False,
                "direct_native_fix_authorized": False,
                "recommended_next_goal": (
                    "Goal5412_full_goal5387_statused_deferral_row_identity_gate"
                    if all_samples_present
                    else "Goal5412_fail_close_explicit_lb_or_design_new_generic_native_trace_semantics"
                ),
            },
            "author_trace_v2": {
                "active_in_queue_size": author["active_in_queue_size"],
                "raw_offload_rows_before_sort_reduce": author["raw_offload_rows_before_sort_reduce"],
                "raw_offload_row_hash": author["raw_offload_row_hash"],
                "feedback_update_count": author["feedback_update_count"],
                "cmin2_after_ray_hash": author["cmin2_after_ray_hash"],
                "cmin2_after_load_balance_hash": author["cmin2_after_load_balance_hash"],
            },
            "timings_sec": {
                "load_inputs": load_sec,
                "grid_cell_mbrs": grid_sec,
                "frontier_rows": frontier_sec,
                "status_bridge": bridge_sec,
                "total": time.perf_counter() - total_start,
            },
            "claim_boundary": {
                "bounded_xhd_author_sample_recovery_claimed": bool(all_samples_present),
                "full_goal5387_row_identity_parity_claimed": False,
                "explicit_lb_support_claimed": False,
                "figure7_reproduction_claimed": False,
                "figure11_reproduction_claimed": False,
                "performance_ratio_claimed": False,
                "exact_paper_dataset_reproduction_claimed": False,
                "full_xhd_paper_reproduction_claimed": False,
            },
        }
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input1", default=str(DEFAULT_INPUT1))
    parser.add_argument("--input2", default=str(DEFAULT_INPUT2))
    parser.add_argument("--input-type", default="ply")
    parser.add_argument("--n-dims", type=int, default=3)
    parser.add_argument("--grid-shape", default="96,60,72")
    parser.add_argument("--grid-cell-point-order", default="point-id")
    parser.add_argument("--max-inline-points", type=int, default=256)
    parser.add_argument("--frontier-row-capacity", type=int, default=None)
    parser.add_argument("--radius", type=float, default=None)
    parser.add_argument("--sort-rows", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--collect-frontier-native-phase-timings", action="store_true")
    parser.add_argument("--translate-each-input-to-min-bound", action="store_true", default=True)
    parser.add_argument("--author-trace-v2", default=str(DEFAULT_AUTHOR_TRACE_V2))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_summary(args)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"output": str(output), "status": payload["status"], "matched": payload["matched"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
