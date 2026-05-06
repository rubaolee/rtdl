from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Mapping
from numbers import Integral
from numbers import Real
from typing import Any


_REDUCE_ROW_OPS = {"any", "count", "sum", "min", "max"}
V1_5_GENERIC_SCALAR_REDUCTION_PRIMITIVES = (
    "COUNT_HITS",
    "REDUCE_FLOAT(MIN)",
    "REDUCE_FLOAT(MAX)",
    "REDUCE_FLOAT(SUM)",
    "REDUCE_INT(COUNT)",
    "REDUCE_INT(SUM)",
)
_FLOAT_REDUCTION_OPS = {
    "REDUCE_FLOAT(MIN)": "min",
    "REDUCE_FLOAT(MAX)": "max",
    "REDUCE_FLOAT(SUM)": "sum",
}


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


def _validate_scalar_reduction_primitive(summary_primitive: str) -> str:
    if summary_primitive not in V1_5_GENERIC_SCALAR_REDUCTION_PRIMITIVES:
        supported = ", ".join(V1_5_GENERIC_SCALAR_REDUCTION_PRIMITIVES)
        raise ValueError(f"generic scalar reduction summary_primitive must be one of: {supported}")
    return summary_primitive


def _validate_optional_field(name: str | None, *, parameter: str) -> str | None:
    if name is None:
        return None
    if not isinstance(name, str) or not name:
        raise ValueError(f"generic scalar reduction {parameter} must be a non-empty string")
    return name


def _as_float(value: Any, *, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"generic scalar reduction field {field} must contain real numeric values")
    return float(value)


def _as_int(value: Any, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"generic scalar reduction field {field} must contain integer values")
    return int(value)


def _reduce_float_values(values: tuple[float, ...], *, primitive: str) -> float:
    if primitive == "REDUCE_FLOAT(SUM)":
        return float(sum(values))
    if not values:
        raise ValueError(f"generic scalar reduction {primitive} has no identity for an empty input")
    if primitive == "REDUCE_FLOAT(MIN)":
        return min(values)
    if primitive == "REDUCE_FLOAT(MAX)":
        return max(values)
    raise AssertionError(f"unreachable float reduction primitive: {primitive}")


def _scalar_result_layout(summary_primitive: str) -> str:
    if summary_primitive == "COUNT_HITS":
        return "scalar_int64_hit_count"
    if summary_primitive == "REDUCE_INT(COUNT)":
        return "scalar_int64_count"
    if summary_primitive == "REDUCE_INT(SUM)":
        return "scalar_int64_sum"
    if summary_primitive.startswith("REDUCE_FLOAT"):
        return f"scalar_float64_{_FLOAT_REDUCTION_OPS[summary_primitive]}"
    raise AssertionError(f"unreachable scalar reduction primitive: {summary_primitive}")


def run_generic_scalar_reduction(
    rows: Iterable[Mapping[str, Any]],
    *,
    summary_primitive: str,
    value_field: str | None = None,
    hit_field: str = "any_hit",
) -> dict[str, Any]:
    """Run an app-name-free v1.5 scalar summary over already-emitted rows.

    This helper standardizes stable scalar primitive names and result layouts.
    It is intentionally backend-neutral Python control code and does not claim
    native backend acceleration by itself.
    """

    primitive = _validate_scalar_reduction_primitive(summary_primitive)
    normalized_value_field = _validate_optional_field(value_field, parameter="value_field")
    normalized_hit_field = _validate_optional_field(hit_field, parameter="hit_field")
    if normalized_hit_field is None:
        raise ValueError("generic scalar reduction hit_field must be a non-empty string")

    normalized_rows = tuple(_require_mapping(row) for row in rows)
    if primitive == "COUNT_HITS":
        if normalized_value_field is not None:
            raise ValueError("COUNT_HITS does not accept value_field")
        result = sum(1 for row in normalized_rows if bool(_field(row, normalized_hit_field)))
        dtype = "int64"
        input_field = normalized_hit_field
    elif primitive == "REDUCE_INT(COUNT)":
        if normalized_value_field is not None:
            raise ValueError("REDUCE_INT(COUNT) does not accept value_field")
        result = len(normalized_rows)
        dtype = "int64"
        input_field = None
    elif primitive == "REDUCE_INT(SUM)":
        if normalized_value_field is None:
            raise ValueError("REDUCE_INT(SUM) requires value_field")
        result = sum(_as_int(_field(row, normalized_value_field), field=normalized_value_field) for row in normalized_rows)
        dtype = "int64"
        input_field = normalized_value_field
    else:
        if normalized_value_field is None:
            raise ValueError(f"{primitive} requires value_field")
        values = tuple(_as_float(_field(row, normalized_value_field), field=normalized_value_field) for row in normalized_rows)
        result = _reduce_float_values(values, primitive=primitive)
        dtype = "float64"
        input_field = normalized_value_field

    return {
        "summary_primitive": primitive,
        "result_layout": _scalar_result_layout(primitive),
        "dtype": dtype,
        "row_count": len(normalized_rows),
        "input_field": input_field,
        "result": result,
        "claim_boundary": (
            "Generic v1.5 scalar reduction primitive over already-emitted rows; "
            "backend-neutral Python helper only, not native backend acceleration "
            "or public speedup wording."
        ),
    }


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
