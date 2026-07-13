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

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from run_xhd_goal5406_real_full_cover_surface_stream_gate import (  # noqa: E402
    DEFAULT_AUTHOR_TRACE_V2,
    DEFAULT_GOAL5365_GATE,
    DEFAULT_INPUT1,
    DEFAULT_INPUT2,
    _goal5365_full_cover_rows,
    _read_author_trace_v2,
    offload_rows_from_frontier_row_table,
    summarize_full_cover_frontier,
)


APP_ROOT = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_ROOT / "results"
DEFAULT_OUTPUT = RESULTS / "xhd_goal5407_full_cover_delta_membership_probe_pod.json"


def per_source_count_summary(source_ids: np.ndarray, *, active_count: int) -> dict[str, Any]:
    source_ids = np.asarray(source_ids, dtype=np.int64)
    if source_ids.size and (np.any(source_ids < 0) or np.any(source_ids >= int(active_count))):
        raise ValueError("source ids must be in [0, active_count)")
    counts = np.bincount(source_ids, minlength=int(active_count)).astype(np.int64, copy=False)
    unique, unique_counts = np.unique(counts, return_counts=True)
    histogram = {str(int(value)): int(count) for value, count in zip(unique, unique_counts)}
    return {
        "active_count": int(active_count),
        "row_count": int(source_ids.size),
        "min_rows_per_active": int(counts.min()) if counts.size else 0,
        "max_rows_per_active": int(counts.max()) if counts.size else 0,
        "mean_rows_per_active": float(counts.mean()) if counts.size else 0.0,
        "unique_rows_per_active": [int(value) for value in unique.tolist()],
        "rows_per_active_histogram": histogram,
        "all_sources_have_same_row_count": bool(unique.size == 1),
    }


def sample_pair_membership(
    *,
    source_ids: np.ndarray,
    cell_ids: np.ndarray,
    sample_source_ids: list[int],
    sample_cell_ids: list[int],
    max_cells_to_record: int = 16,
) -> list[dict[str, Any]]:
    source_ids = np.asarray(source_ids, dtype=np.int64)
    cell_ids = np.asarray(cell_ids, dtype=np.int64)
    if source_ids.shape != cell_ids.shape:
        raise ValueError("source_ids and cell_ids must have the same shape")
    result: list[dict[str, Any]] = []
    for source_id, cell_id in zip(sample_source_ids, sample_cell_ids):
        sid = int(source_id)
        cid = int(cell_id)
        source_mask = source_ids == sid
        source_cells = np.sort(cell_ids[source_mask])
        present = bool(np.any(source_cells == cid))
        result.append(
            {
                "source_id": sid,
                "author_cell_id": cid,
                "rtdl_source_row_count": int(source_cells.size),
                "author_cell_present_in_rtdl_full_cover": present,
                "rtdl_cells_sample": [int(value) for value in source_cells[:max_cells_to_record].tolist()],
            }
        )
    return result


def classify_delta(
    *,
    count_summary: Mapping[str, Any],
    memberships: list[Mapping[str, Any]],
    author_feedback_updates: int,
    cmin2_after_ray_hash: int | None,
    cmin2_after_load_balance_hash: int | None,
) -> dict[str, Any]:
    all_sample_pairs_present = all(bool(row["author_cell_present_in_rtdl_full_cover"]) for row in memberships)
    uniform_count = bool(count_summary["all_sources_have_same_row_count"])
    feedback_changes_cmin2_hash = (
        None
        if cmin2_after_ray_hash is None or cmin2_after_load_balance_hash is None
        else bool(int(cmin2_after_ray_hash) != int(cmin2_after_load_balance_hash))
    )
    if not all_sample_pairs_present:
        label = "author_sample_rows_not_subset_of_rtdl_full_cover__row_identity_gap"
    elif uniform_count:
        label = "author_samples_present_but_uniform_6x_delta_remains"
    else:
        label = "author_samples_present_but_nonuniform_delta_requires_distribution_probe"
    return {
        "label": label,
        "all_author_sample_pairs_present_in_rtdl_full_cover": all_sample_pairs_present,
        "rtdl_full_cover_uniform_rows_per_active": uniform_count,
        "author_feedback_update_count": int(author_feedback_updates),
        "feedback_changes_cmin2_hash": feedback_changes_cmin2_hash,
        "interpretation": (
            "Existing evidence is insufficient to promote explicit -lb. "
            "If author sample rows are absent from the RTDL full-cover surface, "
            "the gap is row identity as well as row count. If samples are present, "
            "the remaining 6 rows/active still need generic status/feedback evidence."
        ),
    }


def build_summary(args: argparse.Namespace) -> dict[str, Any]:
    total_start = time.perf_counter()
    import rtdsl as rt  # noqa: PLC0415
    from run_xhd_active_query_frontier_bridge_probe import (  # noqa: PLC0415
        _columns_3d,
        _full_cover_radius,
        _load_preprocessed_points,
        _parse_grid_shape,
    )

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
    points_a, points_b, preprocessing = _load_preprocessed_points(load_args)
    active_count = int(points_a.shape[0])
    source_columns = _columns_3d(points_a)
    target_columns = _columns_3d(points_b)
    grid_shape = _parse_grid_shape(str(args.grid_shape))
    radius = _full_cover_radius(points_a, points_b) if args.radius is None else float(args.radius)
    goal5365_rows = _goal5365_full_cover_rows(Path(args.goal5365_gate))
    grid = rt.point_grid_cell_mbrs_native_3d_cuda_columns(
        target_columns,
        coordinate_fields=("x", "y", "z"),
        grid_shape=grid_shape,
        cell_point_order=str(args.grid_cell_point_order),
        return_metadata=True,
    )
    frontier_result = rt.cell_mbr_nearest_frontier_native_3d_optix_columns(
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
    offload_rows = offload_rows_from_frontier_row_table(frontier_result["row_table"])
    trace_summary = summarize_full_cover_frontier(
        frontier=frontier_result,
        active_count=active_count,
    )
    count_summary = per_source_count_summary(
        offload_rows["source_ids"],
        active_count=active_count,
    )
    author_trace = _read_author_trace_v2(Path(args.author_trace_v2))
    author_batch = author_trace["batch_0"]
    full_author_payload = json.loads(Path(args.author_trace_v2).read_text(encoding="utf-8"))
    full_batch = full_author_payload["author_lb_trace_v2"]["batch_0"]
    memberships = sample_pair_membership(
        source_ids=offload_rows["source_ids"],
        cell_ids=offload_rows["cell_ids"],
        sample_source_ids=list(author_batch["raw_offload_row_sample_point_ids"]),
        sample_cell_ids=list(author_batch["raw_offload_row_sample_cell_ids"]),
    )
    row_count = int(trace_summary["row_count"])
    author_rows = int(author_trace["raw_offload_rows_before_sort_reduce"])
    author_hash = int(author_batch["raw_offload_row_hash"])
    delta = int(author_rows - row_count)
    delta_q, delta_r = divmod(delta, active_count)
    classification = classify_delta(
        count_summary=count_summary,
        memberships=memberships,
        author_feedback_updates=int(author_trace["feedback_update_count"]),
        cmin2_after_ray_hash=int(full_batch.get("cmin2_after_ray_hash", 0)),
        cmin2_after_load_balance_hash=int(full_batch.get("cmin2_after_load_balance_hash", 0)),
    )
    full_cover_count_matched = row_count == goal5365_rows
    row_hash = int(trace_summary["raw_offload_row_hash"])
    matched = bool(full_cover_count_matched and active_count == int(author_trace["active_in_queue_size"]) and delta_q == 6 and delta_r == 0)
    status = (
        "full_cover_delta_isolated__row_identity_or_feedback_semantics_still_open"
        if matched
        else "full_cover_delta_isolation_failed"
    )
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5407.full_cover_delta_membership_probe.v1",
        "goal": "Goal5407",
        "status": status,
        "matched": matched,
        "purpose": (
            "Probe whether the real RTDL full-cover surface is merely short by "
            "6 rows/active or also differs in sampled row identity from the "
            "Goal5387 author trace."
        ),
        "input1": str(args.input1),
        "input2": str(args.input2),
        "preprocessing": preprocessing,
        "goal5406_summary": {
            "status": "real_full_cover_surface_generated__author_delta_remaining" if full_cover_count_matched else "real_full_cover_surface_count_mismatch",
            "matched": bool(full_cover_count_matched),
            "rtdl_full_cover_rows": row_count,
            "goal5365_full_cover_rows": goal5365_rows,
            "author_raw_offload_rows": author_rows,
            "row_delta_author_minus_rtdl_full_cover": delta,
            "rtdl_full_cover_row_hash": row_hash,
            "author_raw_offload_row_hash": author_hash,
            "row_count_parity_with_author": bool(row_count == author_rows),
            "hash_parity_with_author": bool(row_hash == author_hash),
        },
        "delta": {
            "active_count": active_count,
            "total_delta_rows": delta,
            "delta_rows_per_active_if_uniform": delta_q if delta_r == 0 else None,
            "delta_rows_per_active_remainder": delta_r,
        },
        "rtdl_full_cover_per_source_count_summary": count_summary,
        "author_sample_pair_membership_in_rtdl_full_cover": memberships,
        "author_state_evidence": {
            "feedback_update_count": int(author_trace["feedback_update_count"]),
            "cmin2_after_ray_hash": int(full_batch.get("cmin2_after_ray_hash", 0)),
            "cmin2_after_load_balance_hash": int(full_batch.get("cmin2_after_load_balance_hash", 0)),
            "cmin2_after_ray_equals_after_load_balance": bool(
                int(full_batch.get("cmin2_after_ray_hash", 0))
                == int(full_batch.get("cmin2_after_load_balance_hash", 0))
            ),
            "status_count_miss": int(full_author_payload["author_lb_trace_v2"].get("status_count_miss", 0)),
            "status_count_completed": int(full_author_payload["author_lb_trace_v2"].get("status_count_completed", 0)),
            "status_count_aborted": int(full_author_payload["author_lb_trace_v2"].get("status_count_aborted", 0)),
        },
        "classification": classification,
        "decision": {
            "explicit_lb_support_authorized": False,
            "direct_native_fix_authorized": False,
            "reason": (
                "Goal5407 isolates the real 6 rows/active delta and sample-pair "
                "membership, but does not yet identify a generic native "
                "transition that can close author row/hash parity."
            ),
            "recommended_next_goal": "Goal5408_author_trace_v3_or_generic_delta_transition_design",
        },
        "timings_sec": {
            "total": time.perf_counter() - total_start,
        },
        "claim_boundary": {
            "full_cover_delta_isolated": matched,
            "explicit_lb_support_claimed": False,
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
    parser.add_argument("--grid-cell-builder", choices=("native_cuda",), default="native_cuda")
    parser.add_argument("--grid-cell-point-order", default="point-id")
    parser.add_argument("--max-inline-points", type=int, default=256)
    parser.add_argument("--frontier-row-capacity", type=int, default=None)
    parser.add_argument("--radius", type=float, default=None)
    parser.add_argument("--sort-rows", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--collect-frontier-native-phase-timings", action="store_true")
    parser.add_argument("--translate-each-input-to-min-bound", action="store_true", default=True)
    parser.add_argument("--author-trace-v2", default=str(DEFAULT_AUTHOR_TRACE_V2))
    parser.add_argument("--goal5365-gate", default=str(DEFAULT_GOAL5365_GATE))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    return parser.parse_args(argv)


DEFAULT_OUTPUT = RESULTS / "xhd_goal5407_full_cover_delta_membership_probe_pod.json"


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
