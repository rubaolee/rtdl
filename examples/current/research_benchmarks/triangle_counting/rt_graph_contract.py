from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import struct
from typing import Any
from typing import Iterable


Edge = tuple[int, int]

_TRIANGLE_SUMMARY_BOUNDED_ID_REMAP_MAX_RANGE_FACTOR = 4


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
    partner_timing_ms: dict[str, object]
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


@dataclass(frozen=True)
class RTGraphHostColumnPlaceholder:
    length: int
    shape: tuple[int, ...]
    dtype: str = "int64"
    reason: str = "host materialization intentionally skipped"

    @property
    def size(self) -> int:
        total = 1
        for value in self.shape:
            total *= int(value)
        return total

    def __len__(self) -> int:
        return self.length

    def tolist(self) -> list[object]:
        raise ValueError(self.reason)


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


def build_rt_graph_triangle_summary_contract_cupy_binary(
    path: str | Path,
    *,
    materialize_host_columns: bool = True,
    materialize_two_hop_summary: bool = True,
) -> RTGraphTriangleSummaryContract:
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

    if not materialize_two_hop_summary:
        def estimate_two_hop_relation_count():
            if directed_node_count == 0 or column_indices.size == 0:
                empty_counts = cp.empty(0, dtype=cp.int64)
                return empty_counts, 0, 0
            out_degree = row_offsets[1:] - row_offsets[:-1]
            two_hop_counts = out_degree[column_indices].astype(cp.int64, copy=False)
            total_two_hop = int(two_hop_counts.sum().get()) if int(two_hop_counts.size) else 0
            max_two_hop_per_edge = int(two_hop_counts.max().get()) if int(two_hop_counts.size) else 0
            return two_hop_counts, total_two_hop, max_two_hop_per_edge

        two_hop_counts, total_two_hop, max_two_hop_per_edge = sync_time(
            "two_hop_estimate_ms",
            estimate_two_hop_relation_count,
        )
        directed_edges_host = RTGraphHostColumnPlaceholder(
            length=int(column_indices.size),
            shape=(int(column_indices.size), 2),
            reason="CuPy directed-CSR route skipped directed_edges host materialization",
        )
        row_offsets_host = RTGraphHostColumnPlaceholder(
            length=int(row_offsets.size),
            shape=(int(row_offsets.size),),
            reason="CuPy directed-CSR route skipped row_offsets host materialization",
        )
        column_indices_host = RTGraphHostColumnPlaceholder(
            length=int(column_indices.size),
            shape=(int(column_indices.size),),
            reason="CuPy directed-CSR route skipped column_indices host materialization",
        )
        two_hop_host = RTGraphHostColumnPlaceholder(
            length=int(total_two_hop),
            shape=(int(total_two_hop), 3),
            reason="CuPy directed-CSR route skipped global two-hop summary materialization",
        )
        timing_ms["total_partner_ms"] = sum(value for key, value in timing_ms.items() if key.endswith("_ms"))

        removed_low_degree_vertex_count = int(node_count - directed_node_count)
        removed_low_degree_edge_count = int((~keep_edge).sum().get())
        removed_duplicate_or_self_edge_count = int(
            edges_np.shape[0] - removed_low_degree_edge_count - len(directed_edges_host)
        )
        return RTGraphTriangleSummaryContract(
            original_edge_count=int(edges_np.shape[0]),
            compacted_vertex_count=node_count,
            directed_vertex_count=directed_node_count,
            directed_edges=directed_edges_host,
            row_offsets=row_offsets_host,
            column_indices=column_indices_host,
            triangle_count_value=-1,
            two_hop_rays_2a1=two_hop_host,
            duplicate_two_hop_relation_count_value=int(total_two_hop),
            removed_low_degree_vertex_count=removed_low_degree_vertex_count,
            removed_low_degree_edge_count=removed_low_degree_edge_count,
            removed_duplicate_or_self_edge_count=removed_duplicate_or_self_edge_count,
            partner="cupy_directed_csr",
            partner_timing_ms={key: round(value, 3) for key, value in timing_ms.items()}
            | {
                "host_columns_materialized": False,
                "two_hop_summary_materialized": False,
                "triangle_count_available": False,
                "estimated_two_hop_relation_count": int(total_two_hop),
                "max_two_hop_per_directed_edge": int(max_two_hop_per_edge),
            },
            device_arrays={
                "row_offsets": row_offsets,
                "column_indices": column_indices,
                "directed_src": directed_src,
                "two_hop_counts_per_directed_edge": two_hop_counts,
            },
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

    if materialize_host_columns:
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
                int(two_hop_host[:, 2].sum()) if len(two_hop_host) else 0,
            )

        (
            directed_edges_host,
            row_offsets_host,
            column_indices_host,
            two_hop_host,
            triangle_count,
            duplicate_two_hop_count,
        ) = sync_time(
            "download_needed_columns_ms",
            download_needed_columns,
        )
    else:
        def collect_device_summary_counts():
            duplicate_count = int(two_hop_weights.sum().get()) if int(two_hop_weights.size) else 0
            return int(triangle_count_device.get()), duplicate_count

        triangle_count, duplicate_two_hop_count = sync_time(
            "device_count_summary_ms",
            collect_device_summary_counts,
        )
        directed_edges_host = RTGraphHostColumnPlaceholder(
            length=int(column_indices.size),
            shape=(int(column_indices.size), 2),
            reason="CuPy summary route skipped directed_edges host materialization",
        )
        row_offsets_host = RTGraphHostColumnPlaceholder(
            length=int(row_offsets.size),
            shape=(int(row_offsets.size),),
            reason="CuPy summary route skipped row_offsets host materialization",
        )
        column_indices_host = RTGraphHostColumnPlaceholder(
            length=int(column_indices.size),
            shape=(int(column_indices.size),),
            reason="CuPy summary route skipped column_indices host materialization",
        )
        two_hop_host = RTGraphHostColumnPlaceholder(
            length=int(two_hop_src.size),
            shape=(int(two_hop_src.size), 3),
            reason="CuPy summary route skipped two_hop_rays_2a1 host materialization",
        )
    timing_ms["total_partner_ms"] = sum(value for key, value in timing_ms.items() if key.endswith("_ms"))

    removed_low_degree_vertex_count = int(node_count - directed_node_count)
    removed_low_degree_edge_count = int((~keep_edge).sum().get())
    removed_duplicate_or_self_edge_count = int(edges_np.shape[0] - removed_low_degree_edge_count - len(directed_edges_host))
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
        partner_timing_ms={key: round(value, 3) for key, value in timing_ms.items()}
        | {
            "host_columns_materialized": bool(materialize_host_columns),
            "two_hop_summary_materialized": True,
            "triangle_count_available": True,
        },
        device_arrays={
            "row_offsets": row_offsets,
            "column_indices": column_indices,
            "directed_src": directed_src,
            "two_hop_src": two_hop_src,
            "two_hop_dst": two_hop_dst,
            "two_hop_weights": two_hop_weights,
        },
    )


def build_rt_graph_triangle_summary_contract_numba_binary(path: str | Path) -> RTGraphTriangleSummaryContract:
    """Build a summary contract with Numba CUDA device columns.

    This is a no-C++ reference partner route. M27 used the transitional
    ``cpu_contract_then_numba_device_upload`` path. The current route reads the
    binary edge file directly, builds the compact CSR/two-hop summary with
    vectorized array operations, then uploads the summary columns to Numba
    device arrays for the OptiX device-column ABI.
    """
    import time

    import numpy as np
    from numba import cuda

    timing_ms: dict[str, float] = {}

    started = time.perf_counter()
    edges_np = np.fromfile(path, dtype=np.int32)
    if edges_np.size % 2 != 0:
        raise ValueError("RT-Graph binary edge file size must be a multiple of two int32 values")
    edges_np = edges_np.reshape(-1, 2).astype(np.int64, copy=False)
    if np.any(edges_np < 0):
        raise ValueError("RT-Graph edge endpoints must be non-negative integers")
    timing_ms["load_np_ms"] = (time.perf_counter() - started) * 1000.0

    started = time.perf_counter()
    summary = _build_rt_graph_triangle_summary_arrays_numpy(edges_np)
    timing_ms["direct_binary_summary_ms"] = (time.perf_counter() - started) * 1000.0

    directed_edges_host = summary["directed_edges"]
    row_offsets_host = summary["row_offsets"]
    column_indices_host = summary["column_indices"]
    two_hop_host = summary["two_hop_rays_2a1"]
    triangle_count = int(summary["triangle_count"])
    duplicate_two_hop_count = int(two_hop_host[:, 2].sum(dtype=np.int64)) if two_hop_host.size else 0

    started = time.perf_counter()
    device_arrays = {
        "row_offsets": cuda.to_device(row_offsets_host),
        "column_indices": cuda.to_device(column_indices_host),
        "directed_src": cuda.to_device(directed_edges_host[:, 0].copy()),
        "two_hop_src": cuda.to_device(two_hop_host[:, 0].copy()),
        "two_hop_dst": cuda.to_device(two_hop_host[:, 1].copy()),
        "two_hop_weights": cuda.to_device(two_hop_host[:, 2].astype(np.uint64, copy=True)),
    }
    cuda.synchronize()
    timing_ms["numba_device_upload_ms"] = (time.perf_counter() - started) * 1000.0
    timing_ms["total_partner_ms"] = sum(value for key, value in timing_ms.items() if key.endswith("_ms"))

    return RTGraphTriangleSummaryContract(
        original_edge_count=int(edges_np.shape[0]),
        compacted_vertex_count=int(summary["compacted_vertex_count"]),
        directed_vertex_count=int(summary["directed_vertex_count"]),
        directed_edges=directed_edges_host,
        row_offsets=row_offsets_host,
        column_indices=column_indices_host,
        triangle_count_value=triangle_count,
        two_hop_rays_2a1=two_hop_host,
        duplicate_two_hop_relation_count_value=duplicate_two_hop_count,
        removed_low_degree_vertex_count=int(summary["removed_low_degree_vertex_count"]),
        removed_low_degree_edge_count=int(summary["removed_low_degree_edge_count"]),
        removed_duplicate_or_self_edge_count=int(summary["removed_duplicate_or_self_edge_count"]),
        partner="numba",
        partner_timing_ms={
            key: round(value, 3) for key, value in timing_ms.items()
        }
        | {
            "construction_mode": "direct_binary_numpy_summary_then_numba_device_upload",
            "supersedes_construction_mode": "cpu_contract_then_numba_device_upload",
            "bounded_id_remap_fast_path": bool(summary.get("bounded_id_remap_fast_path")),
            "dense_label_fast_path": bool(summary.get("dense_label_fast_path")),
            "directed_sorted_unique_fast_path": bool(summary.get("directed_sorted_unique_fast_path")),
            "two_hop_sorted_rle_fast_path": bool(summary.get("two_hop_sorted_rle_fast_path")),
        },
        device_arrays=device_arrays,
    )


def _build_rt_graph_triangle_summary_arrays_numpy(edges_np):
    import numpy as np

    if edges_np.size == 0:
        return {
            "compacted_vertex_count": 0,
            "directed_vertex_count": 0,
            "directed_edges": np.empty((0, 2), dtype=np.int64),
            "row_offsets": np.zeros(1, dtype=np.int64),
            "column_indices": np.empty(0, dtype=np.int64),
            "triangle_count": 0,
            "two_hop_rays_2a1": np.empty((0, 3), dtype=np.int64),
            "removed_low_degree_vertex_count": 0,
            "removed_low_degree_edge_count": 0,
            "removed_duplicate_or_self_edge_count": 0,
            "bounded_id_remap_fast_path": False,
            "dense_label_fast_path": False,
            "directed_sorted_unique_fast_path": False,
            "two_hop_sorted_rle_fast_path": False,
        }

    endpoints = edges_np.reshape(-1)
    bounded_inputs = _try_bounded_id_triangle_summary_inputs_numpy(edges_np, endpoints)
    bounded_id_remap_fast_path = bounded_inputs is not None
    dense_label_fast_path = False
    if bounded_inputs is None:
        compacted_vertex_ids, inverse = np.unique(endpoints, return_inverse=True)
        compacted_edges = inverse.reshape(-1, 2).astype(np.int64, copy=False)
        node_count = int(compacted_vertex_ids.size)
        degree = np.bincount(compacted_edges.reshape(-1), minlength=node_count).astype(np.int64, copy=False)
    else:
        compacted_edges, node_count, degree, dense_label_fast_path = bounded_inputs

    src = compacted_edges[:, 0]
    dst = compacted_edges[:, 1]
    deg_src = degree[src]
    deg_dst = degree[dst]
    swap = (deg_src > deg_dst) | ((deg_src == deg_dst) & (src > dst))
    oriented_src = np.where(swap, dst, src)
    oriented_dst = np.where(swap, src, dst)

    keep_vertex = degree > 1
    remap = np.cumsum(keep_vertex.astype(np.int64)) - 1
    keep_edge = keep_vertex[oriented_src] & keep_vertex[oriented_dst]
    directed_node_count = int(keep_vertex.sum())
    removed_low_degree_edge_count = int((~keep_edge).sum())
    directed_sorted_unique_fast_path = False

    if directed_node_count == 0 or not np.any(keep_edge):
        directed_edge_keys = np.empty(0, dtype=np.int64)
        directed_src = np.empty(0, dtype=np.int64)
        column_indices = np.empty(0, dtype=np.int64)
        row_offsets = np.zeros(directed_node_count + 1, dtype=np.int64)
    else:
        vsrc = remap[oriented_src[keep_edge]]
        vdst = remap[oriented_dst[keep_edge]]
        nonself = vsrc != vdst
        vsrc = vsrc[nonself]
        vdst = vdst[nonself]
        if vsrc.size:
            directed_key_candidates = (vsrc * directed_node_count + vdst).astype(np.int64, copy=False)
            directed_edge_keys, directed_sorted_unique_fast_path = _unique_int64_keys_numpy(
                directed_key_candidates
            )
            directed_src = (directed_edge_keys // directed_node_count).astype(np.int64, copy=False)
            column_indices = (directed_edge_keys - directed_src * directed_node_count).astype(np.int64, copy=False)
            row_counts = np.bincount(directed_src, minlength=directed_node_count).astype(np.int64, copy=False)
            row_offsets = np.empty(directed_node_count + 1, dtype=np.int64)
            row_offsets[0] = 0
            row_offsets[1:] = np.cumsum(row_counts)
        else:
            directed_edge_keys = np.empty(0, dtype=np.int64)
            directed_src = np.empty(0, dtype=np.int64)
            column_indices = np.empty(0, dtype=np.int64)
            row_offsets = np.zeros(directed_node_count + 1, dtype=np.int64)

    two_hop_host, triangle_count, two_hop_meta = _build_two_hop_summary_numpy(
        directed_edge_keys=directed_edge_keys,
        directed_node_count=directed_node_count,
        row_offsets=row_offsets,
        column_indices=column_indices,
    )
    two_hop_sorted_rle_fast_path = bool(two_hop_meta["sorted_rle_fast_path"])
    directed_edges_host = (
        np.column_stack((directed_src, column_indices)).astype(np.int64, copy=False)
        if directed_src.size
        else np.empty((0, 2), dtype=np.int64)
    )
    removed_duplicate_or_self_edge_count = int(
        edges_np.shape[0] - removed_low_degree_edge_count - directed_edges_host.shape[0]
    )
    return {
        "compacted_vertex_count": node_count,
        "directed_vertex_count": directed_node_count,
        "directed_edges": directed_edges_host,
        "row_offsets": row_offsets,
        "column_indices": column_indices,
        "triangle_count": int(triangle_count),
        "two_hop_rays_2a1": two_hop_host,
        "removed_low_degree_vertex_count": int(node_count - directed_node_count),
        "removed_low_degree_edge_count": removed_low_degree_edge_count,
        "removed_duplicate_or_self_edge_count": removed_duplicate_or_self_edge_count,
        "bounded_id_remap_fast_path": bounded_id_remap_fast_path,
        "dense_label_fast_path": dense_label_fast_path,
        "directed_sorted_unique_fast_path": directed_sorted_unique_fast_path,
        "two_hop_sorted_rle_fast_path": two_hop_sorted_rle_fast_path,
    }


def _try_bounded_id_triangle_summary_inputs_numpy(edges_np, endpoints):
    import numpy as np

    if endpoints.size == 0 or np.any(endpoints < 0):
        return None
    max_endpoint = int(endpoints.max())
    # Avoid accidental huge bincount/remap arrays for sparse id spaces. When the
    # observed id range is bounded by the input size, bincount-based remapping is
    # a generic fast path for dense and moderately gapped nonnegative ids.
    max_range = endpoints.size * _TRIANGLE_SUMMARY_BOUNDED_ID_REMAP_MAX_RANGE_FACTOR
    if max_endpoint + 1 > max_range:
        return None
    degree_by_original_id = np.bincount(endpoints, minlength=max_endpoint + 1).astype(np.int64, copy=False)
    touched = degree_by_original_id > 0
    node_count = int(np.count_nonzero(touched))
    if node_count == 0:
        return None
    remap = np.cumsum(touched.astype(np.int64)) - 1
    compacted_edges = remap[edges_np].astype(np.int64, copy=False)
    degree = degree_by_original_id[touched].astype(np.int64, copy=False)
    dense_label_fast_path = node_count == max_endpoint + 1
    return compacted_edges, node_count, degree, dense_label_fast_path


def _try_dense_label_triangle_summary_inputs_numpy(edges_np, endpoints):
    bounded = _try_bounded_id_triangle_summary_inputs_numpy(edges_np, endpoints)
    if bounded is None:
        return None
    compacted_edges, node_count, degree, dense_label_fast_path = bounded
    if not dense_label_fast_path:
        return None
    return compacted_edges, node_count, degree


def _unique_int64_keys_numpy(keys):
    import numpy as np

    keys = keys.astype(np.int64, copy=False)
    if keys.size <= 1:
        return keys, True
    if np.all(keys[1:] >= keys[:-1]):
        boundary = np.empty(keys.size, dtype=bool)
        boundary[0] = True
        boundary[1:] = keys[1:] != keys[:-1]
        if np.all(boundary):
            return keys, True
        return keys[boundary].astype(np.int64, copy=False), True
    return np.unique(keys).astype(np.int64, copy=False), False


def _unique_int64_keys_counts_numpy(keys):
    import numpy as np

    keys = keys.astype(np.int64, copy=False)
    if keys.size == 0:
        return keys, np.empty(0, dtype=np.int64), True
    if keys.size == 1:
        return keys, np.ones(1, dtype=np.int64), True
    if np.all(keys[1:] >= keys[:-1]):
        boundary = np.empty(keys.size, dtype=bool)
        boundary[0] = True
        boundary[1:] = keys[1:] != keys[:-1]
        starts = np.flatnonzero(boundary).astype(np.int64, copy=False)
        ends = np.empty(starts.size, dtype=np.int64)
        if starts.size > 1:
            ends[:-1] = starts[1:]
        ends[-1] = keys.size
        counts = (ends - starts).astype(np.int64, copy=False)
        return keys[starts].astype(np.int64, copy=False), counts, True
    unique_keys, unique_counts = np.unique(keys, return_counts=True)
    return (
        unique_keys.astype(np.int64, copy=False),
        unique_counts.astype(np.int64, copy=False),
        False,
    )


def _build_two_hop_summary_numpy(
    *,
    directed_edge_keys,
    directed_node_count: int,
    row_offsets,
    column_indices,
):
    import numpy as np

    if directed_node_count == 0 or column_indices.size == 0:
        return np.empty((0, 3), dtype=np.int64), 0, {"sorted_rle_fast_path": False}
    out_degree = row_offsets[1:] - row_offsets[:-1]
    edge_src = np.repeat(np.arange(directed_node_count, dtype=np.int64), out_degree)
    edge_mid = column_indices
    counts = out_degree[edge_mid]
    nonempty = counts > 0
    counts = counts[nonempty]
    if counts.size == 0:
        return np.empty((0, 3), dtype=np.int64), 0, {"sorted_rle_fast_path": False}
    edge_src = edge_src[nonempty]
    starts = row_offsets[edge_mid[nonempty]]
    total_two_hop = int(counts.sum())
    repeated_starts = np.repeat(starts, counts)
    repeated_prefix = np.repeat(np.cumsum(counts) - counts, counts)
    dst_index = repeated_starts + (np.arange(total_two_hop, dtype=np.int64) - repeated_prefix)
    two_hop_dst = column_indices[dst_index]
    two_hop_src = np.repeat(edge_src, counts)
    two_hop_keys = two_hop_src * directed_node_count + two_hop_dst
    unique_keys, unique_counts, sorted_rle_fast_path = _unique_int64_keys_counts_numpy(two_hop_keys)

    positions = np.searchsorted(directed_edge_keys, unique_keys)
    in_range = positions < directed_edge_keys.size
    found = np.zeros(unique_keys.shape, dtype=bool)
    found[in_range] = directed_edge_keys[positions[in_range]] == unique_keys[in_range]
    triangle_count = int(unique_counts[found].sum(dtype=np.int64))
    ray_src = unique_keys // directed_node_count
    ray_dst = unique_keys - ray_src * directed_node_count
    two_hop_host = np.column_stack((ray_src, ray_dst, unique_counts)).astype(np.int64, copy=False)
    return two_hop_host, triangle_count, {"sorted_rle_fast_path": sorted_rle_fast_path}


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


def _edges_to_numpy(edges: Iterable[Edge]):
    import numpy as np

    rows = tuple(edges)
    if not rows:
        return np.empty((0, 2), dtype=np.int64)
    return np.asarray(rows, dtype=np.int64).reshape(-1, 2)


def _two_hop_to_numpy(rows: Iterable[tuple[int, int, int]]):
    import numpy as np

    materialized = tuple(rows)
    if not materialized:
        return np.empty((0, 3), dtype=np.int64)
    return np.asarray(materialized, dtype=np.int64).reshape(-1, 3)


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
