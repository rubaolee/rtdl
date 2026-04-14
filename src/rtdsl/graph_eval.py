from __future__ import annotations
import statistics
import time
from typing import Optional, Union, Tuple, List, Dict

from .external_baselines import connect_postgresql
from .external_baselines import postgresql_available
from .external_baselines import prepare_postgresql_graph_edges_table
from .external_baselines import query_postgresql_bfs_levels
from .external_baselines import query_postgresql_triangle_count
from .graph_reference import bfs_levels_cpu
from .graph_reference import CSRGraph
from .graph_reference import csr_graph
from .graph_reference import triangle_count_cpu
from .oracle_runtime import bfs_levels_oracle
from .oracle_runtime import triangle_count_oracle


def cycle_graph(vertex_count: int) -> CSRGraph:
    vertex_count = int(vertex_count)
    if vertex_count < 0:
        raise ValueError("cycle_graph vertex_count must be non-negative")
    if vertex_count == 0:
        return csr_graph(row_offsets=(0,), column_indices=())

    neighbors: list[tuple[int, ...]] = []
    for vertex_id in range(vertex_count):
        if vertex_count == 1:
            neighbors.append(())
            continue
        left = (vertex_id - 1) % vertex_count
        right = (vertex_id + 1) % vertex_count
        if left == right:
            neighbors.append((left,))
        else:
            neighbors.append(tuple(sorted((left, right))))
    return csr_graph_from_neighbors(neighbors)


def binary_tree_graph(vertex_count: int) -> CSRGraph:
    vertex_count = int(vertex_count)
    if vertex_count < 0:
        raise ValueError("binary_tree_graph vertex_count must be non-negative")
    if vertex_count == 0:
        return csr_graph(row_offsets=(0,), column_indices=())

    neighbors: list[tuple[int, ...]] = []
    for vertex_id in range(vertex_count):
        children: list[int] = []
        left = (2 * vertex_id) + 1
        right = (2 * vertex_id) + 2
        if left < vertex_count:
            children.append(left)
        if right < vertex_count:
            children.append(right)
        neighbors.append(tuple(children))
    return csr_graph_from_neighbors(neighbors)


def clique_graph(vertex_count: int) -> CSRGraph:
    vertex_count = int(vertex_count)
    if vertex_count < 0:
        raise ValueError("clique_graph vertex_count must be non-negative")
    neighbors = [
        tuple(neighbor_id for neighbor_id in range(vertex_count) if neighbor_id != vertex_id)
        for vertex_id in range(vertex_count)
    ]
    return csr_graph_from_neighbors(neighbors)


def grid_graph(width: int, height: int) -> CSRGraph:
    width = int(width)
    height = int(height)
    if width < 0 or height < 0:
        raise ValueError("grid_graph width and height must be non-negative")
    if width == 0 or height == 0:
        return csr_graph(row_offsets=(0,), column_indices=())

    vertex_count = width * height
    neighbors: list[tuple[int, ...]] = []
    for row in range(height):
        for col in range(width):
            vertex_id = row * width + col
            vertex_neighbors: list[int] = []
            if row > 0:
                vertex_neighbors.append((row - 1) * width + col)
            if row + 1 < height:
                vertex_neighbors.append((row + 1) * width + col)
            if col > 0:
                vertex_neighbors.append(row * width + (col - 1))
            if col + 1 < width:
                vertex_neighbors.append(row * width + (col + 1))
            neighbors.append(tuple(sorted(vertex_neighbors)))
    if len(neighbors) != vertex_count:
        raise RuntimeError("grid_graph internal construction error")
    return csr_graph_from_neighbors(neighbors)


def csr_graph_from_neighbors(neighbors: Union[List[Tuple[int, ...]], Tuple[Tuple[int, ...], ...]]) -> CSRGraph:
    row_offsets = [0]
    column_indices: list[int] = []
    for row in neighbors:
        normalized = tuple(sorted(int(neighbor_id) for neighbor_id in row))
        column_indices.extend(normalized)
        row_offsets.append(len(column_indices))
    return csr_graph(row_offsets=tuple(row_offsets), column_indices=tuple(column_indices))


def bfs_baseline_evaluation(
    graph: CSRGraph,
    *,
    source_id: int,
    repeats: int = 3,
    postgresql_dsn: Optional[str] = None,
) -> Dict[str, object]:
    python_rows, python_seconds = _timed_call(
        lambda: bfs_levels_cpu(graph, source_id=source_id),
        repeats=repeats,
    )
    oracle_rows, oracle_seconds = _timed_call(
        lambda: bfs_levels_oracle(graph, source_id=source_id),
        repeats=repeats,
    )
    result: dict[str, object] = {
        "workload": "bfs",
        "vertex_count": graph.vertex_count,
        "edge_count": len(graph.column_indices),
        "python_seconds": python_seconds,
        "oracle_seconds": oracle_seconds,
        "oracle_match": oracle_rows == python_rows,
    }
    if postgresql_dsn and postgresql_available():
        connection = connect_postgresql(postgresql_dsn)
        try:
            postgresql_rows, postgresql_seconds, postgresql_setup_seconds = _timed_postgresql_call(
                connection=connection,
                graph=graph,
                prepare_fn=lambda: prepare_postgresql_graph_edges_table(
                    connection,
                    graph,
                    canonical_undirected=False,
                ),
                query_fn=lambda: query_postgresql_bfs_levels(
                    connection,
                    source_id=source_id,
                ),
                repeats=repeats,
            )
        finally:
            connection.close()
        result["postgresql_seconds"] = postgresql_seconds
        result["postgresql_setup_seconds"] = postgresql_setup_seconds
        result["postgresql_match"] = postgresql_rows == python_rows
    return result


def triangle_count_baseline_evaluation(
    graph: CSRGraph,
    *,
    repeats: int = 3,
    postgresql_dsn: Optional[str] = None,
) -> Dict[str, object]:
    expected = triangle_count_cpu(graph)
    oracle_value, oracle_seconds = _timed_call(
        lambda: triangle_count_oracle(graph),
        repeats=repeats,
    )
    result: dict[str, object] = {
        "workload": "triangle_count",
        "vertex_count": graph.vertex_count,
        "edge_count": len(graph.column_indices),
        "python_seconds": _timed_call(
            lambda: triangle_count_cpu(graph),
            repeats=repeats,
        )[1],
        "oracle_seconds": oracle_seconds,
        "oracle_match": oracle_value == expected,
    }
    if postgresql_dsn and postgresql_available():
        connection = connect_postgresql(postgresql_dsn)
        try:
            postgresql_value, postgresql_seconds, postgresql_setup_seconds = _timed_postgresql_call(
                connection=connection,
                graph=graph,
                prepare_fn=lambda: prepare_postgresql_graph_edges_table(
                    connection,
                    graph,
                    canonical_undirected=True,
                ),
                query_fn=lambda: query_postgresql_triangle_count(
                    connection,
                ),
                repeats=repeats,
            )
        finally:
            connection.close()
        result["postgresql_seconds"] = postgresql_seconds
        result["postgresql_setup_seconds"] = postgresql_setup_seconds
        result["postgresql_match"] = postgresql_value == expected
    return result


def _timed_call(fn, *, repeats: int) -> tuple[object, float]:
    if repeats <= 0:
        raise ValueError("evaluation repeats must be positive")

    value = None
    samples = []
    for _ in range(repeats):
        started = time.perf_counter()
        value = fn()
        samples.append(time.perf_counter() - started)
    return value, float(statistics.median(samples))


def _timed_postgresql_call(
    *,
    connection,
    graph: CSRGraph,
    prepare_fn,
    query_fn,
    repeats: int,
) -> tuple[object, float, float]:
    del connection
    del graph
    if repeats <= 0:
        raise ValueError("evaluation repeats must be positive")

    started = time.perf_counter()
    prepare_fn()
    setup_seconds = time.perf_counter() - started

    value, query_seconds = _timed_call(query_fn, repeats=repeats)
    return value, query_seconds, float(setup_seconds)
