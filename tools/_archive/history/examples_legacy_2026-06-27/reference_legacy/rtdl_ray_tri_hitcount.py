from __future__ import annotations

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_hitcount_reference():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


def make_random_triangles(count: int, *, seed: int = 7) -> tuple[rt.Triangle, ...]:
    rng = random.Random(seed)
    triangles = []
    for index in range(count):
        cx = rng.uniform(-10.0, 10.0)
        cy = rng.uniform(-10.0, 10.0)
        scale = rng.uniform(0.25, 2.0)
        angles = [rng.uniform(0.0, math.tau) for _ in range(3)]
        vertices = [
            (cx + math.cos(angle) * scale, cy + math.sin(angle) * scale)
            for angle in angles
        ]
        triangles.append(
            rt.Triangle(
                id=index,
                x0=vertices[0][0],
                y0=vertices[0][1],
                x1=vertices[1][0],
                y1=vertices[1][1],
                x2=vertices[2][0],
                y2=vertices[2][1],
            )
        )
    return tuple(triangles)


def make_center_rays(
    count: int,
    *,
    center_x: float = 0.0,
    center_y: float = 0.0,
    max_length: float = 12.0,
    seed: int = 11,
) -> tuple[rt.Ray2D, ...]:
    rng = random.Random(seed)
    rays = []
    for index in range(count):
        angle = rng.uniform(0.0, math.tau)
        length = rng.uniform(0.1, max_length)
        rays.append(
            rt.Ray2D(
                id=index,
                ox=center_x,
                oy=center_y,
                dx=math.cos(angle),
                dy=math.sin(angle),
                tmax=length,
            )
        )
    return tuple(rays)


RAY_QUERY_REFERENCE_KERNELS = (ray_triangle_hitcount_reference,)
