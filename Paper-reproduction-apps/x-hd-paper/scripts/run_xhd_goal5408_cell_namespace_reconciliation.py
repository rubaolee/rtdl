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
from run_xhd_goal5407_full_cover_delta_membership_probe import (  # noqa: E402
    per_source_count_summary,
)


APP_ROOT = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULTS = APP_ROOT / "results"
DEFAULT_OUTPUT = RESULTS / "xhd_goal5408_cell_namespace_reconciliation_pod.json"


def compact_to_original_lookup(
    compact_cell_ids: np.ndarray,
    original_cell_ids: np.ndarray,
) -> np.ndarray:
    compact = np.asarray(compact_cell_ids, dtype=np.int64)
    original = np.asarray(original_cell_ids, dtype=np.int64)
    if compact.ndim != 1 or original.shape != compact.shape:
        raise ValueError("compact and original cell ids must be 1-D arrays with matching shape")
    if compact.size == 0:
        raise ValueError("cell id mapping must be non-empty")
    if np.any(compact < 0):
        raise ValueError("compact cell ids must be non-negative")
    if np.unique(compact).size != compact.size:
        raise ValueError("compact cell ids must be unique")
    max_compact = int(compact.max())
    lookup = np.full(max_compact + 1, -1, dtype=np.int64)
    lookup[compact] = original
    if np.any(lookup < 0):
        raise ValueError("compact cell ids must be dense for this reconciliation")
    return lookup


def map_compact_cells_to_original(
    cell_ids: np.ndarray,
    compact_to_original: np.ndarray,
) -> np.ndarray:
    cells = np.asarray(cell_ids, dtype=np.int64)
    lookup = np.asarray(compact_to_original, dtype=np.int64)
    if np.any(cells < 0) or np.any(cells >= lookup.size):
        raise ValueError("offload cell ids must index the compact-to-original lookup")
    return lookup[cells]


def _int_sample(values: np.ndarray, limit: int) -> list[int]:
    return [int(value) for value in np.asarray(values, dtype=np.int64)[: int(limit)].tolist()]


def sample_namespace_reconciliation(
    *,
    source_ids: np.ndarray,
    compact_cell_ids: np.ndarray,
    original_cell_ids_for_rows: np.ndarray,
    global_compact_cell_ids: np.ndarray,
    global_original_cell_ids: np.ndarray,
    sample_source_ids: list[int],
    sample_cell_ids: list[int],
    max_cells_to_record: int = 16,
) -> list[dict[str, Any]]:
    source_ids = np.asarray(source_ids, dtype=np.int64)
    compact_cell_ids = np.asarray(compact_cell_ids, dtype=np.int64)
    original_cell_ids_for_rows = np.asarray(original_cell_ids_for_rows, dtype=np.int64)
    if source_ids.shape != compact_cell_ids.shape or source_ids.shape != original_cell_ids_for_rows.shape:
        raise ValueError("source, compact-cell, and original-cell row arrays must have matching shape")
    global_compact_cell_ids = np.asarray(global_compact_cell_ids, dtype=np.int64)
    global_original_cell_ids = np.asarray(global_original_cell_ids, dtype=np.int64)
    compact_to_original = {int(c): int(o) for c, o in zip(global_compact_cell_ids, global_original_cell_ids)}
    original_to_compact = {int(o): int(c) for c, o in zip(global_compact_cell_ids, global_original_cell_ids)}
    result: list[dict[str, Any]] = []
    for source_id, author_cell_id in zip(sample_source_ids, sample_cell_ids):
        sid = int(source_id)
        cid = int(author_cell_id)
        source_mask = source_ids == sid
        source_compact = np.sort(compact_cell_ids[source_mask])
        source_original = np.sort(original_cell_ids_for_rows[source_mask])
        compact_present = bool(np.any(source_compact == cid))
        original_present = bool(np.any(source_original == cid))
        global_compact_exists = cid in compact_to_original
        global_original_exists = cid in original_to_compact
        result.append(
            {
                "source_id": sid,
                "author_cell_id": cid,
                "rtdl_source_row_count": int(source_compact.size),
                "author_cell_present_as_compact_in_source": compact_present,
                "author_cell_present_as_original_in_source": original_present,
                "author_cell_exists_as_global_compact": bool(global_compact_exists),
                "author_cell_exists_as_global_original": bool(global_original_exists),
                "author_cell_as_compact_maps_to_original": (
                    int(compact_to_original[cid]) if global_compact_exists else None
                ),
                "author_cell_as_original_maps_to_compact": (
                    int(original_to_compact[cid]) if global_original_exists else None
                ),
                "rtdl_compact_cells_sample": _int_sample(source_compact, max_cells_to_record),
                "rtdl_original_cells_sample": _int_sample(source_original, max_cells_to_record),
            }
        )
    return result


def classify_namespace_reconciliation(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    compact_present = [bool(row["author_cell_present_as_compact_in_source"]) for row in rows]
    original_present = [bool(row["author_cell_present_as_original_in_source"]) for row in rows]
    global_compact = [bool(row["author_cell_exists_as_global_compact"]) for row in rows]
    global_original = [bool(row["author_cell_exists_as_global_original"]) for row in rows]
    if all(compact_present):
        label = "author_samples_recovered_as_rtdl_compact_cell_ids"
    elif all(original_present):
        label = "author_samples_recovered_as_rtdl_original_cell_ids"
    elif any(compact_present) or any(original_present):
        label = "author_samples_partially_recovered_by_rtdl_cell_namespace"
    elif any(global_compact) or any(global_original):
        label = "author_sample_cell_ids_exist_globally_but_not_for_author_sources"
    else:
        label = "author_sample_cell_ids_not_recovered_in_compact_or_original_namespace"
    return {
        "label": label,
        "all_samples_present_as_compact": all(compact_present),
        "all_samples_present_as_original": all(original_present),
        "any_sample_present_as_compact_or_original": any(compact_present) or any(original_present),
        "any_author_cell_id_exists_globally": any(global_compact) or any(global_original),
        "interpretation": (
            "If samples are recovered as original cell ids, the next gate may be "
            "a generic compact/original namespace remap. If not, the gap is not "
            "explained by the existing RTDL compact/original cell id mapping."
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
    cell_columns = grid["cell_columns"]
    compact_lookup = compact_to_original_lookup(
        np.asarray(cell_columns["cell_ids"], dtype=np.int64),
        np.asarray(cell_columns["original_cell_ids"], dtype=np.int64),
    )
    frontier_result = rt.cell_mbr_nearest_frontier_native_3d_optix_columns(
        source_columns,
        cell_columns,
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
    offload_original_cells = map_compact_cells_to_original(
        offload_rows["cell_ids"],
        compact_lookup,
    )
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
    rows = sample_namespace_reconciliation(
        source_ids=offload_rows["source_ids"],
        compact_cell_ids=offload_rows["cell_ids"],
        original_cell_ids_for_rows=offload_original_cells,
        global_compact_cell_ids=np.asarray(cell_columns["cell_ids"], dtype=np.int64),
        global_original_cell_ids=np.asarray(cell_columns["original_cell_ids"], dtype=np.int64),
        sample_source_ids=list(author_batch["raw_offload_row_sample_point_ids"]),
        sample_cell_ids=list(author_batch["raw_offload_row_sample_cell_ids"]),
    )
    classification = classify_namespace_reconciliation(rows)
    row_count = int(trace_summary["row_count"])
    author_rows = int(author_trace["raw_offload_rows_before_sort_reduce"])
    delta = int(author_rows - row_count)
    delta_q, delta_r = divmod(delta, active_count)
    full_cover_count_matched = row_count == int(goal5365_rows)
    active_parity = active_count == int(author_trace["active_in_queue_size"])
    matched = bool(full_cover_count_matched and active_parity and delta_q == 6 and delta_r == 0)
    status = (
        "cell_namespace_reconciliation_complete__sample_rows_not_recovered"
        if matched and not classification["any_sample_present_as_compact_or_original"]
        else (
            "cell_namespace_reconciliation_complete__sample_rows_recovered"
            if matched
            else "cell_namespace_reconciliation_failed"
        )
    )
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5408.cell_namespace_reconciliation.v1",
        "goal": "Goal5408",
        "status": status,
        "matched": matched,
        "purpose": (
            "Determine whether Goal5407's absent author sample rows are merely "
            "a compact-vs-original cell-id namespace issue."
        ),
        "input1": str(args.input1),
        "input2": str(args.input2),
        "preprocessing": preprocessing,
        "grid": {
            "grid_shape": [int(value) for value in grid_shape],
            "cell_count": int(np.asarray(cell_columns["cell_ids"]).size),
            "cell_id_contract": str(grid.get("metadata", {}).get("cell_id_contract")),
            "compact_cell_id_min": int(np.asarray(cell_columns["cell_ids"], dtype=np.int64).min()),
            "compact_cell_id_max": int(np.asarray(cell_columns["cell_ids"], dtype=np.int64).max()),
            "original_cell_id_min": int(np.asarray(cell_columns["original_cell_ids"], dtype=np.int64).min()),
            "original_cell_id_max": int(np.asarray(cell_columns["original_cell_ids"], dtype=np.int64).max()),
        },
        "goal5407_delta": {
            "active_count": active_count,
            "rtdl_full_cover_rows": row_count,
            "goal5365_full_cover_rows": int(goal5365_rows),
            "author_raw_offload_rows": author_rows,
            "total_delta_rows": delta,
            "delta_rows_per_active_if_uniform": delta_q if delta_r == 0 else None,
            "delta_rows_per_active_remainder": delta_r,
            "rtdl_rows_per_active_summary": count_summary,
            "rtdl_full_cover_row_hash": int(trace_summary["raw_offload_row_hash"]),
            "author_raw_offload_row_hash": int(author_batch["raw_offload_row_hash"]),
        },
        "author_sample_namespace_reconciliation": rows,
        "classification": classification,
        "author_state_evidence": {
            "feedback_update_count": int(author_trace["feedback_update_count"]),
            "cmin2_after_ray_hash": int(full_batch.get("cmin2_after_ray_hash", 0)),
            "cmin2_after_load_balance_hash": int(full_batch.get("cmin2_after_load_balance_hash", 0)),
            "cmin2_after_ray_equals_after_load_balance": bool(
                int(full_batch.get("cmin2_after_ray_hash", 0))
                == int(full_batch.get("cmin2_after_load_balance_hash", 0))
            ),
        },
        "decision": {
            "compact_original_namespace_remap_explains_author_samples": bool(
                classification["all_samples_present_as_original"]
                or classification["all_samples_present_as_compact"]
            ),
            "explicit_lb_support_authorized": False,
            "direct_native_fix_authorized": False,
            "recommended_next_goal": (
                "Goal5409_define_generic_row_identity_parity_gate"
                if classification["all_samples_present_as_original"]
                or classification["all_samples_present_as_compact"]
                else "Goal5409_status_machine_semantics_or_fail_closed_decision"
            ),
        },
        "timings_sec": {
            "total": time.perf_counter() - total_start,
        },
        "claim_boundary": {
            "cell_namespace_reconciliation_claimed": matched,
            "explicit_lb_support_claimed": False,
            "row_count_parity_with_author_claimed": False,
            "hash_sample_parity_with_author_claimed": False,
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
