#!/usr/bin/env python3
"""Goal5008 probe: distinct-query prepared-base LSI regime.

This internal probe tests whether the 10x target regime exists for LSI:

    prepared base + same scale-domain + distinct query batches

It deliberately avoids same prepared-query replay.  A domain seed query is run
first to build the base/query scale-domain workspace.  Then three new query
handles with distinct query inputs but the same coordinate domain are measured.
Finally, a far-domain query is measured to verify that changing the domain
forces the expected workspace rebuild.
"""

from __future__ import annotations

import argparse
import gc
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
                traversal_seconds = float(columns.traversal_seconds)
            finally:
                columns.close()
            timings = lsi.prepared.last_phase_timings() or {}
    return {
        "schema": "rtdl.goal5008.generic_lsi_tiny_prewarm.v1",
        "elapsed_sec": float(time.perf_counter() - start),
        "row_count": row_count,
        "traversal_seconds": traversal_seconds,
        "native_timings": timings,
    }


def _extended(native_timings: dict[str, object]) -> dict[str, float]:
    extended = native_timings.get("extended", {}) if isinstance(native_timings, dict) else {}
    if not isinstance(extended, dict):
        extended = {}
    return {
        "scaled_cache_ensure": float(extended.get("scaled_cache_ensure", 0.0)),
        "grouped_range_ensure": float(extended.get("grouped_range_ensure", 0.0)),
        "exact_pipeline_ensure": float(extended.get("exact_pipeline_ensure", 0.0)),
        "split_kernel_ensure": float(extended.get("split_kernel_ensure", 0.0)),
        "optix_launch": float(extended.get("optix_launch", 0.0)),
        "total_native": float(extended.get("total_native", 0.0)),
    }


def _run_query(label: str, lsi, packed_segments, capacity: int) -> dict[str, object]:
    query = None
    try:
        prepare_start = time.perf_counter()
        query = lsi.prepare_query(packed_segments)
        prepare_elapsed = time.perf_counter() - prepare_start
        run_start = time.perf_counter()
        columns = query.run_bounded_pair_id_device_columns(max_rows=int(capacity))
        run_elapsed = time.perf_counter() - run_start
        try:
            native_timings = lsi.prepared.last_phase_timings() or {}
            return {
                "label": label,
                "prepare_query_sec": float(prepare_elapsed),
                "run_elapsed_sec": float(run_elapsed),
                "row_count": int(columns.row_count),
                "capacity": int(columns.capacity),
                "candidate_event_count": int(columns.candidate_event_count),
                "overflow": bool(columns.overflow),
                "traversal_seconds": float(columns.traversal_seconds),
                "native_timings": native_timings,
                "compact_timings": _extended(native_timings),
            }
        finally:
            columns.close()
    finally:
        if query is not None:
            query.close()


def _full_query_batch(app, left, *, batch_id: int, perturb: bool):
    """Build a distinct full-size query batch with unchanged coordinate bounds."""

    base = app.base
    ids = np.asarray(left.seg_ids, dtype=np.int64) + np.int64(batch_id * 10_000_000)
    x0 = np.asarray(left.x0, dtype=np.float64).copy()
    y0 = np.asarray(left.y0, dtype=np.float64).copy()
    x1 = np.asarray(left.x1, dtype=np.float64).copy()
    y1 = np.asarray(left.y1, dtype=np.float64).copy()

    if perturb and x0.size > 4096:
        # Perturb a handful of interior segments without touching extrema.  This
        # keeps the scale domain stable while making the query geometry distinct.
        step = max(1024, x0.size // 32)
        epsilon = 1.0e-9 * float(batch_id)
        for index in range(step, min(x0.size, step * 8), step):
            y0[index] += epsilon
            y1[index] += epsilon

    return base.pack_segments(ids=ids, x0=x0, y0=y0, x1=x1, y1=y1)


def _far_domain_query(app):
    base = app.base
    return base.pack_segments(
        ids=np.array([999_999_001], dtype=np.int64),
        x0=np.array([1.0e7], dtype=np.float64),
        y0=np.array([1.0e7], dtype=np.float64),
        x1=np.array([1.0e7 + 1.0], dtype=np.float64),
        y1=np.array([1.0e7 + 1.0], dtype=np.float64),
    )


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
        "schema": "rtdl.goal5008.distinct_query_many_lsi_probe.v1",
        "left": str(args.left),
        "right": str(args.right),
        "capacity": int(args.capacity),
        "regime_under_test": "prepared_base_same_scale_domain_distinct_query_batches",
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
    result["left_domain"] = {
        "min_x": float(left.min_x),
        "max_x": float(left.max_x),
        "min_y": float(left.min_y),
        "max_y": float(left.max_y),
    }
    result["right_domain"] = {
        "min_x": float(right.min_x),
        "max_x": float(right.max_x),
        "min_y": float(right.min_y),
        "max_y": float(right.max_y),
    }

    runs: list[dict[str, object]] = []
    lsi = None
    try:
        prepare_base_start = time.perf_counter()
        lsi = base.prepare_planar_map_lsi_2d_optix(right.lsi_segments)
        result["prepare_right_base_sec"] = float(time.perf_counter() - prepare_base_start)

        seed = _full_query_batch(app, left, batch_id=0, perturb=False)
        runs.append(_run_query("domain_seed_full_query", lsi, seed, args.capacity))
        del seed
        gc.collect()

        for batch_id in (1, 2, 3):
            batch = _full_query_batch(app, left, batch_id=batch_id, perturb=True)
            runs.append(_run_query(f"distinct_same_domain_query_{batch_id}", lsi, batch, args.capacity))
            del batch
            gc.collect()

        far = _far_domain_query(app)
        runs.append(_run_query("distinct_far_domain_query", lsi, far, args.capacity))
        del far
        gc.collect()
    finally:
        if lsi is not None:
            lsi.close()

    same_domain = [run for run in runs if str(run["label"]).startswith("distinct_same_domain_query_")]
    result["runs"] = runs
    result["decision_inputs"] = {
        "same_domain_distinct_query_count": len(same_domain),
        "same_domain_run_elapsed_sec": [run["run_elapsed_sec"] for run in same_domain],
        "same_domain_row_counts": [run["row_count"] for run in same_domain],
        "same_domain_scaled_cache_ensure_sec": [
            run["compact_timings"]["scaled_cache_ensure"] for run in same_domain
        ],
        "same_domain_grouped_range_ensure_sec": [
            run["compact_timings"]["grouped_range_ensure"] for run in same_domain
        ],
        "far_domain_run_elapsed_sec": next(
            (run["run_elapsed_sec"] for run in runs if run["label"] == "distinct_far_domain_query"),
            None,
        ),
        "query_many_wording_authorized_for_lsi_only": len(same_domain) >= 3,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
