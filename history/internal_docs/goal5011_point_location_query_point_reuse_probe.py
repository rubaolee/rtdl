#!/usr/bin/env python3
"""Goal5011 probe: reuse prepared point-location query points across locators."""

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
    spans = np.maximum(np.asarray(chain_point_counts, dtype=np.int64) - 1, 0)
    offsets = np.empty(spans.shape[0], dtype=np.int64)
    if spans.shape[0] == 0:
        return offsets
    offsets[0] = 0
    if spans.shape[0] > 1:
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
        name=f"{dataset.name}_reuse_variant_{batch_id}",
        point_y=point_y,
        y0=y0,
        y1=y1,
        lsi_segments=lsi_segments,
        cdb_segments=cdb_segments,
        points=points,
    )


def _run_face_ids(app, locator, prepared_points, *, label):
    start = time.perf_counter()
    values = app.run_point_location_face_id_device_columns(
        locator,
        None,
        prepared_points.point_count,
        phase_prefix=label,
        phase_seconds={},
        metadata_records={},
        prepared_points=prepared_points,
        retain_device=False,
        copy_host=True,
    )
    return {
        "elapsed_sec": float(time.perf_counter() - start),
        "face_hash": int(np.asarray(values, dtype=np.uint32).sum(dtype=np.uint64) % np.uint64(2**63 - 1)),
        "positive_count": int(np.count_nonzero(np.asarray(values, dtype=np.uint32))),
        "sample": [int(v) for v in np.asarray(values, dtype=np.uint32)[:8]],
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
    left = base.load_dataset_arrays(args.left)
    right = base.load_dataset_arrays(args.right)
    bounds = base.shared_bounds(left, right)

    result = {
        "schema": "rtdl.goal5011.point_location_query_point_reuse_probe.v1",
        "left": str(args.left),
        "right": str(args.right),
        "shared_bounds": [float(v) for v in bounds],
    }

    variants = [_make_variant(app, left, batch_id=i) for i in (1, 2, 3)]
    locators = []
    try:
        for variant in variants:
            start = time.perf_counter()
            locator = base.prepare_planar_map_point_location_2d_optix(
                variant.cdb_segments,
                query_map_id=1,
                scale_bounds=bounds,
            )
            locators.append((locator, float(time.perf_counter() - start)))

        # Prepare right points once using the first locator.  The probe tests
        # whether this query-point handle is valid across same-domain locators.
        start = time.perf_counter()
        shared_points = locators[0][0].prepare_query_points(right.points)
        shared_prepare_sec = float(time.perf_counter() - start)
        try:
            rows = []
            for index, (locator, prepare_sec) in enumerate(locators, start=1):
                local_start = time.perf_counter()
                local_points = locator.prepare_query_points(right.points)
                local_prepare_sec = float(time.perf_counter() - local_start)
                try:
                    local = _run_face_ids(app, locator, local_points, label=f"local_points_{index}")
                finally:
                    local_points.close()
                shared = _run_face_ids(app, locator, shared_points, label=f"shared_points_{index}")
                rows.append(
                    {
                        "batch_id": index,
                        "prepare_locator_sec": prepare_sec,
                        "local_prepare_points_sec": local_prepare_sec,
                        "local_run": local,
                        "shared_prepare_points_sec_amortized": shared_prepare_sec if index == 1 else 0.0,
                        "shared_run": shared,
                        "same_positive_count": local["positive_count"] == shared["positive_count"],
                        "same_face_hash": local["face_hash"] == shared["face_hash"],
                        "same_sample": local["sample"] == shared["sample"],
                    }
                )
            result["shared_prepare_points_sec"] = shared_prepare_sec
            result["rows"] = rows
            result["decision_inputs"] = {
                "all_same_positive_count": all(row["same_positive_count"] for row in rows),
                "all_same_face_hash": all(row["same_face_hash"] for row in rows),
                "local_prepare_points_sec": [row["local_prepare_points_sec"] for row in rows],
                "shared_prepare_points_sec": shared_prepare_sec,
                "shared_run_sec": [row["shared_run"]["elapsed_sec"] for row in rows],
                "local_run_sec": [row["local_run"]["elapsed_sec"] for row in rows],
            }
        finally:
            shared_points.close()
    finally:
        for locator, _ in locators:
            locator.close()
        del variants
        gc.collect()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
