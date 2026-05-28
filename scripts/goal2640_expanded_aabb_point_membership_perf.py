#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gc
import json
import statistics
import time
from pathlib import Path

from rtdsl.aabb_index import (
    Aabb2D,
    Point2DLike,
    _IdentifiedAabb2D,
    _IdentifiedPoint2D,
    _prepare_embree_aabb_index_2d,
    expanded_aabb_point_membership_rows_2d,
)
from rtdsl.optix_runtime import PreparedOptixAabbIndex2D, pack_points


def _scene(box_count: int, query_count: int):
    side = int(box_count**0.5)
    if side * side < box_count:
        side += 1
    boxes: list[Aabb2D] = []
    indexed_boxes: list[_IdentifiedAabb2D] = []
    for idx in range(box_count):
        col = idx % side
        row = idx // side
        min_x = float(col * 2)
        min_y = float(row * 2)
        max_x = min_x + 1.0
        max_y = min_y + 1.0
        boxes.append(Aabb2D(min_x, min_y, max_x, max_y))
        indexed_boxes.append(_IdentifiedAabb2D(idx, min_x, min_y, max_x, max_y))

    points: list[Point2DLike] = []
    point_records: list[_IdentifiedPoint2D] = []
    x: list[float] = []
    y: list[float] = []
    ids: list[int] = []
    for query_id in range(query_count):
        box = boxes[query_id % box_count]
        px = (box.min_x + box.max_x) * 0.5
        py = (box.min_y + box.max_y) * 0.5
        points.append(Point2DLike(px, py))
        point_records.append(_IdentifiedPoint2D(query_id, px, py))
        ids.append(query_id)
        x.append(px)
        y.append(py)
    return boxes, indexed_boxes, points, point_records, ids, x, y


def _median_ms(samples: list[float]) -> float:
    return statistics.median(samples) * 1000.0


def _time_call(fn, repeats: int) -> tuple[float, object]:
    samples: list[float] = []
    result = None
    for _ in range(repeats):
        gc.collect()
        start = time.perf_counter()
        result = fn()
        samples.append(time.perf_counter() - start)
    return _median_ms(samples), result


def run_case(
    box_count: int,
    query_count: int,
    repeats: int,
    *,
    include_oneshot: bool,
) -> dict[str, object]:
    boxes, indexed_boxes, points, point_records, ids, x, y = _scene(box_count, query_count)
    row_capacity = query_count

    # Prepared Embree path. This includes Embree's current Python-visible row
    # materialization but excludes index construction from query timing.
    embree_prepare_start = time.perf_counter()
    embree = _prepare_embree_aabb_index_2d(tuple(boxes), row_ids=tuple(range(box_count)))
    embree_prepare_ms = (time.perf_counter() - embree_prepare_start) * 1000.0
    try:
        embree_ms, embree_rows = _time_call(
            lambda: embree.point_membership_rows(tuple(points), tuple(ids)),
            repeats,
        )
    finally:
        embree.close()

    optix_prepare_start = time.perf_counter()
    optix = PreparedOptixAabbIndex2D(tuple(indexed_boxes))
    optix_prepare_ms = (time.perf_counter() - optix_prepare_start) * 1000.0
    packed_points = pack_points(ids=ids, x=x, y=y, dimension=2)
    try:
        optix_ms, optix_result = _time_call(
            lambda: optix.collect_point_contains_rows(
                packed_points,
                row_capacity=row_capacity,
            ),
            repeats,
        )
    finally:
        optix.close()
    optix_rows = optix_result["candidate_id_rows"]

    oneshot: dict[str, object] | None = None
    if include_oneshot:
        # One-shot public wrapper timings include expansion, preparation, native
        # call, row sorting/grouping, and result construction.
        embree_oneshot_ms, embree_oneshot = _time_call(
            lambda: expanded_aabb_point_membership_rows_2d(
                boxes,
                points,
                backend="embree",
                row_capacity=row_capacity,
            ),
            max(1, min(repeats, 3)),
        )
        optix_oneshot_ms, optix_oneshot = _time_call(
            lambda: expanded_aabb_point_membership_rows_2d(
                boxes,
                points,
                backend="optix",
                row_capacity=row_capacity,
            ),
            max(1, min(repeats, 3)),
        )
        oneshot = {
            "embree_ms_median": embree_oneshot_ms,
            "optix_ms_median": optix_oneshot_ms,
            "speedup_optix_vs_embree": embree_oneshot_ms / optix_oneshot_ms if optix_oneshot_ms else None,
            "embree_rows": int(embree_oneshot["valid_count"]),
            "optix_rows": int(optix_oneshot["valid_count"]),
            "rows_match": set(embree_oneshot["candidate_id_rows"]) == set(optix_oneshot["candidate_id_rows"]),
        }

    return {
        "box_count": box_count,
        "query_count": query_count,
        "expected_rows": query_count,
        "prepared": {
            "embree_prepare_ms": embree_prepare_ms,
            "optix_prepare_ms": optix_prepare_ms,
            "embree_query_ms_median": embree_ms,
            "optix_query_ms_median": optix_ms,
            "speedup_optix_vs_embree": embree_ms / optix_ms if optix_ms else None,
            "embree_rows": len(embree_rows),
            "optix_rows": len(optix_rows),
            "rows_match": set(embree_rows) == set(optix_rows),
        },
        "oneshot_public_wrapper": oneshot,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--case",
        action="append",
        default=[],
        help="box_count:query_count; may be passed multiple times",
    )
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--skip-oneshot", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    cases = args.case or ["4096:262144", "16384:1048576"]
    results = []
    for item in cases:
        boxes, queries = (int(part) for part in item.split(":", 1))
        result = run_case(
            boxes,
            queries,
            args.repeats,
            include_oneshot=not args.skip_oneshot,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        results.append(result)
    payload = {
        "benchmark": "goal2640_expanded_aabb_point_membership",
        "repeats": args.repeats,
        "cases": results,
    }
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
