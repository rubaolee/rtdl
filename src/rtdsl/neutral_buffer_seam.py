from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from . import partner as _partner
from .partner_protocol import RtdlBufferDescriptor
from .partner_protocol import buffer_descriptor_from_tensor_descriptor


V2_5_NEUTRAL_BUFFER_SEAM_VERSION = "rtdl.neutral_buffer_seam.v2.5"
V2_5_NEUTRAL_BUFFER_API_MATURITY = "experimental_contract_no_native_promotion"
V2_5_NEUTRAL_BUFFER_PROTOCOL_PRIORITY = (
    "registered_partner_adapter",
    "dlpack",
    "cuda_array_interface",
    "array_interface",
)
V2_5_NEUTRAL_BUFFER_TRANSFER_STATUSES = (
    "unknown",
    "host_reference",
    "declared_copy",
    "host_stage",
    "borrowed_device_pointer_unmeasured",
    "zero_copy_measured",
)
V2_5_NEUTRAL_BUFFER_OWNERSHIP_STATES = (
    "caller_retained",
    "producer_retained",
    "partner_borrowed",
    "native_owned_pending_state_machine",
    "released",
)
V2_5_NEUTRAL_BUFFER_LIFETIME_EVENTS = (
    "handoff_begin",
    "continuation_complete",
    "release",
    "failure_cleanup",
)
V2_5_NEUTRAL_BUFFER_SUPPORTED_CONSUMERS = (
    "cpu_reference",
    "torch",
    "cupy",
    "triton",
    "numba",
    "raw_cuda",
)
V2_5_NEUTRAL_BUFFER_ZERO_COPY_EVIDENCE_RULE = (
    "same_pointer_same_device_measured_and_no_host_stage"
)


@dataclass(frozen=True)
class RtdlNeutralBufferSeamDescriptor:
    """Partner-neutral buffer seam for v2.5 planning and conformance.

    The descriptor intentionally records buffer identity, ownership, and copy
    status without making RTDL a general memory manager. It is a contract for
    explicit handoff decisions; it does not authorize native promotion by
    itself.
    """

    buffer: RtdlBufferDescriptor
    producer: str
    consumer: str
    transfer_status: str = "unknown"
    lifetime_state: str = "caller_retained"
    host_materialized_before_handoff: bool = False
    native_producer: bool = False
    measured_same_pointer: bool = False
    measured_no_host_stage: bool = False
    measured_evidence: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if not str(self.producer):
            raise ValueError("neutral buffer seam requires a non-empty producer")
        if not str(self.consumer):
            raise ValueError("neutral buffer seam requires a non-empty consumer")
        if self.transfer_status not in V2_5_NEUTRAL_BUFFER_TRANSFER_STATUSES:
            raise ValueError("unsupported neutral buffer transfer status")
        if self.lifetime_state not in V2_5_NEUTRAL_BUFFER_OWNERSHIP_STATES:
            raise ValueError("unsupported neutral buffer lifetime state")
        if self.host_materialized_before_handoff and self.transfer_status == "zero_copy_measured":
            raise ValueError("zero-copy measured handoff cannot materialize host data first")
        if self.transfer_status == "zero_copy_measured" and not self.zero_copy_claim_authorized:
            raise ValueError(
                "zero_copy_measured requires a CUDA pointer, measured same-pointer evidence, "
                "and measured no-host-stage evidence"
            )
        if (
            self.transfer_status == "borrowed_device_pointer_unmeasured"
            and not self.direct_device_pointer_observed
        ):
            raise ValueError("borrowed device-pointer handoff requires an observed pointer")
        if self.native_producer and self.lifetime_state not in {
            "producer_retained",
            "native_owned_pending_state_machine",
        }:
            raise ValueError("native producers must retain ownership or declare pending native ownership")

    @property
    def direct_device_pointer_observed(self) -> bool:
        return self.buffer.data_ptr is not None and int(self.buffer.data_ptr) > 0

    @property
    def device_resident(self) -> bool:
        return self.buffer.device_type == "cuda" and self.direct_device_pointer_observed

    @property
    def zero_copy_claim_authorized(self) -> bool:
        return (
            self.transfer_status == "zero_copy_measured"
            and self.device_resident
            and bool(self.measured_same_pointer)
            and bool(self.measured_no_host_stage)
            and not bool(self.host_materialized_before_handoff)
        )

    @property
    def native_device_output_promotion_ready(self) -> bool:
        return False

    @property
    def public_speedup_claim_authorized(self) -> bool:
        return False

    def to_metadata(self) -> dict[str, Any]:
        return {
            "contract_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
            "api_maturity": V2_5_NEUTRAL_BUFFER_API_MATURITY,
            "producer": self.producer,
            "consumer": self.consumer,
            "transfer_status": self.transfer_status,
            "copy_status": _copy_status(self.transfer_status),
            "lifetime_state": self.lifetime_state,
            "host_materialized_before_handoff": bool(self.host_materialized_before_handoff),
            "native_producer": bool(self.native_producer),
            "direct_device_pointer_observed": self.direct_device_pointer_observed,
            "device_resident": self.device_resident,
            "zero_copy_evidence_rule": V2_5_NEUTRAL_BUFFER_ZERO_COPY_EVIDENCE_RULE,
            "measured_same_pointer": bool(self.measured_same_pointer),
            "measured_no_host_stage": bool(self.measured_no_host_stage),
            "zero_copy_claim_authorized": self.zero_copy_claim_authorized,
            "native_device_output_promotion_ready": self.native_device_output_promotion_ready,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "buffer": self.buffer.to_metadata(),
            "measured_evidence": dict(self.measured_evidence or {}),
            "claim_boundary": (
                "Neutral buffer seams describe handoff identity, ownership, and copy status. "
                "They do not by themselves authorize native promotion, true zero-copy public "
                "claims, or speedup claims."
            ),
        }


@dataclass(frozen=True)
class RtdlNeutralBufferLifetimePlan:
    producer: str
    consumer: str
    state: str
    retain_until: str
    release_event: str = "continuation_complete"
    failure_cleanup_event: str = "failure_cleanup"

    def __post_init__(self) -> None:
        if not str(self.producer):
            raise ValueError("lifetime plan requires a non-empty producer")
        if not str(self.consumer):
            raise ValueError("lifetime plan requires a non-empty consumer")
        if self.state not in V2_5_NEUTRAL_BUFFER_OWNERSHIP_STATES:
            raise ValueError("unsupported neutral buffer lifetime state")
        if self.release_event not in V2_5_NEUTRAL_BUFFER_LIFETIME_EVENTS:
            raise ValueError("unsupported neutral buffer release event")
        if self.failure_cleanup_event != "failure_cleanup":
            raise ValueError("failure cleanup event must remain failure_cleanup")
        if self.state == "native_owned_pending_state_machine" and self.retain_until != "state_machine_defined":
            raise ValueError("pending native ownership requires retain_until=state_machine_defined")

    @property
    def requires_native_state_machine(self) -> bool:
        return self.state == "native_owned_pending_state_machine"

    def transition(self, next_state: str, *, event: str) -> "RtdlNeutralBufferLifetimePlan":
        validate_neutral_buffer_lifetime_transition(self.state, next_state, event=event)
        return RtdlNeutralBufferLifetimePlan(
            producer=self.producer,
            consumer=self.consumer,
            state=next_state,
            retain_until=self.retain_until if next_state != "released" else "none",
            release_event=self.release_event,
            failure_cleanup_event=self.failure_cleanup_event,
        )

    def to_metadata(self) -> dict[str, Any]:
        return {
            "contract_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
            "producer": self.producer,
            "consumer": self.consumer,
            "state": self.state,
            "retain_until": self.retain_until,
            "release_event": self.release_event,
            "failure_cleanup_event": self.failure_cleanup_event,
            "requires_native_state_machine": self.requires_native_state_machine,
        }


@dataclass(frozen=True)
class RtdlNeutralBufferLease:
    descriptor: RtdlNeutralBufferSeamDescriptor
    owner_state: str
    state: str
    retain_until: str = "continuation_complete"
    event_log: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.owner_state not in V2_5_NEUTRAL_BUFFER_OWNERSHIP_STATES:
            raise ValueError("unsupported neutral buffer lease owner state")
        if self.owner_state in {"partner_borrowed", "released"}:
            raise ValueError("neutral buffer lease owner state must be a retaining owner")
        if self.state not in V2_5_NEUTRAL_BUFFER_OWNERSHIP_STATES:
            raise ValueError("unsupported neutral buffer lease state")
        if self.state == "native_owned_pending_state_machine" and self.retain_until != "state_machine_defined":
            raise ValueError("pending native ownership requires retain_until=state_machine_defined")
        if self.descriptor.native_producer and self.owner_state not in {
            "producer_retained",
            "native_owned_pending_state_machine",
        }:
            raise ValueError("native producer leases require a producer/native owner state")

    @property
    def is_borrowed(self) -> bool:
        return self.state == "partner_borrowed"

    @property
    def is_released(self) -> bool:
        return self.state == "released"

    @property
    def native_state_machine_required(self) -> bool:
        return self.owner_state == "native_owned_pending_state_machine"

    def begin_partner_borrow(self) -> "RtdlNeutralBufferLease":
        validate_neutral_buffer_lifetime_transition(
            self.state,
            "partner_borrowed",
            event="handoff_begin",
        )
        return self._replace_state("partner_borrowed", "handoff_begin")

    def complete_partner_borrow(self) -> "RtdlNeutralBufferLease":
        validate_neutral_buffer_lifetime_transition(
            self.state,
            self.owner_state,
            event="continuation_complete",
        )
        return self._replace_state(self.owner_state, "continuation_complete")

    def release(self) -> "RtdlNeutralBufferLease":
        validate_neutral_buffer_lifetime_transition(
            self.state,
            "released",
            event="release",
        )
        return self._replace_state("released", "release", retain_until="none")

    def failure_cleanup(self) -> "RtdlNeutralBufferLease":
        validate_neutral_buffer_lifetime_transition(
            self.state,
            "released",
            event="failure_cleanup",
        )
        return self._replace_state("released", "failure_cleanup", retain_until="none")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "contract_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
            "buffer_name": self.descriptor.buffer.name,
            "producer": self.descriptor.producer,
            "consumer": self.descriptor.consumer,
            "owner_state": self.owner_state,
            "state": self.state,
            "retain_until": self.retain_until,
            "is_borrowed": self.is_borrowed,
            "is_released": self.is_released,
            "native_state_machine_required": self.native_state_machine_required,
            "event_log": self.event_log,
            "true_zero_copy_authorized": False,
            "public_speedup_claim_authorized": False,
            "claim_boundary": (
                "Neutral buffer leases enforce ownership transitions but do not "
                "allocate CUDA memory, free native buffers, or authorize zero-copy."
            ),
        }

    def _replace_state(
        self,
        state: str,
        event: str,
        *,
        retain_until: str | None = None,
    ) -> "RtdlNeutralBufferLease":
        return RtdlNeutralBufferLease(
            descriptor=self.descriptor,
            owner_state=self.owner_state,
            state=state,
            retain_until=self.retain_until if retain_until is None else retain_until,
            event_log=(*self.event_log, event),
        )


def describe_v2_5_neutral_buffer_seam_contract() -> dict[str, Any]:
    return {
        "contract_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
        "api_maturity": V2_5_NEUTRAL_BUFFER_API_MATURITY,
        "protocol_priority": V2_5_NEUTRAL_BUFFER_PROTOCOL_PRIORITY,
        "transfer_statuses": V2_5_NEUTRAL_BUFFER_TRANSFER_STATUSES,
        "ownership_states": V2_5_NEUTRAL_BUFFER_OWNERSHIP_STATES,
        "lifetime_events": V2_5_NEUTRAL_BUFFER_LIFETIME_EVENTS,
        "lease_state_machine": "RtdlNeutralBufferLease",
        "supported_consumers": V2_5_NEUTRAL_BUFFER_SUPPORTED_CONSUMERS,
        "engine_boundary": "app_agnostic_native_engine",
        "partner_selection_policy": "explicit_per_boundary_app_choice",
        "no_partner_forced": True,
        "multi_partner_composition_allowed": True,
        "unsupported_cells_fail_closed": True,
        "torch_is_not_the_neutral_protocol": True,
        "zero_copy_evidence_rule": V2_5_NEUTRAL_BUFFER_ZERO_COPY_EVIDENCE_RULE,
        "native_device_output_promotion_ready": False,
        "true_zero_copy_public_claim_authorized": False,
        "public_speedup_claim_authorized": False,
        "claim_boundary": (
            "This is a neutral handoff and lifetime contract. It can describe measured "
            "zero-copy evidence, but it does not create native CUDA output, promote "
            "experimental hit-stream APIs, or authorize public performance claims."
        ),
    }


def classify_neutral_buffer_protocol(obj: Any) -> str:
    for name in ("torch", "cupy", "numpy"):
        try:
            adapter = _partner.get(name)
        except KeyError:
            continue
        if adapter.can_export(obj):
            return name
    if callable(getattr(obj, "__dlpack__", None)) and callable(getattr(obj, "__dlpack_device__", None)):
        return "dlpack"
    if isinstance(getattr(obj, "__cuda_array_interface__", None), dict):
        return "cuda_array_interface"
    if isinstance(getattr(obj, "__array_interface__", None), dict):
        return "array_interface"
    raise TypeError("object does not expose a supported neutral buffer protocol")


def neutral_buffer_descriptor_from_object(
    name: str,
    obj: Any,
    *,
    producer: str,
    consumer: str,
    access_mode: str = "read",
    transfer_status: str | None = None,
    lifetime_state: str = "caller_retained",
    native_producer: bool = False,
    host_materialized_before_handoff: bool = False,
    measured_same_pointer: bool = False,
    measured_no_host_stage: bool = False,
    measured_evidence: Mapping[str, Any] | None = None,
) -> RtdlNeutralBufferSeamDescriptor:
    protocol = classify_neutral_buffer_protocol(obj)
    if protocol in {"torch", "cupy", "numpy", "dlpack"}:
        adapter_name = "dlpack" if protocol == "dlpack" else protocol
        tensor = _partner.get(adapter_name).export_tensor(obj, access=access_mode, stream=None)
        buffer = buffer_descriptor_from_tensor_descriptor(
            name,
            tensor,
            access_mode=access_mode,
            lifetime=_buffer_lifetime_for_state(lifetime_state),
        )
    elif protocol == "cuda_array_interface":
        buffer = _buffer_descriptor_from_cuda_array_interface(
            name,
            obj.__cuda_array_interface__,
            access_mode=access_mode,
            lifetime_state=lifetime_state,
            owner=obj,
        )
    else:
        buffer = _buffer_descriptor_from_array_interface(
            name,
            obj.__array_interface__,
            access_mode=access_mode,
            lifetime_state=lifetime_state,
            owner=obj,
        )
    resolved_transfer_status = (
        _default_transfer_status(buffer) if transfer_status is None else str(transfer_status)
    )
    return RtdlNeutralBufferSeamDescriptor(
        buffer=buffer,
        producer=producer,
        consumer=consumer,
        transfer_status=resolved_transfer_status,
        lifetime_state=lifetime_state,
        host_materialized_before_handoff=bool(host_materialized_before_handoff),
        native_producer=bool(native_producer),
        measured_same_pointer=bool(measured_same_pointer),
        measured_no_host_stage=bool(measured_no_host_stage),
        measured_evidence=measured_evidence,
    )


def neutral_buffer_descriptor_from_rtdl_buffer(
    buffer: RtdlBufferDescriptor,
    *,
    producer: str,
    consumer: str,
    transfer_status: str | None = None,
    lifetime_state: str = "caller_retained",
    native_producer: bool = False,
    host_materialized_before_handoff: bool = False,
    measured_same_pointer: bool = False,
    measured_no_host_stage: bool = False,
    measured_evidence: Mapping[str, Any] | None = None,
) -> RtdlNeutralBufferSeamDescriptor:
    resolved_transfer_status = (
        _default_transfer_status(buffer) if transfer_status is None else str(transfer_status)
    )
    return RtdlNeutralBufferSeamDescriptor(
        buffer=buffer,
        producer=producer,
        consumer=consumer,
        transfer_status=resolved_transfer_status,
        lifetime_state=lifetime_state,
        native_producer=bool(native_producer),
        host_materialized_before_handoff=bool(host_materialized_before_handoff),
        measured_same_pointer=bool(measured_same_pointer),
        measured_no_host_stage=bool(measured_no_host_stage),
        measured_evidence=measured_evidence,
    )


def neutral_buffer_lifetime_plan(
    *,
    producer: str,
    consumer: str,
    state: str = "caller_retained",
    retain_until: str = "continuation_complete",
    release_event: str = "continuation_complete",
) -> RtdlNeutralBufferLifetimePlan:
    return RtdlNeutralBufferLifetimePlan(
        producer=producer,
        consumer=consumer,
        state=state,
        retain_until=retain_until,
        release_event=release_event,
    )


def create_neutral_buffer_lease(
    descriptor: RtdlNeutralBufferSeamDescriptor,
    *,
    owner_state: str | None = None,
    retain_until: str | None = None,
) -> RtdlNeutralBufferLease:
    resolved_owner_state = descriptor.lifetime_state if owner_state is None else str(owner_state)
    if resolved_owner_state == "partner_borrowed":
        raise ValueError("neutral buffer lease cannot start in partner_borrowed state")
    if resolved_owner_state == "released":
        raise ValueError("neutral buffer lease cannot start released")
    resolved_retain_until = (
        "state_machine_defined"
        if resolved_owner_state == "native_owned_pending_state_machine"
        else "continuation_complete"
    )
    if retain_until is not None:
        resolved_retain_until = str(retain_until)
    return RtdlNeutralBufferLease(
        descriptor=descriptor,
        owner_state=resolved_owner_state,
        state=resolved_owner_state,
        retain_until=resolved_retain_until,
    )


def validate_neutral_buffer_lifetime_transition(
    current_state: str,
    next_state: str,
    *,
    event: str,
) -> dict[str, Any]:
    if current_state not in V2_5_NEUTRAL_BUFFER_OWNERSHIP_STATES:
        raise ValueError("unsupported current lifetime state")
    if next_state not in V2_5_NEUTRAL_BUFFER_OWNERSHIP_STATES:
        raise ValueError("unsupported next lifetime state")
    if event not in V2_5_NEUTRAL_BUFFER_LIFETIME_EVENTS:
        raise ValueError("unsupported lifetime transition event")
    allowed = _ALLOWED_LIFETIME_TRANSITIONS
    if (current_state, next_state, event) not in allowed:
        raise ValueError(
            f"invalid neutral buffer lifetime transition: {current_state} -> {next_state} via {event}"
        )
    return {
        "contract_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
        "current_state": current_state,
        "next_state": next_state,
        "event": event,
        "valid": True,
    }


_ALLOWED_LIFETIME_TRANSITIONS = {
    ("caller_retained", "partner_borrowed", "handoff_begin"),
    ("producer_retained", "partner_borrowed", "handoff_begin"),
    ("native_owned_pending_state_machine", "partner_borrowed", "handoff_begin"),
    ("partner_borrowed", "producer_retained", "continuation_complete"),
    ("partner_borrowed", "caller_retained", "continuation_complete"),
    ("partner_borrowed", "native_owned_pending_state_machine", "continuation_complete"),
    ("caller_retained", "released", "release"),
    ("producer_retained", "released", "release"),
    ("partner_borrowed", "released", "failure_cleanup"),
    ("native_owned_pending_state_machine", "released", "failure_cleanup"),
}


def _default_transfer_status(buffer: RtdlBufferDescriptor) -> str:
    if buffer.device_type == "cuda" and buffer.data_ptr is not None and int(buffer.data_ptr) > 0:
        return "borrowed_device_pointer_unmeasured"
    if buffer.device_type == "cpu":
        return "host_reference"
    return "unknown"


def _copy_status(transfer_status: str) -> str:
    return {
        "zero_copy_measured": "zero_copy_measured",
        "borrowed_device_pointer_unmeasured": "borrowed_pointer_unmeasured",
        "declared_copy": "copy_declared",
        "host_stage": "host_stage_declared",
        "host_reference": "host_reference",
        "unknown": "unknown",
    }[transfer_status]


def _buffer_lifetime_for_state(lifetime_state: str) -> str:
    if lifetime_state == "caller_retained":
        return "caller_retained"
    if lifetime_state == "partner_borrowed":
        return "borrowed"
    return "session_retained"


def _buffer_descriptor_from_cuda_array_interface(
    name: str,
    interface: Mapping[str, Any],
    *,
    access_mode: str,
    lifetime_state: str,
    owner: Any,
) -> RtdlBufferDescriptor:
    shape = tuple(int(dim) for dim in interface.get("shape", ()))
    strides = interface.get("strides")
    data = interface.get("data")
    if not isinstance(data, tuple) or not data:
        raise ValueError("cuda array interface requires a data pointer tuple")
    return RtdlBufferDescriptor(
        name=name,
        dtype=_dtype_from_array_typestr(str(interface.get("typestr", ""))),
        shape=shape,
        device_type="cuda",
        device_id=int(interface.get("device", 0) or 0),
        data_ptr=int(data[0]),
        strides_bytes=None if strides is None else tuple(int(stride) for stride in strides),
        access_mode=access_mode,
        source_protocol="cuda_array_interface",
        lifetime=_buffer_lifetime_for_state(lifetime_state),
        mutability="immutable" if access_mode == "read" else "mutable",
        owner=owner,
    )


def _buffer_descriptor_from_array_interface(
    name: str,
    interface: Mapping[str, Any],
    *,
    access_mode: str,
    lifetime_state: str,
    owner: Any,
) -> RtdlBufferDescriptor:
    shape = tuple(int(dim) for dim in interface.get("shape", ()))
    strides = interface.get("strides")
    data = interface.get("data")
    data_ptr = None
    if isinstance(data, tuple) and data:
        data_ptr = int(data[0])
    return RtdlBufferDescriptor(
        name=name,
        dtype=_dtype_from_array_typestr(str(interface.get("typestr", ""))),
        shape=shape,
        device_type="cpu",
        device_id=0,
        data_ptr=data_ptr,
        strides_bytes=None if strides is None else tuple(int(stride) for stride in strides),
        access_mode=access_mode,
        source_protocol="array_interface",
        lifetime=_buffer_lifetime_for_state(lifetime_state),
        mutability="immutable" if access_mode == "read" else "mutable",
        owner=owner,
    )


def _dtype_from_array_typestr(typestr: str) -> str:
    normalized = typestr.strip().lower()
    suffix_map = {
        "i8": "int64",
        "u8": "uint64",
        "i4": "int32",
        "u4": "uint32",
        "f8": "float64",
        "f4": "float32",
    }
    suffix = normalized[-2:] if len(normalized) >= 2 else normalized
    return suffix_map.get(suffix, normalized or "unknown")
