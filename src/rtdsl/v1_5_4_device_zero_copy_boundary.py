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
