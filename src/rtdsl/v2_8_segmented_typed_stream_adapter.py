from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .segmented_row_stream import SegmentedRowStream
from .segmented_row_stream import emit_segmented_row_stream
from .segmented_row_stream import validate_segmented_row_pages
from .partner_continuation_protocol import execute_v2_5_partner_continuation_reference
from .v2_8_typed_result_stream import V28GroupedContinuationPlan
from .v2_8_typed_result_stream import V28TypedResultStreamContract
from .v2_8_typed_result_stream import V2_8_TYPED_RESULT_STREAM_CLAIM_BOUNDARY
from .v2_8_typed_result_stream import V2_8_TYPED_RESULT_STREAM_COLUMN_ROLES
from .v2_8_typed_result_stream import V2_8_TYPED_RESULT_STREAM_TARGET
from .v2_8_typed_result_stream import make_typed_result_stream_contract
from .v2_8_typed_result_stream import plan_grouped_continuation_for_typed_result_stream
from .v2_8_typed_result_stream import typed_result_column
from .v2_8_typed_result_stream import typed_result_status_columns
from .v2_8_typed_result_stream import validate_grouped_continuation_plan
from .v2_8_typed_result_stream import validate_typed_result_stream_contract


V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_VERSION = "rtdl.v2_8.segmented_typed_stream_adapter.v1"
V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_STATUS = "internal_reference_adapter_no_native_promotion"
V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_MATERIALIZATION = "host_reference_contract_adapter"
V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_CLAIM_BOUNDARY = (
    "v2.8 segmented typed stream adapter bridges an existing segmented row "
    "stream into the typed result-stream contract for local contract testing. "
    "It does not prove device residency, true zero-copy, release readiness, "
    "public speedup, broad RT-core acceleration, hidden dispatch, hidden "
    "partner selection, app-specific native-engine behavior, or user-defined "
    "shader injection."
)


@dataclass(frozen=True)
class V28SegmentedTypedStreamAdapterResult:
    segmented_stream: SegmentedRowStream
    typed_stream: V28TypedResultStreamContract
    continuation_plan: V28GroupedContinuationPlan | None
    column_roles: tuple[tuple[str, str], ...]
    dtypes: tuple[tuple[str, str], ...]
    status_values: tuple[tuple[str, int | bool], ...]
    materialization: str = V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_MATERIALIZATION
    adapter_version: str = V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_VERSION
    status: str = V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_STATUS
    native_producer_promoted: bool = False
    partner_consumer_promoted: bool = False
    device_resident_result_stream_proven: bool = False
    true_zero_copy_claim_authorized: bool = False
    release_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    rt_core_speedup_claim_authorized: bool = False
    hidden_dispatch_allowed: bool = False
    automatic_partner_selection_allowed: bool = False
    app_specific_engine_logic_allowed: bool = False

    def __post_init__(self) -> None:
        validate_segmented_row_pages(self.segmented_stream.pages)
        stream_validation = validate_typed_result_stream_contract(self.typed_stream)
        if stream_validation["status"] != "accept":
            raise ValueError(f"typed stream validation failed: {stream_validation['errors']}")
        if self.continuation_plan is not None:
            plan_validation = validate_grouped_continuation_plan(self.continuation_plan)
            if plan_validation["status"] != "accept":
                raise ValueError(f"grouped continuation validation failed: {plan_validation['errors']}")
        for field in (
            "native_producer_promoted",
            "partner_consumer_promoted",
            "device_resident_result_stream_proven",
            "true_zero_copy_claim_authorized",
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "hidden_dispatch_allowed",
            "automatic_partner_selection_allowed",
            "app_specific_engine_logic_allowed",
        ):
            if getattr(self, field):
                raise ValueError(f"segmented typed stream adapter must not authorize {field}")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "adapter_version": self.adapter_version,
            "status": self.status,
            "target": V2_8_TYPED_RESULT_STREAM_TARGET,
            "materialization": self.materialization,
            "segmented_stream": self.segmented_stream.to_dict(),
            "typed_stream": self.typed_stream.to_metadata(),
            "continuation_plan": (
                None if self.continuation_plan is None else self.continuation_plan.to_metadata()
            ),
            "column_roles": self.column_roles,
            "dtypes": self.dtypes,
            "status_values": self.status_values,
            "native_producer_promoted": self.native_producer_promoted,
            "partner_consumer_promoted": self.partner_consumer_promoted,
            "device_resident_result_stream_proven": self.device_resident_result_stream_proven,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "rt_core_speedup_claim_authorized": self.rt_core_speedup_claim_authorized,
            "hidden_dispatch_allowed": self.hidden_dispatch_allowed,
            "automatic_partner_selection_allowed": self.automatic_partner_selection_allowed,
            "app_specific_engine_logic_allowed": self.app_specific_engine_logic_allowed,
            "claim_boundary": V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_CLAIM_BOUNDARY,
            "typed_result_stream_claim_boundary": V2_8_TYPED_RESULT_STREAM_CLAIM_BOUNDARY,
        }


def build_segmented_typed_stream_adapter(
    rows: Iterable[Iterable[Any]],
    *,
    row_schema: Iterable[str],
    column_roles: Mapping[str, str],
    dtypes: Mapping[str, str] | None = None,
    page_capacity: int,
    stream_id: str,
    stream_kind: str,
    producer_primitive: str,
    ordering: str,
    operation: str | None = None,
    group_column: str | None = None,
    value_columns: Iterable[str] = (),
    item_column: str | None = None,
    user_selected_partner: str = "explicit_user_choice_required",
    total_row_capacity: int | None = None,
    max_pages: int | None = None,
    device_type: str = "cpu",
    device_id: int = 0,
    data_ptrs: Mapping[str, int] | None = None,
    source_protocol: str = "python",
) -> V28SegmentedTypedStreamAdapterResult:
    schema = tuple(str(name) for name in row_schema)
    roles = _normalize_column_roles(schema, column_roles)
    dtype_map = _normalize_dtypes(schema, roles, dtypes)
    pointer_map = {str(key): int(value) for key, value in dict(data_ptrs or {}).items()}

    segmented_stream = emit_segmented_row_stream(
        rows,
        row_schema=schema,
        page_capacity=page_capacity,
        stream_id=stream_id,
        total_row_capacity=total_row_capacity,
        max_pages=max_pages,
    )
    columns = tuple(
        typed_result_column(
            name,
            roles[name],
            dtype_map[name],
            (segmented_stream.total_rows,),
            device_type=device_type,
            device_id=device_id,
            data_ptr=pointer_map.get(name),
            source_protocol=source_protocol,
            capacity_elements=total_row_capacity,
        )
        for name in schema
    )
    status_columns = typed_result_status_columns(
        device_type=device_type,
        device_id=device_id,
        row_count_ptr=pointer_map.get("row_count"),
        capacity_ptr=pointer_map.get("capacity"),
        overflow_ptr=pointer_map.get("overflow"),
        complete_ptr=pointer_map.get("complete_candidate_coverage"),
        source_protocol=source_protocol,
    )
    typed_stream = make_typed_result_stream_contract(
        stream_id=segmented_stream.stream_id,
        stream_kind=stream_kind,
        producer_primitive=producer_primitive,
        columns=columns,
        status_columns=status_columns,
        ordering=ordering,
        page_capacity=segmented_stream.page_capacity,
    )
    continuation_plan = None
    if operation is not None:
        if group_column is None:
            raise ValueError("group_column is required when operation is provided")
        continuation_plan = plan_grouped_continuation_for_typed_result_stream(
            typed_stream,
            operation=operation,
            group_column=group_column,
            value_columns=value_columns,
            item_column=item_column,
            user_selected_partner=user_selected_partner,
        )

    return V28SegmentedTypedStreamAdapterResult(
        segmented_stream=segmented_stream,
        typed_stream=typed_stream,
        continuation_plan=continuation_plan,
        column_roles=tuple(sorted(roles.items())),
        dtypes=tuple(sorted(dtype_map.items())),
        status_values=(
            ("row_count", segmented_stream.total_rows),
            ("capacity", segmented_stream.page_capacity),
            ("overflow", bool(segmented_stream.overflowed)),
            ("complete_candidate_coverage", bool(segmented_stream.complete_candidate_coverage)),
        ),
    )


def validate_segmented_typed_stream_adapter(
    adapter: V28SegmentedTypedStreamAdapterResult | dict[str, Any],
) -> dict[str, Any]:
    metadata = adapter.to_metadata() if isinstance(adapter, V28SegmentedTypedStreamAdapterResult) else dict(adapter)
    errors: list[str] = []
    if metadata.get("adapter_version") != V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_VERSION:
        errors.append("unexpected segmented typed stream adapter version")
    if metadata.get("status") != V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_STATUS:
        errors.append("unexpected segmented typed stream adapter status")
    if metadata.get("target") != V2_8_TYPED_RESULT_STREAM_TARGET:
        errors.append("segmented typed stream adapter target mismatch")
    if metadata.get("materialization") != V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_MATERIALIZATION:
        errors.append("unexpected segmented typed stream adapter materialization")
    typed_validation = validate_typed_result_stream_contract(metadata.get("typed_stream", {}))
    if typed_validation["status"] != "accept":
        errors.extend(f"typed_stream:{error}" for error in typed_validation["errors"])
    plan = metadata.get("continuation_plan")
    if plan is not None:
        plan_validation = validate_grouped_continuation_plan(plan)
        if plan_validation["status"] != "accept":
            errors.extend(f"continuation_plan:{error}" for error in plan_validation["errors"])
    status_values = dict(metadata.get("status_values", ()))
    for required in ("row_count", "capacity", "overflow", "complete_candidate_coverage"):
        if required not in status_values:
            errors.append(f"missing status value: {required}")
    for field in (
        "native_producer_promoted",
        "partner_consumer_promoted",
        "device_resident_result_stream_proven",
        "true_zero_copy_claim_authorized",
        "release_authorized",
        "public_speedup_claim_authorized",
        "rt_core_speedup_claim_authorized",
        "hidden_dispatch_allowed",
        "automatic_partner_selection_allowed",
        "app_specific_engine_logic_allowed",
    ):
        if metadata.get(field) is not False:
            errors.append(f"{field} must remain false")
    return {
        "status": "accept" if not errors else "reject",
        "adapter_version": metadata.get("adapter_version"),
        "stream_id": metadata.get("typed_stream", {}).get("stream_id"),
        "materialization": metadata.get("materialization"),
        "errors": tuple(errors),
        "claim_boundary": V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_CLAIM_BOUNDARY,
    }


def execute_segmented_typed_stream_reference_continuation(
    adapter: V28SegmentedTypedStreamAdapterResult,
    *,
    group_count: int | None = None,
    k: int | None = None,
    total_row_capacity: int | None = None,
) -> dict[str, Any]:
    """Run the adapter's continuation plan through the v2.5 reference oracle."""

    if adapter.continuation_plan is None:
        raise ValueError("adapter has no grouped continuation plan to execute")
    validation = validate_segmented_typed_stream_adapter(adapter)
    if validation["status"] != "accept":
        raise ValueError(f"segmented typed stream adapter validation failed: {validation['errors']}")
    plan = adapter.continuation_plan
    rows = _adapter_rows(adapter)
    columns = _adapter_columns(adapter, rows)
    inferred_group_count = _resolve_group_count(columns[plan.group_column], group_count)
    inputs = _reference_inputs_for_plan(
        plan,
        columns,
        group_count=inferred_group_count,
        k=k,
        total_row_capacity=total_row_capacity,
    )
    result = execute_v2_5_partner_continuation_reference(plan.operation, inputs)
    return {
        "adapter_version": V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_VERSION,
        "status": "completed_reference_consumer",
        "target": V2_8_TYPED_RESULT_STREAM_TARGET,
        "materialization": V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_MATERIALIZATION,
        "operation": plan.operation,
        "stream_id": adapter.typed_stream.stream_id,
        "user_selected_partner": plan.user_selected_partner,
        "reference_partner": result["partner"],
        "inputs": inputs,
        "outputs": result["outputs"],
        "native_producer_promoted": False,
        "partner_consumer_promoted": False,
        "device_resident_result_stream_proven": False,
        "true_zero_copy_claim_authorized": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "hidden_dispatch_allowed": False,
        "automatic_partner_selection_allowed": False,
        "app_specific_engine_logic_allowed": False,
        "claim_boundary": V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_CLAIM_BOUNDARY,
    }


def v2_8_segmented_typed_stream_adapter_summary() -> dict[str, Any]:
    return {
        "adapter_version": V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_VERSION,
        "status": V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_STATUS,
        "target": V2_8_TYPED_RESULT_STREAM_TARGET,
        "materialization": V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_MATERIALIZATION,
        "native_producer_promoted": False,
        "partner_consumer_promoted": False,
        "device_resident_result_stream_proven": False,
        "true_zero_copy_claim_authorized": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "hidden_dispatch_allowed": False,
        "automatic_partner_selection_allowed": False,
        "app_specific_engine_logic_allowed": False,
        "claim_boundary": V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_CLAIM_BOUNDARY,
    }


def _normalize_column_roles(
    schema: tuple[str, ...],
    column_roles: Mapping[str, str],
) -> dict[str, str]:
    role_map = {str(key): str(value) for key, value in dict(column_roles).items()}
    missing = [name for name in schema if name not in role_map]
    if missing:
        raise ValueError(f"column_roles missing schema fields: {tuple(missing)}")
    extra = [name for name in role_map if name not in schema]
    if extra:
        raise ValueError(f"column_roles contains fields outside row_schema: {tuple(extra)}")
    for name, role in role_map.items():
        if role not in V2_8_TYPED_RESULT_STREAM_COLUMN_ROLES:
            raise ValueError(f"unsupported typed result role for {name}: {role}")
        if role == "status":
            raise ValueError("data row_schema columns must not use status role")
    return role_map


def _normalize_dtypes(
    schema: tuple[str, ...],
    roles: Mapping[str, str],
    dtypes: Mapping[str, str] | None,
) -> dict[str, str]:
    supplied = {str(key): str(value) for key, value in dict(dtypes or {}).items()}
    extra = [name for name in supplied if name not in schema]
    if extra:
        raise ValueError(f"dtypes contains fields outside row_schema: {tuple(extra)}")
    dtype_map: dict[str, str] = {}
    for name in schema:
        dtype_map[name] = supplied.get(name, _default_dtype_for_role(roles[name]))
    return dtype_map


def _default_dtype_for_role(role: str) -> str:
    if role in {"group_key", "item_id", "witness", "row_offset"}:
        return "int64"
    if role == "score":
        return "float64"
    if role == "mask":
        return "uint32"
    return "float64"


def _adapter_rows(adapter: V28SegmentedTypedStreamAdapterResult) -> tuple[tuple[Any, ...], ...]:
    rows: list[tuple[Any, ...]] = []
    for page in adapter.segmented_stream.pages:
        rows.extend(page.rows)
    return tuple(rows)


def _adapter_columns(
    adapter: V28SegmentedTypedStreamAdapterResult,
    rows: tuple[tuple[Any, ...], ...],
) -> dict[str, tuple[Any, ...]]:
    schema = adapter.segmented_stream.row_schema
    return {
        name: tuple(row[index] for row in rows)
        for index, name in enumerate(schema)
    }


def _resolve_group_count(values: tuple[Any, ...], group_count: int | None) -> int:
    if group_count is not None:
        resolved = int(group_count)
        if resolved < 0:
            raise ValueError("group_count must be non-negative")
        return resolved
    if not values:
        return 0
    return max(int(value) for value in values) + 1


def _reference_inputs_for_plan(
    plan: V28GroupedContinuationPlan,
    columns: Mapping[str, tuple[Any, ...]],
    *,
    group_count: int,
    k: int | None,
    total_row_capacity: int | None,
) -> dict[str, object]:
    operation = plan.operation
    group_ids = tuple(int(value) for value in columns[plan.group_column])
    inputs: dict[str, object] = {
        "group_count": int(group_count),
        "group_ids": group_ids,
    }
    if operation == "segmented_count_i64":
        return inputs
    if operation in {"segmented_sum_f64", "segmented_min_f64", "segmented_max_f64"}:
        value_column = _single_value_column(plan)
        inputs["values"] = tuple(float(value) for value in columns[value_column])
        return inputs
    if operation == "grouped_vector_sum_f64x2":
        first, second = _two_value_columns(plan)
        inputs["values_x"] = tuple(float(value) for value in columns[first])
        inputs["values_y"] = tuple(float(value) for value in columns[second])
        return inputs
    if operation in {"grouped_argmin_f64", "grouped_argmax_f64", "grouped_topk_f64"}:
        value_column = _single_value_column(plan)
        item_column = _required_item_column(plan)
        inputs["item_ids"] = tuple(int(value) for value in columns[item_column])
        inputs["scores"] = tuple(float(value) for value in columns[value_column])
        if operation == "grouped_topk_f64":
            if k is None:
                raise ValueError("k is required for grouped_topk_f64")
            inputs["k"] = int(k)
        return inputs
    if operation == "bounded_collect_finalize_i64":
        item_column = _required_item_column(plan)
        if k is None:
            raise ValueError("k is required for bounded_collect_finalize_i64")
        inputs["item_ids"] = tuple(int(value) for value in columns[item_column])
        inputs["k"] = int(k)
        if total_row_capacity is not None:
            inputs["total_row_capacity"] = int(total_row_capacity)
        return inputs
    if operation == "compact_mask_i64":
        first, second = _two_value_columns(plan)
        return {
            "values": tuple(int(value) for value in columns[first]),
            "mask": tuple(bool(value) for value in columns[second]),
        }
    raise ValueError(f"unsupported reference continuation operation: {operation}")


def _single_value_column(plan: V28GroupedContinuationPlan) -> str:
    if len(plan.value_columns) != 1:
        raise ValueError(f"{plan.operation} requires exactly one value column")
    return plan.value_columns[0]


def _two_value_columns(plan: V28GroupedContinuationPlan) -> tuple[str, str]:
    if len(plan.value_columns) != 2:
        raise ValueError(f"{plan.operation} requires exactly two value columns")
    return plan.value_columns[0], plan.value_columns[1]


def _required_item_column(plan: V28GroupedContinuationPlan) -> str:
    if plan.item_column is None:
        raise ValueError(f"{plan.operation} requires an item column")
    return plan.item_column


__all__ = [
    "V28SegmentedTypedStreamAdapterResult",
    "V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_CLAIM_BOUNDARY",
    "V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_MATERIALIZATION",
    "V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_STATUS",
    "V2_8_SEGMENTED_TYPED_STREAM_ADAPTER_VERSION",
    "build_segmented_typed_stream_adapter",
    "execute_segmented_typed_stream_reference_continuation",
    "v2_8_segmented_typed_stream_adapter_summary",
    "validate_segmented_typed_stream_adapter",
]
