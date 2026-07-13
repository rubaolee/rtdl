#!/usr/bin/env python3
"""Parameterized Section 5.7 representative overlay via public RTDL primitives.

This is intentionally a user/application script:

- It does not import ``rtdsl.rayjoin_overlay``.
- RTDL supplies public planar-map LSI and point-location primitives.
- The output-chain assembly below is application logic following the RayJoin
  paper output contract.

Inputs are supplied by command line. Regenerated/current-source pairs must be
reported as representative data, not exact old hidden paper input.
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.util
import hashlib
import json
import math
import os
import sys
import time
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import numpy as np

from rtdsl import prepare_planar_map_lsi_2d_optix
from rtdsl import prepare_planar_map_point_location_2d_optix
from rtdsl import load_planar_map_cdb_packed_inputs
from rtdsl.embree_runtime import PackedRayjoinCdbSegments
from rtdsl.embree_runtime import _RtdlRayjoinCdbSegment
from rtdsl.embree_runtime import pack_rayjoin_cdb_scaled_points
from rtdsl.optix_runtime import pack_points
from rtdsl.optix_runtime import pack_segments


EXTERIOR_FACE_ID = 0
_FMA = None
_FMA_LOOKED_UP = False


@dataclass
class DatasetArrays:
    path: str
    name: str
    chain_count: int
    point_count: int
    edge_count: int
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    chain_offsets: np.ndarray
    chain_point_counts: np.ndarray
    chain_left_faces: np.ndarray
    chain_right_faces: np.ndarray
    point_x: np.ndarray
    point_y: np.ndarray
    seg_ids: np.ndarray
    x0: np.ndarray
    y0: np.ndarray
    x1: np.ndarray
    y1: np.ndarray
    left_face_ids: np.ndarray
    right_face_ids: np.ndarray
    lsi_segments: object
    cdb_segments: object
    points: object


@dataclass
class OverlayIntersection:
    eid0: int
    eid1: int
    x: float
    y: float
    display_x: float | None = None
    display_y: float | None = None
    scaled_x: float | None = None
    scaled_y: float | None = None
    scaled_x_rational: Fraction | None = None
    scaled_y_rational: Fraction | None = None
    mid_point_polygon_id_map0: int = EXTERIOR_FACE_ID
    mid_point_polygon_id_map1: int = EXTERIOR_FACE_ID


@dataclass
class OutputChain:
    points: list[tuple[float, float]]
    left_polygon_id: int
    right_polygon_id: int
    display_points: list[tuple[float, float]] | None = None
    debug_context: str = ""
    other_map_polygon_id: int = EXTERIOR_FACE_ID
    first_point_idx: int = 0
    last_point_idx: int = 0


def _log(message: str) -> None:
    print(f"[goal4880-public-route] {message}", file=sys.stderr, flush=True)


def _timed(label: str, func):
    _log(f"start {label}")
    start = time.perf_counter()
    value = func()
    elapsed = time.perf_counter() - start
    _log(f"done {label}: {elapsed:.6f}s")
    return value, elapsed


def _scan_cdb_values(path: Path):
    values = np.fromfile(path, dtype=np.float64, sep=" ")
    if values.size == 0:
        raise ValueError(f"empty CDB file: {path}")
    index = 0
    chain_count = 0
    point_count = 0
    edge_count = 0
    min_x = float("inf")
    max_x = float("-inf")
    min_y = float("inf")
    max_y = float("-inf")
    while index < values.size:
        if index + 6 > values.size:
            raise ValueError(f"truncated CDB header in {path} at scalar index {index}")
        npoints = int(values[index + 1])
        coord_start = index + 6
        coord_end = coord_start + 2 * npoints
        if coord_end > values.size:
            raise ValueError(f"truncated CDB point payload in {path} at chain {chain_count}")
        coords = values[coord_start:coord_end].reshape((npoints, 2))
        chain_count += 1
        point_count += npoints
        edge_count += max(0, npoints - 1)
        xs = coords[:, 0]
        ys = coords[:, 1]
        min_x = min(min_x, float(np.min(xs)))
        max_x = max(max_x, float(np.max(xs)))
        min_y = min(min_y, float(np.min(ys)))
        max_y = max(max_y, float(np.max(ys)))
        index = coord_end
    if index != values.size:
        raise ValueError(f"CDB parse ended at {index}, expected {values.size}")
    return values, chain_count, point_count, edge_count, min_x, max_x, min_y, max_y


def load_dataset_arrays(path: Path) -> DatasetArrays:
    return load_planar_map_cdb_packed_inputs(path)


def _legacy_load_dataset_arrays(path: Path) -> DatasetArrays:
    values, chain_count, point_count, edge_count, min_x, max_x, min_y, max_y = _scan_cdb_values(path)
    chain_offsets = np.empty(chain_count, dtype=np.int64)
    chain_point_counts = np.empty(chain_count, dtype=np.int64)
    chain_left_faces = np.empty(chain_count, dtype=np.uint32)
    chain_right_faces = np.empty(chain_count, dtype=np.uint32)
    point_x = np.empty(point_count, dtype=np.float64)
    point_y = np.empty(point_count, dtype=np.float64)
    x0 = np.empty(edge_count, dtype=np.float64)
    y0 = np.empty(edge_count, dtype=np.float64)
    x1 = np.empty(edge_count, dtype=np.float64)
    y1 = np.empty(edge_count, dtype=np.float64)
    left_face_ids = np.empty(edge_count, dtype=np.uint32)
    right_face_ids = np.empty(edge_count, dtype=np.uint32)

    scalar_index = 0
    chain_index = 0
    point_index = 0
    edge_index = 0
    while scalar_index < values.size:
        npoints = int(values[scalar_index + 1])
        left_face = int(values[scalar_index + 4])
        right_face = int(values[scalar_index + 5])
        coord_start = scalar_index + 6
        coord_end = coord_start + 2 * npoints
        coords = values[coord_start:coord_end].reshape((npoints, 2))
        chain_offsets[chain_index] = point_index
        chain_point_counts[chain_index] = npoints
        chain_left_faces[chain_index] = np.uint32(left_face)
        chain_right_faces[chain_index] = np.uint32(right_face)
        point_x[point_index:point_index + npoints] = coords[:, 0]
        point_y[point_index:point_index + npoints] = coords[:, 1]
        if npoints > 1:
            span = npoints - 1
            x0[edge_index:edge_index + span] = coords[:-1, 0]
            y0[edge_index:edge_index + span] = coords[:-1, 1]
            x1[edge_index:edge_index + span] = coords[1:, 0]
            y1[edge_index:edge_index + span] = coords[1:, 1]
            left_face_ids[edge_index:edge_index + span] = np.uint32(left_face)
            right_face_ids[edge_index:edge_index + span] = np.uint32(right_face)
            edge_index += span
        point_index += npoints
        chain_index += 1
        scalar_index = coord_end

    seg_ids = np.arange(1, edge_count + 1, dtype=np.int64)
    point_ids = np.arange(1, point_count + 1, dtype=np.int64)
    lsi_segments = pack_segments(ids=seg_ids, x0=x0, y0=y0, x1=x1, y1=y1)
    cdb_segments = pack_cdb_segments_from_arrays(seg_ids, x0, y0, x1, y1, left_face_ids, right_face_ids)
    points = pack_points(ids=point_ids, x=point_x, y=point_y, dimension=2)
    return DatasetArrays(
        path=str(path),
        name=path.stem,
        chain_count=chain_count,
        point_count=point_count,
        edge_count=edge_count,
        min_x=min_x,
        max_x=max_x,
        min_y=min_y,
        max_y=max_y,
        chain_offsets=chain_offsets,
        chain_point_counts=chain_point_counts,
        chain_left_faces=chain_left_faces,
        chain_right_faces=chain_right_faces,
        point_x=point_x,
        point_y=point_y,
        seg_ids=seg_ids,
        x0=x0,
        y0=y0,
        x1=x1,
        y1=y1,
        left_face_ids=left_face_ids,
        right_face_ids=right_face_ids,
        lsi_segments=lsi_segments,
        cdb_segments=cdb_segments,
        points=points,
    )


def pack_cdb_segments_from_arrays(seg_ids, x0, y0, x1, y1, left_face_ids, right_face_ids):
    """Pack directed planar-map face segments without a Python per-edge loop."""

    dtype = np.dtype(
        [
            ("id", np.uint32),
            ("x0", np.float64),
            ("y0", np.float64),
            ("x1", np.float64),
            ("y1", np.float64),
            ("left_face_id", np.uint32),
            ("right_face_id", np.uint32),
        ],
        align=True,
    )
    if dtype.itemsize != ctypes.sizeof(_RtdlRayjoinCdbSegment):
        raise RuntimeError("CDB segment structured dtype does not match native ABI layout")
    owner = np.empty(int(seg_ids.size), dtype=dtype)
    owner["id"] = np.asarray(seg_ids, dtype=np.uint32)
    owner["x0"] = np.asarray(x0, dtype=np.float64)
    owner["y0"] = np.asarray(y0, dtype=np.float64)
    owner["x1"] = np.asarray(x1, dtype=np.float64)
    owner["y1"] = np.asarray(y1, dtype=np.float64)
    owner["left_face_id"] = np.asarray(left_face_ids, dtype=np.uint32)
    owner["right_face_id"] = np.asarray(right_face_ids, dtype=np.uint32)
    records = (_RtdlRayjoinCdbSegment * int(seg_ids.size)).from_buffer(owner)
    return PackedRayjoinCdbSegments(records=records, count=int(seg_ids.size), owner=owner)


def shared_bounds(left: DatasetArrays, right: DatasetArrays) -> tuple[float, float, float, float]:
    return (
        min(left.min_x, right.min_x),
        max(left.max_x, right.max_x),
        min(left.min_y, right.min_y),
        max(left.max_y, right.max_y),
    )


def _rayjoin_scaling_constants(scale_bounds: tuple[float, float, float, float]):
    box_min_x, box_max_x, box_min_y, box_max_y = (float(value) for value in scale_bounds)
    internal_max = (1 << 46) - 1
    internal_min = -(1 << 46)
    margin = 1.0
    box_max_x += margin
    box_min_x -= margin
    box_max_y += margin
    box_min_y -= margin
    internal_range = float(internal_max - internal_min)
    rx_scale = internal_range / (box_max_x - box_min_x)
    ry_scale = internal_range / (box_max_y - box_min_y)
    rrx = 1.0 / rx_scale
    rry = 1.0 / ry_scale
    deltax = 0.5 * (float(internal_max + internal_min) - (box_max_x + box_min_x) * rx_scale)
    deltay = 0.5 * (float(internal_max + internal_min) - (box_max_y + box_min_y) * ry_scale)
    ddeltax = 0.5 * ((box_max_x + box_min_x) - float(internal_max + internal_min) * rrx)
    ddeltay = 0.5 * ((box_max_y + box_min_y) - float(internal_max + internal_min) * rry)
    return rx_scale, ry_scale, deltax, deltay, rrx, rry, ddeltax, ddeltay


def _scale_array(values, scale: float, delta: float):
    array = np.asarray(values, dtype=np.float64)
    fma = _rayjoin_fma()
    if fma is None:
        return (array * scale + delta).astype(np.int64)
    output = np.empty(array.shape, dtype=np.int64)
    flat_in = array.ravel()
    flat_out = output.ravel()
    for index, value in enumerate(flat_in):
        flat_out[index] = int(fma(float(value), float(scale), float(delta)))
    return output


def _rayjoin_fma():
    global _FMA, _FMA_LOOKED_UP
    if _FMA_LOOKED_UP:
        return _FMA
    _FMA_LOOKED_UP = True
    if hasattr(math, "fma"):
        _FMA = math.fma
        return _FMA
    candidates = []
    libm = ctypes.util.find_library("m")
    if libm:
        candidates.append(libm)
    candidates.extend(("libm.so.6", "libm.so", None))
    for candidate in candidates:
        try:
            library = ctypes.CDLL(candidate) if candidate is not None else ctypes.CDLL(None)
            fma = library.fma
        except (AttributeError, OSError):
            continue
        fma.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]
        fma.restype = ctypes.c_double

        def call_fma(a, b, c, _fma=fma):
            return float(_fma(float(a), float(b), float(c)))

        _FMA = call_fma
        return _FMA
    _FMA = None
    return None


def _author_rational_to_internal(value: Fraction) -> int:
    if value.denominator == 1:
        return int(value.numerator)
    return int(float(int(value.numerator)) / float(int(value.denominator)))


def _unscale_rational(value: Fraction, reciprocal_scale: float, delta: float) -> float:
    if value.denominator == 1:
        scaled = float(int(value.numerator))
    else:
        scaled = float(int(value.numerator)) / float(int(value.denominator))
    return scaled * reciprocal_scale + delta


def _display_coordinate(value: float) -> float:
    return float(value)


def _trunc_div2(value: int) -> int:
    if value >= 0:
        return value // 2
    return -((-value) // 2)


def _overlap_midpoint_fallback(lx0, ly0, lx1, ly1, rx0, ry0, rx1, ry1):
    out_x = np.empty(lx0.shape, dtype=np.float64)
    out_y = np.empty(ly0.shape, dtype=np.float64)
    for index in range(int(lx0.shape[0])):
        ldx = float(lx1[index] - lx0[index])
        ldy = float(ly1[index] - ly0[index])
        if abs(ldx) >= abs(ldy) and ldx != 0.0:
            lo = max(min(float(lx0[index]), float(lx1[index])), min(float(rx0[index]), float(rx1[index])))
            hi = min(max(float(lx0[index]), float(lx1[index])), max(float(rx0[index]), float(rx1[index])))
            x = 0.5 * (lo + hi) if lo <= hi else 0.25 * (
                float(lx0[index]) + float(lx1[index]) + float(rx0[index]) + float(rx1[index])
            )
            y = float(ly0[index]) + ((x - float(lx0[index])) / ldx) * ldy
        elif ldy != 0.0:
            lo = max(min(float(ly0[index]), float(ly1[index])), min(float(ry0[index]), float(ry1[index])))
            hi = min(max(float(ly0[index]), float(ly1[index])), max(float(ry0[index]), float(ry1[index])))
            y = 0.5 * (lo + hi) if lo <= hi else 0.25 * (
                float(ly0[index]) + float(ly1[index]) + float(ry0[index]) + float(ry1[index])
            )
            x = float(lx0[index]) + ((y - float(ly0[index])) / ldy) * ldx
        else:
            x = float(lx0[index])
            y = float(ly0[index])
        out_x[index] = x
        out_y[index] = y
    return out_x, out_y


def intersection_rows_from_pairs(
    pairs: np.ndarray,
    left: DatasetArrays,
    right: DatasetArrays,
    *,
    scale_bounds: tuple[float, float, float, float],
):
    pairs = np.asarray(pairs, dtype=np.uint32).reshape((-1, 2))
    left_index = pairs[:, 0].astype(np.int64, copy=False) - 1
    right_index = pairs[:, 1].astype(np.int64, copy=False) - 1
    lx0 = left.x0[left_index]
    ly0 = left.y0[left_index]
    lx1 = left.x1[left_index]
    ly1 = left.y1[left_index]
    rx0 = right.x0[right_index]
    ry0 = right.y0[right_index]
    rx1 = right.x1[right_index]
    ry1 = right.y1[right_index]

    rx_scale, ry_scale, deltax, deltay, rrx, rry, ddeltax, ddeltay = _rayjoin_scaling_constants(scale_bounds)
    slx0 = _scale_array(lx0, rx_scale, deltax)
    sly0 = _scale_array(ly0, ry_scale, deltay)
    slx1 = _scale_array(lx1, rx_scale, deltax)
    sly1 = _scale_array(ly1, ry_scale, deltay)
    srx0 = _scale_array(rx0, rx_scale, deltax)
    sry0 = _scale_array(ry0, ry_scale, deltay)
    srx1 = _scale_array(rx1, rx_scale, deltax)
    sry1 = _scale_array(ry1, ry_scale, deltay)
    fallback_x, fallback_y = _overlap_midpoint_fallback(lx0, ly0, lx1, ly1, rx0, ry0, rx1, ry1)
    fallback_sx = _scale_array(fallback_x, rx_scale, deltax)
    fallback_sy = _scale_array(fallback_y, ry_scale, deltay)

    rows: list[OverlayIntersection] = []
    for index in range(int(pairs.shape[0])):
        left_a = int(sly0[index]) - int(sly1[index])
        left_b = int(slx1[index]) - int(slx0[index])
        left_c = -int(slx0[index]) * left_a - int(sly0[index]) * left_b
        if left_b < 0:
            left_a = -left_a
            left_b = -left_b
            left_c = -left_c
        right_a = int(sry0[index]) - int(sry1[index])
        right_b = int(srx1[index]) - int(srx0[index])
        right_c = -int(srx0[index]) * right_a - int(sry0[index]) * right_b
        if right_b < 0:
            right_a = -right_a
            right_b = -right_b
            right_c = -right_c
        denom = left_a * right_b - right_a * left_b
        if denom == 0:
            sx = int(fallback_sx[index])
            sy = int(fallback_sy[index])
            rx_rat = Fraction(sx, 1)
            ry_rat = Fraction(sy, 1)
            world_x = sx * rrx + ddeltax
            world_y = sy * rry + ddeltay
        else:
            rx_rat = Fraction(right_c * left_b - left_c * right_b, denom)
            ry_rat = Fraction(right_a * left_c - left_a * right_c, denom)
            min_sx = min(int(srx0[index]), int(srx1[index]), int(slx0[index]), int(slx1[index]))
            max_sx = max(int(srx0[index]), int(srx1[index]), int(slx0[index]), int(slx1[index]))
            min_sy = min(int(sry0[index]), int(sry1[index]), int(sly0[index]), int(sly1[index]))
            max_sy = max(int(sry0[index]), int(sry1[index]), int(sly0[index]), int(sly1[index]))
            if rx_rat < min_sx:
                rx_rat = Fraction(min_sx, 1)
            elif rx_rat > max_sx:
                rx_rat = Fraction(max_sx, 1)
            if ry_rat < min_sy:
                ry_rat = Fraction(min_sy, 1)
            elif ry_rat > max_sy:
                ry_rat = Fraction(max_sy, 1)
            sx = _author_rational_to_internal(rx_rat)
            sy = _author_rational_to_internal(ry_rat)
            world_x = _unscale_rational(rx_rat, rrx, ddeltax)
            world_y = _unscale_rational(ry_rat, rry, ddeltay)
        rows.append(
            OverlayIntersection(
                eid0=int(pairs[index, 0]) - 1,
                eid1=int(pairs[index, 1]) - 1,
                x=float(world_x),
                y=float(world_y),
                display_x=_display_coordinate(sx * rrx + ddeltax),
                display_y=_display_coordinate(sy * rry + ddeltay),
                scaled_x=float(sx),
                scaled_y=float(sy),
                scaled_x_rational=rx_rat,
                scaled_y_rational=ry_rat,
            )
        )
    return rows


def sort_xsects_for_map(
    xsects: list[OverlayIntersection],
    dataset: DatasetArrays,
    map_index: int,
    scale_bounds: tuple[float, float, float, float],
) -> list[OverlayIntersection]:
    edge_attr = "eid0" if map_index == 0 else "eid1"
    tie_attr = "eid1" if map_index == 0 else "eid0"
    grouped: dict[int, list[OverlayIntersection]] = {}
    for xsect in xsects:
        grouped.setdefault(int(getattr(xsect, edge_attr)), []).append(xsect)
    rx_scale, ry_scale, deltax, deltay, *_ = _rayjoin_scaling_constants(scale_bounds)
    sorted_rows: list[OverlayIntersection] = []
    for eid in sorted(grouped):
        start_sx = int(_scale_array([dataset.x0[eid]], rx_scale, deltax)[0])
        start_sy = int(_scale_array([dataset.y0[eid]], ry_scale, deltay)[0])

        def key(x):
            dx = x.scaled_x_rational - start_sx
            dy = x.scaled_y_rational - start_sy
            return (dx * dx + dy * dy, int(getattr(x, tie_attr)))

        group = grouped[eid]
        group.sort(key=key)
        sorted_rows.extend(group)
    return sorted_rows


def midpoint_points(
    xsects: list[OverlayIntersection],
    map_index: int,
    *,
    scale_bounds: tuple[float, float, float, float],
):
    edge_attr = "eid0" if map_index == 0 else "eid1"
    *_, rrx, rry, ddeltax, ddeltay = _rayjoin_scaling_constants(scale_bounds)
    midpoints: list[tuple[float, float]] = []
    scaled_midpoints: list[tuple[int, int]] = []
    owners: list[OverlayIntersection] = []
    index = 0
    while index < len(xsects):
        edge_id = int(getattr(xsects[index], edge_attr))
        end = index + 1
        while end < len(xsects) and int(getattr(xsects[end], edge_attr)) == edge_id:
            end += 1
        group = xsects[index:end]
        for left, right in zip(group, group[1:]):
            sx = _trunc_div2(int(left.scaled_x) + int(right.scaled_x))
            sy = _trunc_div2(int(left.scaled_y) + int(right.scaled_y))
            midpoint = (sx * rrx + ddeltax, sy * rry + ddeltay)
            if math.isfinite(midpoint[0]) and math.isfinite(midpoint[1]):
                midpoints.append(midpoint)
                scaled_midpoints.append((sx, sy))
                owners.append(left)
        index = end
    return midpoints, scaled_midpoints, owners


def faces_from_rows(rows, point_count: int) -> np.ndarray:
    columns = rows.to_numpy_columns(copy=True)
    faces = np.zeros(point_count, dtype=np.uint32)
    if point_count:
        point_ids = columns["point_id"].astype(np.int64, copy=False)
        faces[point_ids - 1] = columns["face_id"].astype(np.uint32, copy=False)
    return faces


def run_point_location(locator, points, point_count: int):
    rows = locator.run_raw(points)
    try:
        return faces_from_rows(rows, point_count)
    finally:
        rows.close()


def assign_midpoint_faces(
    owners: list[OverlayIntersection],
    faces: np.ndarray,
    map_index: int,
) -> int:
    positive = 0
    for index, owner in enumerate(owners):
        face = int(faces[index])
        if map_index == 0:
            owner.mid_point_polygon_id_map0 = face
        else:
            owner.mid_point_polygon_id_map1 = face
        if face != EXTERIOR_FACE_ID:
            positive += 1
    return positive


def midpoint_face_for_map(xsect: OverlayIntersection, map_index: int) -> int:
    if map_index == 0:
        return int(xsect.mid_point_polygon_id_map0)
    return int(xsect.mid_point_polygon_id_map1)


def xsect_output_point(xsect: OverlayIntersection) -> tuple[float, float]:
    return (
        float(xsect.display_x if xsect.display_x is not None else xsect.x),
        float(xsect.display_y if xsect.display_y is not None else xsect.y),
    )


def dedupe_point_pairs(points, display_points):
    if not points:
        return points, display_points
    out_points = [points[0]]
    out_display = [display_points[0]]
    for point, display in zip(points[1:], display_points[1:]):
        if point != out_points[-1]:
            out_points.append(point)
            out_display.append(display)
    return out_points, out_display


def write_output_chains_streaming(
    datasets: tuple[DatasetArrays, DatasetArrays],
    xsects_sorted: tuple[list[OverlayIntersection], list[OverlayIntersection]],
    point_faces: tuple[np.ndarray, np.ndarray],
    output_path: Path,
):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    face_ids: dict[tuple[int, int], int] = {}
    point_ids: dict[tuple[float, float], int] = {}
    point_counter = 0
    chain_count = 0
    line_count = 0
    streamed_point_count = 0
    dump_center_env = os.environ.get("RTDL_DUMP_OUTPUT_CHAIN_INDEX")
    dump_radius_env = os.environ.get("RTDL_DUMP_OUTPUT_CHAIN_RADIUS")
    dump_center = int(dump_center_env) if dump_center_env is not None else None
    dump_radius = int(dump_radius_env) if dump_radius_env is not None else 2

    def create_polygon(polygon_id1: int, polygon_id2: int) -> int:
        if polygon_id1 == 0 or polygon_id2 == 0:
            return 0
        key = (polygon_id1, polygon_id2)
        if key not in face_ids:
            face_ids[key] = len(face_ids) + 1
        return face_ids[key]

    def flush(output_chain: OutputChain, handle):
        nonlocal point_counter, chain_count, line_count, streamed_point_count
        if not output_chain.points:
            return
        if output_chain.display_points is None:
            output_chain.display_points = list(output_chain.points)
        keep = (
            output_chain.left_polygon_id * output_chain.other_map_polygon_id != 0
            or output_chain.right_polygon_id * output_chain.other_map_polygon_id != 0
        )
        if keep:
            points, display_points = dedupe_point_pairs(output_chain.points, output_chain.display_points)
            raw_chain_index = chain_count
            if dump_center is not None and abs(raw_chain_index - dump_center) <= dump_radius:
                print(
                    "RTDL_DUMP raw_index="
                    f"{raw_chain_index} output_chain_no={raw_chain_index + 1} "
                    f"point_count={len(points)} left={int(output_chain.left_polygon_id)} "
                    f"right={int(output_chain.right_polygon_id)} "
                    f"other={int(output_chain.other_map_polygon_id)} "
                    f"context={output_chain.debug_context}",
                    file=sys.stderr,
                    flush=True,
                )
                for point_index, point in enumerate(display_points):
                    print(
                        "RTDL_DUMP point raw_index="
                        f"{raw_chain_index} point_index={point_index} "
                        f"x={point[0]} y={point[1]}",
                        file=sys.stderr,
                        flush=True,
                    )
            other = int(output_chain.other_map_polygon_id)
            left_polygon_id = create_polygon(*sorted((int(output_chain.left_polygon_id), other)))
            right_polygon_id = create_polygon(*sorted((int(output_chain.right_polygon_id), other)))
            for point in points:
                if point not in point_ids:
                    point_ids[point] = point_counter
                    point_counter += 1
            first_point_idx = point_ids[points[0]]
            last_point_idx = point_ids[points[-1]]
            chain_count += 1
            handle.write(
                f"{chain_count} {len(points)} {first_point_idx} {last_point_idx} "
                f"{left_polygon_id} {right_polygon_id}\n"
            )
            line_count += 1
            for x, y in display_points:
                handle.write(f"{x:.6f} {y:.6f}\n")
                line_count += 1
                streamed_point_count += 1
        output_chain.points.clear()
        if output_chain.display_points is not None:
            output_chain.display_points.clear()

    with output_path.open("w", encoding="utf-8") as handle:
        for map_index, dataset in enumerate(datasets):
            edge_attr = "eid0" if map_index == 0 else "eid1"
            grouped: dict[int, list[OverlayIntersection]] = {}
            for xsect in xsects_sorted[map_index]:
                grouped.setdefault(int(getattr(xsect, edge_attr)), []).append(xsect)
            edge_id = 0
            for chain_index in range(dataset.chain_count):
                point_offset = int(dataset.chain_offsets[chain_index])
                point_count = int(dataset.chain_point_counts[chain_index])
                output_chain = OutputChain(
                    points=[],
                    display_points=[],
                    left_polygon_id=int(dataset.chain_left_faces[chain_index]),
                    right_polygon_id=int(dataset.chain_right_faces[chain_index]),
                )
                for local_point_index in range(point_count):
                    point_index = point_offset + local_point_index
                    output_chain.other_map_polygon_id = int(point_faces[map_index][point_index])
                    output_chain.points.append((float(dataset.point_x[point_index]), float(dataset.point_y[point_index])))
                    output_chain.display_points.append((float(dataset.point_x[point_index]), float(dataset.point_y[point_index])))
                    if local_point_index == point_count - 1:
                        continue
                    xsects = grouped.get(edge_id)
                    if xsects:
                        first_point = xsect_output_point(xsects[0])
                        output_chain.points.append(first_point)
                        output_chain.display_points.append(first_point)
                        for xsect, next_xsect in zip(xsects, xsects[1:]):
                            output_chain.debug_context = (
                                f"map={map_index} chain={chain_index} edge={edge_id} "
                                f"before_mid_segment xsect=({xsect.eid0},{xsect.eid1}) "
                                f"next=({next_xsect.eid0},{next_xsect.eid1})"
                            )
                            flush(output_chain, handle)
                            output_chain.other_map_polygon_id = midpoint_face_for_map(xsect, map_index)
                            output_chain.debug_context = (
                                f"map={map_index} chain={chain_index} edge={edge_id} "
                                f"mid_segment xsect=({xsect.eid0},{xsect.eid1}) "
                                f"next=({next_xsect.eid0},{next_xsect.eid1}) "
                                f"mid_face={output_chain.other_map_polygon_id}"
                            )
                            xsect_point = xsect_output_point(xsect)
                            next_xsect_point = xsect_output_point(next_xsect)
                            output_chain.points.append(xsect_point)
                            output_chain.display_points.append(xsect_point)
                            output_chain.points.append(next_xsect_point)
                            output_chain.display_points.append(next_xsect_point)
                        flush(output_chain, handle)
                        last_point = xsect_output_point(xsects[-1])
                        output_chain.debug_context = (
                            f"map={map_index} chain={chain_index} edge={edge_id} "
                            f"after_last_xsect xsect=({xsects[-1].eid0},{xsects[-1].eid1})"
                        )
                        output_chain.points.append(last_point)
                        output_chain.display_points.append(last_point)
                    edge_id += 1
                flush(output_chain, handle)
    return {
        "path": str(output_path),
        "chain_count": chain_count,
        "face_count": len(face_ids),
        "line_count": line_count,
        "point_count": streamed_point_count,
    }


def file_summary(path: Path) -> dict[str, object]:
    h = hashlib.sha256()
    lines = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
            lines += chunk.count(b"\n")
    return {"path": str(path), "bytes": path.stat().st_size, "lines": lines, "sha256": h.hexdigest()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    parser.add_argument("--author-output", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--pair-name", default="unnamed_pair")
    parser.add_argument(
        "--dataset-label",
        default="representative_current_source",
        choices=("representative_current_source", "available_bounded_pair", "exact_old_paper_input"),
    )
    parser.add_argument(
        "--cache-dir",
        default=None,
        help="Optional packed CDB cache directory for load_planar_map_cdb_packed_inputs.",
    )
    parser.add_argument("--swap-query-map-ids", action="store_true")
    args = parser.parse_args()

    if "rtdsl.rayjoin_overlay" in sys.modules:
        raise RuntimeError("forbidden import detected: rtdsl.rayjoin_overlay")

    old_cache_dir = os.environ.get("RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR")
    if args.cache_dir:
        os.environ["RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR"] = str(Path(args.cache_dir))

    total_start = time.perf_counter()
    phase_seconds: dict[str, float] = {}
    try:
        left, phase_seconds["load_pack_left_sec"] = _timed("load/pack left", lambda: load_dataset_arrays(Path(args.left)))
        right, phase_seconds["load_pack_right_sec"] = _timed("load/pack right", lambda: load_dataset_arrays(Path(args.right)))
    finally:
        if args.cache_dir:
            if old_cache_dir is None:
                os.environ.pop("RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR", None)
            else:
                os.environ["RTDL_PLANAR_MAP_CDB_PACKED_CACHE_DIR"] = old_cache_dir
    bounds, phase_seconds["shared_bounds_sec"] = _timed("shared bounds", lambda: shared_bounds(left, right))

    def run_lsi():
        with prepare_planar_map_lsi_2d_optix(right.lsi_segments) as lsi:
            with lsi.prepare_query(left.lsi_segments) as query:
                row_view = query.run_pair_id_rows()
                try:
                    columns = row_view.to_numpy_columns(copy=True)
                    pairs = np.column_stack(
                        (
                            columns["left_id"].astype(np.uint32, copy=False),
                            columns["right_id"].astype(np.uint32, copy=False),
                        )
                    )
                finally:
                    row_view.close()
        return pairs

    pairs, phase_seconds["lsi_public_rows_sec"] = _timed("public planar-map LSI rows", run_lsi)
    xsects, phase_seconds["intersection_reprojection_sec"] = _timed(
        "intersection reprojection",
        lambda: intersection_rows_from_pairs(pairs, left, right, scale_bounds=bounds),
    )
    xsects0, phase_seconds["sort_map0_sec"] = _timed(
        "sort xsects map0",
        lambda: sort_xsects_for_map(list(xsects), left, 0, bounds),
    )
    xsects1, phase_seconds["sort_map1_sec"] = _timed(
        "sort xsects map1",
        lambda: sort_xsects_for_map(list(xsects), right, 1, bounds),
    )

    point_timings = {}
    map0_query_map_id = 1 if args.swap_query_map_ids else 0
    map1_query_map_id = 0 if args.swap_query_map_ids else 1
    map0_in_map1, phase_seconds["prepare_point_location_map0_in_map1_sec"] = _timed(
        "prepare point-location map0 in map1",
        lambda: prepare_planar_map_point_location_2d_optix(
            right.cdb_segments,
            query_map_id=map0_query_map_id,
            scale_bounds=bounds,
        ),
    )
    map1_in_map0, phase_seconds["prepare_point_location_map1_in_map0_sec"] = _timed(
        "prepare point-location map1 in map0",
        lambda: prepare_planar_map_point_location_2d_optix(
            left.cdb_segments,
            query_map_id=map1_query_map_id,
            scale_bounds=bounds,
        ),
    )
    try:
        point_faces0, phase_seconds["vertex_pip_map0_in_map1_sec"] = _timed(
            "vertex PIP map0 in map1",
            lambda: run_point_location(map0_in_map1, left.points, left.point_count),
        )
        point_timings["vertex_pip_map0_in_map1"] = map0_in_map1.last_phase_timings() or {}
        point_faces1, phase_seconds["vertex_pip_map1_in_map0_sec"] = _timed(
            "vertex PIP map1 in map0",
            lambda: run_point_location(map1_in_map0, right.points, right.point_count),
        )
        point_timings["vertex_pip_map1_in_map0"] = map1_in_map0.last_phase_timings() or {}

        for map_index, locator, sorted_rows in (
            (0, map0_in_map1, xsects0),
            (1, map1_in_map0, xsects1),
        ):
            (midpoints, scaled_midpoints, owners), phase_seconds[f"midpoint_points_map{map_index}_sec"] = _timed(
                f"midpoint points map{map_index}",
                lambda sorted_rows=sorted_rows, map_index=map_index: midpoint_points(
                    sorted_rows,
                    map_index,
                    scale_bounds=bounds,
                ),
            )

            def pack_midpoint_points():
                ids = np.arange(1, len(midpoints) + 1, dtype=np.int64)
                mx = np.fromiter((p[0] for p in midpoints), dtype=np.float64, count=len(midpoints))
                my = np.fromiter((p[1] for p in midpoints), dtype=np.float64, count=len(midpoints))
                sx = np.fromiter((p[0] for p in scaled_midpoints), dtype=np.int64, count=len(scaled_midpoints))
                sy = np.fromiter((p[1] for p in scaled_midpoints), dtype=np.int64, count=len(scaled_midpoints))
                return pack_rayjoin_cdb_scaled_points(ids=ids, x=mx, y=my, sx=sx, sy=sy)

            scaled_points, phase_seconds[f"pack_midpoint_points_map{map_index}_sec"] = _timed(
                f"pack midpoint points map{map_index}",
                pack_midpoint_points,
            )
            faces, elapsed = _timed(
                f"midpoint PIP map{map_index}",
                lambda locator=locator, scaled_points=scaled_points, count=len(midpoints): run_point_location(
                    locator,
                    scaled_points,
                    count,
                ),
            )
            phase_seconds[f"midpoint_pip_map{map_index}_sec"] = elapsed
            point_timings[f"midpoint_pip_map{map_index}"] = locator.last_phase_timings() or {}
            _, phase_seconds[f"assign_midpoint_faces_map{map_index}_sec"] = _timed(
                f"assign midpoint faces map{map_index}",
                lambda owners=owners, faces=faces, map_index=map_index: assign_midpoint_faces(owners, faces, map_index),
            )
    finally:
        _, phase_seconds["destroy_point_location_sessions_sec"] = _timed(
            "destroy point-location sessions",
            lambda: (map0_in_map1.close(), map1_in_map0.close()),
        )

    output_path = Path(args.output)
    writer_result, phase_seconds["output_chain_write_sec"] = _timed(
        "output-chain streaming write",
        lambda: write_output_chains_streaming((left, right), (xsects0, xsects1), (point_faces0, point_faces1), output_path),
    )

    generated, phase_seconds["file_summary_generated_sec"] = _timed(
        "file summary generated",
        lambda: file_summary(output_path),
    )
    author, phase_seconds["file_summary_author_sec"] = _timed(
        "file summary author",
        lambda: file_summary(Path(args.author_output)),
    )
    summary = {
        "schema": "rtdl.goal4880.section57_public_primitives_overlay_harness.v1",
        "pair_name": args.pair_name,
        "route": "public_planar_map_lsi_and_point_location_plus_python_app_overlay_writer",
        "claim_boundary": {
            "dataset_label": args.dataset_label,
            "exact_old_paper_input_claim": args.dataset_label == "exact_old_paper_input",
            "bundled_rayjoin_overlay_imported": False,
            "public_lsi_used": True,
            "public_point_location_used": True,
            "numba_on_correctness_critical_path": False,
            "full_eight_pair_paper_claim": False,
            "broad_performance_claim": False,
        },
        "left": {"path": left.path, "chains": left.chain_count, "points": left.point_count, "edges": left.edge_count},
        "right": {"path": right.path, "chains": right.chain_count, "points": right.point_count, "edges": right.edge_count},
        "packed_cache": {
            "enabled": bool(args.cache_dir),
            "path": str(Path(args.cache_dir)) if args.cache_dir else None,
        },
        "scale_bounds": bounds,
        "query_map_ids": {
            "map0_in_map1": map0_query_map_id,
            "map1_in_map0": map1_query_map_id,
            "swapped": bool(args.swap_query_map_ids),
        },
        "lsi_row_count": int(pairs.shape[0]),
        "xsect_sorted_counts": {"map0": len(xsects0), "map1": len(xsects1)},
        "vertex_positive_counts": {
            "map0_in_map1": int(np.count_nonzero(point_faces0)),
            "map1_in_map0": int(np.count_nonzero(point_faces1)),
        },
        "writer_result": writer_result,
        "generated_output": generated,
        "author_output": author,
        "byte_equal_to_author": generated["sha256"] == author["sha256"] and generated["bytes"] == author["bytes"],
        "phase_seconds": phase_seconds,
        "native_point_location_timings": point_timings,
        "elapsed_sec": time.perf_counter() - total_start,
    }
    Path(args.summary).write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
