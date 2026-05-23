from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .db_reference import PredicateClause
from .db_reference import _normalize_predicate_clause
from .grouped_reduction import GroupedReductionSpec
from .grouped_reduction import grouped_reduction_spec_from_columnar_plan

UINT32_MAX = 0xFFFFFFFF
SUPPORTED_AGGREGATES = ("count", "sum", "min", "max", "avg_as_sum_count")
NATIVE_COLUMNAR_COUNT_SUM_BACKENDS = ("embree", "optix")
PARTNER_RESIDENT_COLUMNAR_I64_REDUCTION_BACKENDS = ("optix_partner_resident_experimental",)
PARTNER_RESIDENT_COLUMNAR_COUNT_SUM_BACKENDS = PARTNER_RESIDENT_COLUMNAR_I64_REDUCTION_BACKENDS
PARTNER_RESIDENT_COLUMNAR_I64_REDUCTIONS = ("count", "sum", "min", "max")
COMPOSITE_COLUMNAR_AGGREGATE_LOWERINGS = {
    "avg_as_sum_count": ("sum", "count"),
}


@dataclass(frozen=True)
class ColumnarRecordSet:
    row_ids: tuple[int, ...]
    columns: dict[str, tuple[Any, ...]]


@dataclass(frozen=True)
class ColumnarAggregatePlan:
    predicates: tuple[PredicateClause, ...]
    group_keys: tuple[str, ...]
    aggregate: str = "count"
    value_field: str | None = None


@dataclass(frozen=True)
class ColumnarAggregateResult:
    rows: tuple[dict[str, Any], ...]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class ColumnarAggregateLoweringPlan:
    backend: str
    supported_aggregates: tuple[str, ...]
    unsupported_aggregates: tuple[str, ...]
    transfer_path: str
    uses_compatibility_wrapper: bool
    materializes_input_rows_for_wrapper: bool
    direct_columnar_record_set_api: bool
    true_zero_copy_authorized: bool
    requires_runtime_validation: bool
    next_engine_target: str
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "backend": self.backend,
            "supported_aggregates": list(self.supported_aggregates),
            "unsupported_aggregates": list(self.unsupported_aggregates),
            "transfer_path": self.transfer_path,
            "uses_compatibility_wrapper": self.uses_compatibility_wrapper,
            "materializes_input_rows_for_wrapper": self.materializes_input_rows_for_wrapper,
            "direct_columnar_record_set_api": self.direct_columnar_record_set_api,
            "true_zero_copy_authorized": self.true_zero_copy_authorized,
            "requires_runtime_validation": self.requires_runtime_validation,
            "next_engine_target": self.next_engine_target,
            "claim_boundary": self.claim_boundary,
        }


def normalize_columnar_record_set(payload: Mapping[str, Any] | ColumnarRecordSet) -> ColumnarRecordSet:
    if isinstance(payload, ColumnarRecordSet):
        _validate_columnar_record_set(payload)
        return payload
    if not isinstance(payload, Mapping):
        raise ValueError("columnar record set must be a mapping or ColumnarRecordSet")
    row_ids = tuple(_coerce_row_id(value, index) for index, value in enumerate(payload.get("row_ids", ())))
    raw_columns = payload.get("columns")
    if not isinstance(raw_columns, Mapping):
        raise ValueError("columnar record set requires a `columns` mapping")
    columns = {str(name): tuple(values) for name, values in raw_columns.items()}
    record_set = ColumnarRecordSet(row_ids=row_ids, columns=columns)
    _validate_columnar_record_set(record_set)
    return record_set


def normalize_columnar_aggregate_plan(payload: Mapping[str, Any] | ColumnarAggregatePlan) -> ColumnarAggregatePlan:
    if isinstance(payload, ColumnarAggregatePlan):
        _validate_columnar_aggregate_plan(payload)
        return payload
    if not isinstance(payload, Mapping):
        raise ValueError("columnar aggregate plan must be a mapping or ColumnarAggregatePlan")
    predicates = tuple(_normalize_predicate_clause(item) for item in payload.get("predicates", ()))
    group_keys = tuple(str(value) for value in payload.get("group_keys", ()))
    aggregate = str(payload.get("aggregate", "count"))
    value_field = payload.get("value_field")
    if value_field is not None:
        value_field = str(value_field)
    plan = ColumnarAggregatePlan(
        predicates=predicates,
        group_keys=group_keys,
        aggregate=aggregate,
        value_field=value_field,
    )
    _validate_columnar_aggregate_plan(plan)
    return plan


def evaluate_columnar_grouped_aggregate(
    record_set: Mapping[str, Any] | ColumnarRecordSet,
    plan: Mapping[str, Any] | ColumnarAggregatePlan,
) -> ColumnarAggregateResult:
    records = normalize_columnar_record_set(record_set)
    aggregate_plan = normalize_columnar_aggregate_plan(plan)
    _validate_plan_fields(records, aggregate_plan)

    groups: dict[tuple[Any, ...], Any] = {}
    matched_count = 0
    for index in range(len(records.row_ids)):
        if not _record_matches(records, index, aggregate_plan.predicates):
            continue
        matched_count += 1
        key = tuple(records.columns[group_key][index] for group_key in aggregate_plan.group_keys)
        value = _aggregate_input_value(records, index, aggregate_plan)
        groups[key] = _accumulate(groups.get(key), value, aggregate_plan.aggregate)

    rows = tuple(
        _format_result_row(key, groups[key], aggregate_plan)
        for key in sorted(groups)
    )
    return ColumnarAggregateResult(
        rows=rows,
        metadata={
            "contract": "columnar_grouped_aggregate_cpu_reference",
            "aggregate": aggregate_plan.aggregate,
            "record_count": len(records.row_ids),
            "matched_count": matched_count,
            "group_count": len(rows),
            "group_keys": list(aggregate_plan.group_keys),
            "value_field": aggregate_plan.value_field,
            "predicate_count": len(aggregate_plan.predicates),
            "materializes_input_rows": False,
            "prepared_scene_required": False,
            "claim_boundary": (
                "CPU oracle for a generic columnar grouped aggregate contract. "
                "No native acceleration or external-system performance claim is authorized."
            ),
        },
    )


def columnar_record_set_to_row_mappings(record_set: Mapping[str, Any] | ColumnarRecordSet) -> tuple[dict[str, Any], ...]:
    records = normalize_columnar_record_set(record_set)
    return tuple(
        {
            "row_id": row_id,
            **{name: values[index] for name, values in records.columns.items()},
        }
        for index, row_id in enumerate(records.row_ids)
    )


def columnar_plan_to_grouped_query(plan: Mapping[str, Any] | ColumnarAggregatePlan) -> dict[str, Any]:
    aggregate_plan = normalize_columnar_aggregate_plan(plan)
    query: dict[str, Any] = {
        "predicates": tuple(
            (clause.field, clause.op, clause.value, clause.value_hi)
            if clause.value_hi is not None
            else (clause.field, clause.op, clause.value)
            for clause in aggregate_plan.predicates
        ),
        "group_keys": aggregate_plan.group_keys,
    }
    if aggregate_plan.value_field is not None:
        query["value_field"] = aggregate_plan.value_field
    return query


def columnar_plan_to_grouped_reduction_spec(
    plan: Mapping[str, Any] | ColumnarAggregatePlan,
) -> GroupedReductionSpec:
    aggregate_plan = normalize_columnar_aggregate_plan(plan)
    return grouped_reduction_spec_from_columnar_plan(aggregate_plan)


def decompose_columnar_aggregate_plan(
    plan: Mapping[str, Any] | ColumnarAggregatePlan,
) -> tuple[ColumnarAggregatePlan, ...]:
    aggregate_plan = normalize_columnar_aggregate_plan(plan)
    if aggregate_plan.aggregate != "avg_as_sum_count":
        return (aggregate_plan,)
    assert aggregate_plan.value_field is not None
    return (
        ColumnarAggregatePlan(
            predicates=aggregate_plan.predicates,
            group_keys=aggregate_plan.group_keys,
            aggregate="sum",
            value_field=aggregate_plan.value_field,
        ),
        ColumnarAggregatePlan(
            predicates=aggregate_plan.predicates,
            group_keys=aggregate_plan.group_keys,
            aggregate="count",
            value_field=None,
        ),
    )


def merge_columnar_grouped_sum_count_rows(
    sum_rows: Sequence[Mapping[str, Any]],
    count_rows: Sequence[Mapping[str, Any]],
    *,
    group_keys: Sequence[str],
) -> tuple[dict[str, Any], ...]:
    normalized_group_keys = tuple(str(group_key) for group_key in group_keys)
    if not normalized_group_keys:
        raise ValueError("composite grouped sum/count merge requires at least one group key")
    sums = {
        _group_row_key(row, normalized_group_keys): row
        for row in sum_rows
    }
    counts = {
        _group_row_key(row, normalized_group_keys): row
        for row in count_rows
    }
    if set(sums) != set(counts):
        raise ValueError("composite grouped sum/count merge requires matching group keys")
    merged: list[dict[str, Any]] = []
    for key in sorted(sums):
        sum_row = sums[key]
        count_row = counts[key]
        if "sum" not in sum_row or "count" not in count_row:
            raise ValueError("composite grouped sum/count rows require `sum` and `count` fields")
        merged.append(
            {
                **{group_key: key[index] for index, group_key in enumerate(normalized_group_keys)},
                "sum": _stable_number(float(sum_row["sum"])),
                "count": int(count_row["count"]),
            }
        )
    return tuple(merged)


def plan_columnar_aggregate_lowering(backend: str) -> ColumnarAggregateLoweringPlan:
    normalized_backend = str(backend)
    if normalized_backend == "cpu_python_reference":
        return ColumnarAggregateLoweringPlan(
            backend=normalized_backend,
            supported_aggregates=SUPPORTED_AGGREGATES,
            unsupported_aggregates=(),
            transfer_path="python_columnar_reference",
            uses_compatibility_wrapper=False,
            materializes_input_rows_for_wrapper=False,
            direct_columnar_record_set_api=True,
            true_zero_copy_authorized=False,
            requires_runtime_validation=False,
            next_engine_target="native_count_sum_parity",
            claim_boundary=(
                "CPU oracle for the generic columnar grouped aggregate contract. "
                "No native acceleration, public speedup, or true zero-copy claim is authorized."
            ),
        )
    if normalized_backend in NATIVE_COLUMNAR_COUNT_SUM_BACKENDS:
        return ColumnarAggregateLoweringPlan(
            backend=normalized_backend,
            supported_aggregates=("count", "sum"),
            unsupported_aggregates=tuple(mode for mode in SUPPORTED_AGGREGATES if mode not in {"count", "sum"}),
            transfer_path="direct_columnar_record_set_to_columnar_payload",
            uses_compatibility_wrapper=False,
            materializes_input_rows_for_wrapper=False,
            direct_columnar_record_set_api=True,
            true_zero_copy_authorized=False,
            requires_runtime_validation=True,
            next_engine_target="optix_partner_resident_columnar_payload_native_execution",
            claim_boundary=(
                "Native count/sum parity only. The path avoids Python row-mapping materialization "
                "and can reuse matching typed host buffers, but it still may stage unsupported "
                "columns and does not authorize min/max support, true zero-copy, public speedup, "
                "or whole-app wording."
            ),
        )
    if normalized_backend in PARTNER_RESIDENT_COLUMNAR_I64_REDUCTION_BACKENDS:
        supported = PARTNER_RESIDENT_COLUMNAR_I64_REDUCTIONS + tuple(COMPOSITE_COLUMNAR_AGGREGATE_LOWERINGS)
        return ColumnarAggregateLoweringPlan(
            backend=normalized_backend,
            supported_aggregates=supported,
            unsupported_aggregates=tuple(
                mode for mode in SUPPORTED_AGGREGATES if mode not in set(supported)
            ),
            transfer_path="partner_resident_cuda_column_descriptors_to_experimental_optix_grouped_i64",
            uses_compatibility_wrapper=False,
            materializes_input_rows_for_wrapper=False,
            direct_columnar_record_set_api=True,
            true_zero_copy_authorized=False,
            requires_runtime_validation=True,
            next_engine_target="stabilize_partner_resident_columnar_payload_native_execution",
            claim_boundary=(
                "Experimental partner-resident OptiX int64 grouped count/sum/min/max plus "
                "composite avg_as_sum_count lowering over count+sum. The path accepts CUDA partner "
                "column descriptors and materializes compact grouped rows at the boundary, but it "
                "does not authorize true zero-copy, whole-app, or public speedup wording."
            ),
        )
    raise ValueError(f"unsupported columnar aggregate lowering backend: {backend}")


def _validate_columnar_record_set(record_set: ColumnarRecordSet) -> None:
    if not record_set.row_ids:
        raise ValueError("columnar record set requires at least one row_id")
    if len(set(record_set.row_ids)) != len(record_set.row_ids):
        raise ValueError("row_ids must be unique")
    if not record_set.columns:
        raise ValueError("columnar record set requires at least one column")
    expected = len(record_set.row_ids)
    for name, values in record_set.columns.items():
        if not name:
            raise ValueError("column names must be non-empty")
        if len(values) != expected:
            raise ValueError(f"column `{name}` length must match row_ids length")


def _validate_columnar_aggregate_plan(plan: ColumnarAggregatePlan) -> None:
    if not plan.group_keys:
        raise ValueError("columnar aggregate plan requires at least one group key")
    if plan.aggregate not in SUPPORTED_AGGREGATES:
        raise ValueError(f"unsupported aggregate: {plan.aggregate}")
    if plan.aggregate != "count" and not plan.value_field:
        raise ValueError(f"aggregate `{plan.aggregate}` requires a value_field")


def _validate_plan_fields(record_set: ColumnarRecordSet, plan: ColumnarAggregatePlan) -> None:
    for group_key in plan.group_keys:
        if group_key not in record_set.columns:
            raise ValueError(f"group key `{group_key}` is not a column")
    if plan.value_field is not None and plan.value_field not in record_set.columns:
        raise ValueError(f"value field `{plan.value_field}` is not a column")
    for predicate in plan.predicates:
        if predicate.field not in record_set.columns:
            raise ValueError(f"predicate field `{predicate.field}` is not a column")


def _group_row_key(row: Mapping[str, Any], group_keys: tuple[str, ...]) -> tuple[Any, ...]:
    missing = [group_key for group_key in group_keys if group_key not in row]
    if missing:
        raise ValueError(f"grouped row is missing group key `{missing[0]}`")
    return tuple(row[group_key] for group_key in group_keys)


def _record_matches(record_set: ColumnarRecordSet, index: int, predicates: Sequence[PredicateClause]) -> bool:
    return all(_value_matches(record_set.columns[predicate.field][index], predicate) for predicate in predicates)


def _value_matches(value: Any, predicate: PredicateClause) -> bool:
    if predicate.op == "eq":
        return value == predicate.value
    if predicate.op == "lt":
        return value < predicate.value
    if predicate.op == "le":
        return value <= predicate.value
    if predicate.op == "gt":
        return value > predicate.value
    if predicate.op == "ge":
        return value >= predicate.value
    if predicate.op == "between":
        if predicate.value_hi is None:
            raise ValueError("between predicate requires value_hi")
        return predicate.value <= value <= predicate.value_hi
    raise ValueError(f"unsupported predicate operator: {predicate.op}")


def _aggregate_input_value(record_set: ColumnarRecordSet, index: int, plan: ColumnarAggregatePlan) -> float | None:
    if plan.aggregate == "count":
        return None
    assert plan.value_field is not None
    return float(record_set.columns[plan.value_field][index])


def _accumulate(current: Any, value: float | None, aggregate: str) -> Any:
    if aggregate == "count":
        return 1 if current is None else int(current) + 1
    assert value is not None
    if aggregate == "sum":
        return value if current is None else float(current) + value
    if aggregate == "min":
        return value if current is None else min(float(current), value)
    if aggregate == "max":
        return value if current is None else max(float(current), value)
    if aggregate == "avg_as_sum_count":
        if current is None:
            return [value, 1]
        current[0] += value
        current[1] += 1
        return current
    raise ValueError(f"unsupported aggregate: {aggregate}")


def _format_result_row(key: tuple[Any, ...], value: Any, plan: ColumnarAggregatePlan) -> dict[str, Any]:
    row = {group_key: key[index] for index, group_key in enumerate(plan.group_keys)}
    if plan.aggregate == "count":
        row["count"] = int(value)
    elif plan.aggregate == "avg_as_sum_count":
        row["sum"] = _stable_number(value[0])
        row["count"] = int(value[1])
    else:
        row[plan.aggregate] = _stable_number(value)
    return row


def _stable_number(value: float) -> int | float:
    value = float(value)
    if value.is_integer():
        return int(value)
    return value


def _coerce_row_id(value: Any, index: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"row_id at index {index} must be an integer")
    if value < 0 or value > UINT32_MAX:
        raise ValueError(f"row_id at index {index} must be in uint32 range")
    return int(value)
