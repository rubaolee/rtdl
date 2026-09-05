"""Canonical packed forms of the two frozen Goal5848 workloads.

This module is standard-library only.  It constructs one typed byte authority
that RTDL, PyOptix and Direct OptiX adapters can consume without first building
large nested Python row collections.
"""

from __future__ import annotations

import hashlib
import struct
import sys
from array import array
from dataclasses import dataclass

RELATION_TASK = "CUSTOM_AABB_CLOSED_RELATION_COUNT_V1"
TRIANGLE_TASK = "BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1"
RELATION_COUNT = 4096
TRIANGLE_COUNT = 16384
RELATION_INPUT_SHA256 = (
    "8606dd3c22d424a7ee2d64b61918f6185d39d8090d1a0a64001de65054d25e0e"
)
RELATION_OUTPUT_SHA256 = (
    "2fb668490480cbb5d4d9bbf5a8d357435eff5fc6bb3532427ac2726cdaa88c77"
)
TRIANGLE_INPUT_SHA256 = (
    "d994f80418995342d0faa4bda84b42c2ef3604b2798de413a2813dd28dc039a7"
)
TRIANGLE_OUTPUT_SHA256 = (
    "2df49102543561c678ce39e05cc6c79ce92c0ea919ad45134d53d19bb67174ef"
)


def _little_endian_bytes(values: array, *, itemsize: int) -> bytes:
    if values.itemsize != itemsize:
        raise RuntimeError(
            f"Goal5848 host array item size {values.itemsize} != {itemsize}"
        )
    if sys.byteorder == "little":
        return values.tobytes()
    copied = array(values.typecode, values)
    copied.byteswap()
    return copied.tobytes()


def _packed_digest(domain: bytes, rows: tuple[bytes, ...]) -> str:
    value = hashlib.sha256(domain)
    for row in rows:
        value.update(struct.pack("<Q", len(row)))
        value.update(row)
    return value.hexdigest()


@dataclass(frozen=True, slots=True)
class PackedRelationWorkload:
    indexed_bounds_f32le: bytes
    indexed_ids_u32le: bytes
    source_bounds_f32le: bytes
    source_ids_u32le: bytes
    indexed_interleaved_4f_u32le: bytes
    source_interleaved_4f_u32le: bytes
    expected_rows: tuple[tuple[int, int], ...]
    count: int
    minimum_overlap_f32: float
    semantic_input_sha256: str
    public_output_sha256: str
    packed_input_sha256: str


@dataclass(frozen=True, slots=True)
class PackedTriangleWorkload:
    vertices_f32le: bytes
    triangles_u32le: bytes
    query_origins_f32le: bytes
    query_directions_f32le: bytes
    query_tmax_f32le: bytes
    query_weights_u64le: bytes
    rays_interleaved_6f_le: bytes
    triangle_count: int
    vertex_count: int
    query_count: int
    tmin_f32: float
    tmax_f32: float
    expected_reduced_u64: int
    semantic_input_sha256: str
    public_output_sha256: str
    packed_input_sha256: str


def relation_workload() -> PackedRelationWorkload:
    bounds = array("f")
    ids = array("I")
    interleaved = bytearray()
    expected = []
    for item_id in range(RELATION_COUNT):
        lower_x = float(2 * item_id)
        row = (lower_x, 0.0, lower_x + 1.0, 1.0)
        bounds.extend(row)
        ids.append(item_id)
        interleaved.extend(struct.pack("<4fI", *row, item_id))
        expected.append((item_id, item_id))
    bounds_bytes = _little_endian_bytes(bounds, itemsize=4)
    ids_bytes = _little_endian_bytes(ids, itemsize=4)
    interleaved_bytes = bytes(interleaved)
    packed = (
        bounds_bytes,
        ids_bytes,
        bounds_bytes,
        ids_bytes,
        interleaved_bytes,
        interleaved_bytes,
    )
    return PackedRelationWorkload(
        indexed_bounds_f32le=bounds_bytes,
        indexed_ids_u32le=ids_bytes,
        source_bounds_f32le=bounds_bytes,
        source_ids_u32le=ids_bytes,
        indexed_interleaved_4f_u32le=interleaved_bytes,
        source_interleaved_4f_u32le=interleaved_bytes,
        expected_rows=tuple(expected),
        count=RELATION_COUNT,
        minimum_overlap_f32=1.0,
        semantic_input_sha256=RELATION_INPUT_SHA256,
        public_output_sha256=RELATION_OUTPUT_SHA256,
        packed_input_sha256=_packed_digest(
            b"RTDL-GOAL5848-RELATION-PACKED-V1\0", packed
        ),
    )


def triangle_workload() -> PackedTriangleWorkload:
    vertices = array("f")
    triangles = array("I")
    origins = array("f")
    directions = array("f")
    maxima = array("f")
    weights = array("Q")
    rays = bytearray()
    expected_reduced = 0
    for ray_id in range(TRIANGLE_COUNT):
        center_x = float(3 * ray_id)
        vertices.extend((
            center_x - 1.0, -1.0, 1.0,
            center_x + 1.0, -1.0, 1.0,
            center_x, 1.0, 1.0,
        ))
        first_vertex = 3 * ray_id
        triangles.extend((first_vertex, first_vertex + 1, first_vertex + 2))
        origin = (center_x, 0.0, 0.0)
        direction = (0.0, 0.0, 1.0)
        origins.extend(origin)
        directions.extend(direction)
        maxima.append(2.0)
        weight = 1 + ray_id % 7
        weights.append(weight)
        expected_reduced += weight
        rays.extend(struct.pack("<6f", *origin, *direction))
    packed = (
        _little_endian_bytes(vertices, itemsize=4),
        _little_endian_bytes(triangles, itemsize=4),
        _little_endian_bytes(origins, itemsize=4),
        _little_endian_bytes(directions, itemsize=4),
        _little_endian_bytes(maxima, itemsize=4),
        _little_endian_bytes(weights, itemsize=8),
        bytes(rays),
    )
    return PackedTriangleWorkload(
        vertices_f32le=packed[0],
        triangles_u32le=packed[1],
        query_origins_f32le=packed[2],
        query_directions_f32le=packed[3],
        query_tmax_f32le=packed[4],
        query_weights_u64le=packed[5],
        rays_interleaved_6f_le=packed[6],
        triangle_count=TRIANGLE_COUNT,
        vertex_count=3 * TRIANGLE_COUNT,
        query_count=TRIANGLE_COUNT,
        tmin_f32=0.0,
        tmax_f32=2.0,
        expected_reduced_u64=expected_reduced,
        semantic_input_sha256=TRIANGLE_INPUT_SHA256,
        public_output_sha256=TRIANGLE_OUTPUT_SHA256,
        packed_input_sha256=_packed_digest(
            b"RTDL-GOAL5848-TRIANGLE-PACKED-V1\0", packed
        ),
    )


__all__ = [
    "RELATION_COUNT",
    "RELATION_INPUT_SHA256",
    "RELATION_OUTPUT_SHA256",
    "RELATION_TASK",
    "TRIANGLE_COUNT",
    "TRIANGLE_INPUT_SHA256",
    "TRIANGLE_OUTPUT_SHA256",
    "TRIANGLE_TASK",
    "PackedRelationWorkload",
    "PackedTriangleWorkload",
    "relation_workload",
    "triangle_workload",
]
