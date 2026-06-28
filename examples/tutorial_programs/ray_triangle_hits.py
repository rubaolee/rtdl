from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as rtdl_v4


def _orientation(a: tuple[float, float], b: tuple[float, float], c: tuple[float, float]) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _segments_cross(
    a0: tuple[float, float],
    a1: tuple[float, float],
    b0: tuple[float, float],
    b1: tuple[float, float],
) -> bool:
    left0 = _orientation(a0, a1, b0)
    left1 = _orientation(a0, a1, b1)
    right0 = _orientation(b0, b1, a0)
    right1 = _orientation(b0, b1, a1)
    return left0 * left1 <= 0.0 and right0 * right1 <= 0.0


def _point_in_triangle(point: tuple[float, float], triangle: tuple[tuple[float, float], ...]) -> bool:
    signs = [
        _orientation(triangle[index], triangle[(index + 1) % 3], point)
        for index in range(3)
    ]
    return all(value >= 0.0 for value in signs) or all(value <= 0.0 for value in signs)


def _ray_segment(ray: dict[str, float | int]) -> tuple[tuple[float, float], tuple[float, float]]:
    origin = (float(ray["ox"]), float(ray["oy"]))
    end = (
        float(ray["ox"]) + float(ray["dx"]) * float(ray["tmax"]),
        float(ray["oy"]) + float(ray["dy"]) * float(ray["tmax"]),
    )
    return origin, end


def _ray_hits_triangle(ray: dict[str, float | int], triangle: dict[str, object]) -> tuple[bool, str]:
    triangle_vertices = triangle["vertices"]
    ray_start, ray_end = _ray_segment(ray)
    if _point_in_triangle(ray_start, triangle_vertices):
        return True, "ray_origin_inside_triangle"
    if _point_in_triangle(ray_end, triangle_vertices):
        return True, "ray_end_inside_triangle"
    triangle_edges = tuple(
        (triangle_vertices[index], triangle_vertices[(index + 1) % 3])
        for index in range(3)
    )
    for edge_start, edge_end in triangle_edges:
        if _segments_cross(ray_start, ray_end, edge_start, edge_end):
            return True, "ray_crosses_triangle_edge"
    return False, "no_crossing"


def main() -> int:
    rays = (
        {"id": 1, "ox": -1.0, "oy": 0.25, "dx": 1.0, "dy": 0.0, "tmax": 4.0},
        {"id": 2, "ox": -1.0, "oy": 2.0, "dx": 1.0, "dy": 0.0, "tmax": 4.0},
    )
    triangles = (
        {"id": 10, "vertices": ((0.0, 0.0), (1.0, 0.0), (0.0, 1.0))},
        {"id": 20, "vertices": ((2.0, 0.0), (3.0, 0.0), (2.0, 1.0))},
    )

    candidate_rows = []
    hit_rows = []
    for ray in rays:
        any_hit = False
        hit_reason = "no_triangle_hit"
        for triangle in triangles:
            hit, reason = _ray_hits_triangle(ray, triangle)
            candidate_rows.append(
                {
                    "ray_id": int(ray["id"]),
                    "triangle_id": int(triangle["id"]),
                    "hit": hit,
                    "reason": reason,
                }
            )
            any_hit = any_hit or hit
            if hit and hit_reason == "no_triangle_hit":
                hit_reason = reason
        hit_rows.append({"ray_id": int(ray["id"]), "any_hit": int(any_hit), "reason": hit_reason})

    plan = rtdl_v4.plan_operator_request_v4("any_hit", partner="torch")
    payload = {
        "status": "ok",
        "concept": "ray/triangle any-hit is relation building: test ray-primitive candidates, emit one compact hit flag per ray",
        "manual_data_flow": (
            "rays + triangles -> candidate hit tests -> per-ray any-hit continuation"
        ),
        "candidate_rows": tuple(candidate_rows),
        "hit_rows": tuple(hit_rows),
        "v4_surface": {
            "operator": "any_hit",
            "partner": "torch",
            "status": plan.status,
            "surface": plan.api_surface,
            "generic_primitive": plan.generic_primitive,
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
