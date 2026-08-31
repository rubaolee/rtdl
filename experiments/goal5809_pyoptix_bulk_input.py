"""Vectorized host-input packing for the Goal5809 PyOptiX successor.

The frozen Goal5802 PyOptiX arm remains available unchanged by default.  The
Goal5809 two-application worker opts into these immutable host arrays while it
is inside the same prepare+execute phase that owns GAS construction and first
execution.  Only input representation changes: the existing PyOptiX owner,
pipeline, SBT, CuPy upload, device compaction, status-before-output boundary,
and route-independent oracle remain authoritative.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from operator import itemgetter
from typing import Any, Mapping


RELATION_PACKING_SCHEMA = "rtdl.goal5809.pyoptix_relation_bulk_host_input.v1"
TRIANGLE_PACKING_SCHEMA = "rtdl.goal5809.pyoptix_triangle_bulk_host_input.v1"


def _numeric_matrix(
    np: Any, rows: object, *, columns: int, label: str,
) -> Any:
    """Admit one rectangular finite numeric matrix without a row loop."""

    raw = np.asarray(rows)
    if raw.ndim != 2 or raw.shape[1] != columns or raw.shape[0] <= 0:
        raise ValueError(
            f"{label} must be a non-empty N-by-{columns} numeric matrix")
    if raw.dtype.kind not in "iuf":
        raise ValueError(f"{label} must contain only real numeric scalars")
    values = np.asarray(raw, dtype=np.float64, order="C")
    if not bool(np.isfinite(values).all()):
        raise ValueError(f"{label} contains a non-finite value")
    return values


def _u32_column(np: Any, values: Any, *, label: str) -> Any:
    if not bool(np.equal(values, np.floor(values)).all()) \
            or bool((values < 0).any()) \
            or bool((values > np.float64((1 << 32) - 1)).any()):
        raise ValueError(f"{label} is not an exact unsigned-32 value")
    return np.asarray(values, dtype=np.uint32, order="C")


def _u64_vector(np: Any, values: object, *, count: int, label: str) -> Any:
    raw = np.asarray(values)
    if raw.ndim != 1 or raw.shape[0] != count:
        raise ValueError(f"{label} length differs from the ray count")
    if raw.dtype.kind not in "iu" or raw.dtype.kind == "b":
        raise ValueError(f"{label} must contain exact integer values")
    if raw.dtype.kind == "i" and bool((raw < 0).any()):
        raise ValueError(f"{label} contains a negative value")
    try:
        packed = np.asarray(raw, dtype=np.uint64, order="C")
    except (OverflowError, TypeError, ValueError) as error:
        raise ValueError(f"{label} is not representable as unsigned-64") \
            from error
    # The cast must be value-preserving.  This rejects signed overflow and any
    # future caller whose ndarray dtype cannot represent the frozen ABI.
    if not bool(np.equal(raw, packed).all()):
        raise ValueError(f"{label} changes value under unsigned-64 packing")
    return packed


def _freeze_c_array(np: Any, value: Any, *, dtype: Any, label: str) -> Any:
    array = np.ascontiguousarray(value, dtype=dtype)
    if array.dtype != dtype or not bool(array.flags.c_contiguous):
        raise RuntimeError(f"{label} did not materialize the exact C ABI")
    array.setflags(write=False)
    return array


def _pack_boxes(np: Any, box_dtype: Any, rows: object, *, label: str) -> Any:
    matrix = _numeric_matrix(np, rows, columns=5, label=label)
    coordinates = np.asarray(matrix[:, :4], dtype=np.float32, order="C")
    if not bool(np.isfinite(coordinates).all()):
        raise ValueError(f"{label} overflows the binary32 coordinate ABI")
    if bool((coordinates[:, 0] > coordinates[:, 2]).any()) \
            or bool((coordinates[:, 1] > coordinates[:, 3]).any()):
        raise ValueError(f"{label} contains an inverted closed box")
    item_ids = _u32_column(np, matrix[:, 4], label=f"{label}.item_id")

    result = np.zeros(matrix.shape[0], dtype=box_dtype)
    # Seven fixed-column vector assignments replace Goal5802's N row-level
    # Python assignments.  They preserve the exact 28-byte structured ABI.
    result["lower_x"] = coordinates[:, 0]
    result["lower_y"] = coordinates[:, 1]
    result["upper_x"] = coordinates[:, 2]
    result["upper_y"] = coordinates[:, 3]
    result["item_id"] = item_ids
    return _freeze_c_array(
        np, result, dtype=box_dtype, label=f"{label}.packed")


@dataclass(frozen=True, slots=True)
class RelationBulkHostInputs:
    indexed: Any
    sources: Any

    def checked_arrays(self, baseline: Any) -> tuple[Any, Any]:
        expected = baseline.BOX_DTYPE
        for label, value in (
            ("relation.indexed", self.indexed),
            ("relation.sources", self.sources),
        ):
            if value.dtype != expected \
                    or value.ndim != 1 or value.shape[0] <= 0 \
                    or not bool(value.flags.c_contiguous) \
                    or bool(value.flags.writeable):
                raise RuntimeError(f"{label} bulk host ABI is invalid")
        return self.indexed, self.sources

    def receipt(self) -> dict[str, object]:
        return {
            "schema": RELATION_PACKING_SCHEMA,
            "packing": "NUMPY_VECTORIZED_FIXED_COLUMN_ASSIGNMENT",
            "python_row_assignment_count": 0,
            "indexed_count": int(self.indexed.shape[0]),
            "source_count": int(self.sources.shape[0]),
            "indexed_bytes": int(self.indexed.nbytes),
            "source_bytes": int(self.sources.nbytes),
            "device_transfer": (
                "EXISTING_CUPY_STREAM_ORDERED_PINNED_H2D_UNCHANGED"),
        }


@dataclass(frozen=True, slots=True)
class TriangleBulkHostInputs:
    vertices: Any
    rays: Any
    weights: Any
    maximum: Any

    def checked_arrays(self, baseline: Any) -> tuple[Any, Any, Any, Any]:
        checks = (
            ("triangle.vertices", self.vertices, baseline.np.float32, 2),
            ("triangle.rays", self.rays, baseline.RAY_DTYPE, 1),
            ("triangle.weights", self.weights, baseline.np.uint64, 1),
        )
        for label, value, dtype, ndim in checks:
            if value.dtype != dtype or value.ndim != ndim \
                    or value.shape[0] <= 0 \
                    or not bool(value.flags.c_contiguous) \
                    or bool(value.flags.writeable):
                raise RuntimeError(f"{label} bulk host ABI is invalid")
        if self.vertices.shape[1] != 3 \
                or self.vertices.shape[0] % 3 != 0 \
                or self.rays.shape[0] != self.weights.shape[0]:
            raise RuntimeError("triangle bulk host shapes are inconsistent")
        if type(self.maximum) is not baseline.np.float32 \
                or not bool(baseline.np.isfinite(self.maximum)):
            raise RuntimeError("triangle maximum bulk host ABI is invalid")
        return self.vertices, self.rays, self.weights, self.maximum

    def receipt(self) -> dict[str, object]:
        return {
            "schema": TRIANGLE_PACKING_SCHEMA,
            "packing": "NUMPY_VECTORIZED_FIXED_COLUMN_ASSIGNMENT",
            "python_ray_assignment_count": 0,
            "vertex_count": int(self.vertices.shape[0]),
            "ray_count": int(self.rays.shape[0]),
            "vertex_bytes": int(self.vertices.nbytes),
            "ray_bytes": int(self.rays.nbytes),
            "weight_bytes": int(self.weights.nbytes),
            "device_transfer": (
                "EXISTING_CUPY_STREAM_ORDERED_PINNED_H2D_UNCHANGED"),
        }


def pack_relation_host_inputs(
    baseline: Any, workload: Mapping[str, object],
) -> RelationBulkHostInputs:
    """Pack the two matched relation arrays inside successor preparation."""

    indexed = _pack_boxes(
        baseline.np, baseline.BOX_DTYPE, workload["indexed"],
        label="relation.indexed")
    sources = _pack_boxes(
        baseline.np, baseline.BOX_DTYPE, workload["sources"],
        label="relation.sources")
    return RelationBulkHostInputs(indexed=indexed, sources=sources)


def pack_triangle_host_inputs(
    baseline: Any, workload: Mapping[str, object],
) -> TriangleBulkHostInputs:
    """Pack vertices, rays, and weights without a per-ray Python loop."""

    np = baseline.np
    vertex_rows = workload["vertices"]
    try:
        vertex_count = len(vertex_rows)  # type: ignore[arg-type]
        vertex_widths = np.fromiter(
            map(len, vertex_rows), dtype=np.intp, count=vertex_count)
    except (TypeError, ValueError) as error:
        raise ValueError("triangle.vertices is not a rectangular matrix") \
            from error
    if vertex_count <= 0 or vertex_widths.shape != (vertex_count,) \
            or not bool((vertex_widths == 3).all()):
        raise ValueError("triangle.vertices must be a non-empty N-by-3 matrix")
    try:
        vertices = np.fromiter(
            chain.from_iterable(vertex_rows), dtype=np.float32,
            count=vertex_count * 3).reshape((vertex_count, 3))
    except (OverflowError, TypeError, ValueError) as error:
        raise ValueError("triangle.vertices contains a malformed scalar") \
            from error
    if not bool(np.isfinite(vertices).all()):
        raise ValueError("triangle.vertices contains a non-finite value")
    vertices = _freeze_c_array(
        np, vertices, dtype=np.float32, label="triangle.vertices.packed")
    if vertex_count % 3:
        raise ValueError("triangle vertex count is not divisible by three")

    query_rows = workload["queries"]
    try:
        query_count = len(query_rows)  # type: ignore[arg-type]
        query_widths = np.fromiter(
            map(len, query_rows), dtype=np.intp, count=query_count)
        vector_rows = chain.from_iterable(
            map(itemgetter(0, 1), query_rows))
        vector_widths = np.fromiter(
            map(len, vector_rows), dtype=np.intp, count=query_count * 2)
    except (IndexError, TypeError, ValueError) as error:
        raise ValueError("triangle query vectors are malformed") from error
    if query_count <= 0 or query_widths.shape != (query_count,) \
            or not bool((query_widths == 3).all()) \
            or vector_widths.shape != (query_count * 2,) \
            or not bool((vector_widths == 3).all()):
        raise ValueError("triangle.queries must be a non-empty N-by-3 matrix")
    try:
        query_vectors = np.fromiter(
            chain.from_iterable(chain.from_iterable(
                map(itemgetter(0, 1), query_rows))),
            dtype=np.float32, count=query_count * 6).reshape((query_count, 6))
        maxima_f32 = np.fromiter(
            map(itemgetter(2), query_rows), dtype=np.float32,
            count=query_count)
    except (IndexError, OverflowError, TypeError, ValueError) as error:
        raise ValueError("triangle query vectors are malformed") from error
    if query_vectors.shape != (query_count, 6) \
            or maxima_f32.shape != (query_count,) \
            or not bool(np.isfinite(query_vectors).all()) \
            or not bool(np.isfinite(maxima_f32).all()):
        raise ValueError("triangle query vectors are non-finite or malformed")

    if not bool((maxima_f32 == maxima_f32[0]).all()):
        raise ValueError("PyOptiX frozen device ABI accepts one common tmax")

    rays = np.zeros(query_count, dtype=baseline.RAY_DTYPE)
    rays["origin_x"] = query_vectors[:, 0]
    rays["origin_y"] = query_vectors[:, 1]
    rays["origin_z"] = query_vectors[:, 2]
    rays["direction_x"] = query_vectors[:, 3]
    rays["direction_y"] = query_vectors[:, 4]
    rays["direction_z"] = query_vectors[:, 5]
    rays = _freeze_c_array(
        np, rays, dtype=baseline.RAY_DTYPE, label="triangle.rays.packed")
    weights = _u64_vector(
        np, workload["weights"], count=query_count,
        label="triangle.weights")
    weights = _freeze_c_array(
        np, weights, dtype=np.uint64, label="triangle.weights.packed")
    maximum = np.float32(maxima_f32[0])
    return TriangleBulkHostInputs(
        vertices=vertices, rays=rays, weights=weights, maximum=maximum)
