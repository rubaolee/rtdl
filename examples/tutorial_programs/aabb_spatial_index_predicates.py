from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl as rt
import rtdsl.v4 as rtdl_v4
from rtdsl.reference import Point
from rtdsl.reference import Polygon


@rt.kernel(backend="rtdl", precision="float_approx")
def rectangle_containment_kernel():
    points = rt.input("points", rt.Points, role="probe")
    rectangles = rt.input("rectangles", rt.Polygons, role="build")
    candidates = rt.traverse(points, rectangles, accel="bvh")
    hits = rt.refine(
        candidates,
        predicate=rt.point_in_polygon(exact=False, result_mode="positive_hits"),
    )
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])


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


def _box_to_polygon(box: dict[str, float | int]) -> Polygon:
    return Polygon(
        id=int(box["box_id"]),
        vertices=(
            (float(box["min_x"]), float(box["min_y"])),
            (float(box["max_x"]), float(box["min_y"])),
            (float(box["max_x"]), float(box["max_y"])),
            (float(box["min_x"]), float(box["max_y"])),
        ),
    )


def make_case() -> dict[str, object]:
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
    return {"boxes": boxes, "points": points, "query_boxes": query_boxes}


def run_kernel_mode() -> dict[str, object]:
    case = make_case()
    points = tuple(
        Point(id=int(point["query_id"]), x=float(point["x"]), y=float(point["y"]))
        for point in case["points"]
    )
    rectangles = tuple(_box_to_polygon(box) for box in case["boxes"])
    compiled = rt.compile_kernel(rectangle_containment_kernel)
    rows = tuple(rt.run_cpu_python_reference(rectangle_containment_kernel, points=points, rectangles=rectangles))
    return {
        "mode": "kernel",
        "status": "ok",
        "teaches": (
            "RTDL kernel-shaped broadphase: input points and rectangle polygons, "
            "traverse candidates, refine with point_in_polygon, emit hit rows"
        ),
        "honesty_note": (
            "Current public kernel API does not expose a direct AABB-index predicate. "
            "This kernel mode teaches the same rectangle-containment relation; V4 "
            "mode below is the true prepared AABB operator surface."
        ),
        "kernel_summary": compiled.format(),
        "point_contains_rows": tuple(
            {
                "query_id": int(row["point_id"]),
                "box_id": int(row["polygon_id"]),
                "contains": int(row["contains"]),
            }
            for row in rows
        ),
    }


def run_visible_flow() -> dict[str, object]:
    case = make_case()
    boxes = case["boxes"]
    points = case["points"]
    query_boxes = case["query_boxes"]
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
    return {
        "status": "ok",
        "mode": "visible_python_flow",
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
    }


def run_v4_mode() -> dict[str, object]:
    plan = rtdl_v4.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")
    return {
        "mode": "v4",
        "status": "ok",
        "teaches": "V4 prepared AABB operator/runtime mapping",
        "operator": "aabb_index_query",
        "partner": "rtdl_native",
        "plan_status": plan.status,
        "surface": plan.api_surface,
        "v4_surface": {
            "request": "aabb_index_query",
            "partner": "rtdl_native",
            "status": plan.status,
            "surface": plan.api_surface,
        },
        "relationship_to_kernel": (
            "The kernel mode teaches rectangle-containment relation rows. This "
            "V4 route is the current prepared AABB execution surface for point, "
            "range-containment, and range-intersection AABB predicates."
        ),
    }


def run_both_modes() -> dict[str, object]:
    kernel = run_kernel_mode()
    v4 = run_v4_mode()
    return {
        "status": "ok",
        "concept": (
            "AABB starts as broadphase relation thinking; V4 provides the prepared "
            "AABB operator surface for the full predicate family"
        ),
        "kernel_mode": kernel,
        "visible_flow": run_visible_flow(),
        "v4_mode": v4,
        "same_semantics": {
            "shared_relation": "spatial containment/candidate rows",
            "kernel_limit": "point-in-rectangle containment only",
            "v4_expands_to": "point, range-containment, and range-intersection AABB predicates",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="RTDL AABB predicate tutorial")
    parser.add_argument("--mode", choices=("kernel", "v4", "both", "visible"), default="both")
    args = parser.parse_args()
    if args.mode == "kernel":
        payload = run_kernel_mode()
    elif args.mode == "v4":
        payload = run_v4_mode()
    elif args.mode == "visible":
        payload = run_visible_flow()
    else:
        payload = run_both_modes()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
