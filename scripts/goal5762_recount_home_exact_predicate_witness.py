#!/usr/bin/env python3
"""Independent Goal5762 raw recount.

This verifier imports neither the V4 product module nor a Paper-App route.
It reconstructs the three semantic answers from embedded primitive inputs,
checks that the OptiX broad phase is the complete closed-AABB relation, and
checks the behavioral traversal receipts.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

import numpy as np


U32_MAX = (1 << 32) - 1


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rows(value: object) -> tuple[tuple[object, ...], ...]:
    return tuple(tuple(row) for row in value)


def _f32_distance_sq(left: np.ndarray, right: np.ndarray) -> float:
    delta = np.subtract(left, right, dtype=np.float32)
    squared = np.multiply(delta, delta, dtype=np.float32)
    return float(np.add(np.add(squared[0], squared[1], dtype=np.float32),
                        squared[2], dtype=np.float32))


def _xhd_reference(spec: dict[str, object]) -> dict[str, object]:
    sources = np.asarray(spec["source_points_f32"], dtype=np.float32)
    targets = np.asarray(spec["target_points_f32"], dtype=np.float32)
    per_query = []
    for query_id, query in enumerate(sources):
        nearest = min(
            ((_f32_distance_sq(query, target), item_id)
             for item_id, target in enumerate(targets)),
            key=lambda row: (row[0], row[1]),
        )
        per_query.append((query_id, query_id, nearest[1], nearest[0]))
    winner = min(per_query, key=lambda row: (-row[3], row[1], row[2]))
    return {
        "source_index": winner[0],
        "source_id": winner[1],
        "item_id": winner[2],
        "value": math.sqrt(winner[3]),
        "distance_squared": winner[3],
        "per_query_nearest": [list(row) for row in per_query],
        "contract": "global_max_nearest_witness_f32_v1",
    }


def _aabb_relation(sources, indexed) -> tuple[tuple[int, int], ...]:
    return tuple(sorted({
        (int(source[4]), int(item[4]))
        for source in sources
        for item in indexed
        if float(item[0]) <= float(source[2])
        and float(item[2]) >= float(source[0])
        and float(item[1]) <= float(source[3])
        and float(item[3]) >= float(source[1])
    }))


def _outward_f32(value: int, direction: float) -> float:
    return float(np.nextafter(
        np.float32(value),
        np.float32(-math.inf if direction < 0.0 else math.inf),
        dtype=np.float32))


def _segment_boxes(segments) -> tuple[tuple[float, float, float, float, int], ...]:
    return tuple((
        _outward_f32(min(int(row["x0"]), int(row["x1"])), -1.0),
        _outward_f32(min(int(row["y0"]), int(row["y1"])), -1.0),
        _outward_f32(max(int(row["x0"]), int(row["x1"])), 1.0),
        _outward_f32(max(int(row["y0"]), int(row["y1"])), 1.0),
        int(row["segment_id"]),
    ) for row in segments)


def _vertical_ray_boxes(points, segments):
    maximum_y = max(max(int(row["y0"]), int(row["y1"])) for row in segments)
    return tuple((
        _outward_f32(int(row["x"]), -1.0),
        _outward_f32(int(row["y"]), -1.0),
        _outward_f32(int(row["x"]), 1.0),
        _outward_f32(max(int(row["y"]), maximum_y), 1.0),
        int(row["point_id"]),
    ) for row in points)


def _line(segment: dict[str, int]) -> tuple[int, int, int]:
    a = int(segment["y0"]) - int(segment["y1"])
    b = int(segment["x1"]) - int(segment["x0"])
    c = -int(segment["x0"]) * a - int(segment["y0"]) * b
    return (-a, -b, -c) if b < 0 else (a, b, c)


def _line_eval(line: tuple[int, int, int], x: int, y: int) -> int:
    return x * line[0] + y * line[1] + line[2]


def _segment_pair_intersects(left: dict[str, int], right: dict[str, int]) -> bool:
    e1, e2 = _line(left), _line(right)
    values = [
        _line_eval(e2, int(left["x0"]), int(left["y0"])),
        _line_eval(e2, int(left["x1"]), int(left["y1"])),
        _line_eval(e1, int(right["x0"]), int(right["y0"])),
        _line_eval(e1, int(right["x1"]), int(right["y1"])),
    ]
    # First left endpoint, second left endpoint: -e2.a then -e2.b.
    for index in (0, 1):
        if values[index] == 0:
            values[index] = -e2[0]
        if values[index] == 0:
            values[index] = -e2[1]
        if values[index] == 0:
            return False
    if (values[0] > 0) == (values[1] > 0):
        return False
    # Right endpoints: +e1.a then +e1.b.
    for index in (2, 3):
        if values[index] == 0:
            values[index] = e1[0]
        if values[index] == 0:
            values[index] = e1[1]
        if values[index] == 0:
            return False
    if (values[2] > 0) == (values[3] > 0):
        return False
    left_coords = (left["x0"], left["y0"], left["x1"], left["y1"])
    right_coords = (right["x0"], right["y0"], right["x1"], right["y1"])
    reversed_right = (
        right["x1"], right["y1"], right["x0"], right["y0"])
    return left_coords != right_coords and left_coords != reversed_right


def _point_hit(point: dict[str, int], segment: dict[str, int], query_map: int):
    x0, x1 = int(segment["x0"]), int(segment["x1"])
    x_min, x_max = min(x0, x1), max(x0, x1)
    excluded = x_min if query_map == 0 else x_max
    point_x, point_y = int(point["x"]), int(point["y"])
    if point_x < x_min or point_x > x_max or point_x == excluded:
        return None
    a, b, c = _line(segment)
    if b == 0:
        return None
    numerator = -(a * point_x) - c
    diff = point_y * b - numerator
    if diff == 0:
        diff = -a if query_map == 0 else a
    if diff == 0:
        diff = -b if query_map == 0 else b
    if diff > 0:
        return None
    return numerator, b, a


def _point_location(points, segments, query_map: int):
    output = []
    for point in points:
        best = None
        for source_order, segment in enumerate(segments):
            hit = _point_hit(point, segment, query_map)
            if hit is None:
                continue
            numerator, denominator, slope_numerator = hit
            candidate = (numerator, denominator, slope_numerator,
                         source_order, segment)
            if best is None:
                best = candidate
                continue
            best_n, best_d, best_slope, _, _ = best
            lower = numerator * best_d < best_n * denominator
            equal = numerator * best_d == best_n * denominator
            if query_map == 0:
                slope_better = slope_numerator * best_d > best_slope * denominator
            else:
                # The author contract accepts the later source-order segment
                # on equal map-1 slopes.
                slope_better = slope_numerator * best_d <= best_slope * denominator
            if lower or (equal and slope_better):
                best = candidate
        if best is None:
            output.append((int(point["point_id"]), 0, U32_MAX))
        else:
            segment = best[4]
            face = (int(segment["right_face_id"])
                    if int(segment["x0"]) < int(segment["x1"])
                    else int(segment["left_face_id"]))
            output.append((int(point["point_id"]), face,
                           int(segment["segment_id"])))
    return tuple(output)


def _check_receipt(lane: dict[str, object]) -> None:
    receipt = lane["traversal_receipt"]
    snapshot = receipt["native_snapshot"]
    if receipt["physical_executor_classification"] != "optix_traversal_observed":
        raise RuntimeError(f"not behaviorally true-OptiX: {lane['lane']}")
    if int(snapshot["successful_launch_count"]) <= 0 \
            or int(snapshot["successful_launch_count"]) \
            != int(snapshot["complete_context_launch_count"]) \
            or int(snapshot["failed_launch_count"]) != 0 \
            or int(snapshot["incomplete_context_launch_count"]) != 0 \
            or int(snapshot["pending_context_at_finish"]) != 0 \
            or int(snapshot["session_error"]) != 0:
        raise RuntimeError(f"invalid traversal receipt: {lane['lane']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result_path = args.raw / "RESULT.json"
    native_path = args.raw / "librtdl_optix.so"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if _sha(native_path) != result["native_library_sha256"]:
        raise RuntimeError("copied native does not match result identity")
    lanes = {row["lane"]: row for row in result["lanes"]}
    expected_names = {
        "x_hd.nearest_state.cell_mbr_exact_witness.v1",
        "rayjoin.planar_map.directed_segment_point_location_2d.v1",
        "rayjoin.planar_map.segment_pair_grouped_range_exact_count_2d.v1",
    }
    if set(lanes) != expected_names:
        raise RuntimeError("raw evidence does not contain the frozen M4 lanes")

    xhd = lanes["x_hd.nearest_state.cell_mbr_exact_witness.v1"]
    xhd_recount = _xhd_reference(xhd["input"])
    if xhd_recount != xhd["actual"] or xhd["actual"] != xhd["expected"]:
        raise RuntimeError("independent X-HD global-witness recount mismatch")
    _check_receipt(xhd)

    point = lanes["rayjoin.planar_map.directed_segment_point_location_2d.v1"]
    point_input = point["input"]
    if _rows(point_input["source_boxes"]) != _vertical_ray_boxes(
            point_input["points"], point_input["segments"]) \
            or _rows(point_input["indexed_boxes"]) != _segment_boxes(
                point_input["segments"]):
        raise RuntimeError("point-location compiler-owned AABB projection mismatch")
    point_candidates = _aabb_relation(
        point_input["source_boxes"], point_input["indexed_boxes"])
    if point_candidates != _rows(point["candidate_rows"]):
        raise RuntimeError("point-location candidate relation is incomplete or extra")
    point_recount = _point_location(
        point_input["points"], point_input["segments"],
        int(point_input["query_map_id"]))
    if point_recount != _rows(point["actual"]["rows"]) \
            or point_recount != _rows(point["expected_rows"]):
        raise RuntimeError("independent point-location recount mismatch")
    _check_receipt(point)

    pair = lanes["rayjoin.planar_map.segment_pair_grouped_range_exact_count_2d.v1"]
    pair_input = pair["input"]
    if _rows(pair_input["source_boxes"]) != _segment_boxes(
            pair_input["left_segments"]) \
            or _rows(pair_input["indexed_boxes"]) != _segment_boxes(
                pair_input["right_segments"]):
        raise RuntimeError("segment-pair compiler-owned AABB projection mismatch")
    pair_candidates = _aabb_relation(
        pair_input["source_boxes"], pair_input["indexed_boxes"])
    if pair_candidates != _rows(pair["candidate_rows"]):
        raise RuntimeError("segment-pair candidate relation is incomplete or extra")
    left_by_id = {int(row["segment_id"]): row
                  for row in pair_input["left_segments"]}
    right_by_id = {int(row["segment_id"]): row
                   for row in pair_input["right_segments"]}
    exact_pairs = tuple(
        candidate for candidate in pair_candidates
        if _segment_pair_intersects(
            left_by_id[int(candidate[0])], right_by_id[int(candidate[1])]))
    grouped = Counter(
        (int(left_by_id[left]["group_id"]),
         int(right_by_id[right]["group_id"]))
        for left, right in exact_pairs)
    grouped_rows = tuple((left, right, count)
                         for (left, right), count in sorted(grouped.items()))
    if exact_pairs != _rows(pair["actual"]["exact_pairs"]) \
            or grouped_rows != _rows(pair["actual"]["grouped_counts"]) \
            or exact_pairs != _rows(pair["expected_exact_pairs"]) \
            or grouped_rows != _rows(pair["expected_grouped_counts"]):
        raise RuntimeError("independent segment-pair/group recount mismatch")
    _check_receipt(pair)

    recount = {
        "schema": "rtdl.goal5762.independent_home_exact_predicate_witness_recount.v1",
        "raw_result_sha256": _sha(result_path),
        "native_library_sha256": _sha(native_path),
        "lane_count": 3,
        "exact_route_independent_recount_count": 3,
        "complete_broadphase_recount_count": 2,
        "behavioral_true_optix_count": 3,
        "registered_performance_timing_count": 0,
        "imports_product_compiler_runtime_or_paper_app": False,
        "verdict": "pass",
    }
    args.output.write_text(
        json.dumps(recount, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(recount, sort_keys=True))


if __name__ == "__main__":
    main()
