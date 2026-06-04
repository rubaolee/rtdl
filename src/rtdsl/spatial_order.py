from __future__ import annotations

from collections.abc import Callable
from typing import Iterable, Mapping


SPATIAL_POINT_ORDER_MODES_2D = ("natural", "x_then_y", "y_then_x", "morton_xy")
SPATIAL_SEGMENT_ORDER_MODES_2D = SPATIAL_POINT_ORDER_MODES_2D


def spatial_order_points_2d(points: Iterable[object], mode: str = "morton_xy") -> tuple[object, ...]:
    """Return points in a deterministic 2-D locality order without changing IDs."""

    if mode not in SPATIAL_POINT_ORDER_MODES_2D:
        raise ValueError("mode must be one of: natural, x_then_y, y_then_x, morton_xy")
    point_tuple = tuple(points)
    if mode == "natural" or not point_tuple:
        return point_tuple
    ordered = _try_numpy_order_by_xy(point_tuple, mode, _record_xy)
    if ordered is not None:
        return ordered
    return _python_order_by_xy(point_tuple, mode, _record_xy)


def spatial_order_segments_2d(segments: Iterable[object], mode: str = "morton_xy") -> tuple[object, ...]:
    """Return segments in a deterministic centroid-locality order without changing IDs."""

    if mode not in SPATIAL_SEGMENT_ORDER_MODES_2D:
        raise ValueError("mode must be one of: natural, x_then_y, y_then_x, morton_xy")
    segment_tuple = tuple(segments)
    if mode == "natural" or not segment_tuple:
        return segment_tuple
    ordered = _try_numpy_order_by_xy(segment_tuple, mode, _segment_centroid_xy)
    if ordered is not None:
        return ordered
    return _python_order_by_xy(segment_tuple, mode, _segment_centroid_xy)


def _python_order_by_xy(
    records: tuple[object, ...],
    mode: str,
    xy_getter: Callable[[object], tuple[float, float]],
) -> tuple[object, ...]:
    if mode == "x_then_y":
        return tuple(sorted(records, key=lambda record: (*xy_getter(record), _record_id(record))))
    if mode == "y_then_x":
        return tuple(
            sorted(
                records,
                key=lambda record: (
                    xy_getter(record)[1],
                    xy_getter(record)[0],
                    _record_id(record),
                ),
            )
        )

    xs_ys = tuple(xy_getter(record) for record in records)
    min_x = min(x for x, _ in xs_ys)
    max_x = max(x for x, _ in xs_ys)
    min_y = min(y for _, y in xs_ys)
    max_y = max(y for _, y in xs_ys)
    span_x = max(max_x - min_x, 1.0e-30)
    span_y = max(max_y - min_y, 1.0e-30)

    def morton_key(record: object) -> tuple[int, int]:
        x, y = xy_getter(record)
        ix = max(0, min(65535, int(((x - min_x) / span_x) * 65535.0)))
        iy = max(0, min(65535, int(((y - min_y) / span_y) * 65535.0)))
        return (_morton_code_2d_16(ix, iy), _record_id(record))

    return tuple(sorted(records, key=morton_key))


def _try_numpy_order_by_xy(
    records: tuple[object, ...],
    mode: str,
    xy_getter: Callable[[object], tuple[float, float]],
) -> tuple[object, ...] | None:
    try:
        import numpy as np
    except Exception:
        return None
    try:
        ids = np.fromiter((_record_id(record) for record in records), dtype=np.int64, count=len(records))
        xy = np.asarray([xy_getter(record) for record in records], dtype=np.float64)
        if xy.shape != (len(records), 2):
            return None
        xs = xy[:, 0]
        ys = xy[:, 1]
        if mode == "x_then_y":
            order = np.lexsort((ids, ys, xs))
        elif mode == "y_then_x":
            order = np.lexsort((ids, xs, ys))
        else:
            codes = _numpy_morton_codes_2d_16(xs, ys, np)
            order = np.lexsort((ids, codes))
        return tuple(records[int(index)] for index in order)
    except Exception:
        return None


def _numpy_morton_codes_2d_16(xs, ys, np):
    min_x = float(np.min(xs))
    max_x = float(np.max(xs))
    min_y = float(np.min(ys))
    max_y = float(np.max(ys))
    span_x = max(max_x - min_x, 1.0e-30)
    span_y = max(max_y - min_y, 1.0e-30)
    ix = np.clip(((xs - min_x) / span_x) * 65535.0, 0.0, 65535.0).astype(np.uint64)
    iy = np.clip(((ys - min_y) / span_y) * 65535.0, 0.0, 65535.0).astype(np.uint64)
    return _numpy_part1by1_16(ix, np) | (_numpy_part1by1_16(iy, np) << np.uint64(1))


def _numpy_part1by1_16(values, np):
    v = values & np.uint64(0x0000ffff)
    v = (v | (v << np.uint64(8))) & np.uint64(0x00ff00ff)
    v = (v | (v << np.uint64(4))) & np.uint64(0x0f0f0f0f)
    v = (v | (v << np.uint64(2))) & np.uint64(0x33333333)
    v = (v | (v << np.uint64(1))) & np.uint64(0x55555555)
    return v


def _record_id(record: object) -> int:
    if not isinstance(record, Mapping):
        try:
            return int(getattr(record, "id"))
        except AttributeError:
            pass
    if isinstance(record, Mapping):
        return int(record["id"])
    raise TypeError(f"record does not expose an id field: {record!r}")


def _record_xy(record: object) -> tuple[float, float]:
    if not isinstance(record, Mapping):
        try:
            return float(getattr(record, "x")), float(getattr(record, "y"))
        except AttributeError:
            pass
    if isinstance(record, Mapping):
        return float(record["x"]), float(record["y"])
    raise TypeError(f"record does not expose x/y fields: {record!r}")


def _segment_centroid_xy(record: object) -> tuple[float, float]:
    if not isinstance(record, Mapping):
        try:
            x0 = float(getattr(record, "x0"))
            y0 = float(getattr(record, "y0"))
            x1 = float(getattr(record, "x1"))
            y1 = float(getattr(record, "y1"))
            return ((x0 + x1) * 0.5, (y0 + y1) * 0.5)
        except AttributeError:
            pass
    if not isinstance(record, Mapping):
        raise TypeError(f"record does not expose x0/y0/x1/y1 fields: {record!r}")
    x0 = float(record["x0"])
    y0 = float(record["y0"])
    x1 = float(record["x1"])
    y1 = float(record["y1"])
    return ((x0 + x1) * 0.5, (y0 + y1) * 0.5)


def _part1by1_16(value: int) -> int:
    v = int(value) & 0x0000ffff
    v = (v | (v << 8)) & 0x00ff00ff
    v = (v | (v << 4)) & 0x0f0f0f0f
    v = (v | (v << 2)) & 0x33333333
    v = (v | (v << 1)) & 0x55555555
    return v


def _morton_code_2d_16(ix: int, iy: int) -> int:
    return _part1by1_16(ix) | (_part1by1_16(iy) << 1)
