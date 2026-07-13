#!/usr/bin/env python3
"""Goal5010 probe: point-location cost in distinct-query overlay regime."""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from dataclasses import replace
from pathlib import Path

import numpy as np


def _load_app(repo: Path):
    app_dir = repo / "Paper-reproduction-apps" / "rayjoin-paper"
    src_dir = repo / "src"
    sys.path.insert(0, str(app_dir))
    sys.path.insert(0, str(src_dir))
    import section57_overlay_columnar_binary as app  # type: ignore

    return app


def _edge_offsets(chain_point_counts: np.ndarray) -> np.ndarray:
    counts = np.asarray(chain_point_counts, dtype=np.int64)
    spans = np.maximum(counts - 1, 0)
    offsets = np.empty(counts.shape[0], dtype=np.int64)
    if counts.shape[0] == 0:
        return offsets
    offsets[0] = 0
    if counts.shape[0] > 1:
        offsets[1:] = np.cumsum(spans[:-1])
    return offsets


def _make_variant(app, dataset, *, batch_id: int):
    base = app.base
    point_x = np.asarray(dataset.point_x, dtype=np.float64).copy()
    point_y = np.asarray(dataset.point_y, dtype=np.float64).copy()
    x0 = np.asarray(dataset.x0, dtype=np.float64).copy()
    y0 = np.asarray(dataset.y0, dtype=np.float64).copy()
    x1 = np.asarray(dataset.x1, dtype=np.float64).copy()
    y1 = np.asarray(dataset.y1, dtype=np.float64).copy()
    edge_offsets = _edge_offsets(dataset.chain_point_counts)
    epsilon = 1.0e-9 * float(batch_id)
    changed_points = []
    for ordinal in range(min(8, int(dataset.chain_count))):
        chain_index = int((ordinal + 1) * max(1, dataset.chain_count // 9))
        chain_index = min(chain_index, int(dataset.chain_count) - 1)
        point_count = int(dataset.chain_point_counts[chain_index])
        if point_count < 3:
            continue
        local_point = point_count // 2
        point_index = int(dataset.chain_offsets[chain_index]) + local_point
        point_y[point_index] += epsilon
        edge_start = int(edge_offsets[chain_index])
        prev_edge = edge_start + local_point - 1
        next_edge = edge_start + local_point
        if 0 <= prev_edge < y1.shape[0]:
            y1[prev_edge] += epsilon
        if 0 <= next_edge < y0.shape[0]:
            y0[next_edge] += epsilon
        changed_points.append(int(point_index))
    lsi_segments = base.pack_segments(ids=dataset.seg_ids, x0=x0, y0=y0, x1=x1, y1=y1)
    cdb_segments = base.pack_cdb_segments_from_arrays(
        dataset.seg_ids,
        x0,
        y0,
        x1,
        y1,
        dataset.left_face_ids,
        dataset.right_face_ids,
    )
    point_ids = np.arange(1, int(dataset.point_count) + 1, dtype=np.int64)
    points = base.pack_points(ids=point_ids, x=point_x, y=point_y, dimension=2)
    return replace(
        dataset,
        name=f"{dataset.name}_pl_variant_{batch_id}",
        point_y=point_y,
        y0=y0,
        y1=y1,
        lsi_segments=lsi_segments,
        cdb_segments=cdb_segments,
        points=points,
    ), changed_points


def _timings(locator):
    return locator.last_phase_timings() or {}


def _compact_native(native):
    if not isinstance(native, dict):
        native = {}
    extended = native.get("extended", {})
    if not isinstance(extended, dict):
        extended = {}
    compact = {
        "bvh": native.get("bvh"),
        "trav": native.get("trav"),
        "copy": native.get("copy"),
    }
    for key, value in extended.items():
        if isinstance(value, (int, float)):
            compact[key] = float(value)
    return compact


def _run_face_columns(app, locator, points, count: int, *, prepared_points=None, label: str):
    start = time.perf_counter()
    value = app.run_point_location_face_id_device_columns(
        locator,
        points,
        count,
        phase_prefix=label,
        phase_seconds={},
        metadata_records={},
        prepared_points=prepared_points,
        retain_device=False,
        copy_host=True,
    )
    elapsed = time.perf_counter() - start
    return {
        "elapsed_sec": float(elapsed),
        "positive_count": int(np.count_nonzero(np.asarray(value, dtype=np.uint32))),
        "native_timings": _compact_native(_timings(locator)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--left", type=Path, required=True)
    parser.add_argument("--right", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    app = _load_app(args.repo)
    base = app.base
    result = {
        "schema": "rtdl.goal5010.point_location_query_many_probe.v1",
        "left": str(args.left),
        "right": str(args.right),
    }
    load_start = time.perf_counter()
    left = base.load_dataset_arrays(args.left)
    right = base.load_dataset_arrays(args.right)
    bounds = base.shared_bounds(left, right)
    result["load_dataset_arrays_sec"] = float(time.perf_counter() - load_start)
    result["shared_bounds"] = [float(v) for v in bounds]
    result["input_counts"] = {
        "left_edges": int(left.edge_count),
        "left_points": int(left.point_count),
        "right_edges": int(right.edge_count),
        "right_points": int(right.point_count),
    }

    # Reusable right-base locator: left vertices in right map.
    right_locator = None
    try:
        start = time.perf_counter()
        right_locator = base.prepare_planar_map_point_location_2d_optix(
            right.cdb_segments,
            query_map_id=0,
            scale_bounds=bounds,
        )
        result["prepare_reusable_right_locator_sec"] = float(time.perf_counter() - start)
        result["reusable_right_locator_native_timings"] = _compact_native(_timings(right_locator))
        prepared_left_points = None
        try:
            start = time.perf_counter()
            prepared_left_points = right_locator.prepare_query_points(left.points)
            result["prepare_left_points_for_reusable_right_locator_sec"] = float(time.perf_counter() - start)
            result["left_vertices_in_right_run"] = _run_face_columns(
                app,
                right_locator,
                left.points,
                left.point_count,
                prepared_points=prepared_left_points,
                label="left_vertices_in_right_reusable",
            )
        finally:
            if prepared_left_points is not None:
                prepared_left_points.close()
    finally:
        if right_locator is not None:
            right_locator.close()

    rows = []
    for batch_id in (1, 2, 3):
        variant, changed_points = _make_variant(app, left, batch_id=batch_id)
        locator = None
        prepared_right_points = None
        try:
            prepare_start = time.perf_counter()
            locator = base.prepare_planar_map_point_location_2d_optix(
                variant.cdb_segments,
                query_map_id=1,
                scale_bounds=bounds,
            )
            prepare_sec = time.perf_counter() - prepare_start
            prepare_native = _compact_native(_timings(locator))

            points_start = time.perf_counter()
            prepared_right_points = locator.prepare_query_points(right.points)
            prepare_points_sec = time.perf_counter() - points_start
            run = _run_face_columns(
                app,
                locator,
                right.points,
                right.point_count,
                prepared_points=prepared_right_points,
                label=f"right_vertices_in_left_variant_{batch_id}",
            )
            rows.append(
                {
                    "batch_id": int(batch_id),
                    "changed_point_count": len(changed_points),
                    "prepare_left_locator_sec": float(prepare_sec),
                    "prepare_left_locator_native_timings": prepare_native,
                    "prepare_right_query_points_sec": float(prepare_points_sec),
                    "run_right_vertices_in_left_sec": run["elapsed_sec"],
                    "run_native_timings": run["native_timings"],
                    "positive_count": run["positive_count"],
                    "total_point_location_body_sec": float(prepare_sec + prepare_points_sec + run["elapsed_sec"]),
                }
            )
        finally:
            if prepared_right_points is not None:
                prepared_right_points.close()
            if locator is not None:
                locator.close()
            del variant
            gc.collect()
    result["distinct_left_locator_rows"] = rows
    result["decision_inputs"] = {
        "total_point_location_body_sec": [row["total_point_location_body_sec"] for row in rows],
        "prepare_left_locator_sec": [row["prepare_left_locator_sec"] for row in rows],
        "prepare_right_query_points_sec": [row["prepare_right_query_points_sec"] for row in rows],
        "run_right_vertices_in_left_sec": [row["run_right_vertices_in_left_sec"] for row in rows],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
