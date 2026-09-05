"""Packed-host adapters for the frozen PyOptix comparison arms.

The adapter contains representation conversion only. It does not choose an
RT route, perform traversal, compact hits, or validate an application result.
"""

from __future__ import annotations

from typing import Any

from experiments.goal5809_pyoptix_bulk_input import (
    RelationBulkHostInputs,
    TriangleBulkHostInputs,
)

from .workloads import PackedRelationWorkload, PackedTriangleWorkload


def _require_count(value: object, *, label: str) -> int:
    if type(value) is not int or value <= 0:
        raise ValueError(f"{label} must be a positive exact integer")
    return value


def _require_bytes(
    value: object,
    *,
    expected_size: int,
    label: str,
) -> bytes:
    if type(value) is not bytes or len(value) != expected_size:
        raise ValueError(f"{label} byte size differs")
    return value


def _freeze(np: Any, value: Any, *, dtype: Any, label: str) -> Any:
    result = np.ascontiguousarray(value, dtype=dtype)
    if result.dtype != dtype or not bool(result.flags.c_contiguous):
        raise RuntimeError(f"{label} did not materialize its exact host ABI")
    result.setflags(write=False)
    return result


def _packed_boxes(
    baseline: Any,
    bounds_bytes: bytes,
    ids_bytes: bytes,
    *,
    count: int,
    label: str,
) -> Any:
    np = baseline.np
    bounds = np.frombuffer(
        _require_bytes(
            bounds_bytes,
            expected_size=count * 4 * 4,
            label=f"{label}.bounds",
        ),
        dtype="<f4",
    ).reshape((count, 4))
    ids = np.frombuffer(
        _require_bytes(
            ids_bytes,
            expected_size=count * 4,
            label=f"{label}.ids",
        ),
        dtype="<u4",
    )
    if not bool(np.isfinite(bounds).all()):
        raise ValueError(f"{label} contains non-finite bounds")
    if bool((bounds[:, 0] > bounds[:, 2]).any()) or bool(
        (bounds[:, 1] > bounds[:, 3]).any()
    ):
        raise ValueError(f"{label} contains an inverted closed box")
    result = np.zeros(count, dtype=baseline.BOX_DTYPE)
    result["lower_x"] = bounds[:, 0]
    result["lower_y"] = bounds[:, 1]
    result["upper_x"] = bounds[:, 2]
    result["upper_y"] = bounds[:, 3]
    result["item_id"] = ids
    return _freeze(
        np,
        result,
        dtype=baseline.BOX_DTYPE,
        label=f"{label}.packed",
    )


def relation_host_inputs(
    baseline: Any,
    workload: PackedRelationWorkload,
) -> RelationBulkHostInputs:
    if type(workload) is not PackedRelationWorkload:
        raise TypeError("Goal5848 relation packed authority differs")
    count = _require_count(workload.count, label="relation.count")
    indexed = _packed_boxes(
        baseline,
        workload.indexed_bounds_f32le,
        workload.indexed_ids_u32le,
        count=count,
        label="relation.indexed",
    )
    sources = _packed_boxes(
        baseline,
        workload.source_bounds_f32le,
        workload.source_ids_u32le,
        count=count,
        label="relation.sources",
    )
    return RelationBulkHostInputs(indexed=indexed, sources=sources)


def triangle_host_inputs(
    baseline: Any,
    workload: PackedTriangleWorkload,
) -> TriangleBulkHostInputs:
    if type(workload) is not PackedTriangleWorkload:
        raise TypeError("Goal5848 triangle packed authority differs")
    np = baseline.np
    vertex_count = _require_count(
        workload.vertex_count,
        label="triangle.vertex_count",
    )
    triangle_count = _require_count(
        workload.triangle_count,
        label="triangle.triangle_count",
    )
    query_count = _require_count(
        workload.query_count,
        label="triangle.query_count",
    )
    if vertex_count != 3 * triangle_count:
        raise ValueError("triangle vertex/primitive counts differ")
    vertices = np.frombuffer(
        _require_bytes(
            workload.vertices_f32le,
            expected_size=vertex_count * 3 * 4,
            label="triangle.vertices",
        ),
        dtype="<f4",
    ).reshape((vertex_count, 3))
    if not bool(np.isfinite(vertices).all()):
        raise ValueError("triangle vertices contain a non-finite value")
    vertices = _freeze(
        np,
        vertices,
        dtype=np.dtype("float32"),
        label="triangle.vertices.packed",
    )

    triangle_indices = np.frombuffer(
        _require_bytes(
            workload.triangles_u32le,
            expected_size=triangle_count * 3 * 4,
            label="triangle.indices",
        ),
        dtype="<u4",
    )
    expected_indices = np.arange(vertex_count, dtype=np.uint32)
    if not bool(np.array_equal(triangle_indices, expected_indices)):
        raise ValueError(
            "PyOptix frozen triangle ABI requires consecutive triangle indices"
        )

    vectors = np.frombuffer(
        _require_bytes(
            workload.rays_interleaved_6f_le,
            expected_size=query_count * 6 * 4,
            label="triangle.rays",
        ),
        dtype="<f4",
    ).reshape((query_count, 6))
    maxima = np.frombuffer(
        _require_bytes(
            workload.query_tmax_f32le,
            expected_size=query_count * 4,
            label="triangle.tmax",
        ),
        dtype="<f4",
    )
    if not bool(np.isfinite(vectors).all()) or not bool(
        np.isfinite(maxima).all()
    ):
        raise ValueError("triangle queries contain a non-finite value")
    if bool((maxima <= np.float32(0.0)).any()) or not bool(
        (maxima == maxima[0]).all()
    ):
        raise ValueError("triangle queries require one positive common tmax")
    if bool((vectors[:, 3:6] == np.float32(0.0)).all(axis=1).any()):
        raise ValueError("triangle query direction must be nonzero")

    rays = np.zeros(query_count, dtype=baseline.RAY_DTYPE)
    for field, column in (
        ("origin_x", 0),
        ("origin_y", 1),
        ("origin_z", 2),
        ("direction_x", 3),
        ("direction_y", 4),
        ("direction_z", 5),
    ):
        rays[field] = vectors[:, column]
    rays = _freeze(
        np,
        rays,
        dtype=baseline.RAY_DTYPE,
        label="triangle.rays.packed",
    )
    weights = np.frombuffer(
        _require_bytes(
            workload.query_weights_u64le,
            expected_size=query_count * 8,
            label="triangle.weights",
        ),
        dtype="<u8",
    )
    weights = _freeze(
        np,
        weights,
        dtype=np.dtype("uint64"),
        label="triangle.weights.packed",
    )
    return TriangleBulkHostInputs(
        vertices=vertices,
        rays=rays,
        weights=weights,
        maximum=np.float32(maxima[0]),
    )


__all__ = ["relation_host_inputs", "triangle_host_inputs"]
