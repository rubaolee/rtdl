from __future__ import annotations

from collections.abc import Sequence as SequenceABC
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Mapping, Sequence

from .generic_primitives import GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_PRIMITIVE
from .generic_primitives import GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_ROW_SCHEMA
from .neutral_buffer_seam import V2_5_NEUTRAL_BUFFER_SEAM_VERSION
from .neutral_buffer_seam import create_neutral_buffer_lease
from .neutral_buffer_seam import neutral_buffer_descriptor_from_rtdl_buffer
from .partner_protocol import RtdlBufferDescriptor
from .partner_protocol import V2_4_PHASES
from .v2_5_partner_support_matrix import plan_v2_5_partner_support


GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION = "rtdl.rt_hit_stream_handoff.v2.5"
GENERIC_HIT_STREAM_PARTNER_TRANSFER_PLAN_VERSION = "rtdl.hit_stream_partner_transfer_plan.v2.5"
GENERIC_HIT_STREAM_ASYNC_PROMOTION_REQUIREMENTS_VERSION = "rtdl.hit_stream_async_promotion_requirements.v2.5"
GENERIC_HIT_STREAM_NEUTRAL_SEAM_RECONCILIATION_VERSION = "rtdl.hit_stream_neutral_seam_reconciliation.v2.5"
GENERIC_HIT_STREAM_HANDOFF_API_MATURITY = "experimental_host_bridge_contract"
GENERIC_DEVICE_RESIDENT_HIT_STREAM_COLUMNS = ("ray_ids:int64", "primitive_ids:int64")
GENERIC_TYPED_PRIMITIVE_PAYLOAD_COLUMNS = ("primitive_group_ids:int64", "primitive_values:float64")
GENERIC_NATIVE_DEVICE_HIT_STREAM_OUTPUT_ABI_SYMBOLS = {
    "optix": "rtdl_optix_static_triangle_scene_3d_ray_triangle_hit_stream_device_columns",
}
GENERIC_NATIVE_DEVICE_HIT_STREAM_OUTPUT_ABI_FIELDS = (
    "ray_ids_device_ptr:uint64",
    "primitive_ids_device_ptr:uint64",
    "row_count:uint64",
    "capacity:uint64",
    "hit_event_count:uint64",
    "overflow:uint32",
    "device_ordinal:int32",
    "owner_handle:uint64",
    "traversal_seconds:float64",
    "row_count_device_ptr:uint64",
    "hit_event_count_device_ptr:uint64",
    "overflow_device_ptr:uint64",
)
GENERIC_HIT_STREAM_HANDOFF_SOURCE_MODES = (
    "native_device_columns",
    "host_rows_to_columns_bridge",
    "reference_columns",
)
GENERIC_TYPED_PAYLOAD_GROUP_ID_VALIDATION_MODES = (
    "host_scan",
    "caller_asserted",
    "deferred_device_check",
)
GENERIC_HIT_STREAM_HANDOFF_PHASES = (
    "rt_traversal",
    "hit_stream_column_handoff",
    "typed_payload_gather",
    "partner_continuation",
    "host_materialization",
)
GENERIC_TORCH_CARRIER_ADAPTER_MODES = (
    "torch_tensor",
    "cuda_array_interface_to_torch_via_dlpack",
    "host_column_requires_explicit_copy",
    "unsupported",
)
GENERIC_HIT_STREAM_STREAM_ORDERING_STATES = (
    "not_proven",
    "same_stream",
    "producer_event_waited_by_consumer",
    "host_synchronized_before_consumer",
)
GENERIC_HIT_STREAM_ZERO_COPY_COMPATIBLE_STREAM_ORDERING_STATES = (
    "same_stream",
    "producer_event_waited_by_consumer",
)
GENERIC_HIT_STREAM_PARTNER_TRANSFER_STATUSES = (
    "host_reference_ready",
    "explicit_host_materialization_required",
    "torch_carrier_preview",
    "cuda_descriptor_preview",
    "descriptor_only",
    "stream_ordering_proof_required",
    "unsupported_fail_closed",
)
GENERIC_HIT_STREAM_PARTNER_CARRIER_PROTOCOLS = (
    "host_columns",
    "torch_tensor_carrier",
    "cuda_array_interface_to_torch_carrier",
    "cuda_array_interface_descriptor",
    "neutral_buffer_descriptor",
    "none",
)
GENERIC_HIT_STREAM_TORCH_CARRIER_FORBIDDEN_AUTHORITY_FIELDS = (
    "transfer_status",
    "copy_status",
    "lifetime_state",
    "ownership_state",
    "owner_state",
    "release_event",
    "failure_cleanup_event",
    "transfer_copy_lifetime_authority",
    "zero_copy_claim_authorized",
    "native_device_output_promotion_ready",
)
GENERIC_PRIMITIVE_PAYLOAD_COLUMN_DESCRIPTOR_VERSION = (
    "rtdl.primitive_payload_column_descriptor.v2.5"
)
GENERIC_PRIMITIVE_PAYLOAD_COLUMN_ROLES = (
    "hit_stream_key",
    "primitive_payload",
    "status_counter",
    "partial_aggregate_rows",
    "partner_output",
)
GENERIC_PRIMITIVE_PAYLOAD_FALLBACK_REASONS = (
    "none",
    "host_reference",
    "partner_unavailable",
    "stream_ordering_unproven",
    "dtype_or_shape_unsupported",
    "lifetime_unproven",
)
GENERIC_PRIMITIVE_PAYLOAD_CONTINUATION_PLANNER_VERSION = (
    "rtdl.primitive_payload_continuation_planner.v2.5"
)
GENERIC_PRIMITIVE_PAYLOAD_CONTINUATION_PLAN_STATUSES = (
    "accepted_preview",
    "reference_contract",
    "fallback_required",
)
GENERIC_PRIMITIVE_PAYLOAD_CONTINUATION_ENTRYPOINT_METADATA_VERSION = (
    "rtdl.primitive_payload_continuation_entrypoint.v2.5"
)


@dataclass(frozen=True)
class RtdlPrimitivePayloadColumnDescriptor:
    """Partner-neutral descriptor for a primitive payload column.

    This layer wraps an `RtdlBufferDescriptor` with the v2.5 information a
    continuation planner needs: semantic role, producer/consumer boundary,
    stream ordering, fallback reason, and neutral-buffer lifetime accounting.
    """

    buffer: RtdlBufferDescriptor
    semantic_role: str
    producer: str
    consumer: str
    stream_ordering: str = "not_proven"
    lifetime_state: str = "caller_retained"
    transfer_status: str | None = None
    fallback_reason: str = "none"
    host_materialized_before_handoff: bool = False
    native_producer: bool = False
    measured_same_pointer: bool = False
    measured_no_host_stage: bool = False
    measured_evidence: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.semantic_role not in GENERIC_PRIMITIVE_PAYLOAD_COLUMN_ROLES:
            raise ValueError("unsupported primitive payload column role")
        if self.stream_ordering not in GENERIC_HIT_STREAM_STREAM_ORDERING_STATES:
            raise ValueError("unsupported primitive payload stream ordering")
        if self.fallback_reason not in GENERIC_PRIMITIVE_PAYLOAD_FALLBACK_REASONS:
            raise ValueError("unsupported primitive payload fallback reason")
        if not str(self.producer):
            raise ValueError("primitive payload descriptor requires a non-empty producer")
        if not str(self.consumer):
            raise ValueError("primitive payload descriptor requires a non-empty consumer")
        if self.native_producer and self.lifetime_state not in {
            "producer_retained",
            "native_owned_pending_state_machine",
        }:
            raise ValueError("native primitive payload producers must retain ownership")

    @property
    def device_resident(self) -> bool:
        return self.buffer.device_type == "cuda" and self.buffer.data_ptr is not None and int(self.buffer.data_ptr) > 0

    @property
    def stream_ordering_proven(self) -> bool:
        return self.stream_ordering in GENERIC_HIT_STREAM_ZERO_COPY_COMPATIBLE_STREAM_ORDERING_STATES

    @property
    def fallback_required(self) -> bool:
        return self.fallback_reason != "none"

    def neutral_seam(self):
        return neutral_buffer_descriptor_from_rtdl_buffer(
            self.buffer,
            producer=self.producer,
            consumer=self.consumer,
            transfer_status=self.transfer_status,
            lifetime_state=self.lifetime_state,
            native_producer=bool(self.native_producer),
            host_materialized_before_handoff=bool(self.host_materialized_before_handoff),
            measured_same_pointer=bool(self.measured_same_pointer),
            measured_no_host_stage=bool(self.measured_no_host_stage),
            measured_evidence=self.measured_evidence,
        )

    def to_metadata(self) -> dict[str, object]:
        seam = self.neutral_seam()
        return {
            "contract_version": GENERIC_PRIMITIVE_PAYLOAD_COLUMN_DESCRIPTOR_VERSION,
            "name": self.buffer.name,
            "semantic_role": self.semantic_role,
            "producer": self.producer,
            "consumer": self.consumer,
            "dtype": self.buffer.dtype,
            "shape": self.buffer.shape,
            "device": f"{self.buffer.device_type}:{self.buffer.device_id}",
            "data_ptr_observed": self.device_resident,
            "source_protocol": self.buffer.source_protocol,
            "access_mode": self.buffer.access_mode,
            "mutability": self.buffer.mutability,
            "stream_ordering": self.stream_ordering,
            "stream_ordering_proven": self.stream_ordering_proven,
            "event_or_same_stream_ordering_proven": self.stream_ordering_proven,
            "lifetime_state": self.lifetime_state,
            "fallback_reason": self.fallback_reason,
            "fallback_required": self.fallback_required,
            "host_materialized_before_handoff": bool(self.host_materialized_before_handoff),
            "native_producer": bool(self.native_producer),
            "neutral_buffer_seam": seam.to_metadata(),
            "true_zero_copy_authorized": bool(seam.zero_copy_claim_authorized and self.stream_ordering_proven),
            "public_speedup_claim_authorized": False,
            "claim_boundary": (
                "Primitive payload column descriptors describe typed buffers, stream "
                "ordering, fallback reasons, and neutral-buffer lifetime state. They "
                "do not authorize arbitrary partner execution, public speedup claims, "
                "or true-zero-copy claims without measured evidence and ordering proof."
            ),
        }


def describe_primitive_payload_column_descriptor(
    *,
    name: str,
    dtype: str,
    shape: Sequence[int],
    semantic_role: str,
    producer: str,
    consumer: str,
    device_type: str = "cpu",
    device_id: int = 0,
    data_ptr: int | None = None,
    source_protocol: str = "python",
    access_mode: str = "read",
    mutability: str = "immutable",
    stream_ordering: str = "not_proven",
    lifetime_state: str = "caller_retained",
    transfer_status: str | None = None,
    fallback_reason: str = "none",
    capacity_elements: int | None = None,
    owner: Any = None,
    host_materialized_before_handoff: bool = False,
    native_producer: bool = False,
    measured_same_pointer: bool = False,
    measured_no_host_stage: bool = False,
    measured_evidence: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    """Describe one typed primitive payload column without partner-specific coercion."""

    buffer = RtdlBufferDescriptor(
        name=name,
        dtype=dtype,
        shape=tuple(int(dim) for dim in shape),
        device_type=device_type,
        device_id=int(device_id),
        data_ptr=None if data_ptr is None else int(data_ptr),
        access_mode=access_mode,
        source_protocol=source_protocol,
        lifetime="borrowed" if lifetime_state == "partner_borrowed" else "session_retained"
        if lifetime_state in {"producer_retained", "native_owned_pending_state_machine"}
        else "caller_retained",
        mutability=mutability,
        capacity_elements=capacity_elements,
        owner=owner,
    )
    return RtdlPrimitivePayloadColumnDescriptor(
        buffer=buffer,
        semantic_role=semantic_role,
        producer=producer,
        consumer=consumer,
        stream_ordering=stream_ordering,
        lifetime_state=lifetime_state,
        transfer_status=transfer_status,
        fallback_reason=fallback_reason,
        host_materialized_before_handoff=host_materialized_before_handoff,
        native_producer=native_producer,
        measured_same_pointer=measured_same_pointer,
        measured_no_host_stage=measured_no_host_stage,
        measured_evidence=measured_evidence,
    ).to_metadata()


def describe_fixed_radius_graph_partial_payload_descriptor(
    *,
    partials_device_ptr: int,
    partial_count: int,
    stream_ordering: str,
    owner: Any = None,
    request_count: int | None = None,
    query_block_count: int | None = None,
) -> dict[str, object]:
    evidence = {
        "request_count": None if request_count is None else int(request_count),
        "query_block_count": None if query_block_count is None else int(query_block_count),
    }
    return describe_primitive_payload_column_descriptor(
        name="fixed_radius_ranked_summary_aggregate_partials",
        dtype="struct:RtdlFixedRadiusRankedNeighborAggregate",
        shape=(int(partial_count),),
        semantic_role="partial_aggregate_rows",
        producer="optix_cuda_graph",
        consumer="partner_partial_reduction",
        device_type="cuda",
        device_id=0,
        data_ptr=int(partials_device_ptr),
        source_protocol="native_cuda_device_pointer",
        access_mode="read",
        mutability="mutable",
        stream_ordering=stream_ordering,
        lifetime_state="producer_retained",
        transfer_status="borrowed_device_pointer_unmeasured",
        fallback_reason="none",
        capacity_elements=int(partial_count),
        owner=owner,
        host_materialized_before_handoff=False,
        native_producer=True,
        measured_evidence=evidence,
    )


def plan_primitive_payload_partner_continuation(
    operation: str,
    partner: str,
    descriptors: Sequence[Mapping[str, Any] | RtdlPrimitivePayloadColumnDescriptor],
) -> dict[str, object]:
    """Plan partner consumption from typed primitive payload descriptors."""

    support = plan_v2_5_partner_support(operation, partner)
    descriptor_metadata = tuple(_primitive_payload_descriptor_metadata(descriptor) for descriptor in descriptors)
    fallback_reasons: list[str] = []
    resolved_partner = str(support["partner"])
    support_status = str(support["status"])
    reference_partner = resolved_partner == "python_reference"

    if not descriptor_metadata:
        fallback_reasons.append("dtype_or_shape_unsupported")
    if not bool(support["supported"]):
        fallback_reasons.append("partner_unavailable")
    if support_status == "descriptor_only" and not reference_partner:
        fallback_reasons.append("partner_unavailable")

    for descriptor in descriptor_metadata:
        if bool(support["requires_cuda"]) and not str(descriptor.get("device", "")).startswith("cuda:"):
            fallback_reasons.append("host_reference")
        if bool(support["requires_neutral_buffer_seam"]) and "neutral_buffer_seam" not in descriptor:
            fallback_reasons.append("lifetime_unproven")
        if not reference_partner and bool(descriptor.get("fallback_required")):
            fallback_reasons.append(str(descriptor.get("fallback_reason", "dtype_or_shape_unsupported")))
        if (
            not reference_partner
            and bool(support["requires_cuda"])
            and not bool(descriptor.get("stream_ordering_proven"))
        ):
            fallback_reasons.append("stream_ordering_unproven")
        if bool(descriptor.get("native_producer")) and descriptor.get("lifetime_state") not in {
            "producer_retained",
            "native_owned_pending_state_machine",
        }:
            fallback_reasons.append("lifetime_unproven")

    unique_reasons = tuple(dict.fromkeys(reason for reason in fallback_reasons if reason != "none"))
    if unique_reasons:
        plan_status = "fallback_required"
    elif reference_partner:
        plan_status = "reference_contract"
    else:
        plan_status = "accepted_preview"

    return {
        "planner_version": GENERIC_PRIMITIVE_PAYLOAD_CONTINUATION_PLANNER_VERSION,
        "operation": str(operation),
        "requested_partner": str(partner),
        "resolved_partner": resolved_partner,
        "support_status": support_status,
        "plan_status": plan_status,
        "can_execute_preview": plan_status == "accepted_preview",
        "fallback_required": plan_status == "fallback_required",
        "fallback_reasons": unique_reasons,
        "descriptor_count": len(descriptor_metadata),
        "descriptors": descriptor_metadata,
        "support_cell": support,
        "stream_ordering_preserved": all(
            bool(descriptor.get("stream_ordering_proven")) for descriptor in descriptor_metadata
        ),
        "neutral_buffer_seam_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
        "rt_traversal_replacement_allowed": False,
        "true_zero_copy_authorized": False,
        "public_speedup_claim_authorized": False,
        "claim_boundary": (
            "Primitive payload continuation plans select only from explicit descriptor "
            "capabilities and support-matrix cells. They do not execute arbitrary "
            "partner code, replace RT traversal, authorize public speedup claims, or "
            "authorize true-zero-copy claims."
        ),
    }


def describe_primitive_payload_partner_continuation_entrypoint(
    *,
    operation: str,
    partner: str,
    descriptors: Sequence[Mapping[str, Any] | RtdlPrimitivePayloadColumnDescriptor],
    entrypoint: str,
    execution_status: str = "planned_not_executed",
) -> dict[str, object]:
    """Describe how a concrete continuation entrypoint resolves a payload plan."""

    plan = plan_primitive_payload_partner_continuation(operation, partner, descriptors)
    return {
        "contract_version": GENERIC_PRIMITIVE_PAYLOAD_CONTINUATION_ENTRYPOINT_METADATA_VERSION,
        "entrypoint": str(entrypoint),
        "execution_status": str(execution_status),
        "operation": str(plan["operation"]),
        "requested_partner": str(plan["requested_partner"]),
        "resolved_partner": str(plan["resolved_partner"]),
        "support_status": str(plan["support_status"]),
        "plan_status": str(plan["plan_status"]),
        "runtime_action": _primitive_payload_entrypoint_runtime_action(plan),
        "can_execute_preview": bool(plan["can_execute_preview"]),
        "fallback_required": bool(plan["fallback_required"]),
        "fallback_reasons": tuple(plan["fallback_reasons"]),
        "descriptor_count": int(plan["descriptor_count"]),
        "stream_ordering_preserved": bool(plan["stream_ordering_preserved"]),
        "primitive_payload_continuation_plan": plan,
        "rt_traversal_replacement_allowed": False,
        "true_zero_copy_authorized": False,
        "public_speedup_claim_authorized": False,
        "claim_boundary": (
            "This metadata attaches a primitive-payload planner decision to a "
            "specific continuation entrypoint. It is an explain/fail-closed "
            "record only; it does not promote a partner path, replace RT "
            "traversal, or authorize public speedup or true-zero-copy claims."
        ),
    }


def attach_primitive_payload_partner_continuation_metadata(
    result: Mapping[str, Any],
    *,
    operation: str,
    partner: str,
    descriptors: Sequence[Mapping[str, Any] | RtdlPrimitivePayloadColumnDescriptor],
    entrypoint: str,
    execution_status: str = "completed",
) -> dict[str, object]:
    """Return a continuation result with explicit primitive-payload plan metadata."""

    output = dict(result)
    entrypoint_metadata = describe_primitive_payload_partner_continuation_entrypoint(
        operation=operation,
        partner=partner,
        descriptors=descriptors,
        entrypoint=entrypoint,
        execution_status=execution_status,
    )
    output["primitive_payload_continuation_entrypoint"] = entrypoint_metadata
    output["primitive_payload_continuation_plan"] = entrypoint_metadata[
        "primitive_payload_continuation_plan"
    ]
    output["primitive_payload_planner_fallback_required"] = bool(
        entrypoint_metadata["fallback_required"]
    )
    output["primitive_payload_planner_fallback_reasons"] = tuple(
        entrypoint_metadata["fallback_reasons"]
    )
    output["true_zero_copy_authorized"] = False
    output["public_speedup_claim_authorized"] = False
    return output


def _primitive_payload_descriptor_metadata(
    descriptor: Mapping[str, Any] | RtdlPrimitivePayloadColumnDescriptor,
) -> dict[str, Any]:
    if isinstance(descriptor, RtdlPrimitivePayloadColumnDescriptor):
        return descriptor.to_metadata()
    metadata = dict(descriptor)
    if metadata.get("contract_version") != GENERIC_PRIMITIVE_PAYLOAD_COLUMN_DESCRIPTOR_VERSION:
        raise ValueError("primitive payload continuation planner requires descriptor metadata")
    return metadata


def _primitive_payload_entrypoint_runtime_action(plan: Mapping[str, Any]) -> str:
    plan_status = str(plan["plan_status"])
    support_status = str(plan["support_status"])
    if plan_status == "accepted_preview":
        return "execute_preview_with_explicit_descriptor_plan"
    if plan_status == "reference_contract":
        return "execute_reference_contract"
    if support_status == "descriptor_only":
        return "descriptor_only_fail_closed_or_reference_fallback"
    return "fallback_required_before_partner_execution"


@dataclass(frozen=True)
class RtdlHitStreamColumnHandoff:
    ray_ids: Any
    primitive_ids: Any
    row_count: int
    capacity: int
    overflow: bool
    backend: str
    source_mode: str
    phase_timing_seconds: Mapping[str, float]
    native_symbol: str | None = None
    materializes_host_rows_for_bridge: bool = False
    native_device_column_output_proven_on_hardware: bool = False
    owner: Any = None
    producer_consumer_stream_ordering: str = "not_proven"
    caller_owned_output_buffers: bool = False
    reusable_output_buffers_used: bool = False
    row_count_device_ptr: int | None = None
    hit_event_count_device_ptr: int | None = None
    overflow_device_ptr: int | None = None

    def __post_init__(self) -> None:
        row_count = int(self.row_count)
        capacity = int(self.capacity)
        if row_count < 0:
            raise ValueError("hit-stream row_count must be non-negative")
        if capacity < 0:
            raise ValueError("hit-stream capacity must be non-negative")
        if _column_length(self.ray_ids) != row_count:
            raise ValueError("ray_ids length must match row_count")
        if _column_length(self.primitive_ids) != row_count:
            raise ValueError("primitive_ids length must match row_count")
        if self.overflow and row_count != 0:
            raise ValueError("overflowed hit-stream handoffs must be fail-closed with row_count=0")
        if self.source_mode not in GENERIC_HIT_STREAM_HANDOFF_SOURCE_MODES:
            raise ValueError("unsupported hit-stream column source mode")
        if self.producer_consumer_stream_ordering not in GENERIC_HIT_STREAM_STREAM_ORDERING_STATES:
            raise ValueError("unsupported hit-stream stream ordering state")
        for name, value in (
            ("row_count_device_ptr", self.row_count_device_ptr),
            ("hit_event_count_device_ptr", self.hit_event_count_device_ptr),
            ("overflow_device_ptr", self.overflow_device_ptr),
        ):
            if value is not None and int(value) <= 0:
                raise ValueError(f"hit-stream {name} must be a non-zero device pointer when provided")
        _validate_int64_column(self.ray_ids, "ray_ids")
        _validate_int64_column(self.primitive_ids, "primitive_ids")
        if self.native_device_column_output_proven_on_hardware:
            if self.source_mode != "native_device_columns":
                raise ValueError("hardware-proven native device columns require source_mode=native_device_columns")
            if self.materializes_host_rows_for_bridge:
                raise ValueError("hardware-proven native device columns must not materialize host rows first")
            if self.device_type != "cuda":
                raise ValueError("hardware-proven native device columns currently require CUDA-resident columns")

    @property
    def device_type(self) -> str:
        return _device_info(self.primitive_ids)[0]

    @property
    def device_id(self) -> int:
        return _device_info(self.primitive_ids)[1]

    @property
    def source_protocol(self) -> str:
        return _source_protocol(self.primitive_ids)

    @property
    def device_resident(self) -> bool:
        return self.device_type == "cuda" and not self.materializes_host_rows_for_bridge

    @property
    def removes_host_materialization_bottleneck(self) -> bool:
        return (
            self.source_mode == "native_device_columns"
            and self.device_resident
            and not self.materializes_host_rows_for_bridge
            and bool(self.native_device_column_output_proven_on_hardware)
        )

    def to_metadata(self) -> dict[str, object]:
        row_count_device_ptr = 0 if self.row_count_device_ptr is None else int(self.row_count_device_ptr)
        hit_event_count_device_ptr = (
            0 if self.hit_event_count_device_ptr is None else int(self.hit_event_count_device_ptr)
        )
        overflow_device_ptr = 0 if self.overflow_device_ptr is None else int(self.overflow_device_ptr)
        return {
            "contract_version": GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION,
            "api_maturity": GENERIC_HIT_STREAM_HANDOFF_API_MATURITY,
            "columns": GENERIC_DEVICE_RESIDENT_HIT_STREAM_COLUMNS,
            "backend": self.backend,
            "row_count": int(self.row_count),
            "capacity": int(self.capacity),
            "overflow": bool(self.overflow),
            "fail_closed_overflow": True,
            "source_mode": self.source_mode,
            "device": f"{self.device_type}:{self.device_id}",
            "source_protocol": self.source_protocol,
            "native_symbol": self.native_symbol,
            "device_resident": self.device_resident,
            "materializes_host_rows_for_bridge": bool(self.materializes_host_rows_for_bridge),
            "host_hit_rows_materialized_before_handoff": bool(self.materializes_host_rows_for_bridge),
            "removes_host_materialization_bottleneck": self.removes_host_materialization_bottleneck,
            "native_device_column_output_proven_on_hardware": bool(
                self.native_device_column_output_proven_on_hardware
            ),
            "device_resident_but_unproven_native_output": (
                self.source_mode == "native_device_columns"
                and self.device_resident
                and not bool(self.native_device_column_output_proven_on_hardware)
            ),
            "ownership_lifetime_model": (
                "caller_retained_python_reference"
                if self.caller_owned_output_buffers
                else
                "native_owner_state_machine_required_before_promotion"
                if self.source_mode == "native_device_columns"
                else "caller_retained_python_reference"
            ),
            "owner_lifetime_state": _owner_lifetime_state(self.owner),
            "owner_close_supported": callable(getattr(self.owner, "close", None)),
            "handoff_after_owner_close_allowed": False if self.source_mode == "native_device_columns" else None,
            "caller_owned_output_buffers": bool(self.caller_owned_output_buffers),
            "reusable_output_buffers_used": bool(self.reusable_output_buffers_used),
            "producer_consumer_stream_ordering": self.producer_consumer_stream_ordering,
            "stream_synchronization_proven": self.producer_consumer_stream_ordering != "not_proven",
            "host_synchronization_used": self.producer_consumer_stream_ordering == "host_synchronized_before_consumer",
            "event_or_same_stream_ordering_proven": self.producer_consumer_stream_ordering
            in GENERIC_HIT_STREAM_ZERO_COPY_COMPATIBLE_STREAM_ORDERING_STATES,
            "zero_copy_compatible_stream_ordering": self.producer_consumer_stream_ordering
            in GENERIC_HIT_STREAM_ZERO_COPY_COMPATIBLE_STREAM_ORDERING_STATES,
            "row_count_scalar_visibility": "host_visible_after_producer_synchronization",
            "overflow_scalar_visibility": "host_visible_after_producer_synchronization",
            "row_count_device_ptr": row_count_device_ptr,
            "hit_event_count_device_ptr": hit_event_count_device_ptr,
            "overflow_device_ptr": overflow_device_ptr,
            "device_resident_row_count_for_partner": row_count_device_ptr != 0,
            "device_resident_hit_event_count_for_partner": hit_event_count_device_ptr != 0,
            "device_resident_overflow_for_partner": overflow_device_ptr != 0,
            "device_resident_status_for_partner": row_count_device_ptr != 0 and overflow_device_ptr != 0,
            "completion_event_handle_available": False,
            "same_stream_handle_available": False,
            "async_partner_continuation_authorized": False,
            "true_zero_copy_requires_stream_synchronization": True,
            "true_zero_copy_authorized": False,
            "public_speedup_claim_authorized": False,
            "neutral_buffer_seam_contract_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
            "neutral_buffer_seams": (
                _neutral_buffer_seam_metadata(
                    "ray_ids",
                    self.ray_ids,
                    "int64",
                    producer=self.source_mode,
                    consumer="typed_payload_gather",
                    access_mode="read",
                    native_producer=self.source_mode == "native_device_columns"
                    and not self.caller_owned_output_buffers,
                    host_materialized_before_handoff=bool(self.materializes_host_rows_for_bridge),
                    lifetime_state="caller_retained" if self.caller_owned_output_buffers else None,
                ),
                _neutral_buffer_seam_metadata(
                    "primitive_ids",
                    self.primitive_ids,
                    "int64",
                    producer=self.source_mode,
                    consumer="typed_payload_gather",
                    access_mode="read",
                    native_producer=self.source_mode == "native_device_columns"
                    and not self.caller_owned_output_buffers,
                    host_materialized_before_handoff=bool(self.materializes_host_rows_for_bridge),
                    lifetime_state="caller_retained" if self.caller_owned_output_buffers else None,
                ),
            ),
            "column_descriptors": (
                _buffer_descriptor("ray_ids", self.ray_ids, "int64", access_mode="read").to_metadata(),
                _buffer_descriptor("primitive_ids", self.primitive_ids, "int64", access_mode="read").to_metadata(),
            ),
            "phase_timing_seconds": dict(self.phase_timing_seconds),
        }


@dataclass(frozen=True)
class RtdlRawCudaColumn:
    name: str
    dtype: str
    data_ptr: int
    length: int
    device_id: int = 0
    owner: Any = None

    def __post_init__(self) -> None:
        if not str(self.name):
            raise ValueError("raw CUDA column requires a non-empty name")
        if self.dtype not in {"int64", "float64"}:
            raise ValueError("raw CUDA column dtype must be int64 or float64")
        if int(self.length) < 0:
            raise ValueError("raw CUDA column length must be non-negative")
        if int(self.length) > 0 and int(self.data_ptr) <= 0:
            raise ValueError("raw CUDA column requires a non-zero data_ptr when length is non-zero")
        if int(self.device_id) < 0:
            raise ValueError("raw CUDA column device_id must be non-negative")

    @property
    def shape(self) -> tuple[int, ...]:
        return (int(self.length),)

    @property
    def __cuda_array_interface__(self) -> dict[str, object]:
        if _owner_lifetime_state(self.owner) == "closed":
            raise RuntimeError("raw CUDA column owner is closed")
        return {
            "shape": self.shape,
            "strides": None,
            "typestr": "<i8" if self.dtype == "int64" else "<f8",
            "data": (int(self.data_ptr), False),
            "version": 3,
            "device": int(self.device_id),
        }


@dataclass(frozen=True)
class RtdlNativeDeviceHitStreamOutput:
    ray_ids_device_ptr: int
    primitive_ids_device_ptr: int
    row_count: int
    capacity: int
    overflow: bool
    hit_event_count: int
    device_id: int = 0
    backend: str = "optix"
    native_symbol: str | None = None
    owner_handle: int | None = None
    owner: Any = None
    traversal_seconds: float | None = None
    native_device_column_output_proven_on_hardware: bool = False
    closed: bool = False
    producer_consumer_stream_ordering: str = "not_proven"
    row_count_device_ptr: int | None = None
    hit_event_count_device_ptr: int | None = None
    overflow_device_ptr: int | None = None

    def __post_init__(self) -> None:
        backend = str(self.backend).strip().lower()
        if backend not in GENERIC_NATIVE_DEVICE_HIT_STREAM_OUTPUT_ABI_SYMBOLS:
            raise ValueError("unsupported native hit-stream output backend")
        row_count = int(self.row_count)
        capacity = int(self.capacity)
        if row_count < 0:
            raise ValueError("native hit-stream row_count must be non-negative")
        if capacity < 0:
            raise ValueError("native hit-stream capacity must be non-negative")
        if row_count > capacity:
            raise ValueError("native hit-stream row_count cannot exceed capacity")
        if bool(self.overflow) and row_count != 0:
            raise ValueError("overflowed native hit-stream output must fail closed with row_count=0")
        if row_count > 0:
            if int(self.ray_ids_device_ptr) <= 0:
                raise ValueError("native hit-stream ray_ids_device_ptr must be non-zero")
            if int(self.primitive_ids_device_ptr) <= 0:
                raise ValueError("native hit-stream primitive_ids_device_ptr must be non-zero")
        if int(self.hit_event_count) < 0:
            raise ValueError("native hit-stream hit_event_count must be non-negative")
        if int(self.device_id) < 0:
            raise ValueError("native hit-stream device_id must be non-negative")
        if self.producer_consumer_stream_ordering not in GENERIC_HIT_STREAM_STREAM_ORDERING_STATES:
            raise ValueError("unsupported native hit-stream stream ordering state")
        for name, value in (
            ("row_count_device_ptr", self.row_count_device_ptr),
            ("hit_event_count_device_ptr", self.hit_event_count_device_ptr),
            ("overflow_device_ptr", self.overflow_device_ptr),
        ):
            if value is not None and int(value) <= 0:
                raise ValueError(f"native hit-stream {name} must be a non-zero device pointer when provided")
        resolved_symbol = self.native_symbol or GENERIC_NATIVE_DEVICE_HIT_STREAM_OUTPUT_ABI_SYMBOLS[backend]
        object.__setattr__(self, "backend", backend)
        object.__setattr__(self, "native_symbol", resolved_symbol)

    def to_metadata(self) -> dict[str, object]:
        row_count_device_ptr = 0 if self.row_count_device_ptr is None else int(self.row_count_device_ptr)
        hit_event_count_device_ptr = (
            0 if self.hit_event_count_device_ptr is None else int(self.hit_event_count_device_ptr)
        )
        overflow_device_ptr = 0 if self.overflow_device_ptr is None else int(self.overflow_device_ptr)
        return {
            "contract_version": GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION,
            "native_output_abi_symbol": self.native_symbol,
            "native_output_abi_fields": GENERIC_NATIVE_DEVICE_HIT_STREAM_OUTPUT_ABI_FIELDS,
            "backend": self.backend,
            "row_count": int(self.row_count),
            "capacity": int(self.capacity),
            "overflow": bool(self.overflow),
            "fail_closed_overflow": True,
            "hit_event_count": int(self.hit_event_count),
            "device": f"cuda:{int(self.device_id)}",
            "owner_handle_observed": self.owner_handle is not None and int(self.owner_handle) != 0,
            "owner_lifetime_state": "closed" if bool(self.closed) else "open",
            "native_release_enforced_by_python_owner": callable(getattr(self.owner, "close", None)),
            "handoff_after_close_allowed": False,
            "producer_consumer_stream_ordering": self.producer_consumer_stream_ordering,
            "stream_synchronization_proven": self.producer_consumer_stream_ordering != "not_proven",
            "host_synchronization_used": self.producer_consumer_stream_ordering == "host_synchronized_before_consumer",
            "event_or_same_stream_ordering_proven": self.producer_consumer_stream_ordering
            in GENERIC_HIT_STREAM_ZERO_COPY_COMPATIBLE_STREAM_ORDERING_STATES,
            "zero_copy_compatible_stream_ordering": self.producer_consumer_stream_ordering
            in GENERIC_HIT_STREAM_ZERO_COPY_COMPATIBLE_STREAM_ORDERING_STATES,
            "row_count_scalar_visibility": "host_visible_after_producer_synchronization",
            "overflow_scalar_visibility": "host_visible_after_producer_synchronization",
            "row_count_device_ptr": row_count_device_ptr,
            "hit_event_count_device_ptr": hit_event_count_device_ptr,
            "overflow_device_ptr": overflow_device_ptr,
            "device_resident_row_count_for_partner": row_count_device_ptr != 0,
            "device_resident_hit_event_count_for_partner": hit_event_count_device_ptr != 0,
            "device_resident_overflow_for_partner": overflow_device_ptr != 0,
            "device_resident_status_for_partner": row_count_device_ptr != 0 and overflow_device_ptr != 0,
            "completion_event_handle_available": False,
            "same_stream_handle_available": False,
            "async_partner_continuation_authorized": False,
            "true_zero_copy_requires_stream_synchronization": True,
            "traversal_seconds": self.traversal_seconds,
            "native_device_column_output_proven_on_hardware": bool(
                self.native_device_column_output_proven_on_hardware
            ),
            "true_zero_copy_authorized": False,
            "public_speedup_claim_authorized": False,
            "claim_boundary": (
                "This metadata describes native CUDA hit-stream column output. "
                "It does not authorize true zero-copy or performance claims without "
                "pod evidence proving same-pointer/no-host-stage behavior and lifetime cleanup."
            ),
        }

    def close(self) -> None:
        if bool(self.closed):
            return
        close = getattr(self.owner, "close", None)
        if callable(close):
            close()
        object.__setattr__(self, "closed", True)

    def __enter__(self) -> "RtdlNativeDeviceHitStreamOutput":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    def to_handoff(self) -> RtdlHitStreamColumnHandoff:
        if bool(self.closed):
            raise RuntimeError("native hit-stream output is closed")
        ray_ids = RtdlRawCudaColumn(
            "ray_ids",
            "int64",
            int(self.ray_ids_device_ptr),
            int(self.row_count),
            device_id=int(self.device_id),
            owner=self,
        )
        primitive_ids = RtdlRawCudaColumn(
            "primitive_ids",
            "int64",
            int(self.primitive_ids_device_ptr),
            int(self.row_count),
            device_id=int(self.device_id),
            owner=self,
        )
        return prepare_generic_device_resident_hit_stream_columns(
            ray_ids=ray_ids,
            primitive_ids=primitive_ids,
            row_count=int(self.row_count),
            capacity=int(self.capacity),
            overflow=bool(self.overflow),
            backend=self.backend,
            phase_timing_seconds=(
                {}
                if self.traversal_seconds is None
                else {"rt_traversal": float(self.traversal_seconds)}
            ),
            native_symbol=self.native_symbol,
            native_device_column_output_proven_on_hardware=bool(
                self.native_device_column_output_proven_on_hardware
            ),
            owner=self,
            producer_consumer_stream_ordering=self.producer_consumer_stream_ordering,
            row_count_device_ptr=self.row_count_device_ptr,
            hit_event_count_device_ptr=self.hit_event_count_device_ptr,
            overflow_device_ptr=self.overflow_device_ptr,
        )


@dataclass(frozen=True)
class RtdlTypedPrimitivePayloadColumns:
    primitive_group_ids: Any
    primitive_values: Any
    primitive_count: int
    group_count: int
    source_mode: str
    group_id_bounds_validation: str = "host_scan"
    default_primitive_values_used: bool = False
    owner: Any = None

    def __post_init__(self) -> None:
        primitive_count = int(self.primitive_count)
        group_count = int(self.group_count)
        if primitive_count < 0:
            raise ValueError("primitive_count must be non-negative")
        if group_count < 0:
            raise ValueError("group_count must be non-negative")
        if _column_length(self.primitive_group_ids) != primitive_count:
            raise ValueError("primitive_group_ids length must match primitive_count")
        if _column_length(self.primitive_values) != primitive_count:
            raise ValueError("primitive_values length must match primitive_count")
        if self.group_id_bounds_validation not in GENERIC_TYPED_PAYLOAD_GROUP_ID_VALIDATION_MODES:
            raise ValueError("unsupported primitive group-id validation mode")
        _validate_int64_column(self.primitive_group_ids, "primitive_group_ids")
        _validate_float64_column(self.primitive_values, "primitive_values")
        if self.group_id_bounds_validation == "host_scan":
            group_ids = _column_to_host_ints(self.primitive_group_ids)
            if any(group_id < 0 or group_id >= group_count for group_id in group_ids):
                raise ValueError("primitive group ids must be in [0, group_count)")

    @property
    def device_type(self) -> str:
        return _device_info(self.primitive_group_ids)[0]

    @property
    def device_id(self) -> int:
        return _device_info(self.primitive_group_ids)[1]

    @property
    def source_protocol(self) -> str:
        return _source_protocol(self.primitive_group_ids)

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract_version": GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION,
            "api_maturity": GENERIC_HIT_STREAM_HANDOFF_API_MATURITY,
            "columns": GENERIC_TYPED_PRIMITIVE_PAYLOAD_COLUMNS,
            "primitive_count": int(self.primitive_count),
            "group_count": int(self.group_count),
            "source_mode": self.source_mode,
            "group_id_bounds_validation": self.group_id_bounds_validation,
            "group_id_bounds_validated": self.group_id_bounds_validation == "host_scan",
            "group_id_bounds_caller_asserted": self.group_id_bounds_validation == "caller_asserted",
            "group_id_bounds_asserted_not_verified": self.group_id_bounds_validation == "caller_asserted",
            "host_scan_for_group_id_validation": self.group_id_bounds_validation == "host_scan",
            "device_group_id_validation_pending": self.group_id_bounds_validation == "deferred_device_check",
            "default_primitive_values_used": bool(self.default_primitive_values_used),
            "device": f"{self.device_type}:{self.device_id}",
            "source_protocol": self.source_protocol,
            "app_specific_semantics_allowed": False,
            "neutral_buffer_seam_contract_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
            "neutral_buffer_seams": (
                _neutral_buffer_seam_metadata(
                    "primitive_group_ids",
                    self.primitive_group_ids,
                    "int64",
                    producer=self.source_mode,
                    consumer="typed_payload_gather",
                    access_mode="read",
                ),
                _neutral_buffer_seam_metadata(
                    "primitive_values",
                    self.primitive_values,
                    "float64",
                    producer=self.source_mode,
                    consumer="typed_payload_gather",
                    access_mode="read",
                ),
            ),
            "column_descriptors": (
                _buffer_descriptor("primitive_group_ids", self.primitive_group_ids, "int64", access_mode="read").to_metadata(),
                _buffer_descriptor("primitive_values", self.primitive_values, "float64", access_mode="read").to_metadata(),
            ),
        }


def describe_generic_device_resident_hit_stream_handoff_3d() -> dict[str, object]:
    return {
        "contract_version": GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION,
        "api_maturity": GENERIC_HIT_STREAM_HANDOFF_API_MATURITY,
        "hit_stream_primitive": GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_PRIMITIVE,
        "hit_stream_columns": GENERIC_DEVICE_RESIDENT_HIT_STREAM_COLUMNS,
        "typed_primitive_payload_columns": GENERIC_TYPED_PRIMITIVE_PAYLOAD_COLUMNS,
        "row_count_metadata": ("row_count:uint64", "capacity:uint64"),
        "overflow_policy": "fail_closed_bounded_columns",
        "ownership": "producer_retains_until_partner_continuation_finishes",
        "allowed_source_modes": GENERIC_HIT_STREAM_HANDOFF_SOURCE_MODES,
        "typed_payload_group_id_validation_modes": GENERIC_TYPED_PAYLOAD_GROUP_ID_VALIDATION_MODES,
        "phase_timing_required": GENERIC_HIT_STREAM_HANDOFF_PHASES,
        "v2_4_phase_timing_basis": V2_4_PHASES,
        "native_engine_app_specific_vocab_allowed": False,
        "triton_replaces_rt_traversal": False,
        "goal2685_host_bridge_only": True,
        "native_device_column_output_proven_on_hardware": False,
        "removes_host_materialization_bottleneck": False,
        "true_zero_copy_claim_authorized": False,
        "public_speedup_claim_authorized": False,
        "claim_boundary": (
            "Goal2685 defines an experimental typed-column handoff contract for RT-produced "
            "ray/primitive hit streams. The current implementation is a host-row bridge only; "
            "native device-column output, a lifetime/ownership state machine, and pod timings "
            "are required before any zero-copy, removed-bottleneck, or speedup claim."
        ),
    }


def describe_v2_5_native_hit_stream_output_abi(backend: str = "optix") -> dict[str, object]:
    normalized_backend = str(backend).strip().lower()
    if normalized_backend not in GENERIC_NATIVE_DEVICE_HIT_STREAM_OUTPUT_ABI_SYMBOLS:
        raise ValueError("unsupported native hit-stream output backend")
    return {
        "contract_version": GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION,
        "api_maturity": "experimental_native_abi_contract_no_promotion",
        "backend": normalized_backend,
        "native_output_abi_symbol": GENERIC_NATIVE_DEVICE_HIT_STREAM_OUTPUT_ABI_SYMBOLS[normalized_backend],
        "native_output_abi_fields": GENERIC_NATIVE_DEVICE_HIT_STREAM_OUTPUT_ABI_FIELDS,
        "hit_stream_columns": GENERIC_DEVICE_RESIDENT_HIT_STREAM_COLUMNS,
        "row_count_metadata": ("row_count:uint64", "capacity:uint64"),
        "overflow_policy": "fail_closed_bounded_columns",
        "ownership": "native_owner_state_machine_required_until_partner_continuation_finishes",
        "requires_native_release_entrypoint": True,
        "requires_same_pointer_no_host_stage_measurement": True,
        "current_optix_output_abi_proven_on_hardware": True,
        "current_runtime_ordering_state": "host_synchronized_before_consumer",
        "current_runtime_async_promotion_authorized": False,
        "requires_sm70_pod_validation_for_triton": True,
        "native_engine_app_specific_vocab_allowed": False,
        "host_row_materialization_allowed_for_promotion": False,
        "true_zero_copy_claim_authorized": False,
        "public_speedup_claim_authorized": False,
        "claim_boundary": (
            "This describes the native output ABI for v2.5 hit streams. The current "
            "OptiX implementation can return CUDA-resident hit-stream columns and has "
            "pod evidence, but it synchronizes before returning host-visible row-count "
            "metadata. Event/same-stream ordering and device-resident counters are still "
            "required before async partner promotion or true zero-copy wording."
        ),
    }


def describe_v2_5_hit_stream_async_promotion_requirements() -> dict[str, object]:
    """Describe the missing pieces before hit-stream continuations can be async.

    This is a fail-closed design surface. It is intentionally separate from the
    current host-synchronized runtime path so reports and partner code cannot
    confuse reusable CUDA output buffers with a proven event/same-stream handoff.
    """

    return {
        "contract_version": GENERIC_HIT_STREAM_ASYNC_PROMOTION_REQUIREMENTS_VERSION,
        "hit_stream_handoff_contract_version": GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION,
        "partner_transfer_plan_contract_version": GENERIC_HIT_STREAM_PARTNER_TRANSFER_PLAN_VERSION,
        "current_runtime_ordering_state": "host_synchronized_before_consumer",
        "current_bounded_status_consumer_ordering_state": "same_stream",
        "current_runtime_async_promotion_authorized": False,
        "current_runtime_true_zero_copy_authorized": False,
        "current_runtime_public_speedup_claim_authorized": False,
        "current_runtime_row_count_scalar_visibility": "host_visible_after_producer_synchronization",
        "current_runtime_overflow_scalar_visibility": "host_visible_after_producer_synchronization",
        "current_runtime_has_completion_event_handle": False,
        "current_runtime_has_same_stream_handle": True,
        "current_runtime_has_device_resident_row_count_for_partner": True,
        "current_runtime_has_device_resident_overflow_for_partner": True,
        "current_runtime_has_bounded_same_stream_status_consumer": True,
        "bounded_same_stream_status_consumer_scope": "OptiX hit-stream status summary with CuPy RawKernel",
        "general_async_partner_continuation_authorized": False,
        "zero_copy_compatible_ordering_states": GENERIC_HIT_STREAM_ZERO_COPY_COMPATIBLE_STREAM_ORDERING_STATES,
        "required_native_abi_extensions": (
            "producer_stream_handle_or_same_stream_token",
            "completion_event_handle_with_lifetime_owner",
            "device_resident_row_count_ptr",
            "device_resident_overflow_ptr",
            "fail_closed_overflow_flag_visible_to_partner",
            "explicit_release_for_event_and_temporary_counter_storage",
        ),
        "required_python_carrier_fields": (
            "producer_stream_identity",
            "completion_event_identity",
            "consumer_wait_contract",
            "row_count_device_column_or_bounded_capacity_contract",
            "overflow_device_flag_contract",
            "event_owner_lifetime_state",
        ),
        "required_partner_consumer_proofs": (
            "consumer_launches_on_same_stream_or_waits_on_recorded_event",
            "consumer_respects_bounded_capacity_without_host_row_count_read",
            "consumer_observes_overflow_fail_closed_flag_before_using_rows",
            "no_hidden_host_materialization_or_scalar_sync",
        ),
        "required_pod_validation": (
            "same-pointer hit-stream columns preserved",
            "no cuStreamSynchronize on the producer path before partner launch",
            "event_wait_or_same_stream ordering verified by a dependent consumer",
            "row_count_or_overflow consumed through device-resident state",
            "timing separates producer launch, event wait, continuation, and materialization",
        ),
        "forbidden_promotion_shortcuts": (
            "treating host_synchronized_before_consumer as zero-copy-compatible",
            "using reusable output buffers as async proof",
            "using host-visible row_count after cuStreamSynchronize as a device-resident counter",
            "authorizing public speedup from metadata alone",
        ),
        "claim_boundary": (
            "Current v2.5 hit-stream output can be CUDA-resident, reusable, and can drive "
            "a bounded same-stream CuPy status consumer without a producer-side host "
            "scalar sync. General async continuation, true zero-copy wording, and public "
            "speedup claims still require broader event/same-stream evidence."
        ),
    }


def prepare_native_device_hit_stream_columns_from_abi(
    *,
    ray_ids_device_ptr: int,
    primitive_ids_device_ptr: int,
    row_count: int,
    capacity: int,
    overflow: bool,
    hit_event_count: int = 0,
    device_id: int = 0,
    backend: str = "optix",
    native_symbol: str | None = None,
    owner_handle: int | None = None,
    owner: Any = None,
    traversal_seconds: float | None = None,
    native_device_column_output_proven_on_hardware: bool = False,
    producer_consumer_stream_ordering: str = "not_proven",
    row_count_device_ptr: int | None = None,
    hit_event_count_device_ptr: int | None = None,
    overflow_device_ptr: int | None = None,
) -> RtdlHitStreamColumnHandoff:
    native_output = RtdlNativeDeviceHitStreamOutput(
        ray_ids_device_ptr=ray_ids_device_ptr,
        primitive_ids_device_ptr=primitive_ids_device_ptr,
        row_count=row_count,
        capacity=capacity,
        overflow=overflow,
        hit_event_count=hit_event_count,
        device_id=device_id,
        backend=backend,
        native_symbol=native_symbol,
        owner_handle=owner_handle,
        owner=owner,
        traversal_seconds=traversal_seconds,
        native_device_column_output_proven_on_hardware=native_device_column_output_proven_on_hardware,
        producer_consumer_stream_ordering=producer_consumer_stream_ordering,
        row_count_device_ptr=row_count_device_ptr,
        hit_event_count_device_ptr=hit_event_count_device_ptr,
        overflow_device_ptr=overflow_device_ptr,
    )
    return native_output.to_handoff()


def prepare_generic_hit_stream_columns_from_rows(
    hit_stream: Mapping[str, Any],
    *,
    prefer_torch_cuda: bool = False,
    require_torch_cuda: bool = False,
) -> RtdlHitStreamColumnHandoff:
    if hit_stream.get("primitive") != GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_PRIMITIVE:
        raise ValueError("expected a generic ray/triangle hit-stream result")
    if tuple(hit_stream.get("row_schema", ())) != GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_ROW_SCHEMA:
        raise ValueError("unexpected generic hit-stream row schema")
    if bool(hit_stream.get("overflow", False)):
        raise ValueError("cannot prepare columns from an overflowed hit stream; failure mode is fail-closed")

    started = perf_counter()
    rows = tuple(hit_stream.get("rows", ()))
    ray_values = tuple(int(row["ray_id"]) for row in rows)
    primitive_values = tuple(int(row["primitive_id"]) for row in rows)
    ray_ids = _prepare_triton_tensor_carrier_column(
        ray_values,
        dtype="int64",
        prefer_cuda=prefer_torch_cuda,
        require_cuda=require_torch_cuda,
    )
    primitive_ids = _prepare_triton_tensor_carrier_column(
        primitive_values,
        dtype="int64",
        prefer_cuda=prefer_torch_cuda,
        require_cuda=require_torch_cuda,
    )
    elapsed = perf_counter() - started
    timings = dict(hit_stream.get("phase_timing_seconds", {}))
    timings["hit_stream_column_handoff"] = elapsed
    return RtdlHitStreamColumnHandoff(
        ray_ids=ray_ids,
        primitive_ids=primitive_ids,
        row_count=len(rows),
        capacity=int(hit_stream.get("max_rows", len(rows))),
        overflow=False,
        backend=str(hit_stream.get("backend", "unknown")),
        source_mode="host_rows_to_columns_bridge",
        phase_timing_seconds=timings,
        native_symbol=hit_stream.get("native_symbol"),
        materializes_host_rows_for_bridge=True,
        owner=hit_stream,
    )


def prepare_generic_device_resident_hit_stream_columns(
    *,
    ray_ids: Any,
    primitive_ids: Any,
    row_count: int | None = None,
    capacity: int | None = None,
    overflow: bool = False,
    backend: str = "optix",
    phase_timing_seconds: Mapping[str, float] | None = None,
    native_symbol: str | None = None,
    native_device_column_output_proven_on_hardware: bool = False,
    owner: Any = None,
    producer_consumer_stream_ordering: str = "not_proven",
    caller_owned_output_buffers: bool = False,
    reusable_output_buffers_used: bool = False,
    row_count_device_ptr: int | None = None,
    hit_event_count_device_ptr: int | None = None,
    overflow_device_ptr: int | None = None,
) -> RtdlHitStreamColumnHandoff:
    resolved_count = _column_length(primitive_ids) if row_count is None else int(row_count)
    return RtdlHitStreamColumnHandoff(
        ray_ids=ray_ids,
        primitive_ids=primitive_ids,
        row_count=resolved_count,
        capacity=resolved_count if capacity is None else int(capacity),
        overflow=bool(overflow),
        backend=backend,
        source_mode="native_device_columns",
        phase_timing_seconds={} if phase_timing_seconds is None else dict(phase_timing_seconds),
        native_symbol=native_symbol,
        materializes_host_rows_for_bridge=False,
        native_device_column_output_proven_on_hardware=bool(native_device_column_output_proven_on_hardware),
        owner=owner,
        producer_consumer_stream_ordering=producer_consumer_stream_ordering,
        caller_owned_output_buffers=bool(caller_owned_output_buffers),
        reusable_output_buffers_used=bool(reusable_output_buffers_used),
        row_count_device_ptr=row_count_device_ptr,
        hit_event_count_device_ptr=hit_event_count_device_ptr,
        overflow_device_ptr=overflow_device_ptr,
    )


def prepare_generic_typed_primitive_payload_columns(
    primitive_group_ids: Sequence[int] | Any,
    primitive_values: Sequence[float] | Any | None = None,
    *,
    primitive_count: int | None = None,
    group_count: int | None = None,
    prefer_torch_cuda: bool = False,
    require_torch_cuda: bool = False,
    device_like: Any = None,
    group_id_bounds_validation: str | None = None,
) -> RtdlTypedPrimitivePayloadColumns:
    if group_id_bounds_validation is None:
        group_id_bounds_validation = "host_scan"
    if group_id_bounds_validation not in GENERIC_TYPED_PAYLOAD_GROUP_ID_VALIDATION_MODES:
        raise ValueError("unsupported primitive group-id validation mode")
    if primitive_count is None:
        primitive_count = _column_length(primitive_group_ids)
    default_primitive_values_used = primitive_values is None
    if primitive_values is None:
        primitive_values = tuple(1.0 for _ in range(int(primitive_count)))
    if group_count is None:
        if group_id_bounds_validation != "host_scan":
            raise ValueError("group_count must be provided when primitive group ids are not host-scanned")
        group_count = max(_column_to_host_ints(primitive_group_ids), default=-1) + 1
    use_cuda = prefer_torch_cuda or _device_info(device_like)[0] == "cuda"
    group_ids = _prepare_triton_tensor_carrier_column(
        primitive_group_ids,
        dtype="int64",
        prefer_cuda=use_cuda,
        require_cuda=require_torch_cuda,
        device_like=device_like,
    )
    values = _prepare_triton_tensor_carrier_column(
        primitive_values,
        dtype="float64",
        prefer_cuda=use_cuda,
        require_cuda=require_torch_cuda,
        device_like=device_like,
    )
    return RtdlTypedPrimitivePayloadColumns(
        primitive_group_ids=group_ids,
        primitive_values=values,
        primitive_count=int(primitive_count),
        group_count=int(group_count),
        source_mode="typed_payload_columns",
        group_id_bounds_validation=group_id_bounds_validation,
        default_primitive_values_used=default_primitive_values_used,
        owner=(primitive_group_ids, primitive_values),
    )


def describe_v2_5_hit_stream_torch_carrier_adapter(
    hit_stream_columns: RtdlHitStreamColumnHandoff,
    payload_columns: RtdlTypedPrimitivePayloadColumns,
) -> dict[str, object]:
    """Explain whether hit-stream continuation columns can feed Triton.

    This is an explain surface, not a proof of zero-copy. Runtime execution still
    requires the actual torch/CuPy/DLPack libraries and accepted hardware.
    """

    column_specs = (
        ("primitive_ids", hit_stream_columns.primitive_ids, "int64"),
        ("primitive_group_ids", payload_columns.primitive_group_ids, "int64"),
        ("primitive_values", payload_columns.primitive_values, "float64"),
    )
    descriptors: list[dict[str, object]] = []
    for name, column, dtype in column_specs:
        mode = _torch_carrier_adapter_mode(column)
        descriptor = _buffer_descriptor(name, column, dtype, access_mode="read").to_metadata()
        descriptors.append(
            {
                "name": name,
                "required_dtype": dtype,
                "adapter_mode": mode,
                "device": descriptor["device"],
                "source_protocol": descriptor["source_protocol"],
                "data_ptr": _data_ptr(column),
                "host_copy_required": mode == "host_column_requires_explicit_copy",
                "zero_copy_candidate": mode in {"torch_tensor", "cuda_array_interface_to_torch_via_dlpack"},
            }
        )
    adapter_modes = tuple(str(descriptor["adapter_mode"]) for descriptor in descriptors)
    unsupported = any(mode == "unsupported" for mode in adapter_modes)
    host_copy_required = any(mode == "host_column_requires_explicit_copy" for mode in adapter_modes)
    raw_cuda_adapter_required = any(mode == "cuda_array_interface_to_torch_via_dlpack" for mode in adapter_modes)
    no_copy_candidate = not unsupported and not host_copy_required
    return {
        "contract_version": GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION,
        "neutral_seam_reconciliation_version": GENERIC_HIT_STREAM_NEUTRAL_SEAM_RECONCILIATION_VERSION,
        "neutral_buffer_seam_contract_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
        "adapter_modes": GENERIC_TORCH_CARRIER_ADAPTER_MODES,
        "columns": tuple(descriptors),
        "all_columns_adaptable_to_torch_carrier": not unsupported,
        "all_columns_no_copy_torch_carrier_candidates": no_copy_candidate,
        "raw_cuda_adapter_required": raw_cuda_adapter_required,
        "requires_torch_runtime": True,
        "requires_cupy_for_cuda_array_interface_without_dlpack": raw_cuda_adapter_required,
        "support_matrix_is_authority": True,
        "torch_is_neutral_protocol": False,
        "torch_carrier_allowed_only_for_partner": "triton",
        "silent_cross_partner_torch_coercion_allowed": False,
        "host_copy_required": host_copy_required,
        "explicit_copy_required": host_copy_required,
        "torch_carrier_copy_diagnostics_are_advisory": True,
        "carrier_metadata_scope": "triton_launch_carrier_only",
        "authoritative_metadata_origin": "neutral_buffer_seam_only",
        "adapter_execution_proven_on_hardware": False,
        "true_zero_copy_authorized": False,
        "public_speedup_claim_authorized": False,
        "claim_boundary": (
            "This explains the torch/Triton carrier bridge for hit-stream continuation. "
            "Raw CUDA-array columns are only no-copy candidates until pod evidence proves "
            "same-pointer DLPack/CUDA-array-interface adaptation without a host stage."
        ),
    }


def describe_v2_5_hit_stream_neutral_seam_reconciliation() -> dict[str, object]:
    """Describe how the neutral seam bounds legacy Torch carrier helpers."""

    return {
        "contract_version": GENERIC_HIT_STREAM_NEUTRAL_SEAM_RECONCILIATION_VERSION,
        "hit_stream_handoff_contract_version": GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION,
        "partner_transfer_plan_contract_version": GENERIC_HIT_STREAM_PARTNER_TRANSFER_PLAN_VERSION,
        "neutral_buffer_seam_contract_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
        "support_matrix_is_authority": True,
        "torch_is_neutral_protocol": False,
        "torch_is_partner": False,
        "torch_carrier_allowed_only_for_partners": ("triton",),
        "torch_carrier_protocols": ("torch_tensor_carrier", "cuda_array_interface_to_torch_carrier"),
        "non_triton_device_carrier_protocol": "cuda_array_interface_descriptor",
        "silent_cross_partner_torch_coercion_allowed": False,
        "neutral_seam_authority_enforced": True,
        "transfer_copy_lifetime_authority": "neutral_buffer_seam",
        "torch_carrier_forbidden_authority_fields": GENERIC_HIT_STREAM_TORCH_CARRIER_FORBIDDEN_AUTHORITY_FIELDS,
        "torch_carrier_copy_diagnostics_are_advisory": True,
        "legacy_torch_helper_status": "bounded_triton_launch_carrier_not_neutral_seam",
        "partner_choice_policy": "explicit_per_boundary_app_choice",
        "claim_boundary": (
            "The neutral buffer seam is the authority for transfer/copy/lifetime metadata. "
            "Torch may be used only as a Triton tensor carrier and must not become a "
            "hidden neutral protocol, forced partner, zero-copy proof, or public speedup claim."
        ),
    }


def validate_v2_5_hit_stream_neutral_seam_authority(
    hit_stream_columns: RtdlHitStreamColumnHandoff | None = None,
    payload_columns: RtdlTypedPrimitivePayloadColumns | None = None,
) -> dict[str, object]:
    """Validate that torch-carrier metadata cannot become seam authority."""

    if hit_stream_columns is None or payload_columns is None:
        sample_hit_stream = {
            "primitive": GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_PRIMITIVE,
            "row_schema": GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_ROW_SCHEMA,
            "rows": ({"ray_id": 0, "primitive_id": 1}, {"ray_id": 1, "primitive_id": 0}),
            "max_rows": 2,
            "backend": "reference",
            "overflow": False,
            "phase_timing_seconds": {},
        }
        hit_stream_columns = prepare_generic_hit_stream_columns_from_rows(sample_hit_stream)
        payload_columns = prepare_generic_typed_primitive_payload_columns(
            [0, 1],
            [10.0, 20.0],
            group_count=2,
        )

    contract = describe_v2_5_hit_stream_neutral_seam_reconciliation()
    adapter = describe_v2_5_hit_stream_torch_carrier_adapter(hit_stream_columns, payload_columns)
    runtime_trace = trace_v2_5_hit_stream_torch_carrier_runtime_seam_authority(
        hit_stream_columns,
        payload_columns,
        executed=False,
    )
    hit_metadata = hit_stream_columns.to_metadata()
    payload_metadata = payload_columns.to_metadata()
    seams = (
        *hit_metadata["neutral_buffer_seams"],
        *payload_metadata["neutral_buffer_seams"],
    )
    forbidden_fields = GENERIC_HIT_STREAM_TORCH_CARRIER_FORBIDDEN_AUTHORITY_FIELDS
    forbidden_hits = tuple(_metadata_key_hits(adapter, forbidden_fields))
    seam_required_fields = (
        "transfer_status",
        "copy_status",
        "lifetime_state",
        "zero_copy_claim_authorized",
    )
    missing_seam_fields = tuple(
        field for field in seam_required_fields if not all(field in seam for seam in seams)
    )
    errors: list[str] = []
    if contract["transfer_copy_lifetime_authority"] != "neutral_buffer_seam":
        errors.append("neutral seam must be the transfer/copy/lifetime authority")
    if forbidden_hits:
        errors.append("torch carrier metadata contains forbidden authority fields")
    if missing_seam_fields:
        errors.append("neutral seams are missing required authority fields")
    if adapter["torch_carrier_allowed_only_for_partner"] != "triton":
        errors.append("torch carrier must remain Triton-only")
    if adapter["torch_is_neutral_protocol"] is not False:
        errors.append("torch must not become a neutral protocol")
    if adapter["true_zero_copy_authorized"] is not False:
        errors.append("torch carrier adapter must not authorize true zero-copy")
    if adapter["carrier_metadata_scope"] != "triton_launch_carrier_only":
        errors.append("torch carrier adapter must remain launch-carrier scoped")
    if adapter["authoritative_metadata_origin"] != "neutral_buffer_seam_only":
        errors.append("torch carrier adapter must not originate transfer/copy/lifetime metadata")
    if runtime_trace["status"] != "accept":
        errors.append("runtime seam authority trace did not validate")
    return {
        "status": "accept" if not errors else "reject",
        "contract_version": GENERIC_HIT_STREAM_NEUTRAL_SEAM_RECONCILIATION_VERSION,
        "neutral_buffer_seam_contract_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
        "transfer_copy_lifetime_authority": contract["transfer_copy_lifetime_authority"],
        "torch_carrier_forbidden_authority_fields": forbidden_fields,
        "torch_carrier_forbidden_authority_field_hits": forbidden_hits,
        "neutral_seam_required_authority_fields": seam_required_fields,
        "neutral_seam_missing_authority_fields": missing_seam_fields,
        "neutral_seam_count": len(seams),
        "torch_carrier_allowed_only_for_partner": adapter["torch_carrier_allowed_only_for_partner"],
        "torch_is_neutral_protocol": adapter["torch_is_neutral_protocol"],
        "torch_carrier_metadata_scope": adapter["carrier_metadata_scope"],
        "torch_carrier_authoritative_metadata_origin": adapter["authoritative_metadata_origin"],
        "runtime_seam_authority_trace_status": runtime_trace["status"],
        "runtime_seam_authority_trace": runtime_trace,
        "true_zero_copy_authorized": adapter["true_zero_copy_authorized"],
        "public_speedup_claim_authorized": adapter["public_speedup_claim_authorized"],
        "errors": tuple(errors),
    }


def gather_typed_payload_columns_for_hit_stream(
    hit_stream_columns: RtdlHitStreamColumnHandoff,
    payload_columns: RtdlTypedPrimitivePayloadColumns,
    *,
    partner: str = "auto",
    allow_explicit_copy: bool = False,
) -> tuple[dict[str, Any], dict[str, object]]:
    if hit_stream_columns.overflow:
        raise ValueError("cannot gather continuation inputs from an overflowed hit stream")
    gather_partner = _normalize_gather_partner(partner)
    started = perf_counter()
    torch_carrier_adapter = describe_v2_5_hit_stream_torch_carrier_adapter(
        hit_stream_columns,
        payload_columns,
    )
    if gather_partner == "python_reference":
        torch_carrier_execution: dict[str, object] | None = None
        _validate_primitive_ids_in_payload_range(
            hit_stream_columns.primitive_ids,
            payload_columns.primitive_count,
        )
        continuation_inputs, gather_mode, selected_partner = _gather_payload_python_reference(
            hit_stream_columns,
            payload_columns,
        )
    elif gather_partner == "triton":
        if (
            not bool(torch_carrier_adapter["all_columns_no_copy_torch_carrier_candidates"])
            and not allow_explicit_copy
        ):
            raise ValueError(
                "triton gather requires torch tensor carrier columns or CUDA-array-interface columns; "
                "pass allow_explicit_copy=True only when the host/device copy is explicit"
            )
        if (
            bool(torch_carrier_adapter["raw_cuda_adapter_required"])
            and not bool(hit_stream_columns.native_device_column_output_proven_on_hardware)
            and not _all_torch_gather_columns(hit_stream_columns, payload_columns)
        ):
            raise ValueError(
                "triton gather requires existing torch tensor carrier columns or "
                "hardware-proven native CUDA-array-interface columns"
            )
        _validate_primitive_ids_in_payload_range(
            hit_stream_columns.primitive_ids,
            payload_columns.primitive_count,
            prefer_torch_carrier=True,
            allow_explicit_copy=allow_explicit_copy,
        )
        (
            continuation_inputs,
            gather_mode,
            selected_partner,
            torch_carrier_execution,
        ) = _gather_payload_torch_carrier(
            hit_stream_columns,
            payload_columns,
            allow_explicit_copy=allow_explicit_copy,
        )
    elif gather_partner in {"cupy_conformance", "numba"}:
        torch_carrier_execution = None
        _validate_primitive_ids_in_payload_range(
            hit_stream_columns.primitive_ids,
            payload_columns.primitive_count,
        )
        raise ValueError(
            f"{gather_partner} hit-stream gather is descriptor/planning-only in this slice; "
            "use plan_v2_5_hit_stream_partner_continuation before execution"
        )
    elif _is_torch_tensor(hit_stream_columns.primitive_ids) or _is_torch_tensor(payload_columns.primitive_group_ids):
        _validate_primitive_ids_in_payload_range(
            hit_stream_columns.primitive_ids,
            payload_columns.primitive_count,
            prefer_torch_carrier=True,
            allow_explicit_copy=allow_explicit_copy,
        )
        (
            continuation_inputs,
            gather_mode,
            selected_partner,
            torch_carrier_execution,
        ) = _gather_payload_torch_carrier(
            hit_stream_columns,
            payload_columns,
            allow_explicit_copy=allow_explicit_copy,
        )
    else:
        torch_carrier_execution = None
        _validate_primitive_ids_in_payload_range(
            hit_stream_columns.primitive_ids,
            payload_columns.primitive_count,
        )
        continuation_inputs, gather_mode, selected_partner = _gather_payload_python_reference(
            hit_stream_columns,
            payload_columns,
        )
    elapsed = perf_counter() - started
    metadata = {
        "contract_version": GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION,
        "gather_mode": gather_mode,
        "requested_gather_partner": gather_partner,
        "selected_gather_partner": selected_partner,
        "explicit_partner_choice": gather_partner != "auto",
        "allow_explicit_copy": bool(allow_explicit_copy),
        "hit_stream_columns": hit_stream_columns.to_metadata(),
        "typed_primitive_payload_columns": payload_columns.to_metadata(),
        "row_count": int(hit_stream_columns.row_count),
        "group_count": int(payload_columns.group_count),
        "typed_payload_gather_sec": elapsed,
        "primitive_id_bounds_checked": True,
        "python_rebuilt_primitive_row_table": False,
        "materializes_host_rows_for_bridge": bool(hit_stream_columns.materializes_host_rows_for_bridge),
        "host_hit_rows_materialized_before_handoff": bool(hit_stream_columns.materializes_host_rows_for_bridge),
        "native_device_hit_stream_columns_ready": hit_stream_columns.source_mode == "native_device_columns",
        "native_device_column_output_proven_on_hardware": bool(
            hit_stream_columns.native_device_column_output_proven_on_hardware
        ),
        "removes_host_materialization_bottleneck": hit_stream_columns.removes_host_materialization_bottleneck,
        "neutral_buffer_seam_contract_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
        "neutral_buffer_handoff_summary": _neutral_buffer_handoff_summary(
            hit_stream_columns,
            payload_columns,
        ),
        "torch_carrier_adapter": torch_carrier_adapter,
        "torch_carrier_execution": torch_carrier_execution,
        "true_zero_copy_authorized": False,
        "public_speedup_claim_authorized": False,
    }
    return continuation_inputs, metadata


def _gather_payload_torch_carrier(
    hit_stream_columns: RtdlHitStreamColumnHandoff,
    payload_columns: RtdlTypedPrimitivePayloadColumns,
    *,
    allow_explicit_copy: bool = False,
) -> tuple[dict[str, Any], str, str, dict[str, object]]:
    adapter = describe_v2_5_hit_stream_torch_carrier_adapter(hit_stream_columns, payload_columns)
    if not bool(adapter["all_columns_adaptable_to_torch_carrier"]):
        raise ValueError("torch carrier gather requested but at least one column is not adaptable")
    if bool(adapter["host_copy_required"]) and not allow_explicit_copy:
        raise ValueError("torch carrier gather would require a host/device copy; pass allow_explicit_copy=True")

    try:
        import torch
    except Exception as exc:
        raise ValueError(
            "torch carrier gather requires existing torch tensor carrier columns or a working "
            "CUDA-array-interface adapter with torch runtime"
        ) from exc

    (
        primitive_ids_descriptor,
        group_ids_descriptor,
        values_descriptor,
    ) = _torch_carrier_gather_neutral_seam_descriptors(hit_stream_columns, payload_columns)
    primitive_ids, primitive_lease_record = _torch_as_under_neutral_seam_lease(
        primitive_ids_descriptor,
        hit_stream_columns.primitive_ids,
        dtype=torch.int64,
        device_like=payload_columns.primitive_group_ids,
        allow_explicit_copy=allow_explicit_copy,
    )
    group_ids_carrier_source, group_ids_lease_record = _torch_as_under_neutral_seam_lease(
        group_ids_descriptor,
        payload_columns.primitive_group_ids,
        dtype=torch.int64,
        device_like=primitive_ids,
        allow_explicit_copy=allow_explicit_copy,
    )
    group_ids = group_ids_carrier_source[primitive_ids]
    values_carrier_source, values_lease_record = _torch_as_under_neutral_seam_lease(
        values_descriptor,
        payload_columns.primitive_values,
        dtype=torch.float64,
        device_like=primitive_ids,
        allow_explicit_copy=allow_explicit_copy,
    )
    values = values_carrier_source[primitive_ids]
    primitive_ids_input_ptr = _data_ptr(hit_stream_columns.primitive_ids)
    primitive_ids_carrier_ptr = _data_ptr(primitive_ids)
    group_ids_input_ptr = _data_ptr(payload_columns.primitive_group_ids)
    group_ids_carrier_ptr = _data_ptr(group_ids_carrier_source)
    values_input_ptr = _data_ptr(payload_columns.primitive_values)
    values_carrier_ptr = _data_ptr(values_carrier_source)
    primitive_ids_same_pointer = primitive_ids_input_ptr is not None and primitive_ids_input_ptr == primitive_ids_carrier_ptr
    group_ids_same_pointer = group_ids_input_ptr is not None and group_ids_input_ptr == group_ids_carrier_ptr
    values_same_pointer = values_input_ptr is not None and values_input_ptr == values_carrier_ptr
    same_pointer_evidence_observed = (
        primitive_ids_same_pointer and group_ids_same_pointer and values_same_pointer
    )
    adapter_execution_proven_on_hardware = bool(
        same_pointer_evidence_observed
        and _device_info(primitive_ids)[0] == "cuda"
        and _device_info(group_ids_carrier_source)[0] == "cuda"
        and _device_info(values_carrier_source)[0] == "cuda"
        and not bool(adapter["host_copy_required"])
    )
    execution_metadata = {
        "executed": True,
        "adapter_execution_proven_on_hardware": adapter_execution_proven_on_hardware,
        "neutral_seam_runtime_authority_trace": _neutral_seam_runtime_trace_from_lease_records(
            adapter,
            (
                primitive_lease_record,
                group_ids_lease_record,
                values_lease_record,
            ),
            executed=True,
        ),
        "primitive_ids_input_data_ptr": primitive_ids_input_ptr,
        "primitive_ids_carrier_data_ptr": primitive_ids_carrier_ptr,
        "primitive_ids_same_pointer_as_input": primitive_ids_same_pointer,
        "primitive_group_ids_input_data_ptr": group_ids_input_ptr,
        "primitive_group_ids_carrier_data_ptr": group_ids_carrier_ptr,
        "primitive_group_ids_same_pointer_as_input": group_ids_same_pointer,
        "primitive_values_input_data_ptr": values_input_ptr,
        "primitive_values_carrier_data_ptr": values_carrier_ptr,
        "primitive_values_same_pointer_as_input": values_same_pointer,
        "any_host_copy_required": bool(adapter["host_copy_required"]),
        "raw_cuda_adapter_required": bool(adapter["raw_cuda_adapter_required"]),
        "same_pointer_evidence_observed": same_pointer_evidence_observed,
        "true_zero_copy_authorized": False,
        "claim_boundary": (
            "Pointer equality is runtime evidence for the adapter only. It does not "
            "authorize true zero-copy or speedup claims without accepted pod review."
        ),
    }
    gather_mode = (
        "torch_index_select_cuda_array_interface_adapter"
        if bool(adapter["raw_cuda_adapter_required"])
        else "torch_index_select"
    )
    return {
        "group_ids": group_ids,
        "values": values,
        "group_count": int(payload_columns.group_count),
    }, gather_mode, "triton_torch_tensor_carrier", execution_metadata


def trace_v2_5_hit_stream_torch_carrier_runtime_seam_authority(
    hit_stream_columns: RtdlHitStreamColumnHandoff,
    payload_columns: RtdlTypedPrimitivePayloadColumns,
    *,
    executed: bool = False,
) -> dict[str, object]:
    """Trace seam lease transitions for the bounded Triton torch carrier.

    This is deliberately narrow: it records the neutral-buffer lease transitions
    for the columns consumed by the Triton carrier path. It does not allocate,
    copy, free, or prove zero-copy; it makes the runtime authority path explicit
    enough for review and tests.
    """

    adapter = describe_v2_5_hit_stream_torch_carrier_adapter(hit_stream_columns, payload_columns)
    descriptors = _torch_carrier_gather_neutral_seam_descriptors(
        hit_stream_columns,
        payload_columns,
    )
    lease_records: list[dict[str, object]] = []
    errors: list[str] = []

    for descriptor in descriptors:
        try:
            lease = create_neutral_buffer_lease(descriptor)
            borrowed = lease.begin_partner_borrow()
            completed = borrowed.complete_partner_borrow()
        except ValueError as exc:
            errors.append(f"{descriptor.buffer.name}: {exc}")
            continue
        lease_records.append(
            _neutral_seam_lease_record(
                completed,
                conversion_executed_under_seam_lease=False,
            )
        )

    return _neutral_seam_runtime_trace_from_lease_records(
        adapter,
        tuple(lease_records),
        executed=executed,
        existing_errors=tuple(errors),
    )


def _neutral_seam_runtime_trace_from_lease_records(
    adapter: Mapping[str, object],
    lease_records: Sequence[Mapping[str, object]],
    *,
    executed: bool,
    existing_errors: Sequence[str] = (),
) -> dict[str, object]:
    errors = list(existing_errors)

    if adapter["carrier_metadata_scope"] != "triton_launch_carrier_only":
        errors.append("torch carrier metadata scope is not launch-carrier-only")
    if adapter["authoritative_metadata_origin"] != "neutral_buffer_seam_only":
        errors.append("torch carrier authoritative metadata origin is not seam-only")
    if any(record["event_log"] != ("handoff_begin", "continuation_complete") for record in lease_records):
        errors.append("neutral seam leases did not record handoff_begin -> continuation_complete")
    if len(lease_records) != 3:
        errors.append("not all torch-carrier gather columns produced seam lease records")
    copy_decision_wrapped = bool(
        executed
        and lease_records
        and all(bool(record.get("conversion_executed_under_seam_lease")) for record in lease_records)
    )
    if executed and not copy_decision_wrapped:
        errors.append("executed torch-carrier conversions were not wrapped by seam leases")

    return {
        "contract_version": GENERIC_HIT_STREAM_NEUTRAL_SEAM_RECONCILIATION_VERSION,
        "neutral_buffer_seam_contract_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
        "status": "accept" if not errors else "reject",
        "executed": bool(executed),
        "trace_scope": "triton_torch_carrier_gather_columns",
        "carrier_metadata_scope": adapter["carrier_metadata_scope"],
        "authoritative_metadata_origin": adapter["authoritative_metadata_origin"],
        "authority_origin": "neutral_buffer_seam",
        "lease_count": len(lease_records),
        "lease_records": tuple(lease_records),
        "all_leases_completed": not errors
        and all(record["final_state"] == record["owner_state"] for record in lease_records),
        "copy_decision_wrapped_by_seam_lease": copy_decision_wrapped,
        "carrier_authority_disallowed_by_contract": True,
        "true_zero_copy_authorized": False,
        "public_speedup_claim_authorized": False,
        "errors": tuple(errors),
        "claim_boundary": (
            "This trace records neutral-seam lease transitions around the bounded "
            "Triton torch-carrier gather path. It is runtime provenance evidence, "
            "not a zero-copy, speedup, or release claim."
        ),
    }


def _neutral_seam_lease_record(
    lease: Any,
    *,
    conversion_executed_under_seam_lease: bool,
) -> dict[str, object]:
    record = lease.to_metadata()
    return {
        "buffer_name": record["buffer_name"],
        "producer": record["producer"],
        "consumer": record["consumer"],
        "owner_state": record["owner_state"],
        "final_state": record["state"],
        "retain_until": record["retain_until"],
        "event_log": record["event_log"],
        "authority_origin": "neutral_buffer_seam",
        "conversion_executed_under_seam_lease": bool(conversion_executed_under_seam_lease),
        "carrier_authority_disallowed_by_contract": True,
        "true_zero_copy_authorized": False,
        "public_speedup_claim_authorized": False,
    }


def _torch_as_under_neutral_seam_lease(
    descriptor: Any,
    value: Any,
    *,
    dtype: Any,
    device_like: Any,
    allow_explicit_copy: bool,
) -> tuple[Any, dict[str, object]]:
    lease = create_neutral_buffer_lease(descriptor)
    borrowed = lease.begin_partner_borrow()
    try:
        tensor = _torch_as(
            value,
            dtype=dtype,
            device_like=device_like,
            allow_explicit_copy=allow_explicit_copy,
        )
    except Exception:
        borrowed.failure_cleanup()
        raise
    completed = borrowed.complete_partner_borrow()
    return tensor, _neutral_seam_lease_record(
        completed,
        conversion_executed_under_seam_lease=True,
    )


def _gather_payload_python_reference(
    hit_stream_columns: RtdlHitStreamColumnHandoff,
    payload_columns: RtdlTypedPrimitivePayloadColumns,
) -> tuple[dict[str, Any], str, str]:
    primitive_ids = _column_to_host_ints(hit_stream_columns.primitive_ids)
    group_source = tuple(int(value) for value in payload_columns.primitive_group_ids)
    value_source = tuple(float(value) for value in payload_columns.primitive_values)
    return {
        "group_ids": tuple(group_source[index] for index in primitive_ids),
        "values": tuple(value_source[index] for index in primitive_ids),
        "group_count": int(payload_columns.group_count),
    }, "python_reference_columns", "python_reference"


def plan_v2_5_hit_stream_partner_transfer(
    hit_stream_columns: RtdlHitStreamColumnHandoff,
    payload_columns: RtdlTypedPrimitivePayloadColumns,
    *,
    operation: str,
    partner: str,
) -> dict[str, object]:
    """Explain the buffer transfer/carrier boundary for a partner continuation.

    This is deliberately stricter than the execution helpers: every partner
    gets an explicit carrier/status row, and unsupported or descriptor-only
    choices fail closed instead of silently routing through another partner.
    """

    support = plan_v2_5_partner_support(operation, partner)
    hit_metadata = hit_stream_columns.to_metadata()
    payload_metadata = payload_columns.to_metadata()
    summary = _neutral_buffer_handoff_summary(hit_stream_columns, payload_columns)
    seams = (
        *hit_metadata["neutral_buffer_seams"],
        *payload_metadata["neutral_buffer_seams"],
    )
    device_ready = _all_seams_device_ready(seams)
    any_host_stage = bool(summary["any_host_stage"])
    any_device_resident = any(bool(seam["device_resident"]) for seam in seams)
    producer_consumer_stream_ordering = str(hit_metadata["producer_consumer_stream_ordering"])
    stream_synchronization_proven = bool(hit_metadata["stream_synchronization_proven"])
    host_synchronization_used = bool(hit_metadata["host_synchronization_used"])
    zero_copy_compatible_stream_ordering = bool(hit_metadata["zero_copy_compatible_stream_ordering"])
    async_partner_continuation_authorized = bool(hit_metadata["async_partner_continuation_authorized"])
    torch_carrier_adapter = describe_v2_5_hit_stream_torch_carrier_adapter(
        hit_stream_columns,
        payload_columns,
    )
    selected_partner = str(support["partner"])
    device_partner_requested = selected_partner in {"triton", "cupy_conformance", "numba"}
    device_consumer_requires_stream_ordering = bool(device_partner_requested and device_ready)
    stream_ordering_blocks_device_consumer = bool(
        device_consumer_requires_stream_ordering and not stream_synchronization_proven
    )

    status = "unsupported_fail_closed"
    carrier_protocol = "none"
    descriptor_only = False
    executable_preview_available = False
    execution_allowed_without_copy = False
    copy_or_host_stage_required = False
    runtime_action = "fail_closed_unsupported_partner_operation"

    if bool(support["supported"]):
        if selected_partner == "python_reference":
            carrier_protocol = "host_columns"
            if any_device_resident or any_host_stage:
                status = "explicit_host_materialization_required"
                copy_or_host_stage_required = True
                runtime_action = "cpu_reference_requires_explicit_host_materialization"
            else:
                status = "host_reference_ready"
                execution_allowed_without_copy = True
                runtime_action = "plan_available"
        elif selected_partner == "triton":
            if not device_ready:
                status = "explicit_host_materialization_required"
                carrier_protocol = "torch_tensor_carrier"
                copy_or_host_stage_required = True
                runtime_action = "requires_device_resident_columns_or_explicit_copy"
            elif stream_ordering_blocks_device_consumer:
                status = "stream_ordering_proof_required"
                carrier_protocol = (
                    "cuda_array_interface_to_torch_carrier"
                    if bool(torch_carrier_adapter["raw_cuda_adapter_required"])
                    else "torch_tensor_carrier"
                )
                runtime_action = "requires_stream_ordering_proof_before_device_consumer"
            elif bool(torch_carrier_adapter["raw_cuda_adapter_required"]):
                status = "torch_carrier_preview"
                carrier_protocol = "cuda_array_interface_to_torch_carrier"
                executable_preview_available = True
                execution_allowed_without_copy = True
                runtime_action = "requires_torch_cuda_array_interface_adapter_and_pod_validation"
            else:
                status = "torch_carrier_preview"
                carrier_protocol = "torch_tensor_carrier"
                executable_preview_available = True
                execution_allowed_without_copy = True
                runtime_action = "requires_sm70_pod_validation_before_performance_claim"
        elif selected_partner == "cupy_conformance":
            if not device_ready:
                status = "explicit_host_materialization_required"
                carrier_protocol = "cuda_array_interface_descriptor"
                copy_or_host_stage_required = True
                runtime_action = "requires_device_resident_columns_or_explicit_copy"
            elif stream_ordering_blocks_device_consumer:
                status = "stream_ordering_proof_required"
                carrier_protocol = "cuda_array_interface_descriptor"
                runtime_action = "requires_stream_ordering_proof_before_device_consumer"
            elif support["status"] == "preview_not_promoted":
                status = "cuda_descriptor_preview"
                carrier_protocol = "cuda_array_interface_descriptor"
                executable_preview_available = True
                execution_allowed_without_copy = True
                runtime_action = "cupy_preview_requires_explicit_runtime_validation"
            else:
                status = "descriptor_only"
                carrier_protocol = "cuda_array_interface_descriptor"
                descriptor_only = True
                execution_allowed_without_copy = True
                runtime_action = "descriptor_only_no_generic_kernel_execution"
        elif selected_partner == "numba":
            if not device_ready:
                status = "explicit_host_materialization_required"
                carrier_protocol = "cuda_array_interface_descriptor"
                copy_or_host_stage_required = True
                runtime_action = "requires_device_resident_columns_or_explicit_copy"
            elif stream_ordering_blocks_device_consumer:
                status = "stream_ordering_proof_required"
                carrier_protocol = "cuda_array_interface_descriptor"
                runtime_action = "requires_stream_ordering_proof_before_device_consumer"
            else:
                status = "cuda_descriptor_preview"
                carrier_protocol = "cuda_array_interface_descriptor"
                executable_preview_available = True
                execution_allowed_without_copy = True
                runtime_action = "numba_preview_requires_explicit_runtime_validation"

    if status not in GENERIC_HIT_STREAM_PARTNER_TRANSFER_STATUSES:
        raise ValueError("unsupported hit-stream partner transfer status")
    if carrier_protocol not in GENERIC_HIT_STREAM_PARTNER_CARRIER_PROTOCOLS:
        raise ValueError("unsupported hit-stream partner carrier protocol")

    return {
        "contract_version": GENERIC_HIT_STREAM_PARTNER_TRANSFER_PLAN_VERSION,
        "hit_stream_handoff_contract_version": GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION,
        "neutral_seam_reconciliation_version": GENERIC_HIT_STREAM_NEUTRAL_SEAM_RECONCILIATION_VERSION,
        "neutral_buffer_seam_contract_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
        "operation": str(operation),
        "requested_partner": str(partner),
        "selected_partner": selected_partner,
        "status": status,
        "carrier_protocol": carrier_protocol,
        "descriptor_only": bool(descriptor_only),
        "executable_preview_available": bool(executable_preview_available),
        "execution_allowed_without_copy": bool(execution_allowed_without_copy),
        "copy_or_host_stage_required": bool(copy_or_host_stage_required),
        "silent_copy_forbidden": True,
        "support_matrix_is_authority": True,
        "torch_is_neutral_protocol": False,
        "torch_carrier_allowed": selected_partner == "triton",
        "silent_cross_partner_torch_coercion_allowed": False,
        "current_inputs_device_ready": bool(device_ready),
        "any_host_stage": any_host_stage,
        "any_device_resident": bool(any_device_resident),
        "producer_consumer_stream_ordering": producer_consumer_stream_ordering,
        "stream_synchronization_proven": stream_synchronization_proven,
        "host_synchronization_used": host_synchronization_used,
        "zero_copy_compatible_stream_ordering": zero_copy_compatible_stream_ordering,
        "row_count_scalar_visibility": hit_metadata["row_count_scalar_visibility"],
        "overflow_scalar_visibility": hit_metadata["overflow_scalar_visibility"],
        "device_resident_row_count_for_partner": bool(hit_metadata["device_resident_row_count_for_partner"]),
        "device_resident_hit_event_count_for_partner": bool(
            hit_metadata["device_resident_hit_event_count_for_partner"]
        ),
        "device_resident_overflow_for_partner": bool(hit_metadata["device_resident_overflow_for_partner"]),
        "device_resident_status_for_partner": bool(hit_metadata["device_resident_status_for_partner"]),
        "completion_event_handle_available": bool(hit_metadata["completion_event_handle_available"]),
        "same_stream_handle_available": bool(hit_metadata["same_stream_handle_available"]),
        "async_partner_continuation_authorized": async_partner_continuation_authorized,
        "device_consumer_requires_stream_ordering": device_consumer_requires_stream_ordering,
        "stream_ordering_blocks_device_consumer": stream_ordering_blocks_device_consumer,
        "stream_synchronization_required_for_zero_copy_claim": True,
        "true_zero_copy_authorized": False,
        "public_speedup_claim_authorized": False,
        "support_cell": support,
        "neutral_buffer_handoff_summary": summary,
        "torch_carrier_adapter": torch_carrier_adapter,
        "runtime_action": runtime_action,
        "claim_boundary": (
            "This plan records the chosen partner carrier and transfer status. "
            "It forbids silent copies and does not execute, prove true zero-copy, "
            "or authorize public performance claims."
        ),
    }


def plan_v2_5_hit_stream_partner_continuation(
    hit_stream_columns: RtdlHitStreamColumnHandoff,
    payload_columns: RtdlTypedPrimitivePayloadColumns,
    *,
    operation: str,
    partner: str,
) -> dict[str, object]:
    """Plan a v2.5 continuation over hit-stream/payload columns.

    This is a planning surface only. It combines the neutral buffer handoff
    metadata with the declared partner support matrix so apps can fail closed
    before they run an unsupported partner or silently pay for a copy.
    """

    support = plan_v2_5_partner_support(operation, partner)
    transfer_plan = plan_v2_5_hit_stream_partner_transfer(
        hit_stream_columns,
        payload_columns,
        operation=operation,
        partner=partner,
    )
    summary = _neutral_buffer_handoff_summary(hit_stream_columns, payload_columns)
    hit_metadata = hit_stream_columns.to_metadata()
    payload_metadata = payload_columns.to_metadata()
    seams = (
        *hit_metadata["neutral_buffer_seams"],
        *payload_metadata["neutral_buffer_seams"],
    )
    current_inputs_device_ready = all(
        seam["device_resident"] and seam["transfer_status"] != "host_stage"
        for seam in seams
    )
    requires_cuda = bool(support["requires_cuda"])
    requirements_satisfied = bool(support["supported"]) and (
        current_inputs_device_ready if requires_cuda else True
    )
    fail_closed = not bool(support["supported"])
    return {
        "contract_version": GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION,
        "neutral_seam_reconciliation_version": GENERIC_HIT_STREAM_NEUTRAL_SEAM_RECONCILIATION_VERSION,
        "neutral_buffer_seam_contract_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
        "operation": str(operation),
        "requested_partner": str(partner),
        "selected_partner": support["partner"],
        "support_cell": support,
        "partner_transfer_plan": transfer_plan,
        "neutral_buffer_handoff_summary": summary,
        "current_inputs_device_ready": current_inputs_device_ready,
        "current_inputs_satisfy_device_requirements": requirements_satisfied,
        "copy_or_host_stage_required": bool(summary["any_host_stage"]) or (
            requires_cuda and not current_inputs_device_ready
        ),
        "fail_closed": fail_closed,
        "execution_allowed_without_copy": requirements_satisfied and not summary["any_host_stage"],
        "pod_validation_required": bool(support["requires_sm70_plus"]),
        "true_zero_copy_authorized": False,
        "public_speedup_claim_authorized": False,
        "runtime_action": _partner_plan_runtime_action(
            support,
            current_inputs_device_ready=current_inputs_device_ready,
            any_host_stage=bool(summary["any_host_stage"]),
        ),
        "claim_boundary": (
            "This is a plan/explain record only. It does not execute the "
            "partner continuation, prove zero-copy, or authorize speedup claims."
        ),
    }


def _validate_primitive_ids_in_payload_range(
    primitive_ids: Any,
    primitive_count: int,
    *,
    prefer_torch_carrier: bool = False,
    allow_explicit_copy: bool = False,
) -> None:
    primitive_count = int(primitive_count)
    if primitive_count < 0:
        raise ValueError("primitive_count must be non-negative")
    if _column_length(primitive_ids) == 0:
        return
    if prefer_torch_carrier and (_is_torch_tensor(primitive_ids) or _has_cuda_array_interface(primitive_ids)):
        try:
            import torch
        except Exception as exc:
            raise ValueError(
                "triton gather requires existing torch tensor carrier columns or a working "
                "CUDA-array-interface adapter with torch runtime"
            ) from exc

        ids = _torch_as(
            primitive_ids,
            dtype=torch.int64,
            device_like=primitive_ids,
            allow_explicit_copy=allow_explicit_copy,
        )
        if bool(((ids < 0) | (ids >= primitive_count)).any().detach().cpu().item()):
            raise ValueError("primitive ids must be in [0, primitive_count)")
        return
    if _is_torch_tensor(primitive_ids):
        import torch

        ids = primitive_ids.to(dtype=torch.int64)
        if bool(((ids < 0) | (ids >= primitive_count)).any().detach().cpu().item()):
            raise ValueError("primitive ids must be in [0, primitive_count)")
        return
    ids = _column_to_host_ints(primitive_ids)
    if any(primitive_id < 0 or primitive_id >= primitive_count for primitive_id in ids):
        raise ValueError("primitive ids must be in [0, primitive_count)")


def _column_length(column: Any) -> int:
    if column is None:
        return 0
    shape = getattr(column, "shape", None)
    if shape is not None:
        if len(shape) == 0:
            raise ValueError("hit-stream handoff columns must be one-dimensional")
        return int(shape[0])
    return len(column)


def _column_to_host_ints(column: Any) -> tuple[int, ...]:
    if column is None:
        return ()
    if _is_torch_tensor(column):
        return tuple(int(value) for value in column.detach().cpu().tolist())
    tolist = getattr(column, "tolist", None)
    if callable(tolist):
        return tuple(int(value) for value in tolist())
    return tuple(int(value) for value in column)


def _owner_lifetime_state(owner: Any) -> str:
    current = owner
    seen: set[int] = set()
    while current is not None:
        identity = id(current)
        if identity in seen:
            return "unknown_cycle"
        seen.add(identity)
        closed = getattr(current, "closed", None)
        if closed is True:
            return "closed"
        if closed is False:
            return "open"
        current = getattr(current, "owner", None)
    return "unowned"


def _validate_int64_column(column: Any, name: str) -> None:
    dtype = _dtype_name(column)
    if dtype is not None and dtype not in {"int64", "long"}:
        raise ValueError(f"{name} must be int64")


def _validate_float64_column(column: Any, name: str) -> None:
    dtype = _dtype_name(column)
    if dtype is not None and dtype not in {"float64", "double"}:
        raise ValueError(f"{name} must be float64")


def _dtype_name(column: Any) -> str | None:
    dtype = getattr(column, "dtype", None)
    if dtype is None:
        return None
    text = str(dtype).lower()
    if "." in text:
        text = text.rsplit(".", 1)[-1]
    return text


def _device_info(column: Any) -> tuple[str, int]:
    if column is None:
        return "cpu", 0
    device = getattr(column, "device", None)
    if device is not None:
        device_type = getattr(device, "type", None)
        device_index = getattr(device, "index", None)
        if device_type is not None:
            return str(device_type), 0 if device_index is None else int(device_index)
        text = str(device)
        if text.startswith("cuda"):
            _, _, index = text.partition(":")
            return "cuda", int(index) if index else 0
    cuda_interface = getattr(column, "__cuda_array_interface__", None)
    if isinstance(cuda_interface, Mapping):
        return "cuda", 0
    return "cpu", 0


def _source_protocol(column: Any) -> str:
    if column is None:
        return "python"
    module = type(column).__module__.split(".", 1)[0]
    if module in {"torch", "cupy", "numpy"}:
        return module
    if hasattr(column, "__cuda_array_interface__"):
        return "cuda_array_interface"
    return "python"


def _has_cuda_array_interface(column: Any) -> bool:
    return isinstance(getattr(column, "__cuda_array_interface__", None), Mapping)


def _torch_carrier_adapter_mode(column: Any) -> str:
    if _is_torch_tensor(column):
        return "torch_tensor"
    if _has_cuda_array_interface(column):
        return "cuda_array_interface_to_torch_via_dlpack"
    if _host_column_can_be_materialized(column):
        return "host_column_requires_explicit_copy"
    return "unsupported"


def _host_column_can_be_materialized(column: Any) -> bool:
    if column is None:
        return True
    if callable(getattr(column, "tolist", None)):
        return True
    if isinstance(column, SequenceABC) and not isinstance(column, (str, bytes, bytearray)):
        return True
    return callable(getattr(column, "__iter__", None))


def _data_ptr(column: Any) -> int | None:
    data_ptr = getattr(column, "data_ptr", None)
    if callable(data_ptr):
        return int(data_ptr())
    data = getattr(column, "data", None)
    ptr = getattr(data, "ptr", None)
    if ptr is not None:
        return int(ptr)
    cuda_interface = getattr(column, "__cuda_array_interface__", None)
    if isinstance(cuda_interface, Mapping):
        pointer = cuda_interface.get("data", (None,))[0]
        return None if pointer is None else int(pointer)
    return None


def _buffer_descriptor(name: str, column: Any, dtype: str, *, access_mode: str) -> RtdlBufferDescriptor:
    device_type, device_id = _device_info(column)
    return RtdlBufferDescriptor(
        name=name,
        dtype=dtype,
        shape=(_column_length(column),),
        device_type=device_type,
        device_id=device_id,
        data_ptr=_data_ptr(column),
        access_mode=access_mode,
        source_protocol=_source_protocol(column),
        lifetime="caller_retained",
        mutability="immutable",
        capacity_elements=_column_length(column),
        owner=column,
    )


def _neutral_buffer_seam_metadata(
    name: str,
    column: Any,
    dtype: str,
    *,
    producer: str,
    consumer: str,
    access_mode: str,
    native_producer: bool = False,
    host_materialized_before_handoff: bool = False,
    lifetime_state: str | None = None,
) -> dict[str, Any]:
    resolved_lifetime_state = (
        lifetime_state
        if lifetime_state is not None
        else "native_owned_pending_state_machine"
        if native_producer
        else "caller_retained"
    )
    transfer_status = "host_stage" if host_materialized_before_handoff else None
    descriptor = _neutral_buffer_seam_descriptor(
        name,
        column,
        dtype,
        producer=producer,
        consumer=consumer,
        access_mode=access_mode,
        native_producer=native_producer,
        host_materialized_before_handoff=host_materialized_before_handoff,
        lifetime_state=lifetime_state,
    )
    return descriptor.to_metadata()


def _neutral_buffer_seam_descriptor(
    name: str,
    column: Any,
    dtype: str,
    *,
    producer: str,
    consumer: str,
    access_mode: str,
    native_producer: bool = False,
    host_materialized_before_handoff: bool = False,
    lifetime_state: str | None = None,
) -> Any:
    resolved_lifetime_state = (
        lifetime_state
        if lifetime_state is not None
        else "native_owned_pending_state_machine"
        if native_producer
        else "caller_retained"
    )
    transfer_status = "host_stage" if host_materialized_before_handoff else None
    return neutral_buffer_descriptor_from_rtdl_buffer(
        _buffer_descriptor(name, column, dtype, access_mode=access_mode),
        producer=producer,
        consumer=consumer,
        lifetime_state=resolved_lifetime_state,
        native_producer=native_producer,
        transfer_status=transfer_status,
        host_materialized_before_handoff=host_materialized_before_handoff,
    )


def _torch_carrier_gather_neutral_seam_descriptors(
    hit_stream_columns: RtdlHitStreamColumnHandoff,
    payload_columns: RtdlTypedPrimitivePayloadColumns,
) -> tuple[Any, ...]:
    return (
        _neutral_buffer_seam_descriptor(
            "primitive_ids",
            hit_stream_columns.primitive_ids,
            "int64",
            producer=hit_stream_columns.source_mode,
            consumer="triton_torch_carrier_gather",
            access_mode="read",
            native_producer=hit_stream_columns.source_mode == "native_device_columns"
            and not hit_stream_columns.caller_owned_output_buffers,
            host_materialized_before_handoff=bool(hit_stream_columns.materializes_host_rows_for_bridge),
            lifetime_state=(
                "caller_retained"
                if hit_stream_columns.caller_owned_output_buffers
                else None
            ),
        ),
        _neutral_buffer_seam_descriptor(
            "primitive_group_ids",
            payload_columns.primitive_group_ids,
            "int64",
            producer=payload_columns.source_mode,
            consumer="triton_torch_carrier_gather",
            access_mode="read",
        ),
        _neutral_buffer_seam_descriptor(
            "primitive_values",
            payload_columns.primitive_values,
            "float64",
            producer=payload_columns.source_mode,
            consumer="triton_torch_carrier_gather",
            access_mode="read",
        ),
    )


def _neutral_buffer_handoff_summary(
    hit_stream_columns: RtdlHitStreamColumnHandoff,
    payload_columns: RtdlTypedPrimitivePayloadColumns,
) -> dict[str, object]:
    hit_metadata = hit_stream_columns.to_metadata()
    payload_metadata = payload_columns.to_metadata()
    hit_statuses = tuple(
        seam["transfer_status"] for seam in hit_metadata["neutral_buffer_seams"]
    )
    payload_statuses = tuple(
        seam["transfer_status"] for seam in payload_metadata["neutral_buffer_seams"]
    )
    return {
        "contract_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
        "hit_stream_transfer_statuses": hit_statuses,
        "payload_transfer_statuses": payload_statuses,
        "any_zero_copy_claim_authorized": any(
            seam["zero_copy_claim_authorized"]
            for seam in (
                *hit_metadata["neutral_buffer_seams"],
                *payload_metadata["neutral_buffer_seams"],
            )
        ),
        "any_host_stage": any(
            seam["host_materialized_before_handoff"]
            or seam["transfer_status"] == "host_stage"
            for seam in (
                *hit_metadata["neutral_buffer_seams"],
                *payload_metadata["neutral_buffer_seams"],
            )
        ),
        "native_device_column_output_proven_on_hardware": bool(
            hit_metadata["native_device_column_output_proven_on_hardware"]
        ),
        "removes_host_materialization_bottleneck": bool(
            hit_metadata["removes_host_materialization_bottleneck"]
        ),
        "claim_boundary": (
            "Current hit-stream continuation metadata is neutral-buffer-aware. "
            "Native device-column output may be hardware-proven independently, but "
            "true zero-copy and public speedup claims remain unauthorized."
        ),
    }


def _metadata_key_hits(payload: object, keys: Sequence[str], *, prefix: str = "") -> tuple[str, ...]:
    hits: list[str] = []
    key_set = set(keys)
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if str(key) in key_set:
                hits.append(path)
            hits.extend(_metadata_key_hits(value, keys, prefix=path))
    elif isinstance(payload, SequenceABC) and not isinstance(payload, (str, bytes, bytearray)):
        for index, value in enumerate(payload):
            path = f"{prefix}[{index}]" if prefix else f"[{index}]"
            hits.extend(_metadata_key_hits(value, keys, prefix=path))
    return tuple(hits)


def _all_seams_device_ready(seams: Sequence[Mapping[str, Any]]) -> bool:
    return bool(seams) and all(
        bool(seam["device_resident"])
        and seam["transfer_status"] != "host_stage"
        and str(seam["buffer"]["device"]).startswith("cuda:")
        for seam in seams
    )


def _partner_plan_runtime_action(
    support: dict[str, Any],
    *,
    current_inputs_device_ready: bool,
    any_host_stage: bool,
) -> str:
    if not bool(support["supported"]):
        return "fail_closed_unsupported_partner_operation"
    if any_host_stage:
        return "host_stage_or_copy_must_be_explicit"
    if bool(support["requires_cuda"]) and not current_inputs_device_ready:
        return "requires_device_resident_columns_or_explicit_copy"
    if bool(support["requires_sm70_plus"]):
        return "requires_sm70_pod_validation_before_performance_claim"
    return "plan_available"


def _normalize_gather_partner(partner: str) -> str:
    normalized = str(partner).strip().lower().replace("-", "_")
    aliases = {
        "reference": "python_reference",
        "python": "python_reference",
        "torch": "triton",
        "cupy": "cupy_conformance",
        "cupy_descriptor": "cupy_conformance",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in {"auto", "python_reference", "triton", "cupy_conformance", "numba"}:
        raise ValueError("unsupported hit-stream gather partner")
    return normalized


def _all_torch_gather_columns(
    hit_stream_columns: RtdlHitStreamColumnHandoff,
    payload_columns: RtdlTypedPrimitivePayloadColumns,
) -> bool:
    return (
        _is_torch_tensor(hit_stream_columns.primitive_ids)
        and _is_torch_tensor(payload_columns.primitive_group_ids)
        and _is_torch_tensor(payload_columns.primitive_values)
    )


def _torch_carrier_device(device_like: Any) -> Any:
    import torch

    device = getattr(device_like, "device", None)
    if device is not None:
        return device
    device_type, device_id = _device_info(device_like)
    if device_type == "cuda":
        return torch.device(f"cuda:{device_id}")
    return None


def _is_torch_tensor(value: Any) -> bool:
    return type(value).__module__.split(".", 1)[0] == "torch"


def _prepare_triton_tensor_carrier_column(
    values: Any,
    *,
    dtype: str,
    prefer_cuda: bool,
    require_cuda: bool,
    device_like: Any = None,
) -> Any:
    """Prepare an explicit Triton tensor carrier without authorizing zero-copy."""

    if _is_torch_tensor(values):
        import torch

        target_dtype = torch.int64 if dtype == "int64" else torch.float64
        target_device = getattr(device_like, "device", values.device)
        return values.to(device=target_device, dtype=target_dtype)
    if prefer_cuda or require_cuda or _device_info(device_like)[0] == "cuda":
        import torch

        if require_cuda and not torch.cuda.is_available():
            raise RuntimeError("Torch CUDA is required for native device hit-stream handoff validation")
        if torch.cuda.is_available():
            device = _torch_carrier_device(device_like) or torch.device("cuda:0")
            target_dtype = torch.int64 if dtype == "int64" else torch.float64
            return torch.as_tensor(values, dtype=target_dtype, device=device)
    if dtype == "int64":
        return tuple(int(value) for value in values)
    return tuple(float(value) for value in values)


def _torch_as(value: Any, *, dtype: Any, device_like: Any, allow_explicit_copy: bool = False) -> Any:
    import torch

    device = _torch_carrier_device(device_like)
    if _is_torch_tensor(value):
        return value.to(dtype=dtype, device=device)
    if _has_cuda_array_interface(value):
        return _torch_from_cuda_array_interface(value, dtype=dtype, device=device)
    if not allow_explicit_copy:
        raise ValueError(
            "torch carrier gather requires torch tensors or CUDA-array-interface columns; "
            "host columns require allow_explicit_copy=True"
        )
    return torch.as_tensor(value, dtype=dtype, device=device)


def _torch_from_cuda_array_interface(value: Any, *, dtype: Any, device: Any) -> Any:
    import torch

    tensor = None
    dlpack_error: Exception | None = None
    if callable(getattr(value, "__dlpack__", None)):
        try:
            tensor = torch.from_dlpack(value)
        except Exception as exc:  # pragma: no cover - depends on optional runtimes.
            dlpack_error = exc
    if tensor is None:
        try:
            import cupy

            cupy_array = cupy.asarray(value)
            if callable(getattr(torch, "from_dlpack", None)):
                tensor = torch.from_dlpack(cupy_array)
            else:  # pragma: no cover - legacy torch fallback.
                from torch.utils import dlpack

                tensor = dlpack.from_dlpack(cupy_array.toDlpack())
        except Exception as exc:
            if dlpack_error is not None:
                raise RuntimeError(
                    "CUDA-array-interface to torch carrier adapter requires a working "
                    "DLPack or CuPy bridge"
                ) from dlpack_error
            raise RuntimeError(
                "CUDA-array-interface to torch carrier adapter requires CuPy when "
                "the source object does not expose usable DLPack"
            ) from exc
    if tensor.dtype != dtype:
        raise ValueError("CUDA-array-interface adapter dtype mismatch would require a copy")
    if device is not None and tensor.device != torch.device(device):
        raise ValueError("CUDA-array-interface adapter device mismatch would require a copy")
    return tensor
