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
from rtdsl.reference import Ray2D
from rtdsl.reference import Triangle


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_any_hit_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_any_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "any_hit"])


def make_case() -> dict[str, tuple[Ray2D, ...] | tuple[Triangle, ...]]:
    return {
        "rays": (
            Ray2D(id=1, ox=-1.0, oy=0.25, dx=1.0, dy=0.0, tmax=4.0),
            Ray2D(id=2, ox=-1.0, oy=2.0, dx=1.0, dy=0.0, tmax=4.0),
        ),
        "triangles": (
            Triangle(id=10, x0=0.0, y0=0.0, x1=1.0, y1=0.0, x2=0.0, y2=1.0),
            Triangle(id=20, x0=2.0, y0=0.0, x1=3.0, y1=0.0, x2=2.0, y2=1.0),
        ),
    }


def _triangle_vertices(triangle: Triangle) -> tuple[tuple[float, float], ...]:
    return (
        (float(triangle.x0), float(triangle.y0)),
        (float(triangle.x1), float(triangle.y1)),
        (float(triangle.x2), float(triangle.y2)),
    )


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


def _ray_segment(ray: Ray2D) -> tuple[tuple[float, float], tuple[float, float]]:
    origin = (float(ray.ox), float(ray.oy))
    end = (
        float(ray.ox) + float(ray.dx) * float(ray.tmax),
        float(ray.oy) + float(ray.dy) * float(ray.tmax),
    )
    return origin, end


def _ray_hits_triangle(ray: Ray2D, triangle: Triangle) -> tuple[bool, str]:
    triangle_vertices = _triangle_vertices(triangle)
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


def run_kernel_mode() -> dict[str, object]:
    case = make_case()
    compiled = rt.compile_kernel(ray_triangle_any_hit_kernel)
    rows = tuple(rt.run_cpu_python_reference(ray_triangle_any_hit_kernel, **case))
    return {
        "mode": "kernel",
        "status": "ok",
        "teaches": (
            "RTDL kernel: input rays and triangles, traverse candidate ray/triangle "
            "pairs, refine(ray_triangle_any_hit), emit one any-hit row per ray"
        ),
        "kernel_summary": compiled.format(),
        "rays": tuple(ray.__dict__ for ray in case["rays"]),
        "triangles": tuple(triangle.__dict__ for triangle in case["triangles"]),
        "any_hit_rows": tuple(
            {"ray_id": int(row["ray_id"]), "any_hit": int(row["any_hit"])}
            for row in rows
        ),
    }


def run_visible_flow() -> dict[str, object]:
    case = make_case()
    rays = case["rays"]
    triangles = case["triangles"]
    candidate_rows = []
    hit_rows = []
    for ray in rays:
        any_hit = False
        hit_reason = "no_triangle_hit"
        for triangle in triangles:
            hit, reason = _ray_hits_triangle(ray, triangle)
            candidate_rows.append(
                {
                    "ray_id": int(ray.id),
                    "triangle_id": int(triangle.id),
                    "hit": hit,
                    "reason": reason,
                }
            )
            any_hit = any_hit or hit
            if hit and hit_reason == "no_triangle_hit":
                hit_reason = reason
        hit_rows.append({"ray_id": int(ray.id), "any_hit": int(any_hit), "reason": hit_reason})

    return {
        "mode": "visible_python_flow",
        "status": "ok",
        "concept": "manual mirror of the ray/triangle relation and per-ray any-hit continuation",
        "manual_data_flow": (
            "rays + triangles -> candidate hit tests -> per-ray any-hit rows"
        ),
        "candidate_rows": tuple(candidate_rows),
        "any_hit_rows": tuple(hit_rows),
    }


def run_v4_mode() -> dict[str, object]:
    plan = rtdl_v4.plan_operator_request_v4("any_hit", partner="torch")
    return {
        "mode": "v4",
        "status": "ok",
        "teaches": "V4 operator/runtime mapping for ray/triangle any-hit rows",
        "operator": "any_hit",
        "partner": "torch",
        "plan_status": plan.status,
        "surface": plan.api_surface,
        "generic_primitive": plan.generic_primitive,
        "relationship_to_kernel": (
            "The kernel teaches the ray/triangle relation. The V4 route is the "
            "prepared execution surface for the same any-hit pattern when the "
            "user chooses a measured partner."
        ),
    }


def run_both_modes() -> dict[str, object]:
    kernel = run_kernel_mode()
    v4 = run_v4_mode()
    return {
        "status": "ok",
        "concept": (
            "ray/triangle any-hit is first an RTDL kernel relation; V4 then maps "
            "that relation to a prepared partner-backed operator surface"
        ),
        "kernel_mode": kernel,
        "visible_flow": run_visible_flow(),
        "v4_mode": v4,
        "same_semantics": {
            "relation": "ray_triangle_any_hit_rows",
            "kernel_output_field": "any_hit_rows",
            "v4_execution_target": v4["surface"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="RTDL ray/triangle hit tutorial")
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
