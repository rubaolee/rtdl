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
def bfs_kernel():
    frontier = rt.input("frontier", rt.VertexFrontier, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    visited = rt.input("visited", rt.VertexSet, role="probe")
    candidates = rt.traverse(frontier, graph, accel="bvh", mode="graph_expand")
    fresh = rt.refine(candidates, predicate=rt.bfs_discover(visited=visited, dedupe=True))
    return rt.emit(fresh, fields=["src_vertex", "dst_vertex", "level"])


@rt.kernel(backend="rtdl", precision="float_approx")
def bfs_no_dedupe_kernel():
    frontier = rt.input("frontier", rt.VertexFrontier, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    visited = rt.input("visited", rt.VertexSet, role="probe")
    candidates = rt.traverse(frontier, graph, accel="bvh", mode="graph_expand")
    fresh = rt.refine(candidates, predicate=rt.bfs_discover(visited=visited, dedupe=False))
    return rt.emit(fresh, fields=["src_vertex", "dst_vertex", "level"])


@rt.kernel(backend="rtdl", precision="float_approx")
def triangle_match_kernel():
    seeds = rt.input("seeds", rt.EdgeSet, role="probe")
    graph = rt.input("graph", rt.GraphCSR, role="build")
    candidates = rt.traverse(seeds, graph, accel="bvh", mode="graph_intersect")
    triangles = rt.refine(candidates, predicate=rt.triangle_match(order="id_ascending", unique=True))
    return rt.emit(triangles, fields=["u", "v", "w"])


def make_graph(vertex_count: int, degree: int) -> rt.CSRGraph:
    adjacency: list[list[int]] = []
    for vertex in range(vertex_count):
        neighbors = set()
        for step in range(1, degree + 1):
            neighbors.add((vertex + step) % vertex_count)
            neighbors.add((vertex - step) % vertex_count)
        adjacency.append(sorted(neighbors))
    row_offsets = [0]
    columns: list[int] = []
    for neighbors in adjacency:
        columns.extend(neighbors)
        row_offsets.append(len(columns))
    return rt.csr_graph(row_offsets=tuple(row_offsets), column_indices=tuple(columns))


def make_bfs_inputs(vertex_count: int, frontier_count: int) -> tuple[tuple[rt.FrontierVertex, ...], tuple[int, ...]]:
    frontier = tuple(rt.FrontierVertex(vertex_id=i * 3 % vertex_count, level=1) for i in range(frontier_count))
    visited = tuple(range(0, min(vertex_count, frontier_count), 2))
    return frontier, visited


def make_triangle_seeds(vertex_count: int, seed_count: int) -> tuple[rt.EdgeSeed, ...]:
    return tuple(rt.EdgeSeed(i % vertex_count, (i + 1) % vertex_count) for i in range(seed_count))


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


def backend_measurements(
    kernel,
    inputs: dict[str, object],
    reference_rows: tuple[dict[str, object], ...],
) -> dict[str, object]:
    results: dict[str, object] = {}
    for name, runner in (
        ("embree", rt.run_embree),
        ("optix", rt.run_optix),
        ("vulkan", rt.run_vulkan),
        ("hiprt_one_shot", rt.run_hiprt),
    ):
        try:
            measured = measure(lambda runner=runner: runner(kernel, **inputs), 1)
            parity = measured["rows"] == reference_rows
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
    return results


def run_prepared_graph_perf(*, vertex_count: int, degree: int, frontier_count: int, seed_count: int, repeats: int) -> dict[str, object]:
    graph = make_graph(vertex_count, degree)
    frontier, visited = make_bfs_inputs(vertex_count, frontier_count)
    seeds = make_triangle_seeds(vertex_count, seed_count)

    bfs_inputs = {"graph": graph, "frontier": frontier, "visited": visited}
    triangle_inputs = {"graph": graph, "seeds": seeds}
    bfs_cpu = measure(lambda: rt.run_cpu_python_reference(bfs_kernel, **bfs_inputs), 1)
    triangle_cpu = measure(lambda: rt.run_cpu_python_reference(triangle_match_kernel, **triangle_inputs), 1)

    results: dict[str, object] = {
        "bfs_discover": {
            "cpu_python_reference": {
                "row_count": bfs_cpu["row_count"],
                "seconds": bfs_cpu["seconds"],
                "median_seconds": bfs_cpu["median_seconds"],
            },
            "backends": backend_measurements(bfs_kernel, bfs_inputs, bfs_cpu["rows"]),
        },
        "triangle_match": {
            "cpu_python_reference": {
                "row_count": triangle_cpu["row_count"],
                "seconds": triangle_cpu["seconds"],
                "median_seconds": triangle_cpu["median_seconds"],
            },
            "backends": backend_measurements(triangle_match_kernel, triangle_inputs, triangle_cpu["rows"]),
        },
    }

    try:
        started = time.perf_counter()
        prepared = rt.prepare_hiprt_graph_csr(graph)
        prepare_seconds = time.perf_counter() - started
        try:
            bfs_prepared = measure(lambda: prepared.bfs_expand(frontier, visited, dedupe=True), repeats)
            triangle_prepared = measure(
                lambda: prepared.triangle_match(seeds, order="id_ascending", unique=True),
                repeats,
            )
        finally:
            prepared.close()

        for workload, measured, cpu_rows in (
            ("bfs_discover", bfs_prepared, bfs_cpu["rows"]),
            ("triangle_match", triangle_prepared, triangle_cpu["rows"]),
        ):
            parity = measured["rows"] == cpu_rows
            prepared_result = {
                "status": "PASS" if parity else "FAIL",
                "parity_vs_cpu_reference": parity,
                "row_count": measured["row_count"],
                "prepare_seconds": prepare_seconds,
                "query_seconds": measured["seconds"],
                "query_median_seconds": measured["median_seconds"],
                "query_min_seconds": measured["min_seconds"],
                "query_max_seconds": measured["max_seconds"],
            }
            one_shot = results[workload]["backends"].get("hiprt_one_shot", {})
            if isinstance(one_shot, dict) and one_shot.get("status") == "PASS":
                prepared_result["one_shot_to_prepared_query_speedup"] = (
                    float(one_shot["median_seconds"]) / float(measured["median_seconds"])
                )
            results[workload]["hiprt_prepared_graph"] = prepared_result
    except (FileNotFoundError, OSError, NotImplementedError) as exc:
        for workload in ("bfs_discover", "triangle_match"):
            results[workload]["hiprt_prepared_graph"] = {
                "status": "UNAVAILABLE",
                "error_type": type(exc).__name__,
                "message": str(exc).splitlines()[0],
            }

    return {
        "goal": 567,
        "description": "HIPRT prepared graph CSR performance mitigation benchmark for deterministic BFS and triangle-match",
        "vertex_count": vertex_count,
        "degree": degree,
        "edge_count": len(graph.column_indices),
        "frontier_count": frontier_count,
        "seed_count": seed_count,
        "repeats": repeats,
        "results": results,
        "honesty_boundary": (
            "This isolates prepared reuse for a HIPRT graph CSR build side. BFS timing uses dedupe=True, whose "
            "deterministic global dedupe is order-sensitive and intentionally remains serialized for CPU parity. "
            "This is not a full graph-system benchmark, not an AMD GPU claim, and not RT-core speedup evidence."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark prepared HIPRT graph CSR query reuse.")
    parser.add_argument("--vertices", type=int, default=512)
    parser.add_argument("--degree", type=int, default=4)
    parser.add_argument("--frontier", type=int, default=128)
    parser.add_argument("--seeds", type=int, default=256)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.vertices <= 0 or args.degree <= 0 or args.frontier <= 0 or args.seeds <= 0 or args.repeats <= 0:
        raise ValueError("--vertices, --degree, --frontier, --seeds, and --repeats must be positive")
    payload = run_prepared_graph_perf(
        vertex_count=args.vertices,
        degree=args.degree,
        frontier_count=args.frontier,
        seed_count=args.seeds,
        repeats=args.repeats,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    statuses = []
    for workload in payload["results"].values():
        if isinstance(workload, dict):
            prepared = workload.get("hiprt_prepared_graph")
            if isinstance(prepared, dict):
                statuses.append(prepared.get("status"))
            backends = workload.get("backends", {})
            if isinstance(backends, dict):
                statuses.extend(value.get("status") for value in backends.values() if isinstance(value, dict))
    return 1 if "FAIL" in statuses else 0


if __name__ == "__main__":
    raise SystemExit(main())
