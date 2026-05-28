from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from math import prod
from typing import Any

from .partner import ACCESS_MODES
from .partner import DEVICE_TYPES
from .partner import RtdlTensorDescriptor


V2_4_PARTNER_PROTOCOL_VERSION = "rtdl.partner.v2.4"
V2_4_PROTOCOL_SCOPE = "rtdl_primitive_handoff_only"
V2_4_STREAM_POLICY = "stream_handle_field_present_but_reserved_zero"
V2_4_DEFAULT_PARTNER_DIRECTION = "triton_first_with_numba_fallback"
V2_4_NATIVE_ENGINE_BOUNDARY = "app_agnostic_native_engine"
V2_4_MEMORY_MANAGER_BOUNDARY = "not_a_general_purpose_memory_manager"
V2_4_PERFORMANCE_BASIS_HARDWARE = "NVIDIA RTX A5000 pod evidence"
V2_4_PRIMARY_BENCHMARK_APP_COUNT = 10
V2_4_PRIMARY_COMPARISON_ROW_COUNT = 11
V2_4_PROMOTED_PATH_TOLERANCE_RATIO = 0.10
V2_4_OPT_IN_TOLERANCE_RATIO = 0.20
V2_4_STATUS_PROTOCOL_ONLY = "protocol_descriptor_only"
V2_4_COMPLETION_STATUS = "internal_v2_4_complete_no_public_release_tag"
V2_4_NEXT_PARTNER_MILESTONE = "v2_5_triton_first_with_numba_fallback"
V2_4_RELEASE_TAG_AUTHORIZED = False
V2_4_PACKAGE_INSTALL_CLAIM_AUTHORIZED = False
V2_4_PUBLIC_SPEEDUP_CLAIM_AUTHORIZED = False

V2_4_PHASES = (
    "setup",
    "scene_build",
    "transfer",
    "query_preparation",
    "rt_traversal",
    "partner_continuation",
    "materialization",
    "download",
)

V2_4_FORBIDDEN_NATIVE_APP_TOKENS = (
    "barnes",
    "dbscan",
    "raydb",
    "contact",
    "collision",
    "robot",
    "librts",
    "rtnn",
    "hausdorff",
    "triangle_counting",
)

V2_4_REQUIRED_COMPLETION_DELIVERABLES = (
    "roadmap_3ai_consensus",
    "typed_buffer_protocol",
    "prepared_session_protocol",
    "segmented_chunked_row_streaming_protocol",
    "benchmark_protocol_integration",
    "machine_readable_phase_timing",
    "benchmark_performance_basis_gate",
    "native_vocabulary_boundary_gate",
    "partner_direction_gate",
    "documentation_boundary_sync",
)

V2_4_COMPLETION_EVIDENCE_REPORTS = (
    "docs/reports/goal2657_v2_4_v2_5_partner_roadmap_3ai_consensus_2026-05-27.md",
    "docs/reports/goal2658_v2_4_partner_protocol_foundation_2026-05-27.md",
    "docs/reports/goal2659_v2_4_benchmark_protocol_integration_2026-05-27.md",
    "docs/reports/goal2660_v2_4_phase_timing_metadata_2026-05-27.md",
    "docs/reports/goal2661_v2_4_completion_gate_2026-05-27.md",
    "docs/reports/goal2661_v2_4_completion_claude_review_2026-05-27.md",
    "docs/reports/goal2661_v2_4_completion_gemini_review_2026-05-27.md",
    "docs/reports/goal2661_v2_4_completion_3ai_consensus_2026-05-27.md",
)

V2_4_V2_5_PRECONDITIONS = (
    "keep OptiX RT traversal inside generic RTDL primitives",
    "keep Triton/Numba in preparation, continuation, reduction, compaction, and finalization roles",
    "preserve same-phase benchmark comparisons against the v2.3/v2.4 basis",
    "reject app-domain vocabulary in native primitive symbols",
    "label slower convenience paths as optional, compatibility, learner/preview, or rejected",
    "explicitly classify every non-piloted v2.5 benchmark app",
)


@dataclass(frozen=True)
class RtdlBenchmarkBasisRow:
    app: str
    contract: str
    optix_vs_embree_speedup: float
    hardware: str = V2_4_PERFORMANCE_BASIS_HARDWARE
    phase_contract: str = "accepted_exact_subpath"

    @property
    def requires_protocol_overhead_audit(self) -> bool:
        return self.optix_vs_embree_speedup < 6.0

    def to_metadata(self) -> dict[str, object]:
        return {
            "app": self.app,
            "contract": self.contract,
            "optix_vs_embree_speedup": float(self.optix_vs_embree_speedup),
            "hardware": self.hardware,
            "phase_contract": self.phase_contract,
            "requires_protocol_overhead_audit": self.requires_protocol_overhead_audit,
        }


V2_4_BENCHMARK_PERFORMANCE_BASIS: tuple[RtdlBenchmarkBasisRow, ...] = (
    RtdlBenchmarkBasisRow("Hausdorff / X-HD-style", "prepared fixed-radius threshold", 3.29),
    RtdlBenchmarkBasisRow("Spatial RayJoin-style", "prepared spatial relation summary", 38.36),
    RtdlBenchmarkBasisRow("RT-DBSCAN-style", "fixed-radius rows plus continuation", 12.71),
    RtdlBenchmarkBasisRow("Robot collision", "prepared collision flags", 5.29),
    RtdlBenchmarkBasisRow("RayDB-style grouped aggregate", "prepared grouped count", 27.67),
    RtdlBenchmarkBasisRow("RayDB-style grouped aggregate", "prepared grouped sum", 104.00),
    RtdlBenchmarkBasisRow("Barnes-Hut / RT-BarnesHut-style", "node coverage threshold", 4.55),
    RtdlBenchmarkBasisRow("LibRTS-style spatial index", "AABB index count-only", 29.95),
    RtdlBenchmarkBasisRow("RTNN neighbor search", "prepared 3-D ranked summary", 172.14),
    RtdlBenchmarkBasisRow("Triangle counting", "RT-Graph-style RT-2A1 summary", 107.16),
    RtdlBenchmarkBasisRow("Bounded contact witness / contact-manifold", "bounded witness rows", 26.29),
)


@dataclass(frozen=True)
class RtdlBufferDescriptor:
    """RTDL primitive handoff descriptor.

    This descriptor is deliberately narrower than a memory manager. It records
    enough typed buffer metadata for RTDL primitive preparation and phase
    accounting, while keeping ownership, allocation policy, and arbitrary
    partner program execution outside RTDL.
    """

    name: str
    dtype: str
    shape: tuple[int, ...]
    device_type: str
    device_id: int = 0
    data_ptr: int | None = None
    strides_bytes: tuple[int, ...] | None = None
    byte_offset: int = 0
    access_mode: str = "read"
    source_protocol: str = "python"
    lifetime: str = "caller_retained"
    mutability: str = "immutable"
    stream_handle: int = 0
    alignment_bytes: int = 1
    capacity_elements: int | None = None
    owner: Any = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not str(self.name):
            raise ValueError("buffer descriptor requires a non-empty name")
        if not str(self.dtype):
            raise ValueError("buffer descriptor requires a dtype")
        _validate_device(self.device_type, self.device_id)
        _validate_access_mode(self.access_mode)
        shape = tuple(int(dim) for dim in self.shape)
        if any(dim < 0 for dim in shape):
            raise ValueError("buffer descriptor shape dimensions must be non-negative")
        if self.strides_bytes is not None and len(self.strides_bytes) != len(shape):
            raise ValueError("buffer descriptor strides must match shape rank")
        if int(self.byte_offset) < 0:
            raise ValueError("buffer descriptor byte_offset must be non-negative")
        if int(self.stream_handle) != 0:
            raise ValueError("v2.4 stream handles are recorded but reserved; expected 0")
        if int(self.alignment_bytes) <= 0:
            raise ValueError("buffer descriptor alignment must be positive")
        if self.capacity_elements is not None and int(self.capacity_elements) < _element_count(shape):
            raise ValueError("buffer descriptor capacity_elements cannot be smaller than shape element count")
        if self.mutability not in {"immutable", "mutable"}:
            raise ValueError("buffer descriptor mutability must be immutable or mutable")
        if self.lifetime not in {"caller_retained", "session_retained", "borrowed"}:
            raise ValueError("buffer descriptor lifetime must be caller_retained, session_retained, or borrowed")
        object.__setattr__(self, "shape", shape)
        if self.strides_bytes is not None:
            object.__setattr__(self, "strides_bytes", tuple(int(stride) for stride in self.strides_bytes))
        if self.capacity_elements is not None:
            object.__setattr__(self, "capacity_elements", int(self.capacity_elements))

    @property
    def element_count(self) -> int:
        return _element_count(self.shape)

    @property
    def effective_capacity_elements(self) -> int:
        return self.element_count if self.capacity_elements is None else int(self.capacity_elements)

    @property
    def is_cuda(self) -> bool:
        return self.device_type == "cuda"

    def to_metadata(self) -> dict[str, object]:
        return {
            "name": self.name,
            "dtype": self.dtype,
            "shape": self.shape,
            "device": f"{self.device_type}:{self.device_id}",
            "data_ptr_observed": self.data_ptr is not None and int(self.data_ptr) > 0,
            "strides_bytes": self.strides_bytes,
            "byte_offset": int(self.byte_offset),
            "access_mode": self.access_mode,
            "source_protocol": self.source_protocol,
            "lifetime": self.lifetime,
            "mutability": self.mutability,
            "stream_handle": int(self.stream_handle),
            "alignment_bytes": int(self.alignment_bytes),
            "element_count": self.element_count,
            "capacity_elements": self.effective_capacity_elements,
            "scope": V2_4_PROTOCOL_SCOPE,
            "memory_manager_boundary": V2_4_MEMORY_MANAGER_BOUNDARY,
        }


@dataclass(frozen=True)
class RtdlPreparedSessionDescriptor:
    session_id: str
    backend: str
    primitive: str
    input_buffers: tuple[RtdlBufferDescriptor, ...]
    output_buffers: tuple[RtdlBufferDescriptor, ...] = ()
    reusable_scene: bool = False
    reusable_query_buffers: bool = False
    reusable_output_buffers: bool = False
    phase_contract: str = "prepared_query"
    native_symbols: tuple[str, ...] = ()
    status: str = V2_4_STATUS_PROTOCOL_ONLY

    def __post_init__(self) -> None:
        if not str(self.session_id):
            raise ValueError("prepared session requires a non-empty session_id")
        normalized_backend = str(self.backend).strip().lower()
        if normalized_backend not in {"cpu", "embree", "optix"}:
            raise ValueError("prepared session backend must be cpu, embree, or optix")
        _validate_no_app_native_vocab(self.primitive, label="primitive")
        for symbol in self.native_symbols:
            _validate_no_app_native_vocab(symbol, label="native symbol")
        _validate_unique_buffer_names(self.input_buffers, self.output_buffers)
        if self.status != V2_4_STATUS_PROTOCOL_ONLY:
            raise ValueError("v2.4 prepared session descriptors are protocol-only until implementation evidence exists")
        object.__setattr__(self, "backend", normalized_backend)
        object.__setattr__(self, "native_symbols", tuple(str(symbol) for symbol in self.native_symbols))

    def to_metadata(self) -> dict[str, object]:
        return {
            "session_id": self.session_id,
            "backend": self.backend,
            "primitive": self.primitive,
            "input_buffers": tuple(buffer.to_metadata() for buffer in self.input_buffers),
            "output_buffers": tuple(buffer.to_metadata() for buffer in self.output_buffers),
            "reusable_scene": bool(self.reusable_scene),
            "reusable_query_buffers": bool(self.reusable_query_buffers),
            "reusable_output_buffers": bool(self.reusable_output_buffers),
            "phase_contract": self.phase_contract,
            "native_symbols": self.native_symbols,
            "status": self.status,
            "requires_phase_timing": True,
            "native_engine_boundary": V2_4_NATIVE_ENGINE_BOUNDARY,
            "app_specific_native_vocab_allowed": False,
        }


@dataclass(frozen=True)
class RtdlV24PartnerProtocolContract:
    version: str = V2_4_PARTNER_PROTOCOL_VERSION
    scope: str = V2_4_PROTOCOL_SCOPE
    native_engine_boundary: str = V2_4_NATIVE_ENGINE_BOUNDARY
    memory_manager_boundary: str = V2_4_MEMORY_MANAGER_BOUNDARY
    stream_policy: str = V2_4_STREAM_POLICY
    default_partner_direction: str = V2_4_DEFAULT_PARTNER_DIRECTION
    benchmark_app_count: int = V2_4_PRIMARY_BENCHMARK_APP_COUNT
    primary_comparison_row_count: int = V2_4_PRIMARY_COMPARISON_ROW_COUNT
    promoted_path_tolerance_ratio: float = V2_4_PROMOTED_PATH_TOLERANCE_RATIO
    opt_in_tolerance_ratio: float = V2_4_OPT_IN_TOLERANCE_RATIO
    phases: tuple[str, ...] = V2_4_PHASES
    benchmark_basis: tuple[RtdlBenchmarkBasisRow, ...] = V2_4_BENCHMARK_PERFORMANCE_BASIS

    def to_metadata(self) -> dict[str, object]:
        return {
            "version": self.version,
            "scope": self.scope,
            "native_engine_boundary": self.native_engine_boundary,
            "memory_manager_boundary": self.memory_manager_boundary,
            "stream_policy": self.stream_policy,
            "default_partner_direction": self.default_partner_direction,
            "benchmark_app_count": int(self.benchmark_app_count),
            "primary_comparison_row_count": int(self.primary_comparison_row_count),
            "promoted_path_tolerance_ratio": float(self.promoted_path_tolerance_ratio),
            "opt_in_tolerance_ratio": float(self.opt_in_tolerance_ratio),
            "phases": self.phases,
            "benchmark_basis": tuple(row.to_metadata() for row in self.benchmark_basis),
        }


def v2_4_partner_protocol_contract() -> RtdlV24PartnerProtocolContract:
    return RtdlV24PartnerProtocolContract()


def validate_v2_4_partner_protocol_contract(
    contract: RtdlV24PartnerProtocolContract | None = None,
) -> dict[str, object]:
    contract = v2_4_partner_protocol_contract() if contract is None else contract
    errors: list[str] = []
    if contract.version != V2_4_PARTNER_PROTOCOL_VERSION:
        errors.append("unexpected v2.4 partner protocol version")
    if contract.scope != V2_4_PROTOCOL_SCOPE:
        errors.append("v2.4 partner protocol must stay scoped to RTDL primitive handoff")
    if contract.native_engine_boundary != V2_4_NATIVE_ENGINE_BOUNDARY:
        errors.append("native engine boundary must remain app-agnostic")
    if contract.memory_manager_boundary != V2_4_MEMORY_MANAGER_BOUNDARY:
        errors.append("v2.4 descriptor work must not become a general-purpose memory manager")
    if contract.stream_policy != V2_4_STREAM_POLICY:
        errors.append("stream handles must remain reserved-zero until evidence exists")
    if contract.default_partner_direction != V2_4_DEFAULT_PARTNER_DIRECTION:
        errors.append("v2.4/v2.5 roadmap requires Triton-first with Numba fallback")
    if int(contract.benchmark_app_count) != V2_4_PRIMARY_BENCHMARK_APP_COUNT:
        errors.append("benchmark app count must remain 10 for the current v2.3 basis")
    if int(contract.primary_comparison_row_count) != V2_4_PRIMARY_COMPARISON_ROW_COUNT:
        errors.append("primary comparison row count must remain 11 because RayDB has count and sum")
    distinct_apps = {row.app for row in contract.benchmark_basis}
    if len(distinct_apps) != int(contract.benchmark_app_count):
        errors.append("distinct benchmark app count must match the declared benchmark_app_count")
    if len(contract.benchmark_basis) != int(contract.primary_comparison_row_count):
        errors.append("benchmark basis row count must match the declared primary_comparison_row_count")
    if float(contract.promoted_path_tolerance_ratio) != V2_4_PROMOTED_PATH_TOLERANCE_RATIO:
        errors.append("promoted path tolerance ratio must remain 10 percent")
    if float(contract.opt_in_tolerance_ratio) != V2_4_OPT_IN_TOLERANCE_RATIO:
        errors.append("opt-in tolerance ratio must remain 20 percent")
    if tuple(contract.phases) != V2_4_PHASES:
        errors.append("phase timing contract must preserve the accepted split")
    if not any(row.requires_protocol_overhead_audit for row in contract.benchmark_basis):
        errors.append("low-margin benchmark rows must require protocol-overhead audit")
    return {
        "status": "accept" if not errors else "reject",
        "version": contract.version,
        "scope": contract.scope,
        "native_engine_boundary": contract.native_engine_boundary,
        "memory_manager_boundary": contract.memory_manager_boundary,
        "benchmark_app_count": int(contract.benchmark_app_count),
        "primary_comparison_row_count": int(contract.primary_comparison_row_count),
        "low_margin_rows": tuple(
            row.app for row in contract.benchmark_basis if row.requires_protocol_overhead_audit
        ),
        "errors": tuple(errors),
    }


def v2_4_completion_gate() -> dict[str, object]:
    """Return the internal v2.4 completion gate.

    This is deliberately not a public release gate. It closes the v2.4
    protocol-cleanup milestone and records what v2.5 may build on.
    """

    contract_validation = validate_v2_4_partner_protocol_contract()
    return {
        "status": V2_4_COMPLETION_STATUS,
        "protocol_version": V2_4_PARTNER_PROTOCOL_VERSION,
        "internal_milestone_complete": True,
        "public_release_tag_authorized": V2_4_RELEASE_TAG_AUTHORIZED,
        "package_install_claim_authorized": V2_4_PACKAGE_INSTALL_CLAIM_AUTHORIZED,
        "public_speedup_claim_authorized": V2_4_PUBLIC_SPEEDUP_CLAIM_AUTHORIZED,
        "required_deliverables": V2_4_REQUIRED_COMPLETION_DELIVERABLES,
        "evidence_reports": V2_4_COMPLETION_EVIDENCE_REPORTS,
        "benchmark_app_count": V2_4_PRIMARY_BENCHMARK_APP_COUNT,
        "primary_comparison_row_count": V2_4_PRIMARY_COMPARISON_ROW_COUNT,
        "benchmark_basis_hardware": V2_4_PERFORMANCE_BASIS_HARDWARE,
        "same_contract_benchmark_basis_retained": contract_validation["status"] == "accept",
        "low_margin_rows": contract_validation["low_margin_rows"],
        "native_engine_boundary": V2_4_NATIVE_ENGINE_BOUNDARY,
        "app_specific_native_vocab_allowed": False,
        "memory_manager_boundary": V2_4_MEMORY_MANAGER_BOUNDARY,
        "default_partner_direction": V2_4_DEFAULT_PARTNER_DIRECTION,
        "next_partner_milestone": V2_4_NEXT_PARTNER_MILESTONE,
        "v2_5_preconditions": V2_4_V2_5_PRECONDITIONS,
    }


def validate_v2_4_completion_gate(gate: dict[str, Any] | None = None) -> dict[str, object]:
    gate = v2_4_completion_gate() if gate is None else gate
    errors: list[str] = []

    if gate.get("status") != V2_4_COMPLETION_STATUS:
        errors.append("unexpected v2.4 completion status")
    if gate.get("protocol_version") != V2_4_PARTNER_PROTOCOL_VERSION:
        errors.append("unexpected v2.4 protocol version")
    if gate.get("internal_milestone_complete") is not True:
        errors.append("v2.4 internal milestone must be explicitly complete")
    if gate.get("public_release_tag_authorized") is not False:
        errors.append("v2.4 completion does not authorize a public release tag")
    if gate.get("package_install_claim_authorized") is not False:
        errors.append("v2.4 completion does not authorize package-install claims")
    if gate.get("public_speedup_claim_authorized") is not False:
        errors.append("v2.4 completion does not authorize new public speedup claims")
    if tuple(gate.get("required_deliverables", ())) != V2_4_REQUIRED_COMPLETION_DELIVERABLES:
        errors.append("v2.4 required deliverables changed unexpectedly")
    if tuple(gate.get("evidence_reports", ())) != V2_4_COMPLETION_EVIDENCE_REPORTS:
        errors.append("v2.4 evidence report list changed unexpectedly")
    if gate.get("same_contract_benchmark_basis_retained") is not True:
        errors.append("same-contract benchmark basis must be retained")
    if gate.get("benchmark_app_count") != V2_4_PRIMARY_BENCHMARK_APP_COUNT:
        errors.append("benchmark app count must remain 10")
    if gate.get("primary_comparison_row_count") != V2_4_PRIMARY_COMPARISON_ROW_COUNT:
        errors.append("primary comparison row count must remain 11")
    if gate.get("native_engine_boundary") != V2_4_NATIVE_ENGINE_BOUNDARY:
        errors.append("native engine boundary must remain app-agnostic")
    if gate.get("app_specific_native_vocab_allowed") is not False:
        errors.append("app-specific native vocabulary must remain rejected")
    if gate.get("default_partner_direction") != V2_4_DEFAULT_PARTNER_DIRECTION:
        errors.append("next partner direction must remain Triton-first with Numba fallback")
    if gate.get("next_partner_milestone") != V2_4_NEXT_PARTNER_MILESTONE:
        errors.append("unexpected next partner milestone")
    if tuple(gate.get("v2_5_preconditions", ())) != V2_4_V2_5_PRECONDITIONS:
        errors.append("v2.5 preconditions must preserve the Goal2657 consensus gates")

    return {
        "status": "accept" if not errors else "reject",
        "completion_status": gate.get("status"),
        "protocol_version": gate.get("protocol_version"),
        "internal_milestone_complete": gate.get("internal_milestone_complete"),
        "public_release_tag_authorized": gate.get("public_release_tag_authorized"),
        "package_install_claim_authorized": gate.get("package_install_claim_authorized"),
        "public_speedup_claim_authorized": gate.get("public_speedup_claim_authorized"),
        "next_partner_milestone": gate.get("next_partner_milestone"),
        "errors": tuple(errors),
    }


def buffer_descriptor_from_tensor_descriptor(
    name: str,
    descriptor: RtdlTensorDescriptor,
    *,
    access_mode: str | None = None,
    lifetime: str = "caller_retained",
    mutability: str | None = None,
    capacity_elements: int | None = None,
) -> RtdlBufferDescriptor:
    access = descriptor.access_mode if access_mode is None else access_mode
    inferred_mutability = "immutable" if access == "read" else "mutable"
    return RtdlBufferDescriptor(
        name=name,
        dtype=descriptor.dtype,
        shape=descriptor.shape,
        device_type=descriptor.device_type,
        device_id=descriptor.device_id,
        data_ptr=descriptor.data_ptr,
        strides_bytes=descriptor.strides,
        byte_offset=descriptor.byte_offset,
        access_mode=access,
        source_protocol=descriptor.source_protocol,
        lifetime=lifetime,
        mutability=inferred_mutability if mutability is None else mutability,
        stream_handle=descriptor.stream_handle,
        capacity_elements=capacity_elements,
        owner=descriptor.owner,
    )


def low_margin_benchmark_rows(
    basis: tuple[RtdlBenchmarkBasisRow, ...] = V2_4_BENCHMARK_PERFORMANCE_BASIS,
) -> tuple[RtdlBenchmarkBasisRow, ...]:
    return tuple(row for row in basis if row.requires_protocol_overhead_audit)


def v2_4_phase_timing_metadata(
    phases_sec: dict[str, float],
    *,
    promoted_performance_path: bool,
    same_phase_contract_as_basis: bool,
    source: str,
) -> dict[str, object]:
    record = {
        "source": str(source),
        "phases_sec": {str(name): float(value) for name, value in phases_sec.items()},
        "promoted_performance_path": bool(promoted_performance_path),
        "same_phase_contract_as_basis": bool(same_phase_contract_as_basis),
        "phase_contract_version": V2_4_PARTNER_PROTOCOL_VERSION,
    }
    return {
        **record,
        "validation": validate_phase_timing_record(record),
    }


def validate_phase_timing_record(record: dict[str, Any]) -> dict[str, object]:
    """Validate v2.4 machine-readable phase timing metadata.

    Missing phases are acceptable because not every primitive has every phase,
    but RT traversal and partner continuation must not be collapsed into a
    single ambiguous timing field.
    """

    errors: list[str] = []
    if not isinstance(record, dict):
        return {"status": "reject", "errors": ("phase timing record must be a dict",)}
    phases = record.get("phases_sec")
    if not isinstance(phases, dict):
        errors.append("phase timing record requires a phases_sec mapping")
        phases = {}
    unknown = tuple(sorted(set(phases) - set(V2_4_PHASES)))
    if unknown:
        errors.append(f"unknown phase names: {', '.join(unknown)}")
    for name, value in phases.items():
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            errors.append(f"phase {name} must be numeric seconds")
            continue
        if numeric < 0.0:
            errors.append(f"phase {name} must be non-negative")
    if "rt_and_partner_combined" in phases:
        errors.append("RT traversal and partner continuation must be reported as separate phases")
    if record.get("promoted_performance_path") and record.get("same_phase_contract_as_basis") is not True:
        errors.append("promoted performance paths must compare the same phase contract as the basis row")
    return {
        "status": "accept" if not errors else "reject",
        "known_phases": tuple(name for name in V2_4_PHASES if name in phases),
        "errors": tuple(errors),
    }


def _validate_device(device_type: str, device_id: int) -> None:
    if device_type not in DEVICE_TYPES:
        raise ValueError(f"device_type must be one of {DEVICE_TYPES}")
    if int(device_id) < 0:
        raise ValueError("device_id must be non-negative")


def _validate_access_mode(access_mode: str) -> None:
    if access_mode not in ACCESS_MODES:
        raise ValueError(f"access_mode must be one of {ACCESS_MODES}")


def _validate_no_app_native_vocab(value: str, *, label: str) -> None:
    normalized = str(value).strip().lower()
    if not normalized:
        raise ValueError(f"{label} must be non-empty")
    for token in V2_4_FORBIDDEN_NATIVE_APP_TOKENS:
        if token in normalized:
            raise ValueError(f"{label} contains app-specific token `{token}`")


def _validate_unique_buffer_names(
    input_buffers: tuple[RtdlBufferDescriptor, ...],
    output_buffers: tuple[RtdlBufferDescriptor, ...],
) -> None:
    names = [buffer.name for buffer in (*input_buffers, *output_buffers)]
    if len(names) != len(set(names)):
        raise ValueError("prepared session buffer names must be unique")


def _element_count(shape: tuple[int, ...]) -> int:
    return int(prod(shape)) if shape else 1
