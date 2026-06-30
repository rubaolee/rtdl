from __future__ import annotations

import argparse
import json
import math
import os
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

from rtdsl import rayjoin_overlay as overlay


def _load_packed_cache(path: Path):
    meta = json.loads((path / "meta.json").read_text(encoding="utf-8"))
    segments = np.load(path / "segments.npy", mmap_mode="r")
    cdb_segments = np.load(path / "cdb_segments.npy", mmap_mode="r")
    points = np.load(path / "points.npy", mmap_mode="r")
    return overlay._overlay_inputs_from_native_arrays(
        name=str(meta["name"]),
        chain_count=int(meta["chain_count"]),
        segment_array=segments,
        cdb_array=cdb_segments,
        point_array=points,
    )


def _scale_parameters(scale_bounds):
    min_x, max_x, min_y, max_y = (float(value) for value in scale_bounds)
    internal_max = (1 << 46) - 1
    internal_min = -(1 << 46)
    margin = 1.0
    box_max_x = max_x + margin
    box_min_x = min_x - margin
    box_max_y = max_y + margin
    box_min_y = min_y - margin
    internal_range = float(internal_max - internal_min)
    rx_scale = internal_range / (box_max_x - box_min_x)
    ry_scale = internal_range / (box_max_y - box_min_y)
    deltax = 0.5 * (float(internal_max + internal_min) - (box_max_x + box_min_x) * rx_scale)
    deltay = 0.5 * (float(internal_max + internal_min) - (box_max_y + box_min_y) * ry_scale)
    rrx = 1.0 / rx_scale
    rry = 1.0 / ry_scale
    ddeltax = 0.5 * ((box_max_x + box_min_x) - float(internal_max + internal_min) * rrx)
    ddeltay = 0.5 * ((box_max_y + box_min_y) - float(internal_max + internal_min) * rry)
    return rx_scale, ry_scale, deltax, deltay, rrx, rry, ddeltax, ddeltay


def _scale_value(value: float, scale: float, delta: float) -> int:
    return int(np.asarray([value], dtype=np.float64).astype(np.float64)[0] * scale + delta)


def _line_from_scaled(x0: int, y0: int, x1: int, y1: int):
    a = int(y0) - int(y1)
    b = int(x1) - int(x0)
    c = -(int(x0) * a) - (int(y0) * b)
    if b < 0:
        a = -a
        b = -b
        c = -c
    return a, b, c


def _scaled_segment(row, params):
    rx_scale, ry_scale, deltax, deltay, *_ = params
    return (
        _scale_value(float(row["x0"]), rx_scale, deltax),
        _scale_value(float(row["y0"]), ry_scale, deltay),
        _scale_value(float(row["x1"]), rx_scale, deltax),
        _scale_value(float(row["y1"]), ry_scale, deltay),
    )


def _exact_intersection(query_row, base_row, params):
    qx0, qy0, qx1, qy1 = _scaled_segment(query_row, params)
    bx0, by0, bx1, by1 = _scaled_segment(base_row, params)
    qa, qb, qc = _line_from_scaled(qx0, qy0, qx1, qy1)
    ba, bb, bc = _line_from_scaled(bx0, by0, bx1, by1)
    denom = qa * bb - ba * qb
    if denom == 0:
        return None
    x = Fraction(bc * qb - qc * bb, denom)
    y = Fraction(ba * qc - qa * bc, denom)
    min_x = min(qx0, qx1, bx0, bx1)
    max_x = max(qx0, qx1, bx0, bx1)
    min_y = min(qy0, qy1, by0, by1)
    max_y = max(qy0, qy1, by0, by1)
    x = max(Fraction(min_x, 1), min(Fraction(max_x, 1), x))
    y = max(Fraction(min_y, 1), min(Fraction(max_y, 1), y))
    return x, y


def _author_like_pip(point_x: Fraction, point_y: Fraction, base_cdb, params, query_map_id: int, chunk_size: int):
    best_y = math.inf
    best_index = None
    best = None
    top_candidates = []
    point_x_float = float(point_x)
    point_y_float = float(point_y)
    rx_scale, ry_scale, deltax, deltay, *_ = params
    for begin in range(0, int(base_cdb.size), chunk_size):
        chunk = base_cdb[begin : begin + chunk_size]
        sx0 = (chunk["x0"].astype(np.float64) * rx_scale + deltax).astype(np.int64)
        sx1 = (chunk["x1"].astype(np.float64) * rx_scale + deltax).astype(np.int64)
        x_min = np.minimum(sx0, sx1).astype(np.float64)
        x_max = np.maximum(sx0, sx1).astype(np.float64)
        excluded = np.where(query_map_id == 0, x_min, x_max)
        mask = (point_x_float >= x_min) & (point_x_float <= x_max) & (point_x_float != excluded)
        if not np.any(mask):
            continue
        local_indices = np.nonzero(mask)[0]
        for local in local_indices:
            row = chunk[int(local)]
            sx0_i, sy0_i, sx1_i, sy1_i = _scaled_segment(row, params)
            x_min_i = min(sx0_i, sx1_i)
            x_max_i = max(sx0_i, sx1_i)
            excluded_x = x_min_i if query_map_id == 0 else x_max_i
            if point_x < x_min_i or point_x > x_max_i or point_x == excluded_x:
                continue
            a, b, c = _line_from_scaled(sx0_i, sy0_i, sx1_i, sy1_i)
            if b == 0:
                continue
            # Author code casts the rational numerator to double before dividing by b.
            author_xsect_y = float(-a * point_x - c) / float(b)
            native_xsect_y = (-float(a) * point_x_float - float(c)) / float(b)
            diff_y = point_y_float - author_xsect_y
            if diff_y == 0.0:
                diff_y = -a if query_map_id == 0 else a
            if diff_y == 0.0:
                diff_y = -b if query_map_id == 0 else b
            if diff_y > 0.0:
                continue
            face_id = int(row["right_face_id"] if sx0_i < sx1_i else row["left_face_id"])
            slope = float(a) / float(b)
            candidate = {
                "array_index": int(begin + int(local)),
                "segment_id": int(row["id"]),
                "face_id": face_id,
                "left_face_id": int(row["left_face_id"]),
                "right_face_id": int(row["right_face_id"]),
                "sx0": int(sx0_i),
                "sy0": int(sy0_i),
                "sx1": int(sx1_i),
                "sy1": int(sy1_i),
                "a": int(a),
                "b": int(b),
                "c": int(c),
                "author_xsect_y": float(author_xsect_y),
                "native_xsect_y_formula": float(native_xsect_y),
                "xsect_y_delta_native_minus_author": float(native_xsect_y - author_xsect_y),
                "diff_y_author": float(diff_y),
                "slope": float(slope),
            }
            top_candidates.append(candidate)
            if len(top_candidates) > 32:
                top_candidates.sort(key=lambda item: (item["author_xsect_y"], item["segment_id"]))
                del top_candidates[16:]
            if author_xsect_y > best_y:
                continue
            if author_xsect_y == best_y and best is not None:
                current_slope_gt = slope > best["slope"]
                if (query_map_id and not current_slope_gt) or (current_slope_gt and not query_map_id):
                    continue
            best_y = author_xsect_y
            global_index = begin + int(local)
            best_index = global_index
            best = candidate
    top_candidates.sort(key=lambda item: (item["author_xsect_y"], item["segment_id"]))
    return best_index, best, top_candidates[:16]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-root", required=True)
    parser.add_argument("--left-cache-name", default="dtl_cnty_Point")
    parser.add_argument("--right-cache-name", default="USAZIPCodeArea_Point")
    parser.add_argument("--target-map-index", type=int, default=0)
    parser.add_argument("--target-query-eid", type=int, default=14149)
    parser.add_argument("--target-owner-base-eid", type=int, default=8959129)
    parser.add_argument("--chunk-size", type=int, default=1_000_000)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()

    root = Path(args.cache_root)
    left_cache = next(root.glob(f"{args.left_cache_name}_*_rtdl_rayjoin_overlay_packed_v1"))
    right_cache = next(root.glob(f"{args.right_cache_name}_*_rtdl_rayjoin_overlay_packed_v1"))
    left = _load_packed_cache(left_cache)
    right = _load_packed_cache(right_cache)
    scale_bounds = overlay._shared_rayjoin_bounds(left, right)
    params = _scale_parameters(scale_bounds)

    started = time.perf_counter()
    lsi_rows, lsi_timings = overlay._run_lsi_rows(
        "optix",
        left.segments,
        right.segments,
        None,
        None,
        left_coords=left.segment_coords,
        right_coords=right.segment_coords,
        scale_bounds=scale_bounds,
    )
    xsects = overlay._intersections_from_lsi_rows(lsi_rows)
    edge_starts = (left.edge_starts, right.edge_starts)
    sorted_rows = overlay._sort_xsects_for_map(
        xsects,
        edge_starts[args.target_map_index],
        args.target_map_index,
        scale_bounds=scale_bounds,
    )
    all_midpoints, all_owners, all_scaled_midpoints = overlay._midpoints_for_sorted_xsects(
        sorted_rows,
        args.target_map_index,
        scale_bounds=scale_bounds,
        stats={},
    )
    edge_attr = "eid0" if args.target_map_index == 0 else "eid1"
    base_attr = "eid1" if args.target_map_index == 0 else "eid0"
    group = [row for row in sorted_rows if int(getattr(row, edge_attr)) == int(args.target_query_eid)]
    selected_pair = None
    selected_index = None
    for index, (left_x, right_x) in enumerate(zip(group, group[1:])):
        if int(getattr(left_x, base_attr)) == int(args.target_owner_base_eid):
            selected_pair = (left_x, right_x)
            selected_index = index
            break
    if selected_pair is None:
        raise RuntimeError("target owner intersection was not found in sorted group")
    target_midpoint_index = None
    for index, owner in enumerate(all_owners):
        if owner is selected_pair[0]:
            target_midpoint_index = index
            break
    if target_midpoint_index is None:
        for index, owner in enumerate(all_owners):
            if (
                int(getattr(owner, edge_attr)) == int(args.target_query_eid)
                and int(getattr(owner, base_attr)) == int(args.target_owner_base_eid)
            ):
                target_midpoint_index = index
                break
    if target_midpoint_index is None:
        raise RuntimeError("target midpoint owner was not found in full midpoint list")

    query_inputs = left if args.target_map_index == 0 else right
    base_inputs = right if args.target_map_index == 0 else left
    query_row = query_inputs.segments.owner[0][args.target_query_eid]
    base_row0 = base_inputs.segments.owner[0][int(getattr(selected_pair[0], base_attr))]
    base_row1 = base_inputs.segments.owner[0][int(getattr(selected_pair[1], base_attr))]
    p0 = _exact_intersection(query_row, base_row0, params)
    p1 = _exact_intersection(query_row, base_row1, params)
    if p0 is None or p1 is None:
        raise RuntimeError("selected pair has no exact intersection")
    exact_mid_x = p0[0] + (p1[0] - p0[0]) / 2
    exact_mid_y = p0[1] + (p1[1] - p0[1]) / 2
    stored_mid_x = (float(selected_pair[0].scaled_x) + float(selected_pair[1].scaled_x)) * 0.5
    stored_mid_y = (float(selected_pair[0].scaled_y) + float(selected_pair[1].scaled_y)) * 0.5

    with overlay._prepared_point_location_pair(
        "optix",
        right.cdb_segments,
        left.cdb_segments,
        scale_bounds,
        point_counts=(int(left.points.count), int(right.points.count)),
    ) as (map0_in_map1, map1_in_map0, _):
        runner = map0_in_map1 if args.target_map_index == 0 else map1_in_map0
        batch_diagnostics = {}
        with overlay._rayjoin_cdb_point_location_env(runner.query_map_id, runner.scale_bounds):
            rows = runner.prepared.run_scaled_raw(np.asarray([[stored_mid_x, stored_mid_y]], dtype=np.float64))
            try:
                native_columns = rows.to_numpy_columns(copy=True)
                native_timings = runner.prepared.last_phase_timings() or {}
            finally:
                rows.close()
            if args.target_map_index == 0:
                runner.faces(left.points, int(left.points.count))
            else:
                runner.faces(right.points, int(right.points.count))
            rows = runner.prepared.run_scaled_raw(np.asarray([[stored_mid_x, stored_mid_y]], dtype=np.float64))
            try:
                after_vertex_columns = rows.to_numpy_columns(copy=True)
            finally:
                rows.close()
            scaled_array = np.asarray(all_scaled_midpoints, dtype=np.float64)
            lo = max(0, int(target_midpoint_index) - 8)
            hi = min(int(scaled_array.shape[0]), int(target_midpoint_index) + 9)
            rows = runner.prepared.run_scaled_raw(scaled_array[lo:hi])
            try:
                window_columns = rows.to_numpy_columns(copy=True)
            finally:
                rows.close()
            rows = runner.prepared.run_scaled_raw(scaled_array)
            try:
                full_columns = rows.to_numpy_columns(copy=True)
            finally:
                rows.close()
            def target_from_columns(columns, offset):
                point_ids = columns["point_id"].astype(np.int64, copy=False)
                target_point_id = int(target_midpoint_index) - int(offset) + 1
                matches = np.nonzero(point_ids == target_point_id)[0]
                if matches.size == 0:
                    return None
                pos = int(matches[0])
                return {name: columns[name][pos].item() for name in columns}
            batch_diagnostics = {
                "target_midpoint_index": int(target_midpoint_index),
                "total_midpoints": int(scaled_array.shape[0]),
                "single_after_vertex": {name: after_vertex_columns[name].tolist() for name in after_vertex_columns},
                "window_offset": int(lo),
                "window_target": target_from_columns(window_columns, lo),
                "full_target": target_from_columns(full_columns, 0),
            }

    base_cdb = base_inputs.cdb_segments.owner[1]
    author_index, author_best, author_top_candidates = _author_like_pip(
        exact_mid_x,
        exact_mid_y,
        base_cdb,
        params,
        int(args.target_map_index),
        int(args.chunk_size),
    )

    result = {
        "schema": "rtdl.goal4806.rayjoin_first_diff_probe.v1",
        "target": {
            "map_index": int(args.target_map_index),
            "query_eid": int(args.target_query_eid),
            "owner_base_eid": int(args.target_owner_base_eid),
            "group_size": int(len(group)),
            "selected_pair_index": int(selected_index),
            "selected_pair_base_eids": [
                int(getattr(selected_pair[0], base_attr)),
                int(getattr(selected_pair[1], base_attr)),
            ],
        },
        "timings": {
            "total_probe_sec": float(time.perf_counter() - started),
            "lsi": dict(lsi_timings),
            "native_point_location": dict(native_timings),
        },
        "midpoint": {
            "exact_scaled_x_num": int(exact_mid_x.numerator),
            "exact_scaled_x_den": int(exact_mid_x.denominator),
            "exact_scaled_y_num": int(exact_mid_y.numerator),
            "exact_scaled_y_den": int(exact_mid_y.denominator),
            "exact_scaled_x_as_double": float(exact_mid_x),
            "exact_scaled_y_as_double": float(exact_mid_y),
            "stored_scaled_x": float(stored_mid_x),
            "stored_scaled_y": float(stored_mid_y),
            "stored_minus_exact_x": float(stored_mid_x - float(exact_mid_x)),
            "stored_minus_exact_y": float(stored_mid_y - float(exact_mid_y)),
        },
        "native_scaled_raw": {
            name: native_columns[name].tolist() for name in native_columns
        },
        "native_batch_diagnostics": batch_diagnostics,
        "author_like_cpu": {
            "array_index": None if author_index is None else int(author_index),
            "best": author_best,
            "top_candidates": author_top_candidates,
        },
    }
    output = Path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
