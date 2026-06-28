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
def point_in_polygon_kernel():
    points = rt.input("points", rt.Points, role="probe")
    polygons = rt.input("polygons", rt.Polygons, role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    hits = rt.refine(
        candidates,
        predicate=rt.point_in_polygon(exact=False, result_mode="positive_hits"),
    )
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])


def make_case() -> dict[str, tuple[Point, ...] | tuple[Polygon, ...]]:
    return {
        "points": (
            Point(id=1, x=0.25, y=0.25),
            Point(id=2, x=0.75, y=0.75),
            Point(id=3, x=2.50, y=2.50),
            Point(id=4, x=5.00, y=5.00),
        ),
        "polygons": (
            Polygon(id=10, vertices=((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))),
            Polygon(id=20, vertices=((2.0, 2.0), (3.0, 2.0), (3.0, 3.0), (2.0, 3.0))),
        ),
    }


def _polygon_bounds(polygon: Polygon) -> dict[str, float | int]:
    xs = [float(vertex[0]) for vertex in polygon.vertices]
    ys = [float(vertex[1]) for vertex in polygon.vertices]
    return {
        "polygon_id": int(polygon.id),
        "min_x": min(xs),
        "min_y": min(ys),
        "max_x": max(xs),
        "max_y": max(ys),
    }


def _inside_bounds(point: Point, bounds: dict[str, float | int]) -> bool:
    return (
        float(bounds["min_x"]) <= float(point.x) <= float(bounds["max_x"])
        and float(bounds["min_y"]) <= float(point.y) <= float(bounds["max_y"])
    )


def _contains_point(point: Point, polygon: Polygon) -> bool:
    x = float(point.x)
    y = float(point.y)
    inside = False
    vertices = polygon.vertices
    previous_x, previous_y = vertices[-1]
    for current_x, current_y in vertices:
        crosses_y = (float(current_y) > y) != (float(previous_y) > y)
        if crosses_y:
            boundary_x = (
                (float(previous_x) - float(current_x))
                * (y - float(current_y))
                / (float(previous_y) - float(current_y))
                + float(current_x)
            )
            if x < boundary_x:
                inside = not inside
        previous_x, previous_y = current_x, current_y
    return inside


def run_kernel_mode() -> dict[str, object]:
    case = make_case()
    compiled = rt.compile_kernel(point_in_polygon_kernel)
    rows = tuple(rt.run_cpu_python_reference(point_in_polygon_kernel, **case))
    return {
        "mode": "kernel",
        "status": "ok",
        "teaches": (
            "RTDL kernel: input points and polygons, traverse candidate pairs, "
            "refine(point_in_polygon), emit positive containment rows"
        ),
        "kernel_summary": compiled.format(),
        "points": tuple(point.__dict__ for point in case["points"]),
        "polygons": tuple(polygon.__dict__ for polygon in case["polygons"]),
        "positive_hits": tuple(
            {
                "point_id": int(row["point_id"]),
                "polygon_id": int(row["polygon_id"]),
                "contains": int(row["contains"]),
            }
            for row in rows
        ),
    }


def run_visible_flow() -> dict[str, object]:
    case = make_case()
    points = case["points"]
    polygons = case["polygons"]
    bounds_rows = tuple(_polygon_bounds(polygon) for polygon in polygons)
    candidate_rows = []
    positive_hits = []
    for point in points:
        for polygon, bounds in zip(polygons, bounds_rows):
            if not _inside_bounds(point, bounds):
                continue
            candidate = {"point_id": int(point.id), "polygon_id": int(polygon.id)}
            candidate_rows.append(candidate)
            if _contains_point(point, polygon):
                positive_hits.append({**candidate, "contains": True})

    return {
        "mode": "visible_python_flow",
        "status": "ok",
        "concept": "manual mirror of the PIP relation: broadphase candidates plus exact containment",
        "manual_data_flow": (
            "polygons -> bounds rows -> point/polygon candidate rows -> exact containment rows"
        ),
        "bounds_rows": bounds_rows,
        "candidate_rows": tuple(candidate_rows),
        "positive_hits": tuple(positive_hits),
    }


def run_v4_mode() -> dict[str, object]:
    plan = rtdl_v4.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")
    return {
        "mode": "v4",
        "status": "ok",
        "teaches": (
            "V4 operator/runtime mapping for the broadphase candidate relation; "
            "exact PIP semantics remain the RTDL kernel predicate above"
        ),
        "operator": "aabb_index_query",
        "partner": "rtdl_native",
        "plan_status": plan.status,
        "surface": plan.api_surface,
        "generic_primitive": plan.generic_primitive,
        "relationship_to_kernel": (
            "The kernel is the language model: traverse point/polygon candidates "
            "and refine them with point_in_polygon. The V4 AABB route is the "
            "prepared broadphase surface used when the same candidate relation "
            "is executed through the V4 runtime."
        ),
    }


def run_both_modes() -> dict[str, object]:
    kernel = run_kernel_mode()
    v4 = run_v4_mode()
    return {
        "status": "ok",
        "concept": (
            "point-in-polygon is first an RTDL kernel relation; V4 then maps the "
            "candidate-generation part to a prepared operator surface"
        ),
        "kernel_mode": kernel,
        "visible_flow": run_visible_flow(),
        "v4_mode": v4,
        "same_semantics": {
            "relation": "point_polygon_positive_containment_rows",
            "kernel_output_field": "positive_hits",
            "v4_execution_target": v4["surface"],
            "v4_scope": "broadphase candidate generation plus prepared routing",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="RTDL point-in-polygon tutorial")
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
