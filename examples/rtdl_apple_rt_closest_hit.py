from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def apple_rt_closest_hit_kernel():
    rays = rt.input("rays", rt.Rays, layout=rt.Ray3DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles, layout=rt.Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_closest_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "triangle_id", "t"])


def make_scene() -> tuple[tuple[rt.Ray3D, ...], tuple[rt.Triangle3D, ...]]:
    rays = (
        rt.Ray3D(id=1, ox=-1.0, oy=0.0, oz=0.0, dx=1.0, dy=0.0, dz=0.0, tmax=3.0),
        rt.Ray3D(id=2, ox=-1.0, oy=2.0, oz=0.0, dx=1.0, dy=0.0, dz=0.0, tmax=3.0),
        rt.Ray3D(id=3, ox=-1.0, oy=0.0, oz=0.0, dx=1.0, dy=0.0, dz=0.0, tmax=0.1),
    )
    triangles = (
        rt.Triangle3D(id=10, x0=0.7, y0=-1.0, z0=-1.0, x1=0.7, y1=1.0, z1=0.0, x2=0.7, y2=-1.0, z2=1.0),
        rt.Triangle3D(id=11, x0=0.2, y0=-1.0, z0=-1.0, x1=0.2, y1=1.0, z1=0.0, x2=0.2, y2=-1.0, z2=1.0),
    )
    return rays, triangles


def _rows(rows) -> list[dict[str, int | float]]:
    return [
        {
            "ray_id": int(row["ray_id"]),
            "triangle_id": int(row["triangle_id"]),
            "t": float(row["t"]),
        }
        for row in rows
    ]


def _same_rows_approx(left, right, *, tolerance: float = 1e-5) -> bool:
    left_rows = list(left)
    right_rows = list(right)
    if len(left_rows) != len(right_rows):
        return False
    for left_row, right_row in zip(left_rows, right_rows):
        if int(left_row["ray_id"]) != int(right_row["ray_id"]):
            return False
        if int(left_row["triangle_id"]) != int(right_row["triangle_id"]):
            return False
        if abs(float(left_row["t"]) - float(right_row["t"])) > tolerance:
            return False
    return True


def main() -> int:
    rays, triangles = make_scene()
    cpu_rows = rt.run_cpu_python_reference(apple_rt_closest_hit_kernel, rays=rays, triangles=triangles)
    result: dict[str, object] = {
        "example": "apple_rt_closest_hit",
        "scope": "v0.9.1 released Apple Metal/MPS closest-hit example for Ray3D/Triangle3D",
        "cpu_python_reference": _rows(cpu_rows),
    }
    try:
        result["apple_rt_probe"] = rt.apple_rt_context_probe()
        apple_rows = rt.run_apple_rt(apple_rt_closest_hit_kernel, rays=rays, triangles=triangles)
        result["apple_rt_available"] = True
        result["run_apple_rt"] = _rows(apple_rows)
        result["parity"] = _same_rows_approx(apple_rows, cpu_rows)
    except (FileNotFoundError, OSError, RuntimeError, NotImplementedError, ValueError) as exc:
        result["apple_rt_available"] = False
        result["apple_rt_error"] = str(exc).splitlines()[0]

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
