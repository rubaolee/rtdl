from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Mapping

from .v3_0_execution_graph import BACKENDS
from .v3_0_execution_graph import CLAIM_BOUNDARY_KEYS
from .v3_0_execution_graph import LIFETIME_STATES
from .v3_0_execution_graph import REQUIRED_PHASE_NAMES
from .v3_0_execution_graph import RESIDENCY_STATES
from .v3_0_execution_graph import STORAGE_KINDS
from .v3_0_execution_graph import STREAM_ORDERINGS
from .v3_0_execution_graph import ClaimBoundary
from .v3_0_execution_graph import GraphValidationError
from .v3_0_execution_graph import V3_EXECUTION_GRAPH_IR_VERSION
from .v3_0_execution_graph import validate_v3_public_name


V3_INSTRUMENTATION_VERSION = "rtdl.v3_0.instrumentation.m3"
V3_INSTRUMENTATION_STATUS = "m3_metadata_only_no_claim_promotion"

EVIDENCE_KINDS = (
    "cuda_event_pair",
    "nsight_stream_correlation",
    "pointer_identity",
    "backend_native_handle",
    "transfer_counter",
    "no_host_materialization",
    "embree_phase_timer",
    "cpu_phase_timer",
    "host_timer",
)
TIMING_SOURCES = (
    "cuda_event",
    "nsight",
    "embree_timer",
    "cpu_timer",
    "host_timer",
    "metadata_only",
)
CLAIM_READINESS_KEYS = (
    "same_stream_ready",
    "device_resident_ready",
    "true_zero_copy_ready",
    "phase_complete",
    "public_claim_authorized",
)


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    kind: str
    backend: str
    phase: str
    source: str
    hardware: str
    observed: bool = True
    details: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        validate_v3_public_name(self.evidence_id, label="evidence id")
        if self.kind not in EVIDENCE_KINDS:
            raise GraphValidationError("unsupported evidence kind")
        if self.backend not in BACKENDS:
            raise GraphValidationError("unsupported evidence backend")
        if not str(self.phase).strip():
            raise GraphValidationError("evidence record requires phase")
        if not str(self.source).strip() or not str(self.hardware).strip():
            raise GraphValidationError("evidence record requires source and hardware")
        object.__setattr__(self, "details", dict(self.details))

    def to_metadata(self) -> dict[str, object]:
        return {
            "evidence_id": self.evidence_id,
            "kind": self.kind,
            "backend": self.backend,
            "phase": self.phase,
            "source": self.source,
            "hardware": self.hardware,
            "observed": bool(self.observed),
            "details": dict(self.details),
        }


@dataclass(frozen=True)
class PhaseTimingRecord:
    phase: str
    seconds: float
    backend: str
    timing_source: str
    evidence_ids: tuple[str, ...] = ()
    steady_state_candidate: bool = False
    setup_candidate: bool = False
    materialization_candidate: bool = False

    def __post_init__(self) -> None:
        if not str(self.phase).strip():
            raise GraphValidationError("phase timing requires phase")
        if float(self.seconds) < 0.0:
            raise GraphValidationError("phase timing seconds must be non-negative")
        if self.backend not in BACKENDS:
            raise GraphValidationError("unsupported phase timing backend")
        if self.timing_source not in TIMING_SOURCES:
            raise GraphValidationError("unsupported phase timing source")
        object.__setattr__(self, "seconds", float(self.seconds))
        object.__setattr__(self, "evidence_ids", tuple(str(item) for item in self.evidence_ids))

    def to_metadata(self) -> dict[str, object]:
        return {
            "phase": self.phase,
            "seconds": self.seconds,
            "backend": self.backend,
            "timing_source": self.timing_source,
            "evidence_ids": self.evidence_ids,
            "steady_state_candidate": bool(self.steady_state_candidate),
            "setup_candidate": bool(self.setup_candidate),
            "materialization_candidate": bool(self.materialization_candidate),
        }


@dataclass(frozen=True)
class ResidencyEvidence:
    value_name: str
    storage: str
    residency: str
    lifetime: str
    stream_ordering: str = "not_proven"
    data_ptr_observed: bool = False
    backend_handle_observed: bool = False
    transfer_counter_observed: bool = False
    host_materialized: bool = False
    hidden_copy_observed: bool = False
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        validate_v3_public_name(self.value_name, label="residency value")
        if self.storage not in STORAGE_KINDS:
            raise GraphValidationError("unsupported residency evidence storage")
        if self.residency not in RESIDENCY_STATES:
            raise GraphValidationError("unsupported residency evidence state")
        if self.lifetime not in LIFETIME_STATES:
            raise GraphValidationError("unsupported residency evidence lifetime")
        if self.stream_ordering not in STREAM_ORDERINGS:
            raise GraphValidationError("unsupported residency stream ordering")
        object.__setattr__(self, "evidence_ids", tuple(str(item) for item in self.evidence_ids))

    @property
    def device_resident_ready(self) -> bool:
        return (
            self.residency in {"device_resident", "backend_resident", "dual_resident"}
            and self.storage in {"cuda", "backend_native", "dual"}
            and (self.data_ptr_observed or self.backend_handle_observed)
            and self.lifetime in {"session_retained", "native_owned", "partner_owned", "borrowed"}
            and not self.host_materialized
            and bool(self.evidence_ids)
        )

    @property
    def true_zero_copy_ready(self) -> bool:
        return (
            self.device_resident_ready
            and self.transfer_counter_observed
            and not self.hidden_copy_observed
        )

    def to_metadata(self) -> dict[str, object]:
        return {
            "value_name": self.value_name,
            "storage": self.storage,
            "residency": self.residency,
            "lifetime": self.lifetime,
            "stream_ordering": self.stream_ordering,
            "data_ptr_observed": bool(self.data_ptr_observed),
            "backend_handle_observed": bool(self.backend_handle_observed),
            "transfer_counter_observed": bool(self.transfer_counter_observed),
            "host_materialized": bool(self.host_materialized),
            "hidden_copy_observed": bool(self.hidden_copy_observed),
            "evidence_ids": self.evidence_ids,
            "device_resident_ready": self.device_resident_ready,
            "true_zero_copy_ready": self.true_zero_copy_ready,
        }


@dataclass(frozen=True)
class InstrumentationPacket:
    graph_id: str
    backend: str
    hardware: str
    phase_timings: tuple[PhaseTimingRecord, ...]
    evidence_records: tuple[EvidenceRecord, ...] = ()
    residency_evidence: tuple[ResidencyEvidence, ...] = ()
    claim_boundary: ClaimBoundary = field(default_factory=ClaimBoundary)
    ir_version: str = V3_EXECUTION_GRAPH_IR_VERSION
    instrumentation_version: str = V3_INSTRUMENTATION_VERSION

    def __post_init__(self) -> None:
        if self.ir_version != V3_EXECUTION_GRAPH_IR_VERSION:
            raise GraphValidationError("unexpected instrumentation IR version")
        if self.instrumentation_version != V3_INSTRUMENTATION_VERSION:
            raise GraphValidationError("unexpected instrumentation version")
        if not str(self.graph_id).strip():
            raise GraphValidationError("instrumentation packet requires graph_id")
        if self.backend not in BACKENDS:
            raise GraphValidationError("unsupported instrumentation backend")
        if not str(self.hardware).strip():
            raise GraphValidationError("instrumentation packet requires hardware")
        phase_timings = tuple(self.phase_timings)
        evidence_records = tuple(self.evidence_records)
        residency_evidence = tuple(self.residency_evidence)
        _validate_phase_completeness(phase_timings)
        _validate_evidence_references(phase_timings, evidence_records, residency_evidence)
        object.__setattr__(self, "phase_timings", phase_timings)
        object.__setattr__(self, "evidence_records", evidence_records)
        object.__setattr__(self, "residency_evidence", residency_evidence)

    @property
    def phase_complete(self) -> bool:
        phase_names = {record.phase for record in self.phase_timings}
        return all(phase in phase_names for phase in REQUIRED_PHASE_NAMES)

    @property
    def same_stream_ready(self) -> bool:
        return any(
            record.observed and record.kind in {"cuda_event_pair", "nsight_stream_correlation"}
            for record in self.evidence_records
        )

    @property
    def device_resident_ready(self) -> bool:
        return any(item.device_resident_ready for item in self.residency_evidence)

    @property
    def true_zero_copy_ready(self) -> bool:
        return any(item.true_zero_copy_ready for item in self.residency_evidence)

    @property
    def claim_readiness(self) -> dict[str, bool]:
        return {
            "same_stream_ready": self.same_stream_ready,
            "device_resident_ready": self.device_resident_ready,
            "true_zero_copy_ready": self.true_zero_copy_ready,
            "phase_complete": self.phase_complete,
            "public_claim_authorized": False,
        }

    def to_metadata(self) -> dict[str, object]:
        return {
            "ir_version": self.ir_version,
            "instrumentation_version": self.instrumentation_version,
            "status": V3_INSTRUMENTATION_STATUS,
            "graph_id": self.graph_id,
            "backend": self.backend,
            "hardware": self.hardware,
            "phase_timings": tuple(record.to_metadata() for record in self.phase_timings),
            "evidence_records": tuple(record.to_metadata() for record in self.evidence_records),
            "residency_evidence": tuple(record.to_metadata() for record in self.residency_evidence),
            "claim_boundary": self.claim_boundary.to_metadata(),
            "claim_readiness": self.claim_readiness,
            "public_claim_authorized": False,
        }


def claim_readiness_summary(packet: InstrumentationPacket) -> dict[str, bool]:
    return dict(packet.claim_readiness)


def _validate_phase_completeness(phase_timings: tuple[PhaseTimingRecord, ...]) -> None:
    if not phase_timings:
        raise GraphValidationError("instrumentation packet requires phase timings")
    phase_names = tuple(record.phase for record in phase_timings)
    missing = tuple(phase for phase in REQUIRED_PHASE_NAMES if phase not in phase_names)
    if missing:
        raise GraphValidationError("instrumentation packet is missing phases: " + ", ".join(missing))


def _validate_evidence_references(
    phase_timings: tuple[PhaseTimingRecord, ...],
    evidence_records: tuple[EvidenceRecord, ...],
    residency_evidence: tuple[ResidencyEvidence, ...],
) -> None:
    evidence_ids = tuple(record.evidence_id for record in evidence_records)
    if len(set(evidence_ids)) != len(evidence_ids):
        raise GraphValidationError("evidence ids must be unique")
    known = set(evidence_ids)
    for timing in phase_timings:
        unknown = sorted(set(timing.evidence_ids) - known)
        if unknown:
            raise GraphValidationError(f"phase timing references unknown evidence ids: {unknown!r}")
    for evidence in residency_evidence:
        unknown = sorted(set(evidence.evidence_ids) - known)
        if unknown:
            raise GraphValidationError(f"residency evidence references unknown evidence ids: {unknown!r}")


def empty_claim_boundary_metadata() -> dict[str, bool]:
    return {key: False for key in CLAIM_BOUNDARY_KEYS}
