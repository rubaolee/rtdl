from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


def _polygon_bounds(polygon: dict[str, object]) -> dict[str, float | int]:
    vertices = polygon["vertices"]
    xs = [float(vertex[0]) for vertex in vertices]
    ys = [float(vertex[1]) for vertex in vertices]
    return {
        "polygon_id": int(polygon["id"]),
        "min_x": min(xs),
        "min_y": min(ys),
        "max_x": max(xs),
        "max_y": max(ys),
    }


def _inside_bounds(point: dict[str, float | int], bounds: dict[str, float | int]) -> bool:
    return (
        float(bounds["min_x"]) <= float(point["x"]) <= float(bounds["max_x"])
        and float(bounds["min_y"]) <= float(point["y"]) <= float(bounds["max_y"])
    )


def _contains_point(point: dict[str, float | int], polygon: dict[str, object]) -> bool:
    x = float(point["x"])
    y = float(point["y"])
    inside = False
    vertices = polygon["vertices"]
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


def main() -> int:
    points = (
        {"id": 1, "x": 0.25, "y": 0.25},
        {"id": 2, "x": 0.75, "y": 0.75},
        {"id": 3, "x": 2.50, "y": 2.50},
        {"id": 4, "x": 5.00, "y": 5.00},
    )
    polygons = (
        {"id": 10, "vertices": ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))},
        {"id": 20, "vertices": ((2.0, 2.0), (3.0, 2.0), (3.0, 3.0), (2.0, 3.0))},
    )

    bounds_rows = tuple(_polygon_bounds(polygon) for polygon in polygons)
    candidate_rows = []
    positive_hits = []
    for point in points:
        for polygon, bounds in zip(polygons, bounds_rows):
            if not _inside_bounds(point, bounds):
                continue
            candidate = {"point_id": int(point["id"]), "polygon_id": int(polygon["id"])}
            candidate_rows.append(candidate)
            if _contains_point(point, polygon):
                positive_hits.append({**candidate, "contains": True})

    plan = rtdl_v4.plan_operator_request_v4("aabb_index_query", partner="rtdl_native")
    payload = {
        "status": "ok",
        "concept": "PIP is broadphase bounds filtering plus exact containment; RTDL helps produce candidate rows, app logic owns containment meaning",
        "manual_data_flow": (
            "polygons -> bounds rows -> point/polygon candidate rows -> exact containment rows"
        ),
        "bounds_rows": bounds_rows,
        "candidate_rows": tuple(candidate_rows),
        "positive_hits": tuple(positive_hits),
        "v4_surface": {
            "operator": "aabb_index_query",
            "partner": "rtdl_native",
            "status": plan.status,
            "surface": plan.api_surface,
            "generic_primitive": plan.generic_primitive,
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
