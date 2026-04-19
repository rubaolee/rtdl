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
def fixed_radius_3d_kernel():
    query_points = rt.input("query_points", rt.Points3D, layout=rt.Point3DLayout, role="probe")
    search_points = rt.input("search_points", rt.Points3D, layout=rt.Point3DLayout, role="build")
    candidates = rt.traverse(query_points, search_points, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.fixed_radius_neighbors(radius=1.05, k_max=16))
    return rt.emit(hits, fields=["query_id", "neighbor_id", "distance"])


def make_case(query_count: int, search_count: int) -> tuple[tuple[rt.Point3D, ...], tuple[rt.Point3D, ...]]:
    width = max(1, int(search_count**0.5))
    search_points = []
    for i in range(search_count):
        x = float(i % width)
        y = float((i // width) % width)
        z = float((i // (width * width)) % 5) * 0.25
        search_points.append(rt.Point3D(id=i, x=x, y=y, z=z))
    query_points = []
    for i in range(query_count):
        x = float((i * 3) % width) + 0.1
        y = float(((i * 7) // width) % width) + 0.1
        z = float(i % 5) * 0.25
        query_points.append(rt.Point3D(id=i, x=x, y=y, z=z))
    return tuple(query_points), tuple(search_points)


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


def rows_close(left: tuple[dict[str, object], ...], right: tuple[dict[str, object], ...]) -> bool:
    if len(left) != len(right):
        return False
    left_sorted = sorted(left, key=lambda row: (int(row["query_id"]), int(row["neighbor_id"])))
    right_sorted = sorted(right, key=lambda row: (int(row["query_id"]), int(row["neighbor_id"])))
    for left_row, right_row in zip(left_sorted, right_sorted):
        if int(left_row["query_id"]) != int(right_row["query_id"]):
            return False
        if int(left_row["neighbor_id"]) != int(right_row["neighbor_id"]):
            return False
        if abs(float(left_row["distance"]) - float(right_row["distance"])) > 1.0e-5:
            return False
    return True


def run_prepared_nn_perf(*, query_count: int, search_count: int, repeats: int) -> dict[str, object]:
    query_points, search_points = make_case(query_count, search_count)
    cpu = measure(
        lambda: rt.run_cpu_python_reference(
            fixed_radius_3d_kernel,
            query_points=query_points,
            search_points=search_points,
        ),
        1,
    )

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
            measured = measure(
                lambda runner=runner: runner(
                    fixed_radius_3d_kernel,
                    query_points=query_points,
                    search_points=search_points,
                ),
                1,
            )
            parity = rows_close(measured["rows"], cpu["rows"])
            results[name] = {
                "status": "PASS" if parity else "FAIL",
                "parity_vs_cpu_reference": parity,
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
        prepared = rt.prepare_hiprt(fixed_radius_3d_kernel, search_points=search_points)
        prepare_seconds = time.perf_counter() - started
        try:
            measured = measure(lambda: prepared.run(query_points=query_points), repeats)
        finally:
            prepared.close()
        parity = rows_close(measured["rows"], cpu["rows"])
        results["hiprt_prepared"] = {
            "status": "PASS" if parity else "FAIL",
            "parity_vs_cpu_reference": parity,
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
        "goal": 566,
        "description": "HIPRT prepared 3D fixed-radius nearest-neighbor performance mitigation benchmark",
        "query_count": query_count,
        "search_count": search_count,
        "radius": 1.05,
        "k_max": 16,
        "repeats": repeats,
        "results": results,
        "honesty_boundary": (
            "This isolates prepared reuse for 3D fixed-radius nearest neighbors. It does not yet claim prepared "
            "coverage for 2D neighbors, KNN ranking helpers, graph CSR, DB tables, AMD GPUs, or RT-core speedup."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark prepared HIPRT 3D fixed-radius neighbor query reuse.")
    parser.add_argument("--queries", type=int, default=1024)
    parser.add_argument("--search", type=int, default=4096)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.queries <= 0 or args.search <= 0 or args.repeats <= 0:
        raise ValueError("--queries, --search, and --repeats must be positive")
    payload = run_prepared_nn_perf(query_count=args.queries, search_count=args.search, repeats=args.repeats)
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    statuses = [value.get("status") for value in payload["results"].values() if isinstance(value, dict)]
    return 1 if "FAIL" in statuses else 0


if __name__ == "__main__":
    raise SystemExit(main())
