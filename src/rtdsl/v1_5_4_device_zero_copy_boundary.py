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
