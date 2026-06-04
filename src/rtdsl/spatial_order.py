from __future__ import annotations

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
    if mode == "x_then_y":
        return tuple(sorted(point_tuple, key=lambda point: (*_record_xy(point), _record_id(point))))
    if mode == "y_then_x":
        return tuple(sorted(point_tuple, key=lambda point: (_record_xy(point)[1], _record_xy(point)[0], _record_id(point))))

    xs_ys = tuple(_record_xy(point) for point in point_tuple)
    min_x = min(x for x, _ in xs_ys)
    max_x = max(x for x, _ in xs_ys)
    min_y = min(y for _, y in xs_ys)
    max_y = max(y for _, y in xs_ys)
    span_x = max(max_x - min_x, 1.0e-30)
    span_y = max(max_y - min_y, 1.0e-30)

    def morton_key(point: object) -> tuple[int, int]:
        x, y = _record_xy(point)
        ix = max(0, min(65535, int(((x - min_x) / span_x) * 65535.0)))
        iy = max(0, min(65535, int(((y - min_y) / span_y) * 65535.0)))
        return (_morton_code_2d_16(ix, iy), _record_id(point))

    return tuple(sorted(point_tuple, key=morton_key))


def spatial_order_segments_2d(segments: Iterable[object], mode: str = "morton_xy") -> tuple[object, ...]:
    """Return segments in a deterministic centroid-locality order without changing IDs."""

    if mode not in SPATIAL_SEGMENT_ORDER_MODES_2D:
        raise ValueError("mode must be one of: natural, x_then_y, y_then_x, morton_xy")
    segment_tuple = tuple(segments)
    if mode == "natural" or not segment_tuple:
        return segment_tuple
    if mode == "x_then_y":
        return tuple(sorted(segment_tuple, key=lambda segment: (*_segment_centroid_xy(segment), _record_id(segment))))
    if mode == "y_then_x":
        return tuple(
            sorted(
                segment_tuple,
                key=lambda segment: (
                    _segment_centroid_xy(segment)[1],
                    _segment_centroid_xy(segment)[0],
                    _record_id(segment),
                ),
            )
        )

    centroids = tuple(_segment_centroid_xy(segment) for segment in segment_tuple)
    min_x = min(x for x, _ in centroids)
    max_x = max(x for x, _ in centroids)
    min_y = min(y for _, y in centroids)
    max_y = max(y for _, y in centroids)
    span_x = max(max_x - min_x, 1.0e-30)
    span_y = max(max_y - min_y, 1.0e-30)

    def morton_key(segment: object) -> tuple[int, int]:
        x, y = _segment_centroid_xy(segment)
        ix = max(0, min(65535, int(((x - min_x) / span_x) * 65535.0)))
        iy = max(0, min(65535, int(((y - min_y) / span_y) * 65535.0)))
        return (_morton_code_2d_16(ix, iy), _record_id(segment))

    return tuple(sorted(segment_tuple, key=morton_key))


def _record_id(record: object) -> int:
    if isinstance(record, Mapping):
        return int(record["id"])
    if hasattr(record, "id"):
        return int(getattr(record, "id"))
    raise TypeError(f"record does not expose an id field: {record!r}")


def _record_xy(record: object) -> tuple[float, float]:
    if isinstance(record, Mapping):
        return float(record["x"]), float(record["y"])
    if hasattr(record, "x") and hasattr(record, "y"):
        return float(getattr(record, "x")), float(getattr(record, "y"))
    raise TypeError(f"record does not expose x/y fields: {record!r}")


def _segment_centroid_xy(record: object) -> tuple[float, float]:
    if isinstance(record, Mapping):
        x0 = float(record["x0"])
        y0 = float(record["y0"])
        x1 = float(record["x1"])
        y1 = float(record["y1"])
    elif all(hasattr(record, name) for name in ("x0", "y0", "x1", "y1")):
        x0 = float(getattr(record, "x0"))
        y0 = float(getattr(record, "y0"))
        x1 = float(getattr(record, "x1"))
        y1 = float(getattr(record, "y1"))
    else:
        raise TypeError(f"record does not expose x0/y0/x1/y1 fields: {record!r}")
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
