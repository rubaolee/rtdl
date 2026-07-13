#!/usr/bin/env python3
"""Goal5012 probe: full binary overlay body with shared prepared query points.

This internal probe extends Goal5008 from LSI-only to the writer-free binary
overlay body.  It measures a prepared right/base serving distinct same-domain
left/query batches, and includes per-query query-specific preparation that the
full overlay body needs (notably the left-side point-location locator).
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

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


def _make_distinct_dataset_variant(app, dataset, *, batch_id: int):
    """Return a same-domain geometry variant with tiny interior perturbations."""

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
    target_chain_count = min(8, int(dataset.chain_count))
    for ordinal in range(target_chain_count):
        chain_index = int((ordinal + 1) * max(1, dataset.chain_count // (target_chain_count + 1)))
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

    lsi_segments = base.pack_segments(
        ids=dataset.seg_ids,
        x0=x0,
        y0=y0,
        x1=x1,
        y1=y1,
    )
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
        name=f"{dataset.name}_same_domain_variant_{batch_id}",
        point_y=point_y,
        y0=y0,
        y1=y1,
        lsi_segments=lsi_segments,
        cdb_segments=cdb_segments,
        points=points,
    ), changed_points


def _build_run_args(left_path: Path, right_path: Path, capacity: int) -> SimpleNamespace:
    return SimpleNamespace(
        left=str(left_path),
        right=str(right_path),
        summary=None,
        pair_name="top4_county_zipcode",
        author_overlay_compute_sec=None,
        cache_dir=None,
        swap_query_map_ids=False,
        no_numba_warmup=True,
        repeat=1,
        warmup_runs=0,
        prepared_operator_session=False,
        prepared_lsi_replay=False,
        device_columnar=True,
        exact_lsi_device_columns=False,
        bounded_exact_lsi_device_columns=True,
        bounded_exact_lsi_capacity=int(capacity),
        point_location_device_face_columns=True,
        fast_scaled_point_pack=True,
        validate_device_order=False,
        compiled_group=True,
        compiled_group_side_order="0,1",
        device_resident_carrier=False,
        bounded_exact_lsi_repeat_diagnostic=0,
    )


def _compact_overlay_summary(summary: dict[str, object]) -> dict[str, object]:
    phase = summary.get("phase_seconds", {})
    floor = summary.get("downstream_floor_breakdown", {})
    consumer = summary.get("downstream_consumer", {})
    if not isinstance(phase, dict):
        phase = {}
    if not isinstance(floor, dict):
        floor = {}
    if not isinstance(consumer, dict):
        consumer = {}
    return {
        "writer_free_hot_sec": float(summary.get("writer_free_hot_sec", 0.0)),
        "lsi_phase_sec": float(floor.get("lsi_phase_sec", 0.0)),
        "downstream_floor_sec": float(floor.get("downstream_floor_sec", 0.0)),
        "lsi_row_count": int(summary.get("lsi_row_count", 0)),
        "descriptor_pair_count": int(consumer.get("pair_count", 0)),
        "key_phase_seconds": {
            key: float(phase[key])
            for key in (
                "lsi_bounded_exact_pair_id_device_columns_sec",
                "intersection_reprojection_device_columnar_sec",
                "sort_map0_device_columnar_sec",
                "sort_map1_device_columnar_sec",
                "vertex_pip_map0_in_map1_sec",
                "vertex_pip_map1_in_map0_sec",
                "midpoint_points_map0_columnar_sec",
                "midpoint_points_map1_columnar_sec",
                "midpoint_pip_map0_sec",
                "midpoint_pip_map1_sec",
                "assign_midpoint_faces_map0_columnar_sec",
                "assign_midpoint_faces_map1_columnar_sec",
                "grouped_compiled_columnar_carrier_construction_sec",
                "grouped_descriptor_pair_count_consumer_sec",
            )
            if key in phase
        },
    }


def _run_overlay_query(
    app,
    *,
    args_template: SimpleNamespace,
    right,
    bounds,
    lsi,
    map0_in_map1,
    left_variant,
    label: str,
    shared_right_query_points=None,
) -> dict[str, object]:
    query = None
    map1_in_map0 = None
    try:
        prepare_lsi_start = time.perf_counter()
        query = lsi.prepare_query(left_variant.lsi_segments)
        prepare_lsi_sec = time.perf_counter() - prepare_lsi_start

        prepare_map1_start = time.perf_counter()
        map1_in_map0 = app.base.prepare_planar_map_point_location_2d_optix(
            left_variant.cdb_segments,
            query_map_id=1,
            scale_bounds=bounds,
        )
        prepare_map1_sec = time.perf_counter() - prepare_map1_start

        args = SimpleNamespace(**vars(args_template))
        setattr(args, "_preloaded_left", left_variant)
        setattr(args, "_preloaded_right", right)
        setattr(args, "_preloaded_bounds", bounds)
        setattr(args, "_prepared_lsi_session", lsi)
        setattr(args, "_prepared_lsi_query", query)
        setattr(args, "_prepared_point_location_map0_in_map1", map0_in_map1)
        setattr(args, "_prepared_point_location_map1_in_map0", map1_in_map0)
        if shared_right_query_points is not None:
            setattr(args, "_prepared_vertex_points_map1_in_map0", shared_right_query_points)
        setattr(args, "_prepared_operator_session_active", True)

        run_start = time.perf_counter()
        summary = app.run_pipeline(args)
        run_elapsed = time.perf_counter() - run_start
        compact = _compact_overlay_summary(summary)
        total_body = float(prepare_lsi_sec + prepare_map1_sec + compact["writer_free_hot_sec"])
        return {
            "label": label,
            "prepare_lsi_query_sec": float(prepare_lsi_sec),
            "prepare_left_point_location_sec": float(prepare_map1_sec),
            "run_pipeline_elapsed_sec": float(run_elapsed),
            "writer_free_hot_sec_excluding_external_prepares": compact["writer_free_hot_sec"],
            "total_body_sec_including_query_prepares": total_body,
            "summary_compact": compact,
            "shared_right_query_points_used": shared_right_query_points is not None,
        }
    finally:
        if map1_in_map0 is not None:
            map1_in_map0.close()
        if query is not None:
            query.close()


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
        "schema": "rtdl.goal5009.distinct_query_many_overlay_probe.v1",
        "left": str(args.left),
        "right": str(args.right),
        "capacity": int(args.capacity),
        "regime_under_test": "prepared_base_same_scale_domain_distinct_query_batches_full_binary_overlay_body",
    }

    load_start = time.perf_counter()
    left = base.load_dataset_arrays(args.left)
    right = base.load_dataset_arrays(args.right)
    result["load_dataset_arrays_sec"] = float(time.perf_counter() - load_start)
    bounds = base.shared_bounds(left, right)
    result["shared_bounds"] = [float(value) for value in bounds]

    map0_query_map_id = 0
    lsi = map0_in_map1 = bootstrap_locator = shared_right_query_points = None
    try:
        prepare_start = time.perf_counter()
        lsi = base.prepare_planar_map_lsi_2d_optix(right.lsi_segments)
        map0_in_map1 = base.prepare_planar_map_point_location_2d_optix(
            right.cdb_segments,
            query_map_id=map0_query_map_id,
            scale_bounds=bounds,
        )
        result["prepare_base_sessions_sec"] = float(time.perf_counter() - prepare_start)

        args_template = _build_run_args(args.left, args.right, args.capacity)
        variants = []
        for batch_id in (1, 2, 3):
            variant_start = time.perf_counter()
            variant, changed_points = _make_distinct_dataset_variant(app, left, batch_id=batch_id)
            variant_build_sec = time.perf_counter() - variant_start
            variants.append((batch_id, variant, changed_points, variant_build_sec))

        # Prepare the constant right-vertex query point batch once.  Goal5011
        # showed this handle is valid across same-domain point-location
        # locators.  Keep the bootstrap locator alive for conservative lifetime.
        bootstrap_start = time.perf_counter()
        bootstrap_locator = base.prepare_planar_map_point_location_2d_optix(
            variants[0][1].cdb_segments,
            query_map_id=1,
            scale_bounds=bounds,
        )
        result["bootstrap_right_query_points_locator_prepare_sec"] = float(time.perf_counter() - bootstrap_start)
        shared_points_start = time.perf_counter()
        shared_right_query_points = bootstrap_locator.prepare_query_points(right.points)
        result["shared_right_query_points_prepare_sec"] = float(time.perf_counter() - shared_points_start)

        query_results = []
        for batch_id, variant, changed_points, variant_build_sec in variants:
            row = _run_overlay_query(
                app,
                args_template=args_template,
                right=right,
                bounds=bounds,
                lsi=lsi,
                map0_in_map1=map0_in_map1,
                left_variant=variant,
                label=f"distinct_same_domain_overlay_query_{batch_id}",
                shared_right_query_points=shared_right_query_points,
            )
            row["variant_build_sec_not_in_body"] = float(variant_build_sec)
            row["changed_point_count"] = len(changed_points)
            query_results.append(row)
            gc.collect()
        result["query_results"] = query_results
        result["decision_inputs"] = {
            "distinct_query_count": len(query_results),
            "total_body_sec": [row["total_body_sec_including_query_prepares"] for row in query_results],
            "writer_free_hot_sec_excluding_external_prepares": [
                row["writer_free_hot_sec_excluding_external_prepares"] for row in query_results
            ],
            "lsi_row_counts": [row["summary_compact"]["lsi_row_count"] for row in query_results],
            "descriptor_pair_counts": [row["summary_compact"]["descriptor_pair_count"] for row in query_results],
        }
    finally:
        if shared_right_query_points is not None:
            shared_right_query_points.close()
        if bootstrap_locator is not None:
            bootstrap_locator.close()
        if map0_in_map1 is not None:
            map0_in_map1.close()
        if lsi is not None:
            lsi.close()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
