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
def rtxrmq_threshold_hitcount_kernel():
    query_rays = rt.input("query_rays", rt.Rays3D, layout=rt.Ray3DLayout, role="probe")
    element_triangles = rt.input("element_triangles", rt.Triangles3D, layout=rt.Triangle3DLayout, role="build")
    candidates = rt.traverse(query_rays, element_triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


def make_values(count: int) -> tuple[float, ...]:
    if count <= 0:
        raise ValueError("count must be positive")
    return tuple(((index * 37) % 997) / 996.0 for index in range(count))


def make_rmq_queries(count: int, value_count: int, max_range: int) -> tuple[tuple[int, int], ...]:
    if count <= 0 or value_count <= 0 or max_range <= 0:
        raise ValueError("count, value_count, and max_range must be positive")
    queries: list[tuple[int, int]] = []
    for query_id in range(count):
        length = 1 + ((query_id * 17) % min(max_range, value_count))
        left = (query_id * 131) % max(1, value_count - length + 1)
        right = left + length - 1
        queries.append((left, right))
    return tuple(queries)


def exact_rmq_cpu(values: tuple[float, ...], queries: tuple[tuple[int, int], ...]) -> tuple[dict[str, float | int], ...]:
    rows: list[dict[str, float | int]] = []
    for query_id, (left, right) in enumerate(queries):
        if left < 0 or right >= len(values) or left > right:
            raise ValueError(f"invalid RMQ query {(left, right)} for {len(values)} values")
        best_index = left
        best_value = values[left]
        for index in range(left + 1, right + 1):
            value = values[index]
            if value < best_value:
                best_index = index
                best_value = value
        rows.append({"query_id": query_id, "index": best_index, "value": best_value})
    return tuple(rows)


def make_threshold_queries(
    rmq_rows: tuple[dict[str, float | int], ...],
    queries: tuple[tuple[int, int], ...],
    *,
    threshold_slack: float = 0.05,
) -> tuple[tuple[int, int, float], ...]:
    threshold_queries = []
    for row, (left, right) in zip(rmq_rows, queries):
        threshold = min(1.0, float(row["value"]) + threshold_slack)
        threshold_queries.append((left, right, threshold))
    return tuple(threshold_queries)


def make_rtxrmq_like_triangles(values: tuple[float, ...]) -> tuple[rt.Triangle3D, ...]:
    triangles = []
    for index, value in enumerate(values):
        # One YZ-aligned triangle per array element, positioned on X by element
        # index and spanning thresholds from its value upward.
        triangles.append(
            rt.Triangle3D(
                id=index,
                x0=float(index),
                y0=float(value),
                z0=-0.5,
                x1=float(index),
                y1=1.0,
                z1=0.0,
                x2=float(index),
                y2=float(value),
                z2=0.5,
            )
        )
    return tuple(triangles)


def make_threshold_rays(threshold_queries: tuple[tuple[int, int, float], ...]) -> tuple[rt.Ray3D, ...]:
    rays = []
    for query_id, (left, right, threshold) in enumerate(threshold_queries):
        rays.append(
            rt.Ray3D(
                id=query_id,
                ox=float(left) - 0.5,
                oy=float(threshold),
                oz=0.0,
                dx=1.0,
                dy=0.0,
                dz=0.0,
                tmax=float(right - left + 1),
            )
        )
    return tuple(rays)


def threshold_count_cpu(
    values: tuple[float, ...],
    threshold_queries: tuple[tuple[int, int, float], ...],
) -> tuple[dict[str, int], ...]:
    rows = []
    for query_id, (left, right, threshold) in enumerate(threshold_queries):
        count = sum(1 for index in range(left, right + 1) if values[index] <= threshold)
        rows.append({"ray_id": query_id, "hit_count": count})
    return tuple(rows)


def row_signature(rows: tuple[dict[str, object], ...]) -> tuple[tuple[int, int], ...]:
    return tuple(sorted((int(row["ray_id"]), int(row["hit_count"])) for row in rows))


def _safe_version(fn: Callable[[], object]) -> str:
    try:
        return str(fn())
    except Exception as exc:
        return f"unavailable: {type(exc).__name__}: {exc}"


def _command(cmd: list[str]) -> str | None:
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT, timeout=5).strip()
    except Exception:
        return None


def host_info() -> dict[str, object]:
    return {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "nvidia_smi": _command(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "embree_version": _safe_version(rt.embree_version),
        "optix_version": _safe_version(rt.optix_version),
        "vulkan_version": _safe_version(rt.vulkan_version),
        "hiprt_version": _safe_version(rt.hiprt_version),
    }


def median_seconds(fn: Callable[[], tuple[dict[str, object], ...]], iterations: int) -> tuple[dict[str, object], ...]:
    samples = []
    rows: tuple[dict[str, object], ...] | None = None
    for _ in range(iterations):
        gc.collect()
        start = time.perf_counter()
        rows = tuple(fn())
        samples.append(time.perf_counter() - start)
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


def run_backend(
    backend: str,
    query_rays: tuple[rt.Ray3D, ...],
    element_triangles: tuple[rt.Triangle3D, ...],
    iterations: int,
) -> dict[str, object]:
    runners = {
        "cpu_python_reference": rt.run_cpu_python_reference,
        "embree": rt.run_embree,
        "optix": rt.run_optix,
        "vulkan": rt.run_vulkan,
        "hiprt_one_shot": rt.run_hiprt,
    }
    try:
        timing, rows = median_seconds(
            lambda: runners[backend](
                rtxrmq_threshold_hitcount_kernel,
                query_rays=query_rays,
                element_triangles=element_triangles,
            ),
            iterations,
        )
        return {
            "status": "ok",
            **timing,
            "row_count": len(rows),
            "signature": row_signature(rows),
        }
    except Exception as exc:
        return {"status": "error", "error_type": type(exc).__name__, "message": str(exc).splitlines()[0]}


def run_prepared_hiprt(
    query_rays: tuple[rt.Ray3D, ...],
    element_triangles: tuple[rt.Triangle3D, ...],
    iterations: int,
) -> dict[str, object]:
    try:
        start = time.perf_counter()
        prepared = rt.prepare_hiprt(rtxrmq_threshold_hitcount_kernel, element_triangles=element_triangles)
        prepare_seconds = time.perf_counter() - start
        try:
            timing, rows = median_seconds(lambda: prepared.run(query_rays=query_rays), iterations)
        finally:
            prepared.close()
        return {
            "status": "ok",
            "prepare_seconds": prepare_seconds,
            **timing,
            "row_count": len(rows),
            "signature": row_signature(rows),
        }
    except Exception as exc:
        return {"status": "error", "error_type": type(exc).__name__, "message": str(exc).splitlines()[0]}


def run_goal571(*, values: int, queries: int, max_range: int, iterations: int) -> dict[str, object]:
    array_values = make_values(values)
    rmq_queries = make_rmq_queries(queries, values, max_range)
    rmq_rows = exact_rmq_cpu(array_values, rmq_queries)
    threshold_queries = make_threshold_queries(rmq_rows, rmq_queries)
    element_triangles = make_rtxrmq_like_triangles(array_values)
    query_rays = make_threshold_rays(threshold_queries)

    threshold_oracle = threshold_count_cpu(array_values, threshold_queries)
    threshold_signature = row_signature(threshold_oracle)
    rt_cpu_signature = row_signature(tuple(rt.ray_triangle_hit_count_cpu(query_rays, element_triangles)))

    results = {
        "goal": 571,
        "paper": {
            "path": "/Users/rl2025/Downloads/2306.03282v1.pdf",
            "arxiv_id": "2306.03282v1",
            "title": "Accelerating Range Minimum Queries with Ray Tracing Cores",
        },
        "host": host_info(),
        "case": {
            "value_count": values,
            "query_count": queries,
            "max_range": max_range,
            "triangle_count": len(element_triangles),
            "ray_count": len(query_rays),
            "iterations": iterations,
        },
        "exact_rmq_cpu": {
            "status": "ok",
            "row_count": len(rmq_rows),
            "sample_rows": list(rmq_rows[:5]),
        },
        "rtdl_supported_workload": {
            "name": "rtxrmq_range_threshold_hitcount_analogue",
            "description": (
                "One YZ-aligned triangle per array element and one +X ray per query range. "
                "The returned hit_count is the number of values in [l,r] at or below a threshold."
            ),
            "oracle_row_count": len(threshold_oracle),
            "oracle_sample_rows": list(threshold_oracle[:5]),
            "matches_direct_cpu_ray_triangle_reference": rt_cpu_signature == threshold_signature,
        },
        "backends": {},
        "honesty_boundary": (
            "This is a paper-derived traversal subworkload, not full RTXRMQ. Full RTXRMQ needs a closest-hit/argmin "
            "result carrying the hit element id/value; RTDL v0.9 exposes ray_triangle_hit_count but not a public "
            "ray_triangle_closest_hit primitive."
        ),
    }

    for backend in ("cpu_python_reference", "embree", "optix", "vulkan", "hiprt_one_shot"):
        backend_result = run_backend(backend, query_rays, element_triangles, iterations)
        if backend_result["status"] == "ok":
            backend_result["matches_threshold_oracle"] = backend_result["signature"] == threshold_signature
            backend_result.pop("signature", None)
        results["backends"][backend] = backend_result

    prepared = run_prepared_hiprt(query_rays, element_triangles, iterations)
    if prepared["status"] == "ok":
        prepared["matches_threshold_oracle"] = prepared["signature"] == threshold_signature
        prepared.pop("signature", None)
    results["backends"]["hiprt_prepared"] = prepared
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal 571 RTXRMQ paper-derived RTDL workload engine comparison.")
    parser.add_argument("--values", type=int, default=2048)
    parser.add_argument("--queries", type=int, default=1024)
    parser.add_argument("--max-range", type=int, default=64)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_goal571(values=args.values, queries=args.queries, max_range=args.max_range, iterations=args.iterations)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
