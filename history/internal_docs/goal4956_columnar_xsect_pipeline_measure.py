#!/usr/bin/env python3
"""Goal4956 columnar xsect pipeline measurement.

This internal measurement script keeps RTDL core generic and RayJoin as an app.
It continues the Goal4954/4955 numeric binary route, but removes a larger
Python-object boundary:

    LSI pair ids -> columnar numeric xsect arrays -> NumPy sort/group metadata

instead of:

    LSI pair ids -> Python OverlayIntersection objects -> Python object sort

The exact paper text route remains separate.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import goal4954b_writer_free_binary_overlay_measure as b  # noqa: E402
import goal4954e_numeric_binary_route_measure as e  # noqa: E402
import goal4955_projected_descriptor_pipeline_measure as p  # noqa: E402

base = b.base


def _trunc_div2_array(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.int64)
    return np.where(values >= 0, values // 2, -((-values) // 2)).astype(np.int64, copy=False)


def numeric_xsect_columns_from_pairs(pairs, left, right, *, scale_bounds):
    pairs = np.asarray(pairs, dtype=np.uint32).reshape((-1, 2))
    left_index = pairs[:, 0].astype(np.int64, copy=False) - 1
    right_index = pairs[:, 1].astype(np.int64, copy=False) - 1

    lx0 = left.x0[left_index]
    ly0 = left.y0[left_index]
    lx1 = left.x1[left_index]
    ly1 = left.y1[left_index]
    rx0 = right.x0[right_index]
    ry0 = right.y0[right_index]
    rx1 = right.x1[right_index]
    ry1 = right.y1[right_index]

    ldx = lx1 - lx0
    ldy = ly1 - ly0
    rdx = rx1 - rx0
    rdy = ry1 - ry0
    denom = ldx * rdy - ldy * rdx
    qpx = rx0 - lx0
    qpy = ry0 - ly0
    with np.errstate(divide="ignore", invalid="ignore"):
        t = (qpx * rdy - qpy * rdx) / denom
        world_x = lx0 + t * ldx
        world_y = ly0 + t * ldy

    fallback_x, fallback_y = base._overlap_midpoint_fallback(lx0, ly0, lx1, ly1, rx0, ry0, rx1, ry1)
    invalid = ~np.isfinite(world_x) | ~np.isfinite(world_y) | (np.abs(denom) <= 0.0)
    if np.any(invalid):
        world_x = world_x.copy()
        world_y = world_y.copy()
        world_x[invalid] = fallback_x[invalid]
        world_y[invalid] = fallback_y[invalid]

    rx_scale, ry_scale, deltax, deltay, *_ = base._rayjoin_scaling_constants(scale_bounds)
    scaled_x = base._scale_array(world_x, rx_scale, deltax).astype(np.int64, copy=False)
    scaled_y = base._scale_array(world_y, ry_scale, deltay).astype(np.int64, copy=False)

    return {
        "eid0": left_index.astype(np.int64, copy=False),
        "eid1": right_index.astype(np.int64, copy=False),
        "display_x": np.asarray(world_x, dtype=np.float64),
        "display_y": np.asarray(world_y, dtype=np.float64),
        "scaled_x": scaled_x,
        "scaled_y": scaled_y,
    }


def sort_xsect_indices_for_map(columns, dataset, map_index: int, scale_bounds):
    edge_ids = columns["eid0"] if map_index == 0 else columns["eid1"]
    tie_ids = columns["eid1"] if map_index == 0 else columns["eid0"]
    rx_scale, ry_scale, deltax, deltay, *_ = base._rayjoin_scaling_constants(scale_bounds)
    start_sx = base._scale_array(dataset.x0[edge_ids], rx_scale, deltax).astype(np.int64, copy=False)
    start_sy = base._scale_array(dataset.y0[edge_ids], ry_scale, deltay).astype(np.int64, copy=False)
    # Scaled coordinates may be around 1e13; squaring them in int64 silently
    # overflows and changes the author/object-route order.  Use extended
    # floating precision for the ordering distance while keeping ids integer.
    dx = (columns["scaled_x"] - start_sx).astype(np.longdouble, copy=False)
    dy = (columns["scaled_y"] - start_sy).astype(np.longdouble, copy=False)
    dist = dx * dx + dy * dy
    # Python's per-edge ``list.sort(key=(dist, tie))`` is stable. Preserve that
    # final tie behavior explicitly so the columnar route remains semantically
    # equivalent to the object route on degenerate equal-distance/equal-tie
    # events.
    original_index = np.arange(edge_ids.shape[0], dtype=np.int64)
    order = np.lexsort((original_index, tie_ids, dist, edge_ids)).astype(np.int64, copy=False)
    sorted_edges = edge_ids[order]
    return {
        "order": order,
        "edge_ids": sorted_edges,
        "run_start": _run_start_table(sorted_edges, dataset.edge_count),
        "run_end": _run_end_table(sorted_edges, dataset.edge_count),
    }


def _run_start_table(sorted_edges: np.ndarray, edge_count: int) -> np.ndarray:
    starts = np.full(int(edge_count), -1, dtype=np.int64)
    if sorted_edges.size == 0:
        return starts
    change = np.empty(sorted_edges.size, dtype=np.bool_)
    change[0] = True
    change[1:] = sorted_edges[1:] != sorted_edges[:-1]
    positions = np.nonzero(change)[0]
    starts[sorted_edges[positions].astype(np.int64)] = positions.astype(np.int64)
    return starts


def _run_end_table(sorted_edges: np.ndarray, edge_count: int) -> np.ndarray:
    ends = np.full(int(edge_count), -1, dtype=np.int64)
    if sorted_edges.size == 0:
        return ends
    change = np.empty(sorted_edges.size, dtype=np.bool_)
    change[:-1] = sorted_edges[1:] != sorted_edges[:-1]
    change[-1] = True
    positions = np.nonzero(change)[0]
    ends[sorted_edges[positions].astype(np.int64)] = (positions + 1).astype(np.int64)
    return ends


def midpoint_points_columnar(columns, sorted_view, side_id: int, *, scale_bounds):
    order = sorted_view["order"]
    edges = sorted_view["edge_ids"]
    if order.size <= 1:
        return base.pack_rayjoin_cdb_scaled_points(
            ids=np.asarray([], dtype=np.int64),
            x=np.asarray([], dtype=np.float64),
            y=np.asarray([], dtype=np.float64),
            sx=np.asarray([], dtype=np.int64),
            sy=np.asarray([], dtype=np.int64),
        ), np.asarray([], dtype=np.int64), 0

    same_edge = edges[1:] == edges[:-1]
    left_owner_positions = np.nonzero(same_edge)[0]
    owners = order[left_owner_positions]
    right_neighbors = order[left_owner_positions + 1]
    sx = _trunc_div2_array(columns["scaled_x"][owners] + columns["scaled_x"][right_neighbors])
    sy = _trunc_div2_array(columns["scaled_y"][owners] + columns["scaled_y"][right_neighbors])
    *_, rrx, rry, ddeltax, ddeltay = base._rayjoin_scaling_constants(scale_bounds)
    mx = sx.astype(np.float64) * float(rrx) + float(ddeltax)
    my = sy.astype(np.float64) * float(rry) + float(ddeltay)
    finite = np.isfinite(mx) & np.isfinite(my)
    if not np.all(finite):
        owners = owners[finite]
        sx = sx[finite]
        sy = sy[finite]
        mx = mx[finite]
        my = my[finite]
    ids = np.arange(1, owners.size + 1, dtype=np.int64)
    packed = base.pack_rayjoin_cdb_scaled_points(ids=ids, x=mx, y=my, sx=sx, sy=sy)
    return packed, owners.astype(np.int64, copy=False), int(owners.size)


def build_projected_descriptor_carrier_columnar(datasets, columns, sorted_views, point_faces, midpoint_faces):
    group_offset = []
    group_length = []
    label_a = []
    label_b = []
    skipped_group_count = 0
    projected_point_payload_rows = 0

    def flush(display_points, left_label, right_label, other_label):
        nonlocal skipped_group_count, projected_point_payload_rows
        if not display_points:
            return
        keep = int(left_label) * int(other_label) != 0 or int(right_label) * int(other_label) != 0
        if not keep:
            skipped_group_count += 1
            display_points.clear()
            return
        length = p._dedupe_consecutive_point_count(display_points)
        group_offset.append(projected_point_payload_rows)
        group_length.append(length)
        label_a.append(int(left_label))
        label_b.append(int(other_label))
        projected_point_payload_rows += length
        display_points.clear()

    for side_id, dataset in enumerate(datasets):
        view = sorted_views[side_id]
        order = view["order"]
        starts = view["run_start"]
        ends = view["run_end"]
        edge_id = 0
        for chain_index in range(dataset.chain_count):
            point_offset = int(dataset.chain_offsets[chain_index])
            point_count = int(dataset.chain_point_counts[chain_index])
            display_points: list[tuple[float, float]] = []
            left_label = int(dataset.chain_left_faces[chain_index])
            right_label = int(dataset.chain_right_faces[chain_index])
            other_label = 0

            for local_point_index in range(point_count):
                point_index = point_offset + local_point_index
                other_label = int(point_faces[side_id][point_index])
                display_points.append((float(dataset.point_x[point_index]), float(dataset.point_y[point_index])))

                if local_point_index == point_count - 1:
                    continue

                run_start = int(starts[edge_id]) if edge_id < starts.size else -1
                run_end = int(ends[edge_id]) if edge_id < ends.size else -1
                if run_start >= 0 and run_end > run_start:
                    first = int(order[run_start])
                    display_points.append((float(columns["display_x"][first]), float(columns["display_y"][first])))
                    for sorted_pos in range(run_start, run_end - 1):
                        xsect_index = int(order[sorted_pos])
                        next_index = int(order[sorted_pos + 1])
                        flush(display_points, left_label, right_label, other_label)
                        other_label = int(midpoint_faces[side_id][xsect_index])
                        display_points.append(
                            (float(columns["display_x"][xsect_index]), float(columns["display_y"][xsect_index]))
                        )
                        display_points.append(
                            (float(columns["display_x"][next_index]), float(columns["display_y"][next_index]))
                        )
                    flush(display_points, left_label, right_label, other_label)
                    last = int(order[run_end - 1])
                    display_points.append((float(columns["display_x"][last]), float(columns["display_y"][last])))
                edge_id += 1

            flush(display_points, left_label, right_label, other_label)

    carrier = {
        "group_offset": np.asarray(group_offset, dtype=np.int64),
        "group_length": np.asarray(group_length, dtype=np.int64),
        "label_a": np.asarray(label_a, dtype=np.int64),
        "label_b": np.asarray(label_b, dtype=np.int64),
    }
    stats = {
        "schema": "rtdl.internal.goal4956.columnar_xsect_projected_descriptor_carrier.v1",
        "group_count": int(carrier["group_offset"].size),
        "point_row_count": int(carrier["group_length"].sum()),
        "skipped_group_count": int(skipped_group_count),
        "full_geometry_payload_columns_materialized": False,
        "transient_display_point_tuples_used_for_dedupe_count": True,
        "projected_out_columns": ("x", "y", "alt_label", "source_side_id", "source_element_id"),
        "projection_pushdown": True,
        "columnar_xsect_arrays": True,
    }
    return carrier, stats


def run_pipeline(args):
    if "rtdsl.rayjoin_overlay" in sys.modules:
        raise RuntimeError("forbidden import detected: rtdsl.rayjoin_overlay")

    phase_seconds = {}
    native_point_location_timings = {}
    left = b.timed("load_pack_left_sec", lambda: base.load_dataset_arrays(Path(args.left)), phase_seconds)
    right = b.timed("load_pack_right_sec", lambda: base.load_dataset_arrays(Path(args.right)), phase_seconds)
    bounds = b.timed("shared_bounds_sec", lambda: base.shared_bounds(left, right), phase_seconds)
    pairs = b.timed("lsi_public_rows_sec", lambda: b.run_lsi(left, right), phase_seconds)
    columns = b.timed(
        "intersection_reprojection_columnar_sec",
        lambda: numeric_xsect_columns_from_pairs(pairs, left, right, scale_bounds=bounds),
        phase_seconds,
    )
    sorted0 = b.timed(
        "sort_map0_columnar_sec",
        lambda: sort_xsect_indices_for_map(columns, left, 0, bounds),
        phase_seconds,
    )
    sorted1 = b.timed(
        "sort_map1_columnar_sec",
        lambda: sort_xsect_indices_for_map(columns, right, 1, bounds),
        phase_seconds,
    )

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

        midpoint_faces = [
            np.zeros(int(pairs.shape[0]), dtype=np.uint32),
            np.zeros(int(pairs.shape[0]), dtype=np.uint32),
        ]
        for side_id, locator, sorted_view in ((0, map0_in_map1, sorted0), (1, map1_in_map0, sorted1)):
            scaled_points, owners, midpoint_count = b.timed(
                f"midpoint_points_map{side_id}_columnar_sec",
                lambda sorted_view=sorted_view, side_id=side_id: midpoint_points_columnar(
                    columns,
                    sorted_view,
                    side_id,
                    scale_bounds=bounds,
                ),
                phase_seconds,
            )
            faces = b.timed(
                f"midpoint_pip_map{side_id}_sec",
                lambda locator=locator, scaled_points=scaled_points, count=midpoint_count: base.run_point_location(
                    locator,
                    scaled_points,
                    count,
                ),
                phase_seconds,
            )
            native_point_location_timings[f"midpoint_pip_map{side_id}"] = locator.last_phase_timings() or {}
            b.timed(
                f"assign_midpoint_faces_map{side_id}_columnar_sec",
                lambda side_id=side_id, owners=owners, faces=faces: midpoint_faces[side_id].__setitem__(
                    owners,
                    faces.astype(np.uint32, copy=False),
                ),
                phase_seconds,
            )
    finally:
        b.timed("destroy_point_location_sessions_sec", lambda: (map0_in_map1.close(), map1_in_map0.close()), phase_seconds)

    carrier, carrier_stats = b.timed(
        "grouped_columnar_carrier_construction_sec",
        lambda: build_projected_descriptor_carrier_columnar(
            (left, right),
            columns,
            (sorted0, sorted1),
            (point_faces0, point_faces1),
            midpoint_faces,
        ),
        phase_seconds,
    )
    consumer = b.timed(
        "grouped_descriptor_pair_count_consumer_sec",
        lambda: p.descriptor_pair_count_projected(carrier),
        phase_seconds,
    )

    writer_free_hot_keys = [
        "lsi_public_rows_sec",
        "intersection_reprojection_columnar_sec",
        "sort_map0_columnar_sec",
        "sort_map1_columnar_sec",
        "vertex_pip_map0_in_map1_sec",
        "vertex_pip_map1_in_map0_sec",
        "midpoint_points_map0_columnar_sec",
        "midpoint_points_map1_columnar_sec",
        "midpoint_pip_map0_sec",
        "midpoint_pip_map1_sec",
        "assign_midpoint_faces_map0_columnar_sec",
        "assign_midpoint_faces_map1_columnar_sec",
        "grouped_columnar_carrier_construction_sec",
        "grouped_descriptor_pair_count_consumer_sec",
    ]
    writer_free_hot_sec = sum(float(phase_seconds.get(key, 0.0)) for key in writer_free_hot_keys)
    ratio = None
    if args.author_overlay_compute_sec and args.author_overlay_compute_sec > 0:
        ratio = writer_free_hot_sec / args.author_overlay_compute_sec
    return {
        "schema": "rtdl.internal.goal4956.columnar_xsect_pipeline_measure.v1",
        "pair_name": args.pair_name,
        "route": "columnar_xsect_numeric_binary_descriptor_route_public_lsi_pip_numba_consumer",
        "claim_boundary": {
            "numeric_binary_route": True,
            "projection_pushdown": True,
            "columnar_xsect_arrays": True,
            "full_carrier_geometry_payload_columns_materialized": False,
            "transient_display_point_tuples_used_for_dedupe_count": True,
            "paper_byte_equal_route": False,
            "paper_exact_sink_separate": True,
            "layer4_fusion": False,
            "public_high_performance_claim_authorized": False,
            "paper_byte_equality_claim_authorized_for_numeric_route": False,
            "layer4_claim_authorized": False,
            "rtdl_core_change": False,
            "rayjoin_specific_core_primitive": False,
            "bundled_rayjoin_overlay_imported": False,
            "rayjoin_app_adapter_used": True,
            "generic_contract_goal": True,
            "implementation_change": "internal_app_owned_measurement_script_only",
        },
        "left": {"path": left.path, "chains": left.chain_count, "points": left.point_count, "edges": left.edge_count},
        "right": {"path": right.path, "chains": right.chain_count, "points": right.point_count, "edges": right.edge_count},
        "scale_bounds": bounds,
        "lsi_row_count": int(pairs.shape[0]),
        "xsect_sorted_counts": {"side0": int(sorted0["order"].size), "side1": int(sorted1["order"].size)},
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
    parser.add_argument("--no-numba-warmup", action="store_true")
    args = parser.parse_args()

    if args.cache_dir:
        import os

        old_cache_dir = os.environ.get("RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR")
        os.environ["RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR"] = str(Path(args.cache_dir))
    else:
        old_cache_dir = None
    try:
        if not args.no_numba_warmup:
            p._warm_numba()
        summary = run_pipeline(args)
    finally:
        if args.cache_dir:
            import os

            if old_cache_dir is None:
                os.environ.pop("RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR", None)
            else:
                os.environ["RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR"] = old_cache_dir

    Path(args.summary).write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
