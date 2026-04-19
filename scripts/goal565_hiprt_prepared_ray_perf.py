from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys
import time
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def ray_triangle_3d_kernel():
    rays = rt.input("rays", rt.Rays3D, layout=rt.Ray3DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles3D, layout=rt.Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


def make_case(ray_count: int, triangle_count: int) -> tuple[tuple[rt.Ray3D, ...], tuple[rt.Triangle3D, ...]]:
    triangles = []
    grid_width = max(1, int(triangle_count**0.5))
    for i in range(triangle_count):
        x = float(i % grid_width)
        y = float(i // grid_width)
        z = float(i % 7) * 0.125
        triangles.append(
            rt.Triangle3D(
                id=i,
                x0=x,
                y0=y,
                z0=z,
                x1=x + 0.75,
                y1=y,
                z1=z,
                x2=x,
                y2=y + 0.75,
                z2=z,
            )
        )
    rays = []
    for i in range(ray_count):
        x = float(i % grid_width) + 0.2
        y = float((i // grid_width) % grid_width) + 0.2
        rays.append(rt.Ray3D(id=i, ox=x, oy=y, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=4.0))
    return tuple(rays), tuple(triangles)


def measure(fn: Callable[[], tuple[dict[str, object], ...]], repeats: int) -> dict[str, object]:
    rows = None
    timings = []
    for _ in range(repeats):
        started = time.perf_counter()
        rows = fn()
        timings.append(time.perf_counter() - started)
    assert rows is not None
    return {
        "row_count": len(rows),
        "rows": tuple(rows),
        "seconds": timings,
        "median_seconds": statistics.median(timings),
        "min_seconds": min(timings),
        "max_seconds": max(timings),
    }


def run_prepared_perf(*, ray_count: int, triangle_count: int, repeats: int) -> dict[str, object]:
    rays, triangles = make_case(ray_count, triangle_count)
    cpu = measure(lambda: rt.run_cpu_python_reference(ray_triangle_3d_kernel, rays=rays, triangles=triangles), 1)

    results: dict[str, object] = {
        "cpu_python_reference": {
            "row_count": cpu["row_count"],
            "seconds": cpu["seconds"],
            "median_seconds": cpu["median_seconds"],
        }
    }

    for name, runner in (
        ("embree", rt.run_embree),
        ("optix", rt.run_optix),
        ("vulkan", rt.run_vulkan),
        ("hiprt_one_shot", rt.run_hiprt),
    ):
        try:
            measured = measure(lambda runner=runner: runner(ray_triangle_3d_kernel, rays=rays, triangles=triangles), 1)
            results[name] = {
                "status": "PASS" if measured["rows"] == cpu["rows"] else "FAIL",
                "parity_vs_cpu_reference": measured["rows"] == cpu["rows"],
                "row_count": measured["row_count"],
                "seconds": measured["seconds"],
                "median_seconds": measured["median_seconds"],
            }
        except (FileNotFoundError, OSError, NotImplementedError) as exc:
            results[name] = {
                "status": "UNAVAILABLE",
                "error_type": type(exc).__name__,
                "message": str(exc).splitlines()[0],
            }

    try:
        started = time.perf_counter()
        prepared = rt.prepare_hiprt(ray_triangle_3d_kernel, triangles=triangles)
        prepare_seconds = time.perf_counter() - started
        try:
            measured = measure(lambda: prepared.run(rays=rays), repeats)
        finally:
            prepared.close()
        results["hiprt_prepared"] = {
            "status": "PASS" if measured["rows"] == cpu["rows"] else "FAIL",
            "parity_vs_cpu_reference": measured["rows"] == cpu["rows"],
            "row_count": measured["row_count"],
            "prepare_seconds": prepare_seconds,
            "query_seconds": measured["seconds"],
            "query_median_seconds": measured["median_seconds"],
            "query_min_seconds": measured["min_seconds"],
            "query_max_seconds": measured["max_seconds"],
        }
        one_shot = results.get("hiprt_one_shot", {})
        if isinstance(one_shot, dict) and one_shot.get("status") == "PASS":
            one_shot_seconds = float(one_shot["median_seconds"])
            prepared_seconds = float(measured["median_seconds"])
            results["hiprt_prepared"]["one_shot_to_prepared_query_speedup"] = one_shot_seconds / prepared_seconds
    except (FileNotFoundError, OSError, NotImplementedError) as exc:
        results["hiprt_prepared"] = {
            "status": "UNAVAILABLE",
            "error_type": type(exc).__name__,
            "message": str(exc).splitlines()[0],
        }

    return {
        "goal": 565,
        "description": "HIPRT prepared 3D ray/triangle performance mitigation benchmark",
        "ray_count": ray_count,
        "triangle_count": triangle_count,
        "repeats": repeats,
        "results": results,
        "honesty_boundary": (
            "This isolates the already-prepared 3D ray/triangle HIPRT path. It is not broad prepared coverage "
            "for all 18 v0.9 workloads and is not an AMD GPU or RT-core speedup claim."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark prepared HIPRT 3D ray/triangle query reuse.")
    parser.add_argument("--rays", type=int, default=1024)
    parser.add_argument("--triangles", type=int, default=2048)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.rays <= 0 or args.triangles <= 0 or args.repeats <= 0:
        raise ValueError("--rays, --triangles, and --repeats must be positive")
    payload = run_prepared_perf(ray_count=args.rays, triangle_count=args.triangles, repeats=args.repeats)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    statuses = [value.get("status") for value in payload["results"].values() if isinstance(value, dict)]
    return 1 if "FAIL" in statuses else 0


if __name__ == "__main__":
    raise SystemExit(main())
