from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class CSRGraph:
    row_offsets: tuple[int, ...]
    column_indices: tuple[int, ...]
    vertex_count: int

    @property
    def edge_count(self) -> int:
        return len(self.column_indices)


@dataclass(frozen=True)
class FrontierVertex:
    vertex_id: int
    level: int


@dataclass(frozen=True)
class EdgeSeed:
    u: int
    v: int


def csr_graph(*, row_offsets, column_indices, vertex_count: int | None = None) -> CSRGraph:
    offsets = tuple(int(value) for value in row_offsets)
    columns = tuple(int(value) for value in column_indices)
    graph = CSRGraph(
        row_offsets=offsets,
        column_indices=columns,
        vertex_count=(len(offsets) - 1) if vertex_count is None else int(vertex_count),
    )
    validate_csr_graph(graph)
    return graph


def validate_csr_graph(graph: CSRGraph) -> None:
    if graph.vertex_count < 0:
        raise ValueError("CSR graph vertex_count must be non-negative")
    if len(graph.row_offsets) != graph.vertex_count + 1:
        raise ValueError("CSR graph row_offsets length must equal vertex_count + 1")
    if not graph.row_offsets:
        raise ValueError("CSR graph row_offsets must not be empty")
    if graph.row_offsets[0] != 0:
        raise ValueError("CSR graph row_offsets must start at 0")
    if graph.row_offsets[-1] != len(graph.column_indices):
        raise ValueError("CSR graph final row_offset must equal edge_count")
    previous = graph.row_offsets[0]
    for value in graph.row_offsets[1:]:
        if value < previous:
            raise ValueError("CSR graph row_offsets must be non-decreasing")
        previous = value
    for vertex_id in graph.column_indices:
        if vertex_id < 0 or vertex_id >= graph.vertex_count:
            raise ValueError("CSR graph column_indices must be valid vertex IDs")


def normalize_frontier(payload) -> tuple[FrontierVertex, ...]:
    if isinstance(payload, (str, bytes)) or not isinstance(payload, Iterable):
        raise ValueError("vertex frontier input must be an iterable of frontier vertices")
    return tuple(_coerce_frontier_vertex(item) for item in payload)


def normalize_vertex_set(payload) -> tuple[int, ...]:
    if isinstance(payload, (str, bytes)) or not isinstance(payload, Iterable):
        raise ValueError("vertex set input must be an iterable of vertex IDs")
    return tuple(_coerce_vertex_id(item) for item in payload)


def normalize_edge_set(payload) -> tuple[EdgeSeed, ...]:
    if isinstance(payload, (str, bytes)) or not isinstance(payload, Iterable):
        raise ValueError("edge set input must be an iterable of edge seeds")
    return tuple(_coerce_edge_seed(item) for item in payload)


def bfs_expand_cpu(
    graph: CSRGraph,
    frontier: tuple[FrontierVertex, ...],
    visited: tuple[int, ...],
    *,
    dedupe: bool = True,
) -> tuple[dict[str, int], ...]:
    validate_csr_graph(graph)
    visited_ids = {int(vertex_id) for vertex_id in visited}
    discovered_this_step: set[int] = set()
    rows: list[dict[str, int]] = []

    for frontier_vertex in frontier:
        if frontier_vertex.vertex_id < 0 or frontier_vertex.vertex_id >= graph.vertex_count:
            raise ValueError("frontier vertex_id must be a valid graph vertex")
        start = graph.row_offsets[frontier_vertex.vertex_id]
        end = graph.row_offsets[frontier_vertex.vertex_id + 1]
        for neighbor_id in graph.column_indices[start:end]:
            if neighbor_id in visited_ids:
                continue
            if dedupe and neighbor_id in discovered_this_step:
                continue
            discovered_this_step.add(neighbor_id)
            rows.append(
                {
                    "src_vertex": frontier_vertex.vertex_id,
                    "dst_vertex": neighbor_id,
                    "level": frontier_vertex.level + 1,
                }
            )

    rows.sort(key=lambda row: (row["level"], row["dst_vertex"], row["src_vertex"]))
    return tuple(rows)


def triangle_probe_cpu(
    graph: CSRGraph,
    seeds: tuple[EdgeSeed, ...],
    *,
    order: str = "id_ascending",
    unique: bool = True,
) -> tuple[dict[str, int], ...]:
    validate_csr_graph(graph)
    if order != "id_ascending":
        raise ValueError("triangle probe currently supports only order='id_ascending'")

    rows: list[dict[str, int]] = []
    seen: set[tuple[int, int, int]] = set()
    for seed in seeds:
        u = int(seed.u)
        v = int(seed.v)
        if u < 0 or u >= graph.vertex_count or v < 0 or v >= graph.vertex_count:
            raise ValueError("edge seed vertices must be valid graph vertex IDs")
        if u == v:
            continue
        if order == "id_ascending" and not (u < v):
            continue

        u_neighbors = set(_neighbors(graph, u))
        v_neighbors = set(_neighbors(graph, v))
        for w in sorted(u_neighbors & v_neighbors):
            if order == "id_ascending" and not (v < w):
                continue
            triangle = (u, v, w)
            if unique and triangle in seen:
                continue
            seen.add(triangle)
            rows.append({"u": u, "v": v, "w": w})

    return tuple(rows)


def _coerce_frontier_vertex(record) -> FrontierVertex:
    if isinstance(record, FrontierVertex):
        return record
    if isinstance(record, Mapping):
        return FrontierVertex(vertex_id=int(record["vertex_id"]), level=int(record["level"]))
    if isinstance(record, tuple) and len(record) == 2:
        return FrontierVertex(vertex_id=int(record[0]), level=int(record[1]))
    raise ValueError("frontier vertex must be FrontierVertex, mapping, or (vertex_id, level)")


def _coerce_vertex_id(record) -> int:
    if isinstance(record, int):
        return int(record)
    if isinstance(record, Mapping):
        return int(record["vertex_id"])
    raise ValueError("vertex set items must be ints or mappings with vertex_id")


def _coerce_edge_seed(record) -> EdgeSeed:
    if isinstance(record, EdgeSeed):
        return record
    if isinstance(record, Mapping):
        return EdgeSeed(u=int(record["u"]), v=int(record["v"]))
    if isinstance(record, tuple) and len(record) == 2:
        return EdgeSeed(u=int(record[0]), v=int(record[1]))
    raise ValueError("edge seed must be EdgeSeed, mapping, or (u, v)")


def _neighbors(graph: CSRGraph, vertex_id: int) -> tuple[int, ...]:
    start = graph.row_offsets[vertex_id]
    end = graph.row_offsets[vertex_id + 1]
    return graph.column_indices[start:end]
