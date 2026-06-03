from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .partner_protocol import RtdlBufferDescriptor
from .partner_continuation_protocol import V2_5_PARTNER_CONTINUATION_OPERATION_NAMES
from .segmented_row_stream import SEGMENTED_ROW_STREAM_FAILURE_MODE
from .v2_8_benchmark_runtime_gap import V2_8_FIRST_RUNTIME_TARGET


V2_8_TYPED_RESULT_STREAM_VERSION = "rtdl.v2_8.typed_result_stream.v1"
V2_8_TYPED_RESULT_STREAM_STATUS = "internal_contract_no_native_promotion"
V2_8_TYPED_RESULT_STREAM_TARGET = V2_8_FIRST_RUNTIME_TARGET
V2_8_TYPED_RESULT_STREAM_KIND_VALUES = (
    "hit_stream",
    "candidate_stream",
    "adjacency_stream",
    "ranked_summary_stream",
    "bounded_witness_stream",
    "grouped_reduction_stream",
)
V2_8_TYPED_RESULT_STREAM_COLUMN_ROLES = (
    "group_key",
    "item_id",
    "score",
    "payload",
    "mask",
    "status",
    "witness",
    "row_offset",
)
V2_8_TYPED_RESULT_STREAM_ORDERING_STATES = (
    "event_ordered",
    "group_ordered",
    "stable_row_order",
    "unordered_with_explicit_sort_key",
)
V2_8_TYPED_RESULT_STREAM_STATUS_COLUMNS = (
    "row_count",
    "capacity",
    "overflow",
    "complete_candidate_coverage",
)
V2_8_TYPED_RESULT_STREAM_ALLOWED_CONTINUATIONS = (
    "segmented_count_i64",
    "segmented_sum_f64",
    "segmented_min_f64",
    "segmented_max_f64",
    "grouped_argmin_f64",
    "grouped_argmax_f64",
    "grouped_topk_f64",
    "grouped_vector_sum_f64x2",
    "compact_mask_i64",
    "bounded_collect_finalize_i64",
)
V2_8_TYPED_RESULT_STREAM_CONTINUATION_SEMANTICS = {
    "grouped_argmin_f64": "select the lowest score per group; ties choose the lowest item_id",
    "grouped_argmax_f64": "select the highest score per group; ties choose the lowest item_id",
    "grouped_topk_f64": (
        "select the k lowest scores per group in ascending score then item_id order; "
        "ranks are one-based within each group"
    ),
    "grouped_vector_sum_f64x2": "sum paired float64 x/y components per group",
}
V2_8_TYPED_RESULT_STREAM_CLAIM_BOUNDARY = (
    "v2.8 typed result streams are an internal generic contract for RTDL "
    "runtime development. They do not authorize release, public speedup "
    "wording, broad RT-core wording, true-zero-copy wording, hidden dispatch, "
    "hidden partner selection, app-specific native-engine behavior, or "
    "user-defined shader injection."
)


@dataclass(frozen=True)
class V28TypedResultColumn:
    name: str
    role: str
    buffer: RtdlBufferDescriptor
    nullable: bool = False
    required_for_continuation: bool = True

    def __post_init__(self) -> None:
        if not str(self.name):
            raise ValueError("typed result column requires a non-empty name")
        if self.role not in V2_8_TYPED_RESULT_STREAM_COLUMN_ROLES:
            raise ValueError("unsupported typed result column role")
        if self.buffer.name != self.name:
            raise ValueError("typed result column name must match buffer name")

    @property
    def device_resident(self) -> bool:
        return self.buffer.device_type == "cuda" and self.buffer.data_ptr is not None and int(self.buffer.data_ptr) > 0

    def to_metadata(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role,
            "dtype": self.buffer.dtype,
            "shape": self.buffer.shape,
            "nullable": self.nullable,
            "required_for_continuation": self.required_for_continuation,
            "device_resident": self.device_resident,
            "buffer": self.buffer.to_metadata(),
        }


@dataclass(frozen=True)
class V28TypedResultStreamContract:
    stream_id: str
    stream_kind: str
    producer_primitive: str
    columns: tuple[V28TypedResultColumn, ...]
    status_columns: tuple[V28TypedResultColumn, ...]
    ordering: str
    page_capacity: int
    grouped_continuation_ready: bool = True
    event_or_group_ordering_required: bool = True
    app_specific_engine_logic_allowed: bool = False
    automatic_partner_selection_allowed: bool = False
    hidden_dispatch_allowed: bool = False
    release_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    rt_core_speedup_claim_authorized: bool = False
    true_zero_copy_claim_authorized: bool = False
    contract_version: str = V2_8_TYPED_RESULT_STREAM_VERSION
    status: str = V2_8_TYPED_RESULT_STREAM_STATUS

    def __post_init__(self) -> None:
        if not str(self.stream_id):
            raise ValueError("typed result stream requires a non-empty stream_id")
        if self.stream_kind not in V2_8_TYPED_RESULT_STREAM_KIND_VALUES:
            raise ValueError("unsupported typed result stream kind")
        if not str(self.producer_primitive):
            raise ValueError("typed result stream requires a producer primitive")
        if self.ordering not in V2_8_TYPED_RESULT_STREAM_ORDERING_STATES:
            raise ValueError("unsupported typed result stream ordering")
        if int(self.page_capacity) <= 0:
            raise ValueError("typed result stream page_capacity must be positive")
        column_names = tuple(column.name for column in self.columns)
        status_names = tuple(column.name for column in self.status_columns)
        if len(set(column_names)) != len(column_names):
            raise ValueError("typed result stream columns must be unique")
        if len(set(status_names)) != len(status_names):
            raise ValueError("typed result stream status columns must be unique")
        if set(column_names) & set(status_names):
            raise ValueError("data columns and status columns must be disjoint")
        for required in V2_8_TYPED_RESULT_STREAM_STATUS_COLUMNS:
            if required not in status_names:
                raise ValueError(f"typed result stream missing status column: {required}")
        if self.event_or_group_ordering_required and self.ordering == "unordered_with_explicit_sort_key":
            if not any(column.role == "row_offset" for column in self.columns):
                raise ValueError("unordered streams require an explicit row_offset column")
        for field in (
            "app_specific_engine_logic_allowed",
            "automatic_partner_selection_allowed",
            "hidden_dispatch_allowed",
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
        ):
            if getattr(self, field):
                raise ValueError(f"typed result stream must not authorize {field}")

    @property
    def all_columns(self) -> tuple[V28TypedResultColumn, ...]:
        return (*self.columns, *self.status_columns)

    @property
    def column_names(self) -> tuple[str, ...]:
        return tuple(column.name for column in self.columns)

    @property
    def status_column_names(self) -> tuple[str, ...]:
        return tuple(column.name for column in self.status_columns)

    @property
    def device_resident_column_count(self) -> int:
        return sum(1 for column in self.all_columns if column.device_resident)

    def column(self, name: str) -> V28TypedResultColumn:
        for column in self.all_columns:
            if column.name == name:
                return column
        raise ValueError(f"unknown typed result stream column: {name}")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "status": self.status,
            "target": V2_8_TYPED_RESULT_STREAM_TARGET,
            "stream_id": self.stream_id,
            "stream_kind": self.stream_kind,
            "producer_primitive": self.producer_primitive,
            "ordering": self.ordering,
            "page_capacity": int(self.page_capacity),
            "segmented_page_failure_mode": SEGMENTED_ROW_STREAM_FAILURE_MODE,
            "columns": tuple(column.to_metadata() for column in self.columns),
            "status_columns": tuple(column.to_metadata() for column in self.status_columns),
            "column_names": self.column_names,
            "status_column_names": self.status_column_names,
            "device_resident_column_count": self.device_resident_column_count,
            "grouped_continuation_ready": self.grouped_continuation_ready,
            "event_or_group_ordering_required": self.event_or_group_ordering_required,
            "app_specific_engine_logic_allowed": self.app_specific_engine_logic_allowed,
            "automatic_partner_selection_allowed": self.automatic_partner_selection_allowed,
            "hidden_dispatch_allowed": self.hidden_dispatch_allowed,
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "rt_core_speedup_claim_authorized": self.rt_core_speedup_claim_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "claim_boundary": V2_8_TYPED_RESULT_STREAM_CLAIM_BOUNDARY,
        }


@dataclass(frozen=True)
class V28GroupedContinuationPlan:
    stream: V28TypedResultStreamContract
    operation: str
    group_column: str
    value_columns: tuple[str, ...] = ()
    item_column: str | None = None
    user_selected_partner: str = "explicit_user_choice_required"
    continuation_status: str = "contract_only"
    automatic_partner_selection_allowed: bool = False
    hidden_dispatch_allowed: bool = False
    release_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    rt_core_speedup_claim_authorized: bool = False
    true_zero_copy_claim_authorized: bool = False

    def __post_init__(self) -> None:
        if self.operation not in V2_8_TYPED_RESULT_STREAM_ALLOWED_CONTINUATIONS:
            raise ValueError("unsupported v2.8 grouped continuation operation")
        if self.operation not in V2_5_PARTNER_CONTINUATION_OPERATION_NAMES:
            raise ValueError("v2.8 grouped continuation must map to a declared partner operation")
        group = self.stream.column(self.group_column)
        if group.role != "group_key":
            raise ValueError("group_column must have role group_key")
        for value_column in self.value_columns:
            self.stream.column(value_column)
        if self.item_column is not None:
            item = self.stream.column(self.item_column)
            if item.role not in {"item_id", "witness"}:
                raise ValueError("item_column must have role item_id or witness")
        if self.user_selected_partner in {"", "auto", "explicit_user_choice_required"}:
            raise ValueError("v2.8 grouped continuation requires explicit user partner choice")
        for field in (
            "automatic_partner_selection_allowed",
            "hidden_dispatch_allowed",
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
        ):
            if getattr(self, field):
                raise ValueError(f"grouped continuation plan must not authorize {field}")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "contract_version": V2_8_TYPED_RESULT_STREAM_VERSION,
            "target": V2_8_TYPED_RESULT_STREAM_TARGET,
            "stream_id": self.stream.stream_id,
            "stream_kind": self.stream.stream_kind,
            "operation": self.operation,
            "group_column": self.group_column,
            "value_columns": self.value_columns,
            "item_column": self.item_column,
            "user_selected_partner": self.user_selected_partner,
            "continuation_status": self.continuation_status,
            "continuation_semantics": V2_8_TYPED_RESULT_STREAM_CONTINUATION_SEMANTICS.get(self.operation),
            "automatic_partner_selection_allowed": self.automatic_partner_selection_allowed,
            "hidden_dispatch_allowed": self.hidden_dispatch_allowed,
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "rt_core_speedup_claim_authorized": self.rt_core_speedup_claim_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "claim_boundary": V2_8_TYPED_RESULT_STREAM_CLAIM_BOUNDARY,
        }


def typed_result_column(
    name: str,
    role: str,
    dtype: str,
    shape: Iterable[int],
    *,
    device_type: str = "cpu",
    device_id: int = 0,
    data_ptr: int | None = None,
    access_mode: str = "read",
    source_protocol: str = "python",
    lifetime: str = "caller_retained",
    mutability: str = "immutable",
    capacity_elements: int | None = None,
    nullable: bool = False,
    required_for_continuation: bool = True,
) -> V28TypedResultColumn:
    return V28TypedResultColumn(
        name=name,
        role=role,
        buffer=RtdlBufferDescriptor(
            name=name,
            dtype=dtype,
            shape=tuple(int(dim) for dim in shape),
            device_type=device_type,
            device_id=int(device_id),
            data_ptr=data_ptr,
            access_mode=access_mode,
            source_protocol=source_protocol,
            lifetime=lifetime,
            mutability=mutability,
            capacity_elements=capacity_elements,
        ),
        nullable=bool(nullable),
        required_for_continuation=bool(required_for_continuation),
    )


def typed_result_status_columns(
    *,
    device_type: str = "cpu",
    device_id: int = 0,
    row_count_ptr: int | None = None,
    capacity_ptr: int | None = None,
    overflow_ptr: int | None = None,
    complete_ptr: int | None = None,
    source_protocol: str = "python",
) -> tuple[V28TypedResultColumn, ...]:
    specs = (
        ("row_count", "uint64", row_count_ptr),
        ("capacity", "uint64", capacity_ptr),
        ("overflow", "uint32", overflow_ptr),
        ("complete_candidate_coverage", "uint32", complete_ptr),
    )
    return tuple(
        typed_result_column(
            name,
            "status",
            dtype,
            (1,),
            device_type=device_type,
            device_id=device_id,
            data_ptr=ptr,
            source_protocol=source_protocol,
            mutability="mutable",
            required_for_continuation=True,
        )
        for name, dtype, ptr in specs
    )


def make_typed_result_stream_contract(
    *,
    stream_id: str,
    stream_kind: str,
    producer_primitive: str,
    columns: Iterable[V28TypedResultColumn],
    status_columns: Iterable[V28TypedResultColumn],
    ordering: str,
    page_capacity: int,
) -> V28TypedResultStreamContract:
    return V28TypedResultStreamContract(
        stream_id=stream_id,
        stream_kind=stream_kind,
        producer_primitive=producer_primitive,
        columns=tuple(columns),
        status_columns=tuple(status_columns),
        ordering=ordering,
        page_capacity=int(page_capacity),
    )


def plan_grouped_continuation_for_typed_result_stream(
    stream: V28TypedResultStreamContract,
    *,
    operation: str,
    group_column: str,
    value_columns: Iterable[str] = (),
    item_column: str | None = None,
    user_selected_partner: str = "explicit_user_choice_required",
) -> V28GroupedContinuationPlan:
    return V28GroupedContinuationPlan(
        stream=stream,
        operation=operation,
        group_column=group_column,
        value_columns=tuple(str(column) for column in value_columns),
        item_column=item_column,
        user_selected_partner=str(user_selected_partner),
    )


def validate_typed_result_stream_contract(
    stream: V28TypedResultStreamContract | dict[str, Any],
) -> dict[str, Any]:
    metadata = stream.to_metadata() if isinstance(stream, V28TypedResultStreamContract) else dict(stream)
    errors: list[str] = []
    if metadata.get("contract_version") != V2_8_TYPED_RESULT_STREAM_VERSION:
        errors.append("unexpected typed result stream contract version")
    if metadata.get("target") != V2_8_TYPED_RESULT_STREAM_TARGET:
        errors.append("typed result stream target mismatch")
    if metadata.get("status") != V2_8_TYPED_RESULT_STREAM_STATUS:
        errors.append("typed result stream status mismatch")
    if metadata.get("stream_kind") not in V2_8_TYPED_RESULT_STREAM_KIND_VALUES:
        errors.append("unsupported typed result stream kind")
    status_names = tuple(metadata.get("status_column_names", ()))
    for required in V2_8_TYPED_RESULT_STREAM_STATUS_COLUMNS:
        if required not in status_names:
            errors.append(f"missing status column: {required}")
    column_names = tuple(metadata.get("column_names", ()))
    if len(set(column_names)) != len(column_names):
        errors.append("data columns must be unique")
    if set(column_names) & set(status_names):
        errors.append("data and status columns must be disjoint")
    for field in (
        "app_specific_engine_logic_allowed",
        "automatic_partner_selection_allowed",
        "hidden_dispatch_allowed",
        "release_authorized",
        "public_speedup_claim_authorized",
        "rt_core_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
    ):
        if metadata.get(field) is not False:
            errors.append(f"{field} must remain false")
    return {
        "status": "accept" if not errors else "reject",
        "contract_version": metadata.get("contract_version"),
        "stream_id": metadata.get("stream_id"),
        "stream_kind": metadata.get("stream_kind"),
        "errors": tuple(errors),
        "column_count": len(column_names),
        "status_column_count": len(status_names),
        "claim_boundary": V2_8_TYPED_RESULT_STREAM_CLAIM_BOUNDARY,
    }


def validate_grouped_continuation_plan(
    plan: V28GroupedContinuationPlan | dict[str, Any],
) -> dict[str, Any]:
    metadata = plan.to_metadata() if isinstance(plan, V28GroupedContinuationPlan) else dict(plan)
    errors: list[str] = []
    if metadata.get("contract_version") != V2_8_TYPED_RESULT_STREAM_VERSION:
        errors.append("unexpected grouped continuation plan version")
    if metadata.get("operation") not in V2_8_TYPED_RESULT_STREAM_ALLOWED_CONTINUATIONS:
        errors.append("unsupported grouped continuation operation")
    if metadata.get("user_selected_partner") in {"", "auto", "explicit_user_choice_required"}:
        errors.append("grouped continuation requires explicit user partner choice")
    for field in (
        "automatic_partner_selection_allowed",
        "hidden_dispatch_allowed",
        "release_authorized",
        "public_speedup_claim_authorized",
        "rt_core_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
    ):
        if metadata.get(field) is not False:
            errors.append(f"{field} must remain false")
    return {
        "status": "accept" if not errors else "reject",
        "contract_version": metadata.get("contract_version"),
        "operation": metadata.get("operation"),
        "stream_id": metadata.get("stream_id"),
        "errors": tuple(errors),
        "claim_boundary": V2_8_TYPED_RESULT_STREAM_CLAIM_BOUNDARY,
    }


def v2_8_typed_result_stream_contract_summary() -> dict[str, Any]:
    return {
        "contract_version": V2_8_TYPED_RESULT_STREAM_VERSION,
        "status": V2_8_TYPED_RESULT_STREAM_STATUS,
        "target": V2_8_TYPED_RESULT_STREAM_TARGET,
        "stream_kinds": V2_8_TYPED_RESULT_STREAM_KIND_VALUES,
        "column_roles": V2_8_TYPED_RESULT_STREAM_COLUMN_ROLES,
        "status_columns": V2_8_TYPED_RESULT_STREAM_STATUS_COLUMNS,
        "ordering_states": V2_8_TYPED_RESULT_STREAM_ORDERING_STATES,
        "allowed_continuations": V2_8_TYPED_RESULT_STREAM_ALLOWED_CONTINUATIONS,
        "continuation_semantics": V2_8_TYPED_RESULT_STREAM_CONTINUATION_SEMANTICS,
        "segmented_page_failure_mode": SEGMENTED_ROW_STREAM_FAILURE_MODE,
        "native_engine_app_specific_logic_allowed": False,
        "automatic_partner_selection_allowed": False,
        "hidden_dispatch_allowed": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "claim_boundary": V2_8_TYPED_RESULT_STREAM_CLAIM_BOUNDARY,
    }


__all__ = [
    "V28GroupedContinuationPlan",
    "V28TypedResultColumn",
    "V28TypedResultStreamContract",
    "V2_8_TYPED_RESULT_STREAM_ALLOWED_CONTINUATIONS",
    "V2_8_TYPED_RESULT_STREAM_CLAIM_BOUNDARY",
    "V2_8_TYPED_RESULT_STREAM_COLUMN_ROLES",
    "V2_8_TYPED_RESULT_STREAM_CONTINUATION_SEMANTICS",
    "V2_8_TYPED_RESULT_STREAM_KIND_VALUES",
    "V2_8_TYPED_RESULT_STREAM_ORDERING_STATES",
    "V2_8_TYPED_RESULT_STREAM_STATUS",
    "V2_8_TYPED_RESULT_STREAM_STATUS_COLUMNS",
    "V2_8_TYPED_RESULT_STREAM_TARGET",
    "V2_8_TYPED_RESULT_STREAM_VERSION",
    "make_typed_result_stream_contract",
    "plan_grouped_continuation_for_typed_result_stream",
    "typed_result_column",
    "typed_result_status_columns",
    "v2_8_typed_result_stream_contract_summary",
    "validate_grouped_continuation_plan",
    "validate_typed_result_stream_contract",
]
