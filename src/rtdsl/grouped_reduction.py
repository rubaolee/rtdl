from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


GROUPED_REDUCTION_CONTRACT_VERSION = "rtdl.grouped_reduction.v1"
GROUPED_REDUCTION_OUTPUT_MODE_COMPACT_ROWS = "compact_rows"
GROUPED_REDUCTION_OVERFLOW_POLICY_FAIL_CLOSED = "fail_closed"

GROUPED_REDUCTION_OPERATIONS = (
    "group_any",
    "group_count",
    "group_sum_i64",
    "group_sum_f64",
    "group_min_i64",
    "group_max_i64",
    "group_sum_count_i64",
    "group_stats_i64",
)

GROUPED_REDUCTION_VALUE_OPERATIONS = (
    "group_sum_i64",
    "group_sum_f64",
    "group_min_i64",
    "group_max_i64",
    "group_sum_count_i64",
    "group_stats_i64",
)

COLUMNAR_AGGREGATE_TO_GROUPED_REDUCTION = {
    "count": "group_count",
    "sum": "group_sum_i64",
    "min": "group_min_i64",
    "max": "group_max_i64",
    "avg_as_sum_count": "group_sum_count_i64",
}


@dataclass(frozen=True)
class GroupedReductionSpec:
    operation: str
    group_keys: tuple[str, ...]
    value_field: str | None = None
    group_capacity: int | None = None
    output_mode: str = GROUPED_REDUCTION_OUTPUT_MODE_COMPACT_ROWS
    overflow_policy: str = GROUPED_REDUCTION_OVERFLOW_POLICY_FAIL_CLOSED
    contract_version: str = GROUPED_REDUCTION_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if self.operation not in GROUPED_REDUCTION_OPERATIONS:
            raise ValueError(f"unsupported grouped reduction operation: {self.operation}")
        if not self.group_keys:
            raise ValueError("grouped reduction requires at least one group key")
        if len(set(self.group_keys)) != len(self.group_keys):
            raise ValueError("grouped reduction group keys must be unique")
        if self.operation in GROUPED_REDUCTION_VALUE_OPERATIONS and not self.value_field:
            raise ValueError(f"{self.operation} requires a value_field")
        if self.operation not in GROUPED_REDUCTION_VALUE_OPERATIONS and self.value_field is not None:
            raise ValueError(f"{self.operation} does not accept a value_field")
        if self.group_capacity is not None and int(self.group_capacity) <= 0:
            raise ValueError("grouped reduction group_capacity must be positive when provided")
        if self.output_mode != GROUPED_REDUCTION_OUTPUT_MODE_COMPACT_ROWS:
            raise ValueError("grouped reduction currently supports compact_rows output only")
        if self.overflow_policy != GROUPED_REDUCTION_OVERFLOW_POLICY_FAIL_CLOSED:
            raise ValueError("grouped reduction currently supports fail_closed overflow only")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "operation": self.operation,
            "group_keys": self.group_keys,
            "value_field": self.value_field,
            "group_capacity": self.group_capacity,
            "output_mode": self.output_mode,
            "overflow_policy": self.overflow_policy,
            "claim_boundary": (
                "Generic grouped-reduction contract metadata only. It does not authorize "
                "native backend support, public speedup wording, or app-specific engine semantics."
            ),
        }


@dataclass(frozen=True)
class GroupedReductionCapacityStatus:
    group_capacity: int | None
    row_count: int
    required_capacity: int | None = None
    overflowed: bool = False
    overflow_policy: str = GROUPED_REDUCTION_OVERFLOW_POLICY_FAIL_CLOSED

    def __post_init__(self) -> None:
        if self.group_capacity is not None and int(self.group_capacity) <= 0:
            raise ValueError("group_capacity must be positive when provided")
        if int(self.row_count) < 0:
            raise ValueError("row_count must be non-negative")
        if self.required_capacity is not None and int(self.required_capacity) < 0:
            raise ValueError("required_capacity must be non-negative when provided")
        if self.overflow_policy != GROUPED_REDUCTION_OVERFLOW_POLICY_FAIL_CLOSED:
            raise ValueError("grouped reduction currently supports fail_closed overflow only")
        if self.group_capacity is not None and self.required_capacity is not None:
            expected_overflow = int(self.required_capacity) > int(self.group_capacity)
            if bool(self.overflowed) != expected_overflow:
                raise ValueError("overflowed must match required_capacity > group_capacity")
        if self.group_capacity is not None and bool(self.overflowed) and int(self.row_count) != 0:
            raise ValueError("fail-closed grouped reduction overflow must not expose partial rows")

    def raise_if_overflowed(self, *, operation: str) -> None:
        if not self.overflowed:
            return
        raise RuntimeError(
            "grouped reduction "
            f"{operation} overflowed group_capacity={self.group_capacity}; "
            "increase capacity or remap groups before consuming exact rows"
        )

    def to_metadata(self) -> dict[str, Any]:
        return {
            "group_capacity": self.group_capacity,
            "row_count": int(self.row_count),
            "required_capacity": self.required_capacity,
            "overflowed": bool(self.overflowed),
            "overflow_policy": self.overflow_policy,
        }


def normalize_grouped_reduction_spec(
    payload: Mapping[str, Any] | GroupedReductionSpec,
) -> GroupedReductionSpec:
    if isinstance(payload, GroupedReductionSpec):
        return payload
    if not isinstance(payload, Mapping):
        raise ValueError("grouped reduction spec must be a mapping or GroupedReductionSpec")
    raw_group_keys = payload.get("group_keys", ())
    if isinstance(raw_group_keys, str):
        group_keys = (raw_group_keys,)
    else:
        group_keys = tuple(str(value) for value in raw_group_keys)
    raw_value_field = payload.get("value_field")
    raw_group_capacity = payload.get("group_capacity")
    return GroupedReductionSpec(
        operation=str(payload.get("operation", "group_count")),
        group_keys=group_keys,
        value_field=None if raw_value_field is None else str(raw_value_field),
        group_capacity=None if raw_group_capacity is None else int(raw_group_capacity),
        output_mode=str(payload.get("output_mode", GROUPED_REDUCTION_OUTPUT_MODE_COMPACT_ROWS)),
        overflow_policy=str(payload.get("overflow_policy", GROUPED_REDUCTION_OVERFLOW_POLICY_FAIL_CLOSED)),
    )


def grouped_reduction_spec_from_columnar_plan(plan: Mapping[str, Any] | object) -> GroupedReductionSpec:
    aggregate = str(_read_plan_field(plan, "aggregate", "count"))
    if aggregate not in COLUMNAR_AGGREGATE_TO_GROUPED_REDUCTION:
        raise ValueError(f"unsupported columnar aggregate for grouped reduction: {aggregate}")
    value_field = _read_plan_field(plan, "value_field", None)
    raw_group_keys = _read_plan_field(plan, "group_keys", ())
    group_capacity = _read_plan_field(plan, "group_capacity", None)
    return GroupedReductionSpec(
        operation=COLUMNAR_AGGREGATE_TO_GROUPED_REDUCTION[aggregate],
        group_keys=_normalize_group_keys(raw_group_keys),
        value_field=None if value_field is None else str(value_field),
        group_capacity=None if group_capacity is None else int(group_capacity),
    )


def grouped_reduction_contract_metadata(
    *,
    supported_operations: Sequence[str] = GROUPED_REDUCTION_OPERATIONS,
) -> dict[str, Any]:
    normalized_operations = tuple(str(operation) for operation in supported_operations)
    unsupported = tuple(
        operation for operation in normalized_operations if operation not in GROUPED_REDUCTION_OPERATIONS
    )
    if unsupported:
        raise ValueError(f"unsupported grouped reduction operations: {unsupported}")
    return {
        "contract_version": GROUPED_REDUCTION_CONTRACT_VERSION,
        "supported_operations": normalized_operations,
        "output_mode": GROUPED_REDUCTION_OUTPUT_MODE_COMPACT_ROWS,
        "overflow_policy": GROUPED_REDUCTION_OVERFLOW_POLICY_FAIL_CLOSED,
        "capacity_status_fields": (
            "group_capacity",
            "row_count",
            "required_capacity",
            "overflowed",
            "overflow_policy",
        ),
        "claim_boundary": (
            "Shared grouped-reduction substrate contract only. Runtime/native paths must "
            "separately prove backend support and must keep app semantics outside the engine."
        ),
    }


def _read_plan_field(plan: Mapping[str, Any] | object, name: str, default: Any) -> Any:
    if isinstance(plan, Mapping):
        return plan.get(name, default)
    return getattr(plan, name, default)


def _normalize_group_keys(raw_group_keys: object) -> tuple[str, ...]:
    if isinstance(raw_group_keys, str):
        return (raw_group_keys,)
    return tuple(str(value) for value in raw_group_keys)  # type: ignore[arg-type]
