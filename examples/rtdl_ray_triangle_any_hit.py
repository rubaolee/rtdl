from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_any_hit_demo():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray2DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle2DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_any_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "any_hit"])


def main() -> None:
    rays = (
        rt.Ray2D(id=1, ox=0.0, oy=0.0, dx=1.0, dy=0.0, tmax=10.0),
        rt.Ray2D(id=2, ox=0.0, oy=0.0, dx=0.0, dy=1.0, tmax=2.0),
    )
    triangles = (
        rt.Triangle(id=10, x0=2.0, y0=-1.0, x1=3.0, y1=1.0, x2=4.0, y2=-1.0),
        rt.Triangle(id=11, x0=6.0, y0=-1.0, x1=7.0, y1=1.0, x2=8.0, y2=-1.0),
    )

    cpu_python_rows = rt.run_cpu_python_reference(ray_triangle_any_hit_demo, rays=rays, triangles=triangles)
    cpu_oracle_rows = rt.run_cpu(ray_triangle_any_hit_demo, rays=rays, triangles=triangles)

    print(
        json.dumps(
            {
                "workload": "ray_triangle_any_hit",
                "description": "Each ray becomes one boolean row; traversal may stop after the first accepted triangle hit.",
                "cpu_python_reference": list(cpu_python_rows),
                "cpu_oracle": list(cpu_oracle_rows),
                "parity": cpu_python_rows == cpu_oracle_rows,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
