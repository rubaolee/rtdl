from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CSRGraph:
    vertex_count: int
    row_offsets: tuple[int, ...]
    column_indices: tuple[int, ...]


def csr_graph(
    *,
    row_offsets,
    column_indices,
    vertex_count: Optional[int] = None,
) -> CSRGraph:
    normalized_row_offsets = tuple(int(value) for value in row_offsets)
    normalized_column_indices = tuple(int(value) for value in column_indices)

    if vertex_count is None:
        if not normalized_row_offsets:
            raise ValueError("csr_graph requires row_offsets when vertex_count is omitted")
        resolved_vertex_count = len(normalized_row_offsets) - 1
    else:
        resolved_vertex_count = int(vertex_count)

    graph = CSRGraph(
        vertex_count=resolved_vertex_count,
        row_offsets=normalized_row_offsets,
        column_indices=normalized_column_indices,
    )
    validate_csr_graph(graph)
    return graph


def validate_csr_graph(graph: CSRGraph) -> None:
    if graph.vertex_count < 0:
        raise ValueError("csr_graph vertex_count must be non-negative")
    if len(graph.row_offsets) > graph.vertex_count + 1:
        raise ValueError("csr_graph row_offsets length must not exceed vertex_count + 1")
    if graph.row_offsets[0] != 0:
        raise ValueError("csr_graph row_offsets must start at 0")
    if graph.row_offsets[-1] != len(graph.column_indices):
        raise ValueError("csr_graph final row_offsets value must equal column_indices length")

    previous = 0
    for offset in graph.row_offsets:
        if offset < previous:
            raise ValueError("csr_graph row_offsets must be non-decreasing")
        previous = offset

    for neighbor in graph.column_indices:
        if neighbor < 0 or neighbor >= graph.vertex_count:
            raise ValueError("csr_graph column_indices contain out-of-bounds vertex IDs")


def bfs_levels_cpu(graph: CSRGraph, *, source_id: int) -> tuple[dict[str, int], ...]:
    validate_csr_graph(graph)

    source = int(source_id)
    if source < 0 or source >= graph.vertex_count:
        raise ValueError("bfs source_id is out of bounds for the CSR graph")

    visited: set[int] = {source}
    frontier = [source]
    level = 0
    rows: list[dict[str, int]] = []

    while frontier:
        for vertex_id in frontier:
            rows.append({"vertex_id": vertex_id, "level": level})

        next_frontier_candidates: set[int] = set()
        for vertex_id in frontier:
            # In Partial CSR, vertices beyond len(row_offsets)-1 are sinks.
            if vertex_id >= len(graph.row_offsets) - 1:
                continue
            start = graph.row_offsets[vertex_id]
            stop = graph.row_offsets[vertex_id + 1]
            for neighbor_id in graph.column_indices[start:stop]:
                if neighbor_id in visited:
                    continue
                visited.add(neighbor_id)
                next_frontier_candidates.add(neighbor_id)

        frontier = sorted(next_frontier_candidates)
        level += 1

    return tuple(rows)


def triangle_count_cpu(graph: CSRGraph) -> int:
    validate_csr_graph(graph)
    # Ensure neighbors are strictly ascending for the intersection algorithm.
    # Note: We don't modify the input graph in-place to avoid side effects on the caller's immutable tuple.
    for vertex_u in range(graph.vertex_count):
        neighbors_u = _neighbors(graph, vertex_u)
        if any(left >= right for left, right in zip(neighbors_u, neighbors_u[1:])):
            raise ValueError("triangle_count_cpu requires strictly ascending neighbor lists per CSR row")

    triangle_count = 0
    for vertex_u in range(graph.vertex_count):
        neighbors_u = _neighbors(graph, vertex_u)
        for vertex_v in neighbors_u:
            if vertex_v <= vertex_u:
                continue
            triangle_count += _count_sorted_intersection_above_threshold(
                neighbors_u,
                _neighbors(graph, vertex_v),
                lower_bound=vertex_v,
            )

    return triangle_count


def _validate_sorted_csr_neighbors(graph: CSRGraph) -> None:
    for vertex_id in range(graph.vertex_count):
        neighbors = _neighbors(graph, vertex_id)
        if any(left >= right for left, right in zip(neighbors, neighbors[1:])):
            raise ValueError("triangle_count_cpu requires strictly ascending neighbor lists per CSR row")


def _neighbors(graph: CSRGraph, vertex_id: int) -> tuple[int, ...]:
    start = graph.row_offsets[vertex_id]
    stop = graph.row_offsets[vertex_id + 1]
    return graph.column_indices[start:stop]


def _count_sorted_intersection_above_threshold(
    left_neighbors: tuple[int, ...],
    right_neighbors: tuple[int, ...],
    *,
    lower_bound: int,
) -> int:
    left_index = 0
    right_index = 0
    count = 0

    while left_index < len(left_neighbors) and left_neighbors[left_index] <= lower_bound:
        left_index += 1
    while right_index < len(right_neighbors) and right_neighbors[right_index] <= lower_bound:
        right_index += 1

    while left_index < len(left_neighbors) and right_index < len(right_neighbors):
        left_value = left_neighbors[left_index]
        right_value = right_neighbors[right_index]
        if left_value == right_value:
            count += 1
            left_index += 1
            right_index += 1
        elif left_value < right_value:
            left_index += 1
        else:
            right_index += 1

    return count
