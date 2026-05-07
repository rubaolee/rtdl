from __future__ import annotations

from typing import Any

from .v1_5_3_reduced_copy import validate_v1_5_3_post_consensus_checkpoint_gate


V1_5_4_DEVICE_ZERO_COPY_ENTRY_STATUS = "ready_to_start_separate_device_zero_copy_design_claims_blocked"
V1_5_4_DEVICE_ZERO_COPY_TRACK = "python_rtdl"
V1_5_4_DEVICE_ZERO_COPY_SCOPE = (
    "separate_device_resident_or_shareable_memory_path",
    "explicit_host_reduced_copy_vs_device_zero_copy_boundary",
    "optix_first_real_nvidia_evidence_required",
)
V1_5_4_DEVICE_ZERO_COPY_REQUIRED_PRECONDITIONS = (
    "v1_5_3_post_consensus_internal_evidence_checkpoint",
    "same_contract_embree_optix_typed_host_parity_accepted",
    "diagnostic_typed_host_reuse_data_collection_accepted",
    "three_ai_v1_5_3_evidence_summary_consensus",
)
V1_5_4_DEVICE_ZERO_COPY_BLOCKED_CLAIMS = (
    "true_zero_copy",
    "public_speedup",
    "whole_app_speedup",
    "stable_public_primitive",
    "partner_tensor_handoff",
    "release_action",
)
V1_5_4_DEVICE_ZERO_COPY_REQUIRED_FUTURE_EVIDENCE = (
    "measured_gpu_resident_or_externally_shareable_device_memory_path",
    "embree_optix_contract_boundary_for_any_claimed_same_contract_behavior",
    "copy_or_transfer_count_measurement_for_device_path",
    "pod_or_equivalent_real_nvidia_validation",
    "external_ai_review_before_public_performance_wording",
)
V1_5_4_DEVICE_MEMORY_KINDS = (
    "host_staging",
    "device_resident",
    "external_shareable_device",
)
V1_5_4_DEVICE_MEMORY_ALLOWED_DTYPES = (
    "int32",
    "int64",
    "float32",
    "float64",
    "uint32",
    "uint64",
)
V1_5_4_DEVICE_MEMORY_ZERO_COPY_CANDIDATE_KINDS = (
    "device_resident",
    "external_shareable_device",
)
V1_5_4_DEVICE_MEASUREMENT_REQUIRED_FIELDS = (
    "host_to_device_transfers",
    "device_to_host_transfers",
    "device_residency_observed",
    "measurement_backend",
    "measurement_scope",
)
V1_5_4_GPU_MEMORY_ARCHITECTURE_CONSENSUS_STATUS = "accepted_python_rtdl_vs_partner_rtdl_memory_boundary"
V1_5_4_GPU_MEMORY_ARCHITECTURE_REQUIRED_EVIDENCE = (
    "docs/reports/goal1479_gpu_memory_architecture_python_rtdl_vs_partner_rtdl_2026-05-07.md",
    "docs/handoff/goal1479_gpu_memory_architecture_external_review_request_2026-05-07.md",
    "docs/reports/claude_goal1479_gpu_memory_architecture_review_2026-05-07.md",
    "docs/reports/gemini_goal1479_gpu_memory_architecture_review_2026-05-07.md",
    "docs/reports/three_ai_goal1479_gpu_memory_architecture_consensus_2026-05-07.md",
)
V1_5_4_PYTHON_RTDL_MANAGED_BUFFER_STATUS = "ready_to_design_rtdl_owned_managed_buffers_claims_blocked"
V1_5_4_PYTHON_RTDL_MANAGED_BUFFER_KINDS = (
    "prepared_host",
    "pinned_host_staging",
    "rtdl_device_resident",
    "rtdl_managed_unified",
)
V1_5_4_PYTHON_RTDL_MANAGED_BUFFER_REQUIRED_METADATA = (
    "buffer_kind",
    "backend",
    "device",
    "dtype",
    "shape",
    "owner",
    "lifetime",
    "copy_boundary",
    "residency_state",
    "transfer_count_state",
)
V1_5_4_MANAGED_BUFFER_LIFETIMES = (
    "single_call",
    "session",
    "explicit_release",
)
V1_5_4_MANAGED_BUFFER_RESIDENCY_STATES = (
    "host_resident",
    "device_candidate_unmeasured",
    "managed_unified_candidate_unmeasured",
)
V1_5_4_MANAGED_BUFFER_TRANSFER_STATES = (
    "not_measured",
    "instrumentation_planned",
    "measured_candidate",
)
V1_5_4_MANAGED_BUFFER_LIFECYCLE_STATES = (
    "active_unmeasured",
    "released",
)
V1_5_4_MANAGED_BUFFER_TRANSFER_DIRECTIONS = (
    "host_to_rtdl",
    "rtdl_to_host",
    "rtdl_internal",
)
V1_5_4_MANAGED_BUFFER_ALLOCATION_METHODS = (
    "host_prepared",
    "host_pinned_staging",
    "cuda_device_alloc",
    "cuda_managed_alloc",
    "synthetic_contract_only",
)


def v1_5_4_device_zero_copy_entry_gate() -> dict[str, Any]:
    """Describe the safe entry point for the next Python+RTDL zero-copy lane."""
    prior_gate = validate_v1_5_3_post_consensus_checkpoint_gate()
    return {
        "status": V1_5_4_DEVICE_ZERO_COPY_ENTRY_STATUS,
        "track": V1_5_4_DEVICE_ZERO_COPY_TRACK,
        "scope": V1_5_4_DEVICE_ZERO_COPY_SCOPE,
        "required_preconditions": V1_5_4_DEVICE_ZERO_COPY_REQUIRED_PRECONDITIONS,
        "prior_checkpoint_status": prior_gate["status"],
        "prior_checkpoint_accepted": prior_gate["internal_evidence_checkpoint_accepted"],
        "ready_to_start_design": True,
        "ready_to_claim_true_zero_copy": False,
        "ready_to_claim_public_speedup": False,
        "ready_to_release": False,
        "blocked_claims": V1_5_4_DEVICE_ZERO_COPY_BLOCKED_CLAIMS,
        "required_future_evidence": V1_5_4_DEVICE_ZERO_COPY_REQUIRED_FUTURE_EVIDENCE,
        "allowed_next_actions": (
            "design_device_memory_descriptor_contract",
            "design_device_path_copy_count_instrumentation",
            "prepare_optix_first_pod_validation_plan",
            "keep_host_reduced_copy_evidence_separate_from_true_zero_copy_claims",
        ),
        "requires_pod_now": False,
        "pod_required_for": (
            "real_nvidia_device_path_validation",
            "device_memory_transfer_or_residency_measurement",
            "any_public_gpu_performance_claim_review_package",
        ),
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "partner_tensor_handoff_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "v1.5.4 may start a separate device zero-copy design lane only "
            "after the accepted v1.5.3 internal typed-host checkpoint. The "
            "v1.5.3 host reduced-copy evidence is not true zero-copy evidence. "
            "This entry gate does not authorize true zero-copy, public speedup "
            "wording, whole-app claims, stable primitive promotion, partner "
            "tensor handoff, or release action."
        ),
    }


def validate_v1_5_4_device_zero_copy_entry_gate() -> dict[str, Any]:
    gate = v1_5_4_device_zero_copy_entry_gate()
    if gate["status"] != V1_5_4_DEVICE_ZERO_COPY_ENTRY_STATUS:
        raise ValueError("invalid v1.5.4 device zero-copy entry gate status")
    if gate["track"] != V1_5_4_DEVICE_ZERO_COPY_TRACK:
        raise ValueError("invalid v1.5.4 device zero-copy track")
    if tuple(gate["scope"]) != V1_5_4_DEVICE_ZERO_COPY_SCOPE:
        raise ValueError("v1.5.4 device zero-copy scope changed")
    if tuple(gate["required_preconditions"]) != V1_5_4_DEVICE_ZERO_COPY_REQUIRED_PRECONDITIONS:
        raise ValueError("v1.5.4 device zero-copy required preconditions changed")
    if tuple(gate["blocked_claims"]) != V1_5_4_DEVICE_ZERO_COPY_BLOCKED_CLAIMS:
        raise ValueError("v1.5.4 device zero-copy blocked claims changed")
    if tuple(gate["required_future_evidence"]) != V1_5_4_DEVICE_ZERO_COPY_REQUIRED_FUTURE_EVIDENCE:
        raise ValueError("v1.5.4 device zero-copy required future evidence changed")
    if gate["prior_checkpoint_accepted"] is not True:
        raise ValueError("v1.5.4 device zero-copy requires accepted v1.5.3 checkpoint")
    if gate["ready_to_start_design"] is not True:
        raise ValueError("v1.5.4 device zero-copy design should be ready to start")
    for flag in (
        "ready_to_claim_true_zero_copy",
        "ready_to_claim_public_speedup",
        "ready_to_release",
        "true_zero_copy_authorized",
        "public_speedup_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "stable_public_primitive_authorized",
        "partner_tensor_handoff_authorized",
        "release_action_authorized",
    ):
        if gate[flag] is not False:
            raise ValueError(f"v1.5.4 device zero-copy entry gate must keep {flag}=False")
    for phrase in (
        "separate device zero-copy design lane",
        "host reduced-copy evidence is not true zero-copy evidence",
        "does not authorize true zero-copy",
        "public speedup wording",
        "partner tensor handoff",
        "release action",
    ):
        if phrase not in gate["claim_boundary"]:
            raise ValueError("v1.5.4 device zero-copy claim boundary is incomplete")
    return gate


def prepare_v1_5_4_device_memory_descriptor(
    *,
    memory_kind: str,
    backend: str,
    device: str,
    dtype: str,
    shape: tuple[int, ...] | list[int],
    owner: str,
    pointer: int | None = None,
    byte_count: int | None = None,
    external_handle: str | None = None,
    copy_boundary: str | None = None,
) -> dict[str, Any]:
    """Prepare a design-time memory descriptor for the v1.5.4 zero-copy lane."""
    kind = str(memory_kind)
    normalized_shape = tuple(int(value) for value in shape)
    if kind not in V1_5_4_DEVICE_MEMORY_KINDS:
        raise ValueError(f"unsupported v1.5.4 device memory kind: {kind}")
    if dtype not in V1_5_4_DEVICE_MEMORY_ALLOWED_DTYPES:
        raise ValueError(f"unsupported v1.5.4 device memory dtype: {dtype}")
    if not normalized_shape or any(value <= 0 for value in normalized_shape):
        raise ValueError("v1.5.4 device memory descriptor shape must contain positive dimensions")
    normalized_pointer = None if pointer is None else int(pointer)
    normalized_byte_count = None if byte_count is None else int(byte_count)
    if normalized_byte_count is not None and normalized_byte_count <= 0:
        raise ValueError("v1.5.4 device memory descriptor byte_count must be positive")
    if kind in V1_5_4_DEVICE_MEMORY_ZERO_COPY_CANDIDATE_KINDS and normalized_pointer is None:
        raise ValueError("v1.5.4 device zero-copy candidate descriptors require a pointer")
    if kind == "external_shareable_device" and not external_handle:
        raise ValueError("v1.5.4 external shareable device descriptors require an external_handle")
    if kind == "host_staging" and device != "cpu":
        raise ValueError("v1.5.4 host staging descriptors must use device='cpu'")
    if kind != "host_staging" and device == "cpu":
        raise ValueError("v1.5.4 device descriptors must not use device='cpu'")
    inferred_copy_boundary = copy_boundary
    if inferred_copy_boundary is None:
        inferred_copy_boundary = (
            "host_staging_reduced_copy"
            if kind == "host_staging"
            else "device_zero_copy_candidate_unmeasured"
        )
    zero_copy_candidate = kind in V1_5_4_DEVICE_MEMORY_ZERO_COPY_CANDIDATE_KINDS
    return {
        "status": "v1_5_4_device_memory_descriptor_prepared",
        "track": V1_5_4_DEVICE_ZERO_COPY_TRACK,
        "memory_kind": kind,
        "backend": str(backend),
        "device": str(device),
        "dtype": str(dtype),
        "shape": normalized_shape,
        "owner": str(owner),
        "pointer": normalized_pointer,
        "byte_count": normalized_byte_count,
        "external_handle": external_handle,
        "copy_boundary": inferred_copy_boundary,
        "zero_copy_candidate": zero_copy_candidate,
        "measured_device_residency": False,
        "measured_transfer_count": False,
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "partner_tensor_handoff_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "This v1.5.4 descriptor records memory ownership and location for "
            "a future device zero-copy lane. Device-resident descriptors are "
            "zero-copy candidates only until residency and transfer counts are "
            "measured on real hardware. Host staging descriptors are reduced-copy "
            "or transfer-reuse descriptors, not true zero-copy. This descriptor "
            "does not authorize true zero-copy, public speedup wording, "
            "whole-app claims, stable primitive promotion, partner tensor "
            "handoff, or release action."
        ),
    }


def validate_v1_5_4_device_memory_descriptor(descriptor: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(descriptor, dict):
        raise ValueError("v1.5.4 device memory descriptor must be a dictionary")
    if descriptor.get("status") != "v1_5_4_device_memory_descriptor_prepared":
        raise ValueError("invalid v1.5.4 device memory descriptor status")
    kind = descriptor.get("memory_kind")
    if kind not in V1_5_4_DEVICE_MEMORY_KINDS:
        raise ValueError("invalid v1.5.4 device memory kind")
    if descriptor.get("dtype") not in V1_5_4_DEVICE_MEMORY_ALLOWED_DTYPES:
        raise ValueError("invalid v1.5.4 device memory dtype")
    shape = tuple(descriptor.get("shape", ()))
    if not shape or any(int(value) <= 0 for value in shape):
        raise ValueError("invalid v1.5.4 device memory shape")
    expected_zero_copy_candidate = kind in V1_5_4_DEVICE_MEMORY_ZERO_COPY_CANDIDATE_KINDS
    if descriptor.get("zero_copy_candidate") is not expected_zero_copy_candidate:
        raise ValueError("invalid v1.5.4 zero-copy candidate flag")
    if kind == "host_staging":
        if descriptor.get("device") != "cpu":
            raise ValueError("v1.5.4 host staging descriptor must use cpu device")
        if descriptor.get("copy_boundary") != "host_staging_reduced_copy":
            raise ValueError("v1.5.4 host staging descriptor must remain reduced-copy")
    else:
        if descriptor.get("device") == "cpu":
            raise ValueError("v1.5.4 device descriptor must not use cpu device")
        if descriptor.get("pointer") is None:
            raise ValueError("v1.5.4 device descriptor requires pointer")
        if descriptor.get("copy_boundary") != "device_zero_copy_candidate_unmeasured":
            raise ValueError("v1.5.4 device descriptor must remain an unmeasured candidate")
    if kind == "external_shareable_device" and not descriptor.get("external_handle"):
        raise ValueError("v1.5.4 external shareable descriptor requires external_handle")
    for flag in (
        "measured_device_residency",
        "measured_transfer_count",
        "true_zero_copy_authorized",
        "public_speedup_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "stable_public_primitive_authorized",
        "partner_tensor_handoff_authorized",
        "release_action_authorized",
    ):
        if descriptor.get(flag) is not False:
            raise ValueError(f"v1.5.4 device memory descriptor must keep {flag}=False")
    for phrase in (
        "zero-copy candidates only",
        "Host staging descriptors are reduced-copy",
        "not true zero-copy",
        "does not authorize true zero-copy",
        "public speedup wording",
        "partner tensor handoff",
        "release action",
    ):
        if phrase not in descriptor.get("claim_boundary", ""):
            raise ValueError("v1.5.4 device memory descriptor claim boundary is incomplete")
    return descriptor


def attach_v1_5_4_device_memory_measurement(
    descriptor: dict[str, Any],
    *,
    host_to_device_transfers: int,
    device_to_host_transfers: int,
    device_residency_observed: bool,
    measurement_backend: str,
    measurement_scope: str,
    measured_on_real_nvidia: bool = False,
) -> dict[str, Any]:
    """Attach measurement metadata without promoting a descriptor to a public claim."""
    validated = validate_v1_5_4_device_memory_descriptor(descriptor)
    h2d = int(host_to_device_transfers)
    d2h = int(device_to_host_transfers)
    if h2d < 0 or d2h < 0:
        raise ValueError("v1.5.4 device memory transfer counts must be non-negative")
    if not measurement_backend:
        raise ValueError("v1.5.4 device memory measurement requires measurement_backend")
    if not measurement_scope:
        raise ValueError("v1.5.4 device memory measurement requires measurement_scope")
    device_residency = bool(device_residency_observed)
    measured_transfer_count = True
    measured_device_residency = device_residency and validated["memory_kind"] in V1_5_4_DEVICE_MEMORY_ZERO_COPY_CANDIDATE_KINDS
    true_zero_copy_evidence_candidate = (
        validated["zero_copy_candidate"]
        and measured_device_residency
        and h2d == 0
        and d2h == 0
        and bool(measured_on_real_nvidia)
    )
    updated = dict(validated)
    updated.update(
        {
            "status": "v1_5_4_device_memory_descriptor_measured_candidate",
            "host_to_device_transfers": h2d,
            "device_to_host_transfers": d2h,
            "device_residency_observed": device_residency,
            "measurement_backend": str(measurement_backend),
            "measurement_scope": str(measurement_scope),
            "measured_on_real_nvidia": bool(measured_on_real_nvidia),
            "measured_device_residency": measured_device_residency,
            "measured_transfer_count": measured_transfer_count,
            "true_zero_copy_evidence_candidate": true_zero_copy_evidence_candidate,
            "true_zero_copy_authorized": False,
            "public_speedup_wording_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "stable_public_primitive_authorized": False,
            "partner_tensor_handoff_authorized": False,
            "release_action_authorized": False,
            "claim_boundary": (
                "This v1.5.4 measurement envelope records transfer counts and "
                "device residency observations for a descriptor. Even if it "
                "identifies a true zero-copy evidence candidate, it does not "
                "authorize true zero-copy wording, public speedup wording, "
                "whole-app claims, stable primitive promotion, partner tensor "
                "handoff, or release action without separate reviewed evidence."
            ),
        }
    )
    return updated


def validate_v1_5_4_device_memory_measurement(measurement: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(measurement, dict):
        raise ValueError("v1.5.4 device memory measurement must be a dictionary")
    if measurement.get("status") != "v1_5_4_device_memory_descriptor_measured_candidate":
        raise ValueError("invalid v1.5.4 device memory measurement status")
    for field in V1_5_4_DEVICE_MEASUREMENT_REQUIRED_FIELDS:
        if field not in measurement:
            raise ValueError(f"v1.5.4 device memory measurement missing {field}")
    h2d = int(measurement["host_to_device_transfers"])
    d2h = int(measurement["device_to_host_transfers"])
    if h2d < 0 or d2h < 0:
        raise ValueError("v1.5.4 device memory measurement transfer counts must be non-negative")
    kind = measurement.get("memory_kind")
    zero_copy_candidate = kind in V1_5_4_DEVICE_MEMORY_ZERO_COPY_CANDIDATE_KINDS
    expected_measured_residency = bool(measurement["device_residency_observed"]) and zero_copy_candidate
    if measurement.get("measured_device_residency") is not expected_measured_residency:
        raise ValueError("invalid v1.5.4 measured device residency flag")
    if measurement.get("measured_transfer_count") is not True:
        raise ValueError("v1.5.4 device memory measurement must record transfer counts")
    expected_evidence_candidate = (
        zero_copy_candidate
        and expected_measured_residency
        and h2d == 0
        and d2h == 0
        and bool(measurement.get("measured_on_real_nvidia"))
    )
    if measurement.get("true_zero_copy_evidence_candidate") is not expected_evidence_candidate:
        raise ValueError("invalid v1.5.4 true zero-copy evidence candidate flag")
    for flag in (
        "true_zero_copy_authorized",
        "public_speedup_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "stable_public_primitive_authorized",
        "partner_tensor_handoff_authorized",
        "release_action_authorized",
    ):
        if measurement.get(flag) is not False:
            raise ValueError(f"v1.5.4 device memory measurement must keep {flag}=False")
    for phrase in (
        "records transfer counts and device residency observations",
        "true zero-copy evidence candidate",
        "does not authorize true zero-copy wording",
        "public speedup wording",
        "partner tensor handoff",
        "release action",
    ):
        if phrase not in measurement.get("claim_boundary", ""):
            raise ValueError("v1.5.4 device memory measurement claim boundary is incomplete")
    return measurement


def v1_5_4_gpu_memory_architecture_consensus_gate() -> dict[str, Any]:
    """Return the accepted memory ownership boundary for GPU+RTDL work."""
    return {
        "status": V1_5_4_GPU_MEMORY_ARCHITECTURE_CONSENSUS_STATUS,
        "track": V1_5_4_DEVICE_ZERO_COPY_TRACK,
        "required_evidence": V1_5_4_GPU_MEMORY_ARCHITECTURE_REQUIRED_EVIDENCE,
        "python_rtdl_memory_owner": "rtdl",
        "python_rtdl_default_data_location": "cpu_main_memory",
        "python_rtdl_zero_copy_default": False,
        "python_rtdl_allowed_focus": (
            "rtdl_managed_buffers",
            "prepared_host_buffers",
            "resident_rtdl_buffers",
            "managed_or_unified_memory_candidates",
            "measured_transfer_reuse",
        ),
        "python_partner_rtdl_memory_owner": "partner_runtime",
        "python_partner_rtdl_default_data_location": "partner_managed_gpu_memory",
        "python_partner_rtdl_zero_copy_plausible_with_evidence": True,
        "python_partner_rtdl_required_interop_metadata": (
            "device_pointer_or_handle",
            "shape_dtype_layout_stride",
            "owner_lifetime_rules",
            "stream_or_synchronization_metadata",
            "transfer_count_and_residency_evidence",
        ),
        "roadmap_boundary": (
            "v1_5_x_to_v1_6_python_rtdl_managed_memory",
            "v1_7_to_v2_0_python_partner_rtdl_external_gpu_memory_interop",
        ),
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "partner_tensor_handoff_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "This gate records the accepted architecture consensus that "
            "Python+RTDL and Python+partner+RTDL are separate GPU memory "
            "ownership tracks. Python+RTDL may manage or reuse RTDL-owned "
            "buffers but arbitrary Python data is not zero-copy. "
            "Python+partner+RTDL may attach to partner-owned GPU buffers only "
            "with explicit interop metadata and measured evidence. This gate "
            "does not authorize true zero-copy, public speedup wording, "
            "whole-app claims, stable primitive promotion, partner tensor "
            "handoff, or release action."
        ),
    }


def validate_v1_5_4_gpu_memory_architecture_consensus_gate() -> dict[str, Any]:
    gate = v1_5_4_gpu_memory_architecture_consensus_gate()
    if gate["status"] != V1_5_4_GPU_MEMORY_ARCHITECTURE_CONSENSUS_STATUS:
        raise ValueError("invalid v1.5.4 GPU memory architecture consensus status")
    if tuple(gate["required_evidence"]) != V1_5_4_GPU_MEMORY_ARCHITECTURE_REQUIRED_EVIDENCE:
        raise ValueError("v1.5.4 GPU memory architecture required evidence changed")
    if gate["python_rtdl_memory_owner"] != "rtdl":
        raise ValueError("Python+RTDL memory owner must remain RTDL")
    if gate["python_partner_rtdl_memory_owner"] != "partner_runtime":
        raise ValueError("Python+partner+RTDL memory owner must remain partner runtime")
    if gate["python_rtdl_zero_copy_default"] is not False:
        raise ValueError("Python+RTDL arbitrary data must not default to zero-copy")
    if gate["python_partner_rtdl_zero_copy_plausible_with_evidence"] is not True:
        raise ValueError("Python+partner+RTDL should remain plausible only with evidence")
    for flag in (
        "true_zero_copy_authorized",
        "public_speedup_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "stable_public_primitive_authorized",
        "partner_tensor_handoff_authorized",
        "release_action_authorized",
    ):
        if gate[flag] is not False:
            raise ValueError(f"v1.5.4 GPU memory architecture gate must keep {flag}=False")
    for phrase in (
        "separate GPU memory ownership tracks",
        "arbitrary Python data is not zero-copy",
        "partner-owned GPU buffers",
        "measured evidence",
        "does not authorize true zero-copy",
        "release action",
    ):
        if phrase not in gate["claim_boundary"]:
            raise ValueError("v1.5.4 GPU memory architecture claim boundary is incomplete")
    return gate


def v1_5_4_python_rtdl_managed_buffer_design_gate() -> dict[str, Any]:
    architecture_gate = validate_v1_5_4_gpu_memory_architecture_consensus_gate()
    return {
        "status": V1_5_4_PYTHON_RTDL_MANAGED_BUFFER_STATUS,
        "track": "python_rtdl",
        "depends_on_architecture_gate": architecture_gate["status"],
        "memory_owner": "rtdl",
        "not_partner_owned": True,
        "buffer_kinds": V1_5_4_PYTHON_RTDL_MANAGED_BUFFER_KINDS,
        "required_metadata": V1_5_4_PYTHON_RTDL_MANAGED_BUFFER_REQUIRED_METADATA,
        "allowed_design_actions": (
            "define_rtdl_owned_buffer_descriptor",
            "define_buffer_lifetime_and_reuse_rules",
            "define_copy_boundary_and_residency_metadata",
            "define_transfer_count_instrumentation_points",
            "prepare_future_optix_validation_plan",
        ),
        "requires_pod_now": False,
        "pod_required_for": (
            "device_resident_buffer_allocation_validation",
            "managed_or_unified_memory_residency_validation",
            "transfer_count_measurement_on_real_nvidia",
            "public_gpu_performance_claim_review_package",
        ),
        "host_data_zero_copy_default": False,
        "managed_buffer_zero_copy_authorized": False,
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "partner_tensor_handoff_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "This v1.5.4 gate starts the Python+RTDL RTDL-owned managed-buffer "
            "design lane. It covers RTDL-owned prepared host, pinned staging, "
            "device-resident, and managed/unified buffer candidates. It does "
            "not cover partner-owned GPU memory. Ordinary Python input data "
            "does not become zero-copy by default. This gate does not "
            "authorize true zero-copy, public speedup wording, whole-app "
            "claims, stable primitive promotion, partner tensor handoff, or "
            "release action."
        ),
    }


def validate_v1_5_4_python_rtdl_managed_buffer_design_gate() -> dict[str, Any]:
    gate = v1_5_4_python_rtdl_managed_buffer_design_gate()
    if gate["status"] != V1_5_4_PYTHON_RTDL_MANAGED_BUFFER_STATUS:
        raise ValueError("invalid v1.5.4 Python+RTDL managed-buffer gate status")
    if gate["track"] != "python_rtdl":
        raise ValueError("v1.5.4 managed-buffer gate must stay on Python+RTDL track")
    if gate["memory_owner"] != "rtdl":
        raise ValueError("v1.5.4 Python+RTDL managed buffers must be RTDL-owned")
    if gate["not_partner_owned"] is not True:
        raise ValueError("v1.5.4 Python+RTDL managed buffers must not be partner-owned")
    if tuple(gate["buffer_kinds"]) != V1_5_4_PYTHON_RTDL_MANAGED_BUFFER_KINDS:
        raise ValueError("v1.5.4 Python+RTDL managed-buffer kinds changed")
    if tuple(gate["required_metadata"]) != V1_5_4_PYTHON_RTDL_MANAGED_BUFFER_REQUIRED_METADATA:
        raise ValueError("v1.5.4 Python+RTDL managed-buffer metadata changed")
    if gate["requires_pod_now"] is not False:
        raise ValueError("v1.5.4 managed-buffer design gate must not require pod now")
    for flag in (
        "host_data_zero_copy_default",
        "managed_buffer_zero_copy_authorized",
        "true_zero_copy_authorized",
        "public_speedup_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "stable_public_primitive_authorized",
        "partner_tensor_handoff_authorized",
        "release_action_authorized",
    ):
        if gate[flag] is not False:
            raise ValueError(f"v1.5.4 managed-buffer gate must keep {flag}=False")
    for phrase in (
        "RTDL-owned managed-buffer",
        "does not cover partner-owned GPU memory",
        "Ordinary Python input data does not become zero-copy by default",
        "does not authorize true zero-copy",
        "public speedup wording",
        "release action",
    ):
        if phrase not in gate["claim_boundary"]:
            raise ValueError("v1.5.4 managed-buffer gate claim boundary is incomplete")
    return gate


def prepare_v1_5_4_python_rtdl_managed_buffer_descriptor(
    *,
    buffer_kind: str,
    backend: str,
    device: str,
    dtype: str,
    shape: tuple[int, ...] | list[int],
    lifetime: str,
    byte_count: int | None = None,
    pointer: int | None = None,
    residency_state: str | None = None,
    transfer_count_state: str = "not_measured",
) -> dict[str, Any]:
    """Prepare an RTDL-owned managed-buffer descriptor for Python+RTDL."""
    design_gate = validate_v1_5_4_python_rtdl_managed_buffer_design_gate()
    kind = str(buffer_kind)
    if kind not in V1_5_4_PYTHON_RTDL_MANAGED_BUFFER_KINDS:
        raise ValueError(f"unsupported v1.5.4 Python+RTDL managed buffer kind: {kind}")
    if dtype not in V1_5_4_DEVICE_MEMORY_ALLOWED_DTYPES:
        raise ValueError(f"unsupported v1.5.4 Python+RTDL managed buffer dtype: {dtype}")
    normalized_shape = tuple(int(value) for value in shape)
    if not normalized_shape or any(value <= 0 for value in normalized_shape):
        raise ValueError("v1.5.4 Python+RTDL managed buffer shape must contain positive dimensions")
    if lifetime not in V1_5_4_MANAGED_BUFFER_LIFETIMES:
        raise ValueError("unsupported v1.5.4 Python+RTDL managed buffer lifetime")
    normalized_byte_count = None if byte_count is None else int(byte_count)
    if normalized_byte_count is not None and normalized_byte_count <= 0:
        raise ValueError("v1.5.4 Python+RTDL managed buffer byte_count must be positive")
    normalized_pointer = None if pointer is None else int(pointer)
    if kind in ("prepared_host", "pinned_host_staging"):
        if device != "cpu":
            raise ValueError("v1.5.4 Python+RTDL host managed buffers must use device='cpu'")
        inferred_residency = "host_resident"
        copy_boundary = "rtdl_owned_host_reduced_copy"
    elif kind == "rtdl_device_resident":
        if device == "cpu":
            raise ValueError("v1.5.4 RTDL device-resident buffers must not use cpu device")
        inferred_residency = "device_candidate_unmeasured"
        copy_boundary = "rtdl_owned_device_residency_candidate_unmeasured"
    else:
        if device == "cpu":
            raise ValueError("v1.5.4 RTDL managed/unified buffers must not use cpu device")
        inferred_residency = "managed_unified_candidate_unmeasured"
        copy_boundary = "rtdl_owned_managed_unified_candidate_unmeasured"
    final_residency = inferred_residency if residency_state is None else str(residency_state)
    if final_residency not in V1_5_4_MANAGED_BUFFER_RESIDENCY_STATES:
        raise ValueError("unsupported v1.5.4 Python+RTDL managed buffer residency state")
    if final_residency != inferred_residency:
        raise ValueError("v1.5.4 Python+RTDL managed buffer residency state does not match buffer kind")
    if transfer_count_state not in V1_5_4_MANAGED_BUFFER_TRANSFER_STATES:
        raise ValueError("unsupported v1.5.4 Python+RTDL managed buffer transfer-count state")
    device_residency_candidate = kind in ("rtdl_device_resident", "rtdl_managed_unified")
    return {
        "status": "v1_5_4_python_rtdl_managed_buffer_descriptor_prepared",
        "track": "python_rtdl",
        "depends_on_gate": design_gate["status"],
        "buffer_kind": kind,
        "backend": str(backend),
        "device": str(device),
        "dtype": str(dtype),
        "shape": normalized_shape,
        "owner": "rtdl",
        "lifetime": str(lifetime),
        "byte_count": normalized_byte_count,
        "pointer": normalized_pointer,
        "copy_boundary": copy_boundary,
        "residency_state": final_residency,
        "transfer_count_state": str(transfer_count_state),
        "device_residency_candidate": device_residency_candidate,
        "partner_owned": False,
        "host_data_zero_copy_default": False,
        "managed_buffer_zero_copy_authorized": False,
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "partner_tensor_handoff_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "This v1.5.4 Python+RTDL managed-buffer descriptor is RTDL-owned. "
            "Host managed buffers are reduced-copy or transfer-reuse plumbing. "
            "Device-resident and managed/unified buffers are residency "
            "candidates only until real NVIDIA allocation, residency, and "
            "transfer counts are measured. This descriptor does not authorize "
            "true zero-copy, public speedup wording, whole-app claims, stable "
            "primitive promotion, partner tensor handoff, or release action."
        ),
    }


def validate_v1_5_4_python_rtdl_managed_buffer_descriptor(descriptor: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(descriptor, dict):
        raise ValueError("v1.5.4 Python+RTDL managed buffer descriptor must be a dictionary")
    if descriptor.get("status") != "v1_5_4_python_rtdl_managed_buffer_descriptor_prepared":
        raise ValueError("invalid v1.5.4 Python+RTDL managed buffer descriptor status")
    if descriptor.get("track") != "python_rtdl":
        raise ValueError("v1.5.4 managed buffer descriptor must stay on Python+RTDL track")
    if descriptor.get("owner") != "rtdl":
        raise ValueError("v1.5.4 managed buffer descriptor must be RTDL-owned")
    if descriptor.get("partner_owned") is not False:
        raise ValueError("v1.5.4 Python+RTDL managed buffer descriptor must not be partner-owned")
    kind = descriptor.get("buffer_kind")
    if kind not in V1_5_4_PYTHON_RTDL_MANAGED_BUFFER_KINDS:
        raise ValueError("invalid v1.5.4 managed buffer kind")
    if descriptor.get("dtype") not in V1_5_4_DEVICE_MEMORY_ALLOWED_DTYPES:
        raise ValueError("invalid v1.5.4 managed buffer dtype")
    shape = tuple(descriptor.get("shape", ()))
    if not shape or any(int(value) <= 0 for value in shape):
        raise ValueError("invalid v1.5.4 managed buffer shape")
    if descriptor.get("lifetime") not in V1_5_4_MANAGED_BUFFER_LIFETIMES:
        raise ValueError("invalid v1.5.4 managed buffer lifetime")
    if descriptor.get("residency_state") not in V1_5_4_MANAGED_BUFFER_RESIDENCY_STATES:
        raise ValueError("invalid v1.5.4 managed buffer residency state")
    if descriptor.get("transfer_count_state") not in V1_5_4_MANAGED_BUFFER_TRANSFER_STATES:
        raise ValueError("invalid v1.5.4 managed buffer transfer-count state")
    if kind in ("prepared_host", "pinned_host_staging"):
        if descriptor.get("device") != "cpu":
            raise ValueError("v1.5.4 host managed buffer descriptor must use cpu device")
        if descriptor.get("residency_state") != "host_resident":
            raise ValueError("v1.5.4 host managed buffer descriptor must remain host-resident")
        if descriptor.get("copy_boundary") != "rtdl_owned_host_reduced_copy":
            raise ValueError("v1.5.4 host managed buffer copy boundary changed")
        if descriptor.get("device_residency_candidate") is not False:
            raise ValueError("v1.5.4 host managed buffer must not be a device residency candidate")
    else:
        if descriptor.get("device") == "cpu":
            raise ValueError("v1.5.4 device managed buffer descriptor must not use cpu device")
        if descriptor.get("device_residency_candidate") is not True:
            raise ValueError("v1.5.4 device managed buffer must be a residency candidate")
    for flag in (
        "host_data_zero_copy_default",
        "managed_buffer_zero_copy_authorized",
        "true_zero_copy_authorized",
        "public_speedup_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "stable_public_primitive_authorized",
        "partner_tensor_handoff_authorized",
        "release_action_authorized",
    ):
        if descriptor.get(flag) is not False:
            raise ValueError(f"v1.5.4 managed buffer descriptor must keep {flag}=False")
    for phrase in (
        "RTDL-owned",
        "Host managed buffers are reduced-copy",
        "residency candidates only",
        "does not authorize true zero-copy",
        "public speedup wording",
        "partner tensor handoff",
        "release action",
    ):
        if phrase not in descriptor.get("claim_boundary", ""):
            raise ValueError("v1.5.4 managed buffer descriptor claim boundary is incomplete")
    return descriptor


def begin_v1_5_4_python_rtdl_managed_buffer_lifecycle(
    descriptor: dict[str, Any],
    *,
    allocation_id: str,
    allocation_backend: str | None = None,
) -> dict[str, Any]:
    """Create RTDL-owned lifecycle bookkeeping around a managed-buffer descriptor."""
    validated = validate_v1_5_4_python_rtdl_managed_buffer_descriptor(descriptor)
    if not allocation_id:
        raise ValueError("v1.5.4 managed buffer lifecycle requires allocation_id")
    backend = validated["backend"] if allocation_backend is None else str(allocation_backend)
    return {
        "status": "v1_5_4_python_rtdl_managed_buffer_lifecycle_active",
        "track": "python_rtdl",
        "allocation_id": str(allocation_id),
        "allocation_backend": backend,
        "descriptor": dict(validated),
        "owner": "rtdl",
        "lifecycle_state": "active_unmeasured",
        "host_to_rtdl_transfers": 0,
        "rtdl_to_host_transfers": 0,
        "rtdl_internal_transfers": 0,
        "event_log": (
            {
                "event": "begin_lifecycle",
                "allocation_id": str(allocation_id),
                "backend": backend,
                "residency_state": validated["residency_state"],
            },
        ),
        "measured_transfer_count": False,
        "measured_device_residency": False,
        "true_zero_copy_evidence_candidate": False,
        "managed_buffer_zero_copy_authorized": False,
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "partner_tensor_handoff_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "This v1.5.4 lifecycle record tracks RTDL-owned managed-buffer "
            "allocation bookkeeping and transfer events. It is not a native "
            "allocator and does not prove device residency. It does not "
            "authorize true zero-copy, public speedup wording, whole-app "
            "claims, stable primitive promotion, partner tensor handoff, or "
            "release action."
        ),
    }


def record_v1_5_4_python_rtdl_managed_buffer_transfer(
    lifecycle: dict[str, Any],
    *,
    direction: str,
    count: int = 1,
    note: str | None = None,
) -> dict[str, Any]:
    """Record transfer-count instrumentation for an active RTDL-owned buffer."""
    validated = validate_v1_5_4_python_rtdl_managed_buffer_lifecycle(lifecycle)
    if validated["lifecycle_state"] != "active_unmeasured":
        raise ValueError("v1.5.4 managed buffer transfers require an active lifecycle")
    if direction not in V1_5_4_MANAGED_BUFFER_TRANSFER_DIRECTIONS:
        raise ValueError("unsupported v1.5.4 managed buffer transfer direction")
    normalized_count = int(count)
    if normalized_count < 0:
        raise ValueError("v1.5.4 managed buffer transfer count must be non-negative")
    updated = dict(validated)
    if direction == "host_to_rtdl":
        updated["host_to_rtdl_transfers"] += normalized_count
    elif direction == "rtdl_to_host":
        updated["rtdl_to_host_transfers"] += normalized_count
    else:
        updated["rtdl_internal_transfers"] += normalized_count
    event = {
        "event": "record_transfer",
        "direction": direction,
        "count": normalized_count,
    }
    if note is not None:
        event["note"] = str(note)
    updated["event_log"] = tuple(validated["event_log"]) + (event,)
    updated["measured_transfer_count"] = True
    updated["true_zero_copy_evidence_candidate"] = False
    return validate_v1_5_4_python_rtdl_managed_buffer_lifecycle(updated)


def release_v1_5_4_python_rtdl_managed_buffer_lifecycle(lifecycle: dict[str, Any]) -> dict[str, Any]:
    """Mark RTDL-owned managed-buffer bookkeeping as released."""
    validated = validate_v1_5_4_python_rtdl_managed_buffer_lifecycle(lifecycle)
    if validated["lifecycle_state"] == "released":
        return validated
    updated = dict(validated)
    updated["status"] = "v1_5_4_python_rtdl_managed_buffer_lifecycle_released"
    updated["lifecycle_state"] = "released"
    updated["event_log"] = tuple(validated["event_log"]) + (
        {
            "event": "release_lifecycle",
            "allocation_id": validated["allocation_id"],
        },
    )
    return validate_v1_5_4_python_rtdl_managed_buffer_lifecycle(updated)


def validate_v1_5_4_python_rtdl_managed_buffer_lifecycle(lifecycle: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(lifecycle, dict):
        raise ValueError("v1.5.4 managed buffer lifecycle must be a dictionary")
    if lifecycle.get("status") not in (
        "v1_5_4_python_rtdl_managed_buffer_lifecycle_active",
        "v1_5_4_python_rtdl_managed_buffer_lifecycle_released",
    ):
        raise ValueError("invalid v1.5.4 managed buffer lifecycle status")
    if lifecycle.get("track") != "python_rtdl":
        raise ValueError("v1.5.4 managed buffer lifecycle must stay on Python+RTDL track")
    if lifecycle.get("owner") != "rtdl":
        raise ValueError("v1.5.4 managed buffer lifecycle must be RTDL-owned")
    if not lifecycle.get("allocation_id"):
        raise ValueError("v1.5.4 managed buffer lifecycle requires allocation_id")
    if not lifecycle.get("allocation_backend"):
        raise ValueError("v1.5.4 managed buffer lifecycle requires allocation_backend")
    descriptor = validate_v1_5_4_python_rtdl_managed_buffer_descriptor(lifecycle.get("descriptor", {}))
    if descriptor["owner"] != "rtdl":
        raise ValueError("v1.5.4 managed buffer lifecycle descriptor must be RTDL-owned")
    state = lifecycle.get("lifecycle_state")
    if state not in V1_5_4_MANAGED_BUFFER_LIFECYCLE_STATES:
        raise ValueError("invalid v1.5.4 managed buffer lifecycle state")
    expected_status = (
        "v1_5_4_python_rtdl_managed_buffer_lifecycle_released"
        if state == "released"
        else "v1_5_4_python_rtdl_managed_buffer_lifecycle_active"
    )
    if lifecycle.get("status") != expected_status:
        raise ValueError("v1.5.4 managed buffer lifecycle status/state mismatch")
    for field in ("host_to_rtdl_transfers", "rtdl_to_host_transfers", "rtdl_internal_transfers"):
        if int(lifecycle.get(field, -1)) < 0:
            raise ValueError("v1.5.4 managed buffer lifecycle transfer counts must be non-negative")
    event_log = lifecycle.get("event_log")
    if not isinstance(event_log, (tuple, list)) or not event_log:
        raise ValueError("v1.5.4 managed buffer lifecycle requires a non-empty event_log")
    expected_measured_transfer = any(
        int(lifecycle[field]) > 0
        for field in ("host_to_rtdl_transfers", "rtdl_to_host_transfers", "rtdl_internal_transfers")
    )
    if lifecycle.get("measured_transfer_count") is not expected_measured_transfer:
        raise ValueError("v1.5.4 managed buffer lifecycle measured transfer flag is inconsistent")
    if lifecycle.get("measured_device_residency") is not False:
        raise ValueError("v1.5.4 managed buffer lifecycle must not claim measured device residency")
    for flag in (
        "true_zero_copy_evidence_candidate",
        "managed_buffer_zero_copy_authorized",
        "true_zero_copy_authorized",
        "public_speedup_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "stable_public_primitive_authorized",
        "partner_tensor_handoff_authorized",
        "release_action_authorized",
    ):
        if lifecycle.get(flag) is not False:
            raise ValueError(f"v1.5.4 managed buffer lifecycle must keep {flag}=False")
    for phrase in (
        "allocation bookkeeping",
        "transfer events",
        "not a native allocator",
        "does not prove device residency",
        "does not authorize true zero-copy",
        "public speedup wording",
        "release action",
    ):
        if phrase not in lifecycle.get("claim_boundary", ""):
            raise ValueError("v1.5.4 managed buffer lifecycle claim boundary is incomplete")
    return lifecycle


def attach_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(
    lifecycle: dict[str, Any],
    *,
    allocation_method: str,
    measurement_backend: str,
    measurement_scope: str,
    host_to_device_transfers: int,
    device_to_host_transfers: int,
    device_residency_observed: bool,
    measured_on_real_nvidia: bool = False,
    hardware_identity: str | None = None,
    backend_version: str | None = None,
) -> dict[str, Any]:
    """Attach backend allocation evidence without promoting public claims."""
    validated = validate_v1_5_4_python_rtdl_managed_buffer_lifecycle(lifecycle)
    if allocation_method not in V1_5_4_MANAGED_BUFFER_ALLOCATION_METHODS:
        raise ValueError("unsupported v1.5.4 managed buffer allocation method")
    if not measurement_backend:
        raise ValueError("v1.5.4 managed buffer allocation evidence requires measurement_backend")
    if not measurement_scope:
        raise ValueError("v1.5.4 managed buffer allocation evidence requires measurement_scope")
    h2d = int(host_to_device_transfers)
    d2h = int(device_to_host_transfers)
    if h2d < 0 or d2h < 0:
        raise ValueError("v1.5.4 managed buffer allocation evidence transfer counts must be non-negative")
    descriptor = validated["descriptor"]
    device_candidate = bool(descriptor["device_residency_candidate"])
    residency = bool(device_residency_observed)
    measured_device_residency = device_candidate and residency
    true_zero_copy_evidence_candidate = (
        device_candidate
        and measured_device_residency
        and h2d == 0
        and d2h == 0
        and bool(measured_on_real_nvidia)
        and allocation_method in ("cuda_device_alloc", "cuda_managed_alloc")
    )
    return {
        "status": "v1_5_4_python_rtdl_managed_buffer_allocation_evidence_attached",
        "track": "python_rtdl",
        "lifecycle": dict(validated),
        "owner": "rtdl",
        "allocation_id": validated["allocation_id"],
        "allocation_method": str(allocation_method),
        "measurement_backend": str(measurement_backend),
        "measurement_scope": str(measurement_scope),
        "host_to_device_transfers": h2d,
        "device_to_host_transfers": d2h,
        "device_residency_observed": residency,
        "measured_device_residency": measured_device_residency,
        "measured_transfer_count": True,
        "measured_on_real_nvidia": bool(measured_on_real_nvidia),
        "hardware_identity": None if hardware_identity is None else str(hardware_identity),
        "backend_version": None if backend_version is None else str(backend_version),
        "true_zero_copy_evidence_candidate": true_zero_copy_evidence_candidate,
        "managed_buffer_zero_copy_authorized": False,
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "partner_tensor_handoff_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "This v1.5.4 allocation evidence envelope records backend "
            "allocation method, transfer counts, hardware identity, and "
            "device residency observations for an RTDL-owned managed buffer. "
            "It may identify a true zero-copy evidence candidate only when "
            "a real NVIDIA device-resident path records zero host/device "
            "transfers and observed residency. It still does not authorize "
            "true zero-copy wording, public speedup wording, whole-app "
            "claims, stable primitive promotion, partner tensor handoff, or "
            "release action."
        ),
    }


def validate_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(
    evidence: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(evidence, dict):
        raise ValueError("v1.5.4 managed buffer allocation evidence must be a dictionary")
    if evidence.get("status") != "v1_5_4_python_rtdl_managed_buffer_allocation_evidence_attached":
        raise ValueError("invalid v1.5.4 managed buffer allocation evidence status")
    if evidence.get("track") != "python_rtdl":
        raise ValueError("v1.5.4 managed buffer allocation evidence must stay on Python+RTDL track")
    if evidence.get("owner") != "rtdl":
        raise ValueError("v1.5.4 managed buffer allocation evidence must be RTDL-owned")
    lifecycle = validate_v1_5_4_python_rtdl_managed_buffer_lifecycle(evidence.get("lifecycle", {}))
    if evidence.get("allocation_id") != lifecycle["allocation_id"]:
        raise ValueError("v1.5.4 managed buffer allocation evidence allocation_id mismatch")
    if evidence.get("allocation_method") not in V1_5_4_MANAGED_BUFFER_ALLOCATION_METHODS:
        raise ValueError("invalid v1.5.4 managed buffer allocation method")
    if not evidence.get("measurement_backend"):
        raise ValueError("v1.5.4 managed buffer allocation evidence requires measurement_backend")
    if not evidence.get("measurement_scope"):
        raise ValueError("v1.5.4 managed buffer allocation evidence requires measurement_scope")
    h2d = int(evidence.get("host_to_device_transfers", -1))
    d2h = int(evidence.get("device_to_host_transfers", -1))
    if h2d < 0 or d2h < 0:
        raise ValueError("v1.5.4 managed buffer allocation evidence transfer counts must be non-negative")
    descriptor = lifecycle["descriptor"]
    expected_residency = bool(descriptor["device_residency_candidate"]) and bool(
        evidence.get("device_residency_observed")
    )
    if evidence.get("measured_device_residency") is not expected_residency:
        raise ValueError("invalid v1.5.4 managed buffer measured residency flag")
    if evidence.get("measured_transfer_count") is not True:
        raise ValueError("v1.5.4 managed buffer allocation evidence must measure transfer counts")
    expected_candidate = (
        bool(descriptor["device_residency_candidate"])
        and expected_residency
        and h2d == 0
        and d2h == 0
        and bool(evidence.get("measured_on_real_nvidia"))
        and evidence.get("allocation_method") in ("cuda_device_alloc", "cuda_managed_alloc")
    )
    if evidence.get("true_zero_copy_evidence_candidate") is not expected_candidate:
        raise ValueError("invalid v1.5.4 managed buffer true zero-copy evidence candidate flag")
    for flag in (
        "managed_buffer_zero_copy_authorized",
        "true_zero_copy_authorized",
        "public_speedup_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "stable_public_primitive_authorized",
        "partner_tensor_handoff_authorized",
        "release_action_authorized",
    ):
        if evidence.get(flag) is not False:
            raise ValueError(f"v1.5.4 managed buffer allocation evidence must keep {flag}=False")
    for phrase in (
        "allocation method",
        "transfer counts",
        "hardware identity",
        "device residency observations",
        "true zero-copy evidence candidate",
        "does not authorize true zero-copy wording",
        "public speedup wording",
        "release action",
    ):
        if phrase not in evidence.get("claim_boundary", ""):
            raise ValueError("v1.5.4 managed buffer allocation evidence claim boundary is incomplete")
    return evidence


def v1_5_4_managed_buffer_cuda_evidence_boundary_gate(
    *,
    allocation_evidence: dict[str, Any],
    copy_boundary_evidence: dict[str, Any],
) -> dict[str, Any]:
    """Summarize the accepted boundary between allocation-only and copy evidence."""
    allocation = validate_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(allocation_evidence)
    copy_boundary = validate_v1_5_4_python_rtdl_managed_buffer_allocation_evidence(copy_boundary_evidence)
    allocation_candidate = bool(allocation["true_zero_copy_evidence_candidate"])
    copy_candidate = bool(copy_boundary["true_zero_copy_evidence_candidate"])
    allocation_zero_transfers = (
        int(allocation["host_to_device_transfers"]) == 0
        and int(allocation["device_to_host_transfers"]) == 0
    )
    copy_has_counted_transfers = (
        int(copy_boundary["host_to_device_transfers"]) > 0
        or int(copy_boundary["device_to_host_transfers"]) > 0
    )
    accepted = (
        allocation_candidate
        and allocation_zero_transfers
        and not copy_candidate
        and copy_has_counted_transfers
        and bool(allocation["measured_on_real_nvidia"])
        and bool(copy_boundary["measured_on_real_nvidia"])
    )
    return {
        "status": "v1_5_4_managed_buffer_cuda_evidence_boundary_accepted" if accepted else "v1_5_4_managed_buffer_cuda_evidence_boundary_incomplete",
        "track": "python_rtdl",
        "allocation_only_candidate": allocation_candidate,
        "allocation_only_zero_transfers": allocation_zero_transfers,
        "copy_boundary_candidate": copy_candidate,
        "copy_boundary_has_counted_transfers": copy_has_counted_transfers,
        "both_measured_on_real_nvidia": bool(allocation["measured_on_real_nvidia"])
        and bool(copy_boundary["measured_on_real_nvidia"]),
        "accepted_boundary": accepted,
        "proven": (
            "rtdl_owned_cuda_driver_allocation_free_path_exists",
            "allocation_only_probe_can_be_candidate_evidence",
            "python_origin_content_copy_boundary_is_counted",
            "explicit_copy_boundary_is_not_true_zero_copy_candidate",
        ),
        "not_proven": (
            "end_to_end_rtdl_optix_device_buffer_execution",
            "public_true_zero_copy",
            "public_speedup",
            "whole_application_speedup",
            "partner_tensor_handoff",
            "release_readiness",
        ),
        "next_required_evidence": (
            "optix_ready_environment_with_librtdl_optix_or_build_toolchain",
            "rtdl_backend_entry_accepting_rtdl_owned_device_memory_descriptor",
            "same_contract_parity_against_host_or_embree_path",
            "transfer_count_accounting_around_backend_execution",
            "external_ai_review_before_public_claims",
        ),
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "partner_tensor_handoff_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "This v1.5.4 boundary gate accepts the contrast between CUDA "
            "Driver API allocation-only evidence and explicit content-copy "
            "evidence. Allocation-only evidence may be a candidate shape, "
            "while Python-origin content movement must be counted and is not "
            "true zero-copy. This gate does not prove end-to-end RTDL/OptiX "
            "device-buffer execution and does not authorize public true "
            "zero-copy wording, public speedup wording, whole-app claims, "
            "partner tensor handoff, or release action."
        ),
    }


def validate_v1_5_4_managed_buffer_cuda_evidence_boundary_gate(gate: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(gate, dict):
        raise ValueError("v1.5.4 CUDA evidence boundary gate must be a dictionary")
    if gate.get("status") != "v1_5_4_managed_buffer_cuda_evidence_boundary_accepted":
        raise ValueError("v1.5.4 CUDA evidence boundary gate is not accepted")
    if gate.get("track") != "python_rtdl":
        raise ValueError("v1.5.4 CUDA evidence boundary gate must stay on Python+RTDL track")
    if gate.get("allocation_only_candidate") is not True:
        raise ValueError("v1.5.4 CUDA boundary requires allocation-only candidate evidence")
    if gate.get("allocation_only_zero_transfers") is not True:
        raise ValueError("v1.5.4 CUDA boundary requires zero allocation-only transfers")
    if gate.get("copy_boundary_candidate") is not False:
        raise ValueError("v1.5.4 CUDA copy boundary must not be a zero-copy candidate")
    if gate.get("copy_boundary_has_counted_transfers") is not True:
        raise ValueError("v1.5.4 CUDA copy boundary requires counted transfers")
    if gate.get("both_measured_on_real_nvidia") is not True:
        raise ValueError("v1.5.4 CUDA evidence boundary requires real NVIDIA evidence")
    if gate.get("accepted_boundary") is not True:
        raise ValueError("v1.5.4 CUDA evidence boundary must be accepted")
    for required in (
        "rtdl_owned_cuda_driver_allocation_free_path_exists",
        "allocation_only_probe_can_be_candidate_evidence",
        "python_origin_content_copy_boundary_is_counted",
        "explicit_copy_boundary_is_not_true_zero_copy_candidate",
    ):
        if required not in gate.get("proven", ()):
            raise ValueError("v1.5.4 CUDA evidence boundary proven list is incomplete")
    for forbidden in (
        "end_to_end_rtdl_optix_device_buffer_execution",
        "public_true_zero_copy",
        "public_speedup",
        "whole_application_speedup",
        "partner_tensor_handoff",
        "release_readiness",
    ):
        if forbidden not in gate.get("not_proven", ()):
            raise ValueError("v1.5.4 CUDA evidence boundary not_proven list is incomplete")
    for flag in (
        "true_zero_copy_authorized",
        "public_speedup_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "stable_public_primitive_authorized",
        "partner_tensor_handoff_authorized",
        "release_action_authorized",
    ):
        if gate.get(flag) is not False:
            raise ValueError(f"v1.5.4 CUDA evidence boundary must keep {flag}=False")
    for phrase in (
        "allocation-only evidence",
        "explicit content-copy evidence",
        "Python-origin content movement must be counted",
        "does not prove end-to-end RTDL/OptiX",
        "does not authorize public true zero-copy wording",
        "public speedup wording",
        "release action",
    ):
        if phrase not in gate.get("claim_boundary", ""):
            raise ValueError("v1.5.4 CUDA evidence boundary claim boundary is incomplete")
    return gate


def v1_5_4_optix_device_buffer_execution_contract_gate(
    *,
    preflight: dict[str, Any],
    cuda_boundary_gate: dict[str, Any],
) -> dict[str, Any]:
    """Define the next OptiX device-buffer execution contract after preflight."""
    boundary = validate_v1_5_4_managed_buffer_cuda_evidence_boundary_gate(cuda_boundary_gate)
    preflight_valid = bool(preflight.get("valid_for_optix_device_buffer_execution_work"))
    return {
        "status": (
            "v1_5_4_optix_device_buffer_execution_contract_ready"
            if preflight_valid
            else "v1_5_4_optix_device_buffer_execution_contract_blocked_by_preflight"
        ),
        "track": "python_rtdl",
        "depends_on_cuda_boundary_gate": boundary["status"],
        "preflight_valid": preflight_valid,
        "preflight_blockers": tuple(preflight.get("blockers", ())),
        "first_target_primitive": "COLLECT_K_BOUNDED",
        "first_target_native_symbols": (
            "rtdl_embree_collect_k_bounded_i64",
            "rtdl_optix_collect_k_bounded_i64",
        ),
        "input_memory_contract": (
            "rtdl_owned_device_resident_i64_candidate_rows",
            "row_width_explicit",
            "candidate_count_explicit",
            "owner_lifetime_explicit",
        ),
        "output_memory_contract": (
            "bounded_rtdl_owned_result_buffer",
            "valid_count_out",
            "overflowed_out",
            "fail_closed_on_overflow",
        ),
        "required_parity": (
            "same_candidate_rows",
            "same_row_width",
            "same_capacity",
            "same_valid_count",
            "same_overflow_flag",
            "same_deduplicated_lexicographic_rows",
        ),
        "required_transfer_accounting": (
            "host_to_device_transfers_before_backend_execution",
            "device_to_host_transfers_after_backend_execution",
            "internal_device_transfers_if_any",
            "allocation_only_transfers_distinguished_from_content_transfers",
        ),
        "minimum_artifacts": (
            "optix_preflight_green_json",
            "device_buffer_execution_json",
            "device_buffer_execution_markdown",
            "same_contract_parity_json",
            "transfer_accounting_summary",
        ),
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "partner_tensor_handoff_authorized": False,
        "release_action_authorized": False,
        "claim_boundary": (
            "This v1.5.4 OptiX device-buffer execution contract gate defines "
            "the next Python+RTDL backend evidence target after an OptiX-ready "
            "preflight. It targets COLLECT_K_BOUNDED first because the i64 row "
            "ABI and parity contract already exist. The gate does not itself "
            "run OptiX, does not prove true zero-copy, and does not authorize "
            "public speedup wording, whole-app claims, partner tensor handoff, "
            "or release action."
        ),
    }


def validate_v1_5_4_optix_device_buffer_execution_contract_gate(gate: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(gate, dict):
        raise ValueError("v1.5.4 OptiX device-buffer execution contract gate must be a dictionary")
    if gate.get("status") not in (
        "v1_5_4_optix_device_buffer_execution_contract_ready",
        "v1_5_4_optix_device_buffer_execution_contract_blocked_by_preflight",
    ):
        raise ValueError("invalid v1.5.4 OptiX device-buffer execution contract status")
    if gate.get("track") != "python_rtdl":
        raise ValueError("v1.5.4 OptiX device-buffer execution contract must stay on Python+RTDL track")
    if gate.get("depends_on_cuda_boundary_gate") != "v1_5_4_managed_buffer_cuda_evidence_boundary_accepted":
        raise ValueError("v1.5.4 OptiX device-buffer execution contract requires accepted CUDA boundary")
    if gate.get("first_target_primitive") != "COLLECT_K_BOUNDED":
        raise ValueError("v1.5.4 first device-buffer target must remain COLLECT_K_BOUNDED")
    for symbol in ("rtdl_embree_collect_k_bounded_i64", "rtdl_optix_collect_k_bounded_i64"):
        if symbol not in gate.get("first_target_native_symbols", ()):
            raise ValueError("v1.5.4 device-buffer contract native symbol list is incomplete")
    for required in (
        "same_candidate_rows",
        "same_valid_count",
        "same_overflow_flag",
        "same_deduplicated_lexicographic_rows",
    ):
        if required not in gate.get("required_parity", ()):
            raise ValueError("v1.5.4 device-buffer contract parity list is incomplete")
    for required in (
        "host_to_device_transfers_before_backend_execution",
        "device_to_host_transfers_after_backend_execution",
        "allocation_only_transfers_distinguished_from_content_transfers",
    ):
        if required not in gate.get("required_transfer_accounting", ()):
            raise ValueError("v1.5.4 device-buffer contract transfer accounting list is incomplete")
    for flag in (
        "true_zero_copy_authorized",
        "public_speedup_wording_authorized",
        "whole_app_speedup_claim_authorized",
        "stable_public_primitive_authorized",
        "partner_tensor_handoff_authorized",
        "release_action_authorized",
    ):
        if gate.get(flag) is not False:
            raise ValueError(f"v1.5.4 OptiX device-buffer contract must keep {flag}=False")
    for phrase in (
        "OptiX device-buffer execution contract gate",
        "COLLECT_K_BOUNDED first",
        "does not itself run OptiX",
        "does not prove true zero-copy",
        "public speedup wording",
        "partner tensor handoff",
        "release action",
    ):
        if phrase not in gate.get("claim_boundary", ""):
            raise ValueError("v1.5.4 OptiX device-buffer contract claim boundary is incomplete")
    return gate
