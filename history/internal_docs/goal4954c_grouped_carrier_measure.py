#!/usr/bin/env python3
"""Goal4954-C grouped carrier measurement.

This internal prototype keeps the Goal4954-B geometry pipeline unchanged and
only replaces the flat repeated-label binary row representation with a grouped
columnar carrier:

group-level columns:
  group_offset, group_length, label_a, label_b, alt_label, source_side_id,
  source_element_id

point-level columns:
  x, y

No RTDL core/runtime code is changed by this script.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import goal4954b_writer_free_binary_overlay_measure as b  # noqa: E402

base = b.base


def build_grouped_columnar_carrier(datasets, xsects_sorted, point_faces):
    """Build a grouped columnar carrier without repeating labels per point."""

    group_offset = []
    group_length = []
    label_a = []
    label_b = []
    alt_label = []
    source_side_id = []
    source_element_id = []
    point_x = []
    point_y = []
    skipped_group_count = 0

    def flush(points, display_points, left_label, right_label, other_label, side_id, element_id):
        nonlocal skipped_group_count
        if not points:
            return
        keep = int(left_label) * int(other_label) != 0 or int(right_label) * int(other_label) != 0
        if not keep:
            skipped_group_count += 1
            points.clear()
            display_points.clear()
            return

        _deduped_points, deduped_display = base.dedupe_point_pairs(points, display_points)
        offset = len(point_x)
        length = len(deduped_display)
        group_offset.append(offset)
        group_length.append(length)
        label_a.append(int(left_label))
        label_b.append(int(other_label))
        alt_label.append(int(right_label))
        source_side_id.append(int(side_id))
        source_element_id.append(int(element_id))
        for x, y in deduped_display:
            point_x.append(float(x))
            point_y.append(float(y))
        points.clear()
        display_points.clear()

    for side_id, dataset in enumerate(datasets):
        edge_attr = "eid0" if side_id == 0 else "eid1"
        grouped = defaultdict(list)
        for xsect in xsects_sorted[side_id]:
            grouped[int(getattr(xsect, edge_attr))].append(xsect)

        edge_id = 0
        for chain_index in range(dataset.chain_count):
            point_offset = int(dataset.chain_offsets[chain_index])
            point_count = int(dataset.chain_point_counts[chain_index])
            points = []
            display_points = []
            left_label = int(dataset.chain_left_faces[chain_index])
            right_label = int(dataset.chain_right_faces[chain_index])
            other_label = 0

            for local_point_index in range(point_count):
                point_index = point_offset + local_point_index
                other_label = int(point_faces[side_id][point_index])
                px = float(dataset.point_x[point_index])
                py = float(dataset.point_y[point_index])
                points.append((px, py))
                display_points.append((px, py))

                if local_point_index == point_count - 1:
                    continue

                xsects = grouped.get(edge_id)
                if xsects:
                    first_point = base.xsect_output_point(xsects[0])
                    points.append(first_point)
                    display_points.append(first_point)
                    for xsect, next_xsect in zip(xsects, xsects[1:]):
                        flush(
                            points,
                            display_points,
                            left_label,
                            right_label,
                            other_label,
                            side_id,
                            edge_id,
                        )
                        other_label = base.midpoint_face_for_map(xsect, side_id)
                        xsect_point = base.xsect_output_point(xsect)
                        next_xsect_point = base.xsect_output_point(next_xsect)
                        points.append(xsect_point)
                        display_points.append(xsect_point)
                        points.append(next_xsect_point)
                        display_points.append(next_xsect_point)
                    flush(
                        points,
                        display_points,
                        left_label,
                        right_label,
                        other_label,
                        side_id,
                        edge_id,
                    )
                    last_point = base.xsect_output_point(xsects[-1])
                    points.append(last_point)
                    display_points.append(last_point)
                edge_id += 1

            flush(
                points,
                display_points,
                left_label,
                right_label,
                other_label,
                side_id,
                max(edge_id - 1, 0),
            )

    carrier = {
        "group_offset": np.asarray(group_offset, dtype=np.int64),
        "group_length": np.asarray(group_length, dtype=np.int64),
        "label_a": np.asarray(label_a, dtype=np.int64),
        "label_b": np.asarray(label_b, dtype=np.int64),
        "alt_label": np.asarray(alt_label, dtype=np.int64),
        "source_side_id": np.asarray(source_side_id, dtype=np.int32),
        "source_element_id": np.asarray(source_element_id, dtype=np.int64),
        "x": np.asarray(point_x, dtype=np.float64),
        "y": np.asarray(point_y, dtype=np.float64),
    }
    stats = {
        "group_count": int(carrier["group_offset"].size),
        "point_row_count": int(carrier["x"].size),
        "skipped_group_count": int(skipped_group_count),
    }
    return carrier, stats


def descriptor_pair_count_grouped(carrier):
    if carrier["label_a"].size == 0:
        return {
            "pair_count": 0,
            "total_groups": 0,
            "total_point_rows": 0,
            "top_pairs_by_point_rows": [],
        }
    pairs = np.column_stack((carrier["label_a"], carrier["label_b"]))
    unique_pairs, inverse = np.unique(pairs, axis=0, return_inverse=True)
    group_counts = np.bincount(inverse)
    point_counts = np.bincount(inverse, weights=carrier["group_length"]).astype(np.int64, copy=False)
    order = np.argsort(point_counts)[::-1]
    top = [
        {
            "label_a": int(unique_pairs[index, 0]),
            "label_b": int(unique_pairs[index, 1]),
            "group_count": int(group_counts[index]),
            "point_row_count": int(point_counts[index]),
        }
        for index in order[:10]
    ]
    return {
        "pair_count": int(unique_pairs.shape[0]),
        "total_groups": int(carrier["label_a"].size),
        "total_point_rows": int(carrier["group_length"].sum()),
        "top_pairs_by_point_rows": top,
    }


def run_pipeline(args):
    if "rtdsl.rayjoin_overlay" in sys.modules:
        raise RuntimeError("forbidden import detected: rtdsl.rayjoin_overlay")

    old_cache_dir = os.environ.get("RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR")
    if args.cache_dir:
        os.environ["RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR"] = str(Path(args.cache_dir))

    total_start = time.perf_counter()
    phase_seconds = {}
    native_point_location_timings = {}

    try:
        left = b.timed("load_pack_left_sec", lambda: base.load_dataset_arrays(Path(args.left)), phase_seconds)
        right = b.timed("load_pack_right_sec", lambda: base.load_dataset_arrays(Path(args.right)), phase_seconds)
    finally:
        if args.cache_dir:
            if old_cache_dir is None:
                os.environ.pop("RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR", None)
            else:
                os.environ["RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR"] = old_cache_dir

    bounds = b.timed("shared_bounds_sec", lambda: base.shared_bounds(left, right), phase_seconds)
    pairs = b.timed("lsi_public_rows_sec", lambda: b.run_lsi(left, right), phase_seconds)
    xsects = b.timed(
        "intersection_reprojection_sec",
        lambda: base.intersection_rows_from_pairs(pairs, left, right, scale_bounds=bounds),
        phase_seconds,
    )
    xsects0 = b.timed("sort_map0_sec", lambda: base.sort_xsects_for_map(list(xsects), left, 0, bounds), phase_seconds)
    xsects1 = b.timed("sort_map1_sec", lambda: base.sort_xsects_for_map(list(xsects), right, 1, bounds), phase_seconds)

    map0_query_map_id = 1 if args.swap_query_map_ids else 0
    map1_query_map_id = 0 if args.swap_query_map_ids else 1
    map0_in_map1 = b.timed(
        "prepare_point_location_map0_in_map1_sec",
        lambda: base.prepare_planar_map_point_location_2d_optix(
            right.cdb_segments,
            query_map_id=map0_query_map_id,
            scale_bounds=bounds,
        ),
        phase_seconds,
    )
    map1_in_map0 = b.timed(
        "prepare_point_location_map1_in_map0_sec",
        lambda: base.prepare_planar_map_point_location_2d_optix(
            left.cdb_segments,
            query_map_id=map1_query_map_id,
            scale_bounds=bounds,
        ),
        phase_seconds,
    )

    try:
        point_faces0 = b.timed(
            "vertex_pip_map0_in_map1_sec",
            lambda: base.run_point_location(map0_in_map1, left.points, left.point_count),
            phase_seconds,
        )
        native_point_location_timings["vertex_pip_map0_in_map1"] = map0_in_map1.last_phase_timings() or {}
        point_faces1 = b.timed(
            "vertex_pip_map1_in_map0_sec",
            lambda: base.run_point_location(map1_in_map0, right.points, right.point_count),
            phase_seconds,
        )
        native_point_location_timings["vertex_pip_map1_in_map0"] = map1_in_map0.last_phase_timings() or {}

        for side_id, locator, sorted_rows in ((0, map0_in_map1, xsects0), (1, map1_in_map0, xsects1)):
            midpoints, scaled_midpoints, owners = b.timed(
                f"midpoint_points_map{side_id}_sec",
                lambda sorted_rows=sorted_rows, side_id=side_id: base.midpoint_points(
                    sorted_rows,
                    side_id,
                    scale_bounds=bounds,
                ),
                phase_seconds,
            )

            def pack_midpoint_points():
                ids = np.arange(1, len(midpoints) + 1, dtype=np.int64)
                mx = np.fromiter((p[0] for p in midpoints), dtype=np.float64, count=len(midpoints))
                my = np.fromiter((p[1] for p in midpoints), dtype=np.float64, count=len(midpoints))
                sx = np.fromiter((p[0] for p in scaled_midpoints), dtype=np.int64, count=len(scaled_midpoints))
                sy = np.fromiter((p[1] for p in scaled_midpoints), dtype=np.int64, count=len(scaled_midpoints))
                return base.pack_rayjoin_cdb_scaled_points(ids=ids, x=mx, y=my, sx=sx, sy=sy)

            scaled_points = b.timed(f"pack_midpoint_points_map{side_id}_sec", pack_midpoint_points, phase_seconds)
            faces = b.timed(
                f"midpoint_pip_map{side_id}_sec",
                lambda locator=locator, scaled_points=scaled_points, count=len(midpoints): base.run_point_location(
                    locator,
                    scaled_points,
                    count,
                ),
                phase_seconds,
            )
            native_point_location_timings[f"midpoint_pip_map{side_id}"] = locator.last_phase_timings() or {}
            b.timed(
                f"assign_midpoint_faces_map{side_id}_sec",
                lambda owners=owners, faces=faces, side_id=side_id: base.assign_midpoint_faces(
                    owners,
                    faces,
                    side_id,
                ),
                phase_seconds,
            )
    finally:
        b.timed(
            "destroy_point_location_sessions_sec",
            lambda: (map0_in_map1.close(), map1_in_map0.close()),
            phase_seconds,
        )

    carrier, carrier_stats = b.timed(
        "grouped_columnar_carrier_construction_sec",
        lambda: build_grouped_columnar_carrier((left, right), (xsects0, xsects1), (point_faces0, point_faces1)),
        phase_seconds,
    )
    consumer = b.timed(
        "grouped_descriptor_pair_count_consumer_sec",
        lambda: descriptor_pair_count_grouped(carrier),
        phase_seconds,
    )

    writer_free_hot_keys = [
        "lsi_public_rows_sec",
        "intersection_reprojection_sec",
        "sort_map0_sec",
        "sort_map1_sec",
        "vertex_pip_map0_in_map1_sec",
        "vertex_pip_map1_in_map0_sec",
        "midpoint_points_map0_sec",
        "midpoint_points_map1_sec",
        "pack_midpoint_points_map0_sec",
        "pack_midpoint_points_map1_sec",
        "midpoint_pip_map0_sec",
        "midpoint_pip_map1_sec",
        "assign_midpoint_faces_map0_sec",
        "assign_midpoint_faces_map1_sec",
        "grouped_columnar_carrier_construction_sec",
        "grouped_descriptor_pair_count_consumer_sec",
    ]
    writer_free_hot_sec = sum(float(phase_seconds.get(key, 0.0)) for key in writer_free_hot_keys)
    ratio = None
    if args.author_overlay_compute_sec and args.author_overlay_compute_sec > 0:
        ratio = writer_free_hot_sec / args.author_overlay_compute_sec

    return {
        "schema": "rtdl.internal.goal4954c.grouped_carrier_measure.v1",
        "pair_name": args.pair_name,
        "route": "public_planar_map_lsi_point_location_plus_app_owned_grouped_columnar_carrier",
        "claim_boundary": {
            "measurement_only": False,
            "prototype_only": True,
            "implementation_change": "internal_app_owned_measurement_script_only",
            "rtdl_core_change": False,
            "paper_text_writer_in_binary_metric": False,
            "bundled_rayjoin_overlay_imported": False,
            "generic_contract_goal": True,
            "rayjoin_app_adapter_used": True,
            "layer4_fusion": False,
        },
        "left": {"path": left.path, "chains": left.chain_count, "points": left.point_count, "edges": left.edge_count},
        "right": {"path": right.path, "chains": right.chain_count, "points": right.point_count, "edges": right.edge_count},
        "scale_bounds": bounds,
        "lsi_row_count": int(pairs.shape[0]),
        "xsect_sorted_counts": {"side0": len(xsects0), "side1": len(xsects1)},
        "vertex_positive_counts": {
            "side0_in_side1": int(np.count_nonzero(point_faces0)),
            "side1_in_side0": int(np.count_nonzero(point_faces1)),
        },
        "grouped_carrier": carrier_stats,
        "downstream_consumer": consumer,
        "phase_seconds": phase_seconds,
        "native_point_location_timings": native_point_location_timings,
        "writer_free_hot_keys": writer_free_hot_keys,
        "writer_free_hot_sec": writer_free_hot_sec,
        "author_overlay_compute_sec": args.author_overlay_compute_sec,
        "writer_free_hot_vs_author_overlay_compute_ratio": ratio,
        "elapsed_sec": time.perf_counter() - total_start,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--pair-name", default="unnamed_pair")
    parser.add_argument("--author-overlay-compute-sec", type=float, default=None)
    parser.add_argument("--cache-dir", default=None)
    parser.add_argument("--swap-query-map-ids", action="store_true")
    args = parser.parse_args()

    summary = run_pipeline(args)
    Path(args.summary).write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
