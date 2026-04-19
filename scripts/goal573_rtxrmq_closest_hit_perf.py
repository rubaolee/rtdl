from __future__ import annotations

import argparse
import gc
import json
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def rtxrmq_closest_hit_kernel():
    query_rays = rt.input("query_rays", rt.Rays3D, layout=rt.Ray3DLayout, role="probe")
    element_triangles = rt.input("element_triangles", rt.Triangles3D, layout=rt.Triangle3DLayout, role="build")
    candidates = rt.traverse(query_rays, element_triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_closest_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "triangle_id", "t"])


def make_values(count: int) -> tuple[float, ...]:
    if count <= 0:
        raise ValueError("count must be positive")
    return tuple(((index * 37) % 997) / 996.0 for index in range(count))


def make_queries(count: int, value_count: int, max_range: int) -> tuple[tuple[int, int], ...]:
    if count <= 0 or value_count <= 0 or max_range <= 0:
        raise ValueError("count, value_count, and max_range must be positive")
    queries = []
    for query_id in range(count):
        length = 1 + ((query_id * 17) % min(max_range, value_count))
        left = (query_id * 131) % max(1, value_count - length + 1)
        queries.append((left, left + length - 1))
    return tuple(queries)


def exact_rmq_cpu(values: tuple[float, ...], queries: tuple[tuple[int, int], ...]) -> tuple[dict[str, float | int], ...]:
    rows = []
    for query_id, (left, right) in enumerate(queries):
        best_index = left
        best_value = values[left]
        for index in range(left + 1, right + 1):
            value = values[index]
            if value < best_value:
                best_index = index
                best_value = value
        rows.append({"query_id": query_id, "index": best_index, "value": best_value})
    return tuple(rows)


def make_rmq_triangles(values: tuple[float, ...]) -> tuple[rt.Triangle3D, ...]:
    # For element i, the YZ footprint covers all query points (l, r) where
    # l <= i <= r. X is the element value, so closest +X hit is the minimum.
    n = float(len(values))
    triangles = []
    for index, value in enumerate(values):
        x = float(value)
        y0 = 0.0
        y1 = float(index + 1)
        z0 = float(index)
        z1 = n
        base = index * 2
        triangles.append(rt.Triangle3D(id=base, x0=x, y0=y0, z0=z0, x1=x, y1=y1, z1=z0, x2=x, y2=y1, z2=z1))
        triangles.append(rt.Triangle3D(id=base + 1, x0=x, y0=y0, z0=z0, x1=x, y1=y1, z1=z1, x2=x, y2=y0, z2=z1))
    return tuple(triangles)


def make_query_rays(queries: tuple[tuple[int, int], ...]) -> tuple[rt.Ray3D, ...]:
    return tuple(
        rt.Ray3D(id=query_id, ox=-1.0, oy=float(left) + 0.5, oz=float(right) + 0.5, dx=1.0, dy=0.0, dz=0.0, tmax=3.0)
        for query_id, (left, right) in enumerate(queries)
    )


def closest_rows_to_rmq(rows: tuple[dict[str, object], ...], values: tuple[float, ...]) -> tuple[dict[str, float | int], ...]:
    converted = []
    for row in sorted(rows, key=lambda item: int(item["ray_id"])):
        index = int(row["triangle_id"]) // 2
        converted.append({"query_id": int(row["ray_id"]), "index": index, "value": values[index]})
    return tuple(converted)


def _command(cmd: list[str]) -> str | None:
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT, timeout=5).strip()
    except Exception:
        return None


def _safe_version(fn: Callable[[], object]) -> str:
    try:
        return str(fn())
    except Exception as exc:
        return f"unavailable: {type(exc).__name__}: {exc}"


def measure(fn: Callable[[], tuple[dict[str, object], ...]], iterations: int) -> tuple[dict[str, object], tuple[dict[str, object], ...]]:
    samples = []
    rows = None
    for _ in range(iterations):
        gc.collect()
        started = time.perf_counter()
        rows = tuple(fn())
        samples.append(time.perf_counter() - started)
    assert rows is not None
    return (
        {
            "iterations": iterations,
            "median_seconds": statistics.median(samples),
            "min_seconds": min(samples),
            "max_seconds": max(samples),
        },
        rows,
    )


def run_goal573(*, values_count: int, query_count: int, max_range: int, iterations: int) -> dict[str, object]:
    values = make_values(values_count)
    queries = make_queries(query_count, values_count, max_range)
    expected = exact_rmq_cpu(values, queries)
    rays = make_query_rays(queries)
    triangles = make_rmq_triangles(values)
    result: dict[str, object] = {
        "goal": 573,
        "paper": {
            "path": "/Users/rl2025/Downloads/2306.03282v1.pdf",
            "arxiv_id": "2306.03282v1",
            "title": "Accelerating Range Minimum Queries with Ray Tracing Cores",
        },
        "host": {
            "hostname": platform.node(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "nvidia_smi": _command(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
            "embree_version": _safe_version(rt.embree_version),
            "optix_version": _safe_version(rt.optix_version),
            "vulkan_version": _safe_version(rt.vulkan_version),
            "hiprt_version": _safe_version(rt.hiprt_version),
        },
        "case": {
            "value_count": values_count,
            "query_count": query_count,
            "max_range": max_range,
            "triangle_count": len(triangles),
            "ray_count": len(rays),
            "iterations": iterations,
        },
        "expected_sample": list(expected[:5]),
        "backends": {},
        "honesty_boundary": (
            "This is an exact bounded RTXRMQ-style RMQ implementation using the new RTDL "
            "ray_triangle_closest_hit primitive. In this first closure, CPU reference and Embree "
            "are implemented; OptiX, Vulkan, and HIPRT closest-hit kernels remain future native work."
        ),
    }
    for name, runner in (
        ("cpu_python_reference", rt.run_cpu_python_reference),
        ("embree", rt.run_embree),
    ):
        try:
            timing, rows = measure(lambda runner=runner: runner(rtxrmq_closest_hit_kernel, query_rays=rays, element_triangles=triangles), iterations)
            rmq_rows = closest_rows_to_rmq(rows, values)
            result["backends"][name] = {
                "status": "ok",
                **timing,
                "row_count": len(rows),
                "matches_exact_rmq": rmq_rows == expected,
                "sample_rows": list(rmq_rows[:5]),
            }
        except Exception as exc:
            result["backends"][name] = {"status": "error", "error_type": type(exc).__name__, "message": str(exc).splitlines()[0]}
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal 573 exact RTXRMQ closest-hit workload.")
    parser.add_argument("--values", type=int, default=2048)
    parser.add_argument("--queries", type=int, default=1024)
    parser.add_argument("--max-range", type=int, default=128)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_goal573(values_count=args.values, query_count=args.queries, max_range=args.max_range, iterations=args.iterations)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
