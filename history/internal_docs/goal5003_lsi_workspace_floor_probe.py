#!/usr/bin/env python3
"""Goal5003 probe: characterize the fresh LSI per-input workspace floor.

This internal script does not add a product API. It tests whether the remaining
LSI workspace cost after Goal5002's generic pipeline prewarm is tied to:

* the same prepared query handle,
* a new query handle with the same input,
* or a new query whose scale domain changes.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np


def _load_app(repo: Path):
    app_dir = repo / "Paper-reproduction-apps" / "rayjoin-paper"
    src_dir = repo / "src"
    sys.path.insert(0, str(app_dir))
    sys.path.insert(0, str(src_dir))
    import section57_overlay_columnar_binary as app  # type: ignore

    return app


def _generic_lsi_tiny_prewarm(app) -> dict[str, object]:
    base = app.base
    right = base.pack_segments(
        ids=np.array([1], dtype=np.int64),
        x0=np.array([0.0], dtype=np.float64),
        y0=np.array([1.0], dtype=np.float64),
        x1=np.array([1.0], dtype=np.float64),
        y1=np.array([0.0], dtype=np.float64),
    )
    left = base.pack_segments(
        ids=np.array([2], dtype=np.int64),
        x0=np.array([0.0], dtype=np.float64),
        y0=np.array([0.0], dtype=np.float64),
        x1=np.array([1.0], dtype=np.float64),
        y1=np.array([1.0], dtype=np.float64),
    )
    start = time.perf_counter()
    with base.prepare_planar_map_lsi_2d_optix(right) as lsi:
        with lsi.prepare_query(left) as query:
            columns = query.run_bounded_pair_id_device_columns(max_rows=8)
            try:
                row_count = int(columns.row_count)
                timings = lsi.prepared.last_phase_timings() or {}
            finally:
                columns.close()
    return {
        "elapsed_sec": float(time.perf_counter() - start),
        "row_count": row_count,
        "native_timings": timings,
    }


def _run_bounded(label: str, lsi, query, capacity: int) -> dict[str, object]:
    start = time.perf_counter()
    columns = query.run_bounded_pair_id_device_columns(max_rows=int(capacity))
    elapsed = time.perf_counter() - start
    try:
        timings = lsi.prepared.last_phase_timings() or {}
        return {
            "label": label,
            "elapsed_sec": float(elapsed),
            "row_count": int(columns.row_count),
            "capacity": int(columns.capacity),
            "candidate_event_count": int(columns.candidate_event_count),
            "overflow": bool(columns.overflow),
            "traversal_seconds": float(columns.traversal_seconds),
            "native_timings": timings,
        }
    finally:
        columns.close()


def _far_query_segments(app):
    base = app.base
    return base.pack_segments(
        ids=np.array([999_999_001], dtype=np.int64),
        x0=np.array([1.0e7], dtype=np.float64),
        y0=np.array([1.0e7], dtype=np.float64),
        x1=np.array([1.0e7 + 1.0], dtype=np.float64),
        y1=np.array([1.0e7 + 1.0], dtype=np.float64),
    )


def _compact_timing(run: dict[str, object]) -> dict[str, object]:
    native = run.get("native_timings", {})
    if not isinstance(native, dict):
        native = {}
    extended = native.get("extended", {})
    if not isinstance(extended, dict):
        extended = {}
    return {
        "label": run["label"],
        "elapsed_sec": run["elapsed_sec"],
        "row_count": run["row_count"],
        "scaled_cache_ensure": float(extended.get("scaled_cache_ensure", 0.0)),
        "grouped_range_ensure": float(extended.get("grouped_range_ensure", 0.0)),
        "exact_pipeline_ensure": float(extended.get("exact_pipeline_ensure", 0.0)),
        "split_kernel_ensure": float(extended.get("split_kernel_ensure", 0.0)),
        "optix_launch": float(extended.get("optix_launch", 0.0)),
        "total_native": float(extended.get("total_native", 0.0)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--left", type=Path, required=True)
    parser.add_argument("--right", type=Path, required=True)
    parser.add_argument("--capacity", type=int, default=1_000_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    app = _load_app(args.repo)
    base = app.base
    result: dict[str, object] = {
        "schema": "rtdl.paper_reproduction.rayjoin.goal5003.lsi_workspace_floor_probe.v1",
        "left": str(args.left),
        "right": str(args.right),
        "capacity": int(args.capacity),
    }

    result["generic_tiny_prewarm"] = _generic_lsi_tiny_prewarm(app)

    load_start = time.perf_counter()
    left = base.load_dataset_arrays(args.left)
    right = base.load_dataset_arrays(args.right)
    result["load_dataset_arrays_sec"] = float(time.perf_counter() - load_start)
    result["input_counts"] = {
        "left_lsi_segments": int(left.lsi_segments.count),
        "right_lsi_segments": int(right.lsi_segments.count),
    }

    runs: list[dict[str, object]] = []
    lsi = None
    query = None
    query2 = None
    far_query = None
    query3 = None
    try:
        base_start = time.perf_counter()
        lsi = base.prepare_planar_map_lsi_2d_optix(right.lsi_segments)
        result["prepare_right_base_sec"] = float(time.perf_counter() - base_start)

        query_start = time.perf_counter()
        query = lsi.prepare_query(left.lsi_segments)
        result["prepare_full_query_sec"] = float(time.perf_counter() - query_start)

        runs.append(_run_bounded("full_first_run_build_workspace", lsi, query, args.capacity))
        runs.append(_run_bounded("full_same_prepared_query_replay", lsi, query, args.capacity))

        query2_start = time.perf_counter()
        query2 = lsi.prepare_query(left.lsi_segments)
        result["prepare_new_full_query_same_input_sec"] = float(time.perf_counter() - query2_start)
        runs.append(_run_bounded("full_new_query_same_input_same_base", lsi, query2, args.capacity))

        far_query_segments = _far_query_segments(app)
        far_query_start = time.perf_counter()
        far_query = lsi.prepare_query(far_query_segments)
        result["prepare_far_query_same_base_sec"] = float(time.perf_counter() - far_query_start)
        runs.append(_run_bounded("far_query_changed_scale_same_base", lsi, far_query, args.capacity))

        query3_start = time.perf_counter()
        query3 = lsi.prepare_query(left.lsi_segments)
        result["prepare_full_query_after_far_scale_change_sec"] = float(time.perf_counter() - query3_start)
        runs.append(_run_bounded("full_query_after_far_scale_change", lsi, query3, args.capacity))
    finally:
        for handle in (query3, far_query, query2, query, lsi):
            if handle is not None:
                handle.close()

    result["runs"] = runs
    result["compact_runs"] = [_compact_timing(run) for run in runs]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
