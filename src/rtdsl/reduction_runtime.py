from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Mapping
from typing import Any


_REDUCE_ROW_OPS = {"any", "count", "sum", "min", "max"}


def _normalize_group_by(group_by: str | Iterable[str] | None) -> tuple[str, ...]:
    if group_by is None:
        return ()
    if isinstance(group_by, str):
        fields = (group_by,)
    else:
        fields = tuple(group_by)
    if any(not isinstance(field, str) or not field for field in fields):
        raise ValueError("reduce_rows group_by fields must be non-empty strings")
    if len(set(fields)) != len(fields):
        raise ValueError("reduce_rows group_by fields must be unique")
    return fields


def _default_output_field(op: str, value: str | None) -> str:
    if op == "count":
        return "count"
    return f"{op}_{value}"


def _validate_reduce_row_args(
    *,
    op: str,
    value: str | None,
    output_field: str | None,
    group_by: tuple[str, ...],
) -> str:
    if op not in _REDUCE_ROW_OPS:
        supported = ", ".join(sorted(_REDUCE_ROW_OPS))
        raise ValueError(f"reduce_rows op must be one of: {supported}")
    if op == "count":
        if value is not None:
            raise ValueError("reduce_rows count does not accept a value field")
    elif not isinstance(value, str) or not value:
        raise ValueError(f"reduce_rows {op} requires a non-empty value field")
    resolved_output = output_field or _default_output_field(op, value)
    if not isinstance(resolved_output, str) or not resolved_output:
        raise ValueError("reduce_rows output_field must be a non-empty string")
    if resolved_output in group_by:
        raise ValueError("reduce_rows output_field must not duplicate a group_by field")
    return resolved_output


def _require_mapping(row: object) -> Mapping[str, Any]:
    if not isinstance(row, Mapping):
        raise TypeError("reduce_rows rows must be mapping objects")
    return row


def _field(row: Mapping[str, Any], name: str) -> Any:
    try:
        return row[name]
    except KeyError as exc:
        raise ValueError(f"reduce_rows row is missing required field: {name}") from exc


def _update_state(op: str, has_value: bool, accumulator: Any, value: Any) -> tuple[bool, Any]:
    if op == "count":
        return True, (0 if accumulator is None else accumulator) + 1
    if op == "any":
        return True, int(bool(accumulator) or bool(value))
    if op == "sum":
        return True, (0 if accumulator is None else accumulator) + value
    if op == "min":
        return True, value if not has_value else min(accumulator, value)
    if op == "max":
        return True, value if not has_value else max(accumulator, value)
    raise AssertionError(f"unreachable reduce_rows op: {op}")


def _identity_for_empty(op: str) -> Any:
    if op == "count":
        return 0
    if op == "any":
        return 0
    if op == "sum":
        return 0
    raise ValueError(f"reduce_rows {op} has no identity for an empty ungrouped input")


def reduce_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    group_by: str | Iterable[str] | None = (),
    op: str,
    value: str | None = None,
    output_field: str | None = None,
) -> tuple[dict[str, Any], ...]:
    """Reduce emitted RTDL rows into deterministic grouped summary rows.

    This is a backend-neutral standard-library helper. It runs in Python over
    already-emitted rows; it is not a native RT traversal or device-side
    reduction contract.
    """

    group_fields = _normalize_group_by(group_by)
    result_field = _validate_reduce_row_args(
        op=op,
        value=value,
        output_field=output_field,
        group_by=group_fields,
    )

    states: dict[tuple[Any, ...], tuple[bool, Any]] = {}
    for raw_row in rows:
        row = _require_mapping(raw_row)
        key = tuple(_field(row, field) for field in group_fields)
        state_has_value, state_accumulator = states.get(key, (False, None))
        row_value = None if op == "count" else _field(row, value or "")
        states[key] = _update_state(op, state_has_value, state_accumulator, row_value)

    if not states and not group_fields:
        return ({result_field: _identity_for_empty(op)},)
    if not states:
        return ()

    output_rows: list[dict[str, Any]] = []
    for key, (_has_value, accumulator) in states.items():
        output_row = {field: key[index] for index, field in enumerate(group_fields)}
        output_row[result_field] = accumulator
        output_rows.append(output_row)
    return tuple(output_rows)
