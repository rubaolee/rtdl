from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from rtdsl.datasets import chains_to_planar_map_segments
from rtdsl.datasets import load_cdb
from rtdsl.optix_runtime import prepare_planar_map_lsi_2d_optix
from rtdsl.optix_runtime import prepare_segment_pair_intersection_optix


INTERNAL_MAX = (1 << 46) - 1
INTERNAL_MIN = -(1 << 46)


def trunc_i64(value: float) -> int:
    return int(value)


def scale_params(left_segments, right_segments):
    min_x = min(min(s["x0"], s["x1"]) for s in (*left_segments, *right_segments))
    max_x = max(max(s["x0"], s["x1"]) for s in (*left_segments, *right_segments))
    min_y = min(min(s["y0"], s["y1"]) for s in (*left_segments, *right_segments))
    max_y = max(max(s["y0"], s["y1"]) for s in (*left_segments, *right_segments))
    margin = 1.0
    box_max_x = max_x + margin
    box_min_x = min_x - margin
    box_max_y = max_y + margin
    box_min_y = min_y - margin
    internal_range = float(INTERNAL_MAX - INTERNAL_MIN)
    rx = internal_range / (box_max_x - box_min_x)
    ry = internal_range / (box_max_y - box_min_y)
    deltax = 0.5 * (float(INTERNAL_MAX + INTERNAL_MIN) - (box_max_x + box_min_x) * rx)
    deltay = 0.5 * (float(INTERNAL_MAX + INTERNAL_MIN) - (box_max_y + box_min_y) * ry)
    return rx, ry, deltax, deltay


def scaled_segment(segment, scale):
    rx, ry, deltax, deltay = scale
    fma = getattr(math, "fma", None)
    if fma is None:
        sx0 = trunc_i64(segment["x0"] * rx + deltax)
        sy0 = trunc_i64(segment["y0"] * ry + deltay)
        sx1 = trunc_i64(segment["x1"] * rx + deltax)
        sy1 = trunc_i64(segment["y1"] * ry + deltay)
    else:
        sx0 = trunc_i64(fma(segment["x0"], rx, deltax))
        sy0 = trunc_i64(fma(segment["y0"], ry, deltay))
        sx1 = trunc_i64(fma(segment["x1"], rx, deltax))
        sy1 = trunc_i64(fma(segment["y1"], ry, deltay))
    return (int(segment["id"]), sx0, sy0, sx1, sy1)


def line_for_scaled(seg):
    _, x0, y0, x1, y1 = seg
    a = y0 - y1
    b = x1 - x0
    c = -(x0 * a) - (y0 * b)
    if b < 0:
        a = -a
        b = -b
        c = -c
    return a, b, c


def eval_line(line, x, y):
    a, b, c = line
    return x * a + y * b + c


def same_point(ax, ay, bx, by):
    return ax == bx and ay == by


def planar_map_lsi_intersects(left, right) -> bool:
    _, lx0, ly0, lx1, ly1 = left
    _, rx0, ry0, rx1, ry1 = right
    e1 = line_for_scaled(left)
    e2 = line_for_scaled(right)
    if (e1[0] == 0 and e1[1] == 0) or (e2[0] == 0 and e2[1] == 0):
        return False

    e2_p1_agst_e1 = eval_line(e1, rx0, ry0)
    e2_p2_agst_e1 = eval_line(e1, rx1, ry1)
    e1_p1_agst_e2 = eval_line(e2, lx0, ly0)
    e1_p2_agst_e2 = eval_line(e2, lx1, ly1)

    if e1_p1_agst_e2 == 0:
        e1_p1_agst_e2 = -e2[0]
    if e1_p1_agst_e2 == 0:
        e1_p1_agst_e2 = -e2[1]
    if e1_p1_agst_e2 == 0:
        return False
    if e1_p2_agst_e2 == 0:
        e1_p2_agst_e2 = -e2[0]
    if e1_p2_agst_e2 == 0:
        e1_p2_agst_e2 = -e2[1]
    if e1_p2_agst_e2 == 0:
        return False
    if (e1_p1_agst_e2 > 0 and e1_p2_agst_e2 > 0) or (
        e1_p1_agst_e2 < 0 and e1_p2_agst_e2 < 0
    ):
        return False

    if e2_p1_agst_e1 == 0:
        e2_p1_agst_e1 = e1[0]
    if e2_p1_agst_e1 == 0:
        e2_p1_agst_e1 = e1[1]
    if e2_p1_agst_e1 == 0:
        return False
    if e2_p2_agst_e1 == 0:
        e2_p2_agst_e1 = e1[0]
    if e2_p2_agst_e1 == 0:
        e2_p2_agst_e1 = e1[1]
    if e2_p2_agst_e1 == 0:
        return False
    if (e2_p1_agst_e1 > 0 and e2_p2_agst_e1 > 0) or (
        e2_p1_agst_e1 < 0 and e2_p2_agst_e1 < 0
    ):
        return False

    if (
        same_point(lx0, ly0, rx0, ry0)
        and same_point(lx1, ly1, rx1, ry1)
    ) or (
        same_point(lx0, ly0, rx1, ry1)
        and same_point(lx1, ly1, rx0, ry0)
    ):
        return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--expected", type=int)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    t0 = time.perf_counter()
    base = load_cdb(args.base)
    query = load_cdb(args.query)
    base_segments = chains_to_planar_map_segments(base)
    query_segments = chains_to_planar_map_segments(query)
    t1 = time.perf_counter()

    with prepare_planar_map_lsi_2d_optix(base_segments) as lsi:
        lsi_count = lsi.count(query_segments)
    t2 = time.perf_counter()

    scale = scale_params(query_segments, base_segments)
    t3 = time.perf_counter()

    with prepare_segment_pair_intersection_optix(base_segments) as raw_prepared:
        rows = raw_prepared.run_raw(query_segments)
        try:
            raw_count = int(rows.row_count)
            raw_rows = rows.to_dict_rows()
        finally:
            rows.close()

    touched_left_ids = {int(row["left_id"]) for row in raw_rows}
    touched_right_ids = {int(row["right_id"]) for row in raw_rows}
    query_scaled = {
        int(s["id"]): scaled_segment(s, scale)
        for s in query_segments
        if int(s["id"]) in touched_left_ids
    }
    base_scaled = {
        int(s["id"]): scaled_segment(s, scale)
        for s in base_segments
        if int(s["id"]) in touched_right_ids
    }
    t4 = time.perf_counter()

    accepted = []
    rejected = 0
    seen = set()
    for row in raw_rows:
        pair = (int(row["left_id"]), int(row["right_id"]))
        if pair in seen:
            continue
        seen.add(pair)
        left = query_scaled.get(pair[0])
        right = base_scaled.get(pair[1])
        if left is None or right is None:
            rejected += 1
            continue
        if planar_map_lsi_intersects(left, right):
            accepted.append(row)
        else:
            rejected += 1
    t5 = time.perf_counter()

    summary = {
        "schema": "rtdl.goal4859.user_layer_planar_map_lsi_filter_probe.v1",
        "base": str(Path(args.base)),
        "query": str(Path(args.query)),
        "expected": args.expected,
        "planar_map_lsi_count": int(lsi_count),
        "raw_row_count": int(raw_count),
        "filtered_row_count": int(len(accepted)),
        "filtered_equals_planar_map_lsi": int(len(accepted)) == int(lsi_count),
        "filtered_equals_expected": None if args.expected is None else int(len(accepted)) == args.expected,
        "first_filtered_rows": accepted[:5],
        "rejected_or_missing": int(rejected),
        "timings_seconds": {
            "load_and_segment": t1 - t0,
            "public_lsi_count": t2 - t1,
            "scale_params": t3 - t2,
            "raw_rows": t4 - t3,
            "scale_touched_and_python_filter": t5 - t4,
            "total": t5 - t0,
        },
        "route": "public_raw_segment_pair_rows_plus_user_layer_planar_map_lsi_filter",
        "runtime_or_native_edits": False,
        "private_bundled_helper_imported": False,
    }
    Path(args.out).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
