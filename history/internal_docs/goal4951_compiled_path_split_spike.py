"""Goal4951 internal compiled path-split spike.

This file is an internal experiment, not a public API. It compiles the neutral
path-split row expansion step and compares against the existing Python generic
path-split implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np

from rtdsl.output_assembly import GroupedOutputRowBuffer
from rtdsl.output_assembly import GroupedOutputRowBufferSchema
from rtdsl.output_assembly import prepare_grouped_output_row_buffer

try:  # pragma: no cover - availability depends on the execution host.
    from numba import njit

    NUMBA_AVAILABLE = True
except Exception:  # pragma: no cover
    njit = None
    NUMBA_AVAILABLE = False


@dataclass(frozen=True)
class CompiledPathSplitStats:
    input_chain_count: int
    input_point_count: int
    split_event_count: int
    interval_count: int
    emitted_row_count: int
    emitted_group_count: int


def assemble_compiled_path_split_records(
    *,
    chain_ids: object,
    chain_point_offsets: object,
    chain_point_counts: object,
    point_x: object,
    point_y: object,
    split_chain_ids: object | None = None,
    split_edge_orders: object | None = None,
    split_event_orders: object | None = None,
    split_x: object | None = None,
    split_y: object | None = None,
    interval_descriptor_columns: Mapping[str, object] | None = None,
    interval_validity: object | None = None,
    output_group_ids: object | None = None,
    dedupe_consecutive_points: bool = True,
) -> GroupedOutputRowBuffer:
    """Assemble neutral path-split rows with a compiled numeric core."""

    if not NUMBA_AVAILABLE:
        raise RuntimeError("Goal4951 compiled path-split spike requires numba")

    chain_ids_array = np.asarray(chain_ids, dtype=np.int64)
    chain_offsets_array = np.asarray(chain_point_offsets, dtype=np.int64)
    chain_counts_array = np.asarray(chain_point_counts, dtype=np.int64)
    px = np.asarray(point_x, dtype=np.float64)
    py = np.asarray(point_y, dtype=np.float64)
    _validate_base_arrays(chain_ids_array, chain_offsets_array, chain_counts_array, px, py)

    split_arrays = _split_arrays(
        split_chain_ids=split_chain_ids,
        split_edge_orders=split_edge_orders,
        split_event_orders=split_event_orders,
        split_x=split_x,
        split_y=split_y,
    )
    order = np.lexsort(
        (
            split_arrays["event_order"],
            split_arrays["edge_order"],
            split_arrays["chain_id"],
        )
    )
    sorted_chain = np.asarray(split_arrays["chain_id"][order], dtype=np.int64)
    sorted_edge = np.asarray(split_arrays["edge_order"][order], dtype=np.int64)
    sorted_event_order = np.asarray(split_arrays["event_order"][order], dtype=np.int64)
    sorted_x = np.asarray(split_arrays["x"][order], dtype=np.float64)
    sorted_y = np.asarray(split_arrays["y"][order], dtype=np.float64)

    event_starts = np.empty(chain_ids_array.size, dtype=np.int64)
    event_stops = np.empty(chain_ids_array.size, dtype=np.int64)
    for index, chain_id in enumerate(chain_ids_array):
        event_starts[index] = int(np.searchsorted(sorted_chain, chain_id, side="left"))
        event_stops[index] = int(np.searchsorted(sorted_chain, chain_id, side="right"))
    if sorted_chain.size:
        known = set(int(value) for value in chain_ids_array)
        unknown = sorted(set(int(value) for value in sorted_chain) - known)
        if unknown:
            raise ValueError(f"split events reference unknown chain ids: {unknown}")
    _validate_split_events(
        chain_ids_array,
        chain_counts_array,
        sorted_chain,
        sorted_edge,
    )
    scratch_capacity = _scratch_capacity(chain_counts_array, sorted_chain)

    interval_count = int(chain_ids_array.size + sorted_chain.size)
    validity = (
        np.ones(interval_count, dtype=np.bool_)
        if interval_validity is None
        else np.asarray(interval_validity, dtype=np.bool_)
    )
    if validity.ndim != 1 or int(validity.size) != interval_count:
        raise ValueError("interval_validity must have one row per generated interval")
    group_ids = (
        np.arange(1, interval_count + 1, dtype=np.int64)
        if output_group_ids is None
        else np.asarray(output_group_ids, dtype=np.int64)
    )
    if group_ids.ndim != 1 or int(group_ids.size) != interval_count:
        raise ValueError("output_group_ids must have one row per generated interval")

    emitted_count = _count_compiled_path_split_rows(
        chain_offsets_array,
        chain_counts_array,
        px,
        py,
        sorted_edge,
        sorted_x,
        sorted_y,
        event_starts,
        event_stops,
        validity,
        bool(dedupe_consecutive_points),
        int(scratch_capacity),
    )
    out_group = np.empty(emitted_count, dtype=np.int64)
    out_order = np.empty(emitted_count, dtype=np.int64)
    out_interval = np.empty(emitted_count, dtype=np.int64)
    out_x = np.empty(emitted_count, dtype=np.float64)
    out_y = np.empty(emitted_count, dtype=np.float64)
    written = _fill_compiled_path_split_rows(
        chain_offsets_array,
        chain_counts_array,
        px,
        py,
        sorted_edge,
        sorted_x,
        sorted_y,
        event_starts,
        event_stops,
        validity,
        group_ids,
        bool(dedupe_consecutive_points),
        int(scratch_capacity),
        out_group,
        out_order,
        out_interval,
        out_x,
        out_y,
    )
    if int(written) != int(emitted_count):
        raise RuntimeError(f"compiled path-split row count mismatch: {written} != {emitted_count}")

    descriptor_arrays = {
        name: np.asarray(values)
        for name, values in (interval_descriptor_columns or {}).items()
    }
    for name, values in descriptor_arrays.items():
        if values.ndim != 1 or int(values.size) != interval_count:
            raise ValueError(f"interval descriptor column {name!r} must have {interval_count} rows")
        if values.dtype == object:
            raise ValueError(f"interval descriptor column {name!r} must not use object dtype")

    columns: dict[str, np.ndarray] = {
        "group_id": out_group,
        "item_order": out_order,
        "x": out_x,
        "y": out_y,
    }
    for name, values in descriptor_arrays.items():
        columns[name] = np.asarray(values[out_interval], dtype=values.dtype)
    schema = GroupedOutputRowBufferSchema(
        group_key_columns=("group_id",),
        item_order_columns=("item_order",),
        group_descriptor_columns=tuple(descriptor_arrays),
        item_payload_columns=("x", "y"),
    )
    row_buffer = prepare_grouped_output_row_buffer(columns, schema)
    stats = dict(row_buffer.stats)
    emitted_group_count = int(np.unique(out_group).size) if out_group.size else 0
    stats.update(
        {
            "producer_schema": "rtdl.compiled_grouped_path_split_records.v1",
            "chain_count": int(chain_ids_array.size),
            "split_event_count": int(sorted_chain.size),
            "interval_count": int(interval_count),
            "emitted_group_count": emitted_group_count,
            "dedupe_consecutive_points": bool(dedupe_consecutive_points),
            "compiled": True,
        }
    )
    return GroupedOutputRowBuffer(schema=row_buffer.schema, columns=row_buffer.columns, stats=stats)


def _validate_base_arrays(chain_ids, chain_offsets, chain_counts, px, py) -> None:
    if not (chain_ids.ndim == chain_offsets.ndim == chain_counts.ndim == px.ndim == py.ndim == 1):
        raise ValueError("path split inputs must be one-dimensional")
    if chain_ids.size != chain_offsets.size or chain_ids.size != chain_counts.size:
        raise ValueError("chain id, offset, and count arrays must have the same length")
    if px.size != py.size:
        raise ValueError("point_x and point_y must have the same length")
    if np.unique(chain_ids).size != chain_ids.size:
        raise ValueError("chain ids must be unique")


def _split_arrays(
    *,
    split_chain_ids,
    split_edge_orders,
    split_event_orders,
    split_x,
    split_y,
) -> dict[str, np.ndarray]:
    values = (split_chain_ids, split_edge_orders, split_event_orders, split_x, split_y)
    if all(value is None for value in values):
        return {
            "chain_id": np.asarray([], dtype=np.int64),
            "edge_order": np.asarray([], dtype=np.int64),
            "event_order": np.asarray([], dtype=np.int64),
            "x": np.asarray([], dtype=np.float64),
            "y": np.asarray([], dtype=np.float64),
        }
    if any(value is None for value in values):
        raise ValueError("all split event columns must be provided together")
    arrays = {
        "chain_id": np.asarray(split_chain_ids, dtype=np.int64),
        "edge_order": np.asarray(split_edge_orders, dtype=np.int64),
        "event_order": np.asarray(split_event_orders, dtype=np.int64),
        "x": np.asarray(split_x, dtype=np.float64),
        "y": np.asarray(split_y, dtype=np.float64),
    }
    sizes = {int(value.size) for value in arrays.values()}
    if len(sizes) != 1:
        raise ValueError("split event columns must have equal length")
    return arrays


def _validate_split_events(chain_ids, chain_counts, sorted_chain, sorted_edge) -> None:
    chain_counts_by_id = {
        int(chain_id): int(chain_counts[index])
        for index, chain_id in enumerate(chain_ids)
    }
    for chain_id, edge_order in zip(sorted_chain, sorted_edge):
        chain_count = chain_counts_by_id[int(chain_id)]
        if chain_count < 2:
            raise ValueError("split events require chains with at least two points")
        if int(edge_order) < 0 or int(edge_order) >= chain_count - 1:
            raise ValueError(
                f"split edge order {int(edge_order)} is outside chain {int(chain_id)}"
            )


def _scratch_capacity(chain_counts, sorted_chain) -> int:
    if chain_counts.size == 0:
        return 1
    # Each temporary interval contains a run of base points plus inserted events.
    # A conservative per-call bound keeps the compiled core generic and prevents
    # fixed-size scratch overflow on long inputs.
    max_base = int(np.max(chain_counts))
    return max(1, max_base + int(sorted_chain.size) + 2)


if NUMBA_AVAILABLE:

    @njit(cache=True)
    def _same_point(ax, ay, bx, by):
        return ax == bx and ay == by

    @njit(cache=True)
    def _count_emit(points_x, points_y, count, dedupe):
        if count <= 0:
            return 0
        if not dedupe:
            return count
        output = 1
        last_x = points_x[0]
        last_y = points_y[0]
        for index in range(1, count):
            if not _same_point(points_x[index], points_y[index], last_x, last_y):
                output += 1
                last_x = points_x[index]
                last_y = points_y[index]
        return output

    @njit(cache=True)
    def _write_emit(points_x, points_y, count, dedupe, group_id, interval_index, write_index, out_group, out_order, out_interval, out_x, out_y):
        order = 0
        if count <= 0:
            return write_index
        last_x = points_x[0]
        last_y = points_y[0]
        out_group[write_index] = group_id
        out_order[write_index] = order
        out_interval[write_index] = interval_index
        out_x[write_index] = last_x
        out_y[write_index] = last_y
        write_index += 1
        order += 1
        for index in range(1, count):
            current_x = points_x[index]
            current_y = points_y[index]
            if dedupe and _same_point(current_x, current_y, last_x, last_y):
                continue
            out_group[write_index] = group_id
            out_order[write_index] = order
            out_interval[write_index] = interval_index
            out_x[write_index] = current_x
            out_y[write_index] = current_y
            write_index += 1
            order += 1
            last_x = current_x
            last_y = current_y
        return write_index

    @njit(cache=True)
    def _count_compiled_path_split_rows(
        chain_offsets,
        chain_counts,
        px,
        py,
        event_edges,
        event_x,
        event_y,
        event_starts,
        event_stops,
        validity,
        dedupe,
        scratch_capacity,
    ):
        total = 0
        interval_index = 0
        scratch_x = np.empty(scratch_capacity, dtype=np.float64)
        scratch_y = np.empty(scratch_capacity, dtype=np.float64)
        for chain_index in range(chain_offsets.shape[0]):
            point_offset = int(chain_offsets[chain_index])
            point_count = int(chain_counts[chain_index])
            event_cursor = int(event_starts[chain_index])
            event_stop = int(event_stops[chain_index])
            if point_count <= 0:
                interval_index += 1 + (event_stop - event_cursor)
                continue
            if point_count == 1:
                if validity[interval_index]:
                    total += 1
                interval_index += 1
                continue
            current_count = 1
            scratch_x[0] = px[point_offset]
            scratch_y[0] = py[point_offset]
            for edge_order in range(point_count - 1):
                while event_cursor < event_stop and int(event_edges[event_cursor]) == edge_order:
                    scratch_x[current_count] = event_x[event_cursor]
                    scratch_y[current_count] = event_y[event_cursor]
                    current_count += 1
                    if validity[interval_index]:
                        total += _count_emit(scratch_x, scratch_y, current_count, dedupe)
                    interval_index += 1
                    scratch_x[0] = event_x[event_cursor]
                    scratch_y[0] = event_y[event_cursor]
                    current_count = 1
                    event_cursor += 1
                next_point = point_offset + edge_order + 1
                scratch_x[current_count] = px[next_point]
                scratch_y[current_count] = py[next_point]
                current_count += 1
            if validity[interval_index]:
                total += _count_emit(scratch_x, scratch_y, current_count, dedupe)
            interval_index += 1
        return total

    @njit(cache=True)
    def _fill_compiled_path_split_rows(
        chain_offsets,
        chain_counts,
        px,
        py,
        event_edges,
        event_x,
        event_y,
        event_starts,
        event_stops,
        validity,
        group_ids,
        dedupe,
        scratch_capacity,
        out_group,
        out_order,
        out_interval,
        out_x,
        out_y,
    ):
        write_index = 0
        interval_index = 0
        scratch_x = np.empty(scratch_capacity, dtype=np.float64)
        scratch_y = np.empty(scratch_capacity, dtype=np.float64)
        for chain_index in range(chain_offsets.shape[0]):
            point_offset = int(chain_offsets[chain_index])
            point_count = int(chain_counts[chain_index])
            event_cursor = int(event_starts[chain_index])
            event_stop = int(event_stops[chain_index])
            if point_count <= 0:
                interval_index += 1 + (event_stop - event_cursor)
                continue
            if point_count == 1:
                if validity[interval_index]:
                    out_group[write_index] = group_ids[interval_index]
                    out_order[write_index] = 0
                    out_interval[write_index] = interval_index
                    out_x[write_index] = px[point_offset]
                    out_y[write_index] = py[point_offset]
                    write_index += 1
                interval_index += 1
                continue
            current_count = 1
            scratch_x[0] = px[point_offset]
            scratch_y[0] = py[point_offset]
            for edge_order in range(point_count - 1):
                while event_cursor < event_stop and int(event_edges[event_cursor]) == edge_order:
                    scratch_x[current_count] = event_x[event_cursor]
                    scratch_y[current_count] = event_y[event_cursor]
                    current_count += 1
                    if validity[interval_index]:
                        write_index = _write_emit(
                            scratch_x,
                            scratch_y,
                            current_count,
                            dedupe,
                            group_ids[interval_index],
                            interval_index,
                            write_index,
                            out_group,
                            out_order,
                            out_interval,
                            out_x,
                            out_y,
                        )
                    interval_index += 1
                    scratch_x[0] = event_x[event_cursor]
                    scratch_y[0] = event_y[event_cursor]
                    current_count = 1
                    event_cursor += 1
                next_point = point_offset + edge_order + 1
                scratch_x[current_count] = px[next_point]
                scratch_y[current_count] = py[next_point]
                current_count += 1
            if validity[interval_index]:
                write_index = _write_emit(
                    scratch_x,
                    scratch_y,
                    current_count,
                    dedupe,
                    group_ids[interval_index],
                    interval_index,
                    write_index,
                    out_group,
                    out_order,
                    out_interval,
                    out_x,
                    out_y,
                )
            interval_index += 1
        return write_index


__all__ = [
    "CompiledPathSplitStats",
    "NUMBA_AVAILABLE",
    "assemble_compiled_path_split_records",
]
