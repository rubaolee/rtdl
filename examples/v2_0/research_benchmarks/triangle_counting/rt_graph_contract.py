from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import struct
from typing import Any
from typing import Iterable


Edge = tuple[int, int]


@dataclass(frozen=True)
class RTGraphTriangleContract:
    original_edges: tuple[Edge, ...]
    compacted_vertex_ids: tuple[int, ...]
    compacted_edges: tuple[Edge, ...]
    degree_before_orientation: tuple[int, ...]
    directed_edges: tuple[Edge, ...]
    row_offsets: tuple[int, ...]
    column_indices: tuple[int, ...]
    triangle_witnesses: tuple[tuple[int, int, int], ...]
    two_hop_rays_2a1: tuple[tuple[int, int, int], ...]
    directed_vertex_compacted_ids: tuple[int, ...]
    id_ascending_vertex_order: tuple[int, ...]
    id_ascending_edges: tuple[Edge, ...]
    id_ascending_row_offsets: tuple[int, ...]
    id_ascending_column_indices: tuple[int, ...]
    id_ascending_triangle_witnesses: tuple[tuple[int, int, int], ...]
    removed_low_degree_vertex_count: int
    removed_low_degree_edge_count: int
    removed_duplicate_or_self_edge_count: int
    id_ascending_adapter_materialized: bool = True

    @property
    def vertex_count(self) -> int:
        return len(self.row_offsets) - 1

    @property
    def directed_edge_count(self) -> int:
        return len(self.directed_edges)

    @property
    def triangle_count(self) -> int:
        return len(self.triangle_witnesses)

    @property
    def duplicate_two_hop_relation_count(self) -> int:
        return sum(count for _, _, count in self.two_hop_rays_2a1)

    def to_payload(self) -> dict[str, object]:
        return {
            "original_edge_count": len(self.original_edges),
            "compacted_vertex_count": len(self.compacted_vertex_ids),
            "compacted_vertex_ids": list(self.compacted_vertex_ids),
            "compacted_edges": [list(edge) for edge in self.compacted_edges],
            "degree_before_orientation": list(self.degree_before_orientation),
            "directed_vertex_count": self.vertex_count,
            "directed_edge_count": self.directed_edge_count,
            "directed_edges": [list(edge) for edge in self.directed_edges],
            "csr": {
                "row_offsets": list(self.row_offsets),
                "column_indices": list(self.column_indices),
            },
            "triangle_count": self.triangle_count,
            "triangle_witnesses": [list(row) for row in self.triangle_witnesses],
            "two_hop_rays_2a1": [list(row) for row in self.two_hop_rays_2a1],
            "duplicate_two_hop_relation_count": self.duplicate_two_hop_relation_count,
            "id_ascending_adapter": {
                "materialized": self.id_ascending_adapter_materialized,
                "vertex_order": list(self.id_ascending_vertex_order),
                "directed_vertex_compacted_ids": list(self.directed_vertex_compacted_ids),
                "edges": [list(edge) for edge in self.id_ascending_edges],
                "csr": {
                    "row_offsets": list(self.id_ascending_row_offsets),
                    "column_indices": list(self.id_ascending_column_indices),
                },
                "triangle_witnesses": [list(row) for row in self.id_ascending_triangle_witnesses],
            },
            "removed_low_degree_vertex_count": self.removed_low_degree_vertex_count,
            "removed_low_degree_edge_count": self.removed_low_degree_edge_count,
            "removed_duplicate_or_self_edge_count": self.removed_duplicate_or_self_edge_count,
        }


@dataclass(frozen=True)
class RTGraphTriangleSummaryContract:
    original_edge_count: int
    compacted_vertex_count: int
    directed_vertex_count: int
    directed_edges: Any
    row_offsets: Any
    column_indices: Any
    triangle_count_value: int
    two_hop_rays_2a1: Any
    duplicate_two_hop_relation_count_value: int
    removed_low_degree_vertex_count: int
    removed_low_degree_edge_count: int
    removed_duplicate_or_self_edge_count: int
    partner: str
    partner_timing_ms: dict[str, float]
    device_arrays: object | None = None
    id_ascending_adapter_materialized: bool = False
    original_edges: tuple[Edge, ...] = ()
    compacted_vertex_ids: tuple[int, ...] = ()
    compacted_edges: tuple[Edge, ...] = ()
    degree_before_orientation: tuple[int, ...] = ()
    triangle_witnesses: tuple[tuple[int, int, int], ...] = ()
    directed_vertex_compacted_ids: tuple[int, ...] = ()
    id_ascending_vertex_order: tuple[int, ...] = ()
    id_ascending_edges: tuple[Edge, ...] = ()
    id_ascending_row_offsets: tuple[int, ...] = ()
    id_ascending_column_indices: tuple[int, ...] = ()
    id_ascending_triangle_witnesses: tuple[tuple[int, int, int], ...] = ()

    @property
    def vertex_count(self) -> int:
        return self.directed_vertex_count

    @property
    def directed_edge_count(self) -> int:
        return len(self.directed_edges)

    @property
    def triangle_count(self) -> int:
        return self.triangle_count_value

    @property
    def duplicate_two_hop_relation_count(self) -> int:
        return self.duplicate_two_hop_relation_count_value


def fixture_edges(name: str) -> tuple[Edge, ...]:
    if name == "single_triangle":
        return ((10, 20), (10, 30), (20, 30))
    if name == "degree_oriented_two_triangles":
        return ((0, 1), (1, 2), (2, 0), (0, 3), (3, 2))
    if name == "duplicates_self_and_leaf":
        return ((0, 1), (0, 1), (0, 2), (1, 2), (2, 2), (7, 8))
    raise ValueError(f"unknown RT-Graph triangle fixture: {name}")


def read_text_edges(path: str | Path) -> tuple[Edge, ...]:
    edges: list[Edge] = []
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("%"):
            continue
        parts = line.split()
        if len(parts) < 2:
            raise ValueError(f"edge-list line {line_number} must contain at least two integer fields")
        try:
            edges.append((int(parts[0]), int(parts[1])))
        except ValueError as exc:
            raise ValueError(f"edge-list line {line_number} has non-integer endpoints") from exc
    return tuple(edges)


def read_binary_edges(path: str | Path) -> tuple[Edge, ...]:
    data = Path(path).read_bytes()
    if len(data) % 8 != 0:
        raise ValueError("RT-Graph binary edge file size must be a multiple of two int32 values")
    return tuple((int(src), int(dst)) for src, dst in struct.iter_unpack("<ii", data))


def write_binary_edges(path: str | Path, edges: Iterable[Edge]) -> None:
    payload = bytearray()
    for src, dst in _normalize_edges(edges):
        payload.extend(struct.pack("<ii", src, dst))
    Path(path).write_bytes(bytes(payload))


def build_rt_graph_triangle_summary_contract_cupy_binary(path: str | Path) -> RTGraphTriangleSummaryContract:
    import time

    import cupy as cp
    import numpy as np

    timing_ms: dict[str, float] = {}

    def sync_time(label: str, callback):
        cp.cuda.Stream.null.synchronize()
        started = time.perf_counter()
        result = callback()
        cp.cuda.Stream.null.synchronize()
        timing_ms[label] = (time.perf_counter() - started) * 1000.0
        return result

    started = time.perf_counter()
    edges_np = np.fromfile(path, dtype=np.int32)
    if edges_np.size % 2 != 0:
        raise ValueError("RT-Graph binary edge file size must be a multiple of two int32 values")
    edges_np = edges_np.reshape(-1, 2).astype(np.int64, copy=False)
    timing_ms["load_np_ms"] = (time.perf_counter() - started) * 1000.0

    edges = sync_time("upload_ms", lambda: cp.asarray(edges_np))
    endpoints = edges.reshape(-1)
    compacted_vertex_ids, inverse = sync_time(
        "compact_unique_ms",
        lambda: cp.unique(endpoints, return_inverse=True),
    )
    compacted_edges = inverse.reshape(-1, 2).astype(cp.int64, copy=False)
    node_count = int(compacted_vertex_ids.size)
    degree = sync_time(
        "degree_ms",
        lambda: cp.bincount(compacted_edges.reshape(-1), minlength=node_count),
    )

    src = compacted_edges[:, 0]
    dst = compacted_edges[:, 1]
    deg_src = degree[src]
    deg_dst = degree[dst]
    swap = (deg_src > deg_dst) | ((deg_src == deg_dst) & (src > dst))
    oriented_src = cp.where(swap, dst, src)
    oriented_dst = cp.where(swap, src, dst)
    keep_vertex = degree > 1
    remap = cp.cumsum(keep_vertex.astype(cp.int64)) - 1
    keep_edge = keep_vertex[oriented_src] & keep_vertex[oriented_dst]
    directed_node_count = int(keep_vertex.sum().get())

    def build_directed_csr():
        vsrc = remap[oriented_src[keep_edge]]
        vdst = remap[oriented_dst[keep_edge]]
        nonself = vsrc != vdst
        vsrc = vsrc[nonself]
        vdst = vdst[nonself]
        if directed_node_count == 0 or vsrc.size == 0:
            empty = cp.empty(0, dtype=cp.int64)
            row_offsets = cp.zeros(directed_node_count + 1, dtype=cp.int64)
            return empty, empty, empty, row_offsets
        edge_keys = cp.unique(vsrc * directed_node_count + vdst)
        directed_src = edge_keys // directed_node_count
        column_indices = edge_keys - directed_src * directed_node_count
        row_counts = cp.bincount(directed_src, minlength=directed_node_count).astype(cp.int64, copy=False)
        row_offsets = cp.empty(directed_node_count + 1, dtype=cp.int64)
        row_offsets[0] = 0
        row_offsets[1:] = cp.cumsum(row_counts)
        return edge_keys, directed_src.astype(cp.int64), column_indices.astype(cp.int64), row_offsets

    directed_edge_keys, directed_src, column_indices, row_offsets = sync_time(
        "directed_csr_ms",
        build_directed_csr,
    )

    def build_two_hop_and_count():
        if directed_node_count == 0 or column_indices.size == 0:
            empty = cp.empty(0, dtype=cp.int64)
            return empty, empty, cp.empty(0, dtype=cp.uint64), cp.array(0, dtype=cp.uint64)
        out_degree = row_offsets[1:] - row_offsets[:-1]
        edge_src = cp.repeat(cp.arange(directed_node_count, dtype=cp.int64), out_degree)
        edge_mid = column_indices
        counts = out_degree[edge_mid]
        nonempty = counts > 0
        counts = counts[nonempty]
        if counts.size == 0:
            empty = cp.empty(0, dtype=cp.int64)
            return empty, empty, cp.empty(0, dtype=cp.uint64), cp.array(0, dtype=cp.uint64)
        edge_src = edge_src[nonempty]
        starts = row_offsets[edge_mid[nonempty]]
        total_two_hop = int(counts.sum().get())
        repeated_starts = cp.repeat(starts, counts)
        repeated_prefix = cp.repeat(cp.cumsum(counts) - counts, counts)
        dst_index = repeated_starts + (cp.arange(total_two_hop, dtype=cp.int64) - repeated_prefix)
        two_hop_dst = column_indices[dst_index]
        two_hop_src = cp.repeat(edge_src, counts)
        two_hop_keys = two_hop_src * directed_node_count + two_hop_dst
        unique_keys, unique_counts = cp.unique(two_hop_keys, return_counts=True)
        positions = cp.searchsorted(directed_edge_keys, unique_keys)
        in_range = positions < directed_edge_keys.size
        found = cp.zeros(unique_keys.shape, dtype=cp.bool_)
        found[in_range] = directed_edge_keys[positions[in_range]] == unique_keys[in_range]
        triangle_count = unique_counts[found].astype(cp.uint64).sum()
        ray_src = unique_keys // directed_node_count
        ray_dst = unique_keys - ray_src * directed_node_count
        return ray_src.astype(cp.int64), ray_dst.astype(cp.int64), unique_counts.astype(cp.uint64), triangle_count

    two_hop_src, two_hop_dst, two_hop_weights, triangle_count_device = sync_time(
        "two_hop_and_count_ms",
        build_two_hop_and_count,
    )

    def download_needed_columns():
        directed_edges_host = np.column_stack((cp.asnumpy(directed_src), cp.asnumpy(column_indices)))
        two_hop_host = np.column_stack(
            (
                cp.asnumpy(two_hop_src),
                cp.asnumpy(two_hop_dst),
                cp.asnumpy(two_hop_weights),
            )
        )
        return (
            directed_edges_host,
            cp.asnumpy(row_offsets),
            cp.asnumpy(column_indices),
            two_hop_host,
            int(triangle_count_device.get()),
        )

    directed_edges_host, row_offsets_host, column_indices_host, two_hop_host, triangle_count = sync_time(
        "download_needed_columns_ms",
        download_needed_columns,
    )
    timing_ms["total_partner_ms"] = sum(value for key, value in timing_ms.items() if key.endswith("_ms"))

    removed_low_degree_vertex_count = int(node_count - directed_node_count)
    removed_low_degree_edge_count = int((~keep_edge).sum().get())
    removed_duplicate_or_self_edge_count = int(edges_np.shape[0] - removed_low_degree_edge_count - len(directed_edges_host))
    duplicate_two_hop_count = int(two_hop_host[:, 2].sum()) if len(two_hop_host) else 0
    return RTGraphTriangleSummaryContract(
        original_edge_count=int(edges_np.shape[0]),
        compacted_vertex_count=node_count,
        directed_vertex_count=directed_node_count,
        directed_edges=directed_edges_host,
        row_offsets=row_offsets_host,
        column_indices=column_indices_host,
        triangle_count_value=int(triangle_count),
        two_hop_rays_2a1=two_hop_host,
        duplicate_two_hop_relation_count_value=duplicate_two_hop_count,
        removed_low_degree_vertex_count=removed_low_degree_vertex_count,
        removed_low_degree_edge_count=removed_low_degree_edge_count,
        removed_duplicate_or_self_edge_count=removed_duplicate_or_self_edge_count,
        partner="cupy",
        partner_timing_ms={key: round(value, 3) for key, value in timing_ms.items()},
        device_arrays={
            "row_offsets": row_offsets,
            "column_indices": column_indices,
            "directed_src": directed_src,
            "two_hop_src": two_hop_src,
            "two_hop_dst": two_hop_dst,
            "two_hop_weights": two_hop_weights,
        },
    )


def build_rt_graph_triangle_contract(
    edges: Iterable[Edge],
    *,
    include_id_ascending_adapter: bool = True,
) -> RTGraphTriangleContract:
    original_edges = _normalize_edges(edges)
    compacted_vertex_ids, compacted_edges = _compact_vertices(original_edges)
    node_count = len(compacted_vertex_ids)
    degree = [0] * node_count
    for src, dst in compacted_edges:
        degree[src] += 1
        degree[dst] += 1

    oriented_edges = [_orient_edge(src, dst, degree) for src, dst in compacted_edges]
    remove_prefix: list[int] = []
    removed_so_far = 0
    for vertex_degree in degree:
        if vertex_degree <= 1:
            removed_so_far += 1
        remove_prefix.append(removed_so_far)

    valid_edges: list[Edge] = []
    low_degree_edge_count = 0
    for src, dst in oriented_edges:
        if degree[src] <= 1 or degree[dst] <= 1:
            low_degree_edge_count += 1
            continue
        valid_edges.append((src - remove_prefix[src], dst - remove_prefix[dst]))

    sorted_edges = sorted(valid_edges)
    directed_edges: list[Edge] = []
    duplicate_or_self_count = 0
    previous: Edge | None = None
    for edge in sorted_edges:
        if edge[0] == edge[1] or edge == previous:
            duplicate_or_self_count += 1
            previous = edge
            continue
        directed_edges.append(edge)
        previous = edge

    directed_node_count = node_count - removed_so_far
    row_offsets, column_indices = _to_csr(tuple(directed_edges), directed_node_count)
    witnesses = _triangle_witnesses(row_offsets, column_indices)
    two_hop_rays = _two_hop_rays_2a1(row_offsets, column_indices)
    directed_vertex_compacted_ids = tuple(
        vertex_id for vertex_id, vertex_degree in enumerate(degree) if vertex_degree > 1
    )
    if include_id_ascending_adapter:
        (
            id_ascending_vertex_order,
            id_ascending_edges,
            id_ascending_row_offsets,
            id_ascending_column_indices,
            id_ascending_witnesses,
        ) = _build_id_ascending_adapter(
            tuple(directed_edges),
            directed_vertex_compacted_ids,
            tuple(degree),
        )
    else:
        id_ascending_vertex_order = ()
        id_ascending_edges = ()
        id_ascending_row_offsets = ()
        id_ascending_column_indices = ()
        id_ascending_witnesses = ()

    return RTGraphTriangleContract(
        original_edges=original_edges,
        compacted_vertex_ids=compacted_vertex_ids,
        compacted_edges=compacted_edges,
        degree_before_orientation=tuple(degree),
        directed_edges=tuple(directed_edges),
        row_offsets=row_offsets,
        column_indices=column_indices,
        triangle_witnesses=witnesses,
        two_hop_rays_2a1=two_hop_rays,
        directed_vertex_compacted_ids=directed_vertex_compacted_ids,
        id_ascending_vertex_order=id_ascending_vertex_order,
        id_ascending_edges=id_ascending_edges,
        id_ascending_row_offsets=id_ascending_row_offsets,
        id_ascending_column_indices=id_ascending_column_indices,
        id_ascending_triangle_witnesses=id_ascending_witnesses,
        removed_low_degree_vertex_count=removed_so_far,
        removed_low_degree_edge_count=low_degree_edge_count,
        removed_duplicate_or_self_edge_count=duplicate_or_self_count,
        id_ascending_adapter_materialized=include_id_ascending_adapter,
    )


def _normalize_edges(edges: Iterable[Edge]) -> tuple[Edge, ...]:
    normalized: list[Edge] = []
    for raw_src, raw_dst in edges:
        src = int(raw_src)
        dst = int(raw_dst)
        if src < 0 or dst < 0:
            raise ValueError("RT-Graph edge endpoints must be non-negative integers")
        normalized.append((src, dst))
    return tuple(normalized)


def _compact_vertices(edges: tuple[Edge, ...]) -> tuple[tuple[int, ...], tuple[Edge, ...]]:
    vertex_ids = tuple(sorted({endpoint for edge in edges for endpoint in edge}))
    dense_id = {vertex_id: index for index, vertex_id in enumerate(vertex_ids)}
    return vertex_ids, tuple((dense_id[src], dense_id[dst]) for src, dst in edges)


def _orient_edge(src: int, dst: int, degree: list[int]) -> Edge:
    if degree[src] > degree[dst] or (degree[src] == degree[dst] and src > dst):
        return dst, src
    return src, dst


def _to_csr(edges: tuple[Edge, ...], vertex_count: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    adjacency: list[list[int]] = [[] for _ in range(vertex_count)]
    for src, dst in edges:
        adjacency[src].append(dst)
    row_offsets = [0]
    column_indices: list[int] = []
    for neighbors in adjacency:
        column_indices.extend(neighbors)
        row_offsets.append(len(column_indices))
    return tuple(row_offsets), tuple(column_indices)


def _neighbors(row_offsets: tuple[int, ...], column_indices: tuple[int, ...], vertex: int) -> tuple[int, ...]:
    return column_indices[row_offsets[vertex] : row_offsets[vertex + 1]]


def _triangle_witnesses(
    row_offsets: tuple[int, ...],
    column_indices: tuple[int, ...],
) -> tuple[tuple[int, int, int], ...]:
    adjacency_sets = [
        set(_neighbors(row_offsets, column_indices, vertex))
        for vertex in range(len(row_offsets) - 1)
    ]
    witnesses: list[tuple[int, int, int]] = []
    for src, src_neighbors in enumerate(adjacency_sets):
        for mid in sorted(src_neighbors):
            for dst in sorted(src_neighbors & adjacency_sets[mid]):
                witnesses.append((src, mid, dst))
    return tuple(witnesses)


def _two_hop_rays_2a1(
    row_offsets: tuple[int, ...],
    column_indices: tuple[int, ...],
) -> tuple[tuple[int, int, int], ...]:
    rays: list[tuple[int, int, int]] = []
    for src in range(len(row_offsets) - 1):
        two_hops: list[int] = []
        for mid in _neighbors(row_offsets, column_indices, src):
            two_hops.extend(_neighbors(row_offsets, column_indices, mid))
        for dst, count in sorted(Counter(two_hops).items()):
            rays.append((src, dst, count))
    return tuple(rays)


def _build_id_ascending_adapter(
    directed_edges: tuple[Edge, ...],
    directed_vertex_compacted_ids: tuple[int, ...],
    degree_before_orientation: tuple[int, ...],
) -> tuple[
    tuple[int, ...],
    tuple[Edge, ...],
    tuple[int, ...],
    tuple[int, ...],
    tuple[tuple[int, int, int], ...],
]:
    vertex_order = tuple(
        sorted(
            range(len(directed_vertex_compacted_ids)),
            key=lambda vertex: (
                degree_before_orientation[directed_vertex_compacted_ids[vertex]],
                directed_vertex_compacted_ids[vertex],
            ),
        )
    )
    rank = {directed_vertex: adapter_id for adapter_id, directed_vertex in enumerate(vertex_order)}
    adapter_edges = tuple(sorted((rank[src], rank[dst]) for src, dst in directed_edges))
    for src, dst in adapter_edges:
        if src >= dst:
            raise ValueError("RT-Graph id-ascending adapter produced a non-ascending edge")
    row_offsets, column_indices = _to_csr(adapter_edges, len(directed_vertex_compacted_ids))
    witnesses = _triangle_witnesses(row_offsets, column_indices)
    return vertex_order, adapter_edges, row_offsets, column_indices, witnesses
