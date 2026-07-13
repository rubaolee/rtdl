"""Generic host-columnar grouped sequence assembly.

This module intentionally contains no application output format rules. It turns
typed column arrays into deterministic grouped sequences that an application can
serialize or post-process however it needs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np


SUPPORTED_GROUP_POLICIES = frozenset({"skip_empty"})
SUPPORTED_OUTPUT_SHAPES = frozenset({"offsets_and_items", "descriptors_and_items", "columnar_records"})
SUPPORTED_ROW_BUFFER_SCHEMAS = frozenset({"rtdl.grouped_output_row_buffer.v1"})


@dataclass(frozen=True)
class GroupedSequenceAssemblyPlan:
    """Declarative grouping/order/payload contract for columnar rows."""

    group_key_columns: tuple[str, ...]
    order_key_columns: tuple[str, ...] = ()
    payload_columns: tuple[str, ...] = ()
    validity_column: str | None = None
    dedupe_key_columns: tuple[str, ...] = ()
    group_policy: str = "skip_empty"
    output_shape: str = "offsets_and_items"


@dataclass(frozen=True)
class GroupedSequenceAssemblyResult:
    """Columnar grouped-sequence output.

    ``group_offsets`` and ``group_lengths`` describe slices into ``item_indices``
    and every array in ``item_columns``.
    """

    group_key_columns: tuple[str, ...]
    group_keys: Mapping[str, np.ndarray]
    group_offsets: np.ndarray
    group_lengths: np.ndarray
    item_indices: np.ndarray
    item_columns: Mapping[str, np.ndarray]
    stats: Mapping[str, int | str | bool]

    @property
    def group_count(self) -> int:
        return int(self.group_offsets.size)

    @property
    def item_count(self) -> int:
        return int(self.item_indices.size)

    def group_slice(self, group_index: int) -> slice:
        start = int(self.group_offsets[group_index])
        stop = start + int(self.group_lengths[group_index])
        return slice(start, stop)


@dataclass(frozen=True)
class GroupedOutputRowBufferSchema:
    """Neutral row-buffer shape for grouped output materialization.

    This schema names only generic column roles. Applications decide how to map
    their domain fields into descriptor and item payload columns before calling
    generic output assembly.
    """

    group_key_columns: tuple[str, ...]
    item_order_columns: tuple[str, ...] = ()
    group_descriptor_columns: tuple[str, ...] = ()
    item_payload_columns: tuple[str, ...] = ()
    validity_column: str | None = None
    dedupe_key_columns: tuple[str, ...] = ()
    schema: str = "rtdl.grouped_output_row_buffer.v1"


@dataclass(frozen=True)
class GroupedOutputRowBuffer:
    """Validated columnar data shape for future output materializers."""

    schema: GroupedOutputRowBufferSchema
    columns: Mapping[str, np.ndarray]
    stats: Mapping[str, int | str | bool]

    @property
    def row_count(self) -> int:
        return int(self.stats["row_count"])

    def assembly_plan(self, *, output_shape: str = "descriptors_and_items") -> GroupedSequenceAssemblyPlan:
        payload_columns = tuple(self.schema.group_descriptor_columns) + tuple(self.schema.item_payload_columns)
        return GroupedSequenceAssemblyPlan(
            group_key_columns=tuple(self.schema.group_key_columns),
            order_key_columns=tuple(self.schema.item_order_columns),
            payload_columns=payload_columns,
            validity_column=self.schema.validity_column,
            dedupe_key_columns=tuple(self.schema.dedupe_key_columns),
            output_shape=output_shape,
        )


@dataclass(frozen=True)
class GroupedOutputMaterializationResult:
    """Columnar descriptors and items for grouped output backends."""

    schema: GroupedOutputRowBufferSchema
    group_keys: Mapping[str, np.ndarray]
    descriptor_columns: Mapping[str, np.ndarray]
    group_offsets: np.ndarray
    group_lengths: np.ndarray
    item_columns: Mapping[str, np.ndarray]
    stats: Mapping[str, int | str | bool]

    @property
    def group_count(self) -> int:
        return int(self.group_offsets.size)

    @property
    def item_count(self) -> int:
        if not self.item_columns:
            return int(self.group_lengths.sum())
        first_column = next(iter(self.item_columns.values()))
        return int(first_column.size)

    def group_slice(self, group_index: int) -> slice:
        start = int(self.group_offsets[group_index])
        stop = start + int(self.group_lengths[group_index])
        return slice(start, stop)


def assemble_grouped_sequences(
    columns: Mapping[str, object],
    plan: GroupedSequenceAssemblyPlan,
) -> GroupedSequenceAssemblyResult:
    """Assemble deterministic grouped sequences from equal-length columns.

    Rows are filtered by ``validity_column`` when provided, stably sorted by
    group keys then order keys, optionally de-duplicated by group keys plus
    dedupe keys, then returned as compact columnar slices.
    """

    _validate_plan(plan)
    arrays = {name: np.asarray(value) for name, value in columns.items()}
    row_count = _validate_columns(arrays)
    required = _required_columns(plan)
    missing = sorted(name for name in required if name not in arrays)
    if missing:
        raise ValueError(f"missing columns for grouped sequence assembly: {missing}")

    if row_count == 0:
        return _empty_result(arrays, plan)

    if plan.validity_column is None:
        valid_indices = np.arange(row_count, dtype=np.int64)
    else:
        validity = np.asarray(arrays[plan.validity_column], dtype=bool)
        valid_indices = np.nonzero(validity)[0].astype(np.int64, copy=False)

    if valid_indices.size == 0:
        return _empty_result(arrays, plan, input_rows=row_count)

    sorted_indices = _sort_indices(arrays, valid_indices, plan)
    item_indices = _dedupe_indices(arrays, sorted_indices, plan)

    if item_indices.size == 0:
        return _empty_result(arrays, plan, input_rows=row_count, valid_rows=int(valid_indices.size))

    group_starts = _group_starts(arrays, item_indices, plan.group_key_columns)
    group_offsets = group_starts.astype(np.int64, copy=False)
    group_ends = np.concatenate((group_offsets[1:], np.asarray([item_indices.size], dtype=np.int64)))
    group_lengths = (group_ends - group_offsets).astype(np.int64, copy=False)
    group_source_indices = item_indices[group_offsets]
    group_keys = {
        name: np.asarray(arrays[name][group_source_indices]).copy()
        for name in plan.group_key_columns
    }
    item_columns = {
        name: np.asarray(arrays[name][item_indices]).copy()
        for name in plan.payload_columns
    }
    stats = {
        "schema": "rtdl.grouped_sequence_assembly.v1",
        "input_rows": int(row_count),
        "valid_rows": int(valid_indices.size),
        "item_rows": int(item_indices.size),
        "group_count": int(group_offsets.size),
        "dedupe_enabled": bool(plan.dedupe_key_columns),
        "group_policy": plan.group_policy,
        "output_shape": plan.output_shape,
    }
    return GroupedSequenceAssemblyResult(
        group_key_columns=tuple(plan.group_key_columns),
        group_keys=group_keys,
        group_offsets=group_offsets.copy(),
        group_lengths=group_lengths.copy(),
        item_indices=item_indices.copy(),
        item_columns=item_columns,
        stats=stats,
    )


def prepare_grouped_output_row_buffer(
    columns: Mapping[str, object],
    schema: GroupedOutputRowBufferSchema,
    *,
    validate_group_descriptors: bool = True,
) -> GroupedOutputRowBuffer:
    """Validate neutral grouped-output columns before materialization.

    The contract deliberately rejects object-dtype columns. Applications must
    map domain state into primitive/NumPy-compatible columns before generic
    output assembly can own it.
    """

    _validate_row_buffer_schema(schema)
    arrays = {name: np.asarray(value) for name, value in columns.items()}
    row_count = _validate_columns(arrays)
    required = _row_buffer_required_columns(schema)
    missing = sorted(name for name in required if name not in arrays)
    if missing:
        raise ValueError(f"missing columns for grouped output row buffer: {missing}")
    _validate_primitive_columns(arrays)
    if validate_group_descriptors and row_count:
        _validate_group_descriptor_invariants(arrays, schema)
    stats = {
        "schema": schema.schema,
        "row_count": int(row_count),
        "column_count": int(len(arrays)),
        "group_key_count": int(len(schema.group_key_columns)),
        "descriptor_column_count": int(len(schema.group_descriptor_columns)),
        "item_payload_column_count": int(len(schema.item_payload_columns)),
        "has_validity": bool(schema.validity_column is not None),
        "dedupe_enabled": bool(schema.dedupe_key_columns),
    }
    return GroupedOutputRowBuffer(schema=schema, columns=arrays, stats=stats)


def assemble_grouped_output_row_buffer(
    row_buffer: GroupedOutputRowBuffer,
    *,
    output_shape: str = "descriptors_and_items",
) -> GroupedSequenceAssemblyResult:
    """Assemble a validated grouped-output row buffer."""

    return assemble_grouped_sequences(row_buffer.columns, row_buffer.assembly_plan(output_shape=output_shape))


def materialize_grouped_output_row_buffer(
    row_buffer: GroupedOutputRowBuffer,
) -> GroupedOutputMaterializationResult:
    """Materialize neutral grouped descriptors and item payload columns.

    This prototype is intentionally format-neutral. It produces one descriptor
    row per group and ordered payload rows per item, leaving final serialization
    to the application.
    """

    assembled = assemble_grouped_output_row_buffer(row_buffer, output_shape="descriptors_and_items")
    descriptor_columns = {
        name: np.asarray(assembled.item_columns[name][assembled.group_offsets]).copy()
        for name in row_buffer.schema.group_descriptor_columns
    }
    item_columns = {
        name: np.asarray(assembled.item_columns[name]).copy()
        for name in row_buffer.schema.item_payload_columns
    }
    stats = dict(assembled.stats)
    stats["schema"] = "rtdl.grouped_output_materialization.v1"
    stats["descriptor_column_count"] = int(len(descriptor_columns))
    stats["item_payload_column_count"] = int(len(item_columns))
    return GroupedOutputMaterializationResult(
        schema=row_buffer.schema,
        group_keys=assembled.group_keys,
        descriptor_columns=descriptor_columns,
        group_offsets=assembled.group_offsets,
        group_lengths=assembled.group_lengths,
        item_columns=item_columns,
        stats=stats,
    )


def assemble_grouped_path_split_records(
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
    """Build neutral grouped records from path chains and ordered split events.

    The operation is intentionally domain-neutral: it knows only about chains,
    base points, ordered split events, optional interval descriptors, and an
    optional validity mask. Applications own all semantic labels and final
    formatting.
    """

    chain_ids_array = np.asarray(chain_ids, dtype=np.int64)
    chain_offsets_array = np.asarray(chain_point_offsets, dtype=np.int64)
    chain_counts_array = np.asarray(chain_point_counts, dtype=np.int64)
    px = np.asarray(point_x, dtype=np.float64)
    py = np.asarray(point_y, dtype=np.float64)
    if not (
        chain_ids_array.ndim
        == chain_offsets_array.ndim
        == chain_counts_array.ndim
        == px.ndim
        == py.ndim
        == 1
    ):
        raise ValueError("path split inputs must be one-dimensional")
    if chain_ids_array.size != chain_offsets_array.size or chain_ids_array.size != chain_counts_array.size:
        raise ValueError("chain id, offset, and count arrays must have the same length")
    if px.size != py.size:
        raise ValueError("point_x and point_y must have the same length")
    if np.unique(chain_ids_array).size != chain_ids_array.size:
        raise ValueError("chain ids must be unique")

    split_arrays = _path_split_event_arrays(
        split_chain_ids=split_chain_ids,
        split_edge_orders=split_edge_orders,
        split_event_orders=split_event_orders,
        split_x=split_x,
        split_y=split_y,
    )
    events_by_chain: dict[int, list[tuple[int, int, float, float]]] = {}
    for index in range(int(split_arrays["chain_id"].size)):
        key = int(split_arrays["chain_id"][index])
        events_by_chain.setdefault(key, []).append(
            (
                int(split_arrays["edge_order"][index]),
                int(split_arrays["event_order"][index]),
                float(split_arrays["x"][index]),
                float(split_arrays["y"][index]),
            )
        )
    for rows in events_by_chain.values():
        rows.sort(key=lambda item: (item[0], item[1]))
    unknown_chain_ids = sorted(set(events_by_chain) - {int(value) for value in chain_ids_array})
    if unknown_chain_ids:
        raise ValueError(f"split events reference unknown chain ids: {unknown_chain_ids}")

    interval_count = int(chain_ids_array.size + split_arrays["chain_id"].size)
    descriptor_arrays = {
        name: np.asarray(values)
        for name, values in (interval_descriptor_columns or {}).items()
    }
    for name, values in descriptor_arrays.items():
        if values.ndim != 1:
            raise ValueError(f"interval descriptor column {name!r} must be one-dimensional")
        if int(values.size) != interval_count:
            raise ValueError(
                f"interval descriptor column {name!r} must have {interval_count} rows"
            )
        if values.dtype == object:
            raise ValueError(f"interval descriptor column {name!r} must not use object dtype")
    if interval_validity is None:
        validity_array = np.ones(interval_count, dtype=bool)
    else:
        validity_array = np.asarray(interval_validity, dtype=bool)
        if validity_array.ndim != 1 or int(validity_array.size) != interval_count:
            raise ValueError("interval_validity must have one row per generated interval")
    if output_group_ids is None:
        group_ids_array = np.arange(1, interval_count + 1, dtype=np.int64)
    else:
        group_ids_array = np.asarray(output_group_ids, dtype=np.int64)
        if group_ids_array.ndim != 1 or int(group_ids_array.size) != interval_count:
            raise ValueError("output_group_ids must have one row per generated interval")

    output_group: list[int] = []
    output_order: list[int] = []
    output_x: list[float] = []
    output_y: list[float] = []
    output_descriptors: dict[str, list[object]] = {name: [] for name in descriptor_arrays}

    def emit_interval(points: list[tuple[float, float]], interval_index: int) -> None:
        if not bool(validity_array[interval_index]):
            return
        cleaned = _dedupe_consecutive_path_points(points) if dedupe_consecutive_points else points
        if not cleaned:
            return
        group_id = int(group_ids_array[interval_index])
        for order, point in enumerate(cleaned):
            output_group.append(group_id)
            output_order.append(order)
            output_x.append(float(point[0]))
            output_y.append(float(point[1]))
            for name, values in descriptor_arrays.items():
                output_descriptors[name].append(values[interval_index])

    interval_index = 0
    for chain_index in range(int(chain_ids_array.size)):
        chain_id = int(chain_ids_array[chain_index])
        point_offset = int(chain_offsets_array[chain_index])
        point_count = int(chain_counts_array[chain_index])
        if point_count <= 0:
            interval_index += 1 + sum(1 for _ in events_by_chain.get(chain_id, ()))
            continue
        if point_offset < 0 or point_offset + point_count > int(px.size):
            raise ValueError("chain point range is outside point arrays")
        if point_count == 1:
            emit_interval([(float(px[point_offset]), float(py[point_offset]))], interval_index)
            interval_index += 1
            continue

        events = events_by_chain.get(chain_id, [])
        events_by_edge: dict[int, list[tuple[int, float, float]]] = {}
        for edge_order, event_order, event_x, event_y in events:
            if edge_order < 0 or edge_order >= point_count - 1:
                raise ValueError("split edge order is outside the chain edge range")
            events_by_edge.setdefault(edge_order, []).append((event_order, event_x, event_y))
        current_points = [(float(px[point_offset]), float(py[point_offset]))]
        for edge_order in range(point_count - 1):
            for _, event_x, event_y in events_by_edge.get(edge_order, ()):
                event_point = (float(event_x), float(event_y))
                current_points.append(event_point)
                emit_interval(current_points, interval_index)
                interval_index += 1
                current_points = [event_point]
            next_point_index = point_offset + edge_order + 1
            current_points.append((float(px[next_point_index]), float(py[next_point_index])))
        emit_interval(current_points, interval_index)
        interval_index += 1

    columns: dict[str, np.ndarray] = {
        "group_id": np.asarray(output_group, dtype=np.int64),
        "item_order": np.asarray(output_order, dtype=np.int64),
        "x": np.asarray(output_x, dtype=np.float64),
        "y": np.asarray(output_y, dtype=np.float64),
    }
    for name, values in output_descriptors.items():
        columns[name] = np.asarray(values, dtype=descriptor_arrays[name].dtype)
    schema = GroupedOutputRowBufferSchema(
        group_key_columns=("group_id",),
        item_order_columns=("item_order",),
        group_descriptor_columns=tuple(descriptor_arrays),
        item_payload_columns=("x", "y"),
    )
    row_buffer = prepare_grouped_output_row_buffer(columns, schema)
    stats = dict(row_buffer.stats)
    stats.update(
        {
            "producer_schema": "rtdl.grouped_path_split_records.v1",
            "chain_count": int(chain_ids_array.size),
            "split_event_count": int(split_arrays["chain_id"].size),
            "interval_count": int(interval_count),
            "emitted_group_count": int(row_buffer.stats["row_count"] and np.unique(columns["group_id"]).size),
            "dedupe_consecutive_points": bool(dedupe_consecutive_points),
        }
    )
    return GroupedOutputRowBuffer(schema=row_buffer.schema, columns=row_buffer.columns, stats=stats)


def _path_split_event_arrays(
    *,
    split_chain_ids: object | None,
    split_edge_orders: object | None,
    split_event_orders: object | None,
    split_x: object | None,
    split_y: object | None,
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
    row_count = _validate_columns(arrays)
    if row_count == 0:
        return arrays
    return arrays


def _dedupe_consecutive_path_points(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if not points:
        return []
    output = [points[0]]
    for point in points[1:]:
        if point != output[-1]:
            output.append(point)
    return output


def _validate_plan(plan: GroupedSequenceAssemblyPlan) -> None:
    if not plan.group_key_columns:
        raise ValueError("grouped sequence assembly requires at least one group key column")
    if plan.group_policy not in SUPPORTED_GROUP_POLICIES:
        raise ValueError(f"unsupported group_policy: {plan.group_policy!r}")
    if plan.output_shape not in SUPPORTED_OUTPUT_SHAPES:
        raise ValueError(f"unsupported output_shape: {plan.output_shape!r}")
    for field_name in ("group_key_columns", "order_key_columns", "payload_columns", "dedupe_key_columns"):
        values = getattr(plan, field_name)
        if len(set(values)) != len(values):
            raise ValueError(f"{field_name} contains duplicate column names")


def _validate_row_buffer_schema(schema: GroupedOutputRowBufferSchema) -> None:
    if schema.schema not in SUPPORTED_ROW_BUFFER_SCHEMAS:
        raise ValueError(f"unsupported grouped output row-buffer schema: {schema.schema!r}")
    if not schema.group_key_columns:
        raise ValueError("grouped output row buffer requires at least one group key column")
    for field_name in (
        "group_key_columns",
        "item_order_columns",
        "group_descriptor_columns",
        "item_payload_columns",
        "dedupe_key_columns",
    ):
        values = getattr(schema, field_name)
        if len(set(values)) != len(values):
            raise ValueError(f"{field_name} contains duplicate column names")
    all_roles: list[str] = []
    for values in (
        schema.group_key_columns,
        schema.item_order_columns,
        schema.group_descriptor_columns,
        schema.item_payload_columns,
        schema.dedupe_key_columns,
    ):
        all_roles.extend(values)
    if schema.validity_column is not None:
        all_roles.append(schema.validity_column)
    duplicate_roles = sorted({name for name in all_roles if all_roles.count(name) > 1})
    if duplicate_roles:
        raise ValueError(f"grouped output row-buffer columns have multiple roles: {duplicate_roles}")


def _validate_columns(arrays: Mapping[str, np.ndarray]) -> int:
    row_count: int | None = None
    for name, value in arrays.items():
        if value.ndim != 1:
            raise ValueError(f"column {name!r} must be one-dimensional")
        if row_count is None:
            row_count = int(value.shape[0])
        elif int(value.shape[0]) != row_count:
            raise ValueError("all grouped sequence columns must have the same length")
    return 0 if row_count is None else row_count


def _validate_primitive_columns(arrays: Mapping[str, np.ndarray]) -> None:
    for name, value in arrays.items():
        if value.dtype == object:
            raise ValueError(f"column {name!r} must not use object dtype")


def _required_columns(plan: GroupedSequenceAssemblyPlan) -> set[str]:
    required = set(plan.group_key_columns)
    required.update(plan.order_key_columns)
    required.update(plan.payload_columns)
    required.update(plan.dedupe_key_columns)
    if plan.validity_column is not None:
        required.add(plan.validity_column)
    return required


def _row_buffer_required_columns(schema: GroupedOutputRowBufferSchema) -> set[str]:
    required = set(schema.group_key_columns)
    required.update(schema.item_order_columns)
    required.update(schema.group_descriptor_columns)
    required.update(schema.item_payload_columns)
    required.update(schema.dedupe_key_columns)
    if schema.validity_column is not None:
        required.add(schema.validity_column)
    return required


def _validate_group_descriptor_invariants(
    arrays: Mapping[str, np.ndarray],
    schema: GroupedOutputRowBufferSchema,
) -> None:
    if not schema.group_descriptor_columns:
        return
    plan = GroupedSequenceAssemblyPlan(
        group_key_columns=tuple(schema.group_key_columns),
        order_key_columns=tuple(schema.item_order_columns),
        payload_columns=tuple(schema.group_descriptor_columns),
        validity_column=schema.validity_column,
    )
    if plan.validity_column is None:
        indices = np.arange(_validate_columns(arrays), dtype=np.int64)
    else:
        indices = np.nonzero(np.asarray(arrays[plan.validity_column], dtype=bool))[0].astype(np.int64, copy=False)
    if indices.size <= 1:
        return
    sorted_indices = _sort_indices(arrays, indices, plan)
    group_starts = _group_starts(arrays, sorted_indices, tuple(schema.group_key_columns))
    group_offsets = group_starts.astype(np.int64, copy=False)
    group_ends = np.concatenate((group_offsets[1:], np.asarray([sorted_indices.size], dtype=np.int64)))
    for start, end in zip(group_offsets, group_ends):
        group_indices = sorted_indices[int(start) : int(end)]
        if group_indices.size <= 1:
            continue
        first = int(group_indices[0])
        rest = group_indices[1:]
        for name in schema.group_descriptor_columns:
            if not np.all(arrays[name][rest] == arrays[name][first]):
                raise ValueError(f"group descriptor column {name!r} changes within a group")


def _sort_indices(
    arrays: Mapping[str, np.ndarray],
    valid_indices: np.ndarray,
    plan: GroupedSequenceAssemblyPlan,
) -> np.ndarray:
    source_order = valid_indices
    key_names = tuple(plan.group_key_columns) + tuple(plan.order_key_columns)
    sort_keys = [np.asarray(arrays[name][valid_indices]) for name in key_names]
    sort_keys.append(source_order)
    order = np.lexsort(tuple(reversed(sort_keys)))
    return valid_indices[order].astype(np.int64, copy=False)


def _dedupe_indices(
    arrays: Mapping[str, np.ndarray],
    sorted_indices: np.ndarray,
    plan: GroupedSequenceAssemblyPlan,
) -> np.ndarray:
    if not plan.dedupe_key_columns or sorted_indices.size <= 1:
        return sorted_indices.astype(np.int64, copy=False)
    key_names = tuple(plan.group_key_columns) + tuple(plan.dedupe_key_columns)
    keep = np.ones(sorted_indices.size, dtype=bool)
    previous = sorted_indices[:-1]
    current = sorted_indices[1:]
    same = np.ones(previous.size, dtype=bool)
    for name in key_names:
        same &= arrays[name][previous] == arrays[name][current]
    keep[1:] = ~same
    return sorted_indices[keep].astype(np.int64, copy=False)


def _group_starts(
    arrays: Mapping[str, np.ndarray],
    item_indices: np.ndarray,
    group_key_columns: tuple[str, ...],
) -> np.ndarray:
    starts = np.zeros(item_indices.size, dtype=bool)
    starts[0] = True
    previous = item_indices[:-1]
    current = item_indices[1:]
    same_group = np.ones(previous.size, dtype=bool)
    for name in group_key_columns:
        same_group &= arrays[name][previous] == arrays[name][current]
    starts[1:] = ~same_group
    return np.nonzero(starts)[0].astype(np.int64, copy=False)


def _empty_result(
    arrays: Mapping[str, np.ndarray],
    plan: GroupedSequenceAssemblyPlan,
    *,
    input_rows: int | None = None,
    valid_rows: int = 0,
) -> GroupedSequenceAssemblyResult:
    row_count = _validate_columns(arrays) if input_rows is None else input_rows
    group_keys = {
        name: np.asarray(arrays[name][:0]).copy()
        for name in plan.group_key_columns
        if name in arrays
    }
    item_columns = {
        name: np.asarray(arrays[name][:0]).copy()
        for name in plan.payload_columns
        if name in arrays
    }
    return GroupedSequenceAssemblyResult(
        group_key_columns=tuple(plan.group_key_columns),
        group_keys=group_keys,
        group_offsets=np.asarray([], dtype=np.int64),
        group_lengths=np.asarray([], dtype=np.int64),
        item_indices=np.asarray([], dtype=np.int64),
        item_columns=item_columns,
        stats={
            "schema": "rtdl.grouped_sequence_assembly.v1",
            "input_rows": int(row_count),
            "valid_rows": int(valid_rows),
            "item_rows": 0,
            "group_count": 0,
            "dedupe_enabled": bool(plan.dedupe_key_columns),
            "group_policy": plan.group_policy,
            "output_shape": plan.output_shape,
        },
    )


__all__ = [
    "GroupedOutputMaterializationResult",
    "GroupedOutputRowBuffer",
    "GroupedOutputRowBufferSchema",
    "GroupedSequenceAssemblyPlan",
    "GroupedSequenceAssemblyResult",
    "assemble_grouped_path_split_records",
    "assemble_grouped_output_row_buffer",
    "assemble_grouped_sequences",
    "materialize_grouped_output_row_buffer",
    "prepare_grouped_output_row_buffer",
]
