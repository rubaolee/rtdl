from __future__ import annotations

import ctypes
import json
import os
import re
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Iterable

from .datasets import CdbDataset
from .datasets import CdbPoint


EXTERIOR_FACE_ID = 0
PACKED_OVERLAY_CACHE_VERSION = "rtdl_rayjoin_overlay_packed_v1"
POINT_LOCATION_ADAPTIVE_GROUPING_POINT_THRESHOLD = 32_000_000


@dataclass
class RayjoinOverlayIntersection:
    eid0: int
    eid1: int
    x: float
    y: float
    mid_point_polygon_id: int = EXTERIOR_FACE_ID


@dataclass
class RayjoinOverlayOutputChain:
    points: list[tuple[float, float]]
    left_polygon_id: int
    right_polygon_id: int
    other_map_polygon_id: int = EXTERIOR_FACE_ID
    first_point_idx: int = 0
    last_point_idx: int = 0


@dataclass
class RayjoinOverlayPackedInputs:
    name: str
    segments: object
    cdb_segments: object
    points: object
    segment_coords: tuple[object, object, object, object]
    point_coords: tuple[object, object]
    edge_starts: object
    chain_count: int
    edge_count: int
    point_count: int


def _edge_count(dataset: CdbDataset) -> int:
    return sum(max(0, len(chain.points) - 1) for chain in dataset.chains)


def _point_count(dataset: CdbDataset) -> int:
    return sum(len(chain.points) for chain in dataset.chains)


def _rayjoin_cdb_segment_numpy_dtype(np):
    from .embree_runtime import _RtdlRayjoinCdbSegment

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
        raise RuntimeError("NumPy RayJoin CDB segment dtype does not match native ctypes layout")
    return dtype


def _segment_numpy_dtype(np):
    from .embree_runtime import _RtdlSegment

    dtype = np.dtype(
        [
            ("id", np.uint32),
            ("x0", np.float64),
            ("y0", np.float64),
            ("x1", np.float64),
            ("y1", np.float64),
        ],
        align=True,
    )
    if dtype.itemsize != ctypes.sizeof(_RtdlSegment):
        raise RuntimeError("NumPy segment dtype does not match native ctypes layout")
    return dtype


def _point_numpy_dtype(np):
    from .embree_runtime import _RtdlPoint

    dtype = np.dtype(
        [
            ("id", np.uint32),
            ("x", np.float64),
            ("y", np.float64),
        ],
        align=True,
    )
    if dtype.itemsize != ctypes.sizeof(_RtdlPoint):
        raise RuntimeError("NumPy point dtype does not match native ctypes layout")
    return dtype


def _overlay_inputs_from_native_arrays(
    *,
    name: str,
    chain_count: int,
    segment_array,
    cdb_array,
    point_array,
) -> RayjoinOverlayPackedInputs:
    from .embree_runtime import PackedPoints
    from .embree_runtime import PackedRayjoinCdbSegments
    from .embree_runtime import PackedSegments
    from .embree_runtime import _RtdlPoint
    from .embree_runtime import _RtdlRayjoinCdbSegment
    from .embree_runtime import _RtdlSegment

    segment_records = segment_array.ctypes.data_as(ctypes.POINTER(_RtdlSegment))
    cdb_records = cdb_array.ctypes.data_as(ctypes.POINTER(_RtdlRayjoinCdbSegment))
    point_records = point_array.ctypes.data_as(ctypes.POINTER(_RtdlPoint))
    owner = (segment_array, cdb_array, point_array)
    return RayjoinOverlayPackedInputs(
        name=name,
        segments=PackedSegments(records=segment_records, count=int(segment_array.size), owner=owner),
        cdb_segments=PackedRayjoinCdbSegments(records=cdb_records, count=int(cdb_array.size), owner=owner),
        points=PackedPoints(records=point_records, count=int(point_array.size), dimension=2, owner=owner),
        segment_coords=(segment_array["x0"], segment_array["y0"], segment_array["x1"], segment_array["y1"]),
        point_coords=(point_array["x"], point_array["y"]),
        edge_starts=(segment_array["x0"], segment_array["y0"]),
        chain_count=int(chain_count),
        edge_count=int(segment_array.size),
        point_count=int(point_array.size),
    )


def _packed_cache_root() -> Path | None:
    raw = os.environ.get("RTDL_RAYJOIN_OVERLAY_PACKED_CACHE_DIR")
    if raw is None or raw.strip() == "":
        return None
    return Path(raw)


def _packed_cache_path(path: Path) -> Path | None:
    root = _packed_cache_root()
    if root is None:
        return None
    stat = path.stat()
    safe_stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", path.stem)
    return root / f"{safe_stem}_{stat.st_size}_{stat.st_mtime_ns}_{PACKED_OVERLAY_CACHE_VERSION}"


def _try_load_packed_overlay_cache(path: Path) -> RayjoinOverlayPackedInputs | None:
    import numpy as np

    cache_path = _packed_cache_path(path)
    if cache_path is None:
        return None
    meta_path = cache_path / "meta.json"
    if not meta_path.exists():
        return None
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("version") != PACKED_OVERLAY_CACHE_VERSION:
            return None
        stat = path.stat()
        if int(meta.get("source_size", -1)) != stat.st_size:
            return None
        if int(meta.get("source_mtime_ns", -1)) != stat.st_mtime_ns:
            return None
        segment_array = np.load(cache_path / "segments.npy", mmap_mode="r")
        cdb_array = np.load(cache_path / "cdb_segments.npy", mmap_mode="r")
        point_array = np.load(cache_path / "points.npy", mmap_mode="r")
        if segment_array.dtype != _segment_numpy_dtype(np):
            return None
        if cdb_array.dtype != _rayjoin_cdb_segment_numpy_dtype(np):
            return None
        if point_array.dtype != _point_numpy_dtype(np):
            return None
        return _overlay_inputs_from_native_arrays(
            name=str(meta.get("name", path.stem)),
            chain_count=int(meta["chain_count"]),
            segment_array=segment_array,
            cdb_array=cdb_array,
            point_array=point_array,
        )
    except Exception:
        return None


def _write_packed_overlay_cache(path: Path, packed: RayjoinOverlayPackedInputs) -> None:
    import numpy as np

    cache_path = _packed_cache_path(path)
    if cache_path is None:
        return
    cache_path.mkdir(parents=True, exist_ok=True)
    np.save(cache_path / "segments.npy", packed.segments.owner[0])
    np.save(cache_path / "cdb_segments.npy", packed.cdb_segments.owner[1])
    np.save(cache_path / "points.npy", packed.points.owner[2])
    stat = path.stat()
    meta = {
        "version": PACKED_OVERLAY_CACHE_VERSION,
        "name": packed.name,
        "chain_count": int(packed.chain_count),
        "edge_count": int(packed.edge_count),
        "point_count": int(packed.point_count),
        "source": str(path),
        "source_size": int(stat.st_size),
        "source_mtime_ns": int(stat.st_mtime_ns),
    }
    (cache_path / "meta.json").write_text(json.dumps(meta, sort_keys=True) + "\n", encoding="utf-8")


def _overlay_inputs_from_arrays(
    *,
    name: str,
    chain_count: int,
    segment_ids,
    x0,
    y0,
    x1,
    y1,
    left_face_ids,
    right_face_ids,
    point_x,
    point_y,
) -> RayjoinOverlayPackedInputs:
    import numpy as np

    edge_count = int(segment_ids.size)
    point_count = int(point_x.size)
    segment_array = np.empty(edge_count, dtype=_segment_numpy_dtype(np))
    segment_array["id"] = segment_ids.astype(np.uint32, copy=False)
    segment_array["x0"] = x0
    segment_array["y0"] = y0
    segment_array["x1"] = x1
    segment_array["y1"] = y1

    cdb_array = np.empty(edge_count, dtype=_rayjoin_cdb_segment_numpy_dtype(np))
    cdb_array["id"] = segment_ids.astype(np.uint32, copy=False)
    cdb_array["x0"] = x0
    cdb_array["y0"] = y0
    cdb_array["x1"] = x1
    cdb_array["y1"] = y1
    cdb_array["left_face_id"] = left_face_ids
    cdb_array["right_face_id"] = right_face_ids

    point_array = np.empty(point_count, dtype=_point_numpy_dtype(np))
    point_array["id"] = np.arange(1, point_count + 1, dtype=np.uint32)
    point_array["x"] = point_x
    point_array["y"] = point_y

    return _overlay_inputs_from_native_arrays(
        name=name,
        chain_count=chain_count,
        segment_array=segment_array,
        cdb_array=cdb_array,
        point_array=point_array,
    )


def _packed_overlay_inputs(dataset: CdbDataset) -> RayjoinOverlayPackedInputs:
    import numpy as np

    edge_count = _edge_count(dataset)
    point_count = _point_count(dataset)
    segment_ids = np.empty(edge_count, dtype=np.int64)
    x0 = np.empty(edge_count, dtype=np.float64)
    y0 = np.empty(edge_count, dtype=np.float64)
    x1 = np.empty(edge_count, dtype=np.float64)
    y1 = np.empty(edge_count, dtype=np.float64)
    left_face_ids = np.empty(edge_count, dtype=np.uint32)
    right_face_ids = np.empty(edge_count, dtype=np.uint32)
    point_x = np.empty(point_count, dtype=np.float64)
    point_y = np.empty(point_count, dtype=np.float64)

    edge_index = 0
    point_index = 0
    segment_id = 1
    for chain in dataset.chains:
        points = chain.points
        for point in points:
            point_x[point_index] = point.x
            point_y[point_index] = point.y
            point_index += 1
        for start, end in zip(points, points[1:]):
            segment_ids[edge_index] = segment_id
            x0[edge_index] = start.x
            y0[edge_index] = start.y
            x1[edge_index] = end.x
            y1[edge_index] = end.y
            left_face_ids[edge_index] = int(chain.left_face_id)
            right_face_ids[edge_index] = int(chain.right_face_id)
            edge_index += 1
            segment_id += 1

    return _overlay_inputs_from_arrays(
        name=dataset.name,
        chain_count=len(dataset.chains),
        segment_ids=segment_ids,
        x0=x0,
        y0=y0,
        x1=x1,
        y1=y1,
        left_face_ids=left_face_ids,
        right_face_ids=right_face_ids,
        point_x=point_x,
        point_y=point_y,
    )


def load_cdb_overlay_packed_inputs(path: str | Path) -> RayjoinOverlayPackedInputs:
    import numpy as np

    path = Path(path)
    cached = _try_load_packed_overlay_cache(path)
    if cached is not None:
        return cached

    values = np.fromfile(path, dtype=np.float64, sep=" ")
    if values.size == 0:
        packed = _overlay_inputs_from_arrays(
            name=path.stem,
            chain_count=0,
            segment_ids=np.empty(0, dtype=np.int64),
            x0=np.empty(0, dtype=np.float64),
            y0=np.empty(0, dtype=np.float64),
            x1=np.empty(0, dtype=np.float64),
            y1=np.empty(0, dtype=np.float64),
            left_face_ids=np.empty(0, dtype=np.uint32),
            right_face_ids=np.empty(0, dtype=np.uint32),
            point_x=np.empty(0, dtype=np.float64),
            point_y=np.empty(0, dtype=np.float64),
        )
        _write_packed_overlay_cache(path, packed)
        return packed

    if values.size % 10 == 0:
        records = values.reshape((-1, 10))
        if np.all(records[:, 1] == 2):
            chain_count = int(records.shape[0])
            segment_ids = np.arange(1, chain_count + 1, dtype=np.int64)
            x0 = np.ascontiguousarray(records[:, 6], dtype=np.float64)
            y0 = np.ascontiguousarray(records[:, 7], dtype=np.float64)
            x1 = np.ascontiguousarray(records[:, 8], dtype=np.float64)
            y1 = np.ascontiguousarray(records[:, 9], dtype=np.float64)
            point_x = np.empty(chain_count * 2, dtype=np.float64)
            point_y = np.empty(chain_count * 2, dtype=np.float64)
            point_x[0::2] = records[:, 6]
            point_y[0::2] = records[:, 7]
            point_x[1::2] = records[:, 8]
            point_y[1::2] = records[:, 9]
            packed = _overlay_inputs_from_arrays(
                name=path.stem,
                chain_count=chain_count,
                segment_ids=segment_ids,
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
                left_face_ids=records[:, 4].astype(np.uint32, copy=True),
                right_face_ids=records[:, 5].astype(np.uint32, copy=True),
                point_x=point_x,
                point_y=point_y,
            )
            _write_packed_overlay_cache(path, packed)
            return packed

    headers: list[tuple[int, int, int]] = []
    point_counts: list[int] = []
    index = 0
    chain_count = 0
    edge_count = 0
    point_count = 0
    value_count = int(values.size)
    while index < value_count:
        if index + 6 > value_count:
            raise ValueError(f"invalid CDB numeric stream near value {index} in {path}")
        chain_points = int(values[index + 1])
        left_face = int(values[index + 4])
        right_face = int(values[index + 5])
        if chain_points < 0:
            raise ValueError(f"invalid negative CDB point count near value {index} in {path}")
        next_index = index + 6 + chain_points * 2
        if next_index > value_count:
            raise ValueError(f"unexpected EOF in numeric CDB stream near value {index} in {path}")
        point_counts.append(chain_points)
        headers.append((max(0, chain_points - 1), left_face, right_face))
        point_count += chain_points
        edge_count += max(0, chain_points - 1)
        chain_count += 1
        index = next_index
    if index != value_count:
        raise ValueError(f"trailing numeric values in CDB stream for {path}")

    segment_ids = np.arange(1, edge_count + 1, dtype=np.int64)
    x0 = np.empty(edge_count, dtype=np.float64)
    y0 = np.empty(edge_count, dtype=np.float64)
    x1 = np.empty(edge_count, dtype=np.float64)
    y1 = np.empty(edge_count, dtype=np.float64)
    left_face_ids = np.empty(edge_count, dtype=np.uint32)
    right_face_ids = np.empty(edge_count, dtype=np.uint32)
    point_x = np.empty(point_count, dtype=np.float64)
    point_y = np.empty(point_count, dtype=np.float64)

    value_index = 0
    point_offset = 0
    edge_offset = 0
    for chain_points, (chain_edges, left_face, right_face) in zip(point_counts, headers):
        coord_start = value_index + 6
        coord_end = coord_start + chain_points * 2
        coords = values[coord_start:coord_end].reshape((-1, 2))
        point_x[point_offset:point_offset + chain_points] = coords[:, 0]
        point_y[point_offset:point_offset + chain_points] = coords[:, 1]
        if chain_edges:
            edge_end = edge_offset + chain_edges
            x0[edge_offset:edge_end] = coords[:-1, 0]
            y0[edge_offset:edge_end] = coords[:-1, 1]
            x1[edge_offset:edge_end] = coords[1:, 0]
            y1[edge_offset:edge_end] = coords[1:, 1]
            left_face_ids[edge_offset:edge_end] = left_face
            right_face_ids[edge_offset:edge_end] = right_face
            edge_offset = edge_end
        point_offset += chain_points
        value_index = coord_end

    packed = _overlay_inputs_from_arrays(
        name=path.stem,
        chain_count=chain_count,
        segment_ids=segment_ids,
        x0=x0,
        y0=y0,
        x1=x1,
        y1=y1,
        left_face_ids=left_face_ids,
        right_face_ids=right_face_ids,
        point_x=point_x,
        point_y=point_y,
    )
    _write_packed_overlay_cache(path, packed)
    return packed


def _packed_cdb_segments(dataset: CdbDataset):
    from .embree_runtime import PackedRayjoinCdbSegments
    from .embree_runtime import _RtdlRayjoinCdbSegment

    count = _edge_count(dataset)
    rows = (_RtdlRayjoinCdbSegment * count)()
    index = 0
    segment_id = 1
    for chain in dataset.chains:
        for start, end in zip(chain.points, chain.points[1:]):
            rows[index] = _RtdlRayjoinCdbSegment(
                segment_id,
                float(start.x),
                float(start.y),
                float(end.x),
                float(end.y),
                int(chain.left_face_id),
                int(chain.right_face_id),
            )
            index += 1
            segment_id += 1
    return PackedRayjoinCdbSegments(records=rows, count=count, owner=dataset)


def _packed_segments(dataset: CdbDataset):
    import numpy as np
    from .embree_runtime import pack_segments

    count = _edge_count(dataset)
    ids = np.empty(count, dtype=np.int64)
    x0 = np.empty(count, dtype=np.float64)
    y0 = np.empty(count, dtype=np.float64)
    x1 = np.empty(count, dtype=np.float64)
    y1 = np.empty(count, dtype=np.float64)
    index = 0
    segment_id = 1
    for chain in dataset.chains:
        for start, end in zip(chain.points, chain.points[1:]):
            ids[index] = segment_id
            x0[index] = start.x
            y0[index] = start.y
            x1[index] = end.x
            y1[index] = end.y
            index += 1
            segment_id += 1
    return pack_segments(ids=ids, x0=x0, y0=y0, x1=x1, y1=y1)


def _segment_coordinate_arrays(dataset: CdbDataset):
    import numpy as np

    count = _edge_count(dataset)
    x0 = np.empty(count, dtype=np.float64)
    y0 = np.empty(count, dtype=np.float64)
    x1 = np.empty(count, dtype=np.float64)
    y1 = np.empty(count, dtype=np.float64)
    index = 0
    for chain in dataset.chains:
        for start, end in zip(chain.points, chain.points[1:]):
            x0[index] = start.x
            y0[index] = start.y
            x1[index] = end.x
            y1[index] = end.y
            index += 1
    return x0, y0, x1, y1


def _packed_points_from_cdb(dataset: CdbDataset):
    import numpy as np
    from .embree_runtime import pack_points

    count = _point_count(dataset)
    ids = np.arange(1, count + 1, dtype=np.int64)
    x = np.empty(count, dtype=np.float64)
    y = np.empty(count, dtype=np.float64)
    index = 0
    for chain in dataset.chains:
        for point in chain.points:
            x[index] = point.x
            y[index] = point.y
            index += 1
    return pack_points(ids=ids, x=x, y=y, dimension=2)


def _packed_points_from_xy(points: list[tuple[float, float]]):
    import numpy as np
    from .embree_runtime import pack_points

    count = len(points)
    ids = np.arange(1, count + 1, dtype=np.int64)
    x = np.empty(count, dtype=np.float64)
    y = np.empty(count, dtype=np.float64)
    for index, (px, py) in enumerate(points):
        x[index] = px
        y[index] = py
    return pack_points(ids=ids, x=x, y=y, dimension=2)


def _packed_points_from_arrays(x, y):
    import numpy as np
    from .embree_runtime import pack_points

    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if x.shape != y.shape:
        raise ValueError("point coordinate arrays must have matching shapes")
    ids = np.arange(1, int(x.size) + 1, dtype=np.int64)
    return pack_points(ids=ids, x=x, y=y, dimension=2)


def _edge_start_arrays_for_ids(edge_starts, edge_ids):
    import numpy as np

    if isinstance(edge_starts, tuple):
        return (
            np.asarray(edge_starts[0], dtype=np.float64)[edge_ids],
            np.asarray(edge_starts[1], dtype=np.float64)[edge_ids],
        )
    return (
        np.fromiter((float(edge_starts[int(edge_id)].x) for edge_id in edge_ids), dtype=np.float64, count=int(edge_ids.size)),
        np.fromiter((float(edge_starts[int(edge_id)].y) for edge_id in edge_ids), dtype=np.float64, count=int(edge_ids.size)),
    )


def _midpoint_points_from_lsi_rows_numpy(lsi_rows, edge_starts, map_index: int):
    import numpy as np

    if len(lsi_rows) < 2:
        return _packed_points_from_arrays(np.empty(0, dtype=np.float64), np.empty(0, dtype=np.float64))
    edge_field = "left_id" if map_index == 0 else "right_id"
    tie_field = "right_id" if map_index == 0 else "left_id"
    edge_ids = np.asarray(lsi_rows[edge_field], dtype=np.int64) - 1
    tie_ids = np.asarray(lsi_rows[tie_field], dtype=np.int64) - 1
    x = np.asarray(lsi_rows["intersection_point_x"], dtype=np.float64)
    y = np.asarray(lsi_rows["intersection_point_y"], dtype=np.float64)
    start_x, start_y = _edge_start_arrays_for_ids(edge_starts, edge_ids)
    distance2 = (x - start_x) * (x - start_x) + (y - start_y) * (y - start_y)
    order = np.lexsort((tie_ids, distance2, edge_ids))
    sorted_edges = edge_ids[order]
    same_edge = sorted_edges[1:] == sorted_edges[:-1]
    if not bool(np.any(same_edge)):
        return _packed_points_from_arrays(np.empty(0, dtype=np.float64), np.empty(0, dtype=np.float64))
    sorted_x = x[order]
    sorted_y = y[order]
    midpoint_x = (sorted_x[:-1][same_edge] + sorted_x[1:][same_edge]) * 0.5
    midpoint_y = (sorted_y[:-1][same_edge] + sorted_y[1:][same_edge]) * 0.5
    return _packed_points_from_arrays(midpoint_x, midpoint_y)


@contextmanager
def _rayjoin_lsi_predicate_env(backend: str):
    key = "RTDL_OPTIX_SEGMENT_PAIR_PREDICATE" if backend == "optix" else "RTDL_EMBREE_SEGMENT_PAIR_PREDICATE"
    previous_values = {key: os.environ.get(key)}
    os.environ[key] = "rayjoin_lsi"
    if backend == "embree":
        quality_key = "RTDL_EMBREE_AABB_SCENE_BUILD_QUALITY"
        previous_values[quality_key] = os.environ.get(quality_key)
        os.environ.setdefault(quality_key, "low")
    try:
        yield
    finally:
        for env_key, previous in previous_values.items():
            if previous is None:
                os.environ.pop(env_key, None)
            else:
                os.environ[env_key] = previous


@contextmanager
def _rayjoin_cdb_point_location_env(query_map_id: int, scale_bounds: tuple[float, float, float, float] | None):
    values = {"RTDL_RAYJOIN_CDB_QUERY_MAP_ID": str(int(query_map_id))}
    if scale_bounds is not None:
        min_x, max_x, min_y, max_y = scale_bounds
        values.update(
            {
                "RTDL_RAYJOIN_CDB_SCALE_MIN_X": repr(float(min_x)),
                "RTDL_RAYJOIN_CDB_SCALE_MAX_X": repr(float(max_x)),
                "RTDL_RAYJOIN_CDB_SCALE_MIN_Y": repr(float(min_y)),
                "RTDL_RAYJOIN_CDB_SCALE_MAX_Y": repr(float(max_y)),
            }
        )
    previous = {key: os.environ.get(key) for key in values}
    os.environ.update(values)
    try:
        yield
    finally:
        for key, old_value in previous.items():
            if old_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value


@contextmanager
def _directed_segment_point_location_grouping_env(
    backend: str,
    point_counts: tuple[int, ...] = (),
):
    generic_keys = (
        "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE",
        "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_SIZE",
        "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_AREA_ENLARGE",
    )
    legacy_keys = (
        "RTDL_RAYJOIN_CDB_GROUP_MODE",
        "RTDL_RAYJOIN_CDB_GROUP_MAX_SIZE",
        "RTDL_RAYJOIN_CDB_GROUP_AREA_ENLARGE",
    )
    should_auto = (
        backend == "optix"
        and not any(os.environ.get(key) for key in (*generic_keys, *legacy_keys))
        and bool(point_counts)
        and max(int(count) for count in point_counts) >= POINT_LOCATION_ADAPTIVE_GROUPING_POINT_THRESHOLD
    )
    if not should_auto:
        yield
        return

    values = {
        "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE": "adaptive",
        "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_SIZE": "16",
        "RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_AREA_ENLARGE": "1.2",
    }
    previous = {key: os.environ.get(key) for key in values}
    os.environ.update(values)
    try:
        yield
    finally:
        for key, old_value in previous.items():
            if old_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value


def _shared_rayjoin_bounds(
    left_inputs: RayjoinOverlayPackedInputs,
    right_inputs: RayjoinOverlayPackedInputs,
) -> tuple[float, float, float, float]:
    import numpy as np

    arrays_x = [left_inputs.point_coords[0], right_inputs.point_coords[0]]
    arrays_y = [left_inputs.point_coords[1], right_inputs.point_coords[1]]
    non_empty_x = [array for array in arrays_x if int(array.size) > 0]
    non_empty_y = [array for array in arrays_y if int(array.size) > 0]
    if not non_empty_x or not non_empty_y:
        raise ValueError("RayJoin CDB scaling requires non-empty point inputs")
    min_x = min(float(np.min(array)) for array in non_empty_x)
    max_x = max(float(np.max(array)) for array in non_empty_x)
    min_y = min(float(np.min(array)) for array in non_empty_y)
    max_y = max(float(np.max(array)) for array in non_empty_y)
    return min_x, max_x, min_y, max_y


def _simple_lsi_compiled():
    return SimpleNamespace(
        candidates=SimpleNamespace(
            left=SimpleNamespace(name="left"),
            right=SimpleNamespace(name="right"),
        )
    )


def _rows_from_segment_pair_ids(
    pair_path: str | Path,
    left: CdbDataset,
    right: CdbDataset,
    left_coords=None,
    right_coords=None,
    *,
    binary_u64_pairs: bool = False,
):
    import numpy as np

    if binary_u64_pairs:
        encoded_pairs = np.fromfile(pair_path, dtype=np.uint64)
        if encoded_pairs.size:
            pairs = np.empty((int(encoded_pairs.size), 2), dtype=np.uint32)
            pairs[:, 0] = (encoded_pairs >> np.uint64(32)).astype(np.uint32, copy=False)
            pairs[:, 1] = (encoded_pairs & np.uint64(0xFFFFFFFF)).astype(np.uint32, copy=False)
        else:
            pairs = np.empty((0, 2), dtype=np.uint32)
    else:
        pairs = np.loadtxt(pair_path, dtype=np.uint32)
        pairs = np.reshape(pairs, (-1, 2)) if pairs.size else np.empty((0, 2), dtype=np.uint32)
    if pairs.size == 0:
        return np.empty(
            0,
            dtype=[
                ("left_id", np.uint32),
                ("right_id", np.uint32),
                ("intersection_point_x", np.float64),
                ("intersection_point_y", np.float64),
            ],
        )
    left_x0, left_y0, left_x1, left_y1 = (
        left_coords if left_coords is not None else _segment_coordinate_arrays(left)
    )
    right_x0, right_y0, right_x1, right_y1 = (
        right_coords if right_coords is not None else _segment_coordinate_arrays(right)
    )
    left_index = pairs[:, 0].astype(np.int64, copy=False) - 1
    right_index = pairs[:, 1].astype(np.int64, copy=False) - 1

    px = left_x0[left_index]
    py = left_y0[left_index]
    rx = left_x1[left_index] - px
    ry = left_y1[left_index] - py
    qx = right_x0[right_index]
    qy = right_y0[right_index]
    sx = right_x1[right_index] - qx
    sy = right_y1[right_index] - qy
    denom = rx * sy - ry * sx
    qpx = qx - px
    qpy = qy - py
    with np.errstate(divide="ignore", invalid="ignore"):
        t = (qpx * sy - qpy * sx) / denom

    rows = np.empty(
        pairs.shape[0],
        dtype=[
            ("left_id", np.uint32),
            ("right_id", np.uint32),
            ("intersection_point_x", np.float64),
            ("intersection_point_y", np.float64),
        ],
    )
    rows["left_id"] = pairs[:, 0]
    rows["right_id"] = pairs[:, 1]
    rows["intersection_point_x"] = px + t * rx
    rows["intersection_point_y"] = py + t * ry
    return rows


def _run_lsi_rows(
    backend: str,
    map0_segments,
    map1_segments,
    left: CdbDataset,
    right: CdbDataset,
    left_coords=None,
    right_coords=None,
) -> tuple[object, dict[str, object]]:
    start = time.perf_counter()
    with _rayjoin_lsi_predicate_env(backend):
        if backend == "optix":
            from .optix_runtime import prepare_segment_pair_intersection_optix
            from .optix_runtime import prepare_segment_pair_left_set_optix

            prepared = prepare_segment_pair_intersection_optix(map1_segments)
            prepared_left = None
            dump_path = None
            previous_dump_path = os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_DUMP_PATH")
            previous_dump_capacity = os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_DUMP_CAPACITY")
            previous_dump_format = os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_DUMP_FORMAT")
            try:
                prepared_left = prepare_segment_pair_left_set_optix(map0_segments)
                with tempfile.NamedTemporaryFile(prefix="rtdl_overlay_lsi_pairs_", suffix=".bin", delete=False) as handle:
                    dump_path = handle.name
                os.environ["RTDL_OPTIX_SEGMENT_PAIR_DUMP_PATH"] = dump_path
                os.environ["RTDL_OPTIX_SEGMENT_PAIR_DUMP_CAPACITY"] = os.environ.get(
                    "RTDL_RAYJOIN_OVERLAY_PAIR_DUMP_CAPACITY",
                    "5000000",
                )
                os.environ["RTDL_OPTIX_SEGMENT_PAIR_DUMP_FORMAT"] = "binary_u64_pairs"
                count_result = prepared.count_prepared_left_exact_intersections(prepared_left)
                expected_count = int(count_result["count"] if isinstance(count_result, dict) else count_result)
                row_array = _rows_from_segment_pair_ids(
                    dump_path,
                    left,
                    right,
                    left_coords=left_coords,
                    right_coords=right_coords,
                    binary_u64_pairs=True,
                )
                if len(row_array) != expected_count:
                    raise RuntimeError(
                        "OptiX RayJoin overlay LSI pair dump count does not match scalar count: "
                        f"{len(row_array)} != {expected_count}"
                    )
                timings = prepared.last_phase_timings() or {}
            finally:
                if previous_dump_path is None:
                    os.environ.pop("RTDL_OPTIX_SEGMENT_PAIR_DUMP_PATH", None)
                else:
                    os.environ["RTDL_OPTIX_SEGMENT_PAIR_DUMP_PATH"] = previous_dump_path
                if previous_dump_capacity is None:
                    os.environ.pop("RTDL_OPTIX_SEGMENT_PAIR_DUMP_CAPACITY", None)
                else:
                    os.environ["RTDL_OPTIX_SEGMENT_PAIR_DUMP_CAPACITY"] = previous_dump_capacity
                if previous_dump_format is None:
                    os.environ.pop("RTDL_OPTIX_SEGMENT_PAIR_DUMP_FORMAT", None)
                else:
                    os.environ["RTDL_OPTIX_SEGMENT_PAIR_DUMP_FORMAT"] = previous_dump_format
                if dump_path is not None:
                    Path(dump_path).unlink(missing_ok=True)
                if prepared_left is not None:
                    prepared_left.close()
                prepared.close()
        elif backend == "embree":
            from .embree_runtime import _call_rayjoin_lsi_aabb_refined_embree_packed
            from .embree_runtime import _load_embree_library

            library = _load_embree_library()
            row_view, timings = _call_rayjoin_lsi_aabb_refined_embree_packed(
                _simple_lsi_compiled(),
                {"left": map0_segments, "right": map1_segments},
                library,
            )
            try:
                row_array = row_view.to_numpy(copy=True)
            finally:
                row_view.close()
        else:
            raise ValueError("backend must be 'optix' or 'embree'")
    timings = dict(timings)
    timings["hot_call_sec"] = time.perf_counter() - start
    if "native_traversal" in timings:
        timings["native_non_traversal_sec"] = max(
            0.0,
            float(timings["hot_call_sec"]) - float(timings["native_traversal"]),
        )
    return row_array, timings


def _run_point_location_faces(
    backend: str,
    base_segments,
    points,
    point_count: int,
    query_map_id: int = 1,
    scale_bounds: tuple[float, float, float, float] | None = None,
) -> tuple[object, dict[str, object]]:
    import numpy as np

    with _PreparedPointLocationRunner(
        backend,
        base_segments,
        query_map_id=query_map_id,
        scale_bounds=scale_bounds,
    ) as runner:
        return runner.faces(points, point_count)


class _PreparedPointLocationRunner:
    def __init__(
        self,
        backend: str,
        base_segments,
        *,
        query_map_id: int,
        scale_bounds: tuple[float, float, float, float] | None,
    ) -> None:
        if backend not in {"optix", "embree"}:
            raise ValueError("backend must be 'optix' or 'embree'")
        self.backend = backend
        self.base_segments = base_segments
        self.query_map_id = int(query_map_id)
        self.scale_bounds = scale_bounds
        self.prepared = None
        self.prepare_sec = 0.0

    def __enter__(self) -> "_PreparedPointLocationRunner":
        start = time.perf_counter()
        with _rayjoin_cdb_point_location_env(self.query_map_id, self.scale_bounds):
            if self.backend == "optix":
                from .optix_runtime import prepare_directed_segment_point_location_2d_optix

                self.prepared = prepare_directed_segment_point_location_2d_optix(self.base_segments)
            else:
                from .embree_runtime import prepare_directed_segment_point_location_2d_embree

                self.prepared = prepare_directed_segment_point_location_2d_embree(self.base_segments)
        self.prepare_sec = time.perf_counter() - start
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.prepared is not None:
            self.prepared.close()
            self.prepared = None

    def faces(self, points, point_count: int):
        import numpy as np

        if self.prepared is None:
            raise RuntimeError("prepared point-location runner is not open")
        start = time.perf_counter()
        rows = None
        try:
            with _rayjoin_cdb_point_location_env(self.query_map_id, self.scale_bounds):
                rows = self.prepared.run_raw(points)
                columns = rows.to_numpy_columns(copy=True)
                timings = self.prepared.last_phase_timings() or {}
        finally:
            if rows is not None:
                rows.close()

        faces = np.zeros(point_count, dtype=np.uint32)
        if point_count:
            point_ids = columns["point_id"].astype(np.int64, copy=False)
            faces[point_ids - 1] = columns["face_id"].astype(np.uint32, copy=False)
        timings = dict(timings)
        timings["hot_call_sec"] = time.perf_counter() - start
        return faces, timings

    def classify(self, points) -> tuple[int | None, dict[str, object]]:
        if self.prepared is None:
            raise RuntimeError("prepared point-location runner is not open")
        use_device_face_ids = (
            self.backend == "optix"
            and os.environ.get("RTDL_DIRECTED_SEGMENT_POINT_LOCATION_FACE_ID_COLUMNS", "1").lower()
            not in {"0", "false", "no"}
            and hasattr(self.prepared, "prepare_query_points")
            and hasattr(self.prepared, "write_face_ids_device_points")
        )
        if not use_device_face_ids:
            return self.count(points)

        start = time.perf_counter()
        prepared_points = None
        try:
            with _rayjoin_cdb_point_location_env(self.query_map_id, self.scale_bounds):
                prepared_points = self.prepared.prepare_query_points(points)
                result = self.prepared.write_face_ids_device_points(prepared_points)
                timings = self.prepared.last_phase_timings() or {}
        finally:
            if prepared_points is not None:
                prepared_points.close()
        timings = dict(timings)
        timings["hot_call_sec"] = time.perf_counter() - start
        timings["face_id_output_count"] = int(result.get("row_count", 0))
        timings["output_contract"] = (
            "directed_segment_point_location_face_id_device_column_no_host_download_no_positive_count_atomic"
        )
        return None, timings

    def count(self, points) -> tuple[int, dict[str, object]]:
        if self.prepared is None:
            raise RuntimeError("prepared point-location runner is not open")
        start = time.perf_counter()
        with _rayjoin_cdb_point_location_env(self.query_map_id, self.scale_bounds):
            positive_count = int(self.prepared.count_positive_faces(points))
            timings = self.prepared.last_phase_timings() or {}
        timings = dict(timings)
        timings["hot_call_sec"] = time.perf_counter() - start
        return positive_count, timings


@contextmanager
def _prepared_point_location_pair(
    backend: str,
    right_cdb_segments,
    left_cdb_segments,
    scale_bounds: tuple[float, float, float, float] | None,
    point_counts: tuple[int, int] | None = None,
):
    runners = (
        _PreparedPointLocationRunner(
            backend,
            right_cdb_segments,
            query_map_id=0,
            scale_bounds=scale_bounds,
        ),
        _PreparedPointLocationRunner(
            backend,
            left_cdb_segments,
            query_map_id=1,
            scale_bounds=scale_bounds,
        ),
    )
    prepare_start = time.perf_counter()
    entered = []
    optix_parallel_opt_in = os.environ.get("RTDL_RAYJOIN_OVERLAY_OPTIX_PARALLEL_PIP_PREPARE")
    use_parallel_prepare = (
        not os.environ.get("RTDL_RAYJOIN_OVERLAY_SERIAL_PIP_PREPARE")
        and (backend != "optix" or bool(optix_parallel_opt_in))
    )
    try:
        with _directed_segment_point_location_grouping_env(backend, point_counts or ()):
            if use_parallel_prepare:
                from concurrent.futures import ThreadPoolExecutor

                with ThreadPoolExecutor(max_workers=2, thread_name_prefix="rtdl-pip-prepare") as pool:
                    futures = [pool.submit(runner.__enter__) for runner in runners]
                    for runner, future in zip(runners, futures):
                        future.result()
                        entered.append(runner)
            else:
                for runner in runners:
                    runner.__enter__()
                    entered.append(runner)
        prepare_wall_sec = time.perf_counter() - prepare_start
        yield runners[0], runners[1], prepare_wall_sec
    finally:
        for runner in reversed(entered):
            runner.__exit__(None, None, None)


def _intersections_from_lsi_rows(rows) -> list[RayjoinOverlayIntersection]:
    return [
        RayjoinOverlayIntersection(
            eid0=int(row["left_id"]) - 1,
            eid1=int(row["right_id"]) - 1,
            x=float(row["intersection_point_x"]),
            y=float(row["intersection_point_y"]),
        )
        for row in rows
    ]


def _edge_start_points(dataset: CdbDataset) -> list[CdbPoint]:
    starts: list[CdbPoint] = []
    for chain in dataset.chains:
        starts.extend(chain.points[:-1])
    return starts


def _sort_xsects_for_map(
    xsects: Iterable[RayjoinOverlayIntersection],
    edge_starts,
    map_index: int,
) -> list[RayjoinOverlayIntersection]:
    edge_attr = "eid0" if map_index == 0 else "eid1"
    grouped: dict[int, list[RayjoinOverlayIntersection]] = {}
    for xsect in xsects:
        grouped.setdefault(int(getattr(xsect, edge_attr)), []).append(xsect)
    sorted_rows: list[RayjoinOverlayIntersection] = []
    for eid in sorted(grouped):
        if isinstance(edge_starts, tuple):
            start_x = float(edge_starts[0][eid])
            start_y = float(edge_starts[1][eid])
        else:
            start = edge_starts[eid]
            start_x = float(start.x)
            start_y = float(start.y)
        group = grouped[eid]
        group.sort(key=lambda x: ((x.x - start_x) * (x.x - start_x) + (x.y - start_y) * (x.y - start_y), x.eid0, x.eid1))
        sorted_rows.extend(group)
    return sorted_rows


def _midpoints_for_sorted_xsects(
    xsects: list[RayjoinOverlayIntersection],
    map_index: int,
) -> tuple[list[tuple[float, float]], list[RayjoinOverlayIntersection]]:
    edge_attr = "eid0" if map_index == 0 else "eid1"
    midpoints: list[tuple[float, float]] = []
    owners: list[RayjoinOverlayIntersection] = []
    index = 0
    while index < len(xsects):
        edge_id = int(getattr(xsects[index], edge_attr))
        end = index + 1
        while end < len(xsects) and int(getattr(xsects[end], edge_attr)) == edge_id:
            end += 1
        group = xsects[index:end]
        for left, right in zip(group, group[1:]):
            midpoints.append(((left.x + right.x) * 0.5, (left.y + right.y) * 0.5))
            owners.append(left)
        index = end
    return midpoints, owners


def _assign_midpoint_faces(
    owners: list[RayjoinOverlayIntersection],
    faces,
) -> int:
    positive = 0
    for index, owner in enumerate(owners):
        face = int(faces[index])
        owner.mid_point_polygon_id = face
        if face != EXTERIOR_FACE_ID:
            positive += 1
    return positive


def _dedupe_consecutive_points(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if not points:
        return points
    deduped = [points[0]]
    for point in points[1:]:
        if point != deduped[-1]:
            deduped.append(point)
    return deduped


def _assemble_output_chains(
    datasets: tuple[CdbDataset, CdbDataset],
    xsect_edges_sorted: tuple[list[RayjoinOverlayIntersection], list[RayjoinOverlayIntersection]],
    point_in_polygon: tuple[object, object],
) -> tuple[list[RayjoinOverlayOutputChain], int]:
    output_chains: list[RayjoinOverlayOutputChain] = []

    def flush(output_chain: RayjoinOverlayOutputChain) -> None:
        if not output_chain.points:
            return
        keep = (
            output_chain.left_polygon_id * output_chain.other_map_polygon_id != 0
            or output_chain.right_polygon_id * output_chain.other_map_polygon_id != 0
        )
        if keep:
            output_chain.points = _dedupe_consecutive_points(output_chain.points)
            output_chains.append(
                RayjoinOverlayOutputChain(
                    points=list(output_chain.points),
                    left_polygon_id=output_chain.left_polygon_id,
                    right_polygon_id=output_chain.right_polygon_id,
                    other_map_polygon_id=output_chain.other_map_polygon_id,
                )
            )
        output_chain.points.clear()

    for map_index, dataset in enumerate(datasets):
        edge_attr = "eid0" if map_index == 0 else "eid1"
        grouped: dict[int, list[RayjoinOverlayIntersection]] = {}
        for xsect in xsect_edges_sorted[map_index]:
            grouped.setdefault(int(getattr(xsect, edge_attr)), []).append(xsect)
        point_offset = 0
        edge_id = 0
        for chain in dataset.chains:
            output_chain = RayjoinOverlayOutputChain(
                points=[],
                left_polygon_id=int(chain.left_face_id),
                right_polygon_id=int(chain.right_face_id),
            )
            for local_point_index, point in enumerate(chain.points):
                point_index = point_offset + local_point_index
                output_chain.other_map_polygon_id = int(point_in_polygon[map_index][point_index])
                output_chain.points.append((float(point.x), float(point.y)))
                if local_point_index == len(chain.points) - 1:
                    continue
                xsects = grouped.get(edge_id)
                if xsects:
                    output_chain.points.append((xsects[0].x, xsects[0].y))
                    for xsect, next_xsect in zip(xsects, xsects[1:]):
                        flush(output_chain)
                        output_chain.other_map_polygon_id = int(xsect.mid_point_polygon_id)
                        output_chain.points.append((xsect.x, xsect.y))
                        output_chain.points.append((next_xsect.x, next_xsect.y))
                    flush(output_chain)
                    output_chain.points.append((xsects[-1].x, xsects[-1].y))
                edge_id += 1
            flush(output_chain)
            point_offset += len(chain.points)

    face_ids: dict[tuple[int, int], int] = {}
    point_ids: dict[tuple[float, float], int] = {}
    point_counter = 0

    def create_polygon(polygon_id1: int, polygon_id2: int) -> int:
        if polygon_id1 == 0 or polygon_id2 == 0:
            return 0
        key = (polygon_id1, polygon_id2)
        if key not in face_ids:
            face_ids[key] = len(face_ids) + 1
        return face_ids[key]

    for chain in output_chains:
        other = int(chain.other_map_polygon_id)
        chain.left_polygon_id = create_polygon(*sorted((int(chain.left_polygon_id), other)))
        chain.right_polygon_id = create_polygon(*sorted((int(chain.right_polygon_id), other)))
        for point in chain.points:
            if point not in point_ids:
                point_ids[point] = point_counter
                point_counter += 1
        chain.first_point_idx = point_ids[chain.points[0]]
        chain.last_point_idx = point_ids[chain.points[-1]]

    return output_chains, len(face_ids)


def write_output_chains(
    output_chains: list[RayjoinOverlayOutputChain],
    path: str | Path,
) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for index, chain in enumerate(output_chains, start=1):
            handle.write(
                f"{index} {len(chain.points)} {chain.first_point_idx} {chain.last_point_idx} "
                f"{chain.left_polygon_id} {chain.right_polygon_id}\n"
            )
            for x, y in chain.points:
                handle.write(f"{x:.6f} {y:.6f}\n")
    return output


def _run_rayjoin_overlay_packed(
    left_inputs: RayjoinOverlayPackedInputs,
    right_inputs: RayjoinOverlayPackedInputs,
    *,
    backend: str,
    assemble_output: bool = False,
    output_path: str | Path | None = None,
    left: CdbDataset | None = None,
    right: CdbDataset | None = None,
    input_phase_name: str | None = None,
    input_phase_sec: float | None = None,
    total_start: float | None = None,
) -> dict[str, object]:
    import numpy as np

    if total_start is None:
        total_start = time.perf_counter()
    phase_seconds: dict[str, float] = {}
    native_timings: dict[str, object] = {}
    if input_phase_name is not None and input_phase_sec is not None:
        phase_seconds[input_phase_name] = float(input_phase_sec)

    left_segments = left_inputs.segments
    right_segments = right_inputs.segments
    left_cdb_segments = left_inputs.cdb_segments
    right_cdb_segments = right_inputs.cdb_segments
    left_points = left_inputs.points
    right_points = right_inputs.points
    scale_bounds = _shared_rayjoin_bounds(left_inputs, right_inputs)

    lsi_rows, lsi_timings = _run_lsi_rows(
        backend,
        left_segments,
        right_segments,
        left,
        right,
        left_coords=left_inputs.segment_coords,
        right_coords=right_inputs.segment_coords,
    )
    native_timings["lsi"] = lsi_timings

    needs_output_faces = bool(assemble_output or output_path is not None)
    edge_starts = (left_inputs.edge_starts, right_inputs.edge_starts)
    xsects = None
    xsects_sorted = None
    midpoint_point_inputs = None
    if needs_output_faces:
        materialize_start = time.perf_counter()
        xsects = _intersections_from_lsi_rows(lsi_rows)
        phase_seconds["lsi_row_object_materialize_sec"] = time.perf_counter() - materialize_start
        sort_start = time.perf_counter()
        xsects_sorted = (
            _sort_xsects_for_map(xsects, edge_starts[0], 0),
            _sort_xsects_for_map(xsects, edge_starts[1], 1),
        )
        phase_seconds["lsi_row_sort_sec"] = time.perf_counter() - sort_start
    else:
        midpoint_start = time.perf_counter()
        midpoint_point_inputs = (
            _midpoint_points_from_lsi_rows_numpy(lsi_rows, edge_starts[0], 0),
            _midpoint_points_from_lsi_rows_numpy(lsi_rows, edge_starts[1], 1),
        )
        phase_seconds["lsi_midpoint_projection_sec"] = time.perf_counter() - midpoint_start

    vertex0_faces = None
    vertex1_faces = None
    midpoint_counts: list[int] = []
    midpoint_positive_counts: list[int] = []

    with _prepared_point_location_pair(
        backend,
        right_cdb_segments,
        left_cdb_segments,
        scale_bounds,
        point_counts=(int(left_points.count), int(right_points.count)),
    ) as (map0_in_map1, map1_in_map0, prepare_wall_sec):
        phase_seconds["point_location_prepare_sec"] = float(
            map0_in_map1.prepare_sec + map1_in_map0.prepare_sec
        )
        phase_seconds["point_location_prepare_wall_sec"] = float(prepare_wall_sec)
        native_timings["point_location_prepare_map0_in_map1"] = {
            "mode": "prepare",
            "hot_call_sec": float(map0_in_map1.prepare_sec),
        }
        native_timings["point_location_prepare_map1_in_map0"] = {
            "mode": "prepare",
            "hot_call_sec": float(map1_in_map0.prepare_sec),
        }
        if needs_output_faces:
            vertex0_faces, vertex0_timings = map0_in_map1.faces(left_points, int(left_points.count))
            vertex0_positive_count = int(np.count_nonzero(vertex0_faces))
            vertex1_faces, vertex1_timings = map1_in_map0.faces(right_points, int(right_points.count))
            vertex1_positive_count = int(np.count_nonzero(vertex1_faces))
        else:
            vertex0_positive_count, vertex0_timings = map0_in_map1.classify(left_points)
            vertex1_positive_count, vertex1_timings = map1_in_map0.classify(right_points)
        native_timings["vertex_pip_map0_in_map1"] = vertex0_timings
        native_timings["vertex_pip_map1_in_map0"] = vertex1_timings

        if needs_output_faces:
            if xsects_sorted is None:
                raise RuntimeError("overlay output-chain assembly requires sorted LSI rows")
            for map_index, locator in ((0, map0_in_map1), (1, map1_in_map0)):
                midpoints, owners = _midpoints_for_sorted_xsects(xsects_sorted[map_index], map_index)
                midpoint_counts.append(len(midpoints))
                if midpoints:
                    midpoint_points = _packed_points_from_xy(midpoints)
                    faces, midpoint_timings = locator.faces(midpoint_points, int(midpoint_points.count))
                    positive_count = _assign_midpoint_faces(owners, faces)
                else:
                    positive_count = 0
                    midpoint_timings = {
                        "mode": "rows",
                        "hot_call_sec": 0.0,
                        "point_count": 0,
                        "positive_face_count": 0,
                    }
                midpoint_positive_counts.append(None if positive_count is None else int(positive_count))
                native_timings[f"midpoint_pip_map{map_index}_in_map{1 - map_index}"] = midpoint_timings
        else:
            if midpoint_point_inputs is None:
                raise RuntimeError("overlay no-output path requires NumPy midpoint point inputs")
            for map_index, locator, midpoint_points in (
                (0, map0_in_map1, midpoint_point_inputs[0]),
                (1, map1_in_map0, midpoint_point_inputs[1]),
            ):
                midpoint_counts.append(int(midpoint_points.count))
                if int(midpoint_points.count):
                    positive_count, midpoint_timings = locator.classify(midpoint_points)
                else:
                    positive_count = 0
                    midpoint_timings = {
                        "mode": "count",
                        "hot_call_sec": 0.0,
                        "point_count": 0,
                        "positive_face_count": 0,
                    }
                midpoint_positive_counts.append(None if positive_count is None else int(positive_count))
                native_timings[f"midpoint_pip_map{map_index}_in_map{1 - map_index}"] = midpoint_timings

    output_payload: dict[str, object] = {
        "assembled": False,
        "chain_count": None,
        "face_count": None,
        "path": str(output_path) if output_path is not None else None,
    }
    if assemble_output or output_path is not None:
        if left is None or right is None:
            raise ValueError("overlay output-chain assembly requires full CdbDataset inputs")
        if vertex0_faces is None or vertex1_faces is None:
            raise RuntimeError("overlay output-chain assembly requires materialized vertex point-location faces")
        if xsects_sorted is None:
            raise RuntimeError("overlay output-chain assembly requires sorted LSI rows")
        assemble_start = time.perf_counter()
        chains, face_count = _assemble_output_chains(
            (left, right),
            xsects_sorted,
            (vertex0_faces, vertex1_faces),
        )
        phase_seconds["output_chain_assembly_sec"] = time.perf_counter() - assemble_start
        if output_path is not None:
            write_start = time.perf_counter()
            write_output_chains(chains, output_path)
            phase_seconds["output_chain_write_sec"] = time.perf_counter() - write_start
        output_payload = {
            "assembled": True,
            "chain_count": len(chains),
            "face_count": face_count,
            "path": str(output_path) if output_path is not None else None,
        }

    total_sec = time.perf_counter() - total_start
    phase_seconds["total_sec"] = total_sec
    return {
        "schema": "rtdl.rayjoin.overlay_rtdl_run.v1",
        "backend": backend,
        "program": "overlay",
        "input_shape": {
            "map0_chains": int(left_inputs.chain_count),
            "map1_chains": int(right_inputs.chain_count),
            "map0_points": int(left_points.count),
            "map1_points": int(right_points.count),
            "map0_edges": int(left_segments.count),
            "map1_edges": int(right_segments.count),
        },
        "lsi": {
            "intersection_count": int(len(lsi_rows)),
            "predicate_contract": "rayjoin_author_lsi_intersect_test_endpoint_collinear_contract",
        },
        "vertex_pip": {
            "map0_points_in_map1": int(left_points.count),
            "map0_positive_faces": None if vertex0_positive_count is None else int(vertex0_positive_count),
            "map1_points_in_map0": int(right_points.count),
            "map1_positive_faces": None if vertex1_positive_count is None else int(vertex1_positive_count),
        },
        "midpoint_pip": {
            "map0_midpoints_in_map1": int(midpoint_counts[0]),
            "map0_positive_faces": None if midpoint_positive_counts[0] is None else int(midpoint_positive_counts[0]),
            "map1_midpoints_in_map0": int(midpoint_counts[1]),
            "map1_positive_faces": None if midpoint_positive_counts[1] is None else int(midpoint_positive_counts[1]),
        },
        "output": output_payload,
        "phase_seconds": phase_seconds,
        "native_timings": native_timings,
    }


def run_rayjoin_overlay_rtdl(
    left: CdbDataset,
    right: CdbDataset,
    *,
    backend: str,
    assemble_output: bool = False,
    output_path: str | Path | None = None,
) -> dict[str, object]:
    """Run the RayJoin polygon-overlay program shape on RTDL primitives.

    The default mirrors RayJoin ``polyover_exec`` without ``-output``: LSI,
    vertex point-location in both directions, and midpoint classification are
    executed. Output-chain assembly and file writing are opt-in because paper
    timings normally omit the optional output file.
    """

    total_start = time.perf_counter()
    pack_start = time.perf_counter()
    left_inputs = _packed_overlay_inputs(left)
    right_inputs = _packed_overlay_inputs(right)
    return _run_rayjoin_overlay_packed(
        left_inputs,
        right_inputs,
        backend=backend,
        assemble_output=assemble_output,
        output_path=output_path,
        left=left,
        right=right,
        input_phase_name="pack_inputs_sec",
        input_phase_sec=time.perf_counter() - pack_start,
        total_start=total_start,
    )


def run_rayjoin_overlay_rtdl_from_cdb_paths(
    left_path: str | Path,
    right_path: str | Path,
    *,
    backend: str,
    assemble_output: bool = False,
    output_path: str | Path | None = None,
) -> dict[str, object]:
    if assemble_output or output_path is not None:
        from .datasets import load_cdb

        return run_rayjoin_overlay_rtdl(
            load_cdb(left_path),
            load_cdb(right_path),
            backend=backend,
            assemble_output=assemble_output,
            output_path=output_path,
        )

    total_start = time.perf_counter()
    load_pack_start = time.perf_counter()
    left_inputs = load_cdb_overlay_packed_inputs(left_path)
    right_inputs = load_cdb_overlay_packed_inputs(right_path)
    return _run_rayjoin_overlay_packed(
        left_inputs,
        right_inputs,
        backend=backend,
        input_phase_name="load_pack_inputs_sec",
        input_phase_sec=time.perf_counter() - load_pack_start,
        total_start=total_start,
    )
