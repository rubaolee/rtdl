from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


def _contains_point(box: dict[str, float | int], point: dict[str, float | int]) -> bool:
    return (
        float(box["min_x"]) <= float(point["x"]) <= float(box["max_x"])
        and float(box["min_y"]) <= float(point["y"]) <= float(box["max_y"])
    )


def _contains_box(box: dict[str, float | int], query: dict[str, float | int]) -> bool:
    return (
        float(box["min_x"]) <= float(query["min_x"])
        and float(box["min_y"]) <= float(query["min_y"])
        and float(query["max_x"]) <= float(box["max_x"])
        and float(query["max_y"]) <= float(box["max_y"])
    )


def _intersects_box(box: dict[str, float | int], query: dict[str, float | int]) -> bool:
    return not (
        float(box["max_x"]) < float(query["min_x"])
        or float(query["max_x"]) < float(box["min_x"])
        or float(box["max_y"]) < float(query["min_y"])
        or float(query["max_y"]) < float(box["min_y"])
    )


def main() -> int:
    boxes = (
        {"box_id": 1, "min_x": 0.0, "min_y": 0.0, "max_x": 1.0, "max_y": 1.0},
        {"box_id": 2, "min_x": 0.2, "min_y": 0.2, "max_x": 0.8, "max_y": 0.8},
    )
    points = (
        {"query_id": 10, "x": 0.5, "y": 0.5},
        {"query_id": 11, "x": 2.0, "y": 2.0},
    )
    query_boxes = (
        {"query_id": 20, "min_x": 0.25, "min_y": 0.25, "max_x": 0.75, "max_y": 0.75},
        {"query_id": 21, "min_x": 0.9, "min_y": 0.9, "max_x": 1.1, "max_y": 1.1},
    )
    point_contains_rows = tuple(
        {"query_id": point["query_id"], "box_id": box["box_id"], "predicate": "point_contains"}
        for point in points
        for box in boxes
        if _contains_point(box, point)
    )
    range_contains_rows = tuple(
        {"query_id": query["query_id"], "box_id": box["box_id"], "predicate": "range_contains"}
        for query in query_boxes
        for box in boxes
        if _contains_box(box, query)
    )
    range_intersects_rows = tuple(
        {"query_id": query["query_id"], "box_id": box["box_id"], "predicate": "range_intersects"}
        for query in query_boxes
        for box in boxes
        if _intersects_box(box, query)
    )
    plan = rtdl_v4.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")
    payload = {
        "status": "ok",
        "concept": "LibRTS-style spatial indexes ask point containment, range containment, and range intersection over AABB rows",
        "manual_data_flow": "boxes + point/range queries -> predicate-specific relation rows -> count or row summaries",
        "boxes": boxes,
        "point_queries": points,
        "range_queries": query_boxes,
        "point_contains_rows": point_contains_rows,
        "range_contains_rows": range_contains_rows,
        "range_intersects_rows": range_intersects_rows,
        "counts": {
            "point_contains": len(point_contains_rows),
            "range_contains": len(range_contains_rows),
            "range_intersects": len(range_intersects_rows),
        },
        "v4_surface": {
            "request": "aabb_index_query",
            "partner": "rtdl_native",
            "status": plan.status,
            "surface": plan.api_surface,
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
