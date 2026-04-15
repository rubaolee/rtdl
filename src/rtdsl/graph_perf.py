from __future__ import annotations

import statistics
import time

from .api import bfs_discover
from .api import emit
from .api import input
from .api import kernel
from .api import refine
from .api import traverse
from .api import triangle_match
from .embree_runtime import embree_version
from .embree_runtime import prepare_embree
from .graph_postgresql import connect_postgresql
from .graph_postgresql import prepare_postgresql_bfs_inputs
from .graph_postgresql import prepare_postgresql_graph_tables
from .graph_postgresql import prepare_postgresql_triangle_inputs
from .graph_postgresql import query_postgresql_bfs_expand
from .graph_postgresql import query_postgresql_triangle_probe
from .graph_reference import CSRGraph
from .optix_runtime import optix_version
from .optix_runtime import prepare_optix
from .vulkan_runtime import vulkan_version
from .vulkan_runtime import prepare_vulkan


@kernel(backend="rtdl", precision="float_approx")
def bfs_expand_reference():
    frontier = input("frontier", VertexFrontier, role="probe")
    graph = input("graph", GraphCSR, role="build")
    visited = input("visited", VertexSet, role="probe")
    candidates = traverse(frontier, graph, accel="bvh", mode="graph_expand")
    fresh = refine(candidates, predicate=bfs_discover(visited=visited, dedupe=True))
    return emit(fresh, fields=["src_vertex", "dst_vertex", "level"])


@kernel(backend="rtdl", precision="float_approx")
def triangle_probe_reference():
    seeds = input("seeds", EdgeSet, role="probe")
    graph = input("graph", GraphCSR, role="build")
    candidates = traverse(seeds, graph, accel="bvh", mode="graph_intersect")
    triangles = refine(candidates, predicate=triangle_match(order="id_ascending", unique=True))
    return emit(triangles, fields=["u", "v", "w"])


def select_bfs_inputs(
    graph: CSRGraph,
    *,
    frontier_size: int = 1024,
    source_id: int = 0,
) -> dict[str, object]:
    if frontier_size <= 0:
        raise ValueError("frontier_size must be positive")
    frontier: list[tuple[int, int]] = []
    seen: set[int] = set()

    if 0 <= source_id < graph.vertex_count and graph.row_offsets[source_id] < graph.row_offsets[source_id + 1]:
        frontier.append((source_id, 0))
        seen.add(source_id)

    for vertex_id in range(graph.vertex_count):
        if len(frontier) >= frontier_size:
            break
        if vertex_id in seen:
            continue
        if graph.row_offsets[vertex_id] == graph.row_offsets[vertex_id + 1]:
            continue
        frontier.append((vertex_id, 0))
        seen.add(vertex_id)

    if not frontier:
        raise ValueError("graph has no expandable frontier vertices")
    return {
        "frontier": tuple(frontier),
        "graph": graph,
        "visited": tuple(vertex_id for vertex_id, _ in frontier),
    }


def select_triangle_inputs(
    graph: CSRGraph,
    *,
    seed_count: int = 4096,
) -> dict[str, object]:
    if seed_count <= 0:
        raise ValueError("seed_count must be positive")
    seeds: list[tuple[int, int]] = []
    for u in range(graph.vertex_count):
        start = graph.row_offsets[u]
        end = graph.row_offsets[u + 1]
        for v in graph.column_indices[start:end]:
            if u < v:
                seeds.append((u, int(v)))
                if len(seeds) >= seed_count:
                    return {"seeds": tuple(seeds), "graph": graph}
    if not seeds:
        raise ValueError("graph has no canonical triangle seed edges")
    return {"seeds": tuple(seeds), "graph": graph}


def backend_availability() -> dict[str, bool]:
    return {
        "embree": _backend_live(embree_version),
        "optix": _backend_live(optix_version),
        "vulkan": _backend_live(vulkan_version),
    }


def measure_bfs_perf(
    graph: CSRGraph,
    *,
    frontier_size: int,
    source_id: int,
    repeats: int,
    postgresql_dsn: str,
    execution_iterations: int = 1,
    postgresql_query_iterations: int = 1,
    measure_postgresql: bool = True,
) -> dict[str, object]:
    if execution_iterations <= 0:
        raise ValueError("execution_iterations must be positive")
    if postgresql_query_iterations <= 0:
        raise ValueError("postgresql_query_iterations must be positive")
    inputs = select_bfs_inputs(graph, frontier_size=frontier_size, source_id=source_id)
    summary: dict[str, object] = {
        "workload": "bfs",
        "vertex_count": graph.vertex_count,
        "edge_count": graph.edge_count,
        "frontier_size": len(inputs["frontier"]),
        "execution_iterations": execution_iterations,
        "postgresql_query_iterations": postgresql_query_iterations,
    }
    summary.update(
        _measure_backend_family(
            bfs_expand_reference,
            inputs,
            repeats=repeats,
            execution_iterations=execution_iterations,
        )
    )
    if measure_postgresql:
        pg_setup, pg_query = _measure_postgresql_bfs(
            graph,
            inputs,
            dsn=postgresql_dsn,
            repeats=repeats,
            query_iterations=postgresql_query_iterations,
        )
        summary["postgresql_setup_seconds"] = pg_setup
        summary["postgresql_seconds"] = pg_query
    return summary


def measure_triangle_perf(
    graph: CSRGraph,
    *,
    seed_count: int,
    repeats: int,
    postgresql_dsn: str,
    execution_iterations: int = 1,
    postgresql_query_iterations: int = 1,
    measure_postgresql: bool = True,
) -> dict[str, object]:
    if execution_iterations <= 0:
        raise ValueError("execution_iterations must be positive")
    if postgresql_query_iterations <= 0:
        raise ValueError("postgresql_query_iterations must be positive")
    inputs = select_triangle_inputs(graph, seed_count=seed_count)
    summary: dict[str, object] = {
        "workload": "triangle_count",
        "vertex_count": graph.vertex_count,
        "edge_count": graph.edge_count,
        "seed_count": len(inputs["seeds"]),
        "execution_iterations": execution_iterations,
        "postgresql_query_iterations": postgresql_query_iterations,
    }
    summary.update(
        _measure_backend_family(
            triangle_probe_reference,
            inputs,
            repeats=repeats,
            execution_iterations=execution_iterations,
        )
    )
    if measure_postgresql:
        pg_setup, pg_query = _measure_postgresql_triangle(
            graph,
            inputs,
            dsn=postgresql_dsn,
            repeats=repeats,
            query_iterations=postgresql_query_iterations,
        )
        summary["postgresql_setup_seconds"] = pg_setup
        summary["postgresql_seconds"] = pg_query
    return summary


def tune_bfs_perf(
    graph: CSRGraph,
    *,
    frontier_size: int,
    source_id: int,
    repeats: int,
    postgresql_dsn: str,
    target_backend: str,
    target_seconds: float,
    min_factor: float = 0.5,
    max_factor: float = 1.5,
    max_frontier_size: int | None = None,
    max_execution_iterations: int = 1024,
    max_rounds: int = 8,
) -> dict[str, object]:
    if target_seconds <= 0:
        raise ValueError("target_seconds must be positive")
    if max_rounds <= 0:
        raise ValueError("max_rounds must be positive")
    if max_frontier_size is not None and max_frontier_size <= 0:
        raise ValueError("max_frontier_size must be positive when provided")

    requested_frontier_size = frontier_size
    execution_iterations = 1
    history: list[dict[str, object]] = []
    last_summary: dict[str, object] | None = None

    for _ in range(max_rounds):
        summary = measure_bfs_perf(
            graph,
            frontier_size=frontier_size,
            source_id=source_id,
            repeats=repeats,
            postgresql_dsn=postgresql_dsn,
            execution_iterations=execution_iterations,
            postgresql_query_iterations=1,
            measure_postgresql=False,
        )
        backend_seconds = _extract_backend_seconds(summary, target_backend)
        history.append(
            {
                "requested_frontier_size": frontier_size,
                "actual_frontier_size": summary["frontier_size"],
                "execution_iterations": execution_iterations,
                "backend_seconds": backend_seconds,
            }
        )
        last_summary = summary
        if _within_target_window(backend_seconds, target_seconds, min_factor=min_factor, max_factor=max_factor):
            break
        if int(summary["frontier_size"]) < frontier_size:
            next_iterations = _scaled_iteration_count(execution_iterations, backend_seconds, target_seconds)
            next_iterations = min(next_iterations, max_execution_iterations)
            if next_iterations == execution_iterations:
                break
            execution_iterations = next_iterations
            continue
        next_size = _scaled_batch_size(frontier_size, backend_seconds, target_seconds)
        if next_size == frontier_size:
            break
        if max_frontier_size is not None:
            next_size = min(next_size, max_frontier_size)
        if next_size <= frontier_size and backend_seconds < target_seconds * min_factor:
            next_size = frontier_size + max(1, frontier_size // 2)
        if next_size == frontier_size:
            next_iterations = _scaled_iteration_count(execution_iterations, backend_seconds, target_seconds)
            next_iterations = min(next_iterations, max_execution_iterations)
            if next_iterations == execution_iterations:
                break
            execution_iterations = next_iterations
            continue
        frontier_size = next_size

    assert last_summary is not None
    pg_setup, pg_query = _measure_postgresql_bfs(
        graph,
        select_bfs_inputs(graph, frontier_size=int(last_summary["frontier_size"]), source_id=source_id),
        dsn=postgresql_dsn,
        repeats=repeats,
        query_iterations=1,
    )
    last_summary["postgresql_setup_seconds"] = pg_setup
    last_summary["postgresql_seconds"] = pg_query
    last_summary["target_backend"] = target_backend
    last_summary["target_seconds"] = target_seconds
    last_summary["requested_frontier_size"] = requested_frontier_size
    last_summary["final_execution_iterations"] = execution_iterations
    last_summary["tuning_rounds"] = len(history)
    last_summary["tuning_history"] = tuple(history)
    return last_summary


def tune_triangle_perf(
    graph: CSRGraph,
    *,
    seed_count: int,
    repeats: int,
    postgresql_dsn: str,
    target_backend: str,
    target_seconds: float,
    min_factor: float = 0.5,
    max_factor: float = 1.5,
    max_seed_count: int | None = None,
    max_execution_iterations: int = 1024,
    max_rounds: int = 8,
) -> dict[str, object]:
    if target_seconds <= 0:
        raise ValueError("target_seconds must be positive")
    if max_rounds <= 0:
        raise ValueError("max_rounds must be positive")
    if max_seed_count is not None and max_seed_count <= 0:
        raise ValueError("max_seed_count must be positive when provided")

    requested_seed_count = seed_count
    execution_iterations = 1
    history: list[dict[str, object]] = []
    last_summary: dict[str, object] | None = None

    for _ in range(max_rounds):
        summary = measure_triangle_perf(
            graph,
            seed_count=seed_count,
            repeats=repeats,
            postgresql_dsn=postgresql_dsn,
            execution_iterations=execution_iterations,
            postgresql_query_iterations=1,
            measure_postgresql=False,
        )
        backend_seconds = _extract_backend_seconds(summary, target_backend)
        history.append(
            {
                "requested_seed_count": seed_count,
                "actual_seed_count": summary["seed_count"],
                "execution_iterations": execution_iterations,
                "backend_seconds": backend_seconds,
            }
        )
        last_summary = summary
        if _within_target_window(backend_seconds, target_seconds, min_factor=min_factor, max_factor=max_factor):
            break
        if int(summary["seed_count"]) < seed_count:
            next_iterations = _scaled_iteration_count(execution_iterations, backend_seconds, target_seconds)
            next_iterations = min(next_iterations, max_execution_iterations)
            if next_iterations == execution_iterations:
                break
            execution_iterations = next_iterations
            continue
        next_size = _scaled_batch_size(seed_count, backend_seconds, target_seconds)
        if next_size == seed_count:
            break
        if max_seed_count is not None:
            next_size = min(next_size, max_seed_count)
        if next_size <= seed_count and backend_seconds < target_seconds * min_factor:
            next_size = seed_count + max(1, seed_count // 2)
        if next_size == seed_count:
            next_iterations = _scaled_iteration_count(execution_iterations, backend_seconds, target_seconds)
            next_iterations = min(next_iterations, max_execution_iterations)
            if next_iterations == execution_iterations:
                break
            execution_iterations = next_iterations
            continue
        seed_count = next_size

    assert last_summary is not None
    pg_setup, pg_query = _measure_postgresql_triangle(
        graph,
        select_triangle_inputs(graph, seed_count=int(last_summary["seed_count"])),
        dsn=postgresql_dsn,
        repeats=repeats,
        query_iterations=1,
    )
    last_summary["postgresql_setup_seconds"] = pg_setup
    last_summary["postgresql_seconds"] = pg_query
    last_summary["target_backend"] = target_backend
    last_summary["target_seconds"] = target_seconds
    last_summary["requested_seed_count"] = requested_seed_count
    last_summary["final_execution_iterations"] = execution_iterations
    last_summary["tuning_rounds"] = len(history)
    last_summary["tuning_history"] = tuple(history)
    return last_summary


def _measure_backend_family(
    kernel_fn,
    inputs: dict[str, object],
    *,
    repeats: int,
    execution_iterations: int,
) -> dict[str, object]:
    availability = backend_availability()
    results: dict[str, object] = {
        "embree_available": availability["embree"],
        "optix_available": availability["optix"],
        "vulkan_available": availability["vulkan"],
    }
    if availability["embree"]:
        results["embree_prepare_seconds"], results["embree_seconds"] = _measure_prepared_backend(
            prepare_embree,
            kernel_fn,
            inputs,
            repeats=repeats,
            execution_iterations=execution_iterations,
        )
    if availability["optix"]:
        results["optix_prepare_seconds"], results["optix_seconds"] = _measure_prepared_backend(
            prepare_optix,
            kernel_fn,
            inputs,
            repeats=repeats,
            execution_iterations=execution_iterations,
        )
    if availability["vulkan"]:
        results["vulkan_prepare_seconds"], results["vulkan_seconds"] = _measure_prepared_backend(
            prepare_vulkan,
            kernel_fn,
            inputs,
            repeats=repeats,
            execution_iterations=execution_iterations,
        )
    return results


def _measure_prepared_backend(
    prepare_fn,
    kernel_fn,
    inputs: dict[str, object],
    *,
    repeats: int,
    execution_iterations: int,
) -> tuple[float, float]:
    started = time.perf_counter()
    prepared = prepare_fn(kernel_fn)
    execution = prepared.bind(**inputs)
    prepare_seconds = time.perf_counter() - started

    run_samples: list[float] = []
    for _ in range(repeats):
        started = time.perf_counter()
        for _iteration in range(execution_iterations):
            execution.run()
        run_samples.append(time.perf_counter() - started)
    return prepare_seconds, median_seconds(run_samples)


def _measure_postgresql_bfs(
    graph: CSRGraph,
    inputs: dict[str, object],
    *,
    dsn: str,
    repeats: int,
    query_iterations: int,
) -> tuple[float, float]:
    setup_samples: list[float] = []
    query_samples: list[float] = []
    for _ in range(repeats):
        with connect_postgresql(dsn) as connection:
            started = time.perf_counter()
            prepare_postgresql_graph_tables(connection, graph)
            prepare_postgresql_bfs_inputs(connection, inputs["frontier"], inputs["visited"])
            setup_samples.append(time.perf_counter() - started)
            started = time.perf_counter()
            for _iteration in range(query_iterations):
                query_postgresql_bfs_expand(connection)
            query_samples.append(time.perf_counter() - started)
    return median_seconds(setup_samples), median_seconds(query_samples)


def _measure_postgresql_triangle(
    graph: CSRGraph,
    inputs: dict[str, object],
    *,
    dsn: str,
    repeats: int,
    query_iterations: int,
) -> tuple[float, float]:
    setup_samples: list[float] = []
    query_samples: list[float] = []
    for _ in range(repeats):
        with connect_postgresql(dsn) as connection:
            started = time.perf_counter()
            prepare_postgresql_graph_tables(connection, graph)
            prepare_postgresql_triangle_inputs(connection, inputs["seeds"])
            setup_samples.append(time.perf_counter() - started)
            started = time.perf_counter()
            for _iteration in range(query_iterations):
                query_postgresql_triangle_probe(connection)
            query_samples.append(time.perf_counter() - started)
    return median_seconds(setup_samples), median_seconds(query_samples)


def median_seconds(samples: list[float]) -> float:
    if not samples:
        raise ValueError("median_seconds requires at least one sample")
    return float(statistics.median(samples))


def _extract_backend_seconds(summary: dict[str, object], backend: str) -> float:
    field_name = f"{backend}_seconds"
    if field_name not in summary:
        raise ValueError(f"target backend timing is unavailable: {backend!r}")
    return float(summary[field_name])


def _within_target_window(
    seconds: float,
    target_seconds: float,
    *,
    min_factor: float,
    max_factor: float,
) -> bool:
    return (target_seconds * min_factor) <= seconds <= (target_seconds * max_factor)


def _scaled_batch_size(current_size: int, current_seconds: float, target_seconds: float) -> int:
    if current_size <= 0:
        raise ValueError("current_size must be positive")
    if target_seconds <= 0:
        raise ValueError("target_seconds must be positive")
    if current_seconds <= 0:
        return max(current_size * 4, current_size + 1)
    scaled = int(round(current_size * (target_seconds / current_seconds)))
    return max(1, scaled)


def _scaled_iteration_count(current_iterations: int, current_seconds: float, target_seconds: float) -> int:
    if current_iterations <= 0:
        raise ValueError("current_iterations must be positive")
    if target_seconds <= 0:
        raise ValueError("target_seconds must be positive")
    if current_seconds <= 0:
        return max(current_iterations * 4, current_iterations + 1)
    scaled = int(round(current_iterations * (target_seconds / current_seconds)))
    return max(current_iterations + 1, scaled)


def _backend_live(version_fn) -> bool:
    try:
        version_fn()
    except Exception:
        return False
    return True


# Imported late to avoid circular import ordering with the kernel decorator.
from .layout_types import EdgeSet  # noqa: E402
from .layout_types import GraphCSR  # noqa: E402
from .layout_types import VertexFrontier  # noqa: E402
from .layout_types import VertexSet  # noqa: E402
