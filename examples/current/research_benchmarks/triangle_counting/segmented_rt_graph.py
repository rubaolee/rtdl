"""Memory-bounded RT-Graph triangle-counting geometry production.

The paper algorithm is selected by the application.  This module only
partitions the selected algorithm's independent source-vertex domain and
materializes one bounded ray/triangle segment at a time.  Scalar segment
results are exactly additive because the source coordinate is part of both
paper encodings.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tempfile
from typing import Iterator, Mapping


@dataclass(frozen=True)
class SegmentedRTGraphCSR:
    original_edge_count: int
    compacted_vertex_count: int
    directed_vertex_count: int
    row_offsets: object
    column_indices: object
    expected_triangle_count: int
    removed_low_degree_vertex_count: int
    removed_low_degree_edge_count: int
    removed_duplicate_or_self_edge_count: int
    input_path: str
    preprocessing: Mapping[str, object]

    @property
    def vertex_count(self) -> int:
        return self.directed_vertex_count

    @property
    def directed_edge_count(self) -> int:
        return len(self.column_indices)


def build_segmented_rt_graph_csr_binary(
    path: str | Path,
    *,
    expected_triangle_count: int,
    edge_chunk_count: int = 4_194_304,
) -> SegmentedRTGraphCSR:
    """Build the degree-oriented CSR without any global two-hop relation.

    Input edges remain memory-mapped.  Only an O(max_vertex_id + |E|) host
    representation is constructed; GPU memory is not touched.  The sorted
    uint64 edge-key array is temporary and is deleted before return.
    """

    import numpy as np

    source = Path(path)
    if expected_triangle_count < 0:
        raise ValueError("expected_triangle_count must be nonnegative")
    if edge_chunk_count <= 0:
        raise ValueError("edge_chunk_count must be positive")
    raw = np.memmap(source, mode="r", dtype="<i4")
    if raw.size % 2:
        raise ValueError("RT-Graph binary edge file size must contain int32 pairs")
    edges = raw.reshape(-1, 2)
    edge_count = int(edges.shape[0])
    if edge_count == 0:
        return SegmentedRTGraphCSR(
            original_edge_count=0,
            compacted_vertex_count=0,
            directed_vertex_count=0,
            row_offsets=np.zeros(1, dtype=np.int64),
            column_indices=np.empty(0, dtype=np.int64),
            expected_triangle_count=expected_triangle_count,
            removed_low_degree_vertex_count=0,
            removed_low_degree_edge_count=0,
            removed_duplicate_or_self_edge_count=0,
            input_path=str(source),
            preprocessing={
                "contract": "memory_bounded_host_csr_without_global_two_hop.v1",
                "edge_chunk_count": edge_chunk_count,
                "global_two_hop_materialized": False,
            },
        )

    minimum = None
    maximum = None
    for begin in range(0, edge_count, edge_chunk_count):
        chunk = edges[begin : begin + edge_chunk_count]
        chunk_min = int(chunk.min())
        chunk_max = int(chunk.max())
        minimum = chunk_min if minimum is None else min(minimum, chunk_min)
        maximum = chunk_max if maximum is None else max(maximum, chunk_max)
    if minimum is None or minimum < 0 or maximum is None:
        raise ValueError("segmented RT-Graph requires nonnegative int32 vertex ids")
    dense_vertex_extent = maximum + 1
    # A malicious sparse-id file must not turn the dense degree table into an
    # unbounded allocation.  Current paper datasets are well inside this
    # conservative relation to their edge count.
    if dense_vertex_extent > max(16_777_216, edge_count * 8 + 1):
        raise ValueError("SPARSE_VERTEX_ID_EXTENT_REQUIRES_EXTERNAL_REMAP")

    degree = np.zeros(dense_vertex_extent, dtype=np.int64)
    for begin in range(0, edge_count, edge_chunk_count):
        chunk = np.asarray(edges[begin : begin + edge_chunk_count])
        degree += np.bincount(chunk.reshape(-1), minlength=dense_vertex_extent)
    present = degree > 0
    keep_vertex = degree > 1
    compacted_vertex_count = int(present.sum())
    directed_vertex_count = int(keep_vertex.sum())
    remap = np.full(dense_vertex_extent, -1, dtype=np.int64)
    remap[keep_vertex] = np.arange(directed_vertex_count, dtype=np.int64)

    temporary = tempfile.NamedTemporaryFile(
        prefix="rtdl_segmented_edge_keys_", suffix=".u64", delete=False
    )
    temporary_path = Path(temporary.name)
    temporary.close()
    try:
        key_store = np.memmap(
            temporary_path,
            mode="w+",
            dtype=np.uint64,
            shape=(max(edge_count, 1),),
        )
        write_offset = 0
        removed_low_degree_edge_count = 0
        for begin in range(0, edge_count, edge_chunk_count):
            chunk = np.asarray(edges[begin : begin + edge_chunk_count])
            src = chunk[:, 0].astype(np.int64, copy=False)
            dst = chunk[:, 1].astype(np.int64, copy=False)
            deg_src = degree[src]
            deg_dst = degree[dst]
            swap = (deg_src > deg_dst) | ((deg_src == deg_dst) & (src > dst))
            oriented_src = np.where(swap, dst, src)
            oriented_dst = np.where(swap, src, dst)
            low_degree = ~(keep_vertex[oriented_src] & keep_vertex[oriented_dst])
            removed_low_degree_edge_count += int(low_degree.sum())
            valid = ~low_degree
            vsrc = remap[oriented_src[valid]]
            vdst = remap[oriented_dst[valid]]
            nonself = vsrc != vdst
            vsrc = vsrc[nonself].astype(np.uint64, copy=False)
            vdst = vdst[nonself].astype(np.uint64, copy=False)
            count = int(vsrc.size)
            if count:
                key_store[write_offset : write_offset + count] = (
                    vsrc * np.uint64(directed_vertex_count) + vdst
                )
                write_offset += count
        key_store.flush()
        if write_offset:
            unique_keys = np.unique(key_store[:write_offset])
            directed_src = (unique_keys // np.uint64(directed_vertex_count)).astype(
                np.int64, copy=False
            )
            column_indices = (
                unique_keys - directed_src.astype(np.uint64) * np.uint64(directed_vertex_count)
            ).astype(np.int64, copy=False)
            row_counts = np.bincount(
                directed_src, minlength=directed_vertex_count
            ).astype(np.int64, copy=False)
        else:
            unique_keys = np.empty(0, dtype=np.uint64)
            column_indices = np.empty(0, dtype=np.int64)
            row_counts = np.zeros(directed_vertex_count, dtype=np.int64)
        row_offsets = np.empty(directed_vertex_count + 1, dtype=np.int64)
        row_offsets[0] = 0
        row_offsets[1:] = np.cumsum(row_counts, dtype=np.int64)
        directed_edge_count = int(column_indices.size)
        removed_duplicate_or_self_edge_count = (
            edge_count - removed_low_degree_edge_count - directed_edge_count
        )
        return SegmentedRTGraphCSR(
            original_edge_count=edge_count,
            compacted_vertex_count=compacted_vertex_count,
            directed_vertex_count=directed_vertex_count,
            row_offsets=np.ascontiguousarray(row_offsets),
            column_indices=np.ascontiguousarray(column_indices),
            expected_triangle_count=int(expected_triangle_count),
            removed_low_degree_vertex_count=compacted_vertex_count
            - directed_vertex_count,
            removed_low_degree_edge_count=removed_low_degree_edge_count,
            removed_duplicate_or_self_edge_count=removed_duplicate_or_self_edge_count,
            input_path=str(source),
            preprocessing={
                "contract": "memory_bounded_host_csr_without_global_two_hop.v1",
                "edge_chunk_count": edge_chunk_count,
                "dense_vertex_extent": dense_vertex_extent,
                "temporary_edge_key_capacity": edge_count,
                "global_two_hop_materialized": False,
                "gpu_preprocessing_used": False,
            },
        )
    finally:
        try:
            del key_store
        except UnboundLocalError:
            pass
        temporary_path.unlink(missing_ok=True)


def _relation_count(contract: SegmentedRTGraphCSR, begin: int, end: int) -> int:
    import numpy as np

    row_offsets = contract.row_offsets
    columns = contract.column_indices
    out_degree = np.diff(row_offsets)
    edge_begin = int(row_offsets[begin])
    edge_end = int(row_offsets[end])
    if edge_begin == edge_end:
        return 0
    return int(out_degree[columns[edge_begin:edge_end]].sum(dtype=np.int64))


def _source_partitions(
    contract: SegmentedRTGraphCSR,
    *,
    max_relation_rows: int,
    max_directed_edge_rows: int,
) -> Iterator[tuple[int, int]]:
    if max_relation_rows <= 0:
        raise ValueError("max_relation_rows must be positive")
    if max_directed_edge_rows <= 0:
        raise ValueError("max_directed_edge_rows must be positive")
    pending = [(0, contract.vertex_count)]
    while pending:
        begin, end = pending.pop()
        if begin == end:
            continue
        work = _relation_count(contract, begin, end)
        edge_rows = int(contract.row_offsets[end] - contract.row_offsets[begin])
        if (
            work <= max_relation_rows
            and edge_rows <= max_directed_edge_rows
        ) or end - begin == 1:
            if edge_rows > max_directed_edge_rows:
                raise ValueError("SINGLE_SOURCE_DIRECTED_EDGE_BOUND_EXCEEDED")
            if work:
                yield begin, end
            continue
        middle = begin + (end - begin) // 2
        pending.append((middle, end))
        pending.append((begin, middle))


def _relation_arrays_for_source_range(
    contract: SegmentedRTGraphCSR,
    begin: int,
    end: int,
):
    import numpy as np

    row_offsets = contract.row_offsets
    columns = contract.column_indices
    out_degree = np.diff(row_offsets)
    edge_begin = int(row_offsets[begin])
    edge_end = int(row_offsets[end])
    edge_mid = columns[edge_begin:edge_end]
    source_degrees = out_degree[begin:end]
    edge_src = np.repeat(np.arange(begin, end, dtype=np.int64), source_degrees)
    edge_starts = np.repeat(row_offsets[begin:end], source_degrees)
    edge_local = np.arange(edge_begin, edge_end, dtype=np.int64) - edge_starts
    counts = out_degree[edge_mid]
    nonempty = counts > 0
    counts = counts[nonempty]
    edge_src = edge_src[nonempty]
    edge_local = edge_local[nonempty]
    edge_mid = edge_mid[nonempty]
    relation_count = int(counts.sum(dtype=np.int64)) if counts.size else 0
    if relation_count == 0:
        empty = np.empty(0, dtype=np.int64)
        return empty, empty, empty
    rel_src = np.repeat(edge_src, counts)
    rel_local = np.repeat(edge_local, counts)
    starts = row_offsets[edge_mid]
    repeated_starts = np.repeat(starts, counts)
    repeated_prefix = np.repeat(np.cumsum(counts, dtype=np.int64) - counts, counts)
    dst_index = repeated_starts + (
        np.arange(relation_count, dtype=np.int64) - repeated_prefix
    )
    return rel_src, rel_local, columns[dst_index]


def _split_oversized_source_relations(
    contract: SegmentedRTGraphCSR,
    source: int,
    *,
    max_relation_rows: int,
) -> Iterator[tuple[object, object, object]]:
    import numpy as np

    row_offsets = contract.row_offsets
    columns = contract.column_indices
    mids = columns[int(row_offsets[source]) : int(row_offsets[source + 1])]
    local_parts: list[object] = []
    dst_parts: list[object] = []
    used = 0
    for local_index, mid in enumerate(mids):
        destinations = columns[int(row_offsets[mid]) : int(row_offsets[mid + 1])]
        offset = 0
        while offset < len(destinations):
            room = max_relation_rows - used
            take = min(room, len(destinations) - offset)
            local_parts.append(np.full(take, local_index, dtype=np.int64))
            dst_parts.append(np.asarray(destinations[offset : offset + take]))
            used += take
            offset += take
            if used == max_relation_rows:
                rel_local = np.concatenate(local_parts)
                yield (
                    np.full(used, source, dtype=np.int64),
                    rel_local,
                    np.concatenate(dst_parts),
                )
                local_parts = []
                dst_parts = []
                used = 0
    if used:
        yield (
            np.full(used, source, dtype=np.int64),
            np.concatenate(local_parts),
            np.concatenate(dst_parts),
        )


def _host_geometry(
    contract: SegmentedRTGraphCSR,
    *,
    paper_algorithm: str,
    source_begin: int,
    source_end: int,
    rel_src,
    rel_local,
    rel_dst,
) -> tuple[dict[str, object], dict[str, object], object | None]:
    import numpy as np

    row_offsets = contract.row_offsets
    columns = contract.column_indices
    out_degree = np.diff(row_offsets)
    axis_vertex = contract.vertex_count / 2.0
    eps = 0.2
    edge_begin = int(row_offsets[source_begin])
    edge_end = int(row_offsets[source_end])
    edge_dst = columns[edge_begin:edge_end]
    edge_src = np.repeat(
        np.arange(source_begin, source_end, dtype=np.int64),
        out_degree[source_begin:source_end],
    )
    if paper_algorithm == "RT-1A2":
        max_adj_len = int(out_degree.max()) if out_degree.size else 0
        axis_x = max_adj_len / 2.0
        center_x = rel_local.astype(np.float64) - axis_x
        center_y = rel_src.astype(np.float64) - axis_vertex
        center_z = rel_dst.astype(np.float64) - axis_vertex
        primitive_count = int(rel_src.size)
        triangles = {
            "ids": np.arange(primitive_count, dtype=np.uint32),
            "x0": center_x,
            "y0": center_y,
            "z0": center_z + eps,
            "x1": center_x,
            "y1": center_y - eps,
            "z1": center_z - eps,
            "x2": center_x,
            "y2": center_y + eps,
            "z2": center_z - eps,
        }
        ray_count = int(edge_src.size)
        rays = {
            "ids": np.arange(ray_count, dtype=np.uint32),
            "ox": np.full(ray_count, -0.5 - axis_x, dtype=np.float64),
            "oy": edge_src.astype(np.float64) - axis_vertex,
            "oz": edge_dst.astype(np.float64) - axis_vertex,
            "dx": np.ones(ray_count, dtype=np.float64),
            "dy": np.zeros(ray_count, dtype=np.float64),
            "dz": np.zeros(ray_count, dtype=np.float64),
            "tmax": out_degree[edge_src].astype(np.float64),
        }
        return triangles, rays, None
    if paper_algorithm != "RT-2A1":
        raise ValueError("paper_algorithm must be RT-1A2 or RT-2A1")
    center_x = edge_src.astype(np.float64) - axis_vertex
    center_z = edge_dst.astype(np.float64) - axis_vertex
    primitive_count = int(edge_src.size)
    zero = np.zeros(primitive_count, dtype=np.float64)
    triangles = {
        "ids": np.arange(primitive_count, dtype=np.uint32),
        "x0": center_x,
        "y0": zero,
        "z0": center_z + eps,
        "x1": center_x - eps,
        "y1": zero,
        "z1": center_z - eps,
        "x2": center_x + eps,
        "y2": zero,
        "z2": center_z - eps,
    }
    keys = rel_src.astype(np.uint64) * np.uint64(contract.vertex_count) + rel_dst.astype(
        np.uint64
    )
    unique_keys, weights = np.unique(keys, return_counts=True)
    ray_src = (unique_keys // np.uint64(contract.vertex_count)).astype(np.int64)
    ray_dst = (unique_keys % np.uint64(contract.vertex_count)).astype(np.int64)
    ray_count = int(unique_keys.size)
    rays = {
        "ids": np.arange(ray_count, dtype=np.uint32),
        "ox": ray_src.astype(np.float64) - axis_vertex,
        "oy": np.full(ray_count, -0.1, dtype=np.float64),
        "oz": ray_dst.astype(np.float64) - axis_vertex,
        "dx": np.zeros(ray_count, dtype=np.float64),
        "dy": np.ones(ray_count, dtype=np.float64),
        "dz": np.zeros(ray_count, dtype=np.float64),
        "tmax": np.full(ray_count, 0.2, dtype=np.float64),
    }
    return triangles, rays, weights.astype(np.uint64, copy=False)


def iter_segmented_rt_graph_device_geometry(
    contract: SegmentedRTGraphCSR,
    *,
    paper_algorithm: str,
    max_relation_rows: int,
    max_directed_edge_rows: int | None = None,
    start_segment_id: int = 0,
    stop_segment_id: int | None = None,
) -> Iterator[dict[str, object]]:
    """Yield bounded CuPy columns for one caller-selected paper algorithm."""

    import cupy as cp

    if max_directed_edge_rows is None:
        max_directed_edge_rows = max_relation_rows
    if start_segment_id < 0:
        raise ValueError("start_segment_id must be nonnegative")
    if stop_segment_id is not None and stop_segment_id <= start_segment_id:
        raise ValueError("stop_segment_id must be greater than start_segment_id")
    segment_id = 0
    for source_begin, source_end in _source_partitions(
        contract,
        max_relation_rows=max_relation_rows,
        max_directed_edge_rows=max_directed_edge_rows,
    ):
        work = _relation_count(contract, source_begin, source_end)
        if source_end - source_begin == 1 and work > max_relation_rows:
            relation_parts = _split_oversized_source_relations(
                contract,
                source_begin,
                max_relation_rows=max_relation_rows,
            )
        else:
            relation_parts = (
                _relation_arrays_for_source_range(contract, source_begin, source_end),
            )
        part_index = 0
        for rel_src, rel_local, rel_dst in relation_parts:
            current_segment_id = segment_id
            segment_id += 1
            if current_segment_id < start_segment_id:
                part_index += 1
                continue
            if stop_segment_id is not None and current_segment_id >= stop_segment_id:
                return
            triangles, rays, weights = _host_geometry(
                contract,
                paper_algorithm=paper_algorithm,
                source_begin=source_begin,
                source_end=source_end,
                rel_src=rel_src,
                rel_local=rel_local,
                rel_dst=rel_dst,
            )
            ray_rows = int(rays["ids"].size)
            primitive_rows = int(triangles["ids"].size)
            if paper_algorithm == "RT-1A2":
                if primitive_rows > max_relation_rows or ray_rows > max_directed_edge_rows:
                    raise ValueError("SEGMENT_RESOURCE_ROW_BOUND_EXCEEDED")
            elif primitive_rows > max_directed_edge_rows or ray_rows > max_relation_rows:
                raise ValueError("SEGMENT_RESOURCE_ROW_BOUND_EXCEEDED")
            host_geometry_bytes = sum(int(value.nbytes) for value in triangles.values())
            host_geometry_bytes += sum(int(value.nbytes) for value in rays.values())
            if weights is not None:
                host_geometry_bytes += int(weights.nbytes)
            device_segment = {
                "segment_id": current_segment_id - start_segment_id,
                "triangles": {key: cp.asarray(value) for key, value in triangles.items()},
                "rays": {key: cp.asarray(value) for key, value in rays.items()},
                "ray_weights": None if weights is None else cp.asarray(weights),
                "partition": {
                    "source_begin": source_begin,
                    "source_end": source_end,
                    "oversized_source_part": part_index,
                    "global_segment_id": current_segment_id,
                },
                "relation_count": int(rel_src.size),
                "host_geometry_bytes": host_geometry_bytes,
            }
            try:
                yield device_segment
            finally:
                del device_segment
                cp.get_default_memory_pool().free_all_blocks()
            part_index += 1


def count_segmented_rt_graph_segments(
    contract: SegmentedRTGraphCSR,
    *,
    max_relation_rows: int,
    max_directed_edge_rows: int | None = None,
) -> int:
    """Count deterministic physical segments without touching the GPU."""

    if max_directed_edge_rows is None:
        max_directed_edge_rows = max_relation_rows
    count = 0
    for begin, end in _source_partitions(
        contract,
        max_relation_rows=max_relation_rows,
        max_directed_edge_rows=max_directed_edge_rows,
    ):
        work = _relation_count(contract, begin, end)
        if end - begin == 1 and work > max_relation_rows:
            count += (work + max_relation_rows - 1) // max_relation_rows
        else:
            count += 1
    return count


__all__ = [
    "SegmentedRTGraphCSR",
    "build_segmented_rt_graph_csr_binary",
    "count_segmented_rt_graph_segments",
    "iter_segmented_rt_graph_device_geometry",
]
