from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def hiprt_ray_triangle_hitcount_kernel():
    rays = rt.input("rays", rt.Rays3D, layout=rt.Ray3DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles3D, layout=rt.Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


def make_scene() -> tuple[tuple[rt.Ray3D, ...], tuple[rt.Ray3D, ...], tuple[rt.Triangle3D, ...]]:
    triangles = (
        rt.Triangle3D(
            id=10,
            x0=0.0,
            y0=0.0,
            z0=0.0,
            x1=1.0,
            y1=0.0,
            z1=0.0,
            x2=0.0,
            y2=1.0,
            z2=0.0,
        ),
        rt.Triangle3D(
            id=11,
            x0=0.0,
            y0=0.0,
            z0=1.0,
            x1=1.0,
            y1=0.0,
            z1=1.0,
            x2=0.0,
            y2=1.0,
            z2=1.0,
        ),
    )
    first_rays = (
        rt.Ray3D(id=1, ox=0.25, oy=0.25, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=3.0),
        rt.Ray3D(id=2, ox=2.0, oy=2.0, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=3.0),
        rt.Ray3D(id=3, ox=0.25, oy=0.25, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=0.5),
    )
    second_rays = (
        rt.Ray3D(id=4, ox=0.75, oy=0.05, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=2.0),
        rt.Ray3D(id=5, ox=3.0, oy=3.0, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=2.0),
    )
    return first_rays, second_rays, triangles


def _row_list(rows) -> list[dict[str, int]]:
    return [{"ray_id": int(row["ray_id"]), "hit_count": int(row["hit_count"])} for row in rows]


def main() -> int:
    first_rays, second_rays, triangles = make_scene()
    cpu_first = rt.run_cpu_python_reference(
        hiprt_ray_triangle_hitcount_kernel,
        rays=first_rays,
        triangles=triangles,
    )
    cpu_second = rt.run_cpu_python_reference(
        hiprt_ray_triangle_hitcount_kernel,
        rays=second_rays,
        triangles=triangles,
    )

    result: dict[str, object] = {
        "example": "hiprt_ray_triangle_hitcount",
        "scope": (
            "v0.9 HIPRT candidate prepared-path example for Ray3D/Triangle3D "
            "ray_triangle_hit_count; broader run_hiprt coverage is tracked by the 18-workload matrix"
        ),
        "cpu_python_reference": {
            "first_batch": _row_list(cpu_first),
            "second_batch": _row_list(cpu_second),
        },
    }

    try:
        result["hiprt_probe"] = rt.hiprt_context_probe()
        run_rows = rt.run_hiprt(
            hiprt_ray_triangle_hitcount_kernel,
            rays=first_rays,
            triangles=triangles,
        )
        with rt.prepare_hiprt(hiprt_ray_triangle_hitcount_kernel, triangles=triangles) as prepared:
            prepared_first = prepared.run(rays=first_rays)
            prepared_second = prepared.run(rays=second_rays)
        result["hiprt_available"] = True
        result["run_hiprt"] = _row_list(run_rows)
        result["prepare_hiprt"] = {
            "first_batch": _row_list(prepared_first),
            "second_batch": _row_list(prepared_second),
        }
        result["parity"] = {
            "run_hiprt_first_batch": tuple(run_rows) == tuple(cpu_first),
            "prepare_hiprt_first_batch": tuple(prepared_first) == tuple(cpu_first),
            "prepare_hiprt_second_batch": tuple(prepared_second) == tuple(cpu_second),
        }
    except (FileNotFoundError, OSError, RuntimeError) as exc:
        result["hiprt_available"] = False
        result["hiprt_error"] = str(exc).splitlines()[0]

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
