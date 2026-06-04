from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Mapping
from dataclasses import dataclass

from .spatial_order import SPATIAL_SEGMENT_ORDER_MODES_2D
from .spatial_order import _numpy_morton_codes_2d_16


@dataclass(frozen=True)
class SegmentColumns2D:
    """Columnar 2-D segment records with caller IDs preserved."""

    ids: object
    x0: object
    y0: object
    x1: object
    y1: object
    count: int
    order_mode: str = "natural"
    owner: object | None = None


def segment_columns_2d(
    records: Iterable[object] | SegmentColumns2D | None = None,
    *,
    ids=None,
    x0=None,
    y0=None,
    x1=None,
    y1=None,
    order_mode: str = "natural",
) -> SegmentColumns2D:
    """Normalize 2-D segment records or columns into a reusable column batch."""

    if order_mode not in SPATIAL_SEGMENT_ORDER_MODES_2D:
        raise ValueError("order_mode must be one of: natural, x_then_y, y_then_x, morton_xy")
    np = _require_numpy()
    if isinstance(records, SegmentColumns2D):
        arrays = (
            np.asarray(records.ids, dtype=np.int64),
            np.asarray(records.x0, dtype=np.float64),
            np.asarray(records.y0, dtype=np.float64),
            np.asarray(records.x1, dtype=np.float64),
            np.asarray(records.y1, dtype=np.float64),
        )
    elif records is not None:
        if isinstance(records, (str, bytes)):
            raise ValueError("segment records must be an iterable of records")
        record_tuple = tuple(records)
        arrays = _segment_record_arrays_one_pass(record_tuple, np)
    else:
        if any(value is None for value in (ids, x0, y0, x1, y1)):
            raise ValueError("segment column inputs require ids, x0, y0, x1, and y1")
        arrays = (
            np.asarray(ids, dtype=np.int64),
            np.asarray(x0, dtype=np.float64),
            np.asarray(y0, dtype=np.float64),
            np.asarray(x1, dtype=np.float64),
            np.asarray(y1, dtype=np.float64),
        )
    _validate_segment_arrays(arrays)
    if order_mode != "natural":
        arrays = _ordered_segment_arrays(arrays, order_mode, np)
    return SegmentColumns2D(
        ids=arrays[0],
        x0=arrays[1],
        y0=arrays[2],
        x1=arrays[3],
        y1=arrays[4],
        count=int(arrays[0].size),
        order_mode=order_mode,
        owner=records if isinstance(records, SegmentColumns2D) else None,
    )


def segment_columns_with_ids(columns: SegmentColumns2D, ids) -> SegmentColumns2D:
    """Return a column batch with replacement caller IDs and shared geometry columns."""

    np = _require_numpy()
    replacement_ids = np.asarray(ids, dtype=np.int64)
    if replacement_ids.ndim != 1 or int(replacement_ids.size) != int(columns.count):
        raise ValueError("replacement ids must be one-dimensional and match the segment count")
    return SegmentColumns2D(
        ids=replacement_ids,
        x0=columns.x0,
        y0=columns.y0,
        x1=columns.x1,
        y1=columns.y1,
        count=int(columns.count),
        order_mode=columns.order_mode,
        owner=columns,
    )


def _ordered_segment_arrays(arrays, order_mode: str, np):
    ids, x0, y0, x1, y1 = arrays
    if int(ids.size) == 0:
        return arrays
    cx = (x0 + x1) * 0.5
    cy = (y0 + y1) * 0.5
    if order_mode == "x_then_y":
        order = np.lexsort((ids.astype(np.uint64), cy, cx))
    elif order_mode == "y_then_x":
        order = np.lexsort((ids.astype(np.uint64), cx, cy))
    else:
        order = np.lexsort((ids.astype(np.uint64), _numpy_morton_codes_2d_16(cx, cy, np)))
    return tuple(array[order] for array in arrays)


def _segment_record_arrays_one_pass(record_tuple, np):
    count = len(record_tuple)
    ids = np.empty(count, dtype=np.int64)
    x0 = np.empty(count, dtype=np.float64)
    y0 = np.empty(count, dtype=np.float64)
    x1 = np.empty(count, dtype=np.float64)
    y1 = np.empty(count, dtype=np.float64)
    for index, record in enumerate(record_tuple):
        if isinstance(record, Mapping):
            segment_id = record["id"]
            sx0 = record["x0"]
            sy0 = record["y0"]
            sx1 = record["x1"]
            sy1 = record["y1"]
        else:
            try:
                segment_id = record.id
                sx0 = record.x0
                sy0 = record.y0
                sx1 = record.x1
                sy1 = record.y1
            except AttributeError:
                segment_id = _segment_field(record, "id")
                sx0 = _segment_field(record, "x0")
                sy0 = _segment_field(record, "y0")
                sx1 = _segment_field(record, "x1")
                sy1 = _segment_field(record, "y1")
        ids[index] = int(segment_id)
        x0[index] = float(sx0)
        y0[index] = float(sy0)
        x1[index] = float(sx1)
        y1[index] = float(sy1)
    return ids, x0, y0, x1, y1


def _validate_segment_arrays(arrays) -> None:
    lengths = []
    for array in arrays:
        if getattr(array, "ndim", None) != 1:
            raise ValueError("segment columns must be one-dimensional")
        lengths.append(int(array.size))
    if len(set(lengths)) != 1:
        raise ValueError("segment columns must have identical lengths")


def _segment_field(record: object, field_name: str):
    if not isinstance(record, Mapping):
        try:
            return getattr(record, field_name)
        except AttributeError:
            pass
    if isinstance(record, Mapping):
        return record[field_name]
    raise TypeError(f"segment record does not expose {field_name!r}: {record!r}")


def _require_numpy():
    try:
        import numpy as np
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("segment_columns_2d requires numpy") from exc
    return np


__all__ = ["SegmentColumns2D", "segment_columns_2d", "segment_columns_with_ids"]
