#!/usr/bin/env python3
"""CPU-only segment planning for the Goal5791 RT-2A1 ablation.

The formal execution timer must remain continuous across device geometry and
OptiX/reducer work.  Fusion plans therefore cannot be discovered or deeply
verified between a generator yield and the corresponding device launch.  This
module derives the exact deterministic segment descriptors from the already
loaded degree-oriented CSR without importing CuPy or touching a GPU.  The
owning executor can use those descriptors to mint process-local, single-use
execution tokens during preparation.

This is harness planning, not a second paper algorithm.  It deliberately calls
the same frozen partition and relation-array helpers used by the production
geometry generator, and the formal worker must compare every observed device
segment with the planned descriptor before consuming its token.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping

from examples.current.research_benchmarks.triangle_counting import (
    segmented_rt_graph as _segmented,
)


SCHEMA = "rtdl.goal5791.rt2a1_segment_descriptor.v1"


def _positive_integer(value: object, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _descriptor(
    contract,
    *,
    segment_id: int,
    source_begin: int,
    source_end: int,
    oversized_source_part: int,
    rel_src,
    rel_dst,
) -> dict[str, object]:
    import numpy as np

    relation_count = int(rel_src.size)
    primitive_count = int(
        contract.row_offsets[source_end] - contract.row_offsets[source_begin]
    )
    if relation_count <= 0 or primitive_count <= 0:
        raise RuntimeError("Goal5791 planned an empty physical segment")
    keys = (
        rel_src.astype(np.uint64, copy=False) * np.uint64(contract.vertex_count)
        + rel_dst.astype(np.uint64, copy=False)
    )
    _unique_keys, weights = np.unique(keys, return_counts=True)
    query_count = int(weights.size)
    if query_count <= 0:
        raise RuntimeError("Goal5791 planned an RT-2A1 segment without rays")
    # Frozen RT-2A1 host geometry: nine F64 triangle columns plus U32 IDs,
    # seven F64 ray columns plus U32 IDs, and one U64 weight column.  This
    # supplies an O(1) observed-instance check without copying or hashing
    # device arrays inside the registered interval.
    host_geometry_bytes = 76 * primitive_count + 68 * query_count
    return {
        "schema": SCHEMA,
        "segment_id": segment_id,
        "partition": {
            "source_begin": source_begin,
            "source_end": source_end,
            "oversized_source_part": oversized_source_part,
            "global_segment_id": segment_id,
        },
        "relation_count": relation_count,
        "primitive_count": primitive_count,
        "query_count": query_count,
        "host_geometry_bytes": host_geometry_bytes,
        "maximum_weight": int(weights.max()),
        "weight_sum": int(weights.sum(dtype=np.uint64)),
        "paper_algorithm": "RT-2A1",
        "gpu_touched": False,
    }


def iter_rt2a1_segment_descriptors(
    contract,
    *,
    max_relation_rows: int,
    max_directed_edge_rows: int | None = None,
) -> Iterator[dict[str, object]]:
    """Yield every full-run RT-2A1 segment descriptor without GPU work."""

    relation_bound = _positive_integer(max_relation_rows, "max_relation_rows")
    edge_bound = (
        relation_bound
        if max_directed_edge_rows is None
        else _positive_integer(
            max_directed_edge_rows, "max_directed_edge_rows"
        )
    )
    segment_id = 0
    for source_begin, source_end in _segmented._source_partitions(
        contract,
        max_relation_rows=relation_bound,
        max_directed_edge_rows=edge_bound,
    ):
        work = _segmented._relation_count(contract, source_begin, source_end)
        if source_end - source_begin == 1 and work > relation_bound:
            relation_parts = _segmented._split_oversized_source_relations(
                contract,
                source_begin,
                max_relation_rows=relation_bound,
            )
        else:
            relation_parts = (
                _segmented._relation_arrays_for_source_range(
                    contract, source_begin, source_end
                ),
            )
        part_index = 0
        for rel_src, _rel_local, rel_dst in relation_parts:
            result = _descriptor(
                contract,
                segment_id=segment_id,
                source_begin=source_begin,
                source_end=source_end,
                oversized_source_part=part_index,
                rel_src=rel_src,
                rel_dst=rel_dst,
            )
            if int(result["relation_count"]) > relation_bound:
                raise RuntimeError("Goal5791 relation-row bound was exceeded")
            if int(result["primitive_count"]) > edge_bound:
                raise RuntimeError("Goal5791 directed-edge-row bound was exceeded")
            yield result
            segment_id += 1
            part_index += 1


def validate_observed_segment(
    planned: Mapping[str, object], observed: Mapping[str, object]
) -> None:
    """Fail closed unless one yielded device segment matches its CPU plan."""

    if not isinstance(planned, Mapping) or planned.get("schema") != SCHEMA:
        raise ValueError("Goal5791 segment plan has the wrong schema")
    if not isinstance(observed, Mapping):
        raise TypeError("Goal5791 observed segment must be a mapping")
    actual = {
        "segment_id": observed.get("segment_id"),
        "partition": observed.get("partition"),
        "relation_count": observed.get("relation_count"),
        "primitive_count": int(observed["triangles"]["ids"].size),
        "query_count": int(observed["rays"]["ids"].size),
        "host_geometry_bytes": observed.get("host_geometry_bytes"),
    }
    expected = {name: planned[name] for name in actual}
    if actual != expected:
        raise RuntimeError(
            "Goal5791 observed device segment differs from CPU plan: "
            f"expected={expected!r}, actual={actual!r}"
        )


__all__ = [
    "SCHEMA",
    "iter_rt2a1_segment_descriptors",
    "validate_observed_segment",
]
